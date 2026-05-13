# Asset Registry V2 001 Report

## Result

Created the first asset-packet schema, registry v2 seed, validator, and tests for the tactical visual-upgrade experiment.

## Important Semantics

- `baseline_only` entries may pass with `material_map_count: 0` only when they carry explicit blockers.
- `target` entries may describe planned paths that do not exist yet, again only with blockers.
- `production_ready` entries must not carry blockers and must satisfy the stricter gates.
- Production weapons require at least four material maps and anchors: `Muzzle`, `Grip_R`, `Grip_L`, `Optic`, `PickupRoot`.
- Production characters require rig/mixer/clip readiness and core character anchors.

## Verification

```bash
./.venv/bin/python -m pytest tests/test_validate_asset_registry_v2.py
./.venv/bin/python tools/validate_asset_registry_v2.py experiments/tactical_game_visual_upgrade_20260520/assets/asset_registry_v2.json
```

Result:

- `7 passed in 0.07s`
- `validated 5 asset registry v2 entries in experiments/tactical_game_visual_upgrade_20260520/assets/asset_registry_v2.json`

Note: `/usr/bin/python3` on this machine does not currently have `pytest` or `jsonschema`; worker verification should use the repo `.venv`.

## Runner Note

Kimi worker produced the initial schema, then stalled without completing the registry, validator, tests, or report. Codex retained the schema, tightened `model_sha256` handling for planned target assets, and completed the rest locally.
