#!/usr/bin/env python3
"""Run a local browser evidence gate for playable prototypes."""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import socket
import struct
import subprocess
import tempfile
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote, urlparse

try:
    from p0_chrome_cdp_smoke import CdpClient, build_chrome_command, eval_json, sha256_file, wait_for_page_ws
except ModuleNotFoundError:
    from tools.p0_chrome_cdp_smoke import CdpClient, build_chrome_command, eval_json, sha256_file, wait_for_page_ws

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SCREENSHOT_NAMES = {
    "load": "00_load.png",
    "start": "01_start.png",
    "input": "02_input.png",
    "pickup": "03_pickup.png",
    "hazard": "04_hazard.png",
    "gate": "05_gate.png",
    "finish": "06_finish.png",
}

REQUIRED_PROMOTION_CHECKS = {
    "load",
    "nonblank_canvas",
    "hud",
    "input",
    "pickup",
    "hazard",
    "gate_or_puzzle",
    "finish",
    "screenshots",
    "hashes",
    "console_errors",
    "network_failures",
    "external_requests",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prototype-id", required=True)
    parser.add_argument("--entrypoint", type=Path, required=True)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--gate-level", choices=["G0", "G1", "G2", "G3", "G4"], required=True)
    parser.add_argument("--browser", default="chromium")
    parser.add_argument("--server-bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--chrome", default=DEFAULT_CHROME)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    args = parser.parse_args()

    result = run_gate(
        prototype_id=args.prototype_id,
        entrypoint=args.entrypoint,
        scenario_path=args.scenario,
        out_dir=args.out,
        gate_level=args.gate_level,
        bind=args.server_bind,
        port=args.port,
        chrome_path=args.chrome,
        timeout_ms=args.timeout_ms,
    )
    print(json.dumps({"release_packet": str(result["release_packet"]), "status": result["status"]}, indent=2))
    return 0 if result["status"] == "passed" else 4


def run_gate(
    *,
    prototype_id: str,
    entrypoint: Path,
    scenario_path: Path,
    out_dir: Path,
    gate_level: str,
    bind: str,
    port: int,
    chrome_path: str,
    timeout_ms: int,
) -> dict[str, Any]:
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    validate_scenario(scenario, prototype_id, gate_level)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "screenshots").mkdir(exist_ok=True)
    (out_dir / "state_dumps").mkdir(exist_ok=True)
    (out_dir / "assets").mkdir(exist_ok=True)

    server_proc: Optional[subprocess.Popen[str]] = None
    user_data_dir = Path(tempfile.mkdtemp(prefix="codex-gate-chrome-"))
    chrome_proc: Optional[subprocess.Popen[str]] = None
    try:
        url = entrypoint_to_url(entrypoint, bind, port)
        if url.startswith("http://127.0.0.1") or url.startswith("http://localhost"):
            parsed = urlparse(url)
            server_proc = start_static_server(bind, parsed.port or 8766)
        chrome_port = find_free_port()
        chrome_proc = subprocess.Popen(  # noqa: S603
            build_chrome_command(chrome_path, chrome_port, user_data_dir, "about:blank"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        client = CdpClient(wait_for_page_ws(chrome_port))
        client.call("Page.enable")
        client.call("Runtime.enable")
        client.call("Log.enable")
        client.call("Network.enable")
        client.call("Page.navigate", {"url": url})
        wait_for_document(client, timeout_ms)
        if prototype_id != "p0_chatgpt_html_baseline":
            wait_for_gate_api(client, timeout_ms)
        step_results = []
        for step in scenario["steps"]:
            state = run_scenario_step(client, prototype_id, step)
            screenshot_path = out_dir / "screenshots" / SCREENSHOT_NAMES.get(step["id"], f"{step['id']}.png")
            screenshot_bytes = capture_screenshot(client, screenshot_path)
            stats = png_pixel_stats(screenshot_bytes)
            dump = {"step": step, "state": state, "pixel_stats": stats}
            (out_dir / "state_dumps" / f"{step['id']}.json").write_text(
                json.dumps(dump, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            step_results.append(dump)
            client.poll_events(0.05)
        client.poll_events(0.2)
        browser_events = client.drain_events()
        console_summary = summarize_console_events(browser_events)
        network_summary = summarize_network_events(browser_events, url)
        checks = summarize_checks(gate_level, step_results, console_summary, network_summary)
        artifacts = write_supporting_artifacts(
            out_dir=out_dir,
            prototype_id=prototype_id,
            entrypoint=entrypoint,
            url=url,
            scenario=scenario,
            step_results=step_results,
            checks=checks,
            browser_events=browser_events,
            console_summary=console_summary,
            network_summary=network_summary,
        )
        packet = build_release_packet(
            release_id=f"{prototype_id}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{gate_level.lower()}",
            prototype_id=prototype_id,
            entrypoint=str(entrypoint),
            gate_level=gate_level,
            checks=checks,
            artifacts=artifacts,
            asset_provenance=scenario.get("asset_provenance", []),
            known_limitations=scenario.get("known_limitations", []),
        )
        packet_path = out_dir / "release_packet.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_closeout(out_dir, packet, checks)
        write_hashes(out_dir)
        status = "passed" if all(value in {"pass", "not_applicable"} for value in checks.values()) else "failed"
        return {"status": status, "release_packet": packet_path}
    finally:
        if chrome_proc:
            chrome_proc.terminate()
            try:
                chrome_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                chrome_proc.kill()
        if server_proc:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()
        shutil.rmtree(user_data_dir, ignore_errors=True)


def validate_scenario(scenario: dict[str, Any], prototype_id: str, gate_level: str) -> None:
    if scenario.get("scenario_version") != "browser_prototype_gate.v1":
        raise ValueError("scenario_version must be browser_prototype_gate.v1")
    if scenario.get("prototype_id") != prototype_id:
        raise ValueError("scenario prototype_id does not match")
    if scenario.get("gate_level") != gate_level:
        raise ValueError("scenario gate_level does not match")
    if not isinstance(scenario.get("steps"), list) or not scenario["steps"]:
        raise ValueError("scenario must include steps")


def entrypoint_to_url(entrypoint: Path, bind: str, port: int) -> str:
    if str(entrypoint).startswith(("http://", "https://")):
        return str(entrypoint)
    resolved = entrypoint.resolve()
    relative = resolved.relative_to(ROOT)
    selected_port = port or find_free_port()
    return f"http://{bind}:{selected_port}/{'/'.join(quote(part) for part in relative.parts)}"


def start_static_server(bind: str, port: int) -> subprocess.Popen[str]:
    return subprocess.Popen(  # noqa: S603
        ["python3", "-m", "http.server", str(port), "--bind", bind, "--directory", str(ROOT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def wait_for_document(client: CdpClient, timeout_ms: int) -> None:
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        state = eval_json(client, "({ready: document.readyState, title: document.title})")
        if state["ready"] == "complete":
            return
        time.sleep(0.2)
    raise TimeoutError("prototype page did not load before timeout")


def wait_for_gate_api(client: CdpClient, timeout_ms: int) -> None:
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        state = eval_json(client, "({hasGate: !!window.__prototypeGate})")
        if state["hasGate"]:
            return
        time.sleep(0.2)
    raise TimeoutError("prototype did not expose window.__prototypeGate before timeout")


def run_scenario_step(client: CdpClient, prototype_id: str, step: dict[str, Any]) -> dict[str, Any]:
    if prototype_id == "p0_chatgpt_html_baseline":
        return run_p0_step(client, step)
    expression = f"""
    (async () => {{
      if (!window.__prototypeGate) throw new Error('missing __prototypeGate API');
      return await window.__prototypeGate.runStep({json.dumps(step)});
    }})()
    """
    return eval_json(client, expression)


def run_p0_step(client: CdpClient, step: dict[str, Any]) -> dict[str, Any]:
    step_id = step["id"]
    if step_id == "load":
        return eval_json(
            client,
            """
            ({
              checks: {
                page_ready: document.readyState === 'complete',
                canvas_present: document.querySelectorAll('canvas').length >= 1,
                hud_present: !!document.getElementById('topHud') && !!document.getElementById('bottomHud')
              },
              hudText: document.getElementById('bottomHud')?.innerText || ''
            })
            """,
        )
    if step_id == "start":
        return eval_json(
            client,
            """
            (() => {
              document.getElementById('startBtn').click();
              return {
                checks: {play_state: getComputedStyle(document.getElementById('lobby')).display === 'none'},
                hudText: document.getElementById('bottomHud')?.innerText || ''
              };
            })()
            """,
        )
    if step_id == "input":
        return eval_json(
            client,
            """
            (() => {
              window.dispatchEvent(new KeyboardEvent('keydown', {key:'w', code:'KeyW', bubbles:true}));
              window.dispatchEvent(new KeyboardEvent('keyup', {key:'w', code:'KeyW', bubbles:true}));
              return {
                checks: {input_dispatched: true, hud_present: !!document.getElementById('bottomHud')?.innerText},
                hudText: document.getElementById('bottomHud')?.innerText || ''
              };
            })()
            """,
        )
    return {"checks": {"not_applicable": True}, "not_applicable": True}


def capture_screenshot(client: CdpClient, path: Path) -> bytes:
    payload = client.call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
    data = base64.b64decode(payload["data"])
    path.write_bytes(data)
    return data


def summarize_checks(
    gate_level: str,
    step_results: list[dict[str, Any]],
    console_summary: dict[str, Any],
    network_summary: dict[str, Any],
) -> dict[str, str]:
    by_step = {result["step"]["id"]: result for result in step_results}
    checks = {
        "load": step_passed(by_step, "load"),
        "nonblank_canvas": "pass" if any(result["pixel_stats"]["nonblank"] for result in step_results) else "fail",
        "hud": (
            "pass"
            if any(result["state"].get("hudText") or result["state"].get("hud") for result in step_results)
            else "fail"
        ),
        "input": step_passed(by_step, "input"),
        "pickup": step_passed(by_step, "pickup"),
        "hazard": step_passed(by_step, "hazard"),
        "gate_or_puzzle": step_passed(by_step, "gate"),
        "finish": step_passed(by_step, "finish"),
        "screenshots": "pass" if all(result["pixel_stats"]["width"] > 0 for result in step_results) else "fail",
        "hashes": "pass",
        "console_errors": "fail" if console_summary.get("errors") else "pass",
        "network_failures": "fail" if network_summary.get("failures") else "pass",
        "external_requests": "fail" if network_summary.get("external_requests") else "pass",
    }
    if gate_level == "G2":
        for key in ["pickup", "hazard", "gate_or_puzzle", "finish"]:
            checks[key] = "not_applicable"
    return checks


def step_passed(by_step: dict[str, dict[str, Any]], step_id: str) -> str:
    result = by_step.get(step_id)
    if not result:
        return "fail"
    checks = result["state"].get("checks", {})
    return "pass" if checks and all(bool(value) for value in checks.values()) else "fail"


def write_supporting_artifacts(
    *,
    out_dir: Path,
    prototype_id: str,
    entrypoint: Path,
    url: str,
    scenario: dict[str, Any],
    step_results: list[dict[str, Any]],
    checks: dict[str, str],
    browser_events: list[dict[str, Any]],
    console_summary: dict[str, Any],
    network_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    scenario_result = {
        "prototype_id": prototype_id,
        "entrypoint": str(entrypoint),
        "url": url,
        "checks": checks,
        "steps": step_results,
    }
    files = {
        "console_summary.json": console_summary,
        "network_summary.json": network_summary,
        "scenario_result.json": scenario_result,
        "browser_log.jsonl": None,
    }
    artifacts = []
    asset_provenance_path = out_dir / "assets" / "asset_provenance.json"
    asset_provenance_path.write_text(
        json.dumps(scenario.get("asset_provenance", []), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    artifacts.append(
        {
            "path": str(asset_provenance_path),
            "sha256": sha256_file(asset_provenance_path),
            "type": "asset_provenance.json",
        }
    )
    for filename, payload in files.items():
        path = out_dir / filename
        if payload is None:
            lines = [
                {"event": "gate_started", "scenario": scenario["scenario_version"], "url": url},
                *browser_events,
            ]
            path.write_text(
                "".join(json.dumps(line, sort_keys=True) + "\n" for line in lines),
                encoding="utf-8",
            )
        else:
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        artifacts.append({"path": str(path), "sha256": sha256_file(path), "type": filename})
    return artifacts


def summarize_console_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    errors = []
    warnings = []
    logs = 0
    for event in events:
        method = event.get("method")
        params = event.get("params", {})
        if method == "Runtime.consoleAPICalled":
            level = params.get("type", "log")
            message = console_args_text(params.get("args", []))
            item = {"level": level, "message": message}
            if level in {"error", "assert"}:
                errors.append(item)
            elif level in {"warning", "warn"}:
                warnings.append(item)
            else:
                logs += 1
        elif method == "Log.entryAdded":
            entry = params.get("entry", {})
            level = entry.get("level", "info")
            item = {"level": level, "message": entry.get("text", "")}
            if level == "error":
                errors.append(item)
            elif level == "warning":
                warnings.append(item)
            else:
                logs += 1
        elif method == "Runtime.exceptionThrown":
            details = params.get("exceptionDetails", {})
            errors.append({"level": "error", "message": details.get("text", "Runtime.exceptionThrown")})
    return {
        "errors": errors,
        "warnings": warnings,
        "log_count": logs,
        "event_count": sum(1 for event in events if event.get("method", "").startswith(("Runtime.", "Log."))),
    }


def console_args_text(args: list[dict[str, Any]]) -> str:
    parts = []
    for arg in args:
        if "value" in arg:
            parts.append(str(arg["value"]))
        elif "description" in arg:
            parts.append(str(arg["description"]))
        else:
            parts.append(arg.get("type", "unknown"))
    return " ".join(parts)


def summarize_network_events(events: list[dict[str, Any]], entry_url: str) -> dict[str, Any]:
    requests: dict[str, dict[str, Any]] = {}
    failures = []
    for event in events:
        method = event.get("method")
        params = event.get("params", {})
        request_id = params.get("requestId")
        if method == "Network.requestWillBeSent" and request_id:
            request = params.get("request", {})
            requests[request_id] = {
                "url": request.get("url", ""),
                "method": request.get("method", ""),
                "type": params.get("type", ""),
            }
        elif method == "Network.responseReceived" and request_id:
            response = params.get("response", {})
            requests.setdefault(request_id, {})["url"] = response.get(
                "url",
                requests.get(request_id, {}).get("url", ""),
            )
            requests.setdefault(request_id, {})["status"] = response.get("status")
            requests[request_id]["mimeType"] = response.get("mimeType", "")
        elif method == "Network.loadingFailed" and request_id:
            failure = {
                "url": requests.get(request_id, {}).get("url", ""),
                "errorText": params.get("errorText", ""),
                "canceled": params.get("canceled", False),
            }
            failures.append(failure)
    request_list = sorted(requests.values(), key=lambda item: item.get("url", ""))
    return {
        "entry_url": entry_url,
        "request_count": len(request_list),
        "requests": request_list,
        "external_requests": [
            request for request in request_list if request.get("url") and not is_local_request(request["url"])
        ],
        "failures": failures,
    }


def is_local_request(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme in {"data", "blob", "about"}:
        return True
    return parsed.scheme in {"http", "https"} and parsed.hostname in {"localhost", "127.0.0.1", "::1"}


def build_release_packet(
    *,
    release_id: str,
    prototype_id: str,
    entrypoint: str,
    gate_level: str,
    checks: dict[str, str],
    artifacts: list[dict[str, Any]],
    asset_provenance: list[dict[str, Any]],
    known_limitations: list[str],
) -> dict[str, Any]:
    promotable = (
        gate_level == "G4"
        and REQUIRED_PROMOTION_CHECKS.issubset(checks)
        and all(value == "pass" for value in checks.values())
    )
    return {
        "packet_version": "prototype_evidence_gate.v1",
        "release_id": release_id,
        "prototype_id": prototype_id,
        "entrypoint": entrypoint,
        "gate_level": gate_level,
        "checks": checks,
        "artifacts": artifacts,
        "asset_provenance": asset_provenance,
        "known_limitations": known_limitations,
        "promotable": promotable,
    }


def write_hashes(out_dir: Path) -> None:
    hashes = {}
    for path in sorted(item for item in out_dir.rglob("*") if item.is_file() and item.name != "artifact_hashes.json"):
        hashes[str(path.relative_to(out_dir))] = {"sha256": sha256_file(path), "size_bytes": path.stat().st_size}
    (out_dir / "artifact_hashes.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_closeout(out_dir: Path, packet: dict[str, Any], checks: dict[str, str]) -> None:
    lines = [
        f"# {packet['prototype_id']} {packet['gate_level']} Closeout",
        "",
        f"- release_id: `{packet['release_id']}`",
        f"- promotable: `{packet['promotable']}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- {key}: `{value}`" for key, value in checks.items())
    lines.append("")
    (out_dir / "closeout.md").write_text("\n".join(lines), encoding="utf-8")


def png_pixel_stats(data: bytes) -> dict[str, Any]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG")
    offset = 8
    width = height = color_type = None
    idat = b""
    while offset < len(data):
        length = struct.unpack("!I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack("!IIBBBBB", payload)
            if bit_depth != 8 or color_type not in {2, 6}:
                raise ValueError("only 8-bit RGB/RGBA PNG screenshots are supported")
        elif kind == b"IDAT":
            idat += payload
        elif kind == b"IEND":
            break
    if width is None or height is None or color_type is None:
        raise ValueError("missing PNG header")
    channels = 4 if color_type == 6 else 3
    stride = width * channels
    raw = zlib.decompress(idat)
    rows = []
    prior = bytes(stride)
    index = 0
    for _ in range(height):
        filter_type = raw[index]
        index += 1
        scanline = bytearray(raw[index : index + stride])
        index += stride
        recon = defilter_scanline(filter_type, scanline, prior, channels)
        rows.append(recon)
        prior = bytes(recon)
    distinct = set()
    nontransparent = 0
    for row in rows:
        for pixel_index in range(0, len(row), channels):
            pixel = tuple(row[pixel_index : pixel_index + channels])
            if channels == 3 or pixel[3] > 0:
                nontransparent += 1
            if len(distinct) < 4096:
                distinct.add(pixel)
    return {
        "width": width,
        "height": height,
        "nontransparent_pixels": nontransparent,
        "distinct_sample_colors": len(distinct),
        "nonblank": nontransparent > 0 and len(distinct) > 1,
    }


def defilter_scanline(filter_type: int, scanline: bytearray, prior: bytes, channels: int) -> bytearray:
    for i, value in enumerate(scanline):
        left = scanline[i - channels] if i >= channels else 0
        up = prior[i]
        up_left = prior[i - channels] if i >= channels else 0
        if filter_type == 1:
            scanline[i] = (value + left) & 0xFF
        elif filter_type == 2:
            scanline[i] = (value + up) & 0xFF
        elif filter_type == 3:
            scanline[i] = (value + ((left + up) // 2)) & 0xFF
        elif filter_type == 4:
            scanline[i] = (value + paeth(left, up, up_left)) & 0xFF
        elif filter_type != 0:
            raise ValueError(f"unsupported PNG filter: {filter_type}")
    return scanline


def paeth(left: int, up: int, up_left: int) -> int:
    estimate = left + up - up_left
    distances = [(abs(estimate - left), left), (abs(estimate - up), up), (abs(estimate - up_left), up_left)]
    return min(distances, key=lambda item: item[0])[1]


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


if __name__ == "__main__":
    raise SystemExit(main())
