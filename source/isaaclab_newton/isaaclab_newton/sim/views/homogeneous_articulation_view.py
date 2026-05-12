# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Fast Newton articulation view construction for homogeneous clone layouts."""

from __future__ import annotations

import fnmatch

import numpy as np
import warp as wp
from newton import JointType, Model
from newton.selection import ArticulationView
from newton._src.utils.selection import (  # noqa: PLC2701
    AttributeFrequency,
    FrequencyLayout,
    get_name_from_label,
    match_labels,
    set_model_articulation_mask_per_world_kernel,
)


def create_articulation_view(
    model: Model,
    pattern: str,
    include_joints: list[str] | list[int] | None = None,
    exclude_joints: list[str] | list[int] | None = None,
    include_links: list[str] | list[int] | None = None,
    exclude_links: list[str] | list[int] | None = None,
    include_joint_types: list[int] | None = None,
    exclude_joint_types: list[int] | None = None,
    verbose: bool | None = None,
) -> ArticulationView:
    """Create a Newton ``ArticulationView``, using a homogeneous shortcut when possible."""

    view = _try_create_homogeneous_articulation_view(
        model,
        pattern,
        include_joints=include_joints,
        exclude_joints=exclude_joints,
        include_links=include_links,
        exclude_links=exclude_links,
        include_joint_types=include_joint_types,
        exclude_joint_types=exclude_joint_types,
    )
    if view is not None:
        return view

    return ArticulationView(
        model,
        pattern,
        include_joints=include_joints,
        exclude_joints=exclude_joints,
        include_links=include_links,
        exclude_links=exclude_links,
        include_joint_types=include_joint_types,
        exclude_joint_types=exclude_joint_types,
        verbose=verbose,
    )


