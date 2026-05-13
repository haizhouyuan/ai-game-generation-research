# P7 Godot Minimal Playable Capability Matrix - 2026-05-12

| Capability | Result | Evidence | Decision |
|---|---|---|---|
| Existing HomePC Godot runtime | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p6_godot_engine_probe/outputs/godot_version_homepc.log` | Continue using without install. |
| GLB asset instantiation | pass for 3 assets | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/outputs/p7_runtime_report.json` | Promote as engine-loop baseline. |
| Scale normalization | pass for 3 assets | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/outputs/p7_runtime_report.json` | Keep as import gate. |
| Collision proxy creation | pass for 3 assets | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/outputs/p7_runtime_report.json` | Use as simple collider baseline. |
| Player/camera/light scaffold | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/outputs/p7_runtime_report.json` | Promote to P8 gameplay simulation. |
| Saved scene artifact | pass | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p7_godot_minimal_playable_scene/project/scenes/p7_minimal_playable_scene.tscn` | Keep as reproducible artifact. |
| Visual screenshot | not run | Headless-only route used. | Add only with approved display/render path. |
