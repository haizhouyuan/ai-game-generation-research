# Tactical Rifle TRELLIS Candidate Report - 2026-05-13

## Purpose

This experiment generated image-to-3D rifle/GROZA candidates for the tactical compound game goal without starting any new large model downloads.

Input reference:

- `inputs/groza_reference.png`
- SHA256: `af030610a93ccf8d809817979edeb403f4c2aab9c84ed0dd07ce2bda49286d5f`
- Source: local Blender render from `experiments/tactical_rifle_realism_20260513/groza_procedural/preview.png`

## Generation Route

Remote host: `homepc`

Validated caches before generation:

- `/home/yuanhaizhou/TRELLIS`
- `/home/yuanhaizhou/TRELLIS-models/TRELLIS-image-large`
- `~/.cache/torch/hub/facebookresearch_dinov2_main`

Command shape:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY="*" no_proxy="*" \
  python /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p26_trellis_asset_validation_20260512/trellis_meshonly_generate.py \
  inputs/groza_reference.png \
  outputs/groza_trellis_seed_<seed>.glb \
  --gpu 1 --seed <seed> --simplify 0.95
```

Seeds: `42`, `101`, `202`.

The logs show loading from `/home/yuanhaizhou/TRELLIS-models/TRELLIS-image-large` and cached DINOv2 paths. No external model download was needed in this run.

## Candidate Summary

Raw TRELLIS parse:

- seed 42: `188,932` bytes, `1` mesh, `9,406` triangles, no UV/material textures.
- seed 101: `176,416` bytes, `1` mesh, `8,780` triangles, no UV/material textures.
- seed 202: `174,356` bytes, `1` mesh, `8,670` triangles, no UV/material textures.

Blender cleanup added a bbox proxy, normalized scale, and preview renders:

- `blender_seed_42/groza_trellis_seed_42_cleaned.glb`
- `blender_seed_101/groza_trellis_seed_101_cleaned.glb`
- `blender_seed_202/groza_trellis_seed_202_cleaned.glb`

Visual read:

- seed 42 produced the least useful weapon shape.
- seed 101 and seed 202 better preserve the weapon silhouette.
- seed 202 is the strongest TRELLIS candidate, but still mesh-only and untextured.

## Decision

The selected in-game hero asset for this pass is **not** a TRELLIS mesh. It is the local Blender procedural GROZA candidate:

- `experiments/tactical_rifle_realism_20260513/groza_procedural/groza_procedural_candidate.glb`

Reason:

- stronger readable rifle silhouette;
- material separation already present;
- explicit muzzle/grip/sight anchors;
- materially better for current game integration than mesh-only TRELLIS outputs.

The TRELLIS outputs are retained as proof that the image-to-3D route works with cached models and no new large download.

## Evidence

- Hash manifest: `artifact_hashes.json`
- Raw parse: `outputs/three_glb_parse_inventory.json`
- Blender reports/renders: `blender_seed_*/`
- Generation logs: `logs/groza_trellis_seed_*.log`

## Limitations

- TRELLIS outputs are mesh-only; they do not include useful PBR textures.
- Shape quality is not yet good enough to replace the selected procedural GROZA candidate.
- A future final-quality route should use a better orthographic/multi-view rifle reference, Hunyuan3D/PBR-capable generation, or manual Blender hard-surface refinement.
