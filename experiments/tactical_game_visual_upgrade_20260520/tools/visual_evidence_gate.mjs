#!/usr/bin/env node
import { mkdir, rm, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";
import { inflateSync } from "node:zlib";

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const camera = process.argv[2] || "06_final_wide_rainy_container_checkpoint";
const port = 9320 + Math.floor(Math.random() * 500);
const userDataDir = `/tmp/tactical_visual_upgrade_cdp_${process.pid}_${camera}`;
const url = `http://127.0.0.1:8877/experiments/tactical_game_visual_upgrade_20260520/index.html?evidence=${camera}`;
const outDir = new URL("../evidence/", import.meta.url);
const screenshotPath = new URL(`${camera}.png`, outDir);
const reportPath = new URL(`${camera}_report.json`, outDir);

function paeth(a, b, c) {
  const p = a + b - c;
  const pa = Math.abs(p - a);
  const pb = Math.abs(p - b);
  const pc = Math.abs(p - c);
  return pa <= pb && pa <= pc ? a : pb <= pc ? b : c;
}

function pngStats(buffer) {
  if (buffer.toString("ascii", 1, 4) !== "PNG") return { ok: false, reason: "not png" };
  let offset = 8;
  let width = 0;
  let height = 0;
  let colorType = 0;
  let bitDepth = 0;
  const idat = [];
  while (offset < buffer.length) {
    const length = buffer.readUInt32BE(offset);
    const type = buffer.toString("ascii", offset + 4, offset + 8);
    const dataStart = offset + 8;
    const dataEnd = dataStart + length;
    if (type === "IHDR") {
      width = buffer.readUInt32BE(dataStart);
      height = buffer.readUInt32BE(dataStart + 4);
      bitDepth = buffer[dataStart + 8];
      colorType = buffer[dataStart + 9];
    } else if (type === "IDAT") {
      idat.push(buffer.subarray(dataStart, dataEnd));
    } else if (type === "IEND") {
      break;
    }
    offset = dataEnd + 4;
  }
  const channels = colorType === 6 ? 4 : colorType === 2 ? 3 : 0;
  if (!width || !height || bitDepth !== 8 || !channels) {
    return { ok: false, reason: `unsupported png ${width}x${height} bitDepth=${bitDepth} colorType=${colorType}` };
  }
  const raw = inflateSync(Buffer.concat(idat));
  const stride = width * channels;
  const pixels = Buffer.alloc(height * stride);
  let src = 0;
  for (let y = 0; y < height; y += 1) {
    const filter = raw[src++];
    for (let x = 0; x < stride; x += 1) {
      const value = raw[src++];
      const left = x >= channels ? pixels[y * stride + x - channels] : 0;
      const up = y > 0 ? pixels[(y - 1) * stride + x] : 0;
      const upLeft = y > 0 && x >= channels ? pixels[(y - 1) * stride + x - channels] : 0;
      let out = value;
      if (filter === 1) out = (value + left) & 255;
      else if (filter === 2) out = (value + up) & 255;
      else if (filter === 3) out = (value + Math.floor((left + up) / 2)) & 255;
      else if (filter === 4) out = (value + paeth(left, up, upLeft)) & 255;
      pixels[y * stride + x] = out;
    }
  }
  const stepX = Math.max(1, Math.floor(width / 240));
  const stepY = Math.max(1, Math.floor(height / 140));
  let samples = 0;
  let lit = 0;
  let colorful = 0;
  let edgeish = 0;
  for (let y = 0; y < height; y += stepY) {
    for (let x = 0; x < width; x += stepX) {
      const idx = y * stride + x * channels;
      const r = pixels[idx];
      const g = pixels[idx + 1];
      const b = pixels[idx + 2];
      const max = Math.max(r, g, b);
      const min = Math.min(r, g, b);
      if (max > 28) lit += 1;
      if (max - min > 16) colorful += 1;
      if (x >= stepX) {
        const pidx = y * stride + (x - stepX) * channels;
        if (Math.abs(r - pixels[pidx]) + Math.abs(g - pixels[pidx + 1]) + Math.abs(b - pixels[pidx + 2]) > 34) {
          edgeish += 1;
        }
      }
      samples += 1;
    }
  }
  return { ok: true, width, height, litRatio: lit / samples, colorfulRatio: colorful / samples, edgeRatio: edgeish / samples };
}

async function fetchJson(endpoint) {
  const res = await fetch(`http://127.0.0.1:${port}${endpoint}`);
  if (!res.ok) throw new Error(`${endpoint} ${res.status}`);
  return res.json();
}

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
  "about:blank"
], { stdio: ["ignore", "pipe", "pipe"] });

