extends SceneTree

const SCENE_PATH := "res://scenes/p7_minimal_playable_scene.tscn"
const PLAYER_HALF_EXTENTS := Vector3(0.25, 0.35, 0.25)
const CONTACT_EPSILON := 0.02
const PATHS := [
	{
		"id": "approach_chair",
		"target": "triposr_p4_chair_mesh_Collider",
		"start": Vector3(-3.0, 0.35, 1.65),
		"delta": Vector3(0.0, 0.0, -0.22),
		"steps": 14
	},
	{
		"id": "approach_block",
		"target": "triposr_p5_synthetic_block_Collider",
		"start": Vector3(0.0, 0.35, 1.8),
		"delta": Vector3(0.0, 0.0, -0.24),
		"steps": 14
	},
	{
		"id": "approach_tower",
		"target": "triposr_p5_synthetic_tower_Collider",
		"start": Vector3(2.15, 0.35, 1.65),
		"delta": Vector3(0.0, 0.0, -0.22),
		"steps": 14
	}
]

func _initialize() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://outputs"))
	var packed := ResourceLoader.load(SCENE_PATH)
	var report := {
		"scene_path": SCENE_PATH,
		"scene_loaded": packed != null,
		"simulation_mode": "deterministic AABB proxy simulation over saved Godot collision proxies",
		"headless_physics_note": "The check uses saved BoxShape3D proxy bounds and deterministic swept AABB movement. It does not claim real player feel or full physics-controller behavior.",
		"paths": [],
		"summary": {}
	}
	if packed == null or not packed is PackedScene:
		report["summary"] = {"pass": false, "error": "scene did not load as PackedScene"}
		_write_report(report, 1)
		return
	var root: Node = (packed as PackedScene).instantiate()
	var colliders := _collect_colliders(root)
	report["colliders"] = colliders
	var failures := 0
	for path_spec in PATHS:
		var row := _simulate_path(path_spec, colliders)
		report["paths"].append(row)
		if not row.get("pass", false):
			failures += 1
	var blocked_count := 0
	var contact_count := 0
	for row in report["paths"]:
		if row.get("blocked", false):
			blocked_count += 1
		if row.get("contact_detected", false):
			contact_count += 1
	report["summary"] = {
		"path_count": report["paths"].size(),
		"blocked_count": blocked_count,
		"contact_count": contact_count,
		"pass": failures == 0 and blocked_count == PATHS.size() and contact_count == PATHS.size()
	}
	root.free()
	_write_report(report, 0 if report["summary"]["pass"] else 2)

func _collect_colliders(root: Node) -> Dictionary:
	var out := {}
	_walk_colliders(root, out)
	return out

func _walk_colliders(node: Node, out: Dictionary) -> void:
	if node is StaticBody3D and String(node.name).ends_with("_Collider"):
		var shape_node := node.get_node_or_null("CollisionProxy")
		if shape_node is CollisionShape3D and shape_node.shape is BoxShape3D:
			var box_shape := shape_node.shape as BoxShape3D
			var center := (node as StaticBody3D).position
			var size := box_shape.size
			out[node.name] = {
				"center": _vec(center),
				"size": _vec(size),
				"aabb": _aabb(AABB(center - size * 0.5, size))
			}
	for child in node.get_children():
		_walk_colliders(child, out)

func _simulate_path(path_spec: Dictionary, colliders: Dictionary) -> Dictionary:
	var target_name: String = path_spec["target"]
	var row := {
		"id": path_spec["id"],
		"target": target_name,
		"target_found": colliders.has(target_name),
		"steps": [],
		"contact_detected": false,
		"blocked": false,
		"final_position": null,
		"pass": false,
		"errors": []
	}
	if not colliders.has(target_name):
		row["errors"].append("target collider missing")
		return row
	var target_aabb := _dict_to_aabb(colliders[target_name]["aabb"])
	var position: Vector3 = path_spec["start"]
	var delta: Vector3 = path_spec["delta"]
	var previous_distance := INF
	for index in range(int(path_spec["steps"])):
		var next_position := position + delta
		var next_aabb := _player_aabb(next_position)
		var distance := _aabb_distance(next_aabb, target_aabb)
		var contact := next_aabb.intersects(target_aabb) or distance <= CONTACT_EPSILON
		var step := {
			"step": index + 1,
			"candidate_position": _vec(next_position),
			"distance_to_target": distance,
			"contact": contact,
			"moved": false
		}
		if contact:
			row["contact_detected"] = true
			row["blocked"] = true
			step["blocked_here"] = true
			row["steps"].append(step)
			break
		position = next_position
		step["moved"] = true
		step["distance_nonincreasing"] = distance <= previous_distance + 0.0001
		previous_distance = distance
		row["steps"].append(step)
	row["final_position"] = _vec(position)
	row["pass"] = row["target_found"] and row["contact_detected"] and row["blocked"] and row["steps"].size() > 1
	return row

func _player_aabb(center: Vector3) -> AABB:
	return AABB(center - PLAYER_HALF_EXTENTS, PLAYER_HALF_EXTENTS * 2.0)

func _aabb_distance(a: AABB, b: AABB) -> float:
	var a_max := a.position + a.size
	var b_max := b.position + b.size
	var dx: float = max(max(b.position.x - a_max.x, a.position.x - b_max.x), 0.0)
	var dy: float = max(max(b.position.y - a_max.y, a.position.y - b_max.y), 0.0)
	var dz: float = max(max(b.position.z - a_max.z, a.position.z - b_max.z), 0.0)
	return sqrt(dx * dx + dy * dy + dz * dz)

func _dict_to_aabb(data: Dictionary) -> AABB:
	var pos: Array = data["position"]
	var size: Array = data["size"]
	return AABB(Vector3(pos[0], pos[1], pos[2]), Vector3(size[0], size[1], size[2]))

func _write_report(report: Dictionary, exit_code: int) -> void:
	var file := FileAccess.open("res://outputs/p8_movement_collision_report.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify(report))
	quit(exit_code)

func _vec(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

func _aabb(box: AABB) -> Dictionary:
	return {
		"position": _vec(box.position),
		"size": _vec(box.size)
	}
