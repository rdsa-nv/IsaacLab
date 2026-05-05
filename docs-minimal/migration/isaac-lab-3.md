# Isaac Lab 3.0 Migration Guide

**Everything that changed in Isaac Lab 3.0 and how to update your code.**

## Overview of breaking changes

| Change | Impact | Migration effort |
|--------|--------|-----------------|
| Python 3.12 required | All users | Recreate conda env |
| Isaac Sim 6.0.0 | All users | Update Isaac Sim |
| Quaternion format WXYZ → XYZW | All users with custom envs | Find & replace |
| IMU → PVA sensor rename | Users with IMU sensors | Rename imports |
| Multi-backend architecture | Env authors | Optional (backward compatible) |
| `--headless` → `--viz` | CLI scripts | Optional (old flag still works) |
| XformPrimView → FrameView | Advanced users | Deprecated alias available |
| NumPy 2.0+ | All users | Check for breaking NumPy changes |

## Python 3.12 and Isaac Sim 6.0

Isaac Lab 3.0 requires **Python 3.12** (minimum) and targets **Isaac Sim 6.0.0**.

```bash
# Create new environment
conda create -n isaaclab python=3.12 -y
conda activate isaaclab
pip install isaacsim[all]
./isaaclab.sh -i
```

## Quaternion format: WXYZ → XYZW

**This is the most impactful breaking change.** All quaternions in Isaac Lab 3.0 use `(x, y, z, w)` order instead of `(w, x, y, z)`.

```python
# Before (Isaac Lab 2.x) — WXYZ
identity_quat = (1.0, 0.0, 0.0, 0.0)  # w, x, y, z
ik_command[:, 3:] = torch.tensor([1.0, 0.0, 0.0, 0.0])

# After (Isaac Lab 3.0) — XYZW
identity_quat = (0.0, 0.0, 0.0, 1.0)  # x, y, z, w
ik_command[:, 3:] = torch.tensor([0.0, 0.0, 0.0, 1.0])
```

**Why?** Aligns with Warp, PhysX, and Newton internal representations, eliminating conversion overhead.

**What to update:**

- All `rot` parameters in asset/sensor configs
- Hard-coded quaternion values in environment code
- Target orientations in controllers and task definitions
- Goal poses and initial states

**Migration tool:** Use the provided scanner to find quaternions in your code:

```bash
./isaaclab.sh -p scripts/tools/find_quaternions.py --path /path/to/your/code
```

This scans for common WXYZ patterns like `(1.0, 0.0, 0.0, 0.0)` and flags them for manual review.

## IMU sensor → PVA sensor rename

The old `Imu` sensor (which provided full state: pose, velocity, acceleration) has been renamed to **`Pva`** (Pose, Velocity, Acceleration). A new lightweight `Imu` sensor replaces it that only provides gyroscope and accelerometer readings.

```python
# Before (2.x) — full state IMU
from isaaclab.sensors import Imu, ImuCfg

# After (3.0) — for full state, use PVA
from isaaclab.sensors import Pva, PvaCfg

# After (3.0) — for real IMU behavior (gyro + accelerometer)
from isaaclab.sensors import Imu, ImuCfg
```

| Sensor | Data | Gravity in accel? |
|--------|------|:-:|
| `Pva` (was `Imu`) | Position, velocity, raw acceleration | No |
| `Imu` (new) | Angular velocity, linear acceleration | Yes |

The `gravity_bias` parameter has been removed from both sensors.

## Visualizer CLI changes

The `--headless` flag is deprecated (still works). Use `--viz` / `--visualizer` instead:

```bash
# Before
./isaaclab.sh -p train.py --task MyTask --headless

# After
./isaaclab.sh -p train.py --task MyTask --viz none

# Multiple visualizers
./isaaclab.sh -p train.py --task MyTask --viz kit,rerun

# Newton visualizer (works without Isaac Sim)
./isaaclab.sh -p train.py --task MyTask --viz newton
```

