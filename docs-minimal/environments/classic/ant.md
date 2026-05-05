# Ant

**MuJoCo-style ant locomotion — maximize forward velocity while staying upright.**

<!-- VIDEO PLACEHOLDER -->

## Quick start

```bash
# Train (~15 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Ant-Direct-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Ant-Direct-v0 --num_envs 32
```

## Environment variants

| Task ID | Implementation |
|---------|----------------|
| `Isaac-Ant-Direct-v0` | Direct |
| `Isaac-Ant-v0` | Manager-based |

## Source code

- Direct env: `source/isaaclab_tasks/isaaclab_tasks/direct/ant/`
- Manager-based: `source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/ant/`
