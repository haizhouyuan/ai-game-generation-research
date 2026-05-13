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

## Current State

Download is in progress and resumable through `huggingface_hub.snapshot_download`.

Last observed partial size:

```text
5.6G / expected about 14.95G
```

## Next Commands

After the model download completes:

```bash
ssh homepc
BASE=/home/yuanhaizhou/models/hunyuan3d21_factory_20260513
MODEL_DIR=$BASE/models/Hunyuan3D-2.1
find "$MODEL_DIR" -type f -printf "%s %p\n" | sort -n | tail -30
du -sh "$MODEL_DIR"
```

Then run dependency/import smoke in `hy3d21`, install only missing packages/extensions, and use GPU1:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate hy3d21
cd /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/Hunyuan3D-2.1
CUDA_VISIBLE_DEVICES=1 python - <<'PY'
import torch
print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))
PY
```

## Known Risks

- Hunyuan texture/PBR route needs custom rasterizer and DifferentiableRenderer extensions.
- Existing `trellis` environment has many needed dependencies but not all official Hunyuan extras.
- The model download uses a mirror and may have transient `ReadTimeoutError`; snapshot download should resume.
