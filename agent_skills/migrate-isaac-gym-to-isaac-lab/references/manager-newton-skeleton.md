<!--
Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause
-->

# Manager-Based Newton Skeleton

Use this reference when the requested target is `ManagerBasedRLEnv`, Newton/MJWarp, or `presets=newton_mjwarp`. Read the user's Isaac Gym code first; this skeleton is only the target shape.

## Files

```text
<task_package>/
  __init__.py
  <task_name>_env_cfg.py
  assets.py
  mdp/
    __init__.py
    observations.py
    rewards.py
    events.py
    terminations.py
  agents/
    __init__.py
    rsl_rl_ppo_cfg.py
    rl_games_ppo_cfg.yaml
```

## Config Skeleton

```python
from __future__ import annotations

from isaaclab_newton.physics import MJWarpSolverCfg, NewtonCfg
from isaaclab_physx.physics import PhysxCfg

import isaaclab.envs.mdp as base_mdp
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, JointWrenchSensorCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils.configclass import configclass
from isaaclab_tasks.utils import PresetCfg

from . import mdp
from .assets import ROBOT_CFG


@configclass
class TaskPhysicsCfg(PresetCfg):
    # If the user requested Newton-only, make default Newton. If they need
    # PhysX comparison too, set default/physx to PhysxCfg and keep newton_mjwarp.
    default: NewtonCfg = NewtonCfg(
        solver_cfg=MJWarpSolverCfg(
            njmax=128,
            nconmax=64,
            cone="pyramidal",
            integrator="implicitfast",
            impratio=1.0,
        ),
        num_substeps=1,
        debug_mode=False,
        use_cuda_graph=True,
    )
    newton_mjwarp: NewtonCfg = NewtonCfg(
        solver_cfg=MJWarpSolverCfg(
            njmax=128,
            nconmax=64,
            cone="pyramidal",
            integrator="implicitfast",
            impratio=1.0,
        ),
        num_substeps=1,
        debug_mode=False,
        use_cuda_graph=True,
    )
    physx: PhysxCfg = PhysxCfg()


@configclass
class SceneCfg(InteractiveSceneCfg):
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
    )

    robot: ArticulationCfg = ROBOT_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

    # Add only the sensors the source task actually needs. Use
    # JointWrenchSensorCfg when the Isaac Gym source used create_asset_force_sensor
    # and expects 6D force-torque values. Use ContactSensorCfg only for 3D
    # contact-force logic.
    # joint_wrench = JointWrenchSensorCfg(prim_path="{ENV_REGEX_NS}/Robot")
    # contact_forces = ContactSensorCfg(prim_path="{ENV_REGEX_NS}/Robot/.*foot", update_period=0.0)

    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DistantLightCfg(color=(0.75, 0.75, 0.75), intensity=3000.0),
    )


@configclass
class ActionsCfg:
    # Preserve Isaac Gym actuator/joint order with explicit names and preserve_order=True.
    joint_effort = base_mdp.JointEffortActionCfg(
        asset_name="robot",
        joint_names=["<joint_0>", "<joint_1>"],
        scale={"<joint_0>": 1.0, "<joint_1>": 1.0},
        preserve_order=True,
    )


@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        # Order terms to reproduce the source observation vector. Keep custom
        # source math as task-local mdp functions until the port is verified.
        base_height = ObsTerm(func=base_mdp.base_pos_z)
        base_lin_vel = ObsTerm(func=base_mdp.base_lin_vel)
        joint_pos = ObsTerm(
            func=base_mdp.joint_pos_limit_normalized,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=["<joint_0>", "<joint_1>"])},
        )
        source_extra = ObsTerm(func=mdp.source_extra_observation)
        actions = ObsTerm(func=base_mdp.last_action)

        def __post_init__(self) -> None:
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventsCfg:
    reset_base = EventTerm(
        func=base_mdp.reset_root_state_uniform,
        mode="reset",
        params={"pose_range": {}, "velocity_range": {}},
    )
    reset_joints = EventTerm(
        func=base_mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=["<joint_0>", "<joint_1>"]),
            "position_range": (-0.2, 0.2),
            "velocity_range": (-0.1, 0.1),
        },
    )


@configclass
class RewardsCfg:
    # First pass: keep source reward math intact as one custom term when in doubt.
    source_reward = RewTerm(func=mdp.source_reward, weight=1.0)
    alive = RewTerm(func=base_mdp.is_alive, weight=0.0)


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=base_mdp.time_out, time_out=True)
    fallen = DoneTerm(func=base_mdp.root_height_below_minimum, params={"minimum_height": 0.3})


@configclass
class MyGymManagerNewtonEnvCfg(ManagerBasedRLEnvCfg):
    scene: SceneCfg = SceneCfg(num_envs=4096, env_spacing=4.0, clone_in_fabric=True)
    actions: ActionsCfg = ActionsCfg()
    observations: ObservationsCfg = ObservationsCfg()
    events: EventsCfg = EventsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()

    def __post_init__(self) -> None:
        # If Isaac Gym had sim.dt and substeps, preserve the RL step:
        # sim.dt = source_sim_dt / source_substeps
        # decimation = source_substeps * controlFrequencyInv
        self.decimation = 2
        self.episode_length_s = 16.6
        self.sim.dt = 1 / 120
        self.sim.render_interval = self.decimation
        self.sim.physics = TaskPhysicsCfg()
```

