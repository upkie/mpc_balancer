# SPDX-License-Identifier: Apache-2.0

REMOTE = ${UPKIE_NAME}
PROJECT_NAME = mpc_balancer
CURDATE = $(shell date -Iseconds)

# Help snippet adapted from:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@echo "Available targets:\n"
	@grep -P '^[a-zA-Z0-9_-]+:.*? ## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-24s\033[0m %s\n", $$1, $$2}'
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

HOST_CONDA_PATH=~/.micromamba
REMOTE_CONDA_PATH=~/.micromamba
CONDA_ENV_NAME=raspios_$(PROJECT_NAME)

.PHONY: check_conda_env
check_conda_env:
	@command -v micromamba >/dev/null 2>&1 || { \
		echo "micromamba not found: conda rules only work for micromamba for now"; \
		exit 1; \
	}
	@command -v conda-pack >/dev/null 2>&1 || { \
		echo "conda-pack not installed: install it by 'conda install conda-forge::conda-pack'"; \
		exit 1; \
	}

clean:  ## clean up temporary files
	rm -f $(CONDA_ENV_NAME).tar.gz

$(CONDA_ENV_NAME).tar.gz:
	# conda env create -f environment.yaml -n $(CONDA_ENV_NAME) --platform linux-aarch64 -y
	# conda-pack -p $(HOST_CONDA_PATH)/envs/$(CONDA_ENV_NAME) -o $(CONDA_ENV_NAME).tar.gz
	tar -zcf "$(CONDA_ENV_NAME).tar.gz" -C $(HOST_CONDA_PATH)/envs/$(CONDA_ENV_NAME) "."
	# conda env remove -n $(CONDA_ENV_NAME) -y

.PHONY: pack_conda_env
pack_conda_env: check_conda_env $(CONDA_ENV_NAME).tar.gz  ## prepare conda environment to install it offline on your Upkie

.PHONY: unpack_conda_env
unpack_conda_env:  ### unpack conda environment to remote conda path
	micromamba env list | grep $(PROJECT_NAME) && micromamba env remove -n $(PROJECT_NAME) -y
	mkdir -p $(REMOTE_CONDA_PATH)/envs/$(PROJECT_NAME)
	tar -xzf raspios_$(PROJECT_NAME).tar.gz -C $(REMOTE_CONDA_PATH)/envs/$(PROJECT_NAME)
