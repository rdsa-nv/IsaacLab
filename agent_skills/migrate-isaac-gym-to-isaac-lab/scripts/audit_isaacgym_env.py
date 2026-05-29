#!/usr/bin/env python3
# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Audit Isaac Gym style environment code before porting to Isaac Lab."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "logs",
    "outputs",
    "runs",
    "wandb",
}

TEXT_SUFFIXES = {".py", ".yaml", ".yml", ".toml", ".json", ".cfg", ".txt", ".md", ".rst"}

MANAGER_NEWTON_HINTS = {
    "Map to DirectRLEnvCfg.decimation": "Map to `ManagerBasedRLEnvCfg.decimation`",
    "Replace with DirectRLEnv._setup_scene": "Map scene creation to `InteractiveSceneCfg` assets and sensors",
    "Replace with scene.clone_environments": "Replace manual env loops with `InteractiveSceneCfg` cloning",
    "Split into _pre_physics_step and _apply_action": "Map action application to `ActionsCfg` or a custom `ActionTerm`",
    "Map to _get_observations returning {'policy': obs}": (
        "Map observations to ordered `ObservationTermCfg`s in `ObservationsCfg.PolicyCfg`"
    ),
    "Map to _get_rewards": "Map rewards to `RewardTermCfg`s; use `ManagerTermBase` for stateful source math",
    "Map to _reset_idx": "Map resets and reset randomization to reset-mode `EventTermCfg`s",
    "Map to _get_dones and episode_length_buf": "Map failures to `TerminationTermCfg`s and timeouts to `time_out=True`",
    "Port to events or _reset_idx first": "Port randomization to reset/interval `EventTermCfg`s first",
    "Use write_*_to_sim_index methods": "Use built-in reset events, or write_* methods inside custom `EventTermCfg`s",
    "Usually base class flow in Isaac Lab": "Usually handled by manager execution order, events, or custom MDP terms",
}


