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
- `claudeminmax`: available, reports Claude Code `2.1.139`.
- `claudekimi`: available, reports Claude Code `2.1.139`.
- `runner-review`: available for read-only MiniMax/Kimi reviews.
- `runner-gemini-review`: available for read-only Gemini review with `--approval-mode plan` and project MCP allowlist.
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

- Use `bin/runner-review minimax PROMPT_FILE` for low-cost read-only plan/review.
- Use `bin/runner-review kimi PROMPT_FILE` for independent read-only critique.
- Use `gemini -p "...prompt..." --approval-mode plan` for broad read-only plan/research critique.
- Prefer `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-gemini-review PROMPT_FILE` for repeatable Gemini review with timeout and MCP allowlist.
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

## Current Limitations

- Gemini reports no discovered skills in this runner audit. It still has MCP and headless plan mode.
- External provider workers are configured, but should stay on low-risk narrow tasks until the first visual-upgrade worker dry-runs are reviewed.
- No large model download was performed in this readiness check.
