# Asset Registry V3 Gate - 2026-05-13

## Purpose

This is the first machine-checkable Route F registry/material gate. It is a standalone validator and does not touch runtime gameplay code yet.

The gate protects the rebuild from false completion claims by failing `required_for_final=true` assets when they are still placeholders, missing provenance, or missing required PBR texture maps.

## Validator

```bash
python3 tools/validate_asset_registry_v3.py <registry.json>
```

Optional assets root:

```bash
python3 tools/validate_asset_registry_v3.py <registry.json> \
  --assets-root experiments/pubg_like_asset_factory_20260513/assets
```

The default `--assets-root` is:

```text
experiments/pubg_like_asset_factory_20260513/assets
```

The validator emits a JSON report to stdout. It exits `0` when there are no errors and nonzero when errors are present.

## Registry Shape

The accepted registry shape is intentionally simple:

```json
{
  "assets": [
    {
      "asset_id": "hero_rifle_v1",
      "required_for_final": true,
      "model": {
        "optimized_glb": "model/optimized.glb",
        "raw_glb": "model/raw.glb"
      },
      "provenance": {
        "reference": "source/reference.md"
      },
      "materials": {
        "material_map_count": 3,
        "required_material_map_count": 3,
        "required_texture_keys": ["basecolor", "normal", "roughness"],
        "textures": {
          "basecolor": "textures/hero_rifle_basecolor.png",
          "normal": "textures/hero_rifle_normal.png",
          "roughness": "textures/hero_rifle_roughness.png"
        }
      }
    }
  ]
}
```

For path fields, relative paths are resolved as:

```text
<assets-root>/<asset_id>/<path>
```

If a path already begins with `<asset_id>/`, it is resolved as:

```text
<assets-root>/<path>
```

Absolute paths are also accepted.

## Enforced Gates

For every asset where `required_for_final` is exactly `true`, the validator enforces:

- `model.optimized_glb` or `model.raw_glb` exists on disk.
- A non-empty `provenance`, `reference`, or `reference_sha256` field exists.
- `material_map_count` is an integer and is greater than or equal to `required_material_map_count`.
- Every key in `required_texture_keys` exists under `materials.textures` or top-level `textures`, and each referenced file exists on disk.

Defaults:

- `required_material_map_count`: `3`
- `required_texture_keys`: `["basecolor", "normal", "roughness"]`

## Probe Registry

Probe file:

```text
experiments/pubg_like_asset_factory_20260513/asset_registry_v3_probe.json
```

It includes:

- `tactical_crate_trellis_texturealchemy_v1` as `probe_only=true` and `required_for_final=false`. This row records the current TextureAlchemy evidence without claiming final production readiness.
- `hero_rifle_v1` as `required_for_final=true` with intentionally incomplete local files and missing provenance. This row is supposed to fail.

The expected failing probe result is useful: it proves the registry gate blocks final hero assets from silently passing when they still have no GLB, no provenance, too few material maps, or missing required texture files. This is a protection against false completion, not a validator defect.
