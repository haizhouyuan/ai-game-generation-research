# GAME-E3 Report

| Field | Value |
|---|---|
| Task ID | `GAME-E3` |
| Machine | YogaS2 |
| Result | pass |
| Decision | promote as no-download procedural playable baseline |

## Goal

Create a verified game-generation path satisfying concept-to-playable runnable prototype or generated/procedural asset import path.

## Implemented Path

The experiment implements a local browser playable path. Each GAME-B input is converted into a deterministic procedural scene spec, then rendered by a small Canvas isometric engine with movement, pickup collection, collision, a moving hazard, and a finish condition.

## Benchmark Coverage

| Input | Status | Artifact |
|---|---|---|
| `GAME-B1` | implemented | `outputs/generated_scenes/game-b1.json` |
| `GAME-B2` | implemented | `outputs/generated_scenes/game-b2.json` |
| `GAME-B3` | implemented | `outputs/generated_scenes/game-b3.json` |

## Artifacts

| Artifact | Location | Notes |
|---|---|---|
| Runnable prototype | `index.html` | Local browser path, no network assets. |
| Source files | `src/` | Benchmark inputs, scene generator, engine, and app wiring. |
| Export tool | `tools/export_assets.mjs` | Writes benchmark and scene artifacts. |
| Benchmark export | `outputs/benchmark_inputs.json` | Three inputs from GAME-B1/B2/B3. |
| Scene specs | `outputs/generated_scenes/` | Inspectable procedural scenes. |
| Asset inventory | `outputs/procedural_asset_inventory.json` | Generated asset types and per-scene entities. |
| Verification | `outputs/verification/` | Local server probe and screenshots. |

## Verification

```bash
cd /vol1/1000/projects/ai-game-generation-research/experiments/game_e3_engine_import_or_playable
node tools/export_assets.mjs
python3 -m http.server 8125 --bind 127.0.0.1
curl -fsSI http://127.0.0.1:8125/index.html | tee outputs/verification/local_server_probe_headers.txt
google-chrome --headless --disable-gpu --no-sandbox --disable-dev-shm-usage --virtual-time-budget=1500 --screenshot=outputs/verification/game_e3_game_b1.png --window-size=1280,720 'http://127.0.0.1:8125/index.html?benchmark=GAME-B1'
google-chrome --headless --disable-gpu --no-sandbox --disable-dev-shm-usage --virtual-time-budget=1500 --screenshot=outputs/verification/game_e3_game_b2.png --window-size=1280,720 'http://127.0.0.1:8125/index.html?benchmark=GAME-B2'
google-chrome --headless --disable-gpu --no-sandbox --disable-dev-shm-usage --virtual-time-budget=1500 --screenshot=outputs/verification/game_e3_game_b3.png --window-size=1280,720 'http://127.0.0.1:8125/index.html?benchmark=GAME-B3'
python3 - <<'PY' | tee outputs/verification/png_pixel_check.json
from PIL import Image, ImageStat
import json
from pathlib import Path
out = []
for p in sorted(Path("outputs/verification").glob("game_e3_*.png")):
    im = Image.open(p).convert("RGB")
    stat = ImageStat.Stat(im)
    out.append({"file": str(p), "size": im.size, "mean": [round(x, 2) for x in stat.mean], "extrema": stat.extrema})
print(json.dumps(out, indent=2))
PY
node -e "import('./src/proceduralScenes.js').then(({generateAllScenes, buildAssetInventory}) => { const scenes = generateAllScenes(); const inv = buildAssetInventory(scenes); const result = {sceneCount: scenes.length, ids: scenes.map(s => s.id), entityCounts: Object.fromEntries(scenes.map(s => [s.id, s.entities.length])), pickupCounts: Object.fromEntries(scenes.map(s => [s.id, s.entities.filter(e => e.type === 'pickup').length])), inventoryCounts: inv.counts}; console.log(JSON.stringify(result, null, 2)); if (scenes.length !== 3) process.exit(2); if (!scenes.every(s => s.entities.some(e => e.type === 'hazard') && s.entities.some(e => e.type === 'finish'))) process.exit(3); })" | tee outputs/verification/asset_inventory_check.json
google-chrome --headless --disable-gpu --no-sandbox --disable-dev-shm-usage --virtual-time-budget=1500 --dump-dom 'http://127.0.0.1:8125/index.html?benchmark=GAME-B2' > outputs/verification/game_e3_game_b2_dom.html
```

Verification artifacts:

| Check | Artifact | Result |
|---|---|---|
| Local server probe | `outputs/verification/local_server_probe_headers.txt` | HTTP 200 for `index.html`. |
| `GAME-B1` render | `outputs/verification/game_e3_game_b1.png` | 1280x720 nonblank screenshot. |
| `GAME-B2` render | `outputs/verification/game_e3_game_b2.png` | 1280x720 nonblank screenshot. |
| `GAME-B3` render | `outputs/verification/game_e3_game_b3.png` | 1280x720 nonblank screenshot. |
| Pixel check | `outputs/verification/png_pixel_check.json` | Non-flat extrema across all screenshots. |
| Asset inventory check | `outputs/verification/asset_inventory_check.json` | 3 scenes, 3 hazards, 3 finish pads, 10 pickups. |
| DOM status check | `outputs/verification/game_e3_game_b2_dom.html` | Runtime status reports `proceduralAssets: true` and `externalAssets: 0`. |

The local preview server was started at `http://127.0.0.1:8125/index.html`.

## Blockers And Risks

- This is a procedural browser path, not a Godot/Unity/Unreal import test.
- It proves an inspectable concept-to-playable route, not frontier AI mesh generation.
- No private uploads, credentials, external assets, or large model downloads were used.
