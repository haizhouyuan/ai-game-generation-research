# Task: threejs-loader-migration-001

## Goal

Prepare the tactical visual-upgrade experiment to use official Three.js `GLTFLoader` with KTX2/Meshopt readiness and a fail-closed asset registry.

## Host

Mac M2 Max 96GB.

## Runner Route

Preferred: `claudekimi` through `runner-worker` after dry-run. Use MiniMax only for follow-up mechanical edits.

## Read Scope

- `experiments/tactical_game_full_realism_final_20260513/index.html`
- `experiments/tactical_game_full_realism_final_20260513/assets/asset_registry.json`
- `experiments/tactical_game_full_realism_final_20260513/README.md`
- `docs/full_realism_lessons_and_best_practices_2026-05-13.md`

## Write Scope

- `experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js`
- `experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js`
- `experiments/tactical_game_visual_upgrade_20260520/reports/threejs_loader_migration_001.md`

## Forbidden

- `experiments/tactical_game_full_realism_final_20260513/source/14.html`
- `.secrets`
- `.kimi`
- `.claude-minimax`
- `.claude-kimi`
- global proxy configuration
- destructive git commands

## Verification

```bash
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js
```

## Expected Artifacts

- Runtime loader module.
- Runtime registry module.
- Short migration report.

## Acceptance

- Modules parse with `node --check`.
- Loader API exposes asset status, texture-map counts, missing texture failures, and fallback state.
- Evidence mode can be configured to fail on fallback.

## Output Summary

- changed files
- commands run
- evidence paths
- risks
