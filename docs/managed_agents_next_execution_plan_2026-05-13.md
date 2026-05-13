# Managed Agents Next Execution Plan - 2026-05-13

## Current Truth

`production_goal_managed_agents_game_chain_v2_2026-05-12.md` remains the total goal, but `symphony_alignment_2026-05-12.md` changes the direction: do not grow a parallel all-purpose controller. Keep `WORKFLOW.md` authoritative, use `config/lanes.yaml` as capability/evidence/task seed data, and treat code as adapters or evidence extensions.

## Execution Blocks

1. Capability stale checker
   - Add optional stale evidence detection to `check-capabilities`.
   - Keep current missing-path behavior as default.
   - Evidence: targeted pytest and CLI run.

2. External runner pool
   - Record Gemini, YogaS2 Claude/Kimi/MiniMax wrapper readiness.
   - Keep secrets out of repo.
   - Use these runners for planning/review/mechanical tasks where they reduce Codex token use.

3. App Server/Symphony truth correction
   - Stop overclaiming real App Server completion.
   - Reconcile `config/lanes.yaml` and status docs with fake/local-only HTTP proof.
   - Add a clear live-endpoint blocker or proof command.

4. Hero rover asset chain
   - Start one hero rover path, not broad asset generation.
   - Required evidence: reference, GLB candidate, mesh stats, material state, hash, Three.js validation, proxy collider plan.

5. Blender and Unity host probes
   - Probe host/tool readiness without large downloads.
   - Record blocked/partial/available with evidence.
   - Do not promote either lane without disposable local proof.

6. QA gate quality
   - Keep P0 G2 and P1 G4 passing.
   - Improve console/network telemetry later, but do not confuse harness pass with human play quality.

## Runner Assignment

- Codex subagent worker: narrow repo implementation tasks.
- Gemini CLI: read-only audits and spec/code reviews.
- YogaS2 `claudeminmax` / `claudekimi` / `kimicode`: remote planning/review where repo mutation is not required.
- Main Codex: integration, final verification, evidence, and status reconciliation.

## Stop Conditions

- A required credential or account login is missing and cannot be verified without the user.
- A required external file over 100M would need proxy traffic.
- A tool wants to mutate a high-privilege external surface, such as Unity/Blender/Claude project MCP, without a disposable proof path.
