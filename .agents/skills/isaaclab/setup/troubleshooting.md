# Troubleshooting

Start with the official troubleshooting docs:

- `docs/source/refs/troubleshooting.rst`
- `https://isaac-sim.github.io/IsaacLab/develop/source/refs/troubleshooting.html`

Use this file only as a short agent checklist for issues that often come from
the selected interpreter or checkout, not as a complete troubleshooting catalog.

## Wrong Python

Current develop requires Python 3.12. If `./isaaclab.sh --help` fails with
`ModuleNotFoundError: tomllib` or a Python-version error, the wrapper fell back
to an old system Python.

For a fresh kitless setup, fix it with `uv` directly:

```bash
uv python install 3.12
uv venv --python 3.12 --seed env_isaaclab
source env_isaaclab/bin/activate
uv pip install --upgrade pip
uv pip install -e ".[newton,rl]"
./isaaclab.sh --help
```

## Missing Dependencies

`ModuleNotFoundError: gymnasium`, `rsl_rl`, `skrl`, `rl_games`, or
`stable_baselines3` means the selected env is not installed for the requested
workflow. Run `./isaaclab.sh -i` or a narrower selector such as:

```bash
./isaaclab.sh -i newton,'rl[rsl-rl]'
```

## Mixed Checkouts

Avoid using a venv from another Isaac Lab checkout while testing a fresh
worktree. Mixed `PYTHONPATH` or editable installs can import packages from the
wrong path and produce confusing type or config errors.

Check:

```bash
./isaaclab.sh -p -c "import isaaclab, pathlib; print(pathlib.Path(isaaclab.__file__).resolve())"
```

## Simulation and Training

- If a Newton preset fails, first verify the task declares the relevant preset;
  not every environment supports every backend.
- If camera workflows fail, add `--enable_cameras` and verify renderer/data-type
  support in the task config.
- If play fails to load a checkpoint, use the same task, observation preset, and
  library family that produced the checkpoint.
- For OOM, reduce `--num_envs`, disable cameras, or choose a smaller
  observation preset.
