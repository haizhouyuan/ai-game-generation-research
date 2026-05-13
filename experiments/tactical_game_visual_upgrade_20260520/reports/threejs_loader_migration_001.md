# Three.js Loader Migration 001 Report

## Result

Added the first modular runtime loader and registry facade for the tactical visual-upgrade experiment.

## Files

- `src/runtime/assetRegistry.js`
- `src/runtime/assetLoader.js`

## Implemented Contract

- Registry v2 fetch/index helpers.
- Fixed six evidence camera names.
- Material map counting from registry declarations and loaded Three.js materials.
- Required anchor summaries for weapon and character entries.
- Official `GLTFLoader` path with optional KTX2, Meshopt, and Draco loader injection.
- Evidence-mode fallback failure via `createFallback()`.
- Evidence snapshot API for browser/CDP gate scripts.

## Verification

```bash
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetLoader.js
node --check experiments/tactical_game_visual_upgrade_20260520/src/runtime/assetRegistry.js
```

Result: both commands exited `0`.

## Notes

This is a runtime module skeleton. The next task should add an `index.html` or app entrypoint that imports these modules, maps registry entries into visible scene assets, and exposes the six evidence camera modes.
