# External Runner Worker Template

## Purpose

Use this template when the orchestrator wants to delegate a low-risk mechanical implementation task to the local external runner pool while preserving explicit write ownership, verification, and evidence.

This capability is not a sandbox and not a broad autonomous delegation system. It is a controlled wrapper path around `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker`.

## Inputs

Fill these fields before a worker run:

| Field | Value |
|---|---|
| `task_id` | `<managed task id>` |
| `lane_id` | `<controller-core, qa-evidence, asset-generation, etc.>` |
| `repo_id` | `ai-game-generation-research` |
| `provider` | `<minimax or kimi>` |
| `workspace` | `<absolute workspace path>` |
| `prompt_path` | `<local-coding-runners prompt path>` |
| `write_scope` | `<exact files/modules worker may edit>` |
| `do_not_edit` | `<forbidden files/modules, private dirs, generated caches>` |
| `verification_command` | `<command the worker must run before DONE>` |
| `timeout_seconds` | `<default 1200; lower for probes>` |
| `expected_evidence` | `<files, logs, hashes, reports>` |
| `out_dir` | `<immutable evidence directory>` |

Required preconditions:

- The write scope is narrow enough that the orchestrator can inspect it after the run.
- The prompt does not require reading secrets, installing packages, making large downloads, changing proxy/global settings, committing, pushing, or running destructive git commands.
- Any single external file over 100M remains under no-proxy governance, and any single file over 1GB has explicit approval before the worker is dispatched.
- A dry run has been reviewed before provider execution.
- The orchestrator is prepared to verify the result independently instead of trusting the worker's `DONE` response.

## Commands / Placeholders

Dry run first:

```bash
RUNNER_TIMEOUT_SECONDS="<timeout_seconds>" \
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker "<provider>" \
  --workspace "<workspace>" \
  --prompt "<prompt_path>" \
  --write-scope "<write_scope>" \
  --do-not-edit "<do_not_edit>" \
  --verify "<verification_command>" \
  --evidence "<expected_evidence>" \
  --dry-run \
  > "<out_dir>/runner_worker_dry_run_prompt.txt"
```

Execute only after reviewing the dry-run prompt:

```bash
RUNNER_TIMEOUT_SECONDS="<timeout_seconds>" \
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker "<provider>" \
  --workspace "<workspace>" \
  --prompt "<prompt_path>" \
  --write-scope "<write_scope>" \
  --do-not-edit "<do_not_edit>" \
  --verify "<verification_command>" \
  --evidence "<expected_evidence>" \
  --i-understand-write-access \
  > "<out_dir>/runner_worker_stdout.txt" \
  2> "<out_dir>/runner_worker_stderr.txt"
```

Independent verification:

```bash
cd "<workspace>"
<verification_command>
git status --short -- "<write_scope>"
shasum -a 256 "<out_dir>/runner_worker_dry_run_prompt.txt" \
  "<out_dir>/runner_worker_stdout.txt" \
  "<out_dir>/runner_worker_stderr.txt"
```

If the worker edits outside the write scope, do not continue. Record a controller issue and ask for human review before deciding whether to revert, preserve, or isolate those changes.

## Required Evidence

The evidence directory must contain:

- `runner_worker_dry_run_prompt.txt`.
- `runner_worker_stdout.txt`.
- `runner_worker_stderr.txt`.
- Verification command output.
- `git status --short` scoped to the expected files, plus a broader status summary when safe.
- Hashes for dry-run prompt, stdout, stderr, and changed files.
- A short report stating:
  - provider;
  - workspace;
  - write scope;
  - verification command;
  - changed files;
  - whether stderr was empty;
  - whether any out-of-scope change was observed;
  - exact limitations of the proof.

## Pass Criteria

- Dry-run prompt was reviewed before execution.
- Worker returns `DONE` or a clearly handled `BLOCKED`.
- Exit code is captured.
- The verification command passes independently.
- Changed files are inside the declared write scope.
- No secret values are printed into stdout, stderr, evidence, or snapshots.
- Docs/config do not promote the result beyond the scope actually proven.

## Failure Modes

Record these as blockers or controller issues:

- `out_of_scope_edit`: worker edited files outside declared write scope.
- `secret_exposure`: stdout/stderr/evidence includes credential values.
- `verification_missing`: worker returned `DONE` without running the required command.
- `verification_failed`: worker output exists but independent verification failed.
- `timeout`: watchdog terminated the provider run.
- `provider_unavailable`: wrapper could not call the selected provider.
- `scope_too_broad`: requested write scope is too broad for external runner delegation.
- `download_or_proxy_risk`: task requires unmanaged downloads, proxy changes, or >1GB approval.

Use `status: "needs_human"` with a specific question when the task needs approval, account access, broader ownership, destructive commands, or secret-bearing context.

## Current Local Proof

The first real low-risk proof is recorded in:

- `experiments/runner_worker_probe_20260513/runner_worker_probe_report.md`
- `experiments/runner_worker_probe_20260513/worker_probe_result.md`
- `docs/runner_snapshots/local_coding_runners_2026-05-13/runner_worker_real_probe_stdout_2026-05-13.txt`
- `docs/runner_snapshots/local_coding_runners_2026-05-13/runner_worker_real_probe_stderr_2026-05-13.txt`

That proof exercised one MiniMax-backed provider turn that wrote a single marker file and passed marker verification. It does not prove broad autonomous implementation, MCP-augmented runner behavior, or hard sandboxing.
