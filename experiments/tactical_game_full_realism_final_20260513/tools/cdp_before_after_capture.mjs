#!/usr/bin/env node
import { mkdir, rm, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const outDir = new URL("../evidence/", import.meta.url);
const port = 10400 + Math.floor(Math.random() * 1000);
const userDataDir = `/tmp/tactical_game_before_after_cdp_${process.pid}`;

const targets = [
  {
    id: "baseline_source",
    url: "http://localhost:8766/source/14.html",
    screenshot: new URL("before_source_gameplay.png", outDir),
    report: new URL("before_source_gameplay_report.json", outDir),
  },
  {
    id: "upgraded_derivative",
    url: "http://localhost:8765/index.html",
    screenshot: new URL("after_upgraded_gameplay.png", outDir),
    report: new URL("after_upgraded_gameplay_report.json", outDir),
  },
];

await mkdir(outDir, { recursive: true });
await rm(userDataDir, { recursive: true, force: true });

const chrome = spawn(chromePath, [
  "--headless=new",
  "--use-gl=angle",
  "--use-angle=swiftshader",
  "--enable-unsafe-swiftshader",
  "--no-first-run",
  "--disable-extensions",
  `--user-data-dir=${userDataDir}`,
  "--window-size=1440,900",
  `--remote-debugging-port=${port}`,
  "about:blank",
], { stdio: ["ignore", "pipe", "pipe"] });

const stderrChunks = [];
chrome.stderr.on("data", chunk => stderrChunks.push(String(chunk)));

async function fetchJson(endpoint) {
  const res = await fetch(`http://127.0.0.1:${port}${endpoint}`);
  if (!res.ok) throw new Error(`${endpoint} ${res.status}`);
  return res.json();
}

for (let i = 0; i < 80; i++) {
  try {
    await fetchJson("/json/version");
    break;
  } catch (error) {
    if (i === 79) throw error;
    await delay(100);
  }
}

const version = await fetchJson("/json/version");
const ws = new WebSocket(version.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  ws.addEventListener("open", resolve, { once: true });
  ws.addEventListener("error", reject, { once: true });
});

let nextId = 1;
const pending = new Map();
function send(method, params = {}, sessionId = undefined) {
  const id = nextId++;
  ws.send(JSON.stringify({ id, method, params, sessionId }));
  return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
}

ws.addEventListener("message", event => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(JSON.stringify(msg.error)));
    else resolve(msg.result || {});
  }
});

async function captureTarget(target) {
  const events = [];
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });

  const listener = event => {
    const msg = JSON.parse(event.data);
    if (msg.sessionId !== sessionId) return;
    if (["Runtime.exceptionThrown", "Runtime.consoleAPICalled", "Log.entryAdded", "Network.loadingFailed"].includes(msg.method)) {
      events.push(msg);
    }
  };
  ws.addEventListener("message", listener);

  await send("Runtime.enable", {}, sessionId);
  await send("Page.enable", {}, sessionId);
  await send("Network.enable", {}, sessionId);
  await send("Log.enable", {}, sessionId);
  await send("Page.navigate", { url: target.url }, sessionId);
  await delay(1600);
  await send("Runtime.evaluate", {
    expression: `
      (() => {
        const start = document.getElementById("startBtn");
        if (start) start.click();
        if (window.player) {
          player.cameraMode = "third";
          player.weapon = "rifle";
          if (window.weaponState?.rifle) weaponState.rifle.unlocked = true;
          if (window.selectWeapon) selectWeapon("rifle");
          if (window.updateCamera) updateCamera(1);
        }
        return {title: document.title, hasCanvas: !!document.querySelector("canvas")};
      })()
    `,
    returnByValue: true,
    awaitPromise: true,
  }, sessionId);
  await delay(2400);
  await send("Runtime.evaluate", {
    expression: "window.__realismProbe ? window.__realismProbe() : {title: document.title, canvas: !!document.querySelector('canvas')}",
    returnByValue: true,
  }, sessionId);
  const screenshot = await send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  }, sessionId);
  await writeFile(target.screenshot, Buffer.from(screenshot.data, "base64"));

  const filteredEvents = events.map(event => ({
    method: event.method,
    type: event.params?.type || event.params?.entry?.level || null,
    text: event.params?.args?.map(arg => arg.value).filter(Boolean).join(" ")
      || event.params?.entry?.text
      || event.params?.exceptionDetails?.exception?.description
      || event.params?.exceptionDetails?.text
      || null,
  }));
  const report = {
    id: target.id,
    url: target.url,
    screenshot: target.screenshot.pathname,
    events: filteredEvents,
    blockingEvents: filteredEvents.filter(event => event.method === "Runtime.exceptionThrown" || event.method === "Network.loadingFailed" || (event.method === "Log.entryAdded" && event.type === "error")),
  };
  await writeFile(target.report, JSON.stringify(report, null, 2) + "\n");
  ws.removeEventListener("message", listener);
  return report;
}

const reports = [];
for (const target of targets) reports.push(await captureTarget(target));
ws.close();
chrome.kill("SIGTERM");

console.log(JSON.stringify({
  status: reports.every(report => report.screenshot) ? "PASS" : "FAIL",
  reports,
  chromeStderrTail: stderrChunks.join("").split("\n").slice(-20),
}, null, 2));
process.exit(0);
