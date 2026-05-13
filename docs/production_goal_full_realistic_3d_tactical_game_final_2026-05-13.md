# Production Goal: Full Realistic 3D Tactical Game Asset Completion - 2026-05-13

## Objective

Finish the tactical compound survival game so that it looks like a high-completion realistic 3D game, not a prototype with a few upgraded assets.

The current derivative at `experiments/tactical_game_realism_upgrade_20260513/index.html` is only a starting point. It must not be treated as the final result. The final deliverable must make the whole visible game feel materially realistic: weapons, characters, tactical gear, loot, buildings, terrain props, lighting, shadows, scale, and composition must all work together.

## Source And Current Starting Point

- Original game: `/Users/yuanshaochen/Documents/14.html`
- Current upgraded derivative seed:
  - `/Users/yuanshaochen/Projects/ai-game-generation-research/experiments/tactical_game_realism_upgrade_20260513/index.html`
- Existing local weapon references:
  - `/Users/yuanshaochen/Documents/枪械模型包/`
  - `/Users/yuanshaochen/Documents/groza_high_detail_3d_model_viewer.html`
- Existing first-pass documentation:
  - `/Users/yuanshaochen/Projects/ai-game-generation-research/docs/realistic_asset_completion_audit_2026-05-13.md`
  - `/Users/yuanshaochen/Projects/ai-game-generation-research/docs/tactical_game_asset_inventory_2026-05-13.md`

## Non-Negotiable Target

The final game must look realistic as a whole. It is not enough to:

- integrate one hero weapon;
- add procedural boxes with better names;
- document limitations instead of resolving them;
- say "deferred" for major visible asset classes;
- pass static tests while the game still visually reads as a prototype.

Completion requires the major visible asset classes to be genuinely upgraded, visually verified, and playable in the game.

## Execution Method

Use subagent-driven development.

The orchestrator should mainly:

- split independent asset classes into parallel work packages;
- dispatch subagents or local runner wrappers for research, generation, cleanup, integration, and review;
- review outputs against visual quality gates;
- maintain manifests, evidence, and final acceptance status.

Use local and API-backed tools where useful:

- Blender for cleanup, normalization, UV/material assignment, renders, and GLB export;
- TRELLIS / Hunyuan3D / TripoSR / Rodin / Hyper3D or equivalent routes for generated 3D assets;
- Gemini CLI, Claude Code, Kimi, MiniMax, and local runner wrappers for coding/research work when configured;
- browser/CDP evidence gates for final playable validation.

Do not expose or commit API keys.

## Download And Network Policy

Downloads are allowed when useful, but large downloads must not burn paid proxy traffic.

- Any single external download over 100 MB must use command-local no-proxy configuration and record connection evidence.
- Any single external download over 1 GB requires explicit approval for the exact URL/package/version/size before execution.
- Prefer cached local models and already-installed tools when they are adequate.
- Do not modify global proxy settings casually.

## Final Asset Quality Bar

Each visible asset class must meet these standards:

- Game-ready GLB/GLTF or equivalent in-engine asset, not a rough placeholder.
- Correct scale, orientation, origin, and mounting anchors.
- Materials must look believable under the game lighting.
- PBR-style material data, texture maps, baked/painted detail, or a documented equivalent must exist for all important assets.
- Hidden proxy/collider geometry is allowed, but visible gameplay assets must not look like simple primitive boxes/capsules.
- Each asset class must have before/after screenshot evidence and a mesh/material report.

## Required Work Packages

### W1: Tooling And Runner Readiness

- Inspect and document current local runner state for Claude Code, Gemini CLI, Kimi, MiniMax, and relevant MCP/skill configuration.
- Confirm which asset generation routes work locally without new large downloads.
- Confirm which routes require API calls or large downloads.
- Produce a short runner/tooling readiness report with working commands and blocked routes.

Exit criteria:

- At least one working local generation/cleanup pipeline is proven end-to-end.
- At least one fallback manual Blender cleanup route is proven.
- Any unavailable route is documented with concrete blocker, not handwaving.

### W2: Full Asset Inventory And Acceptance Matrix

Create a matrix covering every major visible class:

- first-person weapons;
- third-person/player/NPC weapons;
- player body;
- NPC body;
- helmet;
- armor/plate carrier;
- backpack, pouches, straps, rig, gloves, pads;
- ammo, med items, revive item, armor/helmet pickups;
- crates and storage props;
- containers;
- ladders/stairs;
- rocks;
- trees/bushes/grass;
- building exteriors;
- building interiors;
- doors/windows/vents/pipes/utility details;
- ground/roads/walls/fences;
- lighting, sky, fog, shadow configuration.

For each class record:

- current state;
- target realism level;
- generation/acquisition route;
- cleanup route;
- integration file/function;
- evidence files required;
- acceptance status.

Exit criteria:

- No major visible class is missing from the matrix.
- The matrix becomes the source of truth for completion.

### W3: Weapon Asset Completion

Upgrade all player-visible and world-visible weapons to game-ready realistic assets:

- pistol;
- shotgun;
- rifle/GROZA/TAC-AR;
- DMR.

Each weapon must have:

- GLB/GLTF asset;
- PBR-style materials or texture maps;
- muzzle anchor;
- grip/mount anchor where needed;
- first-person placement;
- third-person mount;
- loot/world display placement;
- NPC mount placement;
- Blender render;
- in-game screenshot in first-person, third-person, NPC/world, and loot contexts.

Exit criteria:

- The four weapon slots no longer rely on visible procedural fallback in normal gameplay.
- Browser evidence proves all weapon assets load and mount without runtime errors.
- Visual screenshots show the weapon clearly, not only a runtime probe.

### W4: Character And Tactical Gear Completion

Replace prototype character silhouettes with believable tactical characters.

Required visible elements:

- head/helmet/visor;
- torso/body shape;
- arms/hands/gloves;
- legs/boots;
- plate carrier or armor vest;
- pouches and straps;
- backpack or tactical rig;
- shoulder/knee/shin pads;
- enemy/player visual distinction.

Acceptable approaches:

- generated character/gear GLBs cleaned in Blender;
- modular GLB gear pieces mounted on existing skeleton-like groups;
- a hybrid where only hidden hitboxes remain primitive and all visible parts are realistic.

Not acceptable:

- visible capsule/sphere/block characters as the final state;
- only adding tiny boxes to a capsule body and calling it complete.

Exit criteria:

- Player and NPC silhouettes read as tactical humans at gameplay camera distance.
- At least three representative screenshots prove player, NPC, and close gear readability.
- Hit detection and NPC behavior still work.

### W5: Loot And Pickup Props Completion

Make pickups read as real objects, not colored placeholders.

Required props:

- ammo box or magazines/rounds;
- bandage;
- first-aid kit;
- medkit;
- revive item;
- armor vest pickup;
- helmet pickup;
- weapon pickup presentation.

Each prop must have:

- readable model shape;
- believable material;
- stable pickup label and interaction behavior;
- before/after evidence.

Exit criteria:

- In-game screenshots show each loot family clearly.
- Pickup behavior is unchanged and verified.

### W6: Environment Asset Completion

Upgrade the compound environment so it supports the realistic tactical look.

Required classes:

- buildings: facade panels, windows, doors, trims, vents, pipes, utility boxes, roof details;
- interiors: tables, cabinets, shelves, floor/wall detail, interior lighting;
- containers: corrugation, doors, hinges, warning markings, wear;
- crates/storage props;
- ladders/stairs/railings;
- walls/fences/gates;
- rocks;
- trees/bushes/grass;
- road/ground materials.

Exit criteria:

- Representative screenshots from outdoor, indoor, rooftop/ladder, and loot-area views show a coherent realistic scene.
- No large visible area reads as empty prototype geometry.
- Performance remains playable.

### W7: Lighting, Camera, And Composition Pass

Tune the overall look after assets are integrated.

Required:

- lighting direction/intensity/color;
- shadows;
- ambient/fog/sky;
- material response under day/sunset/night modes if modes remain;
- first-person weapon framing;
- third-person readability;
- screenshot viewpoints for evidence.

Exit criteria:

- The final screenshots look intentionally composed, not just technically loaded.
- Weapon and character assets are visible enough to judge.
- No UI/text blocks obscure the evidence screenshots used for final acceptance.

### W8: Integration And Playability Preservation

Preserve the actual game.

Must still work:

- start/restart;
- movement;
- camera switch;
- crouch/prone/jump;
- weapon switching;
- shooting, reload, recoil, muzzle effects;
- NPC spawn, movement, damage, death;
- loot pickup;
- ladder/floor movement;
- health/revive;
- skins/settings panels if retained.

Exit criteria:

- Browser/CDP smoke test exercises core gameplay without blocking console errors.
- No missing asset loads.
- No runtime exceptions.
- No obvious severe performance regression.

### W9: Evidence Packet And Final Acceptance

Produce a final evidence packet:

- final playable HTML/game artifact;
- asset inventory matrix with status complete for every class;
- GLB/texture/material manifest;
- hash manifest;
- Blender renders for generated/imported assets;
- in-game before/after screenshots;
- first-person weapon screenshots;
- third-person player/NPC screenshots;
- loot screenshots;
- indoor/outdoor environment screenshots;
- CDP/browser reports with no blocking events;
- final limitation note for genuinely minor issues only.

Exit criteria:

- A reviewer can open the evidence packet and see that the whole game, not just one asset, reached the target look.

## Completion Criteria

This goal is complete only when all of the following are true:

- The final playable upgraded game exists under a clearly named experiment directory.
- The original game is either safely preserved or replaced only by explicit user request.
- All four weapon slots are realistic GLB/in-engine assets in first-person, third-person, NPC/world, and loot contexts.
- Player and NPC visible bodies and gear no longer look like capsule/block prototypes.
- Loot props are realistic/readable.
- Environment classes listed in W6 are upgraded enough that representative screenshots look like a coherent tactical compound.
- Lighting/camera/material tuning supports the realistic look.
- The game is playable locally without blocking browser errors or broken core interactions.
- A complete evidence packet exists with screenshots, mesh/material reports, hash manifests, and browser validation.
- Any remaining limitations are minor polish notes, not missing major asset classes.

## Explicit Non-Completion Conditions

Do not mark this goal complete if any of these are true:

- A major visible class is only documented as deferred.
- Visible characters still look like primitive capsules/spheres/boxes.
- Environment realism depends mostly on flat colored boxes.
- Only one or two hero assets are upgraded.
- Runtime probes pass but screenshots do not visibly show the upgraded assets.
- Browser reports contain blocking runtime exceptions, missing asset loads, or broken controls.
- The final answer says "first pass", "partial", "prototype", or "deferred major class".

## Final User-Facing Summary Requirement

When complete, explain in plain Chinese:

- what final playable file to open;
- what asset classes were upgraded;
- where the evidence packet is;
- what commands passed;
- what minor limitations remain;
- why this is now the full target effect, not merely one step.
