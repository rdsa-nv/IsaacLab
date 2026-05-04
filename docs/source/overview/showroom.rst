.. _showroom:

Isaac Lab Examples Dashboard
============================

Isaac Lab ships with a large set of runnable examples: visual demos, tutorial
scripts, environment probes, learning workflows, data pipelines, and benchmark
utilities. This page is a visual starting point for the examples in Isaac Lab
3.0 on the ``develop`` branch.

Run commands from the repository root. The commands below use Linux syntax:

.. code-block:: bash

   ./isaaclab.sh -p <script.py>

On Windows, use ``isaaclab.bat -p`` and Windows-style path separators.

.. raw:: html

   <div class="il-showroom">
      <section class="il-showroom-hero">
         <img src="../../_static/tasks.jpg" alt="Examples created with Isaac Lab">
         <div class="il-showroom-hero-copy">
            <p class="il-showroom-kicker">Isaac Lab 3.0 example atlas</p>
            <p class="il-showroom-lede">A show-first path through the repository: start with what moves on screen, then jump to the script that makes it happen.</p>
            <div class="il-showroom-stats" aria-label="Example counts">
               <span><strong>22</strong> visual demos</span>
               <span><strong>24</strong> tutorial scripts</span>
               <span><strong>8</strong> environment runners</span>
               <span><strong>6+</strong> learning workflows</span>
            </div>
         </div>
      </section>
      <nav class="il-showroom-jump" aria-label="Example dashboard sections">
         <a href="#demo-menagerie">Demo Menagerie</a>
         <a href="#tutorial-pathways">Tutorial Pathways</a>
         <a href="#environment-entry-points">Environment Entry Points</a>
         <a href="#learning-and-data-workflows">Learning and Data Workflows</a>
         <a href="#tools-and-benchmarks">Tools and Benchmarks</a>
      </nav>
   </div>

Start here if you want the shortest possible orientation:

* Use the **Demo Menagerie** to see Isaac Lab assets, sensors, terrain, and
  interactive scenes.
* Use **Tutorial Pathways** to learn the APIs behind those scenes.
* Use **Environment Entry Points** to inspect registered Gymnasium tasks and
  sanity-check behavior with simple agents.
* Use **Learning and Data Workflows** when you are ready to train, replay,
  generate demonstrations, or deploy policies.

If you prefer a compact prose guide, start with
:ref:`examples-getting-started`. For a traditional script map, see
:ref:`examples-script-reference`.

Demo Menagerie
--------------

The demos in ``scripts/demos`` are the fastest visual tour of what Isaac Lab can
spawn, control, sense, and render.

