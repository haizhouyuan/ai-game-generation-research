# P19-A Game Accepted-Baseline Hash Regression

Status: `P19 Game complete / program active`.

## Scope

P19 turns the P18 compact trace into an accepted-baseline regression gate. It reruns the existing HomePC Godot headless negative scene-CI, rebuilds compact hashes, compares positive layout and negative fixture hashes against the accepted P18 baseline, and emits compact failure diffs for drift counters.

Authority remains proxy scene nodes plus headless physics/input/camera assertions. This does not claim screenshot/visual QA or mesh-accurate GLB collision.

## Command

```bash
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p19_accepted_baseline_hash_regression_20260512
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p19_accepted_baseline_hash_regression_20260512
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "rm -rf '$REMOTE' && mkdir -p '$REMOTE'"
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "mkdir -p '$REMOTE/project/outputs' && cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/scene_ci_negative_fixtures_with_manifest.gd > '$REMOTE/project/outputs/godot_p19_accepted_baseline_hash_regression.log' 2>&1"
scp yuanhaizhou@192.168.1.17:"$REMOTE/project/outputs/p18_negative_scene_ci_full_report.json" "$LOCAL/outputs/p18_negative_scene_ci_full_report.json"
scp yuanhaizhou@192.168.1.17:"$REMOTE/project/outputs/godot_p19_accepted_baseline_hash_regression.log" "$LOCAL/outputs/godot_p19_accepted_baseline_hash_regression.log"
python3 -m py_compile "$LOCAL/run_p19_hash_regression.py"
python3 "$LOCAL/run_p19_hash_regression.py" > "$LOCAL/run.log" 2>&1
```

## Evidence

- Baseline: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p19_accepted_baseline_hash_regression_20260512/baseline/accepted_p18_trace_hash_baseline.json`
- Runner: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p19_accepted_baseline_hash_regression_20260512/run_p19_hash_regression.py`
- Full headless report: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p19_accepted_baseline_hash_regression_20260512/outputs/p18_negative_scene_ci_full_report.json`
- Current compact trace: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p19_accepted_baseline_hash_regression_20260512/outputs/p19_current_compact_trace.json`
- Current hashes: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p19_accepted_baseline_hash_regression_20260512/outputs/p19_current_trace_hashes.json`
- Failure diff report: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p19_accepted_baseline_hash_regression_20260512/outputs/p19_compact_failure_diff_report.json`
- Hash ledger: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p19_accepted_baseline_hash_regression_20260512/outputs/artifact_hashes.json`

## Result Matrix

| Gate | Result |
|---|---:|
| Full headless report summary pass | pass |
| Accepted positive layout hashes match | pass |
| Accepted negative fixture hashes match | pass |
| Positive event-order drift counter detected | pass |
| Negative fixture missing counter detected | pass |

The accepted baseline comparison had zero positive diffs and zero negative diffs. The drift fixtures then intentionally changed compact traces:

- `positive_event_order_reversed_counter` detected `front_linear` hash drift.
- `negative_route_mismatch_fixture_missing_counter` detected missing `route_mismatch`.

## Boundaries

- This is a compact review/regression gate over deterministic headless data.
- It does not validate rendered screenshots, visual composition, human gameplay feel, or mesh-accurate GLB collision.
- The baseline is P18 accepted evidence, not an external QA authority.
