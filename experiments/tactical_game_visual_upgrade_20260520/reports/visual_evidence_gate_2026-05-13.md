# Visual Evidence Gate - 2026-05-13

## Result

All six rainy checkpoint evidence cameras passed the CDP visual gate after adding the runtime animation proof and the hero rifle V2 PBR asset packet.

## Command

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

## Evidence

- `evidence/01_fp_rifle_wet_checkpoint.png`
- `evidence/02_third_person_player_gear.png`
- `evidence/03_enemy_under_checkpoint_light.png`
- `evidence/04_loot_on_wet_asphalt.png`
- `evidence/05_indoor_killhouse_corridor.png`
- `evidence/06_final_wide_rainy_container_checkpoint.png`

Each report has `blockingEvents: []`, nonblank image statistics, `animationOk: true`, and `heroRifleOk: true`.

Hero rifle gate coverage:

- `target_hero_rifle_v2.state`: `loaded`
- `fallbackUsed`: `false`
- runtime `materialMapCount`: `4`
- registry `material_map_count`: `5`
- declared texture maps: `basecolor`, `normal`, `roughness`, `metallic`, `ao`
- missing weapon anchors: none

Animation state coverage:

- `01_fp_rifle_wet_checkpoint`: player `reload`, enemy `aim`
- `02_third_person_player_gear`: player `aim`, enemy `idle`
- `03_enemy_under_checkpoint_light`: player `idle`, enemy `walk`
- `04_loot_on_wet_asphalt`: player `idle`, enemy `idle`
- `05_indoor_killhouse_corridor`: player `crouch`, enemy `hit_reaction`
- `06_final_wide_rainy_container_checkpoint`: player `run`, enemy `aim`

## Remaining Visual Blockers

- The hero rifle V2 is now a local Blender-first PBR proof and is marked `production_ready`, but it is still procedural/local-authored rather than an AI-generated or vendor-grade commercial weapon asset.
- Animation proof is runtime-visible through `AnimationMixer`, but it is still a proxy rig rather than a cleaned production character GLB.
- PBR route benchmark is still pending.
