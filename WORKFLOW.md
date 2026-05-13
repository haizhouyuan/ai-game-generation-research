# Managed Agents Workflow

## Scope

This repository follows a Symphony-aligned workflow contract. The durable control objective is not to grow a separate orchestration platform indefinitely; it is to keep orchestration policy in this repo, use Codex/App Server compatible boundaries, and preserve local evidence for game-generation work.

The AI game-generation pipeline is the proving ground. P0 is a preserved baseline. P1 Rover Workshop is the current browser-playable validation slice. Unity, Blender, and generated hero assets remain evidence-gated workstreams.

## Orchestration Model

- Treat Symphony's repo-local workflow contract as the preferred control-plane shape.
- Use `WORKFLOW.md` as the human-readable source of orchestration truth.
- Keep `config/lanes.yaml` as a seed for lanes, capabilities, evidence, and task status, not as a competing orchestration spec.
- Keep SQLite registry data as local evidence/status extension state.
- Use guarded local-only App Server transports; do not claim real App Server integration until a real local endpoint is proven.
- Use isolated worker scopes for delegated tasks and avoid overlapping write sets.

## Runtime

- Default to local Python tools in `.venv`.
- Browser QA uses local Chrome CDP and the repo tool `tools/run_browser_prototype_gate.py`.
- Codex-bundled Node is acceptable for static local scripts.
- npm/Homebrew/package installation must follow download provenance rules; the USTC Homebrew mirror may be used because the user configured and verified it.
- Do not alter system proxy, Clash, shell profile networking, or global package state unless explicitly requested.

## Task Routing

- Controller/workflow work owns `src/managed_codex/**`, `config/lanes.yaml`, `WORKFLOW.md`, and managed status docs.
- Game prototype work owns `experiments/game_p1_rover_workshop_demo/**` and its scenario/evidence files.
- Substantial game-development work should run in a separate Codex thread opened with `codex://new`, using `docs/game_development_thread_prompt_2026-05-12.md` as the handoff prompt. Do not substitute an in-thread subagent for that thread boundary.
- QA evidence work owns `tools/run_browser_prototype_gate.py`, `scenarios/**`, and evidence packet outputs.
- Asset/Unity/Blender work may not be marked complete without local proof artifacts.

## Evidence Gates

- P0 must retain G2 browser evidence: load, nonblank canvas, HUD, input, screenshots, hashes, and release packet.
- P1 browser prototype must retain G4 evidence: load, nonblank canvas, HUD, input, pickup, hazard, gate or puzzle, finish, screenshots, hashes, asset provenance, and release packet.
- `release_packet.json` and `artifact_hashes.json` are promotion artifacts.
- Generated mesh assets must include provenance, material/texture state, runtime validation, and proxy collision strategy.

## Safety

- No private child data, private screenshots, account sessions, or hosted uploads without explicit approval.
- No single external file over 1GB without explicit approval.
- No blind retries: failed worker output becomes a controller issue, blocker, or human question.
- No overclaims: Unity, Blender, textured GLB, real App Server, or generated hero asset completion require local evidence.

## Status Commands

```bash
.venv/bin/codex-managed workflow
.venv/bin/codex-managed dashboard
.venv/bin/codex-managed check-capabilities
python3 tools/run_browser_prototype_gate.py --prototype-id p1_rover_workshop --entrypoint experiments/game_p1_rover_workshop_demo/index.html --scenario scenarios/p1_rover_workshop_g4.json --out experiments/game_p1_rover_workshop_demo/evidence/2026-05-12_g4 --gate-level G4 --server-bind 127.0.0.1 --timeout-ms 30000
```
