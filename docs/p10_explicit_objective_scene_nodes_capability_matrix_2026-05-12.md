# P10-A Game Capability Matrix: Explicit Objective Scene Nodes

| Capability | Evidence | Result | Boundary |
|---|---|---|---|
| Objective scene-node creation | `experiments/game_p10_explicit_objective_scene_nodes_20260512/outputs/p10_objective_scene_nodes_report.json` | pass | Headless scene structure only |
| Scene tree readback | Same report | 4 objective nodes: 3 checkpoint `Area3D`, 1 finish `Area3D` | Requires stable `ObjectiveRoot`, `Area3D`, `CollisionShape3D`, metadata |
| Objective loop gating | Same report | pre-finish locked; 3/3 collected; finish unlocked/reached | State/assertion loop, not visual playtest |
| Decision | `report.md` and `boundary_ledger.md` | `promote-to-explicit-objective-scene-baseline` | Next step is visual/input replay, not more script-only state |
