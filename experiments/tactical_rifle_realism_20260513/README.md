# Tactical Rifle Realism Experiment - 2026-05-13

Goal: start the realistic asset pipeline for `/Users/yuanshaochen/Documents/14.html` with the rifle/GROZA hero asset.

## Candidate 1: Existing OBJ Baseline

Input:

- `/Users/yuanshaochen/Documents/枪械模型包/rifle.obj`
- `/Users/yuanshaochen/Documents/枪械模型包/rifle.mtl`

Command:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python experiments/tactical_rifle_realism_20260513/blender_obj_weapon_candidate.py -- \
  /Users/yuanshaochen/Documents/枪械模型包/rifle.obj \
  experiments/tactical_rifle_realism_20260513/rifle_obj_baseline \
  --output-name rifle_obj_baseline.glb
```

Outputs:

- `rifle_obj_baseline/rifle_obj_baseline.glb`
- `rifle_obj_baseline/preview.png`
- `rifle_obj_baseline/blender_weapon_candidate_report.json`
- `rifle_obj_baseline/three_glb_parse_inventory.json`

Validation:

```bash
node experiments/game_p5_triposr_three_playable_loop/tools/parse_glb_assets.mjs \
  experiments/tactical_rifle_realism_20260513/rifle_obj_baseline \
  experiments/tactical_rifle_realism_20260513/rifle_obj_baseline/three_glb_parse_inventory.json
```

Result:

- GLB size: 107,992 bytes.
- Meshes: 12.
- Triangles: 2,172.
- Materials: 12 names including metal, glass, polymer, rubber, wood/tan style slots.
- Textures: 0.

Decision:

This candidate is useful as a baseline and integration fallback, but it is not a final realistic asset. It has heuristic PBR-style material adjustments, no source-baked texture maps, and an inferred muzzle anchor.

## Next Candidates

- Candidate 2: GROZA-style high-detail reference-driven candidate, preferably using TRELLIS mesh generation if the existing cached route is available without new large downloads.
- Candidate 3: Hunyuan3D or Rodin comparison only after download/API/cost/proxy constraints are explicitly governed.
