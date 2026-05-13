# Route C/D Textured Crate Preview 008 Summary

## Verdict

`valid_textured_probe`

## What Ran

A headless Blender script imported the TRELLIS crate mesh, applied Smart UV
Project, wired TextureAlchemy PBR maps into a Principled BSDF material, exported
a textured GLB, and rendered a textured preview.

## Outputs

- Textured GLB: `outputs/tactical_crate_textured_probe.glb`
- Textured preview: `evidence/blender_textured_preview.png`
- Script: `reports/blender_textured_crate_preview.py`
- Report: `reports/blender_textured_preview_report.json`
- Hashes: `reports/output_sha256.txt`

## Mesh And Material Facts

- Mesh objects: 1
- Vertices: 16,367
- Polygons: 32,722
- UV layer: `UVMap`
- Material: `TA_probe_crate_pbr`
- Texture nodes wired: `basecolor`, `roughness`, `metallic`, `normal`

## Quality Read

This is a real proof that the generated texture maps can be wired onto the
generated 3D mesh and rendered in Blender. It is not a production-ready prop.

Remaining issues:

- Smart UV projection creates visible arbitrary mapping and color patches.
- The PBR maps are heuristic single-image maps, not true multi-view projection.
- Material zones are not separated.
- No final LOD, collision proxy, or Three.js gameplay evidence exists.
- The visual result is useful as a background diagnostic, not a PUBG-like final asset.

## Next Step

Use this as a test fixture for registry/runtime gates and for comparing Hunyuan
Paint once the DINOv2 dependency finishes downloading. Do not promote it as a
final scene asset without better UVs, texture projection, and runtime evidence.
