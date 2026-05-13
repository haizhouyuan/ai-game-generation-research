# P1 Child-Friendly Game Design Spec - 2026-05-12

## Purpose

P1 turns the original `14.html` / P0 game into a child-friendly playable slice while preserving the reason P0 felt exciting: a player can open the game, enter a 3D world, move immediately, receive constant feedback, collect rewards, improve their avatar, and finish a clear run.

P0's tactical shooting fantasy is intentionally not carried forward as the core theme. P1 keeps the technical vocabulary of 3D navigation, camera control, pickups, hazards, HUD feedback, upgrades, cosmetics, and fast restart, but replaces combat with exploration, collection, avoidance, and light puzzle hazards.

Working title: **Rover Workshop: Battery Rescue**

## Target Player

- Primary player: a child exploring game creation with a parent/operator nearby.
- Secondary user: the parent/operator evaluating whether AI tools can produce a safe, inspectable, repeatable game-development workflow.
- Intended session length: 3-7 minutes for one complete run.
- Skill level: beginner-friendly. The player should be able to move, collect, avoid hazards, and finish without needing shooter reflexes.
- Safety posture: no guns, no humanoid enemies, no realistic violence, no scary punishment loop. Failure states are soft resets, time penalties, or temporary stun/energy loss.

## Core Fantasy

The player controls a small friendly rover inside a colorful workshop maze after the lights go out. Three glowing batteries are scattered across the workshop. The rover explores rooms, avoids moving cleaning bots and sparking floor panels, solves simple switch/gate puzzles, upgrades its lamp beam or magnet range, and reaches a charging pad to restore the workshop.

## Core Loop

P1 loop:

`lobby -> enter workshop -> explore -> collect batteries -> avoid/solve hazards -> earn upgrade/cosmetic -> reach charging pad -> result screen -> replay`

Moment-to-moment loop:

1. Look around and identify the next glowing objective.
2. Move through a small 3D space with first/third-person camera support.
3. Collect a battery, gear token, or cosmetic shard.
4. Avoid a patrol bot, timed spark tile, moving platform, or blocked doorway.
5. Use a simple switch, pressure pad, or keycard to open a path.
6. Receive immediate feedback through soundless visual cues: glow, particles, HUD count, rover animation, score popups, and lighting changes.
7. Finish by reaching the charging pad after all required batteries are collected.

## Design Pillars

1. **Immediate Delight**
   - P1 must feel playable within seconds.
   - Start flow should be as direct as P0's lobby-to-game transition.
   - Every pickup and near miss should visibly respond.

2. **Safe Excitement**
   - Replace shooting tension with navigation tension.
   - Hazards should create urgency without implying harm: sparks drain energy, cleaning bots bump the rover backward, lasers are light beams that temporarily close doors.

3. **AI Asset Pipeline Showcase**
   - At least one hero prop should be an AI-generated GLB, validated through the asset pipeline.
   - Assets must have provenance and import evidence.

4. **Small Enough To Finish**
   - One compact level is better than a large unfinished world.
   - The demo should prove the full loop, not every imagined feature.

5. **Inspectable And Testable**
   - The scene must be representable as data.
   - A deterministic smoke test should prove loading, movement, interaction, collection, hazard response, and finish condition.

## P0 To P1 Feature Mapping

