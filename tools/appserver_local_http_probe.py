#!/usr/bin/env python3
"""Run a disposable localhost JSON-RPC App Server transport proof."""

from __future__ import annotations

import argparse
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from managed_codex.app_server_client import (
    AppServerClient,
    FakeAppServer,
    HttpJsonRpcTransport,
    run_thread_read_fork_interrupt_archive_flow,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "experiments" / "appserver_phase4_local_http_probe_20260512" / "local_http_probe.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result = run_probe()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "events": len(result["events"])}, indent=2))
    return 0


def run_probe() -> dict:
    fake_server = FakeAppServer()
    httpd = make_server(fake_server)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = httpd.server_address
        client = AppServerClient(HttpJsonRpcTransport(f"http://{host}:{port}/rpc"))
        result = run_thread_read_fork_interrupt_archive_flow(
            client,
            name="phase4-local-http-probe",
            prompt="Return schema-valid WORKER_RESULT JSON.",
            output_schema={"type": "object"},
        )
        result["backend_events"] = list(fake_server.events)
        result["transport"] = {
            "url": f"http://{host}:{port}/rpc",
            "local_only": True,
            "fake_server_backend": True,
            "real_app_server_connected": False,
        }
        return result
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def make_server(fake_server: FakeAppServer) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length).decode("utf-8"))
            response = fake_server.handle(request)
            body = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    return ThreadingHTTPServer(("127.0.0.1", find_free_port()), Handler)


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


if __name__ == "__main__":
    raise SystemExit(main())
