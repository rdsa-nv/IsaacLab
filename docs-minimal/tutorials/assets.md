# Working with Assets

**Create rigid bodies, articulated robots, and deformable objects. Manage their state and apply forces.**

## Rigid objects

Rigid objects have a root state (pose + velocity) and respond to physics forces.

```python
from isaaclab.assets import RigidObject, RigidObjectCfg
from isaaclab.sim.spawners import ConeCfg

cone_cfg = RigidObjectCfg(
    prim_path="/World/Origin.*/Cone",    # Regex: spawns at every matching path
    spawn=ConeCfg(
        radius=0.5, height=1.0,
        rigid_props=RigidBodyPropertiesCfg(mass=1.0),
        collision_props=CollisionPropertiesCfg(),
        physics_material=RigidBodyMaterialCfg(),
    ),
)
cone = RigidObject(cfg=cone_cfg)
```

**Read and write state:**

```python
# Read current state
pos = cone.data.root_pos_w          # Position [N, 3]
quat = cone.data.root_quat_w       # Orientation [N, 4]
vel = cone.data.root_lin_vel_w      # Linear velocity [N, 3]

# Reset to a new state
root_state = cone.data.default_root_state.clone()
root_state[:, 2] += 2.0  # Lift 2m
cone.write_root_pose_to_sim(root_state[:, :7])
cone.write_root_velocity_to_sim(root_state[:, 7:])
cone.reset()
```

```bash
./isaaclab.sh -p scripts/tutorials/01_assets/run_rigid_object.py
```

## Articulated robots

Articulations are multiple rigid bodies connected by joints. They have root state plus joint positions and velocities.

```python
from isaaclab.assets import Articulation, ArticulationCfg

cartpole = Articulation(cfg=ArticulationCfg(
    prim_path="/World/Origin.*/Robot",
    spawn=UsdFileCfg(usd_path="path/to/cartpole.usd"),
    actuators={"joint_actuator": ActuatorCfg(...)},
))
```

**Control joints:**

```python
# Read joint state
joint_pos = cartpole.data.joint_pos   # [N, num_joints]
joint_vel = cartpole.data.joint_vel   # [N, num_joints]

# Apply effort commands
efforts = torch.randn(num_envs, num_joints, device=device)
cartpole.set_joint_effort_target(efforts)

# Or position/velocity targets (requires non-zero stiffness/damping)
cartpole.set_joint_position_target(target_pos)
cartpole.set_joint_velocity_target(target_vel)
```

**Reset robot state:**

```python
root_state = cartpole.data.default_root_state.clone()
joint_pos = cartpole.data.default_joint_pos.clone()
joint_vel = cartpole.data.default_joint_vel.clone()

cartpole.write_root_pose_to_sim(root_state[:, :7])
cartpole.write_root_velocity_to_sim(root_state[:, 7:])
cartpole.write_joint_state_to_sim(joint_pos, joint_vel)
cartpole.reset()
```

```bash
./isaaclab.sh -p scripts/tutorials/01_assets/run_articulation.py
```

## Deformable objects

Soft bodies simulated with FEM (Finite Element Method). State is per-node rather than per-body.

```python
from isaaclab.assets import DeformableObject, DeformableObjectCfg
from isaaclab.sim.spawners import CuboidCfg
from isaaclab.sim.spawners.physics import DeformableBodyPropertiesCfg

cube = DeformableObject(cfg=DeformableObjectCfg(
    prim_path="/World/Origin.*/Cube",
    spawn=CuboidCfg(
        size=[0.2, 0.2, 0.2],
        deformable_props=DeformableBodyPropertiesCfg(),
    ),
))
```

**Work with nodal state:**

```python
# Read node positions/velocities
nodal_pos = cube.data.nodal_pos_w     # [N, num_nodes, 3]
nodal_vel = cube.data.nodal_vel_w     # [N, num_nodes, 3]

# Pin specific nodes (partial kinematic control)
kinematic_target = torch.zeros(num_envs, num_nodes, 4, device=device)
kinematic_target[:, node_idx, :3] = desired_pos
kinematic_target[:, node_idx, 3] = 1.0   # Flag as kinematic
cube.write_nodal_kinematic_target_to_sim(kinematic_target)
```

!!! note
    Deformable objects are GPU-only and use tetrahedral meshes for simulation.

```bash
./isaaclab.sh -p scripts/tutorials/01_assets/run_deformable_object.py
```

## Simulation loop pattern

All asset types follow the same loop:

```python
# 1. Spawn (before sim.reset())
asset = Articulation(cfg=...)

# 2. Reset
sim.reset()
asset.reset()

# 3. Step loop
while running:
    asset.set_joint_effort_target(actions)  # Apply commands
    asset.write_data_to_sim()               # Flush to physics
    sim.step()                              # Step physics
    asset.update(sim_dt)                    # Refresh buffers
```

## Script reference

| Script | Asset type |
|--------|-----------|
| `scripts/tutorials/01_assets/run_rigid_object.py` | Rigid bodies |
| `scripts/tutorials/01_assets/run_articulation.py` | Articulated robots |
| `scripts/tutorials/01_assets/run_deformable_object.py` | Soft bodies |
