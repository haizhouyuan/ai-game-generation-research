# PUBG-Like Full AI 3D Asset Pipeline Task Board - 2026-05-13

Goal:

`docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`

## Active Meaning

The previous `tactical_game_visual_upgrade_20260520` release is now the baseline/proof-of-control packet, not final completion. This board tracks the stricter full rebuild: realistic references, local image-to-3D/PBR generation, Blender cleanup, runtime replacement, and evidence gates for all major visible asset classes.

Plain meaning:

- Not a light upgrade of the old game.
- Not just better lighting on procedural GLBs.
- Build a real local asset factory and use it to replace the game assets.
- Every final near-camera asset needs a recorded chain from reference image to 3D/PBR asset packet to Three.js evidence.
- Every minimum production asset class needs a new asset packet with route evidence; empty scaffolds do not count.
- The final playable slice must be dominated by rebuilt/generated/PBR assets, not old procedural fallbacks.
- Test the major local routes in parallel: Hunyuan3D, ComfyUI/PBR projection, TRELLIS/TRELLIS.2, Blender cleanup, and runtime gates.

## Runner Routing

- Codex: orchestration, task packets, integration, evidence, final judgement.
- Kimi: complex code/review/blocker analysis.
- Gemini CLI: broad tool/visual review, must use `gemini-3.1-pro-preview`.
- MiniMax: narrow mechanical tasks only.
- HomePC GPU1: Hunyuan3D, ComfyUI, TRELLIS, Blender render/bake.

## Current Parallel Lanes

| Lane | Owner | Status | Output |
| --- | --- | --- | --- |
| W0 stricter goal | Codex | active | `docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md` |
| W1 Hunyuan install | HomePC GPU / Codex | active | `experiments/pubg_like_asset_factory_20260513/reports/hunyuan3d_env_report.md` |
| W2 reference images | Codex + image generation route | pending | `experiments/pubg_like_asset_factory_20260513/references/` |
| W3 first generated asset | HomePC GPU | active | `experiments/pubg_like_asset_factory_20260513/assets/hunyuan_shape_demo_001/` |
| W4 hero rifle full replacement | HomePC GPU + Blender | pending | generated/PBR hero rifle packet |
| W5 character/gear replacement | HomePC GPU + Blender | pending | production character packets |
| W6 environment/loot/clutter | HomePC GPU + Blender | pending | material and prop packets |
| W7 ComfyUI PBR route | HomePC GPU | minimal proof captured | `experiments/pubg_like_asset_factory_20260513/routes/route_c_comfyui_pbr_probe_004/summary.md` |
| W8 runtime gate v3 | Codex/Kimi | pending | v3 registry and visual evidence gate |
| W9 final release | Codex | pending | new dated release packet |
| W10 local Mac runner capacity | Codex/Gemini | documented/deferred | `docs/mac_local_runner_capacity_2026-05-13.md` |
| Runner MCP/skill control | Codex + runners | active | `docs/coding_runner_mcp_skill_control_2026-05-13.md` |
| Asset packet validation | Codex + worker | active | `tools/validate_asset_packets.py` |
| Route D TRELLIS prop probe | HomePC GPU | evidence captured | `experiments/pubg_like_asset_factory_20260513/routes/route_d_trellis_prop_probe_005/summary.md` |

## Asset Factory Completion Gates

Minimum gates for final release:

- 10+ reference/provenance sets.
- 6+ newly generated realistic reference-image sets.
- All 12 minimum production targets have non-empty asset packets with route reports and runtime integration status.
- All 12 minimum production targets have generated, rebuilt, or PBR-authored production outputs.
- 8+ packets with actual texture maps: basecolor, normal, roughness, and metallic or AO.
- All 12 minimum production targets have Blender preview plus Three.js close-up or gameplay-context evidence, unless explicitly removed from the final playable slice and all target cameras.
- 1+ chain starting from a newly generated realistic reference image.
- 1+ Hunyuan asset attempted through shape and paint/PBR.
- 1+ ComfyUI/PBR projection or equivalent texture completion route tested.
- 1+ TRELLIS/TRELLIS.2 concrete tactical asset candidate attempted.
- Final runtime uses new/rebuilt packets, not mostly old procedural placeholders.
- Polycount/performance gate: generated assets must be decimated or LODed enough for the playable Three.js slice.
- Collision proxy gate: complex visual meshes need simple gameplay collision/proxy shapes.
- PBR consistency gate: assets from different generators must be checked under the same rainy checkpoint lighting/material test scene.

