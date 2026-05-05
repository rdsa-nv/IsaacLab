# Curriculum Learning

**Adapt task difficulty during training to accelerate learning and improve final performance.**

## Overview

Curriculum learning gradually increases task difficulty as the agent improves. In Isaac Lab, this is implemented through curriculum terms that modify environment parameters based on training progress.

## Manager-based curriculum

```python
from isaaclab.managers import CurriculumTermCfg as CurrTerm

@configclass
class CurriculumCfg:
    terrain_levels = CurrTerm(
        func=mdp.terrain_levels_vel,
        params={
            "asset_cfg": SceneEntityCfg("robot"),
        },
    )
```

Curriculum terms are called after each environment step and can modify any aspect of the environment.

## Custom curriculum functions

Write curriculum functions that adjust parameters based on metrics:

```python
def terrain_levels_vel(
    env: ManagerBasedRLEnv,
    env_ids: torch.Tensor,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Move robots to harder terrain based on tracking performance."""
    asset = env.scene[asset_cfg.name]

    # Compute distance walked
    distance = torch.norm(asset.data.root_pos_w[env_ids, :2], dim=1)

    # Advance level if distance threshold met
    move_up = distance > 1.0
    move_down = distance < 0.1

    terrain_levels = env.scene.terrain.terrain_levels
    terrain_levels[env_ids] += move_up.long() - move_down.long()
    terrain_levels.clamp_(0, env.scene.terrain.max_terrain_level)

    return terrain_levels[env_ids]
```

## Common curriculum strategies

### Terrain difficulty

Most locomotion environments use terrain-based curriculum:

```python
from isaaclab.terrains import TerrainGeneratorCfg, HfTerrainBaseCfg

terrain_generator = TerrainGeneratorCfg(
    curriculum=True,   # Enable curriculum-based terrain assignment
    size=(8.0, 8.0),
    num_rows=10,       # 10 difficulty levels
    num_cols=20,       # 20 variations per level
    sub_terrains={
        "flat": HfTerrainBaseCfg(proportion=0.2, noise_scale=0.0),
        "rough": HfTerrainBaseCfg(proportion=0.3, noise_range=(-0.02, 0.02)),
        "slopes": HfTerrainBaseCfg(proportion=0.3, slope_range=(0.0, 0.4)),
        "stairs": HfTerrainBaseCfg(proportion=0.2, step_height_range=(0.05, 0.23)),
    },
)
```

Robots start on easy terrain (row 0) and advance to harder rows as they succeed.

### Reward shaping

Gradually shift from dense to sparse rewards:

```python
@configclass
class RewardsCfg:
    tracking = RewTerm(
        func=mdp.track_lin_vel_xy_exp,
        weight=1.0,
        params={"std": 0.5},   # Start with wide tolerance
    )
```

Then in a curriculum term, tighten the tolerance:

```python
def tighten_tracking(env, env_ids):
    progress = env.common_step_counter / 10000
    env.reward_manager.get_term("tracking").cfg.params["std"] = max(0.1, 0.5 - 0.4 * progress)
```

### Command ranges

Widen the range of commanded velocities as the policy improves:

```python
def expand_commands(env, env_ids):
    if env.common_step_counter > 5000:
        env.command_manager.get_term("velocity").cfg.ranges.lin_vel_x = (-1.5, 1.5)
        env.command_manager.get_term("velocity").cfg.ranges.ang_vel_z = (-1.5, 1.5)
```

## Tips

- **Start simple**: Train a working policy on easy settings first, then add curriculum.
- **Use terrain curriculum** for locomotion tasks — it's the most well-tested approach.
- **Monitor level distribution**: If all agents are stuck at level 0, the jump in difficulty is too large.
- **Combine with domain randomization**: Curriculum controls difficulty; randomization controls robustness.
