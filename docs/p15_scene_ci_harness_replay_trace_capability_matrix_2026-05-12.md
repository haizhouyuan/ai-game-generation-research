# P15 Scene CI Harness Replay Trace Capability Matrix

| Capability | Evidence | Result | Boundary |
|---|---|---:|---|
| No-proxy HomePC Godot execution | `outputs/godot_p15_scene_ci_harness_replay_trace_homepc.log` | pass | Offline/local run only |
| CI-style scene builder | `project/tools/scene_ci_harness_replay_trace.gd` | pass | One deterministic fixture |
| Sensor clearance gate | `scene_builder_clearance_pass=true`, `readback_clearance_pass=true` | pass | Box proxy clearance |
| Objective UI/state feedback | `objective_ui_pass=true`, five required states observed | pass | Headless Label text only |
| Replay trace diff | `trace_diff_pass=true`, no mismatches | pass | Fixed expected event reasons |
| InputMap/key-event replay | `input_key_event_pass=true`, `23` ticks | pass | Requires input flush in headless |
| CharacterBody collision | `collision_pass_count=3/3` | pass | Existing proxy colliders |
| Camera variants | `84/84` samples passed | pass | Headless math/frustum |
| Obstruction counter | block collider ray hit | pass | One deliberate blocked ray |
| Rendered screenshot / visual quality | not attempted | not claimed | P12 screenshot blocker preserved |

Decision: promote P15 as the reusable headless CI harness baseline for scene-building, objective state feedback, trace diffing, input/collision/camera checks, while preserving visual and mesh-accurate collision boundaries.
