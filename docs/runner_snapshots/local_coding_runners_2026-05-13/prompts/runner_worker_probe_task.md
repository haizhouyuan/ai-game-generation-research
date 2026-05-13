# Runner Worker Probe Task

Create exactly one file:

`experiments/runner_worker_probe_20260513/worker_probe_result.md`

The file must contain these lines:

```text
# Runner Worker Probe Result

RUNNER_WORKER_PROBE_OK
provider: minimax
write_scope: experiments/runner_worker_probe_20260513/worker_probe_result.md
verification: test-file-and-marker
```

Do not edit any other file. Do not read secrets. Do not install packages, download files, call unrelated APIs, commit, push, or run destructive git commands.

After writing the file, run:

```bash
test -f experiments/runner_worker_probe_20260513/worker_probe_result.md && rg -n "RUNNER_WORKER_PROBE_OK|provider: minimax|write_scope:" experiments/runner_worker_probe_20260513/worker_probe_result.md
```

Return `DONE` with the file changed and command run. If you cannot create exactly that file, return `BLOCKED`.
