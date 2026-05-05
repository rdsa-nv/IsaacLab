# Project Template

**Start a new Isaac Lab project with the official template. Get a working environment, training config, and project structure in minutes.**

## Create from template

```bash
# Clone the template
git clone https://github.com/isaac-sim/IsaacLabExtensionTemplate.git my_project
cd my_project

# Rename to your project
python setup_template.py --name my_robot_tasks

# Install in editable mode
./isaaclab.sh -e .
```

## Project structure

The template gives you:

```
my_project/
├── my_robot_tasks/
│   ├── __init__.py              # Gymnasium registration
│   ├── my_env_cfg.py            # Environment configuration
│   └── agents/
│       ├── rsl_rl_ppo_cfg.py    # RSL-RL training config
│       └── skrl_ppo_cfg.yaml    # SKRL training config
├── scripts/
│   ├── train.py                 # Training script
│   └── play.py                  # Evaluation script
├── pyproject.toml               # Package metadata
└── setup_template.py            # One-time setup script
```

## Define your environment

Edit `my_robot_tasks/my_env_cfg.py`:

```python
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.assets import ArticulationCfg
from isaaclab.utils import configclass

@configclass
class MySceneCfg(InteractiveSceneCfg):
    robot: ArticulationCfg = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Robot",
        spawn=UsdFileCfg(usd_path="path/to/robot.usd"),
        actuators={
            "joints": ImplicitActuatorCfg(
                joint_names_expr=[".*"],
                stiffness=80.0,
                damping=4.0,
            ),
        },
    )

@configclass
class MyEnvCfg(ManagerBasedRLEnvCfg):
    scene: MySceneCfg = MySceneCfg(num_envs=4096, env_spacing=2.5)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
```

## Register with Gymnasium

In `my_robot_tasks/__init__.py`:

```python
import gymnasium as gym

gym.register(
    id="Isaac-MyTask-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": f"{__name__}.my_env_cfg:MyEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.agents.rsl_rl_ppo_cfg:MyPPORunnerCfg",
    },
)
```

## Train

```bash
./isaaclab.sh -p scripts/train.py --task Isaac-MyTask-v0 --num_envs 4096 --viz none
```

## Evaluate

```bash
./isaaclab.sh -p scripts/play.py --task Isaac-MyTask-v0 --checkpoint logs/model_5000.pt
```

## Tips

- **Start with a working example**: Copy a similar environment from `isaaclab_tasks/` and modify it.
- **Test early**: Run `random_agent.py` after any change to verify the env works.
- **Keep configs composable**: Define scenes, rewards, and observations as separate `@configclass` blocks.
- **Use pre-built reward terms** from `isaaclab.envs.mdp` before writing custom ones.