.. raw:: html

   <div class="il-example-grid il-example-grid-compact">
      <article class="il-example-card">
         <img src="../../_static/demos/arms.jpg" alt="Robot arms in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Assets</p>
            <h3>Robot Arms</h3>
            <p>Spawn multiple arm configurations and drive randomized joint targets.</p>
            <code>./isaaclab.sh -p scripts/demos/arms.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/bipeds.jpg" alt="Biped robots in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Assets</p>
            <h3>Bipeds</h3>
            <p>Inspect biped robot assets in a common scene.</p>
            <code>./isaaclab.sh -p scripts/demos/bipeds.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/deformables.jpg" alt="Deformable objects in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Physics</p>
            <h3>Deformables</h3>
            <p>Drop soft bodies and watch deformable-object simulation in action.</p>
            <code>./isaaclab.sh -p scripts/demos/deformables.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/h1_locomotion.jpg" alt="H1 locomotion policy in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Interactive Policy</p>
            <h3>H1 Locomotion</h3>
            <p>Drive a trained humanoid locomotion policy with keyboard controls.</p>
            <code>./isaaclab.sh -p scripts/demos/h1_locomotion.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/hands.jpg" alt="Dexterous hands in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Assets</p>
            <h3>Dexterous Hands</h3>
            <p>Spawn hand assets and command open-close behavior.</p>
            <code>./isaaclab.sh -p scripts/demos/hands.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/markers.jpg" alt="Visualization markers in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Visualization</p>
            <h3>Markers</h3>
            <p>Preview marker primitives for debugging poses, targets, and scene state.</p>
            <code>./isaaclab.sh -p scripts/demos/markers.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/multi_asset.jpg" alt="Multiple assets spawned in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Scene</p>
            <h3>Multi-Asset Scene</h3>
            <p>Clone many environments with varied assets managed by the same scene handles.</p>
            <code>./isaaclab.sh -p scripts/demos/multi_asset.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/bin_packing.jpg" alt="Bin packing demo in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Scene</p>
            <h3>Bin Packing</h3>
            <p>Spawn randomized object collections for a compact manipulation-style scene.</p>
            <code>./isaaclab.sh -p scripts/demos/bin_packing.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/pick_and_place.jpg" alt="Pick and place demo in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Interactive Control</p>
            <h3>Pick and Place</h3>
            <p>Control a parallel robot and move the cube to the target.</p>
            <code>./isaaclab.sh -p scripts/demos/pick_and_place.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/haply_teleop_franka.jpg" alt="Haply teleoperation with a Franka robot">
         <div>
            <p class="il-example-eyebrow">Teleoperation</p>
            <h3>Haply Teleoperation</h3>
            <p>Teleoperate a Franka with Haply Inverse3 and VerseGrip force feedback.</p>
            <code>./isaaclab.sh -p scripts/demos/haply_teleoperation.py --websocket_uri ws://localhost:10001 --pos_sensitivity 1.65</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/procedural_terrain.jpg" alt="Procedural terrain in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Terrain</p>
            <h3>Procedural Terrain</h3>
            <p>Generate terrain variants and preview curriculum-friendly terrain layouts.</p>
            <code>./isaaclab.sh -p scripts/demos/procedural_terrain.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/quadcopter.jpg" alt="Quadcopter in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Aerial</p>
            <h3>Quadcopter</h3>
            <p>Spawn a quadcopter in the default environment.</p>
            <code>./isaaclab.sh -p scripts/demos/quadcopter.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/quadrupeds.jpg" alt="Quadruped robots in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Assets</p>
            <h3>Quadrupeds</h3>
            <p>Spawn quadruped assets and apply standing joint-position commands.</p>
            <code>./isaaclab.sh -p scripts/demos/quadrupeds.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/overview/sensors/camera_rgb.jpg" alt="RGB camera output in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Sensors</p>
            <h3>Cameras</h3>
            <p>Render RGB, depth, normals, semantic, and instance camera outputs.</p>
            <code>./isaaclab.sh -p scripts/demos/sensors/cameras.py --enable_cameras</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/overview/sensors/contact_visualization.jpg" alt="Contact sensor visualization">
         <div>
            <p class="il-example-eyebrow">Sensors</p>
            <h3>Contact Sensor</h3>
            <p>Read and visualize contact forces in a simulated scene.</p>
            <code>./isaaclab.sh -p scripts/demos/sensors/contact_sensor.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/overview/sensors/frame_transformer_visualizer.jpg" alt="Frame transformer visualization">
         <div>
            <p class="il-example-eyebrow">Sensors</p>
            <h3>Frame Transformer</h3>
            <p>Track relative rigid-body frames with a visualizer-friendly sensor.</p>
            <code>./isaaclab.sh -p scripts/demos/sensors/frame_transformer_sensor.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/overview/sensors/imu_visualizer.jpg" alt="IMU sensor visualization">
         <div>
            <p class="il-example-eyebrow">Sensors</p>
            <h3>IMU Sensor</h3>
            <p>Measure inertial motion and inspect the resulting sensor buffers.</p>
            <code>./isaaclab.sh -p scripts/demos/sensors/imu_sensor.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/demos/multi-mesh-raycast.jpg" alt="Multi-mesh raycaster in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Sensors</p>
            <h3>Multi-Mesh RayCaster</h3>
            <p>Raycast against multiple static meshes through Warp kernels.</p>
            <code>./isaaclab.sh -p scripts/demos/sensors/multi_mesh_raycaster.py --num_envs 16 --asset_type objects</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/overview/sensors/raycaster_visualizer.jpg" alt="Ray caster camera visualization">
         <div>
            <p class="il-example-eyebrow">Sensors</p>
            <h3>RayCaster Camera</h3>
            <p>Use a ray-caster camera variant for geometric sensing.</p>
            <code>./isaaclab.sh -p scripts/demos/sensors/multi_mesh_raycaster_camera.py --num_envs 16 --asset_type objects</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/overview/sensors/camera_depth.jpg" alt="Camera depth output in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Sensors</p>
            <h3>PVA Sensor</h3>
            <p>Inspect position, velocity, and acceleration style sensor readouts.</p>
            <code>./isaaclab.sh -p scripts/demos/sensors/pva_sensor.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/overview/sensors/raycaster_patterns.jpg" alt="Ray caster patterns">
         <div>
            <p class="il-example-eyebrow">Sensors</p>
            <h3>RayCaster Sensor</h3>
            <p>Cast patterned rays against scene geometry for height and range sensing.</p>
            <code>./isaaclab.sh -p scripts/demos/sensors/raycaster_sensor.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/overview/sensors/tacsl_demo.jpg" alt="TacSL tactile sensor demo">
         <div>
            <p class="il-example-eyebrow">Sensors</p>
            <h3>TacSL Sensor</h3>
            <p>Preview visual-tactile sensing with tactile RGB and force-field outputs.</p>
            <code>./isaaclab.sh -p scripts/demos/sensors/tacsl_sensor.py --enable_cameras</code>
         </div>
      </article>
   </div>

