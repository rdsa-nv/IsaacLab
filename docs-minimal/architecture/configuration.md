# Configuration System

Isaac Lab uses Python dataclasses (via `@configclass`) for all configuration. No YAML files, no JSON — just Python with autocomplete and type checking.

!!! info "3.0: Multi-backend PresetCfg"
    Isaac Lab 3.0 adds `PresetCfg` for writing environments that support both PhysX and Newton backends. See [Physics Backends](physics-backends.md).

## The @configclass decorator

```python
from isaaclab.utils import configclass

@configclass
class MyEnvCfg(DirectRLEnvCfg):
    decimation = 2
    episode_length_s = 5.0
    action_scale = 100.0
    action_space = 1
    observation_space = 4
```

`@configclass` is a thin wrapper around `@dataclass` that adds:

- Nested config merging
- YAML serialization
- `.replace()` for creating variants

## Overriding configs

### From the command line (Hydra)

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Cartpole-Direct-v0 \
  env.scene.num_envs=8192 \
  env.episode_length_s=10.0
```

### In Python

```python
@configclass
class MyCustomCfg(CartpoleEnvCfg):
    episode_length_s = 10.0
    action_scale = 200.0

    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=8192, env_spacing=4.0
    )
```

### Using .replace()

```python
robot_cfg = FRANKA_CFG.replace(
    prim_path="/World/envs/env_.*/Robot"
)
```

## Config hierarchy

```
DirectRLEnvCfg / ManagerBasedRLEnvCfg
├── sim: SimulationCfg
│   ├── dt: float
│   ├── render_interval: int
│   └── physics: PhysicsCfg
├── scene: InteractiveSceneCfg
│   ├── num_envs: int
│   └── env_spacing: float
├── robot_cfg: ArticulationCfg  (Direct)
├── observations: ObservationsCfg  (Manager-based)
├── actions: ActionsCfg  (Manager-based)
├── rewards: RewardsCfg  (Manager-based)
├── terminations: TerminationsCfg  (Manager-based)
├── events: EventCfg  (Manager-based)
└── curriculum: CurriculumCfg  (Manager-based)
```

## Physics presets

Each environment supports multiple physics backends:

```python
@configclass
class CartpolePhysicsCfg(PresetCfg):
    default: PhysxCfg = PhysxCfg()
    physx: PhysxCfg = PhysxCfg()
    newton: NewtonCfg = NewtonCfg(
        solver_cfg=MJWarpSolverCfg(integrator="implicitfast"),
        num_substeps=1,
        use_cuda_graph=True,
    )
    ovphysx: OvPhysxCfg = OvPhysxCfg()
```

Select at runtime:

```bash
./isaaclab.sh -p train.py --task Isaac-Cartpole-Direct-v0 \
  env.sim.physics=newton
```

## Agent configs

Agent configs are separate from env configs. Each RL framework has its own format:

=== "RSL-RL (Python)"

    ```python
    @configclass
    class MyPPORunnerCfg(RslRlOnPolicyRunnerCfg):
        num_steps_per_env = 24
        max_iterations = 1500
        policy = RslRlPpoActorCriticCfg(
            actor_hidden_dims=[256, 128, 64],
        )
        algorithm = RslRlPpoAlgorithmCfg(
            learning_rate=1.0e-3,
        )
    ```

=== "SKRL / SB3 / RL Games (YAML)"

    ```yaml
    seed: 42
    agent:
      class: PPO
      learning_rate: 1.0e-3
      rollouts: 24
    ```

## Config dumps

Every training run saves configs to the log directory:

```
logs/rsl_rl/<experiment>/
└── <timestamp>/
    └── params/
        ├── env.yaml      # Full environment config
        └── agent.yaml    # Full agent config
```

This makes runs fully reproducible.
