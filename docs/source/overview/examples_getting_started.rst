.. _examples-getting-started:

Examples: Getting Started
=========================

Isaac Lab examples are meant to be run from the repository root. If you are new
to the project, start with a visual demo, run one tutorial script, then inspect a
registered environment before moving into training or imitation workflows.

On Linux, commands use ``./isaaclab.sh -p``. On Windows, use
``isaaclab.bat -p`` and Windows-style path separators.

Example Families
----------------

``scripts/demos``
   Visual demonstrations for assets, sensors, terrains, interactive control, and
   policy playback. Use these first when you want to see what Isaac Lab can do.

``scripts/tutorials``
   Small scripts that introduce the core APIs in sequence: launching simulation,
   spawning assets, building scenes, defining environments, adding sensors, using
   controllers, and exporting policies.

``scripts/environments``
   Utilities for listing registered tasks, checking environments with zero or
   random actions, teleoperating, and running simple state machines.

``scripts/reinforcement_learning``
   Training and play scripts for supported RL frameworks. Use these after you
   have chosen an environment ID and installed the framework you want to train
   with.

``scripts/imitation_learning``
   Data generation, teleoperation, dataset conversion, training, and evaluation
   workflows for imitation learning examples.

Recommended First Commands
--------------------------

Run a visual demo:

.. code-block:: bash

   ./isaaclab.sh -p scripts/demos/arms.py

Run the first simulation tutorial:

.. code-block:: bash

   ./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py

List available environments and filter the list:

.. code-block:: bash

   ./isaaclab.sh -p scripts/environments/list_envs.py
   ./isaaclab.sh -p scripts/environments/list_envs.py --keyword Cartpole

Sanity-check a task with a simple agent:

.. code-block:: bash

   ./isaaclab.sh -p scripts/environments/random_agent.py --task Isaac-Cartpole-v0 --num_envs 32

When you are ready to train, install one RL backend and launch a small run:

.. code-block:: bash

   ./isaaclab.sh -i rsl_rl
   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless

Choosing a Path
---------------

Choose **demos** when you want a quick visual check of robots, sensors, terrain,
or interactive policies.

Choose **tutorials** when you want to learn how the scene, asset, sensor,
controller, or environment APIs are assembled. The tutorial index is
:ref:`tutorials`.

Choose **environment runners** when you already have a task name and want to
inspect behavior, verify observations and actions, or test a hand-written policy.
The full task list is documented in :ref:`environments`.

Choose **learning workflows** when you want to train, replay, evaluate, or export
policies. RL entry points are described in
:doc:`reinforcement-learning/rl_existing_scripts`; imitation learning workflows
start at :doc:`imitation-learning/index`.

Where to Go Next
----------------

For a visual map of the examples, see :ref:`showroom`. For a structured learning
path, continue through :ref:`tutorials`. For task selection, start with
:ref:`environments`, then move to
:doc:`reinforcement-learning/rl_existing_scripts` or
:doc:`imitation-learning/index` depending on the workflow you want to run.
