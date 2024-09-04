#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 Inria

"""Wheel balancing using model predictive control with the ProxQP solver."""

import socket
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import gin
import gymnasium as gym
import numpy as np
import qpsolvers
import upkie.envs
from proxsuite import proxqp
from qpmpc import MPCQP, Plan, solve_mpc
from qpmpc.systems import WheeledInvertedPendulum
from qpsolvers import solve_problem
from upkie.utils.clamp import clamp_and_warn
from upkie.utils.filters import low_pass_filter
from upkie.utils.raspi import configure_agent_process, on_raspi
from upkie.utils.spdlog import logging

upkie.envs.register()


@gin.configurable
@dataclass
class UpkieGeometry:
    leg_length: float
    wheel_radius: float
    rotation_base_to_imu: Optional[List[float]] = None

    def get_spine_config(self) -> dict:
        spine_config = {
            "wheel_odometry": {
                "signed_radius": {
                    "left_wheel": +self.wheel_radius,
                    "right_wheel": -self.wheel_radius,
                }
            }
        }
        if self.rotation_base_to_imu is not None:
            spine_config["base_orientation"] = {
                "rotation_base_to_imu": np.array(
                    self.rotation_base_to_imu,
                    dtype=float,
                ),
            }
        return spine_config


@gin.configurable
class PendularUpkie(WheeledInvertedPendulum):
    def __init__(
        self,
        max_ground_accel: float,
        nb_timesteps: int,
        sampling_period: float,
    ):
        super().__init__(
            length=UpkieGeometry().leg_length,
            max_ground_accel=max_ground_accel,
            nb_timesteps=nb_timesteps,
            sampling_period=sampling_period,
        )


@gin.configurable
class ProxQPWorkspace:
    def __init__(
        self, mpc_qp: MPCQP, update_preconditioner: bool, verbose: bool
    ):
        n_eq = 0
        n_in = mpc_qp.h.size // 2  # WheeledInvertedPendulum structure
        n = mpc_qp.P.shape[1]
        solver = proxqp.dense.QP(
            n,
            n_eq,
            n_in,
            dense_backend=proxqp.dense.DenseBackend.PrimalDualLDLT,
        )
        solver.settings.eps_abs = 1e-3
        solver.settings.eps_rel = 0.0
        solver.settings.verbose = verbose
        solver.settings.compute_timings = True
        solver.settings.primal_infeasibility_solving = True
        solver.init(
            H=mpc_qp.P,
            g=mpc_qp.q,
            C=mpc_qp.G[::2, :],  # WheeledInvertedPendulum structure
            l=-mpc_qp.h[1::2],  # WheeledInvertedPendulum structure
            u=mpc_qp.h[::2],  # WheeledInvertedPendulum structure
        )
        solver.solve()
        self.update_preconditioner = update_preconditioner
        self.solver = solver

    def solve(self, mpc_qp: MPCQP) -> qpsolvers.Solution:
        self.solver.update(
            g=mpc_qp.q,
            update_preconditioner=self.update_preconditioner,
        )
        self.solver.solve()
        result = self.solver.results
        qpsol = qpsolvers.Solution(mpc_qp.problem)
        qpsol.found = result.info.status == proxqp.QPSolverOutput.PROXQP_SOLVED
        qpsol.x = self.solver.results.x
        return qpsol


@gin.configurable
def balance(
    env: gym.Env,
    rebuild_qp_every_time: bool,
    stage_input_cost_weight: float,
    stage_state_cost_weight: float,
    terminal_cost_weight: float,
    warm_start: bool,
):
    """Run MPC balancer in gym environment with logging.

    Args:
        env: Gym environment to Upkie.
        rebuild_qp_every_time: If set, rebuild all QP matrices at every
            iteration. Otherwise, only update vectors.
        stage_input_cost_weight: Weight for the stage input cost.
        stage_state_cost_weight: Weight for the stage state cost.
        terminal_cost_weight: Weight for the terminal cost.
        warm_start: If set, use the warm-starting feature of ProxQP.
    """
    pendulum = PendularUpkie()
    mpc_problem = pendulum.build_mpc_problem(
        terminal_cost_weight=terminal_cost_weight,
        stage_state_cost_weight=stage_state_cost_weight,
        stage_input_cost_weight=stage_input_cost_weight,
    )
    mpc_problem.initial_state = np.zeros(4)
    mpc_qp = MPCQP(mpc_problem)
    workspace = ProxQPWorkspace(mpc_qp)

    env.reset()  # connects to the spine
    commanded_velocity = 0.0
    action = np.zeros(env.action_space.shape)

    while True:
        action[0] = commanded_velocity
        observation, _, terminated, truncated, info = env.step(action)
        env.unwrapped.log("observation", observation)
        if terminated or truncated:
            observation, info = env.reset()
            commanded_velocity = 0.0

        spine_observation = info["spine_observation"]
        floor_contact = spine_observation["floor_contact"]["contact"]

        # Unpack observation into initial MPC state
        (
            base_pitch,
            ground_position,
            base_angular_velocity,
            ground_velocity,
        ) = observation
        initial_state = np.array(
            [
                ground_position,
                base_pitch,
                ground_velocity,
                base_angular_velocity,
            ]
        )

        nx = WheeledInvertedPendulum.STATE_DIM
        target_states = np.zeros((pendulum.nb_timesteps + 1) * nx)
        mpc_problem.update_initial_state(initial_state)
        mpc_problem.update_goal_state(target_states[-nx:])
        mpc_problem.update_target_states(target_states[:-nx])

        if rebuild_qp_every_time:
            plan = solve_mpc(mpc_problem, solver="proxqp")
        else:
            mpc_qp.update_cost_vector(mpc_problem)
            if warm_start:
                qpsol = workspace.solve(mpc_qp)
            else:
                qpsol = solve_problem(mpc_qp.problem, solver="proxqp")
            if not qpsol.found:
                logging.warn("No solution found to the MPC problem")
            plan = Plan(mpc_problem, qpsol)

        if not floor_contact:
            commanded_velocity = low_pass_filter(
                prev_output=commanded_velocity,
                cutoff_period=0.1,
                new_input=0.0,
                dt=env.unwrapped.dt,
            )
        elif plan.is_empty:
            logging.error("Solver found no solution to the MPC problem")
            logging.info("Continuing with previous action")
        else:  # plan was found
            pendulum.state = initial_state
            commanded_accel = plan.first_input[0]
            commanded_velocity = clamp_and_warn(
                commanded_velocity + commanded_accel * env.unwrapped.dt / 2.0,
                lower=-1.0,
                upper=+1.0,
                label="commanded_velocity",
            )


if __name__ == "__main__":
    if on_raspi():
        configure_agent_process()

    hostname = socket.gethostname()
    config_dir = Path(__file__).parent / "config"
    gin.parse_config_file(f"{config_dir}/base.gin")
    host_config = Path(config_dir / f"{hostname}.gin")
    if host_config.exists():
        gin.parse_config_file(host_config)
    upkie_geometry = UpkieGeometry()
    with gym.make(
        "UpkieGroundVelocity-v3",
        frequency=200.0,
        wheel_radius=upkie_geometry.wheel_radius,
        spine_config=upkie_geometry.get_spine_config(),
        disable_env_checker=True,  # faster startup
    ) as env:
        balance(env)
