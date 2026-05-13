# Unity Editor MCP Probe Template

## Purpose

Use this template after explicit approval exists for the Unity Editor download, or when a worker needs to prove the current Unity host state without downloading anything.

The goal is to move `unity-mcp-001` from "Hub exists" to a clearly evidenced state: either a local Unity Editor can open and mutate a disposable project, or the lane remains blocked with a precise approval, account, package, MCP, or editor reason.

Do not mutate production Unity projects. Do not print account tokens, license values, Unity session data, API keys, or credentials into logs, evidence, or prompts.

## Inputs

Fill these fields before the probe:

| Field | Value |
|---|---|
| `task_id` | `unity-mcp-001` |
| `lane_id` | `unity-agent-mcp` |
| `repo_id` | `ai-game-generation-research` |
| `editor_version` | `6000.3.15f1` or approved replacement |
| `architecture` | `arm64` |
| `changeset` | `c1aa84e375f6` or approved replacement |
| `package_url` | `https://download.unity3d.com/download_unity/c1aa84e375f6/MacEditorInstallerArm64/Unity-6000.3.15f1.pkg` or approved replacement |
| `content_length_bytes` | `5112633639` or refreshed HEAD value |
| `approval_path` | `docs/download_records/unity_editor_6000_3_15f1_approval_2026-05-13.md` or explicit approval note |
| `hub_path` | `/Applications/Unity Hub.app/Contents/MacOS/Unity Hub` |
| `install_root` | `/Applications/Unity/Hub/Editor` |
| `editor_app_path` | `/Applications/Unity/Hub/Editor/<editor_version>/Unity.app` |
| `project_path` | `<absolute disposable project path outside production projects>` |
| `mcp_route` | `<official-unity-ai-mcp, community-unity-mcp, none>` |
| `account_terms_status` | `<unknown, accepted, blocked, not-required-for-editor-only-proof>` |
| `out_dir` | `<immutable evidence directory>` |

Required preconditions:

- Any single Unity Editor package over `1GB` has explicit user approval before download or install.
- Any Editor download uses command-local no-proxy controls and `lsof` evidence during a meaningful part of the transfer.
- Unity Hub is already installed and the target version/package metadata has been captured without installing.
- The first project proof uses a disposable project only.
- Official Unity MCP work is treated as account/package gated until Unity 6.x, Unity AI packages, account terms, Unity Cloud linkage, subscription requirements, and relay availability are all proven.
- Community MCP work is treated as untrusted integration until its source, install command, permissions, and local control surface are documented.

## Commands / Placeholders

Current host checks that do not download:

```bash
"<hub_path>" -- --headless help > "<out_dir>/unity_hub_headless_help.txt"
"<hub_path>" -- --headless editors -i --json > "<out_dir>/unity_hub_editors_installed.json"
"<hub_path>" -- --headless install-path -g > "<out_dir>/unity_hub_install_path.txt"
```

Metadata-only package check:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
    -u http_proxy -u https_proxy -u all_proxy \
    NO_PROXY='*' no_proxy='*' \
  curl -q --proxy '' --noproxy '*' -I -L --max-time 90 \
  "<package_url>" \
  > "<out_dir>/unity_editor_pkg_head.txt"
```

Stop here when `content_length_bytes` is over `1GB` and explicit approval is not present.

Approved download/install path:

```bash
# REQUIRED: run only after approval_path records explicit approval for this exact package/version.
tools/download_no_proxy.sh \
  "<package_url>" \
  "<out_dir>/Unity-<editor_version>.pkg" \
  "<max_seconds>" \
  "<max_bytes>"

lsof -nP -iTCP | rg -i 'curl|Unity|7890|7897|7899|clash|verge' \
  > "<out_dir>/unity_editor_download_lsof.txt"

shasum -a 256 "<out_dir>/Unity-<editor_version>.pkg" \
  > "<out_dir>/unity_editor_pkg_sha256.txt"
wc -c "<out_dir>/Unity-<editor_version>.pkg" \
  > "<out_dir>/unity_editor_pkg_bytes.txt"

# Prefer Hub install if it can use the retained package or governed command.
# If a macOS installer is required, document the exact command and do not run it
# until the approval covers writes into /Applications.
```

Installed Editor proof:

```bash
"<hub_path>" -- --headless editors -i --json \
  > "<out_dir>/unity_hub_editors_installed_after.json"

"<editor_app_path>/Contents/MacOS/Unity" -version \
  > "<out_dir>/unity_editor_version.txt"
```

Disposable project mutation proof:

```bash
mkdir -p "<project_path>"

"<editor_app_path>/Contents/MacOS/Unity" \
  -batchmode \
  -quit \
  -createProject "<project_path>" \
  -logFile "<out_dir>/unity_create_project.log"

# Add a small Editor script inside the disposable project that creates:
# - scene file: Assets/Scenes/ManagedAgentsProbe.unity
# - cube named ManagedAgentsProbeCube
# - material named ManagedAgentsProbeMaterial
# - camera and directional light
# - JSON report with object/material/scene names

