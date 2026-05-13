import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const BENCHMARKS = [
  {
    id: 'GAME-B1',
    label: 'Robot Workshop',
    asset: './outputs/assets/workshop_robot.glb',
    start: new THREE.Vector3(-3.8, 0.25, 3.0),
    collectibles: [[-1.8, 0.35, 1.8], [0.8, 0.35, 0.9], [2.3, 0.35, -1.4]],
    hazards: [[-0.3, 0.35, -1.8]],
    finish: new THREE.Vector3(3.6, 0.08, -3.0),
    camera: new THREE.Vector3(6, 5.5, 7)
  },
  {
    id: 'GAME-B2',
    label: 'Island Course',
    asset: './outputs/assets/island_course.glb',
    start: new THREE.Vector3(-4.2, 0.25, 0),
    collectibles: [[-2.2, 0.35, 1.4], [-0.4, 0.35, -1.2], [1.6, 0.35, 1.1], [3.0, 0.35, -0.4]],
    hazards: [[0.8, 0.35, 0]],
    finish: new THREE.Vector3(4.2, 0.08, 0),
    camera: new THREE.Vector3(6.5, 5, 6.5)
  },
  {
    id: 'GAME-B3',
    label: 'Space Hangar',
    asset: './outputs/assets/space_hangar.glb',
    start: new THREE.Vector3(-3.5, 0.25, -2.5),
    collectibles: [[0.2, 0.35, 0.2]],
    hazards: [[-0.8, 0.35, 1.8]],
    finish: new THREE.Vector3(3.6, 0.08, 2.8),
    camera: new THREE.Vector3(6, 5, 7)
  }
];

const statusEl = document.querySelector('#status');
const selectEl = document.querySelector('#benchmark');
const requestedBenchmark = new URLSearchParams(window.location.search).get('benchmark');
const initialBenchmark = BENCHMARKS.find((item) => item.id === requestedBenchmark) || BENCHMARKS[0];
for (const item of BENCHMARKS) {
  const option = document.createElement('option');
  option.value = item.id;
  option.textContent = `${item.id} ${item.label}`;
  selectEl.appendChild(option);
}
selectEl.value = initialBenchmark.id;

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x111418);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xe8f4ff, 0x1b2430, 2.6));
const keyLight = new THREE.DirectionalLight(0xffffff, 2.4);
keyLight.position.set(4, 8, 5);
scene.add(keyLight);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
const loader = new GLTFLoader();
const keys = new Set();
let active = initialBenchmark;
let importedRoot = null;
let player = null;
let pickups = [];
let hazards = [];
let finishPad = null;
let collected = 0;
let assetLoaded = false;

window.__P2_STATUS__ = {
  loaded: false,
  benchmark: active.id,
  importedGlb: null,
  collectibles: 0,
  collected: 0,
  hazards: 0,
  playableLoop: true
};

function makeMaterial(color, roughness = 0.75) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness: 0.08 });
}

function makeMarker(position, color, scale = 0.22) {
  const mesh = new THREE.Mesh(new THREE.IcosahedronGeometry(scale, 1), makeMaterial(color, 0.45));
  mesh.position.set(position[0], position[1], position[2]);
  scene.add(mesh);
  return mesh;
}

function clearRuntimeObjects() {
  for (const obj of [importedRoot, player, finishPad, ...pickups, ...hazards]) {
    if (obj) scene.remove(obj);
  }
  importedRoot = null;
  player = null;
  pickups = [];
  hazards = [];
  finishPad = null;
  collected = 0;
  assetLoaded = false;
}

async function loadBenchmark(id) {
  active = BENCHMARKS.find((item) => item.id === id) || BENCHMARKS[0];
  clearRuntimeObjects();
  statusEl.textContent = `Loading ${active.id} GLB...`;
  window.__P2_STATUS__ = {
    loaded: false,
    benchmark: active.id,
    importedGlb: active.asset,
    collectibles: active.collectibles.length,
    collected: 0,
    hazards: active.hazards.length,
    playableLoop: true
  };

  const gltf = await loader.loadAsync(active.asset);
  importedRoot = gltf.scene;
  importedRoot.traverse((obj) => {
    if (obj.isMesh) {
      obj.castShadow = false;
      obj.receiveShadow = true;
    }
  });
  scene.add(importedRoot);
  assetLoaded = true;

  player = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.35, 0.45), makeMaterial(0x56c7ff));
  player.position.copy(active.start);
  scene.add(player);

  pickups = active.collectibles.map((pos) => makeMarker(pos, 0xffd34d));
  hazards = active.hazards.map((pos) => makeMarker(pos, 0xff5a6b, 0.28));
  finishPad = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 0.08, 32), makeMaterial(0x4dff88));
  finishPad.position.copy(active.finish);
  scene.add(finishPad);

  camera.position.copy(active.camera);
  camera.lookAt(0, 0, 0);
  updateStatus();
  window.__P2_STATUS__.loaded = true;
}

function updateStatus(extra = '') {
  const complete = collected >= active.collectibles.length;
  const nearFinish = finishPad && player && player.position.distanceTo(finishPad.position) < 0.8;
  const state = complete && nearFinish ? 'finished' : 'running';
  window.__P2_STATUS__.collected = collected;
  window.__P2_STATUS__.state = state;
  statusEl.textContent = `${active.id}: GLB=${assetLoaded ? 'loaded' : 'loading'}, pickups=${collected}/${active.collectibles.length}, hazards=${hazards.length}, state=${state}${extra}`;
}

function step(delta) {
  if (!player) return;
  const speed = 2.7 * delta;
  const move = new THREE.Vector3();
  if (keys.has('ArrowLeft') || keys.has('KeyA')) move.x -= speed;
  if (keys.has('ArrowRight') || keys.has('KeyD')) move.x += speed;
  if (keys.has('ArrowUp') || keys.has('KeyW')) move.z -= speed;
  if (keys.has('ArrowDown') || keys.has('KeyS')) move.z += speed;
  player.position.add(move);
  player.position.x = Math.max(-5, Math.min(5, player.position.x));
  player.position.z = Math.max(-4, Math.min(4, player.position.z));

  for (const pickup of pickups) {
    if (pickup.visible && pickup.position.distanceTo(player.position) < 0.55) {
      pickup.visible = false;
      collected += 1;
    }
    pickup.rotation.y += delta * 2.2;
  }

  hazards.forEach((hazard, index) => {
    hazard.position.x += Math.sin(performance.now() * 0.001 + index) * 0.006;
    hazard.rotation.y += delta * 3.1;
    if (hazard.position.distanceTo(player.position) < 0.55) {
      player.position.copy(active.start);
      updateStatus(' reset');
    }
  });
  updateStatus();
}

let last = performance.now();
function animate(now = performance.now()) {
  const delta = Math.min(0.05, (now - last) / 1000);
  last = now;
  step(delta);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

selectEl.addEventListener('change', () => {
  loadBenchmark(selectEl.value).catch((error) => {
    console.error(error);
    statusEl.textContent = `Asset load failed: ${error.message}`;
    window.__P2_STATUS__.error = error.message;
  });
});
window.addEventListener('keydown', (event) => keys.add(event.code));
window.addEventListener('keyup', (event) => keys.delete(event.code));
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

loadBenchmark(active.id).catch((error) => {
  console.error(error);
  statusEl.textContent = `Asset load failed: ${error.message}`;
  window.__P2_STATUS__.error = error.message;
});
animate();
