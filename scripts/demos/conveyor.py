# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Baggage-claim conveyor driven by the Newton MJWarp backend.

This demo ports Newton's ``basic_conveyor`` scene to Isaac Lab. A scripted
kinematic annular belt carries dynamic "bags" between two static rails, with a
Franka Panda arm mounted beside each conveyor. The belt pose is advanced at the
physics rate so its collision velocity remains consistent with the prescribed
tangential speed.

.. code-block:: bash

    # Interactive Newton visualization.
    ./isaaclab.sh -p scripts/demos/conveyor.py --visualizer newton

    # Ten tiled conveyor environments.
    ./isaaclab.sh -p scripts/demos/conveyor.py --visualizer newton --num-envs 10

    # Finite headless run with transport validation.
    ./isaaclab.sh -p scripts/demos/conveyor.py --visualizer none --max-steps 3000 --validate
"""

from __future__ import annotations

import argparse
import math
from collections.abc import Callable
from dataclasses import MISSING

import numpy as np
import torch

from isaaclab.app import add_launcher_args, launch_simulation

parser = argparse.ArgumentParser(description="Isaac Lab Newton baggage-claim conveyor demo.")
parser.add_argument("--belt-speed", type=float, default=0.75, help="Tangential belt speed [m/s].")
parser.add_argument("--num-envs", type=int, default=1, help="Number of tiled conveyor environments.")
parser.add_argument(
    "--max-steps",
    type=int,
    default=-1,
    help="Stop after this many physics steps; negative runs forever.",
)
parser.add_argument(
    "--validate",
    action="store_true",
    help="Check scene bounds and require bag transport in the commanded direction after a finite run.",
)
add_launcher_args(parser)
parser.set_defaults(visualizer=["newton"])
args_cli = parser.parse_args()


PHYSICS_DT = 0.001
RENDER_INTERVAL = 10
ENV_SPACING = 5.0

BELT_CENTER_Z = 0.55
BELT_RING_RADIUS = 1.8
BELT_HALF_WIDTH = 0.24
BELT_HALF_THICKNESS = 0.04
BELT_MESH_SEGMENTS = 96
BELT_MASS = 15.0

RAIL_WALL_THICKNESS = 0.035
RAIL_HEIGHT = 0.16
# Isaac Lab's scene-level collision filtering is PhysX-specific. Keep the
# static rails outside the belt's Newton contact envelope instead of spending
# MJWarp contact capacity on immovable belt-rail pairs.
RAIL_CLEARANCE = 0.015

FRANKA_BASE_POSITION = (-2.75, 0.0, 0.30)
FRANKA_MOUNT_HEIGHT = 0.30
FRANKA_MOUNT_RADIUS = 0.28

BAG_COUNT = 18
BAG_LANE_OFFSETS = (-0.12, 0.0, 0.12)
BAG_DROP_CLEARANCE = 0.035

MIN_TRANSPORT_VALIDATION_STEPS = 1500
MIN_TRANSPORT_FRACTION = 0.2

BELT_COLOR = (0.09, 0.09, 0.09)
RAIL_COLOR = (0.66, 0.69, 0.74)


def create_annular_prism_mesh(
    inner_radius: float,
    outer_radius: float,
    z_min: float,
    z_max: float,
    segments: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Create a closed annular prism as local-space vertices and triangular faces."""
    if segments < 3:
        raise ValueError("segments must be at least 3")
    if not 0.0 < inner_radius < outer_radius:
        raise ValueError("radii must satisfy 0 < inner_radius < outer_radius")
    if z_max <= z_min:
        raise ValueError("z_max must be greater than z_min")

    angles = np.linspace(0.0, 2.0 * math.pi, segments, endpoint=False, dtype=np.float32)
    unit_xy = np.column_stack((np.cos(angles), np.sin(angles))).astype(np.float32)

    def ring(radius: float, z: float) -> np.ndarray:
        return np.column_stack((radius * unit_xy, np.full(segments, z, dtype=np.float32)))

    # Vertex blocks: inner top, outer top, inner bottom, outer bottom.
    vertices = np.vstack(
        (
            ring(inner_radius, z_max),
            ring(outer_radius, z_max),
            ring(inner_radius, z_min),
            ring(outer_radius, z_min),
        )
    ).astype(np.float32)

    inner_top = np.arange(segments, dtype=np.int32)
    outer_top = inner_top + segments
    inner_bottom = inner_top + 2 * segments
    outer_bottom = inner_top + 3 * segments
    next_index = np.roll(np.arange(segments, dtype=np.int32), -1)

    faces: list[tuple[int, int, int]] = []
    for i, j in enumerate(next_index):
        # Top (+Z), bottom (-Z), outer (+radial), and inner (-radial).
        faces.extend(
            (
                (inner_top[i], outer_top[i], outer_top[j]),
                (inner_top[i], outer_top[j], inner_top[j]),
                (inner_bottom[i], inner_bottom[j], outer_bottom[j]),
                (inner_bottom[i], outer_bottom[j], outer_bottom[i]),
                (outer_bottom[i], outer_bottom[j], outer_top[j]),
                (outer_bottom[i], outer_top[j], outer_top[i]),
                (inner_bottom[i], inner_top[i], inner_top[j]),
                (inner_bottom[i], inner_top[j], inner_bottom[j]),
            )
        )

    return vertices, np.asarray(faces, dtype=np.int32)