| P0 Feature | Why It Worked | P1 Replacement | Acceptance Note |
|---|---|---|---|
| Tactical compound | Recognizable 3D place with rooms, roofs, props, and traversal | Friendly workshop maze with rooms, shelves, ramps, workbenches, gates, and charging bay | Level has at least 3 named zones and visible navigation landmarks |
| First/third-person camera | Made the generated game feel modern and immersive | Keep first/third-person toggle if implementation cost stays low; otherwise ship third-person first | Camera must not clip through major walls in normal play |
| Aim/shoot/action feedback | Constant visual feedback made actions feel responsive | Collection beam, magnet pulse, switch activation, scan ping, light cone, particle burst | Every primary interaction has an immediate visual response |
| NPC enemies | Created moving pressure and goals | Cleaning bots, rolling carts, spark tiles, timed gates, friendly drones | Hazards are nonviolent and readable |
| Damage/health | Added stakes | Rover energy meter, soft stun, battery drain, checkpoint reset | No violent framing; failure explains how to retry |
| Weapons and ammo | Created progression and resource management | Tools: magnet range, lamp brightness, repair pulse cooldown | At least one upgrade changes play meaningfully |
| Loot and gear | Rewarded exploration | Batteries, gear tokens, blueprint cards, cosmetic decals | Required and optional pickups are visually distinct |
| Kill count and coin reward | Short-term achievement loop | Battery count, workshop power restored percentage, sparkle score, rescue badges | HUD shows progress toward finish |
| Skin lottery/localStorage | Cosmetic persistence delighted the player | Rover decals, antenna toppers, wheel colors unlocked by tokens | Optional; if included, store only local cosmetic unlocks |
| NPC strength/spawn/loot settings | Let the player customize difficulty | Assist mode, hazard speed, pickup count, camera mode, graphics quality | Settings should be parent-friendly and simple |
| Muzzle flash/tracers/casings | High feedback density | Glow trails, pickup particles, switch beams, gate lights, wheel dust | Preserve feedback density without weapon imagery |
| Single-file HTML immediacy | Easy to open and share | Keep demo easy to run, but structure code/assets for testing | Demo starts by file open or one local server command |

## Level Structure

### Level 1: Workshop Maze

Goal: collect 3 batteries and reach the charging pad.

Zones:

1. **Entry Bay**
   - Safe start area.
   - Teaches movement, camera, and first pickup.
   - Contains one visible battery and one cosmetic shard.

2. **Tool Shelf Corridor**
   - Narrow path with moving cleaning bot.
   - Teaches avoidance and timing.
   - Contains one switch that opens the central gate.

3. **Spark Floor Room**
   - Timed spark tiles cycle on and off.
   - Teaches waiting, path reading, and risk/reward.
   - Contains one battery behind a short timing challenge.

4. **Puzzle Bench**
   - Two pressure pads or color switches.
   - Teaches simple puzzle sequencing.
   - Unlocks the upgrade station or final battery.

5. **Charging Bay**
   - Finish pad activates only after all required batteries are collected.
   - End screen shows time, batteries, optional pickups, and unlocked cosmetic.

Progression:

- Required: 3 batteries.
- Optional: 5 gear tokens.
- Upgrade: collect 3 gear tokens to unlock magnet range or brighter lamp.
- Cosmetic: collect 5 gear tokens to unlock one rover decal.

Difficulty:

- Default hazards should be slow and readable.
- Assist mode can reduce hazard speed and increase pickup glow radius.
- No fail-hard death loop. Energy reaching zero returns the rover to the last checkpoint with a clear visual explanation.

## Asset List

### Hero Assets

| Asset | Role | Preferred Source | Minimum Acceptance |
|---|---|---|---|
| Friendly rover | Player avatar | AI concept image -> 3D generation candidate -> GLB cleanup | GLB imports into Three.js, has bounding box, readable silhouette |
| Glowing battery | Required collectible | Procedural or AI-generated GLB | Bright material, pickup animation, unique icon |
| Cleaning bot | Moving hazard | Procedural first; AI GLB later | Non-threatening shape, clear patrol path |
| Charging pad | Finish object | Procedural or AI GLB | Activates visually after batteries complete |
| Upgrade station | Progression object | Procedural or AI GLB | Clear before/after upgrade state |

### Environment Assets

| Asset | Role | Preferred Source | Minimum Acceptance |
|---|---|---|---|
| Workshop floor/walls | Level structure | Procedural blockout first | Collision proxies match visible layout |
| Shelves and workbenches | Landmarks and occlusion | Procedural or generated GLB props | Do not block critical path unless intentional |
| Ramps | Traversal | Procedural | Smooth player movement, no snagging |
| Gates/doors | Puzzle feedback | Procedural | Open/closed state visible from distance |
| Spark tiles | Timed hazard | Procedural material/animation | On/off state visually obvious |
| Signs/arrows | Player guidance | Texture/UI generated | No text required for core navigation |

