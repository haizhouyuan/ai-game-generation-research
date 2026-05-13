import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { BENCHMARK_INPUTS } from "../src/benchmarkInputs.js";
import { buildAssetInventory, generateAllScenes } from "../src/proceduralScenes.js";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const outputs = join(root, "outputs");
const generatedScenes = join(outputs, "generated_scenes");

async function writeJson(path, data) {
  await writeFile(path, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

const scenes = generateAllScenes();
await mkdir(generatedScenes, { recursive: true });
await writeJson(join(outputs, "benchmark_inputs.json"), BENCHMARK_INPUTS);
await writeJson(join(outputs, "procedural_asset_inventory.json"), buildAssetInventory(scenes));
for (const scene of scenes) {
  await writeJson(join(generatedScenes, `${scene.id.toLowerCase()}.json`), scene);
}

console.log(`wrote ${scenes.length} generated scene specs to ${generatedScenes}`);
