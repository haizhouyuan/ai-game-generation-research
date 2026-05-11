extends SceneTree

const SOURCE_SCENE := "res://scenes/p7_minimal_playable_scene.tscn"
const P15_SCENE := "res://scenes/p15_ci_objective_scene.tscn"
const OUTPUT_JSON := "res://outputs/p15_scene_ci_harness_replay_trace_report.json"
const SENSOR_CLEARANCE_EPSILON := 0.04
const FLOAT_TOLERANCE := 0.00001
const PLAYER_Y := 0.65
const MOVE_STEP := 0.12
const MAX_STEPS := 30
const FINISH_NAME := "Finish_Area"
const FINISH_CENTER := Vector3(4.5, 0.65, 3.0)
const FINISH_RADIUS := 0.24
const OBJECTIVE_UI_NAME := "ObjectiveUI"
const OBJECTIVE_LABEL_NAME := "ObjectiveStatusLabel"
const CAMERA_TARGET_OFFSET := Vector3(0.0, 0.35, 0.0)
const CAMERA_DOT_MIN := 0.98
const TARGETS := [
	{
		"id": "chair",
		"checkpoint": "Checkpoint_Chair",
		"collider": "triposr_p4_chair_mesh_Collider"
	},
	{
		"id": "block",
		"checkpoint": "Checkpoint_Block",
		"collider": "triposr_p5_synthetic_block_Collider"
	},
	{
		"id": "tower",
		"checkpoint": "Checkpoint_Tower",
		"collider": "triposr_p5_synthetic_tower_Collider"
	},
]
const CAMERA_VARIANTS := [
	{"id": "standard_follow", "offset": Vector3(0.0, 3.05, 4.85), "distance_min": 5.0, "distance_max": 6.2},
	{"id": "close_follow", "offset": Vector3(0.0, 2.25, 3.75), "distance_min": 4.0, "distance_max": 4.8},
	{"id": "high_follow", "offset": Vector3(0.0, 4.2, 5.8), "distance_min": 6.4, "distance_max": 7.4},
]

var event_trace: Array = []
var collected: Array = []
var finish_attempts: Array = []
var input_trace: Array = []
var camera_trace: Array = []
var ui_trace: Array = []
var current_tick := 0

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://outputs"))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://scenes"))
	var report := {
		"source_scene": SOURCE_SCENE,
		"p15_scene": P15_SCENE,
		"simulation_mode": "CI-style scene-builder harness with sensor-clearance, objective UI feedback, trace diff, InputMap key-event replay, camera variants, and obstruction assertions",
		"no_proxy_note": "Godot run is local/offline on HomePC with proxy variables unset by the caller.",
		"visual_probe": {
			"attempted": false,
			"reason": "P15 does not retry or modify the blocked headless screenshot/display path."
		},
		"scene_build": {},
		"scene_readback": {},
		"input_replay": {},
		"summary": {}
	}
	var build := _build_p15_scene()
	report["scene_build"] = build
	if not build.get("pass", false):
		report["summary"] = {"pass": false, "stage": "build", "errors": build.get("errors", [])}
		_write_report(report, 1)
		return
	var readback := _readback_p15_scene()
	report["scene_readback"] = readback
	if not readback.get("pass", false):
		report["summary"] = {"pass": false, "stage": "readback", "errors": readback.get("errors", [])}
		_write_report(report, 1)
		return
	var replay := await _run_input_camera_replay()
	report["input_replay"] = replay
	report["summary"] = {
		"pass": build.get("pass", false) and readback.get("pass", false) and replay.get("summary", {}).get("pass", false),
		"scene_builder_clearance_pass": build.get("clearance_pass", false),
		"readback_clearance_pass": readback.get("clearance_pass", false),
		"input_key_event_pass": replay.get("summary", {}).get("input_key_event_pass", false),
		"collision_pass_count": replay.get("summary", {}).get("collision_pass_count", 0),
		"event_order_passed": replay.get("summary", {}).get("event_order_passed", false),
		"camera_variants_pass": replay.get("summary", {}).get("camera_variants_pass", false),
		"obstruction_counter_pass": replay.get("summary", {}).get("obstruction_counter_pass", false),
		"objective_ui_pass": replay.get("summary", {}).get("objective_ui_pass", false),
		"trace_diff_pass": replay.get("summary", {}).get("trace_diff_pass", false)
	}
	_write_report(report, 0 if report["summary"]["pass"] else 2)

