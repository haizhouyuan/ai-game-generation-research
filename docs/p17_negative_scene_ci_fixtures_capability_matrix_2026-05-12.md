# P17-A Game Negative Scene-CI Fixtures Capability Matrix

| Capability | Evidence | Result | Boundary |
|---|---|---|---|
| Positive multi-layout regression | `matrix.pass=true`, `3/3` layouts | Pass: P16 route/input/collision/UI/camera gates stayed green. | Headless proxy-node CI only. |
| Missing checkpoint counter | `negative_reports.missing_checkpoint.detected_failure=true` | Pass: removed checkpoint failed readback. | Does not inspect arbitrary manually-authored scenes. |
| Route mismatch counter | `negative_reports.route_mismatch.detected_failure=true` | Pass: wrong expected route failed trace diff. | Deterministic replay, not free-play QA. |
| Finish-before-checkpoints counter | `negative_reports.finish_before_checkpoints.detected_failure=true` | Pass: forced early finish was rejected by summary gate. | Covers this explicit objective rule. |
| Sensor-clearance counter | `negative_reports.sensor_clearance_violation.detected_failure=true` | Pass: builder gate rejected unsafe checkpoint sensor placement. | Proxy shape clearance, not mesh-accurate collision. |
| Camera-obstruction counter | `negative_reports.camera_obstruction_failure.detected_failure=true` | Pass: injected obstruction failed camera gate. | No screenshot/visual QA claim. |

Decision: promote P17 as a negative-fixture CI layer for the Godot proxy-scene harness; keep visual QA, mesh-accurate collision, and packaged runtime validation active.
