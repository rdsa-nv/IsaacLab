# Verify

Start with commands that do not launch simulation:

```bash
./isaaclab.sh --help
./isaaclab.sh -p -c "import sys; print(sys.version)"
./isaaclab.sh -p -c "import isaaclab; print(isaaclab.__version__)"
```

Check packages and task registration with the repo interpreter:

```bash
./isaaclab.sh -p -c "import isaaclab_tasks, isaaclab_rl; print('ok')"
./isaaclab.sh -p scripts/environments/list_envs.py
```

For RL command shape, prefer the unified entrypoints:

```bash
./isaaclab.sh train --rl_library rsl_rl --task Isaac-Cartpole-v0 --max_iterations 1
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
