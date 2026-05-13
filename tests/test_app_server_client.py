from managed_codex.app_server_client import (
    AppServerClient,
    AppServerRequestError,
    FakeAppServer,
    FakeAppServerTransport,
    HttpJsonRpcTransport,
    build_request,
    run_thread_read_fork_interrupt_archive_flow,
    run_thread_turn_review_archive_flow,
    validate_response_shape,
)


def test_builds_valid_thread_start_request():
    request = build_request("thread/start", {"name": "worker", "goal": "test"}, request_id=1)
    assert request["jsonrpc"] == "2.0"
    assert request["method"] == "thread/start"
    assert request["id"] == 1


def test_rejects_unknown_method():
    try:
        build_request("thread/shellCommand", {"command": "date"})
    except AppServerRequestError:
        return
    raise AssertionError("expected AppServerRequestError")


def test_rejects_non_object_params():
    try:
        build_request("thread/list", [])  # type: ignore[arg-type]
    except AppServerRequestError:
        return
    raise AssertionError("expected AppServerRequestError")


def test_rejects_turn_start_without_thread_id():
    try:
        build_request("turn/start", {"prompt": "do work"})
    except AppServerRequestError:
        return
    raise AssertionError("expected AppServerRequestError")


def test_rejects_turn_start_without_prompt():
    try:
        build_request("turn/start", {"thread_id": "thr_1"})
    except AppServerRequestError:
        return
    raise AssertionError("expected AppServerRequestError")


def test_fake_server_thread_turn_archive_flow():
    server = FakeAppServer()
    started = server.handle(build_request("thread/start", {"name": "worker"}, request_id="a"))
    thread_id = started["result"]["thread_id"]

    turn = server.handle(
        build_request(
            "turn/start",
            {
                "thread_id": thread_id,
                "prompt": "Return WORKER_RESULT JSON.",
                "outputSchema": {"type": "object"},
            },
            request_id="b",
        )
    )
    assert turn["result"]["turn"]["thread_id"] == thread_id
    assert turn["result"]["turn"]["output_schema"] == {"type": "object"}

    review = server.handle(build_request("review/start", {"thread_id": thread_id}, request_id="c"))
    assert review["result"]["review_id"] == f"rev_{thread_id}"

    archived = server.handle(build_request("thread/archive", {"thread_id": thread_id}, request_id="d"))
    assert archived["result"]["thread"]["archived"] is True
    assert archived["result"]["thread"]["status"] == "archived"

    event_types = [event["type"] for event in server.events]
    assert event_types == ["thread/started", "turn/started", "turn/completed", "review/started", "thread/archived"]


def test_fake_server_rejects_unknown_thread():
    server = FakeAppServer()
    try:
        server.handle(build_request("thread/read", {"thread_id": "thr_missing"}))
    except AppServerRequestError:
        return
    raise AssertionError("expected AppServerRequestError")


def test_validates_jsonrpc_response_shape():
    validate_response_shape({"jsonrpc": "2.0", "result": {"ok": True}, "id": 1})
    try:
        validate_response_shape({"jsonrpc": "2.0", "error": {"message": "bad"}})
    except AppServerRequestError:
        return
    raise AssertionError("expected AppServerRequestError")


def test_http_transport_rejects_non_local_urls():
    for url in ["https://example.com/rpc", "http://192.168.31.38:8080/rpc"]:
        try:
            HttpJsonRpcTransport(url)
        except AppServerRequestError:
            continue
        raise AssertionError(f"expected AppServerRequestError for {url}")


def test_http_transport_accepts_localhost_urls():
    transport = HttpJsonRpcTransport("http://127.0.0.1:8080/rpc")
    assert transport.url == "http://127.0.0.1:8080/rpc"


def test_client_runs_guarded_thread_turn_review_archive_flow():
    server = FakeAppServer()
    client = AppServerClient(FakeAppServerTransport(server))

    result = run_thread_turn_review_archive_flow(
        client,
        name="phase4-smoke",
        prompt="Return schema-valid WORKER_RESULT JSON.",
        output_schema={"type": "object"},
    )

    assert result["thread_id"] == "thr_fake_1"
    assert result["turn_id"] == "turn_fake_1"
    assert result["review_id"] == "rev_thr_fake_1"
    assert result["archived"] is True
    assert [event["type"] for event in result["events"]] == [
        "thread/started",
        "turn/started",
        "turn/completed",
        "review/started",
        "thread/archived",
    ]


def test_client_runs_phase4_thread_read_fork_steer_interrupt_archive_flow():
    server = FakeAppServer()
    client = AppServerClient(FakeAppServerTransport(server))

    result = run_thread_read_fork_interrupt_archive_flow(
        client,
        name="phase4-expanded-smoke",
        prompt="Return schema-valid WORKER_RESULT JSON.",
    )

    assert result["thread_id"] == "thr_fake_1"
    assert result["forked_thread_id"] == "thr_fake_2"
    assert result["read_thread_id"] == "thr_fake_1"
    assert result["interrupted"] is True
    assert result["archived"] is True
    assert [event["type"] for event in result["events"]] == [
        "thread/started",
        "turn/started",
        "turn/completed",
        "turn/steered",
        "turn/interrupted",
        "thread/started",
        "thread/archived",
        "thread/archived",
    ]
