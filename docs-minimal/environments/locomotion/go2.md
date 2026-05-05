# Unitree Go2

**Velocity tracking with the Unitree Go2 quadruped robot.**

<!-- VIDEO PLACEHOLDER -->
<!-- ![Unitree Go2](../../assets/videos/go2-flat.mp4) -->

## Quick start

```bash
# Train on flat terrain (~30 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Flat-Unitree-Go2-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Velocity-Flat-Unitree-Go2-v0 --num_envs 32

# Record video
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Velocity-Flat-Unitree-Go2-v0 --num_envs 32 --video
```

## Environment variants

| Task ID | Terrain |
|---------|---------|
| `Isaac-Velocity-Flat-Unitree-Go2-v0` | Flat |
| `Isaac-Velocity-Rough-Unitree-Go2-v0` | Rough (terrain curriculum) |

## Train on rough terrain

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Rough-Unitree-Go2-v0 --num_envs 4096
```

## Source code

- Config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2/`
- Agent configs: `source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2/agents/`
- Base env config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/velocity_env_cfg.py`
