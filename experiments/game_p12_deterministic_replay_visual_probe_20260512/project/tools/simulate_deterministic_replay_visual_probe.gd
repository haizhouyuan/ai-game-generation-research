extends SceneTree

const SCENE_PATH := "res://scenes/p10_objective_scene.tscn"
const CHECKPOINTS := ["Checkpoint_Chair", "Checkpoint_Block", "Checkpoint_Tower"]
const FINISH_NAME := "Finish_Area"
const AWAY := Vector3(12.0, 3.0, 12.0)
const OUTPUT_JSON := "res://outputs/p12_deterministic_replay_visual_probe_report.json"
const OUTPUT_PNG := "res://outputs/p12_visual_probe.png"

var event_trace: Array = []
var collected: Array = []
var finish_attempts: Array = []
var tick_trace: Array = []
var current_tick := 0

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://outputs"))
	var report := {
		"scene_path": SCENE_PATH,
		"simulation_mode": "deterministic tick replay plus headless viewport screenshot feasibility probe",
		"no_proxy_note": "Godot run is local/offline on HomePC with proxy variables unset by the caller.",
		"node_paths": {},
		"replay_plan": [],
		"tick_trace": [],
		"event_trace": [],
		"visual_probe": {},
		"fallback": {
			"used": false,
			"note": "No fallback is counted as signal or screenshot pass."
		},
		"summary": {}
	}
	var packed := ResourceLoader.load(SCENE_PATH)
	if packed == null or not packed is PackedScene:
		report["summary"] = {"pass": false, "stage": "load", "error": "P10 objective scene did not load"}
		_write_report(report, 1)
		return
	var root: Node = (packed as PackedScene).instantiate()
	get_root().add_child(root)
	var probe := _make_probe()
	root.add_child(probe)
	probe.owner = root
	var setup := _connect_objective_signals(root)
	report["node_paths"] = setup
	if not setup.get("pass", false):
		report["summary"] = {"pass": false, "stage": "setup"}
		root.queue_free()
		_write_report(report, 1)
		return
	await physics_frame

	var plan := _make_replay_plan(root)
	report["replay_plan"] = plan
	for step in plan:
		await _walk_probe(probe, step)

	var visual_probe := await _probe_screenshot()
	var reasons := _event_reasons()
	var signal_passed := reasons == ["finish_locked", "checkpoint_collected", "checkpoint_collected", "checkpoint_collected", "finish_unlocked"]
	var tick_passed := tick_trace.size() == _expected_tick_count(plan)
	var visual_passed := bool(visual_probe.get("saved", false)) and int(visual_probe.get("width", 0)) > 0 and int(visual_probe.get("height", 0)) > 0
	report["tick_trace"] = tick_trace
	report["event_trace"] = event_trace
	report["visual_probe"] = visual_probe
	report["summary"] = {
		"pass": signal_passed and tick_passed,
		"signal_passed": signal_passed,
		"tick_trace_passed": tick_passed,
		"visual_screenshot_passed": visual_passed,
		"visual_screenshot_blocker": "" if visual_passed else str(visual_probe.get("blocker", "headless screenshot unavailable")),
		"event_count": event_trace.size(),
		"tick_count": tick_trace.size(),
		"event_reasons": reasons,
		"collected": collected,
		"finish_attempts": finish_attempts.size()
	}
	root.queue_free()
	_write_report(report, 0 if report["summary"]["pass"] else 2)

func _make_probe() -> Area3D:
	var probe := Area3D.new()
	probe.name = "ObjectiveProbe"
	probe.monitoring = true
	probe.monitorable = true
	probe.collision_layer = 1
	probe.collision_mask = 1
	probe.position = AWAY
	var shape_node := CollisionShape3D.new()
	shape_node.name = "ProbeShape"
	var shape := SphereShape3D.new()
	shape.radius = 0.18
	shape_node.shape = shape
	probe.add_child(shape_node)
	return probe

func _connect_objective_signals(root: Node) -> Dictionary:
	var row := {"checkpoint_paths": [], "finish_path": null, "connected_count": 0, "pass": false, "errors": []}
	for checkpoint_name in CHECKPOINTS:
		var node := root.find_child(checkpoint_name, true, false)
		if not node is Area3D:
			row["errors"].append("checkpoint Area3D missing: %s" % checkpoint_name)
			continue
		var area := node as Area3D
		area.monitoring = true
		area.monitorable = true
		area.area_entered.connect(_on_objective_area_entered.bind(str(area.get_path()), str(area.get_meta("objective_type", "")), str(area.get_meta("objective_id", "")), checkpoint_name))
		row["checkpoint_paths"].append(str(area.get_path()))
		row["connected_count"] += 1
	var finish := root.find_child(FINISH_NAME, true, false)
	if finish is Area3D:
		var finish_area := finish as Area3D
		finish_area.monitoring = true
		finish_area.monitorable = true
		finish_area.area_entered.connect(_on_objective_area_entered.bind(str(finish_area.get_path()), str(finish_area.get_meta("objective_type", "")), "finish", FINISH_NAME))
		row["finish_path"] = str(finish_area.get_path())
		row["connected_count"] += 1
	else:
		row["errors"].append("finish Area3D missing")
	row["pass"] = row["connected_count"] == CHECKPOINTS.size() + 1 and row["errors"].is_empty()
	return row

