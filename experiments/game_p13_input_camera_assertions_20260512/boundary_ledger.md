# P13-A Game Boundary Ledger

## Passed

- Local/offline HomePC Godot 4.4.1 run with proxy variables unset.
- `CharacterBody3D.move_and_collide` reached all three GLB collision proxies.
- Area3D `body_entered` objective events fired in the required order after P13 sensor-clearance repair.
- Camera follow/framing assertions passed for all recorded samples.
- Disabled-repair counter-run failed, proving the P13 repair addresses a real inherited scene-node gap.

## Blocked Or Not Claimed

- No screenshot pass is claimed. P12 already showed headless viewport readback is not reliable enough here.
- No non-headless display path was changed or requested.
- No real gameplay feel, animation, input-map device handling, or packaged build is claimed.
- The block checkpoint repair is a local scene-authoring fix. P10 remains a source of the original sensor-placement gap.

## Next

- Promote sensor-clearance checks into the shared scene-builder harness.
- Add camera obstruction/occlusion checks and deterministic key-event/InputMap replay only if it remains local and does not require display-stack changes.