Tutorial Pathways
-----------------

The scripts in ``scripts/tutorials`` are the most direct way to connect the
visual surface to the underlying Isaac Lab APIs. Read the full walkthroughs in
:ref:`tutorials`.

.. raw:: html

   <div class="il-example-grid">
      <article class="il-example-card il-example-card-wide">
         <img src="../../_static/tutorials/tutorial_create_empty.jpg" alt="Empty simulation tutorial result">
         <div>
            <p class="il-example-eyebrow">00 Sim</p>
            <h3>Simulation Basics</h3>
            <p>Launch the app, create an empty world, spawn primitives, log time, and adjust rendering mode.</p>
            <ul class="il-command-list">
               <li><code>scripts/tutorials/00_sim/create_empty.py</code></li>
               <li><code>scripts/tutorials/00_sim/spawn_prims.py</code></li>
               <li><code>scripts/tutorials/00_sim/launch_app.py</code></li>
               <li><code>scripts/tutorials/00_sim/log_time.py</code></li>
               <li><code>scripts/tutorials/00_sim/set_rendering_mode.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card il-example-card-wide">
         <img src="../../_static/tutorials/tutorial_run_articulation.jpg" alt="Articulation tutorial result">
         <div>
            <p class="il-example-eyebrow">01 Assets</p>
            <h3>Assets and Handles</h3>
            <p>Add robots and interact with rigid objects, articulations, deformables, and surface grippers.</p>
            <ul class="il-command-list">
               <li><code>scripts/tutorials/01_assets/add_new_robot.py</code></li>
               <li><code>scripts/tutorials/01_assets/run_rigid_object.py</code></li>
               <li><code>scripts/tutorials/01_assets/run_articulation.py</code></li>
               <li><code>scripts/tutorials/01_assets/run_deformable_object.py</code></li>
               <li><code>scripts/tutorials/01_assets/run_surface_gripper.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tutorials/tutorial_creating_a_scene.jpg" alt="Interactive scene tutorial result">
         <div>
            <p class="il-example-eyebrow">02 Scene</p>
            <h3>Interactive Scene</h3>
            <p>Use ``InteractiveScene`` to assemble and clone a higher-level simulation scene.</p>
            <code>./isaaclab.sh -p scripts/tutorials/02_scene/create_scene.py --num_envs 32</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tutorials/tutorial_create_manager_base.jpg" alt="Manager-based environment tutorial result">
         <div>
            <p class="il-example-eyebrow">03 Envs</p>
            <h3>Manager-Based Base Envs</h3>
            <p>Compare Cartpole, cube, and quadruped base-environment examples.</p>
            <ul class="il-command-list">
               <li><code>scripts/tutorials/03_envs/create_cartpole_base_env.py</code></li>
               <li><code>scripts/tutorials/03_envs/create_cube_base_env.py</code></li>
               <li><code>scripts/tutorials/03_envs/create_quadruped_base_env.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tutorials/tutorial_create_manager_rl_env.jpg" alt="Manager-based RL environment tutorial result">
         <div>
            <p class="il-example-eyebrow">03 Envs</p>
            <h3>RL Environment Loop</h3>
            <p>Run the Cartpole RL environment and inspect policy-export inference.</p>
            <ul class="il-command-list">
               <li><code>scripts/tutorials/03_envs/run_cartpole_rl_env.py</code></li>
               <li><code>scripts/tutorials/03_envs/policy_inference_in_usd.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tutorials/tutorial_add_sensors.jpg" alt="Sensor tutorial result">
         <div>
            <p class="il-example-eyebrow">04 Sensors</p>
            <h3>Sensor Integration</h3>
            <p>Add robot sensors, then run focused frame-transformer, ray-caster, ray-caster-camera, and USD-camera examples.</p>
            <ul class="il-command-list">
               <li><code>scripts/tutorials/04_sensors/add_sensors_on_robot.py</code></li>
               <li><code>scripts/tutorials/04_sensors/run_frame_transformer.py</code></li>
               <li><code>scripts/tutorials/04_sensors/run_ray_caster.py</code></li>
               <li><code>scripts/tutorials/04_sensors/run_ray_caster_camera.py</code></li>
               <li><code>scripts/tutorials/04_sensors/run_usd_camera.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tutorials/tutorial_task_space_controller.jpg" alt="Differential IK controller tutorial result">
         <div>
            <p class="il-example-eyebrow">05 Controllers</p>
            <h3>Motion Generators</h3>
            <p>Run differential IK and operational-space controller examples.</p>
            <ul class="il-command-list">
               <li><code>scripts/tutorials/05_controllers/run_diff_ik.py</code></li>
               <li><code>scripts/tutorials/05_controllers/run_osc.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/navigation/anymal_c_nav.jpg" alt="ANYmal navigation task in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">06 Deploy</p>
            <h3>Deployment Environment</h3>
            <p>Use an ANYmal-C environment scaffold while moving toward deployed policy workflows.</p>
            <code>scripts/tutorials/06_deploy/anymal_c_env.py</code>
         </div>
      </article>
   </div>

