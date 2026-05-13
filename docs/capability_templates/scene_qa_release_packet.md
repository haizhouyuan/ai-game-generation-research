# Scene QA Release Packet Template

## Purpose

Use this template when a worker promotes a playable prototype, scene, or demo candidate. It standardizes the evidence required to say "this is a release demo candidate" instead of "it looked like it worked once."

For browser prototypes, P0 should reach at least G2 and P1 Rover Workshop should reach G4. For Unity or Godot scenes, map the same ideas to engine-specific play/test evidence.

## Inputs

Fill these fields before running QA:

| Field | Value |
|---|---|
| `task_id` | `<managed task id>` |
| `lane_id` | `qa-evidence`, `threejs-playable-runtime`, or `unity-agent-mcp` |
| `repo_id` | `ai-game-generation-research` |
| `prototype_id` | `<p0_chatgpt_html_baseline, p1_rover_workshop, unity_disposable_scene, etc.>` |
| `gate_level` | `<G0, G1, G2, G3, G4>` |
| `entrypoint` | `<file path, URL, Unity scene, Godot scene>` |
| `scenario_path` | `<scenario/replay/test fixture path>` |
| `out_dir` | `<immutable evidence directory>` |
| `asset_manifest` | `<asset manifest or provenance path>` |
| `runner` | `<browser, Unity, Godot, custom>` |

Required preconditions:

- The source prototype or scene exists.
- The requested gate level is realistic for the current build.
- Generated/non-procedural assets have provenance or are explicitly listed as missing/blocking.
- Engine/editor automation must be local-only.

## Commands / Placeholders

Use the actual QA command when available. Record exact command, cwd, environment notes, and exit code.

```bash
# Browser prototype gate placeholder
python3 tools/run_browser_prototype_gate.py \
  --prototype-id "<prototype_id>" \
  --entrypoint "<entrypoint>" \
  --scenario "<scenario_path>" \
  --out "<out_dir>" \
  --gate-level "<gate_level>" \
  --browser chromium \
  --server-bind 127.0.0.1 \
  --timeout-ms 30000

# Engine scene gate placeholder
<engine_test_runner> \
  --scene "<entrypoint>" \
  --scenario "<scenario_path>" \
  --out "<out_dir>" \
  --local-only

# Packet hash placeholder
find "<out_dir>" -type f -print0 | xargs -0 shasum -a 256 > "<out_dir>/artifact_hashes.txt"
```

Required packet files:

```text
<out_dir>/
  closeout.md
  release_packet.json
  artifact_hashes.txt or artifact_hashes.json
  runner_log.jsonl or runner_log.txt
  console_summary.json
  scenario_result.json
  screenshots/
  state_dumps/
  assets/
```

## Required Evidence

For G2:

- Load result.
- Nonblank render/canvas/screen evidence.
- HUD or visible state evidence.
- Deterministic input proof.
- Screenshot set.
- Hashes for entrypoint, screenshots, logs, and reports.

For G4:

- All G2 evidence.
- Pickup or collectible proof.
- Hazard or obstacle proof.
- Puzzle/gate/route-change proof.
- Finish/result proof.
- Asset provenance for every non-procedural asset.
- Known limitations.
- Human-readable `closeout.md`.
- Machine-readable `release_packet.json`.

Minimum `release_packet.json` shape:

```json
{
  "packet_version": "scene_qa_release_packet.v1",
  "release_id": "<stable release id>",
  "prototype_id": "<prototype_id>",
  "entrypoint": "<entrypoint>",
  "gate_level": "<gate_level>",
  "checks": {},
  "artifacts": [],
  "asset_provenance": [],
  "known_limitations": [],
  "promotable": false
}
```

Pass criteria:

- All required checks for the gate level pass or are marked `not_applicable` with a gate-appropriate reason.
- `promotable` is true only for a complete G4 packet.
- All listed artifacts exist and hashes recompute.
- The packet does not claim Unity, Blender, texture, animation, physics, visual QA, or production readiness without matching evidence.

## Failure Modes

Record these as blockers or risks:

- `entrypoint_missing`: source file, URL, or scene is unavailable.
- `runner_missing`: QA command or engine runtime is not available.
- `load_failed`: page or scene cannot start.
- `blank_render`: canvas/screen is blank or covered by loading UI.
- `input_unproven`: deterministic input cannot be exercised.
- `loop_incomplete`: pickup, hazard, gate, or finish proof missing for G4.
- `asset_provenance_missing`: generated/non-procedural asset lacks provenance.
- `hash_mismatch`: packet hashes do not match artifacts.
- `overclaim`: packet claims a capability not supported by evidence.
- `human_only`: manual play was used without automated or reproducible evidence.

## WORKER_RESULT Expectations

Return schema-valid `WORKER_RESULT` using `schemas/worker_result.schema.json`.

Use `status: "done"` only when the requested gate packet is complete and internally consistent.

Use `status: "partial"` when a lower gate passed but the requested gate did not.

Use `status: "blocked"` when the runner, engine, account, asset, or scenario is unavailable.

Required `tests` entries:

```json
[
  {"name": "<prototype_id> <gate_level> load", "status": "passed", "evidence": "<out_dir>/scenario_result.json"},
  {"name": "<prototype_id> <gate_level> packet", "status": "passed", "evidence": "<out_dir>/release_packet.json"}
]
```

Required `evidence` entries:

```json
[
  {"type": "doc", "path_or_url": "<out_dir>/closeout.md", "notes": "Human-readable closeout"},
  {"type": "test", "path_or_url": "<out_dir>/release_packet.json", "notes": "Machine-readable release packet"},
  {"type": "hash", "path_or_url": "<out_dir>/artifact_hashes.txt", "notes": "Artifact hashes"},
  {"type": "log", "path_or_url": "<out_dir>/runner_log.jsonl", "notes": "Runner log"},
  {"type": "screenshot", "path_or_url": "<out_dir>/screenshots", "notes": "Gate screenshots"}
]
```

Recommended `next_action`:

- `archive` when the packet is complete and no further worker action is needed.
- `review` when packet is complete but human visual/gameplay review is desired.
- `queue_next_turn` when the next known gap is automatable.
- `wait_for_human` when engine login, approval, or subjective design judgment blocks progress.
