# Task: Route C/D Probe Review 007

## Goal

Review the first local mesh + PBR probe chain for the full PUBG-like asset
factory goal. Be strict: this is not final production quality.

## Context

Route D produced a TRELLIS mesh-only tactical crate prop.
Route C installed TextureAlchemy and produced a minimal PBR map set from the
crate reference image.
The combined packet is:

```text
experiments/pubg_like_asset_factory_20260513/assets/tactical_crate_trellis_texturealchemy_v1/
```

## Read-Only Files

- `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
- `tasks/pubg_like_full_rebuild/README.md`
- `experiments/pubg_like_asset_factory_20260513/routes/route_c_comfyui_pbr_probe_004/summary.md`
- `experiments/pubg_like_asset_factory_20260513/routes/route_d_trellis_prop_probe_005/summary.md`
- `experiments/pubg_like_asset_factory_20260513/assets/tactical_crate_trellis_texturealchemy_v1/source/reference.md`
- `experiments/pubg_like_asset_factory_20260513/assets/tactical_crate_trellis_texturealchemy_v1/reports/material_report.json`
- `experiments/pubg_like_asset_factory_20260513/assets/tactical_crate_trellis_texturealchemy_v1/reports/blender_import_report.json`
- `tools/validate_asset_packets.py`

## Questions

1. Does this packet legitimately count as a first probe-only mesh + PBR chain?
2. What are the top 5 missing steps before it could be a production background prop?
3. Is TextureAlchemy direct node-class invocation acceptable as a Route C proof, or must the next probe run through ComfyUI API/UI workflow execution?
4. Should this route be promoted for crate/container props, or treated only as diagnostic?
5. What exact next task should Codex delegate to Kimi/HomePC/Blender?

## Output Format

```markdown
# Route C/D Probe Review 007

## Verdict
valid_probe | weak_probe | invalid

## Top Gaps
- ...

## Promotion Advice
- ...

## Next Delegated Task
- runner:
- task:
- acceptance:
```
