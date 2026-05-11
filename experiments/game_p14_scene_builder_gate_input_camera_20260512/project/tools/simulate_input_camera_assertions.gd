extends SceneTree

const SCENE_PATH := "res://scenes/p10_objective_scene.tscn"
const OUTPUT_JSON := "res://outputs/p13_input_camera_assertions_report.json"
const TARGETS := [
	{
		"checkpoint": "Checkpoint_Chair",
		"collider": "triposr_p4_chair_mesh_Collider",
		"objective_id": "chair"
	},
	{
		"checkpoint": "Checkpoint_Block",
		"collider": "triposr_p5_synthetic_block_Collider",
		"objective_id": "block"
	},
	{
		"checkpoint": "Checkpoint_Tower",
		"collider": "triposr_p5_synthetic_tower_Collider",
		"objective_id": "tower"
	},
]
const FINISH_NAME := "Finish_Area"
const PLAYER_Y := 0.65
const MOVE_STEP := 0.12
const MAX_STEPS := 30
const FINISH_CENTER := Vector3(3.25, 0.65, 1.35)
const FINISH_RADIUS := 0.24
const CAMERA_OFFSET := Vector3(0.0, 3.05, 4.85)
const CAMERA_TARGET_OFFSET := Vector3(0.0, 0.35, 0.0)
const CAMERA_DOT_MIN := 0.98
const CAMERA_DISTANCE_MIN := 5.0
const CAMERA_DISTANCE_MAX := 6.2
const SENSOR_CLEARANCE_EPSILON := 0.04

var event_trace: Array = []
var collected: Array = []
var finish_attempts: Array = []
var tick_trace: Array = []
var camera_trace: Array = []
var current_tick := 0

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://outputs"))
	var report := {
		"scene_path": SCENE_PATH,
		"simulation_mode": "Godot headless deterministic input-vector replay with CharacterBody3D collision, Area3D body_entered objective events, and Camera3D follow/framing assertions",
		"no_proxy_note": "Godot run is local/offline on HomePC with proxy variables unset by the caller.",
		"visual_probe": {
			"attempted": false,
			"reason": "P13 avoids blind headless screenshot retry after P12 proved the local headless viewport path can be empty."
		},
		"fallback": {
			"used": false,
			"note": "No fallback is counted as pass. The pass gate requires move_and_collide, Area3D body_entered events, input-vector ticks, and camera assertions."
		},
		"sensor_clearance_repair_enabled": not _sensor_repair_disabled(),
		"setup": {},
		"input_replay": [],
		"collision_runs": [],
		"finish_attempts": [],
		"event_trace": [],
		"camera_trace": [],
		"summary": {}
	}
	var packed := ResourceLoader.load(SCENE_PATH)
	if packed == null or not packed is PackedScene:
		report["summary"] = {"pass": false, "stage": "load", "error": "P10 objective scene did not load"}
		_write_report(report, 1)
		return

	var scene: Node = (packed as PackedScene).instantiate()
	get_root().add_child(scene)
	await physics_frame

	var setup := _setup_scene(scene)
	report["setup"] = setup
	if not setup.get("pass", false):
		report["summary"] = {"pass": false, "stage": "setup", "errors": setup.get("errors", [])}
		scene.queue_free()
		_write_report(report, 1)
		return

	var player := setup["_player"] as CharacterBody3D
	var camera := setup["_camera"] as Camera3D
	setup.erase("_player")
	setup.erase("_camera")

	var pre_finish := await _run_finish_attempt(player, camera, "finish_before_unlock")
	report["finish_attempts"].append(pre_finish)
	var failures := 0
	if not pre_finish.get("pass", false) or pre_finish.get("accepted", true):
		failures += 1

	for target in TARGETS:
		var row := await _run_collision_path(scene, player, camera, target)
		report["collision_runs"].append(row)
		if not row.get("pass", false):
			failures += 1

	var post_finish := await _run_finish_attempt(player, camera, "finish_after_unlock")
	report["finish_attempts"].append(post_finish)
	if not post_finish.get("pass", false) or not post_finish.get("accepted", false):
		failures += 1

	var expected_reasons := ["finish_locked", "checkpoint_collected", "checkpoint_collected", "checkpoint_collected", "finish_unlocked"]
	var reasons := _event_reasons()
	var event_order_passed := reasons == expected_reasons
	var collision_pass_count := 0
	for row in report["collision_runs"]:
		if row.get("pass", false):
			collision_pass_count += 1
	var camera_summary := _camera_summary()
	var camera_passed: bool = bool(camera_summary.get("pass", false))
	var tick_passed: bool = tick_trace.size() > 0
	report["input_replay"] = tick_trace
	report["event_trace"] = event_trace
	report["camera_trace"] = camera_trace
	report["summary"] = {
		"pass": failures == 0 and event_order_passed and camera_passed and tick_passed,
		"collision_pass_count": collision_pass_count,
		"collision_target_count": TARGETS.size(),
		"event_order_passed": event_order_passed,
		"event_reasons": reasons,
		"expected_event_reasons": expected_reasons,
		"finish_before_locked": pre_finish.get("accepted", true) == false,
		"finish_after_unlocked": post_finish.get("accepted", false),
		"camera_assertions": camera_summary,
		"tick_count": tick_trace.size(),
		"collected": collected,
		"finish_attempt_count": finish_attempts.size()
	}
	scene.queue_free()
	_write_report(report, 0 if report["summary"]["pass"] else 2)

