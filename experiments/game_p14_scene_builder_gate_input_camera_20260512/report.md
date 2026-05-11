# P14-A Game Scene Builder Gate, Input Replay, And Camera Assertions Report

Status: P14-A HomePC headless run passed.

Purpose: promote the P13 sensor-clearance repair into a scene-builder gate, then validate deterministic InputMap/key-event replay, three asset collision paths, objective ordering, camera framing variations, and an obstruction counter in one Godot 4.4.1 headless run.

Command:

```bash
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p14_scene_builder_gate_input_camera_20260512
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p14_scene_builder_gate_input_camera_20260512
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "rm -rf '$REMOTE' && mkdir -p '$REMOTE'"
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/build_scene_gate_and_replay_input_camera.gd > '$REMOTE/godot_p14_scene_builder_gate_input_camera.log' 2>&1"
```

Result:

- Scene-builder gate: created `res://scenes/p14_objective_scene.tscn` with `ObjectiveRoot`, three checkpoint `Area3D` nodes, and one finish `Area3D`.
- Sensor clearance: all three checkpoint sensors pass after scene-build repair and readback; repair deltas were chair `0.3125706547`, block `0.5799999619`, tower `0.3624567473`.
- Objective ordering: `finish_locked -> checkpoint_collected -> checkpoint_collected -> checkpoint_collected -> finish_unlocked`.
- Collision loop: `3/3` assets passed with `CharacterBody3D.move_and_collide` against existing proxy colliders.
- Input replay: `23` deterministic ticks passed with InputMap key events and flushed buffered input.
- Camera gate: `84/84` variant samples passed across `standard_follow`, `close_follow`, and `high_follow`.
- Obstruction counter: ray through the block collider hit `triposr_p5_synthetic_block_Collider`, proving obstruction detection can fail a blocked line.

Artifacts:

- `project/tools/build_scene_gate_and_replay_input_camera.gd`
- `project/scenes/p14_objective_scene.tscn`
- `outputs/p14_scene_builder_gate_input_camera_report.json`
- `outputs/godot_p14_scene_builder_gate_input_camera_homepc.log`
- `outputs/godot_p14_scene_builder_gate_input_camera_verify_homepc.log`
- `outputs/artifact_hashes.json`

Boundary:

- This is a headless engine-assertion gate, not a visual screenshot or human controller-feel proof.
- Collision remains proxy-collider based, not mesh-accurate collision.
- The Godot log still records raw `.glb` ext_resource loader/import warnings in headless mode; P14 does not claim rendered GLB visual validation.
- The key-event path needed `Input.flush_buffered_events()` after `Input.parse_input_event()` to make press/release assertions deterministic in headless.
