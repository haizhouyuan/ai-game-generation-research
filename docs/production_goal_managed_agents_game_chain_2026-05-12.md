# Production Goal: Managed Agents Game Generation Chain - 2026-05-12

## Goal

Build the managed-agents system to production-grade acceptance level, then use it to drive a complete AI-assisted game development chain.

The final outcome is not only research notes or isolated experiments. The system should be able to:

1. Run multiple managed Codex agents with deterministic orchestration, evidence, safety controls, and resumable task state.
2. Continuously research and adopt current best practices across Unity, Three.js, Blender, OpenAI image generation, image-to-3D, texture generation, and community MCP/tooling.
3. Turn the existing ChatGPT-generated single-file HTML game into a better game demo with higher-quality 3D assets, stronger engine architecture, improved gameplay, and verifiable playability.
4. Produce a repeatable game-generation workflow that can go from design intent to playable demo with tracked assets, tests, provenance, and release evidence.

## Production Acceptance For Managed Agents

Managed agents reach production-grade when:

- There is a registry-backed source of truth for lanes, tasks, threads, turns, artifacts, evidence, and blockers.
- The scheduler is deterministic: no duplicate dispatch, no unsafe auto-continuation, no disabled-lane dispatch, and no silent retries.
- Every worker returns schema-valid `WORKER_RESULT` with files, commands, tests, evidence, blockers, risks, and next action.
- The controller can start, resume, steer, interrupt, review, and archive worker threads through validated Codex App Server or SDK calls.
- Work is isolated by worktree/task ownership where appropriate.
- All outputs are auditable through logs, hashes, screenshots, asset readbacks, command results, and source citations.
- Human approval is required for destructive, externally visible, expensive, or proxy-sensitive actions.
- The system can survive restart and explain current state: active work, queued work, blocked work, completed work, and why each lane can or cannot dispatch.

## Game Chain Acceptance

The game-generation chain is considered complete when it can produce a demo that improves on the original `14.html` prototype in these dimensions:

- Better 3D asset quality: generated or authored GLB assets with provenance, previews, hashes, and parser/readback validation.
- Better visual consistency: concept art, style sheet, UI/icon direction, texture/material strategy, and asset naming conventions.
- Better engine structure: modular game code or engine project rather than one large unstructured HTML file.
- Better gameplay: a clear loop, goal, progression, feedback, replayability, and child-friendly theme replacing tactical shooting as the core fantasy.
- Better validation: automated load/play smoke tests, nonblank visual checks, input replay or equivalent, finish condition proof, and release packet.
- Better toolchain: Unity path researched and validated when possible; Three.js remains the fast playable path; Blender and asset generators are integrated where they add real value.

## Target Demo

The next flagship demo should be a P1 game derived from the emotional success of the original HTML game:

- Keep the immediate joy of "I asked AI and got a playable game."
- Keep first/third-person 3D exploration, pickups, upgrades, cosmetics, HUD, and quick feedback.
- Replace the combat-centered loop with a child-friendly exploration/collection/puzzle/avoidance loop.
- Use AI-generated visual assets where they genuinely improve the experience.
- Run locally with a simple command or file open.
- Ship with a release packet containing source, assets, screenshots, validation logs, hashes, known limitations, and next improvements.

## Work Lanes

The production goal is divided into these lanes:

1. `controller-core`: production managed-agents controller.
2. `research-current-best-practices`: continuous current tooling research.
3. `unity-agent-mcp`: Unity Agent/MCP/editor integration.
4. `threejs-playable-runtime`: fast browser playable path and validators.
5. `asset-generation`: OpenAI image, TRELLIS/TripoSR/Hunyuan3D-style 3D asset pipeline.
6. `blender-authoring`: asset cleanup, materials, screenshots, GLB export through Blender/MCP.
7. `game-design`: P1 child-friendly game design and asset plan.
8. `game-prototype`: playable demo implementation.
9. `qa-evidence`: automated evidence, review packets, release packets.
10. `download-provenance`: no-proxy, size, hash, and source governance.

## Immediate Execution Order

1. Build the managed-agents foundation first: lanes config, SQLite registry, worker result schema, scheduler policy, evidence index.
2. In parallel, keep the game path alive through Three.js because it is already the most verified playable path.
3. Treat Unity as a strategic engine lane, but do not depend on it until Editor/MCP/account/download constraints are actually verified.
4. Promote existing experiments into reusable validators before creating more one-off demos.
5. Use HomePC for GPU asset generation, Mac for Codex/controller/playable inspection, and YogaS2/MAINT for infrastructure/context facts.

