# ChatGPT Pro Follow-Up Brief: Full Local AI 3D Asset Factory - 2026-05-13

Repository:

`https://github.com/haizhouyuan/ai-game-generation-research`

## Why This Follow-Up Exists

The earlier GitHub review focused on the browser-playable Three.js tactical-game packet. That packet is useful evidence, but the current goal is stricter:

Build a local-first AI 3D asset factory and use it to rebuild the game toward PUBG-like tactical realism.

This is not a small polish pass. The older procedural/GLB tactical packet is now a baseline and regression reference, not completion.

## Current Active Goal

Read first:

- `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
- `tasks/pubg_like_full_rebuild/README.md`
- `experiments/pubg_like_asset_factory_20260513/reports/hunyuan3d_env_report.md`
- `docs/coding_runner_mcp_skill_control_2026-05-13.md`
- `docs/asset_packet_validation_2026-05-13.md`
- `docs/asset_registry_v3_gate_2026-05-13.md`
- `docs/texture_quality_gate_2026-05-13.md`

Baseline playable packet:

- `experiments/tactical_game_full_realism_final_20260513/index.html`
- `experiments/tactical_game_full_realism_final_20260513/report.md`
- `experiments/tactical_game_full_realism_final_20260513/evidence/`

## What Has Been Done

### Playable Tactical Baseline

The repo contains a browser-playable Three.js tactical-game packet with:

- GLB assets for weapons, characters/tactical overlays, loot, and environment props;
- before/after screenshots;
- CDP/browser evidence reports;
- asset inventory matrix and hash manifest.

Known limitation:

- The visual result is still not commercial/SOTA tactical realism.
- Much of the material work is material factors and procedural/local Blender kit work, not production PBR texture maps.
- It should be treated as an evidence-gated baseline.

### Local Asset Factory Work

The current asset-factory experiment is:

`experiments/pubg_like_asset_factory_20260513/`

Current proof points:

- Hunyuan3D-2.1 repo and model snapshot were installed/downloaded on HomePC with command-local proxy env unset.
- Hunyuan shape-only generation succeeded and produced `hunyuan_shape_demo_001`.
- Hunyuan Paint environment was built separately in Python 3.11; PyTorch CUDA, `bpy`, RealESRGAN, BasicSR/GFPGAN/FaceXLib, `custom_rasterizer`, and `textureGenPipeline` imports were brought up.
- ComfyUI exists on HomePC. `ComfyUI-TextureAlchemy` was installed and a minimal PBR map proof generated basecolor, height, normal, roughness, metallic, AO, and ORM maps for a tactical crate probe.
- Cached TRELLIS generated a non-rifle tactical crate mesh. Blender imported/rendered it. Combined with TextureAlchemy maps, it produced a textured crate probe.
- Kimi/Gemini/MiniMax/Gemini CLI runner routing and MCP/skill configuration were inspected and documented.
- Validators were hardened so current scaffolds cannot be called complete:
  - `tools/validate_asset_packets.py --production-goal`
  - `tools/validate_asset_registry_v3.py --production-goal ...`
  - `tools/validate_texture_quality.py`
- A no-proxy download helper was added:
  - `tools/no_proxy_download.sh`

## Current Blockers And Honest Status

The full asset-factory goal is not complete.

Current fail-closed state:

```bash
python3 tools/validate_asset_packets.py --production-goal
```

Expected current result:

- exits nonzero;
- 12 minimum production assets exist as slots, but are mostly empty scaffolds;
- generated/PBR minimum production packets are `0 / 12`;
- PBR texture packets are `1 / 8`;
- evidence packets are `2 / 12`.

Texture quality gate:

```bash
python3 tools/validate_texture_quality.py
```

Expected current result:

- exits nonzero;
- the probe crate metallic map is detected as solid/placeholder-like.

Hunyuan Paint blocker:

- Paint pipeline currently needs `facebook/dinov2-giant`.
- `config.json` and `preprocessor_config.json` are present.
- `model.safetensors` expected size is `4546005432` bytes, SHA256 `917d3c470db999d32a312f8542149be91c7cbac61ee8fb4b67ae3d82b79ce21f`.
- No-proxy downloads via `huggingface_hub`, `huggingface-cli`, direct `curl`, and `aria2c` reached a partial `4026531840` bytes but stalled/timed out near the end.
- Paid proxy traffic must not be used for large downloads.

## Minimum Production Asset Targets

The active rebuild requires 12 target packets:

1. `hero_rifle_v1`
2. `sidearm_v1`
3. `secondary_weapon_v1`
4. `player_tactical_v1`
5. `enemy_tactical_v1`
6. `gear_set_v1`
7. `wet_asphalt_material_v1`
8. `concrete_wall_material_v1`
9. `container_checkpoint_v1`
10. `loot_set_v1`
11. `clutter_decals_v1`
12. `rainy_checkpoint_scene_v1`

Completion is per-target, not aggregate-only. Route probes, shape-only demos, empty scaffolds, baseline GLBs, and `probe_only` packets do not count as final production assets.

## Local Compute And Agent Setup

Mac:

- Apple M2 Max, 96GB RAM;
- control plane, repo integration, browser evidence, coding, orchestration;
- local MLX/Ollama/llama.cpp not yet installed as production capacity.

HomePC:

- dual RTX 3090 class GPU target;
- Hunyuan3D, TRELLIS, ComfyUI, Blender render/bake jobs;
- large model downloads must use command-local no-proxy evidence.

Coding agents:

- Kimi: stronger coding/blocker analysis/integration critique.
- Gemini CLI: strong broad review/research/visual critique; must use `gemini-3.1-pro-preview`.
- MiniMax: mechanical/report/schema/hash/status tasks only.
- Codex: orchestration, merge review, evidence gates, final judgment.

Relevant docs:

- `docs/coding_runner_mcp_skill_control_2026-05-13.md`
- `docs/mac_local_runner_capacity_2026-05-13.md`
- `tasks/pubg_like_full_rebuild/full_rebuild_strict_goal_review_009.gemini_review.txt`
- `tasks/pubg_like_full_rebuild/full_rebuild_strict_goal_review_009.kimi_review.txt`

## What We Need From ChatGPT Pro

Please use GitHub access to inspect the repo and answer with concrete recommendations, not generic encouragement.

Focus areas:

1. **Visual target and scene design**
   - What is the best next vertical slice: rainy checkpoint, container yard, killhouse corridor, or another compact tactical scene?
   - What exact six screenshots should define success?

2. **Asset production workflows**
   - For each asset class, recommend the strongest practical local or hybrid route:
     - hero rifle / sidearm / secondary weapon;
     - tactical characters and gear;
     - loot props;
     - wet asphalt/concrete/container/checkpoint materials;
     - clutter and decals.
   - Do not assume one model can do everything. Split geometry, texture/PBR, cleanup, animation, and runtime.

3. **Tool research**
   - Find current best community workflows and tools for local 3D asset generation and PBR:
     - Hunyuan3D 2.1/2.x;
     - TRELLIS/TRELLIS.2;
     - ComfyUI Texture Projection / 3D Pack;
     - TextureAlchemy, CHORD, PBRFusion, MaterialAnything or equivalents;
     - StableGen / Blender-first workflows;
     - Modly, Step1X-3D, TripoSR/TripoSG;
     - mesh cleanup, retopo, LOD, collision, UV, glTF validation.
   - Include links and explain what proof would count locally.

4. **DINOv2/Hunyuan Paint blocker**
   - Suggest no-proxy alternatives for obtaining the exact `facebook/dinov2-giant/model.safetensors` or a valid replacement path.
   - If Hunyuan Paint remains blocked, recommend a robust alternate PBR/material route.

5. **Three.js runtime**
   - What should be implemented to receive real assets:
     - GLTFLoader, KTX2, Meshopt, DRACO;
     - AnimationMixer;
     - decals/instancing;
     - postprocessing;
     - evidence cameras;
     - fail-closed asset registry.

6. **Agent/work factory**
   - How should tasks be split across Codex, Kimi, Gemini CLI, MiniMax, HomePC GPU, and Mac?
   - Which tasks should run in parallel now?
   - What should be automated so the factory can repeatedly produce asset packets?

7. **Next 7-14 day plan**
   - Give an implementation plan with concrete artifacts, owners, and acceptance gates.
   - Include "do not waste time" guidance.

## Desired Answer Shape

Please return:

- blunt current-state assessment;
- ranked tool/workflow recommendations with links;
- per-asset pipeline table;
- DINOv2/Hunyuan blocker resolution options;
- Three.js runtime upgrade checklist;
- agent/work routing plan;
- 7-14 day execution plan;
- top risks and non-completion traps.
