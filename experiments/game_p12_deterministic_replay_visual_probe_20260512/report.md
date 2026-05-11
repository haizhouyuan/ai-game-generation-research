# P12-A Game Deterministic Replay And Visual Probe Report

Status: P12-A HomePC headless run passed for replay; screenshot feasibility blocked by headless viewport readback.

Purpose: move beyond P11 signal existence by producing a deterministic tick-by-tick replay trace and checking whether the existing HomePC Godot headless path can provide a screenshot artifact without new display/GPU setup.

Planned gates:

- Deterministic replay follows a fixed step plan and records every tick: pass, `45` ticks.
- Area3D signal sequence remains `finish_locked -> checkpoint x3 -> finish_unlocked`: pass, `5` events.
- Finish lock/unlock: pass, `2` finish attempts.
- Screenshot feasibility: attempted; blocked because HomePC Godot headless returned an empty viewport image.

Artifacts:

- `outputs/p12_deterministic_replay_visual_probe_report.json`
- `outputs/godot_p12_replay_visual_probe_homepc.log`
- `outputs/artifact_hashes.json`
