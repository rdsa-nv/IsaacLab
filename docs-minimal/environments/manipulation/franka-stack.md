# Franka Stack

**Stack colored cubes in the correct order using the Franka arm.**

![Franka stacking cubes](../../_static/tasks/manipulation/franka_stack.jpg)

## Quick start

```bash
# Train (~2 hr)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Stack-Cube-Franka-v0 --num_envs 4096

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Stack-Cube-Franka-v0 --num_envs 32
```

## Environment variants

| Task ID | Controller | Notes |
|---------|-----------|-------|
| `Isaac-Stack-Cube-Franka-v0` | Joint position | Two cubes |
| `Isaac-Stack-Cube-Franka-IK-Rel-v0` | IK (relative) | Two cubes |
| `Isaac-Stack-Cube-Franka-IK-Abs-v0` | IK (absolute) | Two cubes |
| `Isaac-Stack-Cube-RedGreen-Franka-IK-Rel-v0` | IK (relative) | Red on green |
| `Isaac-Stack-Cube-RedGreenBlue-Franka-IK-Rel-v0` | IK (relative) | Three cubes |
| `Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-v0` | IK (relative) | Vision-based |
| `Isaac-Stack-Cube-Instance-Randomize-Franka-v0` | Joint position | Domain randomization |

## Source code

- Config: `source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/stack/config/franka/`
