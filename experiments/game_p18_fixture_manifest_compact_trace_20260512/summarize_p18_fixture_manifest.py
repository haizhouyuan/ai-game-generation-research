#!/usr/bin/env python3
"""Build compact P18 scene-CI manifest, trace diff, and hash evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
FULL_REPORT = OUTPUTS / "p18_negative_scene_ci_full_report.json"
MANIFEST = OUTPUTS / "p18_fixture_manifest.json"
COMPACT_TRACE = OUTPUTS / "p18_compact_replay_trace.json"
TRACE_HASHES = OUTPUTS / "p18_trace_hashes.json"
ARTIFACT_HASHES = OUTPUTS / "artifact_hashes.json"


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_full_report() -> dict[str, Any]:
    return json.loads(FULL_REPORT.read_text())


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


def build_manifest(data: dict[str, Any], layout_compact: list[dict[str, Any]], negative_compact: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "batch": "P18-A fixture manifest",
        "source_full_report": str(FULL_REPORT),
        "source_scene": data.get("source_scene"),
        "authority": "proxy scene nodes plus HomePC Godot headless physics/input/camera assertions",
        "no_proxy_note": data.get("no_proxy_note"),
        "visual_claim": "disabled: no screenshot/visual QA or mesh-accurate collision claim",
        "positive_layouts": [
            {
                "id": row["layout_id"],
                "scene_path": row["scene_path"],
                "route": row["route"],
                "route_signature": row["route_signature"],
                "summary_pass": row["summary_pass"],
                "trace_hash": sha256_text(stable_json(row)),
            }
            for row in layout_compact
        ],
        "negative_fixtures": [
            {
                "id": row["id"],
                "expected_failure": row["expected_failure"],
                "detected_failure": row["detected_failure"],
                "compact_hash": sha256_text(stable_json(row)),
            }
            for row in negative_compact
        ],
    }


def write_artifact_hashes() -> None:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != ARTIFACT_HASHES and ".godot" not in path.parts and "__pycache__" not in path.parts:
            rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    ARTIFACT_HASHES.write_text(json.dumps(rows, indent=2) + "\n")


def main() -> int:
    data = load_full_report()
    layout_compact = [compact_layout(row) for row in data.get("layout_reports", [])]
    negative_compact = [compact_negative(row) for row in data.get("negative_reports", [])]
    manifest = build_manifest(data, layout_compact, negative_compact)
    compact_trace = {
        "batch": "P18-A compact replay trace diff",
        "positive_layouts": layout_compact,
        "negative_fixtures": negative_compact,
        "boundaries": data.get("boundaries", []),
    }
    trace_hashes = {
        "full_report_sha256": sha256_file(FULL_REPORT),
        "manifest_sha256": sha256_text(stable_json(manifest)),
        "compact_trace_sha256": sha256_text(stable_json(compact_trace)),
        "positive_layout_hashes": {row["layout_id"]: sha256_text(stable_json(row)) for row in layout_compact},
        "negative_fixture_hashes": {row["id"]: sha256_text(stable_json(row)) for row in negative_compact},
    }
    checks = {
        "full_summary_pass": data.get("summary", {}).get("pass") is True,
        "positive_layout_count": len(layout_compact) == 3,
        "positive_layouts_pass": all(row["summary_pass"] for row in layout_compact),
        "negative_fixture_count": len(negative_compact) == 5,
        "negative_fixtures_detected": all(row["detected_failure"] for row in negative_compact),
        "manifest_has_hashes": all("trace_hash" in row for row in manifest["positive_layouts"]) and all("compact_hash" in row for row in manifest["negative_fixtures"]),
        "compact_trace_has_event_order": all(row["event_reasons"] for row in layout_compact),
    }
    manifest["checks"] = checks
    compact_trace["checks"] = checks
    trace_hashes["checks"] = checks
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    COMPACT_TRACE.write_text(json.dumps(compact_trace, indent=2) + "\n")
    TRACE_HASHES.write_text(json.dumps(trace_hashes, indent=2) + "\n")
    write_artifact_hashes()
    print(json.dumps({"checks": checks, "trace_hashes": trace_hashes}, indent=2))
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
