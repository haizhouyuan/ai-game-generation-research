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

## Modes

### Default (probe/development) mode

Validates individual assets and warns about incomplete entries. This is the default behavior when `--production-goal` is not passed.

### Production-goal mode (`--production-goal`)

Fail-closed validation that enforces the full PUBG-like rebuild cannot be marked complete through empty scaffold packets or loose registry claims.

```bash
python3 tools/validate_asset_registry_v3.py --production-goal <registry.json>
```

When `--production-goal` is passed, the validator enforces the following on top of default checks:

1. **All 12 minimum production assets must be present.** The registry must contain every asset ID from the minimum production set:
   - `hero_rifle_v1`
   - `sidearm_v1`
   - `secondary_weapon_v1`
   - `player_tactical_v1`
   - `enemy_tactical_v1`
   - `gear_set_v1`
   - `wet_asphalt_material_v1`
   - `concrete_wall_material_v1`
   - `container_checkpoint_v1`
   - `loot_set_v1`
   - `clutter_decals_v1`
   - `rainy_checkpoint_scene_v1`

   Missing any of these produces error code `missing_required_production_asset`.

2. **Each required asset must have `required_for_final=true`.** Any required production asset that is not explicitly marked `required_for_final=true` produces error code `required_asset_not_required_for_final`.

3. **Each required asset must not be `probe_only`.** Any required production asset marked `probe_only=true` produces error code `required_asset_is_probe_only`.

4. **Each required asset must have an acceptable status.** Forbidden statuses for production assets: `baseline_only`, `blocked`, `target`, `in_progress`. Only `production_ready` (and schema-permitted `rejected`) are acceptable. Any forbidden status produces error code `required_asset_has_forbidden_status`.

5. **Standard required-for-final material gates still apply.** Assets that pass the production-goal checks above are still subject to the existing gates: model GLB must exist on disk, provenance/reference must be present, material map count must meet threshold, and required texture files must exist on disk.

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

## Enforced Gates (Default Mode)

For every asset where `required_for_final` is exactly `true`, the validator enforces:

- `model.optimized_glb` or `model.raw_glb` exists on disk.
- A non-empty `provenance`, `reference`, or `reference_sha256` field exists.
- `material_map_count` is an integer and is greater than or equal to `required_material_map_count`.
- Every key in `required_texture_keys` exists under `materials.textures` or top-level `textures`, and each referenced file exists on disk.

Defaults:

- `required_material_map_count`: `3`
- `required_texture_keys`: `["basecolor", "normal", "roughness"]`

## Expected Current Failure State

As of 2026-05-13, running `--production-goal` against `experiments/pubg_like_asset_factory_20260513/asset_registry_v3_probe.json` is expected to fail with:

- **11 missing required assets** — only `hero_rifle_v1` is present; the other 11 are absent from the probe registry.
- **`hero_rifle_v1` has forbidden status `target`** — it is not yet `production_ready`.
- **`hero_rifle_v1` fails material gates** — `material_map_count` is 0 (below required 3), and texture files do not exist on disk.

This confirms the gate is fail-closed: the rebuild cannot be falsely claimed complete.

## Probe Registry

Probe file:

```text
experiments/pubg_like_asset_factory_20260513/asset_registry_v3_probe.json
```

It includes:

- `tactical_crate_trellis_texturealchemy_v1` as `probe_only=true` and `required_for_final=false`. This row records the current TextureAlchemy evidence without claiming final production readiness.
- `hero_rifle_v1` as `required_for_final=true` with intentionally incomplete local files and missing provenance. This row is supposed to fail.

The expected failing probe result is useful: it proves the registry gate blocks final hero assets from silently passing when they still have no GLB, no provenance, too few material maps, or missing required texture files. This is a protection against false completion, not a validator defect.

## Exit Codes

| Exit code | Meaning |
|-----------|---------|
| 0 | Registry is valid (no errors) |
| 1 | One or more errors detected |

## Related Tools

- `tools/validate_asset_packets.py` — scans actual asset packet directories on disk for folders, texture maps, models, and evidence media. Use alongside this registry validator for complete coverage.
