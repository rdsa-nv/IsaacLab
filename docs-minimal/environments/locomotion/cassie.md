# Agility Cassie

**Bipedal locomotion with the Agility Robotics Cassie biped.**

![Agility Cassie](../../_static/demos/bipeds.jpg)

## Quick start

```bash
# Train on flat terrain (~1 hr)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Flat-Cassie-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Velocity-Flat-Cassie-v0 --num_envs 32
```

## Environment variants

| Task ID | Terrain |
|---------|---------|
| `Isaac-Velocity-Flat-Cassie-v0` | Flat |
| `Isaac-Velocity-Rough-Cassie-v0` | Rough |

## Source code

- Config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/cassie/`
