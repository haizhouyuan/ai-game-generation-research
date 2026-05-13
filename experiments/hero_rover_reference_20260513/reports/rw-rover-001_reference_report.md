# RW-ROVER-001 Reference Report - 2026-05-13

## Result

`RW-ROVER-001` now has an OpenAI-generated orthographic reference image saved inside the project:

- image: `experiments/hero_rover_reference_20260513/inputs/rw-rover-001_orthographic_reference_openai_20260513.png`
- sha256: `60fbef87cfcde012219131c336697d9a7c551d77e329f9b1f21454fc39fdb930`
- dimensions: `1536x1024`
- provenance: `experiments/hero_rover_reference_20260513/provenance/rw-rover-001-reference.json`

## Prompt

```text
Use case: stylized-concept
Asset type: orthographic model reference sheet for downstream image-to-3D generation in a child-friendly 3D browser game.
Primary request: Create an orthographic model reference sheet for a friendly small workshop rover character for a child-friendly 3D game.
Subject: The same compact rover shown consistently in front view, side view, back view, and top view. Compact rounded body, four chunky rubber wheels, tiny antenna, expressive headlight eyes, teal shell, soft graphite tires, cyan lamp lens, small orange tool module, toy-like materials, simple clean silhouette.
Composition: Four clean orthographic views arranged on a light neutral background with generous spacing. Consistent proportions across views. High contrast and readable silhouette for 3D modeling.
Style: premium toy-like 3D game asset reference, rounded safe shapes, saturated but not harsh colors, simple production-reference lighting.
Constraints: no weapons, no humanoid enemies, no text, no labels, no logos, no background clutter, no scary mood, no shadows that hide silhouette.
```

## Review

The output satisfies the first reference gate for the hero rover chain:

- front, side, back, and top-style views are present;
- rover identity is teal with graphite tires, cyan lamps, and orange tool details;
- the shape language is rounded, toy-like, and child-friendly;
- no weapons, combat framing, horror, text, logos, or clutter are present.

## Limitations

- This is only a reference sheet. It is not a GLB, not Blender-cleaned, not Three.js-validated, and not Unity-imported.
- Single-image 3D tools may prefer a cropped isolated view rather than the full four-view sheet.
- Generated-mesh collision remains prohibited; future gameplay integration must use a simple collider proxy.

## Next Step

Run one rover 3D candidate path using existing approved resources if available. If no local image-to-3D path is available without new large downloads, record a blocker and proceed with the next evidence-producing slice rather than overclaiming the asset chain.