const stderrChunks = [];
chrome.stderr.on("data", (chunk) => stderrChunks.push(String(chunk)));

for (let i = 0; i < 80; i += 1) {
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

ws.addEventListener("message", (event) => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(JSON.stringify(msg.error)));
    else resolve(msg.result || {});
    return;
  }
  if (["Runtime.exceptionThrown", "Runtime.consoleAPICalled", "Log.entryAdded", "Network.loadingFailed"].includes(msg.method)) {
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
for (let i = 0; i < 120; i += 1) {
  await delay(250);
  const result = await send("Runtime.evaluate", {
    expression: "window.__TACTICAL_VISUAL_UPGRADE__ || null",
    returnByValue: true
  }, sessionId);
  probe = result.result?.value ?? null;
  if (probe?.loaded) break;
}

await delay(1200);
const screenshot = await send("Page.captureScreenshot", {
  format: "png",
  fromSurface: true,
  captureBeyondViewport: false
}, sessionId);
const screenshotBuffer = Buffer.from(screenshot.data, "base64");
await writeFile(screenshotPath, screenshotBuffer);
const imageStats = pngStats(screenshotBuffer);

const filteredEvents = events.map((event) => ({
  method: event.method,
  type: event.params?.type || event.params?.entry?.level || null,
  text: event.params?.args?.map((arg) => arg.value).filter(Boolean).join(" ")
    || event.params?.entry?.text
    || event.params?.exceptionDetails?.exception?.description
    || event.params?.exceptionDetails?.text
    || null
}));
const blockingEvents = filteredEvents.filter((event) => (
  event.method === "Runtime.exceptionThrown"
  || event.method === "Network.loadingFailed"
  || (event.method === "Log.entryAdded" && event.type === "error")
));
const requiredAnimation = probe?.animation?.requiredForEvidence || {};
const animationOk = probe?.animation?.player?.mixerReady === true
  && probe?.animation?.enemy?.mixerReady === true
  && probe?.animation?.player?.requiredClipsPresent === true
  && probe?.animation?.enemy?.requiredClipsPresent === true
  && (!requiredAnimation.player || probe?.animation?.player?.activeClip === requiredAnimation.player)
  && (!requiredAnimation.enemy || probe?.animation?.enemy?.activeClip === requiredAnimation.enemy);

const report = {
  url,
  camera,
  screenshot: screenshotPath.pathname,
  probe,
  imageStats,
  events: filteredEvents,
  blockingEvents,
  chromeStderrTail: stderrChunks.join("").split("\n").slice(-20)
};
await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);

ws.close();
chrome.kill("SIGTERM");
await rm(userDataDir, { recursive: true, force: true });

const imageReadable = imageStats.ok
  && (
    imageStats.litRatio > 0.06
    || (imageStats.colorfulRatio > 0.18 && imageStats.edgeRatio > 0.018)
  )
  && imageStats.colorfulRatio > 0.05
  && imageStats.edgeRatio > 0.008;

const passed = probe?.loaded === true
  && blockingEvents.length === 0
  && imageReadable
  && animationOk;

if (!passed) {
  console.error(JSON.stringify({ passed, report: reportPath.pathname, blockingEvents, imageStats, imageReadable, animationOk, probe }, null, 2));
  process.exit(1);
}

console.log(JSON.stringify({ passed, camera, report: reportPath.pathname, screenshot: screenshotPath.pathname, imageStats, animationOk }, null, 2));
