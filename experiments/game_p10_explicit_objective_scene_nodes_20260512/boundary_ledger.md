# Game P10-A Boundary Ledger

## Resolved

| Requirement | Result |
|---|---|
| Explicit objective nodes | `ObjectiveRoot` contains 3 checkpoint `Area3D` nodes and 1 finish `Area3D` node |
| Shape readback | Checkpoints expose `BoxShape3D`; finish exposes `SphereShape3D` |
| Stable naming | `Checkpoint_Chair`, `Checkpoint_Block`, `Checkpoint_Tower`, `Finish_Area` |
| Asset-adjacent positions | Checkpoints have three distinct positions near the three GLB collision proxies |
| Finish gating | Finish is locked before collection and unlocks/reaches after 3/3 checkpoints |

## Remaining Limits

- Objective entry uses deterministic shape readback, not Godot `area_entered` signal replay.
- This is still headless validation; no screenshot, camera feel, input feel, or packaged build is claimed.
- Checkpoint shapes are proxy gameplay volumes, not mesh-accurate collision.
