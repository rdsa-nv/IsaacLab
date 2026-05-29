# Verify

Start with commands that do not launch simulation:

```bash
./isaaclab.sh --help
./isaaclab.sh -p .agents/skills/isaaclab/scripts/version_summary.py
./isaaclab.sh -p -c "import isaaclab, isaaclab_newton, isaaclab_rl; print('ok')"
```

Run these only after a Python 3.12 environment is active and the wrapper
install has completed. On a fresh checkout, follow `setup/fresh-install.md`
first.

Use the `version_summary.py` output directly for the final "What you have"
block. Keep it as the grouped table, not a flat key/value dump.
Then include a short "Using it" section with activation and train/play command
examples, but do not run training unless the user approves.

Check packages and task registration with the repo interpreter:

```bash
./isaaclab.sh -p -c "import isaaclab_tasks, isaaclab_rl; print('ok')"
./isaaclab.sh -p scripts/environments/list_envs.py
```

Do not run training smoke tests automatically. Ask first:

```text
Imports and versions check out. Do you want me to run a 10-iteration CartPole
Newton training smoke test now? It can take a few minutes and writes logs and
checkpoints.
```

If the user agrees, prefer the unified entrypoints:

```bash
./isaaclab.sh train --rl_library rsl_rl --task Isaac-Cartpole-Direct-v0 --num_envs 16 --max_iterations 10 presets=newton_mjwarp --headless
./isaaclab.sh play --rl_library rsl_rl --task Isaac-Cartpole-v0 --num_envs 32 --checkpoint /path/to/model.pt
```

Use `--viz kit`, `--viz newton`, `--viz rerun`, or `--viz viser` when you want a
visualizer. Omit `--viz` for default headless behavior. `--headless` still
exists for compatibility but is deprecated.

## Tests

```bash
./isaaclab.sh -p -m pytest source/isaaclab_tasks/test/test_hydra.py
./isaaclab.sh -p -m pytest scripts/reinforcement_learning/test/test_typed_preset_cli_train_play.py
```

If tests import a different checkout through `PYTHONPATH`, stop and fix the
environment before trusting results.
