import fs from 'node:fs/promises';
import path from 'node:path';
import * as THREE from '../../game_p2_glb_three_import_loop/node_modules/three/build/three.module.js';
import { GLTFLoader } from '../../game_p2_glb_three_import_loop/node_modules/three/examples/jsm/loaders/GLTFLoader.js';

globalThis.ProgressEvent = class ProgressEvent extends Event {
  constructor(type, init = {}) {
    super(type);
    this.lengthComputable = init.lengthComputable ?? false;
    this.loaded = init.loaded ?? 0;
    this.total = init.total ?? 0;
  }
};

globalThis.self ??= globalThis;
globalThis.createImageBitmap ??= async () => ({ width: 1, height: 1, close() {} });

class LocalResponse {
  constructor(buffer) {
    this._buffer = buffer;
    this.status = 200;
    this.statusText = 'OK';
    this.ok = true;
  }

  async arrayBuffer() {
    return this._buffer.buffer.slice(this._buffer.byteOffset, this._buffer.byteOffset + this._buffer.byteLength);
  }

  async json() {
    return JSON.parse(this._buffer.toString('utf8'));
  }
}

globalThis.fetch = async (url) => {
  const localPath = url instanceof URL ? url.pathname : String(url);
  const resolved = path.isAbsolute(localPath) ? localPath : path.resolve(localPath);
  return new LocalResponse(await fs.readFile(resolved));
};

const loader = new GLTFLoader();
const root = path.resolve(process.argv[2] || 'outputs/assets');
const outPath = path.resolve(process.argv[3] || 'outputs/asset_parse_inventory.json');
const files = (await fs.readdir(root)).filter((name) => name.endsWith('.glb')).sort();
const rows = [];

function parseGlbJson(buffer) {
  if (buffer.readUInt32LE(0) !== 0x46546c67) {
    return null;
  }
  let offset = 12;
  while (offset + 8 <= buffer.length) {
    const chunkLength = buffer.readUInt32LE(offset);
    const chunkType = buffer.readUInt32LE(offset + 4);
    offset += 8;
    if (chunkType === 0x4e4f534a) {
      return JSON.parse(buffer.subarray(offset, offset + chunkLength).toString('utf8'));
    }
    offset += chunkLength;
  }
  return null;
}

for (const name of files) {
  const filePath = path.join(root, name);
  const buffer = await fs.readFile(filePath);
  const glbJson = parseGlbJson(buffer);
  const gltf = await loader.parseAsync(buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength), path.dirname(filePath) + '/');
  const box = new THREE.Box3().setFromObject(gltf.scene);
  const size = new THREE.Vector3();
  box.getSize(size);
  let meshes = 0;
  let triangles = 0;
  let uvAttributeMeshes = 0;
  let materialMapCount = 0;
  const materialNames = new Set();
  gltf.scene.traverse((node) => {
    if (node.isMesh) {
      meshes += 1;
      const indexCount = node.geometry?.index?.count;
      const positionCount = node.geometry?.attributes?.position?.count;
      triangles += indexCount ? indexCount / 3 : (positionCount || 0) / 3;
      if (node.geometry?.attributes?.uv?.count) {
        uvAttributeMeshes += 1;
      }
      const materials = Array.isArray(node.material) ? node.material : [node.material];
      for (const material of materials.filter(Boolean)) {
        materialNames.add(material.name || '(unnamed)');
        if (material.map) {
          materialMapCount += 1;
        }
      }
    }
  });
  rows.push({
    file: filePath,
    bytes: buffer.length,
    scenes: gltf.scenes.length,
    meshes,
    triangles,
    uvAttributeMeshes,
    materialNames: [...materialNames].sort(),
    materialMapCount,
    gltfJsonTextures: glbJson?.textures?.length || 0,
    gltfJsonImages: glbJson?.images?.length || 0,
    gltfJsonEmbeddedImages: (glbJson?.images || []).filter((image) => image.bufferView !== undefined).length,
    gltfJsonBaseColorTextureMaterials: (glbJson?.materials || []).filter(
      (material) => material.pbrMetallicRoughness?.baseColorTexture !== undefined
    ).length,
    bbox: {
      min: [box.min.x, box.min.y, box.min.z],
      max: [box.max.x, box.max.y, box.max.z],
      size: [size.x, size.y, size.z]
    }
  });
}

await fs.writeFile(outPath, JSON.stringify(rows, null, 2));
console.log(JSON.stringify(rows, null, 2));
