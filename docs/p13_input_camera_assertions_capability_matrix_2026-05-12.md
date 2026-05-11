# P13 Input/Camera Assertions Capability Matrix

| Capability | Evidence | Result | Boundary |
|---|---|---:|---|
| No-proxy HomePC Godot execution | `outputs/godot_p13_input_camera_assertions_homepc.log` | pass | Offline/local run only |
| Deterministic input replay | `outputs/p13_input_camera_assertions_report.json` tick trace | pass | Input-vector replay, not physical keyboard/gamepad |
| CharacterBody collision | `collision_pass_count=3/3` | pass | Uses existing proxy colliders, not mesh-accurate collision |
| Objective event ordering | `event_reasons` exact match | pass | Requires P13 sensor-clearance repair for block checkpoint |
| Counter-fixture without repair | `p13_input_camera_assertions_without_sensor_repair_report.json` | fail as expected | Demonstrates inherited P10 blocker |
| Camera follow/framing | `camera_assertions.pass=true`, `sample_count=28` | pass | Headless camera math/frustum, not rendered screenshot |
| Visual screenshot | `visual_probe.attempted=false` | not claimed | P12 blocker preserved |

Decision: promote the P13 game path as a deterministic headless engine-assertion harness, with a required follow-up to make sensor-clearance validation part of the scene-builder gate.
