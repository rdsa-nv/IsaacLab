---
name: migrate-isaac-gym-to-isaac-lab
description: Guide Codex through migrating Isaac Gym Preview Release, IsaacGymEnvs, and OmniIsaacGymEnvs user tasks to Isaac Lab develop. Use when a user asks to port VecTask, RLTask, gymapi/gymtorch, Hydra YAML task configs, asset creation, tensor state APIs, observation/reward/reset logic, or RL training configs into Isaac Lab DirectRLEnv or ManagerBasedRLEnv projects.
---

<!--
Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause
-->

# Migrate Isaac Gym To Isaac Lab

## Overview

Port user environments by reading the user's source code first, then mapping the old Isaac Gym or OmniIsaacGymEnvs task shape into an Isaac Lab project. Prefer the current local Isaac Lab checkout over memory; this skill was seeded from Isaac Lab `develop` commit `4f7dd104af6cbca8035da954b53360f802c2b715`.

## Quick Workflow

1. Locate the old environment root and the target Isaac Lab checkout. If the user did not provide a target checkout, use a clean clone of `isaac-sim/IsaacLab` `develop` and a Python 3.12 `uv` environment.
2. Run the audit script to inventory migration work:

```bash
python scripts/audit_isaacgym_env.py /path/to/old_env --repo /path/to/IsaacLab
```

3. Classify the source:
   - IsaacGymEnvs: imports `isaacgym`, subclasses `VecTask`, uses `gymapi`, `gymtorch`, `create_sim`, `pre_physics_step`, `compute_observations`, `compute_reward`, or Hydra task YAML.
   - OmniIsaacGymEnvs: subclasses `RLTask`, uses `set_up_scene`, `post_reset`, `ArticulationView`, `RigidPrimView`, `calculate_metrics`, or `is_done`.
   - Raw Isaac Gym script: uses `gymapi` and actor/tensor APIs but has no RL task base class.
4. Choose the target workflow:
   - Default to `DirectRLEnv` for IsaacGymEnvs and OmniIsaacGymEnvs ports because it is closest to hand-written reward, reset, observation, and action logic.
   - Use `ManagerBasedRLEnv` when the user explicitly wants modular MDP terms, reusable commands/events/observations/rewards, policy deployment IO descriptors, or an existing manager-based project.
5. Create or reuse an Isaac Lab project. For a new external project, run `./isaaclab.sh --new`, choose Direct unless there is a reason not to, then install it from the active `uv` environment:

```bash
uv pip install -e source/<project_name>
```

6. Port the task in this order: config, asset conversion, scene setup, state access, actions, observations, rewards, dones, resets, registration, RL config, then smoke tests.
7. Keep behavior comparable. Preserve old reward math and reset ranges first; only refactor into nicer Isaac Lab abstractions after a tiny-env smoke test works.

## Source Context

When working in an Isaac Lab checkout, inspect these current files before editing:

- `docs/source/migration/migrating_from_isaacgymenvs.rst`
- `docs/source/migration/migrating_from_omniisaacgymenvs.rst`
- `docs/source/setup/quickstart.rst`
- `docs/source/tutorials/03_envs/create_direct_rl_env.rst`
- `docs/source/tutorials/03_envs/create_manager_rl_env.rst`
- `docs/source/overview/core-concepts/task_workflows.rst`
- `source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/`
- `source/isaaclab_tasks/isaaclab_tasks/direct/locomotion/`

Use the bundled references only after checking local source, or when the user only wants planning:

- `references/isaac-gym-api-map.md`: old-to-new API and config mapping.
- `references/direct-env-skeleton.md`: current Direct workflow file skeletons and smoke checks.

## Porting Rules

