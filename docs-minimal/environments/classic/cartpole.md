# Cartpole

**Balance a pole on a cart. The "hello world" of RL in Isaac Lab.**

![Cartpole balancing](../../_static/tasks/classic/cartpole.jpg)

## Quick start

```bash
# Train (~5 min, converges in 150 iterations)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Cartpole-Direct-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Cartpole-Direct-v0 --num_envs 32

# Record video
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Cartpole-Direct-v0 --num_envs 32 --video
```

## Environment config

```python
@configclass
class CartpoleEnvCfg(DirectRLEnvCfg):
    decimation = 2
    episode_length_s = 5.0
    action_scale = 100.0        # Force applied to cart [N]
    action_space = 1            # 1D continuous
    observation_space = 4       # [cart_pos, cart_vel, pole_angle, pole_vel]

    sim: SimulationCfg = SimulationCfg(dt=1 / 120)

    robot_cfg: ArticulationCfg = CARTPOLE_CFG.replace(
        prim_path="/World/envs/env_.*/Robot"
    )

    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4096, env_spacing=4.0
    )

    # Reset if cart moves too far
    max_cart_pos = 3.0                        # [m]
    initial_pole_angle_range = [-0.25, 0.25]  # [rad]

    # Reward scales
    rew_scale_alive = 1.0
    rew_scale_terminated = -2.0
    rew_scale_pole_pos = -1.0
    rew_scale_cart_vel = -0.01
    rew_scale_pole_vel = -0.005
```

## Agent config (RSL-RL PPO)

```python
@configclass
class CartpolePPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 16
    max_iterations = 150
    experiment_name = "cartpole_direct"
    policy = RslRlPpoActorCriticCfg(
        actor_hidden_dims=[32, 32],
        critic_hidden_dims=[32, 32],
        activation="elu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        clip_param=0.2,
        entropy_coef=0.005,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        gamma=0.99,
        lam=0.95,
    )
```

## All variants

| Task ID | Input | Implementation |
|---------|-------|----------------|
| `Isaac-Cartpole-Direct-v0` | State (4D) | Direct |
| `Isaac-Cartpole-v0` | State (4D) | Manager-based |
| `Isaac-Cartpole-RGB-Camera-Direct-v0` | RGB image | Direct |
| `Isaac-Cartpole-Depth-Camera-Direct-v0` | Depth image | Direct |
| `Isaac-Cartpole-RGB-v0` | RGB image | Manager-based |
| `Isaac-Cartpole-RGB-ResNet18-v0` | RGB + ResNet18 encoder | Manager-based |

## Train with different frameworks

=== "RSL-RL"

    ```bash
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
      --task Isaac-Cartpole-Direct-v0 --num_envs 4096
    ```

=== "SKRL"

    ```bash
    ./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py \
      --task Isaac-Cartpole-Direct-v0 --num_envs 4096
    ```

=== "Stable-Baselines3"

    ```bash
    ./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py \
      --task Isaac-Cartpole-Direct-v0 --num_envs 4096
    ```

=== "RL Games"

    ```bash
    ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train.py \
      --task Isaac-Cartpole-Direct-v0 --num_envs 4096
    ```

## Source code

- Direct env: `source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/cartpole_env.py`
- Direct config: `source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/cartpole_env_cfg.py`
- Manager-based: `source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/`
