# GAME-P4 TripoSR Failure Ledger

| Step | Result | Evidence | Decision |
|---|---|---|---|
| no-proxy/offline env | pass | `environment_no_proxy.log` | Continue explicit proxy-unset wrapper. |
| checkpoint hash | pass | `hash_and_dependency_probe.log` | Use existing ModelScope checkpoint. |
| dependency load | pass with caveat | `torchmcubes` resolves to local shim. | Keep caveat until official path is validated. |
| offline model load | pass | `offline_load_probe.log` | Promote to P5 playable loop. |
| GLB generation | pass | `minimal_glb_probe.log`, `outputs/triposr_p4_chair_mesh.glb` | Promote as generated asset. |
| Three.js parse | pass | `three_gltfloader_probe.log` | Use existing P2 Three.js path for P5. |
