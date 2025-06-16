# SPDX-License-Identifier: Apache-2.0

PROJECT_NAME = mpc_balancer

# Help snippet adapted from:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@echo "Host targets:\n"
	@grep -P '^[a-zA-Z0-9_-]+:.*? ## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-24s\033[0m %s\n", $$1, $$2}'
	@echo "\nRaspberry Pi targets:\n"
	@grep -P '^[a-zA-Z0-9_-]+:.*?### .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?### "}; {printf "    \033[36m%-24s\033[0m %s\n", $$1, $$2}'
	@echo ""  # manicure
.DEFAULT_GOAL := help

.PHONY: check_upkie_name
check_upkie_name:
	@if [ -z "${UPKIE_NAME}" ]; then \
		echo "ERROR: Environment variable UPKIE_NAME is not set.\n"; \
		echo "This variable should contain the robot's hostname or IP address for SSH. "; \
		echo "You can define it inline for a one-time use:\n"; \
		echo "    make some_target UPKIE_NAME=your_robot_hostname\n"; \
		echo "Or add the following line to your shell configuration:\n"; \
		echo "    export UPKIE_NAME=your_robot_hostname\n"; \
		exit 1; \
	fi

.PHONY: upload
upload: check_upkie_name  ## update a remote copy of the repository on the Raspberry Pi
	ssh ${UPKIE_NAME} mkdir -p $(PROJECT_NAME)
	rsync -Lrtu --delete-after --delete-excluded \
		--exclude __pycache__ \
		--exclude cache/ \
		--exclude .pixi/ \
		--progress $(CURDIR)/ ${UPKIE_NAME}:$(PROJECT_NAME)/

# ENVIRONMENT PACKING
# ===================

check_mamba_setup:
	@ if [ -z "${MAMBA_ROOT_PREFIX}" ]; then \
        echo "ERROR: Either MAMBA_EXE or MAMBA_ROOT_PREFIX is not set."; \
        echo "Is Micromamba installed?"; \
        echo "See https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html"; \
        exit 1; \
	fi

pack_env:  ## pack pixi environment to environment.tar
	pixi run pack-to-upkie

unpack_env: check_mamba_setup  ### unpack pixi environment from environment.tar
	pixi-pack unpack environment.tar -e $(PROJECT_NAME) -o ${MAMBA_ROOT_PREFIX}/envs
