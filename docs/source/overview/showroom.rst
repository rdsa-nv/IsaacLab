.. _showroom:
.. _living-examples:

Isaac Lab Living Examples
=========================

This page prototypes a living-doc format for Isaac Lab examples. Instead of a
large gallery of scripts, each example gets an evidence dossier: the source entry
point, the task, the command used to build or exercise it, the rollout command,
the expected recording, the preview asset, and the checkpoint relationship.

The two dossiers below are intentionally small. They are meant to prove the
shape before the format is expanded across every example in Isaac Lab 3.0.

.. raw:: html

   <div class="il-living-page">
      <section class="il-living-hero">
         <img src="../../_static/tasks.jpg" alt="Examples created with Isaac Lab">
         <div class="il-living-hero-copy">
            <p class="il-living-kicker">Isaac Lab 3.0 living examples</p>
            <p class="il-living-lede">Example docs that carry their own evidence: source, smoke test, rollout, recording, preview, and checkpoint.</p>
            <div class="il-living-stats" aria-label="Prototype evidence counts">
               <span><strong>2</strong> prototype dossiers</span>
               <span><strong>6</strong> evidence slots each</span>
               <span><strong>1</strong> manifest</span>
               <span><strong>0</strong> claimed rollouts without artifacts</span>
            </div>
         </div>
      </section>
   </div>

Runtime status in this checkout
-------------------------------

This clean docs environment has not installed the Isaac Lab runtime extensions
yet. A direct runtime probe on May 4, 2026:

.. code-block:: bash

   ./isaaclab.sh -p -c "import isaaclab_tasks; print('isaaclab_tasks import ok')"

returned ``ModuleNotFoundError: No module named 'isaaclab_tasks'``. The docs
and static evidence can be built and checked here, but the simulator rollouts
below should be marked complete only after the listed commands produce the
checkpoint and video artifacts in a fully installed Isaac Lab environment.

Evidence Model
--------------

Each dossier tracks the same six slots:

.. raw:: html

   <div class="il-living-model" aria-label="Living example evidence model">
      <div><span class="il-living-dot il-living-ready"></span><strong>Source</strong><p>Script and task entry point present in this branch.</p></div>
      <div><span class="il-living-dot il-living-pending"></span><strong>Smoke test</strong><p>Short command that should finish without human input.</p></div>
      <div><span class="il-living-dot il-living-pending"></span><strong>Rollout</strong><p>Playback command that exercises the policy path.</p></div>
      <div><span class="il-living-dot il-living-pending"></span><strong>Recording</strong><p>MP4/WebM artifact emitted by the run.</p></div>
      <div><span class="il-living-dot il-living-ready"></span><strong>Preview</strong><p>Static image available to the docs build.</p></div>
      <div><span class="il-living-dot il-living-checkpoint"></span><strong>Checkpoint</strong><p>Generated locally or resolved from published weights.</p></div>
   </div>

Cartpole RSL-RL Smoke Dossier
-----------------------------

.. raw:: html

   <article class="il-living-dossier">
      <div class="il-living-media">
         <img src="../../_static/tasks/classic/cartpole.jpg" alt="Cartpole task in Isaac Lab">
         <span class="il-living-badge il-living-badge-pending">Runtime pending</span>
      </div>
      <div class="il-living-copy">
         <p class="il-living-eyebrow">Smallest trainable loop</p>
         <h2>Cartpole checkpoint and rollout</h2>
         <p>Cartpole is the first useful living-doc target because it proves task registration, vectorized simulation, RSL-RL training, checkpoint creation, playback, and video capture with a low-cost state-based environment.</p>
         <dl class="il-living-facts">
            <div><dt>Task</dt><dd><code>Isaac-Cartpole-v0</code></dd></div>
            <div><dt>Train entry point</dt><dd><code>scripts/reinforcement_learning/rsl_rl/train.py</code></dd></div>
            <div><dt>Play entry point</dt><dd><code>scripts/reinforcement_learning/rsl_rl/play.py</code></dd></div>
            <div><dt>Preview</dt><dd><code>docs/source/_static/tasks/classic/cartpole.jpg</code></dd></div>
         </dl>
      </div>
   </article>

Train just long enough to create a checkpoint and a training video:

.. code-block:: bash

   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
      --task Isaac-Cartpole-v0 \
      --headless \
      --num_envs 256 \
      --max_iterations 2 \
      --video \
      --video_length 120 \
      agent.save_interval=1

Then replay the generated checkpoint and record the rollout:

.. code-block:: bash

   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Cartpole-v0 \
      --headless \
      --num_envs 64 \
      --video \
      --video_length 180 \
      --load_run <cartpole-run-folder> \
      --checkpoint model_1.pt

Expected artifacts:

* ``logs/rsl_rl/cartpole/<run-folder>/model_1.pt``
* ``logs/rsl_rl/cartpole/<run-folder>/videos/train/rl-video-step-0.mp4``
* ``logs/rsl_rl/cartpole/<run-folder>/videos/play/rl-video-step-0.mp4``

H1 Locomotion Policy Dossier
----------------------------

.. raw:: html

   <article class="il-living-dossier">
      <div class="il-living-media">
         <img src="../../_static/demos/h1_locomotion.jpg" alt="H1 locomotion policy in Isaac Lab">
         <span class="il-living-badge il-living-badge-checkpoint">Published checkpoint</span>
      </div>
      <div class="il-living-copy">
         <p class="il-living-eyebrow">Checkpoint-backed policy preview</p>
         <h2>H1 rough-terrain rollout</h2>
         <p>The H1 demo is a stronger visual target. The interactive demo loads a published RSL-RL checkpoint, while the play script provides the repeatable headless path for recorded evidence.</p>
         <dl class="il-living-facts">
            <div><dt>Task</dt><dd><code>Isaac-Velocity-Rough-H1-Play-v0</code></dd></div>
            <div><dt>Demo entry point</dt><dd><code>scripts/demos/h1_locomotion.py</code></dd></div>
            <div><dt>Recorded entry point</dt><dd><code>scripts/reinforcement_learning/rsl_rl/play.py</code></dd></div>
            <div><dt>Preview</dt><dd><code>docs/source/_static/demos/h1_locomotion.jpg</code></dd></div>
         </dl>
      </div>
   </article>

Record a deterministic playback run from the published checkpoint:

.. code-block:: bash

   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
      --task Isaac-Velocity-Rough-H1-Play-v0 \
      --headless \
      --num_envs 25 \
      --use_pretrained_checkpoint \
      --video \
      --video_length 240

Open the interactive version when a person should drive the policy:

.. code-block:: bash

   ./isaaclab.sh -p scripts/demos/h1_locomotion.py

Expected artifacts:

* published checkpoint resolved by
  ``get_published_pretrained_checkpoint("rsl_rl", "Isaac-Velocity-Rough-H1-v0")``
* ``<resolved-checkpoint-dir>/videos/play/rl-video-step-0.mp4``
* ``<resolved-checkpoint-dir>/exported/policy.pt``
* ``<resolved-checkpoint-dir>/exported/policy.onnx``

Machine-Readable Manifest
-------------------------

The prototype evidence is mirrored in a JSON manifest so the page can grow into
a generated dashboard instead of hand-maintained prose.

.. literalinclude:: ../_static/living_examples/manifest.json
   :language: json

Next Steps
----------

The next useful increment is a runner that reads the manifest, executes each
``build_command`` and ``rollout_command``, hashes the resulting artifacts, and
updates each status from ``runtime_pending`` to ``recorded`` only when the video
and checkpoint files exist.
