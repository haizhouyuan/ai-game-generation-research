extends SceneTree

const SCENE_PATH := "res://scenes/p7_minimal_playable_scene.tscn"
const TARGETS := [
	"triposr_p4_chair_mesh_Collider",
	"triposr_p5_synthetic_block_Collider",
	"triposr_p5_synthetic_tower_Collider"
]
const MOVE_STEP := 0.12
const MAX_STEPS := 28
const PLAYER_Y := 0.65
const FINISH_CENTER := Vector3(3.25, 0.65, 1.35)
const FINISH_RADIUS := 0.22

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://outputs"))
	var report := {
		"scene_path": SCENE_PATH,
		"scene_loaded": false,
		"simulation_mode": "Godot headless CharacterBody3D.move_and_collide plus deterministic objective assertions",
		"no_proxy_note": "Godot run is local/offline on HomePC with proxy variables unset by the caller.",
		"targets": TARGETS,
		"collision_runs": [],
		"objective": {},
		"summary": {}
	}
	var packed := ResourceLoader.load(SCENE_PATH)
	if packed == null or not packed is PackedScene:
		report["summary"] = {"pass": false, "error": "scene did not load as PackedScene"}
		_write_report(report, 1)
		return
	report["scene_loaded"] = true
	var scene: Node = (packed as PackedScene).instantiate()
	get_root().add_child(scene)
	await physics_frame

	var player := scene.find_child("Player", true, false)
	if not player is CharacterBody3D:
		report["summary"] = {"pass": false, "error": "Player CharacterBody3D missing"}
		scene.queue_free()
		_write_report(report, 1)
		return
	var character := player as CharacterBody3D
	var collected: Array = []
	var failures := 0
	for target_name in TARGETS:
		var body := scene.find_child(target_name, true, false)
		var row := await _run_collision_path(character, body, target_name)
		report["collision_runs"].append(row)
		if row.get("pass", false):
			collected.append(target_name)
		else:
			failures += 1
	var objective := await _run_finish_loop(character, collected)
	report["objective"] = objective
	if not objective.get("pass", false):
		failures += 1
	report["summary"] = {
		"collision_target_count": TARGETS.size(),
		"collision_pass_count": collected.size(),
		"finish_unlocked": objective.get("finish_unlocked", false),
		"finish_reached": objective.get("finish_reached", false),
		"pass": failures == 0 and collected.size() == TARGETS.size()
	}
	scene.queue_free()
	_write_report(report, 0 if report["summary"]["pass"] else 2)

func _run_collision_path(player: CharacterBody3D, body: Node, target_name: String) -> Dictionary:
	var row := {
		"target": target_name,
		"target_found": body != null,
		"target_is_static_body": body is StaticBody3D,
		"steps": [],
		"collision_detected": false,
		"collider_name": null,
		"pass": false,
		"errors": []
	}
	if body == null or not body is StaticBody3D:
		row["errors"].append("target StaticBody3D missing")
		return row
	var shape_node := body.get_node_or_null("CollisionProxy")
	if not (shape_node is CollisionShape3D) or not ((shape_node as CollisionShape3D).shape is BoxShape3D):
		row["errors"].append("target CollisionProxy BoxShape3D missing")
		return row
	var box := (shape_node as CollisionShape3D).shape as BoxShape3D
	var center := (body as StaticBody3D).global_position
	var start := Vector3(center.x, PLAYER_Y, center.z + box.size.z * 0.5 + 0.72)
	player.global_position = start
	player.velocity = Vector3.ZERO
	await physics_frame
	for index in range(MAX_STEPS):
		var before := player.global_position
		var collision := player.move_and_collide(Vector3(0.0, 0.0, -MOVE_STEP))
		await physics_frame
		var step := {
			"step": index + 1,
			"before": _vec(before),
			"after": _vec(player.global_position),
			"moved_distance": before.distance_to(player.global_position),
			"collision": collision != null
		}
		if collision != null:
			var collider := collision.get_collider()
			var collider_name := str(collider.name) if collider != null else ""
			step["collider_name"] = collider_name
			step["collision_position"] = _vec(collision.get_position())
			step["collision_normal"] = _vec(collision.get_normal())
			row["collision_detected"] = true
			row["collider_name"] = collider_name
			row["pass"] = collider_name == target_name
			if not row["pass"]:
				row["errors"].append("collided with unexpected body: %s" % collider_name)
			row["steps"].append(step)
			return row
		row["steps"].append(step)
	row["errors"].append("no collision detected within max steps")
	return row

func _run_finish_loop(player: CharacterBody3D, collected: Array) -> Dictionary:
	var finish_unlocked := collected.size() == TARGETS.size()
	var objective := {
		"required_checkpoints": TARGETS,
		"collected_order": collected,
		"finish_center": _vec(FINISH_CENTER),
		"finish_radius": FINISH_RADIUS,
		"finish_unlocked": finish_unlocked,
		"finish_reached": false,
		"steps": [],
		"pass": false,
		"errors": []
	}
	if not finish_unlocked:
		objective["errors"].append("finish locked because not all checkpoint collisions passed")
		return objective
	player.global_position = FINISH_CENTER + Vector3(-0.78, 0.0, 0.0)
	player.velocity = Vector3.ZERO
	await physics_frame
	for index in range(12):
		var before: Vector3 = player.global_position
		var direction: Vector3 = FINISH_CENTER - player.global_position
		var motion: Vector3 = direction.normalized() * min(0.14, direction.length())
		var collision := player.move_and_collide(motion)
		await physics_frame
		var distance := player.global_position.distance_to(FINISH_CENTER)
		var step := {
			"step": index + 1,
			"before": _vec(before),
			"after": _vec(player.global_position),
			"distance_to_finish": distance,
			"collision": collision != null
		}
		if collision != null:
			var collider := collision.get_collider()
			step["collider_name"] = str(collider.name) if collider != null else ""
			objective["errors"].append("finish path collided with %s" % step["collider_name"])
			objective["steps"].append(step)
			return objective
		objective["steps"].append(step)
		if distance <= FINISH_RADIUS:
			objective["finish_reached"] = true
			objective["pass"] = true
			return objective
	objective["errors"].append("finish not reached within max steps")
	return objective

func _write_report(report: Dictionary, exit_code: int) -> void:
	var file := FileAccess.open("res://outputs/p9_characterbody_objective_report.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify(report))
	quit(exit_code)

func _vec(v: Vector3) -> Array:
	return [v.x, v.y, v.z]
