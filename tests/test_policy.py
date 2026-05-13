from datetime import datetime, timezone

from managed_codex.policy import can_dispatch

NOW = datetime(2026, 5, 12, 12, 0, tzinfo=timezone.utc)


def lane(**overrides):
    value = {
        "lane_id": "controller-core",
        "state": "enabled",
        "concurrency": 1,
        "repo_write_lock": False,
    }
    value.update(overrides)
    return value


def task(**overrides):
    value = {
        "task_id": "controller-core-phase2",
        "state": "queued",
        "retry_count": 0,
        "max_retries": 1,
    }
    value.update(overrides)
    return value


def test_allows_simple_queued_task():
    decision = can_dispatch(lane=lane(), task=task(), now=NOW)
    assert decision.allowed
    assert decision.reason == "dispatch_allowed"


def test_blocks_paused_lane():
    decision = can_dispatch(lane=lane(state="paused"), task=task(), now=NOW)
    assert not decision.allowed
    assert decision.reason == "lane_not_enabled:paused"


def test_blocks_disabled_lane():
    decision = can_dispatch(lane=lane(state="disabled"), task=task(), now=NOW)
    assert not decision.allowed
    assert decision.reason == "lane_not_enabled:disabled"


def test_blocks_lane_concurrency_limit():
    decision = can_dispatch(lane=lane(concurrency=1), task=task(), active_lane_count=1, now=NOW)
    assert not decision.allowed
    assert decision.reason == "lane_concurrency_limit"


def test_blocks_repo_write_lock():
    decision = can_dispatch(lane=lane(repo_write_lock=True), task=task(), active_repo_count=1, now=NOW)
    assert not decision.allowed
    assert decision.reason == "repo_write_lock_active"


def test_blocks_non_queued_task():
    decision = can_dispatch(lane=lane(), task=task(state="running"), now=NOW)
    assert not decision.allowed
    assert decision.reason == "task_not_dispatchable:running"


def test_blocks_active_turn_duplicate():
    decision = can_dispatch(lane=lane(), task=task(thread_id="thr_1", current_turn_id="turn_1"), now=NOW)
    assert not decision.allowed
    assert decision.reason == "task_already_has_active_turn"


def test_blocks_needs_human():
    decision = can_dispatch(lane=lane(), task=task(needs_human_reason="approve Unity download"), now=NOW)
    assert not decision.allowed
    assert decision.reason == "needs_human"


def test_blocks_blocked_reason():
    decision = can_dispatch(lane=lane(), task=task(blocked_reason="Unity not installed"), now=NOW)
    assert not decision.allowed
    assert decision.reason == "blocked"


def test_blocks_retry_limit():
    decision = can_dispatch(lane=lane(), task=task(state="needs_retry", retry_count=2, max_retries=1), now=NOW)
    assert not decision.allowed
    assert decision.reason == "retry_limit_exceeded"


def test_allows_retry_within_limit():
    decision = can_dispatch(lane=lane(), task=task(state="needs_retry", retry_count=1, max_retries=1), now=NOW)
    assert decision.allowed


def test_blocks_cooldown():
    decision = can_dispatch(lane=lane(), task=task(next_dispatch_at="2026-05-12T12:01:00Z"), now=NOW)
    assert not decision.allowed
    assert decision.reason == "cooldown_active"


def test_blocks_worker_result_stop_states():
    for status in ["blocked", "needs_human", "failed"]:
        decision = can_dispatch(lane=lane(), task=task(last_worker_status=status), now=NOW)
        assert not decision.allowed
        assert decision.reason == f"last_worker_status_stops:{status}"


def test_blocks_next_action_terminal_states():
    for recommended_state in ["wait_for_human", "stop", "review", "archive"]:
        decision = can_dispatch(lane=lane(), task=task(next_action={"recommended_state": recommended_state}), now=NOW)
        assert not decision.allowed
        assert decision.reason == f"next_action_blocks:{recommended_state}"

