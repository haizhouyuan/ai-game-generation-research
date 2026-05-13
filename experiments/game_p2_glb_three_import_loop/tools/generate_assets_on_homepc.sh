#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE="yuanhaizhou@192.168.1.17"
REMOTE_DIR="/tmp/game_p2_glb_three_import_loop"

ssh -o BatchMode=yes "$REMOTE" "rm -rf '$REMOTE_DIR' && mkdir -p '$REMOTE_DIR/tools'"
scp "$ROOT/tools/generate_glb_assets.py" "$REMOTE:$REMOTE_DIR/tools/generate_glb_assets.py" >/dev/null
ssh -o BatchMode=yes "$REMOTE" "cd '$REMOTE_DIR' && python3 tools/generate_glb_assets.py"
mkdir -p "$ROOT/outputs"
rsync -a "$REMOTE:$REMOTE_DIR/outputs/" "$ROOT/outputs/"
