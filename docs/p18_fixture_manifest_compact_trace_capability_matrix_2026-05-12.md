# P18-A Game Fixture Manifest And Compact Trace Capability Matrix

| Capability | Evidence | Result | Boundary |
|---|---|---|---|
| Full headless negative scene CI | `p18_negative_scene_ci_full_report.json` | Pass: `3/3` positive layouts, `5/5` negative fixtures detected. | Proxy scene-node authority only. |
| Fixture manifest | `p18_fixture_manifest.json` | Pass: layout and negative fixture hashes emitted. | Review summary derived from full report. |
| Compact replay trace | `p18_compact_replay_trace.json` | Pass: event/objective order and negative diagnostics preserved compactly. | Not visual QA. |
| Trace hash ledger | `p18_trace_hashes.json` | Pass: full, manifest, compact, layout, and negative fixture hashes recorded. | Hashes anchor evidence identity only. |

Decision: promote P18 as a reviewable CI evidence layer for the P17 negative scene harness; keep screenshot/visual QA and mesh-accurate collision unclaimed.
