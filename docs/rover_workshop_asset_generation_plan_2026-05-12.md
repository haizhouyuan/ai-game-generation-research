# Rover Workshop Asset Generation Plan - 2026-05-12

## Purpose

This plan turns the P1 design spec for **Rover Workshop: Battery Rescue** into an asset-generation workflow that can be run by managed agents without losing provenance, download discipline, or engine validation.

The goal is not to produce every final asset in one pass. The goal is to define a repeatable chain:

`P1 design spec -> OpenAI image references -> 3D generation candidates -> Blender cleanup -> Three.js validation -> release evidence`

P1 should remain a compact, child-friendly Three.js demo first. Unity is a later promotion path once the Unity MCP/editor lane has local evidence.

## Source Inputs

- P1 design spec: `docs/game_p1_child_friendly_design_spec_2026-05-12.md`
- Best-practices matrix: `docs/current_best_practices_matrix_2026-05-12.md`
- Download boundary: `docs/direct_download_policy_2026-05-12.md`

## Production Rules

1. Preserve the original `14.html` as baseline inspiration only.
2. Do not treat one-shot generated assets as production-ready.
3. OpenAI image generation is the first art direction step.
4. GLB is the interchange format for playable P1 assets.
5. Three.js/GLTFLoader is the first runtime validation gate.
6. Blender cleanup is required before calling a generated mesh demo-ready.
7. Generated meshes are never used directly as gameplay collision. Use simple procedural collider proxies.
8. Every non-procedural asset must have provenance, hashes, limitations, and import/readback evidence.
9. No large downloads or model acquisition happen inside this plan. Future downloads must follow the no-proxy policy.

## Style Direction

The visual target is a friendly, toy-like workshop maze:

- rounded rover shapes;
- chunky readable silhouettes;
- soft plastic, rubber, enamel, brushed metal, and glowing glass materials;
- saturated but not harsh colors;
- warm workshop lighting with cyan/yellow objective glows;
- no guns, humanoid enemies, gore, horror, or realistic danger;
- hazards read as playful machines, sparks, moving carts, closing gates, or soft bumpers.

Recommended palette:

| Token | Use | Color note |
| --- | --- | --- |
| Workshop blue | walls, floor accents | calm mid blue |
| Safety yellow | batteries, gates, warning trim | warm yellow |
| Rover teal | player identity | friendly teal |
| Energy cyan | scans, pickup trails, charging beam | bright cyan |
| Gear orange | optional tokens, upgrade station | clear reward color |
| Soft graphite | rubber wheels, shadows, outlines | neutral dark |

Avoid a single-hue theme. The scene should read as a varied workshop, not a blue/purple gradient environment.

## OpenAI Image Prompt Packet

Use OpenAI image generation for references, style sheets, orthographic views, icons, and texture guides. These prompts are designed to produce downstream inputs for TRELLIS, TripoSR, Hunyuan3D, Blender cleanup, and UI implementation.

All generated images must record model, prompt, date, output path, SHA256, operator, and downstream use.

### IMG-001 Art Bible Sheet

Purpose: establish the whole game's visual language.

Prompt:

```text
Create a clean game art bible sheet for a child-friendly 3D browser game titled "Rover Workshop: Battery Rescue". Show a compact colorful workshop maze with a friendly small rover, glowing batteries, a charging pad, soft cleaning bots, spark floor tiles, gates, shelves, ramps, workbenches, UI icons, material swatches, and lighting references. Style: premium toy-like 3D game assets, rounded shapes, readable silhouettes, warm workshop lighting, cyan energy glows, yellow safety accents, teal rover identity, orange gear rewards. No weapons, no humanoid enemies, no violence, no scary mood. White or light neutral background, organized layout, labels optional but not required, high clarity for asset production.
```

Expected output:

- one overview sheet;
- usable as style reference, not direct 3D generation input;
- must show rover, battery, cleaning bot, charging pad, spark tile, and UI icon direction.

### IMG-002 Rover Orthographic Reference

Purpose: primary input for image-to-3D candidates.

Prompt:

