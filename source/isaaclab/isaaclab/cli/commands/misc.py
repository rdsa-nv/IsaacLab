# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Misc commands"""

import json

from ..utils import (
    ISAACLAB_ROOT,
    extract_isaacsim_exe,
    extract_python_exe,
    get_pip_command,
    print_info,
    print_warning,
    run_command,
    run_python_command,
)


def command_run_isaacsim(sim_args: list[str]) -> None:
    """Run Isaac Sim (-s).

    Args:
        sim_args: Additional arguments passed to the Isaac Sim executable.
    """

    isaacsim_exe = extract_isaacsim_exe()
    print_info(f"Running Isaac Sim from: {isaacsim_exe}")

    isaacsim_exe.append("--ext-folder")
    isaacsim_exe.append(str(ISAACLAB_ROOT / "source"))
    isaacsim_exe.extend(sim_args)

    run_command(isaacsim_exe, check=False)


def command_new(new_args: list[str]) -> None:
    """Create a new external project or internal task from template (-n).

    Args:
        new_args: Arguments forwarded to the template generator CLI.
    """

    print_info("Installing template dependencies...")
    reqs = ISAACLAB_ROOT / "tools" / "template" / "requirements.txt"
    run_python_command("pip", ["install", "-q", "-r", str(reqs)], is_module=True)

    print_info("Running template generator...")
    cli_script = ISAACLAB_ROOT / "tools" / "template" / "cli.py"
    run_python_command(cli_script, new_args)


def command_test(test_args: list[str]) -> None:
    """Run pytest for Isaac Lab tests (-t).

    Args:
        test_args: Additional pytest arguments.
    """
    run_python_command("-m", ["pytest", str(ISAACLAB_ROOT / "tools")] + test_args)


def command_vscode_settings() -> None:
    """Update the vscode settings from template and Isaac Sim settings"""

    print_info("Setting up vscode settings...")

    # Path to setup_vscode.py.
    setup_vscode_script = ISAACLAB_ROOT / ".vscode" / "tools" / "setup_vscode.py"

    # Check if the file exists before attempting to run it.
    if setup_vscode_script.exists():
        run_python_command(setup_vscode_script, [])
        print_info("VS Code settings generated successfully.")
    else:
        print_warning("Unable to find the script 'setup_vscode.py'. Aborting vscode settings setup.")


def command_build_docs() -> None:
    """Generate and preview the documentation with Fern."""
    print_info("Generating Fern documentation...")
    python_exe = extract_python_exe()
    docs_dir = ISAACLAB_ROOT / "docs"
    fern_dir = ISAACLAB_ROOT / "fern"

    pip_cmd = get_pip_command(python_exe)
    run_command(
        pip_cmd + ["install", "-r", "requirements.txt"],
        cwd=docs_dir,
    )

    generator = ISAACLAB_ROOT / "tools" / "docs" / "build_fern.py"
    run_command([python_exe, str(generator)])

    config = json.loads((fern_dir / "fern.config.json").read_text())
    fern_command = ["npx", "--yes", f"fern-api@{config['version']}"]
    run_command(fern_command + ["docs", "md", "generate", "--local"], cwd=fern_dir)

    print_info("Starting the Fern preview server...")
    run_command(fern_command + ["docs", "dev"], cwd=fern_dir)


def command_run_docker(args: list[str]) -> None:
    """Run the docker container helper script (docker/container.py).

    Args:
        args: Arguments forwarded to ``docker/container.py``.
    """
    script_path = ISAACLAB_ROOT / "docker" / "container.py"
    print_info(f"Running docker utility script from: {script_path}")
    run_python_command(script_path, args)
