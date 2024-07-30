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
set_date:
	ssh $(REMOTE) sudo date -s "$(CURDATE)"

.PHONY: upload
upload: check_upkie_name set_date  ## upload built targets to the Raspberry Pi
	ssh $(REMOTE) mkdir -p $(PROJECT_NAME)
	rsync -Lrtu --delete-after --delete-excluded \
		--exclude __pycache__ \
		--exclude cache/ \
		--progress $(CURDIR)/ $(REMOTE):$(PROJECT_NAME)/
