# Route C ComfyUI PBR Probe 004 Summary

## Verdict

`usable_with_cleanup`

## Host And Runner

- Host: HomePC (`yuanhaizhou-home`)
- Runner: Codex orchestrated preflight and minimal PBR run
- GPU: GPU1 available at preflight; minimal TextureAlchemy run used CPU/PyTorch tensor ops

## Commands Run

```bash
git -C /home/yuanhaizhou/ComfyUI rev-parse HEAD
find /home/yuanhaizhou/ComfyUI/custom_nodes -maxdepth 2 -type d | sort

env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  git clone https://github.com/amtarr/ComfyUI-TextureAlchemy.git

python3 reports/run_texturealchemy_minimal_pbr.py
sha256sum textures/tactical_crate_*.png > reports/texture_sha256.txt
```

## Custom Nodes / Versions

- ComfyUI revision: `fce0398470fe3ecdb7ab4c5c69555ad0fcbdc09e`
- Installed node: `ComfyUI-TextureAlchemy`
- TextureAlchemy revision: `0afda45713c7b33afbf9d4f757493cca2004f65f`
- TextureAlchemy node import check: 131 node mappings loaded

## Workflow JSON

Saved example workflows from the installed node:

- `workflows/texturealchemy_03_channel_packing_orm.json`
- `workflows/texturealchemy_10_fastest_pbr_extraction.json`

The first practical run used TextureAlchemy node classes directly rather than a live ComfyUI server because this was a headless proof run.

## Generated Outputs

Input:

- `inputs/tactical_crate_reference.png`

Texture outputs:

- `textures/tactical_crate_basecolor.png`
- `textures/tactical_crate_height.png`
- `textures/tactical_crate_normal.png`
- `textures/tactical_crate_roughness.png`
- `textures/tactical_crate_metallic.png`
- `textures/tactical_crate_ao.png`
- `textures/tactical_crate_orm.png`

## PBR Map Count

- basecolor: 1
- normal: 1
- roughness: 1
- metallic: 1
- ao: 1
- height: 1
- ORM packed: 1

## Evidence

- `reports/material_report.json`
- `reports/run_texturealchemy_minimal_pbr.log`
- `reports/texturealchemy_import_check.log`
- `reports/texture_sha256.txt`

## Blockers / Next Action

This is a useful Route C proof, but it is not final production texture quality.

The generated maps are heuristic maps derived from a single reference image. For final PUBG-like assets, Route C still needs one of:

- multi-view texture projection onto an actual generated mesh;
- Hunyuan Paint/PBR output;
- StableGen/Blender texture baking;
- a ComfyUI workflow run using the UI/API, not only direct node-class invocation.

The immediate next action is to apply these maps to the TRELLIS crate GLB in Blender or Three.js and inspect whether the result is visually acceptable as a background prop.
