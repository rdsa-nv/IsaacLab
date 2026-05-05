# Franka Cabinet

**Open a cabinet drawer using the Franka Emika Panda arm.**

![Franka opening cabinet drawer](../../_static/tasks/manipulation/franka_open_drawer.jpg)

## Quick start

=== "Manager-based (modular)"

    ```bash
    # Train (~30 min)
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
      --task Isaac-Open-Drawer-Franka-v0 --num_envs 4096

    # Evaluate
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Open-Drawer-Franka-v0 --num_envs 32
    ```

=== "Direct (single-file)"

    ```bash
    # Train (~45 min)
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
      --task Isaac-Franka-Cabinet-Direct-v0 --num_envs 4096

    # Evaluate
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Franka-Cabinet-Direct-v0 --num_envs 32
    ```

## Environment variants

| Task ID | Controller | Implementation |
|---------|-----------|----------------|
| `Isaac-Open-Drawer-Franka-v0` | Joint position | Manager-based |
| `Isaac-Open-Drawer-Franka-IK-Abs-v0` | IK (absolute) | Manager-based |
| `Isaac-Open-Drawer-Franka-IK-Rel-v0` | IK (relative) | Manager-based |
| `Isaac-Franka-Cabinet-Direct-v0` | Joint position | Direct |

## Agent config (RSL-RL PPO)

=== "Manager-based"

    ```python
    @configclass
    class CabinetPPORunnerCfg(RslRlOnPolicyRunnerCfg):
        num_steps_per_env = 96
        max_iterations = 400
        experiment_name = "franka_open_drawer"
        policy = RslRlPpoActorCriticCfg(
            actor_hidden_dims=[256, 128, 64],
            critic_hidden_dims=[256, 128, 64],
            activation="elu",
        )
        algorithm = RslRlPpoAlgorithmCfg(
            clip_param=0.2,
            entropy_coef=1e-3,
            learning_rate=5.0e-4,
            gamma=0.99,
            lam=0.95,
            desired_kl=0.02,
        )
    ```

=== "Direct"

    ```python
    @configclass
    class FrankaCabinetPPORunnerCfg(RslRlOnPolicyRunnerCfg):
        num_steps_per_env = 16
        max_iterations = 1500
        experiment_name = "franka_cabinet_direct"
        policy = RslRlPpoActorCriticCfg(
            actor_hidden_dims=[256, 128, 64],
            critic_hidden_dims=[256, 128, 64],
            activation="elu",
        )
        algorithm = RslRlPpoAlgorithmCfg(
            clip_param=0.2,
            entropy_coef=0.0,
            num_learning_epochs=8,
            num_mini_batches=8,
            learning_rate=5.0e-4,
        )
    ```

## Source code

- Direct env: `source/isaaclab_tasks/isaaclab_tasks/direct/franka_cabinet/`
- Manager-based config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/cabinet/config/franka/`
