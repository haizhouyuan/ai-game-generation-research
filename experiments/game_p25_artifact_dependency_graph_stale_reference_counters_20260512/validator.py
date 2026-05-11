#!/usr/bin/env python3
"""P25 artifact dependency graph and stale-reference counters for game scene-CI evidence."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
P24_ROOT = ROOT.parents[0] / "game_p24_reviewer_contract_version_integrity_manifest_20260512"
P24_MATRIX = P24_ROOT / "outputs" / "p24_artifact_integrity_check_matrix.json"
P24_MANIFEST = P24_ROOT / "outputs" / "p24_artifact_integrity_manifest.json"
P24_VERSION = P24_ROOT / "outputs" / "p24_reviewer_contract_version_migration_report.json"
GRAPH_MANIFEST = OUT / "artifact_dependency_graph_manifest.json"
RESULT_FILE = OUT / "validator_result.json"
ARTIFACT_HASHES = OUT / "artifact_hashes.json"
CLOSEOUT = ROOT / "closeout.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def artifact_node(path: Path, role: str) -> dict[str, Any]:
    return {
        "id": role,
        "role": role,
        "path": str(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def build_graph() -> dict[str, Any]:
    p24_matrix = load_json(P24_MATRIX)
    p24_manifest = load_json(P24_MANIFEST)
    source_artifacts = [Path(row["path"]) for row in p24_manifest.get("artifacts", [])]
    nodes = [
        artifact_node(P24_MATRIX, "p24_integrity_matrix"),
        artifact_node(P24_MANIFEST, "p24_integrity_manifest"),
        artifact_node(P24_VERSION, "p24_version_report"),
    ]
    for index, path in enumerate(source_artifacts):
        nodes.append(artifact_node(path, f"source_artifact_{index}"))
    edges = [
        {"from": "p24_integrity_matrix", "to": "p24_integrity_manifest", "kind": "validates_manifest"},
        {"from": "p24_integrity_matrix", "to": "p24_version_report", "kind": "validates_version"},
    ]
    for index in range(len(source_artifacts)):
        edges.append({"from": "p24_integrity_manifest", "to": f"source_artifact_{index}", "kind": "declares_artifact"})
    return {
        "graph_version": "1.0",
        "graph_id": "game_p25_scene_ci_artifact_dependency_graph_20260512",
        "p24_overall_pass": p24_matrix.get("overall_pass") is True,
        "nodes": nodes,
        "edges": edges,
        "boundary": "dependency graph covers local reviewer-contract artifacts only",
    }


def validate_graph(graph: dict[str, Any]) -> dict[str, Any]:
    node_ids = {node["id"] for node in graph.get("nodes", [])}
    rows = []
    for node in graph.get("nodes", []):
        path = Path(node.get("path", ""))
        exists = path.exists()
        current_sha = sha256_file(path) if exists else None
        rows.append({
            "id": node.get("id"),
            "path": str(path),
            "exists": exists,
            "expected_sha256": node.get("sha256"),
            "current_sha256": current_sha,
            "pass": exists and current_sha == node.get("sha256"),
        })
    edge_rows = []
    referenced = set()
    for edge in graph.get("edges", []):
        from_ok = edge.get("from") in node_ids
        to_ok = edge.get("to") in node_ids
        referenced.add(edge.get("from"))
        referenced.add(edge.get("to"))
        edge_rows.append({"edge": edge, "pass": from_ok and to_ok, "from_ok": from_ok, "to_ok": to_ok})
    orphans = sorted(node_ids - referenced)
    return {
        "pass": graph.get("p24_overall_pass") is True and bool(rows) and all(row["pass"] for row in rows) and all(row["pass"] for row in edge_rows) and not orphans,
        "artifact_rows": rows,
        "edge_rows": edge_rows,
        "orphans": orphans,
        "node_count": len(node_ids),
        "edge_count": len(graph.get("edges", [])),
    }


def missing_artifact_counter(graph: dict[str, Any]) -> dict[str, Any]:
    counter = copy.deepcopy(graph)
    counter["nodes"][0]["path"] = str(OUT / "missing_artifact_counter.json")
    validation = validate_graph(counter)
    return {"pass": not validation["pass"], "validation": validation}


def tampered_hash_counter(graph: dict[str, Any]) -> dict[str, Any]:
    counter = copy.deepcopy(graph)
    counter["nodes"][0]["sha256"] = "tampered-" + counter["nodes"][0]["sha256"][9:]
    validation = validate_graph(counter)
    return {"pass": not validation["pass"], "validation": validation}


def stale_reference_counter(graph: dict[str, Any]) -> dict[str, Any]:
    counter = copy.deepcopy(graph)
    counter["edges"].append({"from": "p24_integrity_matrix", "to": "stale_missing_node", "kind": "stale_reference_counter"})
    validation = validate_graph(counter)
    return {"pass": not validation["pass"], "validation": validation}


def orphan_reference_counter(graph: dict[str, Any]) -> dict[str, Any]:
    counter = copy.deepcopy(graph)
    counter["nodes"].append({
        "id": "orphan_reference_counter",
        "role": "orphan_reference_counter",
        "path": str(P24_MATRIX),
        "sha256": sha256_file(P24_MATRIX),
        "bytes": P24_MATRIX.stat().st_size,
    })
    validation = validate_graph(counter)
    return {"pass": not validation["pass"], "validation": validation}


def inherited_p24_checks() -> dict[str, Any]:
    matrix = load_json(P24_MATRIX)
    checks = matrix.get("checks", {})
    return {
        "pass": (
            checks.get("migration_v1_to_v2_pass") is True
            and checks.get("manifest_hashes_pass") is True
            and checks.get("tampered_hash_counter_detected") is True
            and checks.get("missing_artifact_counter_detected") is True
        ),
        "source_checks": checks,
    }


def write_artifact_hashes() -> None:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path != ARTIFACT_HASHES and "__pycache__" not in path.parts:
            rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    write_json(ARTIFACT_HASHES, rows)


def write_closeout(result: dict[str, Any]) -> None:
    lines = [
        "# P25 Game Artifact Dependency Graph Stale Reference Counters",
        "",
        f"Status: {'pass' if result['overall_pass'] else 'fail'}.",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    for key, value in result["checks"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend([
        "",
        "## Boundary",
        "",
        "- Dependency graph covers local reviewer-contract artifacts only.",
        "- This does not claim screenshot/visual QA.",
        "- This does not claim mesh-accurate GLB collision.",
    ])
    CLOSEOUT.write_text("\n".join(lines) + "\n")


def run() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    graph = build_graph()
    write_json(GRAPH_MANIFEST, graph)
    valid = validate_graph(graph)
    missing = missing_artifact_counter(graph)
    tampered = tampered_hash_counter(graph)
    stale = stale_reference_counter(graph)
    orphan = orphan_reference_counter(graph)
    inherited = inherited_p24_checks()
    checks = {
        "dependency_graph_valid": valid["pass"],
        "missing_artifact_counter_detected": missing["pass"],
        "tampered_hash_counter_detected": tampered["pass"],
        "stale_reference_counter_detected": stale["pass"],
        "orphan_reference_counter_detected": orphan["pass"],
        "p24_version_integrity_inherited": inherited["pass"],
    }
    result = {
        "batch": "P25-A game artifact dependency graph and stale-reference counters",
        "graph_manifest": graph,
        "valid_graph": valid,
        "counters": {
            "missing_artifact": missing,
            "tampered_hash": tampered,
            "stale_reference": stale,
            "orphan_reference": orphan,
            "inherited_p24": inherited,
        },
        "checks": checks,
        "overall_pass": all(checks.values()),
        "boundaries": [
            "Dependency graph covers local reviewer-contract artifacts only.",
            "This does not claim screenshot/visual QA.",
            "This does not claim mesh-accurate GLB collision.",
        ],
    }
    write_json(RESULT_FILE, result)
    write_closeout(result)
    write_artifact_hashes()
    return result


def main() -> int:
    result = run()
    print(json.dumps({"overall_pass": result["overall_pass"], "checks": result["checks"]}, indent=2))
    return 0 if result["overall_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
