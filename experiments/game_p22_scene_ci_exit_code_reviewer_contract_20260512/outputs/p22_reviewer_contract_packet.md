# P22 Scene-CI Reviewer Contract Packet

Status: compact deterministic headless scene-CI reviewer contract.

| Mode | Observed Exit Code | Expected Example Code | Contract Pass | Evidence |
|---|---:|---:|---|---|
| `match` | 0 | 0 | True | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p22_scene_ci_exit_code_reviewer_contract_20260512/outputs/p22_human_readable_diff_table.md` |
| `diff` | 1 | 1 | True | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p22_scene_ci_exit_code_reviewer_contract_20260512/outputs/p22_human_readable_diff_table.md` |
| `candidate-update` | 0 | 0 | True | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p22_scene_ci_exit_code_reviewer_contract_20260512/outputs/p22_accepted_baseline_update_packet.json` |
| `denied-update` | 2 | 2 | True | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p22_scene_ci_exit_code_reviewer_contract_20260512/outputs/p22_rejected_baseline_update_packet.json` |

## Human-Readable Diff Table

# P22 Scene-CI Match Diff Table

| Group | ID | Status | Accepted | Current |
|---|---|---|---|---|
| positive_layout_hashes | `front_linear` | match | `42aab471352f` | `42aab471352f` |
| positive_layout_hashes | `front_reverse` | match | `dc825e9e56fe` | `dc825e9e56fe` |
| positive_layout_hashes | `front_staggered` | match | `d0ce8dfe7ad4` | `d0ce8dfe7ad4` |
| negative_fixture_hashes | `camera_obstruction_failure` | match | `a6c2547c2488` | `a6c2547c2488` |
| negative_fixture_hashes | `finish_before_checkpoints` | match | `60181f4865e4` | `60181f4865e4` |
| negative_fixture_hashes | `missing_checkpoint` | match | `d3bc7a8e1721` | `d3bc7a8e1721` |
| negative_fixture_hashes | `route_mismatch` | match | `2840bcbab1ed` | `2840bcbab1ed` |
| negative_fixture_hashes | `sensor_clearance_violation` | match | `2d4671870413` | `2d4671870413` |

## Boundary

- Authority is proxy scene nodes plus HomePC Godot headless physics/input/camera assertions.
- This does not claim screenshot/visual QA.
- This does not claim mesh-accurate GLB collision.
- Baseline update packets are review artifacts, not automatic replacements.
