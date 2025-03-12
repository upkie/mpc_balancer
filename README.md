# MPC balancer

[![upkie](https://img.shields.io/badge/upkie-7.0.0-aabbcc)](https://github.com/upkie/upkie/tree/v7.0.0)

Make an Upkie to stand upright by closed-loop model predictive control.

## Installation

We recommend using Anaconda to install the agent and all its dependencies in a clean environment:

```console
conda env create -f environment.yaml
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

## Export dependencies to your Upkie

This agent can export a pixi environment to your Upkie using `pixi-pack`. If you don't have pixi yet, you can [install it](https://pixi.sh/latest/#installation).

First, create an `environment.tar` file with the following command:

```bash
pixi run pack-to-upkie
```

Then, upload it to your Upkie and unpack it by:

```bash
pixi-pack unpack environment.tar
```

If `pixi-pack` is not installed on your Upkie, you can get a `pixi-pack-aarch64-unknown-linux-gnu` binary from the [pixi-pack release page](https://github.com/Quantco/pixi-pack/releases). Finally, activate the environment and run the agent:

```bash
source ./activate.sh
python mpc_balancer/run.py
```

## See also

- [PPO balancer](https://github.com/upkie/ppo_balancer): an MLP agent trained for the same task by reinforcement learning.
- [ProxQP balancer](https://github.com/stephane-caron/proxqp_balancer): prototype for this agent used in the code for the [ProxQP paper](https://inria.hal.science/hal-04198663v2). Currently supports more QP solvers.
