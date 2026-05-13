# Local AI 3D Asset Factory And Tactical Visual Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first AI 3D asset production line and use it to upgrade the tactical HTML/Three.js game into a high-quality rainy-checkpoint visual slice.

**Architecture:** Codex is the orchestrator and evidence owner. Heavy asset generation runs on HomePC/GPU lanes; narrow coding/review work is delegated to MiniMax/Kimi/Gemini runners; the Mac M2 Max 96GB handles repo integration, browser evidence, and light local MLX/llama.cpp fallback inference.

**Tech Stack:** Three.js, GLTFLoader, KTX2/Meshopt readiness, Blender, ComfyUI/Trellis2, Hunyuan3D, StableGen, TextureAlchemy/CHORD/PBRFusion candidates, CDP evidence scripts, local runner wrappers.

---

## Sources Used

- User-provided ChatGPT Pro answer in this thread.
- `docs/chatgpt_pro_github_review_brief_2026-05-13.md`
- `experiments/tactical_game_full_realism_final_20260513/README.md`
- `experiments/tactical_game_full_realism_final_20260513/report.md`
- `docs/full_realism_lessons_and_best_practices_2026-05-13.md`
- MLX-LM official repo: <https://github.com/ml-explore/mlx-lm>
- llama.cpp official repo: <https://github.com/ggml-org/llama.cpp>
- LM Studio docs: <https://lmstudio.ai/docs/app>

## File Structure

- Create: `docs/production_goal_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`
  - User-facing `/goal` source of truth.
- Create: `docs/implementation_plan_local_ai_3d_asset_factory_tactical_visual_upgrade_2026-05-13.md`
  - Implementation plan and worker task order.
- Create: `docs/runner_control_readiness_2026-05-13.md`
  - Runner/Gemini/Claude wrapper readiness evidence.
- Create: `docs/mac_local_model_lane_2026-05-13.md`
  - MLX/llama.cpp/Ollama/LM Studio decision and commands.
- Create: `config/lanes_visual_upgrade_2026-05-13.yaml`
  - Lane ownership and concurrency policy.
- Create: `tasks/visual_upgrade/README.md`
  - Task-board conventions and worker prompt template.
- Create: `tasks/visual_upgrade/*.md`
  - Initial task specs for runner/control work.
- Create: `experiments/tactical_game_visual_upgrade_20260520/`
  - New experiment target, not destructive edits to the current final packet.
- Create later: `experiments/tactical_game_visual_upgrade_20260520/src/runtime/*.js`
  - Loader, registry, animation, decals, lighting, evidence modules.
- Create later: `experiments/tactical_game_visual_upgrade_20260520/assets/**`
  - Asset packets and PBR maps.

## Phase 0: Control Plane Setup

### Task 0.1: Runner Readiness Report

**Files:**
- Create: `docs/runner_control_readiness_2026-05-13.md`

- [ ] **Step 1: Run local runner audit**

Run:

```bash
cd /Users/yuanshaochen/Projects/local-coding-runners
bin/runner-capabilities-audit
```

Expected:

- `claude` version present;
- `gemini` version present;
- `MINIMAX_API_KEY=present`;
- `KIMI_CODINGPLAN_API_KEY=present`;
- MiniMax/Kimi/Gemini MCP can connect to `managed-artifact-verifier`;
- no credential values printed.

- [ ] **Step 2: Record readiness**

Create `docs/runner_control_readiness_2026-05-13.md` with:

```markdown
# Runner Control Readiness - 2026-05-13

## Verified Commands

- `/opt/homebrew/bin/claude --version`
- `/opt/homebrew/bin/gemini --version`
- `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-capabilities-audit`
- `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker --help`

## Current Result

- Claude Code local: available.
- Gemini CLI local: available.
- `claudeminmax`: available.
- `claudekimi`: available.
- `runner-review`: available for read-only reviews.
- `runner-worker`: available for scoped write-capable worker tasks.
- Managed artifact MCP: connected for MiniMax, Kimi, and Gemini.

## Rules

- Use `runner-review` for read-only review.
- Use `runner-worker` only with explicit write scope and verification.
- Do not let provider workers read `.secrets`, `.kimi`, `.claude-minimax`, or `.claude-kimi`.
- No large downloads or package installs inside provider workers unless explicitly authorized.
```

