# Allegro Hand

**In-hand cube reorientation with the Wonik Allegro Hand.**

<!-- VIDEO PLACEHOLDER -->
<!-- ![Allegro repose](../../assets/videos/allegro-repose.mp4) -->

## Quick start

=== "Direct"

    ```bash
    # Train (~8 hr, 4096 envs)
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
      --task Isaac-Repose-Cube-Allegro-Direct-v0 --num_envs 4096

    # Evaluate
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Repose-Cube-Allegro-Direct-v0 --num_envs 32
    ```

=== "Manager-based"

    ```bash
    # Train (~8 hr)
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
      --task Isaac-Repose-Cube-Allegro-v0 --num_envs 4096

    # Evaluate
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Repose-Cube-Allegro-v0 --num_envs 32
    ```

## Environment variants

| Task ID | Implementation | Notes |
|---------|----------------|-------|
| `Isaac-Repose-Cube-Allegro-Direct-v0` | Direct | Fastest iteration |
| `Isaac-Repose-Cube-Allegro-v0` | Manager-based | Modular rewards |
| `Isaac-Repose-Cube-Allegro-NoVelObs-v0` | Manager-based | No velocity observations |

## Agent config (RSL-RL PPO)

```python
@configclass
class AllegroHandPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 16
    max_iterations = 10000
    save_interval = 250
    experiment_name = "allegro_hand"
    policy = RslRlPpoActorCriticCfg(
        actor_obs_normalization=True,
        critic_obs_normalization=True,
        actor_hidden_dims=[1024, 512, 256, 128],
        critic_hidden_dims=[1024, 512, 256, 128],
        activation="elu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        clip_param=0.2,
        entropy_coef=0.005,
        learning_rate=5.0e-4,
        gamma=0.99,
        desired_kl=0.016,
    )
```

!!! tip "Training tips"
    - Use observation normalization (`actor_obs_normalization=True`) - critical for dexterous tasks
    - Larger networks ([1024, 512, 256, 128]) are needed for the high-dimensional action space
    - 10,000 iterations minimum for reasonable performance
    - Use `save_interval=250` to keep intermediate checkpoints

## Source code

- Direct env: `source/isaaclab_tasks/isaaclab_tasks/direct/allegro_hand/`
- Manager-based: `source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/inhand/config/allegro_hand/`
