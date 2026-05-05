# Using Sensors

**Attach cameras, ray casters, and contact sensors to robots. Read sensor data at configurable frequencies.**

## Camera

Captures RGB, depth, normals, and segmentation images.

```python
from isaaclab.sensors import CameraCfg
from isaaclab.sim.spawners.sensors import PinholeCameraCfg

camera = CameraCfg(
    prim_path="{ENV_REGEX_NS}/Robot/base/front_cam",
    update_period=0.1,   # 10 Hz
    height=480,
    width=640,
    data_types=["rgb", "distance_to_image_plane"],
    offset=CameraCfg.OffsetCfg(
        pos=[0.0, 0.0, 0.1],
        rot=[0.707, 0.0, 0.707, 0.0],
        convention="ros",
    ),
    spawn=PinholeCameraCfg(
        focal_length=24.0,
        focus_distance=400.0,
        horizontal_aperture=20.955,
    ),
)
```

**Read camera data:**

```python
rgb = scene["camera"].data.output["rgb"]                          # [N, H, W, 3] uint8
depth = scene["camera"].data.output["distance_to_image_plane"]    # [N, H, W, 1] float32
```

**Available data types:** `rgb`, `rgba`, `distance_to_image_plane`, `depth`, `normals`, `motion_vectors`, `semantic_segmentation`, `instance_segmentation_fast`, `instance_id_segmentation_fast`

!!! note "Tiled rendering"
    For 512+ cameras, use tiled rendering (composites all camera views into one large image). Available on Isaac Sim 4.2.0+ and Newton Warp.

## Ray caster

Virtual sensor that casts rays downward for terrain height scanning. No USD prim needed.

```python
from isaaclab.sensors import RayCasterCfg
from isaaclab.sensors.patterns import GridPatternCfg

height_scanner = RayCasterCfg(
    prim_path="{ENV_REGEX_NS}/Robot/base",
    update_period=0.04,    # 25 Hz
    offset=RayCasterCfg.OffsetCfg(pos=[0.0, 0.0, 0.0]),
    spawn=None,
    pattern=GridPatternCfg(resolution=0.1, size=[1.6, 1.6]),
    ray_alignment="yaw",
    debug_vis=True,
)
```

**Read ray data:**

```python
hits = scene["height_scanner"].data.ray_hits_w    # [N, num_rays, 3]
```

## Contact sensor

Reports net contact force on rigid body surfaces (e.g., feet).

```python
from isaaclab.sensors import ContactSensorCfg

contact = ContactSensorCfg(
    prim_path="{ENV_REGEX_NS}/Robot/.*_FOOT",   # Regex matches all feet
    update_period=0.0,    # Every sim step
    history_length=6,
    force_threshold=1.0,
)
```

**Read contact data:**

```python
forces = scene["contact"].data.net_forces_w         # [N, num_bodies, 3]
force_matrix = scene["contact"].data.force_matrix_w  # [N, num_bodies, max_contacts, 3]
```

!!! warning
    Contact sensors require `activate_contact_sensors=True` in the asset's spawn config.

## IMU

Measures linear acceleration and angular velocity in the body frame.

```python
from isaaclab.sensors import ImuSensorCfg

imu = ImuSensorCfg(
    prim_path="{ENV_REGEX_NS}/Robot/base",
    update_period=0.0,
)
```

**Data:** `lin_acc_b` [m/s^2], `ang_vel_b` [rad/s], `lin_vel_b` [m/s]

## Frame transformer

Tracks relative pose between frames on the robot.

```python
from isaaclab.sensors import FrameTransformerCfg

ee_frame = FrameTransformerCfg(
    prim_path="{ENV_REGEX_NS}/Robot/base",
    target_frames=[
        FrameTransformerCfg.FrameCfg(prim_path="{ENV_REGEX_NS}/Robot/ee_link"),
    ],
)
```

**Data:** `target_pos_source` [N, num_targets, 3], `target_quat_source` [N, num_targets, 4]

## Add sensors to a scene

```python
@configclass
class MySceneCfg(InteractiveSceneCfg):
    robot: ArticulationCfg = ...
    camera: CameraCfg = camera
    height_scanner: RayCasterCfg = height_scanner
    contact: ContactSensorCfg = contact
```

```bash
./isaaclab.sh -p scripts/tutorials/04_sensors/add_sensors_on_robot.py --num_envs 2 --enable_cameras
```

## Sensor summary

| Sensor | Data | Use case | Requires prim |
|--------|------|----------|---------------|
| Camera | RGB, depth, segmentation | Vision-based RL | Yes |
| Ray caster | Hit positions | Terrain scanning | No (virtual) |
| Contact | Force vectors | Gait detection | Yes (rigid body) |
| IMU | Acceleration, angular vel | State estimation | Yes (rigid body) |
| Frame transformer | Relative poses | IK, manipulation | Yes (rigid body) |

## Script reference

| Script | Purpose |
|--------|---------|
| `scripts/tutorials/04_sensors/add_sensors_on_robot.py` | Attach multiple sensors to a quadruped |
| `scripts/tutorials/04_sensors/run_usd_camera.py` | Camera capture and depth reprojection |
