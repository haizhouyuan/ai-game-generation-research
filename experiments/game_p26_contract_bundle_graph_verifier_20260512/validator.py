#!/usr/bin/env python3
"""Validate P26 contract bundle graph verifier outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


REQUIRED_TRUE_CHECKS = [
    "contract_bundle_valid",
    "topological_order_valid",
    "cycle_counter_detected",
    "duplicate_node_counter_detected",
    "stale_bundle_counter_detected",
    "p25_missing_artifact_counter_inherited",
    "p25_tampered_hash_counter_inherited",
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
    result_path = ROOT / "validator_result.json"
    hash_path = ROOT / "artifact_hashes.json"
    closeout_path = ROOT / "closeout.md"
    missing = [str(path) for path in [result_path, hash_path, closeout_path] if not path.exists()]
    result = load_json(result_path) if result_path.exists() else {}
    hashes = load_json(hash_path) if hash_path.exists() else {"artifacts": []}

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

    summary = {
        "overall_pass": bool(result.get("overall_pass"))
        and all(check_rows.values())
        and not missing
        and all(row["pass"] for row in hash_rows),
        "missing_required_files": missing,
        "checks": check_rows,
        "hash_rows": hash_rows,
        "boundary": result.get("boundaries", []),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
