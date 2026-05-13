# Asset Packet Validation - 2026-05-13

This note documents the small repo-side validator for the PUBG-like full AI 3D asset factory.

Tool:

```bash
python3 tools/validate_asset_packets.py
python3 tools/validate_asset_packets.py --markdown
python3 tools/validate_asset_packets.py --strict
```

Default scan root:

```text
experiments/pubg_like_asset_factory_20260513/assets
```

## What It Checks

For each immediate asset packet directory, the validator reports whether these required packet directories exist:

- `source/`
- `model/`
- `textures/`
- `reports/`
- `evidence/`

It also counts files in `textures/` whose names look like:

- basecolor or albedo
- normal
- roughness
- metallic
- ambient occlusion / AO

Finally, it counts image and video evidence files under `evidence/`.

JSON is emitted by default so orchestration scripts can consume the result. `--markdown` emits a review-friendly table for task board updates and runner handoffs.

## Strict Mode

Default mode is informational and exits zero. This is deliberate: early packet slots may exist before an asset route has produced geometry, textures, or evidence.

`--strict` exits nonzero only when a scanned packet is missing one of the required packet directories. It does not fail just because texture maps or evidence are missing.

## Why This Supports The Full Rebuild

The current production goal is a full local asset-factory rebuild, not a light visual upgrade. Each final near-camera or mission-critical asset needs a traceable chain:

```text
reference/provenance -> generated or authored 3D/PBR asset -> Blender cleanup -> Three.js evidence
```

The validator gives the controller a cheap first pass over the packet inventory. It answers:

- Which asset targets have the standard packet scaffold?
- Which packets already contain PBR-named texture maps?
- Which packets have visible evidence media?
- Which packets are structurally incomplete before a worker starts writing into them?

That makes it useful for assigning narrow worker tasks and for spotting empty slots that should not be mistaken for produced assets.

## Directory Presence Is Not Completion

A packet with `source/`, `model/`, `textures/`, `reports/`, and `evidence/` is only structurally ready. It is not production-ready until the contents prove the asset chain.

For example, a complete final packet still needs evidence such as:

- reference prompt/source and license notes;
- raw, cleaned, and optimized model outputs;
- material reports with real texture map counts;
- Blender cleanup report;
- validator or inspect report for the GLB;
- Blender preview image;
- Three.js close-up and gameplay-context screenshots.

Empty directories, `.gitkeep` files, shape-only demos, or material-factor-only assets are useful progress markers. They are not completion for the PUBG-like asset factory goal.
