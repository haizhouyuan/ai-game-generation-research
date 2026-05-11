# P17-A Game Negative Scene-CI Fixtures Report

Status: P17-A HomePC headless run passed.

Purpose: extend the P16 multi-layout Godot scene CI harness with negative fixtures that prove the harness catches broken objective nodes, wrong route expectations, finish-lock regressions, sensor-clearance failures, and camera obstruction failures.

Command:

```bash
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p17_negative_scene_ci_fixtures_20260512
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p17_negative_scene_ci_fixtures_20260512
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "rm -rf '$REMOTE' && mkdir -p '$REMOTE'"
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/scene_ci_negative_fixtures.gd > '$REMOTE/project/outputs/godot_p17_negative_scene_ci_fixtures.log' 2>&1"
```

Result:

- Positive matrix remained green: `3/3` layouts passed with distinct route signatures.
- `missing_checkpoint` was detected by scene readback after a checkpoint node was removed.
- `route_mismatch` was detected by replay trace diff when expected checkpoint order was intentionally wrong.
- `finish_before_checkpoints` was detected when a forced early-finish bug made the pre-checkpoint finish attempt accepted.
- `sensor_clearance_violation` was detected by disabling builder repair and placing sensors behind/inside the collider front.
- `camera_obstruction_failure` was detected by injecting a blocking scene node between the camera and target.

Artifacts:

- `outputs/p17_negative_scene_ci_fixtures_report.json`
- `outputs/godot_p17_negative_scene_ci_fixtures.log`
- `outputs/artifact_hashes.json`
- Generated P17 scene files under `project/scenes/`.

Boundary:

- Authority is proxy scene nodes plus Godot headless physics/input/camera assertions.
- No screenshot, visual QA, human-feel QA, or mesh-accurate GLB collision claim is made.
- HomePC execution was local/offline with proxy variables unset and `NO_PROXY='*'`; no assets, models, or display stack were downloaded or installed.