Environment Entry Points
------------------------

Use these scripts to discover and probe the registered environments listed in
:ref:`environments`.

.. raw:: html

   <div class="il-example-grid">
      <article class="il-example-card">
         <img src="../../_static/tasks.jpg" alt="Isaac Lab task collage">
         <div>
            <p class="il-example-eyebrow">Discover</p>
            <h3>List Environments</h3>
            <p>Print every registered Gymnasium environment available in this checkout.</p>
            <code>./isaaclab.sh -p scripts/environments/list_envs.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/classic/cartpole.jpg" alt="Cartpole task in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Probe</p>
            <h3>Zero Agent</h3>
            <p>Send zero actions to a task to test resets, observations, and rendering.</p>
            <code>./isaaclab.sh -p scripts/environments/zero_agent.py --task Isaac-Cartpole-v0 --num_envs 32</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/classic/cartpole.jpg" alt="Cartpole task in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">Probe</p>
            <h3>Random Agent</h3>
            <p>Drive random actions through a task for a quick behavior smoke test.</p>
            <code>./isaaclab.sh -p scripts/environments/random_agent.py --task Isaac-Cartpole-v0 --num_envs 32</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/manipulation/franka_lift.jpg" alt="Franka cube lift task">
         <div>
            <p class="il-example-eyebrow">State Machine</p>
            <h3>Lift Cube</h3>
            <p>Run a scripted manipulation policy for the Franka lift task.</p>
            <code>./isaaclab.sh -p scripts/environments/state_machine/lift_cube_sm.py --num_envs 32</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/manipulation/franka_lift.jpg" alt="Franka lifting task">
         <div>
            <p class="il-example-eyebrow">State Machine</p>
            <h3>Lift Teddy Bear</h3>
            <p>Run a scripted lifting example for object manipulation.</p>
            <code>./isaaclab.sh -p scripts/environments/state_machine/lift_teddy_bear.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/manipulation/franka_open_drawer.jpg" alt="Franka open drawer task">
         <div>
            <p class="il-example-eyebrow">State Machine</p>
            <h3>Open Cabinet</h3>
            <p>Use a scripted policy for articulated-object manipulation.</p>
            <code>./isaaclab.sh -p scripts/environments/state_machine/open_cabinet_sm.py</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/teleop/teleop_diagram.jpg" alt="Teleoperation pipeline diagram">
         <div>
            <p class="il-example-eyebrow">Teleoperation</p>
            <h3>SE(3) Teleop Agent</h3>
            <p>Control end-effectors with keyboard, SpaceMouse, gamepad, or XR-backed devices where supported.</p>
            <code>./isaaclab.sh -p scripts/environments/teleoperation/teleop_se3_agent.py --task Isaac-Stack-Cube-Franka-IK-Rel-v0 --num_envs 1 --teleop_device keyboard</code>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/locomotion/anymal_d_flat.jpg" alt="ANYmal-D flat locomotion task">
         <div>
            <p class="il-example-eyebrow">Deployment</p>
            <h3>Export IO Descriptors</h3>
            <p>Export action and observation descriptors for policy deployment pipelines.</p>
            <code>./isaaclab.sh -p scripts/environments/export_IODescriptors.py --task Isaac-Velocity-Flat-Anymal-D-v0 --output_dir ./io_descriptors</code>
         </div>
      </article>
   </div>

