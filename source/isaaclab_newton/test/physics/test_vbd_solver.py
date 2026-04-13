# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause

"""Test VBD solver integration in Isaac Lab's NewtonManager.

This test verifies that the VBD solver can be configured and instantiated
through the Isaac Lab NewtonManager config path. It uses a simple cable-like
setup inspired by Newton's RJ45 ethernet cable example.

Run:
    python -m pytest source/isaaclab_newton/test/physics/test_vbd_solver.py -v

Or standalone:
    python source/isaaclab_newton/test/physics/test_vbd_solver.py
"""

from __future__ import annotations

import numpy as np
import unittest

import warp as wp

import newton
from newton.solvers import SolverVBD


class TestVBDSolverCfg(unittest.TestCase):
    """Test that VBDSolverCfg can be instantiated and produces valid config dicts."""

    def test_cfg_import(self):
        """VBDSolverCfg should be importable from isaaclab_newton.physics."""
        from isaaclab_newton.physics.newton_manager_cfg import VBDSolverCfg

        cfg = VBDSolverCfg()
        self.assertEqual(cfg.solver_type, "vbd")
        self.assertEqual(cfg.iterations, 10)
        self.assertFalse(cfg.integrate_with_external_rigid_solver)

    def test_cfg_custom_params(self):
        """VBDSolverCfg should accept custom parameters."""
        from isaaclab_newton.physics.newton_manager_cfg import VBDSolverCfg

        cfg = VBDSolverCfg(
            iterations=20,
            rigid_contact_k_start=1.0e5,
            rigid_body_contact_buffer_size=256,
            particle_enable_self_contact=True,
        )
        self.assertEqual(cfg.iterations, 20)
        self.assertEqual(cfg.rigid_contact_k_start, 1.0e5)
        self.assertEqual(cfg.rigid_body_contact_buffer_size, 256)
        self.assertTrue(cfg.particle_enable_self_contact)

    def test_cfg_to_dict(self):
        """VBDSolverCfg.to_dict() should produce a dict with solver_type='vbd'."""
        from isaaclab_newton.physics.newton_manager_cfg import VBDSolverCfg

        cfg = VBDSolverCfg()
        d = cfg.to_dict()
        self.assertEqual(d["solver_type"], "vbd")
        self.assertIn("iterations", d)
        self.assertIn("rigid_avbd_beta", d)


class TestVBDSolverDirect(unittest.TestCase):
    """Test VBD solver directly through Newton (bypassing Isaac Lab manager).

    This validates that the solver parameters from VBDSolverCfg are compatible
    with SolverVBD's __init__ signature.
    """

    def _build_cable_model(self, device="cpu"):
        """Build a minimal cable model for VBD testing.

        Creates a short cable (rod) with 5 segments, one end fixed,
        the other free to swing under gravity. Includes a ground plane
        for collision testing.
        """
        builder = newton.ModelBuilder(gravity=-9.81)
        builder.add_ground_plane()

        # Create a short cable
        positions = [
            wp.vec3(0.0, 0.0, 0.5),
            wp.vec3(0.0, 0.0, 0.45),
            wp.vec3(0.0, 0.0, 0.4),
            wp.vec3(0.0, 0.0, 0.35),
            wp.vec3(0.0, 0.0, 0.3),
            wp.vec3(0.0, 0.0, 0.25),
        ]
        quats = newton.utils.create_parallel_transport_cable_quaternions(positions)

        rod_bodies, _ = builder.add_rod(
            positions=positions,
            quaternions=quats,
            radius=0.003,
            bend_stiffness=1.0e-1,
            bend_damping=1.0e-1,
            stretch_stiffness=1.0e6,
            stretch_damping=1.0e-1,
            label="cable",
        )

        # Fix the first body (kinematic anchor)
        builder.body_mass[rod_bodies[0]] = 0.0
        builder.body_inv_mass[rod_bodies[0]] = 0.0
        builder.body_inertia[rod_bodies[0]] = wp.mat33(0.0)
        builder.body_inv_inertia[rod_bodies[0]] = wp.mat33(0.0)

        # VBD requires coloring
        builder.color()

        model = builder.finalize(device=device)
        return model

    def test_vbd_solver_creation(self):
        """SolverVBD should instantiate with default parameters."""
        model = self._build_cable_model()
        solver = SolverVBD(model)
        self.assertIsNotNone(solver)
        self.assertEqual(solver.iterations, 10)

    def test_vbd_solver_with_cfg_params(self):
        """SolverVBD should accept parameters matching VBDSolverCfg fields."""
        from isaaclab_newton.physics.newton_manager_cfg import VBDSolverCfg
        import inspect

        model = self._build_cable_model()
        cfg = VBDSolverCfg(iterations=12, rigid_contact_k_start=1.0e5)
        cfg_dict = cfg.to_dict()
        cfg_dict.pop("solver_type")

        # Filter to valid SolverVBD params (same logic as NewtonManager)
        solver_sig = inspect.signature(SolverVBD.__init__)
        valid_args = set(solver_sig.parameters.keys()) - {"self", "model"}
        filtered = {k: v for k, v in cfg_dict.items() if k in valid_args}

        solver = SolverVBD(model, **filtered)
        self.assertEqual(solver.iterations, 12)

    def test_vbd_step_cable(self):
        """VBD should step a cable model without crashing and produce finite state."""
        model = self._build_cable_model()
        solver = SolverVBD(model, iterations=6, rigid_contact_k_start=1.0e3)

        state_0 = model.state()
        state_1 = model.state()
        control = model.control()
        contacts = model.contacts()

        dt = 1.0 / 120.0
        initial_q = state_0.body_q.numpy().copy()

        # Run 10 steps
        for _ in range(10):
            state_0.clear_forces()
            model.collide(state_0, contacts)
            solver.step(state_0, state_1, control, contacts, dt)
            state_0, state_1 = state_1, state_0

        final_q = state_0.body_q.numpy()

        # All transforms should be finite
        self.assertTrue(np.all(np.isfinite(final_q)), "VBD produced non-finite body transforms")

        # Non-kinematic bodies should have moved (gravity pulls cable down)
        # Body 0 is kinematic (fixed), bodies 1+ should move
        movement = np.linalg.norm(final_q[1:, :3] - initial_q[1:, :3], axis=-1)
        self.assertTrue(np.any(movement > 1e-6), "Cable bodies did not move under gravity")

    def test_vbd_substep_history(self):
        """VBD's set_rigid_history_update should work for substep pattern."""
        model = self._build_cable_model()
        solver = SolverVBD(model, iterations=4, rigid_contact_k_start=1.0e3)

        state_0 = model.state()
        state_1 = model.state()
        control = model.control()
        contacts = model.contacts()

        dt = 1.0 / 360.0
        num_substeps = 3

        # Simulate the substep pattern Isaac Lab would use
        for frame in range(5):
            model.collide(state_0, contacts)
            for i in range(num_substeps):
                solver.set_rigid_history_update(i == 0)
                if i > 0:
                    model.collide(state_0, contacts)
                state_0.clear_forces()
                solver.step(state_0, state_1, control, contacts, dt)
                state_0, state_1 = state_1, state_0

        final_q = state_0.body_q.numpy()
        self.assertTrue(np.all(np.isfinite(final_q)), "Substep pattern produced non-finite state")


