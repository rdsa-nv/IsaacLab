#!/usr/bin/env python3
"""Print a compact "What you have" Isaac Lab install summary."""

from __future__ import annotations

import importlib
import importlib.metadata as metadata
import os
import subprocess
import sys


def dist_version(*names: str) -> str | None:
    for name in names:
        try:
            return metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
    return None


def module_version(module_name: str) -> str | None:
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None
    value = getattr(module, "__version__", None)
    return str(value) if value else "available"


def version(*, dists: tuple[str, ...] = (), modules: tuple[str, ...] = ()) -> str:
    value = dist_version(*dists)
    if value:
        return value
    for module_name in modules:
        value = module_version(module_name)
        if value:
            return value
    return "not installed"


def kit_version() -> str:
    value = dist_version("omni-kit-app", "omni.kit.app", "kit-sdk", "kit")
    if value:
        return value
    try:
        omni_kit_app = importlib.import_module("omni.kit.app")
        app = omni_kit_app.get_app()
    except Exception:
        return "not installed"
    for method_name in ("get_build_version", "get_version"):
        method = getattr(app, method_name, None)
        if method is None:
            continue
        try:
            result = method()
        except Exception:
            continue
        if result:
            return str(result)
    return "available"


def gpu_summary() -> str:
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).strip()
    except Exception:
        return "not detected"
    return output.splitlines()[0] if output else "not detected"


def main() -> None:
    try:
        import torch
    except Exception:
        torch_version = "not installed"
        cuda_available = "n/a"
    else:
        torch_version = getattr(torch, "__version__", "available")
        cuda_available = str(torch.cuda.is_available())

    env_path = os.environ.get("VIRTUAL_ENV") or sys.prefix
    lab_version = version(dists=("isaaclab",), modules=("isaaclab",))
    lab_newton_version = version(dists=("isaaclab-newton",), modules=("isaaclab_newton",))
    newton_version = version(dists=("newton", "newton-physics"), modules=("newton",))
    warp_version = version(dists=("warp-lang",), modules=("warp",))
    mujoco_warp_version = version(dists=("mujoco-warp",), modules=("mujoco_warp",))
    rsl_rl_version = version(dists=("rsl-rl-lib", "rsl_rl"), modules=("rsl_rl",))
    isaac_sim_version = version(dists=("isaacsim", "isaac-sim"), modules=("isaacsim",))
    kit = kit_version()

    rows = [
        ("Env", f"{env_path} (Python {sys.version.split()[0]})"),
        ("Isaac Lab", f"isaaclab {lab_version}; isaaclab-newton {lab_newton_version}"),
        ("Physics", f"Newton {newton_version}; Warp {warp_version}; MuJoCo-Warp {mujoco_warp_version}"),
        ("DL / RL", f"torch {torch_version} (CUDA {cuda_available}); rsl-rl-lib {rsl_rl_version}"),
        ("GPU", gpu_summary()),
        ("Isaac Sim", isaac_sim_version),
        ("Kit", kit),
    ]

    print("What you have")
    print()
    print("| Item | Value |")
    print("| --- | --- |")
    for label, value in rows:
        print(f"| {label} | {value} |")


if __name__ == "__main__":
    main()
