---
name: isaaclab
description: Isaac Lab robotics RL framework guidance for the IsaacLab source tree. Use when working on setup, installation verification, manager-based or direct environment design, physics and renderer presets, sensors, actuators, RL training/play workflows, CartPole examples, or troubleshooting in Isaac Lab. Always verify details against the current checkout because develop moves quickly.
---

# Isaac Lab

## Start Here

Read `AGENTS.md` first. It is the authoritative repository guide for coding
style, test commands, changelog policy, and contribution rules.

Before giving branch-sensitive advice, check the live tree:

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
rg -n "^version =|requires-python" source/isaaclab/pyproject.toml pyproject.toml
```

Use `./isaaclab.sh` for Isaac Lab commands. For Python snippets or scripts, use
`./isaaclab.sh -p`; do not use bare `python` unless you are inspecting a
non-Isaac-Lab helper outside the repo.

## References

Setup:
- [Install](setup/fresh-install.md)
- [Verify](setup/verification.md)
- [Troubleshoot](setup/troubleshooting.md)

Architecture:
- [Overview](architecture/overview.md)
- [Backends and renderers](architecture/backends.md)
- [Sensors and actuators](architecture/sensors-actuators.md)

Environment work:
- [Builder](environments/builder.md)
- [Examples and templates](environments/templates.md)

Training:
- [RL training guide](training/guide.md)

## Current Source Anchors

Prefer these live paths over copied examples:
- Install docs: `docs/source/setup/installation/`
- Task workflows: `docs/source/overview/core-concepts/task_workflows.rst`
- Reference architecture: `docs/source/refs/reference_architecture/`
- RL scripts: `scripts/reinforcement_learning/`
- Built-in tasks: `source/isaaclab_tasks/isaaclab_tasks/`
- CartPole examples: `source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/` and `source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/`
- Sensors: `source/isaaclab/isaaclab/sensors/`
- Actuators: `source/isaaclab/isaaclab/actuators/`
- Visualizers: `source/isaaclab_visualizers/isaaclab_visualizers/`

## Guardrails

- Do not preserve benchmark numbers, local hardware notes, or old validation
  reports in answers. Re-run or omit them.
- Treat old per-framework scripts such as
  `scripts/reinforcement_learning/rsl_rl/train.py` as compatibility wrappers.
  Prefer the unified `./isaaclab.sh train --rl_library ...` and
  `./isaaclab.sh play --rl_library ...` entrypoints.
- Verify Newton support per environment. Controller plumbing and presets can
  exist even when a specific task is not ready for Newton.
