#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
INDEX = ROOT / "index.html"
MODELS = ROOT / "assets" / "models"
EVIDENCE = ROOT / "evidence"
SOURCE = pathlib.Path("/Users/yuanshaochen/Documents/14.html")

EXPECTED_SOURCE_SHA256 = "ad82e7d5da575f8e2f783b39e1bfed4736dc032faa6be7ed8be6a66dacbad8b3"
WEAPON_ASSETS = {
    "pistol": "pistol_m5_candidate.glb",
    "shotgun": "shotgun_m5_candidate.glb",
    "rifle": "groza_procedural_candidate.glb",
    "dmr": "dmr_m5_candidate.glb",
}
FINAL_ASSET_KIT = {
    "characterPlayer": "character_player_final.glb",
    "characterEnemy": "character_enemy_final.glb",
    "lootAmmo": "loot_ammo_final.glb",
    "lootBandage": "loot_bandage_final.glb",
    "lootFirstAid": "loot_firstaid_final.glb",
    "lootMedkit": "loot_medkit_final.glb",
    "lootRevive": "loot_revive_final.glb",
    "lootVest": "loot_vest_final.glb",
    "lootHelmet": "loot_helmet_final.glb",
    "propCrate": "prop_crate_final.glb",
    "propContainer": "prop_container_final.glb",
    "propLadderStair": "prop_ladder_stair_final.glb",
    "propInteriorFurniture": "prop_interior_furniture_final.glb",
    "propBuildingDetail": "prop_building_detail_final.glb",
    "propGroundWallFence": "prop_ground_wall_fence_final.glb",
    "propTree": "prop_tree_final.glb",
    "propRockCluster": "prop_rock_cluster_final.glb",
}
EXPECTED_SHOWCASE_COUNTS = {
    "characters_evidence_cdp_report.json": 2,
    "loot_evidence_cdp_report.json": 7,
    "environment_evidence_cdp_report.json": 8,
    "final_evidence_cdp_report.json": 13,
}
REQUIRED_MATRIX_CLASSES = {
    "first-person weapons",
    "third-person/player/NPC weapons",
    "player body",
    "NPC body",
    "helmet",
    "armor/plate carrier",
    "backpack, pouches, straps, rig, gloves, pads",
    "ammo, med items, revive item, armor/helmet pickups",
    "crates and storage props",
    "containers",
    "ladders/stairs",
    "rocks",
    "trees/bushes/grass",
    "building exteriors",
    "building interiors",
    "doors/windows/vents/pipes/utility details",
    "ground/roads/walls/fences",
    "lighting, sky, fog, shadow configuration",
}
EVIDENCE_REPORTS = [
    "rifle_evidence_cdp_first_report.json",
    "rifle_evidence_cdp_third_report.json",
    "weapons_evidence_cdp_report.json",
    "characters_evidence_cdp_report.json",
    "loot_evidence_cdp_report.json",
    "environment_evidence_cdp_report.json",
    "final_evidence_cdp_report.json",
]


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS {message}")
    else:
        print(f"FAIL {message}")
        failures.append(message)


def is_glb(path: pathlib.Path) -> bool:
    header = path.read_bytes()[:12]
    return header[:4] == b"glTF" and header[4:8] == (2).to_bytes(4, "little")


def check_report(path: pathlib.Path, failures: list[str]) -> None:
    require(path.exists(), f"{path.name} exists", failures)
    if not path.exists():
        return
    data = json.loads(path.read_text())
    blocking = data.get("blockingEvents")
    require(blocking == [], f"{path.name} has no blocking browser/runtime events", failures)
    stats = data.get("imageStats") or {}
    require(stats.get("ok") is True, f"{path.name} includes screenshot imageStats", failures)
    require(stats.get("width", 0) >= 1000 and stats.get("height", 0) >= 600, f"{path.name} screenshot dimensions are credible", failures)
    require(stats.get("litRatio", 0) > 0.08 and stats.get("colorfulRatio", 0) > 0.03 and stats.get("edgeRatio", 0) > 0.01, f"{path.name} screenshot is nonblank with visible variation", failures)
    probe = data.get("probe") or {}
    if path.name.startswith("rifle_"):
        require(probe.get("rifleAsset", {}).get("status") == "loaded", f"{path.name} rifle GLB loaded", failures)
        require(bool(probe.get("viewGun", {}).get("assetSource")), f"{path.name} first-person weapon source present", failures)
        require(bool(probe.get("thirdGun", {}).get("assetSource")), f"{path.name} third-person weapon source present", failures)
    if path.name.startswith("weapons_"):
        weapons = probe.get("weaponAssets") or {}
        require(set(weapons) >= set(WEAPON_ASSETS), f"{path.name} exposes all weapon slots", failures)
        require(all(v.get("status") == "loaded" for v in weapons.values()), f"{path.name} all weapon GLBs loaded", failures)
        require((probe.get("m5WeaponShowcase") or {}).get("count") == 4, f"{path.name} four-weapon showcase visible", failures)
    if path.name.startswith(("characters_", "loot_", "environment_", "final_")):
        final_assets = probe.get("finalAssetKit") or {}
        require(set(final_assets) >= set(FINAL_ASSET_KIT), f"{path.name} exposes complete final asset kit", failures)
        require(all(v.get("status") == "loaded" for v in final_assets.values()), f"{path.name} final asset kit loaded", failures)
        showcase = probe.get("finalEvidenceShowcase") or {}
        require(showcase.get("count", 0) == EXPECTED_SHOWCASE_COUNTS[path.name], f"{path.name} final evidence showcase has expected count", failures)
        require(len(showcase.get("assetSources") or {}) == EXPECTED_SHOWCASE_COUNTS[path.name], f"{path.name} final evidence showcase has expected source set size", failures)


