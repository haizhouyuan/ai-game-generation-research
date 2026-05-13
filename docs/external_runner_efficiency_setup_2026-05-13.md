# External Runner Efficiency Setup - 2026-05-13

## Purpose

Use cheaper or already-paid coding runners for bounded work, while this Codex thread stays the orchestrator.

The local strategy is:

- Codex: orchestration, final judgment, repo edits that need tight integration, and evidence closeout.
- Gemini CLI: local read-only audits, simple implementation reviews, and mechanical file-level tasks.
- Local Claude/Kimi/MiniMax wrappers: already-paid runners for planning, review, and low-risk worker turns.
- Codex subagents: scoped implementation and review loops when direct repo edits are needed.

## Captured Source

The ChatGPT reference thread was opened in authenticated Chrome and copied to:

- `docs/source_snapshots/chatgpt_codex_app_dual_agent_clipboard_2026-05-13.txt`

Important extracted direction:

- Prefer Symphony alignment instead of growing a separate full controller.
- Treat commercial or official managed-agent platforms as possible upper layers.
- Keep local self-built code thin: repository/task conventions, runner routing, prompts/profiles, forbidden-task rules, and high-risk approval.
- Use Kimi/MiniMax/Claude/Codex runners for ordinary tasks when the task does not require the strongest model.

## Local Gemini CLI

Verified:

```bash
gemini -p 'Reply with exactly: GEMINI_OK' --output-format text --skip-trust
```

Result: `GEMINI_OK`.

Gemini skills linked locally:

- `subagent-driven-development`
- `test-driven-development`
- `systematic-debugging`
- `verification-before-completion`
- `using-git-worktrees`
- `requesting-code-review`

Gemini currently has no MCP servers configured. This is acceptable for the first runner phase because Gemini CLI already has local shell/file tooling. Add project MCP only when a task needs a specific external system, because every additional MCP server increases context/tool surface.

## Local Runner Install

The active local runner workspace is:

- `/Users/yuanshaochen/Projects/local-coding-runners`

Installed locally:

- Claude Code: `/opt/homebrew/bin/claude`
- Claude Code version: `2.1.139`

Local runner commands:

- `/Users/yuanshaochen/Projects/local-coding-runners/bin/claudeminmax`
- `/Users/yuanshaochen/Projects/local-coding-runners/bin/claudekimi`
- `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-env-check`
- `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-review`
- `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker`
- `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-capabilities-audit`

Prompt templates:

- `/Users/yuanshaochen/Projects/local-coding-runners/prompts/read_only_code_review.md`
- `/Users/yuanshaochen/Projects/local-coding-runners/prompts/implementation_plan_review.md`
- `/Users/yuanshaochen/Projects/local-coding-runners/prompts/mechanical_worker_task.md`
- `/Users/yuanshaochen/Projects/local-coding-runners/prompts/runner_worker_probe_task.md`

Portable non-secret snapshot:

- `docs/runner_snapshots/local_coding_runners_2026-05-13/`

Private local credentials/config copied from YogaS2:

- `/Users/yuanshaochen/Projects/local-coding-runners/.secrets/credentials.env`
- `/Users/yuanshaochen/Projects/local-coding-runners/.kimi/config.toml`
- `/Users/yuanshaochen/Projects/local-coding-runners/.kimi/kimi-code.json`
- `/Users/yuanshaochen/Projects/local-coding-runners/.claude-minimax/.claude.json`
- `/Users/yuanshaochen/Projects/local-coding-runners/.claude-kimi/.claude.json`

Those private files are ignored by the local runner `.gitignore` and are not recorded in this repo.

Verification:

```bash
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-env-check
/Users/yuanshaochen/Projects/local-coding-runners/bin/claudeminmax --version
/Users/yuanshaochen/Projects/local-coding-runners/bin/claudekimi --version
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-review --help
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker --help
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker minimax --workspace /Users/yuanshaochen/Projects/ai-game-generation-research --prompt /Users/yuanshaochen/Projects/local-coding-runners/prompts/mechanical_worker_task.md --write-scope 'owned files/modules only' --verify '.venv/bin/python -m pytest -q targeted_test.py' --dry-run
RUNNER_TIMEOUT_SECONDS=180 /Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker minimax --workspace /Users/yuanshaochen/Projects/ai-game-generation-research --prompt /Users/yuanshaochen/Projects/local-coding-runners/prompts/runner_worker_probe_task.md --write-scope 'experiments/runner_worker_probe_20260513/worker_probe_result.md' --verify 'test -f experiments/runner_worker_probe_20260513/worker_probe_result.md && rg -n "RUNNER_WORKER_PROBE_OK|provider: minimax|write_scope:" experiments/runner_worker_probe_20260513/worker_probe_result.md' --i-understand-write-access
```

