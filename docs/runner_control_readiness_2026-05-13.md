# Runner Control Readiness - 2026-05-13

## Verified Commands

Executed from `/Users/yuanshaochen/Projects` and `/Users/yuanshaochen/Projects/local-coding-runners`.

```bash
command -v claude
command -v gemini
gemini --version
/Users/yuanshaochen/Projects/local-coding-runners/bin/claudeminmax --version
/Users/yuanshaochen/Projects/local-coding-runners/bin/claudekimi --version
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker --help
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-capabilities-audit
```

## Current Result

- Claude Code local: `/opt/homebrew/bin/claude`, version `2.1.139`.
- Gemini CLI local: `/opt/homebrew/bin/gemini`, version `0.41.2`.
- Runner wrappers live under `/Users/yuanshaochen/Projects/local-coding-runners/bin`; they are verified by absolute path and are not assumed to be on the default shell `PATH`.
- `claudeminmax`: available, reports Claude Code `2.1.139`.
- `claudekimi`: available, reports Claude Code `2.1.139`.
- `runner-review`: available for read-only MiniMax/Kimi reviews.
- `runner-mcp-review`: available for read-only MiniMax/Kimi reviews that need the project managed MCP tools.
- `runner-gemini-review`: available for read-only Gemini review with `--approval-mode plan`, project MCP allowlist, and default model `gemini-3.1-pro-preview`.
- `runner-worker`: available for scoped write-capable MiniMax/Kimi worker tasks.
- MiniMax credential presence: reported as present without printing the value.
- Kimi credential presence: reported as present without printing the value.
- Managed artifact MCP: connected for MiniMax, Kimi, and Gemini.
- Managed game factory MCP: connected from project-scoped `.mcp.json` / `.gemini/settings.json`.

## Gemini State

`gemini --help` confirms:

- non-interactive `-p/--prompt` mode;
- `--approval-mode plan` for read-only plan mode;
- MCP management;
- skills/extensions/hooks management;
- local Gemma routing command surface.

The current runner audit shows Gemini MCP server:

`managed-artifact-verifier: /usr/bin/python3 /Users/yuanshaochen/Projects/local-coding-runners/bin/managed-artifact-mcp`

connected successfully.

## Delegation Rules

- Use Kimi for stronger implementation/review tasks that need code understanding or judgment.
- Use Gemini CLI with `gemini-3.1-pro-preview` for broad research, planning, architecture, and high-quality review; user has abundant Gemini quota.
- Use MiniMax only for mechanical, narrow, low-complexity tasks where weaker coding/reasoning is acceptable.
- Use `bin/runner-review minimax PROMPT_FILE` only for low-complexity read-only review.
- Use `bin/runner-review kimi PROMPT_FILE` for stronger independent read-only critique.
- Use `bin/runner-mcp-review minimax|kimi PROMPT_FILE` when the reviewer must inspect task packets or repo status through MCP.
- Use `gemini -p "...prompt..." --approval-mode plan` for broad read-only plan/research critique.
- Prefer `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-gemini-review PROMPT_FILE` for repeatable Gemini 3.1 Pro Preview review with timeout and MCP allowlist.
- Use `bin/runner-worker` only after a dry-run, explicit write scope, verification command, and evidence expectations.
- Provider workers must not read or print `.secrets/`, `.kimi/`, `.claude-minimax/`, `.claude-kimi/`.
- Provider workers must not install packages, make large downloads, call extra paid APIs, commit, push, or run destructive git commands unless explicitly authorized.

## MCP Surface

`managed-artifact-verifier` exposes:

- `verify_artifact_hashes`

`managed-game-factory` exposes:

- `repo_status_summary`
- `list_visual_upgrade_tasks`
- `validate_asset_packet`
- `validate_no_proxy_download_record`
- `verify_artifact_hashes`

The game-factory MCP is intentionally offline and read-only. It only accepts the workspace:

`/Users/yuanshaochen/Projects/ai-game-generation-research`

It does not read credentials, install packages, download files, mutate git state, or write repo files.

## Project-Level Agent Config

Added:

