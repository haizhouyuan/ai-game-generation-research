#!/usr/bin/env python3
"""Validate PNG texture dimensions and placeholder-like content.

This is deliberately dependency-free. It supports the PNG files currently used
by the local asset-factory probes and fails closed on unsupported texture files
when they are part of a required production gate.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ASSETS_DIR = Path("experiments/pubg_like_asset_factory_20260513/assets")
TEXTURE_EXTENSIONS = {".png"}
TEXTURE_PATTERNS = {
    "basecolor_or_albedo": re.compile(r"(base[-_ ]?color|basecolor|albedo|diffuse)", re.I),
    "normal": re.compile(r"(normal|nrm)", re.I),
    "roughness": re.compile(r"(roughness|rough)", re.I),
    "metallic": re.compile(r"(metallic|metalness|metal)", re.I),
    "ao": re.compile(r"(^|[-_ .])(ao|ambient[-_ ]?occlusion)([-_ .]|$)", re.I),
}


@dataclass
class PngInfo:
    width: int
    height: int
    bit_depth: int
    color_type: int
    unique_sample_count: int


def map_kind(path: Path) -> str | None:
    for kind, pattern in TEXTURE_PATTERNS.items():
        if pattern.search(path.name):
            return kind
    return None


def paeth_predictor(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def bytes_per_pixel(color_type: int, bit_depth: int) -> int:
    if bit_depth != 8:
        raise ValueError(f"unsupported PNG bit depth: {bit_depth}")
    channels_by_type = {
        0: 1,  # grayscale
        2: 3,  # RGB
        4: 2,  # grayscale + alpha
        6: 4,  # RGBA
    }
    if color_type not in channels_by_type:
        raise ValueError(f"unsupported PNG color type: {color_type}")
    return channels_by_type[color_type]


def inspect_png(path: Path, max_unique_samples: int = 32) -> PngInfo:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG file")

    pos = 8
    width = height = bit_depth = color_type = None
    idat = bytearray()

    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        pos += 12 + length

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk_data[:10])
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or bit_depth is None or color_type is None:
        raise ValueError("PNG missing IHDR")
    if width <= 0 or height <= 0:
        raise ValueError("PNG has invalid dimensions")

    bpp = bytes_per_pixel(color_type, bit_depth)
    row_size = width * bpp
    raw = zlib.decompress(bytes(idat))
    expected_min = (row_size + 1) * height
    if len(raw) < expected_min:
        raise ValueError("PNG decompressed payload shorter than expected")

    unique_samples: set[bytes] = set()
    previous = bytearray(row_size)
    offset = 0
    sample_stride = max(1, width // 32)
    row_stride = max(1, height // 32)

    for y in range(height):
        filter_type = raw[offset]
        offset += 1
        scanline = bytearray(raw[offset : offset + row_size])
        offset += row_size

        for x in range(row_size):
            left = scanline[x - bpp] if x >= bpp else 0
            up = previous[x]
            upper_left = previous[x - bpp] if x >= bpp else 0
            if filter_type == 0:
                recon = scanline[x]
            elif filter_type == 1:
                recon = (scanline[x] + left) & 0xFF
            elif filter_type == 2:
                recon = (scanline[x] + up) & 0xFF
            elif filter_type == 3:
                recon = (scanline[x] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                recon = (scanline[x] + paeth_predictor(left, up, upper_left)) & 0xFF
            else:
                raise ValueError(f"unsupported PNG filter: {filter_type}")
            scanline[x] = recon

        if y % row_stride == 0:
            for px in range(0, width, sample_stride):
                start = px * bpp
                unique_samples.add(bytes(scanline[start : start + bpp]))
                if len(unique_samples) >= max_unique_samples:
                    break
        previous = scanline

    return PngInfo(
        width=width,
        height=height,
        bit_depth=bit_depth,
        color_type=color_type,
        unique_sample_count=len(unique_samples),
    )


def scan_textures(assets_root: Path, min_size: int) -> dict[str, Any]:
    texture_files = [
        path
        for path in sorted(assets_root.rglob("*"))
        if path.is_file()
        and path.suffix.lower() in TEXTURE_EXTENSIONS
        and path.name != ".gitkeep"
        and map_kind(path) is not None
    ]

    textures: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for path in texture_files:
        rel = path.relative_to(assets_root).as_posix()
        kind = map_kind(path)
        try:
            info = inspect_png(path)
            valid = True
            errors: list[str] = []
            if info.width < min_size or info.height < min_size:
                errors.append("below_min_resolution")
            if info.unique_sample_count <= 1:
                errors.append("solid_or_placeholder_like")
            if errors:
                valid = False
            row = {
                "path": rel,
                "kind": kind,
                "valid_png": True,
                "width": info.width,
                "height": info.height,
                "bit_depth": info.bit_depth,
                "color_type": info.color_type,
                "unique_sample_count": info.unique_sample_count,
                "quality_pass": valid,
                "errors": errors,
            }
        except Exception as exc:  # noqa: BLE001 - validation report should capture parse failures.
            row = {
                "path": rel,
                "kind": kind,
                "valid_png": False,
                "quality_pass": False,
                "errors": [str(exc)],
            }
        textures.append(row)
        if not row["quality_pass"]:
            failures.append(row)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets_root": assets_root.as_posix(),
        "min_size": min_size,
        "texture_count": len(textures),
        "failure_count": len(failures),
        "valid": not failures,
        "textures": textures,
        "failures": failures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate PNG texture dimensions and placeholder-like content."
    )
    parser.add_argument(
        "assets_root",
        nargs="?",
        type=Path,
        default=DEFAULT_ASSETS_DIR,
        help=f"Asset root. Defaults to {DEFAULT_ASSETS_DIR}",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=512,
        help="Minimum accepted width and height for texture maps.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Exit zero when no texture files are found.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = scan_textures(args.assets_root, args.min_size)
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    if report["texture_count"] == 0 and not args.allow_empty:
        return 2
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
