# Task: hunyuan-paint-env-review-001

## Goal

Review the current Hunyuan3D-2.1 paint/PBR environment plan for HomePC and identify obvious risks or better next commands.

## Context

We are working toward:

`docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`

Current proven facts:

- HomePC has `/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/Hunyuan3D-2.1`.
- Model snapshot is downloaded to `/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/models/Hunyuan3D-2.1`.
- `hy3d21` Python 3.10 shape environment works.
- Shape-only demo succeeded and produced `hunyuan_shape_demo_001`.
- `hy3d21` can import `custom_rasterizer`.
- `hy3d21` cannot import `bpy`, `realesrgan`, or `basicsr`.
- Existing `RealESRGAN_x4plus.pth` is partial/corrupt, only about 1.8MB.
- PyPI index under Python 3.11 shows `bpy` versions `4.2.x+`, not `4.0`.
- We created a separate `hy3d21paint` Python 3.11 env instead of disturbing `hy3d21`.
- We are installing `pytorch==2.5.1`, `torchvision==0.20.1`, `pytorch-cuda=12.1` into `hy3d21paint`.

## Proposed Next Plan

1. Install `bpy==4.2.0`, `realesrgan==0.3.0`, and `basicsr==1.4.2` in `hy3d21paint`.
2. Install the Hunyuan repo requirements selectively, avoiding known conflicts.
3. Compile `hy3dpaint/custom_rasterizer` in `hy3d21paint` if it is not already importable there.
4. Compile `hy3dpaint/DifferentiableRenderer/compile_mesh_painter.sh`.
5. Replace corrupt RealESRGAN checkpoint using a no-proxy download route.
6. Run:

```bash
PYTHONPATH=./hy3dpaint python - <<'PY'
import bpy, custom_rasterizer, realesrgan, basicsr
from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig
print("paint imports OK")
PY
```

7. Run `hy3dpaint/demo.py` or a minimal paint script against the already generated shape GLB.

## Constraints

- Do not suggest using paid proxy traffic for downloads.
- Do not copy secrets.
- Prefer moving fast over overly cautious avoidance, but keep `hy3d21` shape env working.
- Output only review comments and next commands. Do not edit files.

## Questions

1. Is Python 3.11 + `bpy==4.2.0` a reasonable practical substitute for official `bpy==4.0`?
2. What dependency/version risks are most likely to block paint?
3. What exact next command sequence should the controller run?
4. Is there a better RealESRGAN weight source or should we bypass super-resolution initially?
