# Agent Guide

## Start Here

Read these files in order:

1. `README.md`
2. `docs/chatgpt_pro_github_review_brief_2026-05-13.md`
3. `docs/chatgpt_pro_full_asset_factory_followup_2026-05-13.md`
4. `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
5. `tasks/pubg_like_full_rebuild/README.md`
6. `experiments/pubg_like_asset_factory_20260513/reports/hunyuan3d_env_report.md`
7. `experiments/tactical_game_full_realism_final_20260513/README.md`
8. `experiments/tactical_game_full_realism_final_20260513/report.md`

For managed-agent/controller work, also read:

1. `WORKFLOW.md`
2. `docs/symphony_alignment_2026-05-12.md`
3. `docs/PRD.md`
4. `docs/pipeline_map.md`
5. `docs/source_registry.md`
6. `docs/experiment_backlog.md`

For local AI 3D asset factory / tactical visual upgrade work, also read:

1. `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
2. `tasks/pubg_like_full_rebuild/README.md`
3. `docs/coding_runner_mcp_skill_control_2026-05-13.md`
4. `docs/asset_packet_validation_2026-05-13.md`
5. `docs/asset_registry_v3_gate_2026-05-13.md`
6. `docs/texture_quality_gate_2026-05-13.md`
7. `docs/runner_control_readiness_2026-05-13.md`
8. `docs/yoga_mcp_skill_reference_mapping_2026-05-13.md`
9. `config/lanes_visual_upgrade_2026-05-13.yaml`
10. `tasks/visual_upgrade/README.md`

## Rules

- Keep research evidence in docs.
- Keep experiments reproducible with commands and artifact paths.
- Do not upload private material without explicit approval.
- Do not claim a tool works until a local run or documented hosted run has evidence.
- Keep large generated assets out of git unless a storage policy is added.
- For any large model or checkpoint download, follow the repo no-proxy evidence discipline in `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md` and `tools/no_proxy_download.sh`.
- Treat older dated docs as historical unless the current review brief or final experiment README points to them.
- For this active asset-factory goal, large model downloads are authorized when necessary, but over 100MB still requires command-local no-proxy evidence and over 1GB requires URL/version/size/hash evidence. Do not use paid proxy traffic.
