# Hero Rifle V2 PBR Asset Packet - 2026-05-13

## Result

`target_hero_rifle_v2` is now a local Blender-first production proof for the rainy checkpoint slice.

It is not a downloaded commercial model and it did not require any external model or asset download. The purpose of this pass was to break the previous `material_factors_only` blocker and prove that the runtime can carry a rifle packet with real texture maps, named weapon anchors, and in-game evidence.

## Asset Packet

- Model: `assets/weapons/hero_rifle_v2/model/optimized.glb`
- Preview: `assets/weapons/hero_rifle_v2/evidence/blender_preview.png`
- Material report: `assets/weapons/hero_rifle_v2/reports/material_report.json`
- Cleanup report: `assets/weapons/hero_rifle_v2/reports/blender_cleanup_report.json`
- Source note: `assets/weapons/hero_rifle_v2/source/reference.md`
- License note: `assets/weapons/hero_rifle_v2/source/license.md`

## PBR Maps

- `basecolor.png`
- `normal.png`
- `roughness.png`
- `metallic.png`
- `ao.png`

The Blender material report records `material_map_count: 5`. Browser evidence reports runtime `materialMapCount: 4`, because the runtime gate counts maps directly connected to the GLB material channels and treats AO as registry-side support evidence.

## Anchors

- `Muzzle`
- `Grip_R`
- `Grip_L`
- `Optic`
- `PickupRoot`
- `ThirdPersonMount`

## Browser Contexts

The same GLB is mounted in four runtime contexts:

- first-person rifle close-up: `fp_hero_rifle_v2_visual`
- third-person player weapon: `third_person_hero_rifle_v2_visual`
- NPC weapon: `npc_hero_rifle_v2_visual`
- world pickup / loot context: `loot_world_hero_rifle_v2_visual`

All six evidence cameras passed with `heroRifleOk: true`, `fallbackUsed: false`, and `blockingEvents: []`.

## Limits

This is a credible local PBR proof, not the final art target. It still needs a stronger artist/model-generation pass for silhouette fidelity, small mechanical details, edge wear directionality, optic glass polish, and animation-authored first-person handling.
