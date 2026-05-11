# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import Any

import torch
import warp as wp
from newton import JointType, Model, ModelBuilder, solvers
from newton._src.usd.schemas import SchemaResolverNewton, SchemaResolverPhysx

from pxr import Usd

from isaaclab_newton.physics import NewtonManager


def _is_homogeneous_clone_mapping(sources: Sequence[str], destinations: Sequence[str], mapping: torch.Tensor) -> bool:
    """Return whether *mapping* represents one source cloned into every environment."""
    return (
        len(sources) == 1
        and len(destinations) == 1
        and mapping.ndim == 2
        and mapping.shape[0] == 1
        and bool(mapping.all().item())
    )


_BULK_REPEATED_ATTRS = (
    "body_inertia",
    "body_mass",
    "body_inv_inertia",
    "body_inv_mass",
    "body_com",
    "body_lock_inertia",
    "body_flags",
    "body_qd",
    "joint_type",
    "joint_enabled",
    "joint_collision_filter_parent",
    "joint_X_c",
    "joint_armature",
    "joint_axis",
    "joint_dof_dim",
    "joint_qd",
    "joint_cts",
    "joint_f",
    "joint_act",
    "joint_target_pos",
    "joint_target_vel",
    "joint_limit_lower",
    "joint_limit_upper",
    "joint_limit_ke",
    "joint_limit_kd",
    "joint_target_ke",
    "joint_target_kd",
    "joint_target_mode",
    "joint_effort_limit",
    "joint_velocity_limit",
    "joint_friction",
    "shape_flags",
    "shape_type",
    "shape_scale",
    "shape_source",
    "shape_color",
    "shape_is_solid",
    "shape_margin",
    "shape_material_ke",
    "shape_material_kd",
    "shape_material_kf",
    "shape_material_ka",
    "shape_material_mu",
    "shape_material_restitution",
    "shape_material_mu_torsional",
    "shape_material_mu_rolling",
    "shape_material_kh",
    "shape_collision_radius",
    "shape_gap",
    "shape_sdf_narrow_band_range",
    "shape_sdf_max_resolution",
    "shape_sdf_target_voxel_size",
    "shape_sdf_texture_format",
    "particle_qd",
    "particle_mass",
    "particle_radius",
    "particle_flags",
    "edge_rest_angle",
    "edge_rest_length",
    "edge_bending_properties",
    "spring_rest_length",
    "spring_stiffness",
    "spring_damping",
    "spring_control",
    "tri_poses",
    "tri_activations",
    "tri_materials",
    "tri_areas",
    "tet_poses",
    "tet_activations",
    "tet_materials",
)

_BUILTIN_FREQUENCY_KEYS = {
    Model.AttributeFrequency.BODY: "body",
    Model.AttributeFrequency.SHAPE: "shape",
    Model.AttributeFrequency.JOINT: "joint",
    Model.AttributeFrequency.JOINT_DOF: "joint_dof",
    Model.AttributeFrequency.JOINT_COORD: "joint_coord",
    Model.AttributeFrequency.JOINT_CONSTRAINT: "joint_constraint",
    Model.AttributeFrequency.ARTICULATION: "articulation",
    Model.AttributeFrequency.EQUALITY_CONSTRAINT: "equality_constraint",
    Model.AttributeFrequency.CONSTRAINT_MIMIC: "constraint_mimic",
    Model.AttributeFrequency.PARTICLE: "particle",
    Model.AttributeFrequency.EDGE: "edge",
    Model.AttributeFrequency.TRIANGLE: "triangle",
    Model.AttributeFrequency.TETRAHEDRON: "tetrahedron",
    Model.AttributeFrequency.SPRING: "spring",
}


def _has_identity_quaternions(quaternions: torch.Tensor) -> bool:
    """Return whether clone orientations are all identity quaternions."""
    if quaternions.numel() == 0:
        return True
    identity = torch.zeros_like(quaternions)
    identity[:, 3] = 1.0
    return bool(torch.allclose(quaternions, identity))


def _translated_transform(transform: wp.transform, delta: Sequence[float]) -> wp.transform:
    """Return *transform* translated by *delta* without changing orientation."""
    return wp.transform(
        transform[0] + float(delta[0]),
        transform[1] + float(delta[1]),
        transform[2] + float(delta[2]),
        transform[3],
        transform[4],
        transform[5],
        transform[6],
    )


