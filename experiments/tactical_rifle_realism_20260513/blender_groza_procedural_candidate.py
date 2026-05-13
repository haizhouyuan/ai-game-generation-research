#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args(argv: list[str] | None = None) -> tuple[Path, str]:
    if argv is None:
        if "--" not in sys.argv:
            raise SystemExit(
                "usage: blender --background --python "
                "blender_groza_procedural_candidate.py -- OUT_DIR"
            )
        argv = sys.argv[sys.argv.index("--") + 1 :]
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--output-name", default="groza_procedural_candidate.glb")
    args = parser.parse_args(argv)
    if Path(args.output_name).name != args.output_name or not args.output_name.endswith(".glb"):
        raise SystemExit("--output-name must be a bare .glb filename")
    return args.out_dir.resolve(), args.output_name


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_mat(name: str, color: tuple[float, float, float, float], roughness: float, metalness: float):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metalness
    return mat


def cube(
    name: str,
    dims: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat,
    bevel: float = 0.025,
    rot: tuple[float, float, float] = (0, 0, 0),
):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        bevel_mod = obj.modifiers.new("small_bevels", "BEVEL")
        bevel_mod.width = bevel
        bevel_mod.segments = 4
        bevel_mod.affect = "EDGES"
    obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return obj


def cyl_x(
    name: str,
    radius: float,
    length: float,
    loc: tuple[float, float, float],
    mat,
    vertices: int = 48,
):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=length,
        location=loc,
        rotation=(0, math.pi / 2, 0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return obj


def add_anchor(name: str, loc: tuple[float, float, float]):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.12
    empty.location = loc
    bpy.context.collection.objects.link(empty)
    return empty


def create_groza_candidate() -> list[bpy.types.Object]:
    mats = {
        "blackened_steel": make_mat("blackened_steel", (0.025, 0.027, 0.03, 1), 0.34, 0.85),
        "worn_blued_steel": make_mat("worn_blued_steel", (0.13, 0.145, 0.16, 1), 0.29, 0.9),
        "rubber": make_mat("matte_rubber", (0.018, 0.018, 0.017, 1), 0.78, 0.0),
        "wood": make_mat("oiled_dark_wood", (0.42, 0.22, 0.095, 1), 0.48, 0.0),
        "edge_wear": make_mat("bright_edge_wear", (0.78, 0.72, 0.62, 1), 0.23, 1.0),
        "brass": make_mat("brass_markings", (0.95, 0.62, 0.19, 1), 0.28, 1.0),
        "proxy": make_mat("transparent_collider_proxy", (0.1, 0.55, 0.95, 0.18), 0.5, 0.0),
    }
    mats["proxy"].blend_method = "BLEND"

    parts: list[bpy.types.Object] = []

    # Coordinates follow the local HTML viewer: muzzle points toward +X.
    parts.append(cube("receiver_main", (2.35, 0.52, 0.46), (-0.05, 0.04, 0), mats["worn_blued_steel"], 0.055))
    parts.append(cube("front_handguard", (1.45, 0.32, 0.42), (0.98, 0.0, 0), mats["worn_blued_steel"], 0.045))
    parts.append(cube("rear_stock_body", (0.82, 0.34, 0.44), (-1.45, 0.03, 0), mats["blackened_steel"], 0.05))
    parts.append(cube("rubber_butt_pad", (0.18, 0.54, 0.48), (-1.88, 0.02, 0), mats["rubber"], 0.025))
    parts.append(cube("top_cover", (1.28, 0.18, 0.44), (-0.55, 0.46, 0), mats["blackened_steel"], 0.04))
    parts.append(cube("carry_handle_bridge", (1.02, 0.16, 0.38), (-0.53, 0.70, 0), mats["worn_blued_steel"], 0.035))
    parts.append(cube("carry_handle_rear_post", (0.16, 0.42, 0.36), (-1.08, 0.57, 0), mats["worn_blued_steel"], 0.025))
    parts.append(cube("carry_handle_front_post", (0.16, 0.36, 0.36), (-0.05, 0.55, 0), mats["worn_blued_steel"], 0.025))
    parts.append(cube("wood_handguard_insert", (0.78, 0.26, 0.50), (-0.56, 0.32, 0), mats["wood"], 0.045))
    parts.append(cube("wood_pistol_grip", (0.32, 0.72, 0.34), (-0.42, -0.76, 0), mats["wood"], 0.055, (0.18, 0, 0)))
    parts.append(cube("trigger_guard", (0.18, 0.38, 0.34), (-0.26, -0.34, 0), mats["blackened_steel"], 0.035))
    parts.append(cube("front_vertical_grip", (0.22, 0.70, 0.32), (-1.34, -0.72, 0), mats["rubber"], 0.05))
    parts.append(cube("front_grip_crossbar", (0.62, 0.18, 0.34), (-1.44, -0.31, 0), mats["blackened_steel"], 0.035))
    parts.append(cyl_x("barrel", 0.08, 1.08, (1.68, 0.08, 0), mats["blackened_steel"], 64))
    parts.append(cyl_x("muzzle_brake", 0.105, 0.34, (2.33, 0.08, 0), mats["edge_wear"], 64))
    parts.append(cube("front_sight_block", (0.14, 0.56, 0.52), (2.56, 0.06, 0), mats["edge_wear"], 0.02))
    parts.append(cube("front_sight_post", (0.14, 0.12, 0.44), (2.60, 0.40, 0), mats["blackened_steel"], 0.015))
    parts.append(cube("rear_sight_rail", (0.52, 0.08, 0.42), (0.18, 0.39, 0), mats["edge_wear"], 0.018))

    for i in range(10):
        parts.append(
            cube(
                f"top_rail_tooth_{i:02d}",
                (0.10, 0.030, 0.50),
                (-0.92 + i * 0.20, 0.38, 0),
                mats["blackened_steel"],
                0.006,
            )
        )

    for i in range(12):
        t = i / 11
        x = math.sin(t * 1.22) * 0.40 + 0.56
        y = -0.55 - t * 0.95 - t * t * 0.25
        rz = -0.18 - t * 0.82
        parts.append(
            cube(
                f"curved_mag_segment_{i:02d}",
                (0.28 * (1 - t * 0.18), 0.17, 0.42),
                (x, y, 0),
                mats["blackened_steel"],
                0.035,
                (0, 0, rz),
            )
        )
        if i % 2 == 0:
            parts.append(
                cube(
                    f"magazine_rib_{i:02d}",
                    (0.32, 0.030, 0.45),
                    (x, y + 0.01, 0),
                    mats["edge_wear"],
                    0.006,
                    (0, 0, rz),
                )
            )
    parts.append(cube("magazine_well", (0.36, 0.18, 0.45), (0.54, -0.50, 0), mats["blackened_steel"], 0.035))

    for i in range(9):
        x = -1.0 + i * 0.28
        parts.append(cyl_x(f"left_rivet_{i:02d}", 0.03, 0.03, (x, 0.12, 0.245), mats["edge_wear"], 18))
        parts.append(cyl_x(f"lower_rivet_{i:02d}", 0.03, 0.03, (x, -0.05, 0.245), mats["edge_wear"], 18))

    parts.append(cube("receiver_panel_line_upper", (1.05, 0.030, 0.035), (0.58, 0.23, 0.252), mats["edge_wear"], 0.004))
    parts.append(cube("receiver_panel_line_lower", (0.74, 0.030, 0.035), (0.74, 0.02, 0.252), mats["edge_wear"], 0.004))
    parts.append(
        cube(
            "762_brass_marking",
            (0.22, 0.030, 0.036),
            (0.36, 0.31, 0.255),
            mats["brass"],
            0.004,
            (0, 0, 0.25),
        )
    )

    for i in range(18):
        x = -1.1 + i * 0.14
        parts.append(
            cube(
                f"handplaced_wear_{i:02d}",
                (0.075, 0.012, 0.025),
                (x, 0.23 + (i % 3) * 0.035, 0.278),
                mats["edge_wear"],
                0.003,
                (0, 0, -0.2 + (i % 5) * 0.1),
            )
        )

    proxy = cube("collision_proxy_nonrender", (4.75, 2.05, 0.82), (0.35, -0.25, 0), mats["proxy"], 0.0)
    proxy.display_type = "WIRE"
    proxy.hide_render = True
    parts.append(proxy)

    add_anchor("Muzzle", (2.75, 0.08, 0))
    add_anchor("GripMount", (-0.42, -0.76, 0))
    add_anchor("SightLine", (0.35, 0.74, 0))

    return parts


def setup_scene() -> None:
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 96
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.ops.object.light_add(type="AREA", location=(-3.2, -4.2, 5.8))
    key = bpy.context.object
    key.name = "large_softbox_key"
    key.data.energy = 520
    key.data.size = 4.5
    bpy.ops.object.light_add(type="POINT", location=(2.5, 3.2, 2.6))
    rim = bpy.context.object
    rim.name = "cool_rim_light"
    rim.data.energy = 80
    rim.data.color = (0.55, 0.68, 1.0)
    bpy.ops.object.camera_add(location=(4.0, -5.0, 2.45), rotation=(math.radians(64), 0, math.radians(42)))
    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1000


def write_report(out_dir: Path, glb_path: Path, render_path: Path, parts: list[bpy.types.Object]) -> None:
    bbox_min = Vector((1e9, 1e9, 1e9))
    bbox_max = Vector((-1e9, -1e9, -1e9))
    for obj in parts:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            bbox_min.x = min(bbox_min.x, world.x)
            bbox_min.y = min(bbox_min.y, world.y)
            bbox_min.z = min(bbox_min.z, world.z)
            bbox_max.x = max(bbox_max.x, world.x)
            bbox_max.y = max(bbox_max.y, world.y)
            bbox_max.z = max(bbox_max.z, world.z)

    report = {
        "candidate": "groza_procedural_candidate",
        "source_reference": "/Users/yuanshaochen/Documents/groza_high_detail_3d_model_viewer.html",
        "output_glb": str(glb_path),
        "preview_png": str(render_path),
        "output_sha256": sha256(glb_path),
        "preview_sha256": sha256(render_path),
        "mesh_object_count": sum(1 for obj in parts if obj.type == "MESH"),
        "anchors": [
            {"name": "Muzzle", "location": [2.75, 0.08, 0]},
            {"name": "GripMount", "location": [-0.42, -0.76, 0]},
            {"name": "SightLine", "location": [0.35, 0.74, 0]},
        ],
        "bbox": {
            "min": list(bbox_min),
            "max": list(bbox_max),
            "size": list(bbox_max - bbox_min),
        },
        "material_names": sorted(mat.name for mat in bpy.data.materials),
        "limitations": [
            "Procedural hard-surface candidate derived from the local GROZA viewer, "
            "not a photogrammetry or text-to-3D generated mesh.",
            "Materials are Blender procedural/PBR-style colors without baked texture images.",
            "Useful for game integration and silhouette proof while a higher-realism generator route is validated.",
        ],
    }
    (out_dir / "blender_groza_procedural_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    out_dir, output_name = parse_args()
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_scene()
    parts = create_groza_candidate()
    setup_scene()

    render_path = out_dir / "preview.png"
    glb_path = out_dir / output_name

    bpy.context.scene.render.filepath = str(render_path)
    bpy.ops.render.render(write_still=True)
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        export_apply=True,
        export_materials="EXPORT",
    )
    write_report(out_dir, glb_path, render_path, parts)


if __name__ == "__main__":
    main()
