# Tactical Game Realism Upgrade Report - 2026-05-13

## Scope

This experiment is a controlled derivative of `/Users/yuanshaochen/Documents/14.html`.

It does not modify the source file. It integrates the selected GROZA hero rifle candidate into the rifle path of the playable tactical compound game.

Playable derivative:

- `index.html`

Selected rifle asset:

- `assets/models/groza_procedural_candidate.glb`

## Integration

`createGunModel("rifle")` now attempts to use the selected GLB before falling back to the original procedural rifle.

The same rifle creation path is still used by:

- first-person weapon rebuild;
- third-person player weapon mount;
- NPC weapon mount;
- ground loot weapon display.

The wrapper preserves `userData.muzzle`. If a future GLB contains a `Muzzle` node, the loader can use it; otherwise it computes a fallback muzzle from the model bounds.

The GLB is rotated from Blender +X muzzle-forward coordinates into the game's +Z weapon-forward convention. Proxy/collider nodes are hidden by name.

## M5 Visible Asset Upgrade Pass 1

This pass starts the M5 full visible asset pass without modifying `/Users/yuanshaochen/Documents/14.html` and without downloading external assets.

Covered in this pass:

- Remaining weapon slots: local Blender generated `pistol_m5_candidate.glb`, `shotgun_m5_candidate.glb`, and `dmr_m5_candidate.glb`; the game now loads pistol, shotgun, rifle, and DMR through a shared `weaponAssets` GLB path before falling back to the original procedural geometry.
- Player/NPC character silhouettes: `createCharacter(kind)` now uses `addM5TacticalGear()` to add helmet comms, visor/helmet accents, plate carrier panels, vest pouches, backpack/rig, shoulder pads, knee/shin pads, and team-color enemy/player accents.
- Non-weapon loot props: `spawnLootAt()` preserves the existing loot table and pickup logic, while `createM5LootProp()` adds readable ammo, medical, armor, helmet, and revive-crystal prop shapes.
- Environment props: `createContainers()` now adds `addM5ContainerDetails()` corrugation ribs, door seams, hinges, and warning strips. Existing facade, ladder, tree, and rock detail remains in place.

Explicit deferrals:

- Imported scan-grade character, gear, loot, crate, ladder, rock, and tree GLBs are deferred. The current pass upgraded these classes in-place with local geometry and PBR-style material response; the next realism step should run a per-class Hunyuan3D/TRELLIS/PBR route and Blender cleanup.
- The selected GROZA and M5 weapon variants are still local hard-surface procedural assets with material factors, not photogrammetry or baked-texture production scans.

## Runtime Evidence

Static verifier:

```bash
python3 experiments/tactical_game_realism_upgrade_20260513/tools/verify_integration.py
```

Result: all checks passed, including retained GROZA rifle integration checks, M5 pistol/shotgun/DMR GLB hash/header checks, shared weapon-loader checks, and M5 static markers for character gear, loot props, and container details.

JS syntax check:

```bash
node - <<'NODE'
const fs=require('fs');
const vm=require('vm');
const html=fs.readFileSync('experiments/tactical_game_realism_upgrade_20260513/index.html','utf8');
const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]).filter(s=>s.trim());
if(!scripts.length) throw new Error('no inline script found');
for(const [i,code] of scripts.entries()) new vm.Script(code,{filename:`index.inline.${i}.js`});
console.log(`PASS parsed ${scripts.length} inline script block(s)`);
NODE
```

Result: `PASS parsed 1 inline script block(s)`.

Headless Chrome CDP evidence:

```bash
node experiments/tactical_game_realism_upgrade_20260513/tools/cdp_evidence_capture.mjs first
node experiments/tactical_game_realism_upgrade_20260513/tools/cdp_evidence_capture.mjs third
node experiments/tactical_game_realism_upgrade_20260513/tools/cdp_evidence_capture.mjs m5
```

The first/third rifle runtime probes returned:

- `rifleAsset.status`: `loaded`
- `player.weapon`: `rifle`
- `viewGun.assetSource`: `assets/models/groza_procedural_candidate.glb`
- `thirdGun.assetSource`: `assets/models/groza_procedural_candidate.glb`
- muzzle present for first-person and third-person gun wrappers

The M5 runtime probe returned all weapon assets loaded and a four-weapon camera showcase:

- `pistol`: `assets/models/pistol_m5_candidate.glb`
- `shotgun`: `assets/models/shotgun_m5_candidate.glb`
- `rifle`: `assets/models/groza_procedural_candidate.glb`
- `dmr`: `assets/models/dmr_m5_candidate.glb`

All three CDP reports have `blockingEvents: []`. The CDP gate now fails on runtime exceptions, network load failures, or browser log errors. This fixed the earlier false-positive path where `updateFlashes` was undefined but asset status still reported loaded.

Evidence files:

- `evidence/rifle_evidence_cdp_first.png`
- `evidence/rifle_evidence_cdp_first_report.json`
- `evidence/rifle_evidence_cdp_third.png`
- `evidence/rifle_evidence_cdp_third_report.json`
- `evidence/m5_evidence_cdp.png`
- `evidence/m5_evidence_cdp_report.json`
- `evidence/before_source_gameplay.png`
- `evidence/before_source_gameplay_report.json`
- `evidence/after_upgraded_gameplay.png`
- `evidence/after_upgraded_gameplay_report.json`
- `artifact_hashes.json`

Before/after note:

- The source `/Users/yuanshaochen/Documents/14.html` baseline screenshot captured the original low-fidelity state and also reproduced the source runtime `updateFlashes is not defined` error.
- The upgraded derivative screenshot/report captured the normal playable derivative with the four weapon GLBs loaded and no blocking browser events.

## Local Run

```bash
cd /Users/yuanshaochen/Projects/ai-game-generation-research/experiments/tactical_game_realism_upgrade_20260513
python3 -m http.server 8765
```

Open:

- `http://localhost:8765/index.html`
- `http://localhost:8765/index.html?evidence=rifle`

## Limitations

- The selected GROZA asset is a local procedural hard-surface candidate, not a photogrammetry or textured generator-final asset.
- The runtime probe confirms GLBs are loaded into first-person, third-person, loot/NPC-capable weapon creation paths, but normal gameplay first-person framing can still be tuned artistically.
- Character/gear/loot/environment classes are upgraded enough to supersede the prototype primitive look, but imported scan-grade/PBR GLBs for those classes are deferred with the route described above.
