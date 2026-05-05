# Contributing

**How to contribute code, environments, and documentation to Isaac Lab.**

## Getting started

1. Fork the repository on GitHub
2. Clone your fork and set up development (see [Developer Setup](setup.md))
3. Create a feature branch: `git checkout -b username/feature-description`
4. Make your changes
5. Run pre-commit: `./isaaclab.sh -f`
6. Push and open a Pull Request

## Branch naming

Use the format `username/feature-description`:

```bash
git checkout -b jdoe/add-spot-env
git checkout -b jdoe/fix-contact-sensor
```

## Code style

- **Python**: PEP 8, enforced by pre-commit hooks
- **Type hints**: Use modern syntax (`x | None` not `Optional[x]`)
- **Docstrings**: Google style
- **Naming**: 
  - Classes: `CamelCase`, grouped by domain (`ActuatorNetLSTM` not `LSTMActuatorNet`)
  - Methods: `snake_case`, noun before modifier (`set_joint_position_target` not `set_target_joint_position`)
  - CLI args: `snake_case`

## Adding a new environment

1. Create a directory under the appropriate category in `source/isaaclab_tasks/`:

```
isaaclab_tasks/locomotion/velocity/my_robot/
├── __init__.py           # Gymnasium registration
├── my_robot_env_cfg.py   # Environment config
└── agents/
    ├── rsl_rl_ppo_cfg.py   # RSL-RL config
    └── skrl_ppo_cfg.yaml   # SKRL config
```

2. Define the environment config:

```python
@configclass
class MyRobotEnvCfg(ManagerBasedRLEnvCfg):
    scene: MyRobotSceneCfg = MyRobotSceneCfg(num_envs=4096)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
```

3. Register with Gymnasium:

```python
gym.register(
    id="Isaac-Velocity-MyRobot-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={"env_cfg_entry_point": f"{__name__}:MyRobotEnvCfg"},
)
```

4. Test: `./isaaclab.sh -p scripts/environments/random_agent.py --task Isaac-Velocity-MyRobot-v0`

## Changelog

Each PR must include a changelog fragment:

```bash
# Create fragment file
echo "Added :class:\`~isaaclab_tasks.locomotion.velocity.MyRobotEnvCfg\` for MyRobot." \
    > source/isaaclab_tasks/changelog.d/username-add-myrobot.rst
```

Fragment format:

```rst
Added
^^^^^

* Added :class:`~isaaclab_tasks.locomotion.velocity.MyRobotEnvCfg` for MyRobot velocity tracking.
```

Categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`.

## Pull request guidelines

- Keep PRs focused — one feature or fix per PR
- Include tests for new functionality
- Update documentation if adding public API
- Add changelog fragment
- Run `./isaaclab.sh -f` before pushing
- Reference related issues in the PR description

## File headers

All new files must include the copyright header:

```python
# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
```

## Testing

Write tests for new features:

```python
# source/isaaclab/test/test_my_feature.py

class TestMyFeature:
    def test_basic_functionality(self):
        ...

    def test_edge_case(self):
        ...
```

Run your tests:

```bash
./isaaclab.sh -p -m pytest source/isaaclab/test/test_my_feature.py -v
```
