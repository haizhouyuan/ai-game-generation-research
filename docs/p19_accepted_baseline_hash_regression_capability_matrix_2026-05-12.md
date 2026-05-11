# P19 Accepted-Baseline Hash Regression Capability Matrix

| Capability | P18 State | P19 State | Status |
|---|---|---|---|
| Compact trace hash ledger | emitted | accepted as baseline input | pass |
| Positive layout regression | hashes recorded | hashes compared against accepted baseline | pass |
| Negative fixture regression | hashes recorded | hashes compared against accepted baseline | pass |
| Route/event drift visibility | compact but not baseline-diffed | compact failure diff report highlights changed layout hash | pass |
| Missing negative fixture visibility | not explicit | missing `route_mismatch` counter is detected | pass |
| Full JSON dependency | full report retained | review can start from compact diff/hash files | improved |
| Visual/screenshot QA | not claimed | still not claimed | boundary |
| Mesh-accurate GLB collision | not claimed | still not claimed | boundary |
