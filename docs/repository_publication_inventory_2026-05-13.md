# Repository Publication Inventory - 2026-05-13

This repository is the public-facing workspace for the AI game generation research run.

## Included in the repository

- Research and planning documents under `docs/`.
- Managed-agent controller code, schemas, scenarios, tools, and tests under `src/`, `schemas/`, `scenarios/`, `tools/`, and `tests/`.
- Reproducible experiment sources under `experiments/`.
- The final tactical game realism packet under `experiments/tactical_game_full_realism_final_20260513/`, including:
  - playable `index.html`;
  - source snapshot `source/14.html`;
  - final GLB assets and preview PNGs;
  - CDP evidence screenshots and report JSON files;
  - asset registry, inventory matrix, and hash manifest.

## Kept local only

These files are intentionally ignored for public GitHub publication:

- `external/downloads/`: large installer downloads such as Blender, Unity Hub, and UI-TARS DMGs.
- `external/research_sources/`: third-party source archives or cloned research references.
- `external/chatgpt_app_extracts/`: raw/private transcript extracts.
- local runtime state such as `.venv/`, caches, `node_modules/`, and `.managed_codex/`.

## Notes

The public repository should preserve enough material to reproduce the final browser evidence and audit the research decisions, without publishing local credentials, raw private transcripts, package caches, or large binary installers.