def _offset_index(value: int, offset: int) -> int:
    """Offset non-negative indices while preserving Newton's negative sentinels."""
    return value + offset if value >= 0 else value


def _transform_index_value(value: Any, offset: int) -> Any:
    """Apply an add_builder-style index offset to a custom attribute value."""
    if offset == 0:
        return value
    if isinstance(value, int):
        return _offset_index(value, offset)
    if isinstance(value, (list, tuple)):
        transformed = [_offset_index(v, offset) if isinstance(v, int) else v for v in value]
        return type(value)(transformed)
    try:
        return value + offset
    except TypeError:
        return value


def _custom_attribute_defaults_match(lhs: Any, rhs: Any) -> bool:
    """Return whether two custom attribute defaults compare equal."""
    try:
        defaults_match = lhs == rhs
        if hasattr(defaults_match, "__iter__") and not isinstance(defaults_match, (str, bytes)):
            defaults_match = all(defaults_match)
        return bool(defaults_match)
    except (ValueError, TypeError):
        return False


def _can_bulk_replicate_homogeneous(proto: ModelBuilder, quaternions: torch.Tensor) -> bool:
    """Return whether the prototype is covered by the bulk homogeneous path."""
    if not getattr(NewtonManager, "_clone_physics_only", False):
        return False
    if not _has_identity_quaternions(quaternions):
        return False

    # The first prototype targets rigid/articulation scenes, which covers the high-env
    # headless workloads under investigation. Deformables and explicit constraints keep
    # using Newton's regular add_builder path until their offset rules are bulk-tested.
    unsupported_counts = (
        proto.particle_count,
        proto.spring_count,
        proto.edge_count,
        proto.tri_count,
        proto.tet_count,
        len(proto.equality_constraint_type),
        len(proto.constraint_mimic_joint0),
    )
    return not any(unsupported_counts)


def _bulk_replicate_custom_attributes(
    builder: ModelBuilder,
    proto: ModelBuilder,
    num_worlds: int,
    start_world_idx: int,
    entity_offsets: dict[str, int],
    entity_counts: dict[str, int],
    custom_frequency_offsets: dict[str, int],
) -> None:
    """Merge custom attributes from *proto* as homogeneous per-world blocks."""

    def get_offset(entity_or_key: str | None, env_index: int) -> int:
        if entity_or_key is None:
            return 0
        if entity_or_key in entity_offsets:
            return entity_offsets[entity_or_key] + env_index * entity_counts[entity_or_key]
        if entity_or_key in custom_frequency_offsets:
            return custom_frequency_offsets[entity_or_key] + env_index * proto._custom_frequency_counts.get(
                entity_or_key, 0
            )
        if entity_or_key in proto._custom_frequency_counts:
            return env_index * proto._custom_frequency_counts[entity_or_key]
        raise ValueError(
            f"Unknown references value '{entity_or_key}'. "
            f"Valid values are: {list(entity_offsets.keys())} or custom frequencies."
        )

    def transform_value(attr: ModelBuilder.CustomAttribute, value: Any, env_index: int) -> Any:
        if attr.references == "world":
            return start_world_idx + env_index
        return _transform_index_value(value, get_offset(attr.references, env_index))

    for full_key, attr in proto.custom_attributes.items():
        if not attr.values:
            if full_key not in builder.custom_attributes:
                freq_key = attr.frequency
                builder.custom_attributes[full_key] = replace(
                    attr,
                    values=[] if isinstance(freq_key, str) else {},
                )
            continue

        freq_key = attr.frequency
        merged = builder.custom_attributes.get(full_key)
        if merged is not None and not _custom_attribute_defaults_match(merged.default, attr.default):
            raise ValueError(
                f"Custom attribute '{full_key}' default mismatch when merging builders: "
                f"existing={merged.default}, incoming={attr.default}"
            )

        if isinstance(freq_key, str):
            mapped_values = [
                transform_value(attr, value, env_index)
                for env_index in range(num_worlds)
                for value in attr.values
            ]
            if merged is None:
                builder.custom_attributes[full_key] = replace(attr, values=mapped_values)
            else:
                if merged.values is None:
                    merged.values = []
                merged.values.extend(mapped_values)
            continue

        mapped_values: dict[int, Any] = {}
        for env_index in range(num_worlds):
            if freq_key == Model.AttributeFrequency.ONCE:
                index_offset = 0
            elif freq_key == Model.AttributeFrequency.WORLD:
                index_offset = start_world_idx + env_index
            else:
                entity_key = _BUILTIN_FREQUENCY_KEYS[freq_key]
                index_offset = entity_offsets[entity_key] + env_index * entity_counts[entity_key]
            for idx, value in attr.values.items():
                mapped_values[index_offset + idx] = transform_value(attr, value, env_index)

        if merged is None:
            builder.custom_attributes[full_key] = replace(attr, values=mapped_values)
        else:
            if merged.values is None:
                merged.values = {}
            merged.values.update(mapped_values)

    for freq_key, freq_obj in proto.custom_frequencies.items():
        if freq_key not in builder.custom_frequencies:
            builder.custom_frequencies[freq_key] = freq_obj

    for freq_key, proto_count in proto._custom_frequency_counts.items():
        builder._custom_frequency_counts[freq_key] = custom_frequency_offsets.get(freq_key, 0) + (
            proto_count * num_worlds
        )


