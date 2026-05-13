# Real 3D Game Asset Landing Lessons And Best Practices - 2026-05-13

## Repo Lessons

- "GLB loaded" does not mean "realistic 3D asset landed." The prior pass proved weapons and some geometry upgrades, but the final goal requires every major visible class to have concrete in-game evidence instead of deferred placeholders.
- The useful shape is asset packet plus evidence gates: GLB, preview, mesh/material/bounds report, runtime screenshot, CDP report, and hash entry.
- PBR evidence must be graded honestly. The current final experiment uses `material_factors_only`: detailed mesh assemblies and PBR-style material values, not baked albedo/normal/roughness/metallic texture maps.
- The custom `loadEmbeddedGlb()` path is enough for simple no-compression GLBs, but it is not the long-term route for texture-heavy production assets. Future final-quality swaps should migrate to official Three.js `GLTFLoader`.
- Browser evidence must fail closed. CDP reports need to reject runtime exceptions, network failures, browser log errors, missing showcase counts, and asset fallback states.
- Hash manifests go stale easily when experiments are copied. The final gate must verify paths, file existence, size, and SHA256 after all artifacts are written.

## Mature External Stack

- Three.js `GLTFLoader`: <https://threejs.org/docs/#examples/en/loaders/GLTFLoader>
- Three.js glTF loading manual: <https://threejs.org/manual/en/load-gltf.html>
- Khronos glTF Validator: <https://github.com/KhronosGroup/glTF-Validator>
- glTF 2.0 spec and PBR model: <https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html>
- Blender glTF exporter manual: <https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html>
- Blender Python export API: <https://docs.blender.org/api/current/bpy.ops.export_scene.html>
- glTF Transform CLI: <https://gltf-transform.dev/cli>
- gltfpack / meshoptimizer: <https://github.com/zeux/meshoptimizer/tree/master/gltf>
- Hunyuan3D 2.1: <https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1>
- TRELLIS: <https://github.com/microsoft/TRELLIS>
- TripoSR: <https://github.com/VAST-AI-Research/TripoSR>
- Hyper3D Rodin API: <https://developer.hyper3d.ai/api-specification/overview>
- OpenGame dynamic game-skill evaluation reference: <https://github.com/leigest519/OpenGame>
- OpenAI Codex subagents: <https://developers.openai.com/codex/subagents>

## Minimum Best Practices

1. Every asset class needs provenance, GLB, preview PNG, mesh/material/bounds report, SHA256, runtime screenshot, and CDP report.
2. Blender export should apply transforms, set realistic scale and origin, preserve named anchors such as `Muzzle`, `Grip`, `Mount`, and `PickupRoot`, and keep collision proxies separate from visible meshes.
3. Every imported GLB should be inspected and validated before integration:

```bash
gltf-transform inspect asset.glb
gltf-transform validate asset.glb
gltf_validator -o asset.glb > asset.validator.json
```

4. Optimization should happen after validation; if runtime anchors matter, use keep-name options such as `gltfpack -kn`.
5. Three.js runtime should prefer `GLTFLoader`; Meshopt, KTX2, and DRACO assets must explicitly configure their decoders and be covered by CDP network-failure checks.
6. Record material grade as `material_factors_only`, `baked_textures`, or `full_pbr_maps`.
7. Browser gates should check runtime exceptions, network errors, console errors, all asset status, showcase count, screenshot nonblank/variance, and basic playability.
8. Do not use generated visual meshes as gameplay collision unless intentionally documented. Collision proxies should stay separate.
9. Done means screenshot plus validator/parser evidence plus hash verification plus playable browser probe, not just model-file existence.

## Subagent Split

- `asset-auditor`: read `assets/models`, reports, and manifests; output missing evidence matrix.
- `gltf-validator`: run `gltf-transform inspect/validate` and Khronos validator; summarize mesh/material/texture/extension warnings.
- `blender-cleanup`: own scale, origin, anchors, preview renders, and export settings.
- `pbr-texture`: compare Hunyuan3D, TRELLIS, TripoSR, and Rodin routes; produce texture-map evidence and VRAM/API/download boundaries.
- `threejs-integration`: migrate custom GLB loading to `GLTFLoader`, configure decoders, and prove fallback did not trigger.
- `browser-gate`: maintain CDP scripts, screenshot nonblank checks, network/resource audits, and input smoke tests.
- `release-manifest`: close hashes, artifact index, evidence packet, and path-prefix validation without touching gameplay.
- `lead orchestrator`: keep the acceptance matrix and merge decisions in repo artifacts so subagents do not need hidden long-term state.
