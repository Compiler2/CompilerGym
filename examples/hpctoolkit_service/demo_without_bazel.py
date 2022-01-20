# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""This script demonstrates how the Python example service without needing
to use the bazel build system. Usage:

    $ python hpctoolkit_service/demo_without_bazel.py

It is equivalent in behavior to the demo.py script in this directory.
"""
import logging
import os
import pdb
import pickle
import subprocess
from pathlib import Path
from typing import Iterable

import gym
import hatchet as ht

from compiler_gym.datasets import Benchmark, Dataset
from compiler_gym.spaces import Reward
from compiler_gym.util.logging import init_logging
from compiler_gym.util.registration import register
from compiler_gym.util.runfiles_path import runfiles_path, site_data_path

reward_metric = "REALTIME (sec) (I)"  # "time (inc)"


HPCTOOLKIT_PY_SERVICE_BINARY: Path = Path(
    "hpctoolkit_service/service_py/example_service.py"
)
assert HPCTOOLKIT_PY_SERVICE_BINARY.is_file(), "Service script not found"

# BENCHMARKS_PATH: Path = runfiles_path("examples/hpctoolkit_service/benchmarks")
BENCHMARKS_PATH: Path = (
    "/home/dx4/tools/CompilerGym/examples/hpctoolkit_service/benchmarks/cpu-benchmarks"
)


class RuntimeReward(Reward):
    """An example reward that uses changes in the "runtime" observation value
    to compute incremental reward.
    """

    def __init__(self):
        super().__init__(
            id="runtime",
            observation_spaces=["runtime"],
            default_value=0,
            default_negates_returns=True,
            deterministic=False,
            platform_dependent=True,
        )
        self.baseline_runtime = 0

    def reset(self, benchmark: str, observation_view):
        print("Reward Runtime: reset")
        del benchmark  # unused
        self.baseline_runtime = observation_view["runtime"]

    def update(self, action, observations, observation_view):
        print("Reward Runtime: update")
        del action
        del observation_view
        return float(self.baseline_runtime - observations[0]) / self.baseline_runtime


class HPCToolkitReward(Reward):
    """An example reward that uses changes in the "runtime" observation value
    to compute incremental reward.
    """

    def __init__(self):
        super().__init__(
            id="hpctoolkit",
            observation_spaces=["hpctoolkit"],
            default_value=0,
            default_negates_returns=True,
            deterministic=False,
            platform_dependent=True,
        )
        self.baseline_cct = None
        self.baseline_runtime = 0

    def reset(self, benchmark: str, observation_view):
        print("Reward HPCToolkit: reset")
        # pdb.set_trace()
        del benchmark  # unused
        unpickled_cct = observation_view["hpctoolkit"]
        gf = pickle.loads(unpickled_cct)
        self.baseline_cct = gf
        self.baseline_runtime = gf.dataframe[reward_metric][0]

    def update(self, action, observations, observation_view):
        print("Reward HPCToolkit: update")
        # pdb.set_trace()
        del action
        del observation_view

        gf = pickle.loads(observations[0])
        new_runtime = gf.dataframe[reward_metric][0]
        return float(self.baseline_runtime - new_runtime) / self.baseline_runtime


class HPCToolkitDataset(Dataset):
    def __init__(self, *args, **kwargs):
        super().__init__(
            name="benchmark://hpctoolkit-cpu-v0",
            license="MIT",
            description="HPCToolkit cpu dataset",
            site_data_base=site_data_path("example_dataset"),
        )
        print(BENCHMARKS_PATH + "/offsets1.c")

        self._benchmarks = {
            "benchmark://hpctoolkit-cpu-v0/offsets1": Benchmark.from_file(
                "benchmark://hpctoolkit-cpu-v0/offsets1",
                BENCHMARKS_PATH + "/offsets1.c",
            ),
            "benchmark://hpctoolkit-cpu-v0/conv2d": Benchmark.from_file(
                "benchmark://hpctoolkit-cpu-v0/conv2d",
                BENCHMARKS_PATH + "/conv2d.c",
            ),
        }

    def benchmark_uris(self) -> Iterable[str]:
        yield from self._benchmarks.keys()

    def benchmark(self, uri: str) -> Benchmark:
        if uri in self._benchmarks:
            return self._benchmarks[uri]
        else:
            raise LookupError("Unknown program name")


# Register the environment for use with gym.make(...).
register(
    id="hpctoolkit-llvm-v0",
    entry_point="compiler_gym.envs:CompilerEnv",
    kwargs={
        "service": HPCTOOLKIT_PY_SERVICE_BINARY,
        "rewards": [RuntimeReward(), HPCToolkitReward()],
        "datasets": [HPCToolkitDataset()],
    },
)


def main():
    # Use debug verbosity to print out extra logging information.
    init_logging(level=logging.DEBUG)

    # Create the environment using the regular gym.make(...) interface.
    with gym.make("hpctoolkit-llvm-v0") as env:
        env.reset()
        for i in range(2):
            print("Main: step = ", i)
            observation, reward, done, info = env.step(
                action=env.action_space.sample(),
                observations=["hpctoolkit"],
                rewards=["hpctoolkit"],
            )
            print(reward)
            # print(observation)
            print(info)
            gf = pickle.loads(observation[0])
            print(gf.dataframe)
            print(gf.tree(metric_column=reward_metric))

            pdb.set_trace()
            if done:
                env.reset()


if __name__ == "__main__":
    main()
