# P11-A Game Capability Matrix: Area3D Signal Replay

| Capability | Evidence | Result | Boundary |
|---|---|---|---|
| Signal replay | `experiments/game_p11_area3d_signal_replay_20260512/outputs/p11_area3d_signal_replay_report.json` | pass: 5 `area_entered` events | Headless Godot physics/signal path |
| Objective event trace | Same report | 3 checkpoint events and 2 finish events with node paths | Signal events only; fallback did not count as pass |
| Finish lock/unlock | Same report | pre-finish rejected as locked; post-collection finish accepted | Logic-level validation, not visual playtest |
| Decision | `report.md` and `boundary_ledger.md` | `promote-signal-replay-baseline` | Next step is visual/input replay, not signal proof |
