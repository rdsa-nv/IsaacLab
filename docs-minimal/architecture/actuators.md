# Actuator Models

**Isaac Lab provides implicit and explicit actuator models that convert action commands into joint torques.**

![Actuator model architecture](../_static/actuator-group/actuator-light.svg)

## Implicit vs explicit

| Type | How it works | When to use |
|------|-------------|-------------|
| **Implicit** | Uses the physics engine's built-in PD controller | Simple tasks, position/velocity control |
| **Explicit** | Runs an external model to compute torques, then applies them | Realistic actuator dynamics, torque clipping, neural nets |

## Implicit actuators

The simplest option. The physics engine computes joint torques from PD gains:

$$\tau = k_p (q_{target} - q) + k_d (\dot{q}_{target} - \dot{q})$$

```python
from isaaclab.actuators import ImplicitActuatorCfg

actuators = {
    "legs": ImplicitActuatorCfg(
        joint_names_expr=[".*_hip_joint", ".*_thigh_joint", ".*_calf_joint"],
        stiffness=80.0,      # k_p [N*m/rad]
        damping=4.0,         # k_d [N*m*s/rad]
        effort_limit=33.5,   # Max torque [N*m]
        velocity_limit=21.0, # Max velocity [rad/s]
    ),
}
```

**Note:** Stiffness and damping are set in the physics engine. The PD computation happens inside the solver — you cannot intercept or modify the torques.

## Explicit actuators

Compute torques outside the physics engine, giving full control over the actuator model.

### DCMotor

Applies effort limits with optional torque clipping:

```python
from isaaclab.actuators import DCMotorCfg

actuators = {
    "legs": DCMotorCfg(
        joint_names_expr=[".*"],
        stiffness=80.0,
        damping=4.0,
        effort_limit=33.5,
        saturation_effort=33.5,   # Clips torques at this value
    ),
}
```

### IdealPD

Like implicit but computes torques explicitly (allows inspection and modification):

```python
from isaaclab.actuators import IdealPDActuatorCfg

actuators = {
    "arm": IdealPDActuatorCfg(
        joint_names_expr=["joint_[1-7]"],
        stiffness=400.0,
        damping=80.0,
        effort_limit=87.0,
    ),
}
```

### Actuator networks (neural net models)

For learned actuator models (e.g., from system identification):

```python
from isaaclab.actuators import ActuatorNetLSTMCfg

actuators = {
    "legs": ActuatorNetLSTMCfg(
        joint_names_expr=[".*"],
        network_file="path/to/actuator_net.pt",
        stiffness=80.0,
        damping=4.0,
        effort_limit=33.5,
    ),
}
```

Available neural actuator types:

| Class | Architecture | Input |
|-------|-------------|-------|
| `ActuatorNetMLPCfg` | MLP | Position error, velocity |
| `ActuatorNetLSTMCfg` | LSTM | Position error, velocity (with history) |

## Actuator groups

Different joints can use different actuators. Match joints with regex patterns:

```python
actuators = {
    "arm": ImplicitActuatorCfg(
        joint_names_expr=["joint_[1-7]"],
        stiffness=400.0,
        damping=80.0,
    ),
    "gripper": ImplicitActuatorCfg(
        joint_names_expr=["finger_.*"],
        stiffness=1000.0,
        damping=10.0,
    ),
}
```

## Control modes

The actuator type determines which control commands are valid:

| Command | Required gains | Method |
|---------|---------------|--------|
| Position target | `stiffness > 0` | `set_joint_position_target()` |
| Velocity target | `damping > 0` | `set_joint_velocity_target()` |
| Effort (torque) | None | `set_joint_effort_target()` |

For effort control with implicit actuators, set `stiffness=0` and `damping=0`:

```python
actuators = {
    "joints": ImplicitActuatorCfg(
        joint_names_expr=[".*"],
        stiffness=0.0,
        damping=0.0,
        effort_limit=87.0,
    ),
}
```

## Choosing an actuator model

| Scenario | Recommended |
|----------|-------------|
| Quick prototyping | `ImplicitActuatorCfg` |
| Need to inspect/clip torques | `DCMotorCfg` |
| Sim-to-real transfer | `ActuatorNetLSTMCfg` or `ActuatorNetMLPCfg` |
| Custom dynamics | Subclass `ActuatorBase` |

For sim-to-real, explicit actuators with learned models give the best transfer because they capture real motor dynamics (backlash, friction, thermal effects) that implicit PD cannot model.
