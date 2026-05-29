# Install

Use the official docs as source of truth and check the current CLI help before
giving a final command:

```bash
./isaaclab.sh --help
```

Current develop targets Isaac Sim 6.x and Python 3.12:

```bash
rg -n "^requires-python" pyproject.toml source/isaaclab/pyproject.toml
rg -n "Isaac Sim 6.X|Python 3.12" docs/source/setup/installation
```

## Environment

```bash
cd IsaacLab
./isaaclab.sh -u
source env_isaaclab/bin/activate
```

`./isaaclab.sh` auto-selects an active `VIRTUAL_ENV`, active conda env,
`env_isaaclab`, or `_isaac_sim/python.sh` before falling back to system Python.
If system Python is selected and is not 3.12, create or activate the repo env.

## Install Packages

The install command always installs core source packages. Optional submodules and
heavy extras are selected explicitly:

```bash
./isaaclab.sh -i
./isaaclab.sh -i core
./isaaclab.sh -i newton,'rl[rsl-rl]'
./isaaclab.sh -i mimic,teleop,'visualizer[rerun]'
./isaaclab.sh -i 'contrib[rlinf]'
./isaaclab.sh -i 'ov[ovrtx]'
```

Known selector groups from current CLI help:
- Optional submodules: `mimic`, `teleop`
- Extras: `contrib`, `newton`, `ov`, `rl`, `visualizer`
- RL selectors: `rl[rsl-rl|skrl|sb3|rl-games]`
- Visualizer selectors: `visualizer[kit|newton|rerun|viser]`
- OV selectors: `ov[ovrtx|ovphysx|all]`

Quote bracketed selectors on Linux/macOS shells.

## Source and Binary Isaac Sim

If using a binary Isaac Sim extraction, `_isaac_sim` should point at that
extraction. `isaaclab.sh` sources `_isaac_sim/setup_conda_env.sh` when present.
If using pip/uv installation, follow `docs/source/setup/installation/`.
