<!--
Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause
-->

# Direct Environment Skeleton

Use this shape for first-pass IsaacGymEnvs and OmniIsaacGymEnvs ports. Match exact imports and method names against the local Isaac Lab checkout before editing.

## Files

```text
<task_package>/
  __init__.py
  <task_name>_env.py
  <task_name>_env_cfg.py
  agents/
    __init__.py
    rsl_rl_ppo_cfg.py
    rl_games_ppo_cfg.yaml
```

## Config

```python
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.utils.configclass import configclass


@configclass
class MyTaskEnvCfg(DirectRLEnvCfg):
    decimation = 2
    episode_length_s = 5.0
    action_space = 1
    observation_space = 4
    state_space = 0

    sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=decimation)
    scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=4096, env_spacing=4.0, replicate_physics=True)

    robot_cfg: ArticulationCfg = ROBOT_CFG.replace(prim_path="/World/envs/env_.*/Robot")
```

## Environment

```python
from __future__ import annotations

from collections.abc import Sequence

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane

from .my_task_env_cfg import MyTaskEnvCfg


class MyTaskEnv(DirectRLEnv):
    cfg: MyTaskEnvCfg

    def __init__(self, cfg: MyTaskEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        self._joint_ids, _ = self.robot.find_joints(".*")
        self.joint_pos = self.robot.data.joint_pos.torch
        self.joint_vel = self.robot.data.joint_vel.torch

    def _setup_scene(self):
        self.robot = Articulation(self.cfg.robot_cfg)
        spawn_ground_plane(prim_path="/World/ground", cfg=GroundPlaneCfg())
        self.scene.clone_environments(copy_from_source=False)
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])
        self.scene.articulations["robot"] = self.robot
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    def _pre_physics_step(self, actions: torch.Tensor) -> None:
        self.actions = actions.clone()

    def _apply_action(self) -> None:
        self.robot.set_joint_effort_target_index(target=self.actions, joint_ids=self._joint_ids)

    def _get_observations(self) -> dict:
        obs = torch.cat((self.joint_pos, self.joint_vel), dim=-1)
        return {"policy": obs}

    def _get_rewards(self) -> torch.Tensor:
        return torch.zeros(self.num_envs, device=self.device)

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        terminated = torch.zeros_like(time_out)
        return terminated, time_out

    def _reset_idx(self, env_ids: Sequence[int] | None):
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        super()._reset_idx(env_ids)
        joint_pos = self.robot.data.default_joint_pos.torch[env_ids].clone()
        joint_vel = self.robot.data.default_joint_vel.torch[env_ids].clone()
        default_root_pose = self.robot.data.default_root_pose.torch[env_ids].clone()
        default_root_vel = self.robot.data.default_root_vel.torch[env_ids].clone()
        default_root_pose[:, :3] += self.scene.env_origins[env_ids]
        self.robot.write_root_pose_to_sim_index(root_pose=default_root_pose, env_ids=env_ids)
        self.robot.write_root_velocity_to_sim_index(root_velocity=default_root_vel, env_ids=env_ids)
        self.robot.write_joint_position_to_sim_index(position=joint_pos, env_ids=env_ids)
        self.robot.write_joint_velocity_to_sim_index(velocity=joint_vel, env_ids=env_ids)
```

## Registration

```python
import gymnasium as gym

from . import agents

gym.register(
    id="Isaac-My-Task-Direct-v0",
    entry_point=f"{__name__}.my_task_env:MyTaskEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.my_task_env_cfg:MyTaskEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:MyTaskPPORunnerCfg",
        "rl_games_cfg_entry_point": f"{agents.__name__}:rl_games_ppo_cfg.yaml",
    },
)
```

## Smoke Checks

```bash
uv run python -c "import <task_package>"
uv run python scripts/environments/list_envs.py | rg "Isaac-My-Task-Direct-v0"
uv run train --rl_library rsl_rl --task Isaac-My-Task-Direct-v0 --num_envs 16 --max_iterations 1 --viz none presets=physx
```

Also keep a tiny registered-env smoke script for migrations with custom assets or hand-ported rewards:

```python
cfg = load_cfg_from_registry("Isaac-My-Task-Direct-v0", "env_cfg_entry_point")
cfg.scene.num_envs = 4
env = gym.make("Isaac-My-Task-Direct-v0", cfg=cfg, render_mode=None)
obs, _ = env.reset()
actions = torch.zeros((4, cfg.action_space), device=env.unwrapped.device)
obs, rew, terminated, truncated, _ = env.step(actions)
print(obs["policy"].shape, rew.shape, terminated.shape, truncated.shape)
print(env.unwrapped.robot.data.joint_names)
env.close()
```

If the task is intended to be kit-less, run the same training smoke with `presets=newton_mjwarp` only after checking that all assets, sensors, contacts, and actuator assumptions are supported by the selected Newton path.