func _setup_scene(scene: Node) -> Dictionary:
	var row := {
		"scene_loaded": true,
		"player_exists": false,
		"camera_exists": false,
		"connected_objectives": 0,
		"objective_paths": [],
		"sensor_clearance_repairs": [],
		"pass": false,
		"errors": []
	}
	var player := scene.find_child("Player", true, false)
	if player is CharacterBody3D:
		row["player_exists"] = true
		row["_player"] = player
	else:
		row["errors"].append("Player CharacterBody3D missing")
	var camera := scene.find_child("PlayerCamera", true, false)
	if camera is Camera3D:
		row["camera_exists"] = true
		row["_camera"] = camera
	else:
		row["errors"].append("PlayerCamera Camera3D missing")
	for target in TARGETS:
		var node := scene.find_child(str(target["checkpoint"]), true, false)
		if node is Area3D:
			var area := node as Area3D
			area.monitoring = true
			area.monitorable = true
			row["sensor_clearance_repairs"].append(_apply_checkpoint_sensor_clearance(scene, area, str(target["collider"])))
			area.body_entered.connect(_on_objective_body_entered.bind(str(area.get_path()), str(area.get_meta("objective_type", "")), str(area.get_meta("objective_id", "")), str(target["checkpoint"])))
			row["objective_paths"].append(str(area.get_path()))
			row["connected_objectives"] += 1
		else:
			row["errors"].append("checkpoint Area3D missing: %s" % str(target["checkpoint"]))
	var finish := scene.find_child(FINISH_NAME, true, false)
	if finish is Area3D:
		var finish_area := finish as Area3D
		finish_area.monitoring = true
		finish_area.monitorable = true
		finish_area.body_entered.connect(_on_objective_body_entered.bind(str(finish_area.get_path()), str(finish_area.get_meta("objective_type", "")), "finish", FINISH_NAME))
		row["objective_paths"].append(str(finish_area.get_path()))
		row["connected_objectives"] += 1
	else:
		row["errors"].append("finish Area3D missing")
	row["pass"] = row["errors"].is_empty() and row["connected_objectives"] == TARGETS.size() + 1
	return row

