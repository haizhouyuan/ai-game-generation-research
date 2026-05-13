# Texture Quality Gate - 2026-05-13

Tool:

```bash
python3 tools/validate_texture_quality.py
```

Purpose:

The packet and registry validators can prove that named texture files exist, but filename checks are not enough for production assets. This gate inspects PNG texture maps without third-party dependencies and blocks obvious placeholders.

Checks:

- file is a parseable PNG;
- width and height are at least `512` by default;
- sampled pixels are not a single solid value;
- texture kind is inferred from names such as `basecolor`, `normal`, `roughness`, `metallic`, and `ao`.

Current expected state:

```text
python3 tools/validate_texture_quality.py
```

exits `1` because the probe crate metallic map is a solid placeholder-like map:

```text
tactical_crate_trellis_texturealchemy_v1/textures/tactical_crate_metallic.png
error: solid_or_placeholder_like
```

This does not invalidate the Route C/D proof. It confirms that the crate remains a probe and should not be promoted to production-ready visual content.

Use this together with:

```bash
python3 tools/validate_asset_packets.py --production-goal
python3 tools/validate_asset_registry_v3.py --production-goal experiments/pubg_like_asset_factory_20260513/asset_registry_v3_probe.json
```
