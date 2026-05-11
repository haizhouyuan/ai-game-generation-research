# P22 Scene-CI Exit-Code Reviewer Contract Capability Matrix

Status: pass on fresh local run.

| Capability | Expected | Evidence |
|---|---|---|
| Match mode returns accepted-baseline success example | pass | `experiments/game_p22_scene_ci_exit_code_reviewer_contract_20260512/outputs/p22_exit_code_matrix.json` |
| Diff mode returns synthetic drift non-zero example | pass | same matrix |
| Candidate update emits accepted review packet | pass | `experiments/game_p22_scene_ci_exit_code_reviewer_contract_20260512/outputs/p22_accepted_baseline_update_packet.json` |
| Denied update emits rejected packet | pass | `experiments/game_p22_scene_ci_exit_code_reviewer_contract_20260512/outputs/p22_rejected_baseline_update_packet.json` |
| Human-readable compact diff table exists | pass | `experiments/game_p22_scene_ci_exit_code_reviewer_contract_20260512/outputs/p22_human_readable_diff_table.md` |

Boundary: P22 is still headless proxy scene-CI evidence, not screenshot/visual QA or mesh-accurate collision validation.
