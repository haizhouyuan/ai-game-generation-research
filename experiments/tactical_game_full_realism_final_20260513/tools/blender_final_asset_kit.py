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
        raise SystemExit("usage: blender --background --python blender_final_asset_kit.py -- OUT_DIR")
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
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(block):
            block.remove(item)


def mat(name: str, color: tuple[float, float, float, float], roughness: float, metalness: float):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metalness
    return m


def mats() -> dict:
    return {
        "cloth": mat("olive_ripstop_cloth", (0.10, 0.15, 0.11, 1), 0.86, 0.0),
        "enemy_cloth": mat("charcoal_enemy_cloth", (0.12, 0.13, 0.16, 1), 0.84, 0.0),
        "armor": mat("ceramic_plate_carrier", (0.17, 0.22, 0.24, 1), 0.58, 0.12),
        "enemy_armor": mat("maroon_enemy_plate_carrier", (0.36, 0.13, 0.16, 1), 0.60, 0.10),
        "webbing": mat("black_nylon_webbing", (0.025, 0.030, 0.030, 1), 0.90, 0.0),
        "skin": mat("muted_skin_visible_face", (0.56, 0.38, 0.27, 1), 0.72, 0.0),
        "visor": mat("smoked_blue_visor_glass", (0.04, 0.12, 0.18, 0.76), 0.08, 0.0),
        "steel": mat("scratched_dark_steel", (0.05, 0.055, 0.06, 1), 0.38, 0.78),
        "paint": mat("worn_painted_metal", (0.30, 0.34, 0.36, 1), 0.66, 0.22),
        "wood": mat("sealed_rough_wood", (0.42, 0.24, 0.10, 1), 0.72, 0.02),
        "canvas": mat("tan_canvas_fabric", (0.46, 0.38, 0.24, 1), 0.90, 0.0),
        "red": mat("medical_red_marking", (0.75, 0.06, 0.08, 1), 0.46, 0.04),
        "glass": mat("revive_glowing_glass", (0.32, 0.12, 0.72, 0.70), 0.12, 0.0),
        "brass": mat("brass_cartridge_metal", (0.95, 0.62, 0.18, 1), 0.28, 1.0),
        "bark": mat("layered_tree_bark", (0.26, 0.14, 0.07, 1), 0.92, 0.0),
        "leaf": mat("mixed_leaf_clusters", (0.08, 0.32, 0.14, 1), 0.96, 0.0),
        "rock": mat("granite_rough_rock", (0.36, 0.38, 0.40, 1), 0.94, 0.04),
        "concrete": mat("weathered_cast_concrete", (0.43, 0.45, 0.43, 1), 0.91, 0.0),
        "asphalt": mat("patched_dark_asphalt", (0.045, 0.048, 0.045, 1), 0.96, 0.0),
        "warning": mat("faded_yellow_warning_paint", (0.88, 0.62, 0.10, 1), 0.68, 0.08),
    }


