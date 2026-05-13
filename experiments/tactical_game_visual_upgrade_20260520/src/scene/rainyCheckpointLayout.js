import { createImpactDecals, scatterClutter } from "../runtime/decalSystem.js";
import { makeGlowMaterial } from "../runtime/lightingSystem.js";
import { createPuddle } from "../runtime/weatherSystem.js";

export const EVIDENCE_CAMERAS = {
  "01_fp_rifle_wet_checkpoint": { position: [0.8, 1.62, 5.2], target: [1.1, 1.3, -2.8], fov: 54 },
  "02_third_person_player_gear": { position: [-2.7, 1.8, 3.2], target: [-0.5, 1.15, 0.6], fov: 38 },
  "03_enemy_under_checkpoint_light": { position: [5.5, 1.9, 1.9], target: [2.6, 1.2, -2.0], fov: 42 },
  "04_loot_on_wet_asphalt": { position: [1.2, 0.62, 1.5], target: [0.15, 0.05, 0.2], fov: 34 },
  "05_indoor_killhouse_corridor": { position: [-5.8, 1.45, 5.15], target: [-4.8, 1.3, 1.0], fov: 46 },
  "06_final_wide_rainy_container_checkpoint": { position: [8.6, 5.1, 8.0], target: [0.2, 0.7, -0.4], fov: 48 }
};

export function createRainyCheckpointLayout(THREE, scene) {
  const assets = [];
  const materials = makeMaterials(THREE);

  const ground = new THREE.Mesh(new THREE.PlaneGeometry(18, 12, 96, 64), materials.wetAsphalt);
  ground.name = "wet_asphalt_road";
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);
  assets.push(ground);

  const grid = new THREE.GridHelper(18, 18, 0x243348, 0x101820);
  grid.position.y = 0.024;
  grid.material.transparent = true;
  grid.material.opacity = 0.18;
  scene.add(grid);

  addContainerStack(THREE, scene, materials, -4.6, -2.8, Math.PI / 2);
  addContainerStack(THREE, scene, materials, 5.2, 1.2, -Math.PI / 2);
  addCheckpointBooth(THREE, scene, materials);
  addKillhouseCorridor(THREE, scene, materials);
  addFenceLine(THREE, scene, materials);

  [
    [-2.4, -0.9, 2.8, 0.95],
    [0.9, 1.3, 2.2, 0.7],
    [3.8, -3.2, 3.3, 0.8],
    [-5.2, 4.6, 2.6, 0.55]
  ].forEach(([x, z, sx, sz]) => scene.add(createPuddle(THREE, x, z, sx, sz)));

  createImpactDecals(THREE, scene, materials.impact);
  const clutter = scatterClutter(THREE, scene, materials);
  assets.push(...clutter);

  return {
    materials,
    evidenceCameras: EVIDENCE_CAMERAS,
    clutterCount: clutter.length + 9,
    assets
  };
}

function makeMaterials(THREE) {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#202934";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (let i = 0; i < 3000; i += 1) {
    const v = 22 + Math.random() * 48;
    ctx.fillStyle = `rgba(${v},${v + 6},${v + 12},${0.18 + Math.random() * 0.25})`;
    ctx.fillRect(Math.random() * 256, Math.random() * 256, 1 + Math.random() * 3, 1 + Math.random() * 3);
  }
  const asphaltTexture = new THREE.CanvasTexture(canvas);
  asphaltTexture.wrapS = THREE.RepeatWrapping;
  asphaltTexture.wrapT = THREE.RepeatWrapping;
  asphaltTexture.repeat.set(10, 7);
  asphaltTexture.colorSpace = THREE.SRGBColorSpace;

  return {
    wetAsphalt: new THREE.MeshStandardMaterial({
      map: asphaltTexture,
      color: 0x8aa0ad,
      roughness: 0.23,
      metalness: 0.02
    }),
    containerBlue: new THREE.MeshStandardMaterial({ color: 0x28455f, roughness: 0.62, metalness: 0.28 }),
    containerGreen: new THREE.MeshStandardMaterial({ color: 0x3f5a45, roughness: 0.66, metalness: 0.24 }),
    concrete: new THREE.MeshStandardMaterial({ color: 0x77808a, roughness: 0.86, metalness: 0.02 }),
    darkMetal: new THREE.MeshStandardMaterial({ color: 0x18212b, roughness: 0.42, metalness: 0.55 }),
    glass: new THREE.MeshStandardMaterial({ color: 0x92c7e8, roughness: 0.08, metalness: 0, transparent: true, opacity: 0.38 }),
    warning: new THREE.MeshStandardMaterial({ color: 0xd7a731, roughness: 0.48, metalness: 0.08 }),
    impact: new THREE.MeshBasicMaterial({ color: 0x080706, transparent: true, opacity: 0.72, depthWrite: false }),
    brass: new THREE.MeshStandardMaterial({ color: 0xc69a4d, roughness: 0.36, metalness: 0.65 }),
    paper: new THREE.MeshStandardMaterial({ color: 0xbfc2b9, roughness: 0.93, metalness: 0, side: THREE.DoubleSide }),
    cable: new THREE.MeshStandardMaterial({ color: 0x050607, roughness: 0.72, metalness: 0.05 }),
    lamp: makeGlowMaterial(THREE, 0xffd08a, 2.3),
    redLamp: makeGlowMaterial(THREE, 0xff4055, 2.8)
  };
}

