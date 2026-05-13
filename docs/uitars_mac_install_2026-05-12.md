# UI-TARS Mac Install Notes - 2026-05-12

## Result

UI-TARS Desktop is installed on this Mac:

- App path: `/Applications/UI TARS.app`
- Bundle identifier: `com.electron.ui-tars`
- App version: `0.2.4`
- Mac architecture: `arm64`
- Installed app size: `220M`
- macOS Gatekeeper assessment: `accepted`, source `Notarized Developer ID`

The app was launched once and process startup was verified.

## Source And Download Evidence

Official quick-start states that macOS can install UI-TARS Desktop from the releases page or via Homebrew cask:

```bash
brew install --cask ui-tars
```

The local Homebrew cask resolved:

- token: `ui-tars`
- name: `UI-TARS Desktop`
- version: `0.2.4`
- URL: `https://github.com/bytedance/UI-TARS-desktop/releases/download/v0.2.4/UI-TARS-0.2.4-arm64.dmg`

To respect the no-proxy/download governance boundary, the DMG was downloaded directly with:

```bash
curl --noproxy '*' -L --fail --show-error --progress-bar \
  -o external/downloads/ui-tars_20260512/UI-TARS-0.2.4-arm64.dmg \
  https://github.com/bytedance/UI-TARS-desktop/releases/download/v0.2.4/UI-TARS-0.2.4-arm64.dmg
```

Download evidence:

- DMG path: `external/downloads/ui-tars_20260512/UI-TARS-0.2.4-arm64.dmg`
- DMG size: `97M`
- HTTP content-length observed before download: `98,161,204` bytes
- SHA256: `30d06c29db88afb7295edb0ae557f8fbac2f47df137232ddbb9999a5a017dfd0`
- Hash file: `external/downloads/ui-tars_20260512/UI-TARS-0.2.4-arm64.dmg.sha256`
- No proxy environment variables were present in this shell.
- No model download was performed on the Mac.
- No >1GB download was performed.

Install command used:

```bash
hdiutil attach external/downloads/ui-tars_20260512/UI-TARS-0.2.4-arm64.dmg -nobrowse -readonly
ditto /Volumes/UI\ TARS/UI\ TARS.app /Applications/UI\ TARS.app
xattr -dr com.apple.quarantine /Applications/UI\ TARS.app
hdiutil detach /Volumes/UI\ TARS
```

## Required Manual Permissions

UI-TARS Desktop needs macOS GUI-control permissions before meaningful desktop automation:

- System Settings -> Privacy & Security -> Accessibility
- System Settings -> Privacy & Security -> Screen Recording

The official quick-start also notes that UI-TARS Desktop is currently only available for single monitor setup; multi-monitor setups may fail for some tasks.

## HomePC Prior Evidence

The current repo docs did not contain a UI-TARS capability entry before this note. However, HomePC does have local UI-TARS artifacts:

- Host: `homepc`
- Hostname: `yuanhaizhou-home`
- Thin config directory: `/home/yuanhaizhou/ui_tars_7b`
- Config file: `/home/yuanhaizhou/ui_tars_7b/config.json`
- Hugging Face cache: `/home/yuanhaizhou/.cache/huggingface/hub/models--bytedance-research--UI-TARS-7B-DPO`
- Cache size observed: `16G`
- Model config says `model_type: qwen2_vl`, architecture `Qwen2VLForConditionalGeneration`, `torch_dtype: bfloat16`

This supports the user's memory that UI-TARS had been tried or at least downloaded on HomePC, but it is not yet a managed capability because no runnable server/API proof or UI-TARS Desktop configuration proof has been captured.

## Current Boundary

Installed does not mean operationally integrated.

Still missing:

- UI-TARS Desktop settings/configuration evidence.
- Local or remote VLM endpoint configured in the app.
- Proof that the Mac app can control a browser or desktop target.
- Proof that HomePC model cache can serve an OpenAI-compatible endpoint for UI-TARS Desktop.
- Security boundary for desktop-control tasks.

The official quick-start says the old Remote Operator service was discontinued on August 20, 2025. Use local/self-hosted model service or a supported provider path rather than relying on the old remote operator.

## Next Steps

1. Manually grant Accessibility and Screen Recording permissions for `/Applications/UI TARS.app`.
2. Decide provider route:
   - use HomePC as model server if we can expose a local/LAN OpenAI-compatible endpoint safely, or
   - configure a supported external provider in UI-TARS Desktop settings.
3. If using HomePC:
   - verify GPU memory and model server command,
   - bind only to LAN or localhost-over-SSH tunnel,
   - do not expose the API publicly,
   - record endpoint, model name, launch command, logs, and a one-screenshot inference proof.
4. Add a managed capability entry only after a real smoke test passes:
   - screenshot input,
   - model response/action parse,
   - browser or desktop operator action,
   - logs and hash/provenance evidence.
