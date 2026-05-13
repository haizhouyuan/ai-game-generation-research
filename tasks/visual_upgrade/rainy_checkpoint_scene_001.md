# Task: rainy-checkpoint-scene-001

## Goal

Build the 12m x 18m rainy tactical checkpoint / container-yard / killhouse-entry micro-slice with six fixed visual evidence cameras.

## Host

Mac M2 Max 96GB.

## Runner Route

Preferred: `claudeminmax` or `claudekimi` through scoped worker after runtime skeleton exists.

## Read Scope

- `experiments/tactical_game_full_realism_final_20260513/index.html`
- `experiments/tactical_game_full_realism_final_20260513/report.md`
- `docs/production_goal_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`

## Write Scope

- `experiments/tactical_game_visual_upgrade_20260520/src/scene/rainyCheckpointLayout.js`
- `experiments/tactical_game_visual_upgrade_20260520/src/runtime/decalSystem.js`
- `experiments/tactical_game_visual_upgrade_20260520/src/runtime/weatherSystem.js`
- `experiments/tactical_game_visual_upgrade_20260520/evidence/rainy_checkpoint/**`

## Forbidden

- broad map expansion outside the micro-slice
- editing the original source snapshot
- global proxy configuration
- destructive git commands

## Verification

```bash
node --check experiments/tactical_game_visual_upgrade_20260520/src/scene/rainyCheckpointLayout.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/decalSystem.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/weatherSystem.js
```

## Expected Artifacts

- six named camera presets
- checkpoint scene layout module
- decal module
- weather/wetness module
- evidence screenshots

## Acceptance

- Six camera names exist:
  - `01_fp_rifle_wet_checkpoint`
  - `02_third_person_player_gear`
  - `03_enemy_under_checkpoint_light`
  - `04_loot_on_wet_asphalt`
  - `05_indoor_killhouse_corridor`
  - `06_final_wide_rainy_container_checkpoint`
- At least 30 clutter/decal instances.
- No screenshot dominated by flat pure-color surfaces.

## Output Summary

- changed files
- camera presets
- instance counts
- evidence paths
- risks

