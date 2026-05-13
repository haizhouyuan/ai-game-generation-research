# Task: Route F Runtime Registry Gate 006

## Goal

Design and implement the runtime asset registry v3 gate for the Three.js tactical game so final integration cannot silently pass with old procedural placeholders, flat materials, missing provenance, or broken hero assets.

This packet is for implementation and review of gates. It does not claim final assets are ready.

## Host / Runner Recommendation

- Primary host: Mac control plane repo checkout.
- Primary implementer: Codex or Kimi.
- Complex code/review owner: Kimi.
- Visual/final gate critique: Gemini CLI with `gemini-3.1-pro-preview`.
- MiniMax: only for mechanical schema/report formatting or hash manifest verification.
- HomePC GPU: not required unless runtime test needs fresh rendered evidence from generated assets.

## Read-Only Files

- `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`
- `tasks/pubg_like_full_rebuild/README.md`
- `tasks/pubg_like_full_rebuild/registry_v3_schema_mechanical_003.md`
- `tasks/pubg_like_full_rebuild/registry_v3_schema_mechanical_003.minimax_review.txt`
- `tasks/pubg_like_full_rebuild/full_rebuild_parallelization_review_002.gemini_review.txt`
- `tasks/pubg_like_full_rebuild/full_rebuild_parallelization_review_002.kimi_review.txt`
- Existing runtime source files and tests, read-only until the implementer declares an exact code write scope.

## Write Scope

For this dispatch packet, proposed implementation write scope is intentionally narrow and must be confirmed by the controller before edits:

- runtime asset registry v3 schema/config files;
- runtime asset loader/gate files that already own asset registration or GLTF loading;
- test files or scripts for registry validation, material map count, polycount, collision proxy, and browser screenshot evidence;
- `experiments/pubg_like_asset_factory_20260513/runtime_gate_006/` for reports and screenshots.

Expected report outputs:

- `experiments/pubg_like_asset_factory_20260513/runtime_gate_006/registry_gate_report.md`
- `experiments/pubg_like_asset_factory_20260513/runtime_gate_006/evidence/*.png`
- `experiments/pubg_like_asset_factory_20260513/runtime_gate_006/validation/*.json`

## Forbidden Paths

- Do not edit generated asset packets except to read validation metadata.
- Do not replace production assets in this task.
- Do not loosen existing tests or disable runtime errors to make the gate pass.
- Do not add silent procedural fallback for hero rifle, player character, enemy character, or mission-critical assets.
- Do not change global dev server, proxy, Homebrew, SSH, or machine settings.
- Do not claim final playable-slice completion.

## Required Gate Behavior

Registry v3 must fail closed for hero and mission-critical assets:

- missing registry entry: fail;
- missing `model/optimized.glb`: fail for required final assets;
- missing provenance/reference SHA256: fail;
- `material_map_count < 3` for hero rifle, player character, or enemy character: fail;
- no normal map or no roughness map for hero assets: fail;
- missing Blender cleanup report: fail;
- missing polycount report: fail;
- polycount over budget: fail unless explicitly marked `probe_only`;
- missing collision proxy for gameplay-colliding meshes: fail;
- animation gate missing for skinned character assets: fail;
- runtime GLB load error: fail visible gate, not silent fallback.

Initial triangle budgets:

- props / loot / clutter: `< 5000` tris;
- hero rifle: `< 15000` tris;
- characters: `< 50000` tris;
- environment ground plane: `< 2000` tris.

## Concrete Commands / Placeholders

First inspect repo scripts and package manager:

```bash
pwd
rg --files
rg -n "GLTFLoader|asset registry|registry|MeshStandardMaterial|procedural|fallback|gltf|three" .
find . -maxdepth 3 -iname 'package.json' -o -iname 'vite.config.*' -o -iname 'playwright.config.*'
```

Run existing checks before edits:

```bash
# Placeholder. Use the repo's actual commands.
npm test
npm run lint
npm run build
```

Implement gate, then run focused validation:

```bash
# Placeholder examples. Replace with actual scripts/tests created or found.
node tools/validate_asset_registry_v3.mjs experiments/pubg_like_asset_factory_20260513/assets
npm run test -- --runInBand
npm run build
```

Browser evidence gate:

```bash
# Placeholder. Use the repo's actual dev command and browser/CDP/Playwright script.
npm run dev -- --host 127.0.0.1 --port <PORT>
npx playwright test <RUNTIME_GATE_TEST>
```

Gemini review command, if sending a read-only critique:

```bash
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-gemini-review \
  --model gemini-3.1-pro-preview \
  --input tasks/pubg_like_full_rebuild/route_f_runtime_registry_gate_006.md
```

## Expected Artifacts

- Registry v3 schema or config with required fields:
  - `asset_id`;
  - `asset_class`;
  - `required_for_final`;
  - `generator_route`;
  - `reference_sha256`;
  - `model.optimized_glb`;
  - `textures.basecolor`;
  - `textures.normal`;
  - `textures.roughness`;
  - `textures.metallic` or `textures.ao`;
  - `material_map_count`;
  - `blender_cleanup_report`;
  - `polycount.triangles`;
  - `collision_proxy`;
  - `animation_gate` for skinned characters;
  - `evidence.threejs_closeup`;
  - `evidence.gameplay_context`.
- Validator or runtime assertions enforcing the gate.
- Focused tests showing pass/fail behavior for missing maps, missing provenance, over-budget polycount, and hero fallback.
- Browser or Playwright screenshot evidence for at least a mock or probe registry scene.
- Report explaining what still uses placeholders and why that means final completion is not met yet.

## Acceptance Gate

Pass if all are true:

- Registry v3 required fields are documented and machine-validated.
- Hero and mission-critical assets fail closed when GLB, provenance, PBR maps, cleanup report, or material map count are missing.
- Polycount and collision-proxy checks exist.
- Character animation gate is represented, even if current assets are not ready.
- Runtime test or browser evidence proves a missing hero asset does not silently fall back to old procedural visuals.
- Existing build/test commands are run and results are recorded, or exact blockers are reported.

Fail if any are true:

- The change only creates a schema document with no validation path.
- Runtime still hides missing hero assets behind old procedural placeholders.
- `material_map_count = 0` can pass for final hero assets.
- The task claims asset production is complete.

## Output Summary Format

Write `registry_gate_report.md` with:

````markdown
# Route F Runtime Registry Gate 006 Summary

## Verdict
implemented | partially_implemented | blocked | review_only

## Host And Runner
- Host:
- Runner:

## Files Changed
- ...

## Commands Run
```bash
<exact commands and pass/fail results>
```

## Gates Enforced
- provenance/reference SHA256:
- material map count:
- fail-closed hero loading:
- polycount:
- collision proxy:
- animation:
- browser evidence:

## Evidence
- validation JSON:
- screenshots:
- test logs:

## Known Non-Completion
- ...

## Next Delegation
- Kimi:
- Gemini:
- MiniMax:
- HomePC GPU:
````
