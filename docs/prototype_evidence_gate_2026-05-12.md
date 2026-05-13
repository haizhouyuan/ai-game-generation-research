# Prototype Evidence Gate For Browser Playable Builds - 2026-05-12

## Purpose

This document defines the QA evidence gate for browser playable prototypes in the AI game generation research program. It is intentionally a documentation-only contract: it describes what future test commands, artifacts, and release packets must prove, but it does not change game code.

The first two target prototypes are:

- **P0 smoke**: the preserved ChatGPT-generated `14.html` baseline, used as the "AI made a real game" excitement benchmark.
- **P1 Rover Workshop**: the child-friendly Three.js playable slice described in `docs/game_p1_child_friendly_design_spec_2026-05-12.md`.

The gate should answer one question with evidence: can this prototype load, render, accept input, run its core loop, produce reproducible artifacts, and be promoted as a release demo without relying on subjective claims?

## Gate Levels

| Level | Name | Required For | Meaning |
|---|---|---|---|
| G0 | File and dependency smoke | Any captured prototype | The entry file exists, dependencies resolve, and the page reaches a stable loaded state. |
| G1 | Visual render smoke | P0 and all future demos | The canvas is present, nonblank, and screenshot evidence exists. |
| G2 | HUD and input smoke | P0 and all future demos | The test can start the game, observe HUD state, and drive deterministic input. |
| G3 | Core interaction playthrough | P1 and later | The test proves pickup, hazard response, puzzle/gate interaction, and finish condition. |
| G4 | Release packet | Any promoted demo | All logs, screenshots, hashes, asset provenance, and known limitations are bundled. |

P0 is expected to reach **G2** at minimum, because its current evidence is only a lobby screenshot smoke test. P1 Rover Workshop must reach **G4** before it is called a release demo.

## Required Checks

### 1. Load Check

The gate must prove that the prototype page loads without fatal browser errors.

Required evidence:

- entry URL or file path;
- HTTP server command when a local server is used;
- browser name and version if available;
- console error summary;
- network/dependency summary;
- timeout budget;
- final page state marker.

Pass criteria:

- the page becomes ready before timeout;
- no uncaught JavaScript exception blocks startup;
- required renderer libraries load;
- if a dependency fails, the failure is reported as a gate failure unless the prototype has a documented local fallback.

P0-specific notes:

- P0 depends on CDN Three.js. The gate must record whether `https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.min.js` loaded or whether an offline fallback was used.

P1-specific notes:

- P1 should prefer local or vendored runtime dependencies for reproducible evidence.

### 2. Nonblank Canvas Check

The gate must prove that the renderer produced visible pixels.

Required evidence:

- canvas selector or renderer target;
- screenshot after the first stable render;
- canvas dimensions;
- pixel statistics, including at least nontransparent pixel count and distinct color/sample count;
- failure screenshot if blank.

Pass criteria:

- a canvas exists and has nonzero width and height;
- the screenshot is not all one color;
- meaningful foreground/background variation is visible by pixel stats;
- the rendered scene is not hidden behind a full-screen loading overlay.

### 3. HUD Check

The gate must prove that game state is visible to the player.

Required evidence:

- DOM selectors or screenshot regions for HUD elements;
- extracted HUD text or state JSON where available;
- before/after HUD snapshots for at least one state change.

P0 minimum HUD evidence:

- lobby/start screen visible;
- in-game state visible after start;
- at least one of health, ammo, loot, coins, weapon, or settings state detected.

P1 minimum HUD evidence:

- battery counter;
- rover energy or assist/fail state;
- gear token or optional reward indicator;
- gate/puzzle state or objective hint;
- finish/result state after completion.

### 4. Input Check

The gate must prove that deterministic input changes the game state.

Required evidence:

- input script or replay steps;
- initial player/camera state;
- final player/camera state;
- screenshot before and after movement;
- any pointer-lock or focus handling notes.

Pass criteria:

- the test can start or enter the playable state;
- at least one movement input changes player position or camera orientation;
- input does not require a human during automated gate execution;
- focus/pointer-lock limitations are documented if the browser test environment cannot fully exercise them.

P0 minimum input evidence:

- click start/lobby action;
- move or camera action changes visible state;
- optional action input such as shoot/reload/pickup may be recorded but is not mandatory for the first G2 gate.

P1 minimum input evidence:

- start;
- move forward/back or to a waypoint;
- rotate camera or verify camera follows the rover;
- interact with pickup/switch/gate/finish trigger.

### 5. Pickup Check

The gate must prove that a collectible can be acquired and reflected in state.

Required evidence:

- pickup id or selector/schema id;
- player path or teleport-free deterministic route;
- pre-pickup screenshot/state;
- post-pickup screenshot/state;
- HUD/state delta.

Pass criteria:

