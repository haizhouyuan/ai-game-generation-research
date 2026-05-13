# Prompt To Send To ChatGPT Pro - 2026-05-13

请连接并检查这个 GitHub 仓库：

https://github.com/haizhouyuan/ai-game-generation-research

请先读这些入口文件：

1. `README.md`
2. `docs/chatgpt_pro_github_review_brief_2026-05-13.md`
3. `docs/chatgpt_pro_full_asset_factory_followup_2026-05-13.md`
4. `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
5. `tasks/pubg_like_full_rebuild/README.md`
6. `experiments/pubg_like_asset_factory_20260513/reports/hunyuan3d_env_report.md`
7. `docs/coding_runner_mcp_skill_control_2026-05-13.md`
8. `docs/asset_packet_validation_2026-05-13.md`
9. `docs/asset_registry_v3_gate_2026-05-13.md`
10. `docs/texture_quality_gate_2026-05-13.md`

背景：

这个仓库已经有一个 browser-playable Three.js tactical-game baseline，但现在目标不是小修小补，而是建设一个本地 AI 3D 游戏资产生产工厂，把游戏升级到接近 PUBG/现代战术游戏的真实感。旧的 procedural/GLB packet 只能当 baseline，不能算完成。

请重点分析：

1. 当前游戏视觉和资产工厂真实进度是什么，哪些只是 probe/scaffold，哪些是真正跑通的链路。
2. 每类资产应该怎么生产：hero rifle、sidearm、secondary weapon、player/enemy character、gear、wet asphalt、concrete wall、container/checkpoint、loot、clutter/decals、rainy checkpoint scene。
3. 请调研并推荐当前更成熟的本地或混合工具/工作流，包括 Hunyuan3D 2.1/2.x、TRELLIS/TRELLIS.2、ComfyUI Texture Projection/3D Pack、TextureAlchemy、CHORD/PBRFusion/MaterialAnything 或同类 PBR 工具、StableGen/Blender-first、Modly、Step1X-3D、TripoSR/TripoSG、Blender cleanup/retopo/LOD/collision/glTF validation。
4. 现在 Hunyuan Paint 卡在 `facebook/dinov2-giant/model.safetensors` 最后约 520MB 无代理下载超时。不能用付费代理下载大文件。请找更合适的无代理下载/镜像/替代路线，或给出 Hunyuan Paint 卡住时可用的替代 PBR/material pipeline。
5. Three.js runtime 要怎么升级才能接真实资产：GLTFLoader、KTX2、Meshopt、DRACO、AnimationMixer、decals/instancing/postprocessing/evidence cameras/fail-closed registry。
6. 作为游戏开发工厂，Codex/Kimi/Gemini CLI/MiniMax/HomePC GPU/Mac M2 Max 应该如何分工并行。Gemini CLI 必须用 `gemini-3.1-pro-preview`；Kimi 适合复杂代码和 blocker 分析；MiniMax 只适合机械任务。
7. 给一个 7-14 天执行计划，包含可并行任务、产物、验收标准、不要浪费时间的清单。

请不要只给方向性建议。需要：

- blunt current-state assessment；
- ranked tool/workflow recommendations with links；
- per-asset pipeline table；
- DINOv2/Hunyuan blocker resolution options；
- Three.js runtime upgrade checklist；
- agent/work routing plan；
- 7-14 day execution plan；
- top risks and non-completion traps。
