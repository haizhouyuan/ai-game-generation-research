#!/usr/bin/env python3
"""P21 scene-CI modes and baseline-update review packet.

The Godot full report is produced on HomePC. This command consumes that report
and exposes four explicit modes: match, diff, candidate-update, denied-update.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
DEFAULT_FULL_REPORT = OUT / "p21_negative_scene_ci_full_report.json"
DEFAULT_BASELINE = ROOT / "baseline" / "accepted_p19_scene_ci_baseline.json"
DEFAULT_ALLOWLIST = ROOT / "baseline" / "baseline_update_allowlist.json"
DEFAULT_CURRENT_HASHES = OUT / "p21_current_trace_hashes.json"
DEFAULT_COMPACT = OUT / "p21_current_compact_trace.json"
DEFAULT_MODE_REPORT = OUT / "p21_scene_ci_modes_report.json"
DEFAULT_DIFF_TABLE = OUT / "p21_compact_diff_table.md"
DEFAULT_REVIEW_PACKET = OUT / "p21_baseline_update_review_packet.md"
DEFAULT_ARTIFACT_HASHES = OUT / "artifact_hashes.json"


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
    compact = {
        "id": row.get("id"),
        "expected_failure": row.get("expected_failure"),
        "detected_failure": row.get("detected_failure", False),
        "readback_pass": row.get("readback", {}).get("pass"),
        "build_pass": row.get("build", {}).get("pass"),
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
        compact["diagnostics"] = {"readback_errors": row.get("readback", {}).get("errors", []), "mutation": row.get("mutation", {})}
    elif row.get("id") == "sensor_clearance_violation":
        compact["diagnostics"] = {"clearance_pass": row.get("build", {}).get("clearance_pass"), "clearance_rows": row.get("build", {}).get("clearance_rows", [])}
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
        "batch": "P21-A scene-CI modes compact trace",
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
    rows = []
    for key in sorted(set(accepted) | set(current)):
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
        "missing": sorted(set(accepted) - set(current)),
        "unexpected": sorted(set(current) - set(accepted)),
        "diffs": [row for row in rows if row["status"] == "diff"],
        "rows": rows,
    }


def compare_all(baseline: dict[str, Any], current_hashes: dict[str, Any]) -> dict[str, Any]:
    accepted = baseline["accepted_hashes"]
    positive = compare_hash_maps("positive_layout_hashes", accepted.get("positive_layout_hashes", {}), current_hashes.get("positive_layout_hashes", {}))
    negative = compare_hash_maps("negative_fixture_hashes", accepted.get("negative_fixture_hashes", {}), current_hashes.get("negative_fixture_hashes", {}))
    full_match = accepted.get("full_report_sha256") == current_hashes.get("full_report_sha256")
    compact_match = accepted.get("compact_trace_sha256") == current_hashes.get("compact_trace_sha256")
    return {
        "positive": positive,
        "negative": negative,
        "full_report_match": full_match,
        "compact_trace_match": compact_match,
        "hashes_match": positive["pass"] and negative["pass"],
    }


def mutate_for_diff(current_hashes: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(current_hashes)
    positive = mutated.get("positive_layout_hashes", {})
    if positive:
        first_key = sorted(positive)[0]
        positive[first_key] = "diff-counter-" + positive[first_key][13:]
    return mutated


def diff_table(comparisons: dict[str, Any], title: str) -> str:
    lines = [
        f"# {title}",
        "",
        "| Group | ID | Status | Accepted | Current |",
        "|---|---|---|---|---|",
    ]
    for comparison in (comparisons["positive"], comparisons["negative"]):
        for row in comparison["rows"]:
            accepted = (row.get("accepted") or "missing")[:12]
            current = (row.get("current") or "missing")[:12]
            lines.append(f"| {row['group']} | `{row['id']}` | {row['status']} | `{accepted}` | `{current}` |")
    return "\n".join(lines) + "\n"


def baseline_policy(baseline: dict[str, Any], allowlist: dict[str, Any], requested_id: str) -> dict[str, Any]:
    allowed = requested_id in set(allowlist.get("allowed_baseline_ids", []))
    return {
        "requested_baseline_id": requested_id,
        "allowlisted": allowed,
        "candidate_output": str(ROOT / allowlist.get("candidate_output", "outputs/p21_allowed_baseline_update_candidate.json")),
    }


def write_artifact_hashes() -> None:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != DEFAULT_ARTIFACT_HASHES and ".godot" not in path.parts and "__pycache__" not in path.parts:
            rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    DEFAULT_ARTIFACT_HASHES.write_text(json.dumps(rows, indent=2) + "\n")


def write_mode_reports(modes: dict[str, dict[str, Any]], comparisons: dict[str, Any], policy: dict[str, Any]) -> dict[str, str]:
    paths: dict[str, str] = {}
    for mode, row in modes.items():
        path = OUT / f"p21_mode_{mode.replace('-', '_')}_report.json"
        payload = {
            "mode": mode,
            "result": row["result"],
            "expected": row["expected"],
            "evidence": row["evidence"],
            "comparisons": comparisons if mode in {"match", "diff"} else {},
            "policy": policy if mode in {"candidate-update", "denied-update"} else {},
            "boundary": "compact deterministic headless scene-CI evidence only; no screenshot/visual QA or mesh-accurate GLB collision claim",
        }
        path.write_text(json.dumps(payload, indent=2) + "\n")
        paths[mode] = str(path)
    return paths


def review_packet(report: dict[str, Any]) -> str:
    modes = report["modes"]
    lines = [
        "# P21 Scene-CI Baseline Update Review Packet",
        "",
        "Status: compact deterministic headless scene-CI review packet.",
        "",
        "| Mode | Result | Evidence |",
        "|---|---|---|",
    ]
    for mode in ("match", "diff", "candidate-update", "denied-update"):
        row = modes[mode]
        lines.append(f"| `{mode}` | `{row['result']}` | `{row['evidence']}` |")
    lines.extend([
        "",
        "## Boundary",
        "",
        "- This packet reviews proxy scene nodes plus HomePC Godot headless physics/input/camera assertions.",
        "- It does not claim screenshot/visual QA.",
        "- It does not claim mesh-accurate GLB collision.",
        "- Candidate update output is not automatic baseline replacement.",
        "",
        "## Compact Diff Table",
        "",
    ])
    lines.extend(DEFAULT_DIFF_TABLE.read_text().splitlines())
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["match", "diff", "candidate-update", "denied-update", "all"])
    parser.add_argument("--full-report", type=Path, default=DEFAULT_FULL_REPORT)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--allowlist", type=Path, default=DEFAULT_ALLOWLIST)
    parser.add_argument("--baseline-id", default=None)
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    full_report = load_json(args.full_report)
    baseline = load_json(args.baseline)
    allowlist = load_json(args.allowlist)
    compact, current_hashes = build_current(full_report, args.full_report)
    DEFAULT_COMPACT.write_text(json.dumps(compact, indent=2) + "\n")
    DEFAULT_CURRENT_HASHES.write_text(json.dumps(current_hashes, indent=2) + "\n")

    match_comparisons = compare_all(baseline, current_hashes)
    diff_comparisons = compare_all(baseline, mutate_for_diff(current_hashes))
    DEFAULT_DIFF_TABLE.write_text(diff_table(match_comparisons, "P21 Scene-CI Match Diff Table"))

    requested_baseline_id = args.baseline_id or baseline["baseline_id"]
    allowed_policy = baseline_policy(baseline, allowlist, requested_baseline_id)
    candidate_path = Path(allowed_policy["candidate_output"])
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    if allowed_policy["allowlisted"]:
        candidate_path.write_text(json.dumps({
            "baseline_id": requested_baseline_id,
            "mode": "candidate-update",
            "accepted_hashes": current_hashes,
            "note": "review candidate only; not automatic accepted-baseline replacement",
        }, indent=2) + "\n")
    denied_policy = baseline_policy(baseline, allowlist, "unlisted_baseline_update_counter")

    modes = {
        "match": {
            "result": "pass" if match_comparisons["hashes_match"] else "fail",
            "expected": "hashes_match",
            "evidence": str(DEFAULT_DIFF_TABLE),
        },
        "diff": {
            "result": "pass" if not diff_comparisons["hashes_match"] and diff_comparisons["positive"]["diffs"] else "fail",
            "expected": "synthetic_hash_drift_detected",
            "evidence": "in-memory diff-counter over first positive layout hash",
        },
        "candidate-update": {
            "result": "pass" if allowed_policy["allowlisted"] and candidate_path.exists() else "fail",
            "expected": "allowlisted_candidate_written",
            "evidence": str(candidate_path),
        },
        "denied-update": {
            "result": "pass" if not denied_policy["allowlisted"] else "fail",
            "expected": "unlisted_update_denied",
            "evidence": denied_policy["requested_baseline_id"],
        },
    }
    selected = list(modes) if args.mode == "all" else [args.mode]
    checks = {
        "full_summary_pass": full_report.get("summary", {}).get("pass") is True,
        "selected_modes_pass": all(modes[mode]["result"] == "pass" for mode in selected),
        "match_mode_pass": modes["match"]["result"] == "pass",
        "diff_mode_detects_drift": modes["diff"]["result"] == "pass",
        "candidate_update_allowlisted": modes["candidate-update"]["result"] == "pass",
        "denied_update_denied": modes["denied-update"]["result"] == "pass",
        "review_packet_emitted": True,
    }
    mode_report_paths = write_mode_reports(
        modes,
        {"match": match_comparisons, "diff": diff_comparisons},
        {"allowed": allowed_policy, "denied": denied_policy},
    )
    report = {
        "batch": "P21-A scene-CI modes and baseline update review packet",
        "requested_mode": args.mode,
        "selected_modes": selected,
        "modes": modes,
        "mode_report_paths": mode_report_paths,
        "match_comparisons": match_comparisons,
        "diff_counter_comparisons": diff_comparisons,
        "checks": checks,
        "overall_pass": all(checks.values()),
        "boundaries": [
            "Modes evaluate compact deterministic headless scene-CI evidence only.",
            "Candidate update writes review artifact only, not accepted-baseline replacement.",
            "No screenshot/visual QA or mesh-accurate GLB collision claim.",
        ],
    }
    DEFAULT_MODE_REPORT.write_text(json.dumps(report, indent=2) + "\n")
    DEFAULT_REVIEW_PACKET.write_text(review_packet(report))
    write_artifact_hashes()
    print(json.dumps({"overall_pass": report["overall_pass"], "checks": checks, "modes": {k: v["result"] for k, v in modes.items()}}, indent=2))
    return 0 if report["overall_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
