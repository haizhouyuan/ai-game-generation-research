"""Schema-boundary helpers for Codex App Server integration.

This module does not talk to a live App Server yet. It defines the small
request-building surface and a fake in-memory server used by controller tests.
The real client should replace the transport while keeping this boundary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol, Union
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ALLOWED_METHODS = {
    "thread/list",
    "thread/read",
    "thread/start",
    "thread/resume",
    "thread/fork",
    "thread/archive",
    "turn/start",
    "turn/steer",
    "turn/interrupt",
    "review/start",
}


class AppServerRequestError(ValueError):
    """Raised before a malformed request can reach App Server."""


class AppServerTransport(Protocol):
    """Transport boundary for fake and live App Server JSON-RPC calls."""

    def send(self, request: dict[str, Any]) -> dict[str, Any]:
        ...


@dataclass
class AppServerClient:
    """Small validated client shared by fake tests and local live transports."""

    transport: AppServerTransport

    def call(
        self,
        method: str,
        params: Optional[dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None,
    ) -> dict[str, Any]:
        request = build_request(method, params=params, request_id=request_id)
        response = self.transport.send(request)
        validate_response_shape(response)
        return response

    def drain_events(self) -> list[dict[str, Any]]:
        pop_events = getattr(self.transport, "pop_events", None)
        if pop_events is None:
            return []
        events = pop_events()
        if not isinstance(events, list):
            raise AppServerRequestError("transport pop_events must return a list")
        for event in events:
            if not isinstance(event, dict):
                raise AppServerRequestError("transport events must be objects")
        return events


@dataclass
class FakeAppServerTransport:
    """Adapter that makes FakeAppServer use the same client as live transports."""

    server: FakeAppServer

    def send(self, request: dict[str, Any]) -> dict[str, Any]:
        return self.server.handle(request)

    def pop_events(self) -> list[dict[str, Any]]:
        events = list(self.server.events)
        self.server.events.clear()
        return events


@dataclass
class HttpJsonRpcTransport:
    """Local-only HTTP JSON-RPC transport for the real App Server bridge."""

    url: str
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        validate_local_http_url(self.url)

    def send(self, request: dict[str, Any]) -> dict[str, Any]:
        validate_request_shape(request)
        body = json.dumps(request, ensure_ascii=True).encode("utf-8")
        http_request = Request(
            self.url,
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urlopen(http_request, timeout=self.timeout_seconds) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise AppServerRequestError("App Server response must be a JSON object")
        return payload


def validate_local_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "http":
        raise AppServerRequestError("live App Server transport must use local http")
    if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise AppServerRequestError("live App Server transport must bind to localhost/127.0.0.1/::1")
    if not parsed.port:
        raise AppServerRequestError("live App Server transport must include an explicit local port")


def build_request(
    method: str,
    params: Optional[dict[str, Any]] = None,
    request_id: Optional[Union[str, int]] = None,
) -> dict[str, Any]:
    if method not in ALLOWED_METHODS:
        raise AppServerRequestError(f"unsupported method: {method}")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        raise AppServerRequestError("params must be an object")
    request: dict[str, Any] = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
    }
    if request_id is not None:
        request["id"] = request_id
    validate_request_shape(request)
    return request


def validate_request_shape(request: dict[str, Any]) -> None:
    if request.get("jsonrpc") != "2.0":
        raise AppServerRequestError("jsonrpc must be 2.0")
    method = request.get("method")
    if method not in ALLOWED_METHODS:
        raise AppServerRequestError(f"unsupported method: {method}")
    params = request.get("params")
    if not isinstance(params, dict):
        raise AppServerRequestError("params must be an object")

    if method in {"thread/read", "thread/resume", "thread/fork", "thread/archive"}:
        require_string(params, "thread_id")
    if method in {"turn/start", "turn/steer", "turn/interrupt", "review/start"}:
        require_string(params, "thread_id")
    if method == "turn/start":
        require_string(params, "prompt")
    if method == "turn/steer":
        require_string(params, "input")


def validate_response_shape(response: dict[str, Any]) -> None:
    if response.get("jsonrpc") != "2.0":
        raise AppServerRequestError("response jsonrpc must be 2.0")
    if "error" in response:
        raise AppServerRequestError(f"App Server error response: {response['error']}")
    if "result" not in response:
        raise AppServerRequestError("response must include result")
    if not isinstance(response["result"], dict):
        raise AppServerRequestError("response result must be an object")


def require_string(params: dict[str, Any], key: str) -> None:
    value = params.get(key)
    if not isinstance(value, str) or not value:
        raise AppServerRequestError(f"{key} must be a non-empty string")


@dataclass
class FakeAppServer:
    """Tiny in-memory App Server harness for controller tests."""

    next_thread_number: int = 1
    next_turn_number: int = 1
    threads: dict[str, dict[str, Any]] = field(default_factory=dict)
    turns: dict[str, dict[str, Any]] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def handle(self, request: dict[str, Any]) -> dict[str, Any]:
        validate_request_shape(request)
        method = request["method"]
        params = request["params"]
        if method == "thread/list":
            return self.response(request, {"threads": list(self.threads.values())})
        if method == "thread/start":
            thread_id = self._new_thread_id()
            thread = {
                "thread_id": thread_id,
                "status": "idle",
                "archived": False,
                "goal": params.get("goal"),
                "name": params.get("name"),
            }
            self.threads[thread_id] = thread
            self.events.append({"type": "thread/started", "thread_id": thread_id})
            return self.response(request, {"thread_id": thread_id, "thread": thread})
        if method in {"thread/read", "thread/resume"}:
            thread = self.require_thread(params["thread_id"])
            return self.response(request, {"thread": thread})
        if method == "thread/fork":
            parent = self.require_thread(params["thread_id"])
            thread_id = self._new_thread_id()
            thread = {
                "thread_id": thread_id,
                "status": "idle",
                "archived": False,
                "forked_from": parent["thread_id"],
                "goal": params.get("goal", parent.get("goal")),
                "name": params.get("name"),
            }
            self.threads[thread_id] = thread
            self.events.append({"type": "thread/started", "thread_id": thread_id, "forked_from": parent["thread_id"]})
            return self.response(request, {"thread_id": thread_id, "thread": thread})
        if method == "thread/archive":
            thread = self.require_thread(params["thread_id"])
            thread["archived"] = True
            thread["status"] = "archived"
            self.events.append({"type": "thread/archived", "thread_id": thread["thread_id"]})
            return self.response(request, {"thread": thread})
        if method == "turn/start":
            thread = self.require_thread(params["thread_id"])
            turn_id = self._new_turn_id()
            turn = {
                "turn_id": turn_id,
                "thread_id": thread["thread_id"],
                "status": "completed",
                "prompt": params["prompt"],
                "output_schema": params.get("outputSchema"),
            }
            self.turns[turn_id] = turn
            thread["status"] = "idle"
            self.events.append({"type": "turn/started", "thread_id": thread["thread_id"], "turn_id": turn_id})
            self.events.append({"type": "turn/completed", "thread_id": thread["thread_id"], "turn_id": turn_id})
            return self.response(request, {"turn_id": turn_id, "turn": turn})
        if method == "turn/steer":
            thread = self.require_thread(params["thread_id"])
            self.events.append({"type": "turn/steered", "thread_id": thread["thread_id"], "input": params["input"]})
            return self.response(request, {"ok": True})
        if method == "turn/interrupt":
            thread = self.require_thread(params["thread_id"])
            thread["status"] = "idle"
            self.events.append({"type": "turn/interrupted", "thread_id": thread["thread_id"]})
            return self.response(request, {"ok": True})
        if method == "review/start":
            thread = self.require_thread(params["thread_id"])
            self.events.append({"type": "review/started", "thread_id": thread["thread_id"]})
            return self.response(request, {"review_id": f"rev_{thread['thread_id']}"})
        raise AppServerRequestError(f"unimplemented fake method: {method}")

    def require_thread(self, thread_id: str) -> dict[str, Any]:
        try:
            return self.threads[thread_id]
        except KeyError as exc:
            raise AppServerRequestError(f"unknown thread_id: {thread_id}") from exc

    def response(self, request: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        response: dict[str, Any] = {"jsonrpc": "2.0", "result": result}
        if "id" in request:
            response["id"] = request["id"]
        return response

    def _new_thread_id(self) -> str:
        thread_id = f"thr_fake_{self.next_thread_number}"
        self.next_thread_number += 1
        return thread_id

    def _new_turn_id(self) -> str:
        turn_id = f"turn_fake_{self.next_turn_number}"
        self.next_turn_number += 1
        return turn_id


def run_thread_turn_review_archive_flow(
    client: AppServerClient,
    *,
    name: str,
    prompt: str,
    output_schema: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Run the minimal managed-agent App Server lifecycle proof."""

    started = client.call("thread/start", {"name": name, "goal": "managed-agents lifecycle smoke"}, request_id="start")
    thread_id = started["result"]["thread_id"]
    turn_params: dict[str, Any] = {"thread_id": thread_id, "prompt": prompt}
    if output_schema is not None:
        turn_params["outputSchema"] = output_schema
    turn = client.call("turn/start", turn_params, request_id="turn")
    review = client.call("review/start", {"thread_id": thread_id}, request_id="review")
    archived = client.call("thread/archive", {"thread_id": thread_id}, request_id="archive")
    events = client.drain_events()
    return {
        "thread_id": thread_id,
        "turn_id": turn["result"]["turn_id"],
        "review_id": review["result"]["review_id"],
        "archived": bool(archived["result"]["thread"].get("archived")),
        "events": events,
    }


