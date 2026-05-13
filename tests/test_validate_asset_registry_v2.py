from __future__ import annotations

import copy
import json
from pathlib import Path

from tools.validate_asset_registry_v2 import validate_registry


def write_registry(tmp_path: Path, registry: dict) -> Path:
    path = tmp_path / "asset_registry_v2.json"
    path.write_text(json.dumps(registry))
    return path


def valid_production_weapon(tmp_path: Path) -> dict:
    model = tmp_path / "weapon.glb"
    screenshot = tmp_path / "shot.png"
    report = tmp_path / "material_report.json"
    model.write_text("glb")
    screenshot.write_text("png")
    report.write_text("{}")
    return {
        "asset_id": "hero_weapon_ready",
        "asset_class": "weapon",
        "role": "ready test weapon",
        "status": "production_ready",
        "paths": {
            "model": str(model),
            "preview": None,
            "textures": {
                "basecolor": str(tmp_path / "basecolor.png"),
                "normal": str(tmp_path / "normal.png"),
                "roughness": str(tmp_path / "roughness.png"),
                "metallic": str(tmp_path / "metallic.png"),
                "ao": str(tmp_path / "ao.png"),
            },
        },
        "provenance": {
            "source": "test",
            "license_risk": "local_only",
            "generation_route": "test",
            "notes": "test",
        },
        "geometry": {
            "meshes": 1,
            "triangles": 10,
            "bbox": {"min": [0, 0, 0], "max": [1, 1, 1], "size": [1, 1, 1]},
        },
        "materials": {
            "material_names": ["steel"],
            "material_map_count": 5,
            "pbr_complete": True,
            "texture_resolution": "2048",
        },
        "anchors": {
            "defined": ["Muzzle", "Grip_R", "Grip_L", "Optic", "PickupRoot"],
            "required_for_class": ["Muzzle", "Grip_R", "Grip_L", "Optic", "PickupRoot"],
        },
        "animations": {"has_rig": False, "clips": [], "mixer_ready": False},
        "lod": {"levels": ["lod0"], "screen_coverage": "hero"},
        "quality_gates": {
            "screenshot_nonblank": True,
            "fallback_allowed_in_evidence": False,
            "no_blocking_browser_errors": True,
            "no_missing_network_resources": True,
        },
        "evidence": {
            "gameplay_screenshots": [str(screenshot)],
            "preview_renders": [],
            "material_reports": [str(report)],
            "blender_screenshots": [],
        },
        "hashes": {"model_sha256": "a" * 64, "preview_sha256": None, "size_bytes": 3},
        "blockers": [],
    }


def valid_registry(tmp_path: Path) -> dict:
    return {
        "schema_version": "2.0.0",
        "generated_at": "2026-05-13T00:00:00+00:00",
        "experiment": "test",
        "assets": [valid_production_weapon(tmp_path)],
    }


def test_valid_registry(tmp_path: Path) -> None:
    path = write_registry(tmp_path, valid_registry(tmp_path))
    ok, errors = validate_registry(path)
    assert ok, errors


def test_missing_required_field(tmp_path: Path) -> None:
    registry = valid_registry(tmp_path)
    del registry["assets"][0]["asset_class"]
    ok, errors = validate_registry(write_registry(tmp_path, registry))
    assert not ok
    assert any("asset_class" in error for error in errors)


def test_missing_hero_pbr_maps_fails_for_production_ready(tmp_path: Path) -> None:
    registry = valid_registry(tmp_path)
    registry["assets"][0]["materials"]["material_map_count"] = 3
    ok, errors = validate_registry(write_registry(tmp_path, registry))
    assert not ok
    assert any("material_map_count >= 4" in error for error in errors)


def test_missing_weapon_anchors_fails_for_production_ready(tmp_path: Path) -> None:
    registry = valid_registry(tmp_path)
    registry["assets"][0]["anchors"]["defined"] = ["Muzzle"]
    ok, errors = validate_registry(write_registry(tmp_path, registry))
    assert not ok
    assert any("missing anchors" in error for error in errors)


def test_missing_evidence_path_fails_for_production_ready(tmp_path: Path) -> None:
    registry = valid_registry(tmp_path)
    registry["assets"][0]["evidence"]["gameplay_screenshots"] = [str(tmp_path / "missing.png")]
    ok, errors = validate_registry(write_registry(tmp_path, registry))
    assert not ok
    assert any("missing evidence or asset path" in error for error in errors)


def test_baseline_zero_maps_passes_when_blocked(tmp_path: Path) -> None:
    baseline = copy.deepcopy(valid_production_weapon(tmp_path))
    baseline["asset_id"] = "baseline_hero_weapon"
    baseline["status"] = "baseline_only"
    baseline["materials"]["material_map_count"] = 0
    baseline["materials"]["pbr_complete"] = False
    baseline["anchors"]["defined"] = []
    baseline["blockers"] = [
        {
            "gate": "hero_pbr",
            "reason": "baseline has no texture maps",
            "resolvable": True,
            "assigned_route": "hero_rifle_v2_001",
        }
    ]
    registry = valid_registry(tmp_path)
    registry["assets"] = [baseline]

    ok, errors = validate_registry(write_registry(tmp_path, registry))
    assert ok, errors


def test_target_missing_paths_passes_when_blocked(tmp_path: Path) -> None:
    target = copy.deepcopy(valid_production_weapon(tmp_path))
    target["asset_id"] = "target_hero_weapon"
    target["status"] = "target"
    target["paths"]["model"] = str(tmp_path / "future.glb")
    target["evidence"]["gameplay_screenshots"] = [str(tmp_path / "future.png")]
    target["materials"]["material_map_count"] = 0
    target["anchors"]["defined"] = []
    target["hashes"]["model_sha256"] = None
    target["blockers"] = [
        {
            "gate": "not_generated",
            "reason": "future target",
            "resolvable": True,
            "assigned_route": "next",
        }
    ]
    registry = valid_registry(tmp_path)
    registry["assets"] = [target]

    ok, errors = validate_registry(write_registry(tmp_path, registry))
    assert ok, errors
