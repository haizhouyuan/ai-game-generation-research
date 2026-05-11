# P16-A Game Boundary Ledger

| Boundary | Current P16 Fact | Next Pressure Test |
|---|---|---|
| Multi-layout CI | Three scene-builder layouts passed with distinct checkpoint/finish routes. | Add randomized but seeded route/layout fixture generation. |
| Objective state | UI/state feedback and locked/unlocked finish assertions passed per layout. | Add failure counters for missing checkpoint, missing UI, and finish-before-checkpoints. |
| Camera | Three camera variants passed per layout, `84` samples per layout. | Add occluder/camera obstruction negative fixture, not just positive obstruction counter. |
| Collision | CharacterBody contacts and Area3D events passed using proxy shapes. | Mesh-accurate GLB collision remains unclaimed. |
| Visual | Screenshot/display path was not retried. | Only reopen if an existing non-headless/display path is available without display-stack changes. |
