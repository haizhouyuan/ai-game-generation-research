# GAME-P2 Failure Ledger

## 2026-05-11

| Item | Status | Evidence | Decision |
|---|---|---|---|
| HomePC GLB generation | pass | `outputs/glb_asset_inventory.json`, 3 GLB assets copied back. | Promote. |
| Asset inventory verification | fixed/pass | First verifier used HomePC `/tmp/...` absolute paths and failed after rsync; verifier now resolves local `outputs/assets/`. | Keep as resolved local-path bug. |
| Three.js import map | fixed/pass | Initial `GLTFLoader` browser module resolution needed an import map for bare `three`. | Keep import map in `index.html`. |
| Headless WebGL | pass with warning | Chrome logged transient GPU/SwiftShader messages but produced 1280x720 non-flat screenshots and DOM `GLB=loaded`. | Treat as headless verification warning, not blocker. |
| Model download | not used | No image-to-3D model/checkpoint files downloaded. | No model approval consumed. |
| System package install | not used | Godot was only probed; no install was run. | Godot remains install-plan only. |
