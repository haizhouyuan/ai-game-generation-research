import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

import { gateSummaryForEntry, texturePathsFromEntry } from "./assetRegistry.js";

const MATERIAL_MAP_SLOTS = ["map", "normalMap", "roughnessMap", "metalnessMap", "aoMap", "emissiveMap"];

export class TacticalAssetLoader {
  constructor({
    registry,
    loadingManager = undefined,
    renderer = undefined,
    ktx2Loader = undefined,
    meshoptDecoder = undefined,
    dracoLoader = undefined,
    baseUrl = "",
    evidenceMode = false,
    failOnFallback = true,
    logger = console
  } = {}) {
    this.registry = registry;
    this.baseUrl = baseUrl;
    this.evidenceMode = evidenceMode;
    this.failOnFallback = failOnFallback;
    this.logger = logger;
    this.statusById = new Map();
    this.loader = new GLTFLoader(loadingManager);

    if (ktx2Loader) {
      if (renderer && typeof ktx2Loader.detectSupport === "function") {
        ktx2Loader.detectSupport(renderer);
      }
      this.loader.setKTX2Loader(ktx2Loader);
    }
    if (meshoptDecoder) this.loader.setMeshoptDecoder(meshoptDecoder);
    if (dracoLoader) this.loader.setDRACOLoader(dracoLoader);
  }

  getEntry(assetId) {
    if (this.registry?.get) return this.registry.get(assetId);
    if (this.registry?.byId instanceof Map) return this.registry.byId.get(assetId) || null;
    return (this.registry?.assets || []).find((entry) => entry.asset_id === assetId) || null;
  }

  getStatus(assetId) {
    return this.statusById.get(assetId) || {
      assetId,
      state: "idle",
      fallbackUsed: false,
      fallbackForbidden: false,
      error: null,
      materialMapCount: 0,
      declaredTextureCount: 0,
      missingTextureDeclarations: []
    };
  }

  setStatus(assetId, patch) {
    const next = { ...this.getStatus(assetId), ...patch };
    this.statusById.set(assetId, next);
    return next;
  }

  resolveUrl(path) {
    if (!path) return path;
    if (/^(https?:)?\/\//.test(path) || path.startsWith("data:") || path.startsWith("blob:")) return path;
    return `${this.baseUrl}${path}`;
  }

  async loadAsset(assetId) {
    const entry = this.getEntry(assetId);
    if (!entry) {
      throw new Error(`Unknown asset id: ${assetId}`);
    }

    const declaredTextures = texturePathsFromEntry(entry);
    this.setStatus(assetId, {
      state: "loading",
      error: null,
      declaredTextureCount: declaredTextures.length,
      fallbackForbidden: entry?.quality_gates?.fallback_allowed_in_evidence === false
    });

    try {
      const gltf = await this.loader.loadAsync(this.resolveUrl(entry.paths.model));
      const materialReport = collectMaterialReport(gltf.scene);
      const status = this.setStatus(assetId, {
        state: "loaded",
        gltf,
        scene: gltf.scene,
        materialMapCount: materialReport.materialMapCount,
        materialReport,
        declaredTextureCount: declaredTextures.length,
        gateSummary: gateSummaryForEntry(entry)
      });
      return { entry, gltf, status };
    } catch (error) {
      this.setStatus(assetId, {
        state: "error",
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  createFallback(assetId, factory) {
    const entry = this.getEntry(assetId);
    const fallbackForbidden = this.evidenceMode
      && this.failOnFallback
      && entry?.quality_gates?.fallback_allowed_in_evidence === false;

    if (fallbackForbidden) {
      const message = `Fallback forbidden in evidence mode for ${assetId}`;
      this.setStatus(assetId, { state: "fallback_forbidden", fallbackUsed: true, fallbackForbidden: true, error: message });
      throw new Error(message);
    }

    const fallback = typeof factory === "function" ? factory(entry) : null;
    this.setStatus(assetId, { state: "fallback", fallbackUsed: true, fallbackForbidden: false });
    this.logger.warn?.(`[asset-loader] fallback used for ${assetId}`);
    return fallback;
  }

  getEvidenceSnapshot() {
    return Object.fromEntries(
      Array.from(this.statusById.entries()).map(([assetId, status]) => [
        assetId,
        {
          state: status.state,
          fallbackUsed: Boolean(status.fallbackUsed),
          fallbackForbidden: Boolean(status.fallbackForbidden),
          error: status.error,
          materialMapCount: status.materialMapCount,
          declaredTextureCount: status.declaredTextureCount,
          gateSummary: status.gateSummary || null
        }
      ])
    );
  }
}

export function collectMaterialReport(root) {
  const materials = new Map();
  let materialMapCount = 0;
  let meshCount = 0;

  root?.traverse?.((node) => {
    if (!node.isMesh) return;
    meshCount += 1;
    const materialList = Array.isArray(node.material) ? node.material : [node.material].filter(Boolean);
    for (const material of materialList) {
      const key = material.uuid || material.name || `material_${materials.size}`;
      if (!materials.has(key)) {
        const mapSlots = MATERIAL_MAP_SLOTS.filter((slot) => Boolean(material[slot]));
        materialMapCount += mapSlots.length;
        materials.set(key, {
          name: material.name || key,
          type: material.type || "Material",
          mapSlots,
          metalness: typeof material.metalness === "number" ? material.metalness : null,
          roughness: typeof material.roughness === "number" ? material.roughness : null
        });
      }
    }
  });

  return {
    meshCount,
    materialCount: materials.size,
    materialMapCount,
    materials: Array.from(materials.values())
  };
}

export function createTacticalAssetLoader(options) {
  return new TacticalAssetLoader(options);
}
