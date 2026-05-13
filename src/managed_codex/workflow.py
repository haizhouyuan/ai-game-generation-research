"""Read the repository workflow contract used by Symphony-compatible runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_workflow_summary(path: Path) -> dict[str, Any]:
    """Return a compact summary of a WORKFLOW.md contract."""

    if not path.exists():
        return {"path": str(path), "exists": False, "title": None, "sections": []}
    title = None
    sections = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") and title is None:
            title = line[2:].strip()
        elif line.startswith("## "):
            sections.append(line[3:].strip())
    return {"path": str(path), "exists": True, "title": title, "sections": sections}
