#!/usr/bin/env python3
"""Verify artifact hash manifests against actual files."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_evidence_shape(manifest_path: Path) -> tuple[int, str]:
    """Verify manifest using evidence directory shape.

    Returns (verified_count, error_message).
    """
    manifest = json.loads(manifest_path.read_text())
    base_dir = manifest_path.parent
    verified = 0

    for rel_path, entry in manifest.items():
        if not isinstance(rel_path, str):
            return 0, f"manifest key must be string, got {type(rel_path).__name__}"
        if not isinstance(entry, dict):
            return 0, f"entry for '{rel_path}' must be object, got {type(entry).__name__}"
        if "sha256" not in entry:
            return 0, f"entry for '{rel_path}' missing sha256"

        file_path = base_dir / rel_path
        if not file_path.exists():
            return 0, f"missing file: {file_path}"
        if "size_bytes" in entry and entry["size_bytes"] != file_path.stat().st_size:
            return 0, (
                f"size mismatch for {rel_path}: "
                f"expected {entry['size_bytes']}, got {file_path.stat().st_size}"
            )

        expected = entry["sha256"]
        actual = compute_sha256(file_path)
        if expected != actual:
            return 0, f"hash mismatch for {rel_path}: expected {expected}, got {actual}"

        verified += 1

    return verified, ""


def verify_asset_chain_shape(manifest_path: Path) -> tuple[int, str]:
    """Verify manifest using asset-chain shape.

    Returns (verified_count, error_message).
    """
    manifest = json.loads(manifest_path.read_text())
    if not isinstance(manifest, dict):
        return 0, "manifest must be object"
    if "artifacts" not in manifest:
        return 0, "manifest missing 'artifacts' key"
    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, list):
        return 0, "'artifacts' must be list"

    verified = 0
    cwd = Path.cwd()

    for i, item in enumerate(artifacts):
        if not isinstance(item, dict):
            return 0, f"artifacts[{i}] must be object, got {type(item).__name__}"
        if "path" not in item:
            return 0, f"artifacts[{i}] missing 'path'"
        if "sha256" not in item:
            return 0, f"artifacts[{i}] missing 'sha256'"

        rel_path = item["path"]
        file_path = Path(rel_path)
        if not file_path.is_absolute():
            # Try repo-relative from cwd first
            candidates = [cwd / rel_path, manifest_path.parent / rel_path]
            for candidate in candidates:
                if candidate.exists():
                    file_path = candidate
                    break
            else:
                return 0, f"missing file: {rel_path} (tried {candidates[0]}, {candidates[1]})"

        if not file_path.exists():
            return 0, f"missing file: {file_path}"

        expected = item["sha256"]
        actual = compute_sha256(file_path)
        if expected != actual:
            return 0, f"hash mismatch for {rel_path}: expected {expected}, got {actual}"

        verified += 1

    return verified, ""


def detect_shape(manifest: dict) -> str | None:
    """Detect manifest shape: 'evidence' or 'asset_chain'."""
    if "artifacts" in manifest and isinstance(manifest.get("artifacts"), list):
        return "asset_chain"
    # Evidence shape: top-level keys are relative paths to files
    # and values are dicts (not a list)
    if manifest and all(
        isinstance(v, dict) for v in manifest.values()
    ):
        return "evidence"
    return None


def verify_manifest(manifest_path: Path) -> bool:
    """Verify a single manifest file. Returns True on success."""
    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        print(f"invalid JSON in {manifest_path}: {e}", file=sys.stderr)
        return False

    if not isinstance(manifest, dict):
        print(f"manifest must be object, got {type(manifest).__name__}", file=sys.stderr)
        return False

    shape = detect_shape(manifest)
    if shape is None:
        print(f"unsupported manifest shape in {manifest_path}", file=sys.stderr)
        return False

    if shape == "evidence":
        count, err = verify_evidence_shape(manifest_path)
    else:
        count, err = verify_asset_chain_shape(manifest_path)

    if err:
        print(err, file=sys.stderr)
        return False

    print(f"verified {count} hashes in {manifest_path}")
    return True


def main(argv: list[str]) -> int:
    if not argv[1:]:
        print("Usage: verify_artifact_hashes.py <manifest>...", file=sys.stderr)
        return 1

    results = [verify_manifest(Path(p)) for p in argv[1:]]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
