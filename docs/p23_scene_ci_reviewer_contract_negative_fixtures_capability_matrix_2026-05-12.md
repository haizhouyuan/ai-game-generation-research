# P23 Scene-CI Reviewer Contract Negative Fixtures Capability Matrix

Status: pass on fresh local run.

| Capability | Expected | Evidence |
|---|---|---|
| Malformed packet fixtures fail validation | pass | `experiments/game_p23_scene_ci_reviewer_contract_negative_fixtures_20260512/outputs/p23_scene_ci_negative_contract_review_matrix.json` |
| Missing diff table fails validation | pass | same matrix |
| Mode-specific exit-code misuse fails validation | pass | same matrix |
| Positive P22 contract remains loaded and valid | pass | same matrix |

Boundary: P23 validates reviewer-contract artifacts only; no screenshot/visual QA or mesh-accurate GLB collision claim.
