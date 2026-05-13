# Tactical Game Full Realism Final Report - 2026-05-13

## Scope

This experiment completes the final visible-asset integration target for:

`docs/production_goal_full_realistic_3d_tactical_game_final_2026-05-13.md`

It keeps `/Users/yuanshaochen/Documents/14.html` unchanged and places all runtime, assets, tools, reports, screenshots, and manifests under:

`experiments/tactical_game_full_realism_final_20260513/`

## Integrated Asset Classes

- Weapons: pistol, shotgun, rifle/GROZA, DMR GLBs.
- Characters: player and enemy tactical body overlays with helmet, visor, plate carrier, backpack, pouches, gloves, and pads.
- Loot: ammo, bandage, first aid, medkit, revive, vest, and helmet GLBs.
- Environment: crate/storage, container, ladder/stair/railing, interior furniture, building utility detail, ground/road/wall/fence/gate, tree, and rock-cluster GLBs added to the playable scene.
- Lighting/composition: existing ACES, shadow, fog, and evidence camera staging retained and reused for final asset proof.

The existing gameplay collision, pickup, enemy, and weapon paths stay active. Final visual GLBs are marked visual-only where needed so they do not become enemy hitboxes by accident.

## Evidence

Asset and parser reports:

- `assets/asset_registry.json`
- `assets/asset_inventory_matrix.json`
- `assets/models/final_asset_kit_report.json`
- `assets/models/final_three_glb_parse_inventory.json`

Screenshots and CDP reports:

- `evidence/rifle_evidence_cdp_first.png`
- `evidence/rifle_evidence_cdp_third.png`
- `evidence/weapons_evidence_cdp.png`
- `evidence/characters_evidence_cdp.png`
- `evidence/loot_evidence_cdp.png`
- `evidence/environment_evidence_cdp.png`
- `evidence/final_evidence_cdp.png`

All CDP reports have `blockingEvents: []`.

The CDP reports also include `imageStats` from the actual captured PNG, so the evidence gate rejects blank screenshots instead of trusting runtime probe state alone.

Representative runtime probe results:

- `weaponAssets`: pistol, shotgun, rifle, and DMR all `loaded`.
- `finalAssetKit`: all 13 final GLB assets `loaded`.
- `finalRuntime.playerAsset`: `assets/models/character_player_final.glb`.
- `finalRuntime.enemyAssets`: enemy GLB overlays attached.
- `finalRuntime.lootFinalCount`: final loot GLBs attached in world loot.
- `finalRuntime.environmentPropsAdded`: `true`.
- `assets/asset_inventory_matrix.json`: every production-goal visible class is recorded with current state, target realism level, generation/acquisition route, cleanup route, integration file/function, required evidence, asset ids, material evidence grade, and acceptance status.

## Verification Commands

```bash
python3 experiments/tactical_game_full_realism_final_20260513/tools/verify_integration.py
python3 tools/verify_artifact_hashes.py experiments/tactical_game_full_realism_final_20260513/artifact_hashes.json
node --check experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs weapons
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs characters
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs loot
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs environment
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs final
```

## Material Evidence Grade

Current asset material grade: `material_factors_only`.

That means the GLBs contain detailed mesh assemblies, UV attributes, material names, and PBR-style Blender material factors, but they do not yet contain baked albedo/normal/roughness/metallic texture maps. The final runtime contract and evidence packet are designed so a later Hunyuan3D/TRELLIS/TripoSR/Rodin or scanned texture-baked kit can replace these GLBs without changing gameplay integration.
