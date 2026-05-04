.. _examples-script-reference:

Example Script Reference
========================

This page is a compact map of the runnable example scripts under ``scripts/``.
Run commands from the Isaac Lab repository root. The examples below use the
Linux launcher; on Windows, use ``isaaclab.bat -p`` and backslash-separated
paths.

For script-specific options, append ``--help``:

.. code:: bash

   ./isaaclab.sh -p scripts/environments/random_agent.py --help

.. list-table::
   :header-rows: 1
   :widths: 24 36 40

   * - Area
     - What it covers
     - Representative commands
   * - ``scripts/demos``
     - Visual demonstrations of assets, sensors, manipulators, legged robots,
       terrain, teleoperation, and scene composition.
     - .. code:: bash

          ./isaaclab.sh -p scripts/demos/arms.py
          ./isaaclab.sh -p scripts/demos/sensors/cameras.py --enable_cameras
          ./isaaclab.sh -p scripts/demos/procedural_terrain.py
   * - ``scripts/tutorials``
     - Step-by-step standalone examples for launching simulation, spawning
       assets, building scenes and environments, adding sensors, and running
       controllers.
     - .. code:: bash

          ./isaaclab.sh -p scripts/tutorials/00_sim/launch_app.py
          ./isaaclab.sh -p scripts/tutorials/01_assets/run_articulation.py
          ./isaaclab.sh -p scripts/tutorials/05_controllers/run_diff_ik.py
   * - ``scripts/environments``
     - Utilities for discovering registered tasks, smoke-testing environments
       with simple agents, running state machines, teleoperation, and exporting
       I/O descriptors.
     - .. code:: bash

          ./isaaclab.sh -p scripts/environments/list_envs.py
          ./isaaclab.sh -p scripts/environments/zero_agent.py --task Isaac-Cartpole-v0 --num_envs 32
          ./isaaclab.sh -p scripts/environments/state_machine/lift_cube_sm.py --num_envs 32
   * - ``scripts/reinforcement_learning``
     - Training, playing, exporting, and orchestration entry points for
       supported RL backends such as RSL-RL, RL-Games, SKRL, Stable-Baselines3,
       Ray, RLinf, and LEAPP.
     - .. code:: bash

          ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --num_envs 64
          ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Cartpole-v0
          ./isaaclab.sh -p scripts/reinforcement_learning/ray/launch.py --help
   * - ``scripts/imitation_learning``
     - Dataset generation, annotation, consolidation, playback, training, and
       evaluation workflows for Isaac Lab Mimic, Robomimic, and locomotion data
       generation.
     - .. code:: bash

          ./isaaclab.sh -p scripts/tools/record_demos.py \
              --task Isaac-Lift-Cube-Franka-IK-Abs-v0 \
              --dataset_file ./datasets/lift_cube.hdf5
          ./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py --help
          ./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py --help
   * - ``scripts/tools``
     - Asset conversion, mesh processing, dataset conversion, demo recording and
       replay, prompt generation, checkpoint publishing, and small inspection
       utilities.
     - .. code:: bash

          ./isaaclab.sh -p scripts/tools/convert_urdf.py --help
          ./isaaclab.sh -p scripts/tools/replay_demos.py --help
          ./isaaclab.sh -p scripts/tools/hdf5_to_mp4.py --help
   * - ``scripts/benchmarks``
     - Startup, simulation, sensor, view, robot-loading, non-RL, and training
       benchmark entry points, plus shell wrappers for benchmark suites.
     - .. code:: bash

          ./isaaclab.sh -p scripts/benchmarks/benchmark_startup.py --help
          ./isaaclab.sh -p scripts/benchmarks/benchmark_rsl_rl.py --help
          bash scripts/benchmarks/run_non_rl_benchmarks.sh

Task-Based Commands
-------------------

Many environment and learning scripts require a registered task name. List
available tasks first, then pass a task to the script:

.. code:: bash

   ./isaaclab.sh -p scripts/environments/list_envs.py
   ./isaaclab.sh -p scripts/environments/random_agent.py --task <TASK_NAME> --num_envs 32
   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task <TASK_NAME>

Common launcher options such as ``--headless``, ``--device``, and
``--enable_cameras`` are provided by the Isaac Lab application launcher and are
available on most scripts that start Isaac Sim.
