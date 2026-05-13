# Tactical Crate TRELLIS + TextureAlchemy Reference

## Status

`probe_only`

This packet exists to prove a local generated-geometry plus PBR-map chain. It is
not a final PUBG-like asset.

## Source Chain

1. Reference image: `source/tactical_crate_reference.png`
2. Mesh route: cached local TRELLIS image-to-3D mesh-only generation
3. Texture route: ComfyUI TextureAlchemy minimal PBR map production
4. DCC evidence: Blender import preview through HomePC `xvfb-run`

## Provenance

The reference image was copied from the prior local TRELLIS crate validation
experiment:

```text
/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p26_trellis_asset_validation_20260512/inputs/typical_misc_crate.png
```

The mesh was generated in:

```text
experiments/pubg_like_asset_factory_20260513/routes/route_d_trellis_prop_probe_005/
```

The PBR maps were generated in:

```text
experiments/pubg_like_asset_factory_20260513/routes/route_c_comfyui_pbr_probe_004/
```

## Completion Caveat

The asset has real generated geometry and named PBR map files, but the texture
maps are heuristic single-image maps. Final production use still requires UV
inspection, material-zone separation, better texture projection or Hunyuan Paint
output, optimization/LOD, collision proxy, and Three.js gameplay evidence.
