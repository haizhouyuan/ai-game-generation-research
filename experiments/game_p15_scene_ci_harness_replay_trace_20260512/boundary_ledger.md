# P15-A Game Boundary Ledger

| Item | Status | Evidence | Boundary |
|---|---:|---|---|
| Reusable CI-style harness | pass | `scene_ci_harness_replay_trace.gd` | One route and one asset set |
| Sensor clearance | pass | build/readback clearance rows | Box proxy clearance |
| Objective UI feedback | pass | `objective_ui_summary.missing_states=[]` | Headless Label text, not rendered HUD proof |
| Replay trace diff | pass | `trace_diff.mismatches=[]` | Fixed expected event sequence |
| InputMap key-event replay | pass | `failed_count=0`, `sample_count=23` | Requires buffered input flush |
| Camera variants | pass | `84/84` samples | Math/frustum assertions, not screenshot |
| Obstruction counter | pass | deliberate block ray hit | One counter ray |
| Visual screenshot | not claimed | P15 skipped display path | No display-stack changes |
