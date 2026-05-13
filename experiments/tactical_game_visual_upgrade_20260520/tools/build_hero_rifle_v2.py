#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import bpy


def parse_args() -> Path:
    if "--" not in sys.argv:
        raise SystemExit("usage: blender --background --python build_hero_rifle_v2.py -- OUT_DIR")
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :]).out_dir.resolve()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images):
        for item in list(block):
            block.remove(item)


def write_image(path: Path, kind: str, size: int = 512) -> None:
    random.seed(kind)
    image = bpy.data.images.new(path.stem, width=size, height=size, alpha=True)
    pixels: list[float] = []
    for y in range(size):
        for x in range(size):
            u = x / max(1, size - 1)
            v = y / max(1, size - 1)
            scratch = 1.0 if (x + y * 3 + random.randint(0, 47)) % 83 == 0 else 0.0
            grime = 0.5 + 0.5 * math.sin(u * 38.0 + v * 17.0)
            if kind == "basecolor":
                r = 0.08 + 0.07 * grime + scratch * 0.44
                g = 0.09 + 0.06 * grime + scratch * 0.40
                b = 0.095 + 0.05 * grime + scratch * 0.32
            elif kind == "normal":
                r = 0.50 + 0.08 * math.sin(u * 70.0)
                g = 0.50 + 0.08 * math.cos(v * 70.0)
                b = 0.92
            elif kind == "roughness":
                r = g = b = 0.28 + 0.46 * grime - scratch * 0.12
            elif kind == "metallic":
                r = g = b = 0.88 if v > 0.18 else 0.12
            elif kind == "ao":
                edge = min(u, v, 1.0 - u, 1.0 - v)
                r = g = b = 0.55 + min(edge * 4.0, 0.42)
            else:
                r = g = b = 1.0
            pixels.extend([max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b)), 1.0])
    image.pixels.foreach_set(pixels)
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()


