# GAME-P7-A Godot Minimal Playable Scene Report

| Field | Value |
|---|---|
| Task ID | `GAME-P7-A-GODOT-MINIMAL-PLAYABLE-SCENE` |
| Status | pass for headless structural playable gate |
| Machine | HomePC existing Godot 4.4.1 via YogaS2 SSH |
| Decision | promote as minimal engine-loop baseline; visual/runtime gameplay still next |

## Scope

P7-A used HomePC's existing `/home/yuanhaizhou/godot/godot` binary. It did not install software, download resources, or use Pro.

The minimal Godot project:

- imports the three P5/P6 GLB assets;
- instantiates all assets;
- normalizes each asset so the largest dimension is `1.8`;
- adds a `StaticBody3D` plus `BoxShape3D` collision proxy for each asset;
- adds a `CharacterBody3D` player with capsule collision;
- adds camera and light;
- packs and saves `res://scenes/p7_minimal_playable_scene.tscn`;
- writes a headless runtime report.

## Commands

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY='*' no_proxy='*' \
  /home/yuanhaizhou/godot/godot --headless \
  --path /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p7_godot_minimal_playable_scene_20260512/project \
  --import

env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY='*' no_proxy='*' \
  /home/yuanhaizhou/godot/godot --headless \
  --path /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p7_godot_minimal_playable_scene_20260512/project \
  --script res://tools/build_and_check_scene.gd
```

## Evidence

| Evidence | Path |
|---|---|
| Local project | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/project/` |
| Runtime report | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/outputs/p7_runtime_report.json` |
| Runtime log | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/outputs/godot_runtime_homepc.log` |
| Import log | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/outputs/godot_import_homepc.log` |
| Saved scene | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/project/scenes/p7_minimal_playable_scene.tscn` |
| Artifact hashes | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/outputs/artifact_hashes.json` |

## Results

| Asset | Instantiated | Normalized scale | Collision proxy | Runtime result |
|---|---:|---:|---|---|
| `triposr_p4_chair_mesh` | yes | `1.92321729618691` | `StaticBody3D` + `BoxShape3D` | pass |
| `triposr_p5_synthetic_block` | yes | `1.76432197173205` | `StaticBody3D` + `BoxShape3D` | pass |
| `triposr_p5_synthetic_tower` | yes | `1.878428561032` | `StaticBody3D` + `BoxShape3D` | pass |

Runtime checks:

- asset count: `3`
- asset pass count: `3`
- collision proxy count: `3`
- normalized scale count: `3`
- player has collision: `true`
- scene pack result: `0`
- scene save result: `0`

## Screenshot Boundary

No screenshot was produced in P7-A. The available route is HomePC Godot headless, and this batch intentionally avoided extra display/GPU setup or new installs. The substitute verification is a saved Godot scene plus structured runtime report proving instantiated assets, normalized scale, collision proxies, player, camera, light, and saved scene.

## Capability Finding

The game chain now has a minimal engine-loop baseline beyond import: generated GLBs can be placed into a Godot scene with collision proxies and a player/camera/light scaffold under a headless runtime check. This is still not a finished game loop with rendered visual QA, controls, level design, or gameplay testing.

## Next Action

P8 should add either a visual render/screenshot path if an approved display route exists, or a scripted movement/collision simulation inside Godot headless.
