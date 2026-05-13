# Production Goal: PUBG-Like Full AI 3D Asset Pipeline And Tactical Game Rebuild - 2026-05-13

## Objective

彻底重做当前 HTML/Three.js tactical game 的视觉资产生产线和最终 playable slice。

这不是“在旧模型上稍微升级一点”。完成标准是：以 PUBG / 现代真实战术游戏为视觉方向，把主要可见资产都通过真实参考图、image-to-3D、本地 3D/PBR 生成、Blender 清理、Three.js 集成和浏览器证据 gate 跑通。

最终结果必须让人一眼看出：这不是旧版 procedural/GLB prototype，而是使用真实 3D 资产生产流程重建的高真实感 tactical vertical slice。

Strong interpretation:

- 旧资产只能作为 baseline、尺寸参考、回归对照或临时占位，不能作为最终完成的主体。
- 目标不是把旧 HTML “调好看一点”，而是让当前游戏场景像一套真实 3D 模型资产重新生产后落进游戏。
- 所有近景/主视角/经常出现在镜头里的资产都必须有独立生产链路记录：参考图、生成或建模路线、贴图/PBR、Blender 清理、运行时截图。
- 必须并行测试多条本地资产生产链路；不能因为 Hunyuan 跑通 shape-only 就跳过 ComfyUI/TRELLIS/PBR 投影等路线。
- Codex 自身不应亲自吞掉所有重复劳动；必须持续把明确、可验收、窄范围的任务交给 Kimi/Gemini/MiniMax/本地 runner/HomePC GPU worker。

Full-rebuild interpretation:

- 最终 playable slice 必须以“新生产资产”为主体；旧版 procedural/embedded GLB 只能用于 before/after 对照、尺寸标尺、失败回退说明，不能充当完成证据。
- 最低生产目标中的 12 类资产都必须进入新资产包；每个资产包至少要有 reference/provenance、route report、Blender inspection/cleanup report、hash entry 和运行时接入状态。
- 近景核心资产必须走完整链路：真实参考图或 AI 生成真实参考图 -> 本地 3D 生成/混合建模路线 -> PBR/纹理路线 -> Blender 清理/预览 -> Three.js 近景和 gameplay context 证据。
- 关键近景资产包括 hero rifle、player tactical character、enemy tactical character、wet asphalt、container/checkpoint booth、loot pickup。它们不能只满足“有模型加载”，必须有可见真实纹理、材质变化和 close-up 截图。
- 所有路线都要实测并给出结论：Hunyuan3D 2.1 shape+paint、ComfyUI/PBR 或投影路线、TRELLIS/TRELLIS.2 mesh route、Blender cleanup、Three.js production loader/runtime gate。失败也必须是带命令、日志和下一步的失败，不能是未尝试。
- “像 PUBG/现代真实战术游戏”在本项目里的验收含义是：第一眼画面里有真实尺度、真实材质、装备和武器细节、湿地/墙面/容器磨损、角色动作、密集小道具和灯光后处理，而不是低多边形玩具感。
- Final completion is per-target, not aggregate-only. Route probes, shape-only demos, scaffold directories, baseline GLBs, and `probe_only` packets do not count toward production completion.
- Hunyuan, ComfyUI/PBR, and TRELLIS route probes are mandatory pipeline evidence, but route success does not automatically make an asset production-ready. A production asset must also pass Blender cleanup, PBR/material report, optimized export, Three.js close-up, gameplay-context screenshot, hash verification, and registry v3 validation.

## Source Repo

`/Users/yuanshaochen/Projects/ai-game-generation-research`

## Non-Negotiable Intent

- 目标不是小修小补，而是完整资产工厂和游戏资产重建。
- 每类主资产都要有真实参考图或 AI 生成真实参考图。
- 每类主资产都要至少跑一条本地 3D 生成或 PBR 生产路线。
- hero/near-camera/mission-critical 资产必须优先尝试 image generation -> image-to-3D -> PBR/texture -> Blender -> Three.js 的完整闭环。
- 资产不能只靠 material factors；hero/near-camera assets 必须有贴图地图。
- 能下载模型，但大文件下载必须不走付费代理流量。
- Codex 做总控和合并，Kimi/Gemini/MiniMax/本地 runner 并行执行窄任务。

## Download Policy

Downloads are allowed.

Rules:

1. Any single external download over 100MB must use command-local no-proxy settings:

```bash
env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl --noproxy '*' -L --fail --continue-at - --output OUTPUT URL
```