def spawn_annular_mesh(
    prim_path: str,
    cfg,
    translation: tuple[float, float, float] | None = None,
    orientation: tuple[float, float, float, float] | None = None,
    **kwargs,
):
    """Spawn a demo-local annular triangle mesh with optional rigid-body properties."""
    from pxr import Gf, UsdGeom

    from isaaclab.sim import schemas
    from isaaclab.sim.spawners.materials import spawn_physics_material
    from isaaclab.sim.utils import bind_physics_material, create_prim, get_current_stage

    stage = get_current_stage()
    vertices = np.asarray(cfg.vertices, dtype=np.float32)
    faces = np.asarray(cfg.faces, dtype=np.int32)

    create_prim(prim_path, prim_type="Xform", translation=translation, orientation=orientation, stage=stage)
    geometry_path = f"{prim_path}/geometry"
    mesh_path = f"{geometry_path}/mesh"
    create_prim(geometry_path, prim_type="Xform", stage=stage)
    mesh_prim = create_prim(
        mesh_path,
        prim_type="Mesh",
        attributes={
            "points": vertices,
            "faceVertexIndices": faces.reshape(-1),
            "faceVertexCounts": np.full(faces.shape[0], 3, dtype=np.int32),
            "subdivisionScheme": "none",
        },
        stage=stage,
    )
    UsdGeom.Gprim(mesh_prim).CreateDisplayColorAttr().Set([Gf.Vec3f(*cfg.color)])

    if cfg.collision_props is not None:
        schemas.define_collision_properties(mesh_path, cfg.collision_props, stage=stage)
    if cfg.mesh_collision_props is not None:
        schemas.define_mesh_collision_properties(mesh_path, cfg.mesh_collision_props, stage=stage)
    if cfg.physics_material is not None:
        material_path = cfg.physics_material_path
        if not material_path.startswith("/"):
            material_path = f"{geometry_path}/{material_path}"
        spawn_physics_material(material_path, cfg.physics_material, stage=stage)
        bind_physics_material(mesh_path, material_path, stage=stage)
    if cfg.mass_props is not None:
        schemas.define_mass_properties(prim_path, cfg.mass_props, stage=stage)
    if cfg.rigid_props is not None:
        schemas.define_rigid_body_properties(prim_path, cfg.rigid_props, stage=stage)

    return stage.GetPrimAtPath(prim_path)


def create_visualizer_cfgs():
    """Create the Newton visualizer configuration requested on the command line."""
    if "newton" not in (args_cli.visualizer or []):
        return []

    from isaaclab_visualizers.newton import NewtonVisualizerCfg

    # Rendering is already throttled by ``RENDER_INTERVAL`` in the simulation
    # loop, so update the visualizer on every render call.
    return [NewtonVisualizerCfg(update_frequency=1)]


def create_sim_cfg():
    """Create a Newton MJWarp simulation config for exact annular mesh contacts."""
    from isaaclab_newton.physics import MJWarpSolverCfg, NewtonCfg

    import isaaclab.sim as sim_utils

    return sim_utils.SimulationCfg(
        dt=PHYSICS_DT,
        device=args_cli.device,
        gravity=(0.0, 0.0, -9.81),
        visualizer_cfgs=create_visualizer_cfgs(),
        physics=NewtonCfg(
            # MJWarp's internal collider treats triangle meshes as convex. Use
            # Newton's collision pipeline so the hollow annular meshes remain
            # hollow while MJWarp still advances the rigid-body dynamics.
            solver_cfg=MJWarpSolverCfg(
                use_mujoco_contacts=False,
                nconmax=512,
                njmax=4096,
            ),
            num_substeps=1,
            simplify_meshes=False,
        ),
    )


