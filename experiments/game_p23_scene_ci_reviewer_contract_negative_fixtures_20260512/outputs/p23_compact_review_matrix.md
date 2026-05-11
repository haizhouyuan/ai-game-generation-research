# P23 Scene-CI Reviewer Contract Negative Fixture Matrix

| Fixture | Category | Expected Failure | Detected |
|---|---|---|---|
| `malformed_candidate_packet` | `malformed_packet` | `invalid_json` | True |
| `candidate_missing_hashes_packet` | `malformed_packet` | `missing_required_field` | True |
| `rejected_packet_wrong_type` | `malformed_packet` | `wrong_packet_type` | True |
| `missing_diff_table` | `missing_diff_table` | `diff_table_absent` | True |
| `positive_diff_table_control` | `positive_control` | `None` | False |
| `match_exit_code_misuse` | `mode_specific_exit_code_misuse` | `observed_exit_code_does_not_match_contract` | True |
| `diff_exit_code_misuse` | `mode_specific_exit_code_misuse` | `observed_exit_code_does_not_match_contract` | True |
| `candidate-update_exit_code_misuse` | `mode_specific_exit_code_misuse` | `observed_exit_code_does_not_match_contract` | True |
| `denied-update_exit_code_misuse` | `mode_specific_exit_code_misuse` | `observed_exit_code_does_not_match_contract` | True |

## Boundary

- This validates reviewer-contract artifacts and compact deterministic headless scene-CI evidence.
- It does not claim screenshot/visual QA.
- It does not claim mesh-accurate GLB collision.
