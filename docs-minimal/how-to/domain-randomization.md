# Domain Randomization

**Randomize physics, visuals, and initial conditions to train robust policies that transfer to real robots.**

## Overview

Isaac Lab uses `EventTermCfg` to define randomization events. Each event specifies:

- **func**: What to randomize
- **mode**: When to apply it (`startup`, `reset`, or `interval`)
- **params**: Randomization ranges

## Event modes

| Mode | When it fires | Use case |
|------|--------------|----------|
| `startup` | Once at sim start | Static properties (mass, friction) per environment |
| `reset` | Each episode reset | Initial state randomization |
| `interval` | Every N seconds | Time-varying disturbances (external forces) |

## Manager-based environments

```python
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.envs.mdp import events

@configclass
class EventCfg:
    # Randomize physics properties at startup
    physics_material = EventTerm(
        func=events.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot"),
            "static_friction_range": (0.7, 1.3),
            "dynamic_friction_range": (0.7, 1.3),
            "restitution_range": (0.0, 0.1),
        },
    )

    # Randomize mass at startup
    add_base_mass = EventTerm(
        func=events.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="base"),
            "mass_distribution_params": (-1.0, 3.0),
            "operation": "add",
        },
    )

    # Randomize initial joint positions at reset
    reset_joints = EventTerm(
        func=events.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot"),
            "position_range": (-0.25, 0.25),
            "velocity_range": (-0.1, 0.1),
        },
    )

    # Apply random external forces periodically
    push_robot = EventTerm(
        func=events.push_by_setting_velocity,
        mode="interval",
        interval_range_s=(10.0, 15.0),
        params={
            "asset_cfg": SceneEntityCfg("robot"),
            "velocity_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)},
        },
    )
```

## Direct environments

In direct environments, apply randomization manually in `_reset_idx`:

```python
class MyEnv(DirectRLEnv):
    def _reset_idx(self, env_ids: torch.Tensor):
        # Randomize initial joint positions
        joint_pos = self._robot.data.default_joint_pos[env_ids].clone()
        joint_pos += torch.randn_like(joint_pos) * 0.25

        joint_vel = torch.zeros_like(joint_pos)

        self._robot.write_joint_state_to_sim(joint_pos, joint_vel, env_ids=env_ids)
```

For startup randomization, use `_setup_scene`:

```python
def _setup_scene(self):
    self._robot = Articulation(self.cfg.robot_cfg)
    self.scene.articulations["robot"] = self._robot

    # Randomize mass per environment
    masses = self._robot.root_physx_view.get_masses()
    masses[:, 0] += torch.empty(self.num_envs, 1, device=self.device).uniform_(-1.0, 3.0)
    self._robot.root_physx_view.set_masses(masses)
```

## What to randomize

| Category | Parameters | Typical range |
|----------|-----------|---------------|
| **Dynamics** | Mass, friction, restitution, CoM | +/- 10-30% |
| **Actuators** | Stiffness, damping, effort limits | +/- 10-20% |
| **Initial state** | Joint positions, base pose | Task-dependent |
| **External forces** | Push velocity, applied wrench | 0.5-2.0 m/s |
| **Sensors** | Noise on observations | 0-5% of range |
| **Terrain** | Roughness, slope, obstacles | Progressive |
| **Visuals** | Texture, lighting, color | For vision RL |

## Available randomization functions

From `isaaclab.envs.mdp.events`:

| Function | What it randomizes |
|----------|--------------------|
| `randomize_rigid_body_material` | Friction and restitution |
| `randomize_rigid_body_mass` | Body masses |
| `reset_root_state_uniform` | Base pose and velocity |
| `reset_joints_by_offset` | Joint positions and velocities |
| `reset_joints_by_scale` | Joint positions scaled from defaults |
| `push_by_setting_velocity` | Apply velocity impulse |
| `reset_scene_to_default` | Reset everything to defaults |
| `randomize_actuator_gains` | PD gains |
| `apply_external_force_torque` | Sustained external wrench |

## Tips

- **Start small**: Begin with no randomization, add gradually once the base policy works.
- **Use startup mode** for properties that are constant within an episode (mass, friction). Each environment gets a different sample.
- **Use reset mode** for initial conditions that change every episode.
- **Monitor training curves**: Too much randomization early can prevent learning. Too little leads to brittle policies.
- **Combine with curriculum**: Start with narrow ranges and widen as the policy improves (see [Curriculum Learning](curriculum-learning.md)).
