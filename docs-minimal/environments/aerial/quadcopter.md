# Quadcopter

**Hover and waypoint tracking with a generic quadcopter.**

<!-- VIDEO PLACEHOLDER -->

## Quick start

```bash
# Train (~30 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Quadcopter-Direct-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Quadcopter-Direct-v0 --num_envs 32
```

## Environment variants

| Task ID | Notes |
|---------|-------|
| `Isaac-Quadcopter-Direct-v0` | Hover / position tracking |
| `Isaac-TrackPositionNoObstacles-ARL-Robot-1-v0` | ARL drone, no obstacles |

## Source code

- Quadcopter: `source/isaaclab_tasks/isaaclab_tasks/direct/quadcopter/`
- ARL drone: `source/isaaclab_tasks/isaaclab_tasks/manager_based/drone_arl/`
