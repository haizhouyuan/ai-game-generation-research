# GAME-P6-A Failure Ledger

| ID | Stage | Failure / Boundary | Evidence | Next Action |
|---|---|---|---|---|
| `GAME-P6-F1` | YogaS2 runtime | YogaS2 has no `godot`, `godot4`, `godot-headless`, or package record. | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p6_godot_engine_probe/outputs/godot_probe_yogas2.log` | Use HomePC existing Godot for now; install on YogaS2 only after explicit approval. |
| `GAME-P6-F2` | engine scope | Godot import passed, but no playable Godot scene/collision loop has been built yet. | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p6_godot_engine_probe/outputs/godot_import_report.json` | P7 should create minimal playable scene and collider checks. |
| `GAME-P6-F3` | dependency policy | TripoSR still uses the local `torchmcubes` shim from P4/P5. | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/failure_ledger.md` | Validate official dependency through no-proxy mirror or formally keep shim fallback. |
