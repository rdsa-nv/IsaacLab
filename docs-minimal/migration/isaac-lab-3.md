# Isaac Lab 3.0 Changes

**What changed in Isaac Lab 3.0 and how to update your code.**

## Major changes

### Multi-backend support

Isaac Lab 3.0 introduced support for multiple physics backends beyond PhysX:

- **Newton** (MuJoCo-Warp): New lightweight backend for rigid-body tasks
- **PhysX GPU**: Remains the default
- Backend selection via CLI: `--physics_backend newton`

### Visualization backends

Four rendering backends are now supported:

| Backend | Use case |
|---------|----------|
| Kit (Omniverse) | Full rendering, USD stage |
| Newton | Lightweight, fast |
| Rerun | Replay and analysis |
| Viser | Web-based viewer |

### Direct environment improvements

- Better `@torch.jit.script` support for reward computation
- Improved reset semantics with `_reset_idx`
- Action application separated into `_pre_physics_step` and `_apply_action`

### New sensor types

- `TiledCameraCfg` for large-scale vision RL
- `RayCasterCameraCfg` for virtual depth cameras
- Improved IMU sensor with configurable noise models

## Breaking changes

### Import path changes

```python
# Before
from isaaclab.envs import ManagerBasedRLEnvCfg

# After (same — no change for core imports)
from isaaclab.envs import ManagerBasedRLEnvCfg
```

### Event manager

```python
# Before: RandomizationTermCfg
from isaaclab.managers import RandomizationTermCfg

# After: EventTermCfg
from isaaclab.managers import EventTermCfg
```

### Simulation config

```python
# Before
sim_cfg = SimulationCfg(dt=0.005)

# After: PhysX config is nested
sim_cfg = SimulationCfg(
    dt=0.005,
    physx=PhysxCfg(
        gpu_found_lost_pairs_capacity=2**23,
    ),
)
```

## How to update

1. **Check import changes**: Most imports remain stable. Update `RandomizationTermCfg` → `EventTermCfg`.
2. **Update SimulationCfg**: Nest PhysX parameters under `physx=PhysxCfg(...)`.
3. **Test your environments**: Run with random agent to verify behavior.
4. **Try Newton backend**: If your task is rigid-body only, test with `--physics_backend newton` for potential speedups.

## Deprecation notices

Deprecated APIs from 2.x that were removed in 3.0:

| Removed | Replacement |
|---------|-------------|
| `RandomizationManager` | `EventManager` |
| `RandomizationTermCfg` | `EventTermCfg` |
| `RLTaskEnv` | `ManagerBasedRLEnv` |
| `RLTaskEnvCfg` | `ManagerBasedRLEnvCfg` |
