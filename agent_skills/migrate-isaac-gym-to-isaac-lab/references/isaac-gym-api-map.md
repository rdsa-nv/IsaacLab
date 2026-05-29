<!--
Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause
-->

# Isaac Gym To Isaac Lab API Map

Use this as a migration checklist after reading the user's source and the current Isaac Lab checkout.

## Config

| Isaac Gym or IsaacGymEnvs | Isaac Lab develop |
| --- | --- |
| task YAML | Python `@configclass` |
| `sim.dt` | `SimulationCfg(dt=...)` |
| `sim.substeps` | Usually fold into `SimulationCfg(dt=...)` plus task `decimation` |
| `controlFrequencyInv` | `decimation` |
| `env.numEnvs` | `InteractiveSceneCfg(num_envs=...)` |
| `env.envSpacing` | `InteractiveSceneCfg(env_spacing=...)` |
| max episode length in steps | `episode_length_s = dt * decimation * steps` |
| `clipObservations`, `clipActions` | RL library config, not task config |
| global PhysX actor properties | Per-asset `RigidBodyPropertiesCfg`, `ArticulationRootPropertiesCfg`, and actuator configs |
| requested Newton backend | `NewtonCfg(solver_cfg=MJWarpSolverCfg(...))`, usually behind a `PresetCfg` field named `newton_mjwarp` |

## Scene And Assets

| Old pattern | New pattern |
| --- | --- |
| `create_sim(...)` | Let Isaac Lab create simulation context |
| `_create_ground_plane()` | `spawn_ground_plane(...)` or `TerrainImporterCfg` |
| `gym.load_asset(...)` | `ArticulationCfg` or `RigidObjectCfg` with `UsdFileCfg`, `UrdfFileCfg`, or other spawner cfg |
| `gym.create_env(...)` loop | Build one source env, then `scene.clone_environments(...)` |
| `gym.create_actor(...)` | Instantiate `Articulation(self.cfg.robot_cfg)` or `RigidObject(self.cfg.object_cfg)` |
| actor handles and rigid body handles | Named scene assets and `find_joints` / `find_bodies` |
| `ArticulationView`, `RigidPrimView` | `Articulation`, `RigidObject`, and their `.data` buffers |

Use prim paths with the environment regex, for example:

```python
robot_cfg = ROBOT_CFG.replace(prim_path="/World/envs/env_.*/Robot")
```

For URDF/MJCF assets, validate conversion separately from the environment. Isaac Gym `AssetOptions` fields such as `collapse_fixed_joints`, `replace_cylinder_with_capsule`, `flip_visual_attachments`, `fix_base_link`, default drive mode, density, damping, and armature may not map one-to-one onto the active Isaac Lab converter plus Isaac Sim importer. MJCF imports may also require `isaacsim.asset.importer.mjcf` to be enabled. If a converter option is source-faithful but unsupported in the current runtime, record it as a behavior gap and consider pre-converting the asset to USD with the matching importer/runtime before finishing the task port.

## Runtime Methods

| IsaacGymEnvs | OmniIsaacGymEnvs | DirectRLEnv |
| --- | --- | --- |
| `create_sim` | `set_up_scene` | `_setup_scene` |
| `pre_physics_step(actions)` | `pre_physics_step(actions)` | `_pre_physics_step(actions)` and `_apply_action()` |
| `compute_observations` | `get_observations` | `_get_observations() -> {"policy": obs}` |
| `compute_reward` | `calculate_metrics` | `_get_rewards() -> reward` |
| `reset_idx(env_ids)` | `reset_idx(env_ids)` | `_reset_idx(env_ids)` |
| custom done/reset buffers | `is_done` | `_get_dones() -> (terminated, time_out)` |
| `post_physics_step` | `post_reset` | Usually base class flow plus `__init__` or `_reset_idx` |

For ManagerBasedRLEnv, map the same old methods into config sections instead of environment overrides:

| Old pattern | Manager-based target |
| --- | --- |
| `pre_physics_step(actions)` | `ActionsCfg` term, usually `JointEffortActionCfg`, `JointPositionActionCfg`, or a custom `ActionTerm` |
| `compute_observations` | ordered `ObservationTermCfg`s inside `ObservationsCfg.PolicyCfg` |
| `compute_reward` | one or more `RewardTermCfg`s; use `ManagerTermBase` for stateful terms |
| `reset_idx` and randomization | reset/interval `EventTermCfg`s |
| `reset_buf` failure logic | `TerminationTermCfg` entries |
| episode length reset | `TerminationTermCfg(func=time_out, time_out=True)` |

## Tensor And State APIs

| Isaac Gym Preview | Isaac Lab develop |
| --- | --- |
| `acquire_dof_state_tensor`, `refresh_dof_state_tensor` | `robot.data.joint_pos.torch`, `robot.data.joint_vel.torch` |
| `acquire_actor_root_state_tensor` | `asset.data.root_pos_w.torch`, `asset.data.root_quat_w.torch`, root velocity fields |
| `gymtorch.wrap_tensor` / `unwrap_tensor` | Native tensor buffers exposed by assets |
| `set_dof_state_tensor_indexed` | `write_joint_position_to_sim_index`, `write_joint_velocity_to_sim_index`, or `write_joint_state_to_sim` if available in the current checkout |
| `set_actor_root_state_tensor_indexed` | `write_root_pose_to_sim_index`, `write_root_velocity_to_sim_index` |
| `create_asset_force_sensor`, `acquire_force_sensor_tensor` | A verified wrench-capable sensor path, or an explicit behavior gap if only 3D net contact forces are available |
| DOF order from asset | `robot.data.joint_names` and `find_joints(...)` |

Current develop examples commonly use `.torch` on data fields, such as `robot.data.default_joint_pos.torch[env_ids]`.

## Gotchas

- Quaternion conventions are branch-sensitive. Isaac Lab develop/3.0 math utilities and data access use `xyzw` with identity `(0, 0, 0, 1)`. Older Isaac Lab docs and code may use or mention `wxyz`; inspect the current checkout and the source task before converting.
- Isaac Gym Preview joint ordering may differ from Isaac Lab/Isaac Sim. Resolve by joint names.
- PhysX actor defaults can differ. Preserve damping, max velocities, contact offsets, solver iteration counts, and actuator limits explicitly when matching behavior matters.
- `apply_action` is called for each simulation step under `decimation`; `_pre_physics_step` is called once per RL step.
- In ManagerBasedRLEnv, action terms are applied by the action manager; preserve Isaac Gym action order with explicit `joint_names` and `preserve_order=True` when action vector compatibility matters.
- If source code uses Hydra interpolation like `${....device}`, replace it with explicit values or Python config fields.
- Keep asset import/conversion separate from environment logic. If URDF/MJCF import is not already represented as USD/config, make that a distinct migration task and do not call the migration runnable until an asset spawn smoke passes.
- Contact and force logic is asset-name sensitive. After fixed-joint merging or importer changes, print `robot.data.joint_names`, body names, and contact sensor matches before trusting terminations, feet/knee indexing, or torque penalties.
- Isaac Gym asset force sensors usually produce 6D force/torque wrenches. `ContactSensorCfg` net contact force is not automatically equivalent, so keep observation dimensions honest and mark any padded/missing torque channels.
- Converted assets may have default joint positions outside their own limits if the source relied on reset-time clamping. Put valid source-equivalent defaults in the asset config before runtime smoke tests.
- Newton/MJWarp has its own contact and solver parameters (`njmax`, `nconmax`, `cone`, `impratio`, `integrator`, `num_substeps`). A task that imports under PhysX may still need tuning or sensor substitutions before it is Newton-compatible.
- IsaacGymEnvs randomization blocks can be present even when `task.randomize: False`. Preserve them as migration notes, but do not mark them implemented unless reset/interval behavior is actually ported.
- Use `scripts/tools/find_quaternions.py --path <user_project>` and, for runtime data reads, `WARN_ON_TORCH_QUATF_ACCESS=1` when quaternion assumptions are likely to affect behavior.