- Convert YAML task config into an `@configclass` that inherits from `DirectRLEnvCfg` or `ManagerBasedRLEnvCfg`.
- Replace `env.numEnvs` and `env.envSpacing` with `InteractiveSceneCfg(num_envs=..., env_spacing=...)`.
- Replace `controlFrequencyInv` with `decimation`.
- Convert maximum episode steps to seconds: `episode_length_s = dt * decimation * max_episode_steps`.
- Move `clipObservations` and `clipActions` into the RL config for libraries that use them.
- Replace `create_sim`, `_create_envs`, actor-handle loops, and manual env creation with `_setup_scene`, config-defined assets, `scene.clone_environments`, and `scene.filter_collisions`.
- Replace `gym.load_asset` and actor options with `ArticulationCfg`, `RigidObjectCfg`, `UsdFileCfg`, `UrdfFileCfg`, rigid body properties, articulation properties, and actuator configs.
- Treat URDF/MJCF conversion as its own validation gate. Map source `gymapi.AssetOptions` fields such as `collapse_fixed_joints`, `replace_cylinder_with_capsule`, `flip_visual_attachments`, `fix_base_link`, `density`, damping, armature, and drive mode, but confirm the current Isaac Lab `UrdfFileCfg`/`MjcfFileCfg` converter and the active Isaac Sim runtime both accept the resulting options before claiming the environment runs. For MJCF, enable or verify `isaacsim.asset.importer.mjcf`; if Isaac Lab develop forwards importer fields unsupported by the active runtime, pre-convert to USD with that runtime and record the mismatch.
- Do not use an existing Isaac Lab example task as the migration source unless the user explicitly asks for that. Examples are useful for API shape; the source of truth for behavior is the user's Isaac Gym code, YAML, and assets.
- Replace `acquire_*_tensor`, `refresh_*_tensor`, `gymtorch.wrap_tensor`, and `gymtorch.unwrap_tensor` with `asset.data` buffers and `write_*_to_sim_index` methods.
- Resolve joints and bodies by name or regex (`find_joints`, `find_bodies`) instead of preserving Isaac Gym integer handle order.
- Check quaternion order against the current checkout. Isaac Lab develop/3.0 math and data paths use `xyzw`; older Isaac Lab docs and some older code may mention `wxyz`. Do not apply a blind conversion.
- Re-check joint ordering. Isaac Gym Preview used depth-first joint ordering; Isaac Lab/Isaac Sim use breadth-first ordering. Do not blindly reuse DOF indices.
- Re-check body names after asset conversion. Fixed-joint merging, visual attachment flipping, and URDF importer behavior can change names used by contact sensors, force sensors, terminations, feet, knees, and base bodies.
- Port `create_asset_force_sensor`, `acquire_force_sensor_tensor`, `enable_actor_dof_force_sensors`, `acquire_dof_force_tensor`, and `acquire_net_contact_force_tensor` deliberately. Isaac Gym force sensors may expose 6D force/torque wrenches; Isaac Lab `ContactSensor` net forces are typically 3D. Do not silently pad or drop torque channels without marking the behavior gap and checking whether a wrench sensor or backend-specific sensor is required.
- Seed default joint positions inside valid converted limits. IsaacGymEnvs tasks often initialize joints whose range excludes zero at the nearest limit before adding reset noise; Isaac Lab may validate the configured default pose before your `_reset_idx` logic runs.
- Preserve domain randomization parameters even when the source has `randomize: False`, but mark them as recorded rather than implemented. If enabled, port reset-time and interval randomization to Isaac Lab events or explicit `_reset_idx`/step logic.
- Keep old Torch reward functions when possible. Port the data sources, not the math, on the first pass.

## Direct Workflow Mapping

For a direct port, map these methods:

- `create_sim` or `set_up_scene` -> `_setup_scene`
- `pre_physics_step(actions)` -> `_pre_physics_step(actions)` plus `_apply_action()`
- `compute_observations` or `get_observations` -> `_get_observations`, returning `{"policy": obs}`
- `compute_reward` or `calculate_metrics` -> `_get_rewards`, returning the reward tensor
- `reset_idx(env_ids)` -> `_reset_idx(env_ids)`
- `is_done` -> `_get_dones`, returning `(terminated, time_out)`
- `post_physics_step` and most `post_reset` logic -> base class flow, `__init__`, or `_reset_idx`

Current develop examples use buffers such as:

```python
self.joint_pos = self.robot.data.joint_pos.torch
self.root_pos_w = self.robot.data.root_pos_w.torch
self.robot.write_root_pose_to_sim_index(root_pose=default_root_pose, env_ids=env_ids)
self.robot.write_joint_position_to_sim_index(position=joint_pos, env_ids=env_ids)
```

## Verification

Run the smallest useful checks first:

```bash
uv run python -c "import <project_package>"
uv run python scripts/environments/list_envs.py | rg "<Task-Name>"
uv run train --rl_library rsl_rl --task <Task-Name> --num_envs 16 --max_iterations 1 --viz none presets=physx
```

If the task imports URDF/MJCF assets, run a conversion/spawn smoke before the full training smoke. A successful config import is not enough: verify the same Isaac Sim runtime that will run the task accepts converter fields such as `merge_fixed_joints`, `replace_cylinders_with_capsules`, and MJCF importer options, then print the resolved joint and body names used by action and contact logic.

For an end-to-end migration smoke, instantiate the registered Gymnasium task with a tiny `scene.num_envs`, run `reset`, run several `step`s with zero or bounded random actions, assert observation/action/reward/done tensor shapes, and print the resolved joint/body/contact names. If the requested PhysX path is blocked by a local Isaac Sim extension mismatch, a Newton smoke is useful for task-logic validation, but label the backend difference instead of claiming PhysX parity.

Use `presets=newton_mjwarp` only when the task's assets and physics choices are known to be compatible with Newton. If the user is comparing to Isaac Gym physics, validate with PhysX first unless they asked for Newton.

For quaternion-heavy ports, run Isaac Lab's finder on the user's code and review the output before changing values:

```bash
uv run python scripts/tools/find_quaternions.py --path /path/to/user_project --likely-wxyz
```
