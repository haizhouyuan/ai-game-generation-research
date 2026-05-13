"""Registry operations that turn worker outputs into durable controller state."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

from .worker_result import validate_worker_result
from .workflow import load_workflow_summary


def record_worker_result(conn: sqlite3.Connection, result_path: Path, schema_path: Path) -> list[str]:
    """Validate and persist a WORKER_RESULT.

    Returns validation errors. When errors are present, the registry is not mutated.
    """

    errors = validate_worker_result(result_path, schema_path)
    if errors:
        return errors

    result = json.loads(result_path.read_text(encoding="utf-8"))
    task_id = result["task_id"]
    lane_id = result["lane_id"]

    conn.execute(
        """
        UPDATE tasks
        SET last_summary=?,
            last_worker_status=?,
            needs_human_reason=?,
            blocked_reason=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE task_id=?
        """,
        (
            result["summary"],
            result["status"],
            result.get("human_question") if result.get("needs_human") else None,
            "\n".join(result.get("blockers", [])) or None,
            task_id,
        ),
    )

    for evidence in result.get("evidence", []):
        conn.execute(
            """
            INSERT INTO evidence_items(task_id, lane_id, evidence_type, path_or_url, notes)
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                task_id,
                lane_id,
                evidence.get("type", "other"),
                evidence["path_or_url"],
                evidence.get("notes", ""),
            ),
        )

    for changed_file in result.get("files_changed", []):
        conn.execute(
            """
            INSERT INTO artifacts(task_id, lane_id, type, path_or_url, validation_status, notes)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                lane_id,
                f"file:{changed_file.get('change_type', 'unknown')}",
                changed_file["path"],
                "unknown",
                changed_file.get("notes", ""),
            ),
        )

    return []


def add_controller_issue(
    conn: sqlite3.Connection,
    *,
    issue_id: str,
    title: str,
    severity: str,
    state: str,
    lane_id: Optional[str],
    task_id: Optional[str],
    symptom: str,
    root_cause: str,
    improvement: str,
    evidence: str,
) -> None:
    conn.execute(
        """
        INSERT INTO controller_issues(
          issue_id, title, severity, state, lane_id, task_id,
          symptom, root_cause, improvement, evidence, updated_at
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(issue_id) DO UPDATE SET
          title=excluded.title,
          severity=excluded.severity,
          state=excluded.state,
          lane_id=excluded.lane_id,
          task_id=excluded.task_id,
          symptom=excluded.symptom,
          root_cause=excluded.root_cause,
          improvement=excluded.improvement,
          evidence=excluded.evidence,
          updated_at=CURRENT_TIMESTAMP
        """,
        (issue_id, title, severity, state, lane_id, task_id, symptom, root_cause, improvement, evidence),
    )


def record_codex_event(conn: sqlite3.Connection, event: dict[str, Any]) -> None:
    """Persist one Codex/App Server event with tolerant field mapping."""

    thread_id = event.get("thread_id") or event.get("threadId")
    turn_id = event.get("turn_id") or event.get("turnId")
    event_type = event.get("type") or event.get("event_type") or event.get("method") or "unknown"
    item_type = event.get("item_type") or event.get("itemType")
    ensure_event_thread(conn, thread_id)
    if thread_id:
        ensure_event_turn(conn, thread_id, turn_id)
    else:
        turn_id = None
    conn.execute(
        """
        INSERT INTO codex_events(thread_id, turn_id, event_type, item_type, payload_json)
        VALUES(?, ?, ?, ?, ?)
        """,
        (thread_id, turn_id, event_type, item_type, json.dumps(event, ensure_ascii=True, sort_keys=True)),
    )


def ensure_event_thread(conn: sqlite3.Connection, thread_id: Optional[str]) -> None:
    if not thread_id:
        return
    conn.execute(
        """
        INSERT INTO threads(thread_id, runtime_status, app_status)
        VALUES(?, 'orphaned_event', 'event-import')
        ON CONFLICT(thread_id) DO UPDATE SET
          last_event_at=CURRENT_TIMESTAMP,
          updated_at=CURRENT_TIMESTAMP
        """,
        (thread_id,),
    )


def ensure_event_turn(conn: sqlite3.Connection, thread_id: str, turn_id: Optional[str]) -> None:
    if not turn_id:
        return
    conn.execute(
        """
        INSERT INTO turns(turn_id, thread_id, state)
        VALUES(?, ?, 'orphaned')
        ON CONFLICT(turn_id) DO UPDATE SET
          updated_at=CURRENT_TIMESTAMP
        """,
        (turn_id, thread_id),
    )


def import_events_jsonl(conn: sqlite3.Connection, path: Path) -> int:
    count = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON event") from exc
        if not isinstance(event, dict):
            raise ValueError(f"{path}:{line_number}: event must be a JSON object")
        record_codex_event(conn, event)
        count += 1
    return count


DOWNLOAD_STATUSES = {"planned", "metadata_only", "needs_approval", "done", "failed", "skipped"}
LARGE_DOWNLOAD_BYTES = 1024 * 1024 * 1024


def record_download(
    conn: sqlite3.Connection,
    *,
    source_url: str,
    task_id: Optional[str] = None,
    retained_path: Optional[str] = None,
    size_bytes: Optional[int] = None,
    sha256: Optional[str] = None,
    command: Optional[str] = None,
    no_proxy_proof: Optional[str] = None,
    status: str = "planned",
    approved_over_1gb: bool = False,
) -> int:
    """Persist governed download metadata without performing a download."""

    status = status.strip()
    if not source_url.strip():
        raise ValueError("source_url is required")
    if status not in DOWNLOAD_STATUSES:
        raise ValueError(f"status must be one of {sorted(DOWNLOAD_STATUSES)}")
    if size_bytes is not None and size_bytes < 0:
        raise ValueError("size_bytes must be non-negative")
    if size_bytes is not None and size_bytes > LARGE_DOWNLOAD_BYTES and not approved_over_1gb:
        if status in {"planned", "metadata_only"}:
            status = "needs_approval"
        elif status == "done":
            raise ValueError("downloads over 1GiB cannot be recorded as done without approved_over_1gb=true")
    if size_bytes is not None and size_bytes <= LARGE_DOWNLOAD_BYTES and status == "needs_approval":
        raise ValueError(
            "needs_approval status is only valid when size_bytes is over 1GiB or size is unknown"
        )
    if status == "done":
        missing_done_fields = [
            name
            for name, value in {
                "retained_path": retained_path,
                "size_bytes": size_bytes,
                "sha256": sha256,
                "command": command,
                "no_proxy_proof": no_proxy_proof,
            }.items()
            if value in (None, "")
        ]
        if missing_done_fields:
            raise ValueError(f"done downloads require {', '.join(missing_done_fields)}")

    cursor = conn.execute(
        """
        INSERT INTO downloads(
          task_id, source_url, retained_path, size_bytes, sha256,
          command, no_proxy_proof, status
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_id,
            source_url,
            retained_path,
            size_bytes,
            sha256,
            command,
            no_proxy_proof,
            status,
        ),
    )
    return int(cursor.lastrowid)


def recent_downloads(conn: sqlite3.Connection, limit: int = 10) -> list[dict[str, Any]]:
    if limit < 1:
        raise ValueError("limit must be positive")
    return rows_as_dicts(
        conn.execute(
            """
            SELECT download_id, task_id, source_url, retained_path, size_bytes, sha256, status, created_at
            FROM downloads
            ORDER BY created_at DESC, download_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    )


def dashboard_snapshot(
    conn: sqlite3.Connection,
    root: Path,
    capability_max_age_days: Optional[int] = None,
) -> dict[str, Any]:
    """Return a compact operator-facing snapshot of controller state."""

    if capability_max_age_days is None:
        missing_capabilities = capability_missing_paths(conn, root)
        stale_capabilities: list[tuple[str, str]] = []
    else:
        capability_findings = capability_evidence_path_findings(
            conn,
            root,
            max_age_days=capability_max_age_days,
        )
        missing_capabilities = capability_findings["missing"]
        stale_capabilities = capability_findings["stale"]

    return {
        "workflow": load_workflow_summary(root / "WORKFLOW.md"),
        "lane_counts": rows_as_dicts(
            conn.execute("SELECT state, COUNT(*) AS count FROM lanes GROUP BY state ORDER BY state").fetchall()
        ),
        "task_counts": rows_as_dicts(
            conn.execute("SELECT state, COUNT(*) AS count FROM tasks GROUP BY state ORDER BY state").fetchall()
        ),
        "active_tasks": rows_as_dicts(
            conn.execute(
                """
                SELECT task_id, lane_id, state, priority, title
                FROM tasks
                WHERE state IN (
                  'queued', 'dispatching', 'planning', 'running', 'blocked',
                  'waiting_user', 'waiting_approval', 'needs_retry'
                )
                ORDER BY priority DESC, created_at ASC
                LIMIT 20
                """
            ).fetchall()
        ),
        "queued_tasks": task_rows_by_states(conn, ["queued"], limit=20),
        "blocked_tasks": task_rows_by_states(conn, ["blocked"], limit=20),
        "completed_tasks": task_rows_by_states(conn, ["task_complete"], limit=20),
        "needs_human_items": needs_human_items(conn),
        "risky_items": risky_items(conn, missing_capabilities, stale_capabilities),
        "open_issues": rows_as_dicts(
            conn.execute(
                """
                SELECT issue_id, severity, lane_id, task_id, title
                FROM controller_issues
                WHERE state IN ('open', 'triaged')
                ORDER BY severity DESC, created_at DESC
                LIMIT 20
                """
            ).fetchall()
        ),
        "capability_counts": rows_as_dicts(
            conn.execute(
                "SELECT status, COUNT(*) AS count FROM capabilities GROUP BY status ORDER BY status"
            ).fetchall()
        ),
        "missing_capability_paths": [
            {"capability_id": capability_id, "path": path}
            for capability_id, path in missing_capabilities
        ],
        "capability_stale_max_age_days": capability_max_age_days,
        "stale_capability_paths": [
            {"capability_id": capability_id, "path": path}
            for capability_id, path in stale_capabilities
        ],
        "recent_events": rows_as_dicts(
            conn.execute(
                """
                SELECT thread_id, turn_id, event_type, item_type, observed_at
                FROM codex_events
                ORDER BY observed_at DESC, event_id DESC
                LIMIT 10
                """
            ).fetchall()
        ),
        "recent_evidence": rows_as_dicts(
            conn.execute(
                """
                SELECT task_id, lane_id, evidence_type, path_or_url, notes
                FROM evidence_items
                ORDER BY created_at DESC, evidence_id DESC
                LIMIT 10
                """
            ).fetchall()
        ),
        "recent_downloads": recent_downloads(conn),
    }


def task_rows_by_states(conn: sqlite3.Connection, states: list[str], limit: int = 20) -> list[dict[str, Any]]:
    placeholders = ", ".join("?" for _ in states)
    return rows_as_dicts(
        conn.execute(
            f"""
            SELECT task_id, lane_id, state, priority, title, blocked_reason, needs_human_reason
            FROM tasks
            WHERE state IN ({placeholders})
            ORDER BY priority DESC, updated_at DESC, created_at ASC
            LIMIT ?
            """,
            (*states, limit),
        ).fetchall()
    )


def needs_human_items(conn: sqlite3.Connection, limit: int = 20) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    tasks = conn.execute(
        """
        SELECT task_id, lane_id, state, priority, title, needs_human_reason, blocked_reason
        FROM tasks
        WHERE state IN ('waiting_user', 'waiting_approval')
           OR needs_human_reason IS NOT NULL
           OR last_worker_status = 'needs_human'
        ORDER BY priority DESC, updated_at DESC, created_at ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    for task in rows_as_dicts(tasks):
        reason = task.get("needs_human_reason") or task.get("blocked_reason") or task["state"]
        items.append(
            {
                "source": "task",
                "id": task["task_id"],
                "lane_id": task["lane_id"],
                "task_id": task["task_id"],
                "state": task["state"],
                "priority": task["priority"],
                "title": task["title"],
                "reason": reason,
            }
        )

    remaining = max(limit - len(items), 0)
    if remaining:
        downloads = conn.execute(
            """
            SELECT download_id, task_id, source_url, size_bytes, status, created_at
            FROM downloads
            WHERE status = 'needs_approval'
            ORDER BY created_at DESC, download_id DESC
            LIMIT ?
            """,
            (remaining,),
        ).fetchall()
        for download in rows_as_dicts(downloads):
            items.append(
                {
                    "source": "download",
                    "id": str(download["download_id"]),
                    "task_id": download["task_id"],
                    "state": download["status"],
                    "title": download["source_url"],
                    "reason": "download requires explicit approval before it can be completed",
                    "size_bytes": download["size_bytes"],
                }
            )
    return items


def risky_items(
    conn: sqlite3.Connection,
    missing_capabilities: list[tuple[str, str]],
    stale_capabilities: list[tuple[str, str]],
    limit: int = 20,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    issue_rows = conn.execute(
        """
        SELECT issue_id, severity, lane_id, task_id, title
        FROM controller_issues
        WHERE state IN ('open', 'triaged')
        ORDER BY severity DESC, updated_at DESC, created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    for issue in rows_as_dicts(issue_rows):
        items.append(
            {
                "source": "controller_issue",
                "id": issue["issue_id"],
                "severity": issue["severity"],
                "lane_id": issue["lane_id"],
                "task_id": issue["task_id"],
                "title": issue["title"],
                "reason": "open controller issue",
            }
        )

    remaining = max(limit - len(items), 0)
    if remaining:
        task_rows = conn.execute(
            """
            SELECT task_id, lane_id, state, priority, title, blocked_reason, last_error
            FROM tasks
            WHERE state IN ('blocked', 'failed', 'needs_retry', 'interrupted')
            ORDER BY priority DESC, updated_at DESC, created_at ASC
            LIMIT ?
            """,
            (remaining,),
        ).fetchall()
        for task in rows_as_dicts(task_rows):
            items.append(
                {
                    "source": "task",
                    "id": task["task_id"],
                    "lane_id": task["lane_id"],
                    "task_id": task["task_id"],
                    "state": task["state"],
                    "priority": task["priority"],
                    "title": task["title"],
                    "reason": task.get("blocked_reason") or task.get("last_error") or task["state"],
                }
            )

    remaining = max(limit - len(items), 0)
    if remaining:
        capability_rows = conn.execute(
            """
            SELECT capability_id, status, category, lane_id, title, limitations_json, next_steps_json
            FROM capabilities
            WHERE status IN ('partial', 'blocked')
            ORDER BY status ASC, capability_id ASC
            LIMIT ?
            """,
            (remaining,),
        ).fetchall()
        for capability in rows_as_dicts(capability_rows):
            limitations = decode_json_cell(capability.pop("limitations_json"))
            next_steps = decode_json_cell(capability.pop("next_steps_json"))
            reason = limitations[0] if limitations else capability["status"]
            items.append(
                {
                    "source": "capability",
                    "id": capability["capability_id"],
                    "lane_id": capability["lane_id"],
                    "state": capability["status"],
                    "title": capability["title"],
                    "category": capability["category"],
                    "reason": reason,
                    "next_step": next_steps[0] if next_steps else None,
                }
            )

    remaining = max(limit - len(items), 0)
    for capability_id, path in missing_capabilities[:remaining]:
        items.append(
            {
                "source": "capability_evidence",
                "id": capability_id,
                "state": "missing",
                "title": path,
                "reason": "capability evidence path is missing",
            }
        )

    remaining = max(limit - len(items), 0)
    for capability_id, path in stale_capabilities[:remaining]:
        items.append(
            {
                "source": "capability_evidence",
                "id": capability_id,
                "state": "stale",
                "title": path,
                "reason": "capability evidence path is stale",
            }
        )

    remaining = max(limit - len(items), 0)
    if remaining:
        download_rows = conn.execute(
            """
            SELECT download_id, task_id, source_url, size_bytes, status
            FROM downloads
            WHERE status IN ('needs_approval', 'failed')
            ORDER BY created_at DESC, download_id DESC
            LIMIT ?
            """,
            (remaining,),
        ).fetchall()
        for download in rows_as_dicts(download_rows):
            items.append(
                {
                    "source": "download",
                    "id": str(download["download_id"]),
                    "task_id": download["task_id"],
                    "state": download["status"],
                    "title": download["source_url"],
                    "reason": "download is not safely complete",
                    "size_bytes": download["size_bytes"],
                }
            )
    return items


def rows_as_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def capability_missing_paths(conn: sqlite3.Connection, root: Path) -> list[tuple[str, str]]:
    return capability_evidence_path_findings(conn, root)["missing"]


def capability_evidence_path_findings(
    conn: sqlite3.Connection,
    root: Path,
    max_age_days: Optional[int] = None,
) -> dict[str, list[tuple[str, str]]]:
    if max_age_days is not None and max_age_days < 0:
        raise ValueError("max_age_days must be non-negative")

    missing: list[tuple[str, str]] = []
    stale: list[tuple[str, str]] = []
    cutoff = None
    if max_age_days is not None:
        cutoff = time.time() - (max_age_days * 24 * 60 * 60)

    rows = conn.execute(
        "SELECT capability_id, evidence_paths_json FROM capabilities ORDER BY capability_id"
    ).fetchall()
    for row in rows:
        for path_value in json.loads(row["evidence_paths_json"]):
            if path_value.startswith(("http://", "https://")):
                continue
            path = Path(path_value)
            if not path.is_absolute():
                path = root / path
            if not path.exists():
                missing.append((row["capability_id"], path_value))
                continue
            if cutoff is not None and latest_path_mtime(path) < cutoff:
                stale.append((row["capability_id"], path_value))
    return {"missing": missing, "stale": stale}


def latest_path_mtime(path: Path) -> float:
    latest = path.stat().st_mtime
    if path.is_dir():
        for child in path.rglob("*"):
            child_mtime = child.stat().st_mtime
            if child_mtime > latest:
                latest = child_mtime
    return latest


def decode_json_cell(value: Any) -> Any:
    if value is None:
        return None
    return json.loads(value)
