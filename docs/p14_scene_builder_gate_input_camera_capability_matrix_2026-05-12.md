# P14 Scene Builder Gate Input Camera Capability Matrix

| Capability | Evidence | Result | Boundary |
|---|---|---:|---|
| No-proxy HomePC Godot execution | `outputs/godot_p14_scene_builder_gate_input_camera_homepc.log` | pass | Offline/local run only |
| Scene-builder objective nodes | `project/scenes/p14_objective_scene.tscn` | pass | ObjectiveRoot/checkpoint/finish only |
| Sensor clearance gate | `scene_build.clearance_pass=true`, `scene_readback.clearance_pass=true` | pass | Box proxy clearance, not mesh surface clearance |
| InputMap/key-event replay | `input_key_event_summary.failed_count=0`, `sample_count=23` | pass | Requires buffered input flush in headless |
| CharacterBody collision | `collision_pass_count=3/3` | pass | Existing proxy colliders |
| Objective lock/unlock order | exact `event_reasons` match | pass | Single deterministic route |
| Camera framing variations | `84/84` samples passed | pass | Headless camera math/frustum only |
| Camera obstruction counter | ray through block collider hit block | pass | One counter ray |
| Rendered screenshot / visual quality | not attempted | not claimed | P12 screenshot blocker preserved |

Decision: promote P14 as the reusable game scene-builder gate baseline. It closes the P13 sensor-clearance follow-up and adds deterministic key-event and camera variation checks, while still not claiming visual screenshot proof or mesh-accurate collision.
