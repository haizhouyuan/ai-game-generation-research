# Game P9-A Failure Ledger

## Resolved Script Failure

| Run | Failure | Resolution |
|---|---|---|
| First HomePC run | Godot parse error: could not infer local `motion` type in finish loop | Added explicit `Vector3` types for `before`, `direction`, and `motion`; rerun passed |

## Active Boundary

- `move_and_collide` hit all three intended P7/P8 BoxShape proxy colliders.
- The finish loop unlocked only after all three checkpoint collisions and then reached the finish radius.
- This is still headless physics/objective validation, not visual QA or gameplay-feel validation.

## Future Failure Conditions

- Any `move_and_collide` target miss or unexpected collider hit must remain recorded as a failure.
- Any finish completion before all three checkpoint collisions must be treated as an objective-loop failure.
