# Production Goal: Realistic 3D Asset Upgrade For Tactical Compound Survival - 2026-05-13

## Objective

Upgrade the existing game in `/Users/yuanshaochen/Documents/14.html` so that its visible in-game assets look convincingly realistic and production-complete, while preserving the current playable game loop.

The goal is not to build a new rover/battery game, not to expand the controller for its own sake, and not to stop at research notes. The goal is a repeatable, evidence-backed 3D asset production pipeline that makes the current tactical compound survival game look substantially more realistic.

## Source Game

- Primary game: `/Users/yuanshaochen/Documents/14.html`
- Existing weapon source pack: `/Users/yuanshaochen/Documents/枪械模型包/`
- Existing GROZA reference viewer: `/Users/yuanshaochen/Documents/groza_high_detail_3d_model_viewer.html`

## Target Outcome

The game should reach a visibly high-completion state from a realistic 3D asset perspective:

- first-person and third-person weapons look like detailed game-ready 3D assets, not simple procedural blocks;
- player/NPC silhouettes, gear, helmets, armor, and carried weapons look coherent and less prototype-like;
- buildings, containers, crates, trees, rocks, ladders, loot, and medical/ammo props look materially believable;
- lighting, material response, shadows, scale, and scene composition support a more realistic tactical compound atmosphere;
- assets can be regenerated, cleaned, validated, and reintegrated through documented commands and evidence gates.

## Execution Strategy

Use subagent-driven development. The orchestrator should mainly coordinate, review, and verify; substantial research, tool setup, asset generation, cleanup, and integration tasks should be delegated to subagents or local runner wrappers whenever safe.

Before spending a long time manually debugging, inspect existing Yoga/maint runner configurations and official docs. Specifically investigate local-compatible patterns for:

- `claudeminmax`
- `claudekimi`
- `kimicode`
- Gemini CLI
- Claude Code MCP
- Kimi/MiniMax/Claude wrapper skills and MCP configuration

Do not expose or commit API keys. Credentials may be copied only into ignored/private local runner locations.

## Asset Pipeline Requirements

Build and prove a pipeline with these stages:

1. Asset inventory
   - Parse `/Users/yuanshaochen/Documents/14.html` and identify visible asset classes.
   - Prioritize assets by visual impact: weapons first, then characters/gear, then scene props and environment.

2. High-realism 3D generation
   - Evaluate and use the strongest practical tools for realistic assets, including Hunyuan3D, TRELLIS, TripoSR, Rodin/Hyper3D, Blender, and any locally available or API-backed generation route.
   - Prefer pipelines that produce usable mesh, UVs, textures, and PBR-style materials.
   - TripoSR-style fast reconstruction may be used as a baseline, but should not be treated as sufficient if the result is not realistic.

3. Blender cleanup and asset normalization
   - Clean geometry, normals, transforms, scale, origin, orientation, UV/material assignments, and export format.
   - Export game-ready GLB/GLTF assets.
   - Capture Blender render or viewport screenshots for review.

4. Game integration
   - Integrate improved assets back into a copy or controlled derivative of the source game.
   - Preserve the playable loop, controls, weapon switching, first/third person views, loot, NPC behavior, and basic performance.
   - Start with one hero weapon asset, then expand to the rest of the asset set.

5. Visual quality gate
   - Produce screenshots or video evidence comparing old vs upgraded assets.
   - Verify GLB parse/readback, material presence, texture presence, bounding boxes, and scene placement.
   - Run browser evidence gates for the integrated game where possible.

## Milestones

### M1: Runner And Tooling Ready

- Yoga/maint runner configuration has been inspected and summarized.
- Local runner wrappers are usable for bounded work.
- Claude/Gemini/Kimi/MiniMax skill and MCP state is documented honestly.
- Broken MCP/client integration is either fixed with evidence or explicitly bypassed in favor of a working runner path.

### M2: Asset Inventory And Plan

- Create an inventory of all major visible assets in `/Users/yuanshaochen/Documents/14.html`.
- Rank each asset by visual impact, difficulty, and replacement strategy.
- Select the first hero asset: likely rifle/GROZA-style weapon.

### M3: First Hero Asset Realism Proof

- Generate or acquire at least three candidate realistic 3D versions of the first hero weapon.
- Select the best candidate by visual realism, material quality, mesh usability, and game integration fit.
- Clean and export it through Blender.
- Produce asset report, screenshots, hash manifest, and GLB validation evidence.

### M4: In-Game Hero Asset Replacement

- Replace the current procedural first-person and third-person rifle representation with the improved GLB asset or a controlled hybrid representation.
- Verify first-person view, third-person mount, muzzle alignment, scale, clipping, and performance.
- Produce browser screenshots and a release packet for this replacement.

### M5: Full Visible Asset Upgrade Pass

- Repeat the asset pipeline for the remaining high-impact assets:
  - pistol, shotgun, DMR/rifle variants;
  - player/NPC body, helmet, armor, backpack/gear;
  - loot items, ammo, medkits, revive crystal;
  - crates, containers, ladders, rocks, trees, building detail props.
- Replace low-fidelity procedural primitives where realistic assets materially improve the scene.

### M6: Whole-Game Realism Closeout

- Produce a final playable upgraded game artifact.
- Capture before/after screenshots from representative viewpoints.
- Verify no blocking console errors, no missing asset loads, no broken controls, and no major performance regression.
- Produce final evidence packet with manifests, screenshots, asset provenance, quality notes, and remaining limitations.

## Download And Network Policy

Downloads are allowed when useful, but large downloads must not use paid proxy traffic.

- Any single external download over 100 MB must use command-local no-proxy configuration and must include connection evidence.
- Any single external download over 1 GB requires explicit approval for the exact package/version/URL/size before execution.
- Do not modify global proxy settings casually. Prefer command-local proxy disabling and record evidence.

## Completion Criteria

This goal is complete only when all of the following are true:

- `/Users/yuanshaochen/Documents/14.html` or a clearly named upgraded derivative has visibly more realistic 3D assets integrated into the playable game.
- The hero weapon asset has been replaced and verified in both first-person and third-person contexts.
- The major visible asset classes have either been upgraded or explicitly deferred with a reason.
- The asset generation and cleanup pipeline is documented and repeatable.
- Evidence exists for generated/imported assets: screenshots, mesh/material reports, hash manifests, and browser or engine validation.
- The final game can be opened and played locally without obvious missing assets or broken core interactions.
- Remaining limitations are documented honestly.

## Non-Goals

- Do not spend the main effort expanding the managed-agent controller unless it directly helps asset realism delivery.
- Do not prioritize the rover/battery workshop game.
- Do not claim completion based only on tests, manifests, or research notes.
- Do not treat rough procedural geometry as realistic final assets.
- Do not download large files through paid proxy traffic.
