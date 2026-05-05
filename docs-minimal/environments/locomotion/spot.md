# Boston Dynamics Spot

**Velocity tracking with the Boston Dynamics Spot quadruped.**

![Spot on flat terrain](../../_static/tasks/locomotion/spot_flat.jpg)

## Quick start

```bash
# Train (~30 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Flat-Spot-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Velocity-Flat-Spot-v0 --num_envs 32
```

## Environment variants

| Task ID | Terrain |
|---------|---------|
| `Isaac-Velocity-Flat-Spot-v0` | Flat |

## Source code

- Config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/spot/`
