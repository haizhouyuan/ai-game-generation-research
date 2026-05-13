# Tactical Game Visual Upgrade - 2026-05-20 Target

This experiment is the working packet for the realistic tactical-game visual upgrade.

## Baseline

The baseline remains read-only:

- `experiments/tactical_game_full_realism_final_20260513/index.html`
- `experiments/tactical_game_full_realism_final_20260513/assets/asset_registry.json`
- `experiments/tactical_game_full_realism_final_20260513/evidence/*`

Do not overwrite the baseline. Copy or reference assets into this experiment only when the task packet explicitly says to.

## Target Scene

Build a dense 12m x 18m rainy tactical checkpoint micro-slice:

- container yard entrance;
- small checkpoint booth;
- killhouse/corridor entry;
- wet asphalt, puddles, decals, clutter, industrial lights, fog/rain;
- hero rifle in first-person and third-person contexts;
- player and enemy tactical characters with minimum animation proof.

## Evidence Cameras

1. `01_fp_rifle_wet_checkpoint`
2. `02_third_person_player_gear`
3. `03_enemy_under_checkpoint_light`
4. `04_loot_on_wet_asphalt`
5. `05_indoor_killhouse_corridor`
6. `06_final_wide_rainy_container_checkpoint`

## Current Skeleton

- `assets/` - new or copied production asset packets.
- `schemas/` - asset packet and registry contracts.
- `src/runtime/` - loader, registry, animation, material, weather, decal, evidence modules.
- `src/scene/` - rainy checkpoint scene layout.
- `tools/` - validation and evidence commands.
- `reports/` - task reports and runner outputs.
- `evidence/` - browser, Blender, and visual gate screenshots/reports.

## Current Production Asset Proof

- Hero rifle: `assets/weapons/hero_rifle_v2/model/optimized.glb`
- PBR maps: `basecolor`, `normal`, `roughness`, `metallic`, `ao`
- Required anchors: `Muzzle`, `Grip_R`, `Grip_L`, `Optic`, `PickupRoot`, `ThirdPersonMount`
- Browser contexts: first-person rifle, third-person player, NPC weapon, and world pickup

This packet is a local Blender-first PBR proof. It used no external asset or model download.

## Run

From the repository root:

```bash
python3 -m http.server 8877
```

Open:

```text
http://127.0.0.1:8877/experiments/tactical_game_visual_upgrade_20260520/index.html
```

Evidence camera example:

```text
http://127.0.0.1:8877/experiments/tactical_game_visual_upgrade_20260520/index.html?evidence=06_final_wide_rainy_container_checkpoint
```

## Verification

From the repository root:

```bash
./.venv/bin/python -m pytest tests/test_validate_asset_registry_v2.py
./.venv/bin/python tools/validate_asset_registry_v2.py experiments/tactical_game_visual_upgrade_20260520/assets/asset_registry_v2.json
python3 -m py_compile experiments/tactical_game_visual_upgrade_20260520/tools/build_hero_rifle_v2.py
node --check experiments/tactical_game_visual_upgrade_20260520/src/main.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/animationSystem.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/lightingSystem.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/weatherSystem.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/decalSystem.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/scene/rainyCheckpointLayout.js
node --check experiments/tactical_game_visual_upgrade_20260520/tools/visual_evidence_gate.mjs
./.venv/bin/python tools/verify_artifact_hashes.py experiments/tactical_game_visual_upgrade_20260520/artifact_hashes.json
```

With the local server running on port `8877`, capture all six evidence cameras:

```bash
for camera in \
  01_fp_rifle_wet_checkpoint \
  02_third_person_player_gear \
  03_enemy_under_checkpoint_light \
  04_loot_on_wet_asphalt \
  05_indoor_killhouse_corridor \
  06_final_wide_rainy_container_checkpoint; do
  node experiments/tactical_game_visual_upgrade_20260520/tools/visual_evidence_gate.mjs "$camera"
done
```

The CDP reports include `probe.animation` and `probe.assetStatus.target_hero_rifle_v2`. The visual gate requires `animationOk: true`, `heroRifleOk: true`, no fallback, and at least four runtime material maps for each camera.
