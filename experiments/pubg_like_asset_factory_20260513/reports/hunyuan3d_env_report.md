# Hunyuan3D 2.1 Environment Report - 2026-05-13

## Purpose

This is the first HomePC setup report for the stricter PUBG-like full asset factory goal:

`docs/production_goal_pubg_like_full_ai_3d_asset_pipeline_2026-05-13.md`

The target is not a small visual polish pass. The target is to make Hunyuan3D 2.1 a real local shape + PBR paint route for generated tactical-game assets.

## Host

- SSH alias: `homepc`
- Hostname: `yuanhaizhou-home`
- User: `yuanhaizhou`
- Main workdir: `/home/yuanhaizhou/models/hunyuan3d21_factory_20260513`
- Repo clone: `/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/Hunyuan3D-2.1`
- Model dir: `/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/models/Hunyuan3D-2.1`

## GPU / Disk Preflight

Observed before model download:

```text
GPU 0: NVIDIA GeForce RTX 3090, 24576 MiB total, about 1295 MiB free
GPU 1: NVIDIA GeForce RTX 3090, 24576 MiB total, about 24246 MiB free
/home: 1.7T total, about 805G free
```

GPU0 is occupied by an existing vLLM/UI-TARS process using about 22.7GB. Hunyuan tasks should use `CUDA_VISIBLE_DEVICES=1` unless GPU0 is intentionally freed.

## Existing Python State

System Python already had:

```text
huggingface_hub 0.36.2
torch 2.5.1+cu121
diffusers 0.37.1
transformers 4.49.0
accelerate 1.13.0
```

The existing `trellis` conda environment has:

```text
torch 2.5.1+cu121
diffusers 0.37.1
transformers 4.49.0
huggingface_hub 0.36.2
accelerate 1.13.0
trimesh 4.12.2
```

`hy3d21` was created by cloning the existing `trellis` environment to avoid starting from a blank environment.

## Source Clone

Command shape:

```bash
env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git \
  /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/Hunyuan3D-2.1
```

Result:

```text
repo revision: 82920d643c0dc2f7bfd7255f45f62d386edfe60c
log: /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/logs/00_clone_repo_20260513_183732.log
```

## Model Download

Official model repo:

`tencent/Hunyuan3D-2.1`

Hugging Face metadata showed total storage around:

```text
14949350689 bytes
```

Download command shape:

```bash
env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  HF_ENDPOINT=https://hf-mirror.com \
  MODEL_DIR=/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/models/Hunyuan3D-2.1 \
  python3 /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/download_hunyuan3d21_snapshot.py
```

The script logs:

- repo id;
- local dir;
- `HF_ENDPOINT`;
- proxy env dictionary;
- `hf-mirror.com` resolved IP.

Observed at start:

```json
{
  "repo_id": "tencent/Hunyuan3D-2.1",
  "HF_ENDPOINT": "https://hf-mirror.com",
  "proxy_env": {},
  "hf_mirror_ip": "160.16.86.14"
}
```

Network evidence during download showed the Python downloader connected to `hf-mirror.com` / remote HTTPS endpoints directly, while local proxy port `7890` was only a listener and was not used by the downloader process.

## Model Download Result

The Hunyuan3D-2.1 model snapshot download completed.

Result:

```text
Fetching 30 files: 100%
duration: about 28 minutes
local size: about 14G
```

Key large files observed:

```text
hunyuan3d-dit-v2-1/model.fp16.ckpt                    7366389768 bytes
hunyuan3d-paintpbr-v2-1/unet/diffusion_pytorch_model.bin 3925293863 bytes
hunyuan3d-paintpbr-v2-1/text_encoder/pytorch_model.bin    1361671895 bytes
hunyuan3d-paintpbr-v2-1/image_encoder/model.safetensors   1264217240 bytes
hunyuan3d-vae-v2-1/model.fp16.ckpt                         655648152 bytes
hunyuan3d-paintpbr-v2-1/vae/diffusion_pytorch_model.bin    334707217 bytes
```

No-proxy evidence:

- command-local proxy env was unset;
- `HF_ENDPOINT=https://hf-mirror.com`;
- start log showed `"proxy_env": {}`;
- `lsof` showed the downloader connected directly to remote HTTPS endpoints, not local proxy port `7890`.

## Shape Smoke Result

The first standalone Hunyuan shape generation smoke test passed on HomePC GPU1.

Command route:

```bash
ssh homepc
BASE=/home/yuanhaizhou/models/hunyuan3d21_factory_20260513
MODEL_DIR=$BASE/models/Hunyuan3D-2.1
source ~/miniconda3/etc/profile.d/conda.sh
conda activate hy3d21
cd "$BASE/Hunyuan3D-2.1"
CUDA_VISIBLE_DEVICES=1 python "$BASE/run_shape_demo_001.py"
```

Result:

```text
input:  /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/Hunyuan3D-2.1/assets/demo.png
output: /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/outputs/shape_demo_001/demo_shape.glb
pipeline load: 14.48s
generation: 71.94s
output size: 12,926,320 bytes
sha256: f52cd0210c8587f5820f93576d230840a2cff2df65bc75dbd52bd8bd4e7263bf
```

The generated GLB, input image, and HomePC log were copied into this repository as:

```text
experiments/pubg_like_asset_factory_20260513/assets/hunyuan_shape_demo_001/
```

Local Blender then imported `model/raw.glb`, rendered `evidence/blender_preview.png`, and exported `model/cleaned.glb` plus `model/optimized.glb`. The asset remains shape-only: `material_map_count = 0`.

## Known Risks

- Hunyuan texture/PBR route needs custom rasterizer and DifferentiableRenderer extensions.
- Existing `trellis` environment has many needed dependencies but not all official Hunyuan extras.
- The Hunyuan shape import path is proven, but the texture/PBR path is not yet proven.
- `hy3dpaint` import currently fails on `ModuleNotFoundError: No module named 'bpy'`.
- A direct GitHub download of `RealESRGAN_x4plus.pth` was killed because it was too slow; the partial file should not be treated as valid.