def _bulk_replicate_actuators(
    builder: ModelBuilder,
    proto: ModelBuilder,
    num_worlds: int,
    start_joint_dof_idx: int,
    start_joint_coord_idx: int,
) -> None:
    """Merge actuator entries from *proto* as homogeneous per-world blocks."""
    for entry_key, sub_entry in proto.actuator_entries.items():
        entry = builder.actuator_entries.setdefault(
            entry_key,
            ModelBuilder.ActuatorEntry(
                controller_class=sub_entry.controller_class,
                clamping_classes=sub_entry.clamping_classes,
                clamping_shared_kwargs=sub_entry.clamping_shared_kwargs,
                controller_shared_kwargs=sub_entry.controller_shared_kwargs,
                indices=[],
                pos_indices=[],
                controller_args=[],
                delay_args=[],
                clamping_args=[],
            ),
        )
        for env_index in range(num_worlds):
            dof_offset = start_joint_dof_idx + env_index * proto.joint_dof_count
            coord_offset = start_joint_coord_idx + env_index * proto.joint_coord_count
            entry.indices.extend(idx + dof_offset for idx in sub_entry.indices)
            entry.pos_indices.extend(idx + coord_offset for idx in sub_entry.pos_indices)
            entry.controller_args.extend(sub_entry.controller_args)
            entry.delay_args.extend(sub_entry.delay_args)
            entry.clamping_args.extend(sub_entry.clamping_args)


