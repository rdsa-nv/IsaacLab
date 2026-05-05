# Interactive Scenes

**Manage multiple entities (robots, objects, sensors) in a single scene with automatic environment cloning.**

## Define a scene with config

```python
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.utils import configclass
import isaaclab.sim as sim_utils

@configclass
class CartpoleSceneCfg(InteractiveSceneCfg):
    # Non-interactive: spawned but not stepped
    ground = AssetBaseCfg(
        prim_path="/World/defaultGroundPlane",
        spawn=sim_utils.GroundPlaneCfg(),
    )
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0),
    )

    # Interactive: stepped during simulation
    cartpole: ArticulationCfg = CARTPOLE_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Robot"
    )
```

## Create and use the scene

```python
from isaaclab.scene import InteractiveScene

scene_cfg = CartpoleSceneCfg(num_envs=32, env_spacing=2.5)
scene = InteractiveScene(scene_cfg)

# Access entities by config attribute name
robot = scene["cartpole"]

# Scene manages all entities together
sim.reset()
scene.reset()

while running:
    robot.set_joint_effort_target(actions)
    scene.write_data_to_sim()
    sim.step()
    scene.update(sim_dt)
```

```bash
./isaaclab.sh -p scripts/tutorials/02_scene/create_scene.py --num_envs 32
```

## Key concepts

| Concept | Description |
|---------|-------------|
| `{ENV_REGEX_NS}` | Replaced with `/World/envs/env_{i}` for each clone |
| `num_envs` | Number of parallel environment copies |
| `env_spacing` | Distance between environment origins [m] |
| Interactive prims | Articulations, rigid objects, sensors — stepped each frame |
| Non-interactive prims | Ground planes, lights — spawned once, not stepped |

The scene automatically clones the environment layout `num_envs` times. Each clone gets its own physics, offset by `env_spacing`.

## Script reference

| Script | Purpose |
|--------|---------|
| `scripts/tutorials/02_scene/create_scene.py` | Create and interact with a multi-env scene |