### UI And Feedback Assets

- Battery counter icon.
- Energy meter.
- Gear token icon.
- Upgrade/cosmetic unlock panel.
- Finish result badges.
- Pickup glow particles.
- Hazard warning ring.
- Charging-pad activation beam.

### Provenance Requirements

Every non-procedural asset must record:

- source prompt or reference image path;
- generator/tool used;
- generation date;
- source file path;
- exported GLB path;
- SHA256 hash;
- import/readback result;
- known limitations, such as mesh-only, no textures, no rig, or collider-proxy-only.

## Scene Schema Sketch

The P1 scene should be expressible as data so agents can generate, validate, and revise it without hand-editing the whole game.

```json
{
  "schema_version": "game_scene_p1_v0",
  "scene_id": "workshop_battery_rescue_01",
  "metadata": {
    "title": "Rover Workshop: Battery Rescue",
    "target_player": "child-with-parent",
    "theme": "friendly workshop exploration"
  },
  "player": {
    "spawn": [0, 0.5, 0],
    "avatar_asset": "assets/rover/rover.glb",
    "camera_modes": ["third_person", "first_person_optional"],
    "energy": 100,
    "abilities": {
      "magnet_range": 2.5,
      "lamp_radius": 8.0
    }
  },
  "objectives": {
    "required_collectibles": {
      "type": "battery",
      "count": 3
    },
    "finish_pad": "finish_charging_pad"
  },
  "zones": [
    {
      "id": "entry_bay",
      "bounds": [-6, 0, -6, 6, 4, 4],
      "teaches": ["movement", "pickup"]
    },
    {
      "id": "tool_shelf_corridor",
      "bounds": [6, 0, -4, 16, 4, 4],
      "teaches": ["avoidance", "switch"]
    },
    {
      "id": "spark_floor_room",
      "bounds": [16, 0, -6, 28, 4, 6],
      "teaches": ["timing", "hazard_reading"]
    }
  ],
  "entities": [
    {
      "id": "battery_01",
      "type": "collectible",
      "kind": "battery",
      "position": [2, 0.7, -2],
      "required": true,
      "feedback": ["glow", "pickup_particles", "hud_increment"]
    },
    {
      "id": "cleaning_bot_01",
      "type": "hazard_patrol",
      "kind": "soft_bumper",
      "path": [[8, 0.4, -2], [14, 0.4, -2]],
      "speed": 1.2,
      "on_contact": {
        "energy_delta": -10,
        "knockback": 1.5
      }
    },
    {
      "id": "switch_01",
      "type": "puzzle_switch",
      "position": [12, 0.5, 3],
      "opens": "gate_01",
      "feedback": ["beam_to_gate", "soundless_light_pulse"]
    },
    {
      "id": "finish_charging_pad",
      "type": "finish_pad",
      "position": [30, 0.2, 0],
      "requires": {
        "battery": 3
      }
    }
  ],
  "settings": {
    "assist_mode": false,
    "hazard_speed_multiplier": 1.0,
    "graphics_quality": "medium"
  }
}
```

## Gameplay Requirements

Minimum P1 playable slice:

- Lobby or start overlay with title and start button.
- Controllable rover/player.
- Third-person camera with stable follow behavior.
- First-person camera toggle is desirable but not required for P1 release.
- One compact 3D workshop level.
- 3 required batteries.
- 5 optional gear tokens.
- At least one moving hazard.
- At least one timed hazard or puzzle gate.
- At least one switch, pressure pad, or keycard interaction.
- One upgrade or cosmetic unlock.
- One finish pad and result screen.
- HUD for energy, batteries, optional tokens, and objective prompt.
- Immediate visual feedback for pickup, hazard contact, switch activation, upgrade unlock, and finish.

## Engine Direction

P1 should ship first as a modular Three.js demo because it is the fastest path from the P0 HTML baseline to a better inspectable prototype. The implementation should avoid another monolithic one-off file if possible.

