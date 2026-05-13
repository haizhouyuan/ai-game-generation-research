# Local Engine Host Probe - 2026-05-13

Goal source: `docs/production_goal_managed_agents_game_chain_v2_2026-05-12.md`

Purpose: record the initial read-only local host probe for Unity and Blender readiness, then append governed install/probe updates without losing the original baseline.

## Commands

Run from `/Users/yuanshaochen/Projects/ai-game-generation-research`:

```bash
find /Applications -maxdepth 3 \( -iname '*Unity*' -o -iname '*Blender*' \) -print 2>/dev/null
command -v blender || true
command -v unity || true
command -v unity-hub || true
command -v Unity || true
mdfind 'kMDItemFSName == "Blender.app" || kMDItemFSName == "Unity Hub.app" || kMDItemFSName == "Unity.app"' 2>/dev/null
find /Users/yuanshaochen -maxdepth 4 \( -iname 'Blender.app' -o -iname 'Unity Hub.app' -o -iname 'Unity.app' -o -iname 'Unity' \) -print 2>/dev/null
```

## Initial Result

No Unity Hub, Unity Editor, or Blender app/binary was found by the read-only probes above.

## 2026-05-13 Blender Update

Blender was later installed under download governance:

- Download record: `docs/download_records/blender_5_1_1_2026-05-13.md`
- Host proof: `docs/blender_host_proof_2026-05-13.md`
- Blender path: `/Applications/Blender.app/Contents/MacOS/Blender`
- Version: `5.1.1`

## 2026-05-13 Unity Hub Update

Unity Hub was later installed under download governance:

- Download record: `docs/download_records/unity_hub_3_18_0_2026-05-13.md`
- Host probe: `docs/unity_hub_host_probe_2026-05-13.md`
- Unity Hub path: `/Applications/Unity Hub.app`
- Version: `3.18.0`
- Headless help evidence: `experiments/unity_host_probe_20260513/outputs/unity_hub_headless_help.txt`
- Installed editor list: empty `[]` in `experiments/unity_host_probe_20260513/outputs/unity_hub_editors_installed.json`
- No-proxy lsof evidence: `experiments/unity_host_probe_20260513/logs/unity_hub_range_lsof.txt`

Unity Hub now exists, but Unity Editor and Unity MCP remain absent/unproven.

## Decision

- `unity-mcp-001` remains blocked until a Unity Editor 6.x host and local editor-control/MCP path are proven.
- `blender-authoring` now has a local Blender Python proof, but Blender MCP remains unproven.
- Do not promote Unity Editor/MCP or Blender MCP capabilities to available based on planning docs alone.
- Any future install must follow no-proxy/download governance. Do not start large downloads implicitly.

## Next Evidence Gate

When an engine host is available, run a disposable proof before touching production assets:

- Unity: version/account/package status, local-only MCP/editor control surface, create/read/modify scene, create or modify material/script/prefab, read console, run play mode or tests, capture screenshot/log.
- Blender: version, background Python execution, import/create mesh, material assignment, scale/orientation report, GLB export, screenshot or deterministic render, Three.js GLB parse/readback.
