# Unity Agent Workchain Research - 2026-05-12

## Goal

Build a multi-agent AI game-development workchain that can move beyond a one-off HTML prototype into a repeatable Unity-centered pipeline:

- game concept and mode design;
- asset and style generation;
- 3D asset creation and cleanup;
- Unity scene/project construction through agent/MCP tooling;
- playable prototype verification;
- evidence capture and regression review.

The immediate research question is not "can we make another demo", but "which links are already reusable, which current tools should be adopted, and what must be validated next before the Unity chain is trusted".

## Starting Point

The original ChatGPT HTML game artifact has now been recovered:

- Source: `/Users/yuanshaochen/Documents/14.html`
- Captured baseline: `experiments/game_p0_chatgpt_html_baseline_20260509/14.html`
- Report: `experiments/game_p0_chatgpt_html_baseline_20260509/report.md`

It is a 98KB single-file Three.js tactical compound survival game titled `战术房区生存：视觉真实感优化版`. It already contains a lobby, procedural 3D compound, first/third-person controls, weapons, NPCs, loot, armor, healing, revive, settings, sky modes, and a skin lottery.

The referenced Codex thread `019e0c2d-58f3-7240-ae17-d76b06c95244` was found at:

- `/Users/yuanshaochen/.codex/sessions/2026/05/09/rollout-2026-05-09T17-59-19-019e0c2d-58f3-7240-ae17-d76b06c95244.jsonl`
- `/Users/yuanshaochen/.codex/shell_snapshots/019e0c2d-58f3-7240-ae17-d76b06c95244.1778320759027918000.sh`

That thread itself does not contain the original ChatGPT Pro HTML game artifact. Its working directory was `/Users/yuanshaochen/Documents/New project`, which currently contains only `.git`.

Other local playable artifacts in this repo:

- `experiments/game_e2_isometric_miniloop/index.html`
- `experiments/game_e3_engine_import_or_playable/index.html`
- `experiments/game_p2_glb_three_import_loop/index.html`
- `experiments/game_p5_triposr_three_playable_loop/index.html`

The original first-person/3D HTML file likely still lives in the ChatGPT App/web conversation, browser downloads, or another local folder not yet identified.

## Existing Capabilities To Solidify

| Capability | Current state | Solidification decision |
|---|---|---|
| Browser playable baseline | `GAME-E2` and `GAME-E3` prove directly playable local web games with movement, pickups, hazards, and finish conditions. | Keep as smoke-test and child-friendly demo baseline. |
| Three.js GLB playable validator | P2 proves GLB import, local playable loop, DOM status, screenshots, and pixel checks. | Promote to reusable `three-glb-playable-loop` template/validator. |
| TripoSR image-to-GLB | P3-P5 prove offline/no-proxy image-to-GLB and Three.js parsing/playable integration. | Promote as experimental command only; keep `torchmcubes` shim caveat explicit. |
| Godot GLB import | P6 proves HomePC Godot 4.4.1 imports three GLBs as `PackedScene` with mesh/bounds checks. | Promote as `godot-headless-glb-import-check` after runtime preflight. |
| Godot scene-builder gate | P7-P14 prove headless scene scaffold, proxy colliders, objective nodes, signal replay, input replay, and camera assertions. | Promote as reusable headless engine assertion gate. |
| Godot scene CI | P15-P21 add reusable scene-CI, multi-layout matrix, negative fixtures, compact traces, hash baselines, and review modes. | Promote as command-level evidence workflow. |
| Reviewer contract and artifact integrity | P22-P25 add exit-code contract, negative contract fixtures, version migration, integrity manifest, dependency graph, stale/orphan counters. | Promote as evidence/review contract layer. |
| Visual QA, mesh-accurate collision, human feel | Explicitly unclaimed through P25. | Must remain next-phase work; do not present as solved. |

## Current Tooling Signals

### Unity AI / Official MCP

Current Unity material indicates Unity AI is now an open beta suite with AI Assistant, Generators, AI Gateway, and Unity's Official MCP Server. Access requires Unity Editor 6.3+ for the open beta guide, project linkage to Unity Cloud, terms acceptance, AI Assistant package install, and AI credit provisioning. Unity support also documents a recent MCP "Capacity Limit" failure mode when a Unity AI seat is not assigned.

Primary implication: the official Unity path is attractive but likely account/license/credit gated. It should be researched first, then validated only after the editor and account state are known.

Local status on 2026-05-12:

