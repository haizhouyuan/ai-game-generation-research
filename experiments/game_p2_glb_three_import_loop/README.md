# GAME-P2 GLB To Three.js Playable Import Loop

Safe P2 experiment for moving from procedural browser-only pilot toward a real local asset import loop.

## Scope

- Generate local GLB assets on HomePC with existing Python `trimesh`.
- Import the GLB assets in a local Three.js scene using `GLTFLoader`.
- Provide a minimal playable loop: movement, benchmark switching, collectibles, hazards, finish zone.
- No model weights, private uploads, external hosted assets, or system package installs.

## Run

```bash
npm install
./tools/generate_assets_on_homepc.sh
python3 -m http.server 8130 --bind 127.0.0.1
```

Open `http://127.0.0.1:8130/index.html`.

Artifacts are written to `outputs/`.
