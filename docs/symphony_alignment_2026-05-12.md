# Symphony Alignment Decision - 2026-05-12

## Decision

Align the Managed Agents work in this repo with OpenAI Symphony rather than continuing to expand a separate all-purpose controller.

The current controller work remains useful, but its role changes:

- `WORKFLOW.md` becomes the main orchestration contract.
- `config/lanes.yaml` becomes a seed for lanes, task status, capabilities, and evidence paths.
- SQLite remains a local status/evidence extension.
- App Server code remains a guarded adapter boundary, not a parallel product.
- Browser game QA remains a repo-specific evidence workflow.

## Why

Symphony provides the better skeleton for multi-agent orchestration: repo-local workflow policy, issue/workspace isolation, runner/tracker boundaries, and observable status. Those are the same concerns this project was starting to rebuild.

The AI game-generation repo has valuable domain extensions that Symphony does not replace:

- P0/P1 browser evidence gates.
- Asset provenance and generated mesh limitations.
- Unity/Blender host-readiness blockers.
- No-proxy and large-download governance.
- Capability registry entries with local evidence paths.

So the right direction is alignment, not replacement.

## Current Local State

- P0 baseline has G2 browser evidence.
- P1 Rover Workshop has a G4 browser release packet using procedural assets.
- `tools/run_browser_prototype_gate.py` is the reusable browser QA command.
- `src/managed_codex/app_server_client.py` has fake and local-only HTTP JSON-RPC boundaries.
- No real App Server endpoint is connected yet.
- Unity and Blender remain blocked/partial until local host proof exists.
- npm is not required for current browser QA. The user configured USTC Homebrew bottle/API mirrors, which makes future Homebrew-based setup more viable, but npm installation remains a governed task rather than an implicit dependency.

## Migration Shape

1. Keep `WORKFLOW.md` short, reviewable, and authoritative for orchestration policy.
2. Add CLI visibility so `codex-managed workflow` and `dashboard --json-output` show the workflow contract.
3. Do not add new scheduler behavior unless it maps cleanly to Symphony concepts.
4. Treat future controller code as adapters or evidence extensions:
   - App Server adapter.
   - capability/evidence registry.
   - QA/release packet commands.
   - local status reports.
5. Move substantial game-development execution into independent `codex://new` threads. Those threads may use subagent-driven development internally, but the top-level boundary is a separate Codex thread with non-overlapping write scope.

## Non-Goals

- Do not claim Symphony is fully integrated locally.
- Do not replace existing P0/P1 evidence with a pure Symphony issue flow.
- Do not promote Unity, Blender, generated hero assets, or textured GLB until local evidence exists.
- Do not install package managers or large tools outside download governance.

## Next Steps

- Keep improving P1 gameplay through independent game-dev Codex threads opened from `docs/game_development_thread_prompt_2026-05-12.md`.
- Convert any future long-running agent task into a `WORKFLOW.md`-compatible task with explicit evidence expectations.
- When a real local Codex App Server endpoint is available, connect it behind the existing local-only HTTP transport and record lifecycle evidence.
- If Homebrew/npm setup is needed, use the verified USTC mirror variables and record source, size, hash, and no-proxy evidence.