def main() -> int:
    failures: list[str] = []
    require(ROOT.name == "tactical_game_full_realism_final_20260513", "verifier is pointed at final experiment", failures)
    require(INDEX.exists(), "final index.html exists", failures)
    require(SOURCE.exists(), "source 14.html exists for non-mutation check", failures)
    if SOURCE.exists():
        require(sha256(SOURCE) == EXPECTED_SOURCE_SHA256, "source 14.html unchanged from baseline", failures)

    for kind, filename in WEAPON_ASSETS.items():
        path = MODELS / filename
        require(path.exists(), f"weapon GLB exists: {kind}", failures)
        if path.exists():
            require(is_glb(path), f"weapon GLB header is glTF 2.0: {kind}", failures)

    for asset_id, filename in FINAL_ASSET_KIT.items():
        path = MODELS / filename
        preview = MODELS / filename.replace(".glb", "_preview.png")
        require(path.exists(), f"final asset GLB exists: {asset_id}", failures)
        require(preview.exists(), f"final asset preview exists: {asset_id}", failures)
        if path.exists():
            require(is_glb(path), f"final asset GLB header is glTF 2.0: {asset_id}", failures)

    final_report = MODELS / "final_asset_kit_report.json"
    parse_inventory = MODELS / "final_three_glb_parse_inventory.json"
    require(final_report.exists(), "Blender final asset kit report exists", failures)
    require(parse_inventory.exists(), "Three.js GLB parse inventory exists", failures)
    if final_report.exists():
        report = json.loads(final_report.read_text())
        asset_names = {item.get("name") for item in report.get("assets", [])}
        require(len(asset_names) >= len(FINAL_ASSET_KIT), "Blender report covers final asset classes", failures)
        require(all(item.get("mesh_object_count", 0) > 0 for item in report.get("assets", [])), "Blender report includes mesh object counts", failures)
    if parse_inventory.exists():
        inventory = json.loads(parse_inventory.read_text())
        require(len(inventory) >= len(WEAPON_ASSETS) + len(FINAL_ASSET_KIT), "GLB parse inventory covers weapons and final assets", failures)
        require(all(item.get("triangles", 0) > 0 for item in inventory), "GLB parse inventory records triangle counts", failures)
        require(any(item.get("meshes", 0) >= 40 for item in inventory), "character/weapon assets are multi-mesh, not single primitive stand-ins", failures)

    registry_path = ROOT / "assets" / "asset_registry.json"
    matrix_path = ROOT / "assets" / "asset_inventory_matrix.json"
    manifest_path = ROOT / "artifact_hashes.json"
    require(registry_path.exists(), "asset registry exists", failures)
    require(matrix_path.exists(), "asset inventory matrix exists", failures)
    require(manifest_path.exists(), "artifact hash manifest exists", failures)
    if matrix_path.exists():
        matrix = json.loads(matrix_path.read_text())
        rows = matrix.get("acceptance", [])
        classes = {row.get("visible_class") for row in rows}
        require(REQUIRED_MATRIX_CLASSES <= classes, "acceptance matrix covers every goal-visible class", failures)
        required_fields = {"current_state", "target_realism_level", "generation_acquisition_route", "cleanup_route", "integration_file_function", "evidence_files_required", "acceptance_status"}
        require(all(required_fields <= set(row) for row in rows), "acceptance matrix rows include required source-of-truth fields", failures)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        manifest_paths = {item.get("path") for item in manifest.get("artifacts", [])}
        preview_paths = {str(p.relative_to(REPO)) for p in MODELS.glob("*_preview.png")}
        require(preview_paths <= manifest_paths, "artifact hash manifest covers all preview PNGs", failures)

    if INDEX.exists():
        text = INDEX.read_text(encoding="utf-8")
        checks = {
            "weapon GLB registry still covers pistol, shotgun, rifle, DMR": "const weaponAssets" in text and all(filename in text for filename in WEAPON_ASSETS.values()),
            "final asset kit registry is embedded": "const finalAssetKit" in text and all(filename in text for filename in FINAL_ASSET_KIT.values()),
            "manual weapons evidence URL is supported": 'evidenceMode==="m5"||evidenceMode==="weapons"' in text,
            "final assets are loaded at startup": "startRifleAssetLoad" in text and "loadFinalAsset(id)" in text,
            "player and enemy get final character overlays": "function attachFinalCharacterVisual" in text and "finalAssetSource" in text,
            "loot uses final GLB visuals": "function createFinalLootVisual" in text and "finalLootAssetByKind" in text,
            "environment final props are staged": "function addFinalEnvironmentProps" in text and "finalEnvironmentPropsAdded=true" in text,
            "final evidence modes are available": "activateEvidenceFinalMode" in text and all(f'"{mode}"' in text for mode in ["characters", "loot", "environment", "final"]),
            "runtime probe exposes final status": "window.__realismProbe" in text and "finalAssetKit:Object.fromEntries" in text and "finalRuntime" in text,
            "visual-only overlays do not become enemy hitboxes": "visualOnly" in text and "!o.userData.visualOnly" in text,
        }
        for message, ok in checks.items():
            require(ok, message, failures)

    for report_name in EVIDENCE_REPORTS:
        check_report(EVIDENCE / report_name, failures)

    if failures:
        print(f"\n{len(failures)} check(s) failed.")
        return 1
    print("\nAll final full-realism integration checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