```text
Orthographic model reference sheet for a friendly small workshop rover character for a child-friendly 3D game. Include front view, side view, back view, and top view of the same rover. Design: compact rounded body, four chunky rubber wheels, tiny antenna, expressive headlight eyes, teal shell, soft graphite tires, cyan lamp lens, small orange tool module, toy-like materials, simple clean silhouette, no weapons, no text, no background clutter, consistent proportions across views, high contrast on a light neutral background.
```

Expected output:

- front/side/back/top views;
- same proportions across views;
- first candidate for TRELLIS, TripoSR, and Hunyuan3D comparison.

### IMG-003 Battery Orthographic Reference

Purpose: required collectible and icon source.

Prompt:

```text
Orthographic reference sheet for a glowing collectible battery capsule for a child-friendly 3D workshop exploration game. Include front, side, top, and three-quarter views. The asset is palm-sized, rounded rectangular capsule shape, yellow outer shell, cyan glowing core, small safety stripes, simple readable silhouette, toy-like PBR material suggestion, no text, no logo, no brand, light neutral background, clean production reference style.
```

Expected output:

- candidate for procedural version, UI icon, and image-to-3D test;
- must remain recognizable at small size.

### IMG-004 Cleaning Bot Orthographic Reference

Purpose: nonviolent moving hazard.

Prompt:

```text
Orthographic reference sheet for a friendly cleaning bot hazard in a child-friendly 3D workshop maze. Include front, side, back, top, and three-quarter views. Shape: low rounded robot vacuum with soft bumper ring, small brush rollers, sleepy indicator light, no face aggression, no weapons, no sharp parts. Color: white shell, teal/cyan lights, safety yellow bumper, graphite wheels. Toy-like 3D game asset style, readable silhouette, clean light background, consistent proportions across views.
```

Expected output:

- used first as visual reference;
- procedural placeholder is acceptable until generated GLB passes validation.

### IMG-005 Charging Pad Orthographic Reference

Purpose: finish object and strong visual reward.

Prompt:

```text
Orthographic reference sheet for a circular charging pad finish object for a child-friendly rover workshop game. Include top, side, front, and three-quarter views. Design: round platform with concentric glowing cyan rings, yellow safety trim, small cable sockets, soft beveled edges, toy-like materials, activated and inactive states shown side by side, no text, light neutral background, clean production reference style.
```

Expected output:

- supports both procedural build and possible generated GLB;
- must show inactive/active state language.

### IMG-006 Upgrade Station Reference

Purpose: progression object.

Prompt:

```text
3D game asset reference sheet for a small rover upgrade station in a friendly workshop. Show a waist-high workbench console with rounded edges, glowing tool slots, magnetic coil icon shape, lamp upgrade lens, orange gear-token receptacle, teal and yellow accents, before and after activation states, toy-like PBR materials, child-safe no sharp edges, no text, clean light background, three-quarter plus side view.
```

Expected output:

- likely procedural blockout plus texture/material style;
- may become GLB if high-quality generation is available.

### IMG-007 Workshop Prop Style Sheet

Purpose: environment prop pack direction.

Prompt:

```text
Style sheet of modular workshop props for a child-friendly 3D rover exploration game: shelves, workbenches, ramps, gates, soft barriers, cable bridges, crates, floor panels, spark tiles, pressure pads, arrows, and small tools. Chunky rounded toy-like shapes, readable silhouettes, warm workshop lighting, teal, yellow, orange, cyan accents, soft graphite shadows, no clutter that blocks gameplay readability, no text required, organized on a neutral background as production references.
```

Expected output:

- guides procedural modeling and Blender cleanup;
- identifies repeated material families.

### IMG-008 UI And Icon Sheet

Purpose: HUD icons and feedback visual language.

Prompt:

```text
Flat and slightly dimensional UI icon sheet for a child-friendly rover workshop game. Include icons for battery count, energy meter, gear token, magnet upgrade, lamp upgrade, cosmetic decal, checkpoint, warning spark tile, cleaning bot, switch, charging pad, finish badge, replay button, assist mode. Style: rounded, high readability, teal/yellow/orange/cyan palette, clean vector-like shapes, consistent stroke weight, transparent or light background, no brand logos, no tiny unreadable text.
```

