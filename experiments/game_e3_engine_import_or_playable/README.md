# GAME-E3 Engine Import Or Playable Path

This experiment creates a no-download playable browser path for the three benchmark inputs in `docs/experiment_backlog.md`.

## Result

- Path type: concept-to-playable runnable prototype with deterministic procedural assets.
- Runtime: local browser, Canvas 2D isometric renderer, ES modules.
- External assets: none.
- Credentials/uploads: none.

## Run

```bash
cd /vol1/1000/projects/ai-game-generation-research/experiments/game_e3_engine_import_or_playable
node tools/export_assets.mjs
python3 -m http.server 8125 --bind 127.0.0.1
```

Open `http://127.0.0.1:8125/index.html`.

Use arrow keys or WASD to move. Select `GAME-B1`, `GAME-B2`, or `GAME-B3` in the top-right benchmark switcher.

## Benchmark Inputs

| Input | Prompt | Output |
|---|---|---|
| `GAME-B1` | `A small friendly robot that collects glowing batteries in a workshop maze.` | Workshop maze with robot, batteries, hazard, and charge dock. |
| `GAME-B2` | `A low-poly island obstacle course with three platforms, coins, and one moving hazard.` | Island platform course with coins, rolling hazard, and finish flag. |
| `GAME-B3` | `A tiny space hangar scene with a controllable rover, one pickup item, and a finish pad.` | Space hangar with rover, fusion core, security hazard, and launch pad. |

## Artifacts

- Runnable prototype: `index.html`
- Source: `src/`
- Export script: `tools/export_assets.mjs`
- Generated scene specs: `outputs/generated_scenes/`
- Benchmark input export: `outputs/benchmark_inputs.json`
- Procedural asset inventory: `outputs/procedural_asset_inventory.json`
- Verification outputs: `outputs/verification/`

## Verification

The verification commands used for the report are:

```bash
node tools/export_assets.mjs
python3 -m http.server 8125 --bind 127.0.0.1
curl -I http://127.0.0.1:8125/index.html
google-chrome --headless --disable-gpu --no-sandbox --screenshot=outputs/verification/game_e3_game_b1.png --window-size=1280,720 "http://127.0.0.1:8125/index.html?benchmark=GAME-B1"
google-chrome --headless --disable-gpu --no-sandbox --screenshot=outputs/verification/game_e3_game_b2.png --window-size=1280,720 "http://127.0.0.1:8125/index.html?benchmark=GAME-B2"
google-chrome --headless --disable-gpu --no-sandbox --screenshot=outputs/verification/game_e3_game_b3.png --window-size=1280,720 "http://127.0.0.1:8125/index.html?benchmark=GAME-B3"
```
