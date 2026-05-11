#!/usr/bin/env python3
"""P24 version migration and artifact-integrity manifest checks for scene-CI reviewer contracts."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
P22_ROOT = ROOT.parents[0] / "game_p22_scene_ci_exit_code_reviewer_contract_20260512"
P23_ROOT = ROOT.parents[0] / "game_p23_scene_ci_reviewer_contract_negative_fixtures_20260512"
OUT = ROOT / "outputs"
P22_REPORT = P22_ROOT / "outputs" / "p22_reviewer_contract_report.json"
P22_EXIT_MATRIX = P22_ROOT / "outputs" / "p22_exit_code_matrix.json"
P22_PACKET = P22_ROOT / "outputs" / "p22_reviewer_contract_packet.md"
P23_NEGATIVE_MATRIX = P23_ROOT / "outputs" / "p23_scene_ci_negative_contract_review_matrix.json"
P23_COMPACT = P23_ROOT / "outputs" / "p23_compact_review_matrix.md"
VERSION_REPORT = OUT / "p24_reviewer_contract_version_migration_report.json"
INTEGRITY_MANIFEST = OUT / "p24_artifact_integrity_manifest.json"
INTEGRITY_MATRIX = OUT / "p24_artifact_integrity_check_matrix.json"
REVIEW_PACKET = OUT / "p24_reviewer_contract_version_integrity_packet.md"
ARTIFACT_HASHES = OUT / "artifact_hashes.json"

SUPPORTED_CONTRACT_VERSION = "2.0"
CONTRACT_ID = "scene_ci_reviewer_contract_v2_20260512"


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def migrate_contract(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_version": SUPPORTED_CONTRACT_VERSION,
        "contract_id": CONTRACT_ID,
        "source_contract_version": str(report.get("contract_version", "1.0-implicit")),
        "source_report_sha256": sha256_text(stable_json(report)),
        "mode_rows": report.get("mode_rows", []),
        "exit_code_contract": report.get("exit_code_contract", {}),
        "boundaries": report.get("boundaries", []),
        "review_only": True,
    }


def validate_contract(payload: dict[str, Any]) -> dict[str, Any]:
    required = {"contract_version", "contract_id", "source_report_sha256", "mode_rows", "exit_code_contract", "review_only"}
    missing = sorted(required - set(payload))
    version_ok = payload.get("contract_version") == SUPPORTED_CONTRACT_VERSION
    modes = {row.get("mode") for row in payload.get("mode_rows", [])}
    expected_modes = {"match", "diff", "candidate-update", "denied-update"}
    return {
        "pass": not missing and version_ok and expected_modes <= modes,
        "missing_fields": missing,
        "version_ok": version_ok,
        "available_modes": sorted(mode for mode in modes if mode),
        "expected_modes": sorted(expected_modes),
    }


def build_manifest(paths: list[Path]) -> dict[str, Any]:
    rows = []
    for path in paths:
        rows.append({
            "path": str(path),
            "relative_to_experiment": str(path.relative_to(ROOT.parents[0])) if path.is_relative_to(ROOT.parents[0]) else str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return {
        "manifest_version": "1.0",
        "contract_id": CONTRACT_ID,
        "artifacts": rows,
        "boundary": "manifest covers local reviewer-contract artifacts only",
    }


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for row in manifest.get("artifacts", []):
        path = Path(row["path"])
        exists = path.exists()
        current_sha = sha256_file(path) if exists else None
        rows.append({
            "path": str(path),
            "exists": exists,
            "expected_sha256": row.get("sha256"),
            "current_sha256": current_sha,
            "pass": exists and current_sha == row.get("sha256"),
        })
    return {
        "pass": bool(rows) and all(row["pass"] for row in rows),
        "rows": rows,
    }


def tamper_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(manifest)
    if payload.get("artifacts"):
        payload["artifacts"][0]["sha256"] = "tampered-" + payload["artifacts"][0]["sha256"][9:]
    return payload


def missing_artifact_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(manifest)
    payload.setdefault("artifacts", []).append({
        "path": str(ROOT / "outputs" / "missing_artifact_counter.json"),
        "relative_to_experiment": "game_p24_reviewer_contract_version_integrity_manifest_20260512/outputs/missing_artifact_counter.json",
        "bytes": 1,
        "sha256": "0" * 64,
    })
    return payload


def write_review_packet(report: dict[str, Any]) -> None:
    lines = [
        "# P24 Scene-CI Reviewer Contract Version And Integrity Packet",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    for key, value in report["checks"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend([
        "",
        "## Boundary",
        "",
        "- This validates local reviewer-contract version and artifact integrity only.",
        "- It does not claim screenshot/visual QA.",
        "- It does not claim mesh-accurate GLB collision.",
    ])
    REVIEW_PACKET.write_text("\n".join(lines) + "\n")


def write_artifact_hashes() -> None:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != ARTIFACT_HASHES and "__pycache__" not in path.parts:
            rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    write_json(ARTIFACT_HASHES, rows)


def run_all() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    p22_report = load_json(P22_REPORT)
    migrated = migrate_contract(p22_report)
    missing_field = copy.deepcopy(migrated)
    missing_field.pop("source_report_sha256", None)
    future = copy.deepcopy(migrated)
    future["contract_version"] = "99.0"
    version_checks = {
        "migration_v1_to_v2_pass": validate_contract(migrated)["pass"],
        "missing_field_counter_fails": not validate_contract(missing_field)["pass"],
        "future_version_counter_fails": not validate_contract(future)["pass"],
    }
    manifest = build_manifest([P22_REPORT, P22_EXIT_MATRIX, P22_PACKET, P23_NEGATIVE_MATRIX, P23_COMPACT])
    write_json(INTEGRITY_MANIFEST, manifest)
    valid_manifest = validate_manifest(manifest)
    tampered = validate_manifest(tamper_manifest(manifest))
    missing = validate_manifest(missing_artifact_manifest(manifest))
    integrity_checks = {
        "manifest_hashes_pass": valid_manifest["pass"],
        "tampered_hash_counter_detected": not tampered["pass"],
        "missing_artifact_counter_detected": not missing["pass"],
    }
    report = {
        "batch": "P24-A scene-CI reviewer-contract version migration and artifact integrity manifest",
        "version_migration": {
            "migrated_contract": migrated,
            "migration_validation": validate_contract(migrated),
            "missing_field_counter": validate_contract(missing_field),
            "future_version_counter": validate_contract(future),
        },
        "integrity": {
            "manifest": manifest,
            "valid_manifest": valid_manifest,
            "tampered_hash_counter": tampered,
            "missing_artifact_counter": missing,
        },
        "checks": {
            **version_checks,
            **integrity_checks,
        },
        "overall_pass": all(version_checks.values()) and all(integrity_checks.values()),
        "boundaries": [
            "P24 validates local reviewer-contract version and artifact integrity only.",
            "It does not claim screenshot/visual QA.",
            "It does not claim mesh-accurate GLB collision.",
        ],
    }
    write_json(VERSION_REPORT, report["version_migration"])
    write_json(INTEGRITY_MATRIX, report)
    write_review_packet(report)
    write_artifact_hashes()
    return report


def main() -> int:
    report = run_all()
    print(json.dumps({"overall_pass": report["overall_pass"], "checks": report["checks"]}, indent=2))
    return 0 if report["overall_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