Learning and Data Workflows
---------------------------

These entry points connect the examples to training, evaluation, dataset
generation, and deployment. See :doc:`reinforcement-learning/rl_existing_scripts`
and :doc:`imitation-learning/index` for the full workflow docs.

.. raw:: html

   <div class="il-example-grid">
      <article class="il-example-card">
         <img src="../../_static/tasks/locomotion/h1_rough.jpg" alt="H1 rough locomotion task">
         <div>
            <p class="il-example-eyebrow">RSL-RL</p>
            <h3>Train and Play</h3>
            <p>Use the default high-throughput RL workflow for many locomotion and manipulation examples.</p>
            <ul class="il-command-list">
               <li><code>scripts/reinforcement_learning/rsl_rl/train.py</code></li>
               <li><code>scripts/reinforcement_learning/rsl_rl/play.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/classic/cartpole.jpg" alt="Cartpole task in Isaac Lab">
         <div>
            <p class="il-example-eyebrow">RL-Games</p>
            <h3>Train and Play</h3>
            <p>Run RL-Games examples for compatible manager-based and direct tasks.</p>
            <ul class="il-command-list">
               <li><code>scripts/reinforcement_learning/rl_games/train.py</code></li>
               <li><code>scripts/reinforcement_learning/rl_games/play.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/manipulation/shadow_cube.jpg" alt="Shadow hand cube manipulation task">
         <div>
            <p class="il-example-eyebrow">SKRL</p>
            <h3>Train and Play</h3>
            <p>Use SKRL for PPO, AMP, IPPO, and MAPPO examples.</p>
            <ul class="il-command-list">
               <li><code>scripts/reinforcement_learning/skrl/train.py</code></li>
               <li><code>scripts/reinforcement_learning/skrl/play.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/benchmarks/cartpole.jpg" alt="Cartpole benchmark task">
         <div>
            <p class="il-example-eyebrow">Stable-Baselines3</p>
            <h3>Train and Play</h3>
            <p>Use the SB3 examples for a compact training loop and familiar baselines.</p>
            <ul class="il-command-list">
               <li><code>scripts/reinforcement_learning/sb3/train.py</code></li>
               <li><code>scripts/reinforcement_learning/sb3/play.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/others/humanoid_amp.jpg" alt="Humanoid AMP task">
         <div>
            <p class="il-example-eyebrow">RLinf</p>
            <h3>Train and Play</h3>
            <p>Run the RLinf integration examples for supported training workflows.</p>
            <ul class="il-command-list">
               <li><code>scripts/reinforcement_learning/rlinf/train.py</code></li>
               <li><code>scripts/reinforcement_learning/rlinf/play.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/benchmarks/cartpole_camera.jpg" alt="Cartpole camera task">
         <div>
            <p class="il-example-eyebrow">Ray</p>
            <h3>Distributed Experiments</h3>
            <p>Launch Ray jobs, tune hyperparameters, and collect experiment artifacts.</p>
            <ul class="il-command-list">
               <li><code>scripts/reinforcement_learning/ray/launch.py</code></li>
               <li><code>scripts/reinforcement_learning/ray/tuner.py</code></li>
               <li><code>scripts/reinforcement_learning/ray/submit_job.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/mimic/franka_mimic_imitation_learning.jpg" alt="Franka mimic imitation learning">
         <div>
            <p class="il-example-eyebrow">Isaac Lab Mimic</p>
            <h3>Generate and Annotate</h3>
            <p>Generate, annotate, and consolidate demonstrations for imitation learning.</p>
            <ul class="il-command-list">
               <li><code>scripts/imitation_learning/isaaclab_mimic/generate_dataset.py</code></li>
               <li><code>scripts/imitation_learning/isaaclab_mimic/annotate_demos.py</code></li>
               <li><code>scripts/imitation_learning/isaaclab_mimic/consolidated_demo.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/mimic/franka_datagen.jpg" alt="Franka demonstration data generation">
         <div>
            <p class="il-example-eyebrow">Robomimic</p>
            <h3>Train, Play, Evaluate</h3>
            <p>Train and evaluate policies from demonstration datasets.</p>
            <ul class="il-command-list">
               <li><code>scripts/imitation_learning/robomimic/train.py</code></li>
               <li><code>scripts/imitation_learning/robomimic/play.py</code></li>
               <li><code>scripts/imitation_learning/robomimic/robust_eval.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/navigation/anymal_c_nav.jpg" alt="ANYmal-C navigation task">
         <div>
            <p class="il-example-eyebrow">Deployment</p>
            <h3>LEAPP and Sim2Sim</h3>
            <p>Export or transfer trained policies into deployment-oriented workflows.</p>
            <ul class="il-command-list">
               <li><code>scripts/reinforcement_learning/leapp/deploy.py</code></li>
               <li><code>scripts/reinforcement_learning/leapp/rsl_rl/export.py</code></li>
               <li><code>scripts/sim2sim_transfer/rsl_rl_transfer.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/manipulation/g1_pick_place_locomanipulation.jpg" alt="G1 loco-manipulation task">
         <div>
            <p class="il-example-eyebrow">Synthetic Data</p>
            <h3>Locomanipulation SDG</h3>
            <p>Generate loco-manipulation data and convert or roll out GR00T-style policies.</p>
            <ul class="il-command-list">
               <li><code>scripts/imitation_learning/locomanipulation_sdg/generate_data.py</code></li>
               <li><code>scripts/imitation_learning/locomanipulation_sdg/gr00t/convert_dataset.py</code></li>
               <li><code>scripts/imitation_learning/locomanipulation_sdg/gr00t/rollout_policy.py</code></li>
            </ul>
         </div>
      </article>
   </div>