- [ ] **Step 3: Verify doc exists**

Run:

```bash
test -f docs/runner_control_readiness_2026-05-13.md
```

Expected: exit code `0`.

### Task 0.2: Create Visual Upgrade Task Board

**Files:**
- Create: `tasks/visual_upgrade/README.md`
- Create: `tasks/visual_upgrade/threejs_loader_migration_001.md`
- Create: `tasks/visual_upgrade/hero_rifle_v2_001.md`
- Create: `tasks/visual_upgrade/rainy_checkpoint_scene_001.md`

- [ ] **Step 1: Create task-board README**

Use this content:

```markdown
# Visual Upgrade Task Board

Each task file is a bounded worker packet. Workers may only edit the declared write scope.

## Required Fields

- Task id
- Goal
- Host
- Runner route
- Read scope
- Write scope
- Forbidden paths
- Verification command
- Expected artifacts
- Acceptance gate
- Output summary format

## Safety

- Do not read secrets.
- Do not run package installs unless explicitly authorized.
- Do not download files over 100MB without no-proxy command-local evidence.
- Do not download files over 1GB without explicit user approval.
- Do not modify global proxy settings.
```

- [ ] **Step 2: Add initial task files**

Each task should use this template:

```markdown
# Task: TASK_ID

## Goal

One sentence.

## Host

Mac or HomePC.

## Runner Route

Codex / claudeminmax / claudekimi / gemini / homepc-gpu-worker.

## Read Scope

- `path`

## Write Scope

- `path`

## Forbidden

- `.secrets`
- `.kimi`
- `.claude-minimax`
- `.claude-kimi`
- global proxy configuration
- destructive git commands

## Verification

```bash
command here
```

## Expected Artifacts

- `path`

## Acceptance

- Concrete pass/fail conditions.

## Output Summary

- changed files
- commands run
- evidence paths
- risks
```

- [ ] **Step 3: Verify task files**

Run:

```bash
test -f tasks/visual_upgrade/README.md
test -f tasks/visual_upgrade/threejs_loader_migration_001.md
test -f tasks/visual_upgrade/hero_rifle_v2_001.md
test -f tasks/visual_upgrade/rainy_checkpoint_scene_001.md
```

Expected: all exit code `0`.

## Phase 1: Local Model And GPU Route Selection

### Task 1.1: Mac Local Model Lane

**Files:**
- Create: `docs/mac_local_model_lane_2026-05-13.md`

- [ ] **Step 1: Choose first local route**

Decision:

- Use `mlx-lm` first for Mac-native lightweight summarization/classification because MLX is Apple Silicon native and `mlx-lm` supports prompt caching and Hugging Face model loading.
- Keep `llama.cpp` as the compatibility/API fallback because it supports Metal and `llama-server`.
- Use LM Studio/Ollama only as convenience wrappers, not as the core automation dependency.

- [ ] **Step 2: Do not download a large model yet**

Document:

```markdown
No model over 100MB should be downloaded until the no-proxy command and target model are recorded.
No model over 1GB should be downloaded without explicit approval.
```

- [ ] **Step 3: Add benchmark plan**

Benchmark tasks:

- tiny local prompt classification;
- task packet summarization;
- screenshot-project OCR text cleanup if OCR text is provided;
- compare latency and output quality against Gemini/MiniMax/Kimi.

### Task 1.2: HomePC GPU Job Contract

**Files:**
- Create: `tasks/visual_upgrade/homepc_gpu_job_contract.md`

- [ ] **Step 1: Create YAML job format**

Use:

```yaml
task_id: asset-hero-rifle-hunyuan-001
owner: homepc-gpu-worker
gpu: 0
download_policy:
  over_100mb_no_proxy_required: true
  over_1gb_user_approval_required: true
input:
  reference_images: []
  source_meshes: []
output:
  expected:
    - outputs/hero_rifle_candidate.glb
    - outputs/hero_rifle_preview.png
    - outputs/material_report.json
acceptance:
  - glb_exists
  - preview_exists
  - material_maps_or_failure_reason
  - no_missing_texture
```

