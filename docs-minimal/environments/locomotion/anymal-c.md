# ANYmal-C Quadruped

**Velocity tracking on flat and rough terrain with the ANYbotics ANYmal-C quadruped robot.**

![ANYmal-C on flat terrain](../../_static/tasks/locomotion/anymal_c_flat.jpg)

![ANYmal-C on rough terrain](../../_static/tasks/locomotion/anymal_c_rough.jpg)

!!! info "Checkpoint available"
    Pre-trained checkpoints can be loaded with `--use_pretrained_checkpoint` flag.

## Quick start

=== "Flat terrain"

    ```bash
    # Train (~30 min, 4096 envs)
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
      --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 4096

    # Evaluate
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 32

    # Record video
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 32 --video
    ```

=== "Rough terrain"

    ```bash
    # Train (~2 hr, 4096 envs)
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
      --task Isaac-Velocity-Rough-Anymal-C-v0 --num_envs 4096

    # Evaluate
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Velocity-Rough-Anymal-C-v0 --num_envs 32

    # Record video
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Velocity-Rough-Anymal-C-v0 --num_envs 32 --video
    ```

=== "Pre-trained checkpoint"

    ```bash
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 32 \
      --use_pretrained_checkpoint
    ```

## Environment variants

| Task ID | Terrain | Implementation | Notes |
|---------|---------|----------------|-------|
| `Isaac-Velocity-Flat-Anymal-C-v0` | Flat | Manager-based | Recommended starting point |
| `Isaac-Velocity-Rough-Anymal-C-v0` | Rough | Manager-based | Terrain curriculum |
| `Isaac-Velocity-Flat-Anymal-C-Direct-v0` | Flat | Direct | Single-file, faster iteration |
| `Isaac-Velocity-Rough-Anymal-C-Direct-v0` | Rough | Direct | Single-file |

## Agent config (RSL-RL PPO)

=== "Flat"

    ```python
    @configclass
    class AnymalCFlatPPORunnerCfg(RslRlOnPolicyRunnerCfg):
        num_steps_per_env = 24
        max_iterations = 300
        experiment_name = "anymal_c_flat"
        policy = RslRlPpoActorCriticCfg(
            actor_hidden_dims=[128, 128, 128],
            critic_hidden_dims=[128, 128, 128],
            activation="elu",
        )
        algorithm = RslRlPpoAlgorithmCfg(
            clip_param=0.2,
            entropy_coef=0.005,
            learning_rate=1.0e-3,
            gamma=0.99,
            lam=0.95,
            desired_kl=0.01,
        )
    ```

=== "Rough"

    ```python
    @configclass
    class AnymalCRoughPPORunnerCfg(RslRlOnPolicyRunnerCfg):
        num_steps_per_env = 24
        max_iterations = 1500
        experiment_name = "anymal_c_rough"
        policy = RslRlPpoActorCriticCfg(
            actor_hidden_dims=[512, 256, 128],
            critic_hidden_dims=[512, 256, 128],
            activation="elu",
        )
        algorithm = RslRlPpoAlgorithmCfg(
            clip_param=0.2,
            entropy_coef=0.005,
            learning_rate=1.0e-3,
            gamma=0.99,
            lam=0.95,
            desired_kl=0.01,
        )
    ```

## Observations

| Observation | Dimension | Description |
|-------------|-----------|-------------|
| Base linear velocity | 3 | Body frame velocity [m/s] |
| Base angular velocity | 3 | Body frame angular velocity [rad/s] |
| Projected gravity | 3 | Gravity in body frame |
| Velocity commands | 3 | Target (vx, vy, yaw rate) |
| Joint positions | 12 | Relative to default [rad] |
| Joint velocities | 12 | [rad/s] |
| Actions (previous) | 12 | Last applied actions |
| Height scan | 187 | Ray-cast terrain heights (rough only) |

## Rewards

| Reward | Weight | Description |
|--------|--------|-------------|
| Linear velocity tracking | 1.0 | Track commanded vx, vy |
| Angular velocity tracking | 0.5 | Track commanded yaw rate |
| Linear velocity penalty (z) | -2.0 | Penalize vertical bouncing |
| Angular velocity penalty (xy) | -0.05 | Penalize roll/pitch rate |
| Joint torques | -0.0001 | Energy efficiency |
| Joint acceleration | -2.5e-7 | Smooth motion |
| Action rate | -0.01 | Smooth actions |
| Feet air time | 0.5 | Encourage gait |
| Undesired contacts | -1.0 | Penalize body contact |
| Flat orientation | -5.0 | Keep body level |

## Training with other frameworks

=== "SKRL"

    ```bash
    ./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py \
      --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 4096
    ```

=== "RL Games"

    ```bash
    ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train.py \
      --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 4096
    ```

## Source code

- Environment: `source/isaaclab_tasks/isaaclab_tasks/direct/anymal_c/anymal_c_env.py`
- Config: `source/isaaclab_tasks/isaaclab_tasks/direct/anymal_c/anymal_c_env_cfg.py`
- Manager-based config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/velocity_env_cfg.py`
- Agent configs: `source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/anymal_c/agents/`
