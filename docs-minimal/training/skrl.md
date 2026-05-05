# SKRL

**Multi-framework RL library supporting PyTorch and JAX backends.**

SKRL provides a clean API for PPO, SAC, TD3, and other algorithms. It supports both PyTorch and JAX, making it useful for research comparisons.

## Install

```bash
pip install -e source/isaaclab_rl[skrl]
```

## Train

```bash
./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py \
  --task <TASK_ID> --num_envs 4096
```

**Examples:**

```bash
# Cartpole
./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py \
  --task Isaac-Cartpole-Direct-v0 --num_envs 4096

# ANYmal-C
./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py \
  --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 4096
```

## Evaluate

```bash
./isaaclab.sh -p scripts/reinforcement_learning/skrl/play.py \
  --task <TASK_ID> --num_envs 32
```

## JAX backend

```bash
./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py \
  --task <TASK_ID> --num_envs 4096 --ml_framework jax
```

## Config format

SKRL configs are YAML files in each task's `agents/` directory:

```yaml
# Example: skrl_ppo_cfg.yaml
seed: 42

models:
  separate: False
  policy:
    class: GaussianMixin
    clip_actions: False
    clip_log_std: True
    min_log_std: -20.0
    max_log_std: 2.0
    initial_log_std: 0.0
    network:
      - name: net
        input: OBSERVATIONS
        layers: [256, 128, 64]
        activations: elu
    output: ACTIONS

agent:
  class: PPO
  rollouts: 24
  learning_epochs: 5
  mini_batches: 4
  discount_factor: 0.99
  lambda: 0.95
  learning_rate: 1.0e-3
  learning_rate_scheduler: KLAdaptiveLR
  learning_rate_scheduler_kwargs:
    kl_threshold: 0.01
  clip_ratio: 0.2
  value_loss_scale: 1.0
  entropy_loss_scale: 0.005
```

## Source code

- Train script: `scripts/reinforcement_learning/skrl/train.py`
- Play script: `scripts/reinforcement_learning/skrl/play.py`
- Wrapper: `source/isaaclab_rl/isaaclab_rl/skrl.py`
