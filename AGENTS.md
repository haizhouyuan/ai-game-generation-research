# Agent Guide

## Start Here

Read these files in order:

1. `README.md`
2. `docs/chatgpt_pro_github_review_brief_2026-05-13.md`
3. `experiments/tactical_game_full_realism_final_20260513/README.md`
4. `experiments/tactical_game_full_realism_final_20260513/report.md`
5. `docs/production_goal_full_realistic_3d_tactical_game_final_2026-05-13.md`
6. `docs/full_realism_lessons_and_best_practices_2026-05-13.md`

For managed-agent/controller work, also read:

1. `WORKFLOW.md`
2. `docs/symphony_alignment_2026-05-12.md`
3. `docs/PRD.md`
4. `docs/pipeline_map.md`
5. `docs/source_registry.md`
6. `docs/experiment_backlog.md`

For local AI 3D asset factory / tactical visual upgrade work, also read:

1. `docs/production_goal_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`
2. `docs/implementation_plan_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`
3. `docs/runner_control_readiness_2026-05-13.md`
4. `docs/yoga_mcp_skill_reference_mapping_2026-05-13.md`
5. `config/lanes_visual_upgrade_2026-05-13.yaml`
6. `tasks/visual_upgrade/README.md`

## Rules

- Keep research evidence in docs.
- Keep experiments reproducible with commands and artifact paths.
- Do not upload private material without explicit approval.
- Do not claim a tool works until a local run or documented hosted run has evidence.
- Keep large generated assets out of git unless a storage policy is added.
- For any large model or checkpoint download, follow the HomePC mirror/cache discipline in `/vol1/maint/docs/homepc_gpu_research_executor_20260511.md`.
- Treat older dated docs as historical unless the current review brief or final experiment README points to them.
- For large downloads, follow the repo goal rule: over 100MB requires command-local no-proxy evidence; over 1GB requires explicit user approval before download.
