# AI Game Generation Experiment Backlog

## Selection Rules

- Use installed tools and existing model caches first.
- Do not download large models or assets through proxy traffic.
- Each experiment needs three representative inputs and a real output artifact.
- A promoted path must import into an engine or produce a minimal runnable project.

## First-Round Candidate Experiments

| ID | Category | Candidate Path | Machine | Status | Success Evidence |
|---|---|---|---|---|---|
| GAME-E1 | Image-to-3D asset | Preflight TripoSR/TRELLIS/Hunyuan3D for local asset generation, then run the lightest approved path. | HomePC for generation, M9/Yoga for CLI inspection | selected-for-preflight | Cache inventory, mirror plan, mesh file, texture inventory, import report. |
| GAME-E2 | Text-to-scene / level | Generate a small obstacle-course or room scene spec and convert to Godot/Three.js layout. | YogaS2 or M9 CLI | selected | Runnable scene/project and screenshot or build log. |
| GAME-E3 | Engine playable loop | Import generated or procedural assets into Godot/Three.js and implement movement + one interaction. | M9 after GUI health, or YogaS2 CLI/web path | selected | Local runnable prototype and command log. |
| GAME-E4 | Prompt-to-playable agent framework | Inspect OpenGame dependency/model/provider assumptions and determine whether a local no-large-download run is feasible. | YogaS2 for inspection; HomePC if model/runtime is required | selected-for-inspection | Repo inspection report, provider/model dependency table, run/no-run decision. |
| GAME-E5 | Rigging/animation baseline | Record Mixamo/Ready Player Me workflow as hosted baseline; do not upload assets without approval. | Hosted only after approval | reserve | Privacy decision and sample/public asset run plan. |

## Benchmark Inputs

| Input ID | Prompt / Input | Purpose |
|---|---|---|
| GAME-B1 | `A small friendly robot that collects glowing batteries in a workshop maze.` | Tests child-friendly concept, simple character, collectable loop, and mechanical props. |
| GAME-B2 | `A low-poly island obstacle course with three platforms, coins, and one moving hazard.` | Tests level layout, imported/procedural props, and player movement. |
| GAME-B3 | `A tiny space hangar scene with a controllable rover, one pickup item, and a finish pad.` | Tests scene assembly, vehicle/character proxy, and win condition. |

## Decision Vocabulary

- `promote`: strong enough for deeper testing.
- `keep watching`: interesting but not first path.
- `drop`: insufficient quality, maintenance, licensing, or reproducibility.
- `blocked by download`: useful but requires an unapproved large download.
- `blocked by GPU`: cannot run without unavailable runtime or driver change.
- `blocked by license`: unclear or unsuitable use rights.
