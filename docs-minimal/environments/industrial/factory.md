# Factory / Forge

**High-precision industrial assembly tasks: peg insertion, gear meshing, and nut threading.**

<!-- VIDEO PLACEHOLDER -->

## Quick start

```bash
# Peg insertion (~2 hr)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Factory-PegInsert-Direct-v0 --num_envs 4096

# Gear meshing
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Factory-GearMesh-Direct-v0 --num_envs 4096

# Nut threading
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Factory-NutThread-Direct-v0 --num_envs 4096
```

## Environment variants

### Factory (legacy)
| Task ID | Task |
|---------|------|
| `Isaac-Factory-PegInsert-Direct-v0` | Peg insertion |
| `Isaac-Factory-GearMesh-Direct-v0` | Gear meshing |
| `Isaac-Factory-NutThread-Direct-v0` | Nut threading |

### Forge (next-gen)
| Task ID | Task |
|---------|------|
| `Isaac-Forge-PegInsert-Direct-v0` | Peg insertion |
| `Isaac-Forge-GearMesh-Direct-v0` | Gear meshing |
| `Isaac-Forge-NutThread-Direct-v0` | Nut threading |

### AutoMate
| Task ID | Task |
|---------|------|
| `Isaac-AutoMate-Assembly-Direct-v0` | Assembly |
| `Isaac-AutoMate-Disassembly-Direct-v0` | Disassembly |

## Source code

- Factory: `source/isaaclab_tasks/isaaclab_tasks/direct/factory/`
- Forge: `source/isaaclab_tasks/isaaclab_tasks/direct/forge/`
- AutoMate: `source/isaaclab_tasks/isaaclab_tasks/direct/automate/`
