# MiniMax Task: Registry V3 Schema Mechanical Draft 003

## Goal

Draft a mechanical JSON-style schema outline for runtime asset registry v3.

## Context

The project is rebuilding a Three.js tactical game with generated/PBR asset packets. Completion gates now require:

- provenance/reference image tracking;
- PBR texture maps;
- generated route details;
- Blender cleanup reports;
- Three.js evidence screenshots;
- polycount/performance gates;
- collision proxy gates;
- PBR consistency gates;
- fail-closed behavior for hero assets.

## Ask

Produce a concise schema outline with required fields and validation notes. Do not edit files. Focus on mechanical completeness, not architecture judgment.

## Output

Return markdown with:

- top-level registry fields;
- per-asset required fields;
- per-texture fields;
- per-evidence fields;
- validation checks.
