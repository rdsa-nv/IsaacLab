# ANYmal-D Quadruped

**Velocity tracking with the ANYbotics ANYmal-D quadruped.**

<!-- VIDEO PLACEHOLDER -->

## Quick start

```bash
# Train on flat terrain (~30 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Flat-Anymal-D-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Velocity-Flat-Anymal-D-v0 --num_envs 32
```

## Environment variants

| Task ID | Terrain |
|---------|---------|
| `Isaac-Velocity-Flat-Anymal-D-v0` | Flat |
| `Isaac-Velocity-Rough-Anymal-D-v0` | Rough |

## Source code

- Config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/anymal_d/`