Available visualizers:

| Visualizer | Description | Requires Isaac Sim |
|-----------|-------------|:-:|
| `kit` | Omniverse rendering (default) | Yes |
| `newton` | Fast, lightweight | No |
| `rerun` | Remote viewing, replay | No |
| `viser` | Web-based browser viewer | No |
| `none` | Headless (no visualization) | No |

![Visualizer comparison](../_static/visualizers/newton_viz.jpg)

## Multi-backend architecture

Isaac Lab 3.0 introduces a **factory-based multi-backend system**. Your existing code works without changes — the factory dispatches to the correct backend automatically.

**Two physics backends:**

| Backend | Package | Features |
|---------|---------|----------|
| PhysX | `isaaclab_physx` | Full-featured, deformables, all sensors |
| Newton | `isaaclab_newton` | Fast rigid-body sim, MuJoCo-Warp |

**No import changes needed:**

```python
# This works for BOTH backends — factory auto-dispatches
from isaaclab.assets import Articulation, ArticulationCfg

robot = Articulation(cfg)  # Factory selects PhysX or Newton implementation
```

**Select backend at runtime:**

```bash
# PhysX (default)
./isaaclab.sh -p train.py --task MyTask

# Newton
./isaaclab.sh -p train.py --task MyTask --physics_backend newton
```

### Multi-backend environments with PresetCfg

To write environments that work with both backends, use `PresetCfg`:

```python
from isaaclab.sim import PresetCfg, PhysxCfg, NewtonCfg

@configclass
class MyPhysicsCfg(PresetCfg):
    default: PhysxCfg = PhysxCfg(dt=0.005)
    physx:   PhysxCfg = PhysxCfg(dt=0.005)
    newton:  NewtonCfg = NewtonCfg(dt=0.005)
```

Select at launch: `--presets newton`

## XformPrimView → FrameView

Internal renaming with deprecated aliases:

| Old name | New name |
|----------|----------|
| `BaseXformPrimView` | `BaseFrameView` |
| `XformPrimView` | `FrameView` |
| `FabricXformPrimView` | `FabricFrameView` |

The old names still work but will be removed in a future release.

## RigidObjectCollection API renaming

Methods on `RigidObjectCollection` have been renamed from `object_*` to `body_*`:

```python
# Before
collection.write_object_state_to_sim(state)
collection.write_object_pose_to_sim(pose)

# After
collection.write_body_state_to_sim(state)
collection.write_body_pose_to_sim(pose)
```

The old names are deprecated but still work.

## Contact sensor changes

`pose_w`, `pos_w`, and `quat_w` on `ContactSensorData` are deprecated. Use `FrameTransformer` to track sensor poses instead.

## Deformable object changes

Deformable objects have moved from `isaaclab` to `isaaclab_physx` (PhysX-only feature):

```python
# Before
from isaaclab.assets import DeformableObject

# After
from isaaclab_physx.assets import DeformableObject
```

Two distinct types:

- **Volume deformables** — 3D FEM tetrahedral meshes
- **Surface deformables** — 2D triangle cloth meshes (new)

## Lazy module loading

Isaac Lab 3.0 uses lazy imports, so heavyweight dependencies (`pxr`, `omni`, `scipy`) don't load until first access. This means:

- Config objects can be constructed before `SimulationApp` initialization
- Backend selection happens automatically
- Faster startup for Newton-only workflows

## Step-by-step migration checklist

1. **Update environment**: Python 3.12, Isaac Sim 6.0.0
2. **Scan for quaternions**: Run `find_quaternions.py` on your code
3. **Update quaternion values**: `(w, x, y, z)` → `(x, y, z, w)`
4. **Rename IMU imports**: `Imu` → `Pva` if you need full state
5. **Update CLI scripts**: `--headless` → `--viz none` (optional)
6. **Test**: Run your environments with `random_agent.py`
7. **Try Newton**: Test with `--physics_backend newton` for speedups
