# Task: hero-rifle-v2-001

## Goal

Produce or select one hero rifle V2 asset packet with PBR texture-map evidence and first-person/third-person game-readiness.

## Host

HomePC dual 3090 for GPU generation/rendering; Mac for integration review.

## Runner Route

HomePC GPU worker for asset generation. Codex reviews and integrates. Do not run large downloads without policy evidence.

## Read Scope

- `experiments/tactical_game_full_realism_final_20260513/assets/models/groza_procedural_candidate.glb`
- `experiments/tactical_game_full_realism_final_20260513/assets/asset_inventory_matrix.json`
- `docs/production_goal_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`

## Write Scope

- `experiments/tactical_game_visual_upgrade_20260520/assets/weapons/hero_rifle_v2/**`
- `experiments/tactical_game_visual_upgrade_20260520/reports/hero_rifle_v2/**`
- `experiments/tactical_game_visual_upgrade_20260520/evidence/hero_rifle_v2/**`

## Forbidden

- real firearm manufacturing details or instructions
- private screenshots or private reference uploads
- global proxy configuration
- any single download over 1GB without explicit approval
- any single download over 100MB without no-proxy evidence

## Verification

```bash
test -f experiments/tactical_game_visual_upgrade_20260520/assets/weapons/hero_rifle_v2/model/cleaned.glb
test -f experiments/tactical_game_visual_upgrade_20260520/assets/weapons/hero_rifle_v2/reports/material_report.json
```

## Expected Artifacts

- `model/cleaned.glb`
- `textures/basecolor.*`
- `textures/normal.*`
- `textures/roughness.*`
- `textures/metallic.*`
- `textures/ao.*`
- `reports/material_report.json`
- `evidence/blender_preview.png`
- `evidence/threejs_first_person.png`
- `evidence/threejs_third_person.png`

## Acceptance

- `material_map_count >= 4` or a concrete blocker report with next route.
- Anchors exist or blocker report explains why not: `Muzzle`, `Grip_R`, `Grip_L`, `Optic`, `PickupRoot`, `ThirdPersonMount`.
- First-person screenshot clearly improves over current procedural candidate.

## Output Summary

- route used
- commands run
- download policy evidence
- generated files
- known visual flaws

