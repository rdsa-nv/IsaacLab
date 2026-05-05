# RSL-RL

**The recommended RL framework for Isaac Lab. On-policy PPO with GPU-accelerated training.**

RSL-RL is the default choice for locomotion and most Isaac Lab tasks. It provides PPO with adaptive learning rate scheduling, observation normalization, and symmetry augmentation.

## Install

```bash
pip install -e source/isaaclab_rl[rsl-rl]
```

## Train

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task <TASK_ID> --num_envs 4096
```

**Examples:**

```bash
# Quadruped locomotion
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 4096

# Manipulation
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Lift-Cube-Franka-v0 --num_envs 4096

# Dexterous
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Repose-Cube-Allegro-Direct-v0 --num_envs 4096
```

## Evaluate

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task <TASK_ID> --num_envs 32
```

The play script automatically:

1. Loads the latest checkpoint from `logs/rsl_rl/<experiment_name>/`
2. Runs the policy in inference mode
3. Exports to JIT (`policy.pt`) and ONNX (`policy.onnx`)

## Record video

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task <TASK_ID> --num_envs 32 --video --video_length 200
```

## Resume training

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task <TASK_ID> --num_envs 4096 \
  --load_run <run_name> --resume
```

## Use a pre-trained checkpoint

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task <TASK_ID> --use_pretrained_checkpoint
```

## Key CLI arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--task` | Required | Gymnasium environment ID |
| `--num_envs` | From config | Number of parallel environments |
| `--max_iterations` | From config | Training iterations |
| `--seed` | From config | Random seed |
| `--video` | `false` | Record training videos |
| `--video_interval` | 2000 | Steps between video recordings |
| `--video_length` | 200 | Video length in steps |
| `--distributed` | `false` | Multi-GPU training |
| `--device` | `cuda:0` | Device for training |
| `--resume` | `false` | Resume from checkpoint |
| `--load_run` | Latest | Specific run to load |

## Config anatomy

Every RSL-RL training is governed by a `RslRlOnPolicyRunnerCfg`:

```python
from isaaclab_rl.rsl_rl import (
    RslRlOnPolicyRunnerCfg,
    RslRlPpoActorCriticCfg,
    RslRlPpoAlgorithmCfg,
)

@configclass
class MyPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    # How many env steps to collect before each PPO update
    num_steps_per_env = 24

    # Total PPO updates
    max_iterations = 1500

    # Save checkpoint every N iterations
    save_interval = 50

    # Experiment name (used for log directory)
    experiment_name = "my_experiment"

    # Network architecture
    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_obs_normalization=False,   # Running mean/std normalization
        critic_obs_normalization=False,
        actor_hidden_dims=[256, 128, 64],
        critic_hidden_dims=[256, 128, 64],
        activation="elu",
    )

    # PPO hyperparameters
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.005,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",     # Adaptive LR based on KL divergence
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )
```

## Hyperparameter guide

| Task type | Network dims | LR | Iterations | Notes |
|-----------|-------------|-----|------------|-------|
| Simple control | [32, 32] | 1e-3 | 150 | Cartpole, pendulums |
| Locomotion (flat) | [128, 128, 128] | 1e-3 | 300 | Fast convergence |
| Locomotion (rough) | [512, 256, 128] | 1e-3 | 1500 | Needs larger network |
| Manipulation | [256, 128, 64] | 1e-4 to 5e-4 | 400-1500 | Lower LR helps |
| Dexterous | [1024, 512, 256, 128] | 5e-4 | 10000+ | Use obs normalization |

## Log directory structure

```
logs/rsl_rl/<experiment_name>/
└── <timestamp>_<run_name>/
    ├── params/
    │   ├── env.yaml           # Environment config dump
    │   └── agent.yaml         # Agent config dump
    ├── model_<iter>.pt        # Checkpoints
    ├── videos/                # If --video was used
    └── exported/
        ├── policy.pt          # TorchScript JIT
        └── policy.onnx        # ONNX export
```

## Source code

- Train script: `scripts/reinforcement_learning/rsl_rl/train.py`
- Play script: `scripts/reinforcement_learning/rsl_rl/play.py`
- CLI args: `scripts/reinforcement_learning/rsl_rl/cli_args.py`
- Wrapper: `source/isaaclab_rl/isaaclab_rl/rsl_rl/`
