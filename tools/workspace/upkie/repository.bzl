# -*- python -*-
#
# SPDX-License-Identifier: Apache-2.0

load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

def upkie_repository():
    """
    Clone repository from GitHub and make its targets available for binding.
    """
    git_repository(
        name = "upkie",
        remote = "https://github.com/upkie/upkie.git",
        commit = "2803a685559a4400be18950ab3cacc5c51501fc9",
        shallow_since = "1708703026 +0100",
    )
