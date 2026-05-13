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
- The Hunyuan shape import path is proven, but the texture/PBR generation path is not yet proven.
- A direct GitHub download of `RealESRGAN_x4plus.pth` was killed because it was too slow; the partial file should not be treated as valid.
- HomePC has `nvcc` 11.5 while `hy3d21paint` uses PyTorch CUDA 12.1; Hunyuan paint extension compilation may need workaround if CUDA ABI/toolkit mismatch appears.

## Paint Environment Follow-Up

The working `hy3d21` shape environment is Python 3.10. Hunyuan Paint needs `bpy`, but the current PyPI index did not expose `bpy==4.0` for that environment. A separate Python 3.11 paint environment was started:

```text
conda env: hy3d21paint
python: 3.11.15
purpose: Hunyuan Paint/PBR only
```

Rationale:

- keep `hy3d21` intact because shape generation is already proven;
- test `bpy==4.2.0` as the closest practical Blender module route;
- install CUDA PyTorch in a separate environment and record no-proxy evidence;
- compile/validate paint extensions there.

External Gemini review agreed that Python 3.11 plus `bpy==4.2.0` is a reasonable practical route, while warning that `basicsr==1.4.2` may need a `torchvision.transforms.functional_tensor` compatibility patch with modern `torchvision`.

## Paint Environment Progress

`hy3d21paint` now has a working CUDA PyTorch base:

```text
torch 2.5.1
torch_cuda 12.1
cuda_available True
device NVIDIA GeForce RTX 3090
nvcc release 11.5, V11.5.119
```

Install logs:

```text
/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/logs/08_install_hy3d21paint_torch_*.log
/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/logs/09_verify_hy3d21paint_cuda_*.log
```

`bpy`, RealESRGAN, BasicSR, and related dependencies were installed with command-local proxy env unset. The first direct dependency install failed because `tb-nightly` was unavailable through the configured PyPI mirror. The successful route was:

1. install real runtime dependencies manually;
2. install `basicsr`, `facexlib`, `gfpgan`, and `realesrgan` with `--no-deps`;
3. patch BasicSR's obsolete `torchvision.transforms.functional_tensor` import.

Post-patch import result:

```text
bpy OK
cv2 OK 4.13.0
facexlib OK 0.3.0
gfpgan OK
basicsr OK 1.4.2
realesrgan OK
```

Hunyuan Paint core dependency import also passed after installing the minimal official requirements needed for paint:

```text
textureGenPipeline OK after deps
```

The paint route is now at extension compile / first texture generation stage, not at Python dependency stage.

## Extension Compile Status

First `custom_rasterizer` compile attempt failed because pip build isolation could not see `torch`:

```text
ModuleNotFoundError: No module named 'torch'
```

Second attempt used `pip install -e . --no-build-isolation`, which reached the real compile step and failed on CUDA compiler mismatch:

```text
RuntimeError:
The detected CUDA version (11.5) mismatches the version that was used to compile
PyTorch (12.1).
```

Mitigation result:

- installed CUDA 12.1 `nvcc` / toolkit into `hy3d21paint`;
- installed conda GCC/G++ 12 for CUDA extension compilation;
- set `CUDA_HOME`, compiler env vars, include paths, and `TORCH_CUDA_ARCH_LIST=8.6`;
- retried `custom_rasterizer` and Hunyuan paint imports successfully.

This was a real Hunyuan Paint blocker, not a missing Python package blocker.

The successful extension/import route used the conda CUDA toolkit and torch
library path:

```bash
export CUDA_HOME="$CONDA_PREFIX"
export PATH="$CONDA_PREFIX/bin:$PATH"
export CC="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-gcc"
export CXX="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-g++"
export CUDAHOSTCXX="$CXX"
export CPATH="$CONDA_PREFIX/targets/x86_64-linux/include:$CONDA_PREFIX/include:${CPATH:-}"
export CFLAGS="-I$CONDA_PREFIX/targets/x86_64-linux/include ${CFLAGS:-}"
export CXXFLAGS="-I$CONDA_PREFIX/targets/x86_64-linux/include ${CXXFLAGS:-}"
export TORCH_CUDA_ARCH_LIST="8.6"
TORCH_LIB=$(python - <<'PY'
import pathlib, torch
print(pathlib.Path(torch.__file__).resolve().parent / "lib")
PY
)
export LD_LIBRARY_PATH="$TORCH_LIB:$CONDA_PREFIX/lib:$CONDA_PREFIX/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"
```

Post-compile import result:

```text
custom_rasterizer OK with torch lib
textureGenPipeline OK after custom_rasterizer and mesh painter
```

## RealESRGAN Checkpoint

The direct official GitHub download was too slow and left a corrupt partial
file. The valid checkpoint was downloaded from a CNB LFS mirror with
command-local proxy env unset.

Result:

```text
path: /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/Hunyuan3D-2.1/hy3dpaint/ckpt/RealESRGAN_x4plus.pth
size: 67040989 bytes
sha256: 4fa0d38905f75ac06eb49a7951b426670021be3018265fd191d2125df9d682f1
source: https://cnb.cool/ai-models/AI-ModelScope/RealESRGAN_x4plus
```

This removes the super-resolution checkpoint as a blocker.

## Paint Smoke Current Blocker

The first Hunyuan Paint smoke reached model loading and then failed because the
paint pipeline also requires `facebook/dinov2-giant`.

Observed failure:

```text
missing preprocessor_config.json for facebook/dinov2-giant
```

Mitigation currently running on HomePC:

```text
repo: facebook/dinov2-giant
local dir: /home/yuanhaizhou/models/hunyuan3d21_factory_20260513/models/facebook_dinov2_giant
allowed files: config.json, preprocessor_config.json, model.safetensors
expected model.safetensors size: 4546005432 bytes
endpoint: HF_ENDPOINT=https://hf-mirror.com
proxy env: command-local unset
```

An accidental broader download also left an incomplete `pytorch_model.bin`
partial. That file is not part of the accepted safetensors-only route and must
not be treated as a completed model artifact.

Next paint command should run with `HF_HUB_OFFLINE=1` and:

```python
conf.dino_ckpt_path = "/home/yuanhaizhou/models/hunyuan3d21_factory_20260513/models/facebook_dinov2_giant"
```

The Hunyuan route remains incomplete until the textured/PBR smoke produces an
output asset or fails with a documented model/runtime blocker after the DINOv2
download is complete.
