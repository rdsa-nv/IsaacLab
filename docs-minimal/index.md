# Isaac Lab

**GPU-accelerated robot learning, batteries included.**

Isaac Lab is an open-source framework for training robot policies in simulation using reinforcement learning. It runs thousands of parallel environments on GPU, ships with dozens of pre-built tasks, and integrates with every major RL library.

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

    [:octicons-arrow-right-24: Deployment](concepts/sim-to-real.md)

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

<!-- Placeholder: add a GIF/video of ANYmal walking here -->
<!-- ![ANYmal-C walking](assets/videos/anymal-c-flat.mp4) -->

## What makes Isaac Lab different

| Feature | Isaac Lab | Other sim frameworks |
|---------|-----------|---------------------|
| Parallel envs | 4096+ on a single GPU | Typically CPU-bound |
| Physics | PhysX 5, Newton, OvPhysX | Usually single backend |
| RL libraries | RSL-RL, SKRL, SB3, RL Games | Often framework-locked |
| Policy export | JIT + ONNX out of the box | Manual conversion |
| Sensors | Cameras, LiDAR, contact | Varies |

## Project structure

```
IsaacLab/
├── source/
│   ├── isaaclab/              # Core framework
│   ├── isaaclab_tasks/        # 50+ pre-built environments
│   ├── isaaclab_rl/           # RL framework wrappers
│   └── isaaclab_assets/       # Robot URDF/USD definitions
├── scripts/
│   ├── reinforcement_learning/  # Train & play scripts per framework
│   ├── demos/                   # Pre-made demonstrations
│   └── tutorials/               # Step-by-step learning
└── docs/                        # This documentation
```