PATTERNS: dict[str, list[tuple[str, str, str]]] = {
    "source_family": [
        (
            "Isaac Gym import",
            r"\b(from|import)\s+isaacgym\b|\bgymapi\b|\bgymtorch\b|\bgymutil\b",
            "Isaac Gym API usage",
        ),
        ("IsaacGymEnvs VecTask", r"\bVecTask\b|isaacgymenvs", "Likely IsaacGymEnvs task"),
        ("OmniIsaacGymEnvs RLTask", r"\bRLTask\b|omniisaacgymenvs", "Likely OmniIsaacGymEnvs task"),
        ("Omni views", r"\bArticulationView\b|\bRigidPrimView\b", "OmniIsaacGymEnvs view classes"),
    ],
    "config": [
        ("numEnvs", r"\bnumEnvs\b", "Map to InteractiveSceneCfg(num_envs=...)"),
        ("envSpacing", r"\benvSpacing\b", "Map to InteractiveSceneCfg(env_spacing=...)"),
        ("controlFrequencyInv", r"\bcontrolFrequencyInv\b", "Map to DirectRLEnvCfg.decimation"),
        ("clipObservations", r"\bclipObservations\b", "Move to RL config clip_observations"),
        ("clipActions", r"\bclipActions\b", "Move to RL config clip_actions"),
        ("substeps", r"\bsubsteps\b", "Fold into sim dt and decimation"),
        (
            "max episode length",
            r"\b(maxEpisodeLength|max_episode_length|episodeLength)\b",
            "Convert step count to episode_length_s",
        ),
    ],
    "scene_assets": [
        ("create_sim", r"\bcreate_sim\s*\(", "Replace with DirectRLEnv._setup_scene"),
        ("create env loop", r"\bcreate_env\s*\(|\b_create_envs\s*\(", "Replace with scene.clone_environments"),
        ("create actor", r"\bcreate_actor\s*\(", "Replace with Articulation/RigidObject configs"),
        ("load asset", r"\bload_asset\s*\(", "Replace with UsdFileCfg/UrdfFileCfg asset configs"),
        (
            "ground plane",
            r"\badd_ground\b|\bcreate_ground_plane\b|_create_ground_plane",
            "Use spawn_ground_plane or TerrainImporterCfg",
        ),
        (
            "actor properties",
            r"\bset_actor_rigid_body_properties\b|\bset_asset_rigid_shape_properties\b",
            "Move to per-asset rigid/articulation properties",
        ),
    ],
    "asset_conversion": [
        (
            "URDF/MJCF asset",
            r"\burdfAsset\b|\.urdf\b|\.mjcf\b|asset_file|asset_root",
            "Validate URDF/MJCF conversion with the active Isaac Sim runtime",
        ),
        (
            "fixed joint collapse",
            r"\bcollapseFixedJoints\b|\bcollapse_fixed_joints\b|\bmerge_fixed_joints\b",
            "Verify fixed-joint merge support and resulting body names",
        ),
        (
            "cylinder capsule replacement",
            r"\breplace_cylinder_with_capsule\b|\breplace_cylinders_with_capsules\b",
            "Check whether the current URDF importer supports capsule replacement",
        ),
        (
            "visual attachment flip",
            r"\bflip_visual_attachments\b|\bflipVisualAttachments\b",
            "Check visual/collision orientation after conversion",
        ),
        (
            "fixed base link",
            r"\bfixBaseLink\b|\bfix_base_link\b|\bfix_base\b",
            "Map fixed-base behavior and verify root articulation setup",
        ),
        (
            "default drive mode",
            r"\bdefaultDofDriveMode\b|\bdefault_dof_drive_mode\b|\bdriveMode\b",
            "Map drive mode to actuator and converter joint-drive configs",
        ),
        (
            "force sensors",
            r"\bcreate_asset_force_sensor\b|\bacquire_force_sensor_tensor\b|\benable_actor_dof_force_sensors\b|\bacquire_dof_force_tensor\b",
            "Map force/wrench readings to actuator or sensor data and verify 3D vs 6D semantics",
        ),
        (
            "contact forces",
            r"\bacquire_net_contact_force_tensor\b|\bcontact_forces\b|\bcontact_collection\b",
            "Map contacts to ContactSensorCfg and verify body regex matches",
        ),
        (
            "body name lookup",
            r"\bget_asset_rigid_body_names\b|\bfind_actor_rigid_body_handle\b|\bbody_names\b",
            "Resolve contact/termination bodies by names after conversion",
        ),
    ],
    "state_tensors": [
        ("acquire tensor", r"\bacquire_[a-z_]*tensor\s*\(", "Use asset.data buffers"),
        ("refresh tensor", r"\brefresh_[a-z_]*tensor\s*\(", "Usually unnecessary with asset.data"),
        ("gymtorch wrap", r"\bgymtorch\.(wrap_tensor|unwrap_tensor)\b", "Use native tensor buffers"),
        ("set indexed tensor", r"\bset_[a-z_]*tensor_indexed\s*\(", "Use write_*_to_sim_index methods"),
        ("dof terminology", r"\bdof(_|s|\b)|DOF", "Map DOF concepts to joint names/ids"),
    ],
    "task_logic": [
        ("pre physics", r"\bpre_physics_step\s*\(", "Split into _pre_physics_step and _apply_action"),
        ("post physics", r"\bpost_physics_step\s*\(", "Usually base class flow in Isaac Lab"),
        (
            "compute observations",
            r"\bcompute_observations\s*\(|\bget_observations\s*\(",
            "Map to _get_observations returning {'policy': obs}",
        ),
        ("compute rewards", r"\bcompute_reward\s*\(|\bcalculate_metrics\s*\(", "Map to _get_rewards"),
        ("reset idx", r"\breset_idx\s*\(", "Map to _reset_idx"),
        ("done logic", r"\bis_done\s*\(|\breset_buf\b|\bprogress_buf\b", "Map to _get_dones and episode_length_buf"),
        ("post reset", r"\bpost_reset\s*\(", "Move to __init__ or _reset_idx"),
    ],
    "behavior_risks": [
        (
            "quaternion slicing",
            r"\bquat|orientation|rotation",
            "Check quaternion convention; Isaac Lab develop expects XYZW",
        ),
        (
            "manual indices",
            r"\b(dof|joint|body)_(idx|indices|ids)\b|\bget_dof_index\b",
            "Resolve by names in Isaac Lab",
        ),
        ("randomization", r"\brandomi[sz]e|domain_randomization|dr_random", "Port to events or _reset_idx first"),
        ("camera", r"\bcamera|Camera|enableCameraSensors|enable_cameras", "Use camera configs and --enable_cameras"),
    ],
}


