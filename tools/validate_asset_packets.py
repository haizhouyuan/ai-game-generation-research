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
    return path.is_file() and path.suffix.lower() in extensions


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

    return {
        "asset_id": packet_dir.name,
        "path": packet_dir.relative_to(assets_root).as_posix(),
        "required_directories": dirs,
        "missing_required_directories": missing_dirs,
        "required_directories_present": not missing_dirs,
        "texture_maps": texture_counts,
        "texture_map_total": sum(texture_counts.values()),
        "evidence_media_count": count_evidence_media(packet_dir / "evidence"),
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

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets_root": assets_root.as_posix(),
        "assets_root_exists": root_exists,
        "required_directories": list(REQUIRED_DIRS),
        "texture_map_keys": list(TEXTURE_PATTERNS),
        "packet_count": len(packets),
        "packets_missing_required_directories": packets_missing_required_dirs,
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

    return "\n".join(lines) + "\n"


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
