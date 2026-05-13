#!/usr/bin/env python3
"""Run a zero-dependency Chrome CDP smoke test for the preserved P0 HTML game."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import secrets
import shutil
import socket
import struct
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "experiments" / "game_p0_g2_browser_smoke_20260512"
DEFAULT_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8766/14.html", help="Local P0 game URL.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Evidence output directory.")
    parser.add_argument("--chrome", default=DEFAULT_CHROME, help="Chrome executable path.")
    parser.add_argument("--port", type=int, default=9237, help="Local Chrome debugging port.")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    result = run_smoke(args.url, args.out_dir, args.chrome, args.port)
    report_path = args.out_dir / "p0_g2_browser_smoke.json"
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hash_path = args.out_dir / "artifact_hashes.json"
    hashes = {path.name: sha256_file(path) for path in sorted(args.out_dir.iterdir()) if path.is_file()}
    hash_path.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path), "hashes": str(hash_path), "status": result["status"]}, indent=2))
    return 0 if result["status"] in {"passed", "partial"} else 1


def run_smoke(url: str, out_dir: Path, chrome_path: str, port: int) -> dict:
    if not is_local_url(url):
        raise ValueError("P0 smoke runner only accepts localhost/127.0.0.1/::1 URLs")
    if not Path(chrome_path).exists():
        raise FileNotFoundError(chrome_path)
    user_data_dir = Path(tempfile.mkdtemp(prefix="codex-p0-chrome-"))
    proc = subprocess.Popen(  # noqa: S603
        build_chrome_command(chrome_path, port, user_data_dir, url),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        websocket_url = wait_for_page_ws(port)
        client = CdpClient(websocket_url)
        client.call("Page.enable")
        client.call("Runtime.enable")
        wait_for_ready(client)
        before = eval_json(
            client,
            """
            ({
              title: document.title,
              canvasCount: document.querySelectorAll('canvas').length,
              hasStartButton: !!document.getElementById('startBtn'),
              hasHud: !!document.getElementById('bottomHud') && !!document.getElementById('topHud'),
              cdnErrorDisplay: getComputedStyle(document.getElementById('cdnError')).display
            })
            """,
        )
        click_result = eval_json(
            client,
            """
            (() => {
              document.getElementById('startBtn').click();
              window.dispatchEvent(new KeyboardEvent('keydown', {key:'w', code:'KeyW', bubbles:true}));
              window.dispatchEvent(new KeyboardEvent('keyup', {key:'w', code:'KeyW', bubbles:true}));
              return {clickedStart: true, dispatchedKeyW: true};
            })()
            """,
        )
        time.sleep(1.0)
        after = eval_json(
            client,
            """
            ({
              lobbyDisplay: getComputedStyle(document.getElementById('lobby')).display,
              pauseDisplay: getComputedStyle(document.getElementById('pauseNotice')).display,
              hasCanvas: !!document.getElementById('game'),
              hudText: document.getElementById('bottomHud').innerText,
              topHudText: document.getElementById('topHud').innerText
            })
            """,
        )
        if after["lobbyDisplay"] != "none":
            rect = eval_json(
                client,
                """
                (() => {
                  const r = document.getElementById('startBtn').getBoundingClientRect();
                  return {x: r.left + r.width / 2, y: r.top + r.height / 2};
                })()
                """,
            )
            client.call(
                "Input.dispatchMouseEvent",
                {"type": "mousePressed", "x": rect["x"], "y": rect["y"], "button": "left", "clickCount": 1},
            )
            client.call(
                "Input.dispatchMouseEvent",
                {"type": "mouseReleased", "x": rect["x"], "y": rect["y"], "button": "left", "clickCount": 1},
            )
            time.sleep(1.0)
            after = eval_json(
                client,
                """
                ({
                  lobbyDisplay: getComputedStyle(document.getElementById('lobby')).display,
                  pauseDisplay: getComputedStyle(document.getElementById('pauseNotice')).display,
                  hasCanvas: !!document.getElementById('game'),
                  hudText: document.getElementById('bottomHud').innerText,
                  topHudText: document.getElementById('topHud').innerText
                })
                """,
            )
            click_result["usedMouseFallback"] = True
        screenshot_path = out_dir / "p0_after_start.png"
        screenshot = client.call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
        screenshot_path.write_bytes(base64.b64decode(screenshot["data"]))
        passed_checks = {
            "loaded_title": bool(before["title"]),
            "canvas_present": before["canvasCount"] >= 1 and after["hasCanvas"],
            "hud_present": before["hasHud"] and bool(after["hudText"]),
            "cdn_loaded": before["cdnErrorDisplay"] == "none",
            "start_clicked": after["lobbyDisplay"] == "none",
            "input_dispatched": True,
            "screenshot_written": screenshot_path.exists() and screenshot_path.stat().st_size > 10_000,
        }
        return {
            "status": "passed" if all(passed_checks.values()) else "partial",
            "url": url,
            "chrome_path": chrome_path,
            "before": before,
            "after": after,
            "input_result": click_result,
            "checks": passed_checks,
            "screenshot": str(screenshot_path),
            "screenshot_sha256": sha256_file(screenshot_path),
            "limitations": [
                "Keyboard input is synthetic CDP dispatch, not a full human playthrough.",
                "Pointer lock is not treated as required for this smoke gate.",
            ],
        }
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(user_data_dir, ignore_errors=True)


def build_chrome_command(chrome_path: str, port: int, user_data_dir: Path, url: str) -> list[str]:
    """Build a local headless Chrome command that keeps WebGL available."""

    return [
        chrome_path,
        "--headless=new",
        "--ignore-gpu-blocklist",
        "--use-gl=angle",
        "--use-angle=metal",
        "--no-first-run",
        "--no-default-browser-check",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--window-size=1440,1000",
        url,
    ]


def is_local_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.hostname in {"localhost", "127.0.0.1", "::1"}


def wait_for_page_ws(port: int) -> str:
    deadline = time.time() + 20
    last_error = None
    while time.time() < deadline:
        try:
            with urlopen(f"http://127.0.0.1:{port}/json", timeout=1) as response:
                pages = json.loads(response.read().decode("utf-8"))
            for page in pages:
                if page.get("type") == "page" and page.get("webSocketDebuggerUrl"):
                    return page["webSocketDebuggerUrl"]
        except Exception as exc:  # noqa: BLE001
            last_error = exc
        time.sleep(0.2)
    raise TimeoutError(f"Chrome debugging endpoint not ready: {last_error}")


def wait_for_ready(client: CdpClient) -> None:
    deadline = time.time() + 20
    while time.time() < deadline:
        state = eval_json(
            client,
            "({ready: document.readyState, hasThree: !!window.THREE, hasStart: !!document.getElementById('startBtn')})",
        )
        if state["ready"] == "complete" and state["hasThree"] and state["hasStart"]:
            return
        time.sleep(0.2)
    raise TimeoutError("P0 page did not become ready")


def eval_json(client: CdpClient, expression: str) -> dict:
    response = client.call(
        "Runtime.evaluate",
        {"expression": expression, "returnByValue": True, "awaitPromise": True},
    )
    result = response["result"]
    if "exceptionDetails" in response:
        raise RuntimeError(response["exceptionDetails"])
    value = result.get("value")
    if not isinstance(value, dict):
        raise RuntimeError(f"Runtime.evaluate did not return an object: {value!r}")
    return value


class CdpClient:
    def __init__(self, websocket_url: str) -> None:
        self.websocket_url = websocket_url
        self.next_id = 1
        self.events: list[dict] = []
        self.socket = connect_websocket(websocket_url)

    def call(self, method: str, params: OptionalDict = None) -> dict:
        request_id = self.next_id
        self.next_id += 1
        self.send({"id": request_id, "method": method, "params": params or {}})
        while True:
            message = self.recv()
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(message["error"])
                return message["result"]
            if "method" in message:
                self.events.append(message)

    def poll_events(self, duration_seconds: float = 0.1) -> None:
        previous_timeout = self.socket.gettimeout()
        deadline = time.time() + duration_seconds
        try:
            self.socket.settimeout(max(0.01, duration_seconds))
            while time.time() < deadline:
                try:
                    message = self.recv()
                except socket.timeout:
                    break
                if "method" in message:
                    self.events.append(message)
        finally:
            self.socket.settimeout(previous_timeout)

    def drain_events(self) -> list[dict]:
        events = self.events
        self.events = []
        return events

    def send(self, message: dict) -> None:
        payload = json.dumps(message, separators=(",", ":")).encode("utf-8")
        self.socket.sendall(encode_ws_frame(payload))

    def recv(self) -> dict:
        while True:
            opcode, payload = read_ws_frame(self.socket)
            if opcode == 1:
                return json.loads(payload.decode("utf-8"))
            if opcode == 9:
                self.socket.sendall(encode_ws_frame(payload, opcode=10))


OptionalDict = Optional[dict[str, object]]


def connect_websocket(websocket_url: str) -> socket.socket:
    parsed = urlparse(websocket_url)
    if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Chrome websocket must be local")
    sock = socket.create_connection((parsed.hostname, parsed.port or 80), timeout=5)
    key = base64.b64encode(secrets.token_bytes(16)).decode("ascii")
    path = parsed.path
    if parsed.query:
        path += "?" + parsed.query
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {parsed.hostname}:{parsed.port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(request.encode("ascii"))
    response = sock.recv(4096)
    if b" 101 " not in response.split(b"\r\n", 1)[0]:
        raise ConnectionError(f"WebSocket handshake failed: {response[:200]!r}")
    return sock


def encode_ws_frame(payload: bytes, opcode: int = 1) -> bytes:
    first = 0x80 | opcode
    mask_bit = 0x80
    length = len(payload)
    header = bytearray([first])
    if length < 126:
        header.append(mask_bit | length)
    elif length < 65536:
        header.extend([mask_bit | 126])
        header.extend(struct.pack("!H", length))
    else:
        header.extend([mask_bit | 127])
        header.extend(struct.pack("!Q", length))
    mask = secrets.token_bytes(4)
    masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    return bytes(header) + mask + masked


def read_ws_frame(sock: socket.socket) -> tuple[int, bytes]:
    first_two = read_exact(sock, 2)
    first, second = first_two
    opcode = first & 0x0F
    masked = bool(second & 0x80)
    length = second & 0x7F
    if length == 126:
        length = struct.unpack("!H", read_exact(sock, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", read_exact(sock, 8))[0]
    mask = read_exact(sock, 4) if masked else b""
    payload = read_exact(sock, length)
    if masked:
        payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    return opcode, payload


def read_exact(sock: socket.socket, size: int) -> bytes:
    chunks = []
    remaining = size
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("WebSocket closed")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