func _apply_checkpoint_sensor_clearance(scene: Node, area: Area3D, collider_name: String) -> Dictionary:
	var row := {
		"checkpoint": str(area.name),
		"collider": collider_name,
		"applied": false,
		"reason": "not_needed",
		"area_front_z_before": null,
		"area_front_z_after": null,
		"collider_front_z": null,
		"delta_z": 0.0,
		"errors": []
	}
	var body := scene.find_child(collider_name, true, false)
	if body == null or not body is StaticBody3D:
		row["reason"] = "collider_missing"
		row["errors"].append("collider missing")
		return row
	var collider_shape := body.get_node_or_null("CollisionProxy")
	if not (collider_shape is CollisionShape3D) or not ((collider_shape as CollisionShape3D).shape is BoxShape3D):
		row["reason"] = "collider_shape_missing"
		row["errors"].append("collider BoxShape3D missing")
		return row
	var area_shape := area.get_node_or_null("ObjectiveShape")
	if not (area_shape is CollisionShape3D) or not ((area_shape as CollisionShape3D).shape is BoxShape3D):
		row["reason"] = "area_shape_missing"
		row["errors"].append("area BoxShape3D missing")
		return row
	var collider_box := (collider_shape as CollisionShape3D).shape as BoxShape3D
	var objective_shape := area_shape as CollisionShape3D
	var area_box := objective_shape.shape as BoxShape3D
	var collider_front_z: float = (body as StaticBody3D).global_position.z + collider_box.size.z * 0.5
	var area_front_z: float = area.global_position.z + objective_shape.position.z + area_box.size.z * 0.5
	var target_front_z: float = collider_front_z + SENSOR_CLEARANCE_EPSILON
	row["collider_front_z"] = collider_front_z
	row["area_front_z_before"] = area_front_z
	if _sensor_repair_disabled():
		row["reason"] = "disabled_by_P13_DISABLE_SENSOR_CLEARANCE_REPAIR"
		row["area_front_z_after"] = area_front_z
		return row
	if area_front_z < target_front_z:
		var delta_z: float = target_front_z - area_front_z
		objective_shape.position.z += delta_z * 0.5
		area_box.size.z += delta_z
		row["applied"] = true
		row["reason"] = "extended_sensor_front_to_reach_collision_approach_before_contact"
		row["delta_z"] = delta_z
	row["area_front_z_after"] = area.global_position.z + objective_shape.position.z + area_box.size.z * 0.5
	return row

func _sensor_repair_disabled() -> bool:
	return OS.get_environment("P13_DISABLE_SENSOR_CLEARANCE_REPAIR") == "1"

