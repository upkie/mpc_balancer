# -*- python -*-
#
# SPDX-License-Identifier: Apache-2.0

workspace(name = "new_agent")  # XXX: rename

# Add default repositories listed in tools/workspace/
load("//tools/workspace:default.bzl", "add_default_repositories")
add_default_repositories()

# @upkie was added by add_default_repositories
load("@upkie//tools/workspace:default.bzl", add_upkie_repositories = "add_default_repositories")
add_upkie_repositories()

# @vulp was added by add_default_repositories
load("@vulp//tools/workspace:default.bzl", add_vulp_repositories = "add_default_repositories")
add_vulp_repositories()

# @palimpsest was added by add_vulp_repositories
load("@palimpsest//tools/workspace:default.bzl", add_palimpsest_repositories = "add_default_repositories")
add_palimpsest_repositories()

# @pi3hat was added by add_vulp_repositories
load("@pi3hat//tools/workspace:default.bzl", add_pi3hat_repositories = "add_default_repositories")
add_pi3hat_repositories()

# @rpi_bazel was added by add_pi3hat_repositories
load("@rpi_bazel//tools/workspace:default.bzl", add_rpi_bazel_repositories = "add_default_repositories")
add_rpi_bazel_repositories()