Schema draft:

`schemas/asset_registry_v3.schema.json`

Packet validator:

```bash
python3 tools/validate_asset_packets.py --markdown
python3 tools/validate_asset_packets.py --strict
```

Current validator meaning:

- all new packet slots have standard directories;
- texture map counts are still zero for the scaffolded production slots;
- `hunyuan_shape_demo_001` has browser-independent Blender evidence but remains shape-only and not a final asset.
- the task is not complete while most packets are scaffolds and only the probe crate has texture maps.

## Immediate Commands

1. Preflight HomePC GPU/disk and running processes. Done.
2. Clone/install Hunyuan3D-2.1 under HomePC without proxy traffic. Done.
3. Download model files with proxy env unset and record evidence. Done.
4. Run a small shape-only smoke test. Done.
5. Run a small textured/PBR smoke test. Active.
6. Generate six realistic reference-image sets for rifle/character/gear/ground/container/loot. Pending.
7. Convert one newly generated reference into a 3D/PBR asset candidate. Pending.
8. Launch or continue ComfyUI/TRELLIS route probes in parallel; do not wait for Hunyuan to be perfect before building alternate chains.
9. Upgrade validators so empty scaffolds cannot be mistaken for completion.
10. Build the new Three.js rebuild experiment only after asset packets start passing PBR/preview gates.

## Current W1/W3 Evidence

- Hunyuan3D-2.1 model snapshot downloaded to HomePC with command-local proxy env unset and `HF_ENDPOINT=https://hf-mirror.com`.
- Shape-only generation succeeded on HomePC GPU1.
- First shape asset packet is in `experiments/pubg_like_asset_factory_20260513/assets/hunyuan_shape_demo_001/`.
- Hash manifest verifies: `python3 tools/verify_artifact_hashes.py experiments/pubg_like_asset_factory_20260513/artifact_hashes.json`.

Important: `hunyuan_shape_demo_001` is not a final game asset. It proves the local Hunyuan shape route only; `material_map_count = 0`.

## Asset Packet Scaffolding

Created standard packet directories under:

`experiments/pubg_like_asset_factory_20260513/assets/`

Current packet slots:

- `hero_rifle_v1`
- `sidearm_v1`
- `secondary_weapon_v1`
- `player_tactical_v1`
- `enemy_tactical_v1`
- `gear_set_v1`
- `wet_asphalt_material_v1`
- `concrete_wall_material_v1`
- `container_checkpoint_v1`
- `loot_set_v1`
- `clutter_decals_v1`
- `rainy_checkpoint_scene_v1`

Each slot has `source/`, `model/`, `textures/`, `reports/`, and `evidence/`.

## Current Texture/PBR Blockers

- Existing `hy3d21` env is Python 3.10; `bpy==4.0` is not installable there on Linux.
- Hunyuan paint imports currently fail because `bpy` is missing.
- `custom_rasterizer` imports successfully in `hy3d21`.
- `realesrgan` and `basicsr` are missing.
- Existing `hy3dpaint/ckpt/RealESRGAN_x4plus.pth` was a partial 1.8MB file and must be replaced.

Active mitigation:

- create a separate `hy3d21paint` Python 3.11 env for Hunyuan Paint instead of disturbing the working shape env;
- download RealESRGAN with proxy env unset and size/hash validation;
- compile or validate Hunyuan paint extensions after `bpy`, `realesrgan`, and `basicsr` imports pass.

Current paint env status:

- `hy3d21paint` exists with Python 3.11.
- PyTorch 2.5.1 + CUDA 12.1 installed and sees RTX 3090.
- `bpy==4.2.0`, `realesrgan==0.3.0`, `basicsr==1.4.2`, `facexlib`, and `gfpgan` import successfully after the BasicSR torchvision compatibility patch.
- Conda CUDA 12.1 `nvcc` and conda GCC/G++ 12 were installed to avoid the system CUDA 11.5 mismatch.
- `custom_rasterizer` and Hunyuan paint mesh-painter imports now pass when the torch library path is included in `LD_LIBRARY_PATH`.
- RealESRGAN checkpoint was replaced with a valid 67,040,989 byte file, SHA256 `4fa0d38905f75ac06eb49a7951b426670021be3018265fd191d2125df9d682f1`.
- Current blocker: `facebook/dinov2-giant` is required by Hunyuan Paint and is downloading safetensors-only with proxy env unset.

## Current Route C / Route D Evidence

Route C ComfyUI/PBR:

- HomePC has `/home/yuanhaizhou/ComfyUI` at revision `fce0398470fe3ecdb7ab4c5c69555ad0fcbdc09e`.
- Relevant blueprints include `Image to Model (Hunyuan3d 2.1).json`.
- Installed `ComfyUI-TextureAlchemy` at revision `0afda45713c7b33afbf9d4f757493cca2004f65f` with command-local proxy env unset.
- TextureAlchemy import check loaded 131 node mappings.
- Minimal PBR proof generated basecolor, height, normal, roughness, metallic, AO, and ORM maps for the tactical crate reference.
- Verdict: usable as a minimal PBR proof, but not final production texture projection.

Route D TRELLIS:

- Ran cached TRELLIS image-to-3D on a non-rifle tactical crate prop.
- Output GLB: `experiments/pubg_like_asset_factory_20260513/routes/route_d_trellis_prop_probe_005/outputs/raw/tactical_crate_trellis_meshonly.glb`.
- Blender import preview: `experiments/pubg_like_asset_factory_20260513/routes/route_d_trellis_prop_probe_005/evidence/blender_import.png`.
- Mesh facts: 16,367 vertices, 32,722 faces after postprocess.
- Texture maps: 0.
- Verdict: background-only until PBR/texture and cleanup are added.

Combined probe asset packet:

- `tactical_crate_trellis_texturealchemy_v1` combines the Route D TRELLIS mesh and Route C TextureAlchemy maps.
- It has `basecolor`, `height`, `normal`, `roughness`, `metallic`, `ao`, and `orm` texture files.
- It has Blender import evidence and a material report.
- It is explicitly `probe_only`, not production-ready: no final UV cleanup, material-zone separation, LOD, collision proxy, or Three.js gameplay evidence yet.
- Hash manifest currently verifies 135 entries with `python3 tools/verify_artifact_hashes.py experiments/pubg_like_asset_factory_20260513/artifact_hashes.json`.

Textured Blender preview:

- Route `route_cd_textured_crate_preview_008` imported the TRELLIS crate mesh, ran Blender Smart UV, wired TextureAlchemy basecolor/roughness/metallic/normal maps, exported a textured GLB, and rendered a preview.
- Output: `experiments/pubg_like_asset_factory_20260513/routes/route_cd_textured_crate_preview_008/evidence/blender_textured_preview.png`.
- Visual read: the chain is real, but the automatic UV/heuristic maps are not production quality.

## External Runner Reviews

`hunyuan_paint_env_review_001` was sent to Gemini and Kimi as read-only runner reviews.

Gemini result is saved at:

`tasks/pubg_like_full_rebuild/hunyuan_paint_env_review_001.gemini_review.txt`

Key Gemini guidance:

- Python 3.11 plus `bpy==4.2.0` is a reasonable practical substitute because current Linux/Python 3.11 PyPI index does not offer `bpy==4.0`.
- `basicsr==1.4.2` may fail with modern `torchvision` because `torchvision.transforms.functional_tensor` was removed; patch to `torchvision.transforms.functional` if import fails.
- Do not let RealESRGAN super-resolution block the core paint validation; first try to get texture generation running, then solve upscaling.

Kimi guidance:

- Use Kimi for hard blocker analysis and implementation critique.
- Patch `basicsr` import if modern torchvision breaks `functional_tensor`.
- Verify `nvcc --version` before compiling extensions.

Gemini routing:

- Use `/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-gemini-review`; it pins `gemini-3.1-pro-preview`.

MiniMax routing:

- Use only for simple report/schema/hash and mechanical first-pass review.
