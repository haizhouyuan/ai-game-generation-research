# Final Release Read-Only Review Prompt

You are reviewing the tactical visual upgrade release packet. Do not modify files.

## Goal

Check whether the release packet is honest, evidence-backed, and aligned with:

`docs/production_goal_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`

## Read These Files

- `experiments/tactical_game_visual_upgrade_20260520/visual_upgrade_report.md`
- `experiments/tactical_game_visual_upgrade_20260520/README.md`
- `experiments/tactical_game_visual_upgrade_20260520/reports/pbr_pipeline_benchmark_2026-05-13.md`
- `experiments/tactical_game_visual_upgrade_20260520/reports/visual_evidence_gate_2026-05-13.md`
- `experiments/tactical_game_visual_upgrade_20260520/reports/hero_rifle_v2_2026-05-13.md`
- `experiments/tactical_game_visual_upgrade_20260520/assets/asset_registry_v2.json`
- `docs/runner_control_readiness_2026-05-13.md`

## Review Questions

1. Does the report overclaim anything compared with the evidence?
2. Are W8 route states described honestly?
3. Does the runner routing rule match the user's preference: Kimi/Gemini for complex review/implementation, Gemini with `gemini-3.1-pro-preview`, MiniMax only for narrow mechanical work?
4. Are the remaining limitations clear enough for a human reviewer?
5. Is there any blocker that should prevent calling the current packet a completed release packet, while still acknowledging future production work?

## Output Format

Return:

- `VERDICT: APPROVE`, `APPROVE_WITH_FIXES`, or `BLOCK`
- Findings, ordered by severity
- Required fixes, if any
- Optional suggestions
