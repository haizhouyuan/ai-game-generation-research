import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const inventoryPath = path.join(root, 'outputs', 'glb_asset_inventory.json');
const inventory = JSON.parse(fs.readFileSync(inventoryPath, 'utf8'));

function localAssetPath(assetFile) {
  if (fs.existsSync(assetFile)) return assetFile;
  return path.join(root, 'outputs', 'assets', path.basename(assetFile));
}

const failures = [];
for (const asset of inventory.assets || []) {
  const resolved = localAssetPath(asset.file);
  if (!fs.existsSync(resolved)) failures.push(`missing ${resolved}`);
  const size = fs.existsSync(resolved) ? fs.statSync(resolved).size : 0;
  if (size <= 0) failures.push(`empty ${resolved}`);
  if (asset.geometry_count <= 0) failures.push(`no geometry ${resolved}`);
}

if ((inventory.assets || []).length !== 3) failures.push(`expected 3 GLB assets, got ${(inventory.assets || []).length}`);

console.log(JSON.stringify({
  assetCount: (inventory.assets || []).length,
  assets: (inventory.assets || []).map((asset) => ({
    file: localAssetPath(asset.file),
    bytes: fs.existsSync(localAssetPath(asset.file)) ? fs.statSync(localAssetPath(asset.file)).size : 0,
    geometry_count: asset.geometry_count
  })),
  failures
}, null, 2));

if (failures.length) process.exit(2);
