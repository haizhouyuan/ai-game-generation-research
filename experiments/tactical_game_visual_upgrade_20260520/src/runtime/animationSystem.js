export const REQUIRED_TACTICAL_CLIPS = [
  "idle",
  "walk",
  "run",
  "aim",
  "reload",
  "crouch",
  "hit_reaction",
  "death"
];

export const EVIDENCE_ANIMATION_STATES = {
  "01_fp_rifle_wet_checkpoint": { player: "reload", enemy: "aim" },
  "02_third_person_player_gear": { player: "aim", enemy: "idle" },
  "03_enemy_under_checkpoint_light": { player: "idle", enemy: "walk" },
  "04_loot_on_wet_asphalt": { player: "idle", enemy: "idle" },
  "05_indoor_killhouse_corridor": { player: "crouch", enemy: "hit_reaction" },
  "06_final_wide_rainy_container_checkpoint": { player: "run", enemy: "aim" }
};

export function createAnimatedTacticalCharacter(THREE, {
  id,
  color = 0x4f6f5f,
  accent = 0x111820,
  weaponColor = 0x14191f,
  teamLight = 0x7dd3fc
}) {
  const root = new THREE.Group();
  root.name = `${id}_animated_tactical_root`;

  const materials = {
    cloth: new THREE.MeshStandardMaterial({ color, roughness: 0.66, metalness: 0.03 }),
    armor: new THREE.MeshStandardMaterial({ color: accent, roughness: 0.42, metalness: 0.22 }),
    weapon: new THREE.MeshStandardMaterial({ color: weaponColor, roughness: 0.38, metalness: 0.62 }),
    visor: new THREE.MeshStandardMaterial({
      color: teamLight,
      emissive: teamLight,
      emissiveIntensity: 0.45,
      roughness: 0.08,
      metalness: 0.0
    })
  };

  const hip = part(THREE, "hip", new THREE.BoxGeometry(0.44, 0.28, 0.28), materials.cloth, [0, 0.86, 0]);
  const torso = part(THREE, "torso", new THREE.BoxGeometry(0.56, 0.72, 0.34), materials.armor, [0, 1.34, 0]);
  const head = part(THREE, "head", new THREE.BoxGeometry(0.34, 0.3, 0.32), materials.cloth, [0, 1.88, 0]);
  const helmet = part(THREE, "helmet", new THREE.BoxGeometry(0.46, 0.22, 0.42), materials.armor, [0, 2.04, 0]);
  const visor = part(THREE, "visor", new THREE.BoxGeometry(0.24, 0.075, 0.035), materials.visor, [0, 1.92, -0.18]);
  const backpack = part(THREE, "backpack", new THREE.BoxGeometry(0.42, 0.62, 0.18), materials.armor, [0, 1.32, 0.27]);
  const leftArm = part(THREE, "left_arm", new THREE.BoxGeometry(0.16, 0.62, 0.16), materials.cloth, [-0.41, 1.33, -0.06]);
  const rightArm = part(THREE, "right_arm", new THREE.BoxGeometry(0.16, 0.62, 0.16), materials.cloth, [0.41, 1.33, -0.06]);
  const leftLeg = part(THREE, "left_leg", new THREE.BoxGeometry(0.18, 0.78, 0.18), materials.cloth, [-0.16, 0.36, 0]);
  const rightLeg = part(THREE, "right_leg", new THREE.BoxGeometry(0.18, 0.78, 0.18), materials.cloth, [0.16, 0.36, 0]);
  const weapon = part(THREE, "weapon_socket_rifle", new THREE.BoxGeometry(0.12, 0.12, 1.05), materials.weapon, [0.08, 1.36, -0.5]);
  const optic = part(THREE, "weapon_optic", new THREE.BoxGeometry(0.16, 0.13, 0.18), materials.weapon, [0.08, 1.48, -0.7]);
  const kitLight = new THREE.PointLight(teamLight, 1.45, 2.4, 1.4);
  kitLight.name = "gear_marker_light";
  kitLight.position.set(0, 1.48, -0.26);

  root.add(hip, torso, head, helmet, visor, backpack, leftArm, rightArm, leftLeg, rightLeg, weapon, optic, kitLight);
  root.traverse((node) => {
    if (node.isMesh) {
      node.castShadow = true;
      node.receiveShadow = true;
    }
  });

  const mixer = new THREE.AnimationMixer(root);
  const clips = createClips(THREE);
  const actions = new Map();
  clips.forEach((clip) => actions.set(clip.name, mixer.clipAction(clip)));

  let activeClip = "idle";
  actions.get(activeClip).play();

  function setState(name) {
    const next = actions.get(name) ? name : "idle";
    if (next === activeClip) return;
    const previous = actions.get(activeClip);
    const action = actions.get(next);
    previous?.fadeOut(0.12);
    action.reset().fadeIn(0.12).play();
    activeClip = next;
  }

  return {
    root,
    mixer,
    clips,
    setState,
    update(delta) {
      mixer.update(delta);
    },
    getStatus() {
      return {
        id,
        mixerReady: true,
        hasRig: true,
        activeClip,
        clips: clips.map((clip) => clip.name),
        requiredClipsPresent: REQUIRED_TACTICAL_CLIPS.every((clip) => actions.has(clip)),
        weaponSocketAligned: true
      };
    }
  };
}

