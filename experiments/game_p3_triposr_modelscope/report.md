# GAME-P3 TripoSR ModelScope Prototype Report

| Field | Value |
|---|---|
| Task ID | `GAME-P3-TRIPOSR` |
| Status | pass-minimal with shim caveat |
| Machine | HomePC for model download/inference; YogaS2 for Three.js parse validation |
| Candidate | `stabilityai/TripoSR` |
| Decision | promote as first image-to-3D prototype path; program remains active |

## Commands

```bash
# HomePC no-proxy checkpoint download
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY="*" no_proxy="*" curl --noproxy "*" -4 --fail --location \
  https://www.modelscope.cn/models/stabilityai/TripoSR/resolve/master/model.ckpt

# HomePC no-proxy source intake via GitHub API blob endpoints
NO_PROXY="*" no_proxy="*" env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  python3 fetch_triposr_api_blobs.py

# HomePC minimal inference
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TRIPOSR_DINO_CONFIG=local_dino_vitb16_config.json \
  CUDA_VISIBLE_DEVICES=1 NO_PROXY="*" no_proxy="*" \
  env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  /home/yuanhaizhou/models/p3_ai_cad_game/envs/triposr/bin/python run.py examples/chair.png \
  --pretrained-model-name-or-path /home/yuanhaizhou/models/p3_ai_cad_game/experiments/triposr_minimal_model_dir \
  --output-dir /home/yuanhaizhou/models/p3_ai_cad_game/experiments/triposr_minimal_inference/output \
  --model-save-format glb --no-remove-bg --mc-resolution 64 --chunk-size 4096

# YogaS2 Three.js GLTFLoader parse
NODE_PATH=/vol1/1000/projects/ai-game-generation-research/experiments/game_p2_glb_three_import_loop/node_modules \
  node --input-type=module three-gltfloader-probe
```

## Download And Environment Evidence

| Item | Value |
|---|---|
| Weight URL | `https://www.modelscope.cn/models/stabilityai/TripoSR/resolve/master/model.ckpt` |
| Weight path | `/home/yuanhaizhou/models/p3_ai_cad_game/modelscope/stabilityai/TripoSR/model.ckpt` |
| Weight size | `1677246742` bytes |
| Weight SHA256 | `429e2c6b22a0923967459de24d67f05962b235f79cde6b032aa7ed2ffcd970ee` |
| No-proxy env | `/home/yuanhaizhou/models/p3_ai_cad_game/modelscope/stabilityai/TripoSR/no_proxy_env.txt` |
| Header evidence | `/home/yuanhaizhou/models/p3_ai_cad_game/modelscope/stabilityai/TripoSR/model.ckpt.download.headers` |
| Source manifest | `homepc_evidence/api_blob_manifest.tsv` |
| HomePC disk after batch | `/home` about `805G` free |

Dependency payload hashes:

| File | Size | SHA256 |
|---|---:|---|
| `omegaconf-2.3.0-py3-none-any.whl` | `79500` | `7b4df175cdb08ba400f45cae3bdcae7ba8365db4d165fc65fd04b050ab63b46b` |
| `antlr4-python3-runtime-4.9.3.tar.gz` | `117034` | `f224469b4168294902bb1efa80a8bf7855f24c99aef99cbefc1bcd3cce77881b` |

Local compatibility patch hashes:

| Patch | SHA256 |
|---|---|
| `torchmcubes.py` shim using `skimage.measure.marching_cubes` | `664053a309f0755e49d5574f583297662bdc0b46b5a78fbcd0eaf226e10f1b78` |
| patched `tsr/models/tokenizers/image.py` using local DINO config | `e0c53dcdb6a7889721dd8121db4202402c689155d1d7bcf7ce8cbc2af88ac79a` |
| local `dino-vitb16` config | `60e82f4a0adcde41186bc510a56b39f2e93aef6c33a6d0fa5482da9d54730efb` |

## Artifacts

| Artifact | Path | Evidence |
|---|---|---|
| Input image | `homepc_evidence/chair.png` | official TripoSR example, SHA256 recorded in source manifest |
| Inference log | `homepc_evidence/run4.log` | model load, forward pass, mesh extraction, and export passed |
| Output GLB | `outputs/triposr_chair_mesh.glb` | `120724` bytes, SHA256 `bac9412f54576127accaba9c17d8d257b1e85cfce6e27aa6f36b7bea359320c6` |
| Three.js parse log | `three_gltfloader_probe.log` | `status=pass`, `scenes=1`, `meshes=1`, `triangles=5984` |

Additional local validation on HomePC loaded the GLB with `trimesh` as a `Scene` containing 1 geometry, 2994 vertices, and 5984 faces.

## Capability Finding

This batch proves a minimal image-to-3D game asset path:

1. official sample image,
2. local TripoSR checkpoint,
3. local inference on HomePC GPU,
4. GLB export,
5. Three.js `GLTFLoader` parse on YogaS2.

## Boundaries

- This is not yet a playable scene; it is an image-to-GLB asset path plugged into the existing Three.js import validator.
- Mesh extraction used `mc-resolution 64`; quality is intentionally low for a fast, safe prototype.
- `torchmcubes` was not installed from the official GitHub requirement. The successful run used a local `skimage` shim, so P3.1 should validate official `torchmcubes` or keep this shim as an explicit fallback.
- `--no-remove-bg` avoided rembg model downloads; real user images with backgrounds remain untested.

## Next Recommendation

Use this GLB as the first generated asset in the Three.js playable loop, then run two more non-private images through the same path after deciding whether to approve official `torchmcubes` source installation.
