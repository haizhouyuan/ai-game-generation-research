#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: $0 URL OUTPUT [MAX_SECONDS] [MAX_BYTES]" >&2
  exit 2
fi

url="$1"
output="$2"
max_seconds="${3:-300}"
max_bytes="${4:-1073741824}"

mkdir -p "$(dirname "$output")"

echo "download_no_proxy: $url"
echo "output: $output"
echo "max_seconds: $max_seconds"
echo "max_bytes: $max_bytes"

env \
  -u HTTP_PROXY -u HTTPS_PROXY -u FTP_PROXY -u ALL_PROXY -u NO_PROXY \
  -u http_proxy -u https_proxy -u ftp_proxy -u all_proxy -u no_proxy \
  -u GIT_PROXY_COMMAND \
  curl \
    -q \
    --proxy "" \
    --noproxy "*" \
    --fail \
    --location \
    --continue-at - \
    --retry 5 \
    --retry-all-errors \
    --retry-delay 3 \
    --connect-timeout 20 \
    --speed-time 60 \
    --speed-limit 1024 \
    --max-filesize "$max_bytes" \
    --max-time "$max_seconds" \
    --output "$output" \
    "$url"

bytes="$(wc -c < "$output" | tr -d ' ')"
sha256="$(shasum -a 256 "$output" | awk '{print $1}')"

echo "bytes: $bytes"
echo "sha256: $sha256"
