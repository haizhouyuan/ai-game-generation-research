# Game Thread Goal: Continue P1 Rover Workshop - 2026-05-12

You are continuing the existing independent game-development Codex thread for:

```bash
/Users/yuanshaochen/Projects/ai-game-generation-research
```

This goal supersedes the previous "single slice" completion mindset. Continue pushing the game forward using subagent-driven development inside this thread.

## Operating Mode

Use the `superpowers:subagent-driven-development` method:

1. Read this goal file, then extract the work into independent implementation tasks.
2. For each substantial task, dispatch a fresh implementer subagent with a narrow write scope.
3. After each task, run a spec-compliance review and a code-quality review before marking it complete.
4. Continue without asking whether to proceed. Stop only when all goals below are complete, or when blocked by a real missing dependency or ambiguity that cannot be resolved from repo context.
5. Keep write scopes non-overlapping. Do not revert user or other-thread work.

## Repo Boundary

Work only on the game-development lane unless a test/evidence contract absolutely requires a tiny supporting change.

Primary files:

- `experiments/game_p1_rover_workshop_demo/index.html`
- `scenarios/p1_rover_workshop_g4.json`
- `experiments/game_p1_rover_workshop_demo/evidence/2026-05-12_g4/`

Reference files:

- `WORKFLOW.md`
- `docs/game_p1_child_friendly_design_spec_2026-05-12.md`
- `docs/rover_workshop_asset_generation_plan_2026-05-12.md`
- `docs/prototype_evidence_gate_2026-05-12.md`
- `tools/run_browser_prototype_gate.py`

Avoid controller/framework edits:

- Do not expand `src/managed_codex/**`.
- Do not modify orchestration docs unless a game evidence contract needs a narrow correction.
- Do not start Unity, Blender, package installation, or external downloads unless the goal file is explicitly updated to request that.

## Final Game Goals To Achieve

Reach a stronger P1 browser-playable game that is visibly and mechanically better than the current P1 slice while preserving fast local verification.

Complete all of these goals:

1. Add a moving friendly cleaning-bot patrol hazard.
   - It should move on a readable route.
   - It should be visually distinct from the spark tile.
   - Contact should give clear non-violent feedback and reduce energy without ending the run immediately.
   - Add or extend evidence so the automated gate proves patrol contact or patrol hazard feedback.

2. Add a second puzzle interaction beyond the existing switch.
   - It can be a pressure pad, gear-powered bridge, timed workshop relay, magnet-only pickup, or equivalent.
   - It must support the child-friendly repair/exploration fantasy.
   - It must affect level progression or optional mastery, not just decorative text.
   - Add automated gate evidence for the puzzle state.

3. Improve the level layout and signposting.
   - Make the route from start to batteries, puzzle, gate, and charging pad more legible.
   - Keep labels and HUD helpful without cluttering the screen.
   - Improve visual contrast between safe path, hazards, interactive objects, and finish.
   - Keep mobile and desktop HUD text from overlapping.

4. Improve moment-to-moment game feel.
   - Rover movement should remain smooth and controllable.
   - Pickups, hazards, puzzle completion, gate opening, magnet boost, and finish should each have clear feedback.
   - The finish screen should summarize meaningful run state.

5. Preserve and strengthen the prototype gate.
   - `window.__prototypeGate` must remain available.
   - G4 must still prove: load, canvas nonblank, HUD, input, pickup, hazard, gate or puzzle, finish, release packet, screenshots, hashes, and asset provenance.
   - If new gameplay states are added, update `scenarios/p1_rover_workshop_g4.json` and the gate-facing state output so the evidence packet captures them.

6. Keep the implementation repo-local and lightweight.
   - No new package manager dependency.
   - No network assets.
   - No external downloads.
   - Procedural Three.js primitives are acceptable for this P1 browser slice.

## Required Verification

Run the P1 G4 gate:

```bash
python3 tools/run_browser_prototype_gate.py \
  --prototype-id p1_rover_workshop \
  --entrypoint experiments/game_p1_rover_workshop_demo/index.html \
  --scenario scenarios/p1_rover_workshop_g4.json \
  --out experiments/game_p1_rover_workshop_demo/evidence/2026-05-12_g4 \
  --gate-level G4 \
  --server-bind 127.0.0.1 \
  --timeout-ms 30000
```

Run focused tests:

```bash
.venv/bin/python -m pytest -q tests/test_browser_prototype_gate.py
```

If you change Python tooling, scenarios, or workflow-facing behavior, run the relevant broader tests too.

## Completion Report

When done, reply with:

- Subagent-driven task breakdown used.
- Files changed.
- Gameplay changes made.
- Evidence generated.
- Commands run and exact pass/fail results.
- Remaining blockers, if any.
- The next two best game-development goals.