def _yaw_quaternion(angle: float) -> tuple[float, float, float, float]:
    """Return an XYZW quaternion for a rotation about +Z."""
    half_angle = 0.5 * angle
    return (0.0, 0.0, math.sin(half_angle), math.cos(half_angle))


def create_scene_cfg():
    """Create the conveyor, rails, Franka arms, and dynamic bag collection."""
    import isaaclab.sim as sim_utils
    from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg, RigidObjectCollectionCfg
    from isaaclab.scene import InteractiveSceneCfg
    from isaaclab.sim.utils import clone
    from isaaclab.utils.configclass import configclass

    from isaaclab_assets.robots.franka import FRANKA_PANDA_HIGH_PD_CFG

    if args_cli.num_envs < 1:
        raise ValueError("--num-envs must be at least 1")

    @configclass
    class AnnularMeshCfg(sim_utils.MeshCfg):
        """Demo-local arbitrary annular mesh asset configuration."""

        func: Callable | str = clone(spawn_annular_mesh)
        vertices: list[list[float]] = MISSING
        faces: list[list[int]] = MISSING
        color: tuple[float, float, float] = (0.5, 0.5, 0.5)
        mesh_collision_props: sim_utils.NewtonMeshCollisionPropertiesCfg | None = None

    belt_inner_radius = BELT_RING_RADIUS - BELT_HALF_WIDTH
    belt_outer_radius = BELT_RING_RADIUS + BELT_HALF_WIDTH
    belt_vertices, belt_faces = create_annular_prism_mesh(
        belt_inner_radius,
        belt_outer_radius,
        -BELT_HALF_THICKNESS,
        BELT_HALF_THICKNESS,
        BELT_MESH_SEGMENTS,
    )
    inner_rail_vertices, inner_rail_faces = create_annular_prism_mesh(
        belt_inner_radius - RAIL_CLEARANCE - RAIL_WALL_THICKNESS,
        belt_inner_radius - RAIL_CLEARANCE,
        BELT_HALF_THICKNESS + RAIL_CLEARANCE,
        BELT_HALF_THICKNESS + RAIL_CLEARANCE + RAIL_HEIGHT,
        BELT_MESH_SEGMENTS,
    )
    outer_rail_vertices, outer_rail_faces = create_annular_prism_mesh(
        belt_outer_radius + RAIL_CLEARANCE,
        belt_outer_radius + RAIL_CLEARANCE + RAIL_WALL_THICKNESS,
        BELT_HALF_THICKNESS + RAIL_CLEARANCE,
        BELT_HALF_THICKNESS + RAIL_CLEARANCE + RAIL_HEIGHT,
        BELT_MESH_SEGMENTS,
    )

    collision_props = sim_utils.NewtonCollisionPropertiesCfg(
        collision_enabled=True,
        contact_margin=0.002,
        contact_gap=0.005,
    )
    exact_mesh_props = sim_utils.NewtonMeshCollisionPropertiesCfg(mesh_approximation_name="none")

    belt_spawn = AnnularMeshCfg(
        vertices=belt_vertices.tolist(),
        faces=belt_faces.tolist(),
        color=BELT_COLOR,
        rigid_props=sim_utils.NewtonRigidBodyPropertiesCfg(
            rigid_body_enabled=True,
            kinematic_enabled=True,
            disable_gravity=True,
        ),
        mass_props=sim_utils.MassPropertiesCfg(mass=BELT_MASS),
        collision_props=collision_props,
        mesh_collision_props=exact_mesh_props,
        physics_material=sim_utils.NewtonMaterialPropertiesCfg(
            static_friction=1.2,
            dynamic_friction=1.2,
            restitution=0.0,
        ),
        physics_material_path="physicsMaterial",
    )

    rail_material = sim_utils.NewtonMaterialPropertiesCfg(
        static_friction=0.8,
        dynamic_friction=0.8,
        restitution=0.0,
    )

    def rail_spawn(vertices: np.ndarray, faces: np.ndarray) -> AnnularMeshCfg:
        return AnnularMeshCfg(
            vertices=vertices.tolist(),
            faces=faces.tolist(),
            color=RAIL_COLOR,
            collision_props=collision_props,
            mesh_collision_props=exact_mesh_props,
            physics_material=rail_material,
            physics_material_path="physicsMaterial",
        )

    bag_material = sim_utils.NewtonMaterialPropertiesCfg(
        static_friction=1.0,
        dynamic_friction=1.0,
        restitution=0.0,
    )
    bag_collision_props = sim_utils.NewtonCollisionPropertiesCfg(
        collision_enabled=True,
        contact_margin=0.002,
        contact_gap=0.005,
    )
    bag_angles = np.linspace(0.0, 2.0 * math.pi, BAG_COUNT, endpoint=False)
    bag_cfgs: dict[str, RigidObjectCfg] = {}
    franka_cfg = FRANKA_PANDA_HIGH_PD_CFG.copy().replace(
        prim_path="{ENV_REGEX_NS}/Franka",
        init_state=ArticulationCfg.InitialStateCfg(
            pos=FRANKA_BASE_POSITION,
            joint_pos={
                "panda_joint1": 0.0,
                "panda_joint2": -0.569,
                "panda_joint3": 0.0,
                "panda_joint4": -2.810,
                "panda_joint5": 0.0,
                "panda_joint6": 3.037,
                "panda_joint7": 0.741,
                "panda_finger_joint.*": 0.04,
            },
        ),
    )
    belt_top_z = BELT_CENTER_Z + BELT_HALF_THICKNESS
    grid_width = math.ceil(math.sqrt(args_cli.num_envs))
    ground_extent = ENV_SPACING * (grid_width + 1)

    for index, angle in enumerate(bag_angles):
        radius = BELT_RING_RADIUS + BAG_LANE_OFFSETS[index % len(BAG_LANE_OFFSETS)]
        bag_position_xy = (radius * math.cos(angle), radius * math.sin(angle))
        shape_type = index % 3

        if shape_type == 0:
            vertical_extent = 0.08
            spawn_cfg = sim_utils.CuboidCfg(
                size=(0.36, 0.24, 0.16),
                rigid_props=sim_utils.NewtonRigidBodyPropertiesCfg(rigid_body_enabled=True),
                mass_props=sim_utils.MassPropertiesCfg(mass=2.8 + 0.1 * index),
                collision_props=bag_collision_props,
                physics_material=bag_material,
                visual_material=None,
            )
        elif shape_type == 1:
            vertical_extent = 0.08
            spawn_cfg = sim_utils.CapsuleCfg(
                radius=0.08,
                height=0.30,
                axis="X",
                rigid_props=sim_utils.NewtonRigidBodyPropertiesCfg(rigid_body_enabled=True),
                mass_props=sim_utils.MassPropertiesCfg(mass=2.8 + 0.1 * index),
                collision_props=bag_collision_props,
                physics_material=bag_material,
                visual_material=None,
            )
        else:
            vertical_extent = 0.11
            spawn_cfg = sim_utils.SphereCfg(
                radius=0.11,
                rigid_props=sim_utils.NewtonRigidBodyPropertiesCfg(rigid_body_enabled=True),
                mass_props=sim_utils.MassPropertiesCfg(mass=2.8 + 0.1 * index),
                collision_props=bag_collision_props,
                physics_material=bag_material,
                visual_material=None,
            )

        bag_cfgs[f"bag_{index:02d}"] = RigidObjectCfg(
            prim_path=f"{{ENV_REGEX_NS}}/Bags/Bag_{index:02d}",
            spawn=spawn_cfg,
            init_state=RigidObjectCfg.InitialStateCfg(
                pos=(
                    bag_position_xy[0],
                    bag_position_xy[1],
                    belt_top_z + vertical_extent + BAG_DROP_CLEARANCE,
                ),
                rot=_yaw_quaternion(float(angle) + 0.5 * math.pi),
            ),
        )

    @configclass
    class ConveyorSceneCfg(InteractiveSceneCfg):
        """Scene containing one kinematic annular conveyor and dynamic bags."""

        ground = AssetBaseCfg(
            prim_path="/World/Ground",
            spawn=sim_utils.GroundPlaneCfg(
                size=(ground_extent, ground_extent),
                color=(0.24, 0.24, 0.24),
            ),
        )

        center_island = AssetBaseCfg(
            prim_path="{ENV_REGEX_NS}/CenterIsland",
            spawn=sim_utils.CylinderCfg(radius=0.9, height=0.16),
            init_state=AssetBaseCfg.InitialStateCfg(
                pos=(0.0, 0.0, BELT_CENTER_Z - BELT_HALF_THICKNESS - 0.08),
            ),
        )

        belt = RigidObjectCfg(
            prim_path="{ENV_REGEX_NS}/ConveyorBelt",
            spawn=belt_spawn,
            init_state=RigidObjectCfg.InitialStateCfg(pos=(0.0, 0.0, BELT_CENTER_Z)),
        )

        inner_rail = AssetBaseCfg(
            prim_path="{ENV_REGEX_NS}/ConveyorRailInner",
            spawn=rail_spawn(inner_rail_vertices, inner_rail_faces),
            init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, BELT_CENTER_Z)),
        )

        outer_rail = AssetBaseCfg(
            prim_path="{ENV_REGEX_NS}/ConveyorRailOuter",
            spawn=rail_spawn(outer_rail_vertices, outer_rail_faces),
            init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, BELT_CENTER_Z)),
        )

        franka_mount = AssetBaseCfg(
            prim_path="{ENV_REGEX_NS}/FrankaMount",
            spawn=sim_utils.CylinderCfg(
                radius=FRANKA_MOUNT_RADIUS,
                height=FRANKA_MOUNT_HEIGHT,
            ),
            init_state=AssetBaseCfg.InitialStateCfg(
                pos=(
                    FRANKA_BASE_POSITION[0],
                    FRANKA_BASE_POSITION[1],
                    0.5 * FRANKA_MOUNT_HEIGHT,
                ),
            ),
        )

        franka = franka_cfg

        bags = RigidObjectCollectionCfg(rigid_objects=bag_cfgs)

        dome_light = AssetBaseCfg(
            prim_path="/World/DomeLight",
            spawn=sim_utils.DomeLightCfg(intensity=2500.0, color=(0.78, 0.78, 0.78)),
        )

    return ConveyorSceneCfg(num_envs=args_cli.num_envs, env_spacing=ENV_SPACING, replicate_physics=True)


