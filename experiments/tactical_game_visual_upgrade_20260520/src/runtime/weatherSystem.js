export function createRainSystem(THREE, scene, { count = 900, radius = 18 } = {}) {
  const positions = new Float32Array(count * 3);
  const velocities = new Float32Array(count);

  for (let i = 0; i < count; i += 1) {
    positions[i * 3] = (Math.random() - 0.5) * radius * 2;
    positions[i * 3 + 1] = Math.random() * 9 + 2;
    positions[i * 3 + 2] = (Math.random() - 0.5) * radius * 2;
    velocities[i] = 8 + Math.random() * 7;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({
    color: 0xbdd8ff,
    size: 0.025,
    transparent: true,
    opacity: 0.52,
    depthWrite: false
  });
  const points = new THREE.Points(geometry, material);
  points.name = "rain_particles";
  scene.add(points);

  return {
    object: points,
    update(delta) {
      const array = geometry.attributes.position.array;
      for (let i = 0; i < count; i += 1) {
        array[i * 3] -= delta * 1.2;
        array[i * 3 + 1] -= velocities[i] * delta;
        if (array[i * 3 + 1] < 0.05) {
          array[i * 3] = (Math.random() - 0.5) * radius * 2;
          array[i * 3 + 1] = Math.random() * 5 + 6;
          array[i * 3 + 2] = (Math.random() - 0.5) * radius * 2;
        }
      }
      geometry.attributes.position.needsUpdate = true;
    }
  };
}

export function createPuddle(THREE, x, z, sx, sz) {
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(sx, sz, 32, 8),
    new THREE.MeshStandardMaterial({
      color: 0x172333,
      roughness: 0.08,
      metalness: 0.0,
      transparent: true,
      opacity: 0.58
    })
  );
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.set(x, 0.022, z);
  mesh.receiveShadow = true;
  return mesh;
}
