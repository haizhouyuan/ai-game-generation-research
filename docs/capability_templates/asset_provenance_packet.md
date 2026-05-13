# Asset Provenance Packet Template

## Purpose

Use this template for every non-procedural or AI-assisted game asset: image references, generated GLBs, cleaned GLBs, textures, icons, material sheets, audio, and external source assets.

The packet answers: where did this asset come from, what tools touched it, what files were produced, what rights or limits apply, and what validation proves it can be used.

## Inputs

Fill these fields before asset work begins:

| Field | Value |
|---|---|
| `task_id` | `<managed task id>` |
| `lane_id` | `asset-generation`, `blender-authoring`, or `threejs-playable-runtime` |
| `repo_id` | `ai-game-generation-research` |
| `asset_id` | `<stable id, for example RW-ROVER-001>` |
| `asset_name` | `<human name>` |
| `asset_role` | `<player_avatar, pickup, hazard, finish, prop, texture, icon, other>` |
| `source_kind` | `<openai_image, procedural, trellis, triposr, hunyuan3d, blender, external_source>` |
| `prompt_path` | `<path to prompt or prompt registry>` |
| `reference_image_path` | `<path, if any>` |
| `raw_output_paths` | `<generated or downloaded outputs>` |
| `cleaned_output_paths` | `<postprocessed outputs, if any>` |
| `host` | `<Mac, HomePC, YogaS2, other>` |
| `tool_versions` | `<model/tool/runtime versions>` |
| `out_dir` | `<immutable packet directory>` |

Required preconditions:

- Prompts and source references must be saved before claiming an asset is reproducible.
- Any downloaded file must include no-proxy evidence or an explicit statement that no download occurred.
- Any generated 3D asset must pass a parser/readback validator before it can be called usable.

## Commands / Placeholders

Use exact commands for the asset step that actually happened.

```bash
# Hash source references and outputs
shasum -a 256 "<reference_image_path>"
shasum -a 256 "<raw_or_cleaned_asset_path>"

# Mesh statistics placeholder
<mesh_stats_tool> \
  --input "<glb_or_mesh_path>" \
  --out "<out_dir>/mesh_stats.json"

# Material/texture inspection placeholder
<material_inspection_tool> \
  --input "<asset_path>" \
  --out "<out_dir>/material_report.json"

# Blender cleanup placeholder, if used
<blender_cleanup_command> \
  --input "<raw_glb_path>" \
  --output "<cleaned_glb_path>" \
  --report "<out_dir>/blender_cleanup_report.md"

# Three.js validation placeholder, if used
<glb_playable_validator_command> \
  --input "<cleaned_or_raw_glb_path>" \
  --out "<out_dir>/threejs_validation"
```

Create a machine-readable packet at:

```text
<out_dir>/asset_provenance.json
```

Minimum shape:

```json
{
  "schema_version": "asset_provenance.v1",
  "asset_id": "<asset_id>",
  "asset_name": "<asset_name>",
  "asset_role": "<asset_role>",
  "status": "reference|candidate|cleaned|validated|rejected",
  "source": {
    "kind": "<source_kind>",
    "prompt_path": "<prompt_path>",
    "reference_image_path": "<reference_image_path>",
    "model_or_tool": "<model_or_tool>",
    "tool_version": "<tool_version>",
    "host": "<host>"
  },
  "files": [],
  "validation": {},
  "license_and_rights": {},
  "limitations": []
}
```

## Required Evidence

The packet must include:

- Prompt text or prompt file path.
- Reference image path and SHA256 when an image is used.
- Tool/model names and versions where available.
- Host used for generation or cleanup.
- Exact commands or notebook/script paths.
- Raw output paths and SHA256.
- Cleaned output paths and SHA256, if cleanup occurred.
- Mesh stats for 3D assets: bounds, vertex/face count when available, material count, texture count, animation count.
- Material/texture report, even when the answer is "mesh-only" or "no textures".
- Validation links: GLB parser/readback, screenshot, Blender inspection, Unity import, or gameplay test, as appropriate.
- Rights/license notes for external or third-party sources.
- Known limitations and forbidden claims.

Pass criteria:

- The packet can be reviewed without reading chat history.
- All referenced local paths exist at completion time or are explicitly marked missing with a blocker.
- Generated assets are not promoted beyond their evidence level.
- Mesh-only, untextured, unrigged, or no-collider states are stated plainly.

## Failure Modes

Record these as blockers or risks:

- `missing_prompt_or_reference`: source prompt/reference cannot be found.
- `missing_hash`: source or output file lacks SHA256 evidence.
- `unknown_tool_version`: model/tool version is unavailable and not documented.
- `download_unproven`: downloaded source lacks no-proxy/hash evidence.
- `rights_unknown`: external source rights are not documented.
- `asset_path_missing`: packet references a file that does not exist.
- `validation_missing`: GLB/image/texture is not validated but is being promoted.
- `texture_or_material_overclaim`: packet says textured/PBR without inspection evidence.
- `collision_overclaim`: generated mesh is treated as gameplay collision without proxy validation.

## WORKER_RESULT Expectations

Return schema-valid `WORKER_RESULT` using `schemas/worker_result.schema.json`.

Use `status: "done"` only when `asset_provenance.json`, hashes, and the relevant validation evidence exist.

Use `status: "partial"` when the packet exists but validation, cleanup, or rights evidence remains incomplete.

Use `status: "blocked"` or `needs_human: true` when an approval, license, account, or download-size decision is required.

Required `evidence` entries:

```json
[
  {"type": "doc", "path_or_url": "<out_dir>/asset_provenance.json", "notes": "Machine-readable provenance packet"},
  {"type": "hash", "path_or_url": "<out_dir>/artifact_hashes.txt", "notes": "Hashes for source and output files"},
  {"type": "asset", "path_or_url": "<raw_or_cleaned_asset_path>", "notes": "Primary asset output"},
  {"type": "test", "path_or_url": "<validation_report_path>", "notes": "Parser/readback/import validation"},
  {"type": "screenshot", "path_or_url": "<preview_path>", "notes": "Preview or render evidence"}
]
```

Recommended `next_action`:

- `queue_next_turn` when the next step is cleanup, validation, playable integration, or Unity import.
- `review` when the asset is technically valid but visual quality needs human judgment.
- `wait_for_human` when rights, license, or large download approval is required.
- `stop` when the asset is rejected and no retry is useful.
