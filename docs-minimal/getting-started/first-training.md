# Train Your First Policy

**Goal**: Train a cartpole to balance, then watch it. Takes 5 minutes.

## 1. Train

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Cartpole-Direct-v0 \
  --num_envs 4096 \
  --max_iterations 150
```

This trains PPO across 4096 parallel cartpoles. Logs go to `logs/rsl_rl/cartpole_direct/`.

<!-- VIDEO PLACEHOLDER: cartpole training visualization -->
<!-- ![Cartpole training](../assets/videos/cartpole-training.mp4) -->

## 2. Evaluate

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Cartpole-Direct-v0 \
  --num_envs 32
```

The script automatically loads the latest checkpoint and runs the policy.

## 3. Record a video

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Cartpole-Direct-v0 \
  --num_envs 32 \
  --video --video_length 200
```

Video saved to `logs/rsl_rl/cartpole_direct/<run>/videos/play/`.

## 4. Export the policy

After `play.py` runs, it automatically exports:

- `logs/rsl_rl/cartpole_direct/<run>/exported/policy.pt` (TorchScript JIT)
- `logs/rsl_rl/cartpole_direct/<run>/exported/policy.onnx` (ONNX)

## What just happened?

| Parameter | Value | Why |
|-----------|-------|-----|
| `--task Isaac-Cartpole-Direct-v0` | Environment ID | Registered via `gymnasium.register()` |
| `--num_envs 4096` | Parallel sims | More envs = more data per step = faster training |
| `--max_iterations 150` | PPO updates | Cartpole converges fast |

The training used this config under the hood:

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
        learning_rate=1.0e-3,
        gamma=0.99,
        lam=0.95,
    )
```

## Next steps

Now try something harder:

```bash
# ANYmal quadruped walking (~30 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 4096

# Franka robot opening a cabinet (~45 min)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Franka-Cabinet-Direct-v0 --num_envs 4096
```

Browse the [Environment Gallery](../environments/index.md) to see all available tasks.
