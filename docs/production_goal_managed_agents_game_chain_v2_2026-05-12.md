# Production Goal V2: Managed Agents First, Game Chain As Proof - 2026-05-12

## How To Use This Document

Use this file as the `/GOAL` target for the next execution run.

This document supersedes `docs/production_goal_managed_agents_game_chain_2026-05-12.md` as the operational goal. The older file remains useful as the first goal snapshot, but it did not fully capture the later decisions:

- Managed Agents is the main product, not a helper script for one game.
- The existing HTML game is a baseline sample, not the production route.
- Web/Three.js is a fast validation and preview lane, not the final engine commitment.
- Unity must be researched and locally proven as the mature game-engine lane.
- Prior experiments must be promoted into a capability library before more one-off work accumulates.
- Every failure, stall, missing evidence, or toolchain surprise must become a controller improvement item.

## Final Objective

Build a production-grade, reusable **Managed Agents control plane** that can coordinate multiple AI workers across research, implementation, asset generation, QA, and engine integration.

Use the AI game-generation project as the first high-value proving ground:

1. Preserve the original `14.html` game as an early AI-generated experience sample.
2. Extract its useful feeling: open-and-play immediacy, 3D exploration, feedback density, pickups, upgrades, HUD, fast loop, and the sense that AI produced a real game.
3. Rebuild that experience through more mature tools and workflows: Unity, generated 3D assets, Blender cleanup, texture/material strategy, provenance, automated QA, and release packets.
4. Keep Web/Three.js available only as the fastest validation, preview, and fallback path.
5. Make the Managed Agents system improve every time it is used.

The goal is not "complete a minimum task." The goal is to reach a durable production capability: a repeatable multi-agent game-development chain that can produce higher-quality demos with tracked assets, tests, evidence, and system learnings.

## Current State Snapshot

Already in place:

- Python engineering environment: `pyproject.toml`, `.venv`, editable package, `pytest`, `ruff`, `typer`, `rich`, `pydantic`, `pyyaml`, `jsonschema`.
- Managed registry MVP: lanes, tasks, threads, turns, artifacts, evidence, downloads, capabilities, controller issues.
- CLI entrypoint: `.venv/bin/codex-managed`.
- Worker result schema and validation.
- Scheduler policy and fake App Server request boundary tests.
- Initial capability registry seeded in `config/lanes.yaml`.
- Current best-practices matrix.
- P1 game design: **Rover Workshop: Battery Rescue**.
- Rover asset generation plan with OpenAI image prompts and provenance schema.
- Prototype evidence gate with G0-G4 levels.

Known incomplete or blocked items:

- Real Codex App Server integration is not connected yet.
- Event collector exists conceptually but not as a real importer.
- Controller dashboard/status report is still minimal CLI output.
- Capability entries exist, but reusable skills/templates are not yet extracted.
- Node/npm frontend toolchain is not configured; Homebrew probing caused a controller issue.
- P0 baseline has not reached automated G2 evidence.
- P1 demo has not been implemented.
- Hero rover asset has not gone through OpenAI reference -> 3D generation -> Blender cleanup -> runtime validation.
- Unity Editor/MCP host readiness is still blocked.
- Blender MCP cleanup loop is still partial.
- TRELLIS textured export is still partial.

## Non-Negotiable Principles

1. **Controller first.** The managed-agents framework is the primary deliverable. Game work is a proving ground and pressure test.
2. **Use the MVP while improving it.** Do not wait for perfect infrastructure, but every problem encountered while using it must be logged and turned into controller work.
3. **No blind retry.** A failed or unclear worker result must produce an issue, blocker, or human question, not an unbounded retry loop.
4. **Evidence over memory.** Agents should learn from registry, capability entries, artifacts, and evidence paths, not from chat recollection.
5. **HTML is baseline only.** The original `14.html` is preserved as an inspiration and benchmark. It is not the production codebase.
6. **Three.js is validator/fallback.** Use it for quick GLB parsing, previews, browser playability, and QA. Do not treat it as the final route unless it is explicitly selected later.
7. **Unity must be proven.** Unity is the mature engine path, but it cannot be promoted until a disposable local Editor/MCP loop is proven.
8. **Hero asset deep first.** Do one important asset deeply before generating many shallow assets.
9. **Generated meshes need cleanup.** Do not trust generated mesh topology, scale, materials, textures, or collision until validated.
10. **No proxy-budget surprises.** Downloads must follow command-local no-proxy governance; any single file over 1GB requires explicit approval.

## Workstreams

### 1. Controller Core

Purpose: make Managed Agents a production-grade universal control plane.

Required capabilities:

