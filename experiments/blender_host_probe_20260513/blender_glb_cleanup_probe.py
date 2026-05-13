#!/usr/bin/env python3
"""Disposable Blender GLB cleanup/export proof.

Run with Blender, for example:

    /Applications/Blender.app/Contents/MacOS/Blender --background --python blender_glb_cleanup_probe.py -- \
        INPUT_GLB OUT_DIR [--output-name NAME.glb] [--material-strategy preserve|rover-v1] \
        [--texture-strategy none|rover-v1-procedural]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

bpy: Any = None
Vector: Any = None


def ensure_blender_modules() -> None:
    global bpy, Vector
    if bpy is not None and Vector is not None:
        return
    import bpy as blender_bpy
    from mathutils import Vector as blender_vector

    bpy = blender_bpy
    Vector = blender_vector


def default_output_name(input_glb: Path) -> str:
    return f"{input_glb.stem}_blender_cleaned_with_proxy.glb"


def validate_output_name(name: str) -> str:
    candidate = Path(name)
    if candidate.name != name or name in {"", ".", ".."}:
        raise argparse.ArgumentTypeError("output name must be a bare filename")
    if candidate.suffix.lower() != ".glb":
        raise argparse.ArgumentTypeError("output name must end with .glb")
    return name


MATERIAL_STRATEGIES = ("preserve", "rover-v1")
TEXTURE_STRATEGIES = ("none", "rover-v1-procedural")


def parse_args(argv: list[str] | None = None) -> tuple[Path, Path, str, str, str, int]:
    if argv is None:
        if "--" not in sys.argv:
            raise SystemExit(
                "usage: blender --background --python blender_glb_cleanup_probe.py -- "
                "INPUT_GLB OUT_DIR [--output-name NAME.glb] [--material-strategy preserve|rover-v1] "
                "[--texture-strategy none|rover-v1-procedural]"
            )
        argv = sys.argv[sys.argv.index("--") + 1 :]
    parser = argparse.ArgumentParser(description="Normalize, proxy, render, and re-export one GLB with Blender.")
    parser.add_argument("input_glb", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--output-name", type=validate_output_name)
    parser.add_argument("--material-strategy", choices=MATERIAL_STRATEGIES, default="preserve")
    parser.add_argument("--texture-strategy", choices=TEXTURE_STRATEGIES, default="none")
    parser.add_argument("--texture-size", type=int, default=512)
    args = parser.parse_args(argv)
    if args.texture_size < 16 or args.texture_size > 4096:
        raise argparse.ArgumentTypeError("texture size must be between 16 and 4096")
    input_glb = args.input_glb.resolve()
    output_name = args.output_name or default_output_name(input_glb)
    return (
        input_glb,
        args.out_dir.resolve(),
        output_name,
        args.material_strategy,
        args.texture_strategy,
        args.texture_size,
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scene_bbox(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points: list[Vector] = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        raise RuntimeError("no mesh bounds found")
    mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return mins, maxs


def set_origin_and_scale(mesh_objects: list[bpy.types.Object], target_max_dimension: float = 2.0) -> dict[str, object]:
    mins, maxs = scene_bbox(mesh_objects)
    center = (mins + maxs) / 2
    dims = maxs - mins
    max_dim = max(dims.x, dims.y, dims.z)
    scale_factor = target_max_dimension / max_dim if max_dim > 0 else 1.0
    for obj in mesh_objects:
        obj.location = (obj.location - center) * scale_factor
        obj.scale = obj.scale * scale_factor
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_objects[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for obj in mesh_objects:
        obj.select_set(False)
    new_mins, new_maxs = scene_bbox(mesh_objects)
    return {
        "original_bbox_min": list(mins),
        "original_bbox_max": list(maxs),
        "original_dimensions": list(dims),
        "scale_factor": scale_factor,
        "normalized_bbox_min": list(new_mins),
        "normalized_bbox_max": list(new_maxs),
        "normalized_dimensions": list(new_maxs - new_mins),
    }


def add_proxy_collider(mesh_objects: list[bpy.types.Object]) -> dict[str, object]:
    mins, maxs = scene_bbox(mesh_objects)
    center = (mins + maxs) / 2
    dims = maxs - mins
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    proxy = bpy.context.object
    proxy.name = "COLLIDER_PROXY_bbox_simple_box"
    proxy.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    material = bpy.data.materials.new("proxy_collider_wire_blue")
    material.diffuse_color = (0.1, 0.55, 1.0, 0.25)
    proxy.data.materials.append(material)
    proxy.display_type = "WIRE"
    proxy.hide_render = True
    return {"name": proxy.name, "type": "box", "dimensions": list(dims), "center": list(center)}


def make_material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    roughness: float,
    metalness: float,
    emissive: tuple[float, float, float] | None = None,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = color
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Roughness"].default_value = roughness
        principled.inputs["Metallic"].default_value = metalness
        if emissive:
            principled.inputs["Emission Color"].default_value = (*emissive, 1.0)
            principled.inputs["Emission Strength"].default_value = 0.25
    return material


def polygon_center(mesh: bpy.types.Mesh, polygon: bpy.types.MeshPolygon) -> Vector:
    total = Vector((0.0, 0.0, 0.0))
    for vertex_index in polygon.vertices:
        total += mesh.vertices[vertex_index].co
    return total / len(polygon.vertices)


def apply_rover_v1_materials(mesh_objects: list[bpy.types.Object]) -> dict[str, object]:
    body = make_material("rw_rover_v1_body_teal", (0.12, 0.58, 0.66, 1.0), roughness=0.54, metalness=0.06)
    accent = make_material(
        "rw_rover_v1_safety_yellow",
        (0.94, 0.66, 0.18, 1.0),
        roughness=0.42,
        metalness=0.03,
    )
    rubber = make_material("rw_rover_v1_rubber_dark", (0.05, 0.07, 0.08, 1.0), roughness=0.82, metalness=0.0)
    glass = make_material(
        "rw_rover_v1_sensor_glass",
        (0.55, 0.95, 1.0, 1.0),
        roughness=0.22,
        metalness=0.0,
        emissive=(0.12, 0.45, 0.55),
    )
    materials = [body, accent, rubber, glass]
    material_counts = {material.name: 0 for material in materials}

    for obj in mesh_objects:
        mesh = obj.data
        mesh.materials.clear()
        for material in materials:
            mesh.materials.append(material)
        xs = [vertex.co.x for vertex in mesh.vertices]
        ys = [vertex.co.y for vertex in mesh.vertices]
        zs = [vertex.co.z for vertex in mesh.vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        dim_x = max(max_x - min_x, 0.0001)
        dim_y = max(max_y - min_y, 0.0001)
        dim_z = max(max_z - min_z, 0.0001)
        for polygon in mesh.polygons:
            center = polygon_center(mesh, polygon)
            if center.z < min_z + dim_z * 0.24 or abs(center.y) > dim_y * 0.36:
                material_index = 2
            elif center.z > min_z + dim_z * 0.74:
                material_index = 1
            elif center.x > max_x - dim_x * 0.18 and center.z > min_z + dim_z * 0.42:
                material_index = 3
            else:
                material_index = 0
            polygon.material_index = material_index
            material_counts[materials[material_index].name] += 1

    return {
        "strategy": "rover-v1",
        "material_names": [material.name for material in materials],
        "polygon_material_counts": material_counts,
        "texture_state": "pbr_materials_no_external_textures",
    }


def apply_material_strategy(mesh_objects: list[bpy.types.Object], strategy: str) -> dict[str, object]:
    if strategy == "preserve":
        return {"strategy": "preserve", "texture_state": "source_materials_preserved"}
    if strategy == "rover-v1":
        return apply_rover_v1_materials(mesh_objects)
    raise ValueError(f"unknown material strategy: {strategy}")


ROVER_TEXTURE_COLORS = {
    "rw_rover_v1_body_teal": (0.12, 0.58, 0.66, 1.0),
    "rw_rover_v1_safety_yellow": (0.94, 0.66, 0.18, 1.0),
    "rw_rover_v1_rubber_dark": (0.05, 0.07, 0.08, 1.0),
    "rw_rover_v1_sensor_glass": (0.55, 0.95, 1.0, 1.0),
}


def ensure_planar_uvs(mesh_objects: list[bpy.types.Object]) -> list[dict[str, object]]:
    uv_reports = []
    for obj in mesh_objects:
        mesh = obj.data
        uv_layer = mesh.uv_layers.get("RW_ROVER_UV0") or mesh.uv_layers.new(name="RW_ROVER_UV0")
        xs = [vertex.co.x for vertex in mesh.vertices]
        zs = [vertex.co.z for vertex in mesh.vertices]
        min_x, max_x = min(xs), max(xs)
        min_z, max_z = min(zs), max(zs)
        dim_x = max(max_x - min_x, 0.0001)
        dim_z = max(max_z - min_z, 0.0001)
        for loop in mesh.loops:
            vertex = mesh.vertices[loop.vertex_index]
            uv_layer.data[loop.index].uv = ((vertex.co.x - min_x) / dim_x, (vertex.co.z - min_z) / dim_z)
        uv_reports.append(
            {
                "object": obj.name,
                "uv_layer": uv_layer.name,
                "uv_loop_count": len(uv_layer.data),
                "mapping": "planar_xz_normalized_bbox",
            }
        )
    return uv_reports


def create_procedural_texture(
    name: str,
    base_color: tuple[float, float, float, float],
    texture_dir: Path,
    size: int,
) -> tuple[bpy.types.Image, Path]:
    image = bpy.data.images.new(name, width=size, height=size, alpha=True)
    pixels = [0.0] * (size * size * 4)
    for y in range(size):
        for x in range(size):
            checker = 0.92 if ((x // 32) + (y // 32)) % 2 else 1.0
            stripe = 1.08 if (x + y) % 97 < 5 else 1.0
            factor = min(checker * stripe, 1.0)
            offset = (y * size + x) * 4
            pixels[offset] = min(base_color[0] * factor, 1.0)
            pixels[offset + 1] = min(base_color[1] * factor, 1.0)
            pixels[offset + 2] = min(base_color[2] * factor, 1.0)
            pixels[offset + 3] = base_color[3]
    image.pixels.foreach_set(pixels)
    image.pack()
    texture_path = texture_dir / f"{name}.png"
    image.filepath_raw = str(texture_path)
    image.file_format = "PNG"
    image.save()
    return image, texture_path


def connect_base_color_texture(material: bpy.types.Material, image: bpy.types.Image) -> None:
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if not principled:
        return
    texture_node = nodes.new(type="ShaderNodeTexImage")
    texture_node.name = f"{material.name}_base_color_texture"
    texture_node.image = image
    material.node_tree.links.new(texture_node.outputs["Color"], principled.inputs["Base Color"])


def apply_texture_strategy(
    mesh_objects: list[bpy.types.Object],
    material_report: dict[str, object],
    out_dir: Path,
    strategy: str,
    size: int,
) -> dict[str, object]:
    if strategy == "none":
        return {"strategy": "none", "texture_state": material_report.get("texture_state", "not_applied")}
    if strategy != "rover-v1-procedural":
        raise ValueError(f"unknown texture strategy: {strategy}")
    if material_report.get("strategy") != "rover-v1":
        raise ValueError("rover-v1-procedural texture strategy requires --material-strategy rover-v1")

    texture_dir = out_dir / "textures"
    texture_dir.mkdir(parents=True, exist_ok=True)
    uv_layers = ensure_planar_uvs(mesh_objects)
    texture_maps = []
    for material_name, color in ROVER_TEXTURE_COLORS.items():
        material = bpy.data.materials.get(material_name)
        if not material:
            continue
        image, texture_path = create_procedural_texture(material_name, color, texture_dir, size)
        connect_base_color_texture(material, image)
        texture_maps.append(
            {
                "material": material_name,
                "role": "base_color",
                "path": str(texture_path),
                "sha256": sha256(texture_path),
                "size_bytes": texture_path.stat().st_size,
            }
        )
    return {
        "strategy": strategy,
        "texture_state": "procedural_external_texture_maps_with_uvs",
        "texture_size": [size, size],
        "uv_layers": uv_layers,
        "texture_maps": texture_maps,
        "limitations": [
            "Procedural material-color texture maps, not source-baked photoreal PBR maps.",
            "Planar normalized bounding-box UVs are a validation pass, not production UV unwrapping.",
        ],
    }


def add_camera_and_light(mesh_objects: list[bpy.types.Object]) -> None:
    mins, maxs = scene_bbox(mesh_objects)
    center = (mins + maxs) / 2
    dims = maxs - mins
    radius = max(dims.length, 2.0)
    bpy.ops.object.light_add(type="AREA", location=(center.x - 2.5, center.y - 3.0, center.z + 4.0))
    light = bpy.context.object
    light.name = "proof_key_area_light"
    light.data.energy = 450
    light.data.size = 4
    bpy.ops.object.camera_add(location=(center.x + radius, center.y - radius * 1.4, center.z + radius * 0.8))
    camera = bpy.context.object
    direction = center - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 55
    bpy.context.scene.camera = camera


def collect_mesh_report(
    input_glb: Path,
    imported_objects: list[bpy.types.Object],
    cleanup: dict[str, object],
    material_report: dict[str, object],
    texture_report: dict[str, object],
) -> dict[str, object]:
    mesh_objects = [obj for obj in imported_objects if obj.type == "MESH"]
    material_names = sorted(
        {slot.material.name for obj in mesh_objects for slot in obj.material_slots if slot.material}
    )
    return {
        "input_glb": str(input_glb),
        "input_sha256": sha256(input_glb),
        "mesh_object_count": len(mesh_objects),
        "mesh_objects": [
            {
                "name": obj.name,
                "vertices": len(obj.data.vertices),
                "faces": len(obj.data.polygons),
                "material_slots": len(obj.material_slots),
            }
            for obj in mesh_objects
        ],
        "material_names": material_names,
        "material_strategy": material_report,
        "texture_strategy": texture_report,
        "texture_state": texture_report.get(
            "texture_state",
            material_report.get(
                "texture_state",
                "mesh-only" if not material_names else "materials-present-textures-not-assumed",
            ),
        ),
        "cleanup": cleanup,
    }


def main() -> None:
    ensure_blender_modules()
    input_glb, out_dir, output_name, material_strategy, texture_strategy, texture_size = parse_args()
    out_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=str(input_glb))
    imported_objects = list(bpy.context.scene.objects)
    mesh_objects = [obj for obj in imported_objects if obj.type == "MESH"]
    if not mesh_objects:
        raise RuntimeError("imported GLB contained no mesh objects")
    cleanup = set_origin_and_scale(mesh_objects)
    material_report = apply_material_strategy(mesh_objects, material_strategy)
    texture_report = apply_texture_strategy(mesh_objects, material_report, out_dir, texture_strategy, texture_size)
    proxy = add_proxy_collider(mesh_objects)
    add_camera_and_light(mesh_objects)
    report = collect_mesh_report(input_glb, imported_objects, cleanup, material_report, texture_report)
    report["proxy_collider"] = proxy
    report_path = out_dir / "blender_cleanup_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    cleaned_glb = out_dir / output_name
    bpy.ops.export_scene.gltf(filepath=str(cleaned_glb), export_format="GLB", export_apply=True)

    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.render.resolution_x = 960
    bpy.context.scene.render.resolution_y = 720
    bpy.context.scene.render.filepath = str(out_dir / "blender_cleanup_render.png")
    bpy.ops.render.render(write_still=True)

    summary = {
        "status": "DONE",
        "input_glb": str(input_glb),
        "cleaned_glb": str(cleaned_glb),
        "cleaned_glb_sha256": sha256(cleaned_glb),
        "render": str(out_dir / "blender_cleanup_render.png"),
        "render_sha256": sha256(out_dir / "blender_cleanup_render.png"),
        "report": str(report_path),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
