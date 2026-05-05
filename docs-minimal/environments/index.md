# Environment Gallery

Every environment below is ready to train. Click through for the training command, configuration, and video.

| | | |
|:-:|:-:|:-:|
| ![Quadrupeds](../_static/demos/quadrupeds.jpg) | ![Bipeds](../_static/demos/bipeds.jpg) | ![Arms](../_static/demos/arms.jpg) |
| Quadrupeds | Bipeds & Humanoids | Manipulation |
| ![Hands](../_static/demos/hands.jpg) | ![Quadcopter](../_static/demos/quadcopter.jpg) | ![Deformables](../_static/demos/deformables.jpg) |
| Dexterous Hands | Aerial | Deformable Objects |

## Locomotion

Velocity tracking on flat and rough terrain.

| Environment | Robot | Terrain | Task ID | Approx. Training Time |
|-------------|-------|---------|---------|-----------------------|
| [ANYmal-C](locomotion/anymal-c.md) | ANYmal-C quadruped | Flat / Rough | `Isaac-Velocity-Flat-Anymal-C-v0` | 30 min / 2 hr |
| [Unitree Go2](locomotion/go2.md) | Unitree Go2 | Flat / Rough | `Isaac-Velocity-Flat-Unitree-Go2-v0` | 30 min / 2 hr |
| [Unitree H1](locomotion/h1.md) | Unitree H1 humanoid | Flat / Rough | `Isaac-Velocity-Flat-H1-v0` | 1 hr / 3 hr |
| [Unitree G1](locomotion/g1.md) | Unitree G1 humanoid | Flat / Rough | `Isaac-Velocity-Flat-G1-v0` | 1 hr / 3 hr |
| [Spot](locomotion/spot.md) | Boston Dynamics Spot | Flat | `Isaac-Velocity-Flat-Spot-v0` | 30 min |
| [ANYmal-D](locomotion/anymal-d.md) | ANYmal-D quadruped | Flat / Rough | `Isaac-Velocity-Flat-Anymal-D-v0` | 30 min / 2 hr |
| [Cassie](locomotion/cassie.md) | Agility Cassie biped | Flat / Rough | `Isaac-Velocity-Flat-Cassie-v0` | 1 hr / 3 hr |

## Manipulation

Arm + gripper tasks with Franka, UR10, and other robots.

| Environment | Robot | Task | Task ID | Approx. Training Time |
|-------------|-------|------|---------|-----------------------|
| [Franka Lift](manipulation/franka-lift.md) | Franka Emika | Lift a cube to target | `Isaac-Lift-Cube-Franka-v0` | 45 min |
| [Franka Cabinet](manipulation/franka-cabinet.md) | Franka Emika | Open a drawer | `Isaac-Open-Drawer-Franka-v0` | 30 min |
| [Franka Reach](manipulation/franka-reach.md) | Franka Emika | Reach a target pose | `Isaac-Reach-Franka-v0` | 20 min |
| [Franka Stack](manipulation/franka-stack.md) | Franka Emika | Stack cubes | `Isaac-Stack-Cube-Franka-v0` | 2 hr |

## Dexterous Manipulation

In-hand object manipulation with multi-fingered hands.

| Environment | Robot | Task | Task ID | Approx. Training Time |
|-------------|-------|------|---------|-----------------------|
| [Allegro Hand](dexterous/allegro.md) | Allegro Hand | Cube repose | `Isaac-Repose-Cube-Allegro-Direct-v0` | 8 hr |
| [Shadow Hand](dexterous/shadow-hand.md) | Shadow Hand | Cube repose | `Isaac-Repose-Cube-Shadow-Direct-v0` | 8 hr |

## Classic Control

Standard RL benchmarks for quick iteration and debugging.

| Environment | Task | Task ID | Approx. Training Time |
|-------------|------|---------|-----------------------|
| [Cartpole](classic/cartpole.md) | Balance a pole | `Isaac-Cartpole-Direct-v0` | 5 min |
| [Ant](classic/ant.md) | Ant locomotion | `Isaac-Ant-Direct-v0` | 15 min |
| [Humanoid](classic/humanoid.md) | Humanoid locomotion | `Isaac-Humanoid-Direct-v0` | 30 min |

## Aerial

| Environment | Robot | Task | Task ID | Approx. Training Time |
|-------------|-------|------|---------|-----------------------|
| [Quadcopter](aerial/quadcopter.md) | Generic quadcopter | Hover / waypoint | `Isaac-Quadcopter-Direct-v0` | 30 min |

## Industrial

| Environment | Robot | Task | Task ID | Approx. Training Time |
|-------------|-------|------|---------|-----------------------|
| [Factory](industrial/factory.md) | Franka | Peg insert, gear mesh, nut thread | `Isaac-Factory-PegInsert-Direct-v0` | 2+ hr |

---

### Environment naming convention

```
Isaac-{Task}-{Variant}-{Robot}-{Controller}-{Version}
```

- **Task**: What the robot does (`Velocity`, `Lift`, `Reach`, `Repose`)
- **Variant**: Terrain or object variant (`Flat`, `Rough`, `Cube`)
- **Robot**: Robot model (`Anymal-C`, `Franka`, `Allegro`)
- **Controller**: Optional control mode (`IK-Abs`, `IK-Rel`, `OSC`)
- **Version**: Always `v0`

Append `-Play` to get the evaluation-only variant (fewer envs, deterministic).

### Direct vs Manager-Based

Each task has two implementations:

- **Direct** (`-Direct-`): Single Python class, full control, fastest iteration
- **Manager-Based** (no `-Direct-`): Modular MDP components, easier to customize rewards/observations

See [Environment Types](../architecture/environments.md) for details.