func _make_replay_plan(root: Node) -> Array:
	var plan: Array = []
	var finish := root.find_child(FINISH_NAME, true, false) as Area3D
	plan.append({"label": "finish_before_unlock", "target": _vec(finish.global_position), "ticks": 6})
	plan.append({"label": "away_after_locked_finish", "target": _vec(AWAY), "ticks": 3})
	for checkpoint_name in CHECKPOINTS:
		var checkpoint := root.find_child(checkpoint_name, true, false) as Area3D
		plan.append({"label": "checkpoint_%s" % checkpoint_name, "target": _vec(checkpoint.global_position), "ticks": 6})
		plan.append({"label": "away_after_%s" % checkpoint_name, "target": _vec(AWAY), "ticks": 3})
	plan.append({"label": "finish_after_unlock", "target": _vec(finish.global_position), "ticks": 6})
	plan.append({"label": "away_after_unlocked_finish", "target": _vec(AWAY), "ticks": 3})
	return plan

func _walk_probe(probe: Area3D, step: Dictionary) -> void:
	var from_position := probe.global_position
	var target := _dict_to_vec(step["target"])
	var ticks := int(step.get("ticks", 1))
	for index in range(ticks):
		var alpha := float(index + 1) / float(ticks)
		probe.global_position = from_position.lerp(target, alpha)
		await physics_frame
		current_tick += 1
		tick_trace.append({
			"tick": current_tick,
			"label": step["label"],
			"position": _vec(probe.global_position),
			"event_count": event_trace.size(),
			"collected": collected.duplicate()
		})

func _on_objective_area_entered(other_area: Area3D, objective_path: String, objective_type: String, objective_id: String, objective_name: String) -> void:
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
		if collected.size() == CHECKPOINTS.size():
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
		"other_area": str(other_area.get_path()),
		"accepted": accepted,
		"reason": reason,
		"collected_snapshot": collected.duplicate()
	}
	event_trace.append(event)
	if objective_type == "finish":
		finish_attempts.append(event)

func _probe_screenshot() -> Dictionary:
	var row := {
		"attempted": true,
		"mode": "headless viewport texture readback",
		"saved": false,
		"output_path": ProjectSettings.globalize_path(OUTPUT_PNG),
		"blocker": ""
	}
	await process_frame
	await physics_frame
	var viewport := get_root()
	if viewport == null:
		row["blocker"] = "SceneTree root viewport unavailable"
		return row
	var texture := viewport.get_texture()
	if texture == null:
		row["blocker"] = "Viewport texture unavailable in headless mode"
		return row
	var image := texture.get_image()
	if image == null or image.get_width() <= 0 or image.get_height() <= 0:
		row["blocker"] = "Viewport image empty in headless mode"
		return row
	var save_error := image.save_png(ProjectSettings.globalize_path(OUTPUT_PNG))
	row["width"] = image.get_width()
	row["height"] = image.get_height()
	row["save_error"] = int(save_error)
	row["non_empty_sample_count"] = _sample_non_empty_pixels(image)
	row["saved"] = save_error == OK
	if not row["saved"]:
		row["blocker"] = "Image.save_png returned error %s" % int(save_error)
	return row

func _sample_non_empty_pixels(image: Image) -> int:
	var count := 0
	var step_x = max(1, int(image.get_width() / 16))
	var step_y = max(1, int(image.get_height() / 16))
	for x in range(0, image.get_width(), step_x):
		for y in range(0, image.get_height(), step_y):
			var c := image.get_pixel(x, y)
			if c.a > 0.01 and (c.r + c.g + c.b) > 0.01:
				count += 1
	return count

func _event_reasons() -> Array:
	var reasons: Array = []
	for event in event_trace:
		reasons.append(event.get("reason", ""))
	return reasons

func _expected_tick_count(plan: Array) -> int:
	var total := 0
	for step in plan:
		total += int(step.get("ticks", 0))
	return total

func _vec(value: Vector3) -> Dictionary:
	return {"x": value.x, "y": value.y, "z": value.z}

func _dict_to_vec(value: Dictionary) -> Vector3:
	return Vector3(float(value["x"]), float(value["y"]), float(value["z"]))

func _write_report(report: Dictionary, exit_code: int) -> void:
	var file := FileAccess.open(OUTPUT_JSON, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify(report))
	quit(exit_code)
