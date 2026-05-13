export const BENCHMARK_INPUTS = [
  {
    id: "GAME-B1",
    title: "Workshop Battery Maze",
    prompt: "A small friendly robot that collects glowing batteries in a workshop maze.",
    playerKind: "robot",
    pickupKind: "battery",
    finishLabel: "Charge dock",
    targetCount: 4,
    theme: {
      backgroundTop: "#20313a",
      backgroundBottom: "#14191c",
      floor: "#3a4f59",
      floorTrim: "#6c7f77",
      accent: "#f4c542",
      player: "#61d4e8",
      pickup: "#ffe66b",
      hazard: "#e85d57",
      finish: "#8bd17c"
    }
  },
  {
    id: "GAME-B2",
    title: "Island Platform Course",
    prompt: "A low-poly island obstacle course with three platforms, coins, and one moving hazard.",
    playerKind: "runner",
    pickupKind: "coin",
    finishLabel: "Signal flag",
    targetCount: 5,
    theme: {
      backgroundTop: "#7fc7d9",
      backgroundBottom: "#224d5c",
      floor: "#5da66f",
      floorTrim: "#d9b66f",
      accent: "#f9d65c",
      player: "#f7f1dc",
      pickup: "#ffd84a",
      hazard: "#d94948",
      finish: "#ffffff"
    }
  },
  {
    id: "GAME-B3",
    title: "Space Hangar Rover",
    prompt: "A tiny space hangar scene with a controllable rover, one pickup item, and a finish pad.",
    playerKind: "rover",
    pickupKind: "core",
    finishLabel: "Launch pad",
    targetCount: 1,
    theme: {
      backgroundTop: "#171d33",
      backgroundBottom: "#080b12",
      floor: "#38405d",
      floorTrim: "#7a819e",
      accent: "#b7f2ff",
      player: "#f2a65a",
      pickup: "#9df2c8",
      hazard: "#b75cff",
      finish: "#7ce38b"
    }
  }
];

export function findBenchmark(id) {
  return BENCHMARK_INPUTS.find((input) => input.id === id) || BENCHMARK_INPUTS[0];
}