func _build_p15_scene() -> Dictionary:
	var row := {
		"source_loaded": false,
		"checkpoint_nodes_created": 0,
		"finish_created": false,
		"clearance_rows": [],
		"clearance_repair_count": 0,
		"clearance_pass": false,
		"save_result": null,
		"pass": false,
		"errors": []
	}
	var packed := ResourceLoader.load(SOURCE_SCENE)
	if packed == null or not packed is PackedScene:
		row["errors"].append("source scene did not load")
		return row
	row["source_loaded"] = true
	var root: Node = (packed as PackedScene).instantiate()
	var prior_objectives := root.find_child("ObjectiveRoot", true, false)
	if prior_objectives != null:
		prior_objectives.queue_free()
	var objective_root := Node3D.new()
	objective_root.name = "ObjectiveRoot"
	root.add_child(objective_root)
	_set_owner_recursive(objective_root, root)
	var objective_ui := _make_objective_ui()
	root.add_child(objective_ui)
	_set_owner_recursive(objective_ui, root)
	for target in TARGETS:
		var collider := root.find_child(str(target["collider"]), true, false)
		if collider == null or not collider is StaticBody3D:
			row["errors"].append("target collider missing: %s" % str(target["collider"]))
			continue
		var checkpoint := _make_checkpoint_area(target, collider as StaticBody3D)
		var clearance := _apply_builder_clearance(checkpoint, collider as StaticBody3D)
		checkpoint.set_meta("sensor_clearance_delta_z", clearance.get("delta_z", 0.0))
		checkpoint.set_meta("sensor_front_z", clearance.get("sensor_front_z_after", 0.0))
		checkpoint.set_meta("collider_front_z", clearance.get("collider_front_z", 0.0))
		checkpoint.set_meta("sensor_clearance_min_z", SENSOR_CLEARANCE_EPSILON)
		checkpoint.set_meta("sensor_clearance_pass", clearance.get("pass", false))
		objective_root.add_child(checkpoint)
		_set_owner_recursive(checkpoint, root)
		row["clearance_rows"].append(clearance)
		if clearance.get("applied", false):
			row["clearance_repair_count"] += 1
		row["checkpoint_nodes_created"] += 1
	var finish := _make_finish_area()
	objective_root.add_child(finish)
	_set_owner_recursive(finish, root)
	row["finish_created"] = true
	var packed_out := PackedScene.new()
	var pack_result := packed_out.pack(root)
	var save_result := ResourceSaver.save(packed_out, P15_SCENE)
	row["pack_result"] = pack_result
	row["save_result"] = save_result
	row["clearance_pass"] = _all_clearance_rows_pass(row["clearance_rows"])
	row["pass"] = row["checkpoint_nodes_created"] == TARGETS.size() and row["finish_created"] and row["clearance_pass"] and pack_result == OK and save_result == OK
	root.queue_free()
	return row

func _make_objective_ui() -> CanvasLayer:
	var layer := CanvasLayer.new()
	layer.name = OBJECTIVE_UI_NAME
	var label := Label.new()
	label.name = OBJECTIVE_LABEL_NAME
	label.text = _objective_status_text(false)
	label.set_meta("ci_role", "objective_status_feedback")
	layer.add_child(label)
	return layer

func _make_checkpoint_area(target: Dictionary, collider: StaticBody3D) -> Area3D:
	var source_shape := collider.get_node_or_null("CollisionProxy")
	var source_size := Vector3(0.6, 0.7, 0.6)
	if source_shape is CollisionShape3D and (source_shape as CollisionShape3D).shape is BoxShape3D:
		var box := (source_shape as CollisionShape3D).shape as BoxShape3D
		source_size = Vector3(min(0.72, max(0.36, box.size.x * 0.45)), min(1.0, max(0.45, box.size.y)), min(0.72, max(0.36, box.size.z * 0.45)))
	var area := Area3D.new()
	area.name = str(target["checkpoint"])
	area.position = Vector3(collider.position.x, PLAYER_Y, collider.position.z + 0.52)
	area.monitoring = true
	area.monitorable = true
	area.set_meta("objective_type", "checkpoint")
	area.set_meta("objective_id", str(target["id"]))
	area.set_meta("target_collider", str(target["collider"]))
	var shape_node := CollisionShape3D.new()
	shape_node.name = "ObjectiveShape"
	var shape := BoxShape3D.new()
	shape.size = source_size
	shape_node.shape = shape
	area.add_child(shape_node)
	return area

