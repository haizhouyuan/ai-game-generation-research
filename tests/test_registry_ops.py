import json
import os
import time
from pathlib import Path

from managed_codex.config import load_config
from managed_codex.db import connect, init_registry
from managed_codex.registry_ops import (
    add_controller_issue,
    capability_evidence_path_findings,
    capability_missing_paths,
    dashboard_snapshot,
    recent_downloads,
    record_download,
    record_worker_result,
)

ROOT = Path(__file__).resolve().parents[1]


def init_tmp_registry(tmp_path):
    db_path = tmp_path / "registry.sqlite3"
    config = load_config(ROOT / "config" / "lanes.yaml")
    init_registry(db_path, config)
    return db_path


def test_init_registry_seeds_capabilities(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) AS count FROM capabilities").fetchone()["count"]
        p0 = conn.execute(
            "SELECT status, lane_id FROM capabilities WHERE capability_id='p0-html-baseline'"
        ).fetchone()
    assert count >= 8
    assert p0["status"] == "available"
    assert p0["lane_id"] == "game-design"


def test_capability_evidence_paths_are_current(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        missing = capability_missing_paths(conn, ROOT)
    assert missing == []


def test_capability_evidence_path_findings_detects_stale_file(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    evidence_path = tmp_path / "old-evidence.md"
    evidence_path.write_text("old proof\n", encoding="utf-8")
    old_mtime = time.time() - (3 * 24 * 60 * 60)
    evidence_json = json.dumps([str(evidence_path)])
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
              'stale-test', 'Stale test', 'test', 'available', 'qa-evidence', 'tmp',
              ?, '[]', '[]', '[]', '[]', '[]'
            )
            """,
            (evidence_json,),
        )
        os.utime(evidence_path, (old_mtime, old_mtime))
        findings = capability_evidence_path_findings(conn, ROOT, max_age_days=1)

    assert findings["missing"] == []
    assert findings["stale"] == [("stale-test", str(evidence_path))]


def test_dashboard_snapshot_reports_stale_capability_when_max_age_is_set(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    evidence_path = tmp_path / "old-evidence.md"
    evidence_path.write_text("old proof\n", encoding="utf-8")
    old_mtime = time.time() - (3 * 24 * 60 * 60)
    evidence_json = json.dumps([str(evidence_path)])
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
              'stale-dashboard-test', 'Stale dashboard test', 'test', 'available', 'qa-evidence', 'tmp',
              ?, '[]', '[]', '[]', '[]', '[]'
            )
            """,
            (evidence_json,),
        )
        os.utime(evidence_path, (old_mtime, old_mtime))
        default_snapshot = dashboard_snapshot(conn, ROOT)
        stale_snapshot = dashboard_snapshot(conn, ROOT, capability_max_age_days=1)

    assert default_snapshot["capability_stale_max_age_days"] is None
    assert default_snapshot["stale_capability_paths"] == []
    assert stale_snapshot["capability_stale_max_age_days"] == 1
    assert stale_snapshot["stale_capability_paths"] == [
        {"capability_id": "stale-dashboard-test", "path": str(evidence_path)}
    ]