def run_thread_read_fork_interrupt_archive_flow(
    client: AppServerClient,
    *,
    name: str,
    prompt: str,
    output_schema: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Run the expanded phase4 App Server lifecycle proof."""

    started = client.call("thread/start", {"name": name, "goal": "managed-agents phase4 smoke"}, request_id="start")
    thread_id = started["result"]["thread_id"]
    read = client.call("thread/read", {"thread_id": thread_id}, request_id="read")
    turn_params: dict[str, Any] = {"thread_id": thread_id, "prompt": prompt}
    if output_schema is not None:
        turn_params["outputSchema"] = output_schema
    turn = client.call("turn/start", turn_params, request_id="turn")
    client.call("turn/steer", {"thread_id": thread_id, "input": "phase4 smoke steer"}, request_id="steer")
    interrupted = client.call("turn/interrupt", {"thread_id": thread_id}, request_id="interrupt")
    forked = client.call("thread/fork", {"thread_id": thread_id, "name": f"{name}-fork"}, request_id="fork")
    forked_thread_id = forked["result"]["thread_id"]
    archived_parent = client.call("thread/archive", {"thread_id": thread_id}, request_id="archive-parent")
    client.call("thread/archive", {"thread_id": forked_thread_id}, request_id="archive-fork")
    events = client.drain_events()
    return {
        "thread_id": thread_id,
        "read_thread_id": read["result"]["thread"]["thread_id"],
        "turn_id": turn["result"]["turn_id"],
        "forked_thread_id": forked_thread_id,
        "interrupted": bool(interrupted["result"].get("ok")),
        "archived": bool(archived_parent["result"]["thread"].get("archived")),
        "events": events,
    }