func _apply_builder_clearance(area: Area3D, collider: StaticBody3D) -> Dictionary:
	var row := _measure_checkpoint_clearance(area, collider)
	if row.get("pass", false):
		return row
	var shape_node := area.get_node_or_null("ObjectiveShape")
	if not shape_node is CollisionShape3D or not ((shape_node as CollisionShape3D).shape is BoxShape3D):
		row["errors"].append("checkpoint BoxShape3D missing")
		return row
	var delta_z: float = float(row["required_sensor_front_z"]) - float(row["sensor_front_z_before"])
	var collision_shape := shape_node as CollisionShape3D
	var box := collision_shape.shape as BoxShape3D
	collision_shape.position.z += delta_z * 0.5
	box.size.z += delta_z
	var after := _measure_checkpoint_clearance(area, collider)
	after["applied"] = true
	after["delta_z"] = delta_z
	after["sensor_front_z_before"] = row["sensor_front_z_before"]
	after["reason"] = "builder_extended_sensor_front_before_scene_save"
	return after

func _measure_checkpoint_clearance(area: Area3D, collider: StaticBody3D) -> Dictionary:
	var row := {
		"checkpoint": str(area.name),
		"collider": str(collider.name),
		"applied": false,
		"delta_z": 0.0,
		"sensor_front_z_before": null,
		"sensor_front_z_after": null,
		"collider_front_z": null,
		"required_sensor_front_z": null,
		"pass": false,
		"errors": []
	}
	var collider_shape := collider.get_node_or_null("CollisionProxy")
	var area_shape := area.get_node_or_null("ObjectiveShape")
	if not (collider_shape is CollisionShape3D) or not ((collider_shape as CollisionShape3D).shape is BoxShape3D):
		row["errors"].append("collider BoxShape3D missing")
		return row
	if not (area_shape is CollisionShape3D) or not ((area_shape as CollisionShape3D).shape is BoxShape3D):
		row["errors"].append("area BoxShape3D missing")
		return row
	var collider_box := (collider_shape as CollisionShape3D).shape as BoxShape3D
	var area_box := (area_shape as CollisionShape3D).shape as BoxShape3D
	var collider_front_z: float = collider.global_position.z + collider_box.size.z * 0.5
	var sensor_front_z: float = area.global_position.z + (area_shape as CollisionShape3D).position.z + area_box.size.z * 0.5
	row["sensor_front_z_before"] = sensor_front_z
	row["sensor_front_z_after"] = sensor_front_z
	row["collider_front_z"] = collider_front_z
	row["required_sensor_front_z"] = collider_front_z + SENSOR_CLEARANCE_EPSILON
	row["pass"] = sensor_front_z + FLOAT_TOLERANCE >= float(row["required_sensor_front_z"])
	return row

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
	shape.radius = FINISH_RADIUS
	shape_node.shape = shape
	area.add_child(shape_node)
	return area

