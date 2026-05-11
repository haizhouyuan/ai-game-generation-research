extends SceneTree

const SOURCE_SCENE := "res://scenes/p7_minimal_playable_scene.tscn"
const P10_SCENE := "res://scenes/p10_objective_scene.tscn"
const TARGETS := [
	{
		"id": "chair",
		"collider": "triposr_p4_chair_mesh_Collider",
		"checkpoint": "Checkpoint_Chair"
	},
	{
		"id": "block",
		"collider": "triposr_p5_synthetic_block_Collider",
		"checkpoint": "Checkpoint_Block"
	},
	{
		"id": "tower",
		"collider": "triposr_p5_synthetic_tower_Collider",
		"checkpoint": "Checkpoint_Tower"
	}
]
const FINISH_NAME := "Finish_Area"
const FINISH_CENTER := Vector3(3.25, 0.65, 1.35)
const PLAYER_Y := 0.65

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://outputs"))
	var report := {
		"source_scene": SOURCE_SCENE,
		"p10_scene": P10_SCENE,
		"simulation_mode": "explicit ObjectiveRoot with Area3D checkpoint/finish nodes plus headless shape-readback objective loop",
		"no_proxy_note": "Godot run is local/offline on HomePC with proxy variables unset by the caller.",
		"scene_build": {},
		"scene_readback": {},
		"objective_loop": {},
		"summary": {}
	}
	var build := _build_scene_with_objectives()
	report["scene_build"] = build
	if not build.get("pass", false):
		report["summary"] = {"pass": false, "stage": "build"}
		_write_report(report, 1)
		return
	var readback := _readback_objective_scene()
	report["scene_readback"] = readback
	if not readback.get("pass", false):
		report["summary"] = {"pass": false, "stage": "readback"}
		_write_report(report, 1)
		return
	var loop := await _simulate_objective_loop(readback)
	report["objective_loop"] = loop
	report["summary"] = {
		"objective_nodes": readback.get("objective_node_count", 0),
		"checkpoint_nodes": readback.get("checkpoint_count", 0),
		"finish_nodes": readback.get("finish_count", 0),
		"pre_finish_locked": loop.get("pre_finish_locked", false),
		"collected_count": loop.get("collected_count", 0),
		"finish_unlocked": loop.get("finish_unlocked", false),
		"finish_reached": loop.get("finish_reached", false),
		"pass": loop.get("pass", false)
	}
	_write_report(report, 0 if report["summary"]["pass"] else 2)

func _build_scene_with_objectives() -> Dictionary:
	var row := {"source_loaded": false, "save_result": null, "checkpoint_nodes_created": 0, "finish_created": false, "pass": false, "errors": []}
	var packed := ResourceLoader.load(SOURCE_SCENE)
	if packed == null or not packed is PackedScene:
		row["errors"].append("source scene did not load")
		return row
	row["source_loaded"] = true
	var root: Node = (packed as PackedScene).instantiate()
	var objective_root := Node3D.new()
	objective_root.name = "ObjectiveRoot"
	root.add_child(objective_root)
	_set_owner_recursive(objective_root, root)

	for target in TARGETS:
		var collider := root.find_child(target["collider"], true, false)
		if collider == null or not collider is StaticBody3D:
			row["errors"].append("target collider missing: %s" % target["collider"])
			continue
		var checkpoint := _make_checkpoint_area(target, collider as StaticBody3D)
		objective_root.add_child(checkpoint)
		_set_owner_recursive(checkpoint, root)
		row["checkpoint_nodes_created"] += 1

	var finish := _make_finish_area()
	objective_root.add_child(finish)
	_set_owner_recursive(finish, root)
	row["finish_created"] = true

	var packed_out := PackedScene.new()
	var pack_result := packed_out.pack(root)
	var save_result := ResourceSaver.save(packed_out, P10_SCENE)
	row["pack_result"] = pack_result
	row["save_result"] = save_result
	row["pass"] = row["checkpoint_nodes_created"] == TARGETS.size() and row["finish_created"] and pack_result == OK and save_result == OK
	root.queue_free()
	return row

