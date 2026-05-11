# P12-A Game Boundary Ledger

- Headless replay validates deterministic objective logic, not human game feel.
- Screenshot readback is a feasibility probe only. If Godot headless cannot return a usable viewport image, the batch records a blocker instead of requesting display/GPU changes.
- Replay still uses collision proxy Area3D nodes, not high-fidelity mesh collision.
