# Import New Assets

**Bring URDF, MJCF, or USD robot/object models into Isaac Lab.**

![URDF to USD conversion](../_static/tutorials/tutorial_convert_urdf.jpg)

## Supported formats

| Format | Source | Converter |
|--------|--------|-----------|
| URDF | ROS ecosystem | `./isaaclab.sh -p scripts/tools/convert_urdf.py` |
| MJCF | MuJoCo | `./isaaclab.sh -p scripts/tools/convert_mjcf.py` |
| USD | Omniverse / Isaac Sim | Native — no conversion needed |

## Convert URDF to USD

```bash
./isaaclab.sh -p scripts/tools/convert_urdf.py \
    --input /path/to/robot.urdf \
    --output /path/to/robot.usd \
    --merge-joints         # Merge fixed joints for performance
```

Key flags:

| Flag | Effect |
|------|--------|
| `--merge-joints` | Merges fixed joints (fewer bodies = faster sim) |
| `--make-instanceable` | Creates instanceable USD for multi-env cloning |
| `--collision-approximation` | `convexDecomposition`, `convexHull`, `boundingCube`, `none` |

## Convert MJCF to USD

```bash
./isaaclab.sh -p scripts/tools/convert_mjcf.py \
    --input /path/to/robot.xml \
    --output /path/to/robot.usd
```

## Use converted assets in code

```python
from isaaclab.assets import ArticulationCfg
from isaaclab.sim import UsdFileCfg

robot_cfg = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Robot",
    spawn=UsdFileCfg(
        usd_path="path/to/converted/robot.usd",
        activate_contact_sensors=True,
    ),
    actuators={
        "legs": ImplicitActuatorCfg(
            joint_names_expr=[".*_hip_joint", ".*_knee_joint"],
            stiffness=80.0,
            damping=4.0,
        ),
    },
)
```

## Make assets instanceable

For multi-environment training, instanceable assets share mesh data across clones — drastically reducing GPU memory.

```bash
./isaaclab.sh -p scripts/tools/convert_urdf.py \
    --input robot.urdf \
    --output robot/robot.usd \
    --make-instanceable
```

This generates:

```
robot/
  robot.usd           # Scene description (references props)
  robot_props.usd     # Shared mesh/material data
```

## Asset configuration tips

**Collision meshes:** Use `convexDecomposition` for concave shapes. Use `convexHull` for simple shapes (faster).

**Joint limits:** Verify limits match your URDF. Override in code if needed:

```python
actuators={
    "arm": ImplicitActuatorCfg(
        joint_names_expr=["joint_[1-7]"],
        effort_limit=87.0,
        velocity_limit=2.175,
        stiffness=400.0,
        damping=80.0,
    ),
}
```

**Self-collision filtering:** Enable in spawn config if the robot has overlapping links:

```python
spawn=UsdFileCfg(
    usd_path="robot.usd",
    articulation_props=ArticulationRootPropertiesCfg(
        enabled_self_collisions=True,
    ),
)
```
