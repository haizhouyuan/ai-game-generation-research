import { BENCHMARK_INPUTS, findBenchmark } from "./benchmarkInputs.js";
import { GameEngine } from "./gameEngine.js";

const canvas = document.querySelector("#game");
const hud = document.querySelector("#status-json");
const promptText = document.querySelector("#prompt-text");
const buttons = document.querySelector("#benchmark-buttons");
const engine = new GameEngine(canvas, hud);

function selectBenchmark(id) {
  const input = findBenchmark(id);
  for (const button of buttons.querySelectorAll("button")) {
    button.classList.toggle("active", button.dataset.benchmark === input.id);
  }
  promptText.textContent = input.prompt;
  engine.load(input);
  const url = new URL(window.location.href);
  url.searchParams.set("benchmark", input.id);
  window.history.replaceState({}, "", url);
}

for (const input of BENCHMARK_INPUTS) {
  const button = document.createElement("button");
  button.type = "button";
  button.dataset.benchmark = input.id;
  button.textContent = input.id;
  button.title = input.title;
  button.addEventListener("click", () => selectBenchmark(input.id));
  buttons.appendChild(button);
}

document.querySelector("#reset").addEventListener("click", () => selectBenchmark(engine.scene.id));

const initialId = new URLSearchParams(window.location.search).get("benchmark") || BENCHMARK_INPUTS[0].id;
const initial = findBenchmark(initialId);
promptText.textContent = initial.prompt;
for (const button of buttons.querySelectorAll("button")) {
  button.classList.toggle("active", button.dataset.benchmark === initial.id);
}
engine.start(initial);