Expected output:

- used for HUD/icon extraction;
- can become CSS sprites, SVG recreation, or texture atlas.

### IMG-009 Texture And Material Reference Sheet

Purpose: material language for Blender/Three.js.

Prompt:

```text
Material reference sheet for a toy-like 3D workshop game. Show seamless or tileable material ideas for soft rubber tires, teal painted plastic rover shell, brushed safe metal, yellow safety trim, cyan glowing glass, orange gear token enamel, workshop floor panels, spark tile emissive patterns, and padded bumper material. Clean organized swatches, PBR-friendly notes visually implied through roughness/metallic look, no text required, light neutral background.
```

Expected output:

- not used as literal production textures until checked for tiling and seams;
- guides procedural material parameters and optional texture generation.

## Asset Pipeline Map

Decision labels:

- **Procedural**: build directly in Three.js or Blender using primitives/materials.
- **OpenAI image**: generate art/reference/icon/texture images.
- **TRELLIS**: primary mesh-quality candidate from image reference; current baseline is mesh-only until textured path is proven.
- **TripoSR**: fast geometry fallback and comparison baseline.
- **Hunyuan3D**: textured/PBR candidate to probe after validators are stable.
- **Blender cleanup**: normalize scale, origin, orientation, material naming, decimation decision, collider proxy, screenshot, GLB export.
- **Three.js validation**: GLTFLoader parse, bbox, materials, texture presence, render screenshot, playable import.

| Asset ID | Asset | P1 role | First-pass source | 3D candidate path | Cleanup path | Runtime validation | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RW-ROVER-001 | Friendly rover | Player avatar | OpenAI orthographic reference | TRELLIS + TripoSR comparison; Hunyuan3D if textured assets are stable | Blender scale/origin/orientation, wheel silhouette cleanup, simple collider capsule/box | Three.js GLB parse, bbox, nonblank screenshot, camera-follow readability | Highest-priority hero GLB |
| RW-BATT-001 | Glowing battery | Required collectible | Procedural first + OpenAI reference | Optional TRELLIS/TripoSR comparison | Blender optional bevel/material cleanup | Three.js pickup animation, emissive material proof | Must be readable at small size |
| RW-BOT-001 | Cleaning bot | Moving hazard | Procedural first + OpenAI reference | TRELLIS/TripoSR after gameplay placeholder works | Blender scale, low-poly cleanup, soft bumper material | Three.js patrol path, contact feedback, bbox proxy | Non-threatening design required |
| RW-PAD-001 | Charging pad | Finish object | Procedural first + OpenAI reference | Optional Hunyuan3D/TRELLIS if style needs upgrade | Blender material/emissive rings | Three.js active/inactive state screenshot | Procedural may be production enough |
| RW-UPG-001 | Upgrade station | Progression object | Procedural blockout + OpenAI reference | TRELLIS/Hunyuan3D if hero prop quality needed | Blender material slots, simplified collision | Three.js activation state, HUD event | Use as second hero prop if rover path blocks |
| RW-SHELF-001 | Shelves/workbenches | Landmarks and occlusion | Procedural modular kit + OpenAI prop sheet | Usually no image-to-3D needed | Blender optional modular GLB pack | Three.js import or procedural scene proof | Keep collision simple and readable |
| RW-RAMP-001 | Ramps | Traversal | Procedural | None | None unless exported as kit | Movement no-snag test | Gameplay collision is source of truth |
| RW-GATE-001 | Gates/doors | Puzzle feedback | Procedural + material style | None first | Blender optional hinge/trim GLB | Open/closed state screenshots | State readability more important than mesh detail |
| RW-SPARK-001 | Spark tiles | Timed hazard | Procedural plane + OpenAI texture/material reference | None first | Optional texture tiling cleanup | Three.js animation, on/off visual proof | Use emissive pattern, not dangerous realism |
| RW-SIGN-001 | Signs/arrows | Guidance | OpenAI UI/texture sheet or procedural decals | None | Texture atlas crop/rebuild if needed | Three.js readability screenshot | No text needed for core navigation |
| RW-UI-001 | Battery icon | HUD | OpenAI icon sheet | None | Crop/recreate as SVG/PNG | HUD screenshot | Must be readable small |
| RW-UI-002 | Energy meter | HUD | Procedural CSS/canvas + icon sheet style | None | None | HUD state test | Avoid tiny text |
| RW-UI-003 | Gear token icon | Optional reward | OpenAI icon sheet + procedural 3D token | Optional battery-like simple GLB | Blender optional bevel/material | Three.js pickup and HUD proof | Orange reward color |
| RW-FX-001 | Pickup glow particles | Feedback | Procedural shader/sprites + OpenAI style | None | None | Pixel/screenshot proof | No heavy texture required |
| RW-FX-002 | Hazard warning ring | Feedback | Procedural ring + style sheet | None | None | Screenshot during hazard | Must be obvious before contact |
| RW-FX-003 | Charging beam | Finish feedback | Procedural light/particles | None | None | Finish screenshot | Strong completion reward |