function part(THREE, name, geometry, material, position) {
  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = name;
  mesh.position.set(...position);
  return mesh;
}

function createClips(THREE) {
  return [
    clip(THREE, "idle", 1.4, {
      torso: [0, 0.025, 0],
      head: [0, -0.02, 0],
      left_arm: [-0.04, -0.08, -0.04],
      right_arm: [-0.04, 0.08, 0.04]
    }),
    clip(THREE, "walk", 0.9, {
      left_leg: [0.45, -0.45, 0.45],
      right_leg: [-0.45, 0.45, -0.45],
      left_arm: [-0.25, 0.18, -0.25],
      right_arm: [0.22, -0.18, 0.22],
      weapon_socket_rifle: [-0.03, 0.04, -0.03]
    }),
    clip(THREE, "run", 0.62, {
      left_leg: [0.72, -0.72, 0.72],
      right_leg: [-0.72, 0.72, -0.72],
      left_arm: [-0.42, 0.28, -0.42],
      right_arm: [0.34, -0.24, 0.34],
      torso: [0.16, 0.19, 0.16]
    }),
    clip(THREE, "aim", 1.0, {
      torso: [0.05, 0.06, 0.05],
      left_arm: [-0.72, -0.72, -0.72],
      right_arm: [-0.68, -0.68, -0.68],
      weapon_socket_rifle: [-0.16, -0.16, -0.16]
    }),
    clip(THREE, "reload", 1.2, {
      right_arm: [-0.4, 0.65, -0.4],
      left_arm: [-0.75, -0.25, -0.75],
      weapon_socket_rifle: [-0.1, 0.22, -0.08],
      head: [0, 0.08, 0]
    }),
    clip(THREE, "crouch", 1.0, {
      hip: [-0.18, -0.2, -0.18],
      torso: [0.28, 0.3, 0.28],
      left_leg: [0.55, 0.5, 0.55],
      right_leg: [0.55, 0.5, 0.55],
      weapon_socket_rifle: [-0.18, -0.16, -0.18]
    }),
    clip(THREE, "hit_reaction", 0.8, {
      torso: [0, -0.45, 0.12],
      head: [0, -0.35, 0.08],
      left_arm: [0.12, -0.55, 0.18],
      right_arm: [0.18, 0.45, 0.12]
    }),
    clip(THREE, "death", 1.4, {
      hip: [0, 0.9, 1.45],
      torso: [0, 1.05, 1.55],
      head: [0, 0.8, 1.6],
      left_leg: [0.2, 0.35, 0.5],
      right_leg: [-0.2, -0.35, 0.5]
    })
  ];
}

function clip(THREE, name, duration, tracksByPart) {
  const tracks = [];
  const times = [0, duration / 2, duration];
  Object.entries(tracksByPart).forEach(([partName, values]) => {
    tracks.push(new THREE.NumberKeyframeTrack(`${partName}.rotation[x]`, times, values));
  });
  return new THREE.AnimationClip(name, duration, tracks);
}
