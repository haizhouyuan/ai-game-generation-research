# P21-A Game Scene-CI Modes Review Packet

Status: `P21 Game complete / program active`.

## Scope

P21 extends the P20 reusable scene-CI wrapper with explicit command modes:

- `match`: current compact hashes must match the accepted baseline.
- `diff`: synthetic hash drift must be detected.
- `candidate-update`: an allowlisted baseline id may write a review candidate.
- `denied-update`: an unlisted baseline id must be denied.

It also writes a compact baseline-update review packet.

## Command

```bash
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p21_scene_ci_modes_review_packet_20260512
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "rm -rf '$REMOTE' && mkdir -p '$REMOTE'"
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "mkdir -p '$REMOTE/project/outputs' && cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/scene_ci_negative_fixtures_with_manifest.gd > '$REMOTE/project/outputs/godot_p21_scene_ci_modes_review_packet.log' 2>&1"
scp yuanhaizhou@192.168.1.17:"$REMOTE/project/outputs/p18_negative_scene_ci_full_report.json" "$LOCAL/outputs/p21_negative_scene_ci_full_report.json"
scp yuanhaizhou@192.168.1.17:"$REMOTE/project/outputs/godot_p21_scene_ci_modes_review_packet.log" "$LOCAL/outputs/godot_p21_scene_ci_modes_review_packet.log"
python3 -m py_compile "$LOCAL/run_scene_ci_modes_review_packet.py"
python3 "$LOCAL/run_scene_ci_modes_review_packet.py" all > "$LOCAL/run.log" 2>&1
```

## Evidence

- Runner: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/run_scene_ci_modes_review_packet.py`
- Mode report: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_scene_ci_modes_report.json`
- Match mode report: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_mode_match_report.json`
- Diff mode report: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_mode_diff_report.json`
- Candidate-update mode report: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_mode_candidate_update_report.json`
- Denied-update mode report: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_mode_denied_update_report.json`
- Review packet: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_baseline_update_review_packet.md`
- Diff table: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_compact_diff_table.md`
- Hash ledger: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/artifact_hashes.json`
- Fresh verification log: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/verify_run.log`

## Result

Checks:

```json
{
  "full_summary_pass": true,
  "selected_modes_pass": true,
  "match_mode_pass": true,
  "diff_mode_detects_drift": true,
  "candidate_update_allowlisted": true,
  "denied_update_denied": true,
  "review_packet_emitted": true
}
```

All four modes passed in the same command run. The compact review packet links the mode evidence and preserves the no-visual/no-mesh boundary.

## Boundaries

- Proxy scene nodes plus headless physics/input/camera evidence remain the authority.
- Candidate update is review-only, not automatic accepted-baseline replacement.
- Screenshot/visual QA and mesh-accurate GLB collision remain unclaimed.
