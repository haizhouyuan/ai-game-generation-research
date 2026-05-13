# Direct Download Policy - 2026-05-12

## Rule

Do not modify Clash Verge, system proxy settings, shell profiles, or Codex process networking.

Downloads are allowed when they are useful. The hard rule is that managed downloads must not consume paid proxy traffic: use command-local proxy disabling, capture no-proxy evidence, and keep a source/size/hash record.

Single files above `1GB` are not forbidden, but they require explicit approval for that exact source/version/size before the transfer starts so the operator does not accidentally pull a multi-gigabyte package in the background.

## Curl Wrapper

Use:

```bash
tools/download_no_proxy.sh URL OUTPUT [MAX_SECONDS] [MAX_BYTES]
```

The wrapper:

- unsets proxy environment variables only for the child process;
- passes `curl -q` so `~/.curlrc` is ignored;
- passes `--proxy ""` and `--noproxy "*"` to disable proxy use;
- supports resume with `--continue-at -`;
- retries transient failures;
- fails on files larger than `1GB` by default unless the caller passes an explicitly approved larger byte limit;
- prints byte count and SHA256 after success.

## Git Pattern

For Git repositories:

```bash
env \
  -u HTTP_PROXY -u HTTPS_PROXY -u FTP_PROXY -u ALL_PROXY -u NO_PROXY \
  -u http_proxy -u https_proxy -u ftp_proxy -u all_proxy -u no_proxy \
  -u GIT_PROXY_COMMAND \
  GIT_CONFIG_COUNT=1 \
  GIT_CONFIG_KEY_0=http.proxy \
  GIT_CONFIG_VALUE_0= \
  git -c http.proxy= -c https.proxy= clone --depth=1 URL TARGET
```

Prefer source archives over full clones when the repo is large or GitHub direct clone hangs.

## Verification

During a large download, run:

```bash
lsof -nP -iTCP | rg -i 'curl|git|7890|7897|7899|clash|verge'
```

Pass condition:

- download process connects to the target host/CDN IP on port `443`;
- download process does not connect to `127.0.0.1:7890`, `127.0.0.1:7897`, or other local Clash ports.

Codex/ChatGPT/browser may still connect to Clash. That is expected and should not be changed.

## Tool-Specific Notes

| Tool | Required controls |
|---|---|
| `curl` | `-q --proxy "" --noproxy "*" --max-filesize 1073741824` |
| `git` | unset proxy env vars and pass `-c http.proxy= -c https.proxy=` |
| `pip` | prefer `pip download`; use `PIP_CONFIG_FILE=/dev/null --isolated --no-input --timeout 60 --retries 5` |
| `npm` | prefer `npm pack`; use `--proxy=false --https-proxy= --noproxy="*" --userconfig=/dev/null --globalconfig=/dev/null` |
| `huggingface` | clean env, dry-run/metadata first, no files over `1GB` without approval |
| `modelscope` | clean env, explicit revision/local dir, lsof verification |

## Observed Results

- Mac direct `curl`/`git` can connect directly to GitHub IPs, but GitHub direct access is unstable and can timeout.
- HomePC direct `curl` also connects directly to GitHub IPs, but the first test had connection timeout behavior.
- YogaS2 is reachable with `ssh yoga`. Its shell has proxy environment variables pointing at `127.0.0.1:7890`, but command-local cleanup plus `curl -q --proxy "" --noproxy "*"` successfully retrieved GitHub headers directly.
- Existing valid local source snapshots are `external/research_sources/blender-mcp` and `external/research_sources/OpenGame-main`.

## Host Roles

| Host | Role | Download boundary |
|---|---|---|
| Mac | Main orchestration and repo workspace | Use wrapper for external downloads; do not alter Clash/Codex networking |
| HomePC | GPU asset generation and large existing model cache | Prefer existing TRELLIS/ComfyUI/model resources before any new download |
| YogaS2 | Lightweight Node/Python/git/curl validation host | Clean inherited proxy env for every download; limited disk and no GPU |