def keep_running(sim, step_count: int) -> bool:
    """Return whether another physics step should run."""
    if args_cli.max_steps >= 0 and step_count >= args_cli.max_steps:
        return False
    return sim.is_headless_or_exist_active_visualizer()


def write_belt_state(belt, env_origins: torch.Tensor, sim_time: float, angular_speed: float) -> None:
    """Write the prescribed belt pose and spatial velocity."""
    angle = angular_speed * sim_time
    pose = belt.data.default_root_pose.torch.clone()
    pose[:, :3] += env_origins
    pose[:, 3:7] = torch.tensor(_yaw_quaternion(angle), dtype=torch.float32, device=belt.device)
    velocity = torch.zeros((belt.num_instances, 6), dtype=torch.float32, device=belt.device)
    velocity[:, 5] = angular_speed
    belt.write_root_link_pose_to_sim_index(root_pose=pose)
    belt.write_root_link_velocity_to_sim_index(root_velocity=velocity)


def write_franka_home_state(franka) -> None:
    """Write and command the Franka joints at their configured home pose."""
    joint_pos = franka.data.default_joint_pos.torch.clone()
    joint_vel = franka.data.default_joint_vel.torch.clone()
    franka.write_joint_position_to_sim_index(position=joint_pos)
    franka.write_joint_velocity_to_sim_index(velocity=joint_vel)
    franka.set_joint_position_target_index(target=joint_pos)


