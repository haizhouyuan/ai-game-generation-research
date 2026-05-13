# Managed Codex Game Generation Full Implementation Plan - 2026-05-12

## Purpose

This plan turns the extracted ChatGPT Pro session `Codex APP Dual Agent` into an executable program of work.

The goal is not merely to open many Codex threads. The target system is a managed multi-agent game-development workchain:

1. A Lead Orchestrator owns goals, registry state, scheduling, safety, and evidence.
2. Worker threads and subagents execute bounded tasks in isolated worktrees.
3. Research lanes keep current best practices fresh across Unity, Three.js, Blender, OpenAI image generation, AI 3D assets, and community MCP projects.
4. Game-development lanes turn the original HTML/Three.js prototype into a repeatable, child-friendly, higher-quality AI-generated game pipeline.
5. Every task leaves machine-readable results and artifact evidence so the chain can be resumed, audited, and improved.

## Source Inputs

Primary local sources:

- `external/chatgpt_app_extracts/codex_app_dual_agent_20260512/full_session_transcript.md`
- `docs/unity_agent_workchain_research_2026-05-12.md`
- `docs/direct_download_policy_2026-05-12.md`
- `docs/computer_use_chatgpt_app_policy_gap_2026-05-12.md`
- `docs/yogas2_maint_context_2026-05-12.md`
- `experiments/game_p0_chatgpt_html_baseline_20260509/`
- `experiments/game_p26_trellis_meshonly_asset_validation_20260512/`

Current official/community reference anchors checked on 2026-05-12:

- OpenAI Codex App Server: `https://developers.openai.com/codex/app-server`
- OpenAI Codex subagents: `https://developers.openai.com/codex/concepts/subagents`
- OpenAI image generation docs: `https://platform.openai.com/docs/guides/image-generation`
- OpenAI model docs for `gpt-image-1.5`: `https://platform.openai.com/docs/models/gpt-image-1.5`
- Unity AI official page: `https://unity.com/features/ai/`
- Unity AI open beta user guide: `https://support.unity.com/hc/en-us/articles/48060149523476-Getting-started-with-Unity-AI-open-beta-user-guide`
- Three.js GLTFLoader docs: `https://threejs.org/docs/#examples/en/loaders/GLTFLoader`
- Community candidates: `CoplayDev/unity-mcp`, `IvanMurzak/Unity-MCP`, `Signal-Loop/UnityCodeMCPServer`, `codemaestroai/advanced-unity-mcp`, `ahujasid/blender-mcp`.

## Architecture Decision

Implement a managed control plane instead of relying on manual multi-thread operation.

The Pro session's architecture should be adopted almost in full:

- Lead Orchestrator: reads the registry, creates or resumes worker threads, dispatches turns, interprets results, and decides whether to retry, review, archive, or wait for a human.
- App Server Client: talks to Codex App Server using generated schemas from the currently installed Codex version. Do not hand-write guessed request fields.
- Task Registry: SQLite + WAL first. Postgres/Supabase can come later only after the local loop is stable.
- Lane Scheduler: deterministic policy layer for lane enablement, cooldowns, retries, concurrency, disabled lanes, and human stops.
- Worker Protocol: every managed worker turn ends with a schema-valid `WORKER_RESULT`.
- Event Collector: stores App Server thread/turn/item events as telemetry and uses completed items as authoritative evidence.
- Evidence/Artifact Index: records changed files, commands, tests, screenshots, GLBs, previews, hashes, source URLs, and download provenance.
- Safety Policy: protects proxy budget, prevents direct ChatGPT app automation, blocks dangerous auto commands, and keeps App Server local-only.
- Dashboard/CLI: starts as `status/lanes/tasks/threads/artifacts`, then grows into a lightweight dashboard.

## Non-Negotiable Safety Boundaries

