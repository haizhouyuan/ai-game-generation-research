#!/usr/bin/env node
import { mkdir, rm, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const mode = process.argv[2] === "m5" ? "m5" : "rifle";
const cameraMode = process.argv[3] === "first" || process.argv[2] === "first" ? "first" : "third";
const url = mode === "m5"
  ? "http://localhost:8765/index.html?evidence=m5"
  : `http://localhost:8765/index.html?evidence=rifle&camera=${cameraMode}`;
const outDir = new URL("../evidence/", import.meta.url);
const screenshotPath = new URL(mode === "m5" ? "m5_evidence_cdp.png" : `rifle_evidence_cdp_${cameraMode}.png`, outDir);
const reportPath = new URL(mode === "m5" ? "m5_evidence_cdp_report.json" : `rifle_evidence_cdp_${cameraMode}_report.json`, outDir);
const port = 9224 + Math.floor(Math.random() * 1000);
const userDataDir = `/tmp/tactical_game_realism_cdp_profile_${process.pid}_${mode}_${cameraMode}`;

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
const events = [];

ws.addEventListener("message", event => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(JSON.stringify(msg.error)));
    else resolve(msg.result || {});
    return;
  }
  if ([
    "Runtime.exceptionThrown",
    "Runtime.consoleAPICalled",
    "Log.entryAdded",
    "Network.loadingFailed",
  ].includes(msg.method)) {
    events.push(msg);
  }
});

function send(method, params = {}, sessionId = undefined) {
  const id = nextId++;
  ws.send(JSON.stringify({ id, method, params, sessionId }));
  return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
}

const { targetId } = await send("Target.createTarget", { url: "about:blank" });
const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
await send("Runtime.enable", {}, sessionId);
await send("Page.enable", {}, sessionId);
await send("Network.enable", {}, sessionId);
await send("Log.enable", {}, sessionId);
await send("Page.navigate", { url }, sessionId);

let probe = null;
for (let i = 0; i < 120; i++) {
  await delay(250);
  const result = await send("Runtime.evaluate", {
    expression: "window.__realismProbe && window.__realismProbe()",
    returnByValue: true,
  }, sessionId);
  probe = result.result?.value ?? null;
  if (
    mode === "rifle" &&
    probe?.rifleAsset?.status === "loaded" &&
    probe?.player?.weapon === "rifle" &&
    probe?.viewGun?.assetSource &&
    probe?.evidenceCameraRifle?.assetSource
  ) {
    break;
  }
  if (
    mode === "m5" &&
    probe?.m5WeaponShowcase?.count === 4 &&
    Object.values(probe?.weaponAssets || {}).every(asset => asset.status === "loaded")
  ) {
    break;
  }
}

await delay(1200);
{
  const result = await send("Runtime.evaluate", {
    expression: "window.__realismProbe && window.__realismProbe()",
    returnByValue: true,
  }, sessionId);
  probe = result.result?.value ?? probe;
}
const screenshot = await send("Page.captureScreenshot", {
  format: "png",
  fromSurface: true,
  captureBeyondViewport: false,
}, sessionId);
await writeFile(screenshotPath, Buffer.from(screenshot.data, "base64"));

const filteredEvents = events.map(event => ({
  method: event.method,
  type: event.params?.type || event.params?.entry?.level || null,
  text: event.params?.args?.map(arg => arg.value).filter(Boolean).join(" ")
    || event.params?.entry?.text
    || event.params?.exceptionDetails?.exception?.description
    || event.params?.exceptionDetails?.text
    || null,
}));

const blockingEvents = filteredEvents.filter(event => {
  if (event.method === "Runtime.exceptionThrown") return true;
  if (event.method === "Network.loadingFailed") return true;
  if (event.method === "Log.entryAdded" && event.type === "error") return true;
  return false;
});

const report = {
  url,
  screenshot: screenshotPath.pathname,
  probe,
  events: filteredEvents,
  blockingEvents,
  chromeStderrTail: stderrChunks.join("").split("\n").slice(-20),
};
await writeFile(reportPath, JSON.stringify(report, null, 2) + "\n");

ws.close();
chrome.kill("SIGTERM");

const passed = blockingEvents.length === 0 && (
  mode === "m5"
    ? probe?.m5WeaponShowcase?.count === 4 && Object.values(probe?.weaponAssets || {}).every(asset => asset.status === "loaded")
    : probe?.rifleAsset?.status === "loaded" && probe?.player?.weapon === "rifle" && probe?.viewGun?.assetSource && probe?.evidenceCameraRifle?.assetSource
);
console.log(JSON.stringify({
  status: passed ? "PASS" : "FAIL",
  screenshot: screenshotPath.pathname,
  report: reportPath.pathname,
  blockingEvents,
  probe,
}, null, 2));

process.exit(passed ? 0 : 1);