def _bulk_add_homogeneous_worlds(
    builder: ModelBuilder,
    proto: ModelBuilder,
    positions: torch.Tensor,
    proto_sites: dict[str, list[int]],
) -> dict[str, list[list[int]]]:
    """Add one rigid/articulation prototype to every world using bulk list operations."""
    num_worlds = positions.size(0)
    env0_pos = positions[0]
    deltas = (positions - env0_pos).detach().cpu().tolist()

    if builder.current_world != -1:
        raise RuntimeError("Bulk Newton replication requires the destination builder to be in global scope.")
    if proto.up_axis != builder.up_axis:
        raise ValueError("Cannot add a builder with a different up axis.")

    start_world_idx = builder.world_count
    start_body_idx = builder.body_count
    start_shape_idx = builder.shape_count
    start_joint_idx = builder.joint_count
    start_joint_dof_idx = builder.joint_dof_count
    start_joint_coord_idx = builder.joint_coord_count
    start_joint_constraint_idx = builder.joint_constraint_count
    start_articulation_idx = builder.articulation_count
    start_equality_constraint_idx = len(builder.equality_constraint_type)
    start_constraint_mimic_idx = len(builder.constraint_mimic_joint0)
    start_particle_idx = builder.particle_count
    start_edge_idx = builder.edge_count
    start_triangle_idx = builder.tri_count
    start_tetrahedron_idx = builder.tet_count
    start_spring_idx = builder.spring_count
    custom_frequency_offsets = dict(builder._custom_frequency_counts)

    builder._requested_contact_attributes.update(proto._requested_contact_attributes)
    builder._requested_state_attributes.update(proto._requested_state_attributes)

    proto_up = proto.up_vector
    world_gravity = (proto_up[0] * proto.gravity, proto_up[1] * proto.gravity, proto_up[2] * proto.gravity)
    builder.world_count += num_worlds
    builder.world_gravity.extend([world_gravity] * num_worlds)

    for env_index, delta in enumerate(deltas):
        body_base = start_body_idx + env_index * proto.body_count
        shape_base = start_shape_idx + env_index * proto.shape_count
        joint_base = start_joint_idx + env_index * proto.joint_count
        coord_base = start_joint_coord_idx + env_index * proto.joint_coord_count
        dof_base = start_joint_dof_idx + env_index * proto.joint_dof_count
        cts_base = start_joint_constraint_idx + env_index * proto.joint_constraint_count
        articulation_base = start_articulation_idx + env_index * proto.articulation_count

        for shape_idx, body_idx in enumerate(proto.shape_body):
            if body_idx > -1:
                builder.shape_body.append(body_idx + body_base)
                builder.shape_transform.append(proto.shape_transform[shape_idx])
            else:
                builder.shape_body.append(-1)
                builder.shape_transform.append(_translated_transform(proto.shape_transform[shape_idx], delta))

        for body_idx, shapes in proto.body_shapes.items():
            translated_shapes = [shape_base + shape_idx for shape_idx in shapes]
            if body_idx == -1:
                builder.body_shapes[-1].extend(translated_shapes)
            else:
                builder.body_shapes[body_base + body_idx] = translated_shapes

        if proto.joint_count:
            joint_X_p = list(proto.joint_X_p)
            joint_q = list(proto.joint_q)
            for joint_idx, joint_type in enumerate(proto.joint_type):
                if int(joint_type) == int(JointType.FREE):
                    q_start = proto.joint_q_start[joint_idx]
                    joint_q[q_start] += float(delta[0])
                    joint_q[q_start + 1] += float(delta[1])
                    joint_q[q_start + 2] += float(delta[2])
                elif proto.joint_parent[joint_idx] == -1:
                    joint_X_p[joint_idx] = _translated_transform(proto.joint_X_p[joint_idx], delta)

            builder.joint_X_p.extend(joint_X_p)
            builder.joint_q.extend(joint_q)
            builder.articulation_start.extend(joint_base + start for start in proto.articulation_start)

            new_parents = [_offset_index(parent, body_base) for parent in proto.joint_parent]
            new_children = [child + body_base for child in proto.joint_child]
            builder.joint_parent.extend(new_parents)
            builder.joint_child.extend(new_children)
            for local_joint_idx, (parent, child) in enumerate(zip(new_parents, new_children, strict=True)):
                new_joint_idx = joint_base + local_joint_idx
                builder.joint_parents.setdefault(child, []).append((parent, new_joint_idx))
                builder.joint_children.setdefault(parent, []).append((child, new_joint_idx))

            builder.joint_q_start.extend(coord_base + start for start in proto.joint_q_start)
            builder.joint_qd_start.extend(dof_base + start for start in proto.joint_qd_start)
            builder.joint_cts_start.extend(cts_base + start for start in proto.joint_cts_start)
            builder.joint_articulation.extend(
                _offset_index(articulation, articulation_base) for articulation in proto.joint_articulation
            )

        builder.body_q.extend(_translated_transform(body_q, delta) for body_q in proto.body_q)
        builder.shape_collision_group.extend(proto.shape_collision_group)
        builder.shape_collision_filter_pairs.extend(
            (shape_base + shape_a, shape_base + shape_b) for shape_a, shape_b in proto.shape_collision_filter_pairs
        )

    for world_idx in range(start_world_idx, start_world_idx + num_worlds):
        builder.body_world.extend([world_idx] * proto.body_count)
        builder.shape_world.extend([world_idx] * proto.shape_count)
        builder.joint_world.extend([world_idx] * proto.joint_count)
        builder.articulation_world.extend([world_idx] * proto.articulation_count)

    for label_attr in ("articulation_label", "body_label", "joint_label", "shape_label"):
        getattr(builder, label_attr).extend(getattr(proto, label_attr) * num_worlds)

    for attr in _BULK_REPEATED_ATTRS:
        getattr(builder, attr).extend(getattr(proto, attr) * num_worlds)

    builder.joint_dof_count += proto.joint_dof_count * num_worlds
    builder.joint_coord_count += proto.joint_coord_count * num_worlds
    builder.joint_constraint_count += proto.joint_constraint_count * num_worlds

    entity_offsets = {
        "body": start_body_idx,
        "shape": start_shape_idx,
        "joint": start_joint_idx,
        "joint_dof": start_joint_dof_idx,
        "joint_coord": start_joint_coord_idx,
        "joint_constraint": start_joint_constraint_idx,
        "articulation": start_articulation_idx,
        "equality_constraint": start_equality_constraint_idx,
        "constraint_mimic": start_constraint_mimic_idx,
        "particle": start_particle_idx,
        "edge": start_edge_idx,
        "triangle": start_triangle_idx,
        "tetrahedron": start_tetrahedron_idx,
        "spring": start_spring_idx,
    }
    entity_counts = {
        "body": proto.body_count,
        "shape": proto.shape_count,
        "joint": proto.joint_count,
        "joint_dof": proto.joint_dof_count,
        "joint_coord": proto.joint_coord_count,
        "joint_constraint": proto.joint_constraint_count,
        "articulation": proto.articulation_count,
        "equality_constraint": len(proto.equality_constraint_type),
        "constraint_mimic": len(proto.constraint_mimic_joint0),
        "particle": proto.particle_count,
        "edge": proto.edge_count,
        "triangle": proto.tri_count,
        "tetrahedron": proto.tet_count,
        "spring": proto.spring_count,
    }
    _bulk_replicate_custom_attributes(
        builder,
        proto,
        num_worlds,
        start_world_idx,
        entity_offsets,
        entity_counts,
        custom_frequency_offsets,
    )
    _bulk_replicate_actuators(builder, proto, num_worlds, start_joint_dof_idx, start_joint_coord_idx)

    return {
        label: [
            [start_shape_idx + env_index * proto.shape_count + shape_idx for shape_idx in shape_indices]
            for env_index in range(num_worlds)
        ]
        for label, shape_indices in proto_sites.items()
    }


