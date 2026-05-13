export const VISUAL_UPGRADE_REGISTRY_URL = "assets/asset_registry_v2.json";

export const FIXED_EVIDENCE_CAMERAS = [
  "01_fp_rifle_wet_checkpoint",
  "02_third_person_player_gear",
  "03_enemy_under_checkpoint_light",
  "04_loot_on_wet_asphalt",
  "05_indoor_killhouse_corridor",
  "06_final_wide_rainy_container_checkpoint"
];

export const REQUIRED_WEAPON_ANCHORS = ["Muzzle", "Grip_R", "Grip_L", "Optic", "PickupRoot"];
export const REQUIRED_CHARACTER_ANCHORS = ["Weapon_R", "Head", "Spine", "Foot_L", "Foot_R"];

export const LEGACY_BASELINE_ASSETS = {
  weapons: {
    pistol: "experiments/tactical_game_full_realism_final_20260513/assets/models/pistol_m5_candidate.glb",
    shotgun: "experiments/tactical_game_full_realism_final_20260513/assets/models/shotgun_m5_candidate.glb",
    rifle: "experiments/tactical_game_full_realism_final_20260513/assets/models/groza_procedural_candidate.glb",
    dmr: "experiments/tactical_game_full_realism_final_20260513/assets/models/dmr_m5_candidate.glb"
  },
  characters: {
    player: "experiments/tactical_game_full_realism_final_20260513/assets/models/character_player_final.glb",
    enemy: "experiments/tactical_game_full_realism_final_20260513/assets/models/character_enemy_final.glb"
  }
};

export function texturePathsFromEntry(entry) {
  const textures = entry?.paths?.textures || {};
  return Object.entries(textures)
    .filter(([, value]) => typeof value === "string" && value.length > 0)
    .map(([slot, path]) => ({ slot, path }));
}

export function materialMapCountFromEntry(entry) {
  const declared = entry?.materials?.material_map_count;
  if (Number.isInteger(declared)) return declared;
  return texturePathsFromEntry(entry).length;
}

export function normalizeAssetEntry(entry) {
  return {
    ...entry,
    materialMapCount: materialMapCountFromEntry(entry),
    texturePaths: texturePathsFromEntry(entry),
    fallbackAllowed: Boolean(entry?.quality_gates?.fallback_allowed_in_evidence),
    blockers: Array.isArray(entry?.blockers) ? entry.blockers : []
  };
}

export function createRegistryIndex(registry) {
  const assets = Array.isArray(registry?.assets) ? registry.assets.map(normalizeAssetEntry) : [];
  const byId = new Map();
  const byClass = new Map();

  for (const asset of assets) {
    byId.set(asset.asset_id, asset);
    if (!byClass.has(asset.asset_class)) byClass.set(asset.asset_class, []);
    byClass.get(asset.asset_class).push(asset);
  }

  return {
    schemaVersion: registry?.schema_version || null,
    experiment: registry?.experiment || null,
    assets,
    byId,
    byClass,
    get(id) {
      return byId.get(id) || null;
    },
    listByClass(assetClass) {
      return byClass.get(assetClass) || [];
    }
  };
}

export async function fetchAssetRegistryV2({
  url = VISUAL_UPGRADE_REGISTRY_URL,
  fetchImpl = globalThis.fetch
} = {}) {
  if (typeof fetchImpl !== "function") {
    throw new Error("fetchAssetRegistryV2 requires a fetch implementation");
  }

  const response = await fetchImpl(url);
  if (!response.ok) {
    throw new Error(`Asset registry fetch failed: ${response.status} ${response.statusText}`);
  }
  const registry = await response.json();
  return createRegistryIndex(registry);
}

export function missingRequiredAnchors(entry) {
  const required = entry?.asset_class === "weapon"
    ? REQUIRED_WEAPON_ANCHORS
    : entry?.asset_class === "character"
      ? REQUIRED_CHARACTER_ANCHORS
      : [];
  const defined = new Set(entry?.anchors?.defined || []);
  return required.filter((anchor) => !defined.has(anchor));
}

export function gateSummaryForEntry(entry) {
  const materialMapCount = materialMapCountFromEntry(entry);
  const missingAnchors = missingRequiredAnchors(entry);
  const productionReady = entry?.status === "production_ready";
  const fallbackForbidden = entry?.quality_gates?.fallback_allowed_in_evidence === false;

  return {
    assetId: entry?.asset_id || null,
    status: entry?.status || null,
    assetClass: entry?.asset_class || null,
    productionReady,
    materialMapCount,
    hasFourPbrMaps: materialMapCount >= 4,
    missingAnchors,
    fallbackForbidden,
    blockers: Array.isArray(entry?.blockers) ? entry.blockers.map((blocker) => blocker.gate) : []
  };
}
