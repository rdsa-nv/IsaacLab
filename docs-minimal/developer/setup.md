# Developer Setup

**Set up Isaac Lab for development: editable installs, pre-commit hooks, and testing.**

## Clone and install (editable)

```bash
git clone -b v3.0.0-beta https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# Create conda environment — Python 3.12 required for 3.0
conda create -n isaaclab python=3.12 -y
conda activate isaaclab

# Install Isaac Sim 6.0
pip install isaacsim[all]

# Install Isaac Lab in editable mode
./isaaclab.sh -i

# Install RL framework
pip install -e "source/isaaclab_rl[rsl-rl]"
```

## Pre-commit hooks

Isaac Lab uses pre-commit for linting and formatting. **Always run before committing:**

```bash
# Check all files
./isaaclab.sh -f

# Workflow:
# 1. Make changes
# 2. Run ./isaaclab.sh -f
# 3. If files were modified, review changes
# 4. git add <modified files>
# 5. Run ./isaaclab.sh -f again (should pass clean)
# 6. git commit
```

## Running tests

```bash
# Run a specific test file
./isaaclab.sh -p -m pytest source/isaaclab/test/test_my_feature.py

# Run a specific test method
./isaaclab.sh -p -m pytest source/isaaclab/test/test_my_feature.py::test_method

# Run all tests (heavy — avoid unless needed)
./isaaclab.sh -t
```

## IDE setup

### VS Code

Recommended extensions:

- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)

Settings for Isaac Lab:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/_isaac_sim/python.sh",
    "python.analysis.extraPaths": [
        "${workspaceFolder}/source/isaaclab/isaaclab",
        "${workspaceFolder}/source/isaaclab_tasks/isaaclab_tasks"
    ]
}
```

## Project structure overview

```
IsaacLab/
  source/
    isaaclab/              # Core library (backend-agnostic API)
      isaaclab/
        assets/            # Articulation, RigidObject
        envs/              # ManagerBasedRLEnv, DirectRLEnv
        managers/          # Observation, Action, Reward, Event managers
        sensors/           # Camera, Contact, IMU, PVA, RayCaster
        sim/               # SimulationContext, spawners
        terrains/          # Terrain generators
        controllers/       # IK, OSC controllers
        utils/             # Math, config, IO utilities
    isaaclab_physx/        # PhysX backend implementation (new in 3.0)
    isaaclab_newton/       # Newton backend implementation (new in 3.0)
    isaaclab_tasks/        # Pre-built environments
    isaaclab_rl/           # RL framework wrappers
    isaaclab_assets/       # Robot USD/URDF assets
  scripts/
    reinforcement_learning/  # Training/play scripts per framework
    tutorials/               # Tutorial scripts
    tools/                   # Asset converters, quaternion migration tool
    environments/            # random_agent.py, etc.
  docs/                      # Documentation source
```

## Useful commands

| Command | Purpose |
|---------|---------|
| `./isaaclab.sh -p script.py` | Run a Python script with Isaac Lab |
| `./isaaclab.sh -i` | Install Isaac Lab (editable) |
| `./isaaclab.sh -e <ext>` | Install an extension |
| `./isaaclab.sh -f` | Run pre-commit checks |
| `./isaaclab.sh -t` | Run all tests |
| `./isaaclab.sh -d` | Build API documentation |
| `./isaaclab.sh -p -c "code"` | Run inline Python |
