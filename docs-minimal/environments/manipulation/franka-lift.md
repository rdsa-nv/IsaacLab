# Franka Lift

**Pick up a cube and move it to a target position using the Franka Emika Panda arm.**

<!-- VIDEO PLACEHOLDER -->
<!-- ![Franka lifting cube](../../assets/videos/franka-lift.mp4) -->

## Quick start

```bash
# Train (~45 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Lift-Cube-Franka-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Lift-Cube-Franka-v0 --num_envs 32

# Record video
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Lift-Cube-Franka-v0 --num_envs 32 --video
```

## Environment variants

| Task ID | Controller | Object |
|---------|-----------|--------|
| `Isaac-Lift-Cube-Franka-v0` | Joint position | Cube |
| `Isaac-Lift-Cube-Franka-IK-Abs-v0` | IK (absolute) | Cube |
| `Isaac-Lift-Cube-Franka-IK-Rel-v0` | IK (relative) | Cube |
| `Isaac-Lift-Teddy-Bear-Franka-IK-Abs-v0` | IK (absolute) | Teddy bear |

## Agent config (RSL-RL PPO)

```python
@configclass
class LiftCubePPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24
    max_iterations = 1500
    experiment_name = "franka_lift"
    policy = RslRlPpoActorCriticCfg(
        actor_hidden_dims=[256, 128, 64],
        critic_hidden_dims=[256, 128, 64],
        activation="elu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        clip_param=0.2,
        entropy_coef=0.006,
        learning_rate=1.0e-4,
        gamma=0.98,
        lam=0.95,
    )
```

## Rewards

| Reward | Weight | Description |
|--------|--------|-------------|
| Reaching object | 1.0 | EE distance to cube |
| Lifting object | 15.0 | Height above table |
| Goal tracking | 16.0 | Distance to target pose |
| Action rate penalty | -0.01 | Smooth actions |
| Joint velocity penalty | -0.001 | Energy efficiency |

## Source code

- Config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/lift/lift_env_cfg.py`
- Franka config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/lift/config/franka/`
- Direct version: `source/isaaclab_tasks/isaaclab_tasks/direct/franka_cabinet/` (cabinet variant)
