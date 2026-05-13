# Full Realistic Tactical Game Execution Plan - 2026-05-13

Target goal: `docs/production_goal_full_realistic_3d_tactical_game_final_2026-05-13.md`

Playable final experiment directory:

- `experiments/tactical_game_full_realism_final_20260513/`

## Controller Rules

- Use subagent-driven development for independent research/review slices.
- Keep implementation in the final experiment directory, not directly in `/Users/yuanshaochen/Documents/14.html`.
- Do not mark complete while a major visible asset class is only deferred.
- Browser evidence must fail on runtime exceptions, missing asset loads, or broken controls.

## Execution Slices

### Slice 1: Asset Kit Generation

Generate a Blender GLB kit covering:

- player tactical character;
- enemy tactical character;
- ammo box;
- bandage/medical pouch;
- first-aid kit;
- medkit;
- revive device;
- vest pickup;
- helmet pickup;
- crate/storage prop;
- building detail kit;
- tree;
- rock cluster.

Each exported asset must include:

- GLB;
- Blender preview PNG;
- mesh/material/bounding box report;
- SHA256 manifest entry.

### Slice 2: Game Integration

Modify `experiments/tactical_game_full_realism_final_20260513/index.html`:

- load final GLBs through an asset registry;
- attach player/enemy character overlays while preserving existing hit logic;
- use GLB loot props in `spawnLootAt()`;
- place environment GLB props in compound, interiors, yard, and loot areas;
- keep weapon GLBs from the previous pass;
- keep all fallbacks non-visible in final evidence.

### Slice 3: Visual Evidence Modes

Add evidence modes:

- `?evidence=weapons`;
- `?evidence=characters`;
- `?evidence=loot`;
- `?evidence=environment`;
- `?evidence=final`.

Each mode must stage the camera so screenshots visibly show the target asset class.

### Slice 4: Verification And Closeout

Required commands:

```bash
python3 experiments/tactical_game_full_realism_final_20260513/tools/verify_integration.py
python3 tools/verify_artifact_hashes.py experiments/tactical_game_full_realism_final_20260513/artifact_hashes.json
node --check experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs weapons
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs characters
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs loot
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs environment
node experiments/tactical_game_full_realism_final_20260513/tools/cdp_evidence_capture.mjs final
```

All CDP reports must have `blockingEvents: []`.

## Acceptance

The final answer can only call the goal complete if:

- every required class in the production goal has an upgraded in-game visual;
- every class has screenshot evidence;
- the game remains playable;
- the evidence packet and hash manifest are current.
