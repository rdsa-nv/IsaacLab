# Troubleshooting

**Common issues and solutions for Isaac Lab development and training.**

## Installation issues

### `ModuleNotFoundError: No module named 'isaacsim'`

Isaac Sim is not installed or not in your Python path:

```bash
pip install isaacsim[all]
```

### `ImportError: libpython3.10.so: cannot open shared object file`

Missing system library. Install it:

```bash
sudo apt-get install libpython3.10-dev
```

### Conda environment conflicts

Create a fresh environment:

```bash
conda create -n isaaclab python=3.10 -y
conda activate isaaclab
pip install isaacsim[all]
./isaaclab.sh -i
```

## Runtime errors

### `PhysX error: out of gpu_found_lost_pairs_capacity`

Increase PhysX GPU buffer sizes in your simulation config:

```python
sim_cfg = SimulationCfg(
    physx=PhysxCfg(
        gpu_found_lost_pairs_capacity=2**24,
        gpu_total_aggregate_pairs_capacity=2**24,
    ),
)
```

### `CUDA out of memory`

Reduce `num_envs` or disable cameras:

```bash
# Fewer environments
./isaaclab.sh -p train.py --task MyTask --num_envs 1024

# Or check what's using GPU memory
nvidia-smi
```

### `RuntimeError: Expected all tensors to be on the same device`

Common when mixing CPU and GPU tensors. Ensure all tensors use the same device:

```python
tensor = torch.zeros(num_envs, 3, device=self.device)  # Use self.device
```

### Simulation runs but robot falls through ground

The collision mesh is missing or misconfigured:

```python
spawn=UsdFileCfg(
    usd_path="robot.usd",
    collision_props=CollisionPropertiesCfg(),  # Ensure this is set
)
```

### Robot explodes or jitters at start

Physics is unstable. Try:

1. Reduce timestep: `dt=0.002` instead of `0.005`
2. Add substeps: `substeps=2`
3. Check actuator gains aren't too high
4. Ensure initial joint positions are within limits

## Training issues

### Reward is NaN

Check for division by zero or log of negative numbers in reward functions:

```python
@torch.jit.script
def compute_rewards(vel: torch.Tensor) -> torch.Tensor:
    reward = torch.exp(-vel.norm(dim=-1))  # Safe — exp never produces NaN
    return reward
```

### Training doesn't converge

Common causes and fixes:

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Reward stays at 0 | Reward scale too small | Increase reward weights |
| Reward oscillates | Learning rate too high | Reduce by 2-5x |
| Policy collapses | Entropy too low | Increase `entropy_coef` |
| Very slow learning | Too few envs | Increase `num_envs` |
| Training crashes after N steps | Episode too long | Add `time_out` termination |

### Multi-GPU training hangs

NCCL communication issue. Check:

```bash
# Verify GPUs can communicate
nvidia-smi topo -m

# Set NCCL debug
export NCCL_DEBUG=INFO
```

## Performance issues

### GPU utilization is low (<50%)

Increase `num_envs`. The GPU needs enough parallel work:

```bash
./isaaclab.sh -p train.py --task MyTask --num_envs 4096
```

### Training is slower than expected

Profile to find the bottleneck:

```bash
# Check if it's simulation or learning
export ISAACLAB_PROFILE=1
./isaaclab.sh -p train.py --task MyTask --num_envs 2048 --headless
```

### Camera rendering is slow

Use tiled rendering for 512+ cameras:

```python
from isaaclab.sensors import TiledCameraCfg
# Instead of CameraCfg
```

## Environment issues

### `KeyError: 'robot'` when accessing scene

The entity name must match the config attribute name:

```python
@configclass
class MySceneCfg(InteractiveSceneCfg):
    my_robot: ArticulationCfg = ...   # Access as scene["my_robot"]
```

### Actions have no effect

Check actuator configuration. For effort control, stiffness and damping must be non-zero (or zero for pure torque mode):

```python
actuators = {
    "joints": ImplicitActuatorCfg(
        joint_names_expr=[".*"],
        stiffness=80.0,   # Non-zero for position control
        damping=4.0,
    ),
}
```

### Environment resets not working

Ensure `_reset_idx` writes state to sim:

```python
def _reset_idx(self, env_ids):
    joint_pos = self._robot.data.default_joint_pos[env_ids]
    joint_vel = torch.zeros_like(joint_pos)
    self._robot.write_joint_state_to_sim(joint_pos, joint_vel, env_ids=env_ids)
    # Don't forget root state too
    self._robot.write_root_pose_to_sim(default_pose[env_ids], env_ids=env_ids)
```

## Getting help

- **GitHub Issues**: [github.com/isaac-sim/IsaacLab/issues](https://github.com/isaac-sim/IsaacLab/issues)
- **Discussions**: [github.com/isaac-sim/IsaacLab/discussions](https://github.com/isaac-sim/IsaacLab/discussions)
- **NVIDIA Forums**: [forums.developer.nvidia.com](https://forums.developer.nvidia.com)
