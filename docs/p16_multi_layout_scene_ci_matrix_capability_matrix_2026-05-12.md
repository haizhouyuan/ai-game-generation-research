# P16 Multi-Layout Scene CI Matrix Capability Matrix

| Capability | Evidence | Result | Boundary |
|---|---|---:|---|
| Multiple scene-builder layouts | `front_linear`, `front_reverse`, `front_staggered` | pass | Same existing asset set |
| Distinct route replay trace diff | Three unique route signatures | pass | Deterministic routes only |
| Objective UI/state feedback | Required locked/unlocked/reached states observed per layout | pass | Headless label state, not visual UX QA |
| Sensor clearance | Builder and readback clearance gates passed per layout | pass | Proxy shapes only |
| InputMap key-event replay | `23` deterministic ticks per layout, `0` key-state failures | pass | Keyboard replay only |
| CharacterBody collision loop | `3/3` target collisions per layout | pass | Proxy collision, not mesh-accurate |
| Camera variants | `84/84` samples per layout | pass | No rendered screenshot proof |
| Obstruction counter | Ray-hit counter collider per layout | pass | Positive counter only; no full camera QA |

Decision: promote P16 as the current headless Godot scene-CI matrix baseline. Keep screenshot/visual QA and mesh-accurate collision explicitly unclaimed.
