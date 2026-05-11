# P21 Game Scene-CI Modes Review Packet Capability Matrix

| Capability | Result | Evidence | Boundary |
|---|---|---|---|
| `match` mode | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_mode_match_report.json` | Compact deterministic hashes only. |
| `diff` mode | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_mode_diff_report.json` | Synthetic drift counter, not visual diff. |
| `candidate-update` mode | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_mode_candidate_update_report.json` | Review candidate only. |
| `denied-update` mode | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_mode_denied_update_report.json` | Unlisted update must be denied. |
| Baseline review packet | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p21_scene_ci_modes_review_packet_20260512/outputs/p21_baseline_update_review_packet.md` | Not accepted-baseline replacement. |
