from pathlib import Path

from typer.testing import CliRunner

from managed_codex.cli import app
from managed_codex.config import load_config
from managed_codex.db import connect, init_registry

ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def test_appserver_smoke_records_fake_lifecycle_events(tmp_path):
    db_path = tmp_path / "registry.sqlite3"
    init_registry(db_path, load_config(ROOT / "config" / "lanes.yaml"))

    result = runner.invoke(
        app,
        [
            "appserver-smoke",
            "--db",
            str(db_path),
            "--name",
            "phase4-cli-smoke",
            "--prompt",
            "Return schema-valid WORKER_RESULT JSON.",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "thread_id=thr_fake_1" in result.output
    assert "events=5" in result.output
    with connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) AS count FROM codex_events WHERE thread_id='thr_fake_1'").fetchone()[
            "count"
        ]
    assert count == 5


def test_appserver_smoke_extended_records_phase4_events(tmp_path):
    db_path = tmp_path / "registry.sqlite3"
    init_registry(db_path, load_config(ROOT / "config" / "lanes.yaml"))

    result = runner.invoke(
        app,
        [
            "appserver-smoke",
            "--extended",
            "--db",
            str(db_path),
            "--name",
            "phase4-cli-expanded-smoke",
            "--prompt",
            "Return schema-valid WORKER_RESULT JSON.",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "thread_id=thr_fake_1" in result.output
    assert "forked_thread_id=thr_fake_2" in result.output
    assert "events=8" in result.output
    with connect(db_path) as conn:
        event_types = [
            row["event_type"]
            for row in conn.execute(
                "SELECT event_type FROM codex_events WHERE thread_id IN ('thr_fake_1', 'thr_fake_2') ORDER BY event_id"
            ).fetchall()
        ]
    assert event_types == [
        "thread/started",
        "turn/started",
        "turn/completed",
        "turn/steered",
        "turn/interrupted",
        "thread/started",
        "thread/archived",
        "thread/archived",
    ]
