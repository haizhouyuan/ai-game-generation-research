#!/usr/bin/env python3
"""P19 accepted-baseline hash regression and compact failure diff."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
FULL_REPORT = OUTPUTS / "p18_negative_scene_ci_full_report.json"
BASELINE = ROOT / "baseline" / "accepted_p18_trace_hash_baseline.json"
CURRENT_COMPACT = OUTPUTS / "p19_current_compact_trace.json"
CURRENT_HASHES = OUTPUTS / "p19_current_trace_hashes.json"
FAILURE_DIFF = OUTPUTS / "p19_compact_failure_diff_report.json"
ARTIFACT_HASHES = OUTPUTS / "artifact_hashes.json"


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
        compact["diagnostics"] = {"camera_variants_pass": summary.get("camera_variants_pass"), "camera_failed_count": camera_summary.get("failed_count"), "by_variant": camera_summary.get("by_variant", {})}
    elif row.get("id") == "route_mismatch":
        compact["diagnostics"] = {"objective_id_mismatches": trace_diff.get("objective_ids", {}).get("mismatches", [])}
    return compact


def build_current(full_report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    positive = [compact_layout(row) for row in full_report.get("layout_reports", [])]
    negative = [compact_negative(row) for row in full_report.get("negative_reports", [])]
    compact = {
        "batch": "P19-A current compact replay trace for accepted-baseline regression",
        "positive_layouts": positive,
        "negative_fixtures": negative,
        "boundaries": full_report.get("boundaries", []),
    }
    hashes = {
        "full_report_sha256": sha256_file(FULL_REPORT),
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
        rows.append({
            "id": key,
            "accepted": accepted.get(key),
            "current": current.get(key),
            "status": "match" if accepted.get(key) == current.get(key) else "diff",
        })
    return {
        "name": name,
        "pass": accepted == current,
        "missing": sorted(accepted_keys - current_keys),
        "unexpected": sorted(current_keys - accepted_keys),
        "diffs": [row for row in rows if row["status"] == "diff"],
        "rows": rows,
    }


def mutate_positive_reorder(compact: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(compact)
    if mutated["positive_layouts"]:
        row = mutated["positive_layouts"][0]
        row["event_reasons"] = list(reversed(row.get("event_reasons", [])))
        row["mutation"] = "reverse first positive layout event_reasons"
    return mutated


def mutate_negative_missing(compact: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(compact)
    mutated["negative_fixtures"] = [row for row in mutated.get("negative_fixtures", []) if row.get("id") != "route_mismatch"]
    mutated["mutation"] = "drop route_mismatch negative fixture"
    return mutated


def hashes_for_compact(compact: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {
        "positive_layout_hashes": {row["layout_id"]: sha256_text(stable_json(row)) for row in compact.get("positive_layouts", [])},
        "negative_fixture_hashes": {row["id"]: sha256_text(stable_json(row)) for row in compact.get("negative_fixtures", [])},
    }


def write_artifact_hashes() -> None:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != ARTIFACT_HASHES and ".godot" not in path.parts and "__pycache__" not in path.parts:
            rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    ARTIFACT_HASHES.write_text(json.dumps(rows, indent=2) + "\n")


def main() -> int:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    full_report = load_json(FULL_REPORT)
    baseline = load_json(BASELINE)
    accepted = baseline["accepted_hashes"]
    compact, current_hashes = build_current(full_report)
    positive_compare = compare_hash_maps("positive_layout_hashes", accepted.get("positive_layout_hashes", {}), current_hashes.get("positive_layout_hashes", {}))
    negative_compare = compare_hash_maps("negative_fixture_hashes", accepted.get("negative_fixture_hashes", {}), current_hashes.get("negative_fixture_hashes", {}))
    reordered = hashes_for_compact(mutate_positive_reorder(compact))
    missing_negative = hashes_for_compact(mutate_negative_missing(compact))
    drift_fixtures = [
        {
            "id": "positive_event_order_reversed_counter",
            "expected_detection": True,
            "compare": compare_hash_maps("positive_layout_hashes", accepted.get("positive_layout_hashes", {}), reordered["positive_layout_hashes"]),
        },
        {
            "id": "negative_route_mismatch_fixture_missing_counter",
            "expected_detection": True,
            "compare": compare_hash_maps("negative_fixture_hashes", accepted.get("negative_fixture_hashes", {}), missing_negative["negative_fixture_hashes"]),
        },
    ]
    checks = {
        "full_summary_pass": full_report.get("summary", {}).get("pass") is True,
        "accepted_positive_hashes_match": positive_compare["pass"],
        "accepted_negative_hashes_match": negative_compare["pass"],
        "positive_drift_counter_detected": not drift_fixtures[0]["compare"]["pass"] and bool(drift_fixtures[0]["compare"]["diffs"]),
        "negative_missing_counter_detected": not drift_fixtures[1]["compare"]["pass"] and "route_mismatch" in drift_fixtures[1]["compare"]["missing"],
    }
    diff_report = {
        "batch": "P19-A accepted-baseline hash regression and compact failure diff",
        "baseline": baseline,
        "current_hashes": current_hashes,
        "accepted_comparisons": {
            "positive": positive_compare,
            "negative": negative_compare,
        },
        "drift_counter_fixtures": drift_fixtures,
        "checks": checks,
        "overall_pass": all(checks.values()),
        "boundaries": [
            "Hash regression checks compact trace/event/objective diagnostics derived from HomePC Godot headless output.",
            "The authority remains proxy scene nodes plus headless physics/input/camera assertions.",
            "This does not claim screenshot/visual QA or mesh-accurate GLB collision.",
        ],
    }
    CURRENT_COMPACT.write_text(json.dumps(compact, indent=2) + "\n")
    CURRENT_HASHES.write_text(json.dumps({**current_hashes, "checks": checks}, indent=2) + "\n")
    FAILURE_DIFF.write_text(json.dumps(diff_report, indent=2) + "\n")
    write_artifact_hashes()
    print(json.dumps({"checks": checks, "overall_pass": diff_report["overall_pass"], "accepted_comparisons": diff_report["accepted_comparisons"], "drift_counter_fixtures": drift_fixtures}, indent=2))
    return 0 if diff_report["overall_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
