#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  tools/no_proxy_download.sh URL OUTPUT REPORT

Downloads a file with proxy environment variables unset and writes a small
evidence report. Use this for external downloads over 100MB.

Environment:
  NO_PROXY_DOWNLOAD_EXPECTED_SIZE   optional expected byte size
  NO_PROXY_DOWNLOAD_SHA256          optional expected sha256
EOF
}

if [[ $# -ne 3 ]]; then
  usage
  exit 2
fi

url=$1
output=$2
report=$3

mkdir -p "$(dirname "$output")" "$(dirname "$report")"

started_at=$(date -Is)
tmp_report="${report}.tmp"

{
  echo "# No-Proxy Download Evidence"
  echo
  echo "- started_at: ${started_at}"
  echo "- url: ${url}"
  echo "- output: ${output}"
  echo "- expected_size_bytes: ${NO_PROXY_DOWNLOAD_EXPECTED_SIZE:-unknown}"
  echo "- expected_sha256: ${NO_PROXY_DOWNLOAD_SHA256:-unknown}"
  echo "- proxy_env_before_command:"
  env | grep -i proxy || true
  echo
  echo "## Command"
  echo
  printf '```bash\n'
  printf 'env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY curl --noproxy %q -L --fail --continue-at - --output %q %q\n' '*' "$output" "$url"
  printf '```\n'
} > "$tmp_report"

env -u http_proxy -u https_proxy -u all_proxy \
  -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl --noproxy '*' -L --fail --continue-at - --output "$output" "$url"

size_bytes=$(stat -f '%z' "$output" 2>/dev/null || stat -c '%s' "$output")
sha256=$(shasum -a 256 "$output" | awk '{print $1}')
finished_at=$(date -Is)

{
  echo
  echo "## Result"
  echo
  echo "- finished_at: ${finished_at}"
  echo "- size_bytes: ${size_bytes}"
  echo "- sha256: ${sha256}"
} >> "$tmp_report"

if [[ -n "${NO_PROXY_DOWNLOAD_EXPECTED_SIZE:-}" && "${NO_PROXY_DOWNLOAD_EXPECTED_SIZE}" != "${size_bytes}" ]]; then
  echo "expected size ${NO_PROXY_DOWNLOAD_EXPECTED_SIZE}, got ${size_bytes}" >&2
  mv "$tmp_report" "$report"
  exit 1
fi

if [[ -n "${NO_PROXY_DOWNLOAD_SHA256:-}" && "${NO_PROXY_DOWNLOAD_SHA256}" != "${sha256}" ]]; then
  echo "expected sha256 ${NO_PROXY_DOWNLOAD_SHA256}, got ${sha256}" >&2
  mv "$tmp_report" "$report"
  exit 1
fi

mv "$tmp_report" "$report"
