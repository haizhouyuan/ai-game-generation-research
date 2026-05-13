# GLB Playable Validator Template

## Purpose

Use this template when a worker must prove that a `.glb` asset can be loaded, inspected, rendered, and, when relevant, exercised inside a lightweight playable scene.

This capability is a validator and preview path. It does not make Three.js the final game route. It is used because GLB parser/readback, screenshots, and browser smoke evidence are the fastest way to prove whether an asset is usable before Unity import.

## Inputs

Fill these fields before running the task:

| Field | Value |
|---|---|
| `task_id` | `<managed task id>` |
| `lane_id` | `threejs-playable-runtime` or `asset-generation` |
| `repo_id` | `ai-game-generation-research` |
| `asset_id` | `<stable asset id, for example RW-ROVER-001>` |
| `glb_path` | `<relative path to GLB>` |
| `asset_role` | `<player_avatar, prop, hazard, pickup, environment, other>` |
| `expected_bbox` | `<expected size range, if known>` |
| `expected_materials` | `<mesh-only, vertex-color, PBR, textured, unknown>` |
| `preview_scene` | `<path to validator scene or placeholder command>` |
| `out_dir` | `<immutable evidence directory>` |
| `provenance_path` | `<asset provenance packet path, if available>` |

Required preconditions:

- The GLB exists locally before the validator starts.
- Any external dependency needed to run validation has an existing local install or is acquired through the no-proxy governed download template.
- Generated meshes are not trusted as gameplay collision. Use or request a collider proxy.

## Commands / Placeholders

Use the repo's actual validator command when available. Until a dedicated tool exists, record the exact command shape used by the worker.

```bash
# Preflight
test -f "<glb_path>"
du -h "<glb_path>"
shasum -a 256 "<glb_path>"

# Parser/readback placeholder
<node_or_python_glb_parser> \
  --input "<glb_path>" \
  --out "<out_dir>/glb_readback.json"

# Three.js preview placeholder
<threejs_preview_runner> \
  --glb "<glb_path>" \
  --out "<out_dir>" \
  --screenshot "<out_dir>/screenshots/glb_preview.png" \
  --server-bind 127.0.0.1 \
  --timeout-ms 30000

# Hash all produced evidence
find "<out_dir>" -type f -print0 | xargs -0 shasum -a 256 > "<out_dir>/artifact_hashes.txt"
```

If the parser or preview runner does not exist yet, do not invent a pass. Record a blocker and return `status: "blocked"` or `status: "partial"` in `WORKER_RESULT`.

## Required Evidence

The evidence directory must contain:

- `glb_readback.json` with node inventory, mesh count, material count, texture count, animation count, bounds, scale, and warnings.
- `screenshots/glb_preview.png` or a failure screenshot.
- `artifact_hashes.txt` or `artifact_hashes.json` covering the GLB and all validator outputs.
- Console/browser log or parser log.
- Link to the asset provenance packet when the GLB is generated or non-procedural.
- Explicit statement of whether textures/materials were present, absent, or not inspectable.
- Explicit statement that collision quality is unproven unless a collider proxy was separately validated.

Pass criteria:

- GLB parser succeeds.
- Asset has visible geometry.
- Bounds are finite and within the expected range, or the deviation is documented.
- Preview screenshot is nonblank and shows the asset under useful lighting.
- Material/texture status is explicit.
- Hashes cover all artifacts.

## Failure Modes

Record these as blockers or risks:

- `glb_missing`: input path does not exist.
- `parser_missing`: no local GLB parser or validator command is available.
- `parser_failed`: GLB cannot be parsed by the selected loader.
- `blank_preview`: screenshot is blank, one-color, or asset is invisible.
- `off_origin_or_scale_bad`: asset is too large, too small, inverted, or far from origin.
- `texture_claim_unproven`: worker claims textured/PBR quality without material and texture readback.
- `collider_claim_unproven`: worker uses generated mesh as gameplay collision without proxy validation.
- `dependency_or_download_blocked`: validation requires a package/model download that violates policy or lacks approval.
- `evidence_incomplete`: missing screenshot, hash, parser log, or provenance link.

## WORKER_RESULT Expectations

Return schema-valid `WORKER_RESULT` using `schemas/worker_result.schema.json`.

Use `status: "done"` only when parser/readback, screenshot, hash, and material/texture status evidence are complete.

Use `status: "partial"` when parser/readback passes but preview, screenshot, gameplay exercise, or provenance is incomplete.

Use `status: "blocked"` when a missing local tool, missing asset, download boundary, or corrupt GLB prevents validation.

Required `evidence` entries:

```json
[
  {"type": "asset", "path_or_url": "<glb_path>", "notes": "Validated GLB input"},
  {"type": "test", "path_or_url": "<out_dir>/glb_readback.json", "notes": "GLB parser/readback report"},
  {"type": "screenshot", "path_or_url": "<out_dir>/screenshots/glb_preview.png", "notes": "Three.js preview or failure screenshot"},
  {"type": "hash", "path_or_url": "<out_dir>/artifact_hashes.txt", "notes": "Artifact hashes"},
  {"type": "doc", "path_or_url": "<provenance_path>", "notes": "Asset provenance packet"}
]
```

Recommended `next_action`:

- `review` when validation passes but a human should inspect asset quality.
- `queue_next_turn` when the next automated step is Blender cleanup, Unity import, or playable integration.
- `wait_for_human` when a download over 1GB, Unity account/license step, or external asset rights decision is required.
- `stop` when the asset is invalid and should be rejected.
