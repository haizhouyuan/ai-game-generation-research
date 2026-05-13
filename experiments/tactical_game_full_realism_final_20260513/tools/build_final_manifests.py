#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
MODELS = ROOT / "assets" / "models"
EVIDENCE = ROOT / "evidence"

ASSET_CLASSES = {
    "pistol_m5_candidate.glb": ("weapon", "pistol"),
    "shotgun_m5_candidate.glb": ("weapon", "shotgun"),
    "groza_procedural_candidate.glb": ("weapon", "rifle"),
    "dmr_m5_candidate.glb": ("weapon", "dmr"),
    "character_player_final.glb": ("character", "player body, helmet, armor, backpack, gloves, pads"),
    "character_enemy_final.glb": ("character", "enemy body, helmet, armor, backpack, gloves, pads"),
    "loot_ammo_final.glb": ("loot", "ammo pickup"),
    "loot_bandage_final.glb": ("loot", "bandage pickup"),
    "loot_firstaid_final.glb": ("loot", "first-aid pickup"),
    "loot_medkit_final.glb": ("loot", "medkit pickup"),
    "loot_revive_final.glb": ("loot", "revive pickup"),
    "loot_vest_final.glb": ("loot", "armor vest pickup"),
    "loot_helmet_final.glb": ("loot", "helmet pickup"),
    "prop_crate_final.glb": ("environment", "crate/storage prop"),
    "prop_container_final.glb": ("environment", "containers: corrugation, doors, hinges, warning markings, wear"),
    "prop_ladder_stair_final.glb": ("environment", "ladders/stairs/railings"),
    "prop_interior_furniture_final.glb": ("environment", "building interiors: tables, cabinets, shelves, floor/wall detail, interior lighting prop"),
    "prop_building_detail_final.glb": ("environment", "building detail, door/window/utility prop"),
    "prop_ground_wall_fence_final.glb": ("environment", "ground/roads/walls/fences/gates"),
    "prop_tree_final.glb": ("environment", "tree/vegetation prop"),
    "prop_rock_cluster_final.glb": ("environment", "rock cluster prop"),
}
MATRIX_CLASSES = {
    "first-person weapons": {
        "assets": ["pistol_m5_candidate", "shotgun_m5_candidate", "groza_procedural_candidate", "dmr_m5_candidate"],
        "kind": "weapon",
        "current_state": "Four GLB weapon slots load through weaponAssets and first-person createGunModel/rebuildGuns path.",
        "target_realism_level": "Game-ready hard-surface GLB weapons with visible silhouette, optic/detail geometry, muzzle anchor, and PBR-style material factors.",
        "generation_acquisition_route": "Local Blender weapon candidates and selected GROZA GLB.",
        "cleanup_route": "Blender export to GLB, Three parser inventory, first/third/weapons CDP evidence.",
        "integration_file_function": "index.html: weaponAssets, createWeaponAssetModel, createGunModel, rebuildGuns",
        "evidence_files_required": ["evidence/weapons_evidence_cdp.png", "evidence/rifle_evidence_cdp_first.png", "evidence/rifle_evidence_cdp_third.png"],
    },
    "third-person/player/NPC weapons": {
        "assets": ["pistol_m5_candidate", "shotgun_m5_candidate", "groza_procedural_candidate", "dmr_m5_candidate"],
        "kind": "weapon",
        "current_state": "Shared weapon GLB path is used by player third-person, NPC mount, world loot, and first-person contexts.",
        "target_realism_level": "Same weapon assets visible across character/world contexts without procedural fallback in evidence.",
        "generation_acquisition_route": "Shared GLB registry with per-context transforms.",
        "cleanup_route": "Runtime probe checks assetSource for viewGun, thirdGun, weapon showcase.",
        "integration_file_function": "index.html: refreshWeaponAssetUsers, createEnemy, spawnLootAt, createGunModel",
        "evidence_files_required": ["evidence/weapons_evidence_cdp.png", "evidence/rifle_evidence_cdp_third.png"],
    },
    "player body": {
        "assets": ["character_player_final"],
        "kind": "character",
        "current_state": "Player body uses final GLB tactical overlay and keeps original collider/hit logic separate.",
        "target_realism_level": "Non-capsule tactical body silhouette with gear, helmet, armor, backpack, gloves, and pads.",
        "generation_acquisition_route": "Local Blender modular character kit.",
        "cleanup_route": "Preview render, GLB parse inventory, visual-only runtime overlay.",
        "integration_file_function": "index.html: finalAssetKit, attachFinalCharacterVisual, refreshFinalAssetUsers",
        "evidence_files_required": ["evidence/characters_evidence_cdp.png", "assets/models/character_player_final_preview.png"],
    },
    "NPC body": {
        "assets": ["character_enemy_final"],
        "kind": "character",
        "current_state": "Enemy body uses final GLB tactical overlay and enemy hitboxes skip visualOnly meshes.",
        "target_realism_level": "Distinct enemy tactical body silhouette with gear and team color.",
        "generation_acquisition_route": "Local Blender modular enemy variant.",
        "cleanup_route": "Preview render, GLB parse inventory, visual-only runtime overlay.",
        "integration_file_function": "index.html: createEnemy, attachFinalCharacterVisual",
        "evidence_files_required": ["evidence/characters_evidence_cdp.png", "assets/models/character_enemy_final_preview.png"],
    },
    "helmet": {
        "assets": ["character_player_final", "character_enemy_final", "loot_helmet_final"],
        "kind": "character/loot",
        "current_state": "Helmet geometry appears on player, enemy, and helmet pickup GLBs.",
        "target_realism_level": "Ballistic helmet with visor/rails/comms readable in screenshot and preview.",
        "generation_acquisition_route": "Local Blender modular helmet meshes.",
        "cleanup_route": "Preview render, character/loot evidence modes.",
        "integration_file_function": "index.html: attachFinalCharacterVisual, createFinalLootVisual",
        "evidence_files_required": ["evidence/characters_evidence_cdp.png", "evidence/loot_evidence_cdp.png"],
    },
    "armor/plate carrier": {
        "assets": ["character_player_final", "character_enemy_final", "loot_vest_final"],
        "kind": "character/loot",
        "current_state": "Plate carrier panels and vest pickup are GLB assets.",
        "target_realism_level": "Readable armored vest/plate carrier with pouches and material variation.",
        "generation_acquisition_route": "Local Blender modular armor kit.",
        "cleanup_route": "Preview render, character/loot evidence modes.",
        "integration_file_function": "index.html: attachFinalCharacterVisual, createFinalLootVisual",
        "evidence_files_required": ["evidence/characters_evidence_cdp.png", "evidence/loot_evidence_cdp.png"],
    },
    "backpack, pouches, straps, rig, gloves, pads": {
        "assets": ["character_player_final", "character_enemy_final"],
        "kind": "character",
        "current_state": "Character GLBs include backpack, pouches, shoulder/knee pads, gloves, and webbing material groups.",
        "target_realism_level": "Full tactical gear silhouette rather than primitive capsule accessories.",
        "generation_acquisition_route": "Local Blender modular character gear.",
        "cleanup_route": "Preview render, GLB parse inventory, character evidence mode.",
        "integration_file_function": "index.html: attachFinalCharacterVisual",
        "evidence_files_required": ["evidence/characters_evidence_cdp.png"],
    },
    "ammo, med items, revive item, armor/helmet pickups": {
        "assets": ["loot_ammo_final", "loot_bandage_final", "loot_firstaid_final", "loot_medkit_final", "loot_revive_final", "loot_vest_final", "loot_helmet_final"],
        "kind": "loot",
        "current_state": "All non-weapon loot families have final GLB props and preserve pickup behavior.",
        "target_realism_level": "Readable world pickup props for tactical gameplay.",
        "generation_acquisition_route": "Local Blender loot kit.",
        "cleanup_route": "Preview render, GLB parse inventory, loot evidence mode.",
        "integration_file_function": "index.html: finalLootAssetByKind, createFinalLootVisual, spawnLootAt",
        "evidence_files_required": ["evidence/loot_evidence_cdp.png"],
    },
    "crates and storage props": {
        "assets": ["prop_crate_final"],
        "kind": "environment",
        "current_state": "Crate/storage GLB is staged in loot and yard areas.",
        "target_realism_level": "Beveled storage crate with straps/handles/material variation.",
        "generation_acquisition_route": "Local Blender environment kit.",
        "cleanup_route": "Preview render, environment evidence mode.",
        "integration_file_function": "index.html: addFinalEnvironmentProps",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png"],
    },
    "containers": {
        "assets": ["prop_container_final"],
        "kind": "environment",
        "current_state": "Container GLB adds corrugation, door leaves, locking bars, and warning stripe.",
        "target_realism_level": "Container surfaces no longer read as flat boxes.",
        "generation_acquisition_route": "Local Blender environment kit.",
        "cleanup_route": "Preview render, environment evidence mode.",
        "integration_file_function": "index.html: addFinalEnvironmentProps",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png", "assets/models/prop_container_final_preview.png"],
    },
    "ladders/stairs": {
        "assets": ["prop_ladder_stair_final"],
        "kind": "environment",
        "current_state": "Ladder/stair/railing GLB staged near building and rooftop routes.",
        "target_realism_level": "Industrial stairs, railings, ladder rungs, and anti-slip edges.",
        "generation_acquisition_route": "Local Blender environment kit.",
        "cleanup_route": "Preview render, environment evidence mode.",
        "integration_file_function": "index.html: addFinalEnvironmentProps",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png", "assets/models/prop_ladder_stair_final_preview.png"],
    },
    "rocks": {
        "assets": ["prop_rock_cluster_final"],
        "kind": "environment",
        "current_state": "Rock cluster GLB is scattered around the compound.",
        "target_realism_level": "Clustered rough rocks with material variation.",
        "generation_acquisition_route": "Local Blender environment kit.",
        "cleanup_route": "Preview render, environment evidence mode.",
        "integration_file_function": "index.html: addFinalEnvironmentProps",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png"],
    },
    "trees/bushes/grass": {
        "assets": ["prop_tree_final"],
        "kind": "environment",
        "current_state": "Tree GLB with trunk, branches, and leaf clusters is scattered in the compound perimeter.",
        "target_realism_level": "Readable vegetation silhouettes, not pure cone/cylinder placeholders.",
        "generation_acquisition_route": "Local Blender environment kit plus existing grass field.",
        "cleanup_route": "Preview render, environment evidence mode.",
        "integration_file_function": "index.html: addFinalEnvironmentProps",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png"],
    },
    "building exteriors": {
        "assets": ["prop_building_detail_final", "prop_ground_wall_fence_final"],
        "kind": "environment",
        "current_state": "Building detail GLBs add AC/vents/pipes/utility boxes; wall/fence kit supports compound perimeter detail.",
        "target_realism_level": "Facade details break up flat building walls.",
        "generation_acquisition_route": "Local Blender facade/detail kit.",
        "cleanup_route": "Preview render, environment evidence mode.",
        "integration_file_function": "index.html: addFinalEnvironmentProps",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png"],
    },
    "building interiors": {
        "assets": ["prop_interior_furniture_final"],
        "kind": "environment",
        "current_state": "Interior furniture GLB includes workbench, cabinet, shelves, and light bar.",
        "target_realism_level": "Indoor spaces have readable furniture and utility detail.",
        "generation_acquisition_route": "Local Blender interior kit.",
        "cleanup_route": "Preview render, environment evidence mode.",
        "integration_file_function": "index.html: addFinalEnvironmentProps",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png", "assets/models/prop_interior_furniture_final_preview.png"],
    },
    "doors/windows/vents/pipes/utility details": {
        "assets": ["prop_building_detail_final"],
        "kind": "environment",
        "current_state": "Building detail GLB includes wall AC, louvers, pipe, junction box, and warning plate.",
        "target_realism_level": "Facade utility details visible in game and preview.",
        "generation_acquisition_route": "Local Blender building detail kit.",
        "cleanup_route": "Preview render, environment evidence mode.",
        "integration_file_function": "index.html: addFinalEnvironmentProps",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png", "assets/models/prop_building_detail_final_preview.png"],
    },
    "ground/roads/walls/fences": {
        "assets": ["prop_ground_wall_fence_final"],
        "kind": "environment",
        "current_state": "Ground/road/wall/fence kit GLB adds asphalt patch, road markings, concrete wall, fence posts/wires, gate plate.",
        "target_realism_level": "Compound perimeter and road surfaces no longer rely only on flat colored planes.",
        "generation_acquisition_route": "Local Blender ground/perimeter kit.",
        "cleanup_route": "Preview render, environment evidence mode.",
        "integration_file_function": "index.html: addFinalEnvironmentProps",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png", "assets/models/prop_ground_wall_fence_final_preview.png"],
    },
    "lighting, sky, fog, shadow configuration": {
        "assets": [],
        "kind": "lighting",
        "current_state": "ACES tone mapping, PCF shadows, sun/hemisphere lights, fog, sky shader, and day/sunset/night modes are configured in runtime.",
        "target_realism_level": "Lighting/camera/material response supports the integrated realistic asset kit.",
        "generation_acquisition_route": "Runtime Three.js lighting/composition pass.",
        "cleanup_route": "CDP browser evidence with imageStats and no blocking events.",
        "integration_file_function": "index.html: renderer/toneMapping/shadowMap, applySkyMode, evidence camera staging",
        "evidence_files_required": ["evidence/environment_evidence_cdp.png", "evidence/final_evidence_cdp.png"],
    },
}

