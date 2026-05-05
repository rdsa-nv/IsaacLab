# Install

## System requirements

| Requirement | Minimum |
|------------|---------|
| **OS** | Ubuntu 22.04 / 24.04 (x64) or Windows 11 |
| **GPU** | NVIDIA RTX 3070+ or data center (A100, L40, H100) |
| **GPU VRAM** | 16 GB+ |
| **RAM** | 32 GB+ |
| **Python** | 3.12 |
| **NVIDIA Driver** | 560+ |

## Full install (Isaac Sim + PhysX + Newton)

```bash
# Clone Isaac Lab 3.0
git clone -b v3.0.0-beta https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# Create conda env with Python 3.12
conda create -n isaaclab python=3.12 -y
conda activate isaaclab

# Install Isaac Sim 6.0
pip install isaacsim[all]

# Install Isaac Lab
./isaaclab.sh -i

# Install RL framework
pip install -e "source/isaaclab_rl[rsl-rl]"
```

## Kit-less install (Newton only — no Isaac Sim)

New in 3.0: run Isaac Lab **without** Isaac Sim for Newton-based workflows:

```bash
git clone -b v3.0.0-beta https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

conda create -n isaaclab python=3.12 -y
conda activate isaaclab

# Install Isaac Lab (no Isaac Sim needed)
./isaaclab.sh -i

# Install Newton backend
pip install -e "source/isaaclab[newton]"

# Install RL framework
pip install -e "source/isaaclab_rl[rsl-rl]"
```

**What works without Isaac Sim:**

| Feature | Kit-less (Newton) | Full (Isaac Sim) |
|---------|:-:|:-:|
| Newton physics | Yes | Yes |
| PhysX physics | No | Yes |
| RL training | Yes | Yes |
| RTX rendering | No | Yes |
| Camera sensors | No | Yes |
| Deformable objects | No | Yes |
| URDF/MJCF import | No | Yes |
| Newton visualizer | Yes | Yes |
| Kit visualizer | No | Yes |

## Install RL frameworks

=== "RSL-RL (recommended)"

    ```bash
    pip install -e "source/isaaclab_rl[rsl-rl]"
    ```

=== "SKRL"

    ```bash
    pip install -e "source/isaaclab_rl[skrl]"
    ```

=== "Stable-Baselines3"

    ```bash
    pip install -e "source/isaaclab_rl[sb3]"
    ```

=== "RL Games"

    ```bash
    pip install -e "source/isaaclab_rl[rl-games]"
    ```

## Verify installation

```bash
# With Isaac Sim — opens a window with cartpole training
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Cartpole-Direct-v0 --num_envs 64 --max_iterations 10

# Kit-less (Newton only) — use Newton visualizer
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Cartpole-Direct-v0 --num_envs 64 --max_iterations 10 \
  --viz newton
```

![Verify installation](../_static/setup/verify_install.jpg)

## Docker

```bash
cd docker
./build.sh   # builds the Docker image
./run.sh     # launches container with GPU access
```

## Key dependencies (3.0)

| Package | Version | Notes |
|---------|---------|-------|
| Python | 3.12 | Required minimum |
| Isaac Sim | 6.0.0 | Optional for Newton-only |
| PyTorch | 2.10+ | GPU acceleration |
| NumPy | 2.0+ | Updated from NumPy 1.x |
| Warp | 1.12.0 | GPU compute framework |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: isaacsim` | Install Isaac Sim: `pip install isaacsim[all]` |
| `CUDA out of memory` | Reduce `--num_envs` (try 512 or 1024) |
| `Python version error` | Isaac Lab 3.0 requires Python 3.12 — check `python --version` |
| Slow training | Check GPU utilization: `nvidia-smi` |
| `PhysX out of buffer` | Increase `gpu_found_lost_pairs_capacity` in sim config |