func _readback_p15_scene() -> Dictionary:
	var row := {"scene_loaded": false, "objective_root_exists": false, "objective_ui_exists": false, "objective_label_exists": false, "objective_label_text": "", "areas": [], "clearance_rows": [], "clearance_pass": false, "pass": false, "errors": []}
	var packed := ResourceLoader.load(P15_SCENE)
	if packed == null or not packed is PackedScene:
		row["errors"].append("P15 scene did not load")
		return row
	row["scene_loaded"] = true
	var root: Node = (packed as PackedScene).instantiate()
	var objective_root := root.find_child("ObjectiveRoot", true, false)
	row["objective_root_exists"] = objective_root != null
	if objective_root == null:
		row["errors"].append("ObjectiveRoot missing")
		root.queue_free()
		return row
	var objective_ui := root.find_child(OBJECTIVE_UI_NAME, true, false)
	row["objective_ui_exists"] = objective_ui != null
	var objective_label := root.find_child(OBJECTIVE_LABEL_NAME, true, false)
	if objective_label is Label:
		row["objective_label_exists"] = true
		row["objective_label_text"] = (objective_label as Label).text
	else:
		row["errors"].append("ObjectiveStatusLabel missing")
	for target in TARGETS:
		var area := root.find_child(str(target["checkpoint"]), true, false)
		var collider := root.find_child(str(target["collider"]), true, false)
		if not area is Area3D or not collider is StaticBody3D:
			row["errors"].append("checkpoint or collider missing for %s" % str(target["id"]))
			continue
		var area_readback := _area_readback(area as Area3D)
		row["areas"].append(area_readback)
		var clearance := _measure_checkpoint_clearance(area as Area3D, collider as StaticBody3D)
		row["clearance_rows"].append(clearance)
		if not area_readback.get("pass", false) or not clearance.get("pass", false):
			row["errors"].append("readback gate failed for %s" % str(target["checkpoint"]))
	var finish := root.find_child(FINISH_NAME, true, false)
	if not finish is Area3D:
		row["errors"].append("finish Area3D missing")
	else:
		row["areas"].append(_area_readback(finish as Area3D))
	row["clearance_pass"] = _all_clearance_rows_pass(row["clearance_rows"])
	row["pass"] = row["scene_loaded"] and row["objective_root_exists"] and row["objective_ui_exists"] and row["objective_label_exists"] and row["clearance_pass"] and row["errors"].is_empty()
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
		"name": str(area.name),
		"objective_type": str(area.get_meta("objective_type", "")),
		"objective_id": str(area.get_meta("objective_id", "")),
		"target_collider": str(area.get_meta("target_collider", "")),
		"shape_type": shape_type,
		"shape_size": shape_size,
		"shape_radius": shape_radius,
		"sensor_clearance_delta_z": area.get_meta("sensor_clearance_delta_z", null),
		"sensor_clearance_pass": area.get_meta("sensor_clearance_pass", null),
		"pass": shape_node != null and shape_type != null and area.has_meta("objective_type")
	}

func _run_input_camera_replay() -> Dictionary:
	event_trace.clear()
	collected.clear()
	finish_attempts.clear()
	input_trace.clear()
	camera_trace.clear()
	ui_trace.clear()
	current_tick = 0
	var report := {"setup": {}, "collision_runs": [], "finish_attempts": [], "event_trace": [], "input_trace": [], "camera_trace": [], "ui_trace": [], "trace_diff": {}, "camera_obstruction_counter": {}, "summary": {}}
	var packed := ResourceLoader.load(P15_SCENE)
	if packed == null or not packed is PackedScene:
		report["summary"] = {"pass": false, "stage": "load", "error": "P15 scene did not load for replay"}
		return report
	var scene: Node = (packed as PackedScene).instantiate()
	get_root().add_child(scene)
	await physics_frame
	var setup := _setup_replay_scene(scene)
	report["setup"] = setup
	if not setup.get("pass", false):
		report["summary"] = {"pass": false, "stage": "setup", "errors": setup.get("errors", [])}
		scene.queue_free()
		return report
	var player := setup["_player"] as CharacterBody3D
	var camera := setup["_camera"] as Camera3D
	setup.erase("_player")
	setup.erase("_camera")
	var input_setup := _ensure_input_map()
	report["input_map"] = input_setup
	_record_ui_state(scene, "initial")

	var pre_finish := await _run_finish_attempt(scene, player, camera, "finish_before_unlock")
	report["finish_attempts"].append(pre_finish)
	for target in TARGETS:
		var collision_row := await _run_collision_path(scene, player, camera, target)
		report["collision_runs"].append(collision_row)
	var post_finish := await _run_finish_attempt(scene, player, camera, "finish_after_unlock")
	report["finish_attempts"].append(post_finish)
	var obstruction_counter := _run_camera_obstruction_counter(scene, player, camera)
	report["camera_obstruction_counter"] = obstruction_counter

	var expected_reasons := ["finish_locked", "checkpoint_collected", "checkpoint_collected", "checkpoint_collected", "finish_unlocked"]
	var reasons := _event_reasons()
	var trace_diff := _trace_diff(reasons, expected_reasons)
	var collision_pass_count := 0
	for row in report["collision_runs"]:
		if row.get("pass", false):
			collision_pass_count += 1
	var input_key_event_pass: bool = bool(_input_key_event_summary().get("pass", false))
	var camera_summary: Dictionary = _camera_summary()
	var objective_ui_summary := _objective_ui_summary()
	report["event_trace"] = event_trace
	report["input_trace"] = input_trace
	report["camera_trace"] = camera_trace
	report["ui_trace"] = ui_trace
	report["trace_diff"] = trace_diff
	report["summary"] = {
		"pass": input_setup.get("pass", false)
			and pre_finish.get("pass", false)
			and post_finish.get("pass", false)
			and collision_pass_count == TARGETS.size()
			and reasons == expected_reasons
			and input_key_event_pass
			and camera_summary.get("pass", false)
			and obstruction_counter.get("pass", false)
			and objective_ui_summary.get("pass", false)
			and trace_diff.get("pass", false),
		"collision_pass_count": collision_pass_count,
		"collision_target_count": TARGETS.size(),
		"event_order_passed": reasons == expected_reasons,
		"event_reasons": reasons,
		"expected_event_reasons": expected_reasons,
		"finish_before_locked": pre_finish.get("accepted", true) == false,
		"finish_after_unlocked": post_finish.get("accepted", false),
		"input_key_event_pass": input_key_event_pass,
		"input_key_event_summary": _input_key_event_summary(),
		"objective_ui_pass": objective_ui_summary.get("pass", false),
		"objective_ui_summary": objective_ui_summary,
		"trace_diff_pass": trace_diff.get("pass", false),
		"camera_variants_pass": camera_summary.get("pass", false),
		"camera_summary": camera_summary,
		"obstruction_counter_pass": obstruction_counter.get("pass", false),
		"tick_count": input_trace.size(),
		"collected": collected
	}
	scene.queue_free()
	return report

