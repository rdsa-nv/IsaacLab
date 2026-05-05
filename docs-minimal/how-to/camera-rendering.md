# Camera & Rendering

**Set up cameras for vision-based RL, capture depth/segmentation, and scale with tiled rendering.**

## Basic camera setup

```python
from isaaclab.sensors import CameraCfg
from isaaclab.sim.spawners.sensors import PinholeCameraCfg

camera_cfg = CameraCfg(
    prim_path="{ENV_REGEX_NS}/Robot/base/front_cam",
    update_period=0.1,   # 10 Hz
    height=480,
    width=640,
    data_types=["rgb", "distance_to_image_plane"],
    offset=CameraCfg.OffsetCfg(
        pos=[0.15, 0.0, 0.1],
        rot=[0.5, -0.5, 0.5, -0.5],   # Camera facing forward
        convention="ros",
    ),
    spawn=PinholeCameraCfg(
        focal_length=24.0,
        focus_distance=400.0,
        horizontal_aperture=20.955,
    ),
)
```

## Available data types

| Data type | Shape | Description |
|-----------|-------|-------------|
| `rgb` | `[N, H, W, 3]` uint8 | Color image |
| `rgba` | `[N, H, W, 4]` uint8 | Color + alpha |
| `distance_to_image_plane` | `[N, H, W, 1]` float32 | Depth (perpendicular to image plane) |
| `depth` | `[N, H, W, 1]` float32 | Depth (distance from camera origin) |
| `normals` | `[N, H, W, 3]` float32 | Surface normals |
| `motion_vectors` | `[N, H, W, 2]` float32 | Per-pixel motion |
| `semantic_segmentation` | `[N, H, W, 1]` int32 | Semantic labels |
| `instance_segmentation_fast` | `[N, H, W, 1]` int32 | Instance IDs |
| `instance_id_segmentation_fast` | `[N, H, W, 1]` int32 | Unique instance IDs |

## Read camera data

```python
camera = scene["camera"]

# Access image tensors (stay on GPU)
rgb = camera.data.output["rgb"]                          # [N, H, W, 3]
depth = camera.data.output["distance_to_image_plane"]    # [N, H, W, 1]

# Camera intrinsic matrix
K = camera.data.intrinsic_matrices                       # [N, 3, 3]
```

## Tiled rendering (512+ cameras)

For large-scale vision RL (hundreds of environments), tiled rendering composites all camera views into a single large image — much faster than rendering each camera individually.

```python
from isaaclab.sensors import TiledCameraCfg

tiled_cam = TiledCameraCfg(
    prim_path="{ENV_REGEX_NS}/Robot/base/front_cam",
    update_period=0.0,
    height=84,
    width=84,
    data_types=["rgb", "distance_to_image_plane"],
    offset=TiledCameraCfg.OffsetCfg(pos=[0.15, 0.0, 0.1], convention="ros"),
    spawn=PinholeCameraCfg(focal_length=24.0, horizontal_aperture=20.955),
)
```

!!! note
    Tiled rendering requires Isaac Sim 4.2.0+ or Newton Warp backend. It's the recommended approach for vision-based RL at scale.

## Depth reprojection to 3D

Convert depth images to 3D point clouds:

```python
from isaaclab.utils.math import unproject_depth

points = unproject_depth(
    depth=camera.data.output["distance_to_image_plane"],
    intrinsics=camera.data.intrinsic_matrices,
)  # [N, H*W, 3] in camera frame
```

## Camera convention

Isaac Lab supports multiple camera conventions via the `convention` parameter:

| Convention | X | Y | Z | Use case |
|-----------|---|---|---|----------|
| `"ros"` | Right | Down | Forward | ROS integration |
| `"opengl"` | Right | Up | Backward | Graphics/rendering |
| `"world"` | World X | World Y | World Z | World-aligned |

## Enable cameras at runtime

Cameras require explicit enabling via CLI flag:

```bash
./isaaclab.sh -p my_script.py --enable_cameras
```

Or in `AppLauncherCfg`:

```python
app_launcher = AppLauncher(enable_cameras=True)
```

## Visualization backends

Isaac Lab supports multiple visualization backends for rendering:

| Backend | Use case | Enable with |
|---------|----------|-------------|
| Kit (Omniverse) | Full rendering, RTX | Default |
| Newton | Lightweight, fast | `--physics_backend newton` |
| Rerun | Replay/analysis | `--rerun` |
| Viser | Web-based viewer | `--viser` |
