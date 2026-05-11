#!/usr/bin/env python3
"""P22 reviewer-contract and exit-code examples for scene-CI modes.

This consumes the local P21/P18-derived Godot headless full report and turns
match/diff/candidate-update/denied-update into explicit CLI contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
P21_ROOT = ROOT.parents[0] / "game_p21_scene_ci_modes_review_packet_20260512"
sys.path.insert(0, str(P21_ROOT))

from run_scene_ci_modes_review_packet import (  # noqa: E402
    build_current,
    compare_all,
    diff_table,
    load_json,
    mutate_for_diff,
)


OUT = ROOT / "outputs"
FULL_REPORT = OUT / "p22_negative_scene_ci_full_report.json"
BASELINE = ROOT / "baseline" / "accepted_p19_scene_ci_baseline.json"
ALLOWLIST = ROOT / "baseline" / "baseline_update_allowlist.json"
COMPACT_TRACE = OUT / "p22_current_compact_trace.json"
CURRENT_HASHES = OUT / "p22_current_trace_hashes.json"
HUMAN_DIFF = OUT / "p22_human_readable_diff_table.md"
ACCEPTED_PACKET = OUT / "p22_accepted_baseline_update_packet.json"
REJECTED_PACKET = OUT / "p22_rejected_baseline_update_packet.json"
EXIT_CODE_MATRIX = OUT / "p22_exit_code_matrix.json"
REVIEWER_CONTRACT = OUT / "p22_reviewer_contract_report.json"
REVIEW_PACKET = OUT / "p22_reviewer_contract_packet.md"
ARTIFACT_HASHES = OUT / "artifact_hashes.json"


EXIT_CONTRACT = {
    "match": {
        "success_code": 0,
        "failure_code": 1,
        "semantics": "strict CI baseline hash match",
        "expected_example_code": 0,
    },
    "diff": {
        "success_code": 1,
        "failure_code": 0,
        "semantics": "reviewer-facing drift example should return non-zero and include compact diff",
        "expected_example_code": 1,
    },
    "candidate-update": {
        "success_code": 0,
        "failure_code": 2,
        "semantics": "allowlisted candidate packet may be written for review only",
        "expected_example_code": 0,
    },
    "denied-update": {
        "success_code": 2,
        "failure_code": 0,
        "semantics": "unlisted baseline update request must be denied with non-zero exit",
        "expected_example_code": 2,
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def baseline_allowed(allowlist: dict[str, Any], baseline_id: str) -> bool:
    return baseline_id in set(allowlist.get("allowed_baseline_ids", []))


def packet_hashes(current_hashes: dict[str, Any]) -> dict[str, Any]:
    return {
        "full_report_sha256": current_hashes["full_report_sha256"],
        "compact_trace_sha256": current_hashes["compact_trace_sha256"],
        "positive_layout_hashes": current_hashes["positive_layout_hashes"],
        "negative_fixture_hashes": current_hashes["negative_fixture_hashes"],
    }


def evaluate_mode(
    mode: str,
    baseline: dict[str, Any],
    allowlist: dict[str, Any],
    current_hashes: dict[str, Any],
    match_comparisons: dict[str, Any],
    drift_comparisons: dict[str, Any],
) -> dict[str, Any]:
    baseline_id = baseline["baseline_id"]
    contract = EXIT_CONTRACT[mode]
    if mode == "match":
        ok = match_comparisons["hashes_match"]
        exit_code = contract["success_code"] if ok else contract["failure_code"]
        evidence = str(HUMAN_DIFF)
        detail = {"hashes_match": ok, "comparisons": match_comparisons}
    elif mode == "diff":
        ok = not drift_comparisons["hashes_match"] and bool(drift_comparisons["positive"]["diffs"])
        exit_code = contract["success_code"] if ok else contract["failure_code"]
        evidence = str(HUMAN_DIFF)
        detail = {"drift_detected": ok, "comparisons": drift_comparisons}
    elif mode == "candidate-update":
        ok = baseline_allowed(allowlist, baseline_id)
        exit_code = contract["success_code"] if ok else contract["failure_code"]
        if ok:
            write_json(ACCEPTED_PACKET, {
                "packet_type": "accepted_baseline_update_candidate",
                "baseline_id": baseline_id,
                "review_only": True,
                "accepted_hashes": packet_hashes(current_hashes),
                "boundary": "candidate packet is not automatic baseline replacement",
            })
        evidence = str(ACCEPTED_PACKET)
        detail = {"allowlisted": ok, "baseline_id": baseline_id}
    elif mode == "denied-update":
        requested = "unlisted_scene_ci_baseline_update_counter"
        ok = not baseline_allowed(allowlist, requested)
        exit_code = contract["success_code"] if ok else contract["failure_code"]
        write_json(REJECTED_PACKET, {
            "packet_type": "rejected_baseline_update_request",
            "requested_baseline_id": requested,
            "allowlisted": False,
            "exit_code": exit_code,
            "reason": "baseline_id_not_allowlisted",
        })
        evidence = str(REJECTED_PACKET)
        detail = {"requested_baseline_id": requested, "denied": ok}
    else:
        raise ValueError(mode)
    return {
        "mode": mode,
        "observed_exit_code": exit_code,
        "expected_example_code": contract["expected_example_code"],
        "contract": contract,
        "contract_pass": exit_code == contract["expected_example_code"],
        "evidence": evidence,
        "detail": detail,
    }


def write_mode_outputs(rows: list[dict[str, Any]]) -> dict[str, str]:
    paths: dict[str, str] = {}
    for row in rows:
        path = OUT / f"p22_mode_{row['mode'].replace('-', '_')}_exit_contract.json"
        write_json(path, row)
        paths[row["mode"]] = str(path)
    return paths


def write_review_packet(report: dict[str, Any]) -> None:
    lines = [
        "# P22 Scene-CI Reviewer Contract Packet",
        "",
        "Status: compact deterministic headless scene-CI reviewer contract.",
        "",
        "| Mode | Observed Exit Code | Expected Example Code | Contract Pass | Evidence |",
        "|---|---:|---:|---|---|",
    ]
    for row in report["mode_rows"]:
        lines.append(
            f"| `{row['mode']}` | {row['observed_exit_code']} | {row['expected_example_code']} | "
            f"{row['contract_pass']} | `{row['evidence']}` |"
        )
    lines.extend([
        "",
        "## Human-Readable Diff Table",
        "",
    ])
    lines.extend(HUMAN_DIFF.read_text().splitlines())
    lines.extend([
        "",
        "## Boundary",
        "",
        "- Authority is proxy scene nodes plus HomePC Godot headless physics/input/camera assertions.",
        "- This does not claim screenshot/visual QA.",
        "- This does not claim mesh-accurate GLB collision.",
        "- Baseline update packets are review artifacts, not automatic replacements.",
    ])
    REVIEW_PACKET.write_text("\n".join(lines) + "\n")


def write_artifact_hashes() -> None:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != ARTIFACT_HASHES and ".godot" not in path.parts and "__pycache__" not in path.parts:
            rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    write_json(ARTIFACT_HASHES, rows)


def run_all() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    full_report = load_json(FULL_REPORT)
    baseline = load_json(BASELINE)
    allowlist = load_json(ALLOWLIST)
    compact, current_hashes = build_current(full_report, FULL_REPORT)
    write_json(COMPACT_TRACE, compact)
    write_json(CURRENT_HASHES, current_hashes)
    match_comparisons = compare_all(baseline, current_hashes)
    drift_comparisons = compare_all(baseline, mutate_for_diff(current_hashes))
    HUMAN_DIFF.write_text(diff_table(match_comparisons, "P22 Scene-CI Match Diff Table"))
    mode_rows = [
        evaluate_mode(mode, baseline, allowlist, current_hashes, match_comparisons, drift_comparisons)
        for mode in ("match", "diff", "candidate-update", "denied-update")
    ]
    mode_paths = write_mode_outputs(mode_rows)
    checks = {
        "full_summary_pass": full_report.get("summary", {}).get("pass") is True,
        "match_exit_code_contract": next(row for row in mode_rows if row["mode"] == "match")["contract_pass"],
        "diff_exit_code_contract": next(row for row in mode_rows if row["mode"] == "diff")["contract_pass"],
        "candidate_update_exit_code_contract": next(row for row in mode_rows if row["mode"] == "candidate-update")["contract_pass"],
        "denied_update_exit_code_contract": next(row for row in mode_rows if row["mode"] == "denied-update")["contract_pass"],
        "accepted_packet_emitted": ACCEPTED_PACKET.exists(),
        "rejected_packet_emitted": REJECTED_PACKET.exists(),
        "human_diff_table_emitted": HUMAN_DIFF.exists(),
    }
    report = {
        "batch": "P22-A scene-CI exit-code reviewer contract",
        "mode_rows": mode_rows,
        "mode_report_paths": mode_paths,
        "exit_code_contract": EXIT_CONTRACT,
        "match_comparisons": match_comparisons,
        "drift_counter_comparisons": drift_comparisons,
        "checks": checks,
        "overall_pass": all(checks.values()),
        "boundaries": [
            "Reviewer contract uses compact deterministic headless scene-CI evidence only.",
            "It does not claim screenshot/visual QA.",
            "It does not claim mesh-accurate GLB collision.",
            "Candidate baseline update packets are review artifacts only.",
        ],
    }
    write_json(EXIT_CODE_MATRIX, {"exit_code_contract": EXIT_CONTRACT, "mode_rows": mode_rows, "checks": checks})
    write_json(REVIEWER_CONTRACT, report)
    write_review_packet(report)
    write_artifact_hashes()
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["match", "diff", "candidate-update", "denied-update", "all"], nargs="?", default="all")
    args = parser.parse_args()
    report = run_all()
    if args.mode != "all":
        selected = next(row for row in report["mode_rows"] if row["mode"] == args.mode)
        print(json.dumps(selected, indent=2))
        return int(selected["observed_exit_code"])
    print(json.dumps({"overall_pass": report["overall_pass"], "checks": report["checks"]}, indent=2))
    return 0 if report["overall_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
