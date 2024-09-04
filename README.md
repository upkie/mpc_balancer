# MPC balancer

Make an Upkie to stand upright by closed-loop model predictive control.

## Installation

We recommend using Anaconda to install the agent and all its dependencies in a clean environment:

```console
conda create -f environment.yaml
conda activate mpc_balancer
```

Alternatively, you should be able to install the packages listed in the environment file from PyPI.

## Usage

To run in simulation, clone the [upkie](https://github.com/upkie/upkie) repository and run:

```console
./start_simulation.sh
```

Activate your conda environment and run the agent by:

```console
python run_agent.py
```

## Solvers

This agent only works with QP solvers that support warm starting. At present we only support one solver:

| Solver | Algorithm | License | Warm-start |
| ------ | --------- | ------- |------------|
| [ProxQP](https://github.com/Simple-Robotics/proxsuite) | Augmented Lagrangian | BSD-2-Clause | ✔️ |

You can take a peek at the [ProxQP balancer](https://github.com/stephane-caron/proxqp_balancer) (research code) for more solvers.

## See also

- [PPO balancer](https://github.com/upkie/ppo_balancer): an MLP agent trained for the same task by reinforcement learning.
- [ProxQP balancer](https://github.com/stephane-caron/proxqp_balancer): prototype for this agent used in the code for the [ProxQP paper](https://inria.hal.science/hal-04198663v2). Currently supports more QP solvers.
