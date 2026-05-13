#!/usr/bin/env python3
"""Probe local browser-QA tooling without downloading anything."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "experiments" / "environment_browser_qa_probe_20260512" / "browser_qa_env_probe.json"
BROWSER_CLIENT = (
    Path.home()
    / ".codex"
    / "plugins"
    / "cache"
    / "openai-bundled"
    / "browser-use"
    / "0.1.0-alpha2"
    / "scripts"
    / "browser-client.mjs"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="JSON evidence output path.")
    args = parser.parse_args()

    evidence = build_probe()
    write_evidence(args.out, evidence)
    print(json.dumps({"out": str(args.out), "sha256": sha256_file(args.out)}, indent=2))
    return 0


def build_probe() -> dict:
    commands = {name: probe_command(name) for name in ["node", "npm", "npx", "python3"]}
    proxy_env = {
        key: os.environ.get(key)
        for key in [
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "NO_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "no_proxy",
        ]
        if os.environ.get(key)
    }
    node_path = commands["node"]["path"]
    codex_node = bool(node_path and "/Applications/Codex.app/" in node_path)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": {
            "network_downloads_attempted": False,
            "system_proxy_modified": False,
            "large_download_boundary": "No downloads were attempted; >1GB remains human-gated.",
        },
        "commands": commands,
        "proxy_env_present": proxy_env,
        "browser_plugin": {
            "browser_client_path": str(BROWSER_CLIENT),
            "browser_client_exists": BROWSER_CLIENT.exists(),
        },
        "readiness": {
            "node_available": bool(commands["node"]["path"]),
            "node_is_codex_bundled": codex_node,
            "npm_available": bool(commands["npm"]["path"]),
            "npx_available": bool(commands["npx"]["path"]),
            "can_run_static_node_scripts": bool(commands["node"]["path"]),
            "can_run_npm_package_installs": bool(commands["npm"]["path"]),
            "can_use_browser_plugin_for_localhost": BROWSER_CLIENT.exists(),
        },
        "recommendations": recommendations(commands, BROWSER_CLIENT.exists()),
    }


def probe_command(name: str) -> dict:
    path = shutil.which(name)
    result = {"path": path, "version": None, "error": None}
    if not path:
        result["error"] = "not found on PATH"
        return result
    try:
        completed = subprocess.run(
            [path, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except OSError as exc:
        result["error"] = str(exc)
        return result
    except subprocess.TimeoutExpired:
        result["error"] = "version command timed out"
        return result
    result["version"] = (completed.stdout or completed.stderr).strip()
    if completed.returncode != 0:
        result["error"] = f"version command exited {completed.returncode}"
    return result


def recommendations(commands: dict, browser_plugin_exists: bool) -> list[str]:
    items = []
    if commands["node"]["path"] and not commands["npm"]["path"]:
        items.append(
            "Use bundled Node for local static scripts, but route npm/package setup through download governance."
        )
    if not commands["node"]["path"]:
        items.append("Select or install Node through no-proxy download governance before browser QA automation.")
    if browser_plugin_exists:
        items.append(
            "Use the Browser plugin for localhost visual evidence while npm/Playwright setup remains unresolved."
        )
    if not commands["npm"]["path"]:
        items.append(
            "Do not claim npm-based gates are available until npm is installed or an alternative runner is chosen."
        )
    return items


def write_evidence(path: Path, evidence: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hash_path = path.with_suffix(path.suffix + ".sha256")
    hash_path.write_text(f"{sha256_file(path)}  {path.name}\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