Recommended structure:

- `index.html`: minimal host page.
- `src/game.js`: game bootstrap and main loop.
- `src/input.js`: keyboard/pointer input.
- `src/player.js`: rover movement and camera anchor.
- `src/scene_schema.js`: scene data loading and validation.
- `src/entities.js`: collectibles, hazards, switches, finish pad.
- `src/hud.js`: UI state.
- `src/assets.js`: GLB loading and provenance references.
- `tests/`: smoke/playthrough checks.

Unity remains a strategic target once Unity Editor/MCP is available, but P1 should not wait on Unity.

## Acceptance Tests

### Design Acceptance

- The P1 concept preserves P0's fast start, movement, feedback, pickups, progression, cosmetics, and clear run completion.
- Tactical shooting, realistic weapons, kill counts, and humanoid combat are not core mechanics.
- The full level can be explained in one paragraph and completed in under 7 minutes.
- The loop has at least one required objective, one optional reward, one hazard, one puzzle interaction, and one finish condition.

### Asset Acceptance

- At least one AI-generated GLB is present in the demo or release packet.
- Every generated GLB has source prompt/reference, generator/tool, SHA256, preview, and readback/import evidence.
- Collision uses explicit simple proxies; generated meshes are not assumed to be production collision.
- If textures/materials are generated, the release packet includes texture paths, material assignment notes, and a screenshot under game lighting.
- Mesh-only assets are labeled honestly as mesh-only or visual-proxy assets.

### Playable Acceptance

- The demo loads locally without relying on a hidden hosted service.
- The canvas is nonblank after load.
- Start flow enters gameplay.
- Movement input changes player position.
- Camera follows the player without disorienting jumps during normal movement.
- Collecting a battery increments the HUD.
- Optional gear tokens increment separately from required batteries.
- Hazard contact visibly affects energy or player state.
- Switch or puzzle interaction changes world state.
- Finish pad does not complete before required batteries are collected.
- Finish pad completes the run after required batteries are collected.
- Result screen shows completion state.

### Evidence Acceptance

The release packet must include:

- playable path or local command;
- source paths;
- asset manifest;
- SHA256 hashes for key generated artifacts;
- at least one screenshot from lobby/start;
- at least one screenshot from in-game play;
- automated smoke-test log;
- known limitations;
- provenance notes for generated assets.

## Release-Demo Criteria

P1 is releasable when a parent/operator can run the demo and observe all of the following in one short session:

1. The game starts cleanly from a local path or one local server command.
2. The player understands the goal without reading external documentation.
3. The rover can move through a compact 3D workshop.
4. The player collects 3 batteries.
5. The player encounters at least one nonviolent hazard.
6. The player solves or activates at least one simple world interaction.
7. The player reaches a final charging pad and sees a result screen.
8. The game shows visibly better asset quality than P0 in at least one area: rover, collectible, environment prop, material, or lighting.
9. The demo has an evidence packet proving load, movement, interaction, finish, and asset provenance.
10. The tactical shooting theme has been fully replaced by exploration, collection, avoidance, and puzzle play.

## Out Of Scope For P1

- Multiplayer.
- Realistic combat.
- Online accounts or hosted leaderboards.
- Large open world.
- Complex dialogue.
- Rigged character animation beyond simple rover movement.
- Production-grade physics.
- Full Unity port.
- Full procedural content-generation editor.

## Open Questions For Later Phases

- Should P2 promote the Three.js prototype into Unity once Unity MCP is working?
- Should the primary avatar be a rover, robot, or creature-like helper after visual concept testing?
- Which asset-generation path gives the best quality-to-control ratio for small child-friendly props: OpenAI image references plus TRELLIS, TripoSR, Hunyuan3D, Blender cleanup, or a hybrid?
- Should the game become a creation tool where the child can edit the workshop layout, or stay a game demo first?
- Which automated test should become the cross-engine standard: browser Playwright, Three.js parser/pixel checks, Godot scene CI, or Unity play-mode tests?