def _bag_angles(scene) -> torch.Tensor:
    """Return each bag's polar angle around the conveyor center."""
    positions = scene["bags"].data.body_link_pos_w.torch[..., :2] - scene.env_origins[:, None, :2]
    return torch.atan2(positions[..., 1], positions[..., 0])


def validate_scene(scene, angular_travel: torch.Tensor, step_count: int) -> None:
    """Validate fixed belt height, finite bag poses, bounds, and tangential transport."""
    belt_z = scene["belt"].data.root_link_pos_w.torch[:, 2] - scene.env_origins[:, 2]
    max_belt_z_error = float((belt_z - BELT_CENTER_Z).abs().max().item())
    if max_belt_z_error >= 0.05:
        raise AssertionError(f"A belt drifted off the conveyor plane: max z error={max_belt_z_error:.4f}")

    bag_positions = scene["bags"].data.body_link_pos_w.torch - scene.env_origins[:, None, :]
    if not bool(torch.isfinite(bag_positions).all().item()):
        raise AssertionError("At least one bag has a non-finite position.")
    if not bool((bag_positions[:, 2] > -0.5).all().item()):
        lowest_z = float(bag_positions[:, 2].min().item())
        raise AssertionError(f"At least one bag fell through the floor: lowest z={lowest_z:.4f}")
    if not bool((bag_positions[:, :2].abs() < 4.0).all().item()):
        max_xy = float(bag_positions[:, :2].abs().max().item())
        raise AssertionError(f"At least one bag left the scene bounds: max |xy|={max_xy:.4f}")

    median_travel = float(torch.median(angular_travel).item())
    travel_direction = 1.0 if args_cli.belt_speed >= 0.0 else -1.0
    directed_median_travel = travel_direction * median_travel
    commanded_angular_travel = abs(args_cli.belt_speed) * step_count * PHYSICS_DT / BELT_RING_RADIUS
    if args_cli.validate:
        if step_count < MIN_TRANSPORT_VALIDATION_STEPS:
            raise AssertionError(
                f"Transport validation requires at least {MIN_TRANSPORT_VALIDATION_STEPS} steps; received {step_count}."
            )
        if commanded_angular_travel == 0.0:
            raise AssertionError("Transport validation requires a non-zero --belt-speed.")
        required_travel = MIN_TRANSPORT_FRACTION * commanded_angular_travel
        if directed_median_travel <= required_travel:
            raise AssertionError(
                "Bags did not move in the commanded belt direction: "
                f"directed median travel={directed_median_travel:.4f} rad, "
                f"expected > {required_travel:.4f} rad "
                f"({MIN_TRANSPORT_FRACTION:.0%} of the commanded travel)."
            )

    check_name = "transport validation" if args_cli.validate else "scene checks"
    print(
        f"[INFO]: Conveyor {check_name} passed: "
        f"{scene.num_envs} envs, {step_count} steps, max belt z error={max_belt_z_error:.3g} m, "
        f"median bag travel={median_travel:.3f} rad.",
        flush=True,
    )