- `.mcp.json`
- `.gemini/settings.json`
- `CLAUDE.md`
- `GEMINI.md`
- `.claude/agents/threejs-runtime-worker.md`
- `.claude/agents/asset-packet-reviewer.md`
- `.claude/agents/visual-upgrade-planner.md`

These files make the target repo itself usable by Claude-compatible workers and Gemini, rather than relying only on the runner wrapper directory.

## First Worker Routes To Use

1. `runner-review minimax`: review the implementation plan for missing gates.
2. `runner-review kimi`: critique the lane split and runner discipline.
3. `gemini --approval-mode plan`: broad review of local 3D asset factory route.
4. `runner-worker minimax --dry-run`: dry-run `threejs-loader-migration-001` before any write-capable external call.

## Current Full-Rebuild Routing Addendum

For the PUBG-like full asset factory goal:

- Use Kimi for complex coding, route blocker analysis, and integration critique.
- Use Gemini through `runner-gemini-review` or explicit `gemini --model gemini-3.1-pro-preview`; do not rely on the Gemini default model.
- Use MiniMax only for mechanical reports, hash manifests, and simple schema checks.
- Use HomePC GPU workers for Hunyuan3D, ComfyUI, TRELLIS, Blender render/bake, and PBR generation.
- Use Codex only as controller, merge reviewer, and evidence closer when the work can be delegated.

## Dry-Run Proof

The first write-capable worker prompt was dry-run only and saved to:

`tasks/visual_upgrade/threejs_loader_migration_001.dry_run.txt`

Command shape:

```bash
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker minimax \
  --workspace /Users/yuanshaochen/Projects/ai-game-generation-research \
  --prompt /Users/yuanshaochen/Projects/ai-game-generation-research/tasks/visual_upgrade/threejs_loader_migration_001.md \
  --write-scope 'experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js experiments/tactical_game_visual_upgrade_20260520/reports/threejs_loader_migration_001.md' \
  --verify 'node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js && node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js' \
  --do-not-edit 'experiments/tactical_game_full_realism_final_20260513/source/14.html, private credential directories, global proxy settings, files outside write scope' \
  --evidence 'changed files, commands run, report path, node --check output' \
  --dry-run
```

Result:

- no provider call was made;
- no files were modified by the worker;
- the composed prompt contains workspace, write scope, forbidden paths, verification command, and required return shape.

## First Real Review Outcomes

Prompt packet:

`tasks/visual_upgrade/review_plan_packet_001.md`

Observed outputs:

- `tasks/visual_upgrade/review_plan_packet_001.gemini_review.txt`
- `tasks/visual_upgrade/review_plan_packet_001.kimi_mcp_review.txt`
- `tasks/visual_upgrade/review_plan_packet_001.minimax_review.txt`
- `tasks/visual_upgrade/review_plan_packet_001.minimax_mcp_review.txt`

Result:

- Gemini CLI did use `gemini-3.1-pro-preview`. The run hit repeated `MODEL_CAPACITY_EXHAUSTED` 429s, then returned `VERDICT: APPROVE`. This is usable but capacity-sensitive; keep Gemini for broad/high-value reviews, and record 429s as a scheduling issue rather than a prompt issue.
- Kimi MCP review returned `VERDICT: APPROVE_WITH_FIXES`. It correctly identified sequencing gaps: the new experiment skeleton did not exist yet, asset registry v2 was not defined, and W3 lacked a task packet. This is the strongest completed external review signal.
- MiniMax without MCP permissions could not read the needed project context. MiniMax with MCP timed out after 300 seconds. Treat MiniMax as a low-complexity/mechanical worker only, not as a planner or schema designer.

Follow-up applied:

- Created `experiments/tactical_game_visual_upgrade_20260520/README.md` as the new experiment skeleton entrypoint.
- Created `tasks/visual_upgrade/asset_registry_v2_001.md` so W3 has a bounded worker packet.
- Routed W3 implementation to Kimi, not MiniMax.

## Current Limitations

- Gemini skills are linked for this project, but the first Gemini review also showed `gemini-3.1-pro-preview` can be temporarily capacity-limited.
- MiniMax review reliability is weaker than Kimi/Gemini for context-heavy work.
- No large model download was performed in this readiness check.