def make_pbr_material(texture_dir: Path):
    mat = bpy.data.materials.new("hero_rifle_v2_pbr_mapped_dark_steel")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    def image_node(name: str, colorspace: str = "sRGB"):
        img = bpy.data.images.load(str(texture_dir / f"{name}.png"))
        img.colorspace_settings.name = colorspace
        node = nodes.new("ShaderNodeTexImage")
        node.name = f"{name}_texture"
        node.image = img
        return node

    base = image_node("basecolor", "sRGB")
    rough = image_node("roughness", "Non-Color")
    metal = image_node("metallic", "Non-Color")
    normal_img = image_node("normal", "Non-Color")
    normal = nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 0.78

    links.new(base.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
    links.new(metal.outputs["Color"], bsdf.inputs["Metallic"])
    links.new(normal_img.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def cube(name: str, dims, loc, mat, bevel: float = 0.025, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("beveled_edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.affect = "EDGES"
    obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return obj


def cyl_x(name: str, radius: float, length: float, loc, mat, vertices: int = 48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=loc, rotation=(0, math.pi / 2, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return obj


def anchor(name: str, loc):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.14
    obj.location = loc
    bpy.context.collection.objects.link(obj)


def add_lights_and_camera() -> None:
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.ops.object.light_add(type="AREA", location=(-3.4, -4.8, 4.2))
    key = bpy.context.object
    key.name = "large_softbox_key"
    key.data.energy = 520
    key.data.size = 4.4
    bpy.ops.object.light_add(type="POINT", location=(2.6, 2.2, 1.8))
    rim = bpy.context.object
    rim.name = "cool_blue_rim"
    rim.data.energy = 95
    rim.data.color = (0.55, 0.68, 1.0)
    bpy.ops.object.camera_add(location=(3.7, -4.2, 1.75), rotation=(math.radians(66), 0, math.radians(42)))
    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.render.resolution_x = 1400
    bpy.context.scene.render.resolution_y = 900


def build_rifle(mat) -> list[bpy.types.Object]:
    parts = [
        cube("receiver_upper_pbr", (1.36, 0.32, 0.42), (-0.45, 0.14, 0), mat, 0.052),
        cube("receiver_lower_pbr", (1.02, 0.28, 0.38), (-0.46, -0.10, 0), mat, 0.045),
        cube("freefloat_rail_pbr", (1.50, 0.30, 0.44), (0.78, 0.04, 0), mat, 0.043),
        cube("folding_stock_pbr", (0.88, 0.32, 0.40), (-1.35, 0.01, 0), mat, 0.046),
        cube("rubber_buttpad_pbr", (0.16, 0.48, 0.42), (-1.86, 0.01, 0), mat, 0.018),
        cube("box_magazine_pbr", (0.34, 0.70, 0.36), (-0.40, -0.60, 0), mat, 0.042, (0, 0, -0.10)),
        cube("angled_foregrip_pbr", (0.24, 0.58, 0.30), (0.62, -0.45, 0), mat, 0.040, (0, 0, 0.18)),
        cyl_x("cold_hammer_barrel_pbr", 0.058, 1.72, (1.78, 0.08, 0), mat, 64),
        cyl_x("ported_muzzle_device_pbr", 0.088, 0.34, (2.78, 0.08, 0), mat, 64),
        cyl_x("optic_body_pbr", 0.145, 0.58, (-0.15, 0.54, 0), mat, 64),
        cube("optic_mount_front_pbr", (0.08, 0.22, 0.28), (0.10, 0.36, 0), mat, 0.012),
        cube("optic_mount_rear_pbr", (0.08, 0.22, 0.28), (-0.42, 0.36, 0), mat, 0.012),
    ]
    for i in range(12):
        parts.append(cube(f"top_rail_tooth_pbr_{i:02d}", (0.070, 0.032, 0.50), (-1.02 + i * 0.18, 0.31, 0), mat, 0.006))
    for i in range(9):
        parts.append(cube(f"mlok_slot_pbr_{i:02d}", (0.050, 0.030, 0.24), (0.25 + i * 0.12, 0.23, 0.245), mat, 0.004))
    for i in range(8):
        parts.append(cyl_x(f"edge_wear_rivet_pbr_{i:02d}", 0.022, 0.022, (-0.95 + i * 0.18, -0.02, 0.235), mat, 18))
    return parts


def main() -> None:
    out_dir = parse_args()
    texture_dir = out_dir / "textures"
    model_dir = out_dir / "model"
    evidence_dir = out_dir / "evidence"
    reports_dir = out_dir / "reports"
    for directory in (texture_dir, model_dir, evidence_dir, reports_dir, out_dir / "source"):
        directory.mkdir(parents=True, exist_ok=True)

    clean_scene()
    for name in ("basecolor", "normal", "roughness", "metallic", "ao"):
        write_image(texture_dir / f"{name}.png", name)
    mat = make_pbr_material(texture_dir)
    parts = build_rifle(mat)
    anchor("Muzzle", (2.98, 0.08, 0))
    anchor("Grip_R", (0.62, -0.45, 0))
    anchor("Grip_L", (0.34, -0.26, 0))
    anchor("Optic", (-0.15, 0.54, 0))
    anchor("PickupRoot", (0, 0, 0))
    anchor("ThirdPersonMount", (-0.30, 0.05, 0))
    add_lights_and_camera()

    preview = evidence_dir / "blender_preview.png"
    glb = model_dir / "optimized.glb"
    bpy.context.scene.render.filepath = str(preview)
    bpy.ops.render.render(write_still=True)
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", export_apply=True, export_materials="EXPORT")

    material_report = {
        "asset_id": "target_hero_rifle_v2",
        "material_map_count": 5,
        "texture_maps": {
            name: {
                "path": str(texture_dir / f"{name}.png"),
                "sha256": sha256(texture_dir / f"{name}.png")
            }
            for name in ("basecolor", "normal", "roughness", "metallic", "ao")
        },
        "material_names": [mat.name],
        "anchors": ["Muzzle", "Grip_R", "Grip_L", "Optic", "PickupRoot", "ThirdPersonMount"],
        "mesh_object_count": sum(1 for obj in parts if obj.type == "MESH"),
        "model_sha256": sha256(glb),
        "preview_sha256": sha256(preview),
        "route": "Route A local Blender-first procedural PBR packet; no external downloads"
    }
    (reports_dir / "material_report.json").write_text(json.dumps(material_report, indent=2) + "\n")
    (reports_dir / "blender_cleanup_report.json").write_text(json.dumps({
        "asset_id": "target_hero_rifle_v2",
        "cleanup": "Generated clean local hard-surface geometry with bevels, weighted normals, named anchors, and image texture nodes.",
        "source": "local procedural Blender script",
        "downloaded_assets": []
    }, indent=2) + "\n")
    (out_dir / "source" / "reference.md").write_text("# Hero Rifle V2 Reference\n\nLocal fictional tactical rifle. No real weapon manufacturing reference or external asset download was used.\n")
    (out_dir / "source" / "license.md").write_text("# License\n\nGenerated locally in this repository with Blender Python. No third-party asset license dependency.\n")
    print(json.dumps(material_report, indent=2))


if __name__ == "__main__":
    main()
