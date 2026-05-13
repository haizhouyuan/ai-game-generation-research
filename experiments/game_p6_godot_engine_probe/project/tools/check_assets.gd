extends SceneTree

const ASSETS := [
	"res://assets/triposr_p4_chair_mesh.glb",
	"res://assets/triposr_p5_synthetic_block.glb",
	"res://assets/triposr_p5_synthetic_tower.glb",
]

func _initialize() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://outputs"))
	var rows: Array = []
	var failures := 0
	for asset in ASSETS:
		var row := _check_asset(asset)
		rows.append(row)
		if not row.get("pass", false):
			failures += 1
	var output_path := "res://outputs/godot_import_report.json"
	var file := FileAccess.open(output_path, FileAccess.WRITE)
	file.store_string(JSON.stringify(rows, "\t"))
	file.close()
	print(JSON.stringify(rows))
	quit(failures)

func _check_asset(asset: String) -> Dictionary:
	var row := {
		"asset": asset,
		"file_exists": FileAccess.file_exists(asset),
		"import_sidecar_exists": FileAccess.file_exists(asset + ".import"),
		"resource_type": null,
		"nodes": 0,
		"mesh_instances": 0,
		"bbox": null,
		"pass": false,
		"errors": [],
	}
	if not row["file_exists"]:
		row["errors"].append("asset file missing")
		return row
	var resource := ResourceLoader.load(asset)
	if resource == null:
		row["errors"].append("ResourceLoader.load returned null")
		return row
	row["resource_type"] = resource.get_class()
	if not resource is PackedScene:
		row["errors"].append("resource is not PackedScene")
		return row
	var root: Node = resource.instantiate()
	var bounds := {
		"has": false,
		"aabb": AABB(),
	}
	_walk(root, row, bounds)
	if bounds["has"]:
		var aabb: AABB = bounds["aabb"]
		row["bbox"] = {
			"position": [aabb.position.x, aabb.position.y, aabb.position.z],
			"size": [aabb.size.x, aabb.size.y, aabb.size.z],
		}
	row["pass"] = row["mesh_instances"] > 0 and bounds["has"]
	if not row["pass"]:
		row["errors"].append("no mesh instances or bounds")
	root.free()
	return row

func _walk(node: Node, row: Dictionary, bounds: Dictionary) -> void:
	row["nodes"] += 1
	if node is MeshInstance3D:
		row["mesh_instances"] += 1
		var mesh_node := node as MeshInstance3D
		var local_aabb := mesh_node.get_aabb()
		var world_aabb := mesh_node.transform * local_aabb
		if bounds["has"]:
			bounds["aabb"] = bounds["aabb"].merge(world_aabb)
		else:
			bounds["aabb"] = world_aabb
			bounds["has"] = true
	for child in node.get_children():
		_walk(child, row, bounds)
