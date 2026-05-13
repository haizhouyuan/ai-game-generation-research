# HomePC GPU Job Contract

Use this format for HomePC/dual-3090 GPU jobs.

```yaml
task_id: asset-hero-rifle-hunyuan-001
owner: homepc-gpu-worker
gpu: 0
download_policy:
  over_100mb_no_proxy_required: true
  over_1gb_user_approval_required: true
  command_local_no_proxy_template: "env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY curl --noproxy '*' -L --fail --continue-at - --output OUTPUT URL"
input:
  reference_images: []
  source_meshes: []
output:
  expected:
    - outputs/hero_rifle_candidate.glb
    - outputs/hero_rifle_preview.png
    - outputs/material_report.json
acceptance:
  - glb_exists
  - preview_exists
  - material_maps_or_failure_reason
  - no_missing_texture
  - sha256_recorded
```

## Return Packet

Every GPU job returns:

- command log;
- download log if any;
- artifact paths;
- SHA256;
- material report;
- preview image;
- failure reason if no usable asset was produced.

