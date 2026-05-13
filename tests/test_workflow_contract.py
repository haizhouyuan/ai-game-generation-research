from typer.testing import CliRunner

from managed_codex.cli import app
from managed_codex.workflow import load_workflow_summary

runner = CliRunner()


def test_load_workflow_summary_extracts_title_and_sections(tmp_path):
    workflow_path = tmp_path / "WORKFLOW.md"
    workflow_path.write_text(
        "\n".join(
            [
                "# Managed Agents Workflow",
                "",
                "## Scope",
                "Use Symphony-compatible orchestration.",
                "",
                "## Evidence",
                "Record local proof.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    summary = load_workflow_summary(workflow_path)

    assert summary == {
        "path": str(workflow_path),
        "exists": True,
        "title": "Managed Agents Workflow",
        "sections": ["Scope", "Evidence"],
    }


def test_load_workflow_summary_reports_missing_file(tmp_path):
    workflow_path = tmp_path / "WORKFLOW.md"

    summary = load_workflow_summary(workflow_path)

    assert summary == {
        "path": str(workflow_path),
        "exists": False,
        "title": None,
        "sections": [],
    }


def test_cli_workflow_prints_json_summary(tmp_path):
    workflow_path = tmp_path / "WORKFLOW.md"
    workflow_path.write_text("# Managed Agents Workflow\n\n## Runtime\nUse local proof.\n", encoding="utf-8")

    result = runner.invoke(app, ["workflow", "--path", str(workflow_path), "--json-output"])

    assert result.exit_code == 0, result.output
    assert '"title": "Managed Agents Workflow"' in result.output
    assert '"Runtime"' in result.output
