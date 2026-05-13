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


def parse_args(argv: list[str] | None = None) -> Path:
    if argv is None:
        if "--" not in sys.argv:
            raise SystemExit("usage: blender --background --python blender_m5_weapon_variants.py -- OUT_DIR")
        argv = sys.argv[sys.argv.index("--") + 1 :]
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    return parser.parse_args(argv).out_dir.resolve()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(block):
            block.remove(item)


def make_mat(name: str, color: tuple[float, float, float, float], roughness: float, metalness: float):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metalness
    return mat


def cube(name: str, dims: tuple[float, float, float], loc: tuple[float, float, float], mat, bevel: float = 0.025, rot: tuple[float, float, float] = (0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("small_bevels", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.affect = "EDGES"
    obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return obj


def cyl_x(name: str, radius: float, length: float, loc: tuple[float, float, float], mat, vertices: int = 48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=loc, rotation=(0, math.pi / 2, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return obj


def cyl_y(name: str, radius: float, length: float, loc: tuple[float, float, float], mat, vertices: int = 32, rot: tuple[float, float, float] = (0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return obj


def anchor(name: str, loc: tuple[float, float, float]):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.12
    empty.location = loc
    bpy.context.collection.objects.link(empty)
    return empty


def add_lights_and_camera(kind: str) -> Path:
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.ops.object.light_add(type="AREA", location=(-3.2, -4.6, 4.8))
    key = bpy.context.object
    key.name = "large_softbox_key"
    key.data.energy = 460
    key.data.size = 4.0
    bpy.ops.object.light_add(type="POINT", location=(2.8, 2.4, 2.2))
    rim = bpy.context.object
    rim.name = "cool_rim_light"
    rim.data.energy = 75
    rim.data.color = (0.55, 0.66, 1.0)
    bpy.ops.object.camera_add(location=(3.8, -4.4, 2.0), rotation=(math.radians(64), 0, math.radians(42)))
    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 820
    return Path(f"{kind}_preview.png")


def materials():
    return {
        "steel": make_mat("blackened_steel", (0.030, 0.032, 0.036, 1), 0.34, 0.86),
        "blued": make_mat("worn_blued_steel", (0.13, 0.145, 0.16, 1), 0.30, 0.88),
        "rubber": make_mat("matte_rubber", (0.020, 0.020, 0.019, 1), 0.82, 0.0),
        "poly": make_mat("fiber_reinforced_polymer", (0.075, 0.085, 0.078, 1), 0.70, 0.08),
        "tan": make_mat("tan_polymer_grip", (0.43, 0.34, 0.22, 1), 0.68, 0.05),
        "edge": make_mat("bright_edge_wear", (0.74, 0.69, 0.58, 1), 0.24, 1.0),
        "glass": make_mat("dark_optic_glass", (0.05, 0.12, 0.18, 1), 0.08, 0.0),
        "brass": make_mat("brass_rounds", (0.95, 0.64, 0.22, 1), 0.27, 1.0),
    }


def add_panel_rivets(parts: list[bpy.types.Object], mats, x0: float, x1: float, y: float, z: float, count: int) -> None:
    for i in range(count):
        t = i / max(1, count - 1)
        x = x0 + (x1 - x0) * t
        parts.append(cyl_x(f"rivet_{x:.2f}_{i:02d}", 0.022, 0.022, (x, y, z), mats["edge"], 18))


def build_pistol(mats) -> tuple[list[bpy.types.Object], dict]:
    parts: list[bpy.types.Object] = []
    parts.append(cube("pistol_slide_beveled", (1.12, 0.23, 0.34), (0.05, 0.22, 0), mats["blued"], 0.045))
    parts.append(cube("pistol_frame_polymer", (0.86, 0.18, 0.36), (-0.06, 0.04, 0), mats["poly"], 0.040))
    parts.append(cube("pistol_grip_textured", (0.26, 0.72, 0.34), (-0.44, -0.42, 0), mats["rubber"], 0.055, (0, 0, -0.18)))
    parts.append(cube("trigger_guard", (0.25, 0.31, 0.30), (-0.15, -0.17, 0), mats["steel"], 0.030))
    parts.append(cyl_x("barrel_visible", 0.050, 0.78, (0.60, 0.22, 0), mats["steel"], 48))
    parts.append(cyl_x("threaded_muzzle", 0.064, 0.18, (1.06, 0.22, 0), mats["edge"], 48))
    parts.append(cube("front_sight", (0.08, 0.05, 0.10), (0.58, 0.37, 0), mats["edge"], 0.010))
    parts.append(cube("rear_sight", (0.13, 0.055, 0.13), (-0.48, 0.38, 0), mats["edge"], 0.010))
    for i in range(6):
        parts.append(cube(f"slide_serration_{i:02d}", (0.035, 0.16, 0.39), (-0.47 + i * 0.055, 0.23, 0), mats["edge"], 0.006, (0, 0, -0.22)))
    for i in range(5):
        parts.append(cube(f"grip_stipple_{i:02d}", (0.020, 0.45, 0.025), (-0.51 + i * 0.035, -0.43, 0.185), mats["edge"], 0.003))
    parts.append(cube("weapon_collision_proxy_nonrender", (1.55, 1.10, 0.58), (0.05, -0.10, 0), mats["glass"], 0.0))
    parts[-1].display_type = "WIRE"
    parts[-1].hide_render = True
    anchor("Muzzle", (1.17, 0.22, 0))
    anchor("GripMount", (-0.43, -0.42, 0))
    return parts, {"muzzle": [1.17, 0.22, 0], "bbox_note": "compact sidearm"}


def build_shotgun(mats) -> tuple[list[bpy.types.Object], dict]:
    parts: list[bpy.types.Object] = []
    parts.append(cube("shotgun_receiver", (1.20, 0.34, 0.42), (-0.28, 0.05, 0), mats["blued"], 0.055))
    parts.append(cube("pump_forend_grooved", (0.92, 0.30, 0.50), (0.78, -0.03, 0), mats["tan"], 0.055))
    parts.append(cube("stock_polymer", (1.05, 0.34, 0.48), (-1.18, 0.02, 0), mats["poly"], 0.055))
    parts.append(cube("rubber_butt_pad", (0.16, 0.54, 0.52), (-1.78, 0.02, 0), mats["rubber"], 0.025))
    parts.append(cyl_x("upper_barrel", 0.072, 2.15, (1.28, 0.16, 0), mats["steel"], 64))
    parts.append(cyl_x("magazine_tube", 0.064, 1.82, (1.12, -0.10, 0), mats["steel"], 48))
    parts.append(cyl_x("ported_choke", 0.095, 0.30, (2.48, 0.16, 0), mats["edge"], 64))
    parts.append(cube("ghost_ring_rear", (0.20, 0.08, 0.35), (-0.62, 0.39, 0), mats["edge"], 0.015))
    parts.append(cube("front_bead_sight", (0.07, 0.055, 0.08), (2.30, 0.32, 0), mats["brass"], 0.010))
    for i in range(7):
        parts.append(cube(f"pump_groove_{i:02d}", (0.045, 0.34, 0.55), (0.42 + i * 0.11, -0.03, 0), mats["edge"], 0.006))
    for i in range(4):
        parts.append(cyl_x(f"side_saddle_shell_{i:02d}", 0.052, 0.34, (-0.52 + i * 0.16, 0.10, 0.31), mats["brass"], 24))
    add_panel_rivets(parts, mats, -0.85, 0.15, 0.09, 0.235, 7)
    parts.append(cube("weapon_collision_proxy_nonrender", (4.35, 1.15, 0.75), (0.35, 0.00, 0), mats["glass"], 0.0))
    parts[-1].display_type = "WIRE"
    parts[-1].hide_render = True
    anchor("Muzzle", (2.66, 0.16, 0))
    anchor("GripMount", (-0.20, -0.22, 0))
    return parts, {"muzzle": [2.66, 0.16, 0], "bbox_note": "pump shotgun with tube and shells"}


def build_dmr(mats) -> tuple[list[bpy.types.Object], dict]:
    parts: list[bpy.types.Object] = []
    parts.append(cube("dmr_receiver_upper", (1.45, 0.30, 0.42), (-0.40, 0.12, 0), mats["blued"], 0.050))
    parts.append(cube("dmr_receiver_lower", (1.10, 0.28, 0.40), (-0.45, -0.10, 0), mats["poly"], 0.045))
    parts.append(cube("freefloat_handguard", (1.55, 0.32, 0.46), (0.90, 0.03, 0), mats["steel"], 0.045))
    parts.append(cube("precision_stock", (1.05, 0.32, 0.42), (-1.52, 0.02, 0), mats["poly"], 0.050))
    parts.append(cube("adjustable_cheek_riser", (0.58, 0.12, 0.34), (-1.52, 0.34, 0), mats["tan"], 0.030))
    parts.append(cube("rubber_butt_pad", (0.16, 0.52, 0.46), (-2.13, 0.02, 0), mats["rubber"], 0.024))
    parts.append(cyl_x("match_barrel", 0.062, 1.92, (1.95, 0.08, 0), mats["steel"], 64))
    parts.append(cyl_x("muzzle_brake_two_port", 0.088, 0.32, (3.03, 0.08, 0), mats["edge"], 64))
    parts.append(cyl_x("scope_body", 0.145, 0.70, (-0.22, 0.55, 0), mats["steel"], 64))
    parts.append(cyl_x("scope_front_lens", 0.18, 0.14, (0.22, 0.55, 0), mats["glass"], 48))
    parts.append(cyl_x("scope_rear_lens", 0.16, 0.12, (-0.62, 0.55, 0), mats["glass"], 48))
    parts.append(cube("scope_mount_front", (0.08, 0.22, 0.30), (0.05, 0.36, 0), mats["edge"], 0.012))
    parts.append(cube("scope_mount_rear", (0.08, 0.22, 0.30), (-0.48, 0.36, 0), mats["edge"], 0.012))
    parts.append(cube("box_magazine", (0.34, 0.70, 0.40), (-0.38, -0.62, 0), mats["steel"], 0.045, (0, 0, -0.08)))
    parts.append(cube("angled_grip", (0.23, 0.62, 0.33), (0.66, -0.48, 0), mats["tan"], 0.045, (0, 0, 0.22)))
    for i in range(11):
        parts.append(cube(f"mlok_slot_{i:02d}", (0.05, 0.030, 0.24), (0.25 + i * 0.12, 0.22, 0.25), mats["edge"], 0.006))
        parts.append(cube(f"top_rail_tooth_{i:02d}", (0.075, 0.035, 0.50), (-0.95 + i * 0.18, 0.31, 0), mats["edge"], 0.006))
    add_panel_rivets(parts, mats, -0.98, 0.22, -0.02, 0.235, 8)
    parts.append(cube("weapon_collision_proxy_nonrender", (5.55, 1.65, 0.82), (0.45, -0.08, 0), mats["glass"], 0.0))
    parts[-1].display_type = "WIRE"
    parts[-1].hide_render = True
    anchor("Muzzle", (3.22, 0.08, 0))
    anchor("GripMount", (0.66, -0.48, 0))
    anchor("SightLine", (-0.22, 0.55, 0))
    return parts, {"muzzle": [3.22, 0.08, 0], "bbox_note": "precision rifle with optic and freefloat handguard"}


BUILDERS = {
    "pistol": build_pistol,
    "shotgun": build_shotgun,
    "dmr": build_dmr,
}


def bbox(parts: list[bpy.types.Object]) -> dict:
    bmin = Vector((1e9, 1e9, 1e9))
    bmax = Vector((-1e9, -1e9, -1e9))
    for obj in parts:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            bmin.x = min(bmin.x, world.x)
            bmin.y = min(bmin.y, world.y)
            bmin.z = min(bmin.z, world.z)
            bmax.x = max(bmax.x, world.x)
            bmax.y = max(bmax.y, world.y)
            bmax.z = max(bmax.z, world.z)
    return {"min": list(bmin), "max": list(bmax), "size": list(bmax - bmin)}


def main() -> None:
    out_dir = parse_args()
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"pipeline": "Blender procedural hard-surface M5 weapon variants", "assets": []}
    for kind, builder in BUILDERS.items():
        clean_scene()
        mats = materials()
        parts, meta = builder(mats)
        add_lights_and_camera(kind)
        preview_path = out_dir / f"{kind}_m5_preview.png"
        glb_path = out_dir / f"{kind}_m5_candidate.glb"
        bpy.context.scene.render.filepath = str(preview_path)
        bpy.ops.render.render(write_still=True)
        bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB", export_apply=True, export_materials="EXPORT")
        report["assets"].append(
            {
                "kind": kind,
                "output_glb": str(glb_path),
                "preview_png": str(preview_path),
                "output_sha256": sha256(glb_path),
                "preview_sha256": sha256(preview_path),
                "mesh_object_count": sum(1 for obj in parts if obj.type == "MESH"),
                "bbox": bbox(parts),
                "anchors": [{"name": "Muzzle", "location": meta["muzzle"]}],
                "material_names": sorted(mat.name for mat in bpy.data.materials),
                "limitations": [
                    "Local procedural hard-surface candidate, not scanned geometry.",
                    "Uses Blender PBR-style material factors without baked texture images.",
                    "Intended to replace low-fidelity in-game weapon primitives while higher-realism generator routes continue.",
                ],
            }
        )
    (out_dir / "m5_weapon_variants_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
