# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for Newton clone-plan helpers."""

import pytest
import torch
from isaaclab_newton.cloner.newton_replicate import (
    _is_homogeneous_clone_mapping,
    _rename_builder_labels,
    _should_rename_builder_labels,
)
from isaaclab_newton.physics import NewtonManager


@pytest.fixture(autouse=True)
def restore_clone_physics_only():
    prev = NewtonManager._clone_physics_only
    yield
    NewtonManager._clone_physics_only = prev


def test_homogeneous_mapping_skips_label_rename_in_physics_only():
    NewtonManager._clone_physics_only = True
    mapping = torch.ones((1, 4), dtype=torch.bool)

    assert _is_homogeneous_clone_mapping(("/World/envs/env_0",), ("/World/envs/env_{}",), mapping)
    assert not _should_rename_builder_labels(("/World/envs/env_0",), ("/World/envs/env_{}",), mapping)


def test_homogeneous_mapping_keeps_label_rename_when_usd_clones_exist():
    NewtonManager._clone_physics_only = False
    mapping = torch.ones((1, 4), dtype=torch.bool)

    assert _should_rename_builder_labels(("/World/envs/env_0",), ("/World/envs/env_{}",), mapping)


def test_heterogeneous_mapping_keeps_label_rename_in_physics_only():
    NewtonManager._clone_physics_only = True
    mapping = torch.tensor([[True, False, True, False], [False, True, False, True]])

    assert not _is_homogeneous_clone_mapping(
        ("/World/envs/env_0/RobotA", "/World/envs/env_1/RobotB"),
        ("/World/envs/env_{}/Robot", "/World/envs/env_{}/Robot"),
        mapping,
    )
    assert _should_rename_builder_labels(
        ("/World/envs/env_0/RobotA", "/World/envs/env_1/RobotB"),
        ("/World/envs/env_{}/Robot", "/World/envs/env_{}/Robot"),
        mapping,
    )


def test_heterogeneous_label_rename_preserves_destination_paths():
    class Builder:
        pass

    builder = Builder()
    builder.body_label = ["/World/envs/env_0/RobotA/base", "/World/envs/env_1/RobotB/base"]
    builder.joint_label = ["/World/envs/env_0/RobotA/joint", "/World/envs/env_1/RobotB/joint"]
    builder.shape_label = ["/World/envs/env_0/RobotA/shape", "/World/envs/env_1/RobotB/shape"]
    builder.articulation_label = ["/World/envs/env_0/RobotA", "/World/envs/env_1/RobotB"]
    builder.body_world = [0, 1]
    builder.joint_world = [0, 1]
    builder.shape_world = [0, 1]
    builder.articulation_world = [0, 1]

    _rename_builder_labels(
        builder,
        ("/World/envs/env_0/RobotA", "/World/envs/env_1/RobotB"),
        ("/World/envs/env_{}/Robot", "/World/envs/env_{}/Robot"),
        torch.tensor([0, 1]),
        torch.tensor([[True, False], [False, True]]),
    )

    assert builder.body_label == ["/World/envs/env_0/Robot/base", "/World/envs/env_1/Robot/base"]
    assert builder.joint_label == ["/World/envs/env_0/Robot/joint", "/World/envs/env_1/Robot/joint"]
    assert builder.shape_label == ["/World/envs/env_0/Robot/shape", "/World/envs/env_1/Robot/shape"]
    assert builder.articulation_label == ["/World/envs/env_0/Robot", "/World/envs/env_1/Robot"]
