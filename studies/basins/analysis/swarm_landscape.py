"""Swarm map as a landscape (laptop): one self-contained HTML page from swarm_analyze.py outputs.

The judge's groups are drawn as basins of one 3D surface. A basin gets deeper with every board item in it, so the
replay shows the surface forming. The judge's possible directions sit on the rim of their basin.

    python3 -m studies.basins.analysis.swarm_landscape studies/basins/results/swarm/<arm>-<nn> <judge model>
    # writes swarm_landscape.html there (holds teammates' board text: not committed)

Layout: basin centres are the centroids of the judge's t-STE map (each axis rank-scaled), pushed apart until no two
are closer than DMIN. An item keeps the direction of its offset from its basin's centroid, shrunk by SHRINK.
"""
import datetime
import json
import math
import pathlib
import sys

WH, DMIN, SHRINK, RMAX, RIM = 0.8, 0.245, 0.45, 0.062, 0.1

d = pathlib.Path(sys.argv[1])
S = json.loads((d / "summary.json").read_text())
M = json.loads((d / "map.json").read_text())
nodes = [n for n in M["nodes"] if not n.get("control_of")]


def scaled(vals, lo, hi):
    """Half rank, half linear, so the dense corner of the map opens up."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    rank = {i: k / (len(vals) - 1) for k, i in enumerate(order)}
    a, b = min(vals), max(vals)
    return [lo + (hi - lo) * (0.6 * rank[i] + 0.4 * (v - a) / (b - a)) for i, v in enumerate(vals)]


for n, x, y in zip(nodes, scaled([n["x"] for n in nodes], 0.14, 0.86), scaled([n["y"] for n in nodes], 0.16, WH - 0.16)):
    n["mx"], n["my"] = x, y
board = sorted((n for n in nodes if n["kind"] != "possible"), key=lambda n: n["at_ns"])
ids = sorted({n["basin"] for n in board})
orig = {b: (sum(n["mx"] for n in board if n["basin"] == b) / sum(n["basin"] == b for n in board),
            sum(n["my"] for n in board if n["basin"] == b) / sum(n["basin"] == b for n in board)) for b in ids}
cen = {b: list(orig[b]) for b in ids}
for _ in range(600):
    for i in ids:
        for j in ids:
            if i < j:
                dx, dy = cen[j][0] - cen[i][0], cen[j][1] - cen[i][1]
                dist = math.hypot(dx, dy) or 1e-6
                if dist < DMIN:
                    push = (DMIN - dist) / 2 + 1e-3
                    for b, sgn in ((i, -1), (j, 1)):
                        cen[b][0] = min(0.83, max(0.17, cen[b][0] + sgn * push * dx / dist))
                        cen[b][1] = min(WH - 0.16, max(0.17, cen[b][1] + sgn * push * dy / dist))

items = []
for n in board:
    b = n["basin"]
    ox, oy = (n["mx"] - orig[b][0]) * SHRINK, (n["my"] - orig[b][1]) * SHRINK
    r = math.hypot(ox, oy)
    if r > RMAX:
        ox, oy = ox * RMAX / r, oy * RMAX / r
    at = datetime.datetime.fromtimestamp(n["at_ns"] / 1e9, datetime.timezone.utc)
    items.append({"id": n["id"], "kind": n["kind"], "who": (n["who"] or "").split("/")[0], "hm": at.strftime("%H:%M"),
                  "x": cen[b][0] + ox, "y": cen[b][1] + oy, "b": b, "text": n["text"]})
for _ in range(40):  # dots of one basin do not sit on each other
    for p in items:
        for q in items:
            if p is not q and p["b"] == q["b"]:
                dx, dy = q["x"] - p["x"], q["y"] - p["y"]
                dist = math.hypot(dx, dy) or 1e-6
                if dist < 0.017:
                    q["x"] += (0.017 - dist) / 2 * dx / dist
                    q["y"] += (0.017 - dist) / 2 * dy / dist

info = {x["id"]: x for x in S["directions"]}
dirs = []
for b in ids:
    ps = sorted((n for n in nodes if n["kind"] == "possible" and n["basin"] == b),
                key=lambda n: math.atan2(n["my"] - orig[b][1], n["mx"] - orig[b][0]))
    ang = [math.atan2(n["my"] - orig[b][1], n["mx"] - orig[b][0]) for n in ps]
    for k in range(1, len(ang)):
        ang[k] = max(ang[k], ang[k - 1] + 0.62)
    for n, a in zip(ps, ang):
        name, _, text = n["text"].partition(": ")
        dirs.append({"id": n["id"], "name": name[0] + name[1:].lower(),
                     "text": text, "b": b, "x": cen[b][0] + RIM * math.cos(a), "y": cen[b][1] + RIM * math.sin(a),
                     "items": info[n["id"]]["items_either"]})
best = {x["basin"]: x["best_base_pct"] for x in S["basins"]}
snap = datetime.datetime.fromtimestamp(board[-1]["at_ns"] / 1e9, datetime.timezone.utc)
data = {"wh": WH, "judge": sys.argv[2] if len(sys.argv) > 2 else "", "day": snap.strftime("%-d %B %Y"),
        "basins": [{"b": b, "name": M["names"][b], "x": cen[b][0], "y": cen[b][1], "best": best.get(b)} for b in ids],
        "items": items, "dirs": dirs, "rl": S["rl_reference_pct"], "base": S["best_base_one_sample_pct"],
        "tste": S["tste_heldout_acc"], "null": S["tste_shuffled_id_null"], "order": S["triplet_order_consistency"]}

PAGE = r"""<title>Basin Atlas Landscape</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* layout: one lit surface fills the screen; the words sit in one flat column on the left, with no boxes */
:root{
  --paper:#e9ecef; --ink:#101820; --mute:#56636d; --faint:#7a8791; --rule:#d0d6dc;
  --blue:#1f43d6; --amber:#b4560f;
  --surf-lo:#c9d0d7; --surf-hi:#ffffff; --wire:#8b98a4; --line:#3d4a57; --deep:#1f43d6; --glow:0;
  --font:"Archivo",ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#070b10; --ink:#e9eff3; --mute:#93a1ad; --faint:#6c7985; --rule:#1b2530;
  --blue:#8fb1ff; --amber:#ffb057;
  --surf-lo:#04070b; --surf-hi:#2c3f52; --wire:#6f88a0; --line:#aebccb; --deep:#8fb1ff; --glow:1; color-scheme:dark}}
:root[data-theme="dark"]{
  --paper:#070b10; --ink:#e9eff3; --mute:#93a1ad; --faint:#6c7985; --rule:#1b2530;
  --blue:#8fb1ff; --amber:#ffb057;
  --surf-lo:#04070b; --surf-hi:#2c3f52; --wire:#6f88a0; --line:#aebccb; --deep:#8fb1ff; --glow:1; color-scheme:dark}
*{box-sizing:border-box}
html,body{height:100%}
body{background:var(--paper);color:var(--ink);font:400 15px/1.5 var(--font);font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased;
  display:grid;grid-template-columns:minmax(300px,372px) minmax(0,1fr);overflow:hidden}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer;text-align:left}
:focus-visible{outline:2px solid var(--blue);outline-offset:3px;border-radius:3px}
.col{display:flex;flex-direction:column;min-height:0;min-width:0;padding-block:26px 22px;padding-left:max(28px,env(safe-area-inset-left,0px));padding-right:8px}
.top{display:flex;justify-content:space-between;align-items:baseline;gap:12px;font-size:13px;color:var(--mute)}
.name{font-weight:740;font-stretch:122%;font-size:15px;letter-spacing:.02em;color:var(--ink)}
h1{font-weight:300;font-size:clamp(27px,2.5vw,36px);line-height:1.14;letter-spacing:-.015em;margin:26px 0 0;text-wrap:balance}
h1 b{font-weight:560}
.lede{color:var(--mute);margin:14px 0 0;max-width:38ch;font-size:14px}
.body{flex:1;min-height:0;overflow-y:auto;margin-top:18px;padding-right:12px;scrollbar-width:thin}
.sec{font-size:12px;font-weight:620;color:var(--faint);padding:12px 0 6px;border-top:1px solid var(--rule)}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;width:100%;padding:5px 0;font-size:14px;align-items:baseline}
.row .n{color:var(--mute)}
.row:hover .t,.row[aria-current="true"] .t{color:var(--blue)}
.row.dir{grid-template-columns:20px minmax(0,1fr)}
.row.dir .k{color:var(--amber);font-weight:620}
.more{color:var(--mute);font-size:13px;margin:0 0 6px 20px;max-width:40ch}
.back{color:var(--mute);font-size:13px;padding:10px 0;border-top:1px solid var(--rule);width:100%}
.back:hover{color:var(--ink)}
h2{font-weight:560;font-size:20px;line-height:1.2;margin:2px 0 4px;text-wrap:balance}
.sub{color:var(--mute);font-size:13px;margin:0 0 12px}
.item{display:grid;grid-template-columns:14px minmax(0,1fr);gap:8px;width:100%;padding:8px 0;border-top:1px solid var(--rule);font-size:13px;align-items:start}
.item .meta{color:var(--faint);font-size:12px}
.item .tx{color:var(--mute);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere}
.item[aria-expanded="true"] .tx{display:block;color:var(--ink)}
.g{width:9px;height:9px;border-radius:50%;margin-top:5px;background:var(--ink)}
.g.work{background:none;border:1.5px solid var(--ink)}
.g.idea,.g.knowledge{width:5px;height:5px;margin:7px 2px 0}
.play{display:flex;align-items:center;gap:12px;padding-top:14px;border-top:1px solid var(--rule);font-size:13px;color:var(--mute);margin-right:20px}
.play button{font-weight:620;color:var(--ink);min-width:52px}
.play input{flex:1;min-width:0;accent-color:var(--blue);height:18px}
.play span{min-width:92px;text-align:right}
.foot{color:var(--faint);font-size:12px;margin:10px 20px 0 0;line-height:1.45}
.scene{position:relative;min-width:0;min-height:0}
canvas{position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:pan-y}
.key{position:absolute;left:18px;bottom:calc(20px + env(safe-area-inset-bottom,0px));right:max(18px,env(safe-area-inset-right,0px));display:flex;flex-wrap:wrap;gap:6px 20px;font-size:12px;color:var(--mute);pointer-events:none}
.key span{display:inline-flex;align-items:center;gap:7px}
.key i{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--ink)}
.key i.work{background:none;border:1.5px solid var(--ink)}
.key i.small{width:5px;height:5px}
.key i.dia{border-radius:0;background:none;border:1.5px solid var(--mute);transform:rotate(45deg);width:8px;height:8px}
.key i.dia.un{border-color:var(--amber)}
@media (max-width:820px){
  html,body{height:auto}
  body{display:flex;flex-direction:column-reverse;overflow:visible}
  .scene{height:62vh;min-height:360px}
  .col{padding-right:max(16px,env(safe-area-inset-right,0px));padding-left:max(16px,env(safe-area-inset-left,0px));padding-block:18px 28px}
  .body{overflow:visible;padding-right:0}
  h1{margin-top:18px}
  .play,.foot{margin-right:0}
}
</style>
<section class="col">
  <div class="top"><span class="name">Basin atlas</span><span id="snap"></span></div>
  <h1 id="h1"></h1>
  <p class="lede">Each dot is an item on the team board. A judge model grouped the items by method. Each group is a basin, and it gets deeper with every item.</p>
  <div class="body" id="body"></div>
  <div class="play"><button id="play" type="button">Replay</button><input id="scrub" type="range" min="0" max="1" step="0.001" value="1" aria-label="Board time"><span id="clock"></span></div>
  <p class="foot" id="foot"></p>
