# Managed Agents Game Chain Handoff - 2026-05-12

## For The Next Thread

Start in:

```bash
cd /Users/yuanshaochen/Projects/ai-game-generation-research
```

Read these first:

1. `docs/production_goal_managed_agents_game_chain_v2_2026-05-12.md`
2. `docs/managed_agents_execution_status_2026-05-12.md`
3. this handoff document

Suggested opening instruction for the new thread:

```text
Continue the Managed Agents production goal from docs/managed_agents_handoff_2026-05-12.md.
Do not restart from planning. Verify current state, read WORKFLOW.md and
docs/symphony_alignment_2026-05-12.md, then continue with Symphony-aligned follow-on work.
Do not claim Unity/Blender/hero asset completion
until local evidence exists.
```

## Current Position

- Repo: `/Users/yuanshaochen/Projects/ai-game-generation-research`
- Current git HEAD verified this turn: `eaa93af`
- Worktree is intentionally very dirty with many untracked docs, experiments, tools, and external research sources. Do not clean/reset unless explicitly asked.
- The user wants the Managed Agents controller to become the primary production-grade multi-agent framework. The game-generation pipeline is the high-value validation scenario, not the only purpose.
- Symphony is now the preferred orchestration skeleton. `WORKFLOW.md` is the repo-local control contract; `config/lanes.yaml` is seed/status/evidence data, not a competing orchestration spec.
- `14.html` is a preserved excitement baseline, not the production route.
- Web/Three.js is only a fast validator/preview/fallback path unless a specific stage needs it.
- Unity remains the mature engine direction, but it is still blocked until local Editor/MCP readiness is proven.

## Completed In This Run

Controller phase 3 is now materially complete, and P0 G2 smoke was fixed after this handoff was first written:

- `src/managed_codex/registry_ops.py`
  - imports JSONL Codex/App Server events
  - creates orphan thread/turn records for incoming events so evidence is not dropped
  - produces dashboard snapshots: lanes, tasks, open issues, capabilities, missing evidence paths, recent events, recent evidence
- `src/managed_codex/cli.py`
  - added `dashboard`
  - added `event-import`
  - added `events`
  - added `appserver-smoke`
- `src/managed_codex/app_server_client.py`
  - added validated `AppServerClient`
  - added fake transport
  - added local-only HTTP JSON-RPC transport
  - rejects non-local live URLs
  - supports a guarded thread/start -> turn/start -> review/start -> thread/archive lifecycle smoke
- `config/lanes.yaml`
  - marks `controller-core-phase3` complete
  - marks `capability-registry-002`, `asset-001`, and `asset-002` complete
  - adds queued `controller-core-phase4`, `controller-core-phase5`, and `download-001`
  - records fixed controller issues for Python 3.9 typing compatibility and ruff regression
  - keeps Homebrew/Node probe as the remaining open controller issue

Capability templates added:

- `docs/capability_templates/glb_playable_validator.md`
- `docs/capability_templates/asset_provenance_packet.md`
- `docs/capability_templates/scene_qa_release_packet.md`
- `docs/capability_templates/no_proxy_governed_download.md`
- `docs/capability_templates/controller_issue_closeout.md`

Environment and P0 evidence added:

- `tools/probe_browser_qa_environment.py`
- `experiments/environment_browser_qa_probe_20260512/browser_qa_env_probe.json`
- `tools/p0_chrome_cdp_smoke.py`
- `experiments/game_p0_g2_browser_smoke_20260512/p0_g2_browser_smoke.json`
- `experiments/game_p0_g2_browser_smoke_20260512/p0_after_start.png`
- `experiments/game_p0_g2_browser_smoke_20260512/artifact_hashes.json`

P0/P1/Symphony follow-up completed:

- `tools/p0_chrome_cdp_smoke.py` no longer launches Chrome with `--disable-gpu`.
- Headless Chrome now uses the local WebGL-preserving flags `--ignore-gpu-blocklist`, `--use-gl=angle`, and `--use-angle=metal`.
- `threejs-001` is marked `task_complete` in `config/lanes.yaml`.
- P0 baseline capability now includes the P0 G2 JSON, screenshot, and hash evidence paths.
- `WORKFLOW.md` added as the Symphony-aligned repo contract.
- `docs/symphony_alignment_2026-05-12.md` records the pivot away from growing a separate universal controller.
- `tools/run_browser_prototype_gate.py` added as reusable P0/P1 browser evidence gate.
- P1 Rover Workshop has a procedural Three.js playable slice and G4 release packet.
- A game-dev worker improved P1 labels, movement, proximity interactions, toast feedback, and replay while preserving G4.
- User configured and verified USTC Homebrew API/bottle mirrors; npm installation remains governed future work.

