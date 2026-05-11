# P20 Scene-CI Compact Diff Table

| Group | ID | Status | Accepted | Current |
|---|---|---|---|---|
| positive_layout_hashes | `front_linear` | match | `42aab471352f` | `42aab471352f` |
| positive_layout_hashes | `front_reverse` | match | `dc825e9e56fe` | `dc825e9e56fe` |
| positive_layout_hashes | `front_staggered` | match | `d0ce8dfe7ad4` | `d0ce8dfe7ad4` |
| negative_fixture_hashes | `camera_obstruction_failure` | match | `a6c2547c2488` | `a6c2547c2488` |
| negative_fixture_hashes | `finish_before_checkpoints` | match | `60181f4865e4` | `60181f4865e4` |
| negative_fixture_hashes | `missing_checkpoint` | match | `d3bc7a8e1721` | `d3bc7a8e1721` |
| negative_fixture_hashes | `route_mismatch` | match | `2840bcbab1ed` | `2840bcbab1ed` |
| negative_fixture_hashes | `sensor_clearance_violation` | match | `2d4671870413` | `2d4671870413` |

## Baseline Update Policy

- Requested baseline id: `accepted_p19_scene_ci_hash_regression_20260512`
- Allowlisted update accepted: `True`
- Unlisted update denied: `True`

Boundary: this table covers compact deterministic headless scene-CI data only, not screenshots or mesh-accurate GLB collision.