func _make_checkpoint_area(target: Dictionary, collider: StaticBody3D) -> Area3D:
	var source_shape := collider.get_node_or_null("CollisionProxy")
	var source_size := Vector3(0.6, 0.7, 0.6)
	if source_shape is CollisionShape3D and (source_shape as CollisionShape3D).shape is BoxShape3D:
		var box := (source_shape as CollisionShape3D).shape as BoxShape3D
		source_size = Vector3(min(0.72, max(0.36, box.size.x * 0.45)), min(1.0, max(0.45, box.size.y)), min(0.72, max(0.36, box.size.z * 0.45)))
	var area := Area3D.new()
	area.name = target["checkpoint"]
	area.position = Vector3(collider.position.x, PLAYER_Y, collider.position.z + 0.52)
	area.monitoring = true
	area.monitorable = true
	area.set_meta("objective_type", "checkpoint")
	area.set_meta("objective_id", target["id"])
	area.set_meta("target_collider", target["collider"])
	var shape_node := CollisionShape3D.new()
	shape_node.name = "ObjectiveShape"
	var shape := BoxShape3D.new()
	shape.size = source_size
	shape_node.shape = shape
	area.add_child(shape_node)
	return area

func _make_finish_area() -> Area3D:
	var area := Area3D.new()
	area.name = FINISH_NAME
	area.position = FINISH_CENTER
	area.monitoring = true
	area.monitorable = true
	area.set_meta("objective_type", "finish")
	area.set_meta("requires_checkpoints", TARGETS.size())
	var shape_node := CollisionShape3D.new()
	shape_node.name = "ObjectiveShape"
	var shape := SphereShape3D.new()
	shape.radius = 0.24
	shape_node.shape = shape
	area.add_child(shape_node)
	return area

func _readback_objective_scene() -> Dictionary:
	var row := {"scene_loaded": false, "objective_root_exists": false, "objective_node_count": 0, "checkpoint_count": 0, "finish_count": 0, "areas": [], "pass": false, "errors": []}
	var packed := ResourceLoader.load(P10_SCENE)
	if packed == null or not packed is PackedScene:
		row["errors"].append("P10 scene did not load")
		return row
	row["scene_loaded"] = true
	var root: Node = (packed as PackedScene).instantiate()
	var objective_root := root.find_child("ObjectiveRoot", true, false)
	row["objective_root_exists"] = objective_root != null
	if objective_root == null:
		row["errors"].append("ObjectiveRoot missing")
		root.queue_free()
		return row
	for child in objective_root.get_children():
		if child is Area3D:
			var area := child as Area3D
			var item := _area_readback(area)
			row["areas"].append(item)
			row["objective_node_count"] += 1
			if item.get("objective_type", "") == "checkpoint":
				row["checkpoint_count"] += 1
			if item.get("objective_type", "") == "finish":
				row["finish_count"] += 1
			if not item.get("pass", false):
				row["errors"].append("area readback failed: %s" % item.get("name", "unknown"))
	row["pass"] = row["scene_loaded"] and row["objective_root_exists"] and row["checkpoint_count"] == TARGETS.size() and row["finish_count"] == 1 and row["errors"].is_empty()
	root.queue_free()
	return row

func _area_readback(area: Area3D) -> Dictionary:
	var shape_node := area.get_node_or_null("ObjectiveShape")
	var shape_type: Variant = null
	var shape_size: Variant = null
	var shape_radius: Variant = null
	if shape_node is CollisionShape3D:
		var shape := (shape_node as CollisionShape3D).shape
		if shape is BoxShape3D:
			shape_type = "BoxShape3D"
			shape_size = _vec((shape as BoxShape3D).size)
		elif shape is SphereShape3D:
			shape_type = "SphereShape3D"
			shape_radius = (shape as SphereShape3D).radius
	return {
		"name": area.name,
		"objective_type": area.get_meta("objective_type", ""),
		"objective_id": area.get_meta("objective_id", ""),
		"target_collider": area.get_meta("target_collider", ""),
		"position": _vec(area.position),
		"monitoring": area.monitoring,
		"monitorable": area.monitorable,
		"shape_node_exists": shape_node != null,
		"shape_type": shape_type,
		"shape_size": shape_size,
		"shape_radius": shape_radius,
		"pass": shape_node != null and shape_type != null and area.has_meta("objective_type")
	}

