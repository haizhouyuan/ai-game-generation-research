# Download Registry Controller Update - 2026-05-13

## Result

The Managed Agents registry now has a normal closeout path for governed download metadata.

This does not perform downloads. It records plans, metadata-only probes, completed downloads, failures, skipped downloads, and approval blockers into the existing SQLite `downloads` table.

## Commands

Record a download or metadata probe:

```bash
.venv/bin/codex-managed download-record SOURCE_URL \
  --task TASK_ID \
  --retained-path PATH \
  --size-bytes BYTES \
  --sha256 SHA256 \
  --command "exact command or plan" \
  --no-proxy-proof PATH_OR_NOTE \
  --status planned
```

List records:

```bash
.venv/bin/codex-managed downloads --json-output
```

Dashboard visibility:

```bash
.venv/bin/codex-managed dashboard --json-output
```

## Policy Behavior

If `size_bytes` is over `1GiB` and `--approved-over-1gb` is not provided, `download-record` does not allow the record to become `done`.

For planned or metadata-only records, the command stores the status as `needs_approval`. This lets the registry represent blocked downloads such as Unity Editor installers without performing them.

The `done` status requires retained artifact path, byte count, SHA256, command text, and no-proxy proof. This keeps `done` aligned with the no-proxy governed download template rather than turning it into a loose note.

## Proof

Temporary registry proof:

```bash
CODEX_MANAGED_DB=/tmp/managed_download_record_demo.sqlite3 .venv/bin/codex-managed init
CODEX_MANAGED_DB=/tmp/managed_download_record_demo.sqlite3 .venv/bin/codex-managed download-record \
  'https://download.unity3d.com/download_unity/c1aa84e375f6/MacEditorInstallerArm64/Unity-6000.3.15f1.pkg' \
  --task unity-mcp-001 \
  --size-bytes 5112633639 \
  --command 'HEAD-only metadata probe; no download' \
  --no-proxy-proof experiments/unity_host_probe_20260513/outputs/unity_6000_3_15f1_macos_arm64_pkg_head.txt \
  --status metadata_only
CODEX_MANAGED_DB=/tmp/managed_download_record_demo.sqlite3 .venv/bin/codex-managed downloads --json-output
```

Observed record:

```json
{
  "source_url": "https://download.unity3d.com/download_unity/c1aa84e375f6/MacEditorInstallerArm64/Unity-6000.3.15f1.pkg",
  "task_id": "unity-mcp-001",
  "size_bytes": 5112633639,
  "status": "needs_approval"
}
```

Verification:

```bash
.venv/bin/python -m pytest -q tests/test_registry_ops.py tests/test_event_dashboard_cli.py
.venv/bin/ruff check src/managed_codex/registry_ops.py src/managed_codex/cli.py tests/test_registry_ops.py tests/test_event_dashboard_cli.py
```

Observed targeted tests after review fixes: `20 passed`.

Observed full test suite after this change: `73 passed`.
