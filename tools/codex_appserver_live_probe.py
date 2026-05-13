#!/usr/bin/env python3
"""Small live probe for the Codex App Server stdio v2 protocol.

The v2 app-server wire format is newline-delimited JSON without a ``jsonrpc``
field. This helper keeps that boundary separate from the older fake JSON-RPC
client in ``src/managed_codex/app_server_client.py``.
"""

from __future__ import annotations

import argparse
import json
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Optional, Protocol, Union

DEFAULT_CODEX = Path("/Applications/Codex.app/Contents/Resources/codex")
DEFAULT_TIMEOUT_SECONDS = 20.0
RequestId = Union[str, int]


class AppServerProbeError(RuntimeError):
    """Raised when the live probe cannot complete a bounded operation."""


class JsonLineTransport(Protocol):
    def send(self, message: dict[str, Any]) -> None:
        ...

    def receive(self, timeout_seconds: float) -> dict[str, Any]:
        ...

    def close(self) -> None:
        ...


class RequestResult:
    def __init__(self, response: dict[str, Any], notifications: list[dict[str, Any]]) -> None:
        self.response = response
        self.notifications = notifications


class PopenJsonLineTransport:
    """Line-oriented JSON transport for ``codex app-server --listen stdio://``."""

    def __init__(self, command: list[str]) -> None:
        self.command = command
        self.process = subprocess.Popen(  # noqa: S603
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        if self.process.stdin is None or self.process.stdout is None:
            raise AppServerProbeError("failed to open app-server stdio pipes")
        self._stdin = self.process.stdin
        self._stdout_queue: queue.Queue[Union[str, BaseException]] = queue.Queue()
        self._stderr_lines: queue.Queue[str] = queue.Queue()
        self._stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()

    def send(self, message: dict[str, Any]) -> None:
        line = json.dumps(message, separators=(",", ":"), ensure_ascii=True)
        try:
            self._stdin.write(line + "\n")
            self._stdin.flush()
        except BrokenPipeError as exc:
            raise AppServerProbeError(f"app-server stdin closed: {self.stderr_tail()}") from exc

    def receive(self, timeout_seconds: float) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"timed out waiting for app-server line; stderr={self.stderr_tail()}")
            if self.process.poll() is not None and self._stdout_queue.empty():
                raise AppServerProbeError(
                    f"app-server exited with {self.process.returncode}; stderr={self.stderr_tail()}"
                )
            try:
                item = self._stdout_queue.get(timeout=min(remaining, 0.25))
            except queue.Empty:
                continue
            if isinstance(item, BaseException):
                raise AppServerProbeError(f"stdout reader failed: {item}") from item
            line = item.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AppServerProbeError(f"app-server emitted non-JSON line: {line[:300]}") from exc
            if not isinstance(payload, dict):
                raise AppServerProbeError(f"app-server emitted non-object JSON line: {line[:300]}")
            return payload

    def close(self) -> None:
        if self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    def stderr_tail(self, limit: int = 20) -> str:
        lines = list(self._stderr_lines.queue)[-limit:]
        return "\n".join(lines)

    def _read_stdout(self) -> None:
        assert self.process.stdout is not None
        try:
            for line in self.process.stdout:
                self._stdout_queue.put(line)
        except BaseException as exc:  # pragma: no cover - defensive reader path
            self._stdout_queue.put(exc)

    def _read_stderr(self) -> None:
        assert self.process.stderr is not None
        for line in self.process.stderr:
            self._stderr_lines.put(line.rstrip("\n"))


class AppServerLiveClient:
    """Request/notification collector for raw v2 app-server messages."""

    def __init__(self, transport: JsonLineTransport, default_timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        self.transport = transport
        self.default_timeout_seconds = default_timeout_seconds
        self._next_id = 1
        self._pending_responses: dict[RequestId, dict[str, Any]] = {}
        self.notifications: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        params: Optional[dict[str, Any]] = None,
        request_id: Optional[RequestId] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RequestResult:
        if request_id is None:
            request_id = self._allocate_id()
        message = build_request(method, params or {}, request_id)
        self.transport.send(message)
        notifications = self.collect_until_response(request_id, timeout_seconds=timeout_seconds)
        response = self._pending_responses.pop(request_id)
        if "error" in response:
            raise AppServerProbeError(f"app-server error for {method}: {response['error']}")
        if "result" not in response:
            raise AppServerProbeError(f"app-server response missing result: {response}")
        return RequestResult(response=response, notifications=notifications)

    def collect_until_response(
        self,
        request_id: RequestId,
        timeout_seconds: Optional[float] = None,
    ) -> list[dict[str, Any]]:
        notifications: list[dict[str, Any]] = []
        if request_id in self._pending_responses:
            return notifications

        deadline = time.monotonic() + (self.default_timeout_seconds if timeout_seconds is None else timeout_seconds)
        while request_id not in self._pending_responses:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"timed out waiting for response id {request_id!r}")
            message = self.transport.receive(remaining)
            message_id = message.get("id")
            if message_id is not None and ("result" in message or "error" in message):
                self._pending_responses[message_id] = message
            elif "method" in message:
                notifications.append(message)
                self.notifications.append(message)
            else:
                raise AppServerProbeError(f"unrecognized app-server message: {message}")
        return notifications

    def collect_until_notification(
        self,
        method: str,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + (self.default_timeout_seconds if timeout_seconds is None else timeout_seconds)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"timed out waiting for notification {method!r}")
            message = self.transport.receive(remaining)
            message_id = message.get("id")
            if message_id is not None and ("result" in message or "error" in message):
                self._pending_responses[message_id] = message
            elif message.get("method") == method:
                self.notifications.append(message)
                return message
            elif "method" in message:
                self.notifications.append(message)
            else:
                raise AppServerProbeError(f"unrecognized app-server message: {message}")

    def close(self) -> None:
        self.transport.close()

    def _allocate_id(self) -> int:
        request_id = self._next_id
        self._next_id += 1
        return request_id


