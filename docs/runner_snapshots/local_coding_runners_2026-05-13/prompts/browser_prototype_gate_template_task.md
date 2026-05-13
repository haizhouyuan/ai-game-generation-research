# Browser Prototype Gate Template Task

Goal:

Create `docs/capability_templates/browser_prototype_gate.md` in the workspace. The template must be worker-readable and must document how to run the local browser prototype evidence gate for P0 G2 and P1 G4 style prototypes.

Write scope:

- `docs/capability_templates/browser_prototype_gate.md`

Do not edit:

- Any other file.
- `config/lanes.yaml`.
- Status or audit documents.
- Private credential directories.
- Generated evidence directories.

Context files to read:

- `tools/run_browser_prototype_gate.py`
- `scenarios/p0_smoke_g2.json`
- `scenarios/p1_rover_workshop_g4.json`
- `docs/capability_templates/scene_qa_release_packet.md`
- `docs/capability_templates/glb_playable_validator.md`

Required content:

- Title: `# Browser Prototype Gate Template`
- Sections:
  - `## Purpose`
  - `## Inputs`
  - `## Commands / Placeholders`
  - `## Required Evidence`
  - `## Pass Criteria`
  - `## Failure Modes`
  - `## WORKER_RESULT Expectations`
  - `## Current Local Proof`
- Include separate command examples for:
  - P0 G2 baseline using `experiments/game_p0_chatgpt_html_baseline_20260509/14.html`, `scenarios/p0_smoke_g2.json`, and a dated output directory under the P0 experiment.
  - P1 G4 rover workshop using `experiments/game_p1_rover_workshop_demo/index.html`, `scenarios/p1_rover_workshop_g4.json`, and a dated output directory under the P1 experiment.
- State that this gate uses local Chrome CDP and a local static server, not a production browser farm.
- State that `--server-bind` must stay loopback such as `127.0.0.1`.
- State that P1 prototypes should expose `window.__prototypeGate`, while P0 has a special legacy path.
- Require `release_packet.json`, `artifact_hashes.json`, screenshots, state dumps, `console_summary.json`, `network_summary.json`, and `closeout.md` when produced by the gate.
- Include limitations:
  - CDP summaries are lighter than a full HAR/trace.
  - Deterministic gate evidence does not replace human playtest.
  - Imported generated GLBs are visual-only unless provenance and collider strategy say otherwise.
  - The browser gate does not prove Unity import.
- Include failure modes for page load timeout, missing gate API, blank canvas, expectation failure, console errors, network failures, missing provenance, missing hashes, and non-loopback binding.
- Do not claim new evidence was generated.
- Do not mark any capability complete.

Verification commands:

```bash
test -f docs/capability_templates/browser_prototype_gate.md
rg -n "Purpose|Inputs|Commands / Placeholders|Required Evidence|Pass Criteria|Failure Modes|WORKER_RESULT Expectations|Current Local Proof|p0_smoke_g2|p1_rover_workshop_g4|window.__prototypeGate|127.0.0.1|release_packet.json|console_summary.json|network_summary.json|Unity" docs/capability_templates/browser_prototype_gate.md
```

Completion response:

```text
DONE

Files changed:
- docs/capability_templates/browser_prototype_gate.md

Commands run:
- ...

Notes:
- ...
```