def run_simulator(sim, scene) -> None:
    """Run the scripted conveyor simulation loop."""
    belt = scene["belt"]
    franka = scene["franka"]
    angular_speed = args_cli.belt_speed / BELT_RING_RADIUS
    write_franka_home_state(franka)
    previous_angles = _bag_angles(scene)
    angular_travel = torch.zeros_like(previous_angles)
    step_count = 0

    while keep_running(sim, step_count):
        write_belt_state(belt, scene.env_origins, step_count * PHYSICS_DT, angular_speed)
        franka.set_joint_position_target_index(target=franka.data.default_joint_pos.torch)
        scene.write_data_to_sim()
        sim.step(render=False)
        scene.update(PHYSICS_DT)

        current_angles = _bag_angles(scene)
        angle_difference = current_angles - previous_angles
        angle_delta = torch.atan2(torch.sin(angle_difference), torch.cos(angle_difference))
        angular_travel += angle_delta
        previous_angles = current_angles

        step_count += 1
        if sim.is_rendering and step_count % RENDER_INTERVAL == 0:
            sim.render()

    validate_scene(scene, angular_travel, step_count)


def main() -> None:
    """Launch and run the Isaac Lab Newton conveyor demo."""
    sim_cfg = create_sim_cfg()
    with launch_simulation(sim_cfg, args_cli):
        import isaaclab.sim as sim_utils
        from isaaclab.scene import InteractiveScene

        sim = sim_utils.SimulationContext(sim_cfg)
        scene = InteractiveScene(create_scene_cfg())
        sim.reset()
        scene_center = scene.env_origins.mean(dim=0).cpu()
        camera_span = ENV_SPACING * math.ceil(math.sqrt(scene.num_envs))
        sim.set_camera_view(
            eye=(
                float(scene_center[0] + 0.7 * camera_span),
                float(scene_center[1] - 0.9 * camera_span),
                max(4.2, 0.8 * camera_span),
            ),
            target=(float(scene_center[0]), float(scene_center[1]), BELT_CENTER_Z),
        )

        print(
            "[INFO]: Isaac Lab Newton conveyor ready. "
            f"Spawned {scene.num_envs} environments with {BAG_COUNT} bags and one Franka arm each; "
            f"belt speed={args_cli.belt_speed:.3f} m/s.",
            flush=True,
        )
        run_simulator(sim, scene)


if __name__ == "__main__":
    main()
