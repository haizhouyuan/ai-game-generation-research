# AI-Assisted 3D Game Generation Source Registry - 2026-05-11

Trust tiers: `T1` official docs, primary paper, official model page, or official repo; `T2` credible GitHub/tool page; `T3` secondary report/community signal used for discovery only.

Scores use `1-5`: `fit` for game-generation relevance, `local` for local reproducibility, `cost` where higher means lower download/API cost, `maint` for maintenance/activity, and `child-safe` for controllable family workflow after adult setup.

| ID | Source | Category | Tier | Link | Fit | Local | Cost | Maint | Child-safe | First Decision |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| GAME-S01 | OpenGame repo | text-to-playable browser game agent | T1 | https://github.com/leigest519/OpenGame | 5 | 3 | 3 | 5 | 4 | High-priority research target; run only after dependency and model/provider preflight. |
| GAME-S02 | OpenGame paper | agentic coding for games | T1 | https://arxiv.org/abs/2604.18394 | 5 | 4 | 5 | 5 | 4 | Use benchmark workflow as evaluation model even if full run is deferred. |
| GAME-S03 | OpenGame news analysis | secondary capability signal | T3 | https://www.creativebloq.com/3d/video-game-design/this-experimental-open-source-ai-turns-prompts-into-playable-marvel-star-wars-and-harry-potter-games | 4 | 3 | 5 | 3 | 3 | Discovery only; verify claims against repo/paper. |
| GAME-S04 | Godot importing 3D scenes | engine import path | T1 | https://docs.godotengine.org/en/4.0/getting_started/workflow/assets/importing_scenes.html | 5 | 5 | 5 | 5 | 5 | Preferred first engine-import target; GLB/glTF recommended. |
| GAME-S05 | Blender glTF manual | asset conversion/inspection | T1 | https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html | 5 | 4 | 5 | 5 | 5 | Use for GLB/glTF inspection and conversion path. |
| GAME-S06 | Khronos glTF-Blender-IO | importer/exporter code | T1 | https://github.com/KhronosGroup/glTF-Blender-IO | 4 | 4 | 5 | 5 | 5 | Support source for GLB validation details. |
| GAME-S07 | Unity AI | engine AI assistant/MCP | T1 | https://unity.com/features/ai | 4 | 2 | 3 | 5 | 3 | Track for Unity-agent workflows; not first due account/editor weight. |
| GAME-S08 | Unity asset formats | asset import/reference | T1 | https://docs.unity.com/unity-studio/develop/assets/asset-file-formats | 4 | 2 | 4 | 5 | 3 | Use for asset compatibility matrix. |
| GAME-S09 | Unreal FBX content pipeline | engine import path | T1 | https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-content-pipeline?application_version=5.6 | 4 | 1 | 3 | 5 | 3 | Keep as high-end import reference; not first local path. |
| GAME-S10 | Unreal glTF import docs | engine import path | T1 | https://dev.epicgames.com/documentation/pl-pl/unreal-engine/importing-gltf-files-into-unreal-engine?application_version=5.6 | 4 | 1 | 3 | 5 | 3 | Use for GLB/GLTF import comparison. |
| GAME-S11 | TRELLIS official repo | image/text-to-3D assets | T1 | https://github.com/microsoft/TRELLIS | 5 | 2 | 2 | 5 | 4 | Strong asset-generation target; HomePC only after cache/mirror plan. |
| GAME-S12 | TRELLIS project clone | community packaged repo | T3 | https://github.com/m4rio/TRELLIS-Tripo-3D | 3 | 2 | 2 | 2 | 3 | Do not use until official repo path is insufficient. |
| GAME-S13 | TRELLIS.2 info hub | image-to-3D 4B signal | T3 | https://trellis-2.org/ | 5 | 2 | 2 | 3 | 4 | Discovery only; verify official Microsoft repo/model before using. |
| GAME-S14 | TRELLIS.2 Text-to-3D demo | wrapper/demo | T2 | https://github.com/PRITHIVSAKTHIUR/TRELLIS.2-Text-to-3D | 4 | 2 | 2 | 3 | 3 | Defer until official weights and download plan are clear. |
| GAME-S15 | TripoSR Stability announcement | image-to-3D model | T1 | https://stability.ai/news/triposr-3d-generation | 5 | 3 | 3 | 4 | 4 | Good first asset model if weights/cache are manageable. |
| GAME-S16 | TripoSR report | method/evaluation | T1 | https://stability.ai/s/TripoSR_report.pdf | 4 | 3 | 5 | 4 | 4 | Use to set speed/quality expectations. |
| GAME-S17 | Hunyuan3D 2.5 paper | high-fidelity 3D assets | T1 | https://arxiv.org/abs/2506.16504 | 5 | 2 | 1 | 5 | 4 | Research target; heavy model likely HomePC Phase 2. |
| GAME-S18 | Hunyuan3D Studio paper | game-ready asset platform | T1 | https://arxiv.org/abs/2509.12815 | 5 | 2 | 2 | 5 | 4 | Use as end-to-end asset workflow reference. |
| GAME-S19 | Points-to-3D paper | controllable 3D generation | T1 | https://arxiv.org/abs/2603.18782 | 4 | 2 | 2 | 4 | 4 | Watch for structure-control workflows. |
| GAME-S20 | Meta 3D AssetGen paper | text-to-mesh/PBR | T1 | https://arxiv.org/abs/2407.02445 | 4 | 1 | 2 | 4 | 4 | Research baseline; not first local path. |
| GAME-S21 | Edify 3D paper | high-quality asset generation | T1 | https://arxiv.org/abs/2411.07135 | 4 | 1 | 2 | 4 | 4 | Research baseline for quality expectations. |
| GAME-S22 | UniTEX paper | 3D texture generation | T1 | https://arxiv.org/abs/2505.23253 | 4 | 2 | 3 | 4 | 4 | Candidate texture pass after mesh generation. |
| GAME-S23 | Ready Player Me docs | rigged avatar pipeline | T1 | https://docs.readyplayer.me/ready-player-me/what-is-ready-player-me | 4 | 2 | 4 | 5 | 4 | Useful hosted avatar shortcut; private/photo use needs approval. |
| GAME-S24 | Ready Player Me integration overview | Unity/Unreal/web avatar import | T1 | https://docs.readyplayer.me/ready-player-me/integration-guides/overview | 4 | 2 | 4 | 5 | 4 | Keep for avatar pipeline matrix. |
| GAME-S25 | Adobe Mixamo rigging docs | automatic humanoid rigging | T1 | https://helpx.adobe.com/creative-cloud/help/mixamo-rigging-animation.html | 4 | 1 | 4 | 5 | 3 | Hosted rigging option; uploads need explicit approval. |
| GAME-S26 | Adobe Mixamo FAQ | rigging limitations | T1 | https://helpx.adobe.com/id_en/creative-cloud/faq/mixamo-faq.html | 4 | 1 | 5 | 5 | 4 | Use to bound biped-only expectations. |
| GAME-S27 | Scenario Unity plugin | AI assets in Unity | T2 | https://github.com/scenario-labs/Scenario-Unity | 3 | 1 | 3 | 4 | 3 | Watch; hosted API/workflow makes it non-first. |
| GAME-S28 | Scenario pricing/features | asset format support | T3 | https://www.scenario.com/pricing | 3 | 1 | 3 | 4 | 3 | Discovery only; verify with product docs before claims. |
| GAME-S29 | Ludo AI Unity plugin | in-editor asset generation | T2/T3 | https://ludo.ai/unity-plugin | 3 | 1 | 3 | 3 | 3 | Watch; not first due hosted/editor dependency. |
| GAME-S30 | OpenGame-Bench concept | evaluation workflow | T1 | https://github.com/leigest519/OpenGame | 5 | 4 | 5 | 5 | 4 | Reuse build health, visual usability, and intent alignment as evaluation axes. |
| GAME-S31 | Godot GLTFDocument docs | runtime GLB/GLTF handling | T2 | https://rokojori.com/en/labs/godot/docs/4.4/gltfdocument-class | 4 | 5 | 5 | 3 | 5 | Use only as supplemental reference; prefer official Godot docs for claims. |
| GAME-S32 | Cube 3D / Roblox model signal | text-to-3D mesh model | T3 | https://huggingface.co/Roblox/cube3d-v0.5 | 4 | 2 | 2 | 4 | 4 | Investigate after official Roblox source confirmation. |
| GAME-S33 | FishWoWater TRELLIS Blender add-on | Blender integration | T2 | https://fishwowater.github.io/projects/trellis_for_blender/ | 3 | 2 | 3 | 3 | 3 | Useful only after TRELLIS local plan exists. |
| GAME-S34 | TripoSR CG Channel report | production-community signal | T3 | https://www.cgchannel.com/2024/03/stability-ai-and-tripo-ai-release-image-to-3d-ai-model-triposr/ | 3 | 3 | 5 | 3 | 4 | Discovery/background only. |
| GAME-S35 | OpenGame secondary report | architecture summary | T3 | https://neurohive.io/en/state-of-the-art/opengame-ai-agent-generates-full-browser-games-from-text-description/ | 4 | 3 | 5 | 3 | 3 | Discovery only; verify against paper/repo. |
| GAME-S36 | Blender as conversion hub | local validation path | T1 | https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html | 5 | 4 | 5 | 5 | 5 | Preferred non-GPU validation step for generated GLB/OBJ/FBX. |

## First-Round Shortlist

| Rank | Candidate | Why | Machine | Preflight |
|---:|---|---|---|---|
| 1 | Godot or Three.js minimal playable loop with generated/procedural assets | Fastest path to prove concept-to-playable without large downloads. | YogaS2 or M9 CLI; M9 GUI only after `gdm3` fix. | Check installed Node/Godot; prefer CLI/web path first. |
| 2 | TripoSR image-to-3D asset | Mature single-image model; likely lighter than Hunyuan3D/TRELLIS. | HomePC. | Check local caches and mirror before any weight download. |
| 3 | TRELLIS/TRELLIS.2 | Higher-quality image/text-to-3D direction. | HomePC only. | Requires explicit model download plan. |
| 4 | OpenGame | Directly matches prompt-to-playable-game interest. | HomePC or YogaS2 depending dependencies/provider needs. | Inspect repo and model/provider assumptions before running. |
| 5 | Mixamo/Ready Player Me | Practical rig/avatar shortcut. | Hosted only after upload/account approval. | Requires privacy decision before using personal photos or assets. |

