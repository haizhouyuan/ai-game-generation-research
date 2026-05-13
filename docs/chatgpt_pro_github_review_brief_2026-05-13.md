# ChatGPT Pro GitHub Review Brief - 2026-05-13

## Purpose

This brief is for an external ChatGPT Pro/GitHub review of the public repository:

`https://github.com/haizhouyuan/ai-game-generation-research`

The review should not only summarize the repo. It should judge the current Three.js tactical-game vertical slice, then focus on the active full local AI 3D asset-factory rebuild: how to get from the current browser-playable baseline to PUBG-like realistic assets through reference generation, local image-to-3D, PBR/texture generation, Blender cleanup, runtime integration, and evidence gates.

## Repository Entry Points

Read these first:

1. `README.md`
2. `docs/chatgpt_pro_full_asset_factory_followup_2026-05-13.md`
3. `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
4. `tasks/pubg_like_full_rebuild/README.md`
5. `experiments/pubg_like_asset_factory_20260513/reports/hunyuan3d_env_report.md`
6. `docs/coding_runner_mcp_skill_control_2026-05-13.md`
7. `docs/asset_packet_validation_2026-05-13.md`
8. `docs/asset_registry_v3_gate_2026-05-13.md`
9. `docs/texture_quality_gate_2026-05-13.md`
10. `experiments/tactical_game_full_realism_final_20260513/README.md`
11. `experiments/tactical_game_full_realism_final_20260513/report.md`
12. `experiments/tactical_game_full_realism_final_20260513/assets/asset_inventory_matrix.json`
13. `docs/full_realism_lessons_and_best_practices_2026-05-13.md`
14. `docs/repository_publication_inventory_2026-05-13.md`

Historical context is useful, but older dated docs can conflict with later state. Prefer the full asset-factory follow-up brief and production goal above when judging what should happen next.

## Current Playable Target

Final playable file:

`experiments/tactical_game_full_realism_final_20260513/index.html`

Source snapshot preserved in repo:

`experiments/tactical_game_full_realism_final_20260513/source/14.html`

Important evidence:

- `experiments/tactical_game_full_realism_final_20260513/evidence/before_source_gameplay.png`
- `experiments/tactical_game_full_realism_final_20260513/evidence/after_upgraded_gameplay.png`
- `experiments/tactical_game_full_realism_final_20260513/evidence/final_evidence_cdp.png`
- `experiments/tactical_game_full_realism_final_20260513/evidence/*_report.json`
- `experiments/tactical_game_full_realism_final_20260513/artifact_hashes.json`

## Known Current State

The final packet has integrated GLB assets for weapons, player/enemy tactical overlays, loot, environment props, and a browser evidence gate. It is materially better than the original prototype, but it should be reviewed honestly:

- It is still an HTML/Three.js vertical slice, not a production game.
- The material grade is `material_factors_only`, not baked full PBR texture maps.
- The runtime still uses a custom embedded GLB loader path in the experiment, not a production `GLTFLoader` pipeline with KTX2/Meshopt/DRACO decisions.
- The current scene is a broad tactical compound, not yet a tightly art-directed AAA-quality slice.
- The useful next step is likely a smaller, denser, more cinematic scene with stronger lighting, PBR textures, decals, clutter, composition, and animation.

After that first packet, the active goal was tightened substantially. The repo now treats the older packet as a baseline, not completion. The active rebuild requires 12 minimum production asset targets to become real asset packets, with reference/provenance, generated or rebuilt 3D/PBR outputs, Blender cleanup, Three.js evidence, and fail-closed validators. Current validators intentionally fail because the production assets are mostly scaffolds.

## Questions To Answer

Please answer in a concrete, implementation-oriented way:

1. For the current HTML/Three.js tactical game, what is the best scene-design direction if the goal is a very high-quality realistic tactical look?
2. Should the next visual target be a compact training range, warehouse/container yard, indoor tactical corridor, rainy street/checkpoint, or another scene type? Explain the tradeoff.
3. What are the highest-leverage visual gaps in the current final packet: lighting, materials, texture maps, geometry density, animation, camera, postprocessing, scene composition, or asset fidelity?
4. What exact asset pipeline should be used for realistic weapons, tactical characters, gear, loot, and environment props?
5. Which mature tools or open-source projects should be tested next for local or API-assisted 3D asset generation/cleanup/validation?
   Include current community practice for Hunyuan3D 2.1/2.x, TRELLIS/TRELLIS.2, ComfyUI Texture Projection, TextureAlchemy, StableGen, Modly, Step1X-3D, TripoSR/TripoSG, MaterialAnything, CHORD/PBR tools, Blender addons, and Three.js glTF optimization.
6. For guns specifically, what should be modeled or replaced first so first-person and third-person screenshots stop looking procedural?
7. For character motion, what is the practical path from the current overlay-style character visuals to believable movement and tactical actions?
8. If we stay in HTML/Three.js, what runtime changes are needed: `GLTFLoader`, KTX2, Meshopt, animation mixer, decals, instancing, lightmaps, environment maps, postprocessing, or asset streaming?
9. If HTML/Three.js is the wrong target for SOTA realism, what would be the lowest-risk migration path to Unity, Unreal, PlayCanvas, or Babylon while preserving the current evidence workflow?
10. What should be the next 7-day execution plan, split into independent agent/worker tasks with clear artifacts and acceptance gates?
11. For local-first deployment, how should Mac M2 Max 96GB and HomePC dual RTX 3090 be split between orchestration, image/reference generation, image-to-3D, PBR, Blender, and runtime evidence?
12. Given the current DINOv2/Hunyuan Paint download blocker, what no-proxy mirror/download or alternate paint/PBR strategy should be tried next?
13. How should coding agents be routed across Kimi, Gemini CLI (`gemini-3.1-pro-preview`), MiniMax, Claude-compatible workers, and MCP/skill tools to maximize throughput without false completion?

## Expected Output

Return:

- A blunt assessment of whether the current repo has enough evidence and where it is weak.
- A ranked list of development directions.
- A recommended next vertical slice with exact asset classes and screenshots to produce.
- A tool shortlist with why each tool is worth trying and what proof would count.
- A concrete task breakdown that can be handed to coding/research agents.
- A research list of better tools/methods for the blocked or weak links, with links/sources and what proof would count locally.
- A "do not waste time on this" list.

Do not optimize for politeness. Optimize for a path that can actually make the game look much more realistic.
