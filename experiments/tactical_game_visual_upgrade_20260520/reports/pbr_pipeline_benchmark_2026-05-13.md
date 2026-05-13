# PBR Pipeline Benchmark - 2026-05-13

## Scope

This report closes the W8 benchmark requirement for the current tactical visual upgrade packet. It records what is actually proven locally today, what is only mesh-only, and what is blocked by missing local installs or governed large model downloads.

No new external model or asset download was performed for this benchmark pass.

## Route A - StableGen / Blender-First Retexture

Status: **partial pass through Blender-first fallback**

StableGen itself was not found in the local Mac or HomePC workspace during this pass. The proven substitute is a local Blender-first PBR packet for the hero rifle:

- `assets/weapons/hero_rifle_v2/model/optimized.glb`
- `assets/weapons/hero_rifle_v2/textures/basecolor.png`
- `assets/weapons/hero_rifle_v2/textures/normal.png`
- `assets/weapons/hero_rifle_v2/textures/roughness.png`
- `assets/weapons/hero_rifle_v2/textures/metallic.png`
- `assets/weapons/hero_rifle_v2/textures/ao.png`
- `assets/weapons/hero_rifle_v2/reports/material_report.json`
- `assets/weapons/hero_rifle_v2/evidence/blender_preview.png`

Evidence:

- Blender 5.1.1 generated and exported the asset packet locally.
- `material_report.json` records `material_map_count: 5`.
- Required anchors exist: `Muzzle`, `Grip_R`, `Grip_L`, `Optic`, `PickupRoot`, `ThirdPersonMount`.
- Browser evidence reports `target_hero_rifle_v2.state: loaded`, `fallbackUsed: false`, runtime `materialMapCount: 4`, and registry `material_map_count: 5`.
- All six CDP cameras passed with `heroRifleOk: true`.

Decision:

This route is good enough as the current production fallback and as a Three.js PBR integration proof. It is not yet a StableGen proof, and it is not the final visual bar for a commercial-grade hero rifle.

Next route task:

Install or locate StableGen only after a bounded task packet is written. The first StableGen task should retexture `hero_rifle_v2` or an existing white-model prop, not change the runtime.

## Route B - Trellis2 / ComfyUI / Texture Projection

Status: **mesh-only pass, PBR projection blocked**

Existing HomePC TRELLIS cache is proven:

- `/home/yuanhaizhou/TRELLIS`
- `/home/yuanhaizhou/TRELLIS-models/TRELLIS-image-large`
- `/home/yuanhaizhou/.cache/huggingface/hub/models--microsoft--TRELLIS-image-large`

Existing tactical rifle TRELLIS experiment:

- `experiments/tactical_rifle_trellis_20260513/outputs/groza_trellis_seed_42.glb`
- `experiments/tactical_rifle_trellis_20260513/outputs/groza_trellis_seed_101.glb`
- `experiments/tactical_rifle_trellis_20260513/outputs/groza_trellis_seed_202.glb`
- `experiments/tactical_rifle_trellis_20260513/blender_seed_202/groza_trellis_seed_202_cleaned.glb`

Observed generation results:

- seed 42: `9,406` postprocessed faces, no useful PBR texture maps.
- seed 101: `8,780` postprocessed faces, no useful PBR texture maps.
- seed 202: `8,670` postprocessed faces, strongest silhouette, no useful PBR texture maps.
- inference time in logs: about `7.6s` to `8.1s` on RTX 3090.

No new download was needed in those TRELLIS runs. The recorded command shape used proxy-free environment variables:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY="*" no_proxy="*" \
  python .../trellis_meshonly_generate.py \
  inputs/groza_reference.png \
  outputs/groza_trellis_seed_<seed>.glb \
  --gpu 1 --seed <seed> --simplify 0.95
```

Blocking point:

HomePC has `/home/yuanhaizhou/ComfyUI`, but no matching custom nodes were found under `/home/yuanhaizhou/ComfyUI/custom_nodes` for Hunyuan, Trellis2 ComfyUI, Texture Projection, TextureAlchemy, StableGen, or PBR projection. Therefore the Trellis/ComfyUI/Texture Projection PBR route is not yet installed or validated.

Decision:

Keep TRELLIS as a fast mesh candidate generator. Do not use the existing mesh-only rifle outputs as final hero assets. The next useful work is ComfyUI node setup plus one projection/PBR proof, using the no-proxy download rule for every model or node payload over 100 MB.

## Route C - Hunyuan3D 2.1 Shape/Paint Or Equivalent PBR Pipeline

Status: **blocked by absent local install/model cache**

Local and HomePC checks found no Hunyuan3D install or model cache in the searched workspace/cache paths. HomePC cache search found only TRELLIS-related entries:

- `/home/yuanhaizhou/.cache/huggingface/hub/models--microsoft--TRELLIS-image-large`
- `/home/yuanhaizhou/TRELLIS-models/TRELLIS-image-large`

No Hunyuan3D 2.1 weights were downloaded in this pass. That is intentional: the expected model payloads are large enough to require explicit URL/version/size planning and no-proxy evidence before acquisition.

Decision:

Hunyuan3D remains the best next PBR-capable generator route, but it is not proven in this repo today. The next step is a HomePC GPU task packet that first checks exact repo, license, model sizes, and disk/cache paths, then requests approval for any single file over 1 GB before downloading.

## Ranking For The Next Work

1. **Blender-first PBR fallback**: proven today, integrated into browser evidence, good for immediate vertical-slice progress.
2. **TRELLIS cached mesh-only**: proven as fast shape candidate generation, not enough for final textured/PBR tactical assets.
3. **ComfyUI Texture Projection / StableGen / TextureAlchemy**: likely high leverage, but currently absent locally and needs setup.
4. **Hunyuan3D 2.1**: strongest candidate for shape+paint, but blocked by absent install/cache and governed large downloads.

## Representative Asset Matrix

| Representative | Current Route A State | Route B State | Route C State | Decision |
| --- | --- | --- | --- | --- |
| Hero rifle | Passed through `hero_rifle_v2` with 5 PBR maps, Blender preview, anchors, browser close-ups, and hashes. | TRELLIS produced three mesh-only rifle candidates; strongest seed was 202, but no PBR maps. | Blocked by absent Hunyuan3D install/cache. | Use Route A fallback now; retry B/C only for higher-quality replacement. |
| Tactical gear / character piece | Runtime proxy rig proves animation states and gear silhouette, but no full baked PBR character packet yet. | Not run for gear in this packet. | Blocked by absent Hunyuan3D install/cache. | Next asset-generation target after rifle; should use Kimi/Gemini-reviewed task packet. |
| Wet ground / container / concrete | Runtime scene has wet asphalt, containers, lighting, decals, and screenshot proof, but not per-material baked PBR packets. | Texture projection route blocked by missing ComfyUI projection nodes. | Blocked by absent Hunyuan3D install/cache. | Use procedural runtime materials now; create dedicated material packets next. |
| Loot / medkit prop | Runtime has loot/world pickup evidence and the hero rifle in loot context; medkit/loot PBR packet not created yet. | Not run for loot in this packet. | Blocked by absent Hunyuan3D install/cache. | Use current runtime proof now; make medkit the first small Route B/C prop test. |

## Plain-English Read

Right now, the factory can already make and ship a browser-visible PBR asset packet through Blender. It can also make TRELLIS mesh candidates quickly on HomePC. What it cannot yet honestly claim is a complete local AI PBR route through StableGen, Texture Projection, TextureAlchemy, or Hunyuan3D. Those are the next installation and GPU proof tasks, not completed facts.
