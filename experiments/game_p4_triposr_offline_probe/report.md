# GAME-P4 TripoSR Offline Model Probe

| Field | Value |
|---|---|
| Task ID | `GAME-P4-TRIPOSR-OFFLINE-PROBE` |
| Status | pass with local shim caveat |
| Machine | HomePC via `ssh yuanhaizhou@192.168.1.17`; YogaS2 for Three.js parse |
| Candidate | `stabilityai/TripoSR` |
| Decision | keep for P5 image-to-3D-to-Three.js playable path |

## Commands

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY='*' no_proxy='*' \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TRIPOSR_DINO_CONFIG=local_dino_vitb16_config.json \
  CUDA_VISIBLE_DEVICES=1 \
  /home/yuanhaizhou/models/p3_ai_cad_game/envs/triposr/bin/python run.py examples/chair.png \
  --pretrained-model-name-or-path /home/yuanhaizhou/models/p3_ai_cad_game/experiments/triposr_minimal_model_dir \
  --output-dir /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p4_offline_model_probe_20260512/triposr/output \
  --model-save-format glb --no-remove-bg --mc-resolution 64 --chunk-size 4096
```

Actual logs are stored under `homepc_evidence/`.

## Evidence

| Probe | Evidence |
|---|---|
| no-proxy/offline env | `homepc_evidence/environment_no_proxy.log` |
| dependency/hash | `homepc_evidence/hash_and_dependency_probe.log` |
| offline load | `homepc_evidence/offline_load_probe.log` |
| GLB generation | `homepc_evidence/minimal_glb_probe.log` |
| GLB output | `outputs/triposr_p4_chair_mesh.glb` |
| Three.js parse | `three_gltfloader_probe.log` |

## Results

| Check | Result |
|---|---|
| checkpoint | `1677246742` bytes, SHA256 `429e2c6b22a0923967459de24d67f05962b235f79cde6b032aa7ed2ffcd970ee` |
| dependency load | required runtime modules imported; `torchmcubes` is local shim |
| model load | pass, `419275628` params, `cuda:0`, `2.702s` |
| GLB generation | pass, `outputs/triposr_p4_chair_mesh.glb`, `120724` bytes |
| GLB SHA256 | `bac9412f54576127accaba9c17d8d257b1e85cfce6e27aa6f36b7bea359320c6` |
| Three.js parse | pass, `scenes=1`, `meshes=1`, `triangles=5984` |

## Boundary

This is a real offline image-to-GLB run, but it is not yet a full game-engine path. It used the local `skimage` `torchmcubes` shim and low `mc-resolution=64`. P5 should integrate the generated GLB into the existing Three.js playable loop and either validate official `torchmcubes` or formally accept the shim as a fallback.

## Next Action

Run P5 with this GLB in the Three.js playable loop, add collision/scale checks, then run two more public/synthetic images through the same offline path.
