# RW-ROVER-001 Asset Chain Report - 2026-05-13

## Result

`RW-ROVER-001` now has a complete mesh-first evidence chain with a Blender-authored material and procedural texture proof pass:

`OpenAI reference -> HomePC TRELLIS mesh-only GLB -> Mac Three.js parse -> Mac Blender cleanup/material/procedural texture/UV/proxy/render -> textured GLB metadata parse -> P1 visual avatar import`

This is a real hero rover slice, but it is not final production art. It now has four GLB material slots assigned in Blender (`rover-v1`), four procedural authoring PNG base-color maps, planar UV proof, and a textured GLB that passes P1 G4. It still has no source-baked photoreal PBR maps, no animation rig, and is not Unity-imported.

## Promoted Candidate

- reference image: `experiments/rw_rover_001_asset_chain_20260513/inputs/rw_rover_001_openai_single_3q.png`
- raw TRELLIS GLB: `experiments/rw_rover_001_asset_chain_20260513/outputs/rw_rover_001_single3q_trellis_meshonly.glb`
- cleaned material GLB: `experiments/rw_rover_001_asset_chain_20260513/blender_single3q/rw_rover_001_single3q_blender_cleaned_with_proxy.glb`
- textured GLB: `experiments/rw_rover_001_asset_chain_20260513/blender_single3q_textured/rw_rover_001_single3q_blender_textured_with_proxy.glb`
- P1 runtime copy: `experiments/game_p1_rover_workshop_demo/assets/models/rw_rover_001_single3q_blender_textured_with_proxy.glb`
- Blender render: `experiments/rw_rover_001_asset_chain_20260513/blender_single3q_textured/blender_cleanup_render.png`
- provenance: `experiments/rw_rover_001_asset_chain_20260513/provenance/asset_provenance.json`
- hashes: `experiments/rw_rover_001_asset_chain_20260513/artifact_hashes.json`
- rig/animation decision: `docs/rover_rig_animation_decision_2026-05-13.md`

## Reference Prompt

```text
Use case: stylized-concept
Asset type: single-view image-to-3D input for a child-friendly 3D browser game hero asset.
Primary request: Create one isolated friendly small workshop rover character as a single centered three-quarter front view for downstream image-to-3D generation.
Subject: One compact rounded rover, four chunky rubber wheels, tiny antenna, expressive cyan headlight eyes, teal shell, soft graphite tires, cyan lamp lenses, small orange side tool module, toy-like materials, simple clean silhouette.
Composition: Single rover only, centered, three-quarter front view with slight top visibility, full body visible, generous padding, light neutral background. Make the silhouette readable and avoid overlapping duplicate views.
Style: premium toy-like 3D game asset reference, rounded safe shapes, saturated but not harsh colors, simple studio lighting.
Constraints: exactly one rover, no orthographic sheet, no extra views, no duplicate copies, no weapons, no humanoid enemies, no text, no labels, no logos, no background clutter, no scary mood.
```

## Commands

TRELLIS used the existing HomePC checkout and cached model. No new model download was performed.

```bash
ssh homepc
EXP=/home/yuanhaizhou/models/p3_ai_cad_game/experiments/rw_rover_001_asset_chain_20260513
cd "$EXP"
source ~/miniconda3/etc/profile.d/conda.sh
conda activate trellis
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY="*" no_proxy="*" \
  python trellis_meshonly_generate.py \
  inputs/rw_rover_001_openai_single_3q.png \
  outputs/rw_rover_001_single3q_trellis_meshonly.glb \
  --gpu 1 --seed 42 --simplify 0.95
```

Local Three.js parse:

```bash
node experiments/game_p5_triposr_three_playable_loop/tools/parse_glb_assets.mjs \
  experiments/rw_rover_001_asset_chain_20260513/outputs \
  experiments/rw_rover_001_asset_chain_20260513/outputs/three_glb_parse_inventory.json
```

Local Blender cleanup:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python experiments/blender_host_probe_20260513/blender_glb_cleanup_probe.py -- \
  experiments/rw_rover_001_asset_chain_20260513/outputs/rw_rover_001_single3q_trellis_meshonly.glb \
  experiments/rw_rover_001_asset_chain_20260513/blender_single3q \
  --output-name rw_rover_001_single3q_blender_cleaned_with_proxy.glb \
  --material-strategy rover-v1
```

Cleaned GLB parse:

```bash
node experiments/game_p5_triposr_three_playable_loop/tools/parse_glb_assets.mjs \
  experiments/rw_rover_001_asset_chain_20260513/blender_single3q \
  experiments/rw_rover_001_asset_chain_20260513/blender_single3q/three_glb_parse_inventory_cleaned.json
