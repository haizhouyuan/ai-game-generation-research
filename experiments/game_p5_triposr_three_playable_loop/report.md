# GAME-P5-A TripoSR To Three.js Playable Loop Report

| Field | Value |
|---|---|
| Task ID | `GAME-P5-A-TRIPOSR-THREE-PLAYABLE-LOOP` |
| Status | pass with local shim caveat |
| Machine | HomePC for TripoSR inference; YogaS2 for Three.js playable validation |
| Decision | promote to P6 engine-import candidate |

## Scope

P5-A placed the P4 TripoSR GLB into a Three.js playable loop, checked GLTF import, scale normalization, bounding boxes, collision probe status, and screenshot nonblank output. It then ran two additional local synthetic images through the already-downloaded TripoSR code/model on HomePC in offline/no-proxy mode and validated those generated GLBs in the same loop.

## No-Proxy/Offline Proof

HomePC synthetic generation used `NO_PROXY='*'`, `no_proxy='*'`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and removed all standard proxy variables.

Evidence:

- `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/homepc_evidence/environment_no_proxy.json`
- `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/homepc_evidence/triposr_synthetic_summary.json`
- `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/homepc_evidence/triposr_synthetic_run.log`

## Commands

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY='*' no_proxy='*' HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES=1 \
  /home/yuanhaizhou/models/p3_ai_cad_game/envs/triposr/bin/python \
  /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p5_triposr_synthetic_probe_20260512/tools/run_triposr_synthetic_homepc.py \
  /home/yuanhaizhou/models/p3_ai_cad_game/repos/triposr_raw_fetch/source \
  /home/yuanhaizhou/models/p3_ai_cad_game/experiments/triposr_minimal_model_dir \
  /home/yuanhaizhou/models/p3_ai_cad_game/experiments/p5_triposr_synthetic_probe_20260512

node tools/parse_glb_assets.mjs outputs/assets outputs/asset_parse_inventory.json

python3 -m http.server 8136 --bind 127.0.0.1
google-chrome --headless --no-sandbox --disable-dev-shm-usage --enable-unsafe-swiftshader \
  --virtual-time-budget=4500 --window-size=1280,720 \
  --screenshot=<asset screenshot> \
  "http://127.0.0.1:8136/game_p5_triposr_three_playable_loop/index.html?asset=<asset>"
```

## Generated Assets

| Asset | Source | Bytes | SHA256 |
|---|---|---:|---|
| `triposr_p4_chair_mesh.glb` | P4 existing artifact | 120724 | `bac9412f54576127accaba9c17d8d257b1e85cfce6e27aa6f36b7bea359320c6` |
| `triposr_p5_synthetic_block.glb` | P5 synthetic image | 84084 | `5748cef4e2f48d427449123fc4247474cf18c5c1979a71ac9f0372a6666e4c47` |
| `triposr_p5_synthetic_tower.glb` | P5 synthetic image | 54084 | `aa38c6a9804692ad04b72483c4bb6452b3c8ab8c64a82afece4dea52fa00e6b2` |

## Playable Import Matrix

Machine-readable matrix:

- `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/outputs/game_p5_import_scale_collision_matrix.json`

Summary:

| Asset | GLTF parse | Triangles | Playable DOM status | Screenshot |
|---|---|---:|---|---|
| `triposr_p4_chair_mesh.glb` | pass | 5984 | `GLB=loaded`, `collisionProbe=true`, `state=running` | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/outputs/verification/p4_chair_playable.png` |
| `triposr_p5_synthetic_block.glb` | pass | 4152 | `GLB=loaded`, `collisionProbe=true`, `state=running` | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/outputs/verification/triposr_p5_synthetic_block_playable.png` |
| `triposr_p5_synthetic_tower.glb` | pass | 2652 | `GLB=loaded`, `collisionProbe=true`, `state=running` | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p5_triposr_three_playable_loop/outputs/verification/triposr_p5_synthetic_tower_playable.png` |

## Capability Finding

The image-to-3D-to-playable browser loop is now real for small assets: local images can become GLBs on HomePC and those GLBs can be imported into a Three.js playable loop with scale/collision checks. This does not yet prove Godot/Unity import quality, textured assets, animation, or production gameplay quality.

## Blockers

- Official `torchmcubes` validation is still unresolved; current TripoSR path uses the local shim recorded in P4.
- Godot/Unity import validation still needs install/runtime approval.

## Next Action

P6 should take the same GLBs into a real engine import path, preferably Godot CLI/editor import first, while preserving the Three.js loop as a quick validator.
