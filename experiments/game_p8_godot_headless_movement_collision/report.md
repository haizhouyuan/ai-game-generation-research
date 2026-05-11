# GAME-P8-A Godot Headless Movement/Collision Simulation Report

| Field | Value |
|---|---|
| Task ID | `GAME-P8-A-GODOT-HEADLESS-MOVEMENT-COLLISION` |
| Status | pass for deterministic proxy-collision simulation |
| Machine | HomePC existing Godot 4.4.1 via YogaS2 SSH |
| Decision | promote as headless collision-simulation baseline; not final gameplay feel |

## Scope

P8-A builds on the saved P7 Godot scene. It adds a headless simulation script that loads `p7_minimal_playable_scene.tscn`, reads the saved `StaticBody3D` + `BoxShape3D` collision proxies, and simulates three player approach paths against the three generated assets.

The simulation uses deterministic swept AABB checks over the saved collision proxies. It records distance changes, contact, and blocking. This avoids new display/GPU setup and does not claim real controller feel or full Godot physics-player behavior.

## Commands

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY='*' no_proxy='*' \
  /home/yuanhaizhou/godot/godot --headless \
  --path /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p8_godot_headless_movement_collision_20260512/project \
  --import

env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY='*' no_proxy='*' \
  /home/yuanhaizhou/godot/godot --headless \
  --path /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p8_godot_headless_movement_collision_20260512/project \
  --script res://tools/simulate_movement_collision.gd
```

## Evidence

| Evidence | Path |
|---|---|
| Simulation report | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p8_godot_headless_movement_collision/outputs/p8_movement_collision_report.json` |
| Simulation log | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p8_godot_headless_movement_collision/outputs/godot_simulation_homepc.log` |
| Import log | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p8_godot_headless_movement_collision/outputs/godot_import_homepc.log` |
| Simulation script | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p8_godot_headless_movement_collision/project/tools/simulate_movement_collision.gd` |
| Artifact hashes | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p8_godot_headless_movement_collision/outputs/artifact_hashes.json` |

## Results

| Path | Target | Contact | Blocked | Result |
|---|---|---:|---:|---|
| `approach_chair` | `triposr_p4_chair_mesh_Collider` | yes | yes | pass |
| `approach_block` | `triposr_p5_synthetic_block_Collider` | yes | yes | pass |
| `approach_tower` | `triposr_p5_synthetic_tower_Collider` | yes | yes | pass |

Summary from runtime report:

- path count: `3`
- contact count: `3`
- blocked count: `3`
- pass: `true`

## Boundary

The simulation verifies collision proxy behavior and movement blocking in a headless, deterministic way. It does not verify real rendered gameplay, input responsiveness, animation, mesh-accurate collision, camera composition, or child-ready game design.

## Next Action

P9 should either add a real Godot physics step with `CharacterBody3D.move_and_collide` if headless runtime supports it cleanly, or add a simple objective loop such as collectibles/checkpoints using the same deterministic verification style.
