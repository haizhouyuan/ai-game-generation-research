# Game Development Thread Prompt - 2026-05-12

You are a new independent Codex thread working in:

```bash
cd /Users/yuanshaochen/Projects/ai-game-generation-research
```

This is not a small cleanup task. Run the game-development lane as a sustained subagent-driven development session inside this new thread.

## Read First

1. `WORKFLOW.md`
2. `docs/production_goal_managed_agents_game_chain_v2_2026-05-12.md`
3. `docs/managed_agents_handoff_2026-05-12.md`
4. `docs/game_p1_child_friendly_design_spec_2026-05-12.md`
5. `docs/rover_workshop_asset_generation_plan_2026-05-12.md`
6. `docs/prototype_evidence_gate_2026-05-12.md`

## Mission

Advance the playable game itself, not the controller framework.

Current flagship prototype:

- `experiments/game_p1_rover_workshop_demo/index.html`
- Scenario: `scenarios/p1_rover_workshop_g4.json`
- Evidence output: `experiments/game_p1_rover_workshop_demo/evidence/2026-05-12_g4/`

Make meaningful game-development progress beyond a tiny patch. Use subagent-driven development inside this thread for independent game tasks where useful, with non-overlapping write scopes.

Good directions:

- Improve P1 Rover Workshop game feel, readability, level design, feedback, camera, pacing, onboarding, and replay value.
- Keep the child-friendly theme: exploration, collection, avoidance, puzzle, repair, and discovery. No weapons or combat fantasy.
- Add or refine gameplay systems only when they can be exercised by the automated G4 gate or a new documented scenario.
- Strengthen procedural visuals and HUD clarity while preserving fast local loading.
- If you start asset work, keep it evidence-gated and do not claim Unity, Blender, or generated-hero-asset completion without local proof.

## Boundaries

- Do not expand the Managed Agents controller or orchestration framework in this thread.
- Avoid touching `src/managed_codex/**`, `WORKFLOW.md`, and controller status docs unless the game evidence contract truly requires it.
- Preserve `window.__prototypeGate`.
- Preserve or improve G4 evidence. Do not leave the repo in a state where the P1 gate fails.
- Respect the dirty worktree. Do not reset, clean, or revert user/other-thread changes.

## Required Verification

At minimum, run:

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

If you change Python tooling or scenarios, also run the relevant tests.

## Output

Keep working until a meaningful game-development slice is complete or blocked. End with:

- Files changed
- Gameplay changes made
- Evidence generated
- Commands run and results
- Any blockers or next recommended game-dev tasks
