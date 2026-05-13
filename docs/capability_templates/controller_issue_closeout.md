# Controller Issue Closeout Template

## Purpose

Use this template whenever managed agents encounter a controller, scheduler, registry, worker protocol, toolchain, or evidence failure that should improve the system rather than become invisible manual memory.

The controller issue log is part of the product. A task that gets stuck, retries blindly, lacks evidence, loses state, or needs unclear human intervention must leave behind a closeout record.

## Inputs

Fill these fields when opening or closing a controller issue:

| Field | Value |
|---|---|
| `issue_id` | `<ctrl-YYYYMMDD-short-slug>` |
| `task_id` | `<managed task id or null>` |
| `lane_id` | `<lane that exposed the issue>` |
| `repo_id` | `ai-game-generation-research` |
| `severity` | `<low, medium, high, critical>` |
| `state` | `<open, investigating, fixed, mitigated, wont_fix, blocked>` |
| `symptom` | `<what went wrong>` |
| `root_cause` | `<known or unknown>` |
| `affected_threads` | `<thread ids if applicable>` |
| `affected_artifacts` | `<paths if applicable>` |
| `closeout_path` | `<path to this closeout record>` |

Required preconditions:

- Do not hide controller problems by simply retrying a worker.
- If an issue affects automatic dispatch safety, default to fail-close.
- If human action is required, record the exact question and set the worker result to `needs_human`.

## Commands / Placeholders

Use the actual command paths available in the repo. Examples:

```bash
# Inspect current status
.venv/bin/codex-managed status
.venv/bin/codex-managed tasks
.venv/bin/codex-managed issues

# Validate worker result when a worker output is involved
.venv/bin/codex-managed validate-result "<worker_result.json>"

# Record or inspect issue evidence, when CLI support exists
<codex_managed_issue_command> \
  --issue-id "<issue_id>" \
  --task-id "<task_id>" \
  --lane-id "<lane_id>" \
  --severity "<severity>" \
  --state "<state>" \
  --evidence "<closeout_path>"
```

If CLI support does not yet exist, create a Markdown closeout and return `WORKER_RESULT` with `status: "partial"` or `status: "needs_review"` so the missing controller feature is visible.

## Required Evidence

Each closeout must include:

- Issue id, lane, task, thread/turn ids if known.
- Symptom and timestamp.
- Triggering command, worker result, scheduler decision, or user-visible failure.
- Expected behavior.
- Actual behavior.
- Root cause or current hypothesis.
- Impact on safety, dispatch, evidence, artifact integrity, or user workflow.
- Fix, mitigation, or recommended controller improvement.
- Verification command and result when fixed.
- Follow-up task if unresolved.

Pass criteria for closing as `fixed`:

- The root cause is documented.
- A fix or mitigation is implemented or clearly linked.
- Verification evidence proves the issue no longer reproduces.
- Related worker/task state is corrected or documented.

Pass criteria for closing as `mitigated`:

- The risk is contained.
- The remaining limitation is documented.
- A future task exists if production acceptance still requires a full fix.

## Failure Modes

Record these as blockers or risks:

- `blind_retry`: worker was retried without understanding failure mode.
- `invalid_worker_result`: worker output failed schema validation.
- `missing_evidence`: worker claimed success without required evidence.
- `duplicate_dispatch`: scheduler dispatched the same task twice.
- `stale_registry`: registry state diverged from actual files, threads, or artifacts.
- `unsafe_autocontinue`: scheduler continued despite blocker, needs_human, cooldown, or disabled lane.
- `app_server_contract_drift`: real App Server behavior differs from request schema or fake harness.
- `download_policy_gap`: tool or worker attempted unmanaged external download.
- `human_question_unclear`: user approval or input was needed but not stated concretely.
- `closeout_unverified`: issue was marked fixed without verification evidence.

## WORKER_RESULT Expectations

Return schema-valid `WORKER_RESULT` using `schemas/worker_result.schema.json`.

Use `status: "done"` only when the issue is fully closed with verification evidence.

Use `status: "partial"` when the issue is documented and triaged but not fixed.

Use `status: "needs_review"` when the closeout needs controller-owner review before state changes.

Use `status: "needs_human"` with a specific `human_question` when approval, product decision, account access, or large download policy is blocking.

Required `evidence` entries:

```json
[
  {"type": "doc", "path_or_url": "<closeout_path>", "notes": "Controller issue closeout"},
  {"type": "log", "path_or_url": "<relevant_log_path>", "notes": "Failure or verification log"},
  {"type": "test", "path_or_url": "<verification_output_path>", "notes": "Verification evidence, if fixed"}
]
```

Recommended `next_action`:

- `archive` when the issue is fixed and verified.
- `review` when a controller owner should approve the closeout.
- `queue_next_turn` when a concrete fix task is ready.
- `wait_for_human` when the issue needs approval or a decision.
- `stop` when the issue makes automatic continuation unsafe.
