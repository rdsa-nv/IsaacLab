# Migrating from Orbit

**Map NVIDIA Orbit concepts to Isaac Lab equivalents.**

## Overview

Isaac Lab is the successor to Orbit. Most Orbit concepts map directly — the main changes are namespace reorganization and API refinements.

## Namespace changes

| Orbit | Isaac Lab |
|-------|-----------|
| `omni.isaac.orbit` | `isaaclab` |
| `omni.isaac.orbit.envs` | `isaaclab.envs` |
| `omni.isaac.orbit.assets` | `isaaclab.assets` |
| `omni.isaac.orbit.sensors` | `isaaclab.sensors` |
| `omni.isaac.orbit.managers` | `isaaclab.managers` |
| `omni.isaac.orbit.scene` | `isaaclab.scene` |
| `omni.isaac.orbit.sim` | `isaaclab.sim` |
| `omni.isaac.orbit.utils` | `isaaclab.utils` |
| `omni.isaac.orbit_tasks` | `isaaclab_tasks` |

## Environment changes

| Orbit | Isaac Lab |
|-------|-----------|
| `BaseEnv` | `ManagerBasedEnv` |
| `RLTaskEnv` | `ManagerBasedRLEnv` |
| `RLTaskEnvCfg` | `ManagerBasedRLEnvCfg` |
| N/A | `DirectRLEnv` (new) |

## Config changes

Orbit used `omni.isaac.orbit.utils.configclass`. Isaac Lab uses:

```python
from isaaclab.utils import configclass

@configclass
class MyEnvCfg(ManagerBasedRLEnvCfg):
    ...
```

## Task registration

**Orbit:**
```python
gym.register(
    id="Isaac-Reach-Franka-v0",
    entry_point="omni.isaac.orbit_tasks.manipulation.reach:ReachEnv",
    kwargs={"env_cfg_entry_point": "omni.isaac.orbit_tasks.manipulation.reach:ReachEnvCfg"},
)
```

**Isaac Lab:**
```python
gym.register(
    id="Isaac-Reach-Franka-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={"env_cfg_entry_point": "isaaclab_tasks.manipulation.reach:ReachEnvCfg"},
)
```

## Manager changes

| Orbit | Isaac Lab | Notes |
|-------|-----------|-------|
| `ObservationManager` | `ObservationManager` | Same |
| `ActionManager` | `ActionManager` | Same |
| `RewardManager` | `RewardManager` | Same |
| `TerminationManager` | `TerminationManager` | Same |
| `RandomizationManager` | `EventManager` | Renamed |
| `CurriculumManager` | `CurriculumManager` | Same |

The `RandomizationManager` was renamed to `EventManager` to reflect its broader scope (handles any event, not just randomization).

## Migration steps

1. **Update imports**: Replace `omni.isaac.orbit` with `isaaclab`
2. **Rename env classes**: `RLTaskEnv` → `ManagerBasedRLEnv`
3. **Update event configs**: `RandomizationCfg` → `EventCfg`
4. **Update task registration**: New package paths
5. **Test**: Run with random agent to verify

Most migrations are find-and-replace on import paths. The core APIs are largely unchanged.
