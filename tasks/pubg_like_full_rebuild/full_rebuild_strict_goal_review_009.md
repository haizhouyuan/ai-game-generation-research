# Runner Review Task 009 - Strict Full Rebuild Goal

## Goal

Review whether the current full rebuild plan and gates prevent a false completion for the user's clarified intent:

- not a light upgrade;
- every major visible asset rebuilt through realistic reference -> local 3D/PBR route -> Blender cleanup -> Three.js evidence;
- Hunyuan3D 2.1, ComfyUI/PBR, TRELLIS/TRELLIS.2, Blender, and runtime gates all tested;
- Codex orchestrates and routes work to Kimi/Gemini/MiniMax/HomePC instead of doing every task manually;
- large downloads are allowed but must not use paid proxy traffic.

## Read These Files

- `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
- `tasks/pubg_like_full_rebuild/README.md`
- `tools/validate_asset_packets.py`
- `docs/asset_packet_validation_2026-05-13.md`
- `experiments/pubg_like_asset_factory_20260513/references/reference_asset_matrix.md`
- `docs/coding_runner_mcp_skill_control_2026-05-13.md`

## Questions

1. What remaining loopholes could let us incorrectly call the goal complete?
2. Which next three implementation tasks should be delegated first?
3. Which task should go to Kimi, which to Gemini, and which to MiniMax?
4. Are the validator thresholds too weak, too strong, or useful as a fail-closed gate?

## Output

Save nothing. Return a concise review with:

- `verdict`
- `remaining_loopholes`
- `next_delegated_tasks`
- `runner_routing`
- `gate_recommendations`
