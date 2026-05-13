# No-Proxy Godot Install Plan Contingency

This is a contingency plan only. P6-A did not install anything because HomePC already has `/home/yuanhaizhou/godot/godot`.

If a future task needs Godot on YogaS2 or a clean HomePC runtime:

1. Check local cache first: `/home/yuanhaizhou/godot/`, `/vol1/1000`, `/opt`, and prior `homepc-llm-opt` logs.
2. Prefer a direct LAN copy of the existing HomePC binary if license/version is acceptable.
3. If download is required, clear proxy variables and use a verified mirror/direct URL:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY='*' no_proxy='*' \
  <download command>
```

4. Record URL, expected file size, SHA256, disk target, and version before running.
5. Stop for user approval before any large download or system package install.

Fallback gate while no local install exists:

- Three.js validator remains the fast local gate for GLB parse, bbox, scale, collision probe, and screenshot checks.
- Godot validation can run on HomePC existing binary until a YogaS2 install is approved.
