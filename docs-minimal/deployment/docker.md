# Docker Deployment

**Run Isaac Lab training in Docker containers for reproducible, portable environments.**

## Pre-built images

NVIDIA provides Docker images with Isaac Sim and Isaac Lab pre-installed:

```bash
# Pull the latest Isaac Lab image
docker pull nvcr.io/nvidia/isaac-lab:latest
```

## Running training in Docker

```bash
docker run --rm --gpus all \
    -v $(pwd)/logs:/workspace/isaaclab/logs \
    nvcr.io/nvidia/isaac-lab:latest \
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
        --task Isaac-Velocity-Flat-Anymal-C-v0 \
        --num_envs 4096 \
        --headless
```

Key flags:

| Flag | Purpose |
|------|---------|
| `--gpus all` | Pass all GPUs to container |
| `-v $(pwd)/logs:/workspace/isaaclab/logs` | Mount log directory for output |
| `--headless` | Required — no display in container |

## Building a custom image

If you need custom packages or environments:

```dockerfile
FROM nvcr.io/nvidia/isaac-lab:latest

# Install additional Python packages
RUN pip install wandb robomimic

# Copy your custom environments
COPY my_envs/ /workspace/isaaclab/source/extensions/my_envs/

# Install your extension
RUN cd /workspace/isaaclab && \
    ./isaaclab.sh -i my_envs
```

Build and run:

```bash
docker build -t my-isaac-lab .
docker run --rm --gpus all my-isaac-lab \
    ./isaaclab.sh -p train.py --task My-Custom-Task-v0 --headless
```

## Docker Compose for multi-GPU

```yaml
version: "3.8"
services:
  trainer:
    image: nvcr.io/nvidia/isaac-lab:latest
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
              count: 4
    volumes:
      - ./logs:/workspace/isaaclab/logs
    command: >
      torchrun --nnodes=1 --nproc_per_node=4
      scripts/reinforcement_learning/rsl_rl/train.py
      --task Isaac-Velocity-Flat-Anymal-C-v0
      --num_envs 4096 --distributed --headless
```

## Tips

- **Always use `--headless`** in containers — there's no display server.
- **Mount volumes** for logs and checkpoints so they persist after the container exits.
- **Pin image versions** in production: use `nvcr.io/nvidia/isaac-lab:4.5.0` instead of `:latest`.
- **GPU driver compatibility**: The container's CUDA version must be compatible with the host's GPU driver. Check with `nvidia-smi`.
