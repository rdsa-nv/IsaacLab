# Motion Controllers

**Use inverse kinematics and operational space control to track end-effector poses.**

![Task-space controller tracking end-effector pose](../_static/tutorials/tutorial_task_space_controller.jpg)

## Differential IK

Compute joint position targets from desired end-effector poses using the Jacobian.

```python
from isaaclab.controllers import DifferentialIKController, DifferentialIKControllerCfg

diff_ik_cfg = DifferentialIKControllerCfg(
    command_type="pose",
    use_relative_mode=False,
    ik_method="dls",        # Damped least-squares
)
diff_ik = DifferentialIKController(diff_ik_cfg, num_envs=num_envs, device=device)
```

**Set target and compute:**

```python
# Target EE pose in robot base frame [x, y, z, qx, qy, qz, qw]
ik_command = torch.zeros(num_envs, 7, device=device)
ik_command[:, :3] = torch.tensor([0.5, 0.0, 0.3])    # Position [m]
ik_command[:, 3:] = torch.tensor([0.0, 0.0, 0.0, 1.0])  # Quaternion (XYZW in 3.0)

diff_ik.set_command(ik_command)

# Compute joint targets from current state
jacobian = robot.data.jacobian[:, ee_body_idx, :, arm_joint_ids]
joint_pos_des = diff_ik.compute(
    ee_pos_b, ee_quat_b, jacobian, robot.data.joint_pos[:, arm_joint_ids]
)

# Apply
robot.set_joint_position_target(joint_pos_des, joint_indices=arm_joint_ids)
```

**Frame conversions matter:** The IK controller works in the robot's base frame. Convert world-frame poses:

```python
from isaaclab.utils.math import subtract_frame_transforms

# World → base frame
ee_pos_b, ee_quat_b = subtract_frame_transforms(
    robot.data.root_pos_w, robot.data.root_quat_w,
    robot.data.body_pos_w[:, ee_body_idx], robot.data.body_quat_w[:, ee_body_idx],
)
```

```bash
./isaaclab.sh -p scripts/tutorials/05_controllers/run_diff_ik.py --robot franka_panda --num_envs 128
```

## IK methods

| Method | Key | Best for |
|--------|-----|----------|
| Damped least-squares | `dls` | General use (default) |
| Pseudo-inverse | `pinv` | Well-conditioned configurations |
| SVD | `svd` | Near-singularity robustness |

## Joint-space vs task-space control

Isaac Lab environments support multiple controller modes via the action space:

| Controller | Action dim | Description |
|-----------|-----------|-------------|
| Joint position | N_joints | Direct joint angle targets |
| Joint velocity | N_joints | Joint velocity targets |
| Joint effort | N_joints | Torque/force commands |
| IK absolute | 7 (pos + quat) | Target EE pose |
| IK relative | 6 (delta pos + delta rot) | Delta EE pose per step |
| OSC | 6 (wrench) | Force/torque at EE |

Many environments offer variants with different controllers (e.g., `Isaac-Reach-Franka-v0` vs `Isaac-Reach-Franka-IK-Abs-v0`).

## Script reference

| Script | Purpose |
|--------|---------|
| `scripts/tutorials/05_controllers/run_diff_ik.py` | Differential IK with Franka or UR10 |
