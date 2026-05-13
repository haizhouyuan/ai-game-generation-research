"""Deterministic scheduler policy for managed Codex tasks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DISPATCHABLE_LANE_STATES = {"enabled"}
DISPATCHABLE_TASK_STATES = {"queued", "needs_retry"}
STOPPING_WORKER_STATUSES = {"blocked", "needs_human", "failed"}


@dataclass(frozen=True)
class DispatchDecision:
    allowed: bool
    reason: str


def can_dispatch(
    *,
    lane: dict[str, Any],
    task: dict[str, Any],
    active_lane_count: int = 0,
    active_repo_count: int = 0,
    now: datetime | None = None,
) -> DispatchDecision:
    """Return whether a task may be dispatched right now."""

    now = now or datetime.now(timezone.utc)

    lane_state = lane.get("state")
    if lane_state not in DISPATCHABLE_LANE_STATES:
        return DispatchDecision(False, f"lane_not_enabled:{lane_state}")

    concurrency = int(lane.get("concurrency", 1))
    if concurrency <= 0:
        return DispatchDecision(False, "lane_concurrency_zero")
    if active_lane_count >= concurrency:
        return DispatchDecision(False, "lane_concurrency_limit")

    if lane.get("repo_write_lock") and active_repo_count > 0:
        return DispatchDecision(False, "repo_write_lock_active")

    task_state = task.get("state")
    if task_state not in DISPATCHABLE_TASK_STATES:
        return DispatchDecision(False, f"task_not_dispatchable:{task_state}")

    if task.get("thread_id") and task.get("current_turn_id"):
        return DispatchDecision(False, "task_already_has_active_turn")

    if task.get("needs_human_reason"):
        return DispatchDecision(False, "needs_human")

    if task.get("blocked_reason"):
        return DispatchDecision(False, "blocked")

    retry_count = int(task.get("retry_count") or 0)
    max_retries = int(task.get("max_retries") or 0)
    if task_state == "needs_retry" and retry_count > max_retries:
        return DispatchDecision(False, "retry_limit_exceeded")

    next_dispatch_at = parse_time(task.get("next_dispatch_at"))
    if next_dispatch_at and next_dispatch_at > now:
        return DispatchDecision(False, "cooldown_active")

    last_worker_status = task.get("last_worker_status")
    if last_worker_status in STOPPING_WORKER_STATUSES and task_state != "needs_retry":
        return DispatchDecision(False, f"last_worker_status_stops:{last_worker_status}")

    next_action = task.get("next_action")
    if isinstance(next_action, dict):
        recommended_state = next_action.get("recommended_state")
        if recommended_state in {"wait_for_human", "stop", "review", "archive"}:
            return DispatchDecision(False, f"next_action_blocks:{recommended_state}")

    return DispatchDecision(True, "dispatch_allowed")


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise ValueError(f"unsupported time value: {value!r}")
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed

