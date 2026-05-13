---
name: local-3d-asset-factory-orchestrator
description: Use when orchestrating local-first AI 3D game asset production, tactical-game visual upgrades, HomePC GPU jobs, Mac MLX/llama.cpp fallback workers, Claude/Kimi/MiniMax/Gemini runner delegation, no-proxy large downloads, PBR asset packets, and evidence-gated Three.js/Blender workflows.
---

# Local 3D Asset Factory Orchestrator

## Role

Act as a scoped worker or reviewer inside Codex's orchestration system.

- Codex owns final coordination, merge decisions, and evidence closeout.
- Use MCP tools when available instead of broad manual scans.
- Stay inside assigned read/write scope.
- Never read credentials or private runner config directories.

## Network Rule

Downloads are allowed only when explicitly authorized.

- Over 100MB: command-local no-proxy evidence is required.
- Over 1GB: explicit user approval is required before download.
- Never change global proxy settings.

No-proxy template:

```bash
env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl --noproxy '*' -L --fail --continue-at - --output OUTPUT URL
```

## Asset Acceptance

Production candidates need an asset packet:

- GLB model;
- BaseColor, Normal, Roughness, Metallic, AO where applicable;
- Blender/material/gltf reports;
- in-game screenshot;
- hash record;
- provenance/license note.

Hero assets should reach `material_map_count >= 4`, or return a concrete blocker and fallback route.

## Runner Routing

- MiniMax: low-cost mechanical edits and first-pass review.
- Kimi: independent critique and scoped implementation.
- Gemini: broad planning/research critique.
- HomePC GPU: Trellis2, Hunyuan3D, ComfyUI, Blender render/bake.
- Mac local MLX/llama.cpp: lightweight local summarization/classification fallback.

## Default Visual Direction

Prefer a small, dense rainy checkpoint / container-yard / killhouse-entry micro-slice over broad map expansion.

Required evidence cameras:

- `01_fp_rifle_wet_checkpoint`
- `02_third_person_player_gear`
- `03_enemy_under_checkpoint_light`
- `04_loot_on_wet_asphalt`
- `05_indoor_killhouse_corridor`
- `06_final_wide_rainy_container_checkpoint`

