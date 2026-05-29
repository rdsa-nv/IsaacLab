# Sensors and Actuators

Always verify classes and config names from the current source tree before
writing code. The high-level package anchors are stable, but individual classes
move.

## Sensors

Source: `source/isaaclab/isaaclab/sensors/`

Current sensor folders include:

- `camera`
- `contact_sensor`
- `frame_transformer`
- `imu`
- `joint_wrench`
- `pva`
- `ray_caster`

Camera sensors usually require `--enable_cameras`. Ray-caster and camera data
types can be backend/renderer-specific, so inspect the task config and tests.

## Actuators

Source: `source/isaaclab/isaaclab/actuators/`

Current actuator modules include:

- `actuator_base.py`
- `actuator_cfg.py`
- `actuator_net.py`
- `actuator_pd.py`

Use the public config classes exported by `isaaclab.actuators`. For robot asset
examples, inspect `source/isaaclab_assets/isaaclab_assets/robots/`.

## Pattern

```python
from isaaclab.actuators import ImplicitActuatorCfg

actuators = {
    "legs": ImplicitActuatorCfg(
        joint_names_expr=[".*"],
        effort_limit_sim=80.0,
        velocity_limit_sim=100.0,
        stiffness=20.0,
        damping=0.5,
    )
}
```

## Verification

Useful checks:

```bash
rg -n "CameraCfg|TiledCamera|RayCaster|ContactSensor|FrameTransformer|Imu|JointWrench|Pva" source/isaaclab source/isaaclab_tasks
rg -n "ImplicitActuatorCfg|ActuatorNet|DCMotor|DelayedPD" source/isaaclab source/isaaclab_assets source/isaaclab_tasks
```

For visual output, also check `source/isaaclab_visualizers/` and renderer
presets in the task config.
