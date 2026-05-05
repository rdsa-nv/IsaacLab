# Environment Types

Isaac Lab has two ways to define RL environments. Both produce Gymnasium-compatible envs that work with all four RL frameworks.

## Direct environments

![Direct workflow](../_static/task-workflows/direct-based-light.svg)

A single Python class that owns the full MDP loop. Best for custom tasks where you want full control.

```python
class CartpoleEnv(DirectRLEnv):
    cfg: CartpoleEnvCfg

    def _setup_scene(self):
        self._cartpole = Articulation(self.cfg.robot_cfg)
        self.scene.articulations["cartpole"] = self._cartpole

    def _get_observations(self) -> dict:
        obs = torch.cat([
            self._cartpole.data.joint_pos,
            self._cartpole.data.joint_vel,
        ], dim=-1)
        return {"policy": obs}

    def _get_rewards(self) -> torch.Tensor:
        return (
            self.cfg.rew_scale_alive * (1.0 - self.reset_terminated.float())
            + self.cfg.rew_scale_pole_pos * torch.abs(self._pole_pos)
        )

    def _pre_physics_step(self, actions: torch.Tensor):
        self._actions = actions.clone()
        self._cartpole.set_joint_effort_target(
            self._actions * self.cfg.action_scale
        )

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        terminated = torch.abs(self._cart_pos) > self.cfg.max_cart_pos
        truncated = self.episode_length_buf >= self.max_episode_length
        return terminated, truncated

    def _reset_idx(self, env_ids: Sequence[int]):
        # randomize initial joint positions
        ...
```

**When to use Direct:**

- You want maximum performance and minimal abstraction
- Your reward/observation logic is tightly coupled
- You're porting from IsaacGym or another framework

## Manager-based environments

![Manager-based workflow](../_static/task-workflows/manager-based-light.svg)

Modular environments where observations, actions, rewards, terminations, and events are separate components managed by "managers."

```python
@configclass
class LocomotionVelocityEnvCfg(ManagerBasedRLEnvCfg):
    # Scene
    scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=4096)

    # MDP components — each is a separate, reusable class
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    curriculum: CurriculumCfg = CurriculumCfg()
```

Each component references a function:

```python
@configclass
class RewardsCfg:
    track_lin_vel_xy = RewTerm(
        func=mdp.track_lin_vel_xy_exp,
        weight=1.0,
        params={"std": 0.25, "command_name": "base_velocity"},
    )
    feet_air_time = RewTerm(
        func=mdp.feet_air_time,
        weight=0.5,
        params={"threshold": 0.5, "sensor_cfg": ...},
    )
```

**When to use Manager-based:**

- You want to mix-and-match reward terms, observations, etc.
- You're experimenting with different MDP designs
- You want terrain curricula, domain randomization events, etc.

## Comparison

| Feature | Direct | Manager-based |
|---------|--------|---------------|
| Complexity | Lower | Higher |
| Modularity | Monolithic | Composable |
| Performance | Slightly faster | Slightly slower |
| Customization | Edit Python class | Swap config entries |
| Terrain curriculum | Manual | Built-in |
| Domain randomization | Manual | Event manager |
| Best for | Simple tasks, porting | Complex tasks, research |

## Registration

Both types register with Gymnasium the same way:

```python
gym.register(
    id="Isaac-My-Task-v0",
    entry_point="my_package.my_env:MyEnv",
    kwargs={
        "env_cfg_entry_point": "my_package.my_env_cfg:MyEnvCfg",
        "rsl_rl_cfg_entry_point": "my_package.agents:MyPPORunnerCfg",
        "skrl_cfg_entry_point": "my_package.agents:skrl_ppo_cfg.yaml",
        "sb3_cfg_entry_point": "my_package.agents:sb3_ppo_cfg.yaml",
    },
)
```

The training scripts use Hydra to resolve the config entry points automatically.