## Recommended Generation Order

### Batch A - Art Direction

1. Generate IMG-001 art bible sheet.
2. Generate IMG-008 UI/icon sheet.
3. Generate IMG-009 material reference sheet.
4. Review for child-safety, readability, and consistency.
5. Record hashes and choose style tokens.

Acceptance:

- rover, battery, cleaning bot, charging pad, spark tile, and UI direction are visible;
- no combat or scary imagery;
- colors match P1 gameplay readability;
- outputs are stored as references, not silently copied into runtime.

### Batch B - Hero 3D References

1. Generate IMG-002 rover orthographic reference.
2. Generate IMG-003 battery orthographic reference.
3. Generate IMG-004 cleaning bot orthographic reference.
4. Generate IMG-005 charging pad reference.
5. Select one hero asset for first 3D run. Default: rover.

Acceptance:

- front/side/top references are consistent enough for 3D generation;
- images have clean neutral backgrounds;
- reference limitations are recorded.

### Batch C - 3D Candidate Comparison

For the selected hero asset:

1. Run TRELLIS image-to-3D if environment and model cache already exist.
2. Run TripoSR on the same reference as speed/fallback baseline.
3. Probe Hunyuan3D only when dependencies/model availability are already within policy or separately approved.
4. Export candidate GLBs.
5. Compute hashes and mesh stats.
6. Label each output as `mesh-only`, `textured`, `visual-proxy`, or `rejected`.

Acceptance:

- at least one GLB parses in Three.js;
- mesh has sane bbox and orientation;
- material/texture presence is reported honestly;
- collision proxy is separate from generated mesh;
- no generated asset is marked production-ready without Blender and runtime evidence.

### Batch D - Blender Cleanup

For each promoted candidate:

1. Import candidate GLB into a disposable Blender scene.
2. Normalize scale to P1 units.
3. Set origin and forward/up orientation.
4. Inspect mesh density, holes, UVs, materials, texture links, and normals.
5. Create or document simple collider proxy.
6. Assign named materials matching style tokens.
7. Export cleaned GLB.
8. Save viewport screenshot and Blender inspection notes.

Acceptance:

- cleaned GLB has stable origin, scale, and orientation;
- material names are meaningful;
- screenshot shows readable silhouette;
- mesh limitations are still recorded.

### Batch E - Three.js Validation

For each cleaned GLB:

1. Load with GLTFLoader.
2. Record node inventory, mesh count, triangle count if available, materials, textures, animations, bbox, and scale.
3. Render in a minimal Three.js validation scene.
4. Capture screenshot under P1 lighting.
5. Add to P1 asset manifest only after parser and screenshot pass.
6. If used in gameplay, verify interaction state in the playable slice.

Acceptance:

- nonblank render;
- bbox is within expected size range;
- asset is not inverted, invisible, or wildly off-origin;
- material/texture report is explicit;
- gameplay code uses separate collider proxy.

