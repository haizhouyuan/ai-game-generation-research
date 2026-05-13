#!/usr/bin/env python3
"""P27 release-packet review layer for P26 contract bundles."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPERIMENTS = ROOT.parent
P26_ROOT = EXPERIMENTS / "game_p26_contract_bundle_graph_verifier_20260512"
P26_RESULT = P26_ROOT / "validator_result.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_sha256(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def validate_bundle_shape(bundle: dict) -> dict:
    nodes = bundle.get("nodes", [])
    edges = bundle.get("edges", [])
    expected_order = bundle.get("topological_order", [])
    node_ids = [node.get("id") for node in nodes]
    node_id_set = set(node_ids)
    duplicate_nodes = sorted({node_id for node_id in node_ids if node_ids.count(node_id) > 1})
    computed_order, acyclic = topological_order(nodes, edges)
    order_ok = acyclic and computed_order == expected_order and set(expected_order) == node_id_set and len(expected_order) == len(node_ids)
    edge_rows = []
    position = {node_id: index for index, node_id in enumerate(expected_order)}
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        edge_rows.append(
            {
                "from": source,
                "to": target,
                "from_ok": source in node_id_set,
                "to_ok": target in node_id_set,
                "order_ok": source in position and target in position and position[source] < position[target],
            }
        )
    artifact_rows = []
    for node in nodes:
        path = Path(node.get("path", ""))
        exists = path.exists()
        current = sha256_file(path) if exists else None
        artifact_rows.append(
            {
                "id": node.get("id"),
                "exists": exists,
                "path": str(path),
                "expected_sha256": node.get("sha256"),
                "current_sha256": current,
                "pass": exists and current == node.get("sha256"),
            }
        )
    return {
        "pass": not duplicate_nodes and order_ok and all(row["pass"] for row in artifact_rows),
        "duplicate_nodes": duplicate_nodes,
        "acyclic": acyclic,
        "computed_order": computed_order,
        "expected_order": expected_order,
        "topological_order_ok": order_ok,
        "edge_rows": edge_rows,
        "artifact_rows": artifact_rows,
    }


def graph_signature(bundle: dict) -> dict:
    return {
        "nodes": [
            {"id": node["id"], "sha256": node["sha256"], "path": node["path"]}
            for node in sorted(bundle["nodes"], key=lambda row: row["id"])
        ],
        "edges": sorted(bundle["edges"], key=lambda row: (row["from"], row["to"], row.get("kind", ""))),
        "topological_order": list(bundle["topological_order"]),
    }


def make_diff_packet(base_bundle: dict, candidate_bundle: dict, reason: str) -> dict:
    base_nodes = {node["id"]: node for node in base_bundle["nodes"]}
    cand_nodes = {node["id"]: node for node in candidate_bundle["nodes"]}
    changed_nodes = []
    for node_id in sorted(set(base_nodes) | set(cand_nodes)):
        base_node = base_nodes.get(node_id)
        cand_node = cand_nodes.get(node_id)
        if base_node != cand_node:
            changed_nodes.append(
                {
                    "id": node_id,
                    "old_sha256": base_node.get("sha256") if base_node else None,
                    "new_sha256": cand_node.get("sha256") if cand_node else None,
                    "status": "modified" if base_node and cand_node else ("added" if cand_node else "removed"),
                }
            )
    base_edges = {json.dumps(edge, sort_keys=True) for edge in base_bundle["edges"]}
    cand_edges = {json.dumps(edge, sort_keys=True) for edge in candidate_bundle["edges"]}
    edge_delta = {
        "added": [json.loads(row) for row in sorted(cand_edges - base_edges)],
        "removed": [json.loads(row) for row in sorted(base_edges - cand_edges)],
    }
    packet = {
        "packet_version": "1.0",
        "reason": reason,
        "changed_nodes": changed_nodes,
        "edge_delta": edge_delta,
        "node_delta_count": len(changed_nodes),
        "edge_delta_count": len(edge_delta["added"]) + len(edge_delta["removed"]),
    }
    packet["sha256"] = stable_sha256(packet)
    return packet


def candidate_bundle(base_bundle: dict, node_id: str, new_hash: str) -> dict:
    bundle = copy.deepcopy(base_bundle)
    for node in bundle["nodes"]:
        if node["id"] == node_id:
            node["old_sha256"] = node["sha256"]
            node["sha256"] = new_hash
            node["update_note"] = "simulated release hash update"
            return bundle
    raise KeyError(node_id)


def validate_update_candidate(candidate: dict, base_bundle: dict, allowlist: dict) -> dict:
    node_id = candidate.get("node_id")
    base_nodes = {node["id"]: node for node in base_bundle["nodes"]}
    node = base_nodes.get(node_id)
    old_hash_ok = bool(node) and candidate.get("old_sha256") == node.get("sha256")
    new_hash_ok = bool(candidate.get("new_sha256")) and candidate.get("new_sha256") != candidate.get("old_sha256")
    rule = allowlist.get(node_id)
    allowlisted = bool(rule) and rule.get("old_sha256") == candidate.get("old_sha256") and rule.get("new_sha256") == candidate.get("new_sha256")
    proposed = candidate.get("proposed_bundle", {})
    shape = validate_bundle_shape(proposed) if proposed else {"pass": False, "edge_rows": []}
    topology_shape_pass = bool(shape.get("topological_order_ok")) and not shape.get("duplicate_nodes")
    edge_unchanged = proposed.get("edges") == base_bundle.get("edges")
    order_preserved = proposed.get("topological_order") == base_bundle.get("topological_order")
    drift_reasons = []
    if not edge_unchanged:
        drift_reasons.append("edge_drift")
    if set(node.get("id") for node in proposed.get("nodes", [])) != set(node.get("id") for node in base_bundle.get("nodes", [])):
        drift_reasons.append("node_drift")
    pass_value = old_hash_ok and new_hash_ok and allowlisted and topology_shape_pass and edge_unchanged and order_preserved and not drift_reasons
    return {
        "pass": pass_value,
        "node_id": node_id,
        "old_hash_ok": old_hash_ok,
        "new_hash_ok": new_hash_ok,
        "allowlisted": allowlisted,
        "shape_pass": topology_shape_pass,
        "candidate_artifact_hash_replacement_required": False,
        "edge_unchanged": edge_unchanged,
        "order_preserved": order_preserved,
        "drift_reasons": drift_reasons,
    }


def make_hashes(paths: list[Path]) -> dict:
    return {
        "algorithm": "sha256",
        "artifacts": [
            {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in paths
            if path.exists()
        ],
    }


def main() -> int:
    if not P26_RESULT.exists():
        raise FileNotFoundError(f"missing P26 result: {P26_RESULT}")

    p26_result = load_json(P26_RESULT)
    p26_hash = sha256_file(P26_RESULT)
    base_bundle = p26_result["contract_bundle"]
    base_shape = validate_bundle_shape(base_bundle)

    input_manifest = {
        "task": "game_p27_contract_bundle_release_packet_review_20260512",
        "source_p26_result": str(P26_RESULT),
        "source_p26_sha256": p26_hash,
        "constraints": [
            "no downloads",
            "no installs",
            "no private uploads",
            "no ChatGPT Pro",
            "no ChatgptREST",
            "no visual QA claim",
            "no mesh-accurate collision claim",
        ],
    }
    write_json(ROOT / "input_manifest.json", input_manifest)

    release_packet = {
        "packet_version": "1.0",
        "release_id": "game_p27_contract_bundle_release_review_20260512",
        "source_p26_sha256": p26_hash,
        "bundle_sha256": stable_sha256(graph_signature(base_bundle)),
        "bundle": base_bundle,
        "topological_order": base_bundle["topological_order"],
        "approval_policy": {
            "requires_old_hash_match": True,
            "requires_new_hash_change": True,
            "requires_allowlisted_node": True,
            "requires_dependency_edges_unchanged": True,
            "requires_topological_order_preserved": True,
        },
        "boundary": "release packet covers local reviewer-contract artifacts only",
    }
    write_json(ROOT / "release_packet.json", release_packet)

    update_node = next(node for node in base_bundle["nodes"] if node["id"].startswith("source_artifact_"))
    new_hash = hashlib.sha256(("p27-allowlisted-update:" + update_node["sha256"]).encode("utf-8")).hexdigest()
    allow_bundle = candidate_bundle(base_bundle, update_node["id"], new_hash)
    allowlist = {update_node["id"]: {"old_sha256": update_node["sha256"], "new_sha256": new_hash}}
    allow_candidate = {
        "candidate_version": "1.0",
        "candidate_id": "allowlisted_hash_update",
        "node_id": update_node["id"],
        "old_sha256": update_node["sha256"],
        "new_sha256": new_hash,
        "proposed_bundle": allow_bundle,
        "allowlist_rule": allowlist[update_node["id"]],
    }
    write_json(ROOT / "allowlisted_update_candidate.json", allow_candidate)

    rejected_bundle = copy.deepcopy(allow_bundle)
    rejected_bundle["edges"].append({"from": update_node["id"], "to": "stale_missing_node", "kind": "stale_edge_counter"})
    rejected_bundle["nodes"].append(
        {
            "id": "orphan_drift_node",
            "path": update_node["path"],
            "sha256": update_node["sha256"],
            "role": "node_drift_counter",
        }
    )
    rejected_candidate = {
        "candidate_version": "1.0",
        "candidate_id": "rejected_stale_edge_node_drift",
        "node_id": update_node["id"],
        "old_sha256": update_node["sha256"],
        "new_sha256": new_hash,
        "proposed_bundle": rejected_bundle,
        "expected_rejection": ["edge_drift", "node_drift"],
    }
    write_json(ROOT / "rejected_update_candidate.json", rejected_candidate)

    graph_diff = {
        "packet_version": "1.0",
        "baseline_to_allowlisted": make_diff_packet(base_bundle, allow_bundle, "allowlisted hash-only update"),
        "baseline_to_rejected": make_diff_packet(base_bundle, rejected_bundle, "stale edge and node drift"),
    }
    graph_diff["sha256"] = stable_sha256(graph_diff)
    write_json(ROOT / "graph_diff_packet.json", graph_diff)

    allow_validation = validate_update_candidate(allow_candidate, base_bundle, allowlist)
    reject_validation = validate_update_candidate(rejected_candidate, base_bundle, allowlist)
    inherited = p26_result.get("checks", {})
    graph_diff_bytes = (ROOT / "graph_diff_packet.json").stat().st_size
    graph_diff_hashable = bool(graph_diff["sha256"]) and graph_diff_bytes < 12000

    result = {
        "batch": "P27-A game contract bundle release packet review",
        "baseline_release_packet": {
            "source_p26_sha256": p26_hash,
            "bundle_sha256": release_packet["bundle_sha256"],
            "topological_order": release_packet["topological_order"],
        },
        "baseline_shape": base_shape,
        "allowlisted_update_validation": allow_validation,
        "rejected_update_validation": reject_validation,
        "graph_diff_packet": {
            "path": str(ROOT / "graph_diff_packet.json"),
            "bytes": graph_diff_bytes,
            "sha256": graph_diff["sha256"],
            "compact": graph_diff_bytes < 12000,
        },
        "checks": {
            "baseline_p26_bundle_loaded": bool(base_shape["pass"]),
            "baseline_topological_order_preserved": bool(base_shape["topological_order_ok"]),
            "allowlisted_update_candidate_accepted": bool(allow_validation["pass"]),
            "rejected_update_candidate_blocked": (not reject_validation["pass"]) and bool(reject_validation["drift_reasons"]),
            "duplicate_node_counter_inherited": bool(inherited.get("duplicate_node_counter_detected")),
            "cycle_counter_inherited": bool(inherited.get("cycle_counter_detected")),
            "missing_artifact_counter_inherited": bool(inherited.get("p25_missing_artifact_counter_inherited")),
            "tampered_hash_counter_inherited": bool(inherited.get("p25_tampered_hash_counter_inherited")),
            "graph_diff_packet_compact_hashable": graph_diff_hashable,
        },
        "boundaries": [
            "Release packet covers local reviewer-contract artifacts only.",
            "This does not claim screenshot/visual QA.",
            "This does not claim mesh-accurate GLB collision.",
            "This does not claim production game quality.",
        ],
    }
    result["overall_pass"] = all(result["checks"].values())
    write_json(ROOT / "validator_result.json", result)

    closeout = [
        "# P27 Game Contract Bundle Release Packet Review",
        "",
        "Status: `P27 complete / lane active / program active`." if result["overall_pass"] else "Status: `P27 failed / lane active / program active`.",
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
            "- Release packet covers local reviewer-contract artifacts only.",
            "- This does not claim screenshot/visual QA.",
            "- This does not claim mesh-accurate GLB collision.",
            "- This does not claim production game quality.",
            "",
            "## P28 Candidate",
            "",
            "- Add a release-bundle promotion ledger with signed-by-local-hash review rows, denylist regression fixtures, and compact reviewer summary.",
        ]
    )
    (ROOT / "closeout.md").write_text("\n".join(closeout) + "\n", encoding="utf-8")

    hashes = make_hashes(
        [
            ROOT / "input_manifest.json",
            ROOT / "run_p27_release_packet_review.py",
            ROOT / "validator.py",
            ROOT / "validator_result.json",
            ROOT / "release_packet.json",
            ROOT / "graph_diff_packet.json",
            ROOT / "allowlisted_update_candidate.json",
            ROOT / "rejected_update_candidate.json",
            ROOT / "closeout.md",
            P26_RESULT,
        ]
    )
    write_json(ROOT / "artifact_hashes.json", hashes)

    print(json.dumps({"overall_pass": result["overall_pass"], "checks": result["checks"]}, indent=2, sort_keys=True))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
