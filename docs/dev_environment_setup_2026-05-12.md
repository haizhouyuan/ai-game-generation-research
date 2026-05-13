# Dev Environment Setup - 2026-05-12

## Status

Python managed-agents environment is configured and verified.

Node/npm game-prototype environment is not configured yet. The machine currently exposes a Codex-bundled `node`, but no `npm` was found on PATH.

Homebrew package discovery is no longer treated as an unresolved controller blocker: the user configured USTC Homebrew mirrors in `~/.zprofile` and `~/.zshrc` and verified new shells plus `brew config` see:

```bash
export HOMEBREW_API_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/api"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"
```

The user also verified the USTC `formula.jws.json` HEAD returns `HTTP/2 200` and a 1MB range download succeeds from `202.141.160.110` in about `0.19s`. Future Homebrew/npm installation is still a governed environment task, not an implicit dependency of browser QA.

## Python Environment

Location:

```text
/Users/yuanshaochen/Projects/ai-game-generation-research/.venv
```

Python:

```text
Python 3.9.6
```

Project package:

```text
src/managed_codex/
```

Primary commands:

```bash
.venv/bin/codex-managed init
.venv/bin/codex-managed status
.venv/bin/codex-managed tasks
.venv/bin/codex-managed validate-result tools/managed_codex/examples/worker_result_valid.json
.venv/bin/python -m pytest -q
.venv/bin/ruff check src tests
```

Dependencies are declared in:

```text
pyproject.toml
```

Installed dependency snapshot:

```text
requirements-dev.lock
```

## Verified

These checks passed after environment setup:

```text
21 passed in 0.01s
All checks passed!
codex-managed init: passed
codex-managed tasks: passed
WORKER_RESULT validation: passed
```

## Why This Replaced The Stdlib-Only Attempt

The stdlib-only script was useful as a spike, but it was the wrong long-term shape for a production managed-agents controller.

The current environment uses:

- `pyproject.toml` for project/dependency metadata;
- editable install for real CLI entrypoint `codex-managed`;
- `src/managed_codex/` package layout;
- `tests/` for pytest tests;
- `pydantic` and `pyyaml` for config loading;
- `jsonschema` for worker result validation;
- `typer` and `rich` for operator-facing CLI;
- `ruff` for lint checks.

## Deferred Frontend Environment

Optional for future npm/Vite prototypes:

- real Node installation outside Codex-bundled Node;
- `npm` or `pnpm`;
- package manager lockfile;
- local dev server command;
- Playwright or browser-use validation path.

Do not block controller-core or P1 browser QA on this. Current P0/P1 evidence uses local Chrome CDP through `tools/run_browser_prototype_gate.py`.