- Unity Editor and Unity Hub were not found under `/Applications`.
- The official relay path `~/.unity/relay/` was not present.
- Therefore, the Unity MCP loop is not yet runnable on this Mac or HomePC.
- The first real Unity validation must start with a disposable Unity 6.x project, `com.unity.ai.assistant`, and the official relay running from Unity settings.

Sources:

- https://docs.unity.com/ai
- https://support.unity.com/hc/en-us/articles/48060149523476-Getting-started-with-Unity-AI-open-beta-user-guide
- https://support.unity.com/hc/en-us/articles/48958235901460-Unity-AI-MCP-connection-fails-with-the-error-message-Status-Capacity-Limit
- https://unity.com/features/ai

### Community Unity MCP

Community Unity MCP projects are active and may be faster to validate than the official gated path. Current search surfaced:

- `CoplayDev/unity-mcp`: broad community MCP candidate for scene/assets/scripts/materials/build/tests/profiler/physics/UI/VFX. It still requires Unity Editor, Python 3.10+, and usually `uv`.
- `IvanMurzak/Unity-MCP`: stronger engineering/extension candidate with Editor + Runtime ambitions, custom C# tool exposure, and CI-oriented positioning.
- `Signal-Loop/UnityCodeMCPServer`: high-power Editor API automation candidate, useful for script/scene/prefab/play-mode/log/screenshot style loops but requires careful disposable-project safety.
- `codemaestroai/advanced-unity-mcp`: lighter community relay path with Unity 2020-2022 and Unity 6 branches.

Primary implication: Unity Agent work should compare official Unity AI MCP against community Unity MCPs on concrete editor-control capabilities: scene mutation, script generation, play mode, screenshots, logs, undo safety, and package/install friction.

### Blender MCP

`ahujasid/blender-mcp` was cloned successfully to:

`external/research_sources/blender-mcp`

Local clone HEAD:

`7636d13`

README highlights:

- Blender add-on plus Python MCP server;
- object creation/manipulation, materials, scene inspection, Python execution;
- viewport screenshots;
- Poly Haven asset search/download;
- Sketchfab model search/download;
- Hyper3D Rodin generation;
- Hunyuan3D support;
- remote host mode.

Primary implication: Blender MCP is a strong asset/scene authoring candidate, but it needs Blender installed locally and a policy for external asset/model downloads.

Source:

- https://github.com/ahujasid/blender-mcp

### OpenGame

OpenGame source archive was downloaded directly and verified:

- `external/research_sources/opengame-main.zip`
- `external/research_sources/OpenGame-main/`

OpenGame is an agentic web-game framework. It is not a Unity pipeline, but it is highly relevant because it formalizes:

- reusable "Game Skill" as Template Skill plus Debug Skill;
- archetype templates such as platformer, top-down, tower defense, grid logic, and UI-heavy;
- headless generation from a prompt;
- evaluation axes: build health, visual usability, and intent alignment.

Primary implication: reuse its architecture ideas for our workchain. Do not blindly adopt its provider stack because its quickstart expects Node/npm and API keys, and local `npm` is not currently installed in this Mac shell.

Source:

- https://github.com/leigest519/OpenGame
- https://arxiv.org/abs/2604.18394

### OpenAI Image Generation

OpenAI current docs list `gpt-image-1.5` as the latest and most advanced GPT Image generation/editing model. For this project, it should be treated as a major production lever for:

- concept art;
- texture/style sheets;
- UI/icon art;
- orthographic references for image-to-3D tools;
- iteration on child-friendly themes and visual consistency.

Source:

- https://platform.openai.com/docs/guides/image-generation
- https://platform.openai.com/docs/models/gpt-image-1.5

### HomePC Asset Generation

HomePC is currently the strongest local asset-generation host:

- Ubuntu 22.04.5;
- 2x RTX 3090 24GB;
- CUDA-capable PyTorch in existing conda envs;
- existing TRELLIS checkout and `TRELLIS-image-large` weights;
- existing ComfyUI tree with Hunyuan3D/Stable3D-related nodes;
- Blender 3.0.1 installed, though the first headless render attempt failed because no display was available.

New P26 result:

- `experiments/game_p26_trellis_meshonly_asset_validation_20260512/`
- Generated `outputs/typical_misc_crate_trellis_meshonly.glb`, 2.1MB, SHA256 `ef03de6e567402ace47af327da875ab10caf093aa1fd209f291371fb82208944`
- Verified by `trimesh`: 54797 vertices, 110066 faces, non-empty, normalized roughly to a 1x1x1 box.
- Verified by existing Three.js/GLTFLoader parser: 1 scene, 1 mesh, 110066 triangles.
- Textured TRELLIS export remains blocked by missing `diff_gaussian_rasterization`; mesh-only export is the working fallback.

