# Task: Route C ComfyUI PBR Probe 004

## Goal

Run a practical ComfyUI-based 3D/PBR route probe for the PUBG-like full rebuild. This is not a final asset completion task. It must prove, with evidence, whether ComfyUI can generate or improve one tactical asset through texture projection, multi-view texture generation, PBR map completion, or an equivalent local workflow.

The minimum useful outcome is one exported asset candidate or texture map set plus a blocker report that is concrete enough for Kimi/Codex to act on.

## Host / Runner Recommendation

- Primary host: HomePC GPU1.
- Primary executor: HomePC GPU worker.
- Hard dependency/debug review: Kimi.
- Visual/workflow strategy review: Gemini CLI with `gemini-3.1-pro-preview`.
- MiniMax: only for mechanical formatting of install inventory, hash manifest, or report tables after evidence exists.

## Read-Only Files

- `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
- `tasks/pubg_like_full_rebuild/README.md`
- `tasks/pubg_like_full_rebuild/full_rebuild_parallelization_review_002.gemini_review.txt`
- `tasks/pubg_like_full_rebuild/full_rebuild_parallelization_review_002.kimi_review.txt`
- `experiments/pubg_like_asset_factory_20260513/assets/hunyuan_shape_demo_001/` if present, only as a known shape-only baseline.
- Existing reference or asset packet directories under `experiments/pubg_like_asset_factory_20260513/`, read-only unless listed in write scope.

## Write Scope

Write only under a new Route C probe directory, unless the controller explicitly assigns a different target:

- `experiments/pubg_like_asset_factory_20260513/routes/route_c_comfyui_pbr_probe_004/`

Expected subpaths:

- `install/custom_node_inventory.md`
- `install/env_report.md`
- `workflows/*.json`
- `inputs/`
- `outputs/`
- `textures/`
- `reports/blocker_report.md`
- `reports/material_report.json`
- `reports/download_evidence.md`
- `evidence/*.png`
- `summary.md`

## Forbidden Paths

- Do not edit game runtime files.
- Do not edit `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`.
- Do not edit `tasks/pubg_like_full_rebuild/README.md`.
- Do not edit Hunyuan working envs: `hy3d21` or `hy3d21paint`.
- Do not overwrite `experiments/pubg_like_asset_factory_20260513/assets/hunyuan_shape_demo_001/`.
- Do not change global proxy, Clash, Homebrew, shell profile, SSH, or system network settings.
- Do not download a single file over 100MB through proxy env vars.

## Candidate Scope

Use one small tactical asset candidate:

- preferred: `loot_set_v1/medkit` or `loot_set_v1/ammo_box`;
- alternate: `gear_set_v1/tactical_pouch`;
- avoid hero rifle and characters in this probe unless explicitly reassigned.

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

Create isolated workspace:

```bash
mkdir -p /home/yuanhaizhou/ai_game_asset_factory/route_c_comfyui_pbr_probe_004
cd /home/yuanhaizhou/ai_game_asset_factory/route_c_comfyui_pbr_probe_004
```

Install or locate ComfyUI in an isolated env. Do not disturb Hunyuan envs:

```bash
# Placeholder. Use the existing local ComfyUI checkout if present.
# If cloning/downloading, record URL, revision, size, and proxy-unset evidence.
git clone <COMFYUI_REPO_URL> ComfyUI
cd ComfyUI
git rev-parse HEAD
```

For any single external download over 100MB, use command-local no-proxy settings and save evidence:

```bash
env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl --noproxy '*' -L --fail --continue-at - --output <OUTPUT_PATH> <URL>
sha256sum <OUTPUT_PATH>
```

Inventory custom nodes:

```bash
find custom_nodes -maxdepth 2 -type d | sort
python - <<'PY'
import sys, torch
print("python", sys.version)
print("torch", torch.__version__)
print("cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
PY
```

Run one workflow:

```bash
# Placeholder: use the ComfyUI CLI/API command that matches the installed build.
# Save the exact workflow JSON under workflows/.
python main.py --listen 127.0.0.1 --port <PORT>
python <COMFYUI_WORKFLOW_RUNNER>.py --workflow workflows/<WORKFLOW>.json --output outputs/
```

If ComfyUI cannot run headlessly, record the UI steps, exact workflow JSON, screenshot, and output paths.

## Expected Artifacts

- Custom node inventory with git revisions or installed package versions.
- Workflow JSON for the attempted texture/PBR route.
- One generated or retouched asset output:
  - GLB/OBJ, or
  - texture map set with at least basecolor, normal, roughness, and metallic or AO, or
  - a clear blocker report if dependency conflicts prevent generation.
- Material report listing texture maps and image dimensions.
- Screenshot evidence of the workflow output or preview.
- Download evidence for all large files, including no-proxy command proof.

## Acceptance Gate

Pass if all are true:

- The probe is isolated from Hunyuan shape/paint envs.
- At least one ComfyUI workflow JSON is saved.
- Custom node inventory is saved.
- One tactical asset candidate or PBR texture set is generated/retouched, or a concrete dependency blocker is documented with exact failing command and traceback.
- PBR practicality is judged explicitly: `promising`, `usable_with_cleanup`, `blocked`, or `not_suitable`.
- No large download lacks no-proxy evidence.

Fail if any are true:

- The output is only a vague research note.
- The route uses only flat material factors and no texture/PBR map attempt.
- The worker edits runtime/game files.
- The worker silently uses old procedural assets as proof of Route C.

## Output Summary Format

Write `summary.md` with:

````markdown
# Route C ComfyUI PBR Probe 004 Summary

## Verdict
promising | usable_with_cleanup | blocked | not_suitable

## Host And Runner
- Host:
- Runner:
- GPU:

## Commands Run
```bash
<exact commands>
```

## Custom Nodes / Versions
- ...

## Workflow JSON
- `workflows/...json`

## Generated Outputs
- `outputs/...`
- `textures/...`

## PBR Map Count
- basecolor:
- normal:
- roughness:
- metallic:
- ao:

## Evidence
- `evidence/...png`
- `reports/material_report.json`

## Blockers / Next Action
- ...
````