Observed result: Claude Code `2.1.139`; MiniMax and Kimi credential variables present; `runner-worker --help` passes; `runner-worker --dry-run` emits a bounded write-capable worker prompt without calling a provider. A real low-risk MiniMax-backed worker probe also completed with exit code `0`, wrote only `experiments/runner_worker_probe_20260513/worker_probe_result.md`, and passed the marker verification command. Future model-call smoke should still use explicit budget and timeout because provider calls may wait or consume paid quota.

MCP/skill inventory:

- Gemini skills are enabled for `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, and `verification-before-completion`.
- Gemini MCP: no servers configured.
- Claude MiniMax MCP: no servers configured after removing copied YogaS2-only entries that failed locally.
- Claude Kimi MCP: no servers configured.
- Runner commands: `runner-worker=executable` in `runner-capabilities-audit`.
- Evidence snapshot: `docs/runner_snapshots/local_coding_runners_2026-05-13/runner_mcp_skill_inventory_2026-05-13.md`
- Real worker probe: `experiments/runner_worker_probe_20260513/runner_worker_probe_report.md`

## YogaS2 Source References

YogaS2 is reachable through the `yoga` SSH alias. The `yoga-lan` LAN alias timed out during banner exchange, but Tailscale shows `yogas2` active.

Remote commands inspected as source references:

- `/home/yuanhaizhou/.nvm/versions/node/v22.22.0/bin/claude`
- `/home/yuanhaizhou/.local/bin/claudeminmax`
- `/home/yuanhaizhou/.local/bin/claudekimi`
- `/home/yuanhaizhou/.local/bin/kimicode`
- `/home/yuanhaizhou/.nvm/versions/node/v22.22.0/bin/gemini`

No YogaS2 credential snapshot is retained as required evidence in this repo. The production local wrapper copy lives in `/Users/yuanshaochen/Projects/local-coding-runners`, with private credentials ignored by that separate repository. This repo records a non-secret wrapper/template snapshot under `docs/runner_snapshots/local_coding_runners_2026-05-13/`, so `check-capabilities` stays portable across fresh checkouts.

Example one-shot read-only review:

```bash
RUNNER_TIMEOUT_SECONDS=600 /Users/yuanshaochen/Projects/local-coding-runners/bin/runner-review minimax /Users/yuanshaochen/Projects/local-coding-runners/prompts/read_only_code_review.md
```

## Routing Rules

- Use Gemini first for local no-secret read-only work and mechanical reviews.
- Use `runner-review` first for read-only MiniMax/Kimi planning and review work. It disables tools, avoids provider-wrapper `bypassPermissions`, and adds a process-tree watchdog timeout.
- Use `runner-worker` for low-risk mechanical implementation tasks only after a dry run confirms the composed prompt has an explicit workspace, write scope, verification command, and evidence plan. Real execution additionally requires `--i-understand-write-access`.
- Use local Claude Code wrappers directly only when `runner-worker` is too constrained and the task still has an explicit write scope, verification commands, and evidence plan. They read local private credentials from `/Users/yuanshaochen/Projects/local-coding-runners/.secrets/credentials.env`.
- Treat MCP as not configured until a concrete local MCP surface is available and passes `runner-capabilities-audit`.
- Use `claudeminmax` with concurrency 1 by default. The remote policy allows explicit concurrency 2, but anything above 2 is clamped.
- Use `claudekimi` for Claude Code-compatible Kimi work; use native Kimi only when a local Kimi CLI is installed and configured here.
- Keep large downloads under the no-proxy governance policy; any external single file over 100M must not use proxy traffic.

## Next Setup Steps

- Use `runner-worker` only for low-risk scoped tasks until repeated nontrivial probes are reviewed.
- If a concrete MCP surface becomes necessary, configure it through project/user scope following Claude Code or Gemini docs; do not commit secrets and verify it with `runner-capabilities-audit`.
- If Kimi CLI is installed locally later, prefer native Kimi provider configuration over pretending it is Claude.
- Promote the runner pool into capability registry as `external-coding-runner-pool`.
