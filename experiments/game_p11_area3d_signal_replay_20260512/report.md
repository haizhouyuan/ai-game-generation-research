# Game P11-A: Area3D Signal Replay

- Date: `2026-05-12`
- Status: `pass`
- Scope: verify explicit P10 objective nodes with real Godot `Area3D.area_entered` signal replay.
- Pro/advisor path: disabled, not used.
- Download/install: none; reuses P10 project assets and HomePC Godot 4.4.1.

## Command

```bash
REMOTE=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p11_area3d_signal_replay_20260512
LOCAL=/vol1/1000/projects/ai-game-generation-research/experiments/game_p11_area3d_signal_replay_20260512
scp -r "$LOCAL/project" yuanhaizhou@192.168.1.17:"$REMOTE/project"
ssh -o BatchMode=yes yuanhaizhou@192.168.1.17 "cd '$REMOTE/project' && env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy NO_PROXY='*' no_proxy='*' /home/yuanhaizhou/godot/godot --headless --path '$REMOTE/project' --script res://tools/simulate_area3d_signal_replay.gd"
```

## Result

| Check | Result |
|---|---|
| Signal mode | pass |
| Fallback used | false |
| Event count | 5 |
| Checkpoint signals | 3 |
| Finish signals | 2 |
| Pre-collection finish signal | received and rejected as `finish_locked` |
| Checkpoint collection | `chair`, `block`, `tower` |
| Post-collection finish signal | accepted as `finish_unlocked` |

Runtime evidence:

- `outputs/p11_area3d_signal_replay_report.json`
- `outputs/godot_p11_signal_replay_homepc.log`
- `outputs/artifact_hashes.json`

## Boundary

This batch is headless signal replay. It is stronger than deterministic shape readback, but still does not claim camera/input feel, visual QA, or packaged-game quality.
