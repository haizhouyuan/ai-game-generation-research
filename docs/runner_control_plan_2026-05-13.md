# Runner Control Plan - 2026-05-13

## Goal

Use Codex as the orchestrator and make Kimi, Gemini CLI, MiniMax, Claude Code, and HomePC GPU workers do bounded work without swallowing the whole project context.

This plan follows the user's routing preference:

- Kimi is strong and should handle complex coding and repo reasoning.
- Gemini CLI is strong and should handle research/review, but must use `gemini-3.1-pro-preview`.
- MiniMax is weaker and should only receive narrow mechanical tasks.
- Claude Code remains the official Claude-compatible baseline and MCP-heavy shell.

## Current Local State

Verified on this Mac:

```text
/opt/homebrew/bin/claude
/opt/homebrew/bin/gemini
/Users/yuanshaochen/Projects/local-coding-runners/bin/claudekimi
/Users/yuanshaochen/Projects/local-coding-runners/bin/claudeminmax
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-review
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-mcp-review
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-gemini-review
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker
```

The runner directory is not assumed to be on `PATH`; orchestration should use absolute paths unless a shell profile later adds it.

## Yoga Reference

The Yoga `/vol1/maint` reference scan found useful structures but credentials must not be blindly copied.

Useful remote patterns:

- Kimi wrapper and runbook shape from `/vol1/maint/docs/2026-04-22_kimi_code_and_cli_runbook.md`.
- Gemini batch wrapper shape from `/vol1/maint/ops/scripts/gemini_batch.sh`.
- MiniMax rate-limit and MCP governance notes from `/vol1/maint/docs/2026-05-08_claudeminmax_rate_limit_policy.md` and related docs.
- Runner policy schemas from `/vol1/maint/MAIN/config/clients.json`, `/vol1/maint/MAIN/config/quota_targets.json`, and control-plane policy docs.

Do not copy:

- OAuth token caches;
- `.claude.json` login state;
- Gemini account files;
- `MAIN/secrets/*`;
- `.env` files with API keys.

## Local MCP Baseline

Enabled project-safe MCPs:

- `managed-artifact-verifier`
- `managed-game-factory`

These are offline/read-only helpers for:

- hash verification;
- asset packet validation;
- repo/task summaries;
- no-proxy download record validation.

Do not enable broad web/search/browser MCPs globally until a specific task needs them.

## Routing Templates

### Kimi Review

Use for complex code critique, route blocker analysis, or integration review.

```bash
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-mcp-review kimi PROMPT_FILE
```

### Gemini Review

Use for broad research, visual direction, architecture critique, and final independent review.

```bash
RUNNER_TIMEOUT_SECONDS=900 \
  /Users/yuanshaochen/Projects/local-coding-runners/bin/runner-gemini-review PROMPT_FILE
```

The wrapper pins:

```text
--model gemini-3.1-pro-preview
--approval-mode plan
```

### MiniMax Mechanical Work

Use only for simple extraction, report formatting, hash-manifest checks, and low-risk mechanical transforms.

```bash
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-review minimax PROMPT_FILE
```

For write-capable work, require explicit write scope and verification:

```bash
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker minimax \
  --workspace /Users/yuanshaochen/Projects/ai-game-generation-research \
  --prompt PROMPT_FILE \
  --write-scope "SPACE_SEPARATED_ALLOWED_PATHS" \
  --verify "COMMAND" \
  --do-not-edit "credentials, global proxy settings, files outside write scope" \
  --evidence "changed files, commands, verification output"
```

### Claude Code

Use when native Claude behavior or interactive MCP-heavy work is needed:

```bash
claude -p "TASK"
```

## Worker Packet Requirements

Every delegated task must include:

- goal;
- files allowed for reading;
- write scope;
- forbidden paths;
- exact verification command;
- evidence output path;
- whether the worker may download anything;
- no-proxy rule if a download is allowed.

## Verification Commands

```bash
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-env-check
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-capabilities-audit
gemini --model gemini-3.1-pro-preview --approval-mode plan -p "reply OK"
```

## Current Caveats

- Gemini can be capacity-limited; record 429/model-capacity failures as scheduling issues.
- MiniMax is not trusted for architecture or complex debugging.
- Use absolute runner paths until PATH is explicitly configured.
- Credentials are present in the local runner secret store but must never be printed into repo docs or task outputs.