function addContainerStack(THREE, scene, materials, x, z, rotationY) {
  for (let i = 0; i < 3; i += 1) {
    const box = new THREE.Mesh(
      new THREE.BoxGeometry(2.4, 1.25, 5.2, 1, 1, 8),
      i % 2 ? materials.containerGreen : materials.containerBlue
    );
    box.name = `corrugated_container_${x}_${i}`;
    box.position.set(x + i * 0.15, 0.64 + i * 0.04, z + i * 1.25);
    box.rotation.y = rotationY;
    box.castShadow = true;
    box.receiveShadow = true;
    scene.add(box);

    for (let stripe = -2; stripe <= 2; stripe += 1) {
      const rib = new THREE.Mesh(new THREE.BoxGeometry(0.035, 1.32, 5.3), materials.darkMetal);
      rib.position.copy(box.position);
      rib.position.x += Math.cos(rotationY) * stripe * 0.42;
      rib.position.z -= Math.sin(rotationY) * stripe * 0.42;
      rib.position.y += 0.02;
      rib.rotation.y = rotationY;
      scene.add(rib);
    }
  }
}

function addCheckpointBooth(THREE, scene, materials) {
  const booth = new THREE.Group();
  booth.name = "checkpoint_booth";
  booth.position.set(2.8, 0, -3.2);
  booth.rotation.y = -0.08;
  scene.add(booth);

  const base = new THREE.Mesh(new THREE.BoxGeometry(2.2, 1.7, 1.8), materials.concrete);
  base.position.y = 0.85;
  base.castShadow = true;
  base.receiveShadow = true;
  booth.add(base);

  const glass = new THREE.Mesh(new THREE.BoxGeometry(2.24, 0.7, 0.035), materials.glass);
  glass.position.set(0, 1.18, 0.92);
  booth.add(glass);

  const roof = new THREE.Mesh(new THREE.BoxGeometry(2.7, 0.18, 2.2), materials.darkMetal);
  roof.position.y = 1.86;
  roof.castShadow = true;
  booth.add(roof);

  const lamp = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.16, 20), materials.lamp);
  lamp.position.set(-0.8, 1.74, 1.12);
  lamp.rotation.x = Math.PI / 2;
  booth.add(lamp);
}

function addKillhouseCorridor(THREE, scene, materials) {
  const group = new THREE.Group();
  group.name = "killhouse_corridor_entry";
  group.position.set(-5.2, 0, 3.0);
  scene.add(group);

  const floor = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.08, 5.8), materials.concrete);
  floor.position.set(0, 0.04, 0);
  floor.receiveShadow = true;
  group.add(floor);

  [-1.35, 1.35].forEach((x) => {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(0.18, 2.2, 5.8), materials.concrete);
    wall.position.set(x, 1.1, 0);
    wall.castShadow = true;
    wall.receiveShadow = true;
    group.add(wall);
  });

  const red = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.08, 0.08), materials.redLamp);
  red.position.set(0, 2.0, -2.4);
  group.add(red);

  for (let i = 0; i < 7; i += 1) {
    const stripe = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.012, 0.08), i % 2 ? materials.warning : materials.darkMetal);
    stripe.position.set(-0.52 + (i % 2) * 1.04, 0.095, -2.45 + i * 0.62);
    stripe.rotation.y = i % 2 ? 0.18 : -0.18;
    group.add(stripe);
  }

  [-1, 1].forEach((side) => {
    for (let i = 0; i < 4; i += 1) {
      const panel = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.72, 0.8), i % 2 ? materials.darkMetal : materials.containerBlue);
      panel.position.set(side * 1.24, 1.08, -1.9 + i * 1.25);
      group.add(panel);
    }
  });

  for (let i = 0; i < 3; i += 1) {
    const stand = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.85, 0.05), materials.darkMetal);
    stand.position.set(-0.72 + i * 0.72, 0.5, -1.7 + i * 0.78);
    group.add(stand);
    const target = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.52, 0.045), materials.paper);
    target.position.set(stand.position.x, 1.04, stand.position.z);
    target.rotation.y = 0.18 - i * 0.16;
    group.add(target);
    const center = new THREE.Mesh(new THREE.CircleGeometry(0.07, 16), materials.impact);
    center.position.set(target.position.x, target.position.y, target.position.z + 0.026);
    center.rotation.y = target.rotation.y;
    group.add(center);
  }
}

function addFenceLine(THREE, scene, materials) {
  for (let i = 0; i < 9; i += 1) {
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 1.7, 10), materials.darkMetal);
    post.position.set(-7.5 + i * 1.85, 0.85, -5.8);
    post.castShadow = true;
    scene.add(post);
  }
  for (let row = 0; row < 3; row += 1) {
    const rail = new THREE.Mesh(new THREE.BoxGeometry(15.2, 0.025, 0.025), materials.darkMetal);
    rail.position.set(0, 0.45 + row * 0.48, -5.8);
    scene.add(rail);
  }
}
