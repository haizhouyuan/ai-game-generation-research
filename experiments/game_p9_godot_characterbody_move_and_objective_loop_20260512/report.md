# Game P9-A: Godot CharacterBody Movement And Objective Loop

- Date: `2026-05-12`
- Status: `pass`
- Scope: headless Godot `CharacterBody3D.move_and_collide` probe plus minimal objective/checkpoint/finish loop.
- Pro/advisor path: disabled, not used.
- Download/install: none; reuses P8 GLB assets and HomePC Godot 4.4.1.

## Command

```bash
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p9_godot_characterbody_move_and_objective_loop_20260512
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p9_godot_characterbody_move_and_objective_loop_20260512
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/simulate_characterbody_objective_loop.gd"
```

## Result

| Check | Result |
|---|---|
| `triposr_p4_chair_mesh_Collider` collision | pass in 5 steps |
| `triposr_p5_synthetic_block_Collider` collision | pass in 5 steps |
| `triposr_p5_synthetic_tower_Collider` collision | pass in 5 steps |
| Objective checkpoint collection | 3/3 collected in order |
| Finish unlock | true after all checkpoints |
| Finish reached | true |

Runtime evidence:

- `outputs/p9_characterbody_objective_report.json`
- `outputs/godot_p9_characterbody_homepc.log`
- `outputs/artifact_hashes.json`

## Boundary

This is a headless movement/collision and objective-state assertion. It does not claim final game feel, camera tuning, animation, rendering quality, or human playability.
