# M5 Visible Asset Upgrade Plan - 2026-05-13

Goal: continue `docs/production_goal_realistic_3d_assets_for_tactical_game_2026-05-13.md` beyond the hero rifle proof.

Current controlled derivative:

- `experiments/tactical_game_realism_upgrade_20260513/index.html`

## Priority Batches

### Batch A: Character And Gear Silhouette

Target functions:

- `createCharacter(kind)`
- `createEnemy(...)`

Expected upgrades:

- helmet shell and visor;
- armor plate/vest;
- shoulder/knee pads;
- backpack or tactical rig;
- pouches and straps;
- enemy/player color differentiation.

Acceptance evidence:

- static verifier checks for named gear markers;
- runtime screenshot where player/NPC silhouette is visible;
- no regression in rifle runtime probe.

### Batch B: Loot Props

Target functions:

- `spawnLootAt(point)`
- `lootTable()`

Expected upgrades:

- ammo box instead of plain rarity block;
- med pouch/first-aid kit/medkit case;
- vest/helmet miniature models;
- revive crystal in a contained prop;
- weapon pickup still routes through `createGunModel`.

Acceptance evidence:

- static verifier checks for prop builder or marker names;
- runtime screenshot or probe with loot props visible;
- pickup logic unchanged.

### Batch C: Environment Props

Target functions:

- `createContainers()`
- `createYard()`
- `createRealTree(...)`
- `addBuildingFacade(...)`
- `addPhysicalStairs(...)`

Expected upgrades:

- corrugation ribs and container door hardware;
- warning stripes/labels;
- ladder rails and repeated rungs;
- rock clusters and trunk bark bands;
- building vents, pipes, utility boxes, trims.

Acceptance evidence:

- static verifier checks for environment detail markers;
- browser or Chrome CDP scene screenshot;
- no major performance regression.

### Batch D: Remaining Weapons

Target functions:

- `createGunModel(type, skinful)`
- optional GLB/procedural candidates.

Expected upgrades:

- pistol, shotgun, DMR visual detail pass;
- better rifle first-person/third-person framing without evidence-only helper.

Acceptance evidence:

- runtime screenshots for each weapon or documented deferral.

## Done Definition For M5

M5 can be considered complete only when every major visible class from the production goal is either:

- upgraded in the controlled derivative with evidence; or
- explicitly deferred with a concrete reason and next route.

Current state after the M5 execution pass:

- Batch A complete with in-place character/gear geometry.
- Batch B complete with readable loot props.
- Batch C complete for the derivative's major visible environment props, with scan-grade imported GLBs deferred.
- Batch D complete for all playable weapon slots through generated local GLBs.

M5 is acceptable for the first production pass because every listed class is either upgraded in the derivative or has a concrete deferral reason in `experiments/tactical_game_realism_upgrade_20260513/report.md`.
