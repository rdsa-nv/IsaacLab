# Backends and Renderers

Isaac Lab separates task configuration from physics backends, renderers, and
visualizers. Do not infer that a backend works for a task just because the
package exists.

## Physics

PhysX and Newton live in separate packages:

- `source/isaaclab_physx/`
- `source/isaaclab_newton/`

Many task configs expose physics presets through `PresetCfg`. Verify the task
before recommending a selector:

```bash
rg -n "newton_mjwarp|Newton|PresetCfg" source/isaaclab_tasks/isaaclab_tasks/<task-path>
```

Common CLI shape:

```bash
./isaaclab.sh train --rl_library rsl_rl --task Isaac-Cartpole-v0 physics=newton_mjwarp
```

Some docs and compatibility scripts still show `presets=newton_mjwarp`; current
Hydra support folds typed selectors into presets where appropriate. Use the task
tests and `docs/source/features/hydra.rst` when exact selector behavior matters.

## Rendering and Cameras

Camera workflows depend on renderer support and selected data types. Check:

- `source/isaaclab/isaaclab/sensors/camera/`
- `source/isaaclab/isaaclab/sensors/ray_caster/`
- task camera config files such as `cartpole_camera_presets_env_cfg.py`

Use `--enable_cameras` for camera sensors. Use renderer presets only when the
task config supports them:

```bash
./isaaclab.sh train --rl_library skrl --task Isaac-Cartpole-Camera-Presets-Direct-v0 --enable_cameras renderer=newton_renderer presets=rgb
```

## Visualizers

Visualizers live in `source/isaaclab_visualizers/isaaclab_visualizers/`:

- `kit`
- `newton`
- `rerun`
- `viser`

```bash
./isaaclab.sh train --rl_library rsl_rl --task Isaac-Cartpole-v0 --viz kit
./isaaclab.sh train --rl_library rsl_rl --task Isaac-Cartpole-v0 --viz none
```

Omit `--viz` for default headless behavior. `--headless` remains accepted but is
deprecated in current `AppLauncher`.

## Docs

- `docs/source/experimental-features/newton-physics-integration/`
- `docs/source/features/hydra.rst`
- `docs/source/overview/core-concepts/physical-backends/`
