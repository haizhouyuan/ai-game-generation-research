#!/usr/bin/env python3
"""Protocol smoke tests for the managed-artifact MCP server."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "bin" / "managed-artifact-mcp"
RESEARCH_ROOT = Path("/Users/yuanshaochen/Projects/ai-game-generation-research")


def frame(payload: dict) -> bytes:
    data = json.dumps(payload).encode()
    return b"Content-Length: " + str(len(data)).encode() + b"\r\n\r\n" + data


def lf_frame(payload: dict) -> bytes:
    data = json.dumps(payload).encode()
    return b"Content-Length: " + str(len(data)).encode() + b"\n\n" + data


def jsonl(payload: dict) -> bytes:
    return json.dumps(payload).encode() + b"\n"


def read_frames(data: bytes) -> list[dict]:
    frames = []
    pos = 0
    while pos < len(data):
        if data[pos : pos + 1] == b"{":
            line_end = data.find(b"\n", pos)
            assert line_end >= 0, data[pos:]
            frames.append(json.loads(data[pos:line_end]))
            pos = line_end + 1
            continue
        header_end = data.find(b"\r\n\r\n", pos)
        assert header_end >= 0, data[pos:]
        header = data[pos:header_end].decode()
        length = None
        for line in header.split("\r\n"):
            if line.lower().startswith("content-length:"):
                length = int(line.split(":", 1)[1].strip())
        assert length is not None
        body_start = header_end + 4
        body_end = body_start + length
        frames.append(json.loads(data[body_start:body_end]))
        pos = body_end
    return frames


def test_lists_verify_tool() -> None:
    stdin = b"".join(
        [
            frame({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            frame({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}),
            frame({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
        ]
    )
    result = subprocess.run(
        [sys.executable, str(SERVER)],
        input=stdin,
        capture_output=True,
        check=True,
    )

    frames = read_frames(result.stdout)
    assert frames[0]["result"]["serverInfo"]["name"] == "managed-artifact-verifier"
    tools = frames[1]["result"]["tools"]
    assert [tool["name"] for tool in tools] == ["verify_artifact_hashes"]


def test_calls_verify_artifact_hashes_tool() -> None:
    manifest = (
        "experiments/game_p1_rover_workshop_demo/evidence/"
        "2026-05-13_rw_rover_001_texture_g4/artifact_hashes.json"
    )
    assert (RESEARCH_ROOT / manifest).is_file()
    stdin = b"".join(
        [
            frame({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            frame({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}),
            frame(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "verify_artifact_hashes",
                        "arguments": {"manifests": [manifest]},
                    },
                }
            ),
        ]
    )
    result = subprocess.run(
        [sys.executable, str(SERVER)],
        input=stdin,
        capture_output=True,
        check=True,
    )

    frames = read_frames(result.stdout)
    tool_result = frames[1]["result"]
    assert tool_result["isError"] is False
    text = tool_result["content"][0]["text"]
    assert "exit_code: 0" in text
    assert "verified" in text
    assert "artifact_hashes.json" in text


def test_accepts_lf_only_headers() -> None:
    stdin = b"".join(
        [
            lf_frame({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            lf_frame({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
        ]
    )
    result = subprocess.run(
        [sys.executable, str(SERVER)],
        input=stdin,
        capture_output=True,
        timeout=2,
        check=True,
    )

    frames = read_frames(result.stdout)
    assert frames[0]["result"]["serverInfo"]["name"] == "managed-artifact-verifier"
    assert frames[1]["result"]["tools"][0]["name"] == "verify_artifact_hashes"


def test_accepts_jsonl_stdio_messages() -> None:
    stdin = b"".join(
        [
            jsonl({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            jsonl({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}),
            jsonl({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
        ]
    )
    result = subprocess.run(
        [sys.executable, str(SERVER)],
        input=stdin,
        capture_output=True,
        check=True,
    )

    assert result.stdout.startswith(b'{"jsonrpc"')
    frames = read_frames(result.stdout)
    assert frames[0]["result"]["serverInfo"]["name"] == "managed-artifact-verifier"
    assert frames[1]["result"]["tools"][0]["name"] == "verify_artifact_hashes"


def test_ignores_cancelled_notification() -> None:
    stdin = b"".join(
        [
            jsonl({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            jsonl(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/cancelled",
                    "params": {"requestId": 99, "reason": "client probe"},
                }
            ),
            jsonl({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
        ]
    )
    result = subprocess.run(
        [sys.executable, str(SERVER)],
        input=stdin,
        capture_output=True,
        check=True,
    )

    frames = read_frames(result.stdout)
    assert [frame["id"] for frame in frames] == [1, 2]
    assert frames[1]["result"]["tools"][0]["name"] == "verify_artifact_hashes"
