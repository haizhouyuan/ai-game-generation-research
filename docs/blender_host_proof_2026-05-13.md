# Blender Host Proof - 2026-05-13

## Result

Blender is now installed locally and has a disposable asset cleanup/export proof.

- Blender path: `/Applications/Blender.app/Contents/MacOS/Blender`
- Version: `5.1.1`
- Build hash: `b70da489d7f4`
- Download record: `docs/download_records/blender_5_1_1_2026-05-13.md`

## Proof Command

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python experiments/blender_host_probe_20260513/blender_glb_cleanup_probe.py -- experiments/game_p26_trellis_meshonly_asset_validation_20260512/outputs/typical_misc_crate_trellis_meshonly.glb experiments/blender_host_probe_20260513/outputs
```

## Evidence

- Script: `experiments/blender_host_probe_20260513/blender_glb_cleanup_probe.py`
- Log: `experiments/blender_host_probe_20260513/logs/blender_cleanup_probe.log`
- Summary: `experiments/blender_host_probe_20260513/outputs/summary.json`
- Mesh/material report: `experiments/blender_host_probe_20260513/outputs/blender_cleanup_report.json`
- Cleaned GLB: `experiments/blender_host_probe_20260513/outputs/typical_misc_crate_blender_cleaned_with_proxy.glb`
- Render: `experiments/blender_host_probe_20260513/outputs/blender_cleanup_render.png`
- Three.js parse readback: `experiments/blender_host_probe_20260513/outputs/three_glb_parse_inventory.json`

## What Was Proven

- Blender can run headless on this Mac.
- Blender can import the existing P26 TRELLIS mesh-only GLB.
- The imported mesh can be normalized to about a 2-unit bounding box.
- A simple box collider proxy can be generated separately from the mesh.
- Blender can export a cleaned GLB.
- Blender can render a PNG proof image.
- The cleaned GLB can be parsed by the existing Three.js/GLTFLoader validation path.

## Mesh Notes

Input mesh:

- Mesh objects: `1`
- Vertices: `54797`
- Faces: `110066`
- Material slots: `1`
- Texture state: material present, texture not assumed.

Proxy collider:

- Name: `COLLIDER_PROXY_bbox_simple_box`
- Type: simple box
- Dimensions: about `2.0 x 2.0 x 1.99`

## Limitations

- This is a Blender Python proof, not Blender MCP.
- The cleaned GLB is still the existing crate asset, not the hero rover.
- The source asset remains mesh-only; this proof does not create textured/PBR output.
- The proxy collider is exported as evidence geometry and should be adapted per runtime before gameplay use.