def _build_newton_builder_from_mapping(
    stage: Usd.Stage,
    sources: Sequence[str],
    env_ids: torch.Tensor,
    mapping: torch.Tensor,
    positions: torch.Tensor | None = None,
    quaternions: torch.Tensor | None = None,
    up_axis: str = "Z",
    simplify_meshes: bool = True,
) -> tuple[ModelBuilder, object, dict]:
    """Build a Newton model builder from clone mapping inputs.

    Args:
        stage: USD stage containing source assets.
        sources: Source prim paths used for cloning.
        env_ids: Environment ids for destination worlds.
        mapping: Boolean source-to-environment mapping matrix.
        positions: Optional per-environment world positions.
        quaternions: Optional per-environment orientations in xyzw order.
        up_axis: Up axis for the Newton model builder.
        simplify_meshes: Whether to run convex-hull mesh approximation.

    Returns:
        Tuple of the populated Newton model builder, stage metadata returned
        by ``add_usd``, and a site index map for
        :attr:`NewtonManager._cl_site_index_map`.
    """
    if positions is None:
        positions = torch.zeros((mapping.size(1), 3), device=mapping.device, dtype=torch.float32)
    if quaternions is None:
        quaternions = torch.zeros((mapping.size(1), 4), device=mapping.device, dtype=torch.float32)
        quaternions[:, 3] = 1.0

    schema_resolvers = [SchemaResolverNewton(), SchemaResolverPhysx()]

    builder = NewtonManager.create_builder(up_axis=up_axis)
    stage_info = builder.add_usd(
        stage,
        ignore_paths=["/World/envs", *sources],
        schema_resolvers=schema_resolvers,
    )

    # The prototype is built from env_0 in absolute world coordinates.
    # add_builder xforms are deltas from env_0 so positions don't get double-counted.
    env0_pos = positions[0]
    protos: dict[str, ModelBuilder] = {}
    for src_path in sources:
        p = NewtonManager.create_builder(up_axis=up_axis)
        solvers.SolverMuJoCo.register_custom_attributes(p)
        p.add_usd(
            stage,
            root_path=src_path,
            load_visual_shapes=True,
            skip_mesh_approximation=True,
            schema_resolvers=schema_resolvers,
        )
        if simplify_meshes:
            p.approximate_meshes("convex_hull", keep_visual_shapes=True)
        protos[src_path] = p

    # Inject registered sites into prototypes (and global sites into main builder)
    global_sites, proto_sites = NewtonManager._cl_inject_sites(builder, protos)

    # Global sites: (int, None)
    global_site_map: dict[str, tuple[int, None]] = {label: (idx, None) for label, idx in global_sites.items()}

    # Local sites: per-world sublists, populated in the loop below
    num_worlds = mapping.size(1)
    local_site_map: dict[str, list[list[int]]] = {}

    homogeneous_mapping = len(sources) == 1 and _is_homogeneous_clone_mapping(sources, sources, mapping)
    if homogeneous_mapping and _can_bulk_replicate_homogeneous(protos[sources[0]], quaternions):
        proto = protos[sources[0]]
        local_site_map = _bulk_add_homogeneous_worlds(builder, proto, positions, proto_sites.get(id(proto), {}))
    else:
        # create a separate world for each environment (heterogeneous spawning)
        # Newton assigns sequential world IDs (0, 1, 2, ...), so we need to track the mapping
        for col, _ in enumerate(env_ids.tolist()):
            # begin a new world context (Newton assigns world ID = col)
            builder.begin_world()
            # add all active sources for this world
            delta_pos = (positions[col] - env0_pos).tolist()
            for row in torch.nonzero(mapping[:, col], as_tuple=True)[0].tolist():
                proto = protos[sources[row]]
                offset = builder.shape_count
                builder.add_builder(
                    proto,
                    xform=wp.transform(delta_pos, quaternions[col].tolist()),
                )
                # Compute final shape indices for sites in this proto
                for label, proto_shape_indices in proto_sites.get(id(proto), {}).items():
                    if label not in local_site_map:
                        local_site_map[label] = [[] for _ in range(num_worlds)]
                    for proto_shape_idx in proto_shape_indices:
                        local_site_map[label][col].append(offset + proto_shape_idx)
            # end the world context
            builder.end_world()

    site_index_map = {
        **global_site_map,
        **{label: (None, per_world) for label, per_world in local_site_map.items()},
    }

    return builder, stage_info, site_index_map


