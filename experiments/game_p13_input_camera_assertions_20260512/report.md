# P13-A Game Input/Camera Assertions Report

Status: P13-A HomePC headless run passed with an explicit sensor-clearance repair and a disabled-repair counter-run.

Purpose: advance P12 deterministic replay beyond event ordering by adding input-vector replay, `CharacterBody3D.move_and_collide`, camera follow/framing assertions, and objective-loop ordering in one local Godot 4.4.1 probe.

Commands:

```bash
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p13_input_camera_assertions_20260512
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p13_input_camera_assertions_20260512
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "cd '$REMOTE/project'; env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' P13_DISABLE_SENSOR_CLEARANCE_REPAIR=1 /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/simulate_input_camera_assertions.gd > '$REMOTE/godot_p13_input_camera_assertions_without_repair.log' 2>&1 || true"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "cd '$REMOTE/project'; env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/simulate_input_camera_assertions.gd > '$REMOTE/godot_p13_input_camera_assertions.log' 2>&1"
```

Result:

- Final repaired run: `pass=true`.
- Collision loop: `3/3` asset collider paths passed via `CharacterBody3D.move_and_collide`.
- Objective loop: event reasons matched `finish_locked`, `checkpoint_collected`, `checkpoint_collected`, `checkpoint_collected`, `finish_unlocked`.
- Camera gate: `28/28` samples passed, target dot `>= 0.98`, distance within `5.0..6.2`, follow error `<= 0.001`, target in frustum.
- Input replay: `23` deterministic ticks recorded with action labels and input vectors.

Counter-run:

- `P13_DISABLE_SENSOR_CLEARANCE_REPAIR=1` produced `pass=false`.
- Failure was not a camera or collision failure. It showed the inherited P10 `Checkpoint_Block` sensor front at `z=0.897724`, behind the block collider front at `z=0.917724`, so the player collision body could hit the block before the Area3D checkpoint fired.
- Final P13 run applies a scene-authoring repair only to `Checkpoint_Block`, extending the trigger front by `0.0599996`. This is counted as a P13 repair, not as proof that P10 was already correct.

Artifacts:

- `outputs/p13_input_camera_assertions_report.json`
- `outputs/p13_input_camera_assertions_without_sensor_repair_report.json`
- `outputs/godot_p13_input_camera_assertions_homepc.log`
- `outputs/godot_p13_input_camera_assertions_without_repair_homepc.log`
- `outputs/artifact_hashes.json`

Boundary:

- This proves deterministic headless input/collision/objective/camera assertions over the local three-asset scene.
- It does not prove screenshot availability, visual composition quality, or human controller feel.
