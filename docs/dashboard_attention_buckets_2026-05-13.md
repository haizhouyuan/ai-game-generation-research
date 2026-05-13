# Dashboard Attention Buckets - 2026-05-13

## Purpose

Close the controller dashboard/status visibility gap from `docs/production_goal_managed_agents_game_chain_v2_2026-05-12.md`: the operator view should answer active, queued, blocked, completed, stale, risky, and needs-human state without requiring manual inference from multiple tables.

## Implemented Shape

`codex-managed dashboard --json-output` now includes first-class fields:

- `queued_tasks`
- `blocked_tasks`
- `completed_tasks`
- `needs_human_items`
- `risky_items`

The human-readable `dashboard` and `status` commands print queued, blocked, completed, missing/stale evidence, needs-human, and risky sections. `status` accepts the same `--capability-max-age-days` stale-evidence option for this compact operator view.

`needs_human_items` is derived from existing registry state without schema changes:

- tasks in `waiting_user` or `waiting_approval`;
- tasks with `needs_human_reason`;
- tasks whose `last_worker_status` is `needs_human`;
- downloads whose status is `needs_approval`.

`risky_items` is a derived operator bucket, not a persistent state:

- open or triaged controller issues;
- tasks in `blocked`, `failed`, `needs_retry`, or `interrupted`;
- capabilities marked `partial` or `blocked`;
- missing or stale capability evidence paths;
- downloads in `needs_approval` or `failed`.

## Verification

```bash
.venv/bin/python -m pytest -q tests/test_registry_ops.py tests/test_event_dashboard_cli.py
.venv/bin/ruff check src/managed_codex/registry_ops.py src/managed_codex/cli.py tests/test_registry_ops.py tests/test_event_dashboard_cli.py
rm -f /tmp/managed_dashboard_attention.sqlite3
.venv/bin/codex-managed init --db /tmp/managed_dashboard_attention.sqlite3 --config config/lanes.yaml
.venv/bin/codex-managed download-record https://download.unity3d.com/download_unity/c1aa84e375f6/MacEditorInstallerArm64/Unity-6000.3.15f1.pkg --task unity-mcp-001 --size-bytes 5112633639 --status metadata_only --db /tmp/managed_dashboard_attention.sqlite3
.venv/bin/codex-managed dashboard --json-output --capability-max-age-days 30 --db /tmp/managed_dashboard_attention.sqlite3
```

Observed:

- targeted dashboard tests: `22 passed`;
- ruff: passed;
- dashboard proof after seeding the Unity Editor approval record:
  - `queued_tasks`: 0
  - `blocked_tasks`: 1
  - `completed_tasks`: 17
  - `needs_human_items`: 1
  - `risky_items`: 6
  - blocked task id: `unity-mcp-001`
  - needs-human source: `download`