@dataclass
class Hit:
    file: str
    line: int
    category: str
    name: str
    hint: str
    text: str


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            files.append(path)
    return sorted(files)


def scan(root: Path) -> list[Hit]:
    compiled = {
        category: [(name, re.compile(pattern), hint) for name, pattern, hint in items]
        for category, items in PATTERNS.items()
    }
    hits: list[Hit] = []
    for file_path in iter_text_files(root):
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(file_path.relative_to(root))
        for line_no, line in enumerate(text.splitlines(), start=1):
            for category, items in compiled.items():
                for name, pattern, hint in items:
                    if pattern.search(line):
                        hits.append(
                            Hit(
                                file=rel,
                                line=line_no,
                                category=category,
                                name=name,
                                hint=hint,
                                text=line.strip()[:180],
                            )
                        )
    return hits


def classify(hits: list[Hit]) -> str:
    names = Counter(hit.name for hit in hits)
    if names["OmniIsaacGymEnvs RLTask"] or names["Omni views"]:
        return "OmniIsaacGymEnvs"
    if names["IsaacGymEnvs VecTask"]:
        return "IsaacGymEnvs"
    if names["Isaac Gym import"]:
        return "Raw Isaac Gym Preview"
    return "Unknown or already partially migrated"


def suggested_workflow(profile: str, hits: list[Hit], target_workflow: str = "auto") -> str:
    if target_workflow == "direct":
        return "DirectRLEnv"
    if target_workflow == "manager":
        return "ManagerBasedRLEnv"
    if target_workflow == "manager-newton":
        return "ManagerBasedRLEnv with Newton/MJWarp"

    names = Counter(hit.name for hit in hits)
    if (
        names["compute rewards"]
        or names["compute observations"]
        or names["pre physics"]
        or profile != "Unknown or already partially migrated"
    ):
        return "DirectRLEnv"
    return "Inspect manually; DirectRLEnv is still the default for close Isaac Gym ports."