- registry-backed source of truth for lanes, tasks, threads, turns, artifacts, evidence, capabilities, downloads, controller issues;
- deterministic scheduler policy;
- schema-valid `WORKER_RESULT` required for managed worker turns;
- fake App Server test harness before real App Server calls;
- real App Server client for thread start/read/fork/resume, turn start/steer/interrupt, review, archive;
- event collector for App Server events;
- artifact/evidence indexing;
- issue/improvement log;
- dashboard or report that explains current system state.

Immediate tasks:

- Finish `controller-core-phase3`: controller issues, artifact/evidence index, event collector.
- Add `record-result` as the normal closeout path for worker outputs.
- Add event import from fake App Server first, then real App Server.
- Add dashboard/status report that answers: active, queued, blocked, completed, stale, risky, needs human.
- Add policy tests for invalid result fail-close, duplicate dispatch, cooldown, retry limit, blocked, needs-human, disabled lane.

Production acceptance:

- Controller restart does not duplicate dispatch.
- Invalid or missing worker output does not auto-continue.
- Every controller issue has id, severity, state, lane/task, symptom, root cause, improvement, evidence.
- Every worker closeout can be traced to artifacts/evidence.
- A human can inspect one report and understand what is running and why.

### 2. Capability Registry And Skill Templates

Purpose: convert prior experiments into reusable capabilities.

Initial statuses:

- Available: P0 baseline, Three.js GLB playable validator, P26 TRELLIS mesh-only GLB, Godot scene CI/reviewer packet, no-proxy download governance.
- Partial: TRELLIS textured export, Blender MCP authoring.
- Blocked: Unity Agent MCP/editor path.

Required outputs:

- capability registry entries with status, evidence paths, commands, inputs, outputs, limitations, next steps;
- stale evidence checker;
- worker-readable templates for:
  - GLB parser/playable validator;
  - asset provenance packet;
  - scene QA/release packet;
  - no-proxy governed download;
  - controller issue closeout.

Acceptance:

- An agent can ask "what can I use?" and get a capability list with evidence and limitations.
- No capability may be marked available without local or documented hosted evidence.
- Missing evidence paths fail a check.
- Reusable experiment commands are discoverable before dispatch.

### 3. Research Refresh

Purpose: keep fast-moving AI/game tooling current without derailing implementation.

Research lanes:

- OpenAI image generation and editing;
- Unity official AI/MCP and community MCPs;
- Blender MCP and Blender Python cleanup;
- TRELLIS, TripoSR, Hunyuan3D, related image-to-3D/texture tools;
- Three.js/GLB validation;
- OpenGame and other game-agent architectures.

Rules:

- Prefer official docs for official products.
- Record source URL, date, decision, and next evidence gate.
- Do not download large files during research tasks.
- Promote tools only through evidence-producing probes.

Acceptance:

- Each candidate is marked adopt, probe, defer, or reject.
- Each adopted/probed candidate has a next local validation task.
- Research never substitutes for local proof when the claim is "this chain works here."

### 4. Game Design And Experience Extraction

Purpose: preserve what made `14.html` exciting while leaving behind its production weaknesses.

Baseline role:

- `14.html` proves that prompt-to-game can create a playable emotional moment.
- It is a reference for immediacy, 3D exploration, HUD, pickups, upgrades, feedback density, and fast loop.
- It is not the game architecture to continue extending.

Target design:

- Working title: **Rover Workshop: Battery Rescue**.
- Core loop: lobby -> workshop -> explore -> collect batteries -> avoid/solve hazards -> upgrade/cosmetic -> charging pad -> result -> replay.
- Theme: child-friendly exploration and puzzle hazards, not tactical shooting.

Acceptance:

- P0 preserved and reaches automated G2 baseline evidence.
- P1 design remains source of truth for game-demo tasks.
- Any final demo must have a complete loop, not just a scene render.

### 5. Asset And 3D Generation

Purpose: prove a real asset pipeline, not just a generated mesh.

First deep asset:

- Friendly rover hero asset.

Required chain:

`P1 spec -> OpenAI image references -> TRELLIS/TripoSR/Hunyuan3D candidates -> Blender cleanup -> GLB -> Three.js validation -> Unity import`

Required provenance for each non-procedural asset:

- prompt/reference image;
- model/tool/version;
- host;
- output path;
- SHA256;
- mesh stats;
- material/texture report;
- Blender cleanup operations;
- Three.js import result;
- Unity import result when ready;
- gameplay collider/proxy strategy;
- known limitations.

Acceptance:

- Hero rover has at least one validated GLB candidate.
- Generated mesh is not used as collision; a proxy collider is defined.
- Material/texture state is explicit. Mesh-only is not called textured.
- Blender cleanup and runtime validation are recorded before demo promotion.

### 6. Unity Engine Lane

Purpose: prove the mature game-engine route.

Steps:

- Probe Mac/HomePC/Yoga for Unity Hub/Editor without triggering large downloads.
- Document version, license/account/cloud/package requirements.
- Compare official Unity AI/MCP and community Unity MCPs.
- Use a disposable project first.
- Bind editor/MCP control surfaces locally only.
- Run minimum scene mutation loop:
  - create/read/modify scene;
  - create or modify script/prefab/material;
  - read console;
  - run play mode or tests;
  - capture screenshot/log evidence.
- Import validated GLB assets into Unity after the asset chain is ready.

Promotion criteria:

- Agent can control Unity safely in a disposable project.
- Every editor action has evidence.
- No unauthenticated remote control surface exists.
- Large downloads follow no-proxy and approval policy.

### 7. QA And Release Evidence

Purpose: prevent "it looks like it works" from becoming the acceptance standard.

Gate levels:

- P0 must reach G2: load, canvas, HUD, input, screenshot, hash.
- P1 must reach G4: load, nonblank, HUD, input, pickup, hazard, puzzle/gate, finish, screenshots, hashes, asset provenance, release packet.

Release packet must include:

- source path and run command;
- screenshots;
- test logs;
- asset manifest;
- provenance files;
- SHA256 hashes;
- known limitations;
- next improvements;
- promotion decision.

Acceptance:

- Demo promotion requires evidence packet.
- Headless checks are not mislabeled as visual QA.
- Visual nonblank checks are not mislabeled as gameplay proof.

### 8. Environment And Infrastructure

Purpose: keep local machines and tools from becoming hidden blockers.

Known machine roles:

- Mac: Codex/controller/playable inspection.
- HomePC: GPU asset generation, TRELLIS/ComfyUI/heavy jobs.
- YogaS2/MAINT: infrastructure/context facts and lightweight support.

Required work:

- Keep Python controller environment reproducible.
- Treat Node/npm setup as a governed task because Homebrew discovery already caused a stall.
- Probe Unity and Blender hosts safely.
- Keep download provenance and no-proxy policy active.
- Add infra capability entries as tools become reliable.

Acceptance:

- Each toolchain has install/status evidence.
- No system proxy/Clash/Codex network settings are changed as a shortcut.
- Any failed environment probe becomes a controller issue or capability blocker.

## Milestones

### M0 - Stabilize Goal And Current Registry

Done when:

- This V2 goal exists and is used as `/GOAL`.
- `.venv/bin/python -m pytest -q` passes.
- `.venv/bin/ruff check src tests` passes.
- `.venv/bin/codex-managed status`, `capabilities`, `issues`, and `check-capabilities` run.

### M1 - Self-Improving Controller

Done when:

- Controller issue log is seeded and CLI-manageable.
- Worker results can be recorded into tasks, artifacts, and evidence.
- App Server event import has fake harness tests.
- Dashboard/status report shows active, blocked, stale, risky, and needs-human items.

### M2 - Capability Library

Done when:

- Existing P0-P27 and controller evidence are classified.
- Capability stale-path checker is part of tests or CLI checks.
- At least four worker templates exist: GLB validator, asset provenance, QA release packet, no-proxy download.

### M3 - Toolchain Readiness

Done when:

- Node/npm or equivalent frontend toolchain is installed through governed process or explicitly deferred.
- Blender host readiness is proven or blocked with evidence.
- Unity host readiness is proven or blocked with evidence.
- HomePC asset-generation path is documented as callable by managed agents.

### M4 - Hero Asset Deep Chain

Done when:

- Rover orthographic reference image is generated and hashed.
- TRELLIS and TripoSR candidates are compared, or blockers are recorded.
- Blender cleanup produces validated GLB or records blocker.
- Three.js GLTFLoader validation produces parse report and screenshot.
- Asset provenance packet is complete.

### M5 - Unity Closed Loop

Done when:

- Disposable Unity project can be controlled by selected MCP/agent route.
- Scene mutation, script/material/prefab operation, console read, play/test, screenshot/log are evidenced.
- Validated rover GLB imports into Unity with material/collider limitations recorded.

### M6 - Game Demo Release

Done when:

- Rover Workshop has a complete loop and release packet.
- The demo uses at least one validated generated/cleaned GLB hero asset.
- P1 reaches G4 QA evidence.
- The demo is clearly positioned as game-chain proof, not final product.

### M7 - Generalized Managed Agents Platform

Done when:

- The controller can run non-game lanes with the same registry/scheduler/evidence model.
- Problems discovered during work become controller issues and feed future improvements.
- App Server/SDK integration, worktree isolation, review/archive, and reporting are stable enough for repeated use.

## Immediate Next Batch

Run these in order:

1. Finish and verify this V2 goal document.
2. Re-run controller tests and capability checks.
3. Complete `controller-core-phase3`.
4. Build capability skill templates.
5. Governed Node/npm or frontend toolchain setup task.
6. P0 G2 evidence gate.
7. Hero rover asset deep chain.
8. Unity host readiness probe.

Do not start broad multi-asset generation or a polished demo until the controller can record evidence, issues, and capability status reliably.