func _setup_replay_scene(scene: Node) -> Dictionary:
	var row := {"player_exists": false, "camera_exists": false, "objective_ui_exists": false, "objective_label_exists": false, "connected_objectives": 0, "pass": false, "errors": []}
	var player := scene.find_child("Player", true, false)
	var camera := scene.find_child("PlayerCamera", true, false)
	var objective_ui := scene.find_child(OBJECTIVE_UI_NAME, true, false)
	var objective_label := scene.find_child(OBJECTIVE_LABEL_NAME, true, false)
	if player is CharacterBody3D:
		row["player_exists"] = true
		row["_player"] = player
	else:
		row["errors"].append("Player CharacterBody3D missing")
	if camera is Camera3D:
		row["camera_exists"] = true
		row["_camera"] = camera
	else:
		row["errors"].append("PlayerCamera missing")
	row["objective_ui_exists"] = objective_ui != null
	row["objective_label_exists"] = objective_label is Label
	if objective_ui == null:
		row["errors"].append("ObjectiveUI missing")
	if not objective_label is Label:
		row["errors"].append("ObjectiveStatusLabel missing")
	for target in TARGETS:
		var area := scene.find_child(str(target["checkpoint"]), true, false)
		if area is Area3D:
			var checkpoint := area as Area3D
			checkpoint.monitoring = true
			checkpoint.monitorable = true
			checkpoint.body_entered.connect(_on_objective_body_entered.bind(str(checkpoint.get_path()), str(checkpoint.get_meta("objective_type", "")), str(checkpoint.get_meta("objective_id", "")), str(target["checkpoint"])))
			row["connected_objectives"] += 1
		else:
			row["errors"].append("checkpoint missing: %s" % str(target["checkpoint"]))
	var finish := scene.find_child(FINISH_NAME, true, false)
	if finish is Area3D:
		var finish_area := finish as Area3D
		finish_area.monitoring = true
		finish_area.monitorable = true
		finish_area.body_entered.connect(_on_objective_body_entered.bind(str(finish_area.get_path()), str(finish_area.get_meta("objective_type", "")), "finish", FINISH_NAME))
		row["connected_objectives"] += 1
	else:
		row["errors"].append("finish missing")
	row["pass"] = row["errors"].is_empty() and row["connected_objectives"] == TARGETS.size() + 1
	return row

func _ensure_input_map() -> Dictionary:
	var actions := {
		"move_forward": KEY_W,
		"move_backward": KEY_S,
		"move_left": KEY_A,
		"move_right": KEY_D
	}
	var rows: Array = []
	for action in actions.keys():
		if InputMap.has_action(action):
			InputMap.erase_action(action)
		InputMap.add_action(action)
		var event := InputEventKey.new()
		event.keycode = int(actions[action])
		event.physical_keycode = int(actions[action])
		InputMap.action_add_event(action, event)
		rows.append({"action": action, "keycode": int(actions[action]), "event_count": InputMap.action_get_events(action).size()})
	return {"pass": rows.size() == actions.size(), "actions": rows}