1. Do not target the ChatGPT macOS app with Computer Use. The local finding says `com.openai.chat` is blocked by target-app safety policy. Use browser extraction, official APIs, or exported transcripts instead.
2. Do not expose App Server or any control WebSocket beyond loopback. Prefer stdio/local socket. If WebSocket is used, bind `127.0.0.1` and require auth.
3. Do not use App Server `thread/shellCommand` from the scheduler. Treat it as user-initiated, full-access shell only.
4. Do not change system proxy, Clash Verge settings, shell profiles, or Codex network settings for downloads.
5. For downloads, use command-local proxy disabling and provenance logs. Single file over 1GB requires explicit user confirmation.
6. Push, merge, deploy, publish, paid asset purchase, and destructive deletion require human confirmation.
7. Game lane can be enabled for this project only through explicit lane config. Disabled lanes must never dispatch.

## System Of Record

Use SQLite as the first registry:

- `repos`: repo id, path, default branch, role.
- `lanes`: lane id, title, state, concurrency, auto_continue, safety policy, owner.
- `tasks`: unit of work, state, priority, dependencies, associated thread/worktree, current turn, retry counters, blocked reasons.
- `threads`: Codex thread id, lane, task, status, last event, archive status.
- `turns`: turn id, method, prompt hash, output schema, lifecycle status.
- `codex_events`: raw event stream, parsed item type, timestamps, thread/turn relation.
- `artifacts`: paths, URLs, hashes, type, producer task, validation status.
- `evidence_items`: command logs, screenshots, test results, metrics, source citations.
- `task_dependencies`: explicit DAG edges.
- `downloads`: source URL, command, proxy status proof, size, hash, retained path.

## Lane Model

Initial lanes:

| Lane | State | Purpose | First Evidence |
| --- | --- | --- | --- |
| `controller-core` | enabled | Build managed Codex control plane from Pro plan | schema, registry, scheduler tests |
| `research-current-best-practices` | enabled | Keep latest Unity/Three/Blender/OpenAI/community MCP research current | dated source matrix |
| `unity-agent-mcp` | paused until editor verified | Validate official Unity AI MCP and community Unity MCPs | disposable Unity project logs |
| `threejs-playable-runtime` | enabled | Turn P0/P2/P5/P26 into reusable web playable validators | browser screenshots, GLB parse JSON |
| `asset-generation` | enabled | OpenAI image references -> TRELLIS/TripoSR/Hunyuan3D -> GLB -> validation | GLB, preview, readback, hashes |
| `blender-authoring` | paused until Blender host verified | Use Blender MCP for cleanup, materials, screenshots, GLB export | MCP logs, blend/glb, screenshot |
| `game-design` | enabled | Convert P0 excitement into child-friendly GDD and prototype spec | GDD, loop mapping, asset list |
| `game-prototype` | enabled after design gate | Build P1 playable slice in Three.js first, Unity after MCP works | runnable prototype, automated playthrough |
| `qa-evidence` | enabled | Standardize validation, review packets, regression gates | test command, fixtures, release packet |
| `download-provenance` | enabled | Enforce no-proxy and source snapshot policy | download log, lsof proof, hashes |
| `infra-map` | enabled | Maintain Mac/YogaS2/HomePC roles and SSH/runtime facts | machine registry, command probes |

Recommended lane states:

- `enabled`: scheduler can dispatch if policy passes.
- `paused`: no new dispatch, existing work may finish.
- `disabled`: hard stop. No dispatch.
- `draining`: finish current work, then pause.
- `error`: blocked by system or safety error.

## Task State Machine

Task states:

- `queued`: ready to dispatch.
- `dispatching`: scheduler is creating/resuming a thread, duplicate dispatch guard active.
- `planning`: worker is understanding scope.
- `running`: worker is changing or validating.
- `waiting_approval`: external approval needed.
- `waiting_user`: human input needed.
- `blocked`: cannot proceed until blocker resolved.
- `review_ready`: output needs review before continuation.
- `task_complete`: done criteria met.
- `needs_retry`: retry allowed by policy.
- `interrupted`: scheduler or user interrupted the turn.
- `failed`: terminal failure.
- `archiving`: thread/artifacts being closed out.
- `archived`: closed.

