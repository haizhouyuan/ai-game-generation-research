export function createImpactDecals(THREE, scene, material) {
  const decals = [];
  const geometry = new THREE.CircleGeometry(0.075, 12);
  const positions = [
    [-3.5, 1.35, -5.82], [-3.1, 1.8, -5.81], [-2.75, 0.9, -5.82],
    [5.72, 1.25, -2.3], [5.71, 2.05, -1.6], [5.72, 1.62, -0.7],
    [1.8, 0.05, 2.2], [-0.8, 0.05, -2.0], [3.4, 0.05, 0.8]
  ];

  positions.forEach(([x, y, z], index) => {
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = `impact_decal_${index}`;
    mesh.position.set(x, y, z);
    if (y < 0.1) {
      mesh.rotation.x = -Math.PI / 2;
      mesh.scale.setScalar(1.8);
    } else if (x > 5) {
      mesh.rotation.y = -Math.PI / 2;
    } else {
      mesh.rotation.y = Math.PI;
    }
    scene.add(mesh);
    decals.push(mesh);
  });

  return decals;
}

export function scatterClutter(THREE, scene, materialByKind) {
  const objects = [];
  const casingGeometry = new THREE.CylinderGeometry(0.025, 0.025, 0.18, 10);
  const paperGeometry = new THREE.PlaneGeometry(0.22, 0.13);
  const cableGeometry = new THREE.TorusGeometry(0.32, 0.014, 8, 36);

  for (let i = 0; i < 26; i += 1) {
    const casing = new THREE.Mesh(casingGeometry, materialByKind.brass);
    casing.name = `spent_casing_${i}`;
    casing.position.set(-1.6 + Math.random() * 3.2, 0.08, -1.2 + Math.random() * 2.2);
    casing.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    casing.castShadow = true;
    scene.add(casing);
    objects.push(casing);
  }

  for (let i = 0; i < 16; i += 1) {
    const paper = new THREE.Mesh(paperGeometry, materialByKind.paper);
    paper.name = `wet_paper_${i}`;
    paper.position.set(-5 + Math.random() * 10, 0.035, -4.8 + Math.random() * 9.2);
    paper.rotation.set(-Math.PI / 2, 0, Math.random() * Math.PI);
    scene.add(paper);
    objects.push(paper);
  }

  for (let i = 0; i < 4; i += 1) {
    const cable = new THREE.Mesh(cableGeometry, materialByKind.cable);
    cable.name = `cable_loop_${i}`;
    cable.position.set(-5.2 + i * 0.9, 0.055, 4.1 + Math.sin(i) * 0.35);
    cable.rotation.x = -Math.PI / 2;
    cable.scale.set(1.4, 0.65, 1);
    scene.add(cable);
    objects.push(cable);
  }

  return objects;
}
