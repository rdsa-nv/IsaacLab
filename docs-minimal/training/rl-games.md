# RL Games

**High-performance RL library originally from NVIDIA.**

RL Games provides PPO and other algorithms with GPU-optimized training. Historically used in IsaacGym.

## Install

```bash
pip install -e source/isaaclab_rl[rl-games]
```

## Train

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train.py \
  --task <TASK_ID> --num_envs 4096
```

## Evaluate

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rl_games/play.py \
  --task <TASK_ID> --num_envs 32
```

## Config format

RL Games uses YAML configs:

```yaml
# Example: rl_games_ppo_cfg.yaml
params:
  seed: 42
  algo:
    name: a2c_continuous
  model:
    name: continuous_a2c_logstd
  network:
    name: actor_critic
    separate: False
    space:
      continuous:
        mu_activation: None
        sigma_activation: None
    mlp:
      units: [256, 128, 64]
      activation: elu
  config:
    name: default
    env_name: rlgpu
    minibatch_size: 4096
    mini_epochs: 5
    lr: 1.0e-3
    gamma: 0.99
    tau: 0.95
    clip_value: True
    clip_value_range: 0.2
    entropy_coef: 0.005
```

## Source code

- Train script: `scripts/reinforcement_learning/rl_games/train.py`
- Play script: `scripts/reinforcement_learning/rl_games/play.py`
- Wrapper: `source/isaaclab_rl/isaaclab_rl/rl_games/`
