# Hunyuan Shape Demo 001 Report

## Status

Passed as a local Hunyuan3D-2.1 shape-generation proof.

This is deliberately not accepted as a final game asset because it has no PBR texture maps yet.

## What Was Proven

- Hunyuan3D-2.1 official code was cloned on HomePC.
- The full Hunyuan3D-2.1 model snapshot was downloaded without using local proxy traffic.
- The standalone shape pipeline ran on GPU1.
- The generated GLB was copied into this repository.
- Local Blender can import, inspect, preview, and re-export the GLB.

## Asset Packet

```text
experiments/pubg_like_asset_factory_20260513/assets/hunyuan_shape_demo_001/
  source/reference.md
  source/license.md
  source/images/input_demo.png
  model/raw.glb
  model/cleaned.glb
  model/optimized.glb
  reports/hunyuan_shape_generation.log
  reports/blender_cleanup_report.json
  reports/material_report.json
  evidence/blender_preview.png
```

## Key Metrics

```text
raw.glb sha256: f52cd0210c8587f5820f93576d230840a2cff2df65bc75dbd52bd8bd4e7263bf
raw.glb size: 12,926,320 bytes
cleaned.glb size: 17,234,896 bytes
optimized.glb size: 17,234,896 bytes
mesh objects: 1
vertices: 359,041
polygons: 718,078
material_map_count: 0
```

## Interpretation

This proves the model installation and shape route are real. It does not prove the final route the user wants, because the final route requires realistic references or generated reference images, PBR texture generation, Blender cleanup, and game-scene integration.

The next required gate is one tactical-domain asset generated through the same route or Hunyuan Paint, with at least:

- `basecolor`
- `normal`
- `roughness`
- `metallic`
- `ao`
- Blender preview
- Three.js close-up
- gameplay-context screenshot

## Current Blocker

The Hunyuan texture/PBR route is blocked at `hy3dpaint` import because the current `hy3d21` Python environment does not provide `bpy`. A separate worker is investigating whether the right fix is Blender Python, an import patch, extension compilation, or a different official invocation path.
