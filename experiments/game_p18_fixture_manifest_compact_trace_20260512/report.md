# P18-A Game Fixture Manifest And Compact Trace Report

Status: P18-A HomePC headless run plus local compact evidence pass.

Purpose: keep the P17 negative scene-CI authority, but add compact artifacts that allow review without reading the huge full JSON report.

Commands:

```bash
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p18_fixture_manifest_compact_trace_20260512
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p18_fixture_manifest_compact_trace_20260512
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "rm -rf '$REMOTE' && mkdir -p '$REMOTE'"
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/scene_ci_negative_fixtures_with_manifest.gd > '$REMOTE/project/outputs/godot_p18_fixture_manifest_compact_trace.log' 2>&1"
python3 "$LOCAL/summarize_p18_fixture_manifest.py"
```

Result:

- Full HomePC Godot headless report passed with `3` positive layouts and `5` detected negative fixtures.
- `p18_fixture_manifest.json` records positive layouts, negative fixtures, expected failures, detection state, and per-fixture compact hashes.
- `p18_compact_replay_trace.json` records compact event-order, objective-order, mismatch, clearance, finish-lock, and camera-obstruction diagnostics.
- `p18_trace_hashes.json` records hash anchors for the full report, manifest, compact trace, each positive layout trace, and each negative fixture trace.

Artifacts:

- `outputs/p18_negative_scene_ci_full_report.json`
- `outputs/p18_fixture_manifest.json`
- `outputs/p18_compact_replay_trace.json`
- `outputs/p18_trace_hashes.json`
- `outputs/artifact_hashes.json`
- `outputs/godot_p18_fixture_manifest_compact_trace.log`

Boundary:

- Authority remains proxy scene nodes plus Godot headless physics/input/camera assertions.
- Compact evidence is derived from the full report and hash-linked to it; it is a review artifact, not a new visual validator.
- No screenshot, visual QA, human-feel QA, or mesh-accurate GLB collision claim is made.