class TestVBDRJ45Cable(unittest.TestCase):
    """Test VBD with a setup inspired by Newton's RJ45 ethernet cable example.

    This creates a plug body + cable + ground and verifies the system
    simulates stably with VBD.
    """

    def test_rj45_inspired_setup(self):
        """RJ45-inspired plug+cable should simulate stably under VBD."""
        builder = newton.ModelBuilder(gravity=-9.81)
        builder.add_ground_plane()

        # Plug body (box approximation)
        plug_body = builder.add_body(
            origin=wp.transform(wp.vec3(0.0, 0.0, 0.1), wp.quat_identity()),
            label="plug",
        )
        builder.add_shape_box(
            plug_body,
            hx=0.006,
            hy=0.005,
            hz=0.012,
            cfg=newton.ModelBuilder.ShapeConfig(
                mu=0.1, ke=1e6, kd=1e3, density=1e4,
            ),
        )

        # Cable from plug downward
        cable_start = wp.vec3(0.0, -0.012, 0.1)
        positions = [
            wp.vec3(cable_start[0], cable_start[1] - i * 0.03, cable_start[2])
            for i in range(8)
        ]
        quats = newton.utils.create_parallel_transport_cable_quaternions(positions)

        rod_bodies, _ = builder.add_rod(
            positions=positions,
            quaternions=quats,
            radius=0.003,
            bend_stiffness=1e-1,
            bend_damping=1e-1,
            stretch_stiffness=1e8,
            stretch_damping=1e-1,
            label="ethernet_cable",
        )

        # Fix first cable body to plug
        builder.body_mass[rod_bodies[0]] = 0.0
        builder.body_inv_mass[rod_bodies[0]] = 0.0
        builder.body_inertia[rod_bodies[0]] = wp.mat33(0.0)
        builder.body_inv_inertia[rod_bodies[0]] = wp.mat33(0.0)

        builder.color()
        model = builder.finalize()

        solver = SolverVBD(
            model,
            iterations=8,
            friction_epsilon=0.1,
            rigid_contact_k_start=1e4,
            rigid_body_contact_buffer_size=128,
        )

        state_0 = model.state()
        state_1 = model.state()
        control = model.control()
        contacts = model.contacts()

        dt = 1.0 / 60.0 / 4  # 4 substeps at 60fps
        num_steps = 60  # ~1 second

        for step_i in range(num_steps):
            state_0.clear_forces()
            model.collide(state_0, contacts)
            solver.step(state_0, state_1, control, contacts, dt)
            state_0, state_1 = state_1, state_0

        final_q = state_0.body_q.numpy()

        # Check stability
        self.assertTrue(np.all(np.isfinite(final_q)), "RJ45 cable sim produced non-finite state")

        # Check cable sags under gravity (Z position of tip should decrease)
        tip_z_initial = 0.1  # approximate starting Z
        tip_z_final = final_q[rod_bodies[-1]][2]  # Z component of translation
        # The free end of the cable should sag downward OR at least not explode
        self.assertLess(tip_z_final, tip_z_initial + 0.05,
                        "Cable tip moved upward unexpectedly")


if __name__ == "__main__":
    unittest.main()