## Verification At Handoff

These passed immediately before the latest handoff update:

```bash
.venv/bin/python -m pytest -q
# 42 passed

.venv/bin/ruff check src tests tools/probe_browser_qa_environment.py tools/p0_chrome_cdp_smoke.py tools/run_browser_prototype_gate.py tools/appserver_local_http_probe.py
# All checks passed
```

Registry smoke also passed:

```bash
tmpdb=$(mktemp -t managed-registry.XXXXXX).sqlite3
.venv/bin/codex-managed init --db "$tmpdb"
.venv/bin/codex-managed appserver-smoke --db "$tmpdb"
.venv/bin/codex-managed events --db "$tmpdb"
.venv/bin/codex-managed workflow --json-output
.venv/bin/codex-managed check-capabilities --db "$tmpdb"
rm -f "$tmpdb"
```

Expected dashboard state after seeded registry:

- lanes: 9 enabled, 2 paused
- tasks: 15 `task_complete`, 1 `blocked`
- next active task is blocked `unity-mcp-001`
- open controller issues should be none

## Important Blockers And Truth Boundaries

Do not overclaim these:

- Real App Server is not connected yet. `appserver-smoke` defaults to the fake harness. `tools/appserver_local_http_probe.py` proves the local-only HTTP transport boundary using a fake backend, not the real service.
- npm/npx are not available on PATH. Current local Node is Codex-bundled: `/Applications/Codex.app/Contents/Resources/node`.
- No downloads were attempted for Node/npm. USTC Homebrew mirrors are configured and verified by the user, but future package installs still need governed evidence.
- Browser plugin timed out twice while opening P0. Treat that older Browser-plugin result as a toolchain issue, not a success.
- P0 G2 smoke is now `passed` through the local CDP runner. Root cause of the old partial result was the smoke runner launching Chrome with `--disable-gpu`, which prevented Three.js WebGL renderer construction and stopped the page before control bindings attached.
- Unity is still blocked. No Editor/Hub/MCP local proof exists yet.
- Blender is still partial. No local Blender MCP cleanup/material/export/screenshot loop exists yet.
- Hero rover asset generation has not started. No OpenAI image reference, TRELLIS/TripoSR/Hunyuan comparison, Blender cleanup, texture/material proof, or Unity import proof exists yet.

## Next Work Order

1. Continue Symphony alignment.
   - Keep future orchestration behavior mapped to `WORKFLOW.md` and Symphony concepts.
   - Do not expand the controller into a competing platform unless there is a repo-specific evidence need.

2. Continue P1 game polish through independent game-dev Codex threads.
   - For substantial game-development execution, open a separate Codex thread with the `codex://new` deeplink and the prompt in `docs/game_development_thread_prompt_2026-05-12.md`; do not replace this thread boundary with an in-thread subagent.
   - Keep `window.__prototypeGate` and G4 evidence passing.
   - Do not touch controller/workflow files from game-development threads.

3. Start the hero rover asset chain only when ready.
   - Rover asset plan is in `docs/rover_workshop_asset_generation_plan_2026-05-12.md`.
   - Use one hero rover asset first, with provenance, mesh/material proof, runtime validation, and no Unity/Blender claims without local evidence.

## Handy Commands

```bash
cd /Users/yuanshaochen/Projects/ai-game-generation-research

.venv/bin/codex-managed status
.venv/bin/codex-managed dashboard
.venv/bin/codex-managed workflow
.venv/bin/codex-managed capabilities
.venv/bin/codex-managed issues
.venv/bin/codex-managed check-capabilities

python3 tools/probe_browser_qa_environment.py

python3 -m http.server 8766 --bind 127.0.0.1 \
  --directory experiments/game_p0_chatgpt_html_baseline_20260509

python3 tools/p0_chrome_cdp_smoke.py \
  --url http://127.0.0.1:8766/14.html \
  --port 9239

python3 tools/run_browser_prototype_gate.py \
  --prototype-id p1_rover_workshop \
  --entrypoint experiments/game_p1_rover_workshop_demo/index.html \
  --scenario scenarios/p1_rover_workshop_g4.json \
  --out experiments/game_p1_rover_workshop_demo/evidence/2026-05-12_g4 \
  --gate-level G4 \
  --server-bind 127.0.0.1 \
  --timeout-ms 30000
```

Stop any temporary `http.server` after use. No local server was left intentionally running at this handoff.
