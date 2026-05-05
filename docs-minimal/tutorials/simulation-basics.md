# Simulation Basics

**Launch Isaac Sim, spawn objects into the scene, and step the physics simulation.**

![Spawning primitives in Isaac Lab](../_static/tutorials/tutorial_spawn_prims.jpg)

## 1. Create an empty simulation

```python
# scripts/tutorials/00_sim/create_empty.py
import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

from isaaclab.sim import SimulationCfg, SimulationContext

sim_cfg = SimulationCfg(dt=0.01)
sim = SimulationContext(sim_cfg)
sim.set_camera_view([2.5, 2.5, 2.5], [0.0, 0.0, 0.0])

sim.reset()
while simulation_app.is_running():
    sim.step()

simulation_app.close()
```

```bash
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py
```

**Key classes:**

- `AppLauncher` — wraps `SimulationApp`, handles CLI args (`--viz`, `--enable_cameras`, etc.)
- `SimulationContext` — manages physics scene, timeline, and stepping
- `sim.reset()` must be called before `sim.step()` (initializes physics handles)

## 2. Spawn objects into the scene

Isaac Lab uses USD (Universal Scene Description) to represent scenes. Objects are placed at **prim paths** (e.g., `/World/Objects/Cone`).

```python
# scripts/tutorials/00_sim/spawn_prims.py

from isaaclab.sim.spawners import GroundPlaneCfg, DistantLightCfg, ConeCfg
from isaaclab.sim.spawners.physics import (
    RigidBodyPropertiesCfg, CollisionPropertiesCfg, RigidBodyMaterialCfg
)
from isaaclab import sim_utils

# Ground plane
cfg_ground = GroundPlaneCfg()
cfg_ground.func("/World/defaultGroundPlane", cfg_ground)

# Light
cfg_light = DistantLightCfg()
cfg_light.func("/World/Light", cfg_light, translation=(1, 0, 10))

# Visual-only cone (no physics)
cfg_cone_visual = ConeCfg(radius=0.5, height=1.0)
cfg_cone_visual.func("/World/Objects/ConeVisual", cfg_cone_visual, translation=[0, 0, 1])

# Physics-enabled cone (falls under gravity)
cfg_cone_rigid = ConeCfg(
    radius=0.5, height=1.0,
    rigid_props=RigidBodyPropertiesCfg(mass=1.0),
    collision_props=CollisionPropertiesCfg(),
    physics_material=RigidBodyMaterialCfg(),
)
cfg_cone_rigid.func("/World/Objects/ConeRigid", cfg_cone_rigid, translation=[2, 0, 1])

# Load a USD asset
from isaaclab.sim.spawners import UsdFileCfg
cfg_table = UsdFileCfg(usd_path="path/to/table.usd")
cfg_table.func("/World/Objects/Table", cfg_table, translation=[0, 0, 1.05])
```

```bash
./isaaclab.sh -p scripts/tutorials/00_sim/spawn_prims.py
```

**Spawner pattern:** Create a config object, then call `config.func(prim_path, config, translation=..., orientation=...)`.

!!! warning "Scene design before simulation"
    All spawning must happen **before** `sim.reset()`. Adding physics-enabled prims during simulation is not supported.

## Key concepts

| Concept | Description |
|---------|-------------|
| **Prim** | A node in the USD scene hierarchy (e.g., `/World/Objects/Cone`) |
| **Stage** | The root container holding all prims |
| **Spawner** | Config + function that places a prim at a path with properties |
| **AppLauncher** | Configures the simulator (rendering, headless, device) |
| **SimulationContext** | Controls physics stepping and timeline |

## Script reference

| Script | Purpose |
|--------|---------|
| `scripts/tutorials/00_sim/create_empty.py` | Empty simulation loop |
| `scripts/tutorials/00_sim/spawn_prims.py` | Spawn shapes, lights, USD assets |