"<editor_app_path>/Contents/MacOS/Unity" \
  -batchmode \
  -quit \
  -projectPath "<project_path>" \
  -executeMethod ManagedAgentsProbe.Run \
  -logFile "<out_dir>/unity_scene_mutation.log"

find "<project_path>" -maxdepth 4 -type f \
  | sort \
  > "<out_dir>/unity_project_file_manifest.txt"
```

MCP/package route proof:

```bash
# Official Unity AI MCP route:
# Record package names/versions, Unity Cloud linkage status, AI terms state,
# subscription or beta gate, and relay process path without printing secrets.

# Community MCP route:
# Record source URL/revision, install command, local server command,
# allowed project path, and a harmless readback/mutation method.

# In both cases, prove connection with a disposable project readback first,
# then a harmless scene mutation, then log/screenshot/test evidence.
```

Screenshot or play/test proof:

```bash
"<editor_app_path>/Contents/MacOS/Unity" \
  -batchmode \
  -quit \
  -projectPath "<project_path>" \
  -runTests \
  -testPlatform EditMode \
  -testResults "<out_dir>/unity_editmode_test_results.xml" \
  -logFile "<out_dir>/unity_editmode_tests.log"
```

If GUI screenshot proof is needed, capture only the disposable project and record the capture command, image path, and hash.

## Required Evidence

The evidence directory must contain:

- Approval note for the exact Editor package when the package is over `1GB`, or a clear `approval_required` blocker report.
- Hub headless help, install path, and installed-editor JSON before and after any install.
- Package HEAD response with `Content-Length`, URL, version, architecture, and changeset.
- Exact download/install command text, no-proxy `lsof` evidence, byte count, and SHA256 for any retained package.
- Editor version output from the installed Editor binary.
- Disposable project absolute path and file manifest.
- Package manifest from the disposable Unity project.
- Scene mutation report, Unity logs, and test/screenshot evidence.
- MCP route record stating official Unity AI MCP, community MCP, or no MCP route, with account/terms/package/subscription blockers when applicable.
- A short report listing pass/fail status, limitations, and the next concrete action.

## Pass Criteria

- No Unity Editor package over `1GB` is downloaded or installed without explicit approval.
- Any approved download has no-proxy process evidence and artifact hash/byte count.
- Unity Hub can list the installed target Editor, or the result is recorded as an explicit blocked state.
- The installed Editor binary reports the expected version.
- A disposable project is created or opened without mutating production projects.
- A scene mutation is verified through project files plus Unity log/readback/test/screenshot evidence.
- MCP is either proven with a harmless disposable-project readback/mutation or blocked with a precise account/package/terms/relay/source reason.
- Evidence and docs do not claim Unity game import or production readiness unless a real import loop has been verified.

## Failure Modes

Record these as blockers, risky items, or controller issues:

- `approval_required`: selected package exceeds `1GB` and lacks explicit approval.
- `proxy_evidence_failed`: download process appears to use local Clash/Verge ports.
- `hub_install_failed`: Unity Hub exists but cannot install or list the approved Editor.
- `editor_missing`: no installed Editor binary exists after the expected install path.
- `editor_version_mismatch`: installed Editor version differs from approved target.
- `account_terms_blocked`: Unity account login, terms, Cloud linkage, subscription, or beta access blocks official MCP.
- `mcp_unavailable`: MCP relay/server cannot be found, installed, started, or connected.
- `package_install_failed`: Unity package installation fails or cannot be audited.
- `scene_mutation_failed`: disposable project opens but scene/object/material mutation cannot be verified.
- `log_readback_failed`: Unity log, test result, or readback evidence is missing.
- `screenshot_failed`: requested screenshot/play/test evidence cannot be captured.
- `production_project_risk`: command would mutate a non-disposable project.
- `secret_exposure`: evidence contains account tokens, session data, API keys, or credentials.

Use `status: "needs_human"` when approval, account action, subscription, terms acceptance, broad application writes, or manual Unity GUI steps are required.

## Current Local Proof

Current dated evidence shows:

- Unity Hub is installed at `/Applications/Unity Hub.app`.
- Unity Hub version is `3.18.0`.
- Hub headless help works.
- Hub installed-editor JSON is empty: `[]`.
- Unity `6000.3.15f1` arm64 is selected as the next Editor candidate.
- The selected macOS ARM64 package reports `Content-Length: 5112633639`, so it must not be downloaded or installed without explicit approval.
- Official Unity MCP remains unproven and is expected to require Unity 6.x, Unity AI packages, account/terms/Cloud/subscription readiness, and local relay proof.

Current evidence paths:

- `docs/unity_hub_host_probe_2026-05-13.md`
- `docs/download_records/unity_editor_6000_3_15f1_approval_2026-05-13.md`
- `experiments/unity_host_probe_20260513/outputs/unity_hub_headless_help.txt`
- `experiments/unity_host_probe_20260513/outputs/unity_hub_editors_installed.json`
- `experiments/unity_host_probe_20260513/outputs/unity_editor_6000_3_15f1_selection_meta.json`
- `experiments/unity_host_probe_20260513/outputs/unity_6000_3_15f1_macos_arm64_pkg_head.txt`