2. Prefer `aria2c`, `git lfs`, `huggingface-cli`, or `hf download` only when proxy env is explicitly unset and the command records evidence.
3. Record URL/repo, expected size when available, command, resolved host/IP when practical, output path, SHA256 or git revision, and proof that proxy env vars were unset.
4. Do not change global Clash, shell proxy, Homebrew proxy, or system proxy settings.
5. If a single file is clearly over 1GB, record exact repo/file/version before download; the user has authorized model downloads for this goal, so proceed when the route is necessary and no-proxy evidence is recorded.

Repo helper:

```bash
tools/no_proxy_download.sh URL OUTPUT REPORT
```

Use the helper for direct file downloads when practical. For `git lfs`, `hf download`, or custom model tools, reproduce the same evidence shape in the route report.

## Required Tool Routes

### Route A - Realistic Reference Images

Use AI image generation or local/reference sources to create high-quality realistic references for:

- hero rifle / optic / magazine / attachment set;
- player tactical character front/side/back plus gear detail;
- enemy tactical character variant;
- backpack, vest, helmet, pouch, gloves, boots;
- wet asphalt, concrete wall, container wall, checkpoint booth;
- loot props: medkit, ammo box, weapon pickup, casing/shells;
- decals: mud, scratches, impacts, warning markings.

Required output:

- reference images;
- prompt/source/provenance;
- SHA256;
- downstream asset mapping.

Acceptance:

- at least 10 named reference sets exist before final release;
- at least 6 reference sets feed a generated/PBR-authored asset packet;
- prompts must target realistic worn tactical materials, not stylized sci-fi or clean toy-like objects.

### Route B - Hunyuan3D 2.1 Shape + Paint/PBR

Install and run Tencent Hunyuan3D-2.1 locally, primarily on HomePC GPU1.

Official facts to respect:

- Hunyuan3D-2.1 is an image-to-3D / text-to-3D system with PBR texture synthesis.
- Official repo reports approximate VRAM needs: shape 10GB, texture 21GB, shape+texture 29GB.
- Official model repo: `tencent/Hunyuan3D-2.1`.
- Model files include shape and PBR paint subfolders, with total storage around 15GB from Hugging Face metadata.

Required proof:

- installation report;
- no-proxy download evidence;
- one successful shape-only generation;
- one successful textured/PBR generation or concrete blocker;
- GLB/OBJ/textures imported into Blender;
- material report showing PBR maps when successful;
- Three.js close-up screenshot.

This route is incomplete until both shape and texture/PBR have been attempted with real commands. A shape-only demo is proof of environment capability, not production completion.

### Route C - ComfyUI 3D Pipeline

On HomePC, configure ComfyUI route(s) for:

- Hunyuan3D 2.1 wrapper if stable;
- Texture Projection / Trellis2 / Flux-Qwen-SDXL multi-view texture route;
- TextureAlchemy / PBRFusion / CHORD / equivalent PBR map completion if practical.

Required proof:

- custom node install inventory;
- workflow JSON;
- one generated/retouched asset;
- exported GLB or texture map set;
- blocker report if dependency conflict occurs.

This route must include at least one practical texture/PBR route, even if the final chosen production path is Hunyuan. Candidate routes include Texture Projection, TextureAlchemy, PBRFusion, CHORD-like map estimation, StableGen/Blender bridge, or equivalent local workflow.

### Route D - TRELLIS / TRELLIS.2 Mesh Route

Current TRELLIS mesh-only evidence is not enough.

Required next proof:

- run current cached TRELLIS on at least one non-rifle prop or gear item;
- attempt texture/PBR improvement via Route C or Blender;
- record why TRELLIS is or is not suitable for final hero assets.

TRELLIS is not allowed to remain only a “we know it exists” research note; it must produce or fail on a concrete tactical asset candidate with evidence.

### Route G - Local Mac Model/Runner Capacity

Mac M2 Max 96GB is the control plane, but it should also be prepared as overflow local inference capacity where useful.

Required:

- document whether MLX, llama.cpp, Ollama, or another local runner is most suitable for lightweight local worker tasks;
- do not let this block HomePC GPU production;
- use it for summarization, OCR/classification, prompt variation, or simple QA only unless a local 3D/vision model is clearly practical.

Exit:

- local model runner recommendation;
- one dry-run local worker task or concrete reason to defer.

### Route E - Blender Production Cleanup

Every generated candidate that reaches the game must pass Blender cleanup:

- scale/origin/orientation normalized;
- named anchors/sockets;
- UV/material inspection;
- decimate/retopo where needed;
- collision/proxy where needed;
- PBR map wiring;
- preview render;
- cleanup report.

### Route F - Three.js Runtime Replacement

The game must replace old/procedural placeholders with generated asset packets.

Required:

- official `GLTFLoader`;
- KTX2/Meshopt readiness;
- runtime asset registry v3;
- fail-closed fallback for hero assets;
- material map count gate;
- animation state gate;
- browser/CDP screenshot gate.

