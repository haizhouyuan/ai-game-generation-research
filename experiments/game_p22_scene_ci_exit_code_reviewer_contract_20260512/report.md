# P22 Game Scene-CI Exit-Code Reviewer Contract

Status: pass on fresh local run.

## Goal

Turn the P21 scene-CI modes into explicit reviewer-contract examples with exit-code semantics, accepted/rejected baseline-update packets, and a compact human-readable diff table.

## Required Outputs

- Runner: `run_p22_scene_ci_exit_code_reviewer_contract.py`
- Contract report: `outputs/p22_reviewer_contract_report.json`
- Exit-code matrix: `outputs/p22_exit_code_matrix.json`
- Reviewer packet: `outputs/p22_reviewer_contract_packet.md`
- Accepted packet: `outputs/p22_accepted_baseline_update_packet.json`
- Rejected packet: `outputs/p22_rejected_baseline_update_packet.json`
- Hash ledger: `outputs/artifact_hashes.json`
- Fresh rerun log: `verify_run.log`

## Result

`run.log` passed with:

- `full_summary_pass=true`
- `match_exit_code_contract=true`
- `diff_exit_code_contract=true`
- `candidate_update_exit_code_contract=true`
- `denied_update_exit_code_contract=true`
- `accepted_packet_emitted=true`
- `rejected_packet_emitted=true`
- `human_diff_table_emitted=true`

Actual CLI examples were also captured in `outputs/p22_cli_exit_code_examples.txt`:

- `match` returned `0`
- `diff` returned `1`
- `candidate-update` returned `0`
- `denied-update` returned `2`

## Capability Boundary

This is a compact deterministic headless scene-CI contract over proxy scene nodes, physics/input/camera assertions, and accepted hash baselines. It does not claim screenshot/visual QA or mesh-accurate GLB collision.