## Provenance Schema

Each non-procedural asset should have a JSON record beside the artifact or in an asset manifest:

```json
{
  "schema_version": "asset_provenance_p1_v0",
  "asset_id": "RW-ROVER-001",
  "asset_name": "Friendly rover",
  "p1_role": "player_avatar",
  "status": "reference|candidate|cleaned|validated|rejected",
  "source": {
    "kind": "openai_image|procedural|trellis|triposr|hunyuan3d|blender|external_source",
    "prompt_id": "IMG-002",
    "prompt_text_path": "docs/rover_workshop_asset_generation_plan_2026-05-12.md",
    "reference_image_path": "assets/references/rover_orthographic.png",
    "reference_image_sha256": "",
    "model_or_tool": "gpt-image-1.5",
    "tool_version": "",
    "operator": "",
    "generated_at": "2026-05-12T00:00:00+08:00"
  },
  "generation": {
    "generator": "TRELLIS-image-large|TripoSR|Hunyuan3D-2.1|Blender|procedural",
    "command_or_notebook": "",
    "host": "Mac|HomePC|YogaS2",
    "input_paths": [],
    "output_paths": [],
    "output_sha256": "",
    "download_evidence_path": "",
    "large_download_approval": "not_required|required|approved|blocked"
  },
  "asset_files": {
    "raw_glb_path": "",
    "cleaned_glb_path": "",
    "preview_image_path": "",
    "texture_paths": [],
    "material_report_path": "",
    "mesh_stats_path": ""
  },
  "validation": {
    "blender_inspection": {
      "passed": false,
      "notes_path": "",
      "known_limitations": []
    },
    "threejs_validation": {
      "passed": false,
      "parser_report_path": "",
      "screenshot_path": "",
      "bbox": null,
      "material_count": null,
      "texture_count": null
    },
    "gameplay_validation": {
      "passed": false,
      "test_log_path": "",
      "collider_proxy_path": "",
      "notes": ""
    }
  },
  "license_and_rights": {
    "source_license": "",
    "allowed_use_notes": "",
    "third_party_dependencies": []
  },
  "limitations": [
    "mesh-only until textured export is validated",
    "not suitable for production collision"
  ]
}
```

## Download And Network Rules

No download or generated artifact in this plan should exceed policy limits without explicit approval.

Use these rules for any future external source/model acquisition:

1. Do not change Clash Verge, system proxy settings, shell profiles, or Codex networking.
2. Prefer existing HomePC model caches before downloading new model files.
3. Use `tools/download_no_proxy.sh URL OUTPUT [MAX_SECONDS] [MAX_BYTES]` for direct file downloads.
4. Use command-local proxy cleanup for Git, pip, npm, Hugging Face, or ModelScope.
5. Default max single file size is `1GB`.
6. Any single file over `1GB` requires explicit user approval.
7. During large downloads, capture `lsof` evidence proving the download process is not using local Clash ports such as `127.0.0.1:7890` or `127.0.0.1:7897`.
8. Record source URL, byte count, SHA256, host, command, and failure reason.
9. MCP/editor servers for Blender or Unity must be local-only and treated as privileged mutation surfaces.

This document itself performs no downloads and creates no image/model files.

## Acceptance Checks

### Plan Acceptance

- Asset map covers hero assets, environment assets, UI/icons, textures/materials, and feedback effects.
- Every asset has a recommended source path and validation gate.
- OpenAI image prompts exist for art bible, orthographic references, UI/icon sheet, and texture/style references.
- Provenance fields cover prompt, reference image, tool/model, command, host, output, hash, limitations, and validation.
- No-proxy and large-download rules are explicit.

### Reference Image Acceptance

- Output matches child-friendly P1 theme.
- No guns, realistic violence, humanoid combat, horror, or unsafe content.
- Orthographic references are consistent enough for 3D generation.
- UI icons remain readable at HUD size.
- Texture/style references can be translated into procedural/Blender/Three.js materials.

### 3D Candidate Acceptance

