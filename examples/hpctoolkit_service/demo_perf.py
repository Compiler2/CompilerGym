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

from compiler_gym.datasets import Benchmark, BenchmarkUri, Dataset
from compiler_gym.envs.llvm.datasets import (
    AnghaBenchDataset,
    BlasDataset,
    CBenchDataset,
    CBenchLegacyDataset,
    CBenchLegacyDataset2,
    CHStoneDataset,
    CsmithDataset,
    NPBDataset,
)
from compiler_gym.envs.llvm.llvm_benchmark import get_system_includes
from compiler_gym.spaces import Reward
from compiler_gym.third_party import llvm
from compiler_gym.util.logging import init_logging
from compiler_gym.util.registration import register
from compiler_gym.util.runfiles_path import runfiles_path, site_data_path
from compiler_gym.service.connection import ServiceError
import utils


from agent_py.rewards import perf_reward
from agent_py.datasets import hpctoolkit_dataset

def register_env():
    register(
        id="perf-v0",
        entry_point="compiler_gym.envs:CompilerEnv",
        kwargs={
            "service": utils.HPCTOOLKIT_PY_SERVICE_BINARY,
            "rewards": [perf_reward.Reward()],
            "datasets": [
                hpctoolkit_dataset.Dataset(),
                CBenchDataset(site_data_path("llvm-v0")),
                CsmithDataset(site_data_path("llvm-v0"), sort_order=0),
                NPBDataset(site_data_path("llvm-v0"), sort_order=0),
                BlasDataset(site_data_path("llvm-v0"), sort_order=0),
                AnghaBenchDataset(site_data_path("llvm-v0"), sort_order=0),
                CHStoneDataset(site_data_path("llvm-v0"), sort_order=0),
            ],
        },
    )


def main():
    # Use debug verbosity to print out extra logging information.
    init_logging(level=logging.DEBUG)
    register_env()

    # Create the environment using the regular gym.make(...) interface.
    with gym.make("perf-v0") as env:

        # env.reset(benchmark="benchmark://cbench-v1/qsort")

        benchmark_to_process = [
            # from benchmarks directory
            "benchmark://hpctoolkit-cpu-v0/simple_pow",
            # "benchmark://hpctoolkit-cpu-v0/offsets1",
            "benchmark://hpctoolkit-cpu-v0/conv2d",
            # "benchmark://hpctoolkit-cpu-v0/nanosleep",
            # cbench-v1
            "benchmark://cbench-v1/bitcount",
            "benchmark://cbench-v1/qsort",
            "benchmark://cbench-v1/blowfish",
            "benchmark://cbench-v1/bzip2",
            "benchmark://cbench-v1/crc32",
            "benchmark://cbench-v1/dijkstra",
            # "benchmark://cbench-v1/gsm",                # FIXME: ValueError: 'utf-8' codec can't decode byte 0xcb in position 2: invalid continuation byte
            "benchmark://cbench-v1/jpeg-c",
            "benchmark://cbench-v1/jpeg-d",
            "benchmark://cbench-v1/patricia",
            "benchmark://cbench-v1/sha",
            "benchmark://cbench-v1/stringsearch",
            "benchmark://cbench-v1/susan",
            "benchmark://cbench-v1/tiff2bw",
            "benchmark://cbench-v1/tiff2rgba",
            "benchmark://cbench-v1/tiffdither",
            "benchmark://cbench-v1/tiffmedian",
            # csmith
            "generator://csmith-v0/0",
            "generator://csmith-v0/1",
            "generator://csmith-v0/2",
            # ...
            # The number represents the seed which needs to be less than or equal to UINT_MAX = (2 ** 32) - 1
            "generator://csmith-v0/23",
            "generator://csmith-v0/33",
            "generator://csmith-v0/1123",
            # ===========================
            # npb
            # "benchmark://npb-v0/3"
            # warning: overriding the module target triple with x86_64-unknown-linux-gnu [-Woverride-module]
            # 1 warning generated.
            # /usr/lib/gcc/x86_64-redhat-linux/8/../../../../lib64/crt1.o: In function `_start':
            # (.text+0x24): undefined reference to `main'
            # clang-12: error: linker command failed with exit code 1 (use -v to see invocation
            # ====================================
            #
            # ====================================
            # "benchmark://blas-v0/1",
            # blas
            # /usr/lib/gcc/x86_64-redhat-linux/8/../../../../lib64/crt1.o: In function `_start':
            # (.text+0x24): undefined reference to `main'
            # /tmp/benchmark-21b6f1.o: In function `dtbsv_':
            # /home/shoshijak/Documents/blas_ir/BLAS-3.8.0/dtbsv.f:230: undefined reference to `lsame_'
            # /home/shoshijak/Documents/blas_ir/BLAS-3.8.0/dtbsv.f:230: undefined reference to `lsame_'
            # /home/shoshijak/Documents/blas_ir/BLAS-3.8.0/dtbsv.f:232: undefined reference to `lsame_'
            # /home/shoshijak/Documents/blas_ir/BLAS-3.8.0/dtbsv.f:232: undefined reference to `lsame_'
            # /home/shoshijak/Documents/blas_ir/BLAS-3.8.0/dtbsv.f:232: undefined reference to `lsame_'
            # ====================================
            # ====================================
            # Maybe we could access to the .c code directly.
            # "benchmark://anghabench-v1/8cc/extr_buffer.c_buf_append"
            # /usr/lib/gcc/x86_64-redhat-linux/8/../../../../lib64/crt1.o: In function `_start':
            # (.text+0x24): undefined reference to `main'
            # /tmp/benchmark-downloaded-36dcc2.o: In function `buf_append':
            # extr_buffer.c_buf_append.c:(.text+0x3e): undefined reference to `buf_write'
            # ====================================
            # chstone seems to work (.c is present)
            "benchmark://chstone-v0/adpcm",
            "benchmark://chstone-v0/aes",
            "benchmark://chstone-v0/blowfish",
            "benchmark://chstone-v0/dfadd",
            "benchmark://chstone-v0/dfdiv",
            "benchmark://chstone-v0/dfmul",
            "benchmark://chstone-v0/dfsin",
            "benchmark://chstone-v0/gsm",
            "benchmark://chstone-v0/jpeg",
            "benchmark://chstone-v0/mips",
            "benchmark://chstone-v0/motion",
            "benchmark://chstone-v0/sha",
        ]

        inc = 0
        for bench in benchmark_to_process:
            try:
                env.reset(benchmark=bench)
            except ServiceError:
                print("AGENT: Timeout Error Reset")
            

            for i in range(2):
                print("Main: step = ", i)
                try:
                    observation, reward, done, info = env.step(
                        action=env.action_space.sample(),
                        observations=["perf"],
                        rewards=["perf"],
                    )
                except ServiceError:
                    print("AGENT: Timeout Error Step")
                    continue

                print(reward)
                # print(observation)
                print(info)
                perf_dict = pickle.loads(observation[0])
                print(perf_dict)

                pdb.set_trace()
                if done:
                    env.reset()
            inc += 1
        print("I run %d benchmarks." % inc)


if __name__ == "__main__":
    main()
