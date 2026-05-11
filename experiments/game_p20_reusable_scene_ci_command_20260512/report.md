# P20-A Game Reusable Scene-CI Command

Status: `P20 Game complete / program active`.

## Scope

P20 wraps the P19 accepted-baseline hash regression into a reusable scene-CI command:

- derives compact trace hashes from a HomePC Godot headless full report;
- compares positive layout and negative fixture hashes against an accepted baseline;
- writes a compact human-readable diff table;
- supports allowlisted baseline update candidates;
- denies unlisted baseline update ids.

This remains proxy scene nodes plus headless physics/input/camera assertions. It is not screenshot/visual QA and not mesh-accurate GLB collision.

## Command

```bash
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p20_reusable_scene_ci_command_20260512
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p20_reusable_scene_ci_command_20260512
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "rm -rf '$REMOTE' && mkdir -p '$REMOTE'"
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "mkdir -p '$REMOTE/project/outputs' && cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/scene_ci_negative_fixtures_with_manifest.gd > '$REMOTE/project/outputs/godot_p20_reusable_scene_ci_command.log' 2>&1"
scp yuanhaizhou@192.168.1.17:"$REMOTE/project/outputs/p18_negative_scene_ci_full_report.json" "$LOCAL/outputs/p20_negative_scene_ci_full_report.json"
scp yuanhaizhou@192.168.1.17:"$REMOTE/project/outputs/godot_p20_reusable_scene_ci_command.log" "$LOCAL/outputs/godot_p20_reusable_scene_ci_command.log"
python3 -m py_compile "$LOCAL/run_scene_ci_command.py"
python3 "$LOCAL/run_scene_ci_command.py" --write-baseline-candidate > "$LOCAL/run.log" 2>&1
```

## Evidence

- Runner: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p20_reusable_scene_ci_command_20260512/run_scene_ci_command.py`
- Baseline: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p20_reusable_scene_ci_command_20260512/baseline/accepted_p19_scene_ci_baseline.json`
- Update allowlist: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p20_reusable_scene_ci_command_20260512/baseline/baseline_update_allowlist.json`
- Regression report: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p20_reusable_scene_ci_command_20260512/outputs/p20_scene_ci_regression_report.json`
- Human diff table: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p20_reusable_scene_ci_command_20260512/outputs/p20_compact_human_diff_table.md`
- Baseline update policy check: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p20_reusable_scene_ci_command_20260512/outputs/p20_baseline_update_policy_check.json`
- Candidate baseline update: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p20_reusable_scene_ci_command_20260512/outputs/p20_allowed_baseline_update_candidate.json`
- Fresh verification log: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p20_reusable_scene_ci_command_20260512/verify_run.log`

## Result

Checks:

```json
{
  "full_summary_pass": true,
  "positive_hashes_match_baseline": true,
  "negative_hashes_match_baseline": true,
  "diff_table_emitted": true,
  "allowlisted_update_allowed": true,
  "unlisted_update_denied": true
}
```

The compact table showed all three positive layouts and all five negative fixtures matching the accepted P19 baseline. The allowlisted baseline id can write a candidate update file; the unlisted counter remains denied.

## Boundaries

- The command wraps deterministic headless scene-CI evidence only.
- Baseline updates are candidate files, not automatic replacement of the accepted baseline.
- Screenshot/visual QA and mesh-accurate GLB collision remain unclaimed.
