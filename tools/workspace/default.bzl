# -*- python -*-
#
# SPDX-License-Identifier: Apache-2.0

load("//tools/workspace/upkie:repository.bzl", "upkie_repository")

def add_default_repositories():
    """
    Declare workspace repositories for all dependencies.

    This function intended to be loaded and called from a WORKSPACE file.
    """
    upkie_repository()
