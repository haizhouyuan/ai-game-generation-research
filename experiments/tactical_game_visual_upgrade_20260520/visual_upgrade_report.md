# Tactical Visual Upgrade Release Report - 2026-05-13

## Plain-Chinese Summary

这次不是把旧 HTML 随便再塞几个模型，而是新建了一个独立的 Three.js 视觉升级包：

`experiments/tactical_game_visual_upgrade_20260520/`

现在它已经能跑一个更密的雨夜战术检查点小场景，有六个固定截图机位、浏览器 CDP 自动证据、PBR hero rifle 资产包、角色运行时动画证明、雨/雾/湿地/灯光/decals/clutter，以及哈希清单。

说人话：它已经从“能加载 GLB 的原型”推进到“有一个可检查的真实感 vertical slice”。但它还不是最终商业级游戏资产生产线。枪已经有 PBR 贴图证明，角色还只是 runtime proxy rig，不是正式绑定角色 GLB；Hunyuan3D、StableGen、Texture Projection 这些更强路线还没有完成安装和生产验证。

## Playable Entry

Run from repo root:

```bash
python3 -m http.server 8877
```

Open:

```text
http://127.0.0.1:8877/experiments/tactical_game_visual_upgrade_20260520/index.html
```

Six evidence cameras:

1. `01_fp_rifle_wet_checkpoint`
2. `02_third_person_player_gear`
3. `03_enemy_under_checkpoint_light`
4. `04_loot_on_wet_asphalt`
5. `05_indoor_killhouse_corridor`
6. `06_final_wide_rainy_container_checkpoint`

## What Changed

### Runtime

- Added a new non-destructive experiment instead of editing the prior final packet.
- Added official `GLTFLoader` path with asset cache, fallback tracking, registry gate summaries, and KTX2/Meshopt readiness fields.
- Added runtime `AnimationMixer` proof for tactical player/enemy proxy rigs.
- Added CDP visual evidence gate that checks screenshot readability, browser blocking events, animation state, hero rifle material maps, anchors, and silent fallback.

### Hero Rifle V2

- Added `target_hero_rifle_v2` as a local Blender-first PBR asset packet.
- Added 5 texture maps: BaseColor, Normal, Roughness, Metallic, AO.
- Added required anchors: `Muzzle`, `Grip_R`, `Grip_L`, `Optic`, `PickupRoot`, `ThirdPersonMount`.
- Mounted the same rifle in first-person, third-person player, NPC, and world-loot contexts.
- All six browser evidence reports pass with `heroRifleOk: true` and `fallbackUsed: false`.

### Characters

- Added runtime-visible player/enemy tactical proxy rigs.
- Added required clips: idle, walk, run, aim, reload, crouch, hit reaction, death.
- Each evidence camera forces a different active animation state so the reports prove `AnimationMixer` is active.

### Scene

- Replaced the broad sparse compound direction with a 12m x 18m rainy checkpoint / container-yard / killhouse-entry micro-slice.
- Added wet asphalt, booth, containers, fence, industrial lights, fog/rain, decals, cables, cones, pallets, papers, casings, and loot context.
- Scene probe reports `clutterOrDecalInstances: 55`, passing the 30-instance threshold.

## Evidence

Core visual proof:

- `evidence/final_visual_grid.png`
- `evidence/01_fp_rifle_wet_checkpoint.png`
- `evidence/02_third_person_player_gear.png`
- `evidence/03_enemy_under_checkpoint_light.png`
- `evidence/04_loot_on_wet_asphalt.png`
- `evidence/05_indoor_killhouse_corridor.png`
- `evidence/06_final_wide_rainy_container_checkpoint.png`

Core reports:

- `reports/visual_evidence_gate_2026-05-13.md`
- `reports/hero_rifle_v2_2026-05-13.md`
- `reports/character_animation_proof_2026-05-13.md`
- `reports/pbr_pipeline_benchmark_2026-05-13.md`
- `reports/threejs_loader_migration_001.md`
- `reports/asset_registry_v2_001.md`