```

Local Blender procedural texture/UV pass:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python experiments/blender_host_probe_20260513/blender_glb_cleanup_probe.py -- \
  experiments/rw_rover_001_asset_chain_20260513/outputs/rw_rover_001_single3q_trellis_meshonly.glb \
  experiments/rw_rover_001_asset_chain_20260513/blender_single3q_textured \
  --output-name rw_rover_001_single3q_blender_textured_with_proxy.glb \
  --material-strategy rover-v1 \
  --texture-strategy rover-v1-procedural \
  --texture-size 512
```

Textured GLB metadata parse:

```bash
node experiments/game_p5_triposr_three_playable_loop/tools/parse_glb_assets.mjs \
  experiments/rw_rover_001_asset_chain_20260513/blender_single3q_textured \
  experiments/rw_rover_001_asset_chain_20260513/blender_single3q_textured/three_glb_parse_inventory_textured.json
```

## Mesh And Validation

Raw promoted TRELLIS candidate:

- bytes: `845520`
- scenes: `1`
- meshes: `1`
- triangles: `42288`
- bbox size: `[0.9360095858573914, 0.8125292956829071, 0.846723884344101]`

Blender-cleaned runtime candidate:

- bytes: `4962528`
- scenes: `1`
- meshes: `5` in Three.js parse, because the materialized visual mesh exports as four material primitives plus the simple box proxy
- triangles: `42300`
- bbox size: `[2, 1.7361558871343732, 1.809220552444458]`
- material state: `pbr_materials_no_external_textures`
- material slots: `rw_rover_v1_body_teal`, `rw_rover_v1_rubber_dark`, `rw_rover_v1_safety_yellow`, `rw_rover_v1_sensor_glass`
- proxy collider: `COLLIDER_PROXY_bbox_simple_box`

Blender textured runtime candidate:

- bytes: `6036088`
- SHA256: `aa254a919d08a92c5e1963fd78a7e4bab49ad878c22a80d8e97ae1e577fb1a44`
- scenes: `1`
- meshes: `5`
- triangles: `42300`
- UV attribute meshes in Three.js readback: `5`
- glTF JSON embedded images: `4`
- glTF JSON textures: `4`
- glTF JSON base-color textured materials: `4`
- Node GLTFLoader material map count: `0`
- parser caveat: Node GLTFLoader logs texture decode warnings for embedded blob images in this headless parser, so the texture readback proof is based on glTF JSON metadata plus successful browser runtime load rather than Node image decode.
- authoring texture maps:
  - `textures/rw_rover_v1_body_teal.png`
  - `textures/rw_rover_v1_safety_yellow.png`
  - `textures/rw_rover_v1_rubber_dark.png`
  - `textures/rw_rover_v1_sensor_glass.png`
- texture state: `procedural_external_texture_maps_with_uvs`
- limitations: procedural material-color texture maps and planar bbox UVs, not source-baked photoreal PBR maps or production UV unwrapping

## Rejected Candidate

The orthographic reference sheet also produced a GLB:

- raw GLB: `experiments/rw_rover_001_asset_chain_20260513/outputs/rw_rover_001_trellis_meshonly.glb`
- cleaned render: `experiments/rw_rover_001_asset_chain_20260513/blender/blender_cleanup_render.png`

It is not promoted because TRELLIS interpreted the four-view sheet as multiple rover bodies. That is useful evidence for prompt/input design, but not a single hero asset.

## P1 Integration

The textured single-view candidate is copied into:

`experiments/game_p1_rover_workshop_demo/assets/models/rw_rover_001_single3q_blender_textured_with_proxy.glb`

P1 imports it as the visual avatar. After the GLB loads, the runtime hides the six procedural fallback visual meshes (body, head, and four wheels). Gameplay movement, pickup range, hazards, and collision remain controlled by the existing procedural rover state/proxy.

The Blender-exported `COLLIDER_PROXY_bbox_simple_box` remains inside the cleaned GLB as evidence of the proxy strategy, but P1 hides any `COLLIDER_PROXY_*` meshes at runtime so the proxy box is not rendered as part of the avatar.

P1 now preserves the GLB-authored rover materials instead of replacing them with a runtime-only material. The latest G4 load gate checks that the hero rover reports at least four material names and loads the textured GLB path.

## Rig And Animation Decision

`RW-ROVER-001` is not promoted as a rigged asset. The generated source is a single mesh without semantic wheel/body separation. P1 records:

- `rigState`: `no_skeletal_rig_single_generated_mesh`
- `animationStrategy`: `runtime_parent_transform_feedback_only`

The G4 load gate now checks `ai_hero_rover_animation_strategy_present` and `ai_hero_rover_replaced_procedural_visuals`. This proves the runtime strategy is explicit and that the procedural rover visual fallback is not layered on top of the GLB avatar; it does not claim a Blender/Unity skeletal rig.

## Limitations

- Mesh generated from a mesh-only TRELLIS output; material and texture pass is heuristic, not artist-authored texture baking.
- Procedural authoring PNG maps are embedded into the runtime GLB; this is not source-baked photoreal PBR.
- No skeletal rig; runtime animation is parent-transform feedback only.
- Unity import is still blocked by missing local Unity host proof.
