# Install

Default to a Newton-focused kitless install. This is the fastest setup and does
not require Isaac Sim or `_isaac_sim`. Use the official docs as backup:

- `docs/source/setup/installation/kitless_installation.rst`
- `docs/source/setup/installation/include/pip_python_virtual_env.rst`

Do not start by running `./isaaclab.sh --help` on a fresh checkout. If no
`env_isaaclab` or active Python 3.12 env exists, the wrapper may fall back to
system Python and fail before help is printed.

Do not spend time searching for every possible environment. Do not inspect
system `python`, `python3`, conda, uv cache directories, or unrelated venv
names unless the default flow fails. Use this rule:
- If `VIRTUAL_ENV` is set, use the active env.
- Else if `env_isaaclab/bin/python` exists, activate `env_isaaclab`.
- Else create `env_isaaclab` with `uv`.

## Default Linux Flow

From the Isaac Lab repo root:

```bash
# Install uv first if needed:
# curl -LsSf https://astral.sh/uv/install.sh | sh

command -v uv >/dev/null || { echo "uv is required"; exit 1; }

if [ -n "${VIRTUAL_ENV:-}" ]; then
  echo "Using active env: $VIRTUAL_ENV"
elif [ -x env_isaaclab/bin/python ]; then
  source env_isaaclab/bin/activate
  echo "Using existing env_isaaclab"
else
  uv python install 3.12
  uv venv --python 3.12 --seed env_isaaclab
  source env_isaaclab/bin/activate
  echo "Created env_isaaclab"
fi

python --version
uv pip install --upgrade pip
./isaaclab.sh -i newton,'rl[rsl-rl]'
```

This creates a Python 3.12 `uv` environment, then lets `./isaaclab.sh -i`
install the source subpackages in editable mode with:
- Newton physics packages
- Newton visualizer extras
- RSL-RL through `isaaclab-rl[rsl-rl]`
- no Isaac Sim pip package

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
./isaaclab.sh -p .agents/skills/isaaclab/scripts/version_summary.py
./isaaclab.sh -p -c "import isaaclab, isaaclab_newton, isaaclab_rl; print('ok')"
```

In the final "what you have" summary, include Python, Isaac Lab, Isaac Lab
Newton, Newton, Warp, Isaac Sim, Kit, Torch/CUDA, RSL-RL, and GPU if detected.
For kitless installs, Isaac Sim and Kit should normally report "not installed".

After these checks pass, ask before launching a training smoke test:

```text
Imports and versions check out. Do you want me to run a 10-iteration CartPole
Newton training smoke test now? It can take a few minutes and writes logs and
checkpoints.
```

Only run training after the user says yes.

Do not inspect install internals or alternate docs unless the command fails.
For setup requests, run the default flow first, then troubleshoot from the
actual error.

## When Not To Use This Default

- If the user needs Isaac Sim RTX rendering, Kit visualizer, ROS, GUI importers,
  or PhysX-only features, use `docs/source/setup/installation/pip_installation.rst`.
- If the user asks for OVRTX/OVPhysX vision workflows, add the relevant `ov` or
  `rtx` extras from `pyproject.toml` after confirming the task and renderer.
