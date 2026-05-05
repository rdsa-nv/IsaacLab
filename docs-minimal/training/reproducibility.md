# Reproducibility

**Control randomness and ensure repeatable training results.**

## Setting seeds

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --seed 42
```

Or in config:

```python
@configclass
class MyEnvCfg(ManagerBasedRLEnvCfg):
    seed = 42
```

## What the seed controls

Setting a seed makes these deterministic:

- PyTorch operations (weight init, dropout)
- NumPy random number generation
- Python `random` module
- Environment initial conditions
- Domain randomization sampling

## What remains non-deterministic

Even with a fixed seed, results may vary due to:

| Source | Why | Impact |
|--------|-----|--------|
| GPU floating-point atomics | Non-deterministic reduction order | Small (~0.1%) |
| cuDNN autotuning | Different algorithm selection | Small |
| NCCL all-reduce | Non-deterministic across ranks | Multi-GPU only |
| Parallel env reset order | Race conditions in reset | Negligible |

## Enabling full determinism

For maximum reproducibility (at a performance cost):

```python
import torch

torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.use_deterministic_algorithms(True)
```

!!! warning
    Full determinism disables some GPU optimizations and can slow training by 10-30%. Use it for debugging and ablation studies, not production training.

## Best practices for reproducible research

### Run multiple seeds

Single-seed results are unreliable. Report mean and standard deviation across seeds:

```bash
for seed in 0 1 2 3 4; do
    ./isaaclab.sh -p train.py --task MyTask --seed $seed --headless &
done
```

### Log everything

Each training run saves its full configuration:

```
logs/rsl_rl/my_task/
  2025-01-15_12-30-00/
    params/
      env_cfg.yaml       # Full environment config
      agent_cfg.yaml     # Full agent config
    model_1000.pt        # Checkpoints
    summaries/           # TensorBoard logs
```

### Version control

Track the exact code version:

```bash
# The training scripts log git hash automatically
git rev-parse HEAD  # Include in your paper's appendix
```

### Checkpoint management

Save checkpoints at regular intervals to analyze learning dynamics:

```python
runner_cfg = OnPolicyRunnerCfg(
    save_interval=500,      # Save every 500 iterations
    max_iterations=5000,
)
```

## Comparing runs

Use TensorBoard to compare across seeds and configurations:

```bash
tensorboard --logdir logs/rsl_rl/my_task/ --port 6006
```

Or Weights & Biases:

```bash
./isaaclab.sh -p train.py --task MyTask --logger wandb --wandb_project my_project
```
