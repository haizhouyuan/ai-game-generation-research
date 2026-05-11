# P18-A Boundary Ledger

| Area | Current Fact | Boundary |
|---|---|---|
| Fixture manifest | Positive layouts and negative fixtures now have compact hashes and expected-failure summaries. | Manifest derives from the full headless report. |
| Compact trace | Event order, objective order, mismatch details, clearance diagnostics, finish-lock diagnostics, and camera failure counts are compacted. | It does not replace the full JSON for deep debugging. |
| Hash evidence | Full report, manifest, compact trace, per-layout trace, and per-fixture trace hashes are recorded. | Hashes prove artifact identity, not gameplay quality. |
| Runtime | Existing HomePC Godot 4.4.1 headless path with no-proxy environment. | No display/driver/reboot/public exposure changes. |
| Visual/mesh claims | None. | Screenshot/visual QA and mesh-accurate GLB collision remain unclaimed. |
