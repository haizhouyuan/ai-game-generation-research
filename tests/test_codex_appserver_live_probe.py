import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "codex_appserver_live_probe.py"


def load_probe_module():
    spec = importlib.util.spec_from_file_location("codex_appserver_live_probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeTransport:
    def __init__(self, incoming):
        self.incoming = list(incoming)
        self.sent = []
        self.closed = False

    def send(self, message):
        self.sent.append(message)

    def receive(self, timeout_seconds):
        if not self.incoming:
            raise TimeoutError("fake timeout")
        next_message = self.incoming.pop(0)
        if isinstance(next_message, BaseException):
            raise next_message
        return next_message

    def close(self):
        self.closed = True


def response(request_id, result=None):
    return {"id": request_id, "result": {} if result is None else result}


def test_build_request_uses_raw_v2_shape_without_jsonrpc():
    probe = load_probe_module()

    message = probe.build_request("thread/read", {"threadId": "thr_1", "includeTurns": False}, "read-1")

    assert message == {
        "id": "read-1",
        "method": "thread/read",
        "params": {"threadId": "thr_1", "includeTurns": False},
    }
    assert "jsonrpc" not in message


def test_client_collects_notifications_until_matching_response():
    probe = load_probe_module()
    transport = FakeTransport(
        [
            {"method": "thread/started", "params": {"thread": {"id": "thr_1"}}},
            response("read-1", {"thread": {"id": "thr_1"}}),
        ]
    )
    client = probe.AppServerLiveClient(transport)

    result = client.request("thread/read", {"threadId": "thr_1"}, request_id="read-1")

    assert transport.sent == [{"id": "read-1", "method": "thread/read", "params": {"threadId": "thr_1"}}]
    assert result.response == response("read-1", {"thread": {"id": "thr_1"}})
    assert result.notifications == [{"method": "thread/started", "params": {"thread": {"id": "thr_1"}}}]


def test_client_preserves_unmatched_responses_for_later_requests():
    probe = load_probe_module()
    transport = FakeTransport(
        [
            response("second", {"ok": 2}),
            response("first", {"ok": 1}),
        ]
    )
    client = probe.AppServerLiveClient(transport)

    first = client.request("noop/first", {}, request_id="first")
    second = client.request("noop/second", {}, request_id="second")

    assert first.response["result"] == {"ok": 1}
    assert second.response["result"] == {"ok": 2}


def test_review_start_request_uses_custom_target_and_thread_id():
    probe = load_probe_module()
    transport = FakeTransport(
        [
            response(
                "review-start",
                {
                    "reviewThreadId": "thr_parent",
                    "turn": {"id": "turn_review", "status": "inProgress", "items": []},
                },
            ),
        ]
    )
    client = probe.AppServerLiveClient(transport)

    result = client.request(
        "review/start",
        {
            "threadId": "thr_parent",
            "target": {"type": "custom", "instructions": "review this disposable probe"},
            "delivery": "inline",
        },
        request_id="review-start",
    )

    assert transport.sent == [
        {
            "id": "review-start",
            "method": "review/start",
            "params": {
                "threadId": "thr_parent",
                "target": {"type": "custom", "instructions": "review this disposable probe"},
                "delivery": "inline",
            },
        }
    ]
    assert result.response["result"]["reviewThreadId"] == "thr_parent"
    assert result.response["result"]["turn"]["id"] == "turn_review"


def test_metadata_lifecycle_does_not_start_turn_by_default(tmp_path):
    probe = load_probe_module()
    transport = FakeTransport(
        [
            response("initialize", {"serverInfo": {"name": "fake-codex"}}),
            response("thread-start", {"thread": {"id": "thr_parent", "ephemeral": False, "cwd": str(tmp_path)}}),
            response("thread-read", {"thread": {"id": "thr_parent", "turns": []}}),
            response("thread-fork", {"thread": {"id": "thr_child", "forkedFromId": "thr_parent"}}),
            response("archive-parent", {}),
            response("archive-fork", {}),
        ]
    )
    client = probe.AppServerLiveClient(transport)

    evidence = probe.run_metadata_lifecycle(client, cwd=tmp_path, include_turn=False)

    methods = [message["method"] for message in transport.sent]
    assert methods == [
        "initialize",
        "thread/start",
        "thread/read",
        "thread/fork",
        "thread/archive",
        "thread/archive",
    ]
    assert all(message["method"] != "turn/start" for message in transport.sent)
    assert transport.sent[1]["params"]["cwd"] == str(tmp_path)
    assert transport.sent[1]["params"]["ephemeral"] is False
    assert transport.sent[1]["params"]["approvalPolicy"] == "never"
    assert transport.sent[1]["params"]["sandbox"] == "read-only"
    assert transport.sent[2]["params"] == {"threadId": "thr_parent", "includeTurns": False}
    assert transport.sent[3]["params"]["ephemeral"] is False
    assert evidence["status"] == "DONE"
    assert evidence["includeTurn"] is False
    assert evidence["parentThreadId"] == "thr_parent"
    assert evidence["forkedThreadId"] == "thr_child"
    assert evidence["turnStarted"] is False


def test_include_turn_adds_turn_start_before_archive(tmp_path):
    probe = load_probe_module()
    transport = FakeTransport(
        [
            response("initialize", {}),
            response("thread-start", {"thread": {"id": "thr_parent"}}),
            response("turn-start", {"turn": {"id": "turn_1"}}),
            {"method": "turn/started", "params": {"threadId": "thr_parent", "turn": {"id": "turn_1"}}},
            response("turn-interrupt", {}),
            response("thread-read-after-interrupt", {"thread": {"id": "thr_parent", "turns": []}}),
            response("thread-fork", {"thread": {"id": "thr_child"}}),
            response("archive-parent", {}),
            response("archive-fork", {}),
        ]
    )
    client = probe.AppServerLiveClient(transport)

    evidence = probe.run_metadata_lifecycle(client, cwd=tmp_path, include_turn=True, turn_input="say hi")

    turn_messages = [message for message in transport.sent if message["method"] == "turn/start"]
    assert len(turn_messages) == 1
    assert turn_messages[0]["params"]["threadId"] == "thr_parent"
    assert turn_messages[0]["params"]["input"] == [{"type": "text", "text": "say hi"}]
    assert evidence["turnStarted"] is True
    assert evidence["turnInterrupted"] is True
    assert evidence["turnId"] == "turn_1"


def test_main_metadata_only_writes_evidence_with_fake_transport(tmp_path):
    probe = load_probe_module()
    out_path = tmp_path / "evidence.json"
    transport = FakeTransport(
        [
            response("initialize", {}),
            response("thread-start", {"thread": {"id": "thr_parent"}}),
            response("thread-read", {"thread": {"id": "thr_parent"}}),
            response("thread-fork", {"thread": {"id": "thr_child"}}),
            response("archive-parent", {}),
            response("archive-fork", {}),
        ]
    )

    exit_code = probe.main(
        ["--metadata-only", "--cwd", str(tmp_path), "--out", str(out_path)],
        transport_factory=lambda _command: transport,
    )

    assert exit_code == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["status"] == "DONE"
    assert payload["includeTurn"] is False
    assert [message["method"] for message in transport.sent if message["method"].startswith("turn/")] == []


def test_main_requires_metadata_only_for_live_lifecycle(tmp_path):
    probe = load_probe_module()

    with pytest.raises(SystemExit) as exc_info:
        probe.main(["--cwd", str(tmp_path), "--out", str(tmp_path / "evidence.json")])

    assert exc_info.value.code == 2
