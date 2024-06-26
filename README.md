# MPC balancer

The MPC balancer allows Upkie to stand upright, balancing with its wheels only, by closed-loop model predictive control. It performs better than the demo [PID balancer](https://github.com/upkie/upkie/tree/902532ecdfdcf0430db7b36cba08a8164c0aa95e/agents/pid_balancer), with significantly less hacks ;-)

## Installation

We recommend using Anaconda to install the agent and all its dependencies in a clean environment:

```console
conda create -f environment.yaml
conda activate mpc_balancer
```

Alternatively, you should be able to install the packages listed in the environment file from PyPI.

## Usage

Start the [pi3hat spine](https://upkie.github.io/upkie/spines.html#pi3hat-spine) to run the agent on your robot, or the [Bullet spine](https://upkie.github.io/upkie/spines.html#bullet-spine) to check the agent first in simulation (recommended). Then, run the agent by:

```console
python mpc_balancer.py
```
