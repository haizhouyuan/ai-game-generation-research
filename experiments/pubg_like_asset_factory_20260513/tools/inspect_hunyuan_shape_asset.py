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


def parse_args() -> Path:
    if "--" not in sys.argv:
        raise SystemExit("usage: blender --background --python inspect_hunyuan_shape_asset.py -- ASSET_DIR")
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_dir", type=Path)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :]).asset_dir.resolve()


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


def import_asset(raw_glb: Path) -> list[bpy.types.Object]:
    bpy.ops.import_scene.gltf(filepath=str(raw_glb))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError(f"No mesh objects imported from {raw_glb}")
    return meshes


def scene_bounds(meshes: list[bpy.types.Object]) -> tuple[Vector, Vector, Vector]:
    corners: list[Vector] = []
    for obj in meshes:
        corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    min_v = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    max_v = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    return min_v, max_v, max_v - min_v


def normalize_scene(meshes: list[bpy.types.Object]) -> dict[str, list[float] | float]:
    min_v, max_v, size = scene_bounds(meshes)
    center = (min_v + max_v) * 0.5
    longest = max(size.x, size.y, size.z, 0.001)
    scale = 2.2 / longest
    root = bpy.data.objects.new("hunyuan_shape_demo_001_root", None)
    bpy.context.collection.objects.link(root)
    for obj in meshes:
        obj.parent = root
    root.location = -center
    root.scale = (scale, scale, scale)
    bpy.context.view_layer.objects.active = root
    root.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
    for obj in meshes:
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return {
        "source_bbox_min": [round(min_v.x, 6), round(min_v.y, 6), round(min_v.z, 6)],
        "source_bbox_max": [round(max_v.x, 6), round(max_v.y, 6), round(max_v.z, 6)],
        "source_bbox_size": [round(size.x, 6), round(size.y, 6), round(size.z, 6)],
        "normalization_scale": round(scale, 6),
    }


def count_texture_maps(materials: list[bpy.types.Material]) -> dict[str, object]:
    image_nodes: list[str] = []
    image_paths: list[str] = []
    for mat in materials:
        if not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.bl_idname == "ShaderNodeTexImage" and getattr(node, "image", None):
                image_nodes.append(f"{mat.name}:{node.name}")
                image_paths.append(bpy.path.abspath(node.image.filepath))
    return {
        "material_map_count": len(image_nodes),
        "image_nodes": image_nodes,
        "image_paths": image_paths,
    }


def add_lighting_and_camera(meshes: list[bpy.types.Object]) -> None:
    _, _, size = scene_bounds(meshes)
    radius = max(size.x, size.y, size.z, 1.0)
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    if hasattr(bpy.context.scene, "eevee"):
        bpy.context.scene.eevee.taa_render_samples = 64
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.ops.object.light_add(type="AREA", location=(-2.7, -3.2, 4.2))
    key = bpy.context.object
    key.name = "asset_preview_large_softbox"
    key.data.energy = 560
    key.data.size = 4.5
    bpy.ops.object.light_add(type="POINT", location=(2.5, 1.8, 2.0))
    rim = bpy.context.object
    rim.name = "asset_preview_cool_rim"
    rim.data.energy = 90
    rim.data.color = (0.58, 0.72, 1.0)
    bpy.ops.object.camera_add(location=(radius * 1.25, -radius * 1.55, radius * 0.75), rotation=(math.radians(63), 0, math.radians(39)))
    camera = bpy.context.object
    camera.name = "asset_preview_camera"
    bpy.context.scene.camera = camera
    bpy.context.scene.render.resolution_x = 1400
    bpy.context.scene.render.resolution_y = 900


def main() -> None:
    asset_dir = parse_args()
    raw_glb = asset_dir / "model" / "raw.glb"
    model_dir = asset_dir / "model"
    evidence_dir = asset_dir / "evidence"
    reports_dir = asset_dir / "reports"
    for directory in (model_dir, evidence_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    clean_scene()
    meshes = import_asset(raw_glb)
    norm_report = normalize_scene(meshes)
    materials = sorted({slot.material for obj in meshes for slot in obj.material_slots if slot.material}, key=lambda mat: mat.name)
    texture_report = count_texture_maps(materials)
    add_lighting_and_camera(meshes)

    cleaned_glb = model_dir / "cleaned.glb"
    optimized_glb = model_dir / "optimized.glb"
    preview = evidence_dir / "blender_preview.png"

    bpy.ops.export_scene.gltf(filepath=str(cleaned_glb), export_format="GLB", export_apply=True, export_materials="EXPORT")
    bpy.ops.export_scene.gltf(filepath=str(optimized_glb), export_format="GLB", export_apply=True, export_materials="EXPORT")
    bpy.context.scene.render.filepath = str(preview)
    bpy.ops.render.render(write_still=True)

    mesh_report = []
    total_vertices = 0
    total_polygons = 0
    for obj in meshes:
        total_vertices += len(obj.data.vertices)
        total_polygons += len(obj.data.polygons)
        mesh_report.append({
            "name": obj.name,
            "vertices": len(obj.data.vertices),
            "polygons": len(obj.data.polygons),
            "materials": [slot.material.name for slot in obj.material_slots if slot.material],
        })

    cleanup_report = {
        "asset_id": asset_dir.name,
        "route": "Hunyuan3D-2.1 standalone shape pipeline on HomePC GPU1",
        "source_model": "tencent/Hunyuan3D-2.1",
        "raw_glb": str(raw_glb),
        "cleaned_glb": str(cleaned_glb),
        "optimized_glb": str(optimized_glb),
        "raw_sha256": sha256(raw_glb),
        "cleaned_sha256": sha256(cleaned_glb),
        "optimized_sha256": sha256(optimized_glb),
        "preview_sha256": sha256(preview),
        "mesh_object_count": len(meshes),
        "total_vertices": total_vertices,
        "total_polygons": total_polygons,
        "normalization": norm_report,
        "mesh_objects": mesh_report,
        "cleanup": [
            "Imported Hunyuan shape-only GLB in Blender.",
            "Centered and normalized asset for deterministic preview/export.",
            "Applied smooth shading for preview readability.",
            "Exported cleaned.glb and optimized.glb placeholders for downstream gates."
        ],
    }
    material_report = {
        "asset_id": asset_dir.name,
        "route": "Hunyuan3D-2.1 shape-only smoke asset",
        "material_grade": "shape_only_no_pbr_maps",
        "accepted_as_final_visual_asset": False,
        "material_names": [mat.name for mat in materials],
        **texture_report,
        "required_next_gate": "Run Hunyuan Paint / PBR or alternate projection pipeline to produce basecolor, normal, roughness, metallic, and ao maps.",
    }
    (reports_dir / "blender_cleanup_report.json").write_text(json.dumps(cleanup_report, indent=2) + "\n")
    (reports_dir / "material_report.json").write_text(json.dumps(material_report, indent=2) + "\n")
    print(json.dumps({"cleanup_report": cleanup_report, "material_report": material_report}, indent=2))


if __name__ == "__main__":
    main()
