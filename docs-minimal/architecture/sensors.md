# Sensor Architecture

**How sensors work in Isaac Lab: update scheduling, data access patterns, and custom sensors.**

## Sensor lifecycle

!!! warning "3.0 Change: IMU → PVA"
    In Isaac Lab 3.0, the old `Imu` sensor (full state) was renamed to `Pva`. The new `Imu` sensor only provides gyroscope and accelerometer data. See [Migration Guide](../migration/isaac-lab-3.md).

All sensors follow the same lifecycle:

1. **Spawn**: Created during scene setup (or virtual, like ray casters)
2. **Update**: Data refreshed at `update_period` intervals
3. **Read**: Access data via `sensor.data.*` attributes

```python
# Update is automatic when using InteractiveScene
scene.update(sim_dt)  # Updates all sensors that are due

# Or update manually
sensor.update(dt=sim_dt, force_recompute=False)
```

## Update scheduling

Sensors don't update every physics step — they follow their configured `update_period`:

```python
camera = CameraCfg(
    update_period=0.1,   # 10 Hz — updates every 0.1s of sim time
    ...
)

contact = ContactSensorCfg(
    update_period=0.0,   # 0 = every physics step
    ...
)
```

**Why?** Camera rendering is expensive. A 10 Hz camera in a 200 Hz sim skips 19 out of 20 steps — massive performance savings. Contact and IMU sensors are cheap and usually run every step.

## Data access patterns

All sensor data lives in a `.data` container with tensorized attributes:

```python
# Camera
rgb = scene["camera"].data.output["rgb"]              # [N, H, W, 3]
depth = scene["camera"].data.output["depth"]           # [N, H, W, 1]
intrinsics = scene["camera"].data.intrinsic_matrices   # [N, 3, 3]

# Contact sensor
forces = scene["contact"].data.net_forces_w            # [N, num_bodies, 3]

# Ray caster
hits = scene["scanner"].data.ray_hits_w                # [N, num_rays, 3]

# IMU
lin_acc = scene["imu"].data.lin_acc_b                  # [N, 3]
ang_vel = scene["imu"].data.ang_vel_b                  # [N, 3]

# Frame transformer
pos = scene["ee_frame"].data.target_pos_source         # [N, num_targets, 3]
quat = scene["ee_frame"].data.target_quat_source       # [N, num_targets, 4]
```

## Sensor types summary

| Sensor | Class | Requires prim | GPU data |
|--------|-------|---------------|----------|
| Camera | `CameraCfg` | Yes | RGB, depth, segmentation |
| Tiled Camera | `TiledCameraCfg` | Yes | Same (faster at scale) |
| Ray Caster | `RayCasterCfg` | No (virtual) | Hit positions |
| Ray Caster Camera | `RayCasterCameraCfg` | No (virtual) | Depth via raycasting |
| Contact | `ContactSensorCfg` | Yes | Force vectors |
| IMU | `ImuSensorCfg` | Yes | Acceleration, angular velocity |
| Frame Transformer | `FrameTransformerCfg` | Yes | Relative poses |

## Ray caster vs camera for depth

Two ways to get depth data:

| Approach | Pros | Cons |
|----------|------|------|
| Camera depth | Physically accurate, supports occlusion | Requires rendering pipeline |
| Ray caster | Fast, no rendering needed | No occlusion, limited to heightfield |

For terrain scanning (locomotion), ray casters are faster. For manipulation with complex scenes, use camera depth.

## Sensor offsets and frames

Sensors can be offset from their parent prim:

```python
camera = CameraCfg(
    prim_path="{ENV_REGEX_NS}/Robot/base",
    offset=CameraCfg.OffsetCfg(
        pos=[0.15, 0.0, 0.1],     # 15cm forward, 10cm up from base
        rot=[0.5, -0.5, 0.5, -0.5],
        convention="ros",
    ),
    ...
)
```

The `convention` parameter controls the coordinate frame interpretation:

- `"ros"`: X-forward, Y-left, Z-up
- `"opengl"`: X-right, Y-up, Z-backward
- `"world"`: World frame orientation

## Contact sensor details

Contact sensors require explicit activation on the asset:

```python
robot_cfg = ArticulationCfg(
    spawn=UsdFileCfg(
        usd_path="robot.usd",
        activate_contact_sensors=True,   # Required!
    ),
    ...
)
```

The `history_length` parameter stores past contact states for gait detection:

```python
contact = ContactSensorCfg(
    prim_path="{ENV_REGEX_NS}/Robot/.*_FOOT",
    history_length=6,     # Store last 6 readings
    force_threshold=1.0,  # Minimum force to register contact [N]
)

# Check if foot was in contact in previous steps
in_contact = scene["contact"].data.net_forces_w_history  # [N, num_bodies, history, 3]
```

## Performance considerations

| Sensor | Cost | Scaling tip |
|--------|------|-------------|
| Camera | High | Use tiled rendering for 512+ cameras |
| Ray caster | Low | Reduce ray count or pattern resolution |
| Contact | Very low | No optimization needed |
| IMU | Very low | No optimization needed |
| Frame transformer | Very low | No optimization needed |