## Phase 2: Runtime Foundation

### Task 2.1: Create New Experiment Skeleton

**Files:**
- Create: `experiments/tactical_game_visual_upgrade_20260520/README.md`
- Copy/reference: current final packet without modifying it.

- [ ] **Step 1: Create experiment README**

Include:

- source final packet path;
- target rainy checkpoint slice;
- six camera names;
- evidence commands;
- explicit note that the current final packet remains preserved.

- [ ] **Step 2: Verify original final packet remains untouched**

Run:

```bash
git diff -- experiments/tactical_game_full_realism_final_20260513
```

Expected: no diff unless intentionally updating documentation only.

### Task 2.2: GLTFLoader Migration Plan

**Files:**
- Create: `tasks/visual_upgrade/threejs_loader_migration_001.md`
- Later create: `experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js`
- Later create: `experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js`

- [ ] **Step 1: Worker dry-run**

Run:

```bash
cd /Users/yuanshaochen/Projects/local-coding-runners
bin/runner-worker minimax \
  --workspace /Users/yuanshaochen/Projects/ai-game-generation-research \
  --prompt /Users/yuanshaochen/Projects/ai-game-generation-research/tasks/visual_upgrade/threejs_loader_migration_001.md \
  --write-scope "experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js" \
  --verify "node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js && node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js" \
  --dry-run
```

Expected:

- composed prompt shows exact write scope;
- no provider call;
- no files modified.

## Phase 3: Asset Production Benchmark

### Task 3.1: Four Benchmark Assets

**Files:**
- Create: `docs/asset_production_benchmark_matrix_2026-05-13.md`

Benchmark:

1. Hero rifle.
2. Tactical gear/character piece.
3. Wet asphalt / concrete / container material.
4. Loot or medkit prop.

Routes:

1. StableGen/Blender-first retexture.
2. Trellis2/ComfyUI/Texture Projection.
3. Hunyuan3D 2.1 Shape/Paint or equivalent PBR route.

Metrics:

- setup friction;
- model/download size;
- no-proxy compliance;
- VRAM/RAM;
- wall-clock time;
- output maps;
- Blender repair time;
- Three.js screenshot quality;
- license/provenance risk.

## Phase 4: Game Visual Slice

### Task 4.1: Six Camera Scene Contract

**Files:**
- Create: `docs/rainy_checkpoint_visual_target_2026-05-13.md`

Camera list:

- `01_fp_rifle_wet_checkpoint`
- `02_third_person_player_gear`
- `03_enemy_under_checkpoint_light`
- `04_loot_on_wet_asphalt`
- `05_indoor_killhouse_corridor`
- `06_final_wide_rainy_container_checkpoint`

Acceptance:

- each screenshot has foreground/midground/background;
- no large pure-color surfaces;
- hero rifle visible in first camera;
- character and gear visible in second and third;
- wet material and clutter visible in fourth and sixth;
- indoor lighting visible in fifth.

### Task 4.2: Visual Evidence Gate

**Files:**
- Later create: `experiments/tactical_game_visual_upgrade_20260520/tools/visual_evidence_gate.mjs`

Gate must check:

- blocking browser errors;
- missing network resources;
- screenshot nonblank stats;
- texture map presence for hero assets;
- animation state;
- fallback state;
- six target camera outputs;
- artifact hash manifest.

## Phase 5: Release

### Task 5.1: Final Packet

**Files:**
- Create: `experiments/tactical_game_visual_upgrade_20260520/visual_upgrade_report.md`
- Create: `experiments/tactical_game_visual_upgrade_20260520/artifact_hashes.json`

Acceptance:

- playable local HTML exists;
- runner review summaries exist;
- six screenshots exist;
- asset packets exist;
- hash verification passes;
- final Chinese summary says what changed, what passed, and what remains.

## Verification Before Completion

Before claiming completion, run:

```bash
git status --short
python3 tools/verify_artifact_hashes.py experiments/tactical_game_visual_upgrade_20260520/artifact_hashes.json
node experiments/tactical_game_visual_upgrade_20260520/tools/visual_evidence_gate.mjs
```

Expected:

- no unrelated dirty files;
- hash verification passes;
- visual gate passes with no blocking events.

