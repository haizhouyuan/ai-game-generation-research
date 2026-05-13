# GAME-P3 TripoSR Failure Ledger

| Step | Result | Evidence | Decision |
|---|---|---|---|
| Hugging Face direct path | fail | HomePC no-proxy curl probes timed out or reset. | Use ModelScope for weights. |
| ModelScope checkpoint download | pass | `model.ckpt` size and SHA256 match linked etag. | Promote no-proxy checkpoint path. |
| GitHub codeload zip | fail | Direct no-proxy codeload timed out and produced incomplete archives. | Do not rely on codeload for this repo. |
| Git shallow clone | fail | `GnuTLS recv error (-110)`. | Do not retry through proxy. |
| GitHub API blob source fetch | pass | `api_blob_manifest.tsv` records 17 selected files with size and SHA256. | Use for small source intake in P3. |
| `torchmcubes` install | blocked | No package available from Tsinghua PyPI mirror; official requirement is GitHub source. | Use local `skimage` shim for P3 only; validate official path later. |
| Mesh extraction attempt 1 | fail | local `mcubes` package lacked `marching_cubes`. | Replace shim implementation. |
| Mesh extraction attempt 2 | fail | negative NumPy stride prevented tensor conversion. | Copy arrays before `torch.as_tensor`. |
| GLB export attempt 3 | fail | `--no-remove-bg` path did not create `output/0`. | Precreate output directory. |
| Final GLB export | pass | `run4.log`, `triposr_chair_mesh.glb`, Three.js parse log. | Promote as P3 minimal image-to-3D path. |
