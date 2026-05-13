# P0 ChatGPT HTML Game Baseline - 2026-05-12

## Source

Original file provided by the user:

`/Users/yuanshaochen/Documents/14.html`

Captured copy:

`experiments/game_p0_chatgpt_html_baseline_20260509/14.html`

This is the HTML game the user's son asked ChatGPT to generate.

## Identity

- Title: `战术房区生存：视觉真实感优化版`
- Format: single-file HTML, CSS, and JavaScript
- Size: `99869` bytes
- Lines: `1136`
- Renderer: Three.js from CDN, `https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.min.js`
- Dependency model: external CDN for Three.js, otherwise procedural/local code

## Screenshot

![Lobby screenshot](/Users/yuanshaochen/Projects/ai-game-generation-research/experiments/game_p0_chatgpt_html_baseline_20260509/lobby_screenshot.png)

## What It Already Does Well

The game is much richer than a trivial generated demo:

- Has a complete lobby and onboarding screen.
- Uses Three.js with perspective camera, fog, lighting, shadows, tone mapping, procedural textures, and generated geometry.
- Builds a multi-building tactical compound with floors, walls, roofs, warehouses, containers, vegetation, roads, indoor ladders, floor supports, balconies, props, labels, and loot points.
- Supports first-person and third-person camera modes.
- Implements player movement, sprinting, crouch, prone, jump, ADS, recoil, stamina, pointer lock, and camera collision.
- Implements weapons: pistol, shotgun, rifle, DMR.
- Implements ammo, reload, fire rate, spread, range falloff, hit markers, tracers, muzzle flash, shell casings, smoke, particles, and impact effects.
- Implements NPCs with patrol/spawn, movement, line-of-sight blocking, shooting, damage, and elimination.
- Implements loot, armor, helmet, healing items, revive stones, and weapon unlocks.
- Implements skin lottery using `localStorage`.
- Includes configurable NPC strength, spawn rate, loot richness, quality, and sky time.

## Why It Felt Exciting

This file has the important "AI made a real game" feeling because it is immediately playable and has a recognizable game fantasy:

`lobby -> enter compound -> move/aim/shoot -> fight NPCs -> loot -> upgrade gear -> collect skins`

It also contains many small feedback loops: hit marker, damage flash, muzzle flash, casings, particles, ammo, healing, coins, and skins. Those feedback loops matter more to first-time delight than architectural cleanliness.

## Current Limitations

- It depends on CDN Three.js. Offline or no-CDN mode will show the built-in CDN error.
- All logic lives in one 98KB file, so it is hard to test, extend, or safely refactor.
- Assets are procedural primitives only; there are no authored GLB models, textures, animation clips, or real character rigs.
- NPC AI is local/simple and not a robust behavior system.
- Collision is AABB/proxy based, not a production physics setup.
- No automated playable test verifies start, pointer lock, shooting, NPC behavior, or win/lose flow.
- No asset provenance, scene schema, or regression evidence packet.
- The theme is tactical shooter; if the target is a child-friendly game-development pipeline, later prototypes should separate "technical FPS controls" from age-appropriate art/game rules.

## Baseline Role In The Research Program

This should become the P0 user-excitement baseline:

1. Preserve the original file unchanged.
2. Extract feature inventory and game loop vocabulary from it.
3. Use it as a comparison target when evaluating AI-generated Unity/Three.js/Godot prototypes.
4. Require future prototypes to keep or improve the immediate feedback loops, while replacing single-file fragility with an agentic production chain.

## Validation

Headless Chrome screenshot succeeded against a local HTTP server:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new \
  --disable-gpu \
  --no-first-run \
  --no-default-browser-check \
  --user-data-dir=/tmp/codex-chrome-14html \
  --window-size=1440,1000 \
  --virtual-time-budget=5000 \
  --screenshot=experiments/game_p0_chatgpt_html_baseline_20260509/lobby_screenshot.png \
  http://127.0.0.1:8765/14.html
```

The browser plugin timed out twice during interactive verification, so the current evidence is a Chrome screenshot smoke test, not an automated in-game playthrough.
