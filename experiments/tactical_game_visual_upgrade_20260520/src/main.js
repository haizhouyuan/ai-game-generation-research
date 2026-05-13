import * as THREE from "three";

import { EVIDENCE_ANIMATION_STATES, createAnimatedTacticalCharacter } from "./runtime/animationSystem.js";
import { createTacticalAssetLoader } from "./runtime/assetLoader.js";
import { fetchAssetRegistryV2 } from "./runtime/assetRegistry.js";
import { configureRainyCheckpointLighting } from "./runtime/lightingSystem.js";
import { createRainSystem } from "./runtime/weatherSystem.js";
import { EVIDENCE_CAMERAS, createRainyCheckpointLayout } from "./scene/rainyCheckpointLayout.js";

const params = new URLSearchParams(window.location.search);
const requestedEvidence = params.get("evidence") || "06_final_wide_rainy_container_checkpoint";
const evidenceMode = params.has("evidence");
if (evidenceMode) document.body.classList.add("evidence");

const statusEl = document.querySelector("#status");
const selectEl = document.querySelector("#cameraSelect");
for (const id of Object.keys(EVIDENCE_CAMERAS)) {
  const option = document.createElement("option");
  option.value = id;
  option.textContent = id;
  selectEl.appendChild(option);
}
selectEl.value = EVIDENCE_CAMERAS[requestedEvidence] ? requestedEvidence : "06_final_wide_rainy_container_checkpoint";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.05, 120);
const cameraFill = new THREE.PointLight(0xcde8ff, 4.2, 7.5, 1.35);
cameraFill.name = "camera_tactical_fill_light";
camera.add(cameraFill);
scene.add(camera);
const clock = new THREE.Clock();
configureRainyCheckpointLighting(THREE, scene, renderer);
const layout = createRainyCheckpointLayout(THREE, scene);
const rain = createRainSystem(THREE, scene);
const animatedCharacters = {
  player: createAnimatedTacticalCharacter(THREE, {
    id: "player_tactical_v2_proxy",
    color: 0x465d4f,
    accent: 0x1a242c,
    teamLight: 0x7dd3fc
  }),
  enemy: createAnimatedTacticalCharacter(THREE, {
    id: "enemy_tactical_v2_proxy",
    color: 0x5d4b45,
    accent: 0x24191b,
    teamLight: 0xff4055
  })
};
animatedCharacters.player.root.position.set(-0.55, 0.02, 0.58);
animatedCharacters.player.root.rotation.y = -0.52;
animatedCharacters.enemy.root.position.set(2.35, 0.02, -1.72);
animatedCharacters.enemy.root.rotation.y = -0.72;
scene.add(animatedCharacters.player.root, animatedCharacters.enemy.root);

window.__TACTICAL_VISUAL_UPGRADE__ = {
  loaded: false,
  evidence: selectEl.value,
  blockingEvents: [],
  assetStatus: {},
  scene: {
    target: "rainy_checkpoint_container_yard_killhouse_entry",
    clutterOrDecalInstances: layout.clutterCount,
    evidenceCameras: Object.keys(EVIDENCE_CAMERAS)
  },
  animation: {
    player: animatedCharacters.player.getStatus(),
    enemy: animatedCharacters.enemy.getStatus(),
    requiredForEvidence: EVIDENCE_ANIMATION_STATES[selectEl.value]
  }
};

function setStatus(message) {
  statusEl.textContent = message;
}

