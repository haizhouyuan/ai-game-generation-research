"""Typer CLI for the managed Codex registry."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table

from .app_server_client import (
    AppServerClient,
    FakeAppServer,
    FakeAppServerTransport,
    HttpJsonRpcTransport,
    run_thread_read_fork_interrupt_archive_flow,
    run_thread_turn_review_archive_flow,
)
from .config import load_config
from .db import connect, init_registry
from .registry_ops import (
    DOWNLOAD_STATUSES,
    add_controller_issue,
    capability_evidence_path_findings,
    capability_missing_paths,
    dashboard_snapshot,
    import_events_jsonl,
    record_codex_event,
    record_download,
    record_worker_result,
)
from .worker_result import validate_worker_result
from .workflow import load_workflow_summary

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / ".managed_codex" / "registry.sqlite3"
DEFAULT_CONFIG = ROOT / "config" / "lanes.yaml"
DEFAULT_WORKER_RESULT_SCHEMA = ROOT / "schemas" / "worker_result.schema.json"

app = typer.Typer(help="Managed Codex registry CLI.")
console = Console()


def db_option() -> Path:
    return Path(os.environ.get("CODEX_MANAGED_DB", DEFAULT_DB))


def require_db(db: Path) -> None:
    if not db.exists():
        raise typer.BadParameter(f"registry does not exist: {db}. Run `codex-managed init` first.")


@app.command()
def init(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    config: Path = typer.Option(DEFAULT_CONFIG, help="Lane/task config path."),
) -> None:
    """Initialize registry and seed lanes/tasks."""

    managed_config = load_config(config)
    init_registry(db, managed_config)
    console.print(f"initialized registry: {db}")


@app.command()
def status(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    capability_max_age_days: Optional[int] = typer.Option(
        None,
        "--capability-max-age-days",
        help="Also show local capability evidence older than this many days.",
    ),
) -> None:
    """Show registry summary."""

    require_db(db)
    if capability_max_age_days is not None and capability_max_age_days < 0:
        raise typer.BadParameter("capability-max-age-days must be non-negative")
    with connect(db) as conn:
        snapshot = dashboard_snapshot(conn, ROOT, capability_max_age_days=capability_max_age_days)
        console.print(f"registry: {db}")
        print_counts(conn, "lanes", "state")
        print_counts(conn, "tasks", "state")
        active = conn.execute(
            """
            SELECT task_id, lane_id, state, priority, title
            FROM tasks
            WHERE state IN (
              'queued', 'dispatching', 'planning', 'running', 'blocked',
              'waiting_user', 'waiting_approval', 'needs_retry'
            )
            ORDER BY priority DESC, created_at ASC
            LIMIT 12
            """
        ).fetchall()
        print_rows("active_or_waiting_tasks", active, ["priority", "state", "lane_id", "task_id", "title"])
        disabled = conn.execute(
            "SELECT lane_id, title, state FROM lanes WHERE state IN ('paused', 'disabled', 'error') ORDER BY lane_id"
        ).fetchall()
        print_rows("non_dispatchable_lanes", disabled, ["lane_id", "state", "title"])
        print_dict_rows(
            "queued_tasks",
            snapshot["queued_tasks"],
            ["priority", "state", "lane_id", "task_id", "title"],
        )
        print_dict_rows(
            "blocked_tasks",
            snapshot["blocked_tasks"],
            ["priority", "state", "lane_id", "task_id", "title", "blocked_reason"],
        )
        print_dict_rows(
            "completed_tasks",
            snapshot["completed_tasks"],
            ["priority", "state", "lane_id", "task_id", "title"],
        )
        print_dict_rows("missing_capability_paths", snapshot["missing_capability_paths"], ["capability_id", "path"])
        print_dict_rows("stale_capability_paths", snapshot["stale_capability_paths"], ["capability_id", "path"])
        print_dict_rows(
            "needs_human_items",
            snapshot["needs_human_items"],
            ["source", "state", "task_id", "id", "title", "reason"],
        )
        print_dict_rows(
            "risky_items",
            snapshot["risky_items"],
            ["source", "state", "severity", "lane_id", "task_id", "id", "title", "reason"],
        )


@app.command()
def dashboard(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    json_output: bool = typer.Option(False, "--json-output", help="Print machine-readable JSON."),
    capability_max_age_days: Optional[int] = typer.Option(
        None,
        "--capability-max-age-days",
        help="Also show local capability evidence older than this many days.",
    ),
) -> None:
    """Answer who is active, blocked, missing evidence, and recently changed."""

    require_db(db)
    if capability_max_age_days is not None and capability_max_age_days < 0:
        raise typer.BadParameter("capability-max-age-days must be non-negative")
    with connect(db) as conn:
        snapshot = dashboard_snapshot(conn, ROOT, capability_max_age_days=capability_max_age_days)
    if json_output:
        console.print(json.dumps(snapshot, indent=2, sort_keys=True), soft_wrap=True)
        return

    console.print(f"registry: {db}")
    workflow = snapshot["workflow"]
    console.print(f"workflow: {workflow['title'] or 'missing'} ({workflow['path']})")
    print_dict_rows("lanes_by_state", snapshot["lane_counts"], ["state", "count"])
    print_dict_rows("tasks_by_state", snapshot["task_counts"], ["state", "count"])
    print_dict_rows(
        "active_or_blocked_tasks",
        snapshot["active_tasks"],
        ["priority", "state", "lane_id", "task_id", "title"],
    )
    print_dict_rows(
        "queued_tasks",
        snapshot["queued_tasks"],
        ["priority", "state", "lane_id", "task_id", "title"],
    )
    print_dict_rows(
        "blocked_tasks",
        snapshot["blocked_tasks"],
        ["priority", "state", "lane_id", "task_id", "title", "blocked_reason"],
    )
    print_dict_rows(
        "completed_tasks",
        snapshot["completed_tasks"],
        ["priority", "state", "lane_id", "task_id", "title"],
    )
    print_dict_rows(
        "needs_human_items",
        snapshot["needs_human_items"],
        ["source", "state", "task_id", "id", "title", "reason"],
    )
    print_dict_rows(
        "risky_items",
        snapshot["risky_items"],
        ["source", "state", "severity", "lane_id", "task_id", "id", "title", "reason"],
    )
    print_dict_rows(
        "open_controller_issues",
        snapshot["open_issues"],
        ["severity", "lane_id", "task_id", "issue_id", "title"],
    )
    print_dict_rows("capabilities_by_status", snapshot["capability_counts"], ["status", "count"])
    print_dict_rows("missing_capability_paths", snapshot["missing_capability_paths"], ["capability_id", "path"])
    print_dict_rows("stale_capability_paths", snapshot["stale_capability_paths"], ["capability_id", "path"])
    print_dict_rows(
        "recent_codex_events",
        snapshot["recent_events"],
        ["observed_at", "thread_id", "turn_id", "event_type", "item_type"],
    )
    print_dict_rows(
        "recent_evidence",
        snapshot["recent_evidence"],
        ["task_id", "lane_id", "evidence_type", "path_or_url", "notes"],
    )
    print_dict_rows(
        "recent_downloads",
        snapshot["recent_downloads"],
        ["download_id", "task_id", "status", "size_bytes", "retained_path", "source_url"],
    )


@app.command()
def workflow(
    path: Path = typer.Option(ROOT / "WORKFLOW.md", help="Workflow contract path."),
    json_output: bool = typer.Option(False, "--json-output", help="Print machine-readable JSON."),
) -> None:
    """Show the Symphony-compatible repository workflow contract summary."""

    summary = load_workflow_summary(path)
    if json_output:
        console.print(json.dumps(summary, indent=2, sort_keys=True))
        return
    console.print(f"workflow: {summary['title'] or 'missing'}")
    console.print(f"path: {summary['path']}")
    console.print(f"exists: {summary['exists']}")
    print_dict_rows("sections", [{"section": section} for section in summary["sections"]], ["section"])


@app.command()
def lanes(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    state: Optional[str] = typer.Option(None, help="Filter by lane state."),
) -> None:
    """List lanes."""

    require_db(db)
    with connect(db) as conn:
        query = "SELECT lane_id, state, auto_continue, concurrency, owner, title FROM lanes"
        params: list[Any] = []
        if state:
            query += " WHERE state = ?"
            params.append(state)
        query += " ORDER BY lane_id"
        rows = conn.execute(query, params).fetchall()
    print_rows("lanes", rows, ["lane_id", "state", "auto_continue", "concurrency", "owner", "title"])


@app.command()
def tasks(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    state: Optional[str] = typer.Option(None, help="Filter by task state."),
    lane: Optional[str] = typer.Option(None, help="Filter by lane id."),
) -> None:
    """List tasks."""

    require_db(db)
    with connect(db) as conn:
        query = "SELECT task_id, lane_id, state, priority, title FROM tasks"
        params: list[Any] = []
        clauses = []
        if state:
            clauses.append("state = ?")
            params.append(state)
        if lane:
            clauses.append("lane_id = ?")
            params.append(lane)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY priority DESC, created_at ASC"
        rows = conn.execute(query, params).fetchall()
    print_rows("tasks", rows, ["task_id", "lane_id", "state", "priority", "title"])


@app.command()
def threads(db: Path = typer.Option(default_factory=db_option, help="SQLite registry path.")) -> None:
    """List threads."""

    require_db(db)
    with connect(db) as conn:
        rows = conn.execute(
            """
            SELECT thread_id, task_id, lane_id, runtime_status, archived, last_event_at
            FROM threads
            ORDER BY updated_at DESC
            """
        ).fetchall()
    print_rows("threads", rows, ["thread_id", "task_id", "lane_id", "runtime_status", "archived", "last_event_at"])


@app.command("event-import")
def event_import(
    path: Path = typer.Argument(..., help="JSONL file containing Codex/App Server events."),
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
) -> None:
    """Import Codex/App Server events into the registry."""

    require_db(db)
    with connect(db) as conn:
        count = import_events_jsonl(conn, path)
    console.print(f"imported events: {count}")


@app.command()
def events(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    thread_id: Optional[str] = typer.Option(None, help="Filter by thread id."),
) -> None:
    """List recently imported Codex/App Server events."""

    require_db(db)
    with connect(db) as conn:
        query = "SELECT observed_at, thread_id, turn_id, event_type, item_type FROM codex_events"
        params: list[Any] = []
        if thread_id:
            query += " WHERE thread_id = ?"
            params.append(thread_id)
        query += " ORDER BY observed_at DESC, event_id DESC LIMIT 50"
        rows = conn.execute(query, params).fetchall()
    print_rows("codex_events", rows, ["observed_at", "thread_id", "turn_id", "event_type", "item_type"])


@app.command("appserver-smoke")
def appserver_smoke(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    url: Optional[str] = typer.Option(None, help="Local HTTP JSON-RPC endpoint. Defaults to fake harness."),
    name: str = typer.Option("managed-agent-smoke", help="Temporary thread name."),
    prompt: str = typer.Option("Return schema-valid WORKER_RESULT JSON.", help="Smoke-test turn prompt."),
    extended: bool = typer.Option(False, "--extended", help="Exercise read, fork, steer, and interrupt too."),
) -> None:
    """Run a guarded App Server lifecycle smoke and record emitted events."""

    require_db(db)
    if url:
        client = AppServerClient(HttpJsonRpcTransport(url))
    else:
        client = AppServerClient(FakeAppServerTransport(FakeAppServer()))
    if extended:
        result = run_thread_read_fork_interrupt_archive_flow(
            client,
            name=name,
            prompt=prompt,
            output_schema={"type": "object"},
        )
    else:
        result = run_thread_turn_review_archive_flow(
            client,
            name=name,
            prompt=prompt,
            output_schema={"type": "object"},
        )
    with connect(db) as conn:
        for event in result["events"]:
            record_codex_event(conn, event)
    fields = [
        f"thread_id={result['thread_id']}",
        f"turn_id={result['turn_id']}",
    ]
    if "review_id" in result:
        fields.append(f"review_id={result['review_id']}")
    if "forked_thread_id" in result:
        fields.append(f"forked_thread_id={result['forked_thread_id']}")
    fields.extend([f"archived={result['archived']}", f"events={len(result['events'])}"])
    console.print(" ".join(fields))


@app.command()
def capabilities(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    status: Optional[str] = typer.Option(None, help="Filter by capability status."),
) -> None:
    """List reusable capabilities discovered from prior experiments."""

    require_db(db)
    with connect(db) as conn:
        query = "SELECT capability_id, status, category, lane_id, title FROM capabilities"
        params: list[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY status, category, capability_id"
        rows = conn.execute(query, params).fetchall()
    print_rows("capabilities", rows, ["capability_id", "status", "category", "lane_id", "title"])


@app.command("check-capabilities")
def check_capabilities(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    max_age_days: Optional[int] = typer.Option(
        None,
        "--max-age-days",
        help="Also fail when local capability evidence is older than this many days.",
    ),
) -> None:
    """Fail if capability evidence paths are stale or missing."""

    require_db(db)
    if max_age_days is not None and max_age_days < 0:
        raise typer.BadParameter("max-age-days must be non-negative")
    with connect(db) as conn:
        if max_age_days is None:
            missing = capability_missing_paths(conn, ROOT)
            stale: list[tuple[str, str]] = []
        else:
            findings = capability_evidence_path_findings(conn, ROOT, max_age_days=max_age_days)
            missing = findings["missing"]
            stale = findings["stale"]
    if missing:
        for capability_id, path in missing:
            console.print(f"[red]MISSING[/red] {capability_id}: {path}")
    if stale:
        for capability_id, path in stale:
            console.print(f"[yellow]STALE[/yellow] {capability_id}: {path}")
    if missing or stale:
        raise typer.Exit(1)
    console.print("capability evidence paths: ok")


@app.command()
def artifacts(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    task: Optional[str] = typer.Option(None, help="Filter by task id."),
) -> None:
    """List indexed artifacts."""

    require_db(db)
    with connect(db) as conn:
        query = "SELECT task_id, lane_id, type, validation_status, path_or_url FROM artifacts"
        params: list[Any] = []
        if task:
            query += " WHERE task_id = ?"
            params.append(task)
        query += " ORDER BY created_at DESC, artifact_id DESC"
        rows = conn.execute(query, params).fetchall()
    print_rows("artifacts", rows, ["task_id", "lane_id", "type", "validation_status", "path_or_url"])


@app.command()
def evidence(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    task: Optional[str] = typer.Option(None, help="Filter by task id."),
) -> None:
    """List indexed evidence items."""

    require_db(db)
    with connect(db) as conn:
        query = "SELECT task_id, lane_id, evidence_type, path_or_url, notes FROM evidence_items"
        params: list[Any] = []
        if task:
            query += " WHERE task_id = ?"
            params.append(task)
        query += " ORDER BY created_at DESC, evidence_id DESC"
        rows = conn.execute(query, params).fetchall()
    print_rows("evidence", rows, ["task_id", "lane_id", "evidence_type", "path_or_url", "notes"])


@app.command()
def issues(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    state: Optional[str] = typer.Option(None, help="Filter by issue state."),
) -> None:
    """List controller improvement issues."""

    require_db(db)
    with connect(db) as conn:
        query = "SELECT issue_id, state, severity, lane_id, task_id, title FROM controller_issues"
        params: list[Any] = []
        if state:
            query += " WHERE state = ?"
            params.append(state)
        query += " ORDER BY state, severity DESC, created_at DESC"
        rows = conn.execute(query, params).fetchall()
    print_rows("controller_issues", rows, ["issue_id", "state", "severity", "lane_id", "task_id", "title"])


@app.command("download-record")
def download_record(
    source_url: str = typer.Argument(..., help="Original source URL or remote."),
    task_id: Optional[str] = typer.Option(None, "--task", "--task-id", help="Related managed task id."),
    retained_path: Optional[str] = typer.Option(None, help="Retained local artifact path, if any."),
    size_bytes: Optional[int] = typer.Option(None, help="Observed or expected size in bytes."),
    sha256: Optional[str] = typer.Option(None, help="SHA256 for retained artifact, when available."),
    command: Optional[str] = typer.Option(None, help="Exact command used or planned."),
    no_proxy_proof: Optional[str] = typer.Option(None, help="Path or note for no-proxy evidence."),
    status: str = typer.Option(
        "planned",
        help="planned, metadata_only, needs_approval, done, failed, skipped.",
    ),
    approved_over_1gb: bool = typer.Option(
        False,
        "--approved-over-1gb",
        help="Explicitly confirm user approval for a single file over 1GiB.",
    ),
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
) -> None:
    """Record governed download metadata without performing a download."""

    require_db(db)
    with connect(db) as conn:
        try:
            download_id = record_download(
                conn,
                task_id=task_id,
                source_url=source_url,
                retained_path=retained_path,
                size_bytes=size_bytes,
                sha256=sha256,
                command=command,
                no_proxy_proof=no_proxy_proof,
                status=status,
                approved_over_1gb=approved_over_1gb,
            )
        except ValueError as exc:
            raise typer.BadParameter(str(exc)) from exc
    console.print(f"recorded download: {download_id}")


@app.command()
def downloads(
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    task: Optional[str] = typer.Option(None, help="Filter by task id."),
    status: Optional[str] = typer.Option(None, help="Filter by download status."),
    limit: int = typer.Option(50, help="Maximum rows to print."),
    json_output: bool = typer.Option(False, "--json-output", help="Print machine-readable JSON."),
) -> None:
    """List governed download records."""

    require_db(db)
    if limit < 1:
        raise typer.BadParameter("limit must be positive")
    if status is not None and status not in DOWNLOAD_STATUSES:
        raise typer.BadParameter(f"status must be one of {sorted(DOWNLOAD_STATUSES)}")
    with connect(db) as conn:
        query = """
            SELECT download_id, task_id, status, size_bytes, sha256, retained_path, source_url
            FROM downloads
        """
        params: list[Any] = []
        clauses = []
        if task:
            clauses.append("task_id = ?")
            params.append(task)
        if status:
            clauses.append("status = ?")
            params.append(status)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at DESC, download_id DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
    if json_output:
        console.print(json.dumps([dict(row) for row in rows], indent=2, sort_keys=True), soft_wrap=True)
        return
    print_rows(
        "downloads",
        rows,
        ["download_id", "task_id", "status", "size_bytes", "sha256", "retained_path", "source_url"],
    )


@app.command("issue-add")
def issue_add(
    issue_id: str = typer.Argument(..., help="Stable controller issue id."),
    title: str = typer.Option(..., help="Short issue title."),
    severity: str = typer.Option("medium", help="low, medium, high, critical."),
    state: str = typer.Option("open", help="open, triaged, fixed, wont_fix."),
    lane_id: Optional[str] = typer.Option(None, help="Related lane id."),
    task_id: Optional[str] = typer.Option(None, help="Related task id."),
    symptom: str = typer.Option("", help="Observed symptom."),
    root_cause: str = typer.Option("", help="Known or suspected root cause."),
    improvement: str = typer.Option("", help="Controller/system improvement to make."),
    evidence_text: str = typer.Option("", "--evidence", help="Evidence path, command, or note."),
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
) -> None:
    """Add or update a controller issue so using agents improves the system."""

    require_db(db)
    with connect(db) as conn:
        add_controller_issue(
            conn,
            issue_id=issue_id,
            title=title,
            severity=severity,
            state=state,
            lane_id=lane_id,
            task_id=task_id,
            symptom=symptom,
            root_cause=root_cause,
            improvement=improvement,
            evidence=evidence_text,
        )
    console.print(f"recorded controller issue: {issue_id}")


@app.command("validate-result")
def validate_result(
    path: Path = typer.Argument(..., help="WORKER_RESULT JSON file."),
    schema: Path = typer.Option(DEFAULT_WORKER_RESULT_SCHEMA, help="WORKER_RESULT schema path."),
) -> None:
    """Validate a WORKER_RESULT JSON file."""

    errors = validate_worker_result(path, schema)
    if errors:
        for error in errors:
            console.print(f"[red]ERROR[/red] {error}")
        raise typer.Exit(1)
    console.print(f"valid WORKER_RESULT: {path}")


@app.command("record-result")
def record_result(
    path: Path = typer.Argument(..., help="WORKER_RESULT JSON file."),
    db: Path = typer.Option(default_factory=db_option, help="SQLite registry path."),
    schema: Path = typer.Option(DEFAULT_WORKER_RESULT_SCHEMA, help="WORKER_RESULT schema path."),
) -> None:
    """Validate and persist a worker result into tasks, artifacts, and evidence."""

    require_db(db)
    with connect(db) as conn:
        errors = record_worker_result(conn, path, schema)
        if errors:
            for error in errors:
                console.print(f"[red]ERROR[/red] {error}")
            raise typer.Exit(1)
    console.print(f"recorded WORKER_RESULT: {path}")


def print_counts(conn: sqlite3.Connection, table_name: str, column: str) -> None:
    rows = conn.execute(
        f"SELECT {column} AS name, COUNT(*) AS count FROM {table_name} GROUP BY {column} ORDER BY {column}"
    ).fetchall()
    print_rows(f"{table_name}_by_{column}", rows, ["name", "count"])


def print_rows(title: str, rows: list[sqlite3.Row], columns: list[str]) -> None:
    console.print(f"\n[bold]{title}[/bold]")
    if not rows:
        console.print("  none")
        return
    table = Table(show_header=True, header_style="bold")
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*(format_cell(row[column]) for column in columns))
    console.print(table)


def print_dict_rows(title: str, rows: list[dict[str, Any]], columns: list[str]) -> None:
    console.print(f"\n[bold]{title}[/bold]")
    if not rows:
        console.print("  none")
        return
    table = Table(show_header=True, header_style="bold")
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*(format_cell(row.get(column)) for column in columns))
    console.print(table)


def format_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value)
