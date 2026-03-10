# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from isaaclab.renderers import RendererCfg
from isaaclab.utils import configclass

from isaaclab_tasks.utils import PresetCfg

# Optional renderer backends — only available when the corresponding package is installed.
try:
    from isaaclab_newton.renderers import NewtonWarpRendererCfg

    _newton_default: RendererCfg | None = NewtonWarpRendererCfg()
except ImportError:
    _newton_default = None

try:
    from isaaclab_ov.renderers import OVRTXRendererCfg

    _ovrtx_default: RendererCfg | None = OVRTXRendererCfg()
except ImportError:
    _ovrtx_default = None

try:
    from isaaclab_physx.renderers import IsaacRtxRendererCfg

    _physx_default: RendererCfg | None = IsaacRtxRendererCfg()
except ImportError:
    _physx_default = None


@configclass
class MultiBackendRendererCfg(PresetCfg):
    default: RendererCfg | None = _physx_default
    newton_renderer: RendererCfg | None = _newton_default
    ovrtx_renderer: RendererCfg | None = _ovrtx_default
    isaacsim_rtx_renderer = _physx_default
