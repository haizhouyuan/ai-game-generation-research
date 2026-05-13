# Tactical Game Asset Inventory - 2026-05-13

Source game: `/Users/yuanshaochen/Documents/14.html`

Related local sources:

- `/Users/yuanshaochen/Documents/枪械模型包/`
- `/Users/yuanshaochen/Documents/groza_high_detail_3d_model_viewer.html`

## Summary

The game is a self-contained Three.js HTML file. It does not currently load external GLB/GLTF weapon assets. Most visible objects are procedural Three.js meshes.

The first realism pass should focus on the rifle/GROZA weapon asset because it is the most repeatedly visible and has the clearest upgrade path.

## Main Asset Classes

| Asset class | Current creation area | Realism impact |
| --- | --- | --- |
| Sky, lighting, ground, roads | `initWorld()` / `createSky()` around `14.html` line 267 | High: affects whole scene mood and material credibility |
| Compound walls, buildings, warehouse, containers | `createCompound()`, `createBuilding()`, `createWarehouse()`, `createContainers()` around lines 295, 307, 468, 481 | High: scene still reads as procedural if boxes dominate |
| Building facade details | `addBuildingFacade()` around line 371 | High: windows, AC units, stains, balconies, pipes break up plain boxes |
| Ladders, platforms, railings | `addPhysicalStairs()` around line 431 | Medium: important close-up navigation props |
| Trees, branches, leaf clusters, shrubs, rocks | `createYard()` and helpers around lines 489 and 532 | Medium-high: improves outdoor realism and scale |
| Grass instances | `createGrass()` around line 611 | Medium: helps ground detail |
| Player and NPC characters | `createCharacter()` around line 683 | Very high but harder: silhouettes, armor, helmet, gear, animation constraints |
| Weapons: pistol, shotgun, rifle, DMR | `gunMaterials()`, `createGunModel()`, `decorateGunVisuals()` around lines 626, 635, 658 | Highest first target: visible in first/third person, NPC, and loot |
| First-person and third-person weapon mounting | `rebuildGuns()` around line 706 | Critical integration point |
| Loot props: weapons, armor, helmets, ammo, medical, revive crystal | `lootTable()` and `spawnLootAt()` around lines 719 and 721 | Medium-high: close interaction objects |
| Shooting effects: tracer, muzzle flash, casing, impact, burst, floating text | around lines 970-1059 | High for perceived shooting realism |
| Labels/text sprites | `makeText()` around line 618 | Low-medium: UI/game readability |

## Existing Weapon Pack

`/Users/yuanshaochen/Documents/枪械模型包/README.txt` describes:

- `rifle.obj` / `rifle.mtl`: TAC-AR high-detail assault rifle prototype;
- `dmr.obj` / `dmr.mtl`: XMR-7 marksman rifle prototype;
- `shotgun.obj` / `shotgun.mtl`: BREACH-12 tactical shotgun prototype;
- `pistol.obj` / `pistol.mtl`: P-9 tactical pistol prototype.

The README states these are editable low/mid-poly web prototype models, not scan-grade realistic assets. They are useful references or fallbacks, not the final realism bar.

## GROZA Viewer

`/Users/yuanshaochen/Documents/groza_high_detail_3d_model_viewer.html` contains a separate procedural GROZA-style model viewer.

Useful areas:

- `createGroza()` around line 441: core rifle construction;
- `createCurvedMagazine()` around line 416: curved magazine logic;
- `noiseTexture()` / `makeMaterials()` around lines 254 and 298: procedural metal/wood texture direction;
- viewer controls around lines 408, 525, 604: labels, exploded view, loop.

This file is the best local art direction reference for the first hero rifle.

## First Hero Asset Recommendation

Build a realistic **GROZA / TAC-AR style rifle GLB** for the `rifle` slot.

Reasons:

- It is large enough to show meaningful details.
- It appears in first-person view, third-person player view, NPC hands, and ground loot.
- It exercises the full weapon integration contract: mount, scale, material, muzzle origin, shadow, ADS framing, and fallback.
- It can reuse the GROZA viewer as a structural reference without copying a real copyrighted game asset.

## Integration Requirements

A GLB-backed weapon replacement must preserve the current gameplay contract:

- The GLB must expose or receive a `userData.muzzle` equivalent for `fireWeapon()`.
- `createGunModel(type, skinful)` should keep a procedural fallback.
- `rebuildGuns()` must handle separate first-person and third-person scale/rotation.
- NPC weapon creation must still provide a muzzle for enemy shots.
- Ground loot must still be visible, scaled, and pickable.
- Shadows must be enabled on imported meshes.
- Materials should preserve PBR/texture information unless a deliberate skin override is applied.

## Verification Checklist

- GLB loads without CORS or missing file errors.
- Rifle appears correctly in first-person hip-fire and ADS views.
- Rifle appears correctly on third-person player/NPC mounts.
- Ground loot rifle appears at readable scale.
- Muzzle flash/tracer origin is visually aligned.
- Weapon switching still works.
- Core controls still work.
- Browser console has no blocking errors.
- Evidence includes screenshots and parse/hash reports.
