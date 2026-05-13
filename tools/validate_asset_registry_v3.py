#!/usr/bin/env python3
"""Validate the Route F asset registry v3 material/provenance gate.

This first gate is intentionally dependency-free and standalone. It validates a
registry JSON file and checks disk paths under the local asset packet root.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ASSETS_ROOT = Path("experiments/pubg_like_asset_factory_20260513/assets")
DEFAULT_REQUIRED_MATERIAL_MAP_COUNT = 3
DEFAULT_REQUIRED_TEXTURE_KEYS = ("basecolor", "normal", "roughness")


def as_bool(value: Any) -> bool:
    return value is True


def get_nested(mapping: dict[str, Any], path: str) -> Any:
    current: Any = mapping
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def first_value(mapping: dict[str, Any], paths: tuple[str, ...]) -> Any:
    for path in paths:
        value = get_nested(mapping, path)
        if value not in (None, ""):
            return value
    return None


def is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def extract_file_path(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        path = value.get("path")
        if isinstance(path, str) and path.strip():
            return path.strip()
    return None


def resolve_asset_path(path_value: Any, assets_root: Path, asset_id: str) -> Path | None:
    raw_path = extract_file_path(path_value)
    if not raw_path:
        return None

    path = Path(raw_path)
    if path.is_absolute():
        return path

    parts = path.parts
    if parts and parts[0] == asset_id:
        return assets_root / path
    return assets_root / asset_id / path


def path_exists(path_value: Any, assets_root: Path, asset_id: str) -> tuple[bool, str | None]:
    resolved = resolve_asset_path(path_value, assets_root, asset_id)
    if resolved is None:
        return False, None
    return resolved.exists(), resolved.as_posix()


def material_map_count(asset: dict[str, Any]) -> int | None:
    value = first_value(asset, ("material_map_count", "materials.material_map_count"))
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def required_material_map_count(asset: dict[str, Any]) -> int:
    value = first_value(
        asset,
        (
            "required_material_map_count",
            "materials.required_material_map_count",
            "quality_gates.required_material_map_count",
        ),
    )
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return DEFAULT_REQUIRED_MATERIAL_MAP_COUNT
    return value


def required_texture_keys(asset: dict[str, Any]) -> list[str]:
    value = first_value(
        asset,
        (
            "required_texture_keys",
            "materials.required_texture_keys",
            "quality_gates.required_texture_keys",
        ),
    )
    if isinstance(value, list):
        keys = [item for item in value if isinstance(item, str) and item.strip()]
        if keys:
            return keys
    return list(DEFAULT_REQUIRED_TEXTURE_KEYS)


def texture_value(asset: dict[str, Any], key: str) -> Any:
    return first_value(asset, (f"textures.{key}", f"materials.textures.{key}"))


def provenance_present(asset: dict[str, Any]) -> bool:
    provenance = first_value(asset, ("provenance", "reference", "reference_sha256"))
    if is_present(provenance):
        return True

    reference_images = first_value(asset, ("provenance.reference_images",))
    return is_present(reference_images)


def validate_required_final_asset(
    asset: dict[str, Any],
    assets_root: Path,
    asset_index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    asset_id = asset.get("asset_id")
    if not isinstance(asset_id, str) or not asset_id.strip():
        errors.append(
            {
                "asset_index": asset_index,
                "asset_id": asset_id,
                "code": "missing_asset_id",
                "message": "Asset row is missing a non-empty asset_id.",
            }
        )
        asset_id = f"asset_{asset_index}"

    optimized_glb = first_value(
        asset,
        ("model.optimized_glb", "model_optimized_glb", "paths.model_optimized"),
    )
    raw_glb = first_value(asset, ("model.raw_glb", "model_raw_glb", "paths.model_raw"))

    optimized_exists, optimized_resolved = path_exists(optimized_glb, assets_root, asset_id)
    raw_exists, raw_resolved = path_exists(raw_glb, assets_root, asset_id)
    if not optimized_exists and not raw_exists:
        errors.append(
            {
                "asset_index": asset_index,
                "asset_id": asset_id,
                "code": "missing_model_glb",
                "message": "required_for_final asset needs model.optimized_glb or model.raw_glb to exist on disk.",
                "checked_paths": {
                    "optimized_glb": optimized_resolved,
                    "raw_glb": raw_resolved,
                },
            }
        )

    if not provenance_present(asset):
        errors.append(
            {
                "asset_index": asset_index,
                "asset_id": asset_id,
                "code": "missing_provenance_or_reference",
                "message": "required_for_final asset needs a non-empty provenance, reference, or reference_sha256 field.",
            }
        )

    actual_count = material_map_count(asset)
    required_count = required_material_map_count(asset)
    if actual_count is None:
        errors.append(
            {
                "asset_index": asset_index,
                "asset_id": asset_id,
                "code": "missing_material_map_count",
                "message": "required_for_final asset needs integer material_map_count or materials.material_map_count.",
                "required_material_map_count": required_count,
            }
        )
    elif actual_count < required_count:
        errors.append(
            {
                "asset_index": asset_index,
                "asset_id": asset_id,
                "code": "material_map_count_too_low",
                "message": "material_map_count is lower than required_material_map_count.",
                "material_map_count": actual_count,
                "required_material_map_count": required_count,
            }
        )

    for key in required_texture_keys(asset):
        value = texture_value(asset, key)
        exists, resolved = path_exists(value, assets_root, asset_id)
        if not exists:
            errors.append(
                {
                    "asset_index": asset_index,
                    "asset_id": asset_id,
                    "code": "missing_required_texture",
                    "message": f"required_for_final asset needs texture key '{key}' to exist on disk.",
                    "texture_key": key,
                    "checked_path": resolved,
                }
            )

    if as_bool(asset.get("probe_only")):
        warnings.append(
            {
                "asset_index": asset_index,
                "asset_id": asset_id,
                "code": "probe_marked_required_for_final",
                "message": "Asset is marked probe_only and required_for_final; final gates still apply.",
            }
        )

    return errors, warnings


def validate_probe_asset(asset: dict[str, Any], asset_index: int) -> list[dict[str, Any]]:
    asset_id = asset.get("asset_id")
    warnings: list[dict[str, Any]] = []

    if as_bool(asset.get("probe_only")):
        warnings.append(
            {
                "asset_index": asset_index,
                "asset_id": asset_id,
                "code": "probe_only_not_final",
                "message": "probe_only asset is recorded for evidence but is not gated as final production content.",
            }
        )
    elif asset.get("required_for_final") is not False:
        warnings.append(
            {
                "asset_index": asset_index,
                "asset_id": asset_id,
                "code": "not_required_for_final",
                "message": "Asset is not required_for_final=true, so Route F final material gates were not applied.",
            }
        )

    return warnings


def validate_registry(registry_path: Path, assets_root: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "registry_path": registry_path.as_posix(),
            "assets_root": assets_root.as_posix(),
            "valid": False,
            "asset_count": 0,
            "required_for_final_count": 0,
            "errors": [
                {
                    "code": "registry_file_not_found",
                    "message": "Registry JSON file does not exist.",
                    "path": registry_path.as_posix(),
                }
            ],
            "warnings": [],
        }
    except json.JSONDecodeError as exc:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "registry_path": registry_path.as_posix(),
            "assets_root": assets_root.as_posix(),
            "valid": False,
            "asset_count": 0,
            "required_for_final_count": 0,
            "errors": [
                {
                    "code": "invalid_json",
                    "message": str(exc),
                    "line": exc.lineno,
                    "column": exc.colno,
                }
            ],
            "warnings": [],
        }

    if not isinstance(registry, dict):
        errors.append(
            {
                "code": "registry_not_object",
                "message": "Registry root must be a JSON object.",
            }
        )
        assets: list[Any] = []
    else:
        assets = registry.get("assets", [])
        if not isinstance(assets, list):
            errors.append(
                {
                    "code": "assets_not_array",
                    "message": "Registry must contain an assets array.",
                }
            )
            assets = []

    required_for_final_count = 0
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            errors.append(
                {
                    "asset_index": index,
                    "code": "asset_not_object",
                    "message": "Each assets entry must be an object.",
                }
            )
            continue

        if as_bool(asset.get("required_for_final")):
            required_for_final_count += 1
            asset_errors, asset_warnings = validate_required_final_asset(
                asset, assets_root, index
            )
            errors.extend(asset_errors)
            warnings.extend(asset_warnings)
        else:
            warnings.extend(validate_probe_asset(asset, index))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registry_path": registry_path.as_posix(),
        "assets_root": assets_root.as_posix(),
        "valid": not errors,
        "asset_count": len(assets),
        "required_for_final_count": required_for_final_count,
        "gates": {
            "required_for_final_model_glb_exists": True,
            "required_for_final_provenance_or_reference_present": True,
            "required_for_final_material_map_count": True,
            "required_for_final_required_texture_keys_exist": True,
        },
        "errors": errors,
        "warnings": warnings,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a Route F asset_registry_v3 JSON file against the first material/provenance gate."
    )
    parser.add_argument("registry_json", type=Path, help="Registry JSON file to validate.")
    parser.add_argument(
        "--assets-root",
        type=Path,
        default=DEFAULT_ASSETS_ROOT,
        help=f"Asset packet root. Defaults to {DEFAULT_ASSETS_ROOT}",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = validate_registry(args.registry_json, args.assets_root)
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
