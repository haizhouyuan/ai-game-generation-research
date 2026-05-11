extends SceneTree

const TARGET_SIZE := 1.8
const ASSETS := [
	{
		"id": "triposr_p4_chair_mesh",
		"path": "res://assets/triposr_p4_chair_mesh.glb",
		"position": Vector3(-2.2, 0.0, 0.0)
	},
	{
		"id": "triposr_p5_synthetic_block",
		"path": "res://assets/triposr_p5_synthetic_block.glb",
		"position": Vector3(0.0, 0.0, 0.0)
	},
	{
		"id": "triposr_p5_synthetic_tower",
		"path": "res://assets/triposr_p5_synthetic_tower.glb",
		"position": Vector3(2.2, 0.0, 0.0)
	},
]

func _initialize() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://outputs"))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://scenes"))

	var root: Node3D = Node3D.new()
	root.name = "P7MinimalPlayableScene"

	var ground: StaticBody3D = _make_ground()
	root.add_child(ground)
	_set_owner_recursive(ground, root)

	var asset_rows: Array = []
	var asset_nodes: Array[Node3D] = []
	var failures := 0
	for spec in ASSETS:
		var row: Dictionary = _add_asset(root, spec)
		asset_rows.append(row)
		if row.get("pass", false):
			asset_nodes.append(row["_node"])
			row.erase("_node")
		else:
			failures += 1

	var player: CharacterBody3D = _make_player()
	root.add_child(player)
	_set_owner_recursive(player, root)

	var camera: Camera3D = Camera3D.new()
	camera.name = "PlayerCamera"
	camera.position = Vector3(0.0, 3.4, 6.2)
	camera.rotation_degrees = Vector3(-25.0, 0.0, 0.0)
	root.add_child(camera)
	camera.owner = root

	var light: DirectionalLight3D = DirectionalLight3D.new()
	light.name = "KeyLight"
	light.rotation_degrees = Vector3(-45.0, 30.0, 0.0)
	root.add_child(light)
	light.owner = root

	var runtime_checks: Dictionary = _runtime_checks(player, asset_rows)
	if not runtime_checks.get("pass", false):
		failures += 1

	var packed: PackedScene = PackedScene.new()
	var pack_result: Error = packed.pack(root)
	var scene_path := "res://scenes/p7_minimal_playable_scene.tscn"
	var save_result: Error = ResourceSaver.save(packed, scene_path)
	var report := {
		"scene_path": scene_path,
		"pack_result": pack_result,
		"save_result": save_result,
		"assets": asset_rows,
		"player": {
			"exists": player != null,
			"has_collision": player.get_node_or_null("PlayerCollision") != null,
			"position": _vec(player.position)
		},
		"camera": {
			"exists": camera != null,
			"position": _vec(camera.position)
		},
		"light": {
			"exists": light != null
		},
		"runtime_checks": runtime_checks,
		"headless_render_note": "P7 uses headless Godot runtime structural checks. No screenshot was produced because the available command path is headless and this batch avoids extra display/GPU setup."
	}
	var file := FileAccess.open("res://outputs/p7_runtime_report.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify(report))
	root.free()
	quit(failures)

func _add_asset(root: Node3D, spec: Dictionary) -> Dictionary:
	var row := {
		"id": spec["id"],
		"path": spec["path"],
		"file_exists": FileAccess.file_exists(spec["path"]),
		"resource_type": null,
		"mesh_instances": 0,
		"raw_bbox": null,
		"normalized_scale": null,
		"world_bbox": null,
		"static_body": false,
		"collision_shape": false,
		"pass": false,
		"errors": [],
	}
	if not row["file_exists"]:
		row["errors"].append("asset file missing")
		return row
	var resource := ResourceLoader.load(spec["path"])
	if resource == null:
		row["errors"].append("ResourceLoader.load returned null")
		return row
	row["resource_type"] = resource.get_class()
	if not resource is PackedScene:
		row["errors"].append("resource is not PackedScene")
		return row
	var node: Node3D = (resource as PackedScene).instantiate()
	node.name = spec["id"]
	var raw_box: AABB = _node_bounds(node)
	row["raw_bbox"] = _aabb(raw_box)
	var max_dim: float = max(raw_box.size.x, max(raw_box.size.y, raw_box.size.z))
	if max_dim <= 0.0:
		row["errors"].append("invalid raw bbox")
		return row
	var scale_factor: float = TARGET_SIZE / max_dim
	node.scale = Vector3.ONE * scale_factor
	var scaled_local_position: Vector3 = raw_box.position * scale_factor
	var scaled_size: Vector3 = raw_box.size * scale_factor
	var target_position: Vector3 = spec["position"]
	var y_lift: float = -(target_position.y + scaled_local_position.y)
	node.position = target_position + Vector3(0.0, y_lift, 0.0)
	root.add_child(node)
	_set_owner_recursive(node, root)
	var world_box := AABB(node.position + scaled_local_position, scaled_size)
	row["world_bbox"] = _aabb(world_box)
	row["normalized_scale"] = scale_factor
	row["mesh_instances"] = _count_meshes(node)

	var body: StaticBody3D = StaticBody3D.new()
	body.name = "%s_Collider" % spec["id"]
	var shape_node: CollisionShape3D = CollisionShape3D.new()
	shape_node.name = "CollisionProxy"
	var shape := BoxShape3D.new()
	shape.size = world_box.size
	shape_node.shape = shape
	body.position = world_box.position + world_box.size * 0.5
	body.add_child(shape_node)
	root.add_child(body)
	_set_owner_recursive(body, root)
	row["static_body"] = true
	row["collision_shape"] = true
	row["pass"] = row["mesh_instances"] > 0 and row["collision_shape"] and row["static_body"]
	row["_node"] = node
	return row

func _make_ground() -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = "Ground"
	var collision := CollisionShape3D.new()
	collision.name = "GroundCollision"
	var shape := BoxShape3D.new()
	shape.size = Vector3(7.0, 0.1, 4.0)
	collision.shape = shape
	body.add_child(collision)
	return body

func _make_player() -> CharacterBody3D:
	var player := CharacterBody3D.new()
	player.name = "Player"
	player.position = Vector3(-3.1, 0.35, 1.35)
	var collision := CollisionShape3D.new()
	collision.name = "PlayerCollision"
	var shape := CapsuleShape3D.new()
	shape.radius = 0.22
	shape.height = 0.7
	collision.shape = shape
	player.add_child(collision)
	return player

func _runtime_checks(player: CharacterBody3D, asset_rows: Array) -> Dictionary:
	var checks := {
		"player_has_collision": player.get_node_or_null("PlayerCollision") != null,
		"asset_count": asset_rows.size(),
		"asset_pass_count": 0,
		"normalized_scale_count": 0,
		"collision_proxy_count": 0,
		"all_assets_pass": false,
		"pass": false,
	}
	for row in asset_rows:
		if row.get("pass", false):
			checks["asset_pass_count"] += 1
		if row.get("normalized_scale", 0.0) > 0.0:
			checks["normalized_scale_count"] += 1
		if row.get("collision_shape", false):
			checks["collision_proxy_count"] += 1
	checks["all_assets_pass"] = checks["asset_pass_count"] == asset_rows.size()
	checks["pass"] = checks["player_has_collision"] and checks["all_assets_pass"] and checks["collision_proxy_count"] == asset_rows.size()
	return checks

func _node_bounds(node: Node3D) -> AABB:
	var state := {
		"has": false,
		"box": AABB()
	}
	_collect_bounds(node, state)
	return state["box"]

func _collect_bounds(node: Node, state: Dictionary) -> void:
	if node is MeshInstance3D:
		var mesh_node := node as MeshInstance3D
		var world_box: AABB = mesh_node.global_transform * mesh_node.get_aabb()
		if state["has"]:
			state["box"] = state["box"].merge(world_box)
		else:
			state["box"] = world_box
			state["has"] = true
	for child in node.get_children():
		_collect_bounds(child, state)

func _count_meshes(node: Node) -> int:
	var count := 0
	if node is MeshInstance3D:
		count += 1
	for child in node.get_children():
		count += _count_meshes(child)
	return count

func _set_owner_recursive(node: Node, owner_node: Node) -> void:
	node.owner = owner_node
	for child in node.get_children():
		_set_owner_recursive(child, owner_node)

func _vec(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

func _aabb(box: AABB) -> Dictionary:
	return {
		"position": _vec(box.position),
		"size": _vec(box.size)
	}
