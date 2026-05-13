#!/usr/bin/env python3
"""P26 contract bundle graph verifier for local scene-CI artifacts."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPERIMENTS = ROOT.parent
REPO_ROOT = EXPERIMENTS.parent
YOGA_GAME_ROOT = "/vol1/1000/projects/ai-game-generation-research"
P25_ROOT = EXPERIMENTS / "game_p25_artifact_dependency_graph_stale_reference_counters_20260512"
P25_RESULT = P25_ROOT / "outputs" / "validator_result.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def topological_order(nodes: list[dict], edges: list[dict]) -> tuple[list[str], bool]:
    node_ids = [node["id"] for node in nodes]
    unique_ids = set(node_ids)
    incoming = {node_id: 0 for node_id in unique_ids}
    outgoing = {node_id: [] for node_id in unique_ids}
    for edge in edges:
        source = edge["from"]
        target = edge["to"]
        if source not in unique_ids or target not in unique_ids:
            continue
        outgoing[source].append(target)
        incoming[target] += 1
    queue = deque(sorted(node_id for node_id, count in incoming.items() if count == 0))
    order: list[str] = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for target in sorted(outgoing[current]):
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)
    return order, len(order) == len(unique_ids) == len(node_ids)


def validate_bundle(bundle: dict, expected_source_hash: str) -> dict:
    nodes = bundle.get("nodes", [])
    edges = bundle.get("edges", [])
    node_ids = [node.get("id") for node in nodes]
    duplicate_nodes = sorted({node_id for node_id in node_ids if node_ids.count(node_id) > 1})
    node_id_set = set(node_ids)

    expected_order = bundle.get("topological_order", [])
    computed_order, acyclic = topological_order(nodes, edges)
    position = {node_id: index for index, node_id in enumerate(expected_order)}
    topo_rows = []
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        row_pass = (
            source in node_id_set
            and target in node_id_set
            and source in position
            and target in position
            and position[source] < position[target]
        )
        topo_rows.append(
            {
                "from": source,
                "to": target,
                "kind": edge.get("kind"),
                "from_ok": source in node_id_set,
                "to_ok": target in node_id_set,
                "order_ok": row_pass,
                "pass": row_pass,
            }
        )

    artifact_rows = []
    for node in nodes:
        path = Path(node.get("path", ""))
        exists = path.exists()
        current_hash = sha256_file(path) if exists else None
        row_pass = exists and current_hash == node.get("sha256")
        artifact_rows.append(
            {
                "id": node.get("id"),
                "path": str(path),
                "exists": exists,
                "expected_sha256": node.get("sha256"),
                "current_sha256": current_hash,
                "pass": row_pass,
            }
        )

    source_ok = bundle.get("source_p25_sha256") == expected_source_hash
    order_set_ok = set(expected_order) == node_id_set and len(expected_order) == len(node_ids)
    computed_order_ok = expected_order == computed_order and acyclic
    topo_ok = all(row["pass"] for row in topo_rows) and order_set_ok and computed_order_ok
    artifact_ok = all(row["pass"] for row in artifact_rows)
    pass_value = source_ok and not duplicate_nodes and artifact_ok and topo_ok

    return {
        "pass": pass_value,
        "source_ok": source_ok,
        "duplicate_nodes": duplicate_nodes,
        "acyclic": acyclic,
        "expected_order": expected_order,
        "computed_order": computed_order,
        "order_set_ok": order_set_ok,
        "computed_order_ok": computed_order_ok,
        "topological_order_ok": topo_ok,
        "artifact_rows": artifact_rows,
        "topological_rows": topo_rows,
    }


def make_bundle(p25_result: dict, source_hash: str) -> dict:
    graph = p25_result["graph_manifest"]
    nodes = copy.deepcopy(graph["nodes"])
    for node in nodes:
        path = str(node.get("path", ""))
        if path.startswith(YOGA_GAME_ROOT + "/"):
            node["source_path"] = path
            node["path"] = str(REPO_ROOT / path.removeprefix(YOGA_GAME_ROOT + "/"))
    edges = copy.deepcopy(graph["edges"])
    order, acyclic = topological_order(nodes, edges)
    if not acyclic:
        raise RuntimeError("P25 graph is not acyclic")
    return {
        "bundle_version": "1.0",
        "bundle_id": "game_p26_contract_bundle_graph_20260512",
        "source_p25_sha256": source_hash,
        "source_graph_id": graph["graph_id"],
        "nodes": nodes,
        "edges": edges,
        "topological_order": order,
        "boundary": "contract bundle covers local reviewer-contract artifacts only",
    }


def make_artifact_hashes(paths: list[Path]) -> dict:
    rows = []
    for path in paths:
        if path.exists():
            rows.append({"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    return {"algorithm": "sha256", "artifacts": rows}


def main() -> int:
    if not P25_RESULT.exists():
        raise FileNotFoundError(f"missing P25 validator result: {P25_RESULT}")

    p25_result = load_json(P25_RESULT)
    p25_hash = sha256_file(P25_RESULT)
    bundle = make_bundle(p25_result, p25_hash)
    valid_bundle = validate_bundle(bundle, p25_hash)

    cycle_bundle = copy.deepcopy(bundle)
    cycle_bundle["edges"].append(
        {"from": bundle["topological_order"][-1], "to": bundle["topological_order"][0], "kind": "cycle_counter"}
    )
    cycle_validation = validate_bundle(cycle_bundle, p25_hash)

    duplicate_bundle = copy.deepcopy(bundle)
    duplicate_bundle["nodes"].append(copy.deepcopy(bundle["nodes"][0]))
    duplicate_validation = validate_bundle(duplicate_bundle, p25_hash)

    stale_bundle = copy.deepcopy(bundle)
    stale_bundle["source_p25_sha256"] = "stale-" + p25_hash[6:]
    stale_validation = validate_bundle(stale_bundle, p25_hash)

    inherited = p25_result.get("checks", {})
    result = {
        "batch": "P26-A game contract bundle graph verifier",
        "contract_bundle": bundle,
        "valid_bundle": valid_bundle,
        "counters": {
            "cycle": {"pass": (not cycle_validation["pass"]) and (not cycle_validation["acyclic"]), "validation": cycle_validation},
            "duplicate_node": {
                "pass": (not duplicate_validation["pass"]) and bool(duplicate_validation["duplicate_nodes"]),
                "validation": duplicate_validation,
            },
            "stale_bundle": {
                "pass": (not stale_validation["pass"]) and (not stale_validation["source_ok"]),
                "validation": stale_validation,
            },
            "inherited_p25": {
                "pass": bool(
                    inherited.get("missing_artifact_counter_detected")
                    and inherited.get("tampered_hash_counter_detected")
                ),
                "source_checks": {
                    "missing_artifact_counter_detected": bool(inherited.get("missing_artifact_counter_detected")),
                    "tampered_hash_counter_detected": bool(inherited.get("tampered_hash_counter_detected")),
                },
            },
        },
        "checks": {
            "contract_bundle_valid": bool(valid_bundle["pass"]),
            "topological_order_valid": bool(valid_bundle["topological_order_ok"]),
            "cycle_counter_detected": False,
            "duplicate_node_counter_detected": False,
            "stale_bundle_counter_detected": False,
            "p25_missing_artifact_counter_inherited": bool(inherited.get("missing_artifact_counter_detected")),
            "p25_tampered_hash_counter_inherited": bool(inherited.get("tampered_hash_counter_detected")),
        },
        "boundaries": [
            "Dependency graph covers local reviewer-contract artifacts only.",
            "This does not claim screenshot/visual QA.",
            "This does not claim mesh-accurate GLB collision.",
        ],
    }
    result["checks"]["cycle_counter_detected"] = result["counters"]["cycle"]["pass"]
    result["checks"]["duplicate_node_counter_detected"] = result["counters"]["duplicate_node"]["pass"]
    result["checks"]["stale_bundle_counter_detected"] = result["counters"]["stale_bundle"]["pass"]
    result["overall_pass"] = all(result["checks"].values())

    write_json(ROOT / "validator_result.json", result)

    closeout = [
        "# P26 Game Contract Bundle Graph Verifier",
        "",
        f"Status: {'pass' if result['overall_pass'] else 'fail'}.",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    for key, value in result["checks"].items():
        closeout.append(f"| `{key}` | {value} |")
    closeout.extend(
        [
            "",
            "## Boundary",
            "",
            "- Dependency graph covers local reviewer-contract artifacts only.",
            "- This does not claim screenshot/visual QA.",
            "- This does not claim mesh-accurate GLB collision.",
            "",
            "## Next Candidates",
            "",
            "- Add contract-bundle release packet review with allowlisted bundle update candidates.",
            "- Add compact graph-diff packet for stale edge/node drift review.",
        ]
    )
    (ROOT / "closeout.md").write_text("\n".join(closeout) + "\n", encoding="utf-8")

    hashes = make_artifact_hashes(
        [
            ROOT / "run_p26_contract_bundle_graph_verifier.py",
            ROOT / "validator.py",
            ROOT / "validator_result.json",
            ROOT / "closeout.md",
            P25_RESULT,
            P25_ROOT / "outputs" / "artifact_dependency_graph_manifest.json",
        ]
    )
    write_json(ROOT / "artifact_hashes.json", hashes)

    print(json.dumps({"overall_pass": result["overall_pass"], "checks": result["checks"]}, indent=2, sort_keys=True))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