## Registration

```python
import gymnasium as gym

from . import agents

gym.register(
    id="Isaac-My-Gym-Manager-Newton-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.my_gym_env_cfg:MyGymManagerNewtonEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:MyGymPPORunnerCfg",
        "rl_games_cfg_entry_point": f"{agents.__name__}:rl_games_ppo_cfg.yaml",
    },
)
```

## Custom MDP Terms

Use task-local functions or `ManagerTermBase` classes when the source logic has state. A progress reward that stores potentials must be a class:

```python
import torch

from isaaclab.envs import ManagerBasedRLEnv
from isaaclab.managers import ManagerTermBase, RewardTermCfg


class source_progress_reward(ManagerTermBase):
    def __init__(self, env: ManagerBasedRLEnv, cfg: RewardTermCfg):
        super().__init__(cfg, env)
        self.potentials = torch.zeros(env.num_envs, device=env.device)
        self.prev_potentials = torch.zeros_like(self.potentials)

    def reset(self, env_ids: torch.Tensor) -> None:
        self.potentials[env_ids] = 0.0
        self.prev_potentials[env_ids] = 0.0

    def __call__(self, env: ManagerBasedRLEnv) -> torch.Tensor:
        self.prev_potentials[:] = self.potentials[:]
        # Recompute source potential from env.scene assets here.
        return self.potentials - self.prev_potentials
```

## Newton Checks

1. Import-check Newton before writing task code:

```bash
uv run python -c "from isaaclab_newton.physics import MJWarpSolverCfg, NewtonCfg; print(NewtonCfg(solver_cfg=MJWarpSolverCfg()))"
```

2. Verify asset conversion or USD spawn under the same runtime that will run Newton.
3. Run a tiny registered-env smoke and print resolved names:

```python
cfg = load_cfg_from_registry("Isaac-My-Gym-Manager-Newton-v0", "env_cfg_entry_point")
cfg.scene.num_envs = 4
env = gym.make("Isaac-My-Gym-Manager-Newton-v0", cfg=cfg, render_mode=None)
obs, _ = env.reset()
actions = torch.zeros(env.action_space.shape, device=env.unwrapped.device)
obs, reward, terminated, truncated, _ = env.step(actions)
print(env.unwrapped.scene["robot"].data.joint_names)
print(obs["policy"].shape, reward.shape, terminated.shape, truncated.shape)
env.close()
```

4. Then run the training launch with `presets=newton_mjwarp` if the config uses `PresetCfg`.

```bash
uv run train --rl_library rsl_rl --task Isaac-My-Gym-Manager-Newton-v0 --num_envs 16 --max_iterations 1 --viz none presets=newton_mjwarp
```

If the default physics config is already Newton, still pass `presets=newton_mjwarp` once to prove the advertised preset path works.
