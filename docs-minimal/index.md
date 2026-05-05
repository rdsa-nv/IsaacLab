# Isaac Lab 3.0

**GPU-accelerated robot learning, batteries included.**

Isaac Lab is an open-source framework for training robot policies in simulation using reinforcement learning. It runs thousands of parallel environments on GPU, ships with dozens of pre-built tasks, and integrates with every major RL library.

![Isaac Lab overview](_static/isaaclab.jpg)

<div class="grid cards" markdown>

-   **Train in 3 commands**

    ---

    Pick a task, pick a framework, hit train.

    ```bash
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
      --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 4096
    ```

    [:octicons-arrow-right-24: Getting started](getting-started/install.md)

-   **50+ environments**

    ---

    Quadrupeds, humanoids, arms, hands, drones — all ready to train.

    [:octicons-arrow-right-24: Environment gallery](environments/index.md)

-   **4 RL frameworks**

    ---

    RSL-RL, SKRL, Stable-Baselines3, RL Games. Same env, swap the backend.

    [:octicons-arrow-right-24: Training guides](training/rsl-rl.md)

-   **Sim-to-real ready**

    ---

    Export to ONNX/JIT, deploy on real hardware.

    [:octicons-arrow-right-24: Deployment](deployment/sim-to-real.md)

</div>

## Quick taste

Train ANYmal-C to walk on flat terrain, then watch it:

```bash
# Train (takes ~30 min on a single GPU)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 4096

# Evaluate the trained policy
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Velocity-Flat-Anymal-C-v0 --num_envs 32
```

![ANYmal-C on flat terrain](_static/tasks/locomotion/anymal_c_flat.jpg)

## What's new in 3.0

| Feature | Details |
|---------|---------|
| **Multi-backend physics** | PhysX + Newton (MuJoCo-Warp) — same code, pick at runtime |
| **Kit-less install** | Run Isaac Lab without Isaac Sim using Newton backend |
| **Python 3.12** | Required minimum (NumPy 2.0+, PyTorch 2.10+) |
| **4 visualizers** | Kit, Newton, Rerun, Viser — any backend with any visualizer |
| **XYZW quaternions** | Aligned with Warp/PhysX/Newton native format |
| **Lazy imports** | Configs load before SimulationApp — faster startup |

See the [3.0 Migration Guide](migration/isaac-lab-3.md) for details.

## What makes Isaac Lab different

| Feature | Isaac Lab | Other sim frameworks |
|---------|-----------|---------------------|
| Parallel envs | 4096+ on a single GPU | Typically CPU-bound |
| Physics backends | PhysX 5, Newton | Usually single backend |
| RL libraries | RSL-RL, SKRL, SB3, RL Games | Often framework-locked |
| Policy export | JIT + ONNX out of the box | Manual conversion |
| Sensors | Cameras, LiDAR, contact, IMU | Varies |
| Install options | Full (Isaac Sim) or kit-less (Newton) | Monolithic |

## Project structure

```
IsaacLab/
├── source/
│   ├── isaaclab/              # Core framework
│   ├── isaaclab_physx/        # PhysX backend (new in 3.0)
│   ├── isaaclab_newton/       # Newton backend (new in 3.0)
│   ├── isaaclab_tasks/        # 50+ pre-built environments
│   ├── isaaclab_rl/           # RL framework wrappers
│   └── isaaclab_assets/       # Robot URDF/USD definitions
├── scripts/
│   ├── reinforcement_learning/  # Train & play scripts per framework
│   ├── demos/                   # Pre-made demonstrations
│   └── tutorials/               # Step-by-step learning
└── docs/                        # This documentation
```
