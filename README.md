# AI Game Generation Research

This public repository records an AI-assisted game-generation research run: tool discovery, asset-pipeline experiments, managed-agent orchestration, browser evidence gates, and a playable Three.js tactical-game visual upgrade.

## Current Review Target

The most important artifact for an external GitHub review is:

`experiments/tactical_game_full_realism_final_20260513/`

It is the final playable packet for:

`docs/production_goal_full_realistic_3d_tactical_game_final_2026-05-13.md`

Start with:

1. `docs/chatgpt_pro_github_review_brief_2026-05-13.md`
2. `experiments/tactical_game_full_realism_final_20260513/README.md`
3. `experiments/tactical_game_full_realism_final_20260513/report.md`
4. `experiments/tactical_game_full_realism_final_20260513/assets/asset_inventory_matrix.json`
5. `docs/full_realism_lessons_and_best_practices_2026-05-13.md`

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
The next useful review should focus on how to move this browser-playable vertical slice toward a high-end tactical-game look.

## Boundary

No private child data, private screenshots, account sessions, hosted uploads, API keys, or local credential files are
intended to be published here. Large installers, raw third-party source archives, and private transcript extracts are
kept local only; see `docs/repository_publication_inventory_2026-05-13.md`.
