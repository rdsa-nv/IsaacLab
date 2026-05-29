# Environment Builder

## Choose the Workflow

Manager-based:
- Use when rewards, observations, events, commands, and actions should be
  reusable config terms.
- Start from `source/isaaclab_tasks/isaaclab_tasks/manager_based/`.

Direct:
- Use when explicit methods are clearer or the task has custom stepping logic.
- Start from `source/isaaclab_tasks/isaaclab_tasks/direct/`.

Docs:
- `docs/source/overview/core-concepts/task_workflows.rst`
- `docs/source/tutorials/03_envs/create_manager_rl_env.rst`
- `docs/source/tutorials/03_envs/create_direct_rl_env.rst`
- `docs/source/tutorials/03_envs/register_rl_env_gym.rst`

## Manager-Based Checklist

- Scene config: assets, terrain, lights, cloning, env count.
- Actions config: action terms and scaling.
- Observations config: policy terms and corruption/noise.
- Rewards config: reward terms and weights.
- Terminations config: timeout and failure/success conditions.
- Events/commands/curriculum as needed.
- Gym registration with `env_cfg_entry_point` and per-library agent configs.

## Direct Checklist

- Env cfg subclass of the current direct RL config base.
- Environment class implementing observation, reward, done, reset, and action
  application hooks.
- Gym registration with entry point and agent configs.
- Tests or a one-iteration smoke run when behavior changes.

## Agent Configs

Keep agent configs next to the task under `agents/`. Check the task
registration kwargs to see which libraries are supported:

```bash
rg -n "_cfg_entry_point|gym.register" source/isaaclab_tasks/isaaclab_tasks/<task-path>
```

## Reward Design

Prefer small, named reward terms with observable units and signs. For
manager-based tasks, keep reward functions in an `mdp/` module and wire them
through `RewTerm` configs. For direct tasks, keep reward computation readable
and tensorized.

## Presets

If adding physics, renderer, or observation-mode presets, use the existing
`PresetCfg` pattern and add validation where invalid combinations are likely.
Observation-mode presets can change checkpoint shape; train and play must use
matching presets.

## Verification

Use narrow checks first:

```bash
./isaaclab.sh -p scripts/environments/list_envs.py | rg "<TaskName>"
./isaaclab.sh train --rl_library rsl_rl --task <TaskName> --max_iterations 1
```

Use the library that the task actually registers.
