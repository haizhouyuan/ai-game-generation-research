import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const ASSETS = [
  {
    id: 'triposr_p4_chair',
    label: 'P4 Chair GLB',
    asset: './outputs/assets/triposr_p4_chair_mesh.glb'
  },
  {
    id: 'triposr_p5_synthetic_block',
    label: 'P5 Synthetic Block',
    asset: './outputs/assets/triposr_p5_synthetic_block.glb'
  },
  {
    id: 'triposr_p5_synthetic_tower',
    label: 'P5 Synthetic Tower',
    asset: './outputs/assets/triposr_p5_synthetic_tower.glb'
  }
];

const statusEl = document.querySelector('#status');
const selectEl = document.querySelector('#asset');
const requestedAsset = new URLSearchParams(window.location.search).get('asset');
let active = ASSETS.find((item) => item.id === requestedAsset) || ASSETS[0];

for (const item of ASSETS) {
  const option = document.createElement('option');
  option.value = item.id;
  option.textContent = `${item.id} ${item.label}`;
  selectEl.appendChild(option);
}
selectEl.value = active.id;

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x151719);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xeaf6ff, 0x29323b, 2.4));
const keyLight = new THREE.DirectionalLight(0xffffff, 2.8);
keyLight.position.set(4, 8, 5);
scene.add(keyLight);
const fillLight = new THREE.DirectionalLight(0xb7e2ff, 1.1);
fillLight.position.set(-5, 4, -4);
scene.add(fillLight);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(4.6, 3.4, 5.1);
camera.lookAt(0, 0.7, 0);

const ground = new THREE.Mesh(
  new THREE.BoxGeometry(5.5, 0.08, 5.5),
  new THREE.MeshStandardMaterial({ color: 0x2a3135, roughness: 0.85, metalness: 0.02 })
);
ground.position.y = -0.04;
scene.add(ground);

const loader = new GLTFLoader();
const keys = new Set();
let importedRoot = null;
let player = null;
let finishPad = null;
let assetBox = null;
let normalizedScale = null;
let collisionProbe = null;
let assetLoaded = false;

window.__P5_STATUS__ = {
  loaded: false,
  asset: active.id,
  importedGlb: active.asset,
  playableLoop: true
};

function material(color, roughness = 0.7) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness: 0.06 });
}

function disposeObject(object) {
  if (!object) return;
  object.traverse((node) => {
    if (node.geometry) node.geometry.dispose();
    if (node.material) {
      const materials = Array.isArray(node.material) ? node.material : [node.material];
      materials.forEach((mat) => mat.dispose());
    }
  });
}

function clearRuntimeObjects() {
  for (const obj of [importedRoot, player, finishPad, collisionProbe]) {
    if (obj) {
      scene.remove(obj);
      disposeObject(obj);
    }
  }
  importedRoot = null;
  player = null;
  finishPad = null;
  collisionProbe = null;
  assetBox = null;
  normalizedScale = null;
  assetLoaded = false;
}

function vectorToObject(vec) {
  return { x: Number(vec.x.toFixed(5)), y: Number(vec.y.toFixed(5)), z: Number(vec.z.toFixed(5)) };
}

function boxToObject(box) {
  const size = new THREE.Vector3();
  const center = new THREE.Vector3();
  box.getSize(size);
  box.getCenter(center);
  return {
    min: vectorToObject(box.min),
    max: vectorToObject(box.max),
    size: vectorToObject(size),
    center: vectorToObject(center),
    maxDimension: Number(Math.max(size.x, size.y, size.z).toFixed(5))
  };
}

