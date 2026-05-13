# Realistic 3D Asset Goal Status - 2026-05-13

Goal file: `docs/production_goal_realistic_3d_assets_for_tactical_game_2026-05-13.md`

## Current State

The active production goal is now the realistic 3D asset upgrade for `/Users/yuanshaochen/Documents/14.html`, not the Rover Workshop game.

## Completed In This Pass

- Located the source game and related asset references in `/Users/yuanshaochen/Documents`.
- Confirmed `/Users/yuanshaochen/Documents/14.html` is the primary tactical compound survival game.
- Confirmed `/Users/yuanshaochen/Documents/枪械模型包/` contains prototype OBJ/MTL weapon assets, not final realism-grade assets.
- Confirmed `/Users/yuanshaochen/Documents/groza_high_detail_3d_model_viewer.html` is a useful local GROZA-style visual reference.
- Created the production goal file:
  - `docs/production_goal_realistic_3d_assets_for_tactical_game_2026-05-13.md`
- Created execution and inventory docs:
  - `docs/realistic_asset_upgrade_execution_plan_2026-05-13.md`
  - `docs/tactical_game_asset_inventory_2026-05-13.md`
- Added `asset-004` to `config/lanes.yaml` for the tactical compound realistic rifle hero asset.
- Started the rifle/GROZA hero-asset experiment:
  - `experiments/tactical_rifle_realism_20260513/`
  - existing `rifle.obj` baseline imported into Blender;
  - exported `rifle_obj_baseline.glb`;
  - captured Blender preview;
  - ran Three.js GLB parse inventory;
  - verified experiment artifact hashes.
- Produced a stronger local procedural GROZA candidate:
  - `experiments/tactical_rifle_realism_20260513/groza_procedural/groza_procedural_candidate.glb`
  - 87 meshes, 21,540 triangles, 7 material names, muzzle/grip/sight anchors;
  - Blender preview and Three.js parse evidence recorded.
- Ran the cached HomePC TRELLIS route without new large model downloads:
  - `experiments/tactical_rifle_trellis_20260513/`
  - three seeds: 42, 101, 202;
  - raw and Blender-cleaned GLBs, renders, parse reports, logs, and hashes recorded;
  - seed 202 was the best TRELLIS shape but remains mesh-only and untextured.
- Created a playable derivative with the selected GROZA GLB integrated into the rifle path:
  - `experiments/tactical_game_realism_upgrade_20260513/index.html`
  - selected asset: `assets/models/groza_procedural_candidate.glb`
  - source `/Users/yuanshaochen/Documents/14.html` left unchanged.
- Verified the integrated derivative:
  - static verifier passed;
  - JS syntax check passed;
  - local HTTP served HTML and GLB with `HTTP 200`;
  - Chrome CDP runtime probes passed for first-person and third-person rifle contexts.
- Extended the derivative beyond the hero rifle:
  - generated local Blender GLB candidates for pistol, shotgun, and DMR;
  - integrated pistol, shotgun, rifle, and DMR through a shared `weaponAssets` GLB loader;
  - added player/NPC tactical gear, loot prop, and container-detail M5 passes;
  - fixed the inherited `updateFlashes is not defined` runtime crash in the derivative;
  - made CDP evidence fail on runtime exceptions/network errors instead of only checking asset status;
  - captured M5 all-weapon evidence and before/after gameplay screenshots.
- Fixed local `managed-artifact-verifier` MCP stdio compatibility:
  - supports JSONL stdio used by Gemini/Claude MCP clients;
  - preserves Content-Length compatibility for local tests;
  - ignores `notifications/cancelled`.
- Verified local MCP connectivity:
  - Gemini MCP: `managed-artifact-verifier` connected.
  - Claude MiniMax MCP: `managed-artifact-verifier` connected.
  - Claude Kimi MCP: `managed-artifact-verifier` connected.
- Verified real MiniMax-backed Claude MCP tool use:
  - `managed-artifact-verifier` verified an existing artifact manifest and returned `exit_code: 0`.
- Updated runner snapshots:
  - `docs/runner_snapshots/local_coding_runners_2026-05-13/bin/managed-artifact-mcp`
  - `docs/runner_snapshots/local_coding_runners_2026-05-13/tests/test_managed_artifact_mcp.py`
  - `docs/runner_snapshots/local_coding_runners_2026-05-13/runner_mcp_skill_inventory_2026-05-13.md`
  - `docs/runner_snapshots/local_coding_runners_2026-05-13/managed_artifact_mcp_tool_call_probe_2026-05-13.txt`

## Subagent Findings

### Asset Inventory

The most valuable first target is a GROZA / TAC-AR style rifle GLB for the `rifle` slot.

Reason:

- It appears in first-person, third-person, NPC, and ground-loot contexts.
- It exercises the full integration contract: mount, scale, material, muzzle origin, shadow, ADS framing, and fallback.
- It can reuse `groza_high_detail_3d_model_viewer.html` as a local visual direction reference.

### 3D Generation Route

Recommended first route:

- high-quality reference image;
- existing TRELLIS image-to-mesh path where available without new large downloads;
- Blender 5.1.1 cleanup/material/UV/proxy/export on M1;
- Three.js GLB parser/viewer validation;
- browser/in-game evidence.

Hunyuan3D-2.1 remains a promising second route for PBR, but likely requires large model downloads and VRAM; it must go through the no-proxy and approval policy before use.

Rodin/Hyper3D is useful as a cloud/API comparison path but is less reproducible and may involve paid/API usage.

### Yoga/Maint Runner Config

YogaS2 was inspected as a reference. The reusable pattern is provider isolation:

- separate `CLAUDE_CONFIG_DIR` per provider;
- provider-specific base URL;
- provider key mapped to `ANTHROPIC_API_KEY`;
- no credential values in repo evidence.

YogaS2 MCP configs should not be copied wholesale because they include machine-local `/vol1/...` paths and localhost services that do not exist on M1.

## Current Completion Read

The controlled derivative now satisfies the practical M1-M6 delivery target for a first production pass:

- M1/M2: runner/tooling and source asset inventory are documented.
- M3/M4: the GROZA hero rifle has multiple candidates, Blender cleanup, reports, hashes, GLB parse evidence, and first/third-person browser proof.
- M5: remaining weapon slots now use generated GLBs; characters/gear, loot, containers, building facades, ladders, trees, and rocks have in-place realism upgrades; imported scan-grade character/environment GLBs are explicitly deferred.
- M6: the derivative is playable locally, has fresh first/third/M5 CDP evidence with `blockingEvents: []`, before/after screenshots, manifests, and limitations.

## Remaining Limitations

- The original source file `/Users/yuanshaochen/Documents/14.html` is intentionally unchanged; the deliverable is the derivative at `experiments/tactical_game_realism_upgrade_20260513/index.html`.
- Weapon assets are local Blender hard-surface procedural GLBs with PBR-style material factors, not scanned or baked-texture production assets.
- Character/gear/loot/environment upgrades are still local Three.js geometry, not imported scan-grade GLBs.
- The next art-quality jump should run per-class Hunyuan3D/TRELLIS/PBR generation plus Blender cleanup and replace those in-place procedural classes with generated assets.
