# Game P3 Image-To-3D Capability Matrix - 2026-05-11

| Candidate | Status | Inputs Tested | Output | Engine/Runtime Validation | Evidence | Decision | Boundary |
|---|---|---:|---|---|---|---|---|
| `stabilityai/TripoSR` | pass-minimal with shim caveat | 1 official sample image | GLB | Three.js `GLTFLoader` parse passed | `/vol1/1000/projects/ai-game-generation-research/experiments/game_p3_triposr_modelscope/report.md` | promote to P3.1 | No playable-loop integration yet; local `torchmcubes` shim used. |

## Conclusion

TripoSR is the first verified neural image-to-3D path in the game-generation stream. It produced a nonzero GLB from an image and the resulting GLB can be parsed by the same Three.js stack used in P2.

## Next Gate

Before treating this as a recommended game asset pipeline, run:

- two more non-private images,
- official `torchmcubes` or approved local shim policy,
- Three.js playable import with movement/collision against the generated asset,
- optional Godot import after system package approval.
