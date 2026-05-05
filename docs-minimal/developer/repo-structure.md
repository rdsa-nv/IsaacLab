# Repository Structure

**How the Isaac Lab codebase is organized.**

## Top-level layout

```
IsaacLab/
├── source/                  # All Python packages
│   ├── isaaclab/            # Core library
│   ├── isaaclab_tasks/      # Pre-built environments
│   ├── isaaclab_rl/         # RL framework wrappers
│   └── extensions/          # Optional extensions
├── scripts/                 # Runnable scripts
├── docs/                    # Documentation source
├── tools/                   # Build and CI tools
├── docker/                  # Dockerfiles
└── isaaclab.sh              # Main entry point script
```

## Core library (`source/isaaclab/`)

The core package provides all building blocks:

| Module | Purpose | Key classes |
|--------|---------|-------------|
| `assets` | Robot and object management | `Articulation`, `RigidObject`, `DeformableObject` |
| `envs` | Environment base classes | `ManagerBasedRLEnv`, `DirectRLEnv` |
| `managers` | MDP component managers | `ObservationManager`, `RewardManager`, `EventManager` |
| `sensors` | Sensor abstractions | `Camera`, `ContactSensor`, `RayCaster`, `Imu` |
| `sim` | Simulation context and spawners | `SimulationContext`, `UsdFileCfg`, spawner configs |
| `scene` | Multi-env scene management | `InteractiveScene`, `InteractiveSceneCfg` |
| `terrains` | Procedural terrain generation | `TerrainGenerator`, terrain configs |
| `controllers` | Motion controllers | `DifferentialIKController`, `OperationalSpaceController` |
| `actuators` | Actuator models | `ImplicitActuator`, `DCMotor`, `ActuatorNetLSTM` |
| `utils` | Utilities | Math, config, IO, timers |

## Task library (`source/isaaclab_tasks/`)

Pre-built environments organized by category:

```
isaaclab_tasks/
├── locomotion/
│   ├── velocity/          # Velocity tracking (Anymal, Go2, H1, etc.)
│   └── navigation/        # Navigation tasks
├── manipulation/
│   ├── reach/             # Reach target pose
│   ├── lift/              # Pick and lift objects
│   ├── stack/             # Stack objects
│   └── cabinet/           # Open cabinet doors/drawers
├── dexterous/
│   ├── allegro/           # Allegro hand tasks
│   └── shadow_hand/       # Shadow hand in-hand manipulation
├── classic/
│   ├── cartpole/          # Cart-pole balance
│   ├── ant/               # Ant locomotion
│   └── humanoid/          # Humanoid locomotion
└── industrial/
    └── factory/           # Factory automation tasks
```

Each task directory contains:

- `__init__.py` — Gymnasium registration
- `*_env_cfg.py` — Environment configuration
- `agents/` — Per-framework training configs (RSL-RL, SKRL, SB3, RL Games)

## Scripts (`scripts/`)

```
scripts/
├── reinforcement_learning/
│   ├── rsl_rl/            # train.py, play.py for RSL-RL
│   ├── skrl/              # train.py, play.py for SKRL
│   ├── sb3/               # train.py, play.py for SB3
│   └── rl_games/          # train.py, play.py for RL Games
├── tutorials/             # Step-by-step tutorial scripts
│   ├── 01_assets/
│   ├── 02_scene/
│   ├── 03_envs/
│   ├── 04_sensors/
│   └── 05_controllers/
├── tools/                 # Asset converters, utilities
├── environments/          # random_agent.py, list_envs.py
└── teleoperation/         # Teleop scripts
```

## Extensions

Isaac Lab uses a modular extension system. Each extension is a separate Python package:

```bash
# Install an extension
./isaaclab.sh -e rsl_rl

# List available extensions
ls source/extensions/
```

## Configuration pattern

Isaac Lab uses `@configclass` (based on Python dataclasses) throughout:

```
EnvCfg
├── SceneCfg
│   ├── ArticulationCfg (robot)
│   ├── RigidObjectCfg (objects)
│   ├── SensorCfg (cameras, contacts)
│   └── TerrainImporterCfg
├── ObservationsCfg
├── ActionsCfg
├── RewardsCfg
├── TerminationsCfg
├── EventCfg
└── CurriculumCfg
```

Each config is composable — swap any component by replacing its config.