def cube(name: str, dims: tuple[float, float, float], loc: tuple[float, float, float], material, bevel: float = 0.025, rot: tuple[float, float, float] = (0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new("beveled_edges", "BEVEL")
        b.width = bevel
        b.segments = 3
        b.affect = "EDGES"
    o.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return o


def cyl(name: str, radius: float, depth: float, loc: tuple[float, float, float], material, vertices: int = 28, rot: tuple[float, float, float] = (0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    o.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return o


def sphere(name: str, radius: float, loc: tuple[float, float, float], material, scale: tuple[float, float, float] = (1, 1, 1), segments: int = 24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=max(8, segments // 2), radius=radius, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(material)
    o.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return o


def anchor(name: str, loc: tuple[float, float, float]):
    o = bpy.data.objects.new(name, None)
    o.empty_display_type = "PLAIN_AXES"
    o.empty_display_size = 0.16
    o.location = loc
    bpy.context.collection.objects.link(o)
    return o


def capsule_like(parts: list, name: str, a: tuple[float, float, float], b: tuple[float, float, float], radius: float, material):
    va, vb = Vector(a), Vector(b)
    mid = (va + vb) * 0.5
    length = (vb - va).length
    o = cyl(name, radius, length, tuple(mid), material, 24)
    o.rotation_euler = (vb - va).to_track_quat("Z", "Y").to_euler()
    parts.append(o)
    parts.append(sphere(name + "_cap_a", radius, a, material, (1, 1, 1), 16))
    parts.append(sphere(name + "_cap_b", radius, b, material, (1, 1, 1), 16))


def build_character(kind: str, m: dict) -> tuple[list, list[str]]:
    parts: list = []
    enemy = kind == "enemy"
    cloth = m["enemy_cloth"] if enemy else m["cloth"]
    armor = m["enemy_armor"] if enemy else m["armor"]
    accent = m["red"] if enemy else m["brass"]
    parts.append(cube("anatomical_torso_underlayer", (0.58, 0.88, 0.34), (0, 1.12, 0), cloth, 0.08))
    parts.append(cube("front_plate_carrier_with_beveled_ceramic_panel", (0.68, 0.72, 0.16), (0, 1.13, 0.23), armor, 0.055))
    parts.append(cube("rear_plate_carrier_panel", (0.60, 0.66, 0.16), (0, 1.15, -0.24), armor, 0.055))
    parts.append(cube("hydration_backpack_and_radio_pack", (0.46, 0.72, 0.22), (0, 1.16, -0.46), m["canvas"], 0.06))
    for x in (-0.23, 0, 0.23):
        parts.append(cube("front_magazine_pouch_" + str(x), (0.15, 0.26, 0.10), (x, 0.82, 0.36), m["webbing"], 0.025))
        parts.append(cube("pouch_pull_tab_" + str(x), (0.12, 0.035, 0.035), (x, 0.99, 0.42), accent, 0.008))
    for x in (-0.39, 0.39):
        parts.append(cube("shoulder_armor_pad_" + str(x), (0.24, 0.16, 0.20), (x, 1.46, 0.02), armor, 0.045, (0, 0, -0.25 if x < 0 else 0.25)))
        capsule_like(parts, "upper_arm_cloth_" + str(x), (x, 1.34, 0.02), (x * 1.12, 0.96, 0.18), 0.08, cloth)
        capsule_like(parts, "forearm_glove_sleeve_" + str(x), (x * 1.12, 0.96, 0.18), (x * 0.55, 0.79, 0.48), 0.065, cloth)
        parts.append(sphere("black_tactical_glove_" + str(x), 0.085, (x * 0.55, 0.79, 0.52), m["webbing"], (1.15, 0.76, 1.0), 16))
    for x in (-0.18, 0.18):
        capsule_like(parts, "upper_leg_fatigues_" + str(x), (x, 0.76, 0.01), (x, 0.34, 0.08), 0.105, cloth)
        capsule_like(parts, "lower_leg_boot_gaiter_" + str(x), (x, 0.34, 0.08), (x, 0.08, 0.12), 0.095, cloth)
        parts.append(cube("hard_knee_pad_" + str(x), (0.22, 0.13, 0.08), (x, 0.47, 0.22), armor, 0.035))
        parts.append(cube("boot_with_sculpted_sole_" + str(x), (0.25, 0.12, 0.38), (x, 0.03, 0.15), m["webbing"], 0.04))
    parts.append(cyl("neck_sleeve", 0.10, 0.16, (0, 1.56, 0.02), cloth, 20))
    parts.append(sphere("human_face_visible_under_helmet", 0.22, (0, 1.74, 0.04), m["skin"], (0.92, 1.08, 0.92), 24))
    parts.append(sphere("ballistic_helmet_shell", 0.27, (0, 1.85, 0.01), armor, (1.04, 0.70, 1.02), 28))
    parts.append(cube("smoked_wraparound_visor", (0.36, 0.08, 0.055), (0, 1.75, 0.24), m["visor"], 0.025))
    parts.append(cube("helmet_comms_left", (0.085, 0.14, 0.07), (-0.25, 1.78, 0.01), m["webbing"], 0.025))
    parts.append(cube("helmet_comms_right", (0.085, 0.14, 0.07), (0.25, 1.78, 0.01), m["webbing"], 0.025))
    parts.append(cyl("boom_microphone", 0.012, 0.30, (-0.20, 1.70, 0.19), m["webbing"], 10, (math.radians(78), 0, math.radians(25))))
    anchor("WeaponMount", (0, 1.22, 0.74))
    return parts, ["tactical human silhouette", "helmet", "plate carrier", "backpack", "gloves", "pads"]


def build_loot(kind: str, m: dict) -> tuple[list, list[str]]:
    parts: list = []
    if kind == "ammo":
        parts.append(cube("steel_ammo_can_with_latched_lid", (0.82, 0.36, 0.52), (0, 0.18, 0), m["paint"], 0.055))
        parts.append(cube("black_lid_gasket", (0.74, 0.055, 0.46), (0, 0.39, 0), m["webbing"], 0.018))
        for i in range(7):
            parts.append(cyl("visible_brass_round_" + str(i), 0.026, 0.34, (-0.30 + i * 0.10, 0.54, 0.08), m["brass"], 18, (math.pi / 2, 0, 0)))
    elif kind in {"firstaid", "medkit", "bandage"}:
        s = 1.18 if kind == "medkit" else 0.88
        parts.append(cube(kind + "_fabric_medical_case", (0.72 * s, 0.34 * s, 0.50 * s), (0, 0.20 * s, 0), m["canvas"], 0.065))
        parts.append(cube("red_cross_horizontal", (0.42 * s, 0.06 * s, 0.055), (0, 0.42 * s, 0.28 * s), m["red"], 0.012))
        parts.append(cube("red_cross_vertical", (0.09 * s, 0.06 * s, 0.30 * s), (0, 0.42 * s, 0.28 * s), m["red"], 0.012))
        parts.append(cube("black_zipper_and_handle", (0.48 * s, 0.05 * s, 0.08 * s), (0, 0.43 * s, -0.05 * s), m["webbing"], 0.014))
        if kind == "bandage":
            for x in (-0.18, 0.18):
                parts.append(cyl("rolled_bandage_" + str(x), 0.12, 0.30, (x, 0.50, 0.02), m["canvas"], 24, (math.pi / 2, 0, 0)))
    elif kind == "revive":
        parts.append(cube("sealed_revive_device_base", (0.56, 0.18, 0.56), (0, 0.09, 0), m["steel"], 0.04))
        parts.append(cyl("glass_energy_capsule", 0.20, 0.55, (0, 0.46, 0), m["glass"], 32))
        parts.append(sphere("faceted_purple_core", 0.19, (0, 0.48, 0), m["glass"], (1, 1.22, 1), 16))
    elif kind == "vest":
        parts.append(cube("pickup_plate_carrier_body", (0.62, 0.74, 0.18), (0, 0.42, 0), m["armor"], 0.055))
        for x in (-0.20, 0, 0.20):
            parts.append(cube("vest_pickup_pouch_" + str(x), (0.15, 0.22, 0.09), (x, 0.34, 0.16), m["webbing"], 0.025))
    elif kind == "helmet":
        parts.append(sphere("pickup_ballistic_helmet_shell", 0.34, (0, 0.36, 0), m["armor"], (1.05, 0.62, 1), 28))
        parts.append(cube("pickup_visor", (0.44, 0.08, 0.10), (0, 0.36, 0.32), m["visor"], 0.026))
        parts.append(cube("helmet_rail_left", (0.11, 0.08, 0.12), (-0.32, 0.38, 0.02), m["webbing"], 0.02))
        parts.append(cube("helmet_rail_right", (0.11, 0.08, 0.12), (0.32, 0.38, 0.02), m["webbing"], 0.02))
    return parts, [kind, "readable pickup prop", "PBR-style material factors"]


def build_prop(kind: str, m: dict) -> tuple[list, list[str]]:
    parts: list = []
    if kind == "crate":
        parts.append(cube("rough_military_storage_crate", (1.20, 0.78, 0.86), (0, 0.39, 0), m["wood"], 0.055))
        for z in (-0.46, 0.46):
            parts.append(cube("steel_crate_band_z_" + str(z), (1.28, 0.10, 0.06), (0, 0.72, z), m["steel"], 0.012))
            parts.append(cube("steel_crate_lower_band_z_" + str(z), (1.28, 0.10, 0.06), (0, 0.18, z), m["steel"], 0.012))
        for x in (-0.54, 0.54):
            parts.append(cube("crate_side_handle_" + str(x), (0.08, 0.24, 0.32), (x, 0.45, 0), m["steel"], 0.02))
    elif kind == "building_detail":
        parts.append(cube("wall_mounted_ac_unit", (1.04, 0.52, 0.38), (0, 0.96, 0), m["paint"], 0.035))
        for i in range(5):
            parts.append(cube("ac_front_louver_" + str(i), (0.84, 0.035, 0.055), (0, 0.80 + i * 0.07, 0.22), m["steel"], 0.006))
        parts.append(cyl("vertical_drain_pipe", 0.035, 1.90, (-0.72, 0.95, 0.10), m["steel"], 14))
        parts.append(cube("utility_junction_box", (0.42, 0.48, 0.16), (0.66, 0.70, 0.05), m["paint"], 0.025))
        parts.append(cube("warning_label_plate", (0.32, 0.055, 0.03), (0.66, 0.71, 0.15), m["brass"], 0.006))
    elif kind == "tree":
        parts.append(cyl("gnarled_main_trunk", 0.24, 2.3, (0, 1.15, 0), m["bark"], 16))
        for i, angle in enumerate((0.2, 2.1, 3.9, 5.2)):
            x, z = math.cos(angle) * 0.72, math.sin(angle) * 0.72
            branch = cyl("branch_" + str(i), 0.07, 1.25, (x * 0.48, 1.76 + 0.08 * i, z * 0.48), m["bark"], 12, (math.radians(62), 0, -angle))
            parts.append(branch)
            parts.append(sphere("leaf_cluster_" + str(i), 0.52, (x, 2.10 + 0.08 * i, z), m["leaf"], (1.35, 0.90, 1.25), 16))
        parts.append(sphere("top_leaf_cluster", 0.72, (0.08, 2.50, -0.05), m["leaf"], (1.18, 0.92, 1.10), 16))
    elif kind == "rock_cluster":
        for i, (x, z, s) in enumerate(((-0.32, 0.02, 0.55), (0.20, 0.12, 0.42), (0.42, -0.18, 0.34), (-0.05, -0.34, 0.28))):
            parts.append(sphere("angular_granite_rock_" + str(i), s, (x, s * 0.45, z), m["rock"], (1.3, 0.55, 0.9), 12))
    elif kind == "container":
        parts.append(cube("corrugated_shipping_container_body", (2.25, 1.08, 1.02), (0, 0.54, 0), m["paint"], 0.025))
        for x in [i * 0.18 - 1.08 for i in range(13)]:
            parts.append(cube("container_corrugation_rib_" + str(round(x, 2)), (0.035, 1.12, 1.08), (x, 0.56, 0), m["steel"], 0.004))
        for x in (-1.05, 1.05):
            parts.append(cube("container_door_leaf_" + str(x), (0.08, 1.00, 0.48), (x, 0.55, 0.52), m["paint"], 0.01))
            parts.append(cyl("container_locking_bar_" + str(x), 0.018, 0.96, (x, 0.55, 0.80), m["steel"], 10))
        parts.append(cube("container_faded_warning_stripe", (1.55, 0.08, 0.035), (0, 0.92, 0.55), m["warning"], 0.004))
    elif kind == "ladder_stair":
        for i in range(6):
            y = 0.12 + i * 0.16
            z = i * 0.18
            parts.append(cube("industrial_stair_tread_" + str(i), (0.90, 0.06, 0.28), (0, y, z), m["steel"], 0.012))
            parts.append(cube("anti_slip_yellow_edge_" + str(i), (0.84, 0.025, 0.035), (0, y + 0.04, z + 0.14), m["warning"], 0.004))
        for x in (-0.52, 0.52):
            parts.append(cyl("stair_handrail_" + str(x), 0.028, 1.35, (x, 0.70, 0.48), m["steel"], 12, (math.radians(40), 0, 0)))
            parts.append(cyl("ladder_vertical_rail_" + str(x), 0.024, 1.35, (x, 0.78, -0.38), m["steel"], 12))
        for i in range(7):
            parts.append(cyl("ladder_rung_" + str(i), 0.018, 1.04, (0, 0.14 + i * 0.17, -0.38), m["steel"], 10, (0, math.radians(90), 0)))
    elif kind == "interior_furniture":
        parts.append(cube("workbench_scratched_tabletop", (1.45, 0.12, 0.58), (0, 0.78, 0), m["wood"], 0.035))
        for x in (-0.58, 0.58):
            for z in (-0.20, 0.20):
                parts.append(cube("workbench_metal_leg_" + str(x) + "_" + str(z), (0.07, 0.72, 0.07), (x, 0.38, z), m["steel"], 0.012))
        parts.append(cube("metal_storage_cabinet", (0.72, 1.10, 0.36), (-0.62, 0.55, -0.62), m["paint"], 0.035))
        for y in (0.35, 0.66, 0.96):
            parts.append(cube("cabinet_shelf_line_" + str(y), (0.66, 0.035, 0.04), (-0.62, y, -0.42), m["steel"], 0.004))
        parts.append(cube("open_wall_shelf", (1.15, 0.08, 0.28), (0.58, 1.08, -0.55), m["wood"], 0.02))
        parts.append(cube("fluorescent_interior_light_bar", (1.10, 0.05, 0.05), (0.22, 1.55, 0.05), m["warning"], 0.01))
    elif kind == "ground_wall_fence":
        parts.append(cube("asphalt_road_patch_with_beveled_edge", (2.25, 0.05, 1.20), (0, 0.025, 0), m["asphalt"], 0.008))
        for x in (-0.55, 0.10, 0.74):
            parts.append(cube("worn_road_marking_" + str(x), (0.38, 0.012, 0.05), (x, 0.062, 0.02), m["warning"], 0.002))
        parts.append(cube("cast_concrete_wall_segment", (2.10, 0.80, 0.16), (0, 0.45, -0.70), m["concrete"], 0.025))
        for x in (-0.82, -0.36, 0.18, 0.72):
            parts.append(cyl("chainlink_fence_post_" + str(x), 0.025, 0.95, (x, 0.55, 0.58), m["steel"], 10))
        for y in (0.24, 0.52, 0.82):
            parts.append(cyl("fence_horizontal_wire_" + str(y), 0.010, 1.70, (-0.05, y, 0.58), m["steel"], 8, (0, math.radians(90), 0)))
        parts.append(cube("sliding_gate_warning_plate", (0.46, 0.22, 0.035), (0.55, 0.55, 0.62), m["warning"], 0.006))
    return parts, [kind, "environment prop", "beveled materialized geometry"]


ASSETS = {
    "character_player_final": lambda m: build_character("player", m),
    "character_enemy_final": lambda m: build_character("enemy", m),
    "loot_ammo_final": lambda m: build_loot("ammo", m),
    "loot_bandage_final": lambda m: build_loot("bandage", m),
    "loot_firstaid_final": lambda m: build_loot("firstaid", m),
    "loot_medkit_final": lambda m: build_loot("medkit", m),
    "loot_revive_final": lambda m: build_loot("revive", m),
    "loot_vest_final": lambda m: build_loot("vest", m),
    "loot_helmet_final": lambda m: build_loot("helmet", m),
    "prop_crate_final": lambda m: build_prop("crate", m),
    "prop_container_final": lambda m: build_prop("container", m),
    "prop_ladder_stair_final": lambda m: build_prop("ladder_stair", m),
    "prop_interior_furniture_final": lambda m: build_prop("interior_furniture", m),
    "prop_building_detail_final": lambda m: build_prop("building_detail", m),
    "prop_ground_wall_fence_final": lambda m: build_prop("ground_wall_fence", m),
    "prop_tree_final": lambda m: build_prop("tree", m),
    "prop_rock_cluster_final": lambda m: build_prop("rock_cluster", m),
}


def setup_render() -> None:
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.render.resolution_x = 1100
    bpy.context.scene.render.resolution_y = 820
    bpy.ops.object.light_add(type="AREA", location=(-3.0, -4.0, 4.8))
    key = bpy.context.object
    key.name = "large_softbox_key"
    key.data.energy = 520
    key.data.size = 4.2
    bpy.ops.object.light_add(type="POINT", location=(2.6, 2.4, 2.8))
    rim = bpy.context.object
    rim.name = "cool_rim_light"
    rim.data.energy = 85
    rim.data.color = (0.55, 0.68, 1.0)
    bpy.ops.object.camera_add(location=(3.2, -4.3, 2.25), rotation=(math.radians(64), 0, math.radians(38)))
    bpy.context.scene.camera = bpy.context.object


def bbox(parts: list) -> dict:
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
    report = {"pipeline": "Blender final full-realism tactical asset kit", "assets": []}
    for name, builder in ASSETS.items():
        clean_scene()
        material_set = mats()
        parts, notes = builder(material_set)
        setup_render()
        preview = out_dir / f"{name}_preview.png"
        glb = out_dir / f"{name}.glb"
        bpy.context.scene.render.filepath = str(preview)
        bpy.ops.render.render(write_still=True)
        bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", export_apply=True, export_materials="EXPORT")
        report["assets"].append(
            {
                "name": name,
                "glb": str(glb),
                "preview": str(preview),
                "sha256": sha256(glb),
                "preview_sha256": sha256(preview),
                "mesh_object_count": sum(1 for obj in parts if obj.type == "MESH"),
                "bbox": bbox(parts),
                "material_names": sorted(mat.name for mat in bpy.data.materials),
                "notes": notes,
            }
        )
    (out_dir / "final_asset_kit_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
