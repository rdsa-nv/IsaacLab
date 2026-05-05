# Install

## Prerequisites

- **NVIDIA GPU**: RTX 3070+ or data center GPU (A100, L40, H100)
- **NVIDIA Driver**: 535.129.03+
- **Isaac Sim**: 4.5.0+ (installed via Omniverse Launcher)
- **Python**: 3.10
- **OS**: Ubuntu 22.04 or Windows 10/11

## Quick install

```bash
# Clone the repo
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# Create conda env (recommended)
conda create -n isaaclab python=3.10 -y
conda activate isaaclab

# Install Isaac Lab + your preferred RL framework
./isaaclab.sh -i        # core install
pip install -e source/isaaclab_rl[rsl-rl]   # RSL-RL (recommended)
```

## Install with other RL frameworks

=== "RSL-RL (recommended)"

    ```bash
    pip install -e source/isaaclab_rl[rsl-rl]
    ```

=== "SKRL"

    ```bash
    pip install -e source/isaaclab_rl[skrl]
    ```

=== "Stable-Baselines3"

    ```bash
    pip install -e source/isaaclab_rl[sb3]
    ```

=== "RL Games"

    ```bash
    pip install -e source/isaaclab_rl[rl-games]
    ```

## Verify installation

```bash
# Should open a window with a cartpole balancing
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Cartpole-Direct-v0 --num_envs 64 --max_iterations 10
```

If you see the cartpole environment running and training logs in the terminal, you're good to go.

## Docker (alternative)

```bash
cd docker
./build.sh   # builds the Docker image
./run.sh     # launches container with GPU access
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: isaacsim` | Install Isaac Sim via Omniverse Launcher first |
| `CUDA out of memory` | Reduce `--num_envs` (try 512 or 1024) |
| Black screen on launch | Set `export DISPLAY=:0` or use headless mode (`--headless`) |
| Slow training | Ensure you're on GPU: check `nvidia-smi` shows utilization |
