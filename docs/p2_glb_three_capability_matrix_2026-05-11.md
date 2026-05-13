# Game P2 GLB/Three.js Capability Matrix - 2026-05-11

Status: `P2 safe batch complete / program active`

## Matrix

| Path | Local Status | Formats / Runtime Verified | Benchmark Count | Artifact Evidence | Capability | Boundary |
|---|---|---|---:|---|---|---|
| HomePC procedural GLB generation | pass | GLB | 3 | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p2_glb_three_import_loop/outputs/assets/` | Produces local 3D assets without model download. | Not image-to-3D inference. |
| Three.js GLB import loop | pass | GLB via `GLTFLoader`, browser playable loop | 3 | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p2_glb_three_import_loop/outputs/verification/` | Imports assets into a playable loop with pickups/hazards/finish state. | Not Godot/Unity/Unreal. |
| Godot | environment-plan only | none | 0 | YogaS2/HomePC probes show not installed. | Candidate for child-friendly engine workflow and native import test. | Requires system package/install approval. |
| image-to-3D models | not started in P2 safe batch | none | 0 | Source registry exists. | Required for frontier asset-generation question. | Requires no-proxy/cache/mirror model plan before weights. |

## Installation Plan Notes

| Tool | YogaS2 Probe | HomePC Probe | Recommendation |
|---|---|---|---|
| Godot 3 | Missing; Debian candidate `3.2.3`; simulated install: 4 packages, installed-size around 64MB for core package. | Missing; Ubuntu candidate `3.2.3`; simulated install: 2 packages, installed-size around 63MB for core package. | Prefer HomePC if approved; still treat as system install requiring approval. |
| Godot 4 | No apt candidate found in current probes. | No apt candidate found in current probes. | Use official binary/AppImage only after approval and checksum plan. |
| Three.js | pass | `three@0.181.2`, `node_modules` about 37M. | Keep local control path. |

## Evidence

- Experiment report: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p2_glb_three_import_loop/report.md`
- Asset inventory: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p2_glb_three_import_loop/outputs/glb_asset_inventory.json`
- Verification screenshots: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p2_glb_three_import_loop/outputs/verification/`
- Failure ledger: `/vol1/1000/projects/ai-game-generation-research/experiments/game_p2_glb_three_import_loop/failure_ledger.md`

## Next Recommendation

Proceed to Godot import only after system-install approval. Keep image-to-3D model experiments queued until no-proxy model download plans are approved.
