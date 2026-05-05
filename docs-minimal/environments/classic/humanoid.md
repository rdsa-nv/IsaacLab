# Humanoid

**MuJoCo-style humanoid locomotion — walk forward while balancing.**

![Humanoid locomotion](../../_static/tasks/classic/humanoid.jpg)

## Quick start

```bash
# Train (~30 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Humanoid-Direct-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Humanoid-Direct-v0 --num_envs 32
```

## Environment variants

| Task ID | Implementation | Notes |
|---------|----------------|-------|
| `Isaac-Humanoid-Direct-v0` | Direct | Standard locomotion |
| `Isaac-Humanoid-v0` | Manager-based | Modular rewards |
| `Isaac-Humanoid-AMP-Walk-Direct-v0` | Direct | AMP: walk motion |
| `Isaac-Humanoid-AMP-Run-Direct-v0` | Direct | AMP: run motion |
| `Isaac-Humanoid-AMP-Dance-Direct-v0` | Direct | AMP: dance motion |

## Agent config (RSL-RL PPO)

```python
@configclass
class HumanoidPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 32
    max_iterations = 1000
    experiment_name = "humanoid_direct"
    policy = RslRlPpoActorCriticCfg(
        actor_obs_normalization=True,
        critic_obs_normalization=True,
        actor_hidden_dims=[400, 200, 100],
        critic_hidden_dims=[400, 200, 100],
        activation="elu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        clip_param=0.2,
        entropy_coef=0.0,
        learning_rate=1.0e-4,
        desired_kl=0.008,
    )
```

## Source code

- Direct env: `source/isaaclab_tasks/isaaclab_tasks/direct/humanoid/`
- AMP envs: `source/isaaclab_tasks/isaaclab_tasks/direct/humanoid_amp/`
- Manager-based: `source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/humanoid/`