func _simulate_objective_loop(readback: Dictionary) -> Dictionary:
	var loop := {"pre_finish_locked": false, "checkpoint_steps": [], "collected": [], "collected_count": 0, "finish_unlocked": false, "finish_reached": false, "pass": false, "errors": []}
	var packed := ResourceLoader.load(P10_SCENE)
	if packed == null or not packed is PackedScene:
		loop["errors"].append("P10 scene did not load for simulation")
		return loop
	var root: Node = (packed as PackedScene).instantiate()
	get_root().add_child(root)
	await physics_frame
	var player := root.find_child("Player", true, false)
	if not player is CharacterBody3D:
		loop["errors"].append("Player CharacterBody3D missing")
		root.queue_free()
		return loop
	var character := player as CharacterBody3D
	var finish := root.find_child(FINISH_NAME, true, false)
	if not finish is Area3D:
		loop["errors"].append("finish Area3D missing")
		root.queue_free()
		return loop

	character.global_position = (finish as Area3D).global_position
	await physics_frame
	loop["pre_finish_locked"] = not _finish_unlocked(loop["collected"])
	for target in TARGETS:
		var area := root.find_child(target["checkpoint"], true, false)
		if not area is Area3D:
			loop["errors"].append("checkpoint area missing: %s" % target["checkpoint"])
			continue
		character.global_position = (area as Area3D).global_position
		await physics_frame
		var entered := _point_inside_area(character.global_position, area as Area3D)
		var step := {"checkpoint": target["checkpoint"], "player_position": _vec(character.global_position), "entered": entered}
		if entered:
			loop["collected"].append(target["id"])
		else:
			loop["errors"].append("player did not enter checkpoint: %s" % target["checkpoint"])
		loop["checkpoint_steps"].append(step)
	loop["collected_count"] = loop["collected"].size()
	loop["finish_unlocked"] = _finish_unlocked(loop["collected"])
	character.global_position = (finish as Area3D).global_position
	await physics_frame
	loop["finish_reached"] = loop["finish_unlocked"] and _point_inside_area(character.global_position, finish as Area3D)
	loop["pass"] = loop["pre_finish_locked"] and loop["collected_count"] == TARGETS.size() and loop["finish_unlocked"] and loop["finish_reached"] and loop["errors"].is_empty()
	root.queue_free()
	return loop

func _finish_unlocked(collected: Array) -> bool:
	return collected.size() == TARGETS.size()

func _point_inside_area(point: Vector3, area: Area3D) -> bool:
	var shape_node := area.get_node_or_null("ObjectiveShape")
	if not shape_node is CollisionShape3D:
		return false
	var local := point - area.global_position
	var shape := (shape_node as CollisionShape3D).shape
	if shape is BoxShape3D:
		var half := (shape as BoxShape3D).size * 0.5
		return abs(local.x) <= half.x and abs(local.y) <= half.y and abs(local.z) <= half.z
	if shape is SphereShape3D:
		return local.length() <= (shape as SphereShape3D).radius
	return false

func _write_report(report: Dictionary, exit_code: int) -> void:
	var file := FileAccess.open("res://outputs/p10_objective_scene_nodes_report.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify(report))
	quit(exit_code)

func _set_owner_recursive(node: Node, owner_node: Node) -> void:
	node.owner = owner_node
	for child in node.get_children():
		_set_owner_recursive(child, owner_node)

func _vec(v: Vector3) -> Array:
	return [v.x, v.y, v.z]