function repoUrl(path) {
  if (/^(https?:)?\/\//.test(path)) return path;
  if (path.startsWith("../")) return path;
  return `../../${path}`;
}

function frameCamera(id) {
  const preset = EVIDENCE_CAMERAS[id] || EVIDENCE_CAMERAS["06_final_wide_rainy_container_checkpoint"];
  const animationState = EVIDENCE_ANIMATION_STATES[id] || EVIDENCE_ANIMATION_STATES["06_final_wide_rainy_container_checkpoint"];
  animatedCharacters.player.setState(animationState.player);
  animatedCharacters.enemy.setState(animationState.enemy);
  camera.fov = preset.fov;
  camera.position.set(...preset.position);
  camera.lookAt(new THREE.Vector3(...preset.target));
  camera.updateProjectionMatrix();
  window.__TACTICAL_VISUAL_UPGRADE__.evidence = id;
  window.__TACTICAL_VISUAL_UPGRADE__.animation = {
    player: animatedCharacters.player.getStatus(),
    enemy: animatedCharacters.enemy.getStatus(),
    requiredForEvidence: animationState
  };
}

function makeBoxFallback(name, color, scale = [1, 1, 1]) {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(scale[0], scale[1], scale[2]),
    new THREE.MeshStandardMaterial({ color, roughness: 0.7, metalness: 0.08 })
  );
  mesh.name = name;
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function normalizeObject(root, maxDimension) {
  const box = new THREE.Box3().setFromObject(root);
  const size = new THREE.Vector3();
  const center = new THREE.Vector3();
  box.getSize(size);
  box.getCenter(center);
  const max = Math.max(size.x, size.y, size.z);
  if (max > 0) {
    root.scale.setScalar(maxDimension / max);
    root.position.sub(center.multiplyScalar(maxDimension / max));
  }
}

async function loadDirectGlb(loader, path, { name, maxDimension, position, rotation = [0, 0, 0] }) {
  try {
    const gltf = await loader.loader.loadAsync(repoUrl(path));
    const root = gltf.scene;
    root.name = name;
    normalizeObject(root, maxDimension);
    root.position.add(new THREE.Vector3(...position));
    root.rotation.set(...rotation);
    root.traverse((node) => {
      if (node.isMesh) {
        node.castShadow = true;
        node.receiveShadow = true;
      }
    });
    scene.add(root);
    return root;
  } catch (error) {
    window.__TACTICAL_VISUAL_UPGRADE__.blockingEvents.push(`${name}: ${error.message}`);
    const fallback = makeBoxFallback(`${name}_fallback`, 0x6b7280, [0.8, 1.2, 0.35]);
    fallback.position.set(...position);
    scene.add(fallback);
    return fallback;
  }
}

async function boot() {
  setStatus("Loading registry and GLB assets...");
  const registry = await fetchAssetRegistryV2();
  const loader = createTacticalAssetLoader({
    registry,
    baseUrl: "../../",
    evidenceMode,
    failOnFallback: true
  });

  await Promise.allSettled([
    loader.loadAsset("target_hero_rifle_v2").then(({ gltf }) => {
      const rifle = gltf.scene.clone(true);
      rifle.name = "fp_hero_rifle_v2_visual";
      normalizeObject(rifle, 1.34);
      camera.add(rifle);
      rifle.position.set(0.35, -0.30, -0.74);
      rifle.rotation.set(-0.04, -0.38, -0.07);

      const thirdPerson = gltf.scene.clone(true);
      thirdPerson.name = "third_person_hero_rifle_v2_visual";
      normalizeObject(thirdPerson, 0.88);
      thirdPerson.position.set(-0.35, 1.15, 0.06);
      thirdPerson.rotation.set(0.0, -0.92, -0.08);
      scene.add(thirdPerson);

      const npcWeapon = gltf.scene.clone(true);
      npcWeapon.name = "npc_hero_rifle_v2_visual";
      normalizeObject(npcWeapon, 0.88);
      npcWeapon.position.set(2.35, 1.16, -2.10);
      npcWeapon.rotation.set(0.0, -1.22, -0.06);
      scene.add(npcWeapon);

      const worldPickup = gltf.scene.clone(true);
      worldPickup.name = "loot_world_hero_rifle_v2_visual";
      normalizeObject(worldPickup, 0.82);
      worldPickup.position.set(0.18, 0.18, -0.62);
      worldPickup.rotation.set(0.0, 0.42, -0.18);
      scene.add(worldPickup);
      return rifle;
    }),
    loader.loadAsset("baseline_character_player_final").then(({ gltf }) => {
      const player = gltf.scene.clone(true);
      player.name = "third_person_player_baseline_visual";
      normalizeObject(player, 1.8);
      player.position.set(-0.9, 0.02, 0.7);
      player.rotation.y = Math.PI * 0.14;
      player.traverse((node) => {
        if (node.isMesh) {
          node.castShadow = true;
          node.receiveShadow = true;
        }
      });
      scene.add(player);
      return player;
    })
  ]);

  await Promise.allSettled([
    loadDirectGlb(loader, "experiments/tactical_game_full_realism_final_20260513/assets/models/character_enemy_final.glb", {
      name: "enemy_under_checkpoint_light",
      maxDimension: 1.75,
      position: [2.4, 0.02, -1.8],
      rotation: [0, -0.72, 0]
    }),
    loadDirectGlb(loader, "experiments/tactical_game_full_realism_final_20260513/assets/models/prop_container_final.glb", {
      name: "baseline_container_glb_detail",
      maxDimension: 3.2,
      position: [-4.8, 0.04, -2.6],
      rotation: [0, Math.PI / 2, 0]
    }),
    loadDirectGlb(loader, "experiments/tactical_game_full_realism_final_20260513/assets/models/loot_medkit_final.glb", {
      name: "loot_medkit_on_wet_asphalt",
      maxDimension: 0.46,
      position: [0.08, 0.08, 0.25],
      rotation: [0, 0.2, 0]
    }),
    loadDirectGlb(loader, "experiments/tactical_game_full_realism_final_20260513/assets/models/loot_ammo_final.glb", {
      name: "loot_ammo_on_wet_asphalt",
      maxDimension: 0.36,
      position: [0.5, 0.08, 0.05],
      rotation: [0, -0.2, 0]
    })
  ]);

  window.__TACTICAL_VISUAL_UPGRADE__.loaded = true;
  window.__TACTICAL_VISUAL_UPGRADE__.assetStatus = loader.getEvidenceSnapshot();
  window.__TACTICAL_VISUAL_UPGRADE__.animation = {
    player: animatedCharacters.player.getStatus(),
    enemy: animatedCharacters.enemy.getStatus(),
    requiredForEvidence: EVIDENCE_ANIMATION_STATES[selectEl.value]
  };
  setStatus(`Loaded rainy checkpoint. Evidence camera: ${selectEl.value}. Clutter/decal instances: ${layout.clutterCount}.`);
  frameCamera(selectEl.value);
}

selectEl.addEventListener("change", () => frameCamera(selectEl.value));
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate() {
  const delta = Math.min(clock.getDelta(), 0.04);
  animatedCharacters.player.update(delta);
  animatedCharacters.enemy.update(delta);
  rain.update(delta);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

boot().catch((error) => {
  window.__TACTICAL_VISUAL_UPGRADE__.blockingEvents.push(error.message);
  setStatus(`Boot failed: ${error.message}`);
  console.error(error);
}).finally(() => {
  frameCamera(selectEl.value);
  animate();
});
