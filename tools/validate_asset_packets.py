#!/usr/bin/env python3
"""Inventory asset packet directory readiness for the PUBG-like asset factory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_ASSETS_DIR = Path("experiments/pubg_like_asset_factory_20260513/assets")
REQUIRED_DIRS = ("source", "model", "textures", "reports", "evidence")
MINIMUM_PRODUCTION_ASSET_IDS = (
    "hero_rifle_v1",
    "sidearm_v1",
    "secondary_weapon_v1",
    "player_tactical_v1",
    "enemy_tactical_v1",
    "gear_set_v1",
    "wet_asphalt_material_v1",
    "concrete_wall_material_v1",
    "container_checkpoint_v1",
    "loot_set_v1",
    "clutter_decals_v1",
    "rainy_checkpoint_scene_v1",
)
MODEL_EXTENSIONS = {".fbx", ".glb", ".gltf", ".obj", ".ply", ".stl", ".usd", ".usdz"}
SOURCE_EXTENSIONS = {".csv", ".json", ".md", ".png", ".jpg", ".jpeg", ".webp", ".txt"}
REPORT_EXTENSIONS = {".csv", ".json", ".log", ".md", ".txt"}
TEXTURE_EXTENSIONS = {
    ".bmp",
    ".exr",
    ".hdr",
    ".jpeg",
    ".jpg",
    ".ktx2",
    ".png",
    ".tga",
    ".tif",
    ".tiff",
    ".webp",
}
EVIDENCE_MEDIA_EXTENSIONS = {
    ".avi",
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".png",
    ".tif",
    ".tiff",
    ".webm",
    ".webp",
}
TEXTURE_PATTERNS = {
    "basecolor_or_albedo": re.compile(r"(base[-_ ]?color|basecolor|albedo|diffuse)", re.I),
    "normal": re.compile(r"(normal|nrm)", re.I),
    "roughness": re.compile(r"(roughness|rough)", re.I),
    "metallic": re.compile(r"(metallic|metalness|metal)", re.I),
    "ao": re.compile(r"(^|[-_ .])(ao|ambient[-_ ]?occlusion)([-_ .]|$)", re.I),
}


def is_countable_file(path: Path, extensions: set[str]) -> bool:
    return path.is_file() and path.name != ".gitkeep" and path.suffix.lower() in extensions


def count_files(root: Path, extensions: set[str]) -> int:
    if not root.is_dir():
        return 0
    return sum(1 for path in root.rglob("*") if is_countable_file(path, extensions))


def count_texture_maps(textures_dir: Path) -> dict[str, int]:
    counts = {name: 0 for name in TEXTURE_PATTERNS}
    if not textures_dir.is_dir():
        return counts

    for path in sorted(textures_dir.iterdir()):
        if not is_countable_file(path, TEXTURE_EXTENSIONS):
            continue
        for map_name, pattern in TEXTURE_PATTERNS.items():
            if pattern.search(path.name):
                counts[map_name] += 1
    return counts


def count_evidence_media(evidence_dir: Path) -> int:
    if not evidence_dir.is_dir():
        return 0
    return sum(
        1
        for path in evidence_dir.rglob("*")
        if is_countable_file(path, EVIDENCE_MEDIA_EXTENSIONS)
    )


def scan_packet(packet_dir: Path, assets_root: Path) -> dict[str, object]:
    dirs = {name: (packet_dir / name).is_dir() for name in REQUIRED_DIRS}
    missing_dirs = [name for name, exists in dirs.items() if not exists]
    texture_counts = count_texture_maps(packet_dir / "textures")
    pbr_complete = (
        texture_counts["basecolor_or_albedo"] > 0
        and texture_counts["normal"] > 0
        and texture_counts["roughness"] > 0
        and (texture_counts["metallic"] > 0 or texture_counts["ao"] > 0)
    )
    source_file_count = count_files(packet_dir / "source", SOURCE_EXTENSIONS)
    model_file_count = count_files(packet_dir / "model", MODEL_EXTENSIONS)
    report_file_count = count_files(packet_dir / "reports", REPORT_EXTENSIONS)
    evidence_media_count = count_evidence_media(packet_dir / "evidence")
    non_empty_packet = any(
        (
            source_file_count,
            model_file_count,
            sum(texture_counts.values()),
            report_file_count,
            evidence_media_count,
        )
    )

    return {
        "asset_id": packet_dir.name,
        "path": packet_dir.relative_to(assets_root).as_posix(),
        "required_directories": dirs,
        "missing_required_directories": missing_dirs,
        "required_directories_present": not missing_dirs,
        "source_file_count": source_file_count,
        "model_file_count": model_file_count,
        "texture_maps": texture_counts,
        "texture_map_total": sum(texture_counts.values()),
        "pbr_texture_set_complete": pbr_complete,
        "report_file_count": report_file_count,
        "evidence_media_count": evidence_media_count,
        "non_empty_packet": non_empty_packet,
    }


def scan_assets(assets_root: Path) -> dict[str, object]:
    root_exists = assets_root.is_dir()
    packet_dirs = []
    if root_exists:
        packet_dirs = [
            path
            for path in sorted(assets_root.iterdir())
            if path.is_dir() and not path.name.startswith(".")
        ]

    packets = [scan_packet(packet_dir, assets_root) for packet_dir in packet_dirs]
    packets_missing_required_dirs = [
        packet["asset_id"]
        for packet in packets
        if packet["missing_required_directories"]
    ]
    packet_ids = {str(packet["asset_id"]) for packet in packets}
    minimum_missing = [
        asset_id for asset_id in MINIMUM_PRODUCTION_ASSET_IDS if asset_id not in packet_ids
    ]
    minimum_packets = [
        packet for packet in packets if str(packet["asset_id"]) in MINIMUM_PRODUCTION_ASSET_IDS
    ]
    minimum_empty_packets = [
        packet["asset_id"] for packet in minimum_packets if not packet["non_empty_packet"]
    ]
    minimum_missing_route_reports = [
        packet["asset_id"] for packet in minimum_packets if int(packet["report_file_count"]) == 0
    ]
    minimum_missing_runtime_status = [
        packet["asset_id"]
        for packet in minimum_packets
        if int(packet["evidence_media_count"]) == 0
    ]
    pbr_texture_packet_count = sum(1 for packet in packets if packet["pbr_texture_set_complete"])
    evidence_packet_count = sum(1 for packet in packets if int(packet["evidence_media_count"]) > 0)
    generated_or_pbr_packet_count = sum(
        1
        for packet in minimum_packets
        if int(packet["model_file_count"]) > 0 or packet["pbr_texture_set_complete"]
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets_root": assets_root.as_posix(),
        "assets_root_exists": root_exists,
        "required_directories": list(REQUIRED_DIRS),
        "minimum_production_asset_ids": list(MINIMUM_PRODUCTION_ASSET_IDS),
        "texture_map_keys": list(TEXTURE_PATTERNS),
        "packet_count": len(packets),
        "packets_missing_required_directories": packets_missing_required_dirs,
        "production_goal_summary": {
            "minimum_missing_asset_ids": minimum_missing,
            "minimum_empty_packets": minimum_empty_packets,
            "minimum_missing_route_reports": minimum_missing_route_reports,
            "minimum_missing_runtime_evidence": minimum_missing_runtime_status,
            "generated_or_pbr_minimum_packet_count": generated_or_pbr_packet_count,
            "pbr_texture_packet_count": pbr_texture_packet_count,
            "evidence_packet_count": evidence_packet_count,
            "required_minimum_packet_count": len(MINIMUM_PRODUCTION_ASSET_IDS),
            "required_generated_or_pbr_minimum_packet_count": len(MINIMUM_PRODUCTION_ASSET_IDS),
            "required_pbr_texture_packet_count": 8,
            "required_evidence_packet_count": len(MINIMUM_PRODUCTION_ASSET_IDS),
        },
        "packets": packets,
    }


def markdown_bool(value: bool) -> str:
    return "yes" if value else "no"


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def emit_markdown(report: dict[str, object]) -> str:
    packets = report["packets"]
    lines = [
        f"# Asset Packet Validation - {markdown_escape(report['assets_root'])}",
        "",
        f"Packets scanned: {report['packet_count']}",
        "",
        "| Asset | Source | Model | Textures | Reports | Evidence | Basecolor/Albedo | Normal | Roughness | Metallic | AO | Evidence Media | Missing |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for packet in packets:
        dirs = packet["required_directories"]
        maps = packet["texture_maps"]
        missing = packet["missing_required_directories"]
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape(packet["asset_id"]),
                    markdown_bool(dirs["source"]),
                    markdown_bool(dirs["model"]),
                    markdown_bool(dirs["textures"]),
                    markdown_bool(dirs["reports"]),
                    markdown_bool(dirs["evidence"]),
                    str(maps["basecolor_or_albedo"]),
                    str(maps["normal"]),
                    str(maps["roughness"]),
                    str(maps["metallic"]),
                    str(maps["ao"]),
                    str(packet["evidence_media_count"]),
                    markdown_escape(", ".join(missing) if missing else ""),
                ]
            )
            + " |"
        )

    if not packets:
        lines.append("| _(none)_ | no | no | no | no | no | 0 | 0 | 0 | 0 | 0 | 0 | no packet directories found |")

    summary = report["production_goal_summary"]
    lines.extend(
        [
            "",
            "## Production Goal Summary",
            "",
            f"- Missing minimum asset packets: {markdown_escape(', '.join(summary['minimum_missing_asset_ids']) or 'none')}",
            f"- Empty minimum packets: {markdown_escape(', '.join(summary['minimum_empty_packets']) or 'none')}",
            f"- Minimum packets missing route reports: {markdown_escape(', '.join(summary['minimum_missing_route_reports']) or 'none')}",
            f"- Minimum packets missing runtime evidence: {markdown_escape(', '.join(summary['minimum_missing_runtime_evidence']) or 'none')}",
            f"- Generated/PBR minimum packets: {summary['generated_or_pbr_minimum_packet_count']} / {summary['required_generated_or_pbr_minimum_packet_count']}",
            f"- PBR texture packets: {summary['pbr_texture_packet_count']} / {summary['required_pbr_texture_packet_count']}",
            f"- Evidence packets: {summary['evidence_packet_count']} / {summary['required_evidence_packet_count']}",
        ]
    )

    return "\n".join(lines) + "\n"


def production_goal_failures(report: dict[str, object]) -> list[str]:
    summary = report["production_goal_summary"]
    failures: list[str] = []
    if summary["minimum_missing_asset_ids"]:
        failures.append("missing minimum production asset packets")
    if summary["minimum_empty_packets"]:
        failures.append("minimum production packets are still empty scaffolds")
    if summary["minimum_missing_route_reports"]:
        failures.append("minimum production packets are missing route reports")
    if summary["minimum_missing_runtime_evidence"]:
        failures.append("minimum production packets are missing runtime evidence")
    if (
        int(summary["generated_or_pbr_minimum_packet_count"])
        < int(summary["required_generated_or_pbr_minimum_packet_count"])
    ):
        failures.append("not enough minimum packets have generated models or PBR texture outputs")
    if int(summary["pbr_texture_packet_count"]) < int(summary["required_pbr_texture_packet_count"]):
        failures.append("not enough packets have complete PBR texture sets")
    if int(summary["evidence_packet_count"]) < int(summary["required_evidence_packet_count"]):
        failures.append("not enough packets have evidence media")
    return failures


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan local asset packet directories for required folders, texture maps, and evidence media."
    )
    parser.add_argument(
        "assets_root",
        nargs="?",
        default=DEFAULT_ASSETS_DIR,
        type=Path,
        help=f"Asset packet root to scan. Defaults to {DEFAULT_ASSETS_DIR}",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Emit a markdown table instead of JSON.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero if any scanned packet is missing a required directory.",
    )
    parser.add_argument(
        "--production-goal",
        action="store_true",
        help="Exit nonzero unless the full PUBG-like rebuild packet thresholds are met.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = scan_assets(args.assets_root)

    if args.markdown:
        sys.stdout.write(emit_markdown(report))
    else:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")

    if args.strict and report["packets_missing_required_directories"]:
        return 1
    if args.production_goal and production_goal_failures(report):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
