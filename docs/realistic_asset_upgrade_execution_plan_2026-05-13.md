# Realistic Asset Upgrade Execution Plan - 2026-05-13

Source goal: `docs/production_goal_realistic_3d_assets_for_tactical_game_2026-05-13.md`

## Plain Target

Upgrade the existing tactical compound survival game at `/Users/yuanshaochen/Documents/14.html` so its visible 3D assets look much more realistic and production-complete. Preserve the playable loop; the asset pipeline is the product.

## Current Findings

- `/Users/yuanshaochen/Documents/14.html` is a self-contained Three.js game.
- It currently creates nearly all visible 3D content procedurally in JavaScript.
- `/Users/yuanshaochen/Documents/枪械模型包/` contains OBJ/MTL weapon prototypes, but its README explicitly says they are low/mid-poly prototype models, not scan-grade realistic assets.
- `/Users/yuanshaochen/Documents/groza_high_detail_3d_model_viewer.html` contains a separate high-detail procedural GROZA-style reference viewer and is the strongest local visual direction for the first hero weapon.

## First Hero Asset

Start with a **GROZA / TAC-AR style rifle GLB** attached to the `rifle` weapon slot.

Why:

- The rifle is the most visually valuable asset class because it appears in first-person view, third-person player view, NPC hands, and ground loot.
- It can show high-value realism details: metal receiver, wood/polymer grip, rails, magazine curvature, muzzle, wear, roughness, small screws, and material contrast.
- The existing game already has well-defined weapon mount points and muzzle-dependent gameplay logic.

## Implementation Tracks

### Track A: Runner And Tooling

Use the local runner workspace at `/Users/yuanshaochen/Projects/local-coding-runners`.

Current verified local state:

- Claude MiniMax wrapper works.
- Claude Kimi wrapper exists.
- Gemini CLI works.
- `managed-artifact-verifier` MCP is connected for Claude MiniMax, Claude Kimi, and Gemini.
- Do not copy YogaS2 MCP configuration wholesale; YogaS2 contains machine-local services and `/vol1/...` paths that do not map to M1.

Use YogaS2 as a reference source only:

- reusable: separate `CLAUDE_CONFIG_DIR` per provider, provider base URL mapping, private credential env pattern, trust/onboarding idea;
- not reusable directly: remote localhost MCP services, `/vol1` paths, Chrome debug ports, maint-specific wrappers.

### Track B: Asset Generation

Preferred first route:

1. Create or select a high-quality rifle/GROZA reference image.
2. Use the already-proven TRELLIS image-to-mesh route on HomePC/Yoga/HomePC-compatible environment if available without new large downloads.
3. Treat the TRELLIS output as mesh/silhouette input, not as final production PBR.
4. Use Blender on M1 for cleanup, scale/origin/orientation normalization, material slots, UV/texture handling, collision proxy, and GLB export.
5. Use Three.js GLB parser/viewer evidence to validate geometry and materials.

Fallback/parallel candidates:

- TripoSR: fast baseline, useful for comparison but not final if visual quality is weak.
- Hunyuan3D-2.1: promising PBR route, but likely requires large weights/VRAM and must go through no-proxy and approval gates before downloads.
- Rodin/Hyper3D: fast cloud/API comparison route, but has cost/API/reproducibility/provenance concerns.
- Pure Blender/manual modeling: most controllable, but highest manual labor.

### Track C: Game Integration

Integrate the rifle GLB into a controlled derivative of `/Users/yuanshaochen/Documents/14.html`, not by destructively overwriting the original.

Key code areas:

- `createGunModel(type, skinful)`: wrap or replace for GLB-backed rifle with procedural fallback.
- `rebuildGuns()`: first-person and third-person gun mounting.
- `spawnLootAt()`: ground-loot weapon preview.
- enemy creation: NPC weapon mount.
- `fireWeapon()`: preserve `userData.muzzle` or equivalent muzzle node so fire, tracers, muzzle flashes, and obstruction checks stay aligned.

Required runtime checks:

- GLB load success and fallback behavior.
- First-person ADS and hip-fire framing.
- Third-person hand/mount alignment.
- NPC muzzle origin.
- Ground loot scale.
- Shadows/materials.
- No broken core controls or major performance regression.

## Evidence Packet For Hero Rifle

Create a dated evidence directory containing:

- input reference image and prompt/provenance;
- raw candidate outputs from each attempted generation route;
- selected raw mesh/GLB;
- Blender cleanup report and screenshot;
- cleaned GLB and optional textures;
- Three.js parse report with bbox, triangle count, material count, texture count;
- browser screenshots of asset viewer and in-game first/third person;
- `artifact_hashes.json`;
- limitations note.

## Completion Order

1. Lock runner/tooling evidence.
2. Build asset inventory and select rifle hero asset.
3. Generate at least three candidate rifle assets or document why a candidate route was skipped.
4. Clean the best candidate in Blender.
5. Build standalone rifle GLB viewer.
6. Integrate into the game derivative.
7. Run browser evidence gate.
8. Repeat for remaining high-impact assets after hero rifle proof is strong.

## Download Policy

Downloads are allowed, but large downloads must not use paid proxy traffic.

- Over 100 MB: command-local no-proxy and connection evidence required.
- Over 1 GB: explicit approval for exact source/version/size before download.
- Do not change global proxy state casually.

## Current Status

M1/M2 are partially satisfied:

- runner wrappers exist and one local MCP surface is connected;
- YogaS2 config has been analyzed at the pattern level;
- the asset inventory is known at a useful first-pass level;
- the first hero asset is selected.

M3-M6 remain open:

- no new realistic rifle asset has been generated yet;
- no Blender cleanup has been run for the rifle yet;
- no in-game rifle replacement exists yet;
- full visible asset upgrade pass is not started.
