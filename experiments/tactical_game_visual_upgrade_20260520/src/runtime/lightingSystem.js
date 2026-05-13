export function configureRainyCheckpointLighting(THREE, scene, renderer) {
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.82;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  scene.background = new THREE.Color(0x05080d);
  scene.fog = new THREE.FogExp2(0x0b1119, 0.045);

  const hemi = new THREE.HemisphereLight(0x9dbbd7, 0x111820, 0.55);
  scene.add(hemi);

  const moon = new THREE.DirectionalLight(0xb7d8ff, 1.25);
  moon.position.set(-7, 12, -8);
  moon.castShadow = true;
  moon.shadow.mapSize.set(2048, 2048);
  moon.shadow.camera.near = 0.5;
  moon.shadow.camera.far = 55;
  moon.shadow.camera.left = -18;
  moon.shadow.camera.right = 18;
  moon.shadow.camera.top = 18;
  moon.shadow.camera.bottom = -18;
  scene.add(moon);

  const checkpointWarm = new THREE.SpotLight(0xffd08a, 4.2, 18, Math.PI / 5, 0.45, 1.2);
  checkpointWarm.position.set(4.2, 5.4, -3.4);
  checkpointWarm.target.position.set(0.6, 0.1, -1.6);
  checkpointWarm.castShadow = true;
  scene.add(checkpointWarm, checkpointWarm.target);

  const corridorCold = new THREE.PointLight(0x7dd3fc, 3.1, 10, 1.4);
  corridorCold.position.set(-4.8, 2.4, 4.4);
  scene.add(corridorCold);

  const redBeacon = new THREE.PointLight(0xff4158, 2.0, 9, 1.8);
  redBeacon.position.set(6.4, 2.8, 4.2);
  scene.add(redBeacon);

  return { hemi, moon, checkpointWarm, corridorCold, redBeacon };
}

export function makeGlowMaterial(THREE, color, intensity = 1.8) {
  return new THREE.MeshStandardMaterial({
    color,
    emissive: color,
    emissiveIntensity: intensity,
    roughness: 0.38,
    metalness: 0.08
  });
}
