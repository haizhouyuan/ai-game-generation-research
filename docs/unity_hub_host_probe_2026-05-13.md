# Unity Hub Host Probe - 2026-05-13

## Result

Unity Hub is now installed locally, but Unity Editor and Unity MCP are still not available.

| Check | Result |
| --- | --- |
| Unity Hub app | `/Applications/Unity Hub.app` |
| Unity Hub version | `3.18.0` |
| Unity Editor install list | empty `[]` from Hub headless `editors -i --json` |
| `unity` CLI on PATH | not found |
| `unity-hub` CLI on PATH | not found |
| Unity AI/MCP relay | not found |
| `unity-mcp-001` state | still blocked |

## Commands

Installed app/version:

```bash
defaults read '/Applications/Unity Hub.app/Contents/Info.plist' CFBundleShortVersionString
defaults read '/Applications/Unity Hub.app/Contents/Info.plist' CFBundleVersion
find /Applications -maxdepth 4 \( -iname '*Unity*' -o -iname 'Unity Hub.app' \) -print 2>/dev/null
```

Hub headless help:

```bash
/Applications/Unity\ Hub.app/Contents/MacOS/Unity\ Hub -- --headless help
```

Evidence:

- `experiments/unity_host_probe_20260513/outputs/unity_hub_headless_help.txt`
- `experiments/unity_host_probe_20260513/outputs/unity_hub_editors_installed.json`

Installed editors:

```bash
/Applications/Unity\ Hub.app/Contents/MacOS/Unity\ Hub -- --headless editors -i --json
```

Observed:

```json
[]
```

## Official Requirements Snapshot

Unity's current AI page says Unity AI includes Assistant, AI Gateway, and Unity's Official MCP Server. It also says the setup requires Unity `6.0+`, AI packages, accepting in-editor terms, and linking the project to Unity Cloud. It states the MCP Server requires a Unity AI Beta subscription.

Sources:

- `https://unity.com/features/ai`
- `https://docs.unity.com/en-us/hub/hub-cli`

## Decision

This probe unblocks the first host layer only: Hub exists and its headless command surface works. It does not complete `unity-mcp-001`.

`unity-mcp-001` remains blocked until at least one Unity Editor 6.x installation exists and a disposable Unity project can prove local editor control. Official MCP remains separately gated by account/subscription, package install, Unity Cloud linkage, AI terms, and relay availability.

## Next Evidence Gate

Before any Editor install:

1. Query available Hub releases for `arm64` without installing. Completed in `experiments/unity_host_probe_20260513/outputs/unity_hub_releases_arm64.json`.
2. Select a Unity 6.x Editor version and determine download/module size. Candidate packet: `docs/download_records/unity_editor_6000_3_15f1_approval_2026-05-13.md`.
3. If any single file is over `1GB`, get explicit approval before download. The selected macOS ARM64 package is `5,112,633,639` bytes, so approval is required before any Editor download.
4. Use command-local no-proxy controls and lsof evidence for downloads.
5. After Editor install, run a disposable project proof: editor version, project creation/open, scene mutation, script/material write, console/log readback, screenshot or play-mode/test proof.
