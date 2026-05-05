# Policy Export

**Export trained policies for deployment on real robots or edge devices.**

## Export formats

| Format | File | Runtime | Use case |
|--------|------|---------|----------|
| TorchScript (JIT) | `policy.pt` | PyTorch | Python robots, GPU inference |
| ONNX | `policy.onnx` | ONNX Runtime | Cross-platform, edge devices |
| LEAPP | Platform-specific | LEAPP runtime | Latency-optimized edge deployment |

## Automatic export

Running `play.py` automatically exports the policy:

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --checkpoint logs/rsl_rl/anymal_c_flat/model_5000.pt
```

Exported files appear in:

```
logs/rsl_rl/anymal_c_flat/<run>/exported/
  policy.pt       # TorchScript
  policy.onnx     # ONNX
```

## Manual export

### TorchScript (JIT)

```python
from isaaclab_rl.rsl_rl import export_policy_as_jit

export_policy_as_jit(
    actor_critic.actor,
    normalizer=actor_critic.normalizer,
    path="exported/",
    filename="policy.pt",
)
```

Load on the robot:

```python
import torch

policy = torch.jit.load("policy.pt")
policy.eval()

with torch.inference_mode():
    obs = get_sensor_data()   # torch.Tensor [1, obs_dim]
    actions = policy(obs)     # [1, action_dim]
```

### ONNX

```python
from isaaclab_rl.rsl_rl import export_policy_as_onnx

export_policy_as_onnx(
    actor_critic.actor,
    normalizer=actor_critic.normalizer,
    path="exported/",
    filename="policy.onnx",
    input_size=obs_dim,
)
```

Load on the robot (no PyTorch needed):

```python
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession("policy.onnx")

obs = get_sensor_data()   # numpy array [1, obs_dim]
actions = session.run(None, {"obs": obs})[0]
```

## IO Descriptors

IO descriptors make exported policies self-documenting. They embed metadata about observation/action semantics directly in the exported model:

```python
from isaaclab.utils.io_descriptors import IODescriptor

descriptor = IODescriptor(
    inputs={
        "joint_pos": {"shape": (12,), "units": "rad", "description": "Joint positions"},
        "joint_vel": {"shape": (12,), "units": "rad/s", "description": "Joint velocities"},
        "base_ang_vel": {"shape": (3,), "units": "rad/s", "description": "Base angular velocity"},
        "command": {"shape": (3,), "units": "m/s, m/s, rad/s", "description": "Velocity command"},
    },
    outputs={
        "joint_pos_target": {"shape": (12,), "units": "rad", "description": "Joint position targets"},
    },
)
```

Benefits:

- Robot code knows exactly what observations to provide and in what order
- Reduces integration errors during sim-to-real transfer
- Self-documenting policy interface

## LEAPP export

LEAPP (Low-latency Edge AI Policy Pipeline) exports policies optimized for edge hardware:

```bash
./isaaclab.sh -p scripts/reinforcement_learning/leapp/export.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --checkpoint model_5000.pt
```

## Observation normalization

If training used observation normalization, the normalizer is embedded in the exported policy. The exported model expects **raw** observations — normalization happens internally.

Verify normalization is included:

```python
# The exported policy already includes normalization
policy = torch.jit.load("policy.pt")

# Input raw observations directly — no manual normalization needed
raw_obs = get_sensor_data()
actions = policy(raw_obs)
```

## Checklist for deployment

1. Train until convergence (check reward curves plateau)
2. Evaluate with `play.py` in simulation
3. Export policy (automatic during play, or manual)
4. Verify exported policy matches simulation behavior
5. Test with IO descriptors to validate observation mapping
6. Deploy on robot with appropriate safety limits