### YogaS2 Utility Host

YogaS2 is now reachable from the Mac:

```bash
ssh yoga
```

Observed 2026-05-12 status:

- Hostname: `YogaS2`
- Python: 3.11.2
- Node: 22.22.0
- npm: 10.9.4
- Git: 2.39.5
- Curl: 7.88.1
- Disk: about 21GB free on `/`
- GPU: no `nvidia-smi`
- Default shell environment includes proxy variables pointing at `127.0.0.1:7890`

Primary implication: YogaS2 is a useful lightweight validation/download host for Node/Python/source metadata, but it should not be used for GPU asset generation, large model downloads, or Unity Editor validation. All YogaS2 downloads must use command-local proxy cleanup.

## No-Proxy Download Experiment

Policy: do not modify Clash Verge, system proxy, shell profile, or Codex networking. Disable proxy only for the child download command.

Working command pattern:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  curl --proxy "" --noproxy "*" -L URL
```

Git pattern:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null \
  git -c http.proxy= -c https.proxy= clone --depth=1 URL TARGET
```

Observed proof:

- During direct `curl`/`git` operations, `curl` and `git-remote` connected to GitHub IPs such as `20.205.243.166:443`, not `127.0.0.1:7897`.
- Codex, ChatGPT, and other apps remained connected through `127.0.0.1:7897`.

This supports command-local direct downloads while preserving Codex's proxy dependency.

Risk:

- If Clash Verge TUN/transparent proxy is enabled, environment cleanup might not bypass proxy. Continue verifying each large download with `lsof -nP -iTCP`.
- GitHub direct downloads can be slow or hang. Use `--max-time`, resumable downloads, checksums, and small source archives before large assets/models.

## Immediate Workchain Threads

1. `capability-solidifier`
   - Promote existing Three.js/Godot/reviewer-contract experiments into command templates or skills.
   - First outputs: `three-glb-playable-loop`, `godot-scene-ci`, `scene-ci-review-contract`.

2. `unity-agent-researcher`
   - Compare official Unity AI MCP, CoplayDev/unity-mcp, IvanMurzak AI Game Developer MCP, advanced-unity-mcp, and UnityCodeMCPServer.
   - First outputs: capability matrix, install matrix, license/account risk, minimal proof plan.

3. `asset-pipeline-researcher`
   - Rank `gpt-image-1.5`, Blender MCP, TripoSR, Hunyuan3D/TRELLIS-style tools, Hyper3D/Rodin, Poly Haven/Sketchfab paths.
   - First outputs: child-safe asset workflow, no-proxy policy, asset provenance schema.

4. `game-design-agent`
   - Convert the initial HTML-game excitement into a stronger design brief and mode library.
   - First outputs: playable loop candidates, target audience rules, Unity prototype spec.

5. `download-verifier`
   - Wrap all external downloads with command-local no-proxy templates, lsof checks, timeout, hash ledger, and source manifest.
   - First outputs: reusable `download_no_proxy` script and evidence report.

## Next Validation Targets

1. Install/runtime inventory:
   - Unity Hub / Unity Editor are not currently visible under `/Applications`.
   - Blender is not currently visible under `/Applications`.
   - `npm` is not currently available in the active shell.
   - YogaS2 has `npm`, but no GPU and limited disk.

2. Unity path:
   - Decide whether to install Unity Hub/Unity 6.3+ first, or validate a community Unity MCP source package before editor install.
   - Do not download Unity editor packages until no-proxy strategy is explicitly verified for that installer path.

3. ChatGPT App deep-research bridge:
   - Computer Use is currently blocked from controlling `com.openai.chat` in this environment.
   - Alternative: use web/search plus Codex subagents for now; revisit ChatGPT App bridge only if the app becomes allowed or a connector/tool exists.

4. Original HTML artifact:
   - Recovered and captured as P0 baseline.
   - Next: add automated playable smoke test for entering the game, loading Three.js, and verifying HUD/canvas state after start.

5. P26 continuity:
   - P26 now also includes a HomePC TRELLIS mesh-only asset validation result.
   - Continue toward Three.js/Godot import checks for the generated GLB, then Unity import once Unity Editor/MCP are available.
