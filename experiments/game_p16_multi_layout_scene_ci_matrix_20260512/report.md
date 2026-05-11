# P16-A Game Multi-Layout Scene CI Matrix Report

Status: P16-A HomePC headless run passed.

Purpose: extend the P15 single-fixture Godot scene CI harness into a multi-layout, multi-route matrix without installing software, downloading assets, or reopening the blocked screenshot path.

Command:

```bash
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p16_multi_layout_scene_ci_matrix_20260512
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p16_multi_layout_scene_ci_matrix_20260512
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "rm -rf '$REMOTE' && mkdir -p '$REMOTE'"
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/scene_ci_multi_layout_matrix.gd > '$REMOTE/godot_p16_multi_layout_scene_ci_matrix.log' 2>&1"
scp yuanhaizhou@192.168.1.17:"$REMOTE/project/outputs/p16_multi_layout_scene_ci_matrix_report.json" "$LOCAL/outputs/"
scp yuanhaizhou@192.168.1.17:"$REMOTE/godot_p16_multi_layout_scene_ci_matrix.log" "$LOCAL/outputs/godot_p16_multi_layout_scene_ci_matrix_homepc.log"
```

Result:

- Matrix passed for `3/3` layouts: `front_linear`, `front_reverse`, and `front_staggered`.
- Route trace diff passed with distinct signatures:
  - `finish>chair>block>tower>finish`
  - `finish>tower>block>chair>finish`
  - `finish>block>chair>tower>finish`
- Each layout passed scene-builder checkpoint creation, saved-scene readback, sensor-clearance gates, objective UI/state feedback, InputMap key-event replay, `3/3` CharacterBody collision paths, ordered checkpoint/finish events, `84/84` camera samples, and obstruction counter.
- No screenshot or visual QA claim was made; the script explicitly marks the visual path as not attempted in P16.
- The Godot log still contains inherited GLB loader warnings from the copied P7 scene references. The P16 pass is based on saved proxy-collider scene nodes and headless physics assertions, not GLB visual import proof.

Artifacts:

- `project/tools/scene_ci_multi_layout_matrix.gd`
- `project/scenes/p16_front_linear_ci_scene.tscn`
- `project/scenes/p16_front_reverse_ci_scene.tscn`
- `project/scenes/p16_front_staggered_ci_scene.tscn`
- `outputs/p16_multi_layout_scene_ci_matrix_report.json`
- `outputs/godot_p16_multi_layout_scene_ci_matrix_homepc.log`
- `outputs/artifact_hashes.json`

Boundary:

- This is a deterministic headless engine assertion matrix, not rendered visual QA.
- Collision remains proxy-collider based, not mesh-accurate GLB collision.
- The matrix uses existing HomePC Godot 4.4.1 and existing local assets only.