def build_request(method: str, params: dict[str, Any], request_id: RequestId) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise AppServerProbeError("params must be an object")
    return {"id": request_id, "method": method, "params": params}


def spawn_app_server_transport(command: Optional[list[str]] = None) -> PopenJsonLineTransport:
    return PopenJsonLineTransport(command or default_app_server_command())


def default_app_server_command(codex_path: Path = DEFAULT_CODEX) -> list[str]:
    return [str(codex_path), "app-server", "--listen", "stdio://"]


def run_metadata_lifecycle(
    client: AppServerLiveClient,
    *,
    cwd: Path,
    include_turn: bool = False,
    turn_input: str = "Return a short lifecycle probe acknowledgement.",
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    cwd = cwd.resolve()
    evidence: dict[str, Any] = {
        "status": "DONE",
        "mode": "metadata-only" if not include_turn else "include-turn",
        "includeTurn": include_turn,
        "cwd": str(cwd),
        "requests": [],
        "notifications": [],
        "turnStarted": False,
    }
    parent_thread_id: Optional[str] = None
    forked_thread_id: Optional[str] = None

    try:
        initialize = _request_and_record(
            client,
            evidence,
            "initialize",
            {
                "clientInfo": {
                    "name": "codex-appserver-live-probe",
                    "title": "Codex App Server Live Probe",
                    "version": "0.1.0",
                },
                "capabilities": {"experimentalApi": True},
            },
            "initialize",
            timeout_seconds,
        )
        evidence["initializeResultKeys"] = sorted(initialize.response.get("result", {}).keys())

        started = _request_and_record(
            client,
            evidence,
            "thread/start",
            {
                "cwd": str(cwd),
                "ephemeral": False,
                "approvalPolicy": "never",
                "sandbox": "read-only",
                "model": "gpt-5.4-mini",
                "threadSource": "user",
            },
            "thread-start",
            timeout_seconds,
        )
        parent_thread_id = extract_thread_id(started.response)
        evidence["parentThreadId"] = parent_thread_id

        if include_turn:
            turn = _request_and_record(
                client,
                evidence,
                "turn/start",
                {
                    "threadId": parent_thread_id,
                    "cwd": str(cwd),
                    "input": [{"type": "text", "text": turn_input}],
                    "effort": "minimal",
                    "approvalPolicy": "never",
                    "sandboxPolicy": {"type": "readOnly", "networkAccess": False},
                },
                "turn-start",
                timeout_seconds,
            )
            evidence["turnStarted"] = True
            turn_id = extract_turn_id(turn.response)
            evidence["turnId"] = turn_id
            started_event = client.collect_until_notification("turn/started", timeout_seconds=timeout_seconds)
            evidence["notifications"].append(started_event)
            _request_and_record(
                client,
                evidence,
                "turn/interrupt",
                {"threadId": parent_thread_id, "turnId": turn_id},
                "turn-interrupt",
                timeout_seconds,
            )
            evidence["turnInterrupted"] = True
            _request_and_record(
                client,
                evidence,
                "thread/read",
                {"threadId": parent_thread_id, "includeTurns": True},
                "thread-read-after-interrupt",
                timeout_seconds,
            )
        else:
            _request_and_record(
                client,
                evidence,
                "thread/read",
                {"threadId": parent_thread_id, "includeTurns": False},
                "thread-read",
                timeout_seconds,
            )

        forked = _request_and_record(
            client,
            evidence,
            "thread/fork",
            {
                "threadId": parent_thread_id,
                "cwd": str(cwd),
                "ephemeral": False,
                "approvalPolicy": "never",
                "sandbox": "read-only",
                "excludeTurns": True,
            },
            "thread-fork",
            timeout_seconds,
        )
        forked_thread_id = extract_thread_id(forked.response)
        evidence["forkedThreadId"] = forked_thread_id
    except Exception as exc:
        evidence["status"] = "BLOCKED"
        evidence["error"] = str(exc)
    finally:
        for label, thread_id in (("archive-parent", parent_thread_id), ("archive-fork", forked_thread_id)):
            if thread_id is None:
                continue
            try:
                _request_and_record(
                    client,
                    evidence,
                    "thread/archive",
                    {"threadId": thread_id},
                    label,
                    timeout_seconds,
                )
            except Exception as exc:
                evidence["status"] = "DONE_WITH_CONCERNS" if evidence["status"] == "DONE" else evidence["status"]
                evidence.setdefault("archiveErrors", []).append({"threadId": thread_id, "error": str(exc)})

    evidence["notificationCount"] = len(evidence["notifications"])
    return evidence


def summarize_lifecycle_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Return a dry, stable summary useful for tests and release packets."""

    return {
        "status": evidence.get("status", "BLOCKED"),
        "mode": evidence.get("mode"),
        "includeTurn": bool(evidence.get("includeTurn")),
        "parentThreadId": evidence.get("parentThreadId"),
        "forkedThreadId": evidence.get("forkedThreadId"),
        "turnStarted": bool(evidence.get("turnStarted")),
        "turnInterrupted": bool(evidence.get("turnInterrupted")),
        "turnId": evidence.get("turnId"),
        "requestMethods": [request.get("method") for request in evidence.get("requests", [])],
        "notificationCount": len(evidence.get("notifications", [])),
        "archiveErrors": evidence.get("archiveErrors", []),
        "error": evidence.get("error"),
    }


def extract_thread_id(response: dict[str, Any]) -> str:
    result = response.get("result")
    if not isinstance(result, dict):
        raise AppServerProbeError(f"response result must be an object: {response}")
    thread = result.get("thread")
    if isinstance(thread, dict) and isinstance(thread.get("id"), str):
        return thread["id"]
    if isinstance(result.get("threadId"), str):
        return result["threadId"]
    raise AppServerProbeError(f"could not find thread id in response: {response}")


def extract_turn_id(response: dict[str, Any]) -> str:
    result = response.get("result")
    if not isinstance(result, dict):
        raise AppServerProbeError(f"response result must be an object: {response}")
    turn = result.get("turn")
    if isinstance(turn, dict) and isinstance(turn.get("id"), str):
        return turn["id"]
    if isinstance(result.get("turnId"), str):
        return result["turnId"]
    raise AppServerProbeError(f"could not find turn id in response: {response}")


def _request_and_record(
    client: AppServerLiveClient,
    evidence: dict[str, Any],
    method: str,
    params: dict[str, Any],
    request_id: RequestId,
    timeout_seconds: float,
) -> RequestResult:
    evidence["requests"].append({"id": request_id, "method": method, "params": params})
    result = client.request(method, params, request_id=request_id, timeout_seconds=timeout_seconds)
    evidence["notifications"].extend(result.notifications)
    return result


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-only", action="store_true", help="Run initialize/read/fork/archive without a turn")
    parser.add_argument(
        "--include-turn",
        action="store_true",
        help="Also start one model turn during the disposable probe",
    )
    parser.add_argument("--turn-input", default="Return a short lifecycle probe acknowledgement.")
    parser.add_argument(
        "--cwd",
        type=Path,
        required=True,
        help="Working directory for the disposable App Server thread",
    )
    parser.add_argument("--out", type=Path, required=True, help="JSON evidence output path")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--codex", type=Path, default=DEFAULT_CODEX)
    args = parser.parse_args(argv)
    if not args.metadata_only and not args.include_turn:
        parser.error("pass --metadata-only, or explicitly pass --include-turn to permit turn/start")
    if args.include_turn:
        args.metadata_only = False
    return args


def main(
    argv: Optional[list[str]] = None,
    *,
    transport_factory: Optional[Callable[[list[str]], JsonLineTransport]] = None,
) -> int:
    args = parse_args(argv)
    command = default_app_server_command(args.codex)
    transport = (transport_factory or (lambda cmd: spawn_app_server_transport(cmd)))(command)
    client = AppServerLiveClient(transport, default_timeout_seconds=args.timeout_seconds)
    try:
        evidence = run_metadata_lifecycle(
            client,
            cwd=args.cwd,
            include_turn=args.include_turn,
            turn_input=args.turn_input,
            timeout_seconds=args.timeout_seconds,
        )
    finally:
        client.close()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summarize_lifecycle_evidence(evidence), indent=2, sort_keys=True))
    return 0 if evidence["status"] in {"DONE", "DONE_WITH_CONCERNS"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