</section>
<section class="scene" id="scene">
  <canvas id="cv" aria-label="The board's items as a landscape of basins"></canvas>
  <div class="key"><span><i></i>Result</span><span><i class="work"></i>Open work</span><span><i class="small"></i>Idea or note</span><span><i class="dia"></i>Possible direction, tried</span><span><i class="dia un"></i>Not tried</span></div>
</section>
<script>
(() => {
"use strict";
const D = __DATA__, WH = D.wh, $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const items = D.items, N = items.length, basins = D.basins, dirs = D.dirs;
const byId = Object.fromEntries(items.map((n, i) => [n.id, i]));
const BZ = Object.fromEntries(basins.map(b => [b.b, b]));
items.forEach((n, i) => { n.u = i / (N - 1); n.w = 1; });
dirs.forEach(d => { d.first = Math.min(1e9, ...d.items.map(id => byId[id] ?? 1e9)); });
dirs.filter(d => d.first > N).forEach((d, k) => d.num = k + 1);

/* ---------- the surface: a grid of heights, each item a Gaussian dent ---------- */
const NX = 100, NY = Math.round(NX * WH) + 1, SIG = 0.037, AMP = 0.118;
const Z = new Float32Array(NX * NY), DEN = new Float32Array(NX * NY), PX = new Float32Array(NX * NY), PY = new Float32Array(NX * NY);
const gx = i => i / (NX - 1), gy = j => j / (NY - 1) * WH;
const kern = items.map(n => {
  const idx = [], val = [], r = 3.6 * SIG, cut = Math.exp(-3.6 * 3.6 / 2);
  for (let j = Math.max(0, Math.floor((n.y - r) / WH * (NY - 1))); j <= Math.min(NY - 1, Math.ceil((n.y + r) / WH * (NY - 1))); j++)
    for (let i = Math.max(0, Math.floor((n.x - r) * (NX - 1))); i <= Math.min(NX - 1, Math.ceil((n.x + r) * (NX - 1))); i++) {
      const v = Math.exp(-((gx(i) - n.x) ** 2 + (gy(j) - n.y) ** 2) / (2 * SIG * SIG)) - cut;
      if (v > 0) { idx.push(j * NX + i); val.push(v); }
    }
  return {idx, val};
});
let DMAX = 0;
function heights() {
  DEN.fill(0);
  for (let k = 0; k < N; k++) { const w = items[k].w; if (w <= 0) continue; const {idx, val} = kern[k]; for (let q = 0; q < idx.length; q++) DEN[idx[q]] += w * val[q]; }
  if (!DMAX) for (let q = 0; q < DEN.length; q++) DMAX = Math.max(DMAX, DEN[q]);
  for (let q = 0; q < DEN.length; q++) { const t = DEN[q] / DMAX; Z[q] = -AMP * 2 * t / (t + 1); }
}
function zAt(x, y) {
  const fx = Math.min(NX - 1.001, Math.max(0, x * (NX - 1))), fy = Math.min(NY - 1.001, Math.max(0, y / WH * (NY - 1)));
  const i = fx | 0, j = fy | 0, a = fx - i, b = fy - j, q = j * NX + i;
  return (Z[q] * (1 - a) + Z[q + 1] * a) * (1 - b) + (Z[q + NX] * (1 - a) + Z[q + NX + 1] * a) * b;
}

/* ---------- colors, read from the tokens so both themes work ---------- */
let C = {};
const hex = h => { h = h.trim().replace("#", ""); if (h.length === 3) h = [...h].map(c => c + c).join(""); return [0, 2, 4].map(k => parseInt(h.slice(k, k + 2), 16)); };
const mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const rgb = (c, a = 1) => a >= 1 ? `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})` : `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a.toFixed(3)})`;
const NQ = (NX - 1) * (NY - 1), fillC = new Array(NQ), wireC = new Array(NQ), edge = new Float32Array(NQ), NLV = 13, lvC = [];
for (let j = 0; j < NY - 1; j++) for (let i = 0; i < NX - 1; i++) {
  const ex = Math.min(gx(i + .5), 1 - gx(i + .5)) / 0.1, ey = Math.min(gy(j + .5), WH - gy(j + .5)) / 0.11;
  const e = Math.max(0, Math.min(1, Math.min(ex, ey))); edge[j * (NX - 1) + i] = 1 - e * e * (3 - 2 * e);
}
function readTheme() {
  const cs = getComputedStyle(document.documentElement), g = k => hex(cs.getPropertyValue(k));
  C = {paper: g("--paper"), ink: g("--ink"), mute: g("--mute"), blue: g("--blue"), amber: g("--amber"), lo: g("--surf-lo"), hi: g("--surf-hi"),
       wire: g("--wire"), line: g("--line"), deep: g("--deep"), glow: +cs.getPropertyValue("--glow")};
  for (let l = 0; l < NLV; l++) lvC[l] = rgb(mix(C.line, C.deep, Math.min(1, l / 6)), 0.22 + 0.6 * Math.min(1, l / 7));
  shadeDirty = true;
}
const LX = -0.52, LY = -0.58, LZ = 0.63, L0 = LZ / Math.hypot(LX, LY, LZ);
function shade() {
  const dx = 1 / (NX - 1), dy = WH / (NY - 1);
  for (let j = 0; j < NY - 1; j++) for (let i = 0; i < NX - 1; i++) {
    const q = j * (NX - 1) + i, v = j * NX + i;
    const sx = (Z[v + 1] + Z[v + NX + 1] - Z[v] - Z[v + NX]) / (2 * dx), sy = (Z[v + NX] + Z[v + NX + 1] - Z[v] - Z[v + 1]) / (2 * dy);
    const lam = (-sx * LX - sy * LY + LZ) / Math.hypot(sx, sy, 1) / Math.hypot(LX, LY, LZ);
    const s = Math.max(0, Math.min(1, 0.4 + (lam - L0) * 2.2));
    const dep = Math.min(1, -(Z[v] + Z[v + NX + 1]) / 2 / AMP);
    let c = mix(mix(C.lo, C.hi, s), C.deep, dep * (C.glow ? 0.16 : 0.2));
    c = mix(c, C.paper, edge[q]);
    fillC[q] = rgb(c); wireC[q] = rgb(mix(c, C.wire, (0.2 + 0.25 * dep) * (1 - edge[q])));
  }
}

/* ---------- camera: our own projection, seen from slightly above ---------- */
const cv = $("#cv"), ctx = cv.getContext("2d");
let W = 0, H = 0, DPR = 1, SC = 1, OX = 0, OY = 0, yaw = 0, pitch = 0.92, cyw = 1, syw = 0, sp = 0, cp = 0;
const FD = 2.6;
function proj(x, y, z) {
  const X = x - 0.5, Y = y - WH / 2, xr = X * cyw - Y * syw, yr = X * syw + Y * cyw, s = FD / (FD - (yr * cp + z * sp));
  return [OX + xr * s * SC, OY + (yr * sp - z * cp) * s * SC, s];
}
function resize() {
  const r = cv.getBoundingClientRect(); if (!r.width) return;
  DPR = Math.min(2, devicePixelRatio || 1); W = r.width; H = r.height;
  cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
  SC = Math.min(W / 1.04, H / 0.86); OX = W / 2; OY = H * 0.5;
}
new ResizeObserver(resize).observe(cv);

/* ---------- state ---------- */
let simU = 1, playing = false, zDirty = true, shadeDirty = true, sel = {b: null, item: null, dir: null}, lean = [0, 0], leanT = [0, 0];
let nActive = -1, hits = [];
const glowSprite = (() => { const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d"), r = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  r.addColorStop(0, "rgba(255,255,255,.9)"); r.addColorStop(.25, "rgba(255,255,255,.32)"); r.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = r; g.fillRect(0, 0, 128, 128); return c; })();

function step(dt) {
  let moved = false;
  for (const n of items) {
    const tgt = n.u <= simU + 1e-9 ? 1 : 0;
    if (n.w !== tgt) { n.w = reduce ? tgt : tgt > n.w ? Math.min(1, n.w + dt / 0.85) : Math.max(0, n.w - dt / 0.25); moved = true; }
  }
  if (moved) zDirty = true;
}

function frame(now) {
  const dt = Math.min(0.05, (now - (frame.t || now)) / 1000); frame.t = now;
  if (playing) { simU = Math.min(1, simU + dt / 20); $("#scrub").value = simU; if (simU >= 1) setPlaying(false); }
  step(dt);
  if (zDirty) { heights(); shadeDirty = true; zDirty = false; }
  if (shadeDirty) { shade(); shadeDirty = false; }
  readout();
  if (!W) { requestAnimationFrame(frame); return; }
  lean[0] += (leanT[0] - lean[0]) * Math.min(1, dt * 3); lean[1] += (leanT[1] - lean[1]) * Math.min(1, dt * 3);
  const sway = reduce ? 0 : now / 1000;
  yaw = 0.11 * Math.sin(sway / 7.5) + 0.1 * lean[0]; pitch = 0.99 + 0.025 * Math.sin(sway / 11) + 0.05 * lean[1];
  cyw = Math.cos(yaw); syw = Math.sin(yaw); sp = Math.sin(pitch); cp = Math.cos(pitch);
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.clearRect(0, 0, W, H);
  for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) { const v = j * NX + i, p = proj(gx(i), gy(j), Z[v]); PX[v] = p[0]; PY[v] = p[1]; }

  /* surface, far row first; each row's contour lines are drawn before the nearer rows cover them */
  ctx.lineJoin = "round"; ctx.lineWidth = 0.6;
  const stepZ = AMP / NLV;
  for (let j = 0; j < NY - 1; j++) {
    for (let i = 0; i < NX - 1; i++) {
      const q = j * (NX - 1) + i; if (edge[q] > 0.985) continue;
      const v = j * NX + i;
      ctx.fillStyle = fillC[q]; ctx.strokeStyle = wireC[q];
      ctx.beginPath(); ctx.moveTo(PX[v], PY[v]); ctx.lineTo(PX[v + 1], PY[v + 1]); ctx.lineTo(PX[v + NX + 1], PY[v + NX + 1]); ctx.lineTo(PX[v + NX], PY[v + NX]); ctx.closePath();
      ctx.fill(); ctx.stroke();
    }
    let lo = 0;
    for (let i = 0; i < NX; i++) lo = Math.min(lo, Z[j * NX + i], Z[(j + 1) * NX + i]);
    const deepest = Math.min(NLV - 1, Math.floor(-lo / stepZ - 0.5));
    for (let l = 0; l <= deepest; l++) {
      const L = -(l + 0.5) * stepZ; let any = false;
      ctx.beginPath();
      for (let i = 0; i < NX - 1; i++) {
        const v = j * NX + i, a = Z[v], b = Z[v + 1], c = Z[v + NX + 1], d = Z[v + NX];
        const m = (a > L ? 8 : 0) | (b > L ? 4 : 0) | (c > L ? 2 : 0) | (d > L ? 1 : 0);
        if (m === 0 || m === 15) continue; any = true;
        const E = (p, q, zp, zq) => { const t = (L - zp) / (zq - zp); return [PX[p] + (PX[q] - PX[p]) * t, PY[p] + (PY[q] - PY[p]) * t]; };
        const T = () => E(v, v + 1, a, b), R = () => E(v + 1, v + NX + 1, b, c), B = () => E(v + NX, v + NX + 1, d, c), Lf = () => E(v, v + NX, a, d);
        const seg = (p, q) => { ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]); };
        switch (m) {
          case 1: case 14: seg(Lf(), B()); break; case 2: case 13: seg(B(), R()); break; case 3: case 12: seg(Lf(), R()); break;
          case 4: case 11: seg(T(), R()); break; case 6: case 9: seg(T(), B()); break; case 7: case 8: seg(Lf(), T()); break;
          case 5: seg(Lf(), T()); seg(B(), R()); break; case 10: seg(Lf(), B()); seg(T(), R()); break;
        }
      }
      if (any) { ctx.strokeStyle = lvC[l]; ctx.lineWidth = 0.7 + 0.5 * Math.min(1, l / 8); ctx.stroke(); ctx.lineWidth = 0.6; }
    }
  }

  hits = [];
  const dimB = b => sel.b != null && sel.b !== b;
  /* light at the bottom of each basin (dark theme) */
  if (C.glow) { ctx.globalCompositeOperation = "lighter";
    for (const b of basins) { const z = zAt(b.x, b.y), dep = -z / AMP; if (dep < 0.05) continue; const p = proj(b.x, b.y, z), r = SC * 0.13 * p[2];
      ctx.globalAlpha = (dimB(b.b) ? 0.05 : 0.2) * dep; ctx.drawImage(glowSprite, p[0] - r, p[1] - r * sp, 2 * r, 2 * r * sp); }
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over"; }
  /* ring around the selected basin, drawn on the surface */
  if (sel.b != null) { const b = BZ[sel.b]; ctx.beginPath();
    for (let k = 0; k <= 48; k++) { const a = k / 48 * 6.2832, x = b.x + 0.118 * Math.cos(a), y = b.y + 0.118 * Math.sin(a), p = proj(x, y, zAt(x, y)); k ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); }
    ctx.strokeStyle = rgb(C.blue, 0.9); ctx.lineWidth = 1.3; ctx.stroke(); }

  /* possible directions on the rims */
  for (const d of dirs) {
    const tried = d.first < N && items[d.first].w > 0.5, p = proj(d.x, d.y, zAt(d.x, d.y)), r = (tried ? 3.6 : 4.6) * p[2] * Math.max(0.75, SC / 900);
    const on = sel.dir === d.id, a = dimB(d.b) && !on ? 0.22 : 1;
    ctx.beginPath(); ctx.moveTo(p[0], p[1] - r * 0.86); ctx.lineTo(p[0] + r, p[1]); ctx.lineTo(p[0], p[1] + r * 0.86); ctx.lineTo(p[0] - r, p[1]); ctx.closePath();
    ctx.fillStyle = rgb(C.paper, a); ctx.fill();
    ctx.strokeStyle = tried ? rgb(C.mute, 0.8 * a) : rgb(C.amber, a); ctx.lineWidth = tried ? 1 : 1.6; ctx.stroke();
    if (!tried && d.num && simU >= 1) { ctx.font = `620 ${Math.round(11 * Math.max(0.9, p[2]))}px Archivo, sans-serif`; ctx.fillStyle = rgb(C.amber, a); ctx.textAlign = "left"; ctx.textBaseline = "middle"; ctx.fillText(d.num, p[0] + r + 4, p[1]); }
    if (on) { ctx.beginPath(); ctx.arc(p[0], p[1], r + 7, 0, 6.2832); ctx.strokeStyle = rgb(C.amber, 0.9); ctx.lineWidth = 1.2; ctx.stroke(); }
    hits.push({x: p[0], y: p[1], r: 13, dir: d.id});
  }

  /* board items: a dot falls in, the basin sinks, a ring runs out over the surface */
  const order = items.map((n, i) => i).sort((a, b) => items[a].y - items[b].y);
  for (const i of order) {
    const n = items[i]; if (n.w <= 0) continue;
    const zs = zAt(n.x, n.y), fall = (1 - n.w) ** 2 * 0.3, p = proj(n.x, n.y, zs + fall), k = p[2] * Math.max(0.75, SC / 900);
    const on = sel.item === n.id, a = (dimB(n.b) ? 0.2 : 1) * Math.min(1, n.w * 3);
    if (n.w < 1 && n.w > 0.55) { const t = (n.w - 0.55) / 0.45; ctx.beginPath();
      for (let q = 0; q <= 28; q++) { const an = q / 28 * 6.2832, x = n.x + 0.075 * t * Math.cos(an), y = n.y + 0.075 * t * Math.sin(an), pp = proj(x, y, zAt(x, y)); q ? ctx.lineTo(pp[0], pp[1]) : ctx.moveTo(pp[0], pp[1]); }
      ctx.strokeStyle = rgb(C.blue, 0.8 * (1 - t)); ctx.lineWidth = 1.2; ctx.stroke(); }
    const fresh = n.w < 1, col = fresh || on ? C.blue : C.ink, r = (n.kind === "result" ? 4.1 : n.kind === "work" ? 3.6 : 2.3) * k;
    if (C.glow) { ctx.globalCompositeOperation = "lighter"; ctx.globalAlpha = a * (fresh || on ? 0.85 : 0.3); const g = r * (fresh ? 7 : 4.2); ctx.drawImage(glowSprite, p[0] - g, p[1] - g, 2 * g, 2 * g); ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over"; }
    ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, 6.2832);
    if (n.kind === "work") { ctx.fillStyle = rgb(C.paper, a * 0.85); ctx.fill(); ctx.strokeStyle = rgb(col, a); ctx.lineWidth = 1.5; ctx.stroke(); }
    else { ctx.fillStyle = rgb(col, a); ctx.fill(); }
    if (on) { ctx.beginPath(); ctx.arc(p[0], p[1], r + 6, 0, 6.2832); ctx.strokeStyle = rgb(C.blue); ctx.lineWidth = 1.3; ctx.stroke(); }
    hits.push({x: p[0], y: p[1], r: 12, item: n.id});
  }

  /* names: upright, above their basin, on a hairline that ends at its floor */
  const fs = W > 520 ? Math.max(11, Math.min(14, SC / 62)) : 10.5, lh = fs * 1.22, labs = [];
  for (const b of basins) {
    const n = items.filter(x => x.b === b.b && x.w > 0.5).length, foot = proj(b.x, b.y - 0.092, zAt(b.x, b.y - 0.092)), top = proj(b.x, b.y - 0.118, 0.012);
    const cut = b.name.indexOf(" and "), lines = cut < 0 ? [b.name] : W > 520 ? [b.name.slice(0, cut), b.name.slice(cut + 1)] : [b.name.slice(0, cut)];
    ctx.font = `600 ${fs}px Archivo, sans-serif`; const w = Math.max(...lines.map(l => ctx.measureText(l).width), 40);
    labs.push({b, n, foot, lines, w, x: top[0], y: top[1], h: lines.length * lh + lh});
  }
  labs.sort((p, q) => p.y - q.y);
  for (let it = 0; it < 6; it++) for (let p = 0; p < labs.length; p++) for (let q = p + 1; q < labs.length; q++) {
    const A = labs[p], B = labs[q]; if (Math.abs(A.x - B.x) < (A.w + B.w) / 2 + 10 && B.y - B.h < A.y + 4) { const o = (A.y + 4 - (B.y - B.h)) / 2; A.y -= o; B.y += o; } }
  ctx.textAlign = "center"; ctx.textBaseline = "alphabetic";
  for (const l of labs) {
    const a = dimB(l.b.b) ? 0.25 : 1, x = Math.max(l.w / 2 + 6, Math.min(W - l.w / 2 - 6, l.x));
    ctx.beginPath(); ctx.moveTo(x, l.y + 5); ctx.lineTo(l.foot[0], l.foot[1]); ctx.strokeStyle = rgb(C.ink, 0.4 * a); ctx.lineWidth = 0.8; ctx.stroke();
    ctx.lineWidth = 5; ctx.strokeStyle = rgb(C.paper, 0.75 * a);
    ctx.font = `600 ${fs}px Archivo, sans-serif`; l.lines.forEach((t, k) => ctx.strokeText(t, x, l.y - l.h + lh * (k + 1)));
    ctx.font = `400 ${fs - 1}px Archivo, sans-serif`; ctx.strokeText(l.n === 1 ? "1 item" : l.n + " items", x, l.y);
    ctx.font = `600 ${fs}px Archivo, sans-serif`; ctx.fillStyle = rgb(sel.b === l.b.b ? C.blue : C.ink, a);
    l.lines.forEach((t, k) => ctx.fillText(t, x, l.y - l.h + lh * (k + 1)));
    ctx.font = `400 ${fs - 1}px Archivo, sans-serif`; ctx.fillStyle = rgb(C.mute, a);
    ctx.fillText(l.n === 1 ? "1 item" : l.n + " items", x, l.y);
    hits.push({x, y: l.y - l.h / 2, rw: l.w / 2 + 8, rh: l.h / 2 + 6, basin: l.b.b});
  }
  requestAnimationFrame(frame);
}

/* ---------- the words ---------- */
const body = $("#body");
function readout() {
  const act = items.filter(n => n.u <= simU + 1e-9).length; if (act === nActive) return; nActive = act;
  const tried = dirs.filter(d => d.first < act).length, last = items[Math.max(0, act - 1)];
  $("#h1").innerHTML = `The swarm has worked in <b>${tried} of ${dirs.length}</b> possible directions.`;
  $("#clock").textContent = `${last.hm} UTC · ${act} items`;
  body.querySelectorAll("[data-count]").forEach(el => { el.textContent = items.filter(n => n.b === +el.dataset.count && n.u <= simU + 1e-9).length; });
}
function render() {
  if (sel.b == null) {
    const un = dirs.filter(d => d.num);
    body.innerHTML = `<div class="sec">Possible directions nobody has tried</div>` + un.map(d =>
      `<button class="row dir" type="button" data-dir="${d.id}" aria-current="${sel.dir === d.id}"><span class="k">${d.num}</span><span class="t">${esc(d.name)}</span></button>` +
      (sel.dir === d.id ? `<p class="more">${esc(d.text)} The judge placed it in ${esc(BZ[d.b].name.toLowerCase())}.</p>` : "")).join("") +
      `<div class="sec" style="margin-top:12px">Basins</div>` + basins.slice().sort((a, b) => a.name.localeCompare(b.name)).map(b =>
      `<button class="row" type="button" data-b="${b.b}"><span class="t">${esc(b.name)}</span><span class="n" data-count="${b.b}"></span></button>`).join("");
  } else {
    const b = BZ[sel.b], its = items.filter(n => n.b === b.b), ds = dirs.filter(d => d.b === b.b);
    body.innerHTML = `<button class="back" type="button" data-home="1">All basins</button><h2>${esc(b.name)}</h2>` +
      `<p class="sub">${its.length} board items. ${ds.length ? `${ds.filter(d => !d.num).length} of its ${ds.length} possible directions tried.` : "The judge listed no possible direction here."}${b.best ? ` Best base score from this basin: ${b.best.toFixed(1)} % on MATH-500.` : ""}</p>` +
      ds.filter(d => d.num).map(d => `<button class="row dir" type="button" data-dir="${d.id}" aria-current="${sel.dir === d.id}"><span class="k">${d.num}</span><span class="t">${esc(d.name)}, not tried</span></button>` + (sel.dir === d.id ? `<p class="more">${esc(d.text)}</p>` : "")).join("") +
      its.map(n => `<button class="item" type="button" data-item="${n.id}" aria-expanded="${sel.item === n.id}"><span class="g ${n.kind}"></span><span><span class="meta">${n.hm} · ${n.kind === "knowledge" ? "note" : n.kind} · ${esc(n.who)}</span><span class="tx">${esc(n.text)}</span></span></button>`).join("");
    const open = body.querySelector('[aria-expanded="true"]'); if (open) open.scrollIntoView({block: "nearest"});
  }
  nActive = -1;
}
function select(s, push = true) {
  sel = {b: null, item: null, dir: null, ...s};
  if (sel.item) sel.b = items[byId[sel.item]].b;
  render();
  const h = sel.item ? "item-" + sel.item : sel.dir ? sel.dir : sel.b != null ? "basin-" + sel.b : "";
  if (push && location.hash.slice(1) !== h) history.pushState(null, "", h ? "#" + h : location.pathname + location.search);
}
function fromHash() {
  const h = location.hash.slice(1);
  if (h.startsWith("item-") && h.slice(5) in byId) select({item: h.slice(5)}, false);
  else if (h.startsWith("basin-") && BZ[+h.slice(6)]) select({b: +h.slice(6)}, false);
  else if (dirs.some(d => d.id === h)) select({dir: h, b: sel.b}, false);
  else select({}, false);
}
body.addEventListener("click", e => {
  const el = e.target.closest("button"); if (!el) return;
  if (el.dataset.home) select({});
  else if (el.dataset.b) select({b: +el.dataset.b});
  else if (el.dataset.dir) select({b: sel.b, dir: sel.dir === el.dataset.dir ? null : el.dataset.dir});
  else if (el.dataset.item) select({b: sel.b, item: sel.item === el.dataset.item ? null : el.dataset.item});
});
cv.addEventListener("click", e => {
  const r = cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top; let best = null, bd = 1e9;
  for (const h of hits) { if (h.basin != null) continue; const d = Math.hypot(h.x - x, h.y - y); if (d < h.r && d < bd) { bd = d; best = h; } }
  if (!best) best = hits.find(h => h.basin != null && Math.abs(h.x - x) < h.rw && Math.abs(h.y - y) < h.rh);
  if (!best) { let nb = null, nd = 1e9; for (const b of basins) { const p = proj(b.x, b.y, zAt(b.x, b.y)), d = Math.hypot(p[0] - x, p[1] - y); if (d < nd) { nd = d; nb = b; } } if (nd < SC * 0.075) best = {basin: nb.b}; }
  if (!best) select({}); else if (best.item) select({item: best.item}); else if (best.dir) select({b: dirs.find(d => d.id === best.dir).b, dir: best.dir}); else select({b: best.basin});
});
cv.addEventListener("pointermove", e => { const r = cv.getBoundingClientRect(); leanT = [((e.clientX - r.left) / r.width - 0.5) * 2, ((e.clientY - r.top) / r.height - 0.5) * 2];
  const x = e.clientX - r.left, y = e.clientY - r.top; cv.style.cursor = hits.some(h => h.basin != null ? Math.abs(h.x - x) < h.rw && Math.abs(h.y - y) < h.rh : Math.hypot(h.x - x, h.y - y) < h.r) ? "pointer" : "default"; });
cv.addEventListener("pointerleave", () => { leanT = [0, 0]; });
addEventListener("keydown", e => { if (e.key === "Escape") select(sel.item || sel.dir ? {b: sel.b} : {}); if (e.key === " " && e.target === document.body) { e.preventDefault(); $("#play").click(); } });
addEventListener("hashchange", fromHash); addEventListener("popstate", fromHash);

const playBtn = $("#play");
function setPlaying(p) { playing = p; playBtn.textContent = p ? "Pause" : simU >= 1 ? "Replay" : "Play"; }
playBtn.onclick = () => { if (playing) return setPlaying(false); if (simU >= 1) { simU = 0; items.forEach(n => n.w = 0); zDirty = true; } if (reduce) { simU = 1; $("#scrub").value = 1; return; } setPlaying(true); };
$("#scrub").oninput = e => { simU = +e.target.value; setPlaying(false); };

$("#snap").textContent = `Board on ${D.day}`;
$("#foot").textContent = `Judge ${D.judge}. Its map predicts ${Math.round(D.tste * 100)} % of held-out "which is closer" answers, against ${Math.round(D.null * 100)} % with shuffled items. Basin centres are spread apart so that basins do not overlap. Best base score ${D.base.toFixed(1)} %, RL ${D.rl.toFixed(1)} % on MATH-500.`;
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", readTheme);
new MutationObserver(readTheme).observe(document.documentElement, {attributes: true, attributeFilter: ["data-theme"]});
readTheme(); fromHash(); resize(); requestAnimationFrame(frame);
if (!reduce && !location.hash) setTimeout(() => { if (simU >= 1 && !playing && sel.b == null) playBtn.click(); }, 1400);
})();
</script>
"""
out = d / "swarm_landscape.html"
out.write_text(PAGE.replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
print(out)
