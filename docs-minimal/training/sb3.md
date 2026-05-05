# Stable-Baselines3

**Popular RL library with extensive documentation and community support.**

SB3 provides reliable implementations of PPO, SAC, A2C, and other algorithms. Good for researchers who want well-tested baselines.

## Install

```bash
pip install -e source/isaaclab_rl[sb3]
```

## Train

```bash
./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py \
  --task <TASK_ID> --num_envs 4096
```

**Examples:**

```bash
# Cartpole
./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py \
  --task Isaac-Cartpole-Direct-v0 --num_envs 4096

# Franka Reach
./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py \
  --task Isaac-Reach-Franka-v0 --num_envs 4096
```

## Evaluate

```bash
./isaaclab.sh -p scripts/reinforcement_learning/sb3/play.py \
  --task <TASK_ID> --num_envs 32
```

## Config format

SB3 configs are YAML files:

```yaml
# Example: sb3_ppo_cfg.yaml
seed: 42
n_timesteps: 100000
policy: MlpPolicy
n_steps: 16
batch_size: 1024
n_epochs: 5
learning_rate: 0.001
gamma: 0.99
gae_lambda: 0.95
clip_range: 0.2
ent_coef: 0.005
vf_coef: 1.0
max_grad_norm: 1.0
policy_kwargs:
  activation_fn: elu
  net_arch: [32, 32]
```

!!! note "Performance note"
    SB3 wraps Isaac Lab envs in a vectorized wrapper. Performance is generally similar to other frameworks for most tasks, but RSL-RL or SKRL may be faster for large-scale locomotion training.

## Source code

- Train script: `scripts/reinforcement_learning/sb3/train.py`
- Play script: `scripts/reinforcement_learning/sb3/play.py`
- Wrapper: `source/isaaclab_rl/isaaclab_rl/sb3.py`
