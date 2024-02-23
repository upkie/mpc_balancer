# MPC balancer

The MPC balancer allows Upkie to stand upright, balancing with its wheels only, by closed-loop model predictive control. It performs better than the demo [PID balancer](https://github.com/upkie/upkie/tree/902532ecdfdcf0430db7b36cba08a8164c0aa95e/agents/pid_balancer) with significantly less hacks ;-)

## Installation

### From Conda

```console
conda create -f environment.yaml
conda activate mpc_balancer
```

### From PyPI

```console
pip install upkie[mpc_balancer]
```

This instruction works on both your dev machine and the robot's Raspberry Pi.

## Simulation

To test the agent in simulation, run the [Bullet spine](https://upkie.github.io/upkie/spines.html#bullet-spine), then start the agent:

```console
./run_agent.sh
```

## Real robot

To run this agent on a real Upkie, you can use the Makefile at the root of the repository:

```console
$ make build
$ make upload
$ ssh your-upkie
user@your-upkie:~$ make run_mpc_balancer
```