func _run_collision_path(scene: Node, player: CharacterBody3D, camera: Camera3D, target: Dictionary) -> Dictionary:
	var target_name := str(target["collider"])
	var objective_id := str(target["id"])
	var row := {"id": objective_id, "collider": target_name, "input_ticks": [], "collision_detected": false, "checkpoint_collected": false, "pass": false, "errors": []}
	var body := scene.find_child(target_name, true, false)
	if body == null or not body is StaticBody3D:
		row["errors"].append("target StaticBody3D missing")
		return row
	var shape_node := body.get_node_or_null("CollisionProxy")
	if not (shape_node is CollisionShape3D) or not ((shape_node as CollisionShape3D).shape is BoxShape3D):
		row["errors"].append("target CollisionProxy missing")
		return row
	var box := (shape_node as CollisionShape3D).shape as BoxShape3D
	var center := (body as StaticBody3D).global_position
	player.global_position = Vector3(center.x, PLAYER_Y, center.z + box.size.z * 0.5 + 0.72)
	player.velocity = Vector3.ZERO
	await physics_frame
	_record_camera_variants(scene, player, camera, "start_%s" % objective_id)
	for index in range(MAX_STEPS):
		var tick := await _step_with_key(scene, player, camera, "move_forward", "approach_%s" % objective_id)
		row["input_ticks"].append(tick)
		if bool(tick.get("collision", false)):
			row["collision_detected"] = true
			row["collider_name"] = tick.get("collider_name", "")
			row["checkpoint_collected"] = collected.has(objective_id)
			row["pass"] = row["collider_name"] == target_name and row["checkpoint_collected"]
			if not row["pass"]:
				row["errors"].append("collision or checkpoint gate failed")
			return row
	row["checkpoint_collected"] = collected.has(objective_id)
	row["errors"].append("no collision detected within max steps")
	return row

func _run_finish_attempt(scene: Node, player: CharacterBody3D, camera: Camera3D, label: String) -> Dictionary:
	var before_count := finish_attempts.size()
	var row := {"label": label, "input_ticks": [], "accepted": false, "signal_received": false, "pass": false, "errors": []}
	player.global_position = FINISH_CENTER + Vector3(-0.78, 0.0, 0.0)
	player.velocity = Vector3.ZERO
	await physics_frame
	_record_camera_variants(scene, player, camera, "%s_start" % label)
	for index in range(12):
		var tick := await _step_with_key(scene, player, camera, "move_right", label)
		row["input_ticks"].append(tick)
		if bool(tick.get("collision", false)):
			row["errors"].append("finish path collided")
			return row
		if finish_attempts.size() > before_count:
			var event: Dictionary = finish_attempts[finish_attempts.size() - 1]
			row["accepted"] = bool(event.get("accepted", false))
			row["signal_received"] = true
			row["pass"] = label == "finish_before_unlock" and not row["accepted"] or label == "finish_after_unlock" and row["accepted"]
			return row
	row["errors"].append("finish signal gate failed")
	return row

func _step_with_key(scene: Node, player: CharacterBody3D, camera: Camera3D, action: String, label: String) -> Dictionary:
	var press := _emit_key_action(action, true)
	var vector := _current_input_vector()
	var before := player.global_position
	var motion: Vector3 = vector * MOVE_STEP
	var collision := player.move_and_collide(motion)
	await physics_frame
	current_tick += 1
	var release := _emit_key_action(action, false)
	var tick := {
		"tick": current_tick,
		"label": label,
		"action": action,
		"key_event_press": press,
		"key_event_release": release,
		"input_vector": _vec(vector),
		"before": _vec(before),
		"after": _vec(player.global_position),
		"moved_distance": before.distance_to(player.global_position),
		"collision": collision != null,
		"event_count": event_trace.size(),
		"collected": collected.duplicate()
	}
	if collision != null:
		var collider := collision.get_collider()
		tick["collider_name"] = str(collider.name) if collider != null else ""
		tick["collision_position"] = _vec(collision.get_position())
		tick["collision_normal"] = _vec(collision.get_normal())
	input_trace.append(tick)
	_record_ui_state(scene, label)
	_record_camera_variants(scene, player, camera, label)
	return tick