- pickup disappears, animates, or marks itself collected;
- HUD or game state increments;
- the test records the exact pickup count after collection.

P1 minimum pickup evidence:

- collect at least one required battery;
- collect at least one optional gear token if present in the build;
- prove the battery counter moves toward the required finish count.

### 6. Hazard Check

The gate must prove that a moving or timed obstacle affects gameplay without blocking the full run.

Required evidence:

- hazard id/type;
- controlled route into or near the hazard;
- pre-contact state;
- post-contact or near-miss state;
- screenshot showing the hazard visible and readable.

Pass criteria:

- hazard is visually readable before contact;
- contact or near miss changes state, such as energy loss, stun, bounce-back, warning, or route timing;
- the player can recover and continue;
- the outcome is child-friendly for P1: no violent framing, no hard death loop.

P1 minimum hazard evidence:

- one cleaning bot, spark tile, rolling cart, light beam, or equivalent hazard is exercised;
- the rover energy/status changes or the gate logs a near-miss/warning event.

### 7. Gate Or Puzzle Check

The gate must prove that a puzzle interaction changes the traversable route.

Required evidence:

- switch, pressure pad, keycard, or puzzle id;
- gate/door id;
- before state showing the route blocked;
- activation state;
- after state showing the route open or changed;
- screenshot or state diff for both the puzzle object and gate.

Pass criteria:

- the gate starts closed/blocked;
- the player activates the puzzle by normal input or deterministic replay;
- the gate opens, unlocks, or visibly changes state;
- the test can proceed through the changed route.

P1 minimum puzzle evidence:

- central gate opened by a switch, pressure pad, keycard, or equivalent interaction;
- puzzle feedback visible through light beam, color change, animation, or HUD/objective update.

### 8. Finish Check

The gate must prove that the playable loop can complete.

Required evidence:

- finish object id;
- required objective count;
- state before finish is available;
- state after entering finish;
- result screen or completion marker;
- run duration or step count.

Pass criteria:

- finish is not available before required objectives unless intentionally documented;
- after required objectives, the finish trigger completes the run;
- result state is visible in DOM, canvas, log, or game state JSON;
- the run can be repeated from a clean start.

P1 minimum finish evidence:

- collect the required three batteries or the build's configured required count;
- activate the charging pad;
- show a result screen with completion status, battery count, and optional reward summary.

### 9. Screenshot Check

Every gate run must produce screenshots that are useful for human review.

Required screenshots:

- `00_load.png`: first stable loaded state;
- `01_start.png`: playable state after start;
- `02_input.png`: after movement/camera input;
- `03_pickup.png`: after at least one pickup;
- `04_hazard.png`: hazard visible during or after exercise;
- `05_gate.png`: puzzle/gate before and/or after activation;
- `06_finish.png`: completion/result state;
- `failure_*.png`: any failure point, when applicable.

For P0 G2, `03_pickup`, `04_hazard`, `05_gate`, and `06_finish` may be marked `not_applicable_yet` only if the release packet clearly says P0 remains a smoke baseline, not a full playthrough proof.

### 10. Hash Check

The gate must make artifacts reviewable and tamper-evident.

Required evidence:

- SHA256 for the entry HTML or build bundle;
- SHA256 for every generated screenshot;
- SHA256 for logs and machine-readable reports;
- SHA256 for non-procedural assets such as GLB, PNG, JPG, audio, or shader files;
- byte size and relative path for each artifact.

Pass criteria:

- all artifacts listed in the release packet exist;
- hash recomputation matches the packet;
- any missing artifact fails G4;
- any changed artifact must produce a new packet id or explicit update record.

### 11. Release Packet Check

A promoted browser prototype must have a release packet that a reviewer can inspect without rerunning the game.

Required files:

- human-readable `closeout.md`;
- machine-readable `release_packet.json`;
- `artifact_hashes.json`;
- browser/test log;
- console/network summary;
- screenshots;
- known limitations;
- provenance for non-procedural assets;
- command transcript or exact command shape.

Required packet fields:

```json
{
  "packet_version": "prototype_evidence_gate.v1",
  "release_id": "game_p1_rover_workshop_demo_YYYYMMDD",
  "prototype_id": "p1_rover_workshop",
  "entrypoint": "path-or-url",
  "gate_level": "G4",
  "checks": {
    "load": "pass",
    "nonblank_canvas": "pass",
    "hud": "pass",
    "input": "pass",
    "pickup": "pass",
    "hazard": "pass",
    "gate_or_puzzle": "pass",
    "finish": "pass",
    "screenshots": "pass",
    "hashes": "pass"
  },
  "artifacts": [],
  "asset_provenance": [],
  "known_limitations": [],
  "promotable": true
}
```

Pass criteria:

- every required check is `pass` or explicitly marked `not_applicable` with a reason accepted by the gate level;
- `promotable` is true only for G4 packets;
- the packet never claims visual QA, asset quality, collision quality, or production readiness beyond the evidence actually collected.

## Suggested Command Shape

The eventual command should be deterministic and local-first. Exact implementation can use Playwright, Chrome headless, or another browser runner, but it should expose a stable command shape like this:

```bash
python3 tools/run_browser_prototype_gate.py \
  --prototype-id p1_rover_workshop \
  --entrypoint experiments/game_p1_rover_workshop_demo/index.html \
  --scenario scenarios/p1_rover_workshop_g4_playthrough.json \
  --out experiments/game_p1_rover_workshop_demo/evidence/2026-05-12_g4 \
  --gate-level G4 \
  --browser chromium \
  --server-bind 127.0.0.1 \
  --timeout-ms 30000
```

P0 can use the same shape at G2:

```bash
python3 tools/run_browser_prototype_gate.py \
  --prototype-id p0_chatgpt_html_baseline \
  --entrypoint experiments/game_p0_chatgpt_html_baseline_20260509/14.html \
  --scenario scenarios/p0_smoke_g2.json \
  --out experiments/game_p0_chatgpt_html_baseline_20260509/evidence/2026-05-12_g2 \
  --gate-level G2 \
  --browser chromium \
  --server-bind 127.0.0.1 \
  --timeout-ms 30000
```

Suggested exit codes:

| Exit Code | Meaning |
|---:|---|
| 0 | Requested gate passed. |
| 1 | Browser or page load failed. |
| 2 | Render/canvas/HUD failed. |
| 3 | Interaction or playthrough check failed. |
| 4 | Artifact, screenshot, hash, or release packet failure. |
| 5 | Scenario definition invalid. |
| 6 | Unsupported prototype or gate level. |

## Suggested Artifact Layout

Use one immutable evidence directory per gate run:

```text
experiments/<prototype_id>/evidence/<date>_<gate_level>/
  closeout.md
  release_packet.json
  artifact_hashes.json
  browser_log.jsonl
  console_summary.json
  network_summary.json
  scenario_result.json
  screenshots/
    00_load.png
    01_start.png
    02_input.png
    03_pickup.png
    04_hazard.png
    05_gate.png
    06_finish.png
  state_dumps/
    00_load.json
    01_start.json
    02_input.json
    03_pickup.json
    04_hazard.json
    05_gate.json
    06_finish.json
  assets/
    asset_provenance.json
    glb_readback.json
```

If a prototype is a single-file baseline such as P0, keep the evidence under the original experiment directory and do not modify the preserved source file.

## Scenario Contract

The scenario file should describe user-visible actions, expected state changes, and screenshot capture points. It should avoid brittle implementation details when a prototype exposes a better state API.

Suggested shape:

```json
{
  "scenario_version": "browser_prototype_gate.v1",
  "prototype_id": "p1_rover_workshop",
  "gate_level": "G4",
  "steps": [
    {"id": "load", "action": "open", "expect": ["page_ready", "canvas_present"]},
    {"id": "start", "action": "click", "target": "start_button", "expect": ["play_state"]},
    {"id": "input", "action": "replay", "keys": ["KeyW", "KeyD"], "expect": ["position_changed"]},
    {"id": "pickup", "action": "navigate_to", "target": "battery_01", "expect": ["battery_count_incremented"]},
    {"id": "hazard", "action": "navigate_near", "target": "spark_tile_01", "expect": ["hazard_feedback"]},
    {"id": "gate", "action": "activate", "target": "switch_01", "expect": ["gate_01_open"]},
    {"id": "finish", "action": "navigate_to", "target": "finish_charging_pad", "expect": ["result_screen"]}
  ]
}
```

## Promotion Rules

A prototype may be called a release demo only when:

1. The requested gate level passes.
2. The release packet is complete and hash-valid.
3. Known limitations are explicit.
4. At least one human-reviewable screenshot shows the actual playable state.
5. P1 or later demos prove a complete loop, not just a rendered scene.
6. Generated assets have provenance and import/readback evidence.
7. The packet does not claim Unity, Blender, textured GLB, physics, animation, or production quality unless that specific chain has evidence.

## Current Expected Status

| Prototype | Current Evidence | Target Gate | Gap |
|---|---|---|---|
| P0 `14.html` | Headless Chrome lobby screenshot smoke | G2 | Needs automated start, nonblank canvas stats, HUD capture, input proof, hashes, and packet. |
| P1 Rover Workshop | Design spec only | G4 | Needs playable build plus load, canvas, HUD, input, pickup, hazard, puzzle/gate, finish, screenshots, hashes, and release packet. |

The important distinction is that **P0 is the excitement baseline**, while **P1 is the production-chain proving ground**. P0 can remain preserved and imperfect; P1 must carry the full browser prototype evidence gate.
