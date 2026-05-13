# No-Proxy Governed Download Template

## Purpose

Use this template for every external source, dependency, model, package, archive, or tool download that supports the managed agents game-generation program.

The goal is to allow useful downloads without surprise Clash Verge traffic usage, while preserving source provenance, byte counts, hashes, and failure evidence. Do not change system proxy settings, Clash Verge, shell profiles, or Codex process networking.

## Inputs

Fill these fields before downloading:

| Field | Value |
|---|---|
| `task_id` | `<managed task id>` |
| `lane_id` | `download-provenance`, `unity-agent-mcp`, `asset-generation`, or relevant lane |
| `repo_id` | `ai-game-generation-research` |
| `source_url` | `<URL or git remote>` |
| `source_type` | `<file, archive, git, pip, npm, huggingface, modelscope, unity, other>` |
| `target_path` | `<destination path>` |
| `expected_size_bytes` | `<known size or unknown>` |
| `max_bytes` | `1073741824 unless explicitly approved` |
| `host` | `<Mac, HomePC, YogaS2, other>` |
| `approval_path` | `<approval note path, only required for any single file over 1GB>` |
| `out_dir` | `<download evidence directory>` |

Required preconditions:

- Any single file over 1GB has explicit user approval before the download starts. This is an operator-confirmation guard, not a ban.
- Existing local/HomePC caches are checked before downloading large model files.
- The worker knows which process to inspect with `lsof`.
- Downloads are command-local no-proxy only. Do not modify global networking.

## Commands / Placeholders

Direct file download:

```bash
tools/download_no_proxy.sh \
  "<source_url>" \
  "<target_path>" \
  "<max_seconds>" \
  "<max_bytes>"
```

Git source snapshot:

```bash
env \
  -u HTTP_PROXY -u HTTPS_PROXY -u FTP_PROXY -u ALL_PROXY -u NO_PROXY \
  -u http_proxy -u https_proxy -u ftp_proxy -u all_proxy -u no_proxy \
  -u GIT_PROXY_COMMAND \
  GIT_CONFIG_COUNT=1 \
  GIT_CONFIG_KEY_0=http.proxy \
  GIT_CONFIG_VALUE_0= \
  git -c http.proxy= -c https.proxy= clone --depth=1 "<source_url>" "<target_path>"
```

Proxy verification while the download is running:

```bash
lsof -nP -iTCP | rg -i 'curl|git|pip|npm|python|node|7890|7897|7899|clash|verge'
```

Hash and size:

```bash
du -b "<target_path>" 2>/dev/null || wc -c "<target_path>"
shasum -a 256 "<target_path>"
```

If the selected tool is `pip`, `npm`, Hugging Face, ModelScope, Unity Hub, or another installer, document the equivalent command-local proxy cleanup and the exact command used.

## Required Evidence

The evidence directory must contain:

- `download_plan.md` with source URL, target path, expected size, max bytes, host, and approval status.
- `download_command.txt` with the exact command used.
- `download_log.txt` with stdout/stderr or captured terminal output.
- `lsof_no_proxy_evidence.txt` captured during a meaningful part of the download.
- `artifact_hashes.txt` with SHA256 and byte count for retained files.
- `source_manifest.json` with source URL, retrieved revision or HTTP metadata when available, timestamp, host, output path, byte count, and SHA256.
- Failure log when the download fails or is intentionally skipped.

Pass criteria:

- Download command uses command-local no-proxy controls.
- No evidence shows the download process connecting to local Clash ports such as `127.0.0.1:7890` or `127.0.0.1:7897`.
- Single-file size stays under the approved limit.
- Retained file or source snapshot has SHA256.
- Source and license notes are recorded when known.

## Failure Modes

Record these as blockers or risks:

- `approval_required`: a single file is over 1GB or expected to exceed the currently approved byte limit.
- `proxy_evidence_failed`: download process appears to use local Clash ports.
- `global_proxy_change_requested`: task requires changing system/Clash/shell networking.
- `source_timeout`: direct source access times out without producing a retained artifact.
- `size_unknown_large_risk`: expected size cannot be determined and could exceed 1GB.
- `hash_missing`: artifact retained without SHA256.
- `license_unknown`: source can be downloaded but rights or license are unclear.
- `installer_uncontrolled`: GUI installer or package manager cannot be constrained or inspected.

## WORKER_RESULT Expectations

Return schema-valid `WORKER_RESULT` using `schemas/worker_result.schema.json`.

Use `status: "done"` only when the artifact is retained, no-proxy evidence is captured, size limit is respected, and hashes exist.

Use `status: "partial"` when metadata or a small source snapshot was collected but the main download was skipped or failed safely.

Use `status: "needs_human"` with `needs_human: true` when approval is required for a large file, license, account, Unity installer, or other controlled download.

Use `status: "blocked"` when the download cannot be performed without violating policy.

Required `evidence` entries:

```json
[
  {"type": "doc", "path_or_url": "<out_dir>/download_plan.md", "notes": "Download plan and policy decision"},
  {"type": "log", "path_or_url": "<out_dir>/download_log.txt", "notes": "Download command output"},
  {"type": "log", "path_or_url": "<out_dir>/lsof_no_proxy_evidence.txt", "notes": "No-proxy process evidence"},
  {"type": "hash", "path_or_url": "<out_dir>/artifact_hashes.txt", "notes": "Byte count and SHA256"},
  {"type": "source", "path_or_url": "<source_url>", "notes": "Original source URL"}
]
```

Recommended `next_action`:

- `queue_next_turn` when the artifact is ready for validation or extraction.
- `wait_for_human` when a large download, login, license, or installer decision is required.
- `retry` only when the source timed out and policy controls remain intact.
- `stop` when the source is unsuitable, too large without approval, or cannot be governed.
