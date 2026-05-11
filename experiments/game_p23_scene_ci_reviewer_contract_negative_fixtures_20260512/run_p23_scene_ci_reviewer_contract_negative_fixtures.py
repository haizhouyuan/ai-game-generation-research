#!/usr/bin/env python3
"""P23 negative fixtures for the scene-CI reviewer contract.

This validates the P22 reviewer contract against malformed packets, missing
diff-table evidence, and mode-specific exit-code misuse examples.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
P22_ROOT = ROOT.parents[0] / "game_p22_scene_ci_exit_code_reviewer_contract_20260512"
OUT = ROOT / "outputs"
FIXTURES = OUT / "fixtures"
P22_REPORT = P22_ROOT / "outputs" / "p22_reviewer_contract_report.json"
P22_EXIT_MATRIX = P22_ROOT / "outputs" / "p22_exit_code_matrix.json"
P22_ACCEPTED_PACKET = P22_ROOT / "outputs" / "p22_accepted_baseline_update_packet.json"
P22_REJECTED_PACKET = P22_ROOT / "outputs" / "p22_rejected_baseline_update_packet.json"
P22_DIFF_TABLE = P22_ROOT / "outputs" / "p22_human_readable_diff_table.md"
REVIEW_MATRIX = OUT / "p23_scene_ci_negative_contract_review_matrix.json"
COMPACT_REVIEW = OUT / "p23_compact_review_matrix.md"
ARTIFACT_HASHES = OUT / "artifact_hashes.json"

REQUIRED_ACCEPTED_PACKET_FIELDS = {"packet_type", "baseline_id", "review_only", "accepted_hashes", "boundary"}
REQUIRED_REJECTED_PACKET_FIELDS = {"packet_type", "requested_baseline_id", "allowlisted", "exit_code", "reason"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def validate_packet(path: Path, required: set[str], expected_type: str) -> dict[str, Any]:
    try:
        data = load_json(path)
    except Exception as exc:  # noqa: BLE001 - fixture intentionally covers malformed JSON.
        return {
            "pass": False,
            "path": str(path),
            "error": "invalid_json",
            "detail": str(exc),
            "missing_fields": sorted(required),
        }
    missing = sorted(required - set(data))
    type_ok = data.get("packet_type") == expected_type
    return {
        "pass": not missing and type_ok,
        "path": str(path),
        "error": None if not missing and type_ok else "schema_or_type_mismatch",
        "missing_fields": missing,
        "packet_type": data.get("packet_type"),
        "expected_packet_type": expected_type,
    }


def validate_diff_table(path: Path) -> dict[str, Any]:
    exists = path.exists()
    content = path.read_text() if exists else ""
    required_markers = ["| Group | ID | Status |", "positive_layout_hashes", "negative_fixture_hashes"]
    return {
        "pass": exists and all(marker in content for marker in required_markers),
        "path": str(path),
        "exists": exists,
        "missing_markers": [marker for marker in required_markers if marker not in content],
    }


def validate_exit_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "pass": int(row["observed_exit_code"]) == int(row["expected_example_code"]),
        "mode": row["mode"],
        "observed_exit_code": row["observed_exit_code"],
        "expected_example_code": row["expected_example_code"],
    }


def mutate_exit_row(row: dict[str, Any]) -> dict[str, Any]:
    mutated = dict(row)
    expected = int(mutated["expected_example_code"])
    mutated["observed_exit_code"] = 0 if expected != 0 else 1
    mutated["mutation"] = "mode_specific_exit_code_misuse"
    return mutated


def create_fixture_packets() -> dict[str, Path]:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    accepted = load_json(P22_ACCEPTED_PACKET)
    rejected = load_json(P22_REJECTED_PACKET)
    malformed_json = FIXTURES / "malformed_candidate_packet.json"
    malformed_json.write_text('{"packet_type": "accepted_baseline_update_candidate", "accepted_hashes":')
    missing_hashes = FIXTURES / "candidate_missing_hashes_packet.json"
    missing_payload = dict(accepted)
    missing_payload.pop("accepted_hashes", None)
    write_json(missing_hashes, missing_payload)
    rejected_wrong_type = FIXTURES / "rejected_packet_wrong_type.json"
    wrong_payload = dict(rejected)
    wrong_payload["packet_type"] = "accepted_baseline_update_candidate"
    write_json(rejected_wrong_type, wrong_payload)
    return {
        "malformed_json": malformed_json,
        "candidate_missing_hashes": missing_hashes,
        "rejected_wrong_type": rejected_wrong_type,
        "missing_diff_table": FIXTURES / "missing_diff_table_counter.md",
    }


def negative_fixture_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    paths = create_fixture_packets()
    rows: list[dict[str, Any]] = []
    packet_checks = [
        (
            "malformed_candidate_packet",
            validate_packet(paths["malformed_json"], REQUIRED_ACCEPTED_PACKET_FIELDS, "accepted_baseline_update_candidate"),
            "invalid_json",
        ),
        (
            "candidate_missing_hashes_packet",
            validate_packet(paths["candidate_missing_hashes"], REQUIRED_ACCEPTED_PACKET_FIELDS, "accepted_baseline_update_candidate"),
            "missing_required_field",
        ),
        (
            "rejected_packet_wrong_type",
            validate_packet(paths["rejected_wrong_type"], REQUIRED_REJECTED_PACKET_FIELDS, "rejected_baseline_update_request"),
            "wrong_packet_type",
        ),
    ]
    for fixture_id, validation, expected_failure in packet_checks:
        rows.append({
            "fixture_id": fixture_id,
            "category": "malformed_packet",
            "expected_failure": expected_failure,
            "detected_failure": validation["pass"] is False,
            "validation": validation,
        })
    missing_diff = validate_diff_table(paths["missing_diff_table"])
    rows.append({
        "fixture_id": "missing_diff_table",
        "category": "missing_diff_table",
        "expected_failure": "diff_table_absent",
        "detected_failure": missing_diff["pass"] is False,
        "validation": missing_diff,
    })
    positive_diff = validate_diff_table(P22_DIFF_TABLE)
    rows.append({
        "fixture_id": "positive_diff_table_control",
        "category": "positive_control",
        "expected_failure": None,
        "detected_failure": False,
        "validation": positive_diff,
        "control_pass": positive_diff["pass"],
    })
    for row in report.get("mode_rows", []):
        mutated = mutate_exit_row(row)
        validation = validate_exit_row(mutated)
        rows.append({
            "fixture_id": f"{row['mode']}_exit_code_misuse",
            "category": "mode_specific_exit_code_misuse",
            "expected_failure": "observed_exit_code_does_not_match_contract",
            "detected_failure": validation["pass"] is False,
            "validation": validation,
        })
    return rows


def compact_markdown(matrix: dict[str, Any]) -> str:
    lines = [
        "# P23 Scene-CI Reviewer Contract Negative Fixture Matrix",
        "",
        "| Fixture | Category | Expected Failure | Detected |",
        "|---|---|---|---|",
    ]
    for row in matrix["negative_fixtures"]:
        lines.append(
            f"| `{row['fixture_id']}` | `{row['category']}` | `{row.get('expected_failure')}` | {row['detected_failure']} |"
        )
    lines.extend([
        "",
        "## Boundary",
        "",
        "- This validates reviewer-contract artifacts and compact deterministic headless scene-CI evidence.",
        "- It does not claim screenshot/visual QA.",
        "- It does not claim mesh-accurate GLB collision.",
    ])
    return "\n".join(lines) + "\n"


def write_artifact_hashes() -> None:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != ARTIFACT_HASHES and "__pycache__" not in path.parts:
            rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    write_json(ARTIFACT_HASHES, rows)


def run_all() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    report = load_json(P22_REPORT)
    exit_matrix = load_json(P22_EXIT_MATRIX)
    rows = negative_fixture_rows(report)
    checks = {
        "positive_p22_contract_pass": report.get("overall_pass") is True,
        "exit_matrix_loaded": bool(exit_matrix.get("mode_rows")),
        "malformed_packet_fixtures_detected": all(row["detected_failure"] for row in rows if row["category"] == "malformed_packet"),
        "missing_diff_table_detected": all(row["detected_failure"] for row in rows if row["category"] == "missing_diff_table"),
        "mode_exit_misuse_detected": all(row["detected_failure"] for row in rows if row["category"] == "mode_specific_exit_code_misuse"),
        "positive_diff_table_control_pass": all(row.get("control_pass") for row in rows if row["fixture_id"] == "positive_diff_table_control"),
    }
    matrix = {
        "batch": "P23-A scene-CI reviewer contract negative fixtures",
        "source_report": str(P22_REPORT),
        "source_exit_matrix": str(P22_EXIT_MATRIX),
        "negative_fixtures": rows,
        "checks": checks,
        "overall_pass": all(checks.values()),
        "boundaries": [
            "P23 validates reviewer-contract artifacts and headless scene-CI evidence only.",
            "It does not claim screenshot/visual QA.",
            "It does not claim mesh-accurate GLB collision.",
        ],
    }
    write_json(REVIEW_MATRIX, matrix)
    COMPACT_REVIEW.write_text(compact_markdown(matrix))
    write_artifact_hashes()
    return matrix


def main() -> int:
    matrix = run_all()
    print(json.dumps({"overall_pass": matrix["overall_pass"], "checks": matrix["checks"]}, indent=2))
    return 0 if matrix["overall_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