func _emit_key_action(action: String, pressed: bool) -> Dictionary:
	var events := InputMap.action_get_events(action)
	var keycode := 0
	if events.size() > 0 and events[0] is InputEventKey:
		keycode = int((events[0] as InputEventKey).keycode)
	var event := InputEventKey.new()
	event.keycode = keycode
	event.physical_keycode = keycode
	event.pressed = pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()
	return {"action": action, "pressed": pressed, "keycode": keycode, "action_state_after": Input.is_action_pressed(action)}

func _current_input_vector() -> Vector3:
	var x: float = Input.get_action_strength("move_right") - Input.get_action_strength("move_left")
	var z: float = Input.get_action_strength("move_backward") - Input.get_action_strength("move_forward")
	var vector := Vector3(x, 0.0, z)
	if vector.length() > 1.0:
		return vector.normalized()
	return vector

func _record_camera_variants(scene: Node, player: CharacterBody3D, camera: Camera3D, label: String) -> void:
	for variant in CAMERA_VARIANTS:
		var row := _evaluate_camera_variant(scene, player, camera, label, variant)
		camera_trace.append(row)

func _evaluate_camera_variant(scene: Node, player: CharacterBody3D, camera: Camera3D, label: String, variant: Dictionary) -> Dictionary:
	var offset: Vector3 = variant["offset"]
	var target := player.global_position + CAMERA_TARGET_OFFSET
	var expected_position := player.global_position + offset
	camera.global_position = expected_position
	camera.look_at(target, Vector3.UP)
	var forward := -camera.global_transform.basis.z.normalized()
	var to_target := (target - camera.global_position).normalized()
	var dot := forward.dot(to_target)
	var distance := camera.global_position.distance_to(target)
	var frustum_contains := true
	if camera.has_method("is_position_in_frustum"):
		frustum_contains = camera.is_position_in_frustum(target)
	var obstruction := _ray_obstruction(scene, camera.global_position, target, player)
	var pass_gate: bool = dot >= CAMERA_DOT_MIN and distance >= float(variant["distance_min"]) and distance <= float(variant["distance_max"]) and frustum_contains and not obstruction.get("blocked", false)
	return {
		"tick": current_tick,
		"label": label,
		"variant": str(variant["id"]),
		"camera_position": _vec(camera.global_position),
		"target": _vec(target),
		"forward_dot_target": dot,
		"distance_to_target": distance,
		"frustum_contains_target": frustum_contains,
		"obstruction": obstruction,
		"pass": pass_gate
	}

func _ray_obstruction(scene: Node, from_point: Vector3, to_point: Vector3, player: CharacterBody3D) -> Dictionary:
	if not scene is Node3D:
		return {"blocked": false, "reason": "scene_not_node3d"}
	var query := PhysicsRayQueryParameters3D.create(from_point, to_point)
	query.exclude = [player.get_rid()]
	var hit := (scene as Node3D).get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return {"blocked": false}
	var collider: Variant = hit.get("collider", null)
	return {"blocked": true, "collider": str(collider.name) if collider != null and collider is Node else str(collider), "position": _vec(hit.get("position", Vector3.ZERO))}

func _run_camera_obstruction_counter(scene: Node, player: CharacterBody3D, camera: Camera3D) -> Dictionary:
	var body := scene.find_child("triposr_p5_synthetic_block_Collider", true, false)
	if not body is StaticBody3D:
		return {"pass": false, "error": "block collider missing"}
	var shape_node := body.get_node_or_null("CollisionProxy")
	if not (shape_node is CollisionShape3D) or not ((shape_node as CollisionShape3D).shape is BoxShape3D):
		return {"pass": false, "error": "block collider shape missing"}
	var box := (shape_node as CollisionShape3D).shape as BoxShape3D
	var center := (body as StaticBody3D).global_position
	var from_point := center + Vector3(0.0, 0.0, box.size.z * 0.75 + 0.4)
	var to_point := center - Vector3(0.0, 0.0, box.size.z * 0.75 + 0.4)
	var obstruction := _ray_obstruction(scene, from_point, to_point, player)
	return {"pass": obstruction.get("blocked", false) and obstruction.get("collider", "") == str(body.name), "from": _vec(from_point), "to": _vec(to_point), "obstruction": obstruction}

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

func _objective_status_text(finished: bool) -> String:
	if finished:
		return "Checkpoints %d/%d | Finish reached" % [collected.size(), TARGETS.size()]
	var lock_state := "unlocked" if collected.size() == TARGETS.size() else "locked"
	return "Checkpoints %d/%d | Finish %s" % [collected.size(), TARGETS.size(), lock_state]

