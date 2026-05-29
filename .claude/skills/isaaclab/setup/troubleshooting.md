# Troubleshooting

## Wrong Python

Current develop requires Python 3.12. If `./isaaclab.sh --help` fails with
`ModuleNotFoundError: tomllib` or a Python-version error, the wrapper fell back
to an old system Python.

Fix by activating or creating the repo env:

```bash
./isaaclab.sh -u
source env_isaaclab/bin/activate
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
