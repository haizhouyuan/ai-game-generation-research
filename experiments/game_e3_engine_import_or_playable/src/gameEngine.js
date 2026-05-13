import { generateScene } from "./proceduralScenes.js";

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function rectHitCircle(rect, circle) {
  const x0 = rect.x - rect.w / 2;
  const x1 = rect.x + rect.w / 2;
  const y0 = rect.y - rect.h / 2;
  const y1 = rect.y + rect.h / 2;
  const cx = clamp(circle.x, x0, x1);
  const cy = clamp(circle.y, y0, y1);
  return Math.hypot(circle.x - cx, circle.y - cy) < circle.radius;
}

export class GameEngine {
  constructor(canvas, hud) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.hud = hud;
    this.keys = new Set();
    this.time = 0;
    this.last = performance.now();
    this.activeInput = null;
    this.scene = null;
    this.collected = 0;
    this.won = false;
    this.message = "";
    this.loop = this.loop.bind(this);
  }

  start(input) {
    this.load(input);
    window.addEventListener("keydown", (event) => this.keys.add(event.key.toLowerCase()));
    window.addEventListener("keyup", (event) => this.keys.delete(event.key.toLowerCase()));
    requestAnimationFrame(this.loop);
  }

  load(input) {
    this.activeInput = input;
    this.scene = structuredClone(generateScene(input));
    this.collected = 0;
    this.won = false;
    this.message = "";
    this.time = 0;
    this.setStatus();
  }

  get player() {
    return this.scene.entities.find((entity) => entity.id === "player");
  }

  resize() {
    const dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    const width = Math.floor(window.innerWidth * dpr);
    const height = Math.floor(window.innerHeight * dpr);
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
    }
  }

  project(x, y, z = 0) {
    const bounds = this.scene.bounds;
    const scale = Math.min(this.canvas.width / (bounds.w * 1.8), this.canvas.height / (bounds.h * 1.55));
    const originX = this.canvas.width * 0.5;
    const originY = this.canvas.height * 0.2;
    return {
      x: originX + (x - y) * scale,
      y: originY + (x + y) * scale * 0.5 - z * scale,
      s: scale
    };
  }

  loop(now) {
    const dt = Math.min(0.04, (now - this.last) / 1000);
    this.last = now;
    this.time += dt;
    this.update(dt);
    this.draw();
    requestAnimationFrame(this.loop);
  }

  update(dt) {
    if (!this.scene || this.won) {
      this.setStatus();
      return;
    }
    const player = this.player;
    const prev = { x: player.x, y: player.y };
    let dx = 0;
    let dy = 0;
    if (this.keys.has("arrowleft") || this.keys.has("a")) dx -= 1;
    if (this.keys.has("arrowright") || this.keys.has("d")) dx += 1;
    if (this.keys.has("arrowup") || this.keys.has("w")) dy -= 1;
    if (this.keys.has("arrowdown") || this.keys.has("s")) dy += 1;
    const mag = Math.hypot(dx, dy) || 1;
    player.x += (dx / mag) * 2.35 * dt;
    player.y += (dy / mag) * 2.35 * dt;
    player.x = clamp(player.x, player.radius, this.scene.bounds.w - player.radius);
    player.y = clamp(player.y, player.radius, this.scene.bounds.h - player.radius);

    for (const entity of this.scene.entities) {
      if (entity.solid && rectHitCircle(entity, player)) {
        player.x = prev.x;
        player.y = prev.y;
        break;
      }
    }

    for (const pickup of this.scene.entities.filter((entity) => entity.type === "pickup")) {
      if (!pickup.collected && Math.hypot(player.x - pickup.x, player.y - pickup.y) < pickup.radius + player.radius) {
        pickup.collected = true;
        this.collected += 1;
        this.message = `${pickup.kind} collected`;
      }
    }

    for (const hazard of this.scene.entities.filter((entity) => entity.type === "hazard")) {
      this.updateHazard(hazard);
      if (Math.hypot(player.x - hazard.x, player.y - hazard.y) < hazard.radius + player.radius * 0.75) {
        player.x = this.scene.start.x;
        player.y = this.scene.start.y;
        this.message = "Reset by hazard";
      }
    }

    const finish = this.scene.entities.find((entity) => entity.type === "finish");
    if (finish && this.collected >= this.scene.targetCount && rectHitCircle(finish, player)) {
      this.won = true;
      this.message = "Loop complete";
    }
    this.setStatus();
  }

  updateHazard(hazard) {
    const offset = Math.sin(this.time * hazard.speed) * hazard.travel.amount;
    if (hazard.travel.axis === "x") {
      hazard.x = hazard.baseX + offset;
      hazard.y = hazard.baseY;
    } else {
      hazard.x = hazard.baseX;
      hazard.y = hazard.baseY + offset;
    }
  }

  draw() {
    this.resize();
    const ctx = this.ctx;
    const theme = this.scene.theme;
    const gradient = ctx.createLinearGradient(0, 0, 0, this.canvas.height);
    gradient.addColorStop(0, theme.backgroundTop);
    gradient.addColorStop(1, theme.backgroundBottom);
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    const drawable = [...this.scene.entities].filter((entity) => entity.type !== "player");
    drawable.sort((a, b) => (a.x + a.y + (a.z || 0)) - (b.x + b.y + (b.z || 0)));
    for (const entity of drawable) this.drawEntity(entity);
    this.drawPlayer(this.player);
    this.drawHud();
  }

  drawEntity(entity) {
    if (entity.type === "block" || entity.type === "prop" || entity.type === "finish") {
      this.drawPrism(entity.x, entity.y, entity.w, entity.h, entity.z || 0, entity.d || 0.1, entity.color);
      if (entity.type === "finish") this.drawFinishMarker(entity);
    } else if (entity.type === "pickup") {
      this.drawPickup(entity);
    } else if (entity.type === "hazard") {
      this.drawHazard(entity);
    }
  }

  drawPrism(cx, cy, w, h, z, d, color) {
    const ctx = this.ctx;
    const top = [
      this.project(cx - w / 2, cy - h / 2, z + d),
      this.project(cx + w / 2, cy - h / 2, z + d),
      this.project(cx + w / 2, cy + h / 2, z + d),
      this.project(cx - w / 2, cy + h / 2, z + d)
    ];
    const lower = [
      this.project(cx - w / 2, cy - h / 2, z),
      this.project(cx + w / 2, cy - h / 2, z),
      this.project(cx + w / 2, cy + h / 2, z),
      this.project(cx - w / 2, cy + h / 2, z)
    ];
    ctx.beginPath();
    ctx.moveTo(top[0].x, top[0].y);
    for (const point of top.slice(1)) ctx.lineTo(point.x, point.y);
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = "rgba(6, 10, 12, 0.42)";
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(top[1].x, top[1].y);
    ctx.lineTo(lower[1].x, lower[1].y);
    ctx.lineTo(lower[2].x, lower[2].y);
    ctx.lineTo(top[2].x, top[2].y);
    ctx.closePath();
    ctx.fillStyle = "rgba(0, 0, 0, 0.22)";
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(top[2].x, top[2].y);
    ctx.lineTo(lower[2].x, lower[2].y);
    ctx.lineTo(lower[3].x, lower[3].y);
    ctx.lineTo(top[3].x, top[3].y);
    ctx.closePath();
    ctx.fillStyle = "rgba(0, 0, 0, 0.34)";
    ctx.fill();
  }

  drawPickup(entity) {
    if (entity.collected) return;
    const ctx = this.ctx;
    const pulse = Math.sin(this.time * 3 + entity.x) * 0.05;
    const p = this.project(entity.x, entity.y, entity.z + pulse);
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.fillStyle = entity.color;
    ctx.strokeStyle = "#111719";
    ctx.lineWidth = 2;
    if (entity.kind === "coin") {
      ctx.beginPath();
      ctx.ellipse(0, 0, p.s * 0.18, p.s * 0.25, 0.25, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "rgba(255,255,255,0.55)";
      ctx.fillRect(-p.s * 0.04, -p.s * 0.16, p.s * 0.05, p.s * 0.3);
    } else if (entity.kind === "core") {
      ctx.beginPath();
      for (let i = 0; i < 6; i++) {
        const a = (Math.PI * 2 * i) / 6;
        ctx.lineTo(Math.cos(a) * p.s * 0.22, Math.sin(a) * p.s * 0.22);
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.roundRect(-p.s * 0.16, -p.s * 0.23, p.s * 0.32, p.s * 0.42, 5);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "#e6a933";
      ctx.fillRect(-p.s * 0.07, -p.s * 0.3, p.s * 0.14, p.s * 0.08);
    }
    ctx.restore();
  }

  drawHazard(entity) {
    const ctx = this.ctx;
    const p = this.project(entity.x, entity.y, 0.35);
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(this.time * 2.7);
    ctx.fillStyle = entity.color;
    ctx.strokeStyle = "#190609";
    ctx.lineWidth = 3;
    ctx.beginPath();
    for (let i = 0; i < 8; i++) {
      const r = i % 2 === 0 ? p.s * 0.32 : p.s * 0.14;
      const a = (Math.PI * 2 * i) / 8;
      ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }

  drawFinishMarker(entity) {
    const ctx = this.ctx;
    const p = this.project(entity.x, entity.y, 0.4);
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.strokeStyle = "#162015";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, -p.s * 0.55);
    ctx.stroke();
    ctx.fillStyle = entity.color;
    ctx.beginPath();
    ctx.moveTo(0, -p.s * 0.55);
    ctx.lineTo(p.s * 0.36, -p.s * 0.43);
    ctx.lineTo(0, -p.s * 0.31);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  drawPlayer(player) {
    const ctx = this.ctx;
    const p = this.project(player.x, player.y, 0.42);
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.fillStyle = player.color;
    ctx.strokeStyle = "#071014";
    ctx.lineWidth = 3;
    if (player.kind === "rover") {
      ctx.beginPath();
      ctx.roundRect(-p.s * 0.3, -p.s * 0.18, p.s * 0.6, p.s * 0.32, 7);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "#222936";
      ctx.beginPath();
      ctx.arc(-p.s * 0.2, p.s * 0.16, p.s * 0.09, 0, Math.PI * 2);
      ctx.arc(p.s * 0.2, p.s * 0.16, p.s * 0.09, 0, Math.PI * 2);
      ctx.fill();
    } else if (player.kind === "runner") {
      ctx.beginPath();
      ctx.arc(0, -p.s * 0.2, p.s * 0.14, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.beginPath();
      ctx.roundRect(-p.s * 0.16, -p.s * 0.08, p.s * 0.32, p.s * 0.33, 6);
      ctx.fill();
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.roundRect(-p.s * 0.27, -p.s * 0.21, p.s * 0.54, p.s * 0.38, 8);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "#eef9fb";
      ctx.fillRect(-p.s * 0.12, -p.s * 0.31, p.s * 0.24, p.s * 0.12);
      ctx.fillStyle = "#101417";
      ctx.fillRect(-p.s * 0.16, p.s * 0.12, p.s * 0.11, p.s * 0.11);
      ctx.fillRect(p.s * 0.05, p.s * 0.12, p.s * 0.11, p.s * 0.11);
    }
    ctx.restore();
  }

  drawHud() {
    const ctx = this.ctx;
    const scale = Math.max(1, Math.min(1.25, this.canvas.width / 1280));
    ctx.save();
    ctx.fillStyle = "rgba(8, 11, 13, 0.76)";
    ctx.strokeStyle = "rgba(255, 255, 255, 0.16)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(24 * scale, 24 * scale, 380 * scale, 96 * scale, 8 * scale);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = "#f6f3ea";
    ctx.font = `${20 * scale}px system-ui`;
    ctx.fillText(`${this.scene.id}: ${this.scene.title}`, 42 * scale, 58 * scale);
    ctx.font = `${15 * scale}px system-ui`;
    ctx.fillText(`Items ${this.collected}/${this.scene.targetCount} | ${this.scene.finishLabel}`, 42 * scale, 87 * scale);
    if (this.message) ctx.fillText(this.message, 42 * scale, 112 * scale);
    if (this.won) {
      ctx.fillStyle = "rgba(7, 13, 10, 0.86)";
      const w = this.canvas.width * 0.36;
      const h = 88 * scale;
      const x = (this.canvas.width - w) / 2;
      const y = this.canvas.height * 0.42;
      ctx.beginPath();
      ctx.roundRect(x, y, w, h, 8 * scale);
      ctx.fill();
      ctx.fillStyle = "#b6f5ca";
      ctx.font = `${26 * scale}px system-ui`;
      ctx.textAlign = "center";
      ctx.fillText("Playable loop complete", this.canvas.width / 2, y + 54 * scale);
      ctx.textAlign = "left";
    }
    ctx.restore();
  }

  setStatus() {
    if (!this.scene) return;
    const pickupTotal = this.scene.entities.filter((entity) => entity.type === "pickup").length;
    const status = {
      experiment: "GAME-E3",
      benchmarkId: this.scene.id,
      prompt: this.scene.prompt,
      title: this.scene.title,
      entityCount: this.scene.entities.length,
      pickupTotal,
      collected: this.collected,
      won: this.won,
      proceduralAssets: true,
      externalAssets: 0,
      status: this.won ? "complete" : "running"
    };
    window.__GAME_E3_STATUS__ = status;
    this.hud.textContent = JSON.stringify(status);
  }
}
