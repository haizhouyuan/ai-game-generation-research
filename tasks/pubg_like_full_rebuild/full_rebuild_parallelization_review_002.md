# Runner Review Task: Full Rebuild Parallelization 002

## Context

Repo: `/Users/yuanshaochen/Projects/ai-game-generation-research`

Active goal:

`docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`

Task board:

`tasks/pubg_like_full_rebuild/README.md`

The owner clarified that the goal is not a light visual upgrade. The target is a full local AI 3D asset factory and a PUBG-like tactical game rebuild:

- realistic reference images;
- local image-to-3D / Hunyuan3D / ComfyUI / TRELLIS route tests;
- PBR texture maps;
- Blender cleanup;
- Three.js runtime integration;
- evidence gates;
- no paid proxy traffic for large downloads.

## Ask

Give a read-only execution critique:

1. Identify the highest-value parallel tasks that can run immediately without blocking Hunyuan Paint.
2. Point out missing acceptance gates that would let a weak partial upgrade be mistaken for completion.
3. Propose which tasks should go to Kimi, Gemini, MiniMax, HomePC GPU, or Codex.
4. Keep the answer concrete and action-oriented; do not rewrite the whole plan.

## Constraints

- Do not edit files.
- Assume Gemini must use `gemini-3.1-pro-preview`.
- Assume Kimi is stronger than MiniMax for complex coding/reasoning.
- MiniMax should only get mechanical/report/schema/hash work.
- Large downloads are allowed only with command-local no-proxy evidence.