def test_dashboard_snapshot_reports_needs_human_and_risky_items(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            UPDATE tasks
            SET state='waiting_approval', needs_human_reason='approve Unity Editor download'
            WHERE task_id='unity-mcp-001'
            """
        )
        conn.execute(
            """
            UPDATE tasks
            SET state='needs_retry', last_error='transient App Server failure'
            WHERE task_id='controller-core-phase5'
            """
        )
        conn.execute(
            """
            UPDATE tasks
            SET last_worker_status='needs_human', needs_human_reason=NULL
            WHERE task_id='download-001'
            """
        )
        add_controller_issue(
            conn,
            issue_id="ctrl-test-risk",
            title="High risk open issue",
            severity="high",
            state="open",
            lane_id="controller-core",
            task_id="controller-core-phase5",
            symptom="Risk was found.",
            root_cause="Test setup.",
            improvement="Expose it.",
            evidence="tests/test_registry_ops.py",
        )
        record_download(
            conn,
            task_id="unity-mcp-001",
            source_url="https://download.unity3d.com/Unity-6000.3.15f1.pkg",
            size_bytes=5_112_633_639,
            status="metadata_only",
        )
        snapshot = dashboard_snapshot(conn, ROOT)

    assert any(item["task_id"] == "unity-mcp-001" for item in snapshot["needs_human_items"])
    assert any(item["task_id"] == "download-001" for item in snapshot["needs_human_items"])
    assert any(
        item["source"] == "download" and item["state"] == "needs_approval"
        for item in snapshot["needs_human_items"]
    )
    assert any(
        item["source"] == "controller_issue" and item["id"] == "ctrl-test-risk"
        for item in snapshot["risky_items"]
    )
    assert any(item["source"] == "task" and item["id"] == "controller-core-phase5" for item in snapshot["risky_items"])
    assert any(item["source"] == "capability" and item["state"] == "blocked" for item in snapshot["risky_items"])


def test_record_worker_result_indexes_evidence_and_artifacts(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        errors = record_worker_result(
            conn,
            ROOT / "tools" / "managed_codex" / "examples" / "worker_result_valid.json",
            ROOT / "schemas" / "worker_result.schema.json",
        )
        task = conn.execute(
            "SELECT last_worker_status, last_summary FROM tasks WHERE task_id='controller-core-phase1'"
        ).fetchone()
        evidence_count = conn.execute(
            "SELECT COUNT(*) AS count FROM evidence_items WHERE task_id='controller-core-phase1'"
        ).fetchone()["count"]
        artifact_count = conn.execute(
            "SELECT COUNT(*) AS count FROM artifacts WHERE task_id='controller-core-phase1'"
        ).fetchone()["count"]

    assert errors == []
    assert task["last_worker_status"] == "done"
    assert "registry foundation" in task["last_summary"]
    assert evidence_count == 1
    assert artifact_count == 1


def test_add_controller_issue_upserts(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        add_controller_issue(
            conn,
            issue_id="ctrl-test-001",
            title="Worker retried without evidence",
            severity="high",
            state="open",
            lane_id="controller-core",
            task_id="controller-core-phase3",
            symptom="Retry happened after invalid result.",
            root_cause="Missing fail-close policy.",
            improvement="Block retry until WORKER_RESULT validates.",
            evidence="tests/test_registry_ops.py",
        )
        add_controller_issue(
            conn,
            issue_id="ctrl-test-001",
            title="Worker retried without evidence",
            severity="high",
            state="triaged",
            lane_id="controller-core",
            task_id="controller-core-phase3",
            symptom="Retry happened after invalid result.",
            root_cause="Missing fail-close policy.",
            improvement="Block retry until WORKER_RESULT validates.",
            evidence="tests/test_registry_ops.py",
        )
        issue = conn.execute("SELECT state FROM controller_issues WHERE issue_id='ctrl-test-001'").fetchone()
        count = conn.execute(
            "SELECT COUNT(*) AS count FROM controller_issues WHERE issue_id='ctrl-test-001'"
        ).fetchone()["count"]

    assert issue["state"] == "triaged"
    assert count == 1


def test_record_download_records_existing_table_fields(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        download_id = record_download(
            conn,
            task_id="download-001",
            source_url="https://example.test/tool.tar.gz",
            retained_path="external/downloads/tool.tar.gz",
            size_bytes=1024,
            sha256="a" * 64,
            command="tools/download_no_proxy.sh https://example.test/tool.tar.gz external/downloads/tool.tar.gz",
            no_proxy_proof="experiments/download/lsof.txt",
            status="done",
        )
        row = conn.execute(
            """
            SELECT task_id, source_url, retained_path, size_bytes, sha256, command, no_proxy_proof, status
            FROM downloads
            WHERE download_id=?
            """,
            (download_id,),
        ).fetchone()

    assert dict(row) == {
        "task_id": "download-001",
        "source_url": "https://example.test/tool.tar.gz",
        "retained_path": "external/downloads/tool.tar.gz",
        "size_bytes": 1024,
        "sha256": "a" * 64,
        "command": "tools/download_no_proxy.sh https://example.test/tool.tar.gz external/downloads/tool.tar.gz",
        "no_proxy_proof": "experiments/download/lsof.txt",
        "status": "done",
    }


def test_record_download_large_unapproved_becomes_needs_approval(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        download_id = record_download(
            conn,
            task_id="unity-mcp-001",
            source_url="https://download.unity3d.com/Unity-6000.3.15f1.pkg",
            size_bytes=1_073_741_825,
            status="planned",
        )
        row = conn.execute("SELECT size_bytes, status FROM downloads WHERE download_id=?", (download_id,)).fetchone()

    assert row["size_bytes"] == 1_073_741_825
    assert row["status"] == "needs_approval"


def test_record_download_rejects_done_without_provenance(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        try:
            record_download(conn, source_url="https://example.test/tool.tar.gz", status="done")
        except ValueError as exc:
            error = str(exc)
        else:
            error = ""

    assert "done downloads require" in error
    assert "retained_path" in error
    assert "sha256" in error


def test_dashboard_snapshot_includes_recent_downloads(tmp_path):
    db_path = init_tmp_registry(tmp_path)
    with connect(db_path) as conn:
        record_download(
            conn,
            task_id="unity-mcp-001",
            source_url="https://download.unity3d.com/Unity-6000.3.15f1.pkg",
            size_bytes=5_112_633_639,
            status="metadata_only",
        )
        downloads = recent_downloads(conn)
        snapshot = dashboard_snapshot(conn, ROOT)

    assert downloads[0]["source_url"] == "https://download.unity3d.com/Unity-6000.3.15f1.pkg"
    assert downloads[0]["status"] == "needs_approval"
    assert snapshot["recent_downloads"][0]["task_id"] == "unity-mcp-001"
