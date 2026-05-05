# Cloud Deployment

**Run Isaac Lab training on cloud GPU instances.**

## Supported platforms

Isaac Lab runs on any cloud provider with NVIDIA GPUs:

| Provider | GPU instances | Notes |
|----------|-------------|-------|
| NVIDIA DGX Cloud | A100, H100 | Native support, pre-built images |
| AWS | p4d (A100), p5 (H100), g5 (A10G) | Use NGC containers |
| GCP | a2 (A100), a3 (H100) | Use NGC containers |
| Azure | ND (A100), NC (T4/V100) | Use NGC containers |

## Quick start with NGC

```bash
# Pull and run the Isaac Lab container
docker run --rm --gpus all \
    -v $(pwd)/logs:/workspace/isaaclab/logs \
    nvcr.io/nvidia/isaac-lab:latest \
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
        --task Isaac-Velocity-Flat-Anymal-C-v0 \
        --num_envs 4096 --headless
```

## Instance selection guide

| Task type | Recommended GPU | Min VRAM | Envs |
|-----------|----------------|----------|------|
| Locomotion (state-based) | A10G / L40 | 24 GB | 4096 |
| Manipulation (state-based) | A10G / L40 | 24 GB | 2048 |
| Vision RL | A100 / H100 | 40-80 GB | 512-2048 |
| Multi-GPU training | 4x A100 | 4x 40 GB | 16384 |

## Cost optimization

### Spot/preemptible instances

Use spot instances for 60-90% cost savings. Save checkpoints frequently:

```bash
./isaaclab.sh -p train.py \
    --task MyTask \
    --save_interval 100 \
    --headless
```

Resume from checkpoint if preempted:

```bash
./isaaclab.sh -p train.py \
    --task MyTask \
    --checkpoint logs/rsl_rl/my_task/model_latest.pt \
    --headless
```

### Right-size your instance

Don't over-provision. Check GPU utilization during training:

```bash
watch nvidia-smi   # Should show >80% GPU utilization
```

If utilization is low, increase `num_envs` or use a smaller GPU.

## Remote monitoring

### TensorBoard

```bash
# On the cloud instance
tensorboard --logdir logs/ --port 6006 --bind_all

# On your local machine
ssh -L 6006:localhost:6006 user@cloud-instance
# Open http://localhost:6006
```

### Weights & Biases

No port forwarding needed — logs stream to wandb.ai:

```bash
pip install wandb
wandb login

./isaaclab.sh -p train.py \
    --task MyTask \
    --logger wandb \
    --wandb_project my_project \
    --headless
```

## Multi-node cloud training

For large-scale training across multiple GPU instances:

```bash
# Node 0 (master)
torchrun --nnodes=2 --nproc_per_node=4 \
    --node_rank=0 --master_addr=<NODE0_IP> --master_port=29500 \
    scripts/reinforcement_learning/rsl_rl/train.py \
    --task MyTask --num_envs 8192 --distributed --headless

# Node 1
torchrun --nnodes=2 --nproc_per_node=4 \
    --node_rank=1 --master_addr=<NODE0_IP> --master_port=29500 \
    scripts/reinforcement_learning/rsl_rl/train.py \
    --task MyTask --num_envs 8192 --distributed --headless
```

## Tips

- **Always use `--headless`** on cloud instances.
- **Save checkpoints frequently** when using spot instances.
- **Use WandB** for monitoring — it's easier than setting up SSH tunnels for TensorBoard.
- **Start training on a small instance**, then scale up once you've verified the config works.
- **Download only final checkpoints** — avoid syncing full log directories over the network.