Asset packet proof:

- `assets/weapons/hero_rifle_v2/model/optimized.glb`
- `assets/weapons/hero_rifle_v2/textures/*.png`
- `assets/weapons/hero_rifle_v2/reports/material_report.json`
- `assets/weapons/hero_rifle_v2/reports/blender_cleanup_report.json`
- `assets/asset_registry_v2.json`

Hash proof:

- `artifact_hashes.json`

## Route Benchmark

Primary route for now:

- Blender-first PBR fallback. It is proven by `hero_rifle_v2`, browser screenshots, material reports, and hashes.

Secondary route:

- Cached HomePC TRELLIS. It can generate mesh-only rifle candidates in about 7.6-8.1 seconds on RTX 3090, but current outputs have no useful PBR texture maps, so it is not selected as final hero-asset route yet.

Blocked next routes:

- StableGen / Texture Projection / TextureAlchemy: not found in current local/HomePC installs.
- Hunyuan3D 2.1: no local install or model cache found; likely requires governed large downloads and an explicit HomePC GPU setup packet.

## Runner And MCP State

Runner setup is documented in:

- `docs/runner_control_readiness_2026-05-13.md`
- `docs/runner_snapshots/local_coding_runners_2026-05-13/`

Routing rule now in force:

- Kimi: stronger implementation/review tasks with real code understanding.
- Gemini CLI: broad research, architecture, and high-quality review through `gemini-3.1-pro-preview`.
- MiniMax: only narrow, mechanical, low-complexity tasks.

MCP proof:

- Managed artifact verifier connected for MiniMax, Kimi, and Gemini.
- Managed game factory MCP connected project-side.
- Prior review packet recorded Gemini, Kimi, and MiniMax review outcomes under `tasks/visual_upgrade/`.

Final release review:

- `tasks/visual_upgrade/final_release_review_prompt_001.gemini_review.txt`: `VERDICT: APPROVE`.
- `tasks/visual_upgrade/final_release_review_prompt_001.kimi_review.txt`: timed out after 300 seconds; no blocking finding was returned.

## Verification Commands

These passed after the hero rifle and evidence updates:

```bash
./.venv/bin/python -m pytest tests/test_validate_asset_registry_v2.py
./.venv/bin/python tools/validate_asset_registry_v2.py experiments/tactical_game_visual_upgrade_20260520/assets/asset_registry_v2.json
python3 -m py_compile experiments/tactical_game_visual_upgrade_20260520/tools/build_hero_rifle_v2.py
node --check experiments/tactical_game_visual_upgrade_20260520/src/main.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/animationSystem.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/lightingSystem.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/weatherSystem.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/decalSystem.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/scene/rainyCheckpointLayout.js
node --check experiments/tactical_game_visual_upgrade_20260520/tools/visual_evidence_gate.mjs
./.venv/bin/python tools/verify_artifact_hashes.py experiments/tactical_game_visual_upgrade_20260520/artifact_hashes.json
```

With the local server on port `8877`, all six visual gates passed with `animationOk: true` and `heroRifleOk: true`.

## Limitations

- Hero rifle V2 is a credible local PBR proof, not a final commercial-grade weapon model.
- Character animation is runtime-visible through proxy rigs, not a cleaned production character GLB with artist-authored skeletal animation.
- Wet asphalt/container/loot realism is currently runtime/procedural, not a full per-asset baked PBR packet.
- StableGen, Texture Projection, TextureAlchemy, and Hunyuan3D 2.1 are not yet locally proven.
- No large model download was attempted in this pass, so no proxy-cost risk was introduced.

## Next Decision

Continue Three.js for the next production pass. The current blockers are asset generation and PBR workflow maturity, not engine migration.

Open an Unreal lane only after one of these is true:

- Hunyuan3D or StableGen produces clearly better PBR assets than the Blender-first fallback;
- the Three.js renderer becomes the bottleneck for lighting, animation, or asset volume;
- the project needs cinematic/editor tooling more than browser-deliverable evidence.
