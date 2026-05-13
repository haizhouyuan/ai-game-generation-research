# Tactical Game Full Realism Final - 2026-05-13

This is the final playable experiment for:

`docs/production_goal_full_realistic_3d_tactical_game_final_2026-05-13.md`

It is a controlled derivative of `source/14.html`, which is a repository snapshot of the original `/Users/yuanshaochen/Documents/14.html`; the original source file is not modified.

## What Changed

- All four weapon slots load GLB assets: pistol, shotgun, rifle/GROZA, and DMR.
- Player and enemy bodies get final GLB tactical overlays with helmet, visor, plate carrier, backpack, pouches, gloves, and pads.
- Non-weapon loot uses final GLB props for ammo, bandage, first aid, medkit, revive, vest, and helmet.
- The scene stages final GLB environment props for crates, containers, ladder/stair/railing modules, interior furniture, building utility details, ground/road/wall/fence/gate kits, trees, and rock clusters while keeping existing collision/gameplay logic intact.
- Evidence modes cover weapons, characters, loot, environment, and a combined final showcase.

## Run

```bash
cd /Users/yuanshaochen/Projects/ai-game-generation-research/experiments/tactical_game_full_realism_final_20260513
python3 -m http.server 8765
```

Open:

- `http://localhost:8765/index.html`
- `http://localhost:8765/index.html?evidence=weapons`
- `http://localhost:8765/index.html?evidence=characters`
- `http://localhost:8765/index.html?evidence=loot`
- `http://localhost:8765/index.html?evidence=environment`
- `http://localhost:8765/index.html?evidence=final`

## Evidence Packet

- `assets/asset_registry.json`
- `assets/asset_inventory_matrix.json`
- `assets/models/final_asset_kit_report.json`
- `assets/models/final_three_glb_parse_inventory.json`
- `evidence/rifle_evidence_cdp_first.png`
- `evidence/rifle_evidence_cdp_third.png`
- `evidence/weapons_evidence_cdp.png`
- `evidence/characters_evidence_cdp.png`
- `evidence/loot_evidence_cdp.png`
- `evidence/environment_evidence_cdp.png`
- `evidence/final_evidence_cdp.png`
- `artifact_hashes.json`

## Verification

From the repository root:

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

Every generated CDP report must have `blockingEvents: []`.

For before/after capture, start two local servers from this experiment directory:

```bash
cd /Users/yuanshaochen/Projects/ai-game-generation-research/experiments/tactical_game_full_realism_final_20260513
python3 -m http.server 8765
python3 -m http.server 8766
```

Then run from the repository root:

```bash
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_before_after_capture.mjs
```

## Asset Notes

The final kit is locally generated/selected and integrated as GLB assets with mesh counts, material names, bounds, previews, parse inventory, screenshots, and hash manifest. Material evidence is PBR-style Blender material factors plus mesh detail; the runtime contract is deliberately asset-registry-based so a future Hunyuan3D/TRELLIS/scanned texture-baked kit can replace these GLBs without changing gameplay wiring.

The acceptance matrix in `assets/asset_inventory_matrix.json` is the source-of-truth checklist for the production goal. It covers every required visible class, including containers, ladders/stairs, interiors, ground/roads/walls/fences, and lighting/sky/fog/shadow configuration.
