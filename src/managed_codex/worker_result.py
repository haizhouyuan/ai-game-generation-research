"""WORKER_RESULT validation."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


def load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_worker_result(result_path: Path, schema_path: Path) -> list[str]:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(result), key=lambda error: list(error.path))
    messages = [format_error(error) for error in errors]

    if result.get("status") == "done" and not result.get("evidence"):
        messages.append("done result must include at least one evidence item")
    if result.get("needs_human") and not result.get("human_question"):
        messages.append("needs_human true requires human_question")
    return messages


def format_error(error) -> str:
    path = ".".join(str(part) for part in error.path)
    prefix = f"{path}: " if path else ""
    return f"{prefix}{error.message}"

