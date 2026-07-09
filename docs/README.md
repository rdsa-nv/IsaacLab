<!--
Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause
-->

# Building documentation

Isaac Lab uses [Fern](https://buildwithfern.com/docs) to preview and publish its documentation. The existing reStructuredText pages remain the source of truth and are converted to Fern-compatible MDX during each build. Fern's library reference generator produces the Python source API directly from `source/`.

## Local preview

Install Node.js 20 or newer and Docker, then run:

```bash
./isaaclab.sh -d
```

The command installs the Python converter dependency, generates the guide and source API pages, and starts Fern's local development server.

To run each step directly:

```bash
uv venv
uv pip install -r docs/requirements.txt
.venv/bin/python tools/docs/build_fern.py
cd fern
npx --yes fern-api@5.67.1 docs md generate --local
npx --yes fern-api@5.67.1 docs dev
```

Generated content lives under `fern/generated/` and is intentionally ignored by Git.

## Preview and publish

The Docs workflow validates every branch and pull request. When `FERN_TOKEN` is configured, pull requests receive shareable Fern previews. Scheduled and manually dispatched runs from the upstream repository publish `isaaclab.docs.buildwithfern.com`.
