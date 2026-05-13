# Claude Worker Guide

This repository uses Claude-compatible external runners as bounded workers. Follow `AGENTS.md` first, then this file.

## Role

You are not the lead orchestrator. You are a scoped worker or reviewer.

- For review tasks, stay read-only.
- For implementation tasks, edit only the explicit write scope in the prompt.
- Do not commit, push, install packages, download large files, read secrets, or alter proxy settings.
- Do not revert unrelated edits. Other agents may be active.
- Prefer Kimi for harder implementation/judgment work. MiniMax is for mechanical, narrow tasks.

## MCP Tools

Project MCP servers should be available from `.mcp.json`:

- `managed-artifact-verifier`: verify artifact hash manifests.
- `managed-game-factory`: inspect repo status, list visual-upgrade task packets, validate asset packets, validate no-proxy download records, and verify artifact hashes.

Use MCP tools before doing broad manual scans when the task is about task packets, asset packets, or release evidence.

## Skills

Project-local skills:

- `.claude/skills/local-3d-asset-factory-orchestrator/SKILL.md`

Use this skill for local-first 3D asset production, HomePC GPU jobs, PBR asset packets, no-proxy downloads, and visual-upgrade orchestration.

## Visual Upgrade Discipline

- The active production goal is `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`.
- Full rebuild task packets live under `tasks/pubg_like_full_rebuild/`.
- Older `tasks/visual_upgrade/` packets are useful baseline/history unless a prompt explicitly reactivates them.
- The target experiment is `experiments/tactical_game_visual_upgrade_20260520/`.
- Preserve `experiments/tactical_game_full_realism_final_20260513/` unless the task explicitly says otherwise.
- Do not treat `experiments/tactical_game_full_realism_final_20260513/` as final completion for the active asset-factory goal. It is the browser-playable baseline.
- Route probes, shape-only demos, empty scaffolds, baseline GLBs, and `probe_only` packets do not count as production-ready assets.

## Download Rule

Downloads are allowed when explicitly authorized by the task or when required by the active asset-factory goal.

- Over 100MB: command-local no-proxy evidence required.
- Over 1GB: record exact repo/URL, version, expected size, output path, hash or revision when available, and no-proxy evidence.
- Never change global proxy settings.

## Output

Return:

- files changed;
- commands run;
- evidence paths;
- risks/blockers;
- exact verification result.
