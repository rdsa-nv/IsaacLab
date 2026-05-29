# Architecture Overview

Isaac Lab is split into source packages under `source/`. Check versions and
package names from each `pyproject.toml`; do not assume a previous release
layout.

## Stack

Think of the current stack as:

```text
OpenUSD assets and scene data -> physics/rendering backends -> Isaac Lab robot learning workflows
```

Isaac Lab is not only an RL environment package. It is the robot learning layer
used for RL, imitation learning, data generation, teleoperation, and related
workflows. The core `isaaclab` package defines shared abstractions and config
patterns; concrete backend behavior lives in backend packages such as
`isaaclab_physx`, `isaaclab_newton`, `isaaclab_ov`, and `isaaclab_ovphysx`.

Core packages on current develop include:

- `source/isaaclab/` - shared app, env, sim, manager, sensor, and actuator abstractions
- `source/isaaclab_tasks/` - built-in tasks and task utilities
- `source/isaaclab_assets/` - robot and asset configs
- `source/isaaclab_rl/` - RL library wrappers
- `source/isaaclab_newton/`, `source/isaaclab_physx/` - physics backends
- `source/isaaclab_ov/`, `source/isaaclab_ovphysx/` - OpenUSD/OpenVDB and OvPhysX integrations
- `source/isaaclab_visualizers/` - Kit, Newton, Rerun, Viser visualizers
- `source/isaaclab_mimic/`, `source/isaaclab_teleop/`, `source/isaaclab_contrib/` - optional workflows

## Environment Workflows

Manager-based environments compose config classes for scene, actions,
observations, rewards, terminations, events, commands, and curriculum. Use this
when you want modular MDP terms and reusable config overrides.

Direct environments implement environment logic in one environment class. Use
this when the task is performance-sensitive, nonstandard, or clearer as explicit
Python methods.

Source anchors:

- `docs/source/overview/core-concepts/task_workflows.rst`
- `source/isaaclab/isaaclab/envs/manager_based_rl_env.py`
- `source/isaaclab/isaaclab/envs/direct_rl_env.py`
- `source/isaaclab_tasks/isaaclab_tasks/manager_based/`
- `source/isaaclab_tasks/isaaclab_tasks/direct/`

## Gym Registration

Tasks are registered with Gymnasium in package `__init__.py` files. For example,
CartPole registrations live in:

- `source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/__init__.py`
- `source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/__init__.py`

Check the registration kwargs for the task config and per-library agent config
entry points before writing training commands.

## Presets and Hydra

Hydra overrides use `env.` and `agent.` prefixes. Current develop also supports
typed preset tokens:

```bash
./isaaclab.sh train --rl_library rsl_rl --task Isaac-Cartpole-v0 physics=newton_mjwarp
./isaaclab.sh train --rl_library skrl --task Isaac-Cartpole-Camera-Presets-Direct-v0 renderer=newton_renderer presets=rgb
```

Preset details are in `docs/source/features/hydra.rst` and
`source/isaaclab_tasks/isaaclab_tasks/utils/hydra.py`.

## Public API Discipline

Follow `AGENTS.md`: use modern type hints, Google-style docstrings, SI units for
public physical quantities, and deprecation before public API removal.
