<!--
Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause
-->

# Fern documentation

Isaac Lab publishes its existing reStructuredText guides with [Fern](https://buildwithfern.com/docs). The generated MDX and copied assets under `fern/generated/` are build outputs and are not committed.

## Preview locally

Install Node.js 20 or newer and Docker. Then, from the repository root:

```bash
uv venv
uv pip install -r docs/requirements.txt
.venv/bin/python tools/docs/build_fern.py
cd fern
npx --yes fern-api@5.67.1 docs md generate --local
npx --yes fern-api@5.67.1 docs dev
```

Alternatively, use `./isaaclab.sh -d` to generate the content and start the preview server.

## Publish

Set the `FERN_TOKEN` GitHub Actions secret after connecting this repository to the `isaac-lab` organization in the Fern Dashboard. Pull requests receive preview builds and scheduled or manually dispatched workflow runs publish the production site.
