# GAME-P5-A Failure Ledger

| ID | Stage | Asset | Failure | Evidence | Next Action |
|---|---|---|---|---|---|
| `GAME-P5-F1` | dependency policy | all TripoSR assets | Official `torchmcubes` path is not validated; current P4/P5 path uses the local shim. | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p4_triposr_offline_probe/report.md` | Decide whether to approve the shim as a controlled fallback or validate official package through no-proxy mirror. |
| `GAME-P5-F2` | engine validation | all TripoSR assets | Three.js playable loop passed, but Godot/Unity import is not yet tested. | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/outputs/game_p5_import_scale_collision_matrix.json` | Run P6 Godot/Unity import path after install/runtime approval. |
