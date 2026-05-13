# Task: Route D TRELLIS Prop Probe 005

## Goal

Run the current cached TRELLIS or TRELLIS.2 route on one non-rifle tactical prop or gear item. The purpose is to move Route D from "known to exist" into concrete asset evidence: a mesh candidate, an import/preview, and a suitability judgment for the PUBG-like rebuild.

This is a probe, not final production completion. It must also attempt or specify the next texture/PBR improvement route through ComfyUI or Blender.

## Host / Runner Recommendation

- Primary host: HomePC GPU1.
- Primary executor: HomePC GPU worker.
- Blocker/debug owner: Kimi.
- Visual suitability reviewer: Gemini CLI with `gemini-3.1-pro-preview`.
- MiniMax: only for hash manifest or report reformatting after outputs exist.

## Read-Only Files

- `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
- `tasks/pubg_like_full_rebuild/README.md`
- `tasks/pubg_like_full_rebuild/full_rebuild_parallelization_review_002.gemini_review.txt`
- `tasks/pubg_like_full_rebuild/full_rebuild_parallelization_review_002.kimi_review.txt`
- Current TRELLIS checkout/cache/model dirs on HomePC.
- Existing reference images or asset packet scaffolds under `experiments/pubg_like_asset_factory_20260513/`, read-only unless listed in write scope.

## Write Scope

Write only under:

- `experiments/pubg_like_asset_factory_20260513/routes/route_d_trellis_prop_probe_005/`

Expected subpaths:

- `inputs/`
- `outputs/raw/`
- `outputs/converted/`
- `reports/env_report.md`
- `reports/run_report.md`
- `reports/material_or_texture_plan.md`
- `reports/download_evidence.md`
- `evidence/trellis_preview.png`
- `evidence/blender_import.png`
- `summary.md`

If the generated prop is promoted later, Codex will copy or merge it into an official asset packet. Do not promote it yourself.

## Forbidden Paths

- Do not edit runtime/game code.
- Do not edit Route C outputs.
- Do not edit Hunyuan envs or Hunyuan output packets.
- Do not overwrite official asset packet slots such as `assets/loot_set_v1/` or `assets/gear_set_v1/`.
- Do not change global proxy, Clash, shell profile, Homebrew, SSH, or system network settings.
- Do not download a single file over 100MB without command-local no-proxy evidence.
- Do not use hero rifle as the probe target; Route D must test a non-rifle prop or gear item first.

## Candidate Scope

Choose exactly one:

- preferred: medkit;
- preferred: ammo box;
- alternate: tactical pouch;
- alternate: helmet accessory or loose magazine.

Use a realistic reference image if already available. If no suitable reference exists, use a text prompt and record it clearly, but mark the reference-chain gap.

## Concrete Commands / Placeholders

Record exact commands actually run. Replace placeholders before execution.

Preflight:

```bash
date -Is
hostname
nvidia-smi
df -h
env | grep -i proxy || true
```

Locate TRELLIS:

```bash
find /home/yuanhaizhou -maxdepth 5 -iname '*trellis*' -type d 2>/dev/null | sort
cd <TRELLIS_CHECKOUT>
git rev-parse HEAD || true
```

Check env:

```bash
python - <<'PY'
import sys
print("python", sys.version)
try:
    import torch
    print("torch", torch.__version__)
    print("cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
except Exception as exc:
    print("torch import failed:", repr(exc))
PY
```

Run TRELLIS on one prop. Use the repo's actual inference command:

```bash
# Placeholder. Replace with the real cached TRELLIS command.
python <TRELLIS_INFER_SCRIPT>.py \
  --input <REFERENCE_IMAGE_OR_PROMPT_FILE> \
  --output /home/yuanhaizhou/ai_game_asset_factory/route_d_trellis_prop_probe_005/outputs/raw \
  --seed <SEED>
```

Convert if needed:

```bash
# Placeholder. Use Blender or repo converter if output is not already GLB/OBJ.
blender --background --python <CONVERT_OR_IMPORT_SCRIPT>.py -- \
  --input outputs/raw/<OUTPUT> \
  --output outputs/converted/<PROP_ID>.glb
```

For any single external download over 100MB:

```bash
env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl --noproxy '*' -L --fail --continue-at - --output <OUTPUT_PATH> <URL>
sha256sum <OUTPUT_PATH>
```

## Expected Artifacts

- Env report with TRELLIS path, git revision if available, Python, PyTorch, CUDA, GPU, and model/cache paths.
- Input reference image or prompt file.
- Raw TRELLIS output.
- Converted GLB/OBJ if conversion is possible.
- Blender import screenshot or exact import failure.
- Basic mesh facts: file size, vertices/faces/triangles if available.
- Texture/PBR improvement plan:
  - route through ComfyUI texture projection/PBR completion, or
  - Blender material/UV cleanup plan, or
  - concrete reason texture improvement is blocked.

## Acceptance Gate

Pass if all are true:

- One non-rifle tactical prop or gear item is attempted with exact command evidence.
- Raw output is saved, or a concrete failure with traceback/log is saved.
- Blender import is attempted and screenshot or import error is saved.
- Suitability is judged explicitly for final production use: `suitable_after_cleanup`, `background_only`, `blocked`, or `not_suitable`.
- Texture/PBR next step is specified and linked to Route C or Blender cleanup.
- No large download lacks no-proxy evidence.

Fail if any are true:

- The output only says TRELLIS is installed/cached.
- The worker uses a rifle/hero asset despite this packet targeting props.
- No Blender import or equivalent mesh inspection is attempted.
- The report claims completion without a texture/PBR improvement path.

## Output Summary Format

Write `summary.md` with:

````markdown
# Route D TRELLIS Prop Probe 005 Summary

## Verdict
suitable_after_cleanup | background_only | blocked | not_suitable

## Host And Runner
- Host:
- Runner:
- GPU:

## Target Prop
- Asset candidate:
- Reference image or prompt:
- Reference SHA256 if available:

## Commands Run
```bash
<exact commands>
```

## Outputs
- Raw:
- Converted:
- Blender evidence:

## Mesh Facts
- File size:
- Vertices:
- Triangles:
- Materials:
- Texture maps:

## Texture / PBR Next Step
- Route C:
- Blender cleanup:
- Blocker:

## Production Suitability Notes
- ...
````
