# Managed Codex Registry CLI

This is the Phase 1 managed-agents foundation for the game-generation chain.

It is intentionally read-only beyond registry initialization and config seeding. It does not dispatch Codex turns, touch live threads, or call App Server yet.

## Commands

```bash
.venv/bin/codex-managed init
.venv/bin/codex-managed status
.venv/bin/codex-managed lanes
.venv/bin/codex-managed tasks
.venv/bin/codex-managed threads
.venv/bin/codex-managed validate-result path/to/worker_result.json
```

Default registry path:

```text
.managed_codex/registry.sqlite3
```

Override with:

```bash
CODEX_MANAGED_DB=/tmp/managed.sqlite3 .venv/bin/codex-managed init
```

The legacy script path remains as a compatibility wrapper:

```bash
.venv/bin/python tools/managed_codex/codex_managed.py status
```

## Current Scope

- Seed repos, lanes, and initial tasks from `config/lanes.yaml`.
- Create SQLite tables for repos, lanes, tasks, threads, turns, events, artifacts, evidence, task dependencies, and downloads.
- Show lane/task/thread state without changing dispatch behavior.
- Validate the minimum worker result contract.

## Next Scope

- Add generated App Server schema support.
- Add fake App Server tests.
- Add deterministic scheduler policy checks.
- Persist parsed `WORKER_RESULT` objects into the registry.
- Integrate evidence/artifact indexing commands.
