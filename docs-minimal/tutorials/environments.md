# Building Environments

**Create RL environments using either the manager-based or direct workflow, then register them with Gymnasium.**

![Manager-based environment](../_static/tutorials/tutorial_create_manager_rl_env.jpg)

## Manager-based environments

Decompose the MDP into modular managers for observations, actions, rewards, terminations, and events.

```python
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import RewardTermCfg as RewTerm, TerminationTermCfg as DoneCfg
from isaaclab.envs.mdp import joint_pos_rel, joint_vel_rel, is_alive, is_terminated, time_out

@configclass
class RewardsCfg:
    alive = RewTerm(func=is_alive, weight=1.0)
    terminating = RewTerm(func=is_terminated, weight=-2.0)
    pole_pos = RewTerm(
        func=mdp.joint_pos_deviation, weight=-1.0,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )

@configclass
class TerminationsCfg:
    time_out = DoneCfg(func=time_out, time_out=True)
    cart_out = DoneCfg(
        func=mdp.root_position_below_threshold,
        params={"threshold": 3.0},
    )

@configclass
class CartpoleEnvCfg(ManagerBasedRLEnvCfg):
    scene: CartpoleSceneCfg = CartpoleSceneCfg(num_envs=4096)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()  # Domain randomization
```

**Run it:**

```python
env = ManagerBasedRLEnv(cfg=CartpoleEnvCfg())
obs, info = env.reset()
for _ in range(1000):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
```

## Direct environments

Single class with full control over the MDP loop. Supports `@torch.jit.script` for performance.

```python
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg

class CartpoleEnv(DirectRLEnv):
    cfg: CartpoleEnvCfg

    def _setup_scene(self):
        self._robot = Articulation(self.cfg.robot_cfg)
        self.scene.articulations["robot"] = self._robot

    def _pre_physics_step(self, actions: torch.Tensor):
        self._actions = actions.clone()

    def _apply_action(self):
        self._robot.set_joint_effort_target(self._actions * self.cfg.action_scale)

    def _get_observations(self) -> dict:
        obs = torch.cat([self._robot.data.joint_pos, self._robot.data.joint_vel], dim=-1)
        return {"policy": obs}

    def _get_rewards(self) -> torch.Tensor:
        return compute_rewards(self._robot.data.joint_pos, ...)

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        terminated = torch.abs(self._cart_pos) > self.cfg.max_cart_pos
        truncated = self.episode_length_buf >= self.max_episode_length
        return terminated, truncated

    def _reset_idx(self, env_ids: torch.Tensor):
        # Randomize initial state for these environments
        ...
```

!!! tip "Performance"
    Extract reward computation into a `@torch.jit.script` function for GPU acceleration:
    ```python
    @torch.jit.script
    def compute_rewards(pole_pos: torch.Tensor, ...) -> torch.Tensor:
        ...
    ```

## Register with Gymnasium

```python
import gymnasium as gym

gym.register(
    id="Isaac-My-Task-v0",
    entry_point="my_package.my_env:MyEnv",       # Direct
    # OR entry_point="isaaclab.envs:ManagerBasedRLEnv",  # Manager-based
    kwargs={
        "env_cfg_entry_point": "my_package:MyEnvCfg",
        "rsl_rl_cfg_entry_point": "my_package.agents:MyPPORunnerCfg",
        "skrl_cfg_entry_point": "my_package.agents:skrl_ppo_cfg.yaml",
        "sb3_cfg_entry_point": "my_package.agents:sb3_ppo_cfg.yaml",
    },
)
```

Then train with any framework:
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-My-Task-v0
```

## When to use which

| | Manager-based | Direct |
|---|---|---|
| Best for | Prototyping, reward experiments | Performance, custom logic |
| Modularity | Swap reward/obs terms via config | Monolithic class |
| JIT support | No | Yes (`@torch.jit.script`) |
| Domain randomization | EventManager built-in | Manual via EventTermCfg |
| Migration from IsaacGym | Less familiar | More familiar |

## Script reference

| Script | Purpose |
|--------|---------|
| `scripts/tutorials/03_envs/create_cartpole_base_env.py` | Manager-based env from scratch |
| `scripts/tutorials/03_envs/run_cartpole_rl_env.py` | Run manager-based env |
| `scripts/environments/random_agent.py` | Test any registered env with random actions |
