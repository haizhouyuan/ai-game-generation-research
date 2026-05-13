# Gemini Worker Guide

Use this repository as a scoped planning/review workspace unless a prompt explicitly gives a write scope.

## Primary Role

Gemini is preferred for:

- broad research synthesis;
- plan review;
- task packet critique;
- visual/product critique;
- independent sanity checks before Codex merges work.

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

`docs/production_goal_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`