def _should_rename_builder_labels(sources: Sequence[str], destinations: Sequence[str], mapping: torch.Tensor) -> bool:
    """Return whether expanded Newton labels need env-specific USD paths.

    In headless Newton physics-only runs, homogeneous env-root scenes do not author
    cloned USD asset specs.  Newton selections can operate on duplicated env_0
    labels because pattern matching returns every repeated label index and the
    model's world arrays still separate environments.  Keeping compact labels
    avoids another O(num_envs * labels_per_env) pass over the expanded builder.

    Heterogeneous scenes keep unique labels because different source rows may
    populate different envs and downstream tooling can inspect destination paths.
    """
    return not (
        getattr(NewtonManager, "_clone_physics_only", False)
        and _is_homogeneous_clone_mapping(sources, destinations, mapping)
    )


def _rename_builder_labels(
    builder: ModelBuilder,
    sources: Sequence[str],
    destinations: Sequence[str],
    env_ids: torch.Tensor,
    mapping: torch.Tensor,
) -> None:
    """Rename builder labels/keys from source roots to destination roots.

    Args:
        builder: Newton model builder to update in-place.
        sources: Source prim root paths.
        destinations: Destination prim path templates.
        env_ids: Environment ids corresponding to mapping columns.
        mapping: Boolean source-to-environment mapping matrix.
    """
    # per-source, per-world renaming (strict prefix swap), compact style preserved
    for i, src_path in enumerate(sources):
        src_prefix_len = len(src_path.rstrip("/"))
        swap = lambda name, new_root: new_root + name[src_prefix_len:]  # noqa: E731
        world_cols = torch.nonzero(mapping[i], as_tuple=True)[0].tolist()
        # Map Newton world IDs (sequential) to destination paths using env_ids
        world_roots = {int(env_ids[c]): destinations[i].format(int(env_ids[c])) for c in world_cols}

        for t in ("body", "joint", "shape", "articulation"):
            labels = getattr(builder, f"{t}_label", None)
            if labels is None:
                labels = getattr(builder, f"{t}_key")
            worlds_arr = getattr(builder, f"{t}_world")
            for k, w in enumerate(worlds_arr):
                world_id = int(w)
                if world_id in world_roots and labels[k].startswith(src_path):
                    labels[k] = swap(labels[k], world_roots[world_id])


