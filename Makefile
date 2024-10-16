# SPDX-License-Identifier: Apache-2.0

PROJECT_NAME = mpc_balancer

CURDATE = $(shell date -Iseconds)
CONDA_ENV_FILE = conda_env.tar.gz

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

clean:  ## clean up temporary files
	rm -f $(CONDA_ENV_FILE)

# This rule is handy if the target Upkie is not connected to the Internet
.PHONY: set_date
set_date:  check_upkie_name
	ssh ${UPKIE_NAME} sudo date -s "$(CURDATE)"

.PHONY: upload
upload: check_upkie_name set_date  ## update a remote copy of the repository on the Raspberry Pi
	ssh ${UPKIE_NAME} mkdir -p $(PROJECT_NAME)
	rsync -Lrtu --delete-after --delete-excluded \
		--exclude __pycache__ \
		--exclude cache/ \
		--progress $(CURDIR)/ ${UPKIE_NAME}:$(PROJECT_NAME)/

# Packing and unpacking conda environment for an offline Upkie
# ============================================================

.PHONY: check_mamba_setup
check_mamba_setup:
	@ if [ -z "${MAMBA_EXE}" ] || [ -z "${MAMBA_ROOT_PREFIX}" ]; then \
		echo "ERROR: Either MAMBA_EXE or MAMBA_ROOT_PREFIX is not set."; \
		echo "Is Micromamba installed?"; \
		echo "See https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html"; \
		exit 1; \
	fi

.PHONY: pack_conda_env
pack_conda_env: check_mamba_setup  ## prepare conda environment to install it offline on your Upkie
	${MAMBA_EXE} env create -f environment.yaml -n raspios_$(PROJECT_NAME) --platform linux-aarch64 -y
	tar -zcf $(CONDA_ENV_FILE) -C ${MAMBA_ROOT_PREFIX}/envs/raspios_$(PROJECT_NAME) .
	${MAMBA_EXE} env remove -n raspios_$(PROJECT_NAME) -y

.PHONY: check_mamba_setup unpack_conda_env
unpack_conda_env:  ### unpack conda environment to remote conda path
	-${MAMBA_EXE} env list | grep $(PROJECT_NAME) > /dev/null && ${MAMBA_EXE} env remove -n $(PROJECT_NAME) -y
	mkdir -p ${MAMBA_ROOT_PREFIX}/envs/$(PROJECT_NAME)
	tar -zxf $(CONDA_ENV_FILE) -C ${MAMBA_ROOT_PREFIX}/envs/$(PROJECT_NAME)
