#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix, translation_matrix


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "outputs" / "assets"


def material(color: tuple[int, int, int, int]) -> trimesh.visual.material.PBRMaterial:
    return trimesh.visual.material.PBRMaterial(baseColorFactor=[c / 255 for c in color], roughnessFactor=0.72)


def box(name: str, size: tuple[float, float, float], loc: tuple[float, float, float], color: tuple[int, int, int, int]):
    mesh = trimesh.creation.box(extents=size)
    mesh.visual.material = material(color)
    mesh.apply_transform(translation_matrix(loc))
    mesh.metadata["name"] = name
    return mesh


def cylinder(name: str, radius: float, height: float, loc: tuple[float, float, float], color: tuple[int, int, int, int]):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    mesh.visual.material = material(color)
    mesh.apply_transform(translation_matrix(loc))
    mesh.metadata["name"] = name
    return mesh


def sphere(name: str, radius: float, loc: tuple[float, float, float], color: tuple[int, int, int, int]):
    mesh = trimesh.creation.icosphere(subdivisions=2, radius=radius)
    mesh.visual.material = material(color)
    mesh.apply_transform(translation_matrix(loc))
    mesh.metadata["name"] = name
    return mesh


def scene_from_meshes(meshes: list[trimesh.Trimesh]) -> trimesh.Scene:
    scene = trimesh.Scene()
    for mesh in meshes:
        scene.add_geometry(mesh, geom_name=mesh.metadata.get("name", "mesh"))
    return scene


def workshop_robot() -> trimesh.Scene:
    meshes = [
        box("workshop_floor", (9, 0.12, 7), (0, -0.06, 0), (56, 64, 72, 255)),
        box("bench", (2.2, 0.35, 0.8), (-2.5, 0.18, -1.8), (120, 86, 54, 255)),
        box("shelf", (0.25, 1.5, 2.2), (2.7, 0.75, 1.4), (72, 92, 110, 255)),
        cylinder("robot_body", 0.48, 0.9, (0, 0.55, 0), (62, 176, 236, 255)),
        sphere("robot_head", 0.38, (0, 1.2, 0), (238, 246, 255, 255)),
        box("left_arm", (0.25, 0.25, 0.9), (-0.6, 0.75, 0), (62, 176, 236, 255)),
        box("right_arm", (0.25, 0.25, 0.9), (0.6, 0.75, 0), (62, 176, 236, 255)),
    ]
    for i, loc in enumerate([(-1.8, 0.22, 1.8), (0.8, 0.22, 0.9), (2.3, 0.22, -1.4)]):
        meshes.append(cylinder(f"battery_{i}", 0.18, 0.4, loc, (255, 210, 74, 255)))
    return scene_from_meshes(meshes)


def island_course() -> trimesh.Scene:
    meshes = [
        cylinder("island_base", 4.4, 0.25, (0, 0, 0), (77, 152, 96, 255)),
        box("bridge_a", (2.4, 0.16, 0.55), (-1.9, 0.18, 0.8), (176, 128, 72, 255)),
        box("bridge_b", (2.8, 0.16, 0.55), (1.4, 0.18, -0.7), (176, 128, 72, 255)),
        cylinder("finish_flag_pole", 0.05, 1.2, (4.0, 0.65, 0), (240, 240, 245, 255)),
        box("finish_flag", (0.08, 0.5, 0.7), (4.15, 1.05, 0), (255, 90, 90, 255)),
    ]
    for i, loc in enumerate([(-2.2, 0.32, 1.4), (-0.4, 0.32, -1.2), (1.6, 0.32, 1.1), (3.0, 0.32, -0.4)]):
        meshes.append(cylinder(f"coin_{i}", 0.16, 0.06, loc, (255, 207, 52, 255)))
    return scene_from_meshes(meshes)


def space_hangar() -> trimesh.Scene:
    meshes = [
        box("hangar_floor", (9, 0.12, 7), (0, -0.06, 0), (42, 48, 62, 255)),
        box("rear_wall", (9, 2.4, 0.18), (0, 1.15, -3.4), (50, 58, 80, 255)),
        box("left_crate", (1.2, 0.6, 1.0), (-2.7, 0.3, 1.5), (94, 112, 132, 255)),
        cylinder("rover_body", 0.5, 0.55, (-0.1, 0.45, 0.1), (120, 190, 255, 255)),
        sphere("fusion_core", 0.28, (0.2, 0.45, 0.2), (102, 255, 209, 255)),
        cylinder("launch_pad", 0.65, 0.08, (3.6, 0.05, 2.8), (88, 255, 132, 255)),
    ]
    rover = meshes[3]
    rover.apply_transform(rotation_matrix(math.radians(90), np.array([1, 0, 0]), point=[-0.1, 0.45, 0.1]))
    return scene_from_meshes(meshes)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    specs = {
        "workshop_robot.glb": workshop_robot(),
        "island_course.glb": island_course(),
        "space_hangar.glb": space_hangar(),
    }
    inventory = []
    for filename, scene in specs.items():
        path = ASSETS / filename
        scene.export(path)
        inventory.append({
            "file": str(path),
            "bytes": path.stat().st_size,
            "geometry_count": len(scene.geometry),
            "bounds": scene.bounds.tolist(),
        })
    out = {"generator": "trimesh on HomePC", "assets": inventory}
    (ROOT / "outputs" / "glb_asset_inventory.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
