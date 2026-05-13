# Production Goal: Local AI 3D Asset Factory And Tactical Visual Upgrade - 2026-05-13

## Objective

Build a local-first AI 3D game-asset production line and use it to upgrade the current HTML/Three.js tactical game from an evidence-gated GLB prototype into a high-quality realistic tactical-game vertical slice.

This goal is not just a tool survey. It is complete only when multiple local/remote production routes are proven, runner orchestration is operational, the playable tactical game has a visibly higher-quality micro-slice, and the evidence packet proves the improvement.

## Current Starting Point

Repository:

`/Users/yuanshaochen/Projects/ai-game-generation-research`

Current final tactical packet:

`experiments/tactical_game_full_realism_final_20260513/`

Current limitation to resolve:

- The final packet has GLB assets and browser evidence, but material quality is still `material_factors_only`.
- Major hero assets need baked texture maps: BaseColor, Normal, Roughness, Metallic, AO.
- The scene is too broad and sparse for a commercial tactical-game look.
- Characters need rigged animation instead of static tactical overlays.
- Runtime should move toward official Three.js `GLTFLoader`, KTX2/Meshopt readiness, AnimationMixer, decals, postprocessing, and stricter visual gates.

## Non-Negotiable Download Policy

Downloads are allowed, including model downloads, but large downloads must not use paid proxy traffic.

- Any single external download over 100MB must use command-local no-proxy settings.
- Any single external download over 1GB requires explicit user approval for exact URL/package/version/size before download.
- Do not change global proxy settings, shell profile proxy settings, Clash, or Homebrew networking unless explicitly asked.
- Record URL, expected size, command, SHA256, and no-proxy evidence for every large download.
- Prefer existing caches and already-installed tools.

## Orchestration Policy

Codex is the lead orchestrator, not the only worker.

Use:

- `claudeminmax` for low-cost mechanical implementation and first-pass review.
- `claudekimi` for alternate implementation critique and scoped worker tasks.
- `gemini` CLI for broad research synthesis and plan review.
- Mac M2 Max 96GB for control-plane, repo work, browser evidence, Three.js coding, light local MLX/llama.cpp inference, and emergency parallel local-model tasks.
- HomePC / dual 3090 as the primary heavy GPU production surface for Trellis2, Hunyuan3D, ComfyUI, Blender render/bake, texture and PBR generation.

Every worker task must have:

- narrow read scope;
- narrow write scope;
- forbidden paths;
- exact verification command;
- expected artifacts;
- no secret reads;
- no package installs or large downloads unless the task explicitly authorizes and follows download policy.

## Local Model Policy For Mac M2 Max 96GB

The Mac is not the primary heavy 3D model host, but it should have a useful local inference lane for budget-efficient parallel work.

Preferred sequence:

1. `mlx-lm` / MLX-native models for Apple Silicon local summarization, classification, task decomposition, and prompt drafting.
2. `llama.cpp` / GGUF for broad model compatibility and OpenAI-compatible local server fallback.
3. LM Studio or Ollama only as convenience wrappers when they reduce operational friction.

Mac local models are not allowed to become a distraction from the main asset pipeline. They are successful when they can handle lightweight review/classification tasks without consuming paid provider tokens.

## Production Routes To Prove

Prove at least three asset-production chains:

### Route A: StableGen / Blender-First Retexture

Purpose: existing white mesh or current GLB asset gets high-quality projected/baked PBR textures.

Required proof:

- one hero weapon or environment asset retextured;
- BaseColor, Normal, Roughness, Metallic, AO outputs;
- Blender preview;
- in-game Three.js close-up;
- material report;
- hash manifest.

### Route B: Trellis2 / ComfyUI / Texture Projection

Purpose: generate or improve asset candidates using Trellis2, Flux/Qwen/SDXL multi-view texture generation, projection, and Blender repair.

Required proof:

- one prop or gear asset candidate;
- clear record of low/normal VRAM settings used;
- texture projection output;
- Blender seam repair notes or failure reason;
- in-game screenshot.

### Route C: Hunyuan3D 2.1 Shape/Paint Or Equivalent PBR Pipeline

Purpose: test official/near-official shape plus paint/PBR route against Route A/B.

Required proof:

- one asset candidate;
- VRAM/runtime/download requirements;
- output GLB and texture maps if successful;
- failure report if blocked;
- comparison against Route A/B.

Optional follow-up routes:

- Modly for fast local image-to-3D triage.
- Step1X-3D as an observed candidate, not first-line dependency.
- TextureAlchemy, CHORD, PBRFusion4, MaterialAnything, MC PBR Master for PBR-map completion.
- SegviGen/Hunyuan3D-Part for future part segmentation and material-zone separation.

## Target Game Slice

Do not continue expanding the broad compound. Build a small dense micro-slice:

`12m x 18m rainy tactical checkpoint / container-yard / killhouse-entry scene`

Six required evidence cameras:

1. `01_fp_rifle_wet_checkpoint`
2. `02_third_person_player_gear`
3. `03_enemy_under_checkpoint_light`
4. `04_loot_on_wet_asphalt`
5. `05_indoor_killhouse_corridor`
6. `06_final_wide_rainy_container_checkpoint`

The scene must include:

- hero rifle close-up;
- rigged tactical player/enemy;
- helmet, vest, pouches, gloves, backpack/rig;
- wet asphalt/concrete/container PBR materials;
- checkpoint booth, fence, industrial lights;
- clutter: pallets, cones, cables, papers, ammo casings;
- decals: scratches, mud, bullet impacts, warning markings;
- rain/fog/wetness lighting setup;
- playable movement, weapon, NPC, loot behavior preserved.

## Required Work Packages

### W1: Runner Control And Delegation

- Verify `claudeminmax`, `claudekimi`, `gemini`, `runner-review`, `runner-worker`, and managed-artifact MCP health.
- Create reusable worker prompts for visual-upgrade tasks.
- Add task board files under `tasks/visual_upgrade/`.
- Use external runners for at least two read-only reviews and at least one dry-run write-capable worker prompt before implementation.

Exit criteria:

- Runner readiness report exists.
- At least one MiniMax/Kimi review and one Gemini review are recorded.
- Worker prompt dry-run proves narrow write scope and verification.

### W2: Local Model Control Lane On Mac

- Decide between MLX, llama.cpp/GGUF, LM Studio/Ollama wrapper for first local model lane.
- Install only if needed; avoid large model downloads unless no-proxy policy is followed.
- Prefer a small model first to prove local inference and prompt-cache workflow.
- Document when Mac local model is useful versus when to use HomePC or paid runner.

Exit criteria:

- A Mac local inference readiness note exists with selected route and commands.
- No large model download occurs without no-proxy evidence and approval when applicable.

### W3: Asset Packet Schema And Registry V2

- Define asset packet schema for source, model, textures, reports, and evidence.
- Add registry fields for material maps, animations, anchors, LOD, validation, source/license, and runtime proof.
- Build validation script or extend existing verification for asset packets.

Exit criteria:

- Registry v2 validates example asset packets.
- Existing final assets can be represented without lying about missing texture maps.

### W4: Three.js Runtime Upgrade

- Create a new experiment directory, not destructive edits to the existing final packet.
- Migrate production assets toward official `GLTFLoader`.
- Add KTX2/Meshopt readiness, even if initial assets still use PNG/simple GLB.
- Add central asset cache and fail-closed evidence mode.
- Add AnimationMixer-ready runtime.

Exit criteria:

- Old final packet still runs.
- New experiment loads current assets through the new loader where possible.
- Evidence mode fails if fallback assets are used silently.

### W5: Hero Rifle V2

