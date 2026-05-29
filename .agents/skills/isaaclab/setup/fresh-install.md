# Install

Default to a Newton-focused kitless install. This is the fastest setup and does
not require Isaac Sim or `_isaac_sim`. Use the official docs as backup:

- `docs/source/setup/installation/kitless_installation.rst`
- `docs/source/setup/installation/include/pip_python_virtual_env.rst`

Do not start by running `./isaaclab.sh --help` on a fresh checkout. If no
`env_isaaclab` or active Python 3.12 env exists, the wrapper may fall back to
system Python and fail before help is printed.

## Default Linux Flow

From the Isaac Lab repo root:

```bash
# Install uv first if needed:
# curl -LsSf https://astral.sh/uv/install.sh | sh

uv python install 3.12
uv venv --python 3.12 --seed env_isaaclab
source env_isaaclab/bin/activate
uv pip install --upgrade pip
./isaaclab.sh -i newton,'rl[rsl-rl]'
```

This creates a Python 3.12 `uv` environment, then lets `./isaaclab.sh -i`
install the source subpackages in editable mode with:
- Newton physics packages
- Newton visualizer extras
- RSL-RL through `isaaclab-rl[rsl-rl]`
- no Isaac Sim pip package

If `env_isaaclab` already exists, do not recreate it unless the user asks. Use
the existing environment:

```bash
source env_isaaclab/bin/activate
uv pip install --upgrade pip
./isaaclab.sh -i newton,'rl[rsl-rl]'
```

Do not run `uv pip install -e .` or `uv pip install -e ".[newton,rl]"` from the
repo root. The root `pyproject.toml` is a development/meta project, not the
editable package target; installing it can fail with setuptools flat-layout
package discovery errors. The wrapper uses `uv pip` internally, with the active
venv selected, and installs `source/isaaclab_*` packages directly.

If resolution fails, check the `[tool.uv]`, `[tool.uv.sources]`, and
`[tool.uv.pip]` sections before adding ad hoc index flags.

## Verify

After activation and install:

```bash
./isaaclab.sh --help
./isaaclab.sh -p -c "import sys; print(sys.version)"
./isaaclab.sh -p -c "import isaaclab, isaaclab_newton, isaaclab_rl; print('ok')"
./isaaclab.sh train --rl_library rsl_rl \
  --task Isaac-Cartpole-Direct-v0 \
  --num_envs 16 --max_iterations 10 \
  presets=newton_mjwarp --viz newton
```

Do not inspect install internals or alternate docs unless the command fails.
For setup requests, run the default flow first, then troubleshoot from the
actual error.

## When Not To Use This Default

- If the user needs Isaac Sim RTX rendering, Kit visualizer, ROS, GUI importers,
  or PhysX-only features, use `docs/source/setup/installation/pip_installation.rst`.
- If the user asks for OVRTX/OVPhysX vision workflows, add the relevant `ov` or
  `rtx` extras from `pyproject.toml` after confirming the task and renderer.
