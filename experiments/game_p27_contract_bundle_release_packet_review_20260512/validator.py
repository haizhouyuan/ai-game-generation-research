#!/usr/bin/env python3
"""Validate P27 release packet review outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "input_manifest.json",
    "run_p27_release_packet_review.py",
    "validator.py",
    "validator_result.json",
    "release_packet.json",
    "graph_diff_packet.json",
    "allowlisted_update_candidate.json",
    "rejected_update_candidate.json",
    "artifact_hashes.json",
    "closeout.md",
]

REQUIRED_TRUE_CHECKS = [
    "baseline_p26_bundle_loaded",
    "baseline_topological_order_preserved",
    "allowlisted_update_candidate_accepted",
    "rejected_update_candidate_blocked",
    "duplicate_node_counter_inherited",
    "cycle_counter_inherited",
    "missing_artifact_counter_inherited",
    "tampered_hash_counter_inherited",
    "graph_diff_packet_compact_hashable",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).exists()]
    result = load_json(ROOT / "validator_result.json") if (ROOT / "validator_result.json").exists() else {}
    hashes = load_json(ROOT / "artifact_hashes.json") if (ROOT / "artifact_hashes.json").exists() else {"artifacts": []}
    graph_diff = load_json(ROOT / "graph_diff_packet.json") if (ROOT / "graph_diff_packet.json").exists() else {}
    closeout = (ROOT / "closeout.md").read_text(encoding="utf-8") if (ROOT / "closeout.md").exists() else ""

    check_rows = {key: bool(result.get("checks", {}).get(key)) for key in REQUIRED_TRUE_CHECKS}
    hash_rows = []
    for row in hashes.get("artifacts", []):
        path = Path(row["path"])
        exists = path.exists()
        current = sha256_file(path) if exists else None
        hash_rows.append(
            {
                "path": str(path),
                "exists": exists,
                "expected_sha256": row.get("sha256"),
                "current_sha256": current,
                "pass": exists and current == row.get("sha256"),
            }
        )

    graph_diff_size = (ROOT / "graph_diff_packet.json").stat().st_size if (ROOT / "graph_diff_packet.json").exists() else 0
    graph_diff_ok = graph_diff_size < 12000 and bool(graph_diff.get("sha256"))
    closeout_ok = "P27 complete / lane active / program active" in closeout and "P28 Candidate" in closeout

    summary = {
        "overall_pass": bool(result.get("overall_pass"))
        and not missing
        and all(check_rows.values())
        and all(row["pass"] for row in hash_rows)
        and graph_diff_ok
        and closeout_ok,
        "missing_required_files": missing,
        "checks": check_rows,
        "hash_rows": hash_rows,
        "graph_diff_bytes": graph_diff_size,
        "graph_diff_hashable": graph_diff_ok,
        "closeout_contract_ok": closeout_ok,
        "boundary": result.get("boundaries", []),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
