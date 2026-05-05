# Performance Tuning

**Optimize simulation speed and GPU utilization for faster training.**

## Quick wins

| Optimization | Speedup | Effort |
|-------------|---------|--------|
| Increase `num_envs` | 2-10x | Trivial |
| Use `@torch.jit.script` for rewards | 1.2-2x | Low |
| Reduce `decimation` | 1.5-3x | Low |
| Disable rendering (`--viz none`) | 1.3-2x | Trivial |
| Use instanceable assets | Memory savings | Low |
| Tiled camera rendering | 5-20x for vision | Medium |

## Scale environment count

The single biggest performance lever. GPU utilization increases with more parallel environments:

```bash
# Start with powers of 2
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --num_envs 4096 \
    --headless
```

**Guidelines:**

| GPU VRAM | Recommended `num_envs` (locomotion) | Vision RL |
|----------|-------------------------------------|-----------|
| 8 GB | 512-1024 | 64-128 |
| 24 GB | 2048-4096 | 256-512 |
| 48 GB | 4096-8192 | 512-2048 |
| 80 GB | 8192-16384 | 2048-4096 |

## JIT-compile reward functions

Extract reward computation into `@torch.jit.script` functions (direct environments only):

```python
@torch.jit.script
def compute_rewards(
    joint_pos: torch.Tensor,
    joint_vel: torch.Tensor,
    actions: torch.Tensor,
    reset_buf: torch.Tensor,
) -> torch.Tensor:
    reward = 1.0 - 0.1 * torch.sum(joint_vel ** 2, dim=-1)
    reward *= ~reset_buf
    return reward
```

## Decimation

Decimation controls how many physics steps run per RL step. Higher decimation = more physics fidelity but slower training:

```python
@configclass
class MyEnvCfg(DirectRLEnvCfg):
    decimation = 4          # 4 physics steps per RL step
    sim = SimulationCfg(dt=0.005)  # 200 Hz physics
    # Effective control rate: 200/4 = 50 Hz
```

Reduce decimation if your task doesn't need high-frequency control.

## Disable visualization

Disable rendering entirely for pure training:

```bash
./isaaclab.sh -p train.py --task MyTask --viz none
```

!!! note
    The old `--headless` flag still works but `--viz none` is preferred in 3.0.

## Physics backend selection

| Backend | Speed | Features | When to use |
|---------|-------|----------|-------------|
| PhysX (GPU) | Fast | Full featured | Default for training |
| Newton | Faster | Limited soft body | Locomotion, simple manipulation |
| PhysX (CPU) | Slow | Full featured | Debugging only |

```bash
# Use Newton for faster locomotion training
./isaaclab.sh -p train.py --task MyTask --physics_backend newton
```

## Profiling

### Built-in timer

```python
import isaaclab.utils.timer as timer_utils

with timer_utils.Timer("my_operation"):
    expensive_computation()

# Prints elapsed time
```

### NVIDIA Nsight

For deep GPU profiling:

```bash
nsys profile -o report ./isaaclab.sh -p train.py --task MyTask --num_envs 1024 --viz none
```

## Common bottlenecks

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| GPU utilization < 50% | Too few envs | Increase `num_envs` |
| OOM errors | Too many envs or cameras | Reduce `num_envs`, use tiled rendering |
| Slow episode resets | Complex reset logic | Batch reset operations |
| Slow observations | Python loops over envs | Use vectorized tensor ops |
| Training slower than sim | RL framework overhead | Check batch size, increase `num_steps_per_env` |

## Multi-GPU training

For tasks that exceed single-GPU memory, use distributed training:

```bash
torchrun --nnodes=1 --nproc_per_node=4 \
    scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --num_envs 4096 \
    --distributed
```

Each GPU runs its own simulation with `num_envs / num_gpus` environments. See [Multi-GPU Training](../training/multi-gpu.md) for details.
