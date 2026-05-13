import json
import os
import time
from pathlib import Path

from typer.testing import CliRunner

from managed_codex.cli import app
from managed_codex.config import load_config
from managed_codex.db import connect, init_registry
from managed_codex.registry_ops import dashboard_snapshot, import_events_jsonl

ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def init_tmp_registry(tmp_path):
    db_path = tmp_path / "registry.sqlite3"
    config = load_config(ROOT / "config" / "lanes.yaml")
    init_registry(db_path, config)
    return db_path


def test_import_events_jsonl_persists_codex_events(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(
        "\n".join(
            [
                json.dumps({"type": "thread.started", "thread_id": "thread-a", "item_type": "thread"}),
                json.dumps(
                    {
                        "event_type": "turn.completed",
                        "threadId": "thread-a",
                        "turnId": "turn-a",
                        "itemType": "turn",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    with connect(db_path) as conn:
        imported = import_events_jsonl(conn, events_path)
        rows = conn.execute(
            "SELECT thread_id, turn_id, event_type, item_type FROM codex_events ORDER BY event_id"
        ).fetchall()

    assert imported == 2
    assert [dict(row) for row in rows] == [
        {"thread_id": "thread-a", "turn_id": None, "event_type": "thread.started", "item_type": "thread"},
        {"thread_id": "thread-a", "turn_id": "turn-a", "event_type": "turn.completed", "item_type": "turn"},
    ]


def test_dashboard_snapshot_answers_active_work_and_issues(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        snapshot = dashboard_snapshot(conn, ROOT)

    task_counts = {count["state"]: count["count"] for count in snapshot["task_counts"]}
    assert task_counts["task_complete"] >= 16
    assert task_counts["blocked"] >= 1
    assert not any(task["task_id"] == "controller-core-phase4" for task in snapshot["active_tasks"])
    assert not any(task["task_id"] == "controller-core-phase4-live-proof" for task in snapshot["active_tasks"])
    assert any(task["task_id"] == "unity-mcp-001" for task in snapshot["active_tasks"])
    assert not any(task["task_id"] == "threejs-001" for task in snapshot["active_tasks"])
    assert not any(
        issue["issue_id"] == "ctrl-20260513-phase4-live-appserver-proof-gap"
        and issue["task_id"] == "controller-core-phase4-live-proof"
        for issue in snapshot["open_issues"]
    )
    assert snapshot["missing_capability_paths"] == []
    assert snapshot["stale_capability_paths"] == []


def test_cli_imports_events_and_prints_dashboard_json(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(
        json.dumps({"type": "thread.started", "thread_id": "thread-cli", "item_type": "thread"}) + "\n",
        encoding="utf-8",
    )
    with connect(db_path) as conn:
        conn.execute(
            """
            UPDATE tasks
            SET state='waiting_user', needs_human_reason='choose next engine host'
            WHERE task_id='unity-mcp-001'
            """
        )

    import_result = runner.invoke(app, ["event-import", str(events_path), "--db", str(db_path)])
    assert import_result.exit_code == 0, import_result.output
    assert "imported events: 1" in import_result.output

    dashboard_result = runner.invoke(app, ["dashboard", "--json-output", "--db", str(db_path)])
    assert dashboard_result.exit_code == 0, dashboard_result.output
    payload = json.loads(dashboard_result.output)
    assert any(event["thread_id"] == "thread-cli" for event in payload["recent_events"])
    assert any(task["task_id"] == "unity-mcp-001" for task in payload["active_tasks"])
    assert any(task["task_id"] == "unity-mcp-001" for task in payload["needs_human_items"])
    assert "queued_tasks" in payload
    assert "blocked_tasks" in payload
    assert "completed_tasks" in payload
    assert "risky_items" in payload
    assert not any(
        issue["issue_id"] == "ctrl-20260513-phase4-live-appserver-proof-gap"
        and issue["task_id"] == "controller-core-phase4-live-proof"
        for issue in payload["open_issues"]
    )


def test_cli_status_and_dashboard_print_attention_sections(tmp_path):
    db_path = init_tmp_registry(tmp_path)

    status_result = runner.invoke(
        app,
        ["status", "--capability-max-age-days", "30", "--db", str(db_path)],
    )
    assert status_result.exit_code == 0, status_result.output
    assert "queued_tasks" in status_result.output
    assert "blocked_tasks" in status_result.output
    assert "completed_tasks" in status_result.output
    assert "missing_capability_paths" in status_result.output
    assert "stale_capability_paths" in status_result.output
    assert "needs_human_items" in status_result.output
    assert "risky_items" in status_result.output

    dashboard_result = runner.invoke(app, ["dashboard", "--db", str(db_path)])
    assert dashboard_result.exit_code == 0, dashboard_result.output
    assert "queued_tasks" in dashboard_result.output
    assert "blocked_tasks" in dashboard_result.output
    assert "completed_tasks" in dashboard_result.output
    assert "needs_human_items" in dashboard_result.output
    assert "risky_items" in dashboard_result.output


def test_cli_check_capabilities_reports_stale_when_max_age_days_is_set(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    evidence_path = tmp_path / "old-evidence.md"
    evidence_path.write_text("old proof\n", encoding="utf-8")
    old_mtime = time.time() - (3 * 24 * 60 * 60)
    os.utime(evidence_path, (old_mtime, old_mtime))

    with connect(db_path) as conn:
        conn.execute("DELETE FROM capabilities")
        conn.execute(
            """
            INSERT INTO capabilities(
              capability_id, title, category, status, lane_id, summary,
              evidence_paths_json, commands_json, inputs_json, outputs_json,
              limitations_json, next_steps_json
            )
            VALUES(
              'stale-cli-test', 'Stale CLI test', 'test', 'available', 'qa-evidence', 'tmp',
              ?, '[]', '[]', '[]', '[]', '[]'
            )
            """,
            (json.dumps([str(evidence_path)]),),
        )

    result = runner.invoke(app, ["check-capabilities", "--max-age-days", "1", "--db", str(db_path)])

    assert result.exit_code == 1
    assert "STALE stale-cli-test" in result.output
    assert evidence_path.name in result.output


def test_cli_dashboard_json_reports_stale_when_capability_max_age_days_is_set(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    evidence_path = tmp_path / "old-dashboard-evidence.md"
    evidence_path.write_text("old proof\n", encoding="utf-8")
    old_mtime = time.time() - (3 * 24 * 60 * 60)
    os.utime(evidence_path, (old_mtime, old_mtime))

    with connect(db_path) as conn:
        conn.execute("DELETE FROM capabilities")
        conn.execute(
            """
            INSERT INTO capabilities(
              capability_id, title, category, status, lane_id, summary,
              evidence_paths_json, commands_json, inputs_json, outputs_json,
              limitations_json, next_steps_json
            )
            VALUES(
              'stale-dashboard-cli-test', 'Stale dashboard CLI test', 'test', 'available', 'qa-evidence', 'tmp',
              ?, '[]', '[]', '[]', '[]', '[]'
            )
            """,
            (json.dumps([str(evidence_path)]),),
        )

    result = runner.invoke(
        app,
        ["dashboard", "--json-output", "--capability-max-age-days", "1", "--db", str(db_path)],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["capability_stale_max_age_days"] == 1
    assert payload["stale_capability_paths"] == [
        {"capability_id": "stale-dashboard-cli-test", "path": str(evidence_path)}
    ]


def test_cli_records_and_lists_downloads(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    source_url = "https://example.test/tool.tar.gz"

    record_result = runner.invoke(
        app,
        [
            "download-record",
            source_url,
            "--task",
            "download-001",
            "--retained-path",
            "external/downloads/tool.tar.gz",
            "--size-bytes",
            "2048",
            "--sha256",
            "b" * 64,
            "--command",
            "tools/download_no_proxy.sh https://example.test/tool.tar.gz external/downloads/tool.tar.gz",
            "--no-proxy-proof",
            "experiments/download/lsof.txt",
            "--status",
            "done",
            "--db",
            str(db_path),
        ],
    )
    assert record_result.exit_code == 0, record_result.output
    assert "recorded download:" in record_result.output

    list_result = runner.invoke(
        app,
        ["downloads", "--task", "download-001", "--json-output", "--db", str(db_path)],
    )
    assert list_result.exit_code == 0, list_result.output
    downloads = json.loads(list_result.output)
    assert downloads[0]["source_url"] == source_url
    assert downloads[0]["status"] == "done"


def test_cli_large_unapproved_download_records_needs_approval(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    source_url = "https://download.unity3d.com/download_unity/c1aa84e375f6/MacEditorInstallerArm64/Unity-6000.3.15f1.pkg"

    record_result = runner.invoke(
        app,
        [
            "download-record",
            source_url,
            "--task",
            "unity-mcp-001",
            "--size-bytes",
            "5112633639",
            "--status",
            "planned",
            "--db",
            str(db_path),
        ],
    )
    assert record_result.exit_code == 0, record_result.output

    dashboard_result = runner.invoke(app, ["dashboard", "--json-output", "--db", str(db_path)])
    assert dashboard_result.exit_code == 0, dashboard_result.output
    payload = json.loads(dashboard_result.output)
    assert payload["recent_downloads"][0]["source_url"] == source_url
    assert payload["recent_downloads"][0]["status"] == "needs_approval"
    assert any(
        item["source"] == "download" and item["state"] == "needs_approval"
        for item in payload["needs_human_items"]
    )


def test_cli_rejects_done_download_without_provenance(tmp_path):
    db_path = init_tmp_registry(tmp_path)

    result = runner.invoke(
        app,
        [
            "download-record",
            "https://example.test/tool.tar.gz",
            "--status",
            "done",
            "--db",
            str(db_path),
        ],
    )

    assert result.exit_code != 0
    assert "done downloads require" in result.output


def test_cli_downloads_rejects_invalid_filters(tmp_path):
    db_path = init_tmp_registry(tmp_path)

    bad_limit = runner.invoke(app, ["downloads", "--limit", "-1", "--db", str(db_path)])
    assert bad_limit.exit_code != 0
    assert "limit must be positive" in bad_limit.output

    bad_status = runner.invoke(app, ["downloads", "--status", "wat", "--db", str(db_path)])
    assert bad_status.exit_code != 0
    assert "status must be one of" in bad_status.output


def test_init_registry_migrates_older_downloads_table(tmp_path):
    db_path = tmp_path / "registry.sqlite3"
    with connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE repos (
              repo_id TEXT PRIMARY KEY,
              path TEXT NOT NULL,
              role TEXT NOT NULL DEFAULT '',
              default_branch TEXT NOT NULL DEFAULT 'main',
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE lanes (
              lane_id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              state TEXT NOT NULL,
              auto_continue INTEGER NOT NULL DEFAULT 0,
              concurrency INTEGER NOT NULL DEFAULT 1,
              owner TEXT NOT NULL DEFAULT '',
              safety_policy TEXT NOT NULL DEFAULT '',
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE tasks (
              task_id TEXT PRIMARY KEY,
              lane_id TEXT NOT NULL,
              repo_id TEXT NOT NULL,
              title TEXT NOT NULL,
              goal TEXT NOT NULL DEFAULT '',
              done_criteria TEXT NOT NULL DEFAULT '',
              state TEXT NOT NULL,
              priority INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE downloads (
              download_id INTEGER PRIMARY KEY AUTOINCREMENT,
              task_id TEXT,
              source_url TEXT NOT NULL,
              retained_path TEXT,
              size_bytes INTEGER,
              sha256 TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

    init_registry(db_path, load_config(ROOT / "config" / "lanes.yaml"))
    result = runner.invoke(
        app,
        [
            "download-record",
            "https://example.test/tool.tar.gz",
            "--task",
            "download-001",
            "--size-bytes",
            "2048",
            "--status",
            "planned",
            "--db",
            str(db_path),
        ],
    )

    assert result.exit_code == 0, result.output

    dashboard_result = runner.invoke(app, ["dashboard", "--json-output", "--db", str(db_path)])
    assert dashboard_result.exit_code == 0, dashboard_result.output
    payload = json.loads(dashboard_result.output)
    assert "needs_human_items" in payload
    assert "risky_items" in payload

    status_result = runner.invoke(app, ["status", "--db", str(db_path)])
    assert status_result.exit_code == 0, status_result.output
    assert "needs_human_items" in status_result.output
    assert "risky_items" in status_result.output
