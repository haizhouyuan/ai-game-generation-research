import { BENCHMARK_INPUTS } from "./benchmarkInputs.js";

const COMMON_ASSET_TYPES = [
  "isometric_prism_tile",
  "procedural_player_proxy",
  "procedural_pickup",
  "moving_hazard",
  "finish_pad",
  "collision_block",
  "decorative_prop"
];

function block(id, x, y, w, h, d, color, solid = true) {
  return { id, type: "block", x, y, w, h, z: 0, d, color, solid };
}

function pickup(id, kind, x, y, color) {
  return { id, type: "pickup", kind, x, y, z: 0.34, radius: 0.42, color, collected: false };
}

function prop(id, kind, x, y, w, h, d, color) {
  return { id, type: "prop", kind, x, y, w, h, z: 0.02, d, color, solid: false };
}

function hazard(id, x, y, travel, speed, color) {
  return {
    id,
    type: "hazard",
    x,
    y,
    baseX: x,
    baseY: y,
    travel,
    speed,
    radius: 0.44,
    color
  };
}

function finish(id, x, y, w, h, color, label) {
  return { id, type: "finish", x, y, w, h, z: 0.04, d: 0.08, color, label };
}

export function generateScene(input) {
  if (input.id === "GAME-B2") return islandScene(input);
  if (input.id === "GAME-B3") return hangarScene(input);
  return workshopScene(input);
}

export function generateAllScenes() {
  return BENCHMARK_INPUTS.map((input) => generateScene(input));
}

export function buildAssetInventory(scenes = generateAllScenes()) {
  const counts = {};
  const generatedAssets = [];
  for (const scene of scenes) {
    for (const entity of scene.entities) {
      const key = entity.type === "player" ? "procedural_player_proxy" : entity.type;
      counts[key] = (counts[key] || 0) + 1;
      generatedAssets.push({
        sceneId: scene.id,
        entityId: entity.id,
        type: entity.type,
        kind: entity.kind || entity.type,
        generatedBy: "src/proceduralScenes.js"
      });
    }
  }
  return {
    method: "deterministic procedural scene generation; no external asset downloads",
    assetTypes: COMMON_ASSET_TYPES,
    counts,
    generatedAssets
  };
}

function baseScene(input, bounds) {
  return {
    id: input.id,
    title: input.title,
    prompt: input.prompt,
    playerKind: input.playerKind,
    pickupKind: input.pickupKind,
    finishLabel: input.finishLabel,
    targetCount: input.targetCount,
    theme: input.theme,
    bounds,
    start: { x: 0.65, y: 0.65 },
    entities: [
      {
        id: "player",
        type: "player",
        kind: input.playerKind,
        x: 0.65,
        y: 0.65,
        radius: 0.34,
        color: input.theme.player
      }
    ]
  };
}

function workshopScene(input) {
  const scene = baseScene(input, { w: 8.8, h: 5.2 });
  scene.entities.push(
    block("floor", 4.4, 2.6, 8.8, 5.2, 0.16, input.theme.floor, false),
    block("bench-west", 2.1, 1.55, 0.65, 2.2, 0.42, "#56676e"),
    block("bench-east", 5.0, 3.45, 2.1, 0.56, 0.35, "#63755f"),
    block("crate-stack", 6.75, 1.2, 1.1, 0.9, 0.58, "#735944"),
    block("tool-rack", 3.75, 0.42, 1.5, 0.42, 0.46, "#65737a"),
    prop("wire-a", "cable", 1.2, 4.4, 0.9, 0.2, 0.06, "#202629"),
    prop("wire-b", "cable", 7.5, 3.0, 0.7, 0.2, 0.06, "#202629"),
    pickup("battery-1", input.pickupKind, 1.45, 0.85, input.theme.pickup),
    pickup("battery-2", input.pickupKind, 3.45, 2.25, input.theme.pickup),
    pickup("battery-3", input.pickupKind, 6.15, 0.62, input.theme.pickup),
    pickup("battery-4", input.pickupKind, 7.55, 4.42, input.theme.pickup),
    hazard("saw-arm", 4.55, 1.75, { axis: "x", amount: 1.45 }, 1.35, input.theme.hazard),
    finish("charge-dock", 8.0, 4.55, 0.9, 0.58, input.theme.finish, input.finishLabel)
  );
  return scene;
}

function islandScene(input) {
  const scene = baseScene(input, { w: 9.2, h: 5.6 });
  scene.entities.push(
    block("island-main", 4.6, 2.8, 9.2, 5.6, 0.18, input.theme.floor, false),
    block("platform-1", 2.2, 1.25, 1.7, 1.05, 0.35, "#77b96d", false),
    block("platform-2", 4.95, 2.65, 1.8, 1.1, 0.45, "#6cab70", false),
    block("platform-3", 7.2, 4.0, 1.65, 0.95, 0.55, "#88bd73", false),
    block("palm-rock", 3.55, 4.55, 0.8, 0.62, 0.42, "#7d8170"),
    prop("shore-left", "sandbar", 0.7, 2.9, 0.8, 3.8, 0.04, input.theme.floorTrim),
    prop("shore-right", "sandbar", 8.55, 2.7, 0.7, 3.4, 0.04, input.theme.floorTrim),
    pickup("coin-1", input.pickupKind, 1.85, 1.25, input.theme.pickup),
    pickup("coin-2", input.pickupKind, 3.8, 1.95, input.theme.pickup),
    pickup("coin-3", input.pickupKind, 4.95, 2.65, input.theme.pickup),
    pickup("coin-4", input.pickupKind, 6.35, 3.45, input.theme.pickup),
    pickup("coin-5", input.pickupKind, 7.25, 4.0, input.theme.pickup),
    hazard("rolling-log", 5.1, 1.1, { axis: "y", amount: 1.7 }, 1.1, input.theme.hazard),
    finish("signal-flag", 8.1, 4.75, 0.72, 0.62, input.theme.finish, input.finishLabel)
  );
  return scene;
}

function hangarScene(input) {
  const scene = baseScene(input, { w: 8.4, h: 4.9 });
  scene.entities.push(
    block("hangar-deck", 4.2, 2.45, 8.4, 4.9, 0.15, input.theme.floor, false),
    block("cargo-left", 2.1, 3.55, 1.0, 0.82, 0.52, "#545b78"),
    block("cargo-right", 6.75, 1.0, 0.95, 0.82, 0.52, "#5a637f"),
    block("engine-rack", 4.0, 0.48, 1.65, 0.46, 0.46, "#68708a"),
    prop("light-strip-a", "light", 1.55, 0.35, 0.9, 0.18, 0.05, input.theme.accent),
    prop("light-strip-b", "light", 5.5, 4.45, 1.1, 0.18, 0.05, input.theme.accent),
    pickup("fusion-core", input.pickupKind, 4.35, 2.55, input.theme.pickup),
    hazard("security-drone", 3.2, 1.55, { axis: "x", amount: 2.0 }, 0.9, input.theme.hazard),
    finish("launch-pad", 7.55, 4.15, 0.95, 0.72, input.theme.finish, input.finishLabel)
  );
  return scene;
}