def _try_create_homogeneous_articulation_view(
    model: Model,
    pattern: str,
    *,
    include_joints: list[str] | list[int] | None,
    exclude_joints: list[str] | list[int] | None,
    include_links: list[str] | list[int] | None,
    exclude_links: list[str] | list[int] | None,
    include_joint_types: list[int] | None,
    exclude_joint_types: list[int] | None,
) -> ArticulationView | None:
    homogeneous_info = getattr(model, "_isaaclab_newton_homogeneous_clone", None)
    if homogeneous_info is None:
        return None

    # Keep the shortcut conservative. The generic Newton view still handles
    # multi-articulation selections, tendons, globals, and heterogeneous layouts.
    start_articulation_idx = homogeneous_info["start_articulation_idx"]
    proto_articulation_count = homogeneous_info["articulation_count"]
    num_worlds = homogeneous_info["num_worlds"]
    if proto_articulation_count <= 0 or num_worlds <= 0:
        return None

    local_articulation_labels = model.articulation_label[
        start_articulation_idx : start_articulation_idx + proto_articulation_count
    ]
    local_matches = [idx for idx, label in enumerate(local_articulation_labels) if fnmatch.fnmatch(label, pattern)]
    if len(local_matches) != 1:
        return None

    mujoco_attrs = getattr(model, "mujoco", None)
    tendon_world = getattr(mujoco_attrs, "tendon_world", None) if mujoco_attrs is not None else None
    if tendon_world is not None and tendon_world.shape[0] > 0:
        return None

    local_articulation_idx = local_matches[0]
    articulation_id = start_articulation_idx + local_articulation_idx

    model_articulation_start = model.articulation_start.numpy()
    model_joint_type = model.joint_type.numpy()
    model_joint_child = model.joint_child.numpy()
    model_joint_q_start = model.joint_q_start.numpy()
    model_joint_qd_start = model.joint_qd_start.numpy()

    joint_begin = int(model_articulation_start[articulation_id])
    joint_end = int(model_articulation_start[articulation_id + 1])
    arti_joint_count = joint_end - joint_begin
    if arti_joint_count <= 0:
        return None

    joint_ids = list(range(joint_begin, joint_end))
    joint_names = [get_name_from_label(model.joint_label[joint_id]) for joint_id in joint_ids]
    joint_types = [int(model_joint_type[joint_id]) for joint_id in joint_ids]

    link_ids = sorted(int(model_joint_child[joint_id]) for joint_id in joint_ids)
    link_names = [get_name_from_label(model.body_label[link_id]) for link_id in link_ids]

    shape_ids: list[int] = []
    for link_id in link_ids:
        shape_ids.extend(model.body_shapes[link_id])
    shape_ids = sorted(shape_ids)
    shape_names = [get_name_from_label(model.shape_label[shape_id]) for shape_id in shape_ids]

    joint_dof_begin = int(model_joint_qd_start[joint_begin])
    joint_dof_end = int(model_joint_qd_start[joint_end])
    joint_coord_begin = int(model_joint_q_start[joint_begin])
    joint_coord_end = int(model_joint_q_start[joint_end])
    joint_dof_count = joint_dof_end - joint_dof_begin
    joint_coord_count = joint_coord_end - joint_coord_begin

    if include_joints is None and include_joint_types is None:
        joint_include_indices = set(range(arti_joint_count))
    else:
        joint_include_indices = set()
        if include_joints is not None:
            joint_include_indices.update(
                idx for idx in match_labels(joint_names, include_joints) if 0 <= idx < arti_joint_count
            )
        if include_joint_types is not None:
            joint_include_indices.update(
                idx for idx, joint_type in enumerate(joint_types) if joint_type in include_joint_types
            )

    joint_exclude_indices = set()
    if exclude_joints is not None:
        joint_exclude_indices.update(
            idx for idx in match_labels(joint_names, exclude_joints) if 0 <= idx < arti_joint_count
        )
    if exclude_joint_types is not None:
        joint_exclude_indices.update(
            idx for idx, joint_type in enumerate(joint_types) if joint_type in exclude_joint_types
        )

    if include_links is None:
        link_include_indices = set(range(len(link_ids)))
    else:
        link_include_indices = {idx for idx in match_labels(link_names, include_links) if 0 <= idx < len(link_ids)}

    link_exclude_indices = set()
    if exclude_links is not None:
        link_exclude_indices.update(idx for idx in match_labels(link_names, exclude_links) if 0 <= idx < len(link_ids))

    selected_joint_indices = sorted(joint_include_indices - joint_exclude_indices)
    selected_link_indices = sorted(link_include_indices - link_exclude_indices)

    selected_joint_dof_indices: list[int] = []
    selected_joint_coord_indices: list[int] = []
    selected_joint_names: list[str] = []
    selected_joint_dof_names: list[str] = []
    selected_joint_coord_names: list[str] = []
    selected_joint_dof_counts: list[int] = []
    selected_joint_coord_counts: list[int] = []

    for joint_idx in selected_joint_indices:
        joint_id = joint_ids[joint_idx]
        joint_name = joint_names[joint_idx]
        selected_joint_names.append(joint_name)

        dof_begin = int(model_joint_qd_start[joint_id])
        dof_end = int(model_joint_qd_start[joint_id + 1])
        dof_count = dof_end - dof_begin
        selected_joint_dof_counts.append(dof_count)
        if dof_count == 1:
            selected_joint_dof_names.append(joint_name)
            selected_joint_dof_indices.append(dof_begin - joint_dof_begin)
        elif dof_count > 1:
            for dof in range(dof_count):
                selected_joint_dof_names.append(f"{joint_name}:{dof}")
                selected_joint_dof_indices.append(dof_begin + dof - joint_dof_begin)

        coord_begin = int(model_joint_q_start[joint_id])
        coord_end = int(model_joint_q_start[joint_id + 1])
        coord_count = coord_end - coord_begin
        selected_joint_coord_counts.append(coord_count)
        if coord_count == 1:
            selected_joint_coord_names.append(joint_name)
            selected_joint_coord_indices.append(coord_begin - joint_coord_begin)
        elif coord_count > 1:
            for coord in range(coord_count):
                selected_joint_coord_names.append(f"{joint_name}:{coord}")
                selected_joint_coord_indices.append(coord_begin + coord - joint_coord_begin)

    selected_link_names: list[str] = []
    selected_shape_indices: list[int] = []
    selected_shape_names: list[str] = []
    selected_link_shapes: list[list[int]] = []
    shape_id_to_local = {shape_id: shape_idx for shape_idx, shape_id in enumerate(shape_ids)}
    shape_link_idx: dict[int, int] = {}

    for selected_link_idx, link_idx in enumerate(selected_link_indices):
        body_id = link_ids[link_idx]
        selected_link_names.append(link_names[link_idx])
        selected_link_shapes.append([])
        for shape_id in model.body_shapes[body_id]:
            local_shape_idx = shape_id_to_local[shape_id]
            selected_shape_indices.append(local_shape_idx)
            shape_link_idx[local_shape_idx] = selected_link_idx

    selected_shape_indices = sorted(selected_shape_indices)
    for shape_idx, local_shape_idx in enumerate(selected_shape_indices):
        selected_shape_names.append(shape_names[local_shape_idx])
        selected_link_shapes[shape_link_idx[local_shape_idx]].append(shape_idx)

    body_stride = homogeneous_info["body_count"]
    shape_stride = homogeneous_info["shape_count"]
    joint_stride = homogeneous_info["joint_count"]
    joint_dof_stride = homogeneous_info["joint_dof_count"]
    joint_coord_stride = homogeneous_info["joint_coord_count"]
    articulation_stride = homogeneous_info["articulation_count"]

    link_offset = link_ids[0] if link_ids else 0
    shape_offset = min(shape_ids) if shape_ids else 0

    view = ArticulationView.__new__(ArticulationView)
    view.model = model
    view.device = model.device
    view.root_joint_type = joint_types[0]
    view.is_fixed_base = view.root_joint_type == JointType.FIXED
    view.is_floating_base = view.root_joint_type in (JointType.FREE, JointType.DISTANCE)

    view.joint_names = selected_joint_names
    view.joint_dof_names = selected_joint_dof_names
    view.joint_dof_counts = selected_joint_dof_counts
    view.joint_coord_names = selected_joint_coord_names
    view.joint_coord_counts = selected_joint_coord_counts
    view.link_names = selected_link_names
    view.link_shapes = selected_link_shapes
    view.shape_names = selected_shape_names

    view.count = num_worlds
    view.world_count = num_worlds
    view.count_per_world = 1
    view.joint_count = len(selected_joint_indices)
    view.joint_dof_count = len(selected_joint_dof_indices)
    view.joint_coord_count = len(selected_joint_coord_indices)
    view.link_count = len(selected_link_indices)
    view.shape_count = len(selected_shape_indices)

    view.frequency_layouts = {
        AttributeFrequency.JOINT: FrequencyLayout(
            joint_begin,
            joint_stride,
            arti_joint_count,
            arti_joint_count,
            selected_joint_indices,
            view.device,
        ),
        AttributeFrequency.JOINT_DOF: FrequencyLayout(
            joint_dof_begin,
            joint_dof_stride,
            joint_dof_count,
            joint_dof_count,
            selected_joint_dof_indices,
            view.device,
        ),
        AttributeFrequency.JOINT_COORD: FrequencyLayout(
            joint_coord_begin,
            joint_coord_stride,
            joint_coord_count,
            joint_coord_count,
            selected_joint_coord_indices,
            view.device,
        ),
        AttributeFrequency.BODY: FrequencyLayout(
            link_offset,
            body_stride,
            len(link_ids),
            len(link_ids),
            selected_link_indices,
            view.device,
        ),
        AttributeFrequency.SHAPE: FrequencyLayout(
            shape_offset,
            shape_stride,
            len(shape_ids),
            len(shape_ids),
            selected_shape_indices,
            view.device,
        ),
    }

    view.tendon_count = 0
    view.tendon_names = []

    view.joints_contiguous = view.frequency_layouts[AttributeFrequency.JOINT].is_contiguous
    view.joint_dofs_contiguous = view.frequency_layouts[AttributeFrequency.JOINT_DOF].is_contiguous
    view.joint_coords_contiguous = view.frequency_layouts[AttributeFrequency.JOINT_COORD].is_contiguous
    view.links_contiguous = view.frequency_layouts[AttributeFrequency.BODY].is_contiguous
    view.shapes_contiguous = view.frequency_layouts[AttributeFrequency.SHAPE].is_contiguous

    articulation_ids = (
        start_articulation_idx
        + np.arange(num_worlds, dtype=np.int32)[:, None] * articulation_stride
        + np.asarray([[local_articulation_idx]], dtype=np.int32)
    )
    view.articulation_ids = wp.array(articulation_ids, dtype=int, device=view.device)
    view.full_mask = wp.full(num_worlds, True, dtype=bool, device=view.device)
    view.articulation_mask = wp.zeros(model.articulation_count, dtype=bool, device=view.device)
    wp.launch(
        set_model_articulation_mask_per_world_kernel,
        dim=view.articulation_ids.shape,
        inputs=[view.full_mask, view.articulation_ids, view.articulation_mask],
        device=view.device,
    )

    return view
