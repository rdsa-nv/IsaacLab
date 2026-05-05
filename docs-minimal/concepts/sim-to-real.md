# Sim-to-Real Deployment

**Train in simulation, deploy on real hardware.**

## Export trained policies

After running `play.py`, policies are automatically exported to:

```
logs/rsl_rl/<experiment>/<run>/exported/
├── policy.pt    # TorchScript JIT
└── policy.onnx  # ONNX
```

### Manual export

```python
from isaaclab_rl.rsl_rl import export_policy_as_jit, export_policy_as_onnx

# After loading runner
export_policy_as_jit(policy_nn, normalizer=normalizer, path="exported/", filename="policy.pt")
export_policy_as_onnx(policy_nn, normalizer=normalizer, path="exported/", filename="policy.onnx")
```

## Load on a robot

### PyTorch (JIT)

```python
import torch

policy = torch.jit.load("policy.pt")
policy.eval()

# Inference loop
with torch.inference_mode():
    obs = get_robot_observations()  # torch.Tensor
    actions = policy(obs)
    send_to_robot(actions)
```

### ONNX Runtime

```python
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession("policy.onnx")

# Inference loop
obs = get_robot_observations()  # numpy array
actions = session.run(None, {"obs": obs})[0]
send_to_robot(actions)
```

## Sim-to-real tips

| Technique | What it does | Where in Isaac Lab |
|-----------|-------------|-------------------|
| Domain randomization | Vary physics, visuals at training time | `EventCfg` in manager-based envs |
| Observation noise | Add noise to sensor readings | Observation terms with noise params |
| Action delay | Simulate actuator latency | Config parameter |
| Terrain curriculum | Progressively harder terrain | `CurriculumCfg` |
| Observation normalization | Running mean/std normalization | `actor_obs_normalization=True` in agent config |

## Deploy with ROS

Isaac Lab includes ROS inference environments for deployment:

```bash
# UR10e with ROS inference
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Deploy-GearAssembly-UR10e-2F140-ROS-Inference-v0
```

Available deploy environments:

| Task ID | Robot | Task |
|---------|-------|------|
| `Isaac-Deploy-Reach-UR10e-v0` | UR10e | Reach target |
| `Isaac-Deploy-GearAssembly-UR10e-2F140-v0` | UR10e + 2F-140 | Gear assembly |
| `Isaac-Deploy-GearAssembly-UR10e-2F85-v0` | UR10e + 2F-85 | Gear assembly |
| `Isaac-Deploy-Reach-Rizon4s-v0` | Flexiv Rizon 4s | Reach target |
| `Isaac-Deploy-GearAssembly-Rizon4s-Grav-v0` | Flexiv Rizon 4s | Gear assembly |

## LEAPP deployment

For edge deployment and latency-optimized inference:

```bash
./isaaclab.sh -p scripts/reinforcement_learning/leapp/deploy.py \
  --task <TASK_ID>
```