def newton_physics_replicate(
    stage: Usd.Stage,
    sources: Sequence[str],
    destinations: Sequence[str],
    env_ids: torch.Tensor,
    mapping: torch.Tensor,
    positions: torch.Tensor | None = None,
    quaternions: torch.Tensor | None = None,
    device: str = "cpu",
    up_axis: str = "Z",
    simplify_meshes: bool = True,
):
    """Replicate prims into a Newton ``ModelBuilder`` using a per-source mapping.

    Args:
        stage: USD stage containing source assets.
        sources: Source prim paths used for cloning.
        destinations: Destination prim path templates.
        env_ids: Environment ids for destination worlds.
        mapping: Boolean source-to-environment mapping matrix.
        positions: Optional per-environment world positions.
        quaternions: Optional per-environment orientations in xyzw order.
        device: Device used by the finalized Newton model builder.
        up_axis: Up axis for the Newton model builder.
        simplify_meshes: Whether to run convex-hull mesh approximation.

    Returns:
        Tuple of the populated Newton model builder and stage metadata.
    """
    builder, stage_info, site_index_map = _build_newton_builder_from_mapping(
        stage=stage,
        sources=sources,
        env_ids=env_ids,
        mapping=mapping,
        positions=positions,
        quaternions=quaternions,
        up_axis=up_axis,
        simplify_meshes=simplify_meshes,
    )
    if _should_rename_builder_labels(sources, destinations, mapping):
        _rename_builder_labels(builder, sources, destinations, env_ids, mapping)
    NewtonManager._cl_site_index_map = site_index_map
    NewtonManager.set_builder(builder)
    NewtonManager._num_envs = mapping.size(1)
    return builder, stage_info


def newton_visualizer_prebuild(
    stage: Usd.Stage,
    sources: Sequence[str],
    destinations: Sequence[str],
    env_ids: torch.Tensor,
    mapping: torch.Tensor,
    positions: torch.Tensor | None = None,
    quaternions: torch.Tensor | None = None,
    device: str = "cpu",
    up_axis: str = "Z",
    simplify_meshes: bool = True,
):
    """Replicate a clone plan into a finalized Newton model/state for visualization.

    Unlike :func:`newton_physics_replicate`, this path does not mutate ``NewtonManager`` and is intended
    for prebuilding visualizer-only artifacts that can be consumed by scene data providers.

    Args:
        stage: USD stage containing source assets.
        sources: Source prim paths used for cloning.
        destinations: Destination prim path templates.
        env_ids: Environment ids for destination worlds.
        mapping: Boolean source-to-environment mapping matrix.
        positions: Optional per-environment world positions.
        quaternions: Optional per-environment orientations in xyzw order.
        device: Device used by the finalized Newton model.
        up_axis: Up axis for the Newton model builder.
        simplify_meshes: Whether to run convex-hull mesh approximation.

    Returns:
        Tuple of finalized Newton model and state.
    """
    builder, _, _site_index_map = _build_newton_builder_from_mapping(
        stage=stage,
        sources=sources,
        env_ids=env_ids,
        mapping=mapping,
        positions=positions,
        quaternions=quaternions,
        up_axis=up_axis,
        simplify_meshes=simplify_meshes,
    )
    if _should_rename_builder_labels(sources, destinations, mapping):
        _rename_builder_labels(builder, sources, destinations, env_ids, mapping)
    model = builder.finalize(device=device)
    state = model.state()
    return model, state
