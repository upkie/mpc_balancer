#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 Inria

import abc

import qpsolvers
from qpmpc import MPCQP


class Workspace(abc.ABC):
    @abc.abstractmethod
    def solve(self, mpc_qp: MPCQP) -> qpsolvers.Solution:
        """Solve a new QP, using warm-starting if possible.

        Args:
            mpc_qp: New model-predictive control QP.

        Returns:
            Results from solver.
        """
