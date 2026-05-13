# P5 TripoSR Three.js Playable Capability Matrix - 2026-05-12

| Capability | Result | Evidence | Decision |
|---|---|---|---|
| Offline/no-proxy TripoSR inference | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/homepc_evidence/environment_no_proxy.json` | Continue HomePC no-proxy path. |
| Additional image-to-GLB probes | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/homepc_evidence/triposr_synthetic_summary.json` | Keep TripoSR for small local asset probes. |
| GLTFLoader parse | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/outputs/asset_parse_inventory.json` | Assets are importable by Three.js. |
| Playable loop import | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/outputs/game_p5_import_scale_collision_matrix.json` | Promote to P6 engine import. |
| Scale and collision probe | pass for three small assets | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/outputs/verification/playable_dom_status_summary.json` | Reuse as lightweight validator. |
| Visual nonblank screenshot | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/outputs/verification/playable_pixel_checks.json` | Good enough for local browser validation. |
| Official engine import | not tested | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/failure_ledger.md` | P6 should test Godot/Unity. |

## Boundary

P5 proves a local image-to-3D-to-Three.js playable loop for three small generated/imported GLB assets. It does not yet prove material quality, animation, collision-shape quality, or Godot/Unity production import.
