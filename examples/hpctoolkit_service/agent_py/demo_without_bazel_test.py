# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""Smoke test for examples/hpctoolkit_service/demo_without_bazel.py"""
from flaky import flaky
from hpctoolkit_service.demo_without_bazel import main
import pdb
pdb.set_trace()

@flaky
def test_demo_without_bazel():
    main()
