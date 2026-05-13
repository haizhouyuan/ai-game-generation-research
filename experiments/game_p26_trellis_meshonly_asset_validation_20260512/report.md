# P26 TRELLIS Mesh-Only Asset Validation - 2026-05-12

## Result

HomePC can generate a usable mesh-only GLB from an image using the existing TRELLIS checkout and cached `TRELLIS-image-large` model.

This validates the smallest local AI asset loop:

`reference image -> TRELLIS inference -> postprocessed mesh -> GLB export -> mesh readback -> preview image`

No new model or source download was required for this run.

## Environment

- Host: `homepc` (`yuanhaizhou-home`)
- GPU: RTX 3090, selected with `--gpu 1`
- Conda env: `trellis`
- TRELLIS code: `/home/yuanhaizhou/TRELLIS`
- Model: `/home/yuanhaizhou/TRELLIS-models/TRELLIS-image-large`
- Remote experiment path: `/home/yuanhaizhou/models/p3_ai_cad_game/experiments/p26_trellis_asset_validation_20260512`

## Artifacts

| Artifact | Bytes | SHA256 |
|---|---:|---|
| `inputs/typical_misc_crate.png` | 642105 | `59fd9884301faca93265166d90078e8c31e76c7f93524b1db31975df4b450748` |
| `outputs/typical_misc_crate_trellis_meshonly.glb` | 2198560 | `ef03de6e567402ace47af327da875ab10caf093aa1fd209f291371fb82208944` |
| `outputs/typical_misc_crate_trellis_meshonly_preview.png` | 356563 | `f2c7eb6076f78bd4a7e99bbcc78cfe1fb858c82abbf9b2c880e20102f9d63945` |
| `outputs/three_glb_parse_inventory.json` | 622 | `fede9f884ea73b348f36c52d13d3fbb7021c5b24e99be4f886938436e2d7b7c4` |
| `logs/meshonly_rerun_20260512.log` | 13663 | `c08036e5f765f09b6723730a943a783d7934548bb0e1a3065c1b2e83b187febe` |

Preview:

![TRELLIS mesh-only crate preview](/Users/yuanshaochen/Projects/ai-game-generation-research/experiments/game_p26_trellis_meshonly_asset_validation_20260512/outputs/typical_misc_crate_trellis_meshonly_preview.png)

## Mesh Verification

`trimesh` readback on HomePC:

```json
{
  "bytes": 2198560,
  "vertices": 54797,
  "faces": 110066,
  "bounds": [
    [-0.5000529289245605, -0.4970507323741913, -0.4999831020832062],
    [0.4995141625404358, 0.49968603253364563, 0.49970439076423645]
  ],
  "extents": [0.9995670914649963, 0.9967367649078369, 0.9996874928474426],
  "is_empty": false,
  "is_watertight": false
}
```

The exported mesh is not watertight, so it should be treated as a visual asset or proxy-collider source until a collision cleanup pass is added.

## Three.js GLB Parse Smoke Test

The existing P5 parser was run without downloading new dependencies:

```bash
node experiments/game_p5_triposr_three_playable_loop/tools/parse_glb_assets.mjs \
  experiments/game_p26_trellis_meshonly_asset_validation_20260512/outputs \
  experiments/game_p26_trellis_meshonly_asset_validation_20260512/outputs/three_glb_parse_inventory.json
```

Result:

```json
{
  "scenes": 1,
  "meshes": 1,
  "triangles": 110066,
  "bbox_size": [0.9995670914649963, 0.9967367649078369, 0.9996874928474426]
}
```

This confirms the generated GLB can be consumed by the existing Three.js/GLTFLoader validation path.

## Command

```bash
ssh homepc
cd /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p26_trellis_asset_validation_20260512
source ~/miniconda3/etc/profile.d/conda.sh
conda activate trellis
export TRELLIS_GPU=1
python trellis_meshonly_generate.py \
  inputs/typical_misc_crate.png \
  outputs/typical_misc_crate_trellis_meshonly.glb \
  --gpu 1 \
  --seed 42 \
  --simplify 0.95
```

## Observed Output

- Model load and inference completed.
- Inference time: `30.4s`
- Raw mesh: `1102702` vertices, `2205932` faces
- Postprocessed mesh: `54797` vertices, `110066` faces
- Exported GLB: `2.1MB`

## Blockers And Caveats

- Textured TRELLIS GLB export is still blocked in the current environment by missing `diff_gaussian_rasterization`.
- Blender headless preview failed on HomePC with `Unable to open a display`; the preview image here was generated with a pure Python/PIL orthographic projection instead.
- This is a mesh-only asset. It proves local generation and GLB export, not production material quality, UVs, collision mesh quality, or Unity import behavior.

## Next Step

Use this GLB as the first asset smoke test for:

1. `three-glb-playable-validator`;
2. Godot import/readback gate;
3. Unity import once Unity Editor and MCP are available.
