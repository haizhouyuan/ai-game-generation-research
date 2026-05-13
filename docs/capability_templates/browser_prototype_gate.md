# Browser Prototype Gate Template

## Purpose

Use this template when running the local browser evidence gate for a playable prototype. The gate exercises a prototype through a defined scenario using Chrome DevTools Protocol (CDP) and a local static HTTP server, producing structured evidence for promotion review.

This gate is for local prototyping evidence only. It does not use a production browser farm.

## Inputs

| Field | Value |
|---|---|
| `prototype_id` | `<stable prototype id>` |
| `entrypoint` | `<path to HTML entrypoint>` |
| `scenario` | `<path to scenario JSON>` |
| `out` | `<immutable evidence output directory>` |
| `gate-level` | `<G0, G1, G2, G3, G4>` |
| `server-bind` | `127.0.0.1` (must remain loopback) |
| `browser` | `chromium` |
| `chrome` | `<path to Google Chrome>` |
| `timeout-ms` | `30000` |

Required preconditions:

- Chrome is installed at the default path or the path is provided via `--chrome`.
- The scenario JSON uses `scenario_version: "browser_prototype_gate.v1"` and its `prototype_id` and `gate_level` match the gate arguments.
- P1 prototypes expose `window.__prototypeGate` before the gate times out. P0 prototypes use the legacy script-injection path instead.
- The server bind address stays on the loopback interface (127.0.0.1). Non-loopback binding is a failure mode.
- No external network is required beyond localhost; the gate serves the prototype from the local repo. External requests in `network_summary.json` require separate review and should not be treated as an automatic pass.

## Commands / Placeholders

### P0 G2 Baseline

```bash
python3 tools/run_browser_prototype_gate.py \
  --prototype-id "p0_chatgpt_html_baseline" \
  --entrypoint "experiments/game_p0_chatgpt_html_baseline_20260509/14.html" \
  --scenario "scenarios/p0_smoke_g2.json" \
  --out "experiments/game_p0_chatgpt_html_baseline_20260509/evidence/20260513T000000Z_g2" \
  --gate-level "G2" \
  --browser chromium \
  --server-bind 127.0.0.1 \
  --timeout-ms 30000
```

P0 uses a legacy script-injection step runner rather than `window.__prototypeGate`.

### P1 G4 Rover Workshop

```bash
python3 tools/run_browser_prototype_gate.py \
  --prototype-id "p1_rover_workshop" \
  --entrypoint "experiments/game_p1_rover_workshop_demo/index.html" \
  --scenario "scenarios/p1_rover_workshop_g4.json" \
  --out "experiments/game_p1_rover_workshop_demo/evidence/20260513T000000Z_g4" \
  --gate-level "G4" \
  --browser chromium \
  --server-bind 127.0.0.1 \
  --timeout-ms 30000
```

P1 prototypes must expose `window.__prototypeGate` before the gate API wait times out. The gate calls `window.__prototypeGate.runStep(step)` for each scenario step.

Verify the hash manifest after the gate:

```bash
python3 tools/verify_artifact_hashes.py \
  "experiments/game_p1_rover_workshop_demo/evidence/20260513T000000Z_g4/artifact_hashes.json"
```

## Required Evidence

When produced by the gate, the evidence directory must contain:

- `release_packet.json` — machine-readable packet with `packet_version`, `release_id`, `prototype_id`, `entrypoint`, `gate_level`, `checks`, `artifacts`, `asset_provenance`, `known_limitations`, and `promotable` fields.
- `artifact_hashes.json` — SHA-256 hashes for files present when the gate writes the hash manifest, excluding `artifact_hashes.json` itself. The current tool writes `closeout.md` before the hash manifest, so the closeout hash must recompute from this manifest.
- `screenshots/` — PNG screenshots at each scenario step (e.g., `00_load.png`, `01_start.png`, …).
- `state_dumps/` — JSON state dump per step with `step`, `state`, and `pixel_stats`.
- `console_summary.json` — summarized console events with `errors` and `warnings` lists plus `log_count` and `event_count`.
- `network_summary.json` — summarized network activity: entry URL, request count, local vs. external requests, failure list.
- `closeout.md` — human-readable closeout with `release_id`, `promotable`, and per-check results.

