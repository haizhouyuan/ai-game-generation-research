"""SQLite registry access for managed Codex."""

from __future__ import annotations

import json
import sqlite3
from importlib import resources
from pathlib import Path
from typing import Any

from .config import ManagedConfig


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def schema_sql() -> str:
    return resources.files("managed_codex").joinpath("schema.sql").read_text(encoding="utf-8")


def init_registry(db_path: Path, config: ManagedConfig) -> None:
    with connect(db_path) as conn:
        conn.executescript(schema_sql())
        migrate_registry(conn)
        seed_repos(conn, [repo.model_dump() for repo in config.repos])
        seed_lanes(conn, [lane.model_dump() for lane in config.lanes])
        seed_tasks(conn, [task.model_dump() for task in config.tasks])
        seed_capabilities(conn, [capability.model_dump() for capability in config.capabilities])
        seed_controller_issues(conn, [issue.model_dump() for issue in config.controller_issues])
        conn.execute(
            """
            INSERT INTO registry_meta(key, value, updated_at)
            VALUES('schema_version', '1', CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
            """
        )


def migrate_registry(conn: sqlite3.Connection) -> None:
    """Apply lightweight additive migrations for existing local registries."""

    ensure_columns(
        conn,
        "tasks",
        {
            "last_worker_status": "TEXT",
            "last_error": "TEXT",
            "blocked_reason": "TEXT",
            "needs_human_reason": "TEXT",
        },
    )
    ensure_columns(
        conn,
        "downloads",
        {
            "command": "TEXT",
            "no_proxy_proof": "TEXT",
            "status": "TEXT NOT NULL DEFAULT 'planned'",
        },
    )


def ensure_columns(conn: sqlite3.Connection, table_name: str, columns: dict[str, str]) -> None:
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
    for column_name, definition in columns.items():
        if column_name not in existing:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def seed_repos(conn: sqlite3.Connection, repos: list[dict[str, Any]]) -> None:
    for repo in repos:
        conn.execute(
            """
            INSERT INTO repos(repo_id, path, role, default_branch, updated_at)
            VALUES(?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(repo_id) DO UPDATE SET
              path=excluded.path,
              role=excluded.role,
              default_branch=excluded.default_branch,
              updated_at=CURRENT_TIMESTAMP
            """,
            (repo["repo_id"], repo["path"], repo.get("role", ""), repo.get("default_branch", "main")),
        )


def seed_lanes(conn: sqlite3.Connection, lanes: list[dict[str, Any]]) -> None:
    for lane in lanes:
        conn.execute(
            """
            INSERT INTO lanes(lane_id, title, state, auto_continue, concurrency, owner, safety_policy, updated_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(lane_id) DO UPDATE SET
              title=excluded.title,
              state=excluded.state,
              auto_continue=excluded.auto_continue,
              concurrency=excluded.concurrency,
              owner=excluded.owner,
              safety_policy=excluded.safety_policy,
              updated_at=CURRENT_TIMESTAMP
            """,
            (
                lane["lane_id"],
                lane["title"],
                lane["state"],
                1 if lane.get("auto_continue", False) else 0,
                int(lane.get("concurrency", 1)),
                lane.get("owner", ""),
                lane.get("safety_policy", ""),
            ),
        )


def seed_tasks(conn: sqlite3.Connection, tasks: list[dict[str, Any]]) -> None:
    for task in tasks:
        conn.execute(
            """
            INSERT INTO tasks(task_id, lane_id, repo_id, title, goal, done_criteria, state, priority, updated_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(task_id) DO UPDATE SET
              lane_id=excluded.lane_id,
              repo_id=excluded.repo_id,
              title=excluded.title,
              goal=excluded.goal,
              done_criteria=excluded.done_criteria,
              state=excluded.state,
              priority=excluded.priority,
              updated_at=CURRENT_TIMESTAMP
            """,
            (
                task["task_id"],
                task["lane_id"],
                task["repo_id"],
                task["title"],
                task.get("goal", ""),
                task.get("done_criteria", ""),
                task.get("state", "queued"),
                int(task.get("priority", 0)),
            ),
        )


def seed_capabilities(conn: sqlite3.Connection, capabilities: list[dict[str, Any]]) -> None:
    for capability in capabilities:
        conn.execute(
            """
            INSERT INTO capabilities(
              capability_id, title, category, status, lane_id, summary,
              evidence_paths_json, commands_json, inputs_json, outputs_json,
              limitations_json, next_steps_json, updated_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(capability_id) DO UPDATE SET
              title=excluded.title,
              category=excluded.category,
              status=excluded.status,
              lane_id=excluded.lane_id,
              summary=excluded.summary,
              evidence_paths_json=excluded.evidence_paths_json,
              commands_json=excluded.commands_json,
              inputs_json=excluded.inputs_json,
              outputs_json=excluded.outputs_json,
              limitations_json=excluded.limitations_json,
              next_steps_json=excluded.next_steps_json,
              updated_at=CURRENT_TIMESTAMP
            """,
            (
                capability["capability_id"],
                capability["title"],
                capability["category"],
                capability["status"],
                capability["lane_id"],
                capability["summary"],
                json.dumps(capability.get("evidence_paths", []), ensure_ascii=True),
                json.dumps(capability.get("commands", []), ensure_ascii=True),
                json.dumps(capability.get("inputs", []), ensure_ascii=True),
                json.dumps(capability.get("outputs", []), ensure_ascii=True),
                json.dumps(capability.get("limitations", []), ensure_ascii=True),
                json.dumps(capability.get("next_steps", []), ensure_ascii=True),
            ),
        )


def seed_controller_issues(conn: sqlite3.Connection, issues: list[dict[str, Any]]) -> None:
    for issue in issues:
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
            (
                issue["issue_id"],
                issue["title"],
                issue["severity"],
                issue["state"],
                issue.get("lane_id"),
                issue.get("task_id"),
                issue.get("symptom", ""),
                issue.get("root_cause", ""),
                issue.get("improvement", ""),
                issue.get("evidence", ""),
            ),
        )