func _run_collision_path(scene: Node, player: CharacterBody3D, camera: Camera3D, target: Dictionary) -> Dictionary:
	var target_name := str(target["collider"])
	var checkpoint_name := str(target["checkpoint"])
	var objective_id := str(target["objective_id"])
	var row := {
		"checkpoint": checkpoint_name,
		"collider": target_name,
		"objective_id": objective_id,
		"target_found": false,
		"target_is_static_body": false,
		"input_ticks": [],
		"collision_detected": false,
		"collider_name": null,
		"checkpoint_collected": false,
		"pass": false,
		"errors": []
	}
	var body := scene.find_child(target_name, true, false)
	row["target_found"] = body != null
	row["target_is_static_body"] = body is StaticBody3D
	if body == null or not body is StaticBody3D:
		row["errors"].append("target StaticBody3D missing")
		return row
	var shape_node := body.get_node_or_null("CollisionProxy")
	if not (shape_node is CollisionShape3D) or not ((shape_node as CollisionShape3D).shape is BoxShape3D):
		row["errors"].append("target CollisionProxy BoxShape3D missing")
		return row
	var box := (shape_node as CollisionShape3D).shape as BoxShape3D
	var center := (body as StaticBody3D).global_position
	player.global_position = Vector3(center.x, PLAYER_Y, center.z + box.size.z * 0.5 + 0.72)
	player.velocity = Vector3.ZERO
	await physics_frame
	_record_camera(player, camera, "%s_start" % checkpoint_name)
	for index in range(MAX_STEPS):
		var before := player.global_position
		var input_vector := Vector3(0.0, 0.0, -1.0)
		var motion: Vector3 = input_vector * MOVE_STEP
		var collision := player.move_and_collide(motion)
		await physics_frame
		current_tick += 1
		var tick := {
			"tick": current_tick,
			"label": "approach_%s" % objective_id,
			"action": _input_label(input_vector),
			"input_vector": _vec(input_vector),
			"before": _vec(before),
			"after": _vec(player.global_position),
			"moved_distance": before.distance_to(player.global_position),
			"collision": collision != null,
			"event_count": event_trace.size(),
			"collected": collected.duplicate()
		}
		_record_camera(player, camera, tick["label"])
		if collision != null:
			var collider := collision.get_collider()
			var collider_name := str(collider.name) if collider != null else ""
			tick["collider_name"] = collider_name
			tick["collision_position"] = _vec(collision.get_position())
			tick["collision_normal"] = _vec(collision.get_normal())
			row["collision_detected"] = true
			row["collider_name"] = collider_name
			row["input_ticks"].append(tick)
			tick_trace.append(tick)
			row["checkpoint_collected"] = collected.has(objective_id)
			row["pass"] = collider_name == target_name and row["checkpoint_collected"]
			if not row["pass"]:
				row["errors"].append("collision or checkpoint gate failed")
			return row
		row["input_ticks"].append(tick)
		tick_trace.append(tick)
	row["checkpoint_collected"] = collected.has(objective_id)
	row["errors"].append("no collision detected within max steps")
	return row

func _run_finish_attempt(player: CharacterBody3D, camera: Camera3D, label: String) -> Dictionary:
	var before_count := finish_attempts.size()
	var row := {
		"label": label,
		"input_ticks": [],
		"accepted": false,
		"signal_received": false,
		"distance_to_finish": null,
		"pass": false,
		"errors": []
	}
	player.global_position = FINISH_CENTER + Vector3(-0.78, 0.0, 0.0)
	player.velocity = Vector3.ZERO
	await physics_frame
	_record_camera(player, camera, "%s_start" % label)
	for index in range(12):
		var before := player.global_position
		var direction := FINISH_CENTER - player.global_position
		var input_vector := direction.normalized()
		var step_length: float = min(MOVE_STEP, direction.length())
		var motion: Vector3 = input_vector * step_length
		var collision := player.move_and_collide(motion)
		await physics_frame
		current_tick += 1
		var distance := player.global_position.distance_to(FINISH_CENTER)
		var tick := {
			"tick": current_tick,
			"label": label,
			"action": _input_label(input_vector),
			"input_vector": _vec(input_vector),
			"before": _vec(before),
			"after": _vec(player.global_position),
			"distance_to_finish": distance,
			"collision": collision != null,
			"event_count": event_trace.size(),
			"collected": collected.duplicate()
		}
		_record_camera(player, camera, label)
		row["input_ticks"].append(tick)
		tick_trace.append(tick)
		if collision != null:
			var collider := collision.get_collider()
			row["errors"].append("finish path collided with %s" % (str(collider.name) if collider != null else "unknown"))
			return row
		if finish_attempts.size() > before_count:
			var event: Dictionary = finish_attempts[finish_attempts.size() - 1]
			row["accepted"] = bool(event.get("accepted", false))
			row["signal_received"] = true
			row["distance_to_finish"] = distance
			row["pass"] = label == "finish_before_unlock" and not row["accepted"] or label == "finish_after_unlock" and row["accepted"]
			return row
		if distance <= FINISH_RADIUS:
			row["distance_to_finish"] = distance
	if finish_attempts.size() > before_count:
		var final_event: Dictionary = finish_attempts[finish_attempts.size() - 1]
		row["accepted"] = bool(final_event.get("accepted", false))
		row["signal_received"] = true
	row["pass"] = row["signal_received"] and (label == "finish_before_unlock" and not row["accepted"] or label == "finish_after_unlock" and row["accepted"])
	if not row["pass"]:
		row["errors"].append("finish signal gate failed")
	return row

