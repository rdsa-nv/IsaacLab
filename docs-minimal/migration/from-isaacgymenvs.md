# Migrating from IsaacGymEnvs

**Map IsaacGymEnvs concepts to Isaac Lab equivalents.**

## Overview

IsaacGymEnvs (IGE) was the predecessor to Isaac Lab for GPU-accelerated RL. Isaac Lab replaces it with a more modular architecture, better asset management, and Gymnasium compatibility.

## Key differences

| Concept | IsaacGymEnvs | Isaac Lab |
|---------|-------------|-----------|
| Environment class | `VecTask` | `DirectRLEnv` or `ManagerBasedRLEnv` |
| Config system | YAML + Hydra | `@configclass` + Hydra |
| Physics | IsaacGym (Preview 4) | Isaac Sim (PhysX 5 / Newton) |
| Asset loading | `gym.create_actor()` | `ArticulationCfg` + USD |
| Tensor API | `gym.acquire_*_tensor()` | `robot.data.*` attributes |
| Environment cloning | `gym.create_env()` | `InteractiveScene` + `{ENV_REGEX_NS}` |
| Rendering | IsaacGym viewer | Kit / Newton / Rerun / Viser |
| RL interface | Custom `VecTask` | Gymnasium API |

## Migration mapping

### Environment structure

**IsaacGymEnvs:**
```python
class MyTask(VecTask):
    def __init__(self, cfg, sim_device, graphics_device_id, headless):
        super().__init__(cfg, sim_device, graphics_device_id, headless)

    def create_sim(self):
        self.sim = super().create_sim(...)
        self._create_ground_plane()
        self._create_envs()

    def pre_physics_step(self, actions):
        self.actions = actions.clone()
        forces = self.actions * self.action_scale
        self.gym.set_dof_actuation_force_tensor(self.sim, gymtorch.unwrap_tensor(forces))

    def post_physics_step(self):
        self.obs_buf[:] = compute_observations(...)
        self.rew_buf[:] = compute_rewards(...)
        self.reset_buf[:] = ...
```

**Isaac Lab (Direct):**
```python
class MyTask(DirectRLEnv):
    cfg: MyTaskCfg

    def _setup_scene(self):
        self._robot = Articulation(self.cfg.robot_cfg)
        self.scene.articulations["robot"] = self._robot

    def _pre_physics_step(self, actions):
        self._actions = actions.clone()

    def _apply_action(self):
        self._robot.set_joint_effort_target(self._actions * self.cfg.action_scale)

    def _get_observations(self) -> dict:
        obs = torch.cat([self._robot.data.joint_pos, self._robot.data.joint_vel], dim=-1)
        return {"policy": obs}

    def _get_rewards(self) -> torch.Tensor:
        return compute_rewards(...)

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        return terminated, truncated

    def _reset_idx(self, env_ids):
        ...
```

### Tensor access

| IsaacGymEnvs | Isaac Lab |
|-------------|-----------|
| `self.gym.acquire_dof_state_tensor(self.sim)` | `robot.data.joint_pos`, `robot.data.joint_vel` |
| `self.gym.acquire_actor_root_state_tensor(self.sim)` | `robot.data.root_pos_w`, `robot.data.root_quat_w` |
| `self.gym.acquire_rigid_body_state_tensor(self.sim)` | `robot.data.body_pos_w`, `robot.data.body_quat_w` |
| `self.gym.acquire_jacobian_tensor(self.sim)` | `robot.data.jacobian` |
| `self.gym.acquire_mass_matrix_tensor(self.sim)` | `robot.data.mass_matrix` |
| `self.gym.acquire_net_contact_force_tensor(self.sim)` | `contact_sensor.data.net_forces_w` |

### Actions

| IsaacGymEnvs | Isaac Lab |
|-------------|-----------|
| `self.gym.set_dof_actuation_force_tensor(...)` | `robot.set_joint_effort_target(...)` |
| `self.gym.set_dof_position_target_tensor(...)` | `robot.set_joint_position_target(...)` |
| `self.gym.set_dof_velocity_target_tensor(...)` | `robot.set_joint_velocity_target(...)` |

### Resets

| IsaacGymEnvs | Isaac Lab |
|-------------|-----------|
| `self.gym.set_actor_root_state_tensor_indexed(...)` | `robot.write_root_pose_to_sim(...)` |
| `self.gym.set_dof_state_tensor_indexed(...)` | `robot.write_joint_state_to_sim(...)` |

## Step-by-step migration

1. **Convert assets**: Convert your URDF/MJCF files to USD (see [Import Assets](../how-to/import-assets.md))
2. **Create config**: Replace YAML config with `@configclass`-based config
3. **Subclass DirectRLEnv**: Map `VecTask` methods to `DirectRLEnv` methods
4. **Update tensor access**: Replace `gym.acquire_*` with `robot.data.*`
5. **Register with Gymnasium**: Add `gym.register()` call
6. **Test with random agent**: `./isaaclab.sh -p scripts/environments/random_agent.py --task MyTask`

## Tips

- **Direct environments** are closest to IsaacGymEnvs style — start there.
- **`@torch.jit.script`** still works for reward functions.
- **Multi-env cloning** is automatic via `InteractiveScene` — no manual `create_env` loop needed.
- Isaac Lab's Gymnasium interface means you can use **any RL framework**, not just rl_games.
