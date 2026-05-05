# Multi-GPU Training

**Scale training across multiple GPUs for faster convergence on complex tasks.**

![Multi-GPU training architecture](../_static/reference-architecture/multi-gpu-training-light.svg)

## Distributed training with RSL-RL

```bash
# 2 GPUs
torchrun --nproc_per_node=2 \
  scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Rough-Anymal-C-v0 \
  --num_envs 4096 --distributed

# 4 GPUs
torchrun --nproc_per_node=4 \
  scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Rough-Anymal-C-v0 \
  --num_envs 4096 --distributed

# Using isaaclab.sh wrapper
./isaaclab.sh -p -m torch.distributed.run --nproc_per_node=2 \
  scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Rough-Anymal-C-v0 \
  --num_envs 4096 --distributed
```

## How it works

- Each GPU runs its own set of parallel environments
- Gradients are synchronized across GPUs after each PPO update
- Seeds are automatically offset per rank to ensure diversity
- The device is auto-resolved per rank (no need for `--device`)

## When to use multi-GPU

| Scenario | Recommendation |
|----------|---------------|
| Simple tasks (cartpole, reach) | Single GPU is fine |
| Locomotion (rough terrain) | 2 GPUs speeds up curriculum |
| Dexterous manipulation | 2-4 GPUs recommended |
| Vision-based tasks | Multi-GPU for throughput |

## Distributed training with SKRL

```bash
torchrun --nproc_per_node=2 \
  scripts/reinforcement_learning/skrl/train.py \
  --task Isaac-Velocity-Rough-Anymal-C-v0 \
  --num_envs 4096 --distributed
```

## Ray/RLlib (hyperparameter tuning)

For large-scale hyperparameter sweeps:

```bash
./isaaclab.sh -p scripts/reinforcement_learning/ray/launch.py \
  --task Isaac-Velocity-Flat-Anymal-C-v0

./isaaclab.sh -p scripts/reinforcement_learning/ray/tuner.py \
  --task Isaac-Velocity-Flat-Anymal-C-v0
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| NCCL timeout | Set `NCCL_SOCKET_IFNAME=eth0` or your interface |
| OOM with multi-GPU | Reduce `--num_envs` per GPU |
| Uneven GPU utilization | Check `CUDA_VISIBLE_DEVICES` |
| Slow startup | First run compiles CUDA kernels; subsequent runs are faster |
