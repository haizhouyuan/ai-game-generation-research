# P14-A Game Boundary Ledger

| Item | Status | Evidence | Boundary |
|---|---:|---|---|
| Scene-builder ObjectiveRoot | pass | `project/scenes/p14_objective_scene.tscn` | Built from existing P7/P10 scene; not a general level editor |
| Checkpoint sensor clearance | pass | `scene_build.clearance_rows` and `scene_readback.clearance_rows` | Uses box proxy extents and float tolerance `0.00001` |
| Deterministic InputMap key events | pass | `input_key_event_summary.failed_count=0` | Headless run requires `Input.flush_buffered_events()` |
| CharacterBody collision | pass | `collision_pass_count=3` | Proxy colliders only |
| Objective ordering | pass | exact `event_reasons` match | Single deterministic route |
| Camera variants | pass | `84` samples, `0` failed | Frustum/math assertions only, no rendered screenshot |
| Obstruction counter | pass | block collider ray hit | One deliberate blocked ray counter |
| Raw GLB visual import | not claimed | HomePC Godot log warnings | Scene gates rely on collision proxies and nodes, not rendered mesh validation |
