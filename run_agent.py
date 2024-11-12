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
import upkie.envs
from qpmpc import MPCQP, Plan, solve_mpc
from qpmpc.systems import WheeledInvertedPendulum
from qpsolvers import solve_problem
from upkie.utils.clamp import clamp_and_warn
from upkie.utils.filters import low_pass_filter
from upkie.utils.raspi import configure_agent_process, on_raspi
from upkie.utils.spdlog import logging

from mpc_balancer import ProxQPWorkspace

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
def balance(
    env: gym.Env,
    max_ground_accel: float,
    max_ground_velocity: float,
    mpc_sampling_period: float,
    nb_mpc_timesteps: int,
    rebuild_qp_every_time: bool,
    stage_input_cost_weight: float,
    stage_state_cost_weight: float,
    terminal_cost_weight: float,
    warm_start: bool,
):
    """Run MPC balancer with logging.

    Args:
        env: Gymnasium environment to Upkie.
        max_ground_accel: Maximum ground acceleration, in [m] / [s]².
        max_ground_velocity: Maximum ground velocity, in [m] / [s].
        mpc_sampling_period: Duration of an MPC timestep, in [s].
        nb_mpc_timesteps: Number of timesteps in the receding horizon.
        rebuild_qp_every_time: If set, rebuild all QP matrices at every
            iteration. Otherwise, only update vectors.
        stage_input_cost_weight: Weight for the stage input cost.
        stage_state_cost_weight: Weight for the stage state cost.
        terminal_cost_weight: Weight for the terminal cost.
        warm_start: If set, use the warm-starting feature of ProxQP.
    """
    pendulum = WheeledInvertedPendulum(
        length=UpkieGeometry().leg_length,
        max_ground_accel=max_ground_accel,
        nb_timesteps=nb_mpc_timesteps,
        sampling_period=mpc_sampling_period,
    )
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
                logging.warning("No solution found to the MPC problem")
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
                lower=-max_ground_velocity,
                upper=+max_ground_velocity,
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
    logging.info(f"Leg length: {upkie_geometry.leg_length} m")
    logging.info(f"Wheel radius: {upkie_geometry.wheel_radius} m")
    with gym.make(
        "UpkieGroundVelocity-v3",
        disable_env_checker=True,  # faster startup
        frequency=200.0,
        spine_config=upkie_geometry.get_spine_config(),
        wheel_radius=upkie_geometry.wheel_radius,
    ) as env:
        balance(env)