def render_markdown(root: Path, repo: Path | None, hits: list[Hit], max_hits: int, target_workflow: str) -> str:
    profile = classify(hits)
    workflow = suggested_workflow(profile, hits, target_workflow)
    by_category = Counter(hit.category for hit in hits)
    by_file = Counter(hit.file for hit in hits)
    by_hint: dict[str, set[str]] = defaultdict(set)
    for hit in hits:
        by_hint[hit.hint].add(hit.name)

    lines = [
        "# Isaac Gym Migration Audit",
        "",
        f"- Source root: `{root}`",
        f"- Isaac Lab checkout: `{repo}`" if repo else "- Isaac Lab checkout: not provided",
        f"- Source profile: **{profile}**",
        f"- Suggested first target: **{workflow}**",
        f"- Total hits: **{len(hits)}**",
        "",
        "## Category Counts",
        "",
    ]
    if by_category:
        for category, count in sorted(by_category.items()):
            lines.append(f"- `{category}`: {count}")
    else:
        lines.append("- No Isaac Gym migration patterns found.")

    lines.extend(["", "## Highest Signal Files", ""])
    for file_name, count in by_file.most_common(15):
        lines.append(f"- `{file_name}`: {count} hits")

    lines.extend(["", "## Suggested Migration Tasks", ""])
    if by_hint:
        for source_hint in sorted(by_hint):
            hint = source_hint
            if target_workflow == "manager-newton":
                hint = MANAGER_NEWTON_HINTS.get(hint, hint)
            names = ", ".join(sorted(by_hint[source_hint]))
            lines.append(f"- {hint} (`{names}`)")
    else:
        lines.append("- Inspect source manually; this audit did not find known patterns.")

    lines.extend(["", "## Detailed Hits", ""])
    for hit in hits[:max_hits]:
        lines.append(f"- `{hit.file}:{hit.line}` [{hit.category}/{hit.name}] {hit.text}")
    if len(hits) > max_hits:
        lines.append(f"- ... truncated {len(hits) - max_hits} additional hits; rerun with `--max-hits {len(hits)}`.")

    if target_workflow == "manager-newton":
        lines.extend(
            [
                "",
                "## Next Steps",
                "",
                "1. Port config fields into a `ManagerBasedRLEnvCfg` configclass.",
                "2. Build assets and scene setup with config-defined `Articulation`/`RigidObject` objects.",
                "3. Replace tensor acquire/refresh logic with `asset.data.*.torch` buffers inside MDP terms.",
                "4. Port actions, observations, rewards, dones, and resets into manager config sections.",
                "5. Add or default to a Newton/MJWarp physics preset and verify assets under that backend.",
                "6. Register the task with `entry_point=\"isaaclab.envs:ManagerBasedRLEnv\"` and run a tiny smoke.",
                "",
                "## Manager-Based Newton Notes",
                "",
                "- Split source logic into `scene`, `actions`, `observations`, `events`, `rewards`, and"
                " `terminations` config sections.",
                "- Add a `newton_mjwarp` physics preset with `NewtonCfg(solver_cfg=MJWarpSolverCfg(...))` or"
                " make Newton the default if the target is Newton-only.",
                "- Preserve observation order with ordered `ObsTerm`s and `concatenate_terms=True`.",
                "- Use `ManagerTermBase` for source reward or observation logic that stores cross-step state.",
                "- Run a tiny Gymnasium reset/step smoke with `scene.num_envs=4` before launching training with"
                " `presets=newton_mjwarp`.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Next Steps",
                "",
                "1. Port config fields into an Isaac Lab configclass.",
                "2. Build assets and scene setup with config-defined `Articulation`/`RigidObject` objects.",
                "3. Replace tensor acquire/refresh logic with `asset.data.*.torch` buffers.",
                "4. Port actions, observations, rewards, dones, and resets into DirectRLEnv methods.",
                "5. If URDF/MJCF assets are involved, run an asset conversion/spawn smoke and print joint/body names.",
                "6. Register the task and run a tiny `--num_envs` smoke test.",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root", type=Path, help="Isaac Gym, IsaacGymEnvs, or OmniIsaacGymEnvs environment root to scan."
    )
    parser.add_argument("--repo", type=Path, default=None, help="Optional Isaac Lab checkout path for report context.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    parser.add_argument(
        "--target-workflow",
        choices=("auto", "direct", "manager", "manager-newton"),
        default="auto",
        help="Requested target workflow hint to include in the report.",
    )
    parser.add_argument(
        "--max-hits", type=int, default=200, help="Maximum detailed hits to include in Markdown output."
    )
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.exists():
        parser.error(f"root does not exist: {root}")
    if not root.is_dir():
        parser.error(f"root must be a directory: {root}")

    repo = args.repo.expanduser().resolve() if args.repo else None
    hits = scan(root)

    if args.json:
        payload = {
            "root": str(root),
            "repo": str(repo) if repo else None,
            "profile": classify(hits),
            "suggested_workflow": suggested_workflow(classify(hits), hits, args.target_workflow),
            "target_workflow": args.target_workflow,
            "category_counts": dict(Counter(hit.category for hit in hits)),
            "file_counts": dict(Counter(hit.file for hit in hits)),
            "hits": [asdict(hit) for hit in hits],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_markdown(root, repo, hits, args.max_hits, args.target_workflow))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
