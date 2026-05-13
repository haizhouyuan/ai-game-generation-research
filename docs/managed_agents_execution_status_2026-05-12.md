# Managed Agents Execution Status - 2026-05-12

Source goal: `docs/production_goal_managed_agents_game_chain_v2_2026-05-12.md`

## Snapshot

- Registry seed check with a temporary DB shows 11 lanes: 9 enabled, 2 paused.
- Task state from seeded registry after this run: 15 `task_complete`, 1 `blocked`.
- Capability state: 7 available, 2 partial, 1 blocked; capability evidence paths pass.
- Open controller issues: none.
- Symphony alignment: `WORKFLOW.md` is now the repo-local orchestration contract; `config/lanes.yaml` remains seed/status/evidence data.
- Fresh P0 G2 evidence: `tools/p0_chrome_cdp_smoke.py` now passes with load/start/canvas/HUD/input screenshot and hashes.
- Fresh verification: `pytest` passes with 42 tests; `ruff check src tests tools/probe_browser_qa_environment.py tools/p0_chrome_cdp_smoke.py tools/run_browser_prototype_gate.py tools/appserver_local_http_probe.py` passes.

## Status By Workstream

| Workstream | Done | Partial | Blocked | Next |
| --- | --- | --- | --- | --- |
| controller-core | Phase 1-5 are seeded as complete for local proof. Registry, scheduler policy, worker result validation, fake/local HTTP App Server boundary, `record-result`, issue commands, event import, orphan event capture, dashboard, and workflow summary code/tests exist. | Real App Server endpoint is not connected; local HTTP proof uses fake backend behind live transport boundary. | None open. | Align future controller work to Symphony concepts instead of expanding a parallel orchestrator. |
| capability-registry | Initial capability entries exist for P0, Three.js GLB validation, P26 TRELLIS mesh-only, Godot CI/reviewer packet, no-proxy downloads, Unity MCP, Blender MCP, and TRELLIS textured export. Evidence path check passes. Worker templates now exist for GLB validation, asset provenance, scene QA release packet, no-proxy download, and controller issue closeout. | P0-P27 are still only partially promoted into capability-grade skills/templates beyond the first reusable set. | None hard, but broader stale-template coverage is still missing. | Continue promoting remaining high-value P0-P27 experiments after real controller phase 4 is stable. |
| research | Current best-practices matrix exists and classifies managed agents, Unity AI/MCP, community Unity MCPs, Blender MCP, OpenAI image, Three.js, TRELLIS, TripoSR, Hunyuan3D, and OpenGame. | Research is not yet a recurring refresh skill or automation. Adopt/probe/defer decisions still need local evidence gates for promoted tools. | No large-download research probes should run until governed download path is active. | Convert matrix entries into dated validation tasks and keep current research separate from local proof claims. |
| game-design | P1 design exists: `Rover Workshop: Battery Rescue`. P0 has automated G2 evidence. P1 now has a procedural browser playable slice with G4 release evidence and a game-dev worker increment: in-world labels, smoother movement, proximity interactions, toast feedback, and replay. | P0 remains a baseline, not a production route. P1 is procedural and not yet backed by generated hero GLB assets. | None hard. | Keep P1 as browser validation slice while asset pipeline develops the hero rover. |
| asset-generation | Rover Workshop asset generation plan exists. P26 proves TRELLIS mesh-only GLB generation/readback/preview/hash. Hero rover is correctly chosen as the first deep asset. Image-to-GLB validation and asset provenance templates are now in place. | OpenAI reference images, TRELLIS vs TripoSR/Hunyuan3D comparison, Blender cleanup, material/texture report, and runtime validation are not done for the rover. | TRELLIS textured export remains partial because textured/material path is not proven. | Start one hero rover chain only: reference image, candidate GLBs, mesh stats, cleanup, Three.js validation, provenance packet. |
| Unity | Unity lane is explicitly present and correctly paused/blocked until host readiness is proven. Goal and matrix keep Unity as the mature engine route, not replaced by Web/Three.js. | Official/community MCP comparison exists at research level only. No disposable Unity project proof yet. | `unity-mcp-001` is blocked: local Editor/Hub/MCP/account/download readiness is not proven. | Probe Mac/HomePC/Yoga without large downloads; record version/license/account/download constraints; then run disposable scene mutation loop. |
| Blender | Blender MCP is classified as partial and source/research evidence exists. It is correctly positioned for cleanup/material/screenshot/GLB export. | No local Blender/MCP create-material-export-screenshot cycle is proven. No rover cleanup has happened. | Lane is paused pending host verification. | Verify Blender host, then run a disposable minimal cycle before touching hero asset cleanup. |
| QA | Prototype evidence gate document defines G0-G4. `tools/run_browser_prototype_gate.py` now produces browser release packets, screenshots, state dumps, hashes, and closeouts. P0 G2 and P1 G4 packets exist. | Console/network summaries are basic in the first CDP runner. | None hard. | Extend richer browser telemetry later if needed. |
| environment | Python environment and tests are usable. Browser QA uses local Chrome CDP and does not require npm. User configured and verified USTC Homebrew API/bottle mirrors for future package setup. | npm still is not installed on PATH, but it is no longer blocking current P0/P1 gates. HomePC/Yoga/Mac tool readiness is documented but not fully automated into capability probes. | Unity/Blender host readiness blocks engine lanes. | Use USTC mirror variables for future governed Homebrew installs only when needed. |

## Key Conclusions

- The immediate highest-value direction is Symphony alignment: keep `WORKFLOW.md` as the orchestration contract and stop growing a separate universal orchestrator.
- Web/Three.js should remain validator/fallback only: use it for P0 G2, GLB previews, and P1 evidence gates, not as the final engine commitment.
- Unity and Blender should not be promoted until local host readiness and disposable proof loops exist.
- Capability-registry is the bridge from prior experiments to production work; without templates, agents will keep rediscovering old evidence manually.
- Asset work should start with one hero rover asset and a full provenance chain, not broad multi-asset generation.

## Fresh Verification

- `./.venv/bin/python -m pytest -q`: 42 passed.
- `./.venv/bin/ruff check src tests tools/probe_browser_qa_environment.py tools/p0_chrome_cdp_smoke.py tools/run_browser_prototype_gate.py tools/appserver_local_http_probe.py`: passed.
- Temporary registry commands: `init`, `status`, `check-capabilities`, `issues`, `event-import`, and `dashboard --json-output` ran successfully against temporary inputs/DBs.
- `python3 tools/p0_chrome_cdp_smoke.py --url http://127.0.0.1:8766/14.html --port 9239`: passed, writing `experiments/game_p0_g2_browser_smoke_20260512/p0_g2_browser_smoke.json`, `p0_after_start.png`, and `artifact_hashes.json`.
- `python3 tools/run_browser_prototype_gate.py --prototype-id p1_rover_workshop --entrypoint experiments/game_p1_rover_workshop_demo/index.html --scenario scenarios/p1_rover_workshop_g4.json --out experiments/game_p1_rover_workshop_demo/evidence/2026-05-12_g4 --gate-level G4 --server-bind 127.0.0.1 --timeout-ms 30000`: passed.
- `.venv/bin/codex-managed workflow --json-output`: reports `WORKFLOW.md` title `Managed Agents Workflow` and expected sections.
- `.venv/bin/codex-managed check-capabilities`: capability evidence paths pass.
- Seeded task state after config reconciliation: 15 `task_complete`, 1 `blocked`.
