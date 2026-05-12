# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for Newton clone-plan helpers."""

import pytest
import torch
import warp as wp
from newton import Model, ModelBuilder
from isaaclab.physics.physics_manager import PhysicsManager
from isaaclab_newton.cloner.newton_replicate import (
    _bulk_add_homogeneous_worlds,
    _can_bulk_replicate_homogeneous,
    _is_homogeneous_clone_mapping,
    _load_visual_shapes_for_physics,
    _rename_builder_labels,
    _should_rename_builder_labels,
)
from isaaclab_newton.physics import NewtonManager


def _as_list(value):
    return value.tolist() if hasattr(value, "tolist") else value


@pytest.fixture(autouse=True)
def restore_clone_physics_only():
    prev = NewtonManager._clone_physics_only
    prev_sim = PhysicsManager._sim
    yield
    NewtonManager._clone_physics_only = prev
    PhysicsManager._sim = prev_sim


class _SceneDataRequirements:
    def __init__(self, requires_newton_model: bool):
        self.requires_newton_model = requires_newton_model


class _SimulationContextStub:
    def __init__(self, requires_newton_model: bool):
        self._requirements = _SceneDataRequirements(requires_newton_model)

    def get_scene_data_requirements(self):
        return self._requirements


def test_physics_only_skips_visual_shapes_without_scene_data_consumer(monkeypatch):
    monkeypatch.delenv("ISAACLAB_NEWTON_LOAD_VISUAL_SHAPES", raising=False)
    NewtonManager._clone_physics_only = True
    PhysicsManager._sim = _SimulationContextStub(requires_newton_model=False)

    assert not _load_visual_shapes_for_physics()


def test_visualizer_scene_data_consumer_loads_visual_shapes(monkeypatch):
    monkeypatch.delenv("ISAACLAB_NEWTON_LOAD_VISUAL_SHAPES", raising=False)
    NewtonManager._clone_physics_only = True
    PhysicsManager._sim = _SimulationContextStub(requires_newton_model=True)

    assert _load_visual_shapes_for_physics()


def test_visual_shape_env_override_takes_precedence(monkeypatch):
    monkeypatch.setenv("ISAACLAB_NEWTON_LOAD_VISUAL_SHAPES", "0")
    NewtonManager._clone_physics_only = False
    PhysicsManager._sim = _SimulationContextStub(requires_newton_model=True)

    assert not _load_visual_shapes_for_physics()


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


def test_bulk_homogeneous_worlds_match_add_builder_for_rigid_scene():
    proto = NewtonManager.create_builder()
    proto.add_custom_attribute(
        ModelBuilder.CustomAttribute(
            name="body_index",
            dtype=wp.int32,
            frequency=Model.AttributeFrequency.SHAPE,
            namespace="test",
            references="body",
        )
    )
    body = proto.add_body(xform=wp.transform((1.0, 2.0, 3.0), wp.quat_identity()), mass=1.0, label="body")
    proto.add_shape_box(body, hx=0.1, hy=0.2, hz=0.3, label="box", custom_attributes={"test:body_index": body})
    proto.add_shape_box(
        -1,
        xform=wp.transform((0.5, 0.0, 0.0), wp.quat_identity()),
        hx=0.4,
        label="root_box",
    )

    positions = torch.tensor([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [4.0, 1.0, 0.0]], dtype=torch.float32)

    loop_builder = NewtonManager.create_builder()
    for env_index in range(positions.shape[0]):
        loop_builder.begin_world()
        loop_builder.add_builder(
            proto,
            xform=wp.transform((positions[env_index] - positions[0]).tolist(), (0.0, 0.0, 0.0, 1.0)),
        )
        loop_builder.end_world()

    bulk_builder = NewtonManager.create_builder()
    site_map = _bulk_add_homogeneous_worlds(bulk_builder, proto, positions, {"site": [1]})

    assert bulk_builder.world_count == loop_builder.world_count
    assert _as_list(bulk_builder.body_world) == loop_builder.body_world
    assert _as_list(bulk_builder.shape_world) == loop_builder.shape_world
    assert _as_list(bulk_builder.joint_world) == loop_builder.joint_world
    assert _as_list(bulk_builder.shape_body) == loop_builder.shape_body
    assert _as_list(bulk_builder.joint_parent) == loop_builder.joint_parent
    assert _as_list(bulk_builder.joint_child) == loop_builder.joint_child
    assert _as_list(bulk_builder.joint_q) == loop_builder.joint_q
    assert list(bulk_builder.body_shapes.keys()) == list(loop_builder.body_shapes.keys())
    for body_idx, shapes in loop_builder.body_shapes.items():
        assert bulk_builder.body_shapes[body_idx] == shapes
        assert bulk_builder.body_shapes.get(body_idx) == shapes
    assert bulk_builder.body_shapes.get(999, []) == []
    assert bulk_builder.body_label == loop_builder.body_label
    assert bulk_builder.shape_label == loop_builder.shape_label
    assert _as_list(bulk_builder.shape_collision_group) == loop_builder.shape_collision_group
    assert bulk_builder.custom_attributes["test:body_index"].values == loop_builder.custom_attributes[
        "test:body_index"
    ].values
    assert site_map == {"site": [[1], [3], [5]]}

    loop_builder.finalize("cpu")
    bulk_builder.finalize("cpu")


def test_bulk_homogeneous_support_keeps_rotated_clones_on_existing_path():
    NewtonManager._clone_physics_only = True
    proto = NewtonManager.create_builder()
    proto.add_body(mass=1.0)
    rotated_quats = torch.tensor([[0.0, 0.0, 0.7071068, 0.7071068]], dtype=torch.float32)

    assert not _can_bulk_replicate_homogeneous(proto, rotated_quats)
