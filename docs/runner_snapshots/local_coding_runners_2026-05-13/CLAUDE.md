# Local Coding Runners

This workspace contains local wrapper scripts and prompt templates for bounded runner use.

## Rules

- Prefer `bin/runner-review` for planning and review tasks.
- `bin/runner-review` sets `RUNNER_READ_ONLY=1`, disables Claude tools, and enforces a process-tree timeout.
- Prefer `bin/runner-worker` for low-risk mechanical implementation tasks with explicit write scope, verification commands, and evidence plan.
- Use provider wrappers directly only when `runner-worker` is too constrained and the task still has an explicit write scope, verification commands, and evidence plan.
- Do not read or print files under `.secrets/`, `.kimi/`, `.claude-minimax/`, or `.claude-kimi/`.
- Do not install packages, make large downloads, or call paid providers unless the prompt explicitly authorizes it.

## Prompt Templates

- `prompts/read_only_code_review.md`
- `prompts/implementation_plan_review.md`
- `prompts/mechanical_worker_task.md`
- `prompts/runner_worker_probe_task.md`

## Write-Capable Worker Dry Run

Inspect the composed worker prompt before allowing a provider call:

```bash
bin/runner-worker minimax \
  --workspace /Users/yuanshaochen/Projects/ai-game-generation-research \
  --prompt prompts/mechanical_worker_task.md \
  --write-scope "owned files/modules only" \
  --verify ".venv/bin/python -m pytest -q targeted_test.py" \
  --dry-run
```

Real worker execution also requires `--i-understand-write-access`.

## Audit

Run:

```bash
bin/runner-capabilities-audit
```

The audit prints tool versions, MCP status, Gemini skill status, and prompt-template paths without printing credential values.
