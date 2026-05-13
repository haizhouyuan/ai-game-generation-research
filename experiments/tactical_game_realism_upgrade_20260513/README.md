# Tactical Game Realism Upgrade: GROZA GLB Integration Probe

This controlled derivative wires the selected local GROZA GLB candidate into the source game's rifle creation path without modifying `/Users/yuanshaochen/Documents/14.html`.

## Files

- `index.html` is copied from the source game and patched locally in this experiment.
- `assets/models/groza_procedural_candidate.glb` is copied from `../tactical_rifle_realism_20260513/groza_procedural/groza_procedural_candidate.glb`.
- `tools/verify_integration.py` performs lightweight static and asset-header checks.

## Integration Points

- `createGunModel("rifle", ...)` first attempts to clone `assets/models/groza_procedural_candidate.glb`.
- The page uses a small built-in GLB reader for this embedded baseline asset. If the GLB fails to load or parse, `createGunModel` falls through to the original procedural rifle.
- `rebuildGuns()` remains the first-person and third-person rebuild path, so the active player rifle can use the GLB once loaded.
- `spawnLootAt()` and `createEnemy()` still call `createGunModel()`, so rifle loot and NPC rifles can use the same replaceable GLB path.
- Every GLB rifle wrapper sets `userData.muzzle`; if the GLB contains a `Muzzle` node it uses that anchor, otherwise it falls back to the original procedural rifle muzzle position `(0, .06, 1.82)`.
- The GROZA candidate is rotated from Blender's +X muzzle axis into the game's +Z weapon-forward axis, and proxy/collider nodes are hidden by name.

## M5 Visible Asset Upgrade Pass 1

This pass keeps the GROZA GLB rifle integration intact and upgrades additional visible assets with local Three.js procedural geometry:

- `weaponAssets` now loads GLB candidates for all four playable weapon slots: pistol, shotgun, rifle/GROZA, and DMR. The pistol, shotgun, and DMR candidates are generated locally through Blender and stored under `assets/models/*_m5_candidate.glb`.
- `createCharacter(kind)` now layers tactical silhouettes onto player and NPC bodies: plate carrier panels, front pouches, shoulder/knee pads, backpack/rig, helmet comms, visor details, and team-color accents.
- `spawnLootAt()` keeps the same pickup data and behavior, but non-weapon loot now routes through `createM5LootProp()` for readable props: ammo box with rounds, med pouch/medkit case with medical cross, vest mini model, helmet mini model, and revive crystal container.
- `createContainers()` calls `addM5ContainerDetails()` for corrugation ribs, door seams, hinges, and warning strips without changing container colliders.
- Existing tree bark strips, branches, rocks, ladder rails/rungs, and building facade details remain part of this derivative's environment art pass.

Generated M5 weapon evidence:

- `assets/models/m5_weapon_variants_report.json`
- `assets/models/pistol_m5_preview.png`
- `assets/models/shotgun_m5_preview.png`
- `assets/models/dmr_m5_preview.png`

## Local Run

From the repository root:

```bash
cd /Users/yuanshaochen/Projects/ai-game-generation-research/experiments/tactical_game_realism_upgrade_20260513
python3 -m http.server 8765
```

Then open `http://127.0.0.1:8765/index.html`.

Serving over HTTP is recommended because the GLB is loaded with `fetch`; opening the HTML directly from `file://` may keep the game playable through fallback but can block model loading.

For automated visual evidence, open:

```text
http://127.0.0.1:8765/index.html?evidence=rifle
```

That mode starts a local run, unlocks/selects the rifle, keeps the normal game systems active, and exposes `window.__realismProbe()` for validation.

For an all-weapon M5 evidence view, open:

```text
http://127.0.0.1:8765/index.html?evidence=m5
```

The CDP evidence tool now fails on runtime exceptions, network load failures, or browser log errors instead of reporting success from asset status alone.

## Limitations

- `groza_procedural_candidate.glb` is a local procedural hard-surface candidate, not a photogrammetry or textured generator-final production rifle.
- Materials are Blender procedural/PBR-style material assignments with no baked texture maps.
- Muzzle placement is wired and fallback-safe, but final high-realism GLBs should include an explicit `Muzzle` node and be visually checked in first-person, third-person, NPC, and loot contexts.
- Character/gear, loot, containers, ladders, rocks, trees, and building facade details are upgraded in-place with local Three.js geometry and PBR-style materials, not imported scan-grade GLBs.
- Imported character/environment GLBs are deferred because no sufficiently realistic, low-risk local generation route was validated within this pass. The next route should be Hunyuan3D/TRELLIS/PBR generation plus Blender cleanup per class.