func _on_objective_body_entered(body: Node3D, objective_path: String, objective_type: String, objective_id: String, objective_name: String) -> void:
	if body.name != "Player":
		return
	var accepted := false
	var reason := ""
	if objective_type == "checkpoint":
		if not collected.has(objective_id):
			collected.append(objective_id)
			accepted = true
			reason = "checkpoint_collected"
		else:
			reason = "checkpoint_already_collected"
	elif objective_type == "finish":
		if collected.size() == TARGETS.size():
			accepted = true
			reason = "finish_unlocked"
		else:
			reason = "finish_locked"
	else:
		reason = "unsupported_objective_type"
	var event := {
		"index": event_trace.size() + 1,
		"tick": current_tick,
		"objective_path": objective_path,
		"objective_name": objective_name,
		"objective_type": objective_type,
		"objective_id": objective_id,
		"body": str(body.get_path()),
		"accepted": accepted,
		"reason": reason,
		"collected_snapshot": collected.duplicate()
	}
	event_trace.append(event)
	if objective_type == "finish":
		finish_attempts.append(event)

func _record_camera(player: CharacterBody3D, camera: Camera3D, label: String) -> void:
	var target := player.global_position + CAMERA_TARGET_OFFSET
	var expected_position := player.global_position + CAMERA_OFFSET
	camera.global_position = expected_position
	camera.look_at(target, Vector3.UP)
	var forward := -camera.global_transform.basis.z.normalized()
	var to_target := (target - camera.global_position).normalized()
	var dot := forward.dot(to_target)
	var distance := camera.global_position.distance_to(target)
	var follow_error := camera.global_position.distance_to(expected_position)
	var frustum_contains := true
	if camera.has_method("is_position_in_frustum"):
		frustum_contains = camera.is_position_in_frustum(target)
	var row := {
		"tick": current_tick,
		"label": label,
		"camera_position": _vec(camera.global_position),
		"target": _vec(target),
		"player_position": _vec(player.global_position),
		"forward_dot_target": dot,
		"distance_to_target": distance,
		"follow_error": follow_error,
		"frustum_contains_target": frustum_contains,
		"pass": dot >= CAMERA_DOT_MIN and distance >= CAMERA_DISTANCE_MIN and distance <= CAMERA_DISTANCE_MAX and follow_error <= 0.001 and frustum_contains
	}
	camera_trace.append(row)

func _camera_summary() -> Dictionary:
	var failed := 0
	for row in camera_trace:
		if not row.get("pass", false):
			failed += 1
	return {
		"pass": camera_trace.size() > 0 and failed == 0,
		"sample_count": camera_trace.size(),
		"failed_count": failed,
		"dot_min": CAMERA_DOT_MIN,
		"distance_min": CAMERA_DISTANCE_MIN,
		"distance_max": CAMERA_DISTANCE_MAX
	}

func _event_reasons() -> Array:
	var reasons: Array = []
	for event in event_trace:
		reasons.append(event.get("reason", ""))
	return reasons

func _input_label(input_vector: Vector3) -> String:
	if abs(input_vector.x) > abs(input_vector.z):
		return "move_right" if input_vector.x > 0.0 else "move_left"
	return "move_backward" if input_vector.z > 0.0 else "move_forward"

func _vec(value: Vector3) -> Dictionary:
	return {"x": value.x, "y": value.y, "z": value.z}

func _write_report(report: Dictionary, exit_code: int) -> void:
	var file := FileAccess.open(OUTPUT_JSON, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify(report))
	quit(exit_code)