function updateStatus(extra = '') {
  const playerBox = player ? new THREE.Box3().setFromObject(player) : null;
  const finishReached = player && finishPad && player.position.distanceTo(finishPad.position) < 0.55;
  const collisionInitial = Boolean(assetBox && playerBox && assetBox.intersectsBox(playerBox));
  const collisionProbeHit = Boolean(assetBox && collisionProbe && assetBox.intersectsBox(new THREE.Box3().setFromObject(collisionProbe)));
  const state = finishReached ? 'finished' : 'running';
  window.__P5_STATUS__ = {
    loaded: assetLoaded,
    asset: active.id,
    importedGlb: active.asset,
    playableLoop: true,
    normalizedScale,
    bbox: assetBox ? boxToObject(assetBox) : null,
    collisionInitial,
    collisionProbeHit,
    scaleOk: Boolean(normalizedScale && normalizedScale > 0 && normalizedScale <= 100),
    state
  };
  statusEl.textContent = `${active.id}: GLB=${assetLoaded ? 'loaded' : 'loading'}, scale=${normalizedScale ?? 'n/a'}, collisionProbe=${collisionProbeHit}, state=${state}${extra}`;
}

async function loadAsset(id) {
  active = ASSETS.find((item) => item.id === id) || ASSETS[0];
  clearRuntimeObjects();
  statusEl.textContent = `Loading ${active.id}...`;
  updateStatus();

  const gltf = await loader.loadAsync(active.asset);
  importedRoot = gltf.scene;
  importedRoot.traverse((obj) => {
    if (obj.isMesh) {
      obj.castShadow = false;
      obj.receiveShadow = true;
      if (!obj.material) obj.material = material(0xb9c7d1);
    }
  });

  const rawBox = new THREE.Box3().setFromObject(importedRoot);
  const rawSize = new THREE.Vector3();
  const rawCenter = new THREE.Vector3();
  rawBox.getSize(rawSize);
  rawBox.getCenter(rawCenter);
  const maxDimension = Math.max(rawSize.x, rawSize.y, rawSize.z);
  if (!(maxDimension > 0)) {
    throw new Error(`Invalid GLB bounds for ${active.id}`);
  }
  normalizedScale = Number((1.7 / maxDimension).toFixed(6));
  importedRoot.scale.setScalar(normalizedScale);
  importedRoot.position.sub(rawCenter.multiplyScalar(normalizedScale));
  scene.add(importedRoot);

  assetBox = new THREE.Box3().setFromObject(importedRoot);
  importedRoot.position.y += -assetBox.min.y;
  assetBox = new THREE.Box3().setFromObject(importedRoot);

  player = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.32, 0.36), material(0x59c6ff, 0.55));
  player.position.set(-2.1, 0.2, 1.85);
  scene.add(player);

  finishPad = new THREE.Mesh(new THREE.CylinderGeometry(0.44, 0.44, 0.08, 32), material(0x6cff8a, 0.6));
  finishPad.position.set(2.1, 0.04, -1.85);
  scene.add(finishPad);

  const center = new THREE.Vector3();
  assetBox.getCenter(center);
  collisionProbe = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.24, 0.24), material(0xffd45c, 0.5));
  collisionProbe.position.copy(center);
  scene.add(collisionProbe);

  assetLoaded = true;
  updateStatus();
}

function step(delta) {
  if (!player) return;
  const speed = 2.5 * delta;
  const move = new THREE.Vector3();
  if (keys.has('ArrowLeft') || keys.has('KeyA')) move.x -= speed;
  if (keys.has('ArrowRight') || keys.has('KeyD')) move.x += speed;
  if (keys.has('ArrowUp') || keys.has('KeyW')) move.z -= speed;
  if (keys.has('ArrowDown') || keys.has('KeyS')) move.z += speed;
  player.position.add(move);
  player.position.x = Math.max(-2.6, Math.min(2.6, player.position.x));
  player.position.z = Math.max(-2.6, Math.min(2.6, player.position.z));
  if (importedRoot) importedRoot.rotation.y += delta * 0.25;
  if (collisionProbe) collisionProbe.rotation.y += delta * 1.6;
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
  loadAsset(selectEl.value).catch((error) => {
    console.error(error);
    statusEl.textContent = `Asset load failed: ${error.message}`;
    window.__P5_STATUS__.error = error.message;
  });
});
window.addEventListener('keydown', (event) => keys.add(event.code));
window.addEventListener('keyup', (event) => keys.delete(event.code));
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

loadAsset(active.id).catch((error) => {
  console.error(error);
  statusEl.textContent = `Asset load failed: ${error.message}`;
  window.__P5_STATUS__.error = error.message;
});
animate();
