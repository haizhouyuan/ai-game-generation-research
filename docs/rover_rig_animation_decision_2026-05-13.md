# RW-ROVER-001 Rig And Animation Decision - 2026-05-13

## Decision

`RW-ROVER-001` is not promoted as a rigged asset.

The current generated rover GLB is treated as a single visual avatar mesh with Blender-authored material slots, procedural embedded base-color maps, and UV proof. P1 uses runtime parent-transform feedback animation only:

- rover group follows the gameplay proxy position and heading;
- feedback pulses scale the parent rover object;
- gameplay collision, pickup, hazard, and movement remain procedural;
- exported `COLLIDER_PROXY_*` mesh is hidden at runtime.

## Evidence

- Textured GLB: `experiments/game_p1_rover_workshop_demo/assets/models/rw_rover_001_single3q_blender_textured_with_proxy.glb`
- Blender texture/UV report: `experiments/rw_rover_001_asset_chain_20260513/blender_single3q_textured/blender_cleanup_report.json`
- Three.js metadata parse: `experiments/rw_rover_001_asset_chain_20260513/blender_single3q_textured/three_glb_parse_inventory_textured.json`
- P1 G4 texture gate: `experiments/game_p1_rover_workshop_demo/evidence/2026-05-13_rw_rover_001_texture_g4/release_packet.json`

## Why No Rig Yet

- TRELLIS produced a mesh-only single object without semantic wheel/body separation.
- A skeletal rig would imply controllable parts or deformation that are not present in the generated source.
- A fake rig on the whole mesh would not improve gameplay evidence and would overstate production readiness.

## Next Rig Gate

Promote rigging only after one of these is true:

- the asset is rebuilt with separate semantic wheel/body parts;
- Blender authoring splits the mesh into named wheel/body/sensor components with evidence;
- a Unity or Blender rig proof shows readable wheel spin, suspension/body motion, and reversible import/export without breaking material/texture provenance.

Until then, report animation as `runtime_parent_transform_feedback_only`.