## Pass Criteria

- All required checks for the gate level return `pass` or `not_applicable`.
- `promotable` is `true` only when all G4 checks pass.
- All listed artifacts exist. Hashes in `artifact_hashes.json` recompute for the files it records, including `closeout.md`.
- Page load completes within the timeout.
- For P1 prototypes, `window.__prototypeGate` is detected before the timeout.
- The requested `--server-bind` is loopback such as `127.0.0.1`.
- `console_summary.json` is reviewed and contains no unhandled errors.
- `network_summary.json` is reviewed; external requests must be absent or explicitly justified in the closeout before the worker returns `done`.

## Failure Modes

- `page_load_timeout`: page did not reach `document.readyState === 'complete'` before `--timeout-ms` elapsed.
- `missing_gate_api` (P1 only): `window.__prototypeGate` was not detected before the timeout.
- `blank_canvas`: all screenshots are blank (zero nontransparent pixels) or have only one distinct color.
- `expectation_failure`: a scenario step returned `pass: false` for one or more expected checks.
- `console_errors`: console summary contains errors that are not marked `not_applicable`.
- `network_failures`: one or more external network requests failed.
- `missing_provenance`: a non-procedural or generated GLB asset lacks an entry in `asset_provenance`.
- `missing_hashes`: `artifact_hashes.json` is absent or a hash does not recompute.
- `non_loopback_binding`: `--server-bind` is not `127.0.0.1` or equivalent loopback address.

## WORKER_RESULT Expectations

Return schema-valid `WORKER_RESULT` using `schemas/worker_result.schema.json`.

Use `status: "done"` only when the gate completed, all required artifacts exist, recorded hashes match the files covered by `artifact_hashes.json`, `console_summary.json` and `network_summary.json` have been reviewed, and any external request is explicitly justified in the closeout.

Use `status: "partial"` when a lower gate level passed but the requested gate level did not.

Use `status: "blocked"` when Chrome is unavailable, the entrypoint or scenario is missing, or the server bind cannot be set to loopback.

Required `tests` entries:

```json
[
  {"name": "<prototype_id> <gate_level> load", "status": "passed", "evidence": "<out>/scenario_result.json"},
  {"name": "<prototype_id> <gate_level> packet", "status": "passed", "evidence": "<out>/release_packet.json"}
]
```

Required `evidence` entries:

```json
[
  {"type": "doc", "path_or_url": "<out>/closeout.md", "notes": "Human-readable closeout"},
  {"type": "test", "path_or_url": "<out>/release_packet.json", "notes": "Machine-readable release packet"},
  {"type": "hash", "path_or_url": "<out>/artifact_hashes.json", "notes": "Artifact hashes"},
  {"type": "screenshot", "path_or_url": "<out>/screenshots", "notes": "Gate screenshots"},
  {"type": "log", "path_or_url": "<out>/browser_log.jsonl", "notes": "Browser CDP events"}
]
```

Recommended `next_action`:

- `archive` when the packet is complete and no further worker action is needed.
- `review` when packet is complete but human visual or gameplay review is desired.
- `queue_next_turn` when the next known gap (e.g., Unity import) is automatable.
- `wait_for_human` when a subjective design judgment or external platform step is required.

## Current Local Proof

Local proof exists for:

- P0 G2 baseline at `experiments/game_p0_chatgpt_html_baseline_20260509/14.html` run against `scenarios/p0_smoke_g2.json`.
- P1 G4 rover workshop at `experiments/game_p1_rover_workshop_demo/index.html` run against `scenarios/p1_rover_workshop_g4.json`.

## Limitations

- CDP console and network summaries are lighter than a full HAR or trace export; they provide a functional check but not exhaustive fidelity.
- Deterministic gate evidence through the `__prototypeGate` API does not replace human playtest for feel, difficulty, and edge cases.
- Imported generated GLBs are visual-only unless the asset provenance explicitly states a collider strategy.
- The browser gate does not prove Unity import, Godot import, or any engine-specific runtime behavior.