- Candidate GLB has SHA256 and source chain.
- Mesh stats include bbox, orientation, node/mesh count, material count, texture count if available, and known limitations.
- Blender inspection either passes or documents why the candidate is rejected.
- Three.js GLTFLoader parses the GLB.
- Screenshot proves visible, correctly scaled asset under P1 lighting.
- Gameplay collision proxy is explicit and simple.

### Demo Asset Acceptance

P1 should ship with at least:

- one validated AI-generated or AI-assisted GLB asset, preferably the rover;
- one procedural collectible with generated style/icon support;
- one procedural hazard with generated style support;
- one UI/icon sheet or recreated icon set derived from OpenAI references;
- one material/style sheet applied through Three.js or Blender material parameters;
- asset manifest and provenance records included in the release packet.

### Rejection Criteria

Reject or quarantine an asset if:

- it introduces combat/weapon/scary framing;
- it is unreadable in the game camera;
- bbox or origin makes runtime placement unstable;
- textures/materials are missing but the asset is claimed as textured;
- mesh is too dense for the P1 browser demo without simplification;
- generated mesh is being used as collision without a proxy;
- source prompt/model/hash/validation evidence is missing.

## Managed-Agent Work Items

| Task ID | Lane | Worker type | Output | Done criteria |
| --- | --- | --- | --- | --- |
| ASSET-P1-001 | image-assets | image prompt worker | Art bible + UI/style/reference prompt packet | Prompts logged; generated outputs, if any, hashed and reviewed for child safety |
| ASSET-P1-002 | asset-3d | 3D generation worker | Rover TRELLIS/TripoSR comparison | Same reference image, GLB candidates, mesh stats, previews, limitations |
| ASSET-P1-003 | blender-cleanup | Blender worker | Cleaned rover GLB or documented blocker | Scale/origin/material/collider proxy report, screenshot, exported GLB |
| ASSET-P1-004 | threejs-runtime | Validation worker | GLB validation report | GLTFLoader parse, bbox/material/texture report, nonblank screenshot |
| ASSET-P1-005 | qa-evidence | QA worker | Asset release packet | Manifest, hashes, screenshots, smoke-test logs, known limitations |

Worker results must use the managed-agents `WORKER_RESULT` schema once the controller-core lane is ready. Until then, workers should return file paths, commands run, evidence paths, blockers, and next action in plain structured markdown.

## First Practical Slice

The smallest useful slice is:

1. Generate or select the rover orthographic reference.
2. Run one TRELLIS mesh-only rover candidate if existing HomePC resources are ready.
3. Run one TripoSR rover candidate as comparison if existing resources are ready.
4. Clean the better candidate in Blender or document the Blender blocker.
5. Validate the cleaned GLB in Three.js.
6. Put the rover into the P1 demo as visual avatar with a simple proxy collider.
7. Include provenance, screenshots, and limitations in the release packet.

If rover generation blocks, use the upgrade station or battery as the first AI-assisted GLB and keep the rover as a procedural placeholder. The acceptance requirement is one validated AI-assisted GLB in the demo or release packet, not a perfect rover on the first pass.

## Execution Note - 2026-05-13

`RW-ROVER-001` now has a first mesh-first execution slice with a Blender material pass:

- OpenAI references: `experiments/rw_rover_001_asset_chain_20260513/inputs/`
- promoted TRELLIS mesh-only candidate: `experiments/rw_rover_001_asset_chain_20260513/outputs/rw_rover_001_single3q_trellis_meshonly.glb`
- Blender cleanup/proxy/render: `experiments/rw_rover_001_asset_chain_20260513/blender_single3q/`
- P1 visual-avatar import evidence: `experiments/game_p1_rover_workshop_demo/evidence/2026-05-13_rw_rover_001_material_g4/release_packet.json`

The orthographic-sheet candidate was rejected because TRELLIS interpreted the sheet as multiple rover bodies. The single three-quarter reference produced a better single rover mesh. The result now has Blender-authored `rover-v1` PBR-style material slots, but still has no external texture maps, no rig/animation, and is not Unity-imported.
