extends SceneTree

const SCENE_PATH := "res://scenes/p10_objective_scene.tscn"
const CHECKPOINTS := ["Checkpoint_Chair", "Checkpoint_Block", "Checkpoint_Tower"]
const FINISH_NAME := "Finish_Area"
const AWAY := Vector3(12.0, 3.0, 12.0)

var event_trace: Array = []
var collected: Array = []
var finish_attempts: Array = []
var signal_mode_passed := false

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://outputs"))
	var report := {
		"scene_path": SCENE_PATH,
		"simulation_mode": "Area3D.area_entered signal replay with ObjectiveProbe Area3D",
		"no_proxy_note": "Godot run is local/offline on HomePC with proxy variables unset by the caller.",
		"node_paths": {},
		"event_trace": [],
		"fallback": {},
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

	var finish := root.find_child(FINISH_NAME, true, false) as Area3D
	await _move_probe_to(probe, finish.global_position)
	var pre_finish_attempt: Dictionary = finish_attempts[finish_attempts.size() - 1] if finish_attempts.size() > 0 else {}
	await _move_probe_to(probe, AWAY)

	for checkpoint_name in CHECKPOINTS:
		var checkpoint := root.find_child(checkpoint_name, true, false) as Area3D
		await _move_probe_to(probe, checkpoint.global_position)
		await _move_probe_to(probe, AWAY)

	await _move_probe_to(probe, finish.global_position)
	var post_finish_attempt: Dictionary = finish_attempts[finish_attempts.size() - 1] if finish_attempts.size() > 0 else {}
	await _move_probe_to(probe, AWAY)

	var signal_summary := {
		"event_count": event_trace.size(),
		"checkpoint_events": _event_count("checkpoint"),
		"finish_events": _event_count("finish"),
		"pre_finish_locked": pre_finish_attempt.get("accepted", true) == false,
		"pre_finish_signal_received": pre_finish_attempt.size() > 0,
		"post_finish_accepted": post_finish_attempt.get("accepted", false),
		"collected_count": collected.size(),
		"collected": collected,
	}
	signal_mode_passed = signal_summary["pre_finish_signal_received"] \
		and signal_summary["pre_finish_locked"] \
		and signal_summary["checkpoint_events"] >= CHECKPOINTS.size() \
		and signal_summary["finish_events"] >= 2 \
		and signal_summary["post_finish_accepted"] \
		and signal_summary["collected_count"] == CHECKPOINTS.size()
	report["event_trace"] = event_trace
	report["fallback"] = {
		"used": false,
		"note": "No deterministic fallback was used for pass. If signal replay fails in a future run, fallback must be reported separately and cannot be counted as signal pass."
	}
	report["summary"] = signal_summary
	report["summary"]["signal_mode_passed"] = signal_mode_passed
	report["summary"]["pass"] = signal_mode_passed
	root.queue_free()
	_write_report(report, 0 if signal_mode_passed else 2)

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
		area.area_entered.connect(_on_objective_area_entered.bind(str(area.get_path()), str(area.get_meta("objective_type", "")), str(area.get_meta("objective_id", ""))))
		row["checkpoint_paths"].append(str(area.get_path()))
		row["connected_count"] += 1
	var finish := root.find_child(FINISH_NAME, true, false)
	if finish is Area3D:
		var finish_area := finish as Area3D
		finish_area.monitoring = true
		finish_area.monitorable = true
		finish_area.area_entered.connect(_on_objective_area_entered.bind(str(finish_area.get_path()), str(finish_area.get_meta("objective_type", "")), "finish"))
		row["finish_path"] = str(finish_area.get_path())
		row["connected_count"] += 1
	else:
		row["errors"].append("finish Area3D missing")
	row["pass"] = row["connected_count"] == CHECKPOINTS.size() + 1 and row["errors"].is_empty()
	return row

func _on_objective_area_entered(other_area: Area3D, objective_path: String, objective_type: String, objective_id: String) -> void:
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
		"objective_path": objective_path,
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

func _move_probe_to(probe: Area3D, position: Vector3) -> void:
	probe.global_position = position
	await physics_frame
	await physics_frame

func _event_count(objective_type: String) -> int:
	var count := 0
	for event in event_trace:
		if event.get("objective_type", "") == objective_type:
			count += 1
	return count

func _write_report(report: Dictionary, exit_code: int) -> void:
	var file := FileAccess.open("res://outputs/p11_area3d_signal_replay_report.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify(report))
	quit(exit_code)
