# P21 Scene-CI Baseline Update Review Packet

Status: compact deterministic headless scene-CI review packet.

| Mode | Result | Evidence |
|---|---|---|
| `match` | `pass` | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_compact_diff_table.md` |
| `diff` | `pass` | `in-memory diff-counter over first positive layout hash` |
| `candidate-update` | `pass` | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_allowed_baseline_update_candidate.json` |
| `denied-update` | `pass` | `unlisted_baseline_update_counter` |

## Boundary

- This packet reviews proxy scene nodes plus HomePC Godot headless physics/input/camera assertions.
- It does not claim screenshot/visual QA.
- It does not claim mesh-accurate GLB collision.
- Candidate update output is not automatic baseline replacement.

## Compact Diff Table

# P21 Scene-CI Match Diff Table

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
