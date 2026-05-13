# AI-Assisted 3D Game Generation Pipeline Map

## Pipeline Stages

| Stage | Goal | Candidate Inputs | Candidate Outputs | First Evaluation Question |
|---|---|---|---|---|
| Concept | Turn a loose idea into a small scoped game concept. | Text prompt, reference image, child-safe theme constraints. | One-page concept, mechanics list, art direction. | Does it reduce scope to something buildable? |
| Visual Direction | Create style references and asset briefs. | Concept text, mood board, screenshots approved for use. | Character/environment/item briefs, style sheet. | Are assets consistent enough for one prototype? |
| 3D Asset Generation | Create mesh assets from image/text. | Text prompt, single image, multi-view images. | GLB/OBJ/FBX, textures, previews. | Can assets import into an engine without major repair? |
| Material And Texture | Improve or generate textures/materials. | Mesh UVs, prompt, image reference. | PBR textures, texture atlas, material settings. | Are textures usable under game lighting? |
| Rigging And Animation | Prepare characters or interactive objects. | Mesh, skeleton, animation prompt or clips. | Rigged model, animation clips. | Is the result stable enough for gameplay? |
| Scene Assembly | Place assets into a level. | Asset set, terrain prompt, layout sketch. | Engine scene, level file, navigation layout. | Can a player move through it? |
| Gameplay Logic | Add rules and interactions. | Mechanics spec, engine scripts, examples. | Godot/Unity/Unreal project scripts. | Is there a playable loop? |
| Packaging And Test | Build a runnable prototype. | Engine project. | Local build, browser build, or recorded walkthrough. | Can it be run and evaluated repeatedly? |

## First Prototype Bias

The first prototype should prefer Godot or a lightweight web/Three.js path because setup and artifact inspection are easier than full Unreal/Unity workflows. Unity and Unreal remain in research scope for import and higher-end asset pipelines.

