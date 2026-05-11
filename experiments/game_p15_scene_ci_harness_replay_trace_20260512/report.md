# P15-A Game Scene CI Harness Replay Trace Report

Status: P15-A HomePC headless run passed.

Purpose: turn the P14 scene-builder gate into a reusable CI-style harness and add objective UI/state feedback plus replay trace diffing while preserving the existing no-proxy/headless path.

Command:

```bash
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p15_scene_ci_harness_replay_trace_20260512
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p15_scene_ci_harness_replay_trace_20260512
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "rm -rf '$REMOTE' && mkdir -p '$REMOTE'"
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/scene_ci_harness_replay_trace.gd > '$REMOTE/godot_p15_scene_ci_harness_replay_trace.log' 2>&1"
```

Result:

- Scene-builder CI harness created `res://scenes/p15_ci_objective_scene.tscn` from the P7 base scene.
- Sensor clearance and readback passed for all three checkpoint sensors.
- Objective UI feedback passed: required states were observed from `Checkpoints 0/3 | Finish locked` through `Checkpoints 3/3 | Finish reached`.
- Replay trace diff passed: actual event reasons matched `finish_locked -> checkpoint_collected -> checkpoint_collected -> checkpoint_collected -> finish_unlocked`.
- InputMap key-event replay passed with `23` deterministic ticks and `0` failed key-state samples.
- Collision loop passed for `3/3` assets using `CharacterBody3D.move_and_collide`.
- Camera variants passed `84/84` samples across standard, close, and high follow variants.
- Obstruction counter passed by ray-hitting `triposr_p5_synthetic_block_Collider`.

Artifacts:

- `project/tools/scene_ci_harness_replay_trace.gd`
- `project/scenes/p15_ci_objective_scene.tscn`
- `outputs/p15_scene_ci_harness_replay_trace_report.json`
- `outputs/godot_p15_scene_ci_harness_replay_trace_homepc.log`
- `outputs/godot_p15_scene_ci_harness_replay_trace_verify_homepc.log`
- `outputs/artifact_hashes.json`

Boundary:

- This is a CI-style headless engine assertion harness, not rendered screenshot proof.
- Collision remains proxy-collider based, not mesh-accurate.
- The harness validates one deterministic route over three assets; broader layouts and replay fixtures remain P16 work.
