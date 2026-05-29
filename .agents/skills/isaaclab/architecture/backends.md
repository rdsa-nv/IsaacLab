# Backends and Renderers

Isaac Lab separates task configuration from physics backends, renderers, and
visualizers. Do not infer that a backend works for a task just because the
package exists.

## Rendering Presets Quick Answer

When a user asks for "render modes" or "rendering modes", they usually mean
camera renderer/data presets. Answer this first. Do not start by searching for
`RenderMode`, `render_mode`, or visualizer `set_render_mode` unless the user
explicitly asks about Gymnasium `render_mode` or a visualizer UI dropdown.

Renderer selectors:
- `renderer=default` or `renderer=isaacsim_rtx_renderer`: Isaac Sim RTX
  renderer. This is the default camera renderer and requires Kit.
- `renderer=newton_renderer`: Newton Warp renderer. This is kitless and is the
  usual Newton camera-rendering option.
- `renderer=ovrtx_renderer`: OV RTX renderer. This is kitless when paired with
  compatible physics such as `newton_mjwarp` or `ovphysx`.

Common camera data/AOV presets, when the task defines them:
- `presets=rgb`
- `presets=depth`
- `presets=albedo`
- `presets=semantic_segmentation`
- `presets=simple_shading_constant_diffuse`
- `presets=simple_shading_diffuse_mdl`
- `presets=simple_shading_full_mdl`

Set them with typed selectors after the normal CLI args:

```bash
./isaaclab.sh train --rl_library skrl \
  --task Isaac-Cartpole-Camera-Presets-Direct-v0 \
  --enable_cameras renderer=newton_renderer presets=rgb

./isaaclab.sh train --rl_library skrl \
  --task Isaac-Cartpole-Camera-Presets-Direct-v0 \
  --enable_cameras physics=newton_mjwarp renderer=ovrtx_renderer presets=depth
```

Equivalent broadcast form:

```bash
presets=newton_mjwarp,newton_renderer,rgb
```

Availability is task-specific. The quickest authoritative check is:

```bash
./isaaclab.sh train --rl_library <library> --task <TASK> --help
```

Ground-truth source anchors:
- renderer preset names: `source/isaaclab_tasks/isaaclab_tasks/utils/presets.py`
- CLI selector behavior: `docs/source/features/hydra.rst`
- tested renderer/data combinations: `source/isaaclab_tasks/test/rendering_test_utils.py`
- Kit requirement cases: `source/isaaclab_tasks/test/test_preset_kit_decision.py`

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

For current camera test coverage, RTX/OVRTX paths cover `rgb`, `albedo`,
`depth`, `semantic_segmentation`, and the `simple_shading_*` presets. The
Newton Warp renderer coverage is narrower, commonly `rgb` and `depth`; verify
the target task before promising a data type.

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