Tools and Benchmarks
--------------------

The remaining scripts are utility examples for asset conversion, demonstration
recording, dataset conversion, and performance checks.

.. raw:: html

   <div class="il-example-grid il-example-grid-small">
      <article class="il-example-card">
         <img src="../../_static/tutorials/tutorial_convert_urdf.jpg" alt="URDF conversion tutorial result">
         <div>
            <p class="il-example-eyebrow">Assets</p>
            <h3>Conversion Tools</h3>
            <p>Convert or inspect imported assets and meshes.</p>
            <ul class="il-command-list">
               <li><code>scripts/tools/convert_urdf.py</code></li>
               <li><code>scripts/tools/convert_mjcf.py</code></li>
               <li><code>scripts/tools/convert_mesh.py</code></li>
               <li><code>scripts/tools/convert_instanceable.py</code></li>
               <li><code>scripts/tools/check_instanceable.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/tasks/manipulation/franka_stack.jpg" alt="Franka cube stacking environment">
         <div>
            <p class="il-example-eyebrow">Datasets</p>
            <h3>Demonstration Tools</h3>
            <p>Record, replay, merge, and convert demonstration datasets.</p>
            <ul class="il-command-list">
               <li><code>scripts/tools/record_demos.py</code></li>
               <li><code>scripts/tools/replay_demos.py</code></li>
               <li><code>scripts/tools/hdf5_to_mp4.py</code></li>
               <li><code>scripts/tools/mp4_to_hdf5.py</code></li>
               <li><code>scripts/tools/merge_hdf5_datasets.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/benchmarks/g1_rough.jpg" alt="G1 rough locomotion benchmark">
         <div>
            <p class="il-example-eyebrow">Performance</p>
            <h3>Benchmarks</h3>
            <p>Measure startup, camera, view, robot-load, non-RL, RSL-RL, and RL-Games performance.</p>
            <ul class="il-command-list">
               <li><code>scripts/benchmarks/benchmark_startup.py</code></li>
               <li><code>scripts/benchmarks/benchmark_cameras.py</code></li>
               <li><code>scripts/benchmarks/benchmark_rsl_rl.py</code></li>
               <li><code>scripts/benchmarks/benchmark_rlgames.py</code></li>
            </ul>
         </div>
      </article>
      <article class="il-example-card">
         <img src="../../_static/benchmarks/cartpole_camera.jpg" alt="Camera benchmark example">
         <div>
            <p class="il-example-eyebrow">Diagnostics</p>
            <h3>Helper Utilities</h3>
            <p>Use smaller helper scripts for mesh processing, quaternion checks, Warp wrapping, Cosmos prompts, and checkpoint publishing.</p>
            <ul class="il-command-list">
               <li><code>scripts/tools/process_meshes_to_obj.py</code></li>
               <li><code>scripts/tools/find_quaternions.py</code></li>
               <li><code>scripts/tools/wrap_warp_to_torch.py</code></li>
               <li><code>scripts/tools/cosmos/cosmos_prompt_gen.py</code></li>
               <li><code>scripts/tools/train_and_publish_checkpoints.py</code></li>
            </ul>
         </div>
      </article>
   </div>