Scheduler rule: never dispatch only because a thread looks idle. It must check lane state, task state, dependencies, cooldown, retry count, current turn state, per-lane concurrency, per-repo write lock, and the last `WORKER_RESULT.next_action`.

## Worker Result Contract

Every managed worker turn must finish with JSON matching this logical shape:

```json
{
  "schema_version": "1.0",
  "task_id": "game-design-p1-gdd",
  "lane_id": "game-design",
  "repo_id": "ai-game-generation-research",
  "thread_id": "optional-codex-thread-id",
  "turn_id": "optional-turn-id",
  "status": "done",
  "summary": "Short human-readable result.",
  "work_performed": ["Concrete action"],
  "files_changed": [
    {
      "path": "/absolute/path",
      "change_type": "created|modified|deleted",
      "notes": "Why it changed"
    }
  ],
  "commands_run": [
    {
      "command": "npm test",
      "cwd": "/absolute/path",
      "status": "passed|failed|skipped",
      "notes": "Important output"
    }
  ],
  "tests": [
    {
      "name": "playwright-smoke",
      "status": "passed|failed|skipped",
      "evidence": "/absolute/path/to/log-or-screenshot"
    }
  ],
  "evidence": [
    {
      "type": "doc|log|screenshot|asset|hash|source",
      "path_or_url": "/absolute/path/or/url",
      "notes": "What this proves"
    }
  ],
  "risks": ["Known residual risk"],
  "blockers": [],
  "needs_human": false,
  "human_question": null,
  "next_action": {
    "recommended_state": "review|archive|queue_next_turn|retry|wait_for_human|stop",
    "prompt": "Optional next prompt"
  }
}
```

If the result is missing, invalid JSON, lacks evidence, or says `needs_human: true`, the scheduler must stop automatic continuation.

## Implementation Phases

### Phase 0 - Freeze And Baseline

Goal: preserve the existing controller behavior and evidence before changing it.

Tasks:

- Snapshot current controller state/logs from the machine where `codex_managed_controller.py` lives.
- Record active lanes, active threads, and auto-dispatch behavior.
- Confirm game lane and any risky lane are disabled until explicitly enabled.
- Store extracted transcript hash and provenance in the repo.

Done when:

- Existing watcher still works.
- There is a backup state file and a baseline event log.
- We can answer: which threads exist, which lane owns them, and why they can or cannot dispatch.

### Phase 1 - Registry And Config

Goal: create the fact source without changing dispatch behavior.

Tasks:

- Add `config/lanes.yaml`.
- Add SQLite schema and migration command.
- Import current state JSON into registry tables.
- Add read-only CLI: `codex-managed status`, `lanes`, `tasks`, `threads`.
- Add lane config for the research/game lanes listed above.

Done when:

- CLI explains active lanes/tasks/threads.
- Restarting the controller does not lose state.
- Disabled lanes remain non-dispatchable.

### Phase 2 - Schema-Driven App Server Client

Goal: stop guessing App Server methods.

Tasks:

- Generate TypeScript schema or JSON Schema bundle from the installed Codex App Server.
- Build a small client wrapper for `thread/list`, `thread/read`, `thread/start`, `thread/resume`, `thread/fork`, `turn/start`, `turn/steer`, `turn/interrupt`, `thread/archive`, and `review/start`.
- Gate experimental methods behind explicit config.
- Add fake App Server tests for request validation and event parsing.

Done when:

- Invalid request shapes fail before dispatch.
- Fake server tests cover successful start, failure, interrupt, timeout, and archive.
- No scheduler code directly constructs unvalidated JSON-RPC payloads.

### Phase 3 - Worker Result And Scheduler Policy

Goal: make auto-continuation deterministic.

Tasks:

- Add `schemas/worker_result.schema.json`.
- Use `turn/start.outputSchema` where available.
- Parse final worker result and write it to registry.
- Implement scheduler policy: lane state, dependencies, cooldown, max retries, concurrency, per-repo write lock, duplicate dispatch guard, `needs_human`, and blocked states.

Done when:

- A worker with invalid output does not auto-continue.
- A blocked or human-needed worker does not auto-continue.
- A failed worker retries only within policy.
- A completed worker either archives or moves to review based on `next_action`.

### Phase 4 - Evidence And Artifacts

Goal: make every result auditable.

Tasks:

- Add artifact and evidence index commands.
- Require each research task to cite source URLs and local docs.
- Require each game/asset task to write hashes, screenshots/previews, and validation logs.
- Add source download registry and no-proxy evidence capture.

Done when:

- Each task can show evidence paths and validation status.
- No large download lacks source, size, hash, and no-proxy proof.
- Game artifacts are not considered valid just because files exist; they need validators.

### Phase 5 - Review, Interrupt, Archive

Goal: manage lifecycle safely.

Tasks:

- Add `turn/interrupt` policy for timeout, stalled worker, or explicit user stop.
- Add `review/start` integration for code changes and release packets.
- Add `thread/archive` only after artifacts and worker result are indexed.
- Add closeout report generation per task.

Done when:

- A timed-out worker is interrupted and marked with evidence.
- Review is started for nontrivial file changes.
- Archived threads are discoverable through registry.

### Phase 6 - Custom Agents And Skills

Goal: convert repeated workflows into reusable capabilities.

Tasks:

- Define custom agent profiles for `repo_explorer`, `implementation_worker`, `reviewer`, `test_mapper`, `asset_pipeline_worker`, `game_designer`.
- Promote proven experiment patterns into skills:
  - Three.js GLB playable validator.
  - TRELLIS mesh-only asset validation.
  - Godot scene CI/reviewer packet.
  - Download no-proxy provenance.
  - Current best-practice research packet.
- Keep `max_threads` conservative and `max_depth = 1` until scheduling is stable.

Done when:

- Repeat work can be dispatched with a short task prompt and stable output expectations.
- Skills include command templates, required evidence, and failure modes.

### Phase 7 - Dashboard And Heartbeats

Goal: make the system understandable at a glance.

Tasks:

- Add local dashboard or Markdown report that shows lanes, tasks, active threads, blockers, recent artifacts, and pending human decisions.
- Add heartbeat automation for periodic status refresh, not as the scheduler itself.
- Add daily research refresh option for fast-moving tools.

Done when:

- User can see what is running, blocked, done, or waiting.
- Heartbeat reports do not dispatch unsafe work by themselves.

### Phase 8 - Game Chain Full Pass

Goal: produce a better game through the managed pipeline.

Tasks:

- Convert P0 into a P1 design spec.
- Build P1 child-friendly playable slice in Three.js first.
- Use OpenAI image generation for concept art, style sheet, UI/icon direction, and orthographic asset references.
- Generate 3D assets through TRELLIS/TripoSR/Hunyuan3D candidates on HomePC.
- Clean and preview assets through Blender MCP once Blender is available.
- Import assets into Three.js validators and eventually Unity once Unity MCP is runnable.
- Add automated playthrough and visual smoke tests.
- Package a release packet: playable URL/path, source, assets, hashes, screenshots, known limitations.

Done when:

- The game has a playable loop beyond P0 quality, with authored or AI-generated assets tracked by provenance.
- It can be started locally by a simple command or file open.
- It has automated evidence for loading, movement, interaction, finish condition, and visual nonblankness.

## Current Game Development Direction

The original P0 game is valuable because it proved the emotional loop: a child can ask ChatGPT for a game, open one HTML file, and feel immediate creation power.

For the next version, preserve the energy but change the production model:

- Keep: first/third-person exploration, immediate feedback, pickups, upgrades, map navigation, HUD, skin/cosmetic reward, fast restart.
- Replace: tactical shooting theme as the core loop.
- New candidate loop: `lobby -> explore -> collect -> solve/avoid -> upgrade/cosmetic -> finish`.
- Candidate theme: robot/rover exploration, space hangar, island obstacle course, battery collection, friendly drones, puzzle hazards.

P1 playable slice:

- One small 3D level.
- Player movement and camera.
- Three collectible objectives.
- One nonviolent hazard or NPC-equivalent.
- One upgrade or cosmetic unlock.
- One finish pad.
- HUD and simple result screen.
- At least one AI-generated GLB validated through Three.js parser.

## Research Lanes And First Tasks

### Current Best Practices Research

Task `research-current-001`:

- Build a dated matrix for official Unity AI/MCP, community Unity MCPs, Blender MCP, Three.js GLB workflows, OpenAI image generation, TRELLIS/TripoSR/Hunyuan3D, and OpenGame.
- For each tool: source URL, last activity/currentness, install size, license, required accounts, local/offline behavior, proxy risk, evidence status.

Done when:

- Matrix is saved in `docs/`.
- Each row says `adopt`, `probe`, `defer`, or `reject`.

### Unity Agent MCP

Task `unity-mcp-001`:

- Verify whether Unity Hub/Editor exists on Mac, HomePC, or YogaS2.
- If absent, document install options and estimate download sizes before downloading.
- Do not download Unity Editor packages until the no-proxy strategy is verified for that installer.

Task `unity-mcp-002`:

- Compare official Unity AI MCP with community candidates on scene mutation, scripts, play mode, logs, screenshots, undo safety, package friction, and account gating.

Task `unity-mcp-003`:

- After a Unity host is available, create a disposable project and run one minimal MCP action: create scene object, add component/script, enter play mode or capture log/screenshot.

### Three.js Runtime

Task `threejs-001`:

- Turn P0 into a smoke-tested baseline: load, enter game, canvas nonblank, HUD present, basic input accepted.

Task `threejs-002`:

- Promote P2/P5/P26 GLB parsing into a reusable `three-glb-playable-validator`.

Task `threejs-003`:

- Build P1 prototype in a modular Three.js app before Unity is ready.

### Asset Generation

Task `asset-001`:

- Define prompt templates for OpenAI image references: concept sheet, orthographic asset sheet, UI icon sheet, texture/style references.

Task `asset-002`:

- Standardize TRELLIS mesh-only pipeline: image -> GLB -> trimesh readback -> Three.js readback -> preview -> hash.

Task `asset-003`:

- Attack textured TRELLIS export blocker or document a fallback using mesh-only plus Blender/OpenAI texture direction.

### Blender Authoring

Task `blender-001`:

- Locate or install Blender under no-proxy/download policy.

Task `blender-002`:

- Run Blender MCP minimal operation: create object, assign material, export GLB, screenshot viewport.

Task `blender-003`:

- Clean P26 mesh asset into a game-ready visual mesh plus separate proxy collider.

### Game Design

Task `game-design-001`:

- Write one-page P1 GDD with target audience, core loop, moment-to-moment actions, win/lose conditions, three-level pacing, reward/cosmetic loop, and P0 feature mapping.

Task `game-design-002`:

- Produce asset list and style guide, including which assets should be primitive, generated image, generated GLB, or authored cleanup.

### QA And Evidence

Task `qa-001`:

- Define evidence gate for playable prototypes: load, nonblank, input, collect, hazard interaction, finish, screenshot, hash, test log.

Task `qa-002`:

- Build release packet template for game experiments.

## Current Multi-Agent Dispatch

Already dispatched this turn:

- `019e1a5a-2eb0-74f2-9957-3c93782688dc`: controller/control-plane explorer.
- `019e1a5a-5d2b-7e91-ae2f-fb1529989328`: Unity/asset/toolchain explorer.
- `019e1a5a-89c7-7be2-be57-f7cb6b9ce98a`: P0 game baseline/game-dev explorer.

Their findings are integrated into this plan:

- Controller: build the managed control plane around registry, schema, scheduler, worker result, evidence, review, and archive.
- Toolchain: Three.js is currently the most mature playable validation lane; Unity is not live until Editor/MCP is verified; HomePC is the GPU asset host; TRELLIS mesh-only is real but textured export is blocked; Blender MCP source is available but needs host validation.
- Game: P0 is playable and emotionally successful, but not productionized. The next version should keep feedback density while moving to a child-friendly exploration/collection loop.

## Next Worker Prompts

