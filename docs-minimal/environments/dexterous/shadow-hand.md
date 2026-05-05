# Shadow Hand

**In-hand cube reorientation with the Shadow Dexterous Hand. Multiple observation modes including vision.**

<!-- VIDEO PLACEHOLDER -->
<!-- ![Shadow hand repose](../../assets/videos/shadow-hand-repose.mp4) -->

## Quick start

```bash
# Train (~8 hr)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Repose-Cube-Shadow-Direct-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Repose-Cube-Shadow-Direct-v0 --num_envs 32
```

## Environment variants

| Task ID | Policy Type | Notes |
|---------|-------------|-------|
| `Isaac-Repose-Cube-Shadow-Direct-v0` | Symmetric (state) | Default, same obs for actor & critic |
| `Isaac-Repose-Cube-Shadow-OpenAI-FF-Direct-v0` | Asymmetric FF | Privileged critic observations |
| `Isaac-Repose-Cube-Shadow-OpenAI-LSTM-Direct-v0` | Asymmetric LSTM | Recurrent policy |
| `Isaac-Repose-Cube-Shadow-Vision-Direct-v0` | Vision-based | Camera input |
| `Isaac-Shadow-Hand-Over-Direct-v0` | Two-hand pass | Object handover between two hands |

## Agent config (RSL-RL PPO)

=== "Symmetric"

    ```python
    @configclass
    class ShadowHandPPORunnerCfg(RslRlOnPolicyRunnerCfg):
        num_steps_per_env = 16
        max_iterations = 10000
        experiment_name = "shadow_hand"
        policy = RslRlPpoActorCriticCfg(
            actor_obs_normalization=True,
            actor_hidden_dims=[512, 512, 256, 128],
            critic_hidden_dims=[512, 512, 256, 128],
            activation="elu",
        )
        algorithm = RslRlPpoAlgorithmCfg(
            clip_param=0.2,
            entropy_coef=0.005,
            learning_rate=5.0e-4,
            desired_kl=0.016,
        )
    ```

=== "Asymmetric FF"

    ```python
    @configclass
    class ShadowHandAsymFFPPORunnerCfg(RslRlOnPolicyRunnerCfg):
        num_steps_per_env = 16
        max_iterations = 10000
        experiment_name = "shadow_hand_openai_ff"
        policy = RslRlPpoActorCriticCfg(
            actor_hidden_dims=[400, 400, 200, 100],
            critic_hidden_dims=[512, 512, 256, 128],
            activation="elu",
        )
    ```

=== "Vision"

    ```python
    @configclass
    class ShadowHandVisionFFPPORunnerCfg(RslRlOnPolicyRunnerCfg):
        num_steps_per_env = 64
        max_iterations = 50000
        experiment_name = "shadow_hand_vision"
        policy = RslRlPpoActorCriticCfg(
            actor_hidden_dims=[1024, 512, 512, 256, 128],
            critic_hidden_dims=[1024, 512, 512, 256, 128],
        )
    ```

## Source code

- Environment: `source/isaaclab_tasks/isaaclab_tasks/direct/shadow_hand/`
- Hand-over: `source/isaaclab_tasks/isaaclab_tasks/direct/shadow_hand_over/`
