# Route D TRELLIS Prop Probe 005 Summary

## Verdict

`background_only`

## Host And Runner

- Host: HomePC (`yuanhaizhou-home`)
- Runner: Codex orchestrated shell job
- GPU: GPU1, RTX 3090

## Target Prop

- Asset candidate: tactical crate / hard-surface supply box
- Reference image: `inputs/tactical_crate_reference.png`
- Reference source: copied from prior local TRELLIS crate validation experiment as a non-rifle prop probe input

## Commands Run

```bash
TRELLIS_GPU=1 python /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p26_trellis_asset_validation_20260512/trellis_meshonly_generate.py \
  /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/routes/route_d_trellis_prop_probe_005/inputs/tactical_crate_reference.png \
  /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/routes/route_d_trellis_prop_probe_005/outputs/raw/tactical_crate_trellis_meshonly.glb \
  --gpu 1 --seed 77 --simplify 0.96

xvfb-run -a blender --background \
  --python /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/routes/route_d_trellis_prop_probe_005/reports/blender_preview.py \
  -- /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/routes/route_d_trellis_prop_probe_005/outputs/raw/tactical_crate_trellis_meshonly.glb \
     /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/routes/route_d_trellis_prop_probe_005/evidence/blender_import.png \
     /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/routes/route_d_trellis_prop_probe_005/reports/blender_import_report.json
```

The first Blender attempt without Xvfb failed with `Unable to open a display`; the Xvfb run succeeded.

## Outputs

- Raw GLB: `outputs/raw/tactical_crate_trellis_meshonly.glb`
- SHA256: `outputs/raw/tactical_crate_trellis_meshonly.glb.sha256`
- Blender evidence: `evidence/blender_import.png`
- Blender import report: `reports/blender_import_report.json`
- Run log: `reports/run_report.md`

## Mesh Facts

- File size: 655,544 bytes
- Raw TRELLIS mesh: 974,896 vertices, 1,949,820 faces
- Postprocessed mesh: 16,367 vertices, 32,722 faces
- Blender import: 1 mesh object, 1 material
- Texture maps: 0

## Texture / PBR Next Step

- Route C: use ComfyUI/Hunyuan/Texture Projection or equivalent route to create basecolor, normal, roughness, and metallic/AO maps.
- Blender cleanup: decimate further if used as a repeated prop; add UV/material zones; add collision proxy.
- Blocker: TRELLIS mesh-only route gives usable silhouette evidence, not production PBR. It should not be promoted as a final near-camera asset without texture/PBR and cleanup.

## Production Suitability Notes

The generated crate is visibly better than a plain procedural cube for background or mid-distance scene dressing. It still reads like a clay preview, not a PUBG-like production asset. Final use requires PBR texture maps, material separation, wear decals, and lower-triangle optimized variants.