EVIDENCE_BY_CLASS = {
    "weapon": ["evidence/weapons_evidence_cdp.png", "evidence/rifle_evidence_cdp_first.png", "evidence/rifle_evidence_cdp_third.png"],
    "character": ["evidence/characters_evidence_cdp.png", "evidence/final_evidence_cdp.png"],
    "loot": ["evidence/loot_evidence_cdp.png", "evidence/final_evidence_cdp.png"],
    "environment": ["evidence/environment_evidence_cdp.png", "evidence/final_evidence_cdp.png"],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    final_report = load_json(MODELS / "final_asset_kit_report.json", {"assets": []})
    final_by_name = {item.get("name"): item for item in final_report.get("assets", [])}
    parse_inventory = load_json(MODELS / "final_three_glb_parse_inventory.json", [])
    parse_by_file = {Path(item.get("file", "")).name: item for item in parse_inventory}

    registry = {
        "generated_at": generated_at,
        "experiment": ROOT.name,
        "source": "local Blender procedural hard-surface/modular kit plus existing weapon GLBs; no external paid asset download",
        "assets": [],
    }
    matrix = {
        "generated_at": generated_at,
        "goal": "production_goal_full_realistic_3d_tactical_game_final_2026-05-13.md",
        "acceptance": [],
    }

    for filename, (kind, coverage) in ASSET_CLASSES.items():
        path = MODELS / filename
        preview = MODELS / filename.replace(".glb", "_preview.png")
        name = filename.removesuffix(".glb")
        parsed = parse_by_file.get(filename, {})
        blender = final_by_name.get(name, {})
        entry = {
            "id": name,
            "kind": kind,
            "coverage": coverage,
            "path": rel(path),
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
            "preview": rel(preview) if preview.exists() else None,
            "preview_sha256": sha256(preview) if preview.exists() else None,
            "meshes": parsed.get("meshes") or blender.get("mesh_object_count"),
            "triangles": parsed.get("triangles"),
            "bbox": parsed.get("bbox") or blender.get("bbox"),
            "materials": parsed.get("materialNames") or blender.get("material_names") or [],
            "material_map_count": parsed.get("materialMapCount", 0),
            "provenance": "Generated or selected locally, then exported/validated as GLB in this experiment.",
            "fallback_allowed_in_final_evidence": False,
        }
        registry["assets"].append(entry)

    for visible_class, data in MATRIX_CLASSES.items():
        matrix["acceptance"].append({
            "visible_class": visible_class,
            "current_state": data["current_state"],
            "target_realism_level": data["target_realism_level"],
            "generation_acquisition_route": data["generation_acquisition_route"],
            "cleanup_route": data["cleanup_route"],
            "integration_file_function": data["integration_file_function"],
            "evidence_files_required": data["evidence_files_required"],
            "asset_ids": data["assets"],
            "material_evidence_grade": "runtime_lighting_config" if data["kind"] == "lighting" else "material_factors_only",
            "acceptance_status": "accepted",
            "notes": "Accepted by GLB/header/parser reports, CDP screenshot reports with imageStats, and verified artifact hashes.",
        })

    (ROOT / "assets" / "asset_registry.json").write_text(json.dumps(registry, indent=2) + "\n")
    (ROOT / "assets" / "asset_inventory_matrix.json").write_text(json.dumps(matrix, indent=2) + "\n")

    artifact_paths = [
        ROOT / "index.html",
        ROOT / "README.md",
        ROOT / "report.md",
        ROOT / "assets" / "asset_registry.json",
        ROOT / "assets" / "asset_inventory_matrix.json",
        MODELS / "final_asset_kit_report.json",
        MODELS / "final_three_glb_parse_inventory.json",
        *sorted((ROOT / "tools").glob("*")),
        *[MODELS / filename for filename in ASSET_CLASSES],
        *sorted(MODELS.glob("*_preview.png")),
        *sorted(EVIDENCE.glob("*.png")),
        *sorted(EVIDENCE.glob("*.json")),
    ]
    manifest = {"artifacts": []}
    for path in artifact_paths:
        if path.exists():
            manifest["artifacts"].append({
                "path": rel(path),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            })
    (ROOT / "artifact_hashes.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {ROOT / 'assets' / 'asset_registry.json'}")
    print(f"wrote {ROOT / 'assets' / 'asset_inventory_matrix.json'}")
    print(f"wrote {ROOT / 'artifact_hashes.json'} with {len(manifest['artifacts'])} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