Use these as first managed-worker prompts once registry/scheduler exists. Until then, they can be run manually as bounded Codex threads.

### Worker: Controller Core

Scope:

- Files under `tools/managed_codex/`, `config/`, and `schemas/`.

Prompt:

```text
Implement Phase 1 of the managed Codex control plane. Add lanes.yaml, SQLite schema, migration/init command, and read-only CLI commands status/lanes/tasks/threads. Do not change existing watcher dispatch behavior. End with WORKER_RESULT JSON and include commands/tests/evidence.
```

### Worker: Current Research

Scope:

- `docs/` only.

Prompt:

```text
Create a dated current-best-practices matrix for Unity AI/MCP, community Unity MCPs, Blender MCP, Three.js GLB workflows, OpenAI image generation, TRELLIS/TripoSR/Hunyuan3D, and OpenGame. Use official sources where possible and cite URLs. Mark each candidate adopt/probe/defer/reject. Do not download files. End with WORKER_RESULT JSON.
```

### Worker: Three.js QA

Scope:

- `experiments/game_p0_chatgpt_html_baseline_20260509/` and new validator code under `tools/`.

Prompt:

```text
Add automated smoke evidence for P0: load the HTML game, start the game, verify canvas is nonblank, HUD exists, and basic input is accepted. Preserve original 14.html. Save screenshots/logs/hashes under the experiment outputs directory. End with WORKER_RESULT JSON.
```

### Worker: Game Design

Scope:

- New doc under `docs/` and optional experiment spec under `experiments/game_p1_child_friendly_playable_slice_*/`.

Prompt:

```text
Write the P1 child-friendly game design spec derived from P0. Preserve the excitement loop but replace tactical shooting with exploration/collection/avoidance/puzzle hazards. Include feature mapping from P0, asset list, scene schema sketch, and acceptance tests. End with WORKER_RESULT JSON.
```

### Worker: Asset Pipeline

Scope:

- `docs/`, `tools/`, and new experiment template only.

Prompt:

```text
Standardize the image-to-GLB validation pipeline based on P26: input image, generated GLB, trimesh readback, Three.js GLTFLoader readback, preview image, SHA256 hashes, and limitations. Do not download models or files over 1GB. End with WORKER_RESULT JSON.
```

## 30 / 60 / 90 Minute Execution Plan

### First 30 Minutes

- Create this plan document.
- Freeze current understanding of Pro transcript and subagent findings.
- Draft `lanes.yaml` content but do not wire scheduler yet.
- Pick the first implementation worker: `controller-core Phase 1`.

### First 60 Minutes

- Implement registry MVP and read-only CLI.
- Create `worker_result.schema.json`.
- Create a research matrix doc shell with current citations.
- Add P0 smoke-test task spec.

### First 90 Minutes

- Add fake App Server tests.
- Add scheduler policy tests for disabled lane, retry, cooldown, duplicate dispatch, `needs_human`, invalid worker result.
- Start first manual worker run for `game-design-001` or `threejs-001`.
- Produce a dashboard/status report from registry.

## Definition Of Done For The Whole Program

The full program is working when:

1. The controller can answer active lanes, tasks, threads, approvals, archives, and why a lane is or is not dispatchable.
2. Restarting the controller does not duplicate dispatch and recovers thread state.
3. Every worker completion has schema-valid result, evidence, commands, tests, and next action.
4. Timeout, failed retry, blocked, `needs_human`, and disabled lane behavior are deterministic.
5. Safety boundaries are enforced: no exposed control server, no direct ChatGPT app automation, no unsafe shell automation, no proxy-budget leaks, no large unapproved downloads.
6. Unity, Three.js, Blender, OpenAI image, and AI asset tools each have current research notes and a clear status: live, blocked, probe, or defer.
7. P0 has automated evidence.
8. P1 has a child-friendly design spec, asset plan, and playable slice.
9. AI-generated assets have provenance, hashes, preview, parser readback, and known limitations.
10. The user can inspect one dashboard or report and understand what is running, what is blocked, and what should happen next.

