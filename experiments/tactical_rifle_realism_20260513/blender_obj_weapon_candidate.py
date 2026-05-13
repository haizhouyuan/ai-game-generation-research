#!/usr/bin/env python3
"""Import a weapon OBJ, normalize it, add gameplay anchors, render, and export GLB.

Run with Blender:

    /Applications/Blender.app/Contents/MacOS/Blender --background --python blender_obj_weapon_candidate.py -- \
      INPUT_OBJ OUT_DIR --output-name rifle_obj_baseline.glb
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
    if bpy is not None:
        return
    import bpy as blender_bpy
    from mathutils import Vector as blender_vector

    bpy = blender_bpy
    Vector = blender_vector


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args(argv: list[str] | None = None) -> tuple[Path, Path, str]:
    if argv is None:
        if "--" not in sys.argv:
            raise SystemExit(
                "usage: blender --background --python "
                "blender_obj_weapon_candidate.py -- INPUT_OBJ OUT_DIR"
            )
        argv = sys.argv[sys.argv.index("--") + 1 :]
    parser = argparse.ArgumentParser()
    parser.add_argument("input_obj", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--output-name", default="rifle_obj_baseline.glb")
    args = parser.parse_args(argv)
    if Path(args.output_name).name != args.output_name or not args.output_name.endswith(".glb"):
        raise SystemExit("--output-name must be a bare .glb filename")
    return args.input_obj.resolve(), args.out_dir.resolve(), args.output_name


def scene_bbox(mesh_objects: list[Any]) -> tuple[Any, Any]:
    points = []
    for obj in mesh_objects:
        if obj.type == "MESH":
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        raise RuntimeError("no mesh objects found")
    mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return mins, maxs


def normalize_weapon(mesh_objects: list[Any], target_length: float = 1.55) -> dict[str, object]:
    mins, maxs = scene_bbox(mesh_objects)
    center = (mins + maxs) / 2
    dims = maxs - mins
    length = max(dims.z, 0.0001)
    scale_factor = target_length / length
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


def improve_materials(mesh_objects: list[Any]) -> list[dict[str, object]]:
    rows = []
    for obj in mesh_objects:
        for material in obj.data.materials:
            if not material:
                continue
            material.use_nodes = True
            principled = material.node_tree.nodes.get("Principled BSDF")
            name = material.name.lower()
            if principled:
                if "metal" in name or "steel" in name or "gunbody" in name:
                    principled.inputs["Metallic"].default_value = 0.82
                    principled.inputs["Roughness"].default_value = 0.34
                elif "wood" in name:
                    principled.inputs["Metallic"].default_value = 0.0
                    principled.inputs["Roughness"].default_value = 0.68
                elif "rubber" in name or "polymer" in name:
                    principled.inputs["Metallic"].default_value = 0.0
                    principled.inputs["Roughness"].default_value = 0.82
                elif "glass" in name or "lens" in name:
                    principled.inputs["Metallic"].default_value = 0.0
                    principled.inputs["Roughness"].default_value = 0.08
                    material.blend_method = "BLEND"
            rows.append({"object": obj.name, "material": material.name})
    return rows


def add_anchor(name: str, location: tuple[float, float, float]) -> Any:
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=location)
    empty = bpy.context.object
    empty.name = name
    empty.empty_display_size = 0.08
    return empty


def add_proxy(mesh_objects: list[Any]) -> dict[str, object]:
    mins, maxs = scene_bbox(mesh_objects)
    center = (mins + maxs) / 2
    dims = maxs - mins
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    proxy = bpy.context.object
    proxy.name = "COLLIDER_PROXY_weapon_bbox"
    proxy.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    proxy.display_type = "WIRE"
    proxy.hide_render = True
    return {"name": proxy.name, "center": list(center), "dimensions": list(dims)}


def setup_render(mesh_objects: list[Any]) -> Path:
    bpy.ops.object.light_add(type="AREA", location=(-2.5, -3.2, 3.0))
    key = bpy.context.object
    key.name = "key_softbox"
    key.data.energy = 550
    key.data.size = 4.0
    bpy.ops.object.camera_add(location=(2.8, -4.6, 2.0), rotation=(1.18, 0.0, 0.55))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    mins, maxs = scene_bbox(mesh_objects)
    target = (mins + maxs) / 2
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.render.resolution_x = 1400
    bpy.context.scene.render.resolution_y = 900
    bpy.context.scene.eevee.taa_render_samples = 64
    return Path("preview.png")


def main() -> int:
    ensure_blender_modules()
    input_obj, out_dir, output_name = parse_args()
    out_dir.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    if hasattr(bpy.ops.wm, "obj_import"):
        bpy.ops.wm.obj_import(filepath=str(input_obj))
    else:
        bpy.ops.import_scene.obj(filepath=str(input_obj))

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    normalization = normalize_weapon(mesh_objects)
    material_rows = improve_materials(mesh_objects)

    mins, maxs = scene_bbox(mesh_objects)
    muzzle = add_anchor("Muzzle", (0.0, 0.0, maxs.z + 0.04))
    grip = add_anchor("GripMount", (0.0, mins.y, (mins.z + maxs.z) * 0.42))
    proxy = add_proxy(mesh_objects)

    render_name = setup_render(mesh_objects)
    render_path = out_dir / render_name
    bpy.context.scene.render.filepath = str(render_path)
    bpy.ops.render.render(write_still=True)

    output_path = out_dir / output_name
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
    )

    report = {
        "input_obj": str(input_obj),
        "output_glb": str(output_path),
        "preview_png": str(render_path),
        "output_sha256": sha256(output_path),
        "preview_sha256": sha256(render_path),
        "normalization": normalization,
        "anchors": [
            {"name": muzzle.name, "location": list(muzzle.location)},
            {"name": grip.name, "location": list(grip.location)},
        ],
        "proxy": proxy,
        "mesh_count": len(mesh_objects),
        "material_bindings": material_rows,
        "limitations": [
            "Candidate is an existing prototype OBJ baseline, not a generated high-realism final asset.",
            "Materials are heuristic PBR-style adjustments without source-baked texture maps.",
            "Muzzle anchor is inferred from bounding box and must be checked in-game.",
        ],
    }
    (out_dir / "blender_weapon_candidate_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
