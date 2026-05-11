# Game P11-A Boundary Ledger

## Resolved

| Requirement | Result |
|---|---|
| Real signal replay | `Area3D.area_entered` emitted 5 events |
| Fallback exclusion | fallback `used=false`; fallback did not count as pass |
| Finish before collection | signal received but rejected as `finish_locked` |
| Checkpoint signals | 3 checkpoint events collected `chair`, `block`, `tower` |
| Finish after collection | signal accepted as `finish_unlocked` |
| Node paths | Event trace records objective paths and probe path |

## Remaining Limits

- This is still headless and uses an `ObjectiveProbe` Area3D, not human input.
- It does not validate camera, animation, visual readability, controller feel, or packaged builds.
