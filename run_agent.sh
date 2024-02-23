#!/bin/bash

SCRIPT=$(realpath "$0")
SCRIPTDIR=$(dirname "${SCRIPT}")

${SCRIPTDIR}/tools/bazelisk run //mpc_balancer
