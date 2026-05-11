# P12 Deterministic Replay And Visual Probe Capability Matrix

Status: P12-A HomePC headless run passed for deterministic replay; screenshot feasibility blocked.

| Capability | Evidence target | Current claim |
| --- | --- | --- |
| Deterministic replay trace | Fixed plan plus tick trace JSON | Pass: 45 ticks |
| Area3D signal order | Signal event trace | Pass: `finish_locked -> checkpoint_collected x3 -> finish_unlocked` |
| Finish lock/unlock | Pre-finish locked, post-checkpoint finish accepted | Pass: 2 finish attempts |
| Visual/screenshot feasibility | Headless viewport PNG or explicit blocker | Blocked: viewport image empty in headless mode |

Fresh run:

- Report: `experiments/game_p12_deterministic_replay_visual_probe_20260512/outputs/p12_deterministic_replay_visual_probe_report.json`
- Log: `experiments/game_p12_deterministic_replay_visual_probe_20260512/outputs/godot_p12_replay_visual_probe_homepc.log`
- Screenshot output: no PNG saved; headless viewport returned empty image.