## Asset Classes That Must Be Rebuilt

Minimum production targets:

1. Hero rifle with optic and attachments.
2. Sidearm.
3. At least one additional visible weapon class or tactical weapon pickup beyond the hero rifle and sidearm.
4. Player tactical character with gear.
5. Enemy tactical character variant.
6. Helmet/vest/pouches/backpack/gloves/boots as visible gear modules or a generated combined character packet.
7. Wet asphalt ground material.
8. Concrete wall material.
9. Container wall / checkpoint booth asset.
10. Loot set: medkit, ammo box, weapon pickup.
11. Clutter/decal set: casings, paper, cable, cone, pallet, mud/scratch/impact decals.
12. Rainy checkpoint/killhouse micro-scene assembled from generated/PBR assets.

Each target must become an asset packet:

```text
asset_id/
  source/reference.md
  source/license.md
  source/images/
  model/raw.*
  model/cleaned.*
  model/optimized.glb
  textures/basecolor.*
  textures/normal.*
  textures/roughness.*
  textures/metallic.*
  textures/ao.*
  reports/blender_cleanup_report.json
  reports/material_report.json
  reports/gltf_validator_or_inspect.json
  evidence/blender_preview.png
  evidence/threejs_closeup.png
  evidence/gameplay_context.png
```

## Runner Orchestration Rules

Codex:

- owns goal, task board, merge review, evidence gates, final judgement.

Kimi:

- complex implementation, code review, route blocker analysis, integration critique.

Gemini CLI:

- broad research, visual direction critique, tool comparison, final review;
- must use `gemini-3.1-pro-preview`, not default model.

MiniMax:

- only narrow mechanical tasks: report formatting, hash manifest checks, simple schema updates, first-pass low-risk review.

Efficiency rule:

- prefer moving work out to runners once a task can be specified in a bounded packet;
- Kimi and Gemini can handle harder reasoning/review tasks;
- MiniMax should not own ambiguous architecture or complex coding;
- every runner output must be saved under `tasks/pubg_like_full_rebuild/` or the relevant experiment report directory.

HomePC GPU:

- Hunyuan3D, ComfyUI, TRELLIS, Blender render/bake, batch texture generation.

Mac M2 Max:

- control-plane, browser evidence, repo integration, lightweight local inference fallback.

## Work Packages

### W0 - Correct Goal And Baseline

- Create this stricter goal.
- Mark previous release as partial W0 baseline, not final completion.
- Create task board for full rebuild.

Exit:

- new goal file exists;
- old packet limitations are explicit.

### W1 - Hunyuan3D 2.1 Installation And No-Proxy Model Acquisition

- Install repo/dependencies on HomePC.
- Download required Hunyuan3D-2.1 model files without proxy traffic.
- Use GPU1 unless GPU0 is intentionally freed.
- Record install, version, model revision, disk, VRAM, command logs.

Exit:

- `hunyuan3d_env_report.md`;
- no-proxy download record;
- import/smoke test passes or concrete dependency blocker.

### W2 - Reference Image Generation

- Generate or collect realistic reference images for all minimum asset classes.
- Prioritize consistent style: rainy tactical, worn metal, wet surfaces, realistic gear.
- Use Codex image generation or local generation routes to create reference images where no suitable local reference exists.
- Create an asset-to-reference matrix before producing final game packets.

Exit:

- 10+ named realistic reference sets with provenance and hashes;
- at least 6 newly generated realistic reference-image sets, not only text prompts;
- asset-to-reference matrix mapping every minimum production asset to a reference set and downstream route.

### W3 - First Hunyuan Asset Chain

- Run Hunyuan3D shape+paint on one small prop first, then hero rifle or gear.
- Prefer loot/medkit or container prop as lower-risk first target.
- The first acceptable chain must start from a realistic reference image, not only an official demo image.

Exit:

- raw generated model;
- textured/PBR output or blocker;
- Blender preview;
- Three.js close-up.

This work package is not complete if the output is shape-only. Shape-only is useful as W1 environment proof, but W3 requires paint/PBR success or a concrete paint blocker plus a parallel alternate PBR route applied to the same asset.

### W4 - Hero Rifle Full Replacement

- Generate or refine hero rifle through Hunyuan/Comfy/TRELLIS+PBR/Blender route.
- Replace current Blender-first proof only if the new asset is visibly better.
- If image-to-3D produces bad firearm geometry, preserve that evidence and switch to hybrid workflow: realistic reference image -> Blender hard-surface cleanup -> PBR texture generation/projection -> Three.js.
- The final rifle may not be a procedural old fallback unless all local image-to-3D attempts fail and a documented hybrid Blender/PBR rebuild visibly beats them.

Exit:

- first-person screenshot looks like a real high-detail tactical game weapon;
- PBR maps and anchors present.
- at least first-person, third-person, loot pickup, and NPC-held evidence views pass.

### W5 - Character And Gear Full Replacement

- Generate/assemble player and enemy characters with realistic tactical gear.
- Add/retarget animation set.
- Use reference front/side/back or equivalent multi-view source; a static tactical overlay is not acceptable as final.

Exit:

- production character GLBs replace runtime proxy rig;
- idle/walk/run/aim/reload/crouch/hit/death evidence.

### W6 - Environment Material And Prop Replacement

- Replace wet asphalt/concrete/container/checkpoint booth/loot/clutter with generated or PBR-authored packets.
- Build a small dense rainy checkpoint/killhouse scene from these packets instead of enlarging the old broad compound.

Exit:

- close-up material screenshots show real texture detail, not flat procedural material.
- ground, wall, container, loot, clutter/decal, and checkpoint booth all have individual packets and gameplay context screenshots.

### W7 - ComfyUI Projection/PBR Pipeline

- Install and validate one ComfyUI workflow for 3D texture/PBR improvement.
- Export asset or texture set into Blender and Three.js.

Exit:

- workflow JSON;
- output asset/textures;
- blocker if dependency conflict.

### W8 - Runtime And Evidence Gate V3

- Extend registry/gate from v2 to v3.
- Require generated asset provenance, PBR maps, no fallback, animation, screenshot readability, and material close-ups.

Exit:

- six old cameras plus additional close-up cameras pass;
- gate fails if generated assets are missing.

### W9 - Final PUBG-Like Slice Release

- Build final release packet under a new dated experiment directory.
- Include playable HTML, assets, references, generated models, textures, Blender reports, CDP reports, final visual grid, and a plain-Chinese release report.
- The release must be a new rebuild experiment, not a rename of the earlier final packet.
- Include before/after evidence against the previous baseline so the visual rebuild is obvious.

Exit:

- reviewer can inspect screenshots and agree it is a real asset-pipeline rebuild;
- all hashes verify;
- pushed to GitHub.

## Completion Criteria

Do not mark complete until all are true:

- Hunyuan3D 2.1 is installed or has a concrete dependency blocker after real no-proxy setup attempt.
- At least one Hunyuan-generated asset reaches Blender and Three.js, unless blocked by documented install/runtime failure.
- At least one ComfyUI/PBR projection or equivalent PBR completion route is tested.
- At least 10 minimum production asset targets have reference/provenance entries.
- All 12 minimum production asset targets have new asset packets with route reports and runtime integration status.
- All 12 minimum production asset targets have generated, rebuilt, or PBR-authored production outputs, not only empty scaffolds.
- At least 8 asset packets must have real texture map sets with `basecolor`, `normal`, `roughness`, and either `metallic` or `ao`.
- All hero, near-camera, loot, character/gear, and environment-surface production packets must have real texture maps. Material factors alone are never acceptable for final visible assets.
- All 12 minimum production asset targets must have Blender preview plus Three.js close-up or gameplay context evidence, unless a target is explicitly removed from the playable slice and from all final evidence cameras.
- At least 6 newly generated realistic reference images exist and are linked to downstream asset packets.
- At least 1 generated reference-image-to-3D chain must start from a newly generated realistic reference image, not only an existing demo/reference.
- Hero rifle is a new/hybrid rebuilt asset with anchors, texture maps, and four runtime contexts, unless all generation attempts have documented failures and a manually rebuilt PBR asset is superior.
- Runtime character proxy is replaced by a production character/gear asset with animation evidence; a concrete blocked route is not final completion, only an interim blocker.
- The final visual slice is substantially rebuilt, not just relit.
- The final playable scene uses the new asset packets as the dominant visible content in all six target cameras.
- Large downloads have no-proxy evidence.
- Any asset/model dependency over 100MB without recorded command-local no-proxy evidence is disqualified from final evidence. Final release must include a download ledger with URL/repo, revision/version, size when available, SHA256 or git revision, command, output path, and proxy-unset proof.
- Kimi/Gemini/MiniMax runner usage follows the routing rules and is recorded.

## Explicit Non-Completion Conditions

This goal is not complete if:

- only the previous `tactical_game_visual_upgrade_20260520` packet is submitted again;
- Hunyuan3D is not actually attempted;
- assets are mostly procedural boxes/cylinders with nicer lighting;
- no AI/reference image to 3D generation chain reaches the game;
- no real PBR texture maps are generated for multiple asset classes;
- any minimum production asset remains only an empty scaffold without a route report;
- hero rifle, character, wet ground, and checkpoint/container assets do not have close-up runtime evidence;
- visual screenshots still look like the previous simple Three.js prototype;
- large downloads happen through proxy traffic or without evidence.
