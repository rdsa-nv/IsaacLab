# RL Training

Current develop has unified train/play entrypoints:

```bash
./isaaclab.sh train --rl_library <library> --task <TASK> [args]
./isaaclab.sh play --rl_library <library> --task <TASK> [args]
```

Supported libraries are defined in `scripts/reinforcement_learning/train.py` and
`play.py`:

- `rsl_rl`
- `skrl`
- `sb3`
- `rl_games`
- `rlinf`

The older per-library scripts remain as compatibility wrappers and emit
deprecation guidance. Prefer the unified entrypoints in new instructions.

## Examples

```bash
./isaaclab.sh train --rl_library rsl_rl --task Isaac-Cartpole-v0 --max_iterations 10
./isaaclab.sh train --rl_library sb3 --task Isaac-Cartpole-v0 --num_envs 64
./isaaclab.sh train --rl_library skrl --task Isaac-Cartpole-Direct-v0 --num_envs 4096
./isaaclab.sh train --rl_library rl_games --task Isaac-Cartpole-v0 --max_iterations 10
```

Play examples:

```bash
./isaaclab.sh play --rl_library rsl_rl --task Isaac-Cartpole-v0 --num_envs 32 --checkpoint /path/to/model.pt
./isaaclab.sh play --rl_library skrl --task Isaac-Cartpole-Direct-v0 --num_envs 32 --checkpoint /path/to/model.pt
```

Use the task's registered agent config entry points to choose a compatible
library. CartPole manager-based supports `rsl_rl`, `skrl`, `sb3`, and
`rl_games`; several camera tasks only register camera-capable configs for a
subset of libraries.

## Common Arguments

- `--task`: Gymnasium task id
- `--num_envs`: number of parallel envs
- `--seed`: random seed
- `--max_iterations`: training length for libraries that expose it
- `--checkpoint`: resume or play from a checkpoint where supported
- `--video`, `--video_length`, `--video_interval`: video recording
- `--enable_cameras`: enable camera sensors and dependencies
- `--distributed`: multi-GPU or multi-node support where implemented
- `--device`: simulation device, for example `cuda`, `cuda:0`, or `cpu`

Launcher flags:
- Omit `--viz` for default headless behavior.
- Use `--viz kit,newton,rerun,viser` to enable visualizers.
- Use `--viz none` to force-disable visualizers.
- `--headless` is accepted but deprecated.

## Presets and Overrides

Hydra overrides and typed preset tokens are passed after normal args:

```bash
./isaaclab.sh train --rl_library rsl_rl --task Isaac-Cartpole-v0 env.actions.joint_effort.scale=10.0 agent.seed=2024
./isaaclab.sh train --rl_library skrl --task Isaac-Cartpole-Camera-Presets-Direct-v0 --enable_cameras renderer=newton_renderer presets=rgb
```

If the user asks about "render modes", answer in terms of renderer/data
presets first:
- renderer presets: `isaacsim_rtx_renderer`, `newton_renderer`, `ovrtx_renderer`
- data presets, when defined by the task: `rgb`, `depth`, `albedo`,
  `semantic_segmentation`, `simple_shading_constant_diffuse`,
  `simple_shading_diffuse_mdl`, `simple_shading_full_mdl`

Observation presets can change checkpoint shape. Use the same observation
preset for play that was used for training.

## Logs and Checkpoints

Logs are under `logs/<library>/<experiment_name>/<run>/` for most libraries, but
exact layout is library-specific. Inspect the selected agent config for
`experiment_name` and checkpoint settings.

TensorBoard:

```bash
./isaaclab.sh -p -m tensorboard.main --logdir logs/
```

## Source Anchors

- Unified dispatch: `scripts/reinforcement_learning/common.py`
- Train entrypoint: `scripts/reinforcement_learning/train.py`
- Play entrypoint: `scripts/reinforcement_learning/play.py`
- Multigpu entrypoint: `scripts/reinforcement_learning/train_multigpu.py`
- RL docs: `docs/source/overview/reinforcement-learning/`
- Hydra and presets: `docs/source/features/hydra.rst`
