#!/usr/bin/env python3
"""Reusable P20 scene-CI regression command.

The Godot scene-CI full report is produced separately on HomePC. This command
turns that full report into compact hashes, compares them against an accepted
baseline, writes a human-readable diff table, and enforces allowlisted baseline
update policy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_FULL_REPORT = ROOT / "outputs" / "p20_negative_scene_ci_full_report.json"
DEFAULT_BASELINE = ROOT / "baseline" / "accepted_p19_scene_ci_baseline.json"
DEFAULT_ALLOWLIST = ROOT / "baseline" / "baseline_update_allowlist.json"
DEFAULT_OUTPUT = ROOT / "outputs" / "p20_scene_ci_regression_report.json"
DEFAULT_DIFF_TABLE = ROOT / "outputs" / "p20_compact_human_diff_table.md"
DEFAULT_HASHES = ROOT / "outputs" / "p20_current_trace_hashes.json"
DEFAULT_COMPACT = ROOT / "outputs" / "p20_current_compact_trace.json"
DEFAULT_POLICY = ROOT / "outputs" / "p20_baseline_update_policy_check.json"
DEFAULT_ARTIFACT_HASHES = ROOT / "outputs" / "artifact_hashes.json"


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def compact_layout(report: dict[str, Any]) -> dict[str, Any]:
    replay = report.get("replay", {})
    summary = replay.get("summary", {})
    trace_diff = replay.get("trace_diff", {})
    return {
        "layout_id": report.get("layout_id"),
        "scene_path": report.get("scene_path"),
        "route": report.get("route", []),
        "summary_pass": report.get("summary", {}).get("pass", False),
        "route_signature": summary.get("route_signature", ""),
        "event_reasons": summary.get("event_reasons", []),
        "expected_event_reasons": summary.get("expected_event_reasons", []),
        "event_objective_ids": summary.get("event_objective_ids", []),
        "expected_event_objective_ids": summary.get("expected_event_objective_ids", []),
        "trace_diff": {
            "reasons_pass": trace_diff.get("reasons", {}).get("pass", False),
            "objective_ids_pass": trace_diff.get("objective_ids", {}).get("pass", False),
            "reason_mismatches": trace_diff.get("reasons", {}).get("mismatches", []),
            "objective_id_mismatches": trace_diff.get("objective_ids", {}).get("mismatches", []),
        },
        "gate_counts": {
            "collision_pass_count": summary.get("collision_pass_count", 0),
            "collision_target_count": summary.get("collision_target_count", 0),
            "input_key_event_pass": summary.get("input_key_event_pass", False),
            "objective_ui_pass": summary.get("objective_ui_pass", False),
            "camera_variants_pass": summary.get("camera_variants_pass", False),
            "obstruction_counter_pass": summary.get("obstruction_counter_pass", False),
            "tick_count": summary.get("tick_count", 0),
        },
    }


def compact_negative(row: dict[str, Any]) -> dict[str, Any]:
    replay = row.get("replay", {})
    summary = replay.get("summary", {})
    trace_diff = replay.get("trace_diff", {})
    readback = row.get("readback", {})
    build = row.get("build", {})
    compact = {
        "id": row.get("id"),
        "expected_failure": row.get("expected_failure"),
        "detected_failure": row.get("detected_failure", False),
        "readback_pass": readback.get("pass"),
        "build_pass": build.get("pass"),
        "summary_pass": summary.get("pass"),
        "event_reasons": summary.get("event_reasons", []),
        "event_objective_ids": summary.get("event_objective_ids", []),
        "trace_diff": {
            "reasons_pass": trace_diff.get("reasons", {}).get("pass"),
            "objective_ids_pass": trace_diff.get("objective_ids", {}).get("pass"),
            "reason_mismatches": trace_diff.get("reasons", {}).get("mismatches", []),
            "objective_id_mismatches": trace_diff.get("objective_ids", {}).get("mismatches", []),
        },
        "diagnostics": {},
    }
    if row.get("id") == "missing_checkpoint":
        compact["diagnostics"] = {"readback_errors": readback.get("errors", []), "mutation": row.get("mutation", {})}
    elif row.get("id") == "sensor_clearance_violation":
        compact["diagnostics"] = {"clearance_pass": build.get("clearance_pass"), "clearance_rows": build.get("clearance_rows", [])}
    elif row.get("id") == "finish_before_checkpoints":
        attempts = replay.get("finish_attempts", [])
        compact["diagnostics"] = {"first_finish_attempt": attempts[0] if attempts else {}}
    elif row.get("id") == "camera_obstruction_failure":
        camera_summary = summary.get("camera_summary", {})
        compact["diagnostics"] = {
            "camera_variants_pass": summary.get("camera_variants_pass"),
            "camera_failed_count": camera_summary.get("failed_count"),
            "by_variant": camera_summary.get("by_variant", {}),
        }
    elif row.get("id") == "route_mismatch":
        compact["diagnostics"] = {"objective_id_mismatches": trace_diff.get("objective_ids", {}).get("mismatches", [])}
    return compact


def build_current(full_report: dict[str, Any], full_report_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    positive = [compact_layout(row) for row in full_report.get("layout_reports", [])]
    negative = [compact_negative(row) for row in full_report.get("negative_reports", [])]
    compact = {
        "batch": "P20-A reusable scene-CI compact trace",
        "positive_layouts": positive,
        "negative_fixtures": negative,
        "boundaries": full_report.get("boundaries", []),
    }
    hashes = {
        "full_report_sha256": sha256_file(full_report_path),
        "compact_trace_sha256": sha256_text(stable_json(compact)),
        "positive_layout_hashes": {row["layout_id"]: sha256_text(stable_json(row)) for row in positive},
        "negative_fixture_hashes": {row["id"]: sha256_text(stable_json(row)) for row in negative},
    }
    return compact, hashes


def compare_hash_maps(name: str, accepted: dict[str, str], current: dict[str, str]) -> dict[str, Any]:
    accepted_keys = set(accepted)
    current_keys = set(current)
    rows = []
    for key in sorted(accepted_keys | current_keys):
        accepted_hash = accepted.get(key)
        current_hash = current.get(key)
        rows.append({
            "group": name,
            "id": key,
            "status": "match" if accepted_hash == current_hash else "diff",
            "accepted": accepted_hash,
            "current": current_hash,
        })
    return {
        "name": name,
        "pass": accepted == current,
        "missing": sorted(accepted_keys - current_keys),
        "unexpected": sorted(current_keys - accepted_keys),
        "diffs": [row for row in rows if row["status"] == "diff"],
        "rows": rows,
    }


def diff_table(report: dict[str, Any]) -> str:
    lines = [
        "# P20 Scene-CI Compact Diff Table",
        "",
        "| Group | ID | Status | Accepted | Current |",
        "|---|---|---|---|---|",
    ]
    for comparison in (report["comparisons"]["positive"], report["comparisons"]["negative"]):
        for row in comparison["rows"]:
            accepted = (row.get("accepted") or "missing")[:12]
            current = (row.get("current") or "missing")[:12]
            lines.append(f"| {row['group']} | `{row['id']}` | {row['status']} | `{accepted}` | `{current}` |")
    lines.extend([
        "",
        "## Baseline Update Policy",
        "",
        f"- Requested baseline id: `{report['baseline_update_policy']['requested_baseline_id']}`",
        f"- Allowlisted update accepted: `{report['baseline_update_policy']['allowlisted_update_allowed']}`",
        f"- Unlisted update denied: `{report['baseline_update_policy']['unlisted_update_denied']}`",
        "",
        "Boundary: this table covers compact deterministic headless scene-CI data only, not screenshots or mesh-accurate GLB collision.",
    ])
    return "\n".join(lines) + "\n"


def baseline_update_policy(
    baseline: dict[str, Any],
    allowlist: dict[str, Any],
    current_hashes: dict[str, Any],
    write_candidate: bool,
) -> dict[str, Any]:
    baseline_id = baseline["baseline_id"]
    allowed = baseline_id in set(allowlist.get("allowed_baseline_ids", []))
    denied_id = "unlisted_baseline_update_counter"
    denied = denied_id not in set(allowlist.get("allowed_baseline_ids", []))
    candidate_path = ROOT / allowlist.get("candidate_output", "outputs/p20_allowed_baseline_update_candidate.json")
    candidate = {
        "baseline_id": baseline_id,
        "source": "P20 reusable scene-CI command candidate",
        "accepted_hashes": current_hashes,
    }
    if write_candidate and allowed:
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_path.write_text(json.dumps(candidate, indent=2) + "\n")
    return {
        "requested_baseline_id": baseline_id,
        "allowlisted_update_allowed": allowed,
        "unlisted_update_denied": denied,
        "candidate_path": str(candidate_path),
        "candidate_written": write_candidate and allowed and candidate_path.exists(),
    }


def write_artifact_hashes() -> None:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != DEFAULT_ARTIFACT_HASHES and ".godot" not in path.parts and "__pycache__" not in path.parts:
            rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    DEFAULT_ARTIFACT_HASHES.write_text(json.dumps(rows, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-report", type=Path, default=DEFAULT_FULL_REPORT)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--allowlist", type=Path, default=DEFAULT_ALLOWLIST)
    parser.add_argument("--write-baseline-candidate", action="store_true")
    args = parser.parse_args()

    full_report = load_json(args.full_report)
    baseline = load_json(args.baseline)
    allowlist = load_json(args.allowlist)
    accepted = baseline["accepted_hashes"]
    compact, current_hashes = build_current(full_report, args.full_report)
    positive_compare = compare_hash_maps("positive_layout_hashes", accepted.get("positive_layout_hashes", {}), current_hashes.get("positive_layout_hashes", {}))
    negative_compare = compare_hash_maps("negative_fixture_hashes", accepted.get("negative_fixture_hashes", {}), current_hashes.get("negative_fixture_hashes", {}))
    policy = baseline_update_policy(baseline, allowlist, current_hashes, args.write_baseline_candidate)
    checks = {
        "full_summary_pass": full_report.get("summary", {}).get("pass") is True,
        "positive_hashes_match_baseline": positive_compare["pass"],
        "negative_hashes_match_baseline": negative_compare["pass"],
        "diff_table_emitted": True,
        "allowlisted_update_allowed": policy["allowlisted_update_allowed"],
        "unlisted_update_denied": policy["unlisted_update_denied"],
    }
    report = {
        "batch": "P20-A reusable scene-CI command",
        "baseline": baseline,
        "current_hashes": current_hashes,
        "comparisons": {
            "positive": positive_compare,
            "negative": negative_compare,
        },
        "baseline_update_policy": policy,
        "checks": checks,
        "overall_pass": all(checks.values()),
        "boundaries": [
            "Reusable command checks compact deterministic headless scene-CI hashes and writes a readable diff table.",
            "Baseline updates are allowlist-gated and written only as candidates.",
            "This does not claim screenshot/visual QA or mesh-accurate GLB collision.",
        ],
    }
    DEFAULT_COMPACT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_COMPACT.write_text(json.dumps(compact, indent=2) + "\n")
    DEFAULT_HASHES.write_text(json.dumps({**current_hashes, "checks": checks}, indent=2) + "\n")
    DEFAULT_OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    DEFAULT_DIFF_TABLE.write_text(diff_table(report))
    DEFAULT_POLICY.write_text(json.dumps(policy, indent=2) + "\n")
    write_artifact_hashes()
    print(json.dumps({"overall_pass": report["overall_pass"], "checks": checks, "diff_table": str(DEFAULT_DIFF_TABLE), "policy": policy}, indent=2))
    return 0 if report["overall_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
