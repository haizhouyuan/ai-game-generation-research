# Visual Evidence Gate - 2026-05-13

## Result

All six rainy checkpoint evidence cameras passed the new CDP visual gate.

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

Each report has `blockingEvents: []`, nonblank image statistics, and `animationOk: true`.

Animation state coverage:

- `01_fp_rifle_wet_checkpoint`: player `reload`, enemy `aim`
- `02_third_person_player_gear`: player `aim`, enemy `idle`
- `03_enemy_under_checkpoint_light`: player `idle`, enemy `walk`
- `04_loot_on_wet_asphalt`: player `idle`, enemy `idle`
- `05_indoor_killhouse_corridor`: player `crouch`, enemy `hit_reaction`
- `06_final_wide_rainy_container_checkpoint`: player `run`, enemy `aim`

## Remaining Visual Blockers

- The rifle and character are still baseline GLB assets, not final PBR hero assets.
- The registry marks those baseline assets as `baseline_only` with blockers, not `production_ready`.
- Animation proof is runtime-visible through `AnimationMixer`, but it is still a proxy rig rather than a cleaned production character GLB.
- PBR route benchmark is still pending.
