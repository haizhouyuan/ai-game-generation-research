# Unity Editor 6000.3.15f1 Approval Packet - 2026-05-13

## Result

No Unity Editor download or install was performed.

Unity Hub metadata and Unity release-page metadata identify `6000.3.15f1` as a viable Unity 6 arm64 Editor candidate, but the macOS ARM64 Editor package is `5,112,633,639` bytes, about `4.76 GiB`. This exceeds the project policy threshold, so it requires explicit user approval before download.

## Candidate

| Field | Value |
| --- | --- |
| Version | `6000.3.15f1` |
| Channel | stable `f1` release |
| Architecture | `arm64` |
| Changeset | `c1aa84e375f6` |
| Release date | 2026-05-08 |
| Hub install path | `/Applications/Unity/Hub/Editor` |
| Manual macOS ARM64 package URL | `https://download.unity3d.com/download_unity/c1aa84e375f6/MacEditorInstallerArm64/Unity-6000.3.15f1.pkg` |
| HEAD `Content-Length` | `5112633639` |
| Approval status | required before download |

## Evidence

- Hub arm64 release metadata: `experiments/unity_host_probe_20260513/outputs/unity_hub_releases_arm64.json`
- Hub release command metadata: `experiments/unity_host_probe_20260513/outputs/unity_hub_releases_arm64_meta.json`
- Hub install path: `experiments/unity_host_probe_20260513/outputs/unity_hub_install_path.txt`
- Candidate selection summary: `experiments/unity_host_probe_20260513/outputs/unity_editor_6000_3_15f1_selection_meta.json`
- Package HEAD response: `experiments/unity_host_probe_20260513/outputs/unity_6000_3_15f1_macos_arm64_pkg_head.txt`

## Commands Run

Query promoted arm64 releases without installing:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY='*' no_proxy='*' \
  /Applications/Unity\ Hub.app/Contents/MacOS/Unity\ Hub \
  -- --headless editors -r --json --architecture arm64
```

Query Hub install path:

```bash
/Applications/Unity\ Hub.app/Contents/MacOS/Unity\ Hub -- --headless install-path -g
```

Check candidate package headers only:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY='*' no_proxy='*' \
  curl -q --proxy '' --noproxy '*' -I -L --max-time 90 \
  https://download.unity3d.com/download_unity/c1aa84e375f6/MacEditorInstallerArm64/Unity-6000.3.15f1.pkg
```

Observed HEAD response:

```text
HTTP/1.1 200 OK
Content-Type: application/octet-stream
Last-Modified: Wed, 29 Apr 2026 20:02:07 GMT
ETag: "7a1f387478fcd42ad9640fc7d2add38b"
Accept-Ranges: bytes
Content-Length: 5112633639
```

## Available Arm64 Releases From Hub

```json
[
  {"version": "6000.6.0a3", "architecture": "arm64"},
  {"version": "6000.5.0b7", "architecture": "arm64"},
  {"version": "6000.3.15f1", "architecture": "arm64"},
  {"version": "6000.0.74f1", "architecture": "arm64"},
  {"version": "2022.3.62f3", "architecture": "arm64"},
  {"version": "6000.4.6f1", "architecture": "arm64"}
]
```

## Download Gate

Run these commands only after explicit user approval for this exact package/version/size, and only with command-local no-proxy controls plus lsof evidence:

- `Unity Hub -- --headless install --version 6000.3.15f1 --architecture arm64`
- any direct `curl`/installer download for `Unity-6000.3.15f1.pkg`
- `install-modules`
- `install-path --set`
- `--add`
- any installer command writing into `/Applications` or `/Applications/Unity/Hub/Editor`

This gate is not a download ban; it is a guard against accidentally pulling a multi-gigabyte package through paid proxy traffic or without operator confirmation. The first install should avoid optional build-support modules unless a specific Unity proof requires them.

## Sources

- `https://unity.com/es/releases/editor/whats-new/6000.3.15f1`
- `https://docs.unity.com/en-us/hub/hub-cli`
- `https://docs.unity.com/en-us/hub/add-editor`
