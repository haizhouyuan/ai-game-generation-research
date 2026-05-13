# AI Game Generation Research

This public repository records an AI-assisted game-generation research run: tool discovery, asset-pipeline experiments, managed-agent orchestration, browser evidence gates, and a playable Three.js tactical-game visual upgrade.

## Current Review Target

The current external review should cover two layers.

Layer 1 is the preserved playable browser baseline:

`experiments/tactical_game_full_realism_final_20260513/`

`docs/production_goal_full_realistic_3d_tactical_game_final_2026-05-13.md`

Layer 2 is the active full local AI 3D asset-factory rebuild:

`docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`

Start with:

1. `docs/chatgpt_pro_github_review_brief_2026-05-13.md`
2. `docs/chatgpt_pro_full_asset_factory_followup_2026-05-13.md`
3. `tasks/pubg_like_full_rebuild/README.md`
4. `experiments/pubg_like_asset_factory_20260513/reports/hunyuan3d_env_report.md`
5. `docs/coding_runner_mcp_skill_control_2026-05-13.md`
6. `experiments/tactical_game_full_realism_final_20260513/README.md`
7. `experiments/tactical_game_full_realism_final_20260513/report.md`

## What This Repo Contains

- A preserved source snapshot at `experiments/tactical_game_full_realism_final_20260513/source/14.html`.
- A playable upgraded HTML game at `experiments/tactical_game_full_realism_final_20260513/index.html`.
- Runtime GLB assets, preview images, before/after screenshots, CDP evidence reports, asset registries, and hash manifests for the final tactical-game packet.
- Managed-agent controller experiments under `src/managed_codex/`, `config/lanes.yaml`, and `WORKFLOW.md`.
- Earlier prototype and capability experiments under `experiments/` and dated research notes under `docs/`.

## Known Visual Limitation

The final tactical packet upgrades all major visible classes, but it is not yet a commercial/SOTA art pass.
The current material grade is `material_factors_only`: the GLBs contain mesh assemblies, UV attributes,
material names, and PBR-style material factors, but not baked albedo/normal/roughness/metallic texture-map sets.
The active goal is stricter than a visual polish pass: build a local asset factory that can produce realistic reference images,
image-to-3D/PBR candidates, Blender-cleaned asset packets, and Three.js evidence for all major visible tactical-game assets.

Current fail-closed gates intentionally show that the full rebuild is not complete yet:

```bash
python3 tools/validate_asset_packets.py --production-goal
python3 tools/validate_asset_registry_v3.py --production-goal experiments/pubg_like_asset_factory_20260513/asset_registry_v3_probe.json
python3 tools/validate_texture_quality.py
```

These fail because most production asset packets are still scaffolds and the current textured crate is a probe, not final art.

## Boundary

No private child data, private screenshots, account sessions, hosted uploads, API keys, or local credential files are
intended to be published here. Large installers, raw third-party source archives, and private transcript extracts are
kept local only; see `docs/repository_publication_inventory_2026-05-13.md`.
