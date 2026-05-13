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
| W3 first generated asset | HomePC GPU | active | `experiments/pubg_like_asset_factory_20260513/assets/hunyuan_shape_demo_001/` |
| W4 hero rifle full replacement | HomePC GPU + Blender | pending | generated/PBR hero rifle packet |
| W5 character/gear replacement | HomePC GPU + Blender | pending | production character packets |
| W6 environment/loot/clutter | HomePC GPU + Blender | pending | material and prop packets |
| W7 ComfyUI PBR route | HomePC GPU | pending | workflow JSON and output asset |
| W8 runtime gate v3 | Codex/Kimi | pending | v3 registry and visual evidence gate |
| W9 final release | Codex | pending | new dated release packet |

## Immediate Commands

1. Preflight HomePC GPU/disk and running processes. Done.
2. Clone/install Hunyuan3D-2.1 under HomePC without proxy traffic. Done.
3. Download model files with proxy env unset and record evidence. Done.
4. Run a small shape-only smoke test. Done.
5. Run a small textured/PBR smoke test. Active.

## Current W1/W3 Evidence

- Hunyuan3D-2.1 model snapshot downloaded to HomePC with command-local proxy env unset and `HF_ENDPOINT=https://hf-mirror.com`.
- Shape-only generation succeeded on HomePC GPU1.
- First shape asset packet is in `experiments/pubg_like_asset_factory_20260513/assets/hunyuan_shape_demo_001/`.
- Hash manifest verifies: `python3 tools/verify_artifact_hashes.py experiments/pubg_like_asset_factory_20260513/artifact_hashes.json`.

Important: `hunyuan_shape_demo_001` is not a final game asset. It proves the local Hunyuan shape route only; `material_map_count = 0`.

## Current Texture/PBR Blockers

- Existing `hy3d21` env is Python 3.10; `bpy==4.0` is not installable there on Linux.
- Hunyuan paint imports currently fail because `bpy` is missing.
- `custom_rasterizer` imports successfully in `hy3d21`.
- `realesrgan` and `basicsr` are missing.
- Existing `hy3dpaint/ckpt/RealESRGAN_x4plus.pth` was a partial 1.8MB file and must be replaced.

Active mitigation:

- create a separate `hy3d21paint` Python 3.11 env for Hunyuan Paint instead of disturbing the working shape env;
- download RealESRGAN with proxy env unset and size/hash validation;
- compile or validate Hunyuan paint extensions after `bpy`, `realesrgan`, and `basicsr` imports pass.

## External Runner Reviews

`hunyuan_paint_env_review_001` was sent to Gemini and Kimi as read-only runner reviews.

Gemini result is saved at:

`tasks/pubg_like_full_rebuild/hunyuan_paint_env_review_001.gemini_review.txt`

Key Gemini guidance:

- Python 3.11 plus `bpy==4.2.0` is a reasonable practical substitute because current Linux/Python 3.11 PyPI index does not offer `bpy==4.0`.
- `basicsr==1.4.2` may fail with modern `torchvision` because `torchvision.transforms.functional_tensor` was removed; patch to `torchvision.transforms.functional` if import fails.
- Do not let RealESRGAN super-resolution block the core paint validation; first try to get texture generation running, then solve upscaling.
