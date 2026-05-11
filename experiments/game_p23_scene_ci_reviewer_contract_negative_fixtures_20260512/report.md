# P23 Game Scene-CI Reviewer Contract Negative Fixtures

Status: pass on fresh local run.

## Goal

Add negative fixtures for the P22 scene-CI reviewer contract: malformed packet, missing diff table, and mode-specific exit-code misuse.

## Required Outputs

- Runner: `run_p23_scene_ci_reviewer_contract_negative_fixtures.py`
- Review matrix: `outputs/p23_scene_ci_negative_contract_review_matrix.json`
- Compact matrix: `outputs/p23_compact_review_matrix.md`
- Fixture packets: `outputs/fixtures/`
- Hash ledger: `outputs/artifact_hashes.json`
- Fresh rerun log: `verify_run.log`

## Result

`run.log` passed with:

- `positive_p22_contract_pass=true`
- `exit_matrix_loaded=true`
- `malformed_packet_fixtures_detected=true`
- `missing_diff_table_detected=true`
- `mode_exit_misuse_detected=true`
- `positive_diff_table_control_pass=true`

The matrix contains 9 fixture rows: 3 malformed packet fixtures, 1 missing diff table fixture, 1 positive diff-table control, and 4 mode-specific exit-code misuse fixtures.

## Capability Boundary

This validates reviewer-contract artifacts and compact deterministic headless scene-CI evidence. It does not claim screenshot/visual QA or mesh-accurate GLB collision.
