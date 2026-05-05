# Physics Backends

**Isaac Lab supports multiple physics engines. Choose the right one for your task.**

## Available backends

| Backend | Engine | GPU | Soft body | Best for |
|---------|--------|-----|-----------|----------|
| PhysX (GPU) | NVIDIA PhysX 5 | Yes | Yes | Default — most features, well tested |
| Newton | MuJoCo-Warp | Yes | Limited | Speed — locomotion, simple manipulation |
| PhysX (CPU) | NVIDIA PhysX 5 | No | Yes | Debugging, small-scale testing |

## Selecting a backend

### Via CLI

```bash
# PhysX GPU (default)
./isaaclab.sh -p train.py --task MyTask

# Newton
./isaaclab.sh -p train.py --task MyTask --physics_backend newton

# PhysX CPU (debugging only)
./isaaclab.sh -p train.py --task MyTask --physics_backend cpu
```

### Via config

```python
from isaaclab.sim import SimulationCfg, PhysxCfg

sim_cfg = SimulationCfg(
    dt=0.005,
    physx=PhysxCfg(
        gpu_found_lost_pairs_capacity=2**23,
        gpu_total_aggregate_pairs_capacity=2**23,
    ),
)
```

## PhysX GPU

The default and most mature backend. Supports all Isaac Lab features:

- Rigid body dynamics
- Articulated robots
- Deformable objects (FEM)
- Collision detection with GPU broadphase
- Convex decomposition, mesh collisions
- All sensor types

**Tuning GPU buffers:** For large scenes (8000+ envs), increase buffer sizes:

```python
physx=PhysxCfg(
    gpu_found_lost_pairs_capacity=2**24,       # Default: 2**21
    gpu_total_aggregate_pairs_capacity=2**24,   # Default: 2**21
    gpu_max_rigid_contact_count=2**22,          # Default: 2**19
    gpu_heap_capacity=2**27,                    # Default: 2**26
)
```

If you see `PhysX error: out of ...` messages, increase the relevant capacity.

## Newton (MuJoCo-Warp)

A newer, lightweight backend built on Warp. Faster for locomotion tasks but with fewer features.

**Advantages:**

- Faster simulation step for rigid-body-only scenes
- Lower memory overhead
- MuJoCo-compatible contact model

**Limitations:**

- No deformable body support
- Limited collision geometry types
- Fewer sensor types supported
- Beta status — API may change

```bash
./isaaclab.sh -p train.py --task Isaac-Velocity-Flat-Anymal-C-v0 --physics_backend newton
```

## Simulation parameters

Key parameters that affect both accuracy and speed:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `dt` | 0.005 | Physics timestep [s]. Smaller = more accurate, slower |
| `substeps` | 1 | Physics substeps per step. More = more stable |
| `gravity` | (0, 0, -9.81) | Gravity vector [m/s^2] |
| `enable_scene_query_support` | False | Enable raycasts (needed for ray caster sensor) |

```python
sim_cfg = SimulationCfg(
    dt=0.005,
    substeps=1,
    gravity=(0.0, 0.0, -9.81),
    enable_scene_query_support=True,   # Required for ray caster
)
```

## Physics presets

Isaac Lab provides presets for common scenarios:

```bash
# High-fidelity manipulation
./isaaclab.sh -p train.py --task MyTask --physics_preset manipulation

# Fast locomotion training
./isaaclab.sh -p train.py --task MyTask --physics_preset locomotion
```

## Choosing a backend

```
Need deformable objects?
  └─ Yes → PhysX GPU
  └─ No → Need maximum speed?
      └─ Yes → Newton (if your task is supported)
      └─ No → PhysX GPU (safest default)
```

For most users, **PhysX GPU is the right choice**. Switch to Newton only if you need faster training for rigid-body-only tasks and have verified your task works with it.
