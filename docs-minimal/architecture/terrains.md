# Terrain System

**Generate procedural terrains for locomotion training with automatic curriculum support.**

## Overview

Isaac Lab's terrain system generates heightfield or trimesh terrains arranged in a grid. Rows represent difficulty levels; columns represent random variations at each level. Combined with curriculum learning, robots automatically progress to harder terrain as they improve.

## Terrain generator

```python
from isaaclab.terrains import TerrainGeneratorCfg
from isaaclab.terrains.height_field import HfRandomUniformTerrainCfg, HfWaveTerrainCfg

terrain_generator = TerrainGeneratorCfg(
    curriculum=True,          # Enable curriculum-based assignment
    size=(8.0, 8.0),          # Each sub-terrain patch [m]
    num_rows=10,              # 10 difficulty levels
    num_cols=20,              # 20 variations per level
    border_width=20.0,        # Border around terrain grid [m]
    sub_terrains={
        "flat": HfRandomUniformTerrainCfg(
            proportion=0.2,
            noise_range=(0.0, 0.0),
            noise_step=0.01,
        ),
        "rough": HfRandomUniformTerrainCfg(
            proportion=0.2,
            noise_range=(-0.02, 0.02),
            noise_step=0.01,
        ),
        "slopes": HfRandomUniformTerrainCfg(
            proportion=0.2,
            slope_range=(0.0, 0.4),
        ),
        "stairs_up": HfRandomUniformTerrainCfg(
            proportion=0.2,
            step_height_range=(0.05, 0.23),
            step_width=0.31,
        ),
        "waves": HfWaveTerrainCfg(
            proportion=0.2,
            amplitude_range=(0.01, 0.06),
            num_waves=3,
        ),
    },
)
```

## Available terrain types

### Height-field based

| Type | Description | Key params |
|------|-------------|------------|
| `HfRandomUniformTerrainCfg` | Random bumps | `noise_range`, `noise_step` |
| `HfWaveTerrainCfg` | Sinusoidal waves | `amplitude_range`, `num_waves` |
| `HfSteppingStonesTerrainCfg` | Discrete stepping stones | `stone_height_max`, `stone_distance_range` |
| `HfPyramidSlopedTerrainCfg` | Pyramid slopes | `slope_range` |
| `HfPyramidStairsTerrainCfg` | Pyramid stairs | `step_height_range`, `step_width` |
| `HfInvertedPyramidSlopedTerrainCfg` | Inverted pyramid slopes | `slope_range` |
| `HfInvertedPyramidStairsTerrainCfg` | Inverted pyramid stairs | `step_height_range` |
| `HfDiscreteObstaclesTerrainCfg` | Random box obstacles | `obstacle_height_range` |

### Trimesh based

| Type | Description |
|------|-------------|
| `MeshPlaneTerrainCfg` | Flat plane |
| `MeshPyramidStairsTerrainCfg` | Stairs mesh |
| `MeshInvertedPyramidStairsTerrainCfg` | Inverted stairs mesh |
| `MeshRandomGridTerrainCfg` | Random grid terrain |
| `MeshRepeatedObjectsTerrainCfg` | Repeated obstacle patterns |
| `MeshGapTerrainCfg` | Terrain with gaps |
| `MeshRailsTerrainCfg` | Rail-like terrain |

## Using terrain in a scene

```python
from isaaclab.terrains import TerrainImporterCfg

@configclass
class MySceneCfg(InteractiveSceneCfg):
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="generator",
        terrain_generator=terrain_generator,
        max_init_terrain_level=5,   # Max starting difficulty
        collision_group=-1,
        physics_material=RigidBodyMaterialCfg(
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
    )
```

## Terrain types

| `terrain_type` | Source | Use case |
|----------------|--------|----------|
| `"generator"` | Procedural (from `TerrainGeneratorCfg`) | Training with curriculum |
| `"plane"` | Flat ground plane | Simple tasks |
| `"usd"` | Load from USD file | Custom/scanned terrains |

## Curriculum integration

When `curriculum=True`, each environment is assigned a terrain level (row). The curriculum manager moves robots to harder rows as they succeed:

```
Row 0 (easiest):  [flat] [flat] [flat] ... (20 columns)
Row 1:            [rough] [rough] [rough] ...
Row 2:            [slopes] [slopes] [slopes] ...
...
Row 9 (hardest):  [stairs] [stairs] [stairs] ...
```

Difficulty increases with row number. Within each row, columns provide variation. See [Curriculum Learning](../how-to/curriculum-learning.md) for details on the advancement logic.

## Tips

- **Proportions must sum to 1.0** across all sub-terrain types.
- **Difficulty scales with row**: Parameters interpolate from min to max values across rows 0 to `num_rows-1`.
- **Border width** prevents robots from falling off the edge of the terrain grid.
- **Height-field resolution**: Default is sufficient for most tasks. Increase for fine-grained features.
- **Use flat terrain first** when developing a new task, add complex terrain after the policy works on flat ground.
