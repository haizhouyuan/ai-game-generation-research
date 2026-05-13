# Worker Task 010 - Registry V3 Fail-Closed Gate

## Goal

Tighten the registry v3 validator so the full PUBG-like rebuild cannot be falsely marked complete through empty scaffold packets or loose registry claims.

## Context

The user clarified that this is a complete local AI 3D asset factory rebuild, not a light visual upgrade. Final assets must be real production packets with route/provenance, models or PBR outputs, texture maps where required, and runtime evidence.

## Read

- `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
- `tasks/pubg_like_full_rebuild/README.md`
- `tools/validate_asset_packets.py`
- `tools/validate_asset_registry_v3.py`
- `schemas/asset_registry_v3.schema.json`
- `experiments/pubg_like_asset_factory_20260513/asset_registry_v3_probe.json`

## Write Scope

- `tools/validate_asset_registry_v3.py`
- `docs/asset_registry_v3_gate_2026-05-13.md`

Do not edit other files.

## Required Changes

1. Add an explicit final-manifest mode to `validate_asset_registry_v3.py`:
   - CLI flag name: `--production-goal`
   - It must require the 12 minimum production asset IDs used by `tools/validate_asset_packets.py`:
     `hero_rifle_v1`, `sidearm_v1`, `secondary_weapon_v1`, `player_tactical_v1`, `enemy_tactical_v1`, `gear_set_v1`, `wet_asphalt_material_v1`, `concrete_wall_material_v1`, `container_checkpoint_v1`, `loot_set_v1`, `clutter_decals_v1`, `rainy_checkpoint_scene_v1`.
   - It must fail if any required final asset is missing from registry.
   - It must fail if any required final asset is `probe_only`, `baseline_only`, `blocked`, `target`, or `in_progress`.
   - It must fail if any required final asset is not `required_for_final=true`.
2. Keep the current default behavior intact for probe/development validation.
3. Do not introduce third-party dependencies.
4. Update `docs/asset_registry_v3_gate_2026-05-13.md` to document the new mode and the expected current failure state.

## Verification

Run:

```bash
python3 -m py_compile tools/validate_asset_registry_v3.py
python3 tools/validate_asset_registry_v3.py experiments/pubg_like_asset_factory_20260513/asset_registry_v3_probe.json >/tmp/registry_default.json || test $? -eq 1
python3 tools/validate_asset_registry_v3.py --production-goal experiments/pubg_like_asset_factory_20260513/asset_registry_v3_probe.json >/tmp/registry_production.json || test $? -eq 1
python3 -m json.tool /tmp/registry_production.json >/tmp/registry_production.pretty.json
```

The production goal mode is expected to fail on the current probe registry.

## Output Summary

Return:

- status
- changed files
- commands run
- expected current failures
- risks or follow-up gates
