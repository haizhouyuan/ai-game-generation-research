# Task: asset-registry-v2-001

## Goal

Define the production asset-packet and asset-registry v2 contract for the tactical visual upgrade, then add a validator and tests. The contract must honestly represent the current final-packet assets, including `material_map_count: 0`, while making the target PBR/animation/anchor gates explicit for the next workers.

## Host

Mac M2 Max 96GB.

## Runner Route

Preferred: `claudekimi` through scoped worker because this touches schema design, validator behavior, and tests. Use MiniMax only for later mechanical fixture cleanup.

## Read Scope

- `experiments/tactical_game_full_realism_final_20260513/assets/asset_registry.json`
- `experiments/tactical_game_full_realism_final_20260513/assets/asset_inventory_matrix.json`
- `docs/production_goal_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`
- `docs/implementation_plan_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`
- `tools/verify_artifact_hashes.py`
- `tests/test_verify_artifact_hashes.py`

## Write Scope

- `experiments/tactical_game_visual_upgrade_20260520/schemas/asset_packet.schema.json`
- `experiments/tactical_game_visual_upgrade_20260520/assets/asset_registry_v2.json`
- `tools/validate_asset_registry_v2.py`
- `tests/test_validate_asset_registry_v2.py`
- `experiments/tactical_game_visual_upgrade_20260520/reports/asset_registry_v2_001.md`

## Must Not Touch

- `experiments/tactical_game_full_realism_final_20260513/source/14.html`
- `experiments/tactical_game_full_realism_final_20260513/index.html`
- private credential directories
- global proxy settings
- files outside the write scope

## Required Contract Fields

Each asset entry must include:

- `asset_id`
- `asset_class`
- `role`
- `status`
- `paths`
- `provenance`
- `geometry`
- `materials`
- `anchors`
- `animations`
- `lod`
- `quality_gates`
- `evidence`
- `hashes`
- `blockers`

The schema must support current baseline assets that have no texture maps, while allowing target hero assets to require:

- `material_map_count >= 4`
- weapon anchors: `Muzzle`, `Grip_R`, `Grip_L`, `Optic`, `PickupRoot`
- at least one gameplay-context screenshot
- no runtime fallback for hero evidence

## Verification

```bash
python3 -m pytest tests/test_validate_asset_registry_v2.py
python3 tools/validate_asset_registry_v2.py experiments/tactical_game_visual_upgrade_20260520/assets/asset_registry_v2.json
```

## Acceptance

- Validator exits `0` on the new registry.
- Tests cover valid registry, missing required field, missing hero PBR maps, missing weapon anchors, missing evidence path, and baseline accepted-with-blocker behavior.
- The registry contains at least these entries:
  - `baseline_groza_procedural_candidate`
  - `baseline_character_player_final`
  - `target_hero_rifle_v2`
  - `target_player_tactical_v2`
  - `target_wet_asphalt_material`
- Current baseline entries are marked as `baseline_only` or equivalent, not falsely accepted as production hero assets.

## Output Summary

Return:

- changed files
- commands run
- validation result
- risks or blockers
