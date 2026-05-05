# Franka Reach

**Move the Franka end-effector to a randomly sampled target pose.**

<!-- VIDEO PLACEHOLDER -->

## Quick start

```bash
# Train (~20 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Reach-Franka-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Reach-Franka-v0 --num_envs 32
```

## Environment variants

| Task ID | Controller |
|---------|-----------|
| `Isaac-Reach-Franka-v0` | Joint position |
| `Isaac-Reach-Franka-IK-Abs-v0` | IK (absolute) |
| `Isaac-Reach-Franka-IK-Rel-v0` | IK (relative) |
| `Isaac-Reach-Franka-OSC-v0` | Operational Space Control |

## Agent config (RSL-RL PPO)

```python
@configclass
class FrankaReachPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24
    max_iterations = 1000
    experiment_name = "franka_reach"
    policy = RslRlPpoActorCriticCfg(
        actor_hidden_dims=[64, 64],
        critic_hidden_dims=[64, 64],
        activation="elu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        clip_param=0.2,
        entropy_coef=0.001,
        num_learning_epochs=8,
        learning_rate=1.0e-3,
    )
```

## Source code

- Config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/reach/config/franka/`
