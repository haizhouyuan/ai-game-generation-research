# Gemini Worker Guide

Use this repository as a scoped planning/review workspace unless a prompt explicitly gives a write scope.

## Primary Role

Gemini is preferred for:

- broad research synthesis;
- plan review;
- task packet critique;
- visual/product critique;
- independent sanity checks before Codex merges work.

Use `gemini-3.1-pro-preview` for this project unless a task explicitly asks for a different model.

## MCP Tools

Project MCP configuration is in `.gemini/settings.json`.

Available MCP servers:

- `managed-artifact-verifier`
- `managed-game-factory`

Use `managed-game-factory` to inspect task packets, repo status, asset packet readiness, and download-record compliance.

## Skills

The local 3D asset factory skill has been linked into Gemini skills:

`local-3d-asset-factory-orchestrator`

Use it for visual-upgrade planning, task packet critique, no-proxy download discipline, and local/remote model routing.

## Rules

- Do not read secrets.
- Do not install packages or download large files unless explicitly authorized.
- Do not modify global proxy configuration.
- Do not commit or push.
- Treat `tasks/visual_upgrade/` files as the authoritative worker packets.
- Treat the current final packet as preserved baseline unless the task says otherwise.

## Active Goal

`docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`

Read first:

1. `docs/chatgpt_pro_full_asset_factory_followup_2026-05-13.md`
2. `tasks/pubg_like_full_rebuild/README.md`
3. `experiments/pubg_like_asset_factory_20260513/reports/hunyuan3d_env_report.md`
4. `docs/coding_runner_mcp_skill_control_2026-05-13.md`

The old Three.js final packet is the playable baseline, not completion. The active target is a full local AI 3D asset factory with per-asset reference -> 3D/PBR -> Blender -> Three.js evidence. Use `gemini-3.1-pro-preview` for review/research tasks.
