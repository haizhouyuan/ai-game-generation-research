#!/usr/bin/env python3
"""Validate tactical visual-upgrade asset registry v2 files."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = (
    REPO_ROOT
    / "experiments"
    / "tactical_game_visual_upgrade_20260520"
    / "schemas"
    / "asset_packet.schema.json"
)
WEAPON_ANCHORS = {"Muzzle", "Grip_R", "Grip_L", "Optic", "PickupRoot"}
CHARACTER_ANCHORS = {"Weapon_R", "Head", "Spine", "Foot_L", "Foot_R"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def resolve_repo_path(raw_path: str | None) -> Path | None:
    if not raw_path:
        return None
    path = Path(raw_path)
    return path if path.is_absolute() else REPO_ROOT / path


def list_schema_errors(registry: dict[str, Any], schema_path: Path = DEFAULT_SCHEMA) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft7Validator(schema)
    return [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(registry), key=lambda err: list(err.path))
    ]


def entry_paths(entry: dict[str, Any]) -> list[str]:
    evidence = entry.get("evidence", {})
    paths = entry.get("paths", {})
    values: list[str] = []
    for key in ("model", "preview"):
        value = paths.get(key)
        if value:
            values.append(value)
    for bucket in ("gameplay_screenshots", "preview_renders", "material_reports", "blender_screenshots"):
        values.extend(evidence.get(bucket, []))
    return values


def list_semantic_errors(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()

    for index, entry in enumerate(registry.get("assets", [])):
        asset_id = entry.get("asset_id", f"<asset {index}>")
        status = entry.get("status")
        asset_class = entry.get("asset_class")
        blockers = entry.get("blockers", [])
        materials = entry.get("materials", {})
        anchors = entry.get("anchors", {})
        quality_gates = entry.get("quality_gates", {})

        if asset_id in seen:
            errors.append(f"{asset_id}: duplicate asset_id")
        seen.add(asset_id)

        if status in {"baseline_only", "target"} and not blockers:
            errors.append(f"{asset_id}: {status} assets must explain remaining blockers")

        if status == "production_ready" and blockers:
            errors.append(f"{asset_id}: production_ready assets must not carry blockers")

        if status == "production_ready":
            if materials.get("material_map_count", 0) < 4:
                errors.append(f"{asset_id}: production_ready asset requires material_map_count >= 4")
            if quality_gates.get("fallback_allowed_in_evidence"):
                errors.append(f"{asset_id}: production_ready evidence cannot allow runtime fallback")
            if not quality_gates.get("screenshot_nonblank"):
                errors.append(f"{asset_id}: production_ready asset requires nonblank screenshot gate")

        if asset_class == "weapon" and status == "production_ready":
            defined = set(anchors.get("defined", []))
            missing = sorted(WEAPON_ANCHORS - defined)
            if missing:
                errors.append(f"{asset_id}: production_ready weapon missing anchors {missing}")

        if asset_class == "character" and status == "production_ready":
            defined = set(anchors.get("defined", []))
            missing = sorted(CHARACTER_ANCHORS - defined)
            if missing:
                errors.append(f"{asset_id}: production_ready character missing anchors {missing}")
            animations = entry.get("animations", {})
            if not animations.get("has_rig") or not animations.get("mixer_ready") or not animations.get("clips"):
                errors.append(f"{asset_id}: production_ready character requires rig, mixer readiness, and clips")

        should_check_paths = status in {"baseline_only", "production_ready"}
        if should_check_paths:
            for raw_path in entry_paths(entry):
                path = resolve_repo_path(raw_path)
                if path is not None and not path.exists():
                    errors.append(f"{asset_id}: missing evidence or asset path {raw_path}")

        if status == "production_ready":
            model_sha = entry.get("hashes", {}).get("model_sha256")
            if not model_sha:
                errors.append(f"{asset_id}: production_ready asset requires model_sha256")

    return errors


def validate_registry(path: Path) -> tuple[bool, list[str]]:
    registry = load_json(path)
    if not isinstance(registry, dict):
        return False, [f"{path}: registry must be a JSON object"]

    errors = list_schema_errors(registry)
    if not errors:
        errors.extend(list_semantic_errors(registry))
    return not errors, errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_asset_registry_v2.py <asset_registry_v2.json>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    try:
        ok, errors = validate_registry(path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not ok:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    registry = load_json(path)
    print(f"validated {len(registry.get('assets', []))} asset registry v2 entries in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
