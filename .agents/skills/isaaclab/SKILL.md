---
name: isaaclab
description: Isaac Lab source-tree guidance for setup, verification, env/task work, physics/renderers, sensors/actuators, RL/IL workflows, and troubleshooting. Stay lightweight on bare /isaaclab; load narrow references only after the user gives a concrete task.
---

# Isaac Lab

## Start Here

Keep startup light. If the user only invokes `/isaaclab` without a concrete
task, do not read files or run commands, and do not print a banner. Reply with:

```text
The Isaac Lab skill is ready. What would you like to do?

A few common starting points:
- Setup / install - fresh kitless uv install, or fixing a broken env
- Verify an existing install - imports and version checks
- Environment/task work - build a new env or adapt a template
- RL training / play - launch or configure training
- Architecture questions - backends, renderers, sensors, actuators
- Troubleshooting an error
```

Use `./isaaclab.sh` for Isaac Lab commands. For Python snippets or scripts, use
`./isaaclab.sh -p`; do not use bare `python` unless you are inspecting a
non-Isaac-Lab helper outside the repo.

For setup/install, read only [Install](setup/fresh-install.md) first. Do not
do branch orientation or broad environment searches. The default is a
Newton-focused kitless flow: create or activate a Python 3.12 `uv` env, then
run the repo wrapper install. Do not run `./isaaclab.sh --help` before a
Python 3.12 environment is active.

Read `AGENTS.md` only before code edits, tests, commits, contribution-policy
answers, or other tasks where repository rules matter.

Check the live tree only when the user asks a branch-sensitive question or
before changing code:

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
rg -n "^version =|requires-python" source/isaaclab/pyproject.toml pyproject.toml
```

## Task Routing

Do not preload all references. Read one narrow reference only when it matches
the task:
- setup/install: [Install](setup/fresh-install.md)
- verification: [Verify](setup/verification.md)
- errors or broken envs: [Troubleshoot](setup/troubleshooting.md)
- render modes/rendering modes/rendering presets: [Backends and renderers](architecture/backends.md)
- architecture/backends/renderers: [Overview](architecture/overview.md) or
  [Backends and renderers](architecture/backends.md)
- sensors/actuators: [Sensors and actuators](architecture/sensors-actuators.md)
- environment creation: [Builder](environments/builder.md), then
  [Examples and templates](environments/templates.md) only if examples are
  needed
- RL training/play: [RL training guide](training/guide.md)

## Guardrails

- Do not preserve benchmark numbers, local hardware notes, or old validation
  reports in answers. Re-run or omit them.
- Do not run training smoke tests automatically. After install/import/version
  checks pass, ask before launching any train or play command.
- Treat old per-framework scripts such as
  `scripts/reinforcement_learning/rsl_rl/train.py` as compatibility wrappers.
  Prefer the unified `./isaaclab.sh train --rl_library ...` and
  `./isaaclab.sh play --rl_library ...` entrypoints.
- Verify Newton support per environment. Controller plumbing and presets can
  exist even when a specific task is not ready for Newton.