- Upgrade one hero rifle first.
- Ensure anchors: `Muzzle`, `Grip_R`, `Grip_L`, `Optic`, `PickupRoot`, `ThirdPersonMount`.
- Produce PBR map set or a documented failed route with next attempt.
- Integrate first-person, third-person, NPC, and loot/world placement.

Exit criteria:

- `material_map_count >= 4` or explicit blocker with route evidence.
- Four context screenshots exist.
- The first-person screenshot no longer looks like procedural geometry.

### W6: Character Rig And Animation Minimum Set

- Replace static tactical overlay behavior with rigged/animated player/enemy proof.
- Minimum animation clips: idle, walk, run, aim, reload, crouch, hit reaction, death.
- Add weapon socket alignment.

Exit criteria:

- `AnimationMixer` state is visible in evidence reports.
- At least idle, walk, aim, reload evidence screenshots exist.
- NPC behavior remains playable.

### W7: Rainy Checkpoint Environment

- Build the 12m x 18m rainy checkpoint scene.
- Add wet ground, container, booth, fence, lights, clutter, decals, and fog/rain.
- Use instancing for repeated clutter.

Exit criteria:

- Six fixed evidence cameras generate nonblank screenshots.
- No large flat pure-color surfaces dominate target screenshots.
- At least 30 clutter/decal instances are present.

### W8: PBR Pipeline Benchmark

- Run Route A/B/C against representative assets:
  - hero rifle;
  - tactical gear or character piece;
  - wet ground/container/concrete material;
  - loot/medkit prop.
- Compare quality, setup friction, runtime, VRAM, output maps, licensing, and game fit.

Exit criteria:

- A benchmark matrix recommends one primary production route and one fallback.
- Each route has success artifacts or concrete blocker reports.

### W9: Visual Evidence Gate

- Extend browser/CDP gate beyond "asset loaded".
- Check material map count, texture presence, animation state, fallback state, screenshot camera preset, nonblank image stats, console/network errors, and performance budget.
- Generate before/after visual grid.

Exit criteria:

- Gate fails on missing textures for hero assets.
- Gate fails on silent fallback.
- Six screenshots and one final grid are produced.

### W10: Release Packet

Final output directory:

`experiments/tactical_game_visual_upgrade_20260520/`

Required contents:

- playable `index.html`;
- `assets/`;
- `asset_registry_v2.json`;
- asset packets;
- evidence screenshots;
- CDP/browser reports;
- GLTF/Blender/material reports;
- `artifact_hashes.json`;
- `visual_upgrade_report.md`;
- runner review summaries;
- limitations and next decision: continue Three.js or open Unreal migration lane.

Exit criteria:

- A reviewer can judge visual improvement from screenshots and reports without reading code.
- Playability is preserved.
- All artifacts pass hash verification.
- Remaining limitations are minor or clearly assigned to the next production route.

## Completion Criteria

This goal is complete only when all are true:

- Runner control and delegation are operational and documented.
- No large download violated the no-proxy policy.
- At least three production routes are tested or concretely blocked with evidence.
- A new tactical visual-upgrade experiment exists and runs locally.
- Hero rifle V2 has PBR texture-map evidence or a route-blocked failure report plus a better selected fallback.
- Character animation proof exists in runtime, not only in docs.
- Rainy checkpoint micro-slice exists with six target screenshots.
- Visual evidence gate checks material maps, animation state, fallback state, browser errors, and screenshot quality.
- Final release packet, hash manifest, and plain-Chinese summary exist.

## Explicit Non-Completion Conditions

Do not mark complete if:

- the result only adds more procedural GLBs;
- major hero assets remain `material_factors_only` without documented route failure and fallback;
- no runner delegation was actually tested;
- no local/remote GPU production route was proven;
- broad compound expansion replaces the rainy micro-slice;
- screenshots do not visibly improve over `experiments/tactical_game_full_realism_final_20260513/evidence/after_upgraded_gameplay.png`;
- large downloads used proxy traffic or lack evidence.

