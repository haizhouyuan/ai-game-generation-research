# Local Coding Runners Setup - 2026-05-13

## What This Directory Is

This directory keeps local runner setup outside `/Users/yuanshaochen/Projects` root and outside the game research repo.

Installed locally:

- Claude Code: `/opt/homebrew/bin/claude`
- Version verified: `2.1.139`

Copied from YogaS2:

- `.secrets/credentials.env`
- `.kimi/config.toml`
- `.kimi/kimi-code.json`
- `.claude-minimax/.claude.json`
- `.claude-kimi/.claude.json`

These files are private and ignored by git.

## Commands

```bash
bin/runner-env-check
bin/runner-capabilities-audit
bin/claudeminmax --version
bin/claudekimi --version
bin/runner-review --help
bin/runner-worker --help
```

For one-shot non-interactive tasks:

```bash
bin/claudeminmax --print --output-format text --tools "" "Reply with RUNNER_OK only."
bin/claudekimi --print --output-format text --tools "" "Reply with RUNNER_OK only."
```

For bounded read-only review tasks:

```bash
RUNNER_TIMEOUT_SECONDS=600 bin/runner-review minimax prompts/read_only_code_review.md
RUNNER_TIMEOUT_SECONDS=600 bin/runner-review kimi prompts/implementation_plan_review.md
```

## Routing

- Use `bin/claudeminmax` for low-cost mechanical work and reviews. Concurrency defaults to 1 and is clamped to 2.
- Use `bin/claudekimi` for Kimi-backed Claude Code compatibility.
- Use `bin/runner-review` first for read-only review/planning tasks. It disables tools, sets `RUNNER_READ_ONLY=1` so provider wrappers do not enable `bypassPermissions`, and enforces a process-tree watchdog timeout.
- Use `bin/runner-worker` for low-risk mechanical implementation tasks after defining a workspace, write scope, verification command, and evidence plan. Start with `--dry-run` to inspect the composed worker prompt before allowing provider execution.
- Use `prompts/mechanical_worker_task.md` as the task body for `runner-worker` when a task has an explicit write scope and verification plan.
- Use `bin/runner-capabilities-audit` to verify MCP/skill state without printing credential values.
- Keep secrets in `.secrets` and provider-specific private config directories.
- Do not commit `.secrets`, `.kimi`, `.claude-minimax`, or `.claude-kimi`.

Dry-run write-capable worker shape:

```bash
bin/runner-worker minimax \
  --workspace /Users/yuanshaochen/Projects/ai-game-generation-research \
  --prompt prompts/mechanical_worker_task.md \
  --write-scope "owned files/modules only" \
  --verify ".venv/bin/python -m pytest -q targeted_test.py" \
  --dry-run
```

Real worker execution also requires `--i-understand-write-access`.

The first real write-capable probe used `prompts/runner_worker_probe_task.md` to create exactly one evidence file in the research repo and run a marker verification command.
