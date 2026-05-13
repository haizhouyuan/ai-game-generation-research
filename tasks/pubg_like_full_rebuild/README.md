# PUBG-Like Full AI 3D Asset Pipeline Task Board - 2026-05-13

Goal:

`docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`

## Active Meaning

The previous `tactical_game_visual_upgrade_20260520` release is now the baseline/proof-of-control packet, not final completion. This board tracks the stricter full rebuild: realistic references, local image-to-3D/PBR generation, Blender cleanup, runtime replacement, and evidence gates for all major visible asset classes.

## Runner Routing

- Codex: orchestration, task packets, integration, evidence, final judgement.
- Kimi: complex code/review/blocker analysis.
- Gemini CLI: broad tool/visual review, must use `gemini-3.1-pro-preview`.
- MiniMax: narrow mechanical tasks only.
- HomePC GPU1: Hunyuan3D, ComfyUI, TRELLIS, Blender render/bake.

## Current Parallel Lanes

| Lane | Owner | Status | Output |
| --- | --- | --- | --- |
| W0 stricter goal | Codex | active | `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md` |
| W1 Hunyuan install | HomePC GPU / Codex | active | `experiments/pubg_like_asset_factory_20260513/reports/hunyuan3d_env_report.md` |
| W2 reference images | Codex + image generation route | pending | `experiments/pubg_like_asset_factory_20260513/references/` |
| W3 first generated asset | HomePC GPU | pending | first Hunyuan asset packet |
| W4 hero rifle full replacement | HomePC GPU + Blender | pending | generated/PBR hero rifle packet |
| W5 character/gear replacement | HomePC GPU + Blender | pending | production character packets |
| W6 environment/loot/clutter | HomePC GPU + Blender | pending | material and prop packets |
| W7 ComfyUI PBR route | HomePC GPU | pending | workflow JSON and output asset |
| W8 runtime gate v3 | Codex/Kimi | pending | v3 registry and visual evidence gate |
| W9 final release | Codex | pending | new dated release packet |

## Immediate Commands

1. Preflight HomePC GPU/disk and running processes.
2. Clone/install Hunyuan3D-2.1 under HomePC without proxy traffic.
3. Download model files with proxy env unset and record evidence.
4. Run a small shape-only smoke test.
5. Run a small textured/PBR smoke test.
