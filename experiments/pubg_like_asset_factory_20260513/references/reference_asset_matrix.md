# Reference Asset Matrix - PUBG-Like Local AI 3D Asset Factory

Goal file:

`docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`

This matrix tracks the source image or prompt set that feeds each production asset packet. A final asset is not complete unless it has a reference/provenance row, a generated or PBR-authored packet, Blender cleanup evidence, and Three.js evidence.

## Reference Style Contract

- Realistic modern tactical survival shooter direction.
- Rainy checkpoint / container yard / killhouse entry.
- Worn metal, fabric weave, mud, scratches, wet asphalt, industrial lighting.
- Avoid stylized sci-fi, fantasy, toy-like plastic, clean showroom surfaces.
- Avoid real weapon manufacturing detail; the target is game visual believability.

## Matrix

| ID | Asset Target | Reference Source | Generation Prompt File | 3D Route | PBR Route | Status | Acceptance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ref_hero_rifle_001 | Hero rifle + optic + magazine + attachments | AI reference required | `prompts/hero_rifle_reference_001.md` | Hunyuan/TRELLIS/Blender hybrid | Hunyuan Paint or ComfyUI/PBR projection | pending | first-person close-up, anchors, 4+ maps |
| ref_sidearm_001 | Sidearm or compact secondary | AI reference required | `prompts/sidearm_reference_001.md` | Hunyuan or TRELLIS | PBR projection/completion | pending | loot and first-person close-up |
| ref_player_tactical_001 | Player tactical character front/side/back | AI reference required | `prompts/player_tactical_reference_001.md` | Hunyuan/character workflow/Blender | texture projection/PBR maps | pending | rig/animation or blocker |
| ref_enemy_tactical_001 | Enemy tactical variant | AI reference required | `prompts/enemy_tactical_reference_001.md` | Hunyuan/character workflow/Blender | texture projection/PBR maps | pending | distinct silhouette and animation |
| ref_gear_set_001 | Helmet, vest, pouches, backpack, gloves, boots | AI reference required | `prompts/gear_set_reference_001.md` | Hunyuan/TRELLIS per module | PBR projection/completion | pending | modular or combined gear packet |
| ref_wet_asphalt_001 | Wet asphalt ground material | AI/local material reference | `prompts/wet_asphalt_reference_001.md` | material texture workflow | TextureAlchemy/CHORD/PBRFusion equivalent | pending | basecolor/normal/roughness/AO |
| ref_concrete_wall_001 | Dirty concrete wall material | AI/local material reference | `prompts/concrete_wall_reference_001.md` | material texture workflow | TextureAlchemy/CHORD/PBRFusion equivalent | pending | visible roughness/normal variation |
| ref_container_checkpoint_001 | Container wall + checkpoint booth | AI reference required | `prompts/container_checkpoint_reference_001.md` | Hunyuan/TRELLIS/Blender | PBR projection/completion | pending | scene module in Three.js |
| ref_loot_set_001 | Medkit, ammo box, weapon pickup | AI reference required | `prompts/loot_set_reference_001.md` | Hunyuan small prop first | Hunyuan Paint/PBR or projection | pending | 3+ loot props on wet ground |
| ref_clutter_decals_001 | Casings, cable, cone, pallet, mud/scratch/impact decals | AI/local reference | `prompts/clutter_decals_reference_001.md` | Blender/TRELLIS/Hunyuan per prop | PBR/decal texture workflow | pending | 30+ placed instances/decals |

## Immediate First Chain

First full reference-to-3D/PBR candidate should be one low-risk prop from `ref_loot_set_001`, preferably a medkit or ammo box:

1. Generate realistic reference image.
2. Run Hunyuan shape.
3. Run Hunyuan Paint or PBR fallback.
4. Clean in Blender.
5. Add Three.js close-up.
6. Record why each stage passed or failed.
