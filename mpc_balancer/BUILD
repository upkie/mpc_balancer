# -*- python -*-
#
# SPDX-License-Identifier: Apache-2.0

package(default_visibility = ["//visibility:public"])

filegroup(
    name = "config",
    srcs = glob(["*.gin"]),
)

py_binary(
    name = "mpc_balancer",
    srcs = ["main.py"],
    main = "main.py",

    # Enable `from X import y` rather than `from agents.agent_name.X import y`
    # so that the agent can be run indifferently via Python or Bazel.
    imports = ["."],

    data = [
        ":config",
    ],
    deps = [
        "@upkie//upkie/envs",
        "@upkie//upkie/observers/base_pitch",
        "@upkie//upkie/utils:clamp",
        "@upkie//upkie/utils:filters",
        "@upkie//upkie/utils:raspi",
        "@upkie//upkie/utils:spdlog",
    ],
)