func _record_ui_state(scene: Node, label: String) -> void:
	var objective_label := scene.find_child(OBJECTIVE_LABEL_NAME, true, false)
	if not objective_label is Label:
		ui_trace.append({"tick": current_tick, "label": label, "pass": false, "error": "ObjectiveStatusLabel missing"})
		return
	var finished := false
	if finish_attempts.size() > 0:
		var latest: Dictionary = finish_attempts[finish_attempts.size() - 1]
		finished = bool(latest.get("accepted", false))
	var text := _objective_status_text(finished)
	(objective_label as Label).text = text
	ui_trace.append({
		"tick": current_tick,
		"label": label,
		"text": text,
		"collected_count": collected.size(),
		"finish_unlocked": collected.size() == TARGETS.size(),
		"finished": finished,
		"pass": true
	})

func _objective_ui_summary() -> Dictionary:
	var texts: Array = []
	var failed := 0
	for row in ui_trace:
		if not row.get("pass", false):
			failed += 1
		texts.append(str(row.get("text", "")))
	var required := [
		"Checkpoints 0/3 | Finish locked",
		"Checkpoints 1/3 | Finish locked",
		"Checkpoints 2/3 | Finish locked",
		"Checkpoints 3/3 | Finish unlocked",
		"Checkpoints 3/3 | Finish reached",
	]
	var missing: Array = []
	for item in required:
		if not texts.has(item):
			missing.append(item)
	return {
		"pass": ui_trace.size() > 0 and failed == 0 and missing.is_empty(),
		"sample_count": ui_trace.size(),
		"failed_count": failed,
		"required_states": required,
		"missing_states": missing,
		"unique_texts": _unique_strings(texts)
	}

func _trace_diff(actual: Array, expected: Array) -> Dictionary:
	var mismatches: Array = []
	var max_len: int = max(actual.size(), expected.size())
	for index in range(max_len):
		var actual_value := str(actual[index]) if index < actual.size() else "<missing>"
		var expected_value := str(expected[index]) if index < expected.size() else "<extra>"
		if actual_value != expected_value:
			mismatches.append({"index": index, "actual": actual_value, "expected": expected_value})
	return {"pass": mismatches.is_empty(), "actual": actual, "expected": expected, "mismatches": mismatches}

func _unique_strings(values: Array) -> Array:
	var seen := {}
	var out: Array = []
	for value in values:
		var key := str(value)
		if not seen.has(key):
			seen[key] = true
			out.append(key)
	return out

func _input_key_event_summary() -> Dictionary:
	var failed := 0
	for row in input_trace:
		var press: Dictionary = row.get("key_event_press", {})
		var release: Dictionary = row.get("key_event_release", {})
		if not bool(press.get("action_state_after", false)) or bool(release.get("action_state_after", true)):
			failed += 1
	return {"pass": input_trace.size() > 0 and failed == 0, "sample_count": input_trace.size(), "failed_count": failed}

func _camera_summary() -> Dictionary:
	var failed := 0
	var by_variant := {}
	for row in camera_trace:
		var variant := str(row.get("variant", "unknown"))
		if not by_variant.has(variant):
			by_variant[variant] = {"samples": 0, "failed": 0}
		by_variant[variant]["samples"] += 1
		if not row.get("pass", false):
			failed += 1
			by_variant[variant]["failed"] += 1
	return {"pass": camera_trace.size() > 0 and failed == 0, "sample_count": camera_trace.size(), "failed_count": failed, "by_variant": by_variant}

func _event_reasons() -> Array:
	var reasons: Array = []
	for event in event_trace:
		reasons.append(event.get("reason", ""))
	return reasons

func _all_clearance_rows_pass(rows: Array) -> bool:
	if rows.size() != TARGETS.size():
		return false
	for row in rows:
		if not row.get("pass", false):
			return false
	return true

func _set_owner_recursive(node: Node, owner: Node) -> void:
	node.owner = owner
	for child in node.get_children():
		_set_owner_recursive(child, owner)

func _vec(value: Vector3) -> Dictionary:
	return {"x": value.x, "y": value.y, "z": value.z}

func _write_report(report: Dictionary, exit_code: int) -> void:
	var file := FileAccess.open(OUTPUT_JSON, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify(report))
	quit(exit_code)
