# Teleoperation

**Control robots interactively using keyboards, gamepads, spacemouse, or VR devices.**

## Overview

Isaac Lab provides a device abstraction layer for teleoperation. Any input device maps to either SE(3) pose commands (for manipulation) or velocity commands (for locomotion).

## Supported devices

| Device | Class | Best for |
|--------|-------|----------|
| Keyboard | `Se3Keyboard` | Quick testing, no hardware needed |
| Gamepad | `Se3Gamepad` | Smooth analog control |
| SpaceMouse | `Se3SpaceMouse` | 6-DoF manipulation |

## Keyboard teleoperation

```bash
./isaaclab.sh -p scripts/teleoperation/teleop_se3_agent.py \
    --task Isaac-Lift-Franka-v0 \
    --device keyboard \
    --num_envs 1
```

Default keyboard bindings:

| Key | Action |
|-----|--------|
| W / S | Move forward / backward |
| A / D | Move left / right |
| Q / E | Move up / down |
| Z / X | Roll |
| T / G | Pitch |
| C / V | Yaw |
| Space | Toggle gripper |
| R | Reset environment |

## Gamepad teleoperation

```bash
./isaaclab.sh -p scripts/teleoperation/teleop_se3_agent.py \
    --task Isaac-Lift-Franka-v0 \
    --device gamepad \
    --sensitivity 0.1
```

## Using teleoperation in code

```python
from isaaclab.devices import Se3Keyboard

teleop = Se3Keyboard(pos_sensitivity=0.05, rot_sensitivity=0.05)
teleop.reset()

while sim.is_running():
    # Get delta pose from device
    delta_pose, gripper_cmd = teleop.advance()

    # delta_pose: [3] position + [3] rotation (axis-angle)
    # gripper_cmd: bool (True = close)

    # Apply to IK controller or directly to robot
    ...
```

## Record demonstrations

Teleoperation data can be recorded for imitation learning:

```bash
./isaaclab.sh -p scripts/teleoperation/teleop_se3_agent.py \
    --task Isaac-Lift-Franka-v0 \
    --device keyboard \
    --record \
    --record_dir ./demos/
```

This saves observation-action pairs as HDF5 files compatible with robomimic and other imitation learning frameworks.

## Tips

- **Start with keyboard** for quick debugging — no hardware setup needed.
- **Use `--num_envs 1`** for teleoperation — running multiple envs slows down the interactive loop.
- **Lower sensitivity** if control feels too twitchy: `--sensitivity 0.02`.
- **SpaceMouse** provides the most natural 6-DoF control for manipulation tasks.
