# Examples and Templates

Prefer copying from current source examples over writing structure from memory.

## Manager-Based Examples

- CartPole: `source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/`
- Locomotion: `source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/`
- Manipulation: `source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/`

## Direct Examples

- CartPole: `source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/`
- CartPole camera presets: `source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/cartpole_camera_presets_env_cfg.py`
- Showcase tasks: `source/isaaclab_tasks/isaaclab_tasks/direct/cartpole_showcase/`

## Generated Templates

Use:

```bash
./isaaclab.sh --new
```

or inspect template sources directly:

- `tools/template/`
- `tools/template/templates/extension/`
- `tools/template/templates/external/`

## What to Copy

- `__init__.py` gym registration pattern
- env cfg class
- env implementation or MDP terms
- `agents/` per-framework RL configs
- tests if nearby

## What to Recheck

- Gym IDs and registration kwargs
- class names and import paths
- asset paths
- experiment names in agent configs
- physics/renderer presets
- whether the task supports the selected RL library

## Search Patterns

```bash
rg -n "gym.register|env_cfg_entry_point|rsl_rl_cfg_entry_point|skrl_cfg_entry_point|sb3_cfg_entry_point|rl_games_cfg_entry_point" source/isaaclab_tasks
rg -n "class .*EnvCfg|PresetCfg|validate_config" source/isaaclab_tasks/isaaclab_tasks
```
