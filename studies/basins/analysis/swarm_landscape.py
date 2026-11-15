"""Swarm map as a landscape (laptop): one self-contained HTML page from swarm_analyze.py outputs.

The judge's groups are drawn as basins of one 3D surface (WebGL 2, no library). A basin gets deeper with every board
item in it, so the replay shows the surface forming. Each possible direction stands as a pin beside its basin until
a board item works on it.

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

WH, DMIN, SHRINK, RMAX, RIM = 0.8, 0.245, 0.45, 0.062, 0.125

SHORT = {  # names shown on the picture; the panel shows the judge's full name
    "Prompt and reasoning protocols": "Prompt protocols", "Sampling and decoding controls": "Sampling and decoding",
    "Multiattempt search and budget allocation": "Multi-attempt search", "Weight and neuron interventions": "Weight and neuron edits",
    "Mechanistic readouts and trajectory analysis": "Mechanistic readouts", "Grading and dataset validation": "Grading and data checks",
    "Benchmark and checkpoint comparisons": "Benchmarks and checkpoints", "Experiment infrastructure and board tooling": "Infrastructure and tooling",
    "Research coordination and process evaluation": "Coordination and process"}

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
        "basins": [{"b": b, "name": M["names"][b], "short": SHORT.get(M["names"][b], M["names"][b]), "x": cen[b][0], "y": cen[b][1], "best": best.get(b)} for b in ids],
        "items": items, "dirs": dirs, "rl": S["rl_reference_pct"], "base": S["best_base_one_sample_pct"],
        "tste": S["tste_heldout_acc"], "null": S["tste_shuffled_id_null"], "order": S["triplet_order_consistency"]}

PAGE = r"""<title>Basin Atlas Landscape</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* layout: one dark room and one lit surface that fills it. One sentence top left. Detail opens on the right only when asked.
   One look, dark, by choice: the surface is a light source and needs a dark room. */
:root{
  --bg:#04070b; --ink:#eaf0f4; --mute:#8b98a5; --faint:#5b6773; --rule:rgba(255,255,255,.11);
  --blue:#9db9ff; --amber:#ffb057; color-scheme:dark;
  --font:"Archivo",ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif;
  --gl:max(28px,env(safe-area-inset-left,0px)); --gr:max(28px,env(safe-area-inset-right,0px));
}
*{box-sizing:border-box}
html,body{height:100%}
body{background:var(--bg);color:var(--ink);font:400 15px/1.5 var(--font);font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased;position:relative;overflow:hidden}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer;text-align:left}
:focus-visible{outline:2px solid var(--blue);outline-offset:3px;border-radius:3px}
canvas{position:absolute;inset:0;width:100%;height:100%;display:block}
#gl{touch-action:none;cursor:grab}
#ov,#labs{pointer-events:none}
#labs{position:absolute;inset:0;overflow:hidden}
.lab{position:absolute;left:0;top:0;pointer-events:auto;white-space:nowrap;font-size:12.5px;font-weight:500;letter-spacing:.01em;color:var(--ink);padding:4px 6px;
  text-shadow:0 0 6px var(--bg),0 0 12px var(--bg);transition:opacity .5s,color .3s;will-change:transform}
.lab i{font-style:normal;color:var(--mute);margin-left:7px;font-weight:400}
.lab:hover,.lab.on{color:var(--blue)}
#pin{position:absolute;left:0;top:0;white-space:nowrap;font-size:12.5px;font-weight:560;color:var(--amber);text-shadow:0 0 6px var(--bg),0 0 12px var(--bg);transition:opacity .6s;opacity:0;will-change:transform}
.top{position:absolute;left:0;right:0;top:0;display:flex;justify-content:space-between;align-items:baseline;gap:16px;padding-block:22px 0;padding-left:var(--gl);padding-right:var(--gr);font-size:13px;color:var(--mute);pointer-events:none}
.top>*{pointer-events:auto}
.name{font-weight:740;font-stretch:122%;font-size:15px;letter-spacing:.02em;color:var(--ink)}
.top button{color:var(--mute);margin-left:18px}
.top button:hover{color:var(--ink)}
.words{position:absolute;left:0;top:74px;padding-left:var(--gl);padding-right:16px;max-width:min(520px,100%);pointer-events:none}
h1{font-weight:300;font-size:clamp(30px,3.5vw,54px);line-height:1.08;letter-spacing:-.022em;margin:0;text-wrap:balance}
h1 b{font-weight:300;color:var(--amber)}
.lede{color:var(--mute);margin:18px 0 0;max-width:36ch;font-size:14px;line-height:1.5;transition:opacity .4s}
body.open .lede{opacity:0}
.play{position:absolute;left:0;bottom:0;display:flex;align-items:center;gap:14px;padding-block:0 calc(22px + env(safe-area-inset-bottom,0px));padding-left:var(--gl);padding-right:16px;font-size:13px;color:var(--mute)}
.play button{font-weight:600;color:var(--ink);min-width:50px}
input[type=range]{-webkit-appearance:none;appearance:none;background:none;width:clamp(120px,16vw,220px);height:22px;margin:0;cursor:pointer}
input[type=range]::-webkit-slider-runnable-track{height:1px;background:rgba(255,255,255,.3)}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:9px;height:9px;border-radius:50%;background:var(--ink);margin-top:-4px}
input[type=range]::-moz-range-track{height:1px;background:rgba(255,255,255,.3)}
input[type=range]::-moz-range-thumb{width:9px;height:9px;border:0;border-radius:50%;background:var(--ink)}
#panel{position:absolute;right:0;top:0;bottom:0;width:min(400px,100%);padding-block:70px 26px;padding-left:44px;padding-right:var(--gr);overflow-y:auto;scrollbar-width:thin;
  background:linear-gradient(to right,transparent,rgba(4,7,11,.9) 13%,var(--bg) 40%)}
#panel .x{color:var(--mute);font-size:13px;margin-bottom:22px}
#panel .x:hover{color:var(--ink)}
.tag{font-size:12px;font-weight:600;color:var(--amber);margin:0 0 4px}
h2{font-weight:400;font-size:25px;line-height:1.15;letter-spacing:-.01em;margin:0 0 8px;text-wrap:balance}
.sub{color:var(--mute);font-size:13.5px;margin:0 0 18px;max-width:40ch}
.sub+.sub{margin-top:-8px}
.item,.dirrow{display:block;width:100%;padding:10px 0;border-top:1px solid var(--rule);font-size:13px}
.item .meta{display:block;color:var(--faint);font-size:12px;margin-bottom:2px}
.item .tx{color:var(--mute);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere}
.item[aria-expanded="true"] .tx{display:block;color:var(--ink)}
.item:hover .tx{color:var(--ink)}
.dirrow{color:var(--amber)}
#nogl{position:absolute;inset:40% 0 auto;text-align:center;color:var(--mute)}
@media (max-width:820px){
  .words{top:60px}
  h1{font-size:27px}
  .lede{display:none}
  .lab{font-size:11px;padding:3px 4px}
  #panel{top:auto;left:0;width:100%;max-height:58%;padding-block:18px calc(20px + env(safe-area-inset-bottom,0px));padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));background:var(--bg);border-top:1px solid var(--rule)}
  body.open .play{display:none}
  :root{--gl:max(16px,env(safe-area-inset-left,0px));--gr:max(16px,env(safe-area-inset-right,0px))}
}
</style>
<canvas id="gl" aria-label="The team board as a landscape: each basin is a group of items with the same method"></canvas>
<canvas id="ov" aria-hidden="true"></canvas>
<div id="labs"><div id="pin"></div></div>
<header class="top"><span class="name">Basin atlas</span><span><span id="snap"></span><button id="method" type="button">Method</button></span></header>
<div class="words">
  <h1 id="h1"></h1>
  <p class="lede">Each light is an item on the team board. Items that use the same method fall into the same basin. An amber pin marks a direction nobody has worked on.</p>
</div>
<div class="play"><button id="play" type="button">Replay</button><input id="scrub" type="range" min="0" max="1" step="0.001" value="1" aria-label="Board time"><span id="clock"></span></div>
<aside id="panel" hidden></aside>
<p id="nogl" hidden>This page needs WebGL 2, which this browser does not offer.</p>
<script>
(() => {
"use strict";
const D = __DATA__, WH = D.wh, $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const items = D.items, N = items.length, basins = D.basins, dirs = D.dirs;
const byId = Object.fromEntries(items.map((n, i) => [n.id, i])), BZ = Object.fromEntries(basins.map(b => [b.b, b]));
items.forEach((n, i) => { n.u = i / (N - 1); n.w = 1; });
dirs.forEach(d => { d.first = Math.min(1e9, ...d.items.map(id => byId[id] ?? 1e9)); d.a = d.first > N ? 1 : 0; });
const untried = dirs.filter(d => d.first > N);
const cv = $("#gl"), gl = cv.getContext("webgl2", {antialias: true, alpha: false});
if (!gl) { $("#nogl").hidden = false; return; }

/* ---------- the surface: a fine grid of heights; every board item is a dent ---------- */
const CELL = 0.00625, GX0 = -0.4, GY0 = -0.4, NX = Math.round(1.8 / CELL) + 1, NY = Math.round((WH + 0.8) / CELL) + 1, SIG = 0.037, AMP = 0.12;
const DEN = new Float32Array(NX * NY), HB = new Float32Array(NX * NY * 3);
const kern = items.map(n => {
  const idx = [], val = [], r = 3.6 * SIG, cut = Math.exp(-3.6 * 3.6 / 2);
  for (let j = Math.floor((n.y - r - GY0) / CELL); j <= Math.ceil((n.y + r - GY0) / CELL); j++)
    for (let i = Math.floor((n.x - r - GX0) / CELL); i <= Math.ceil((n.x + r - GX0) / CELL); i++) {
      const v = Math.exp(-((GX0 + i * CELL - n.x) ** 2 + (GY0 + j * CELL - n.y) ** 2) / (2 * SIG * SIG)) - cut;
      if (v > 0) { idx.push(j * NX + i); val.push(v); }
    }
  return {idx, val};
});
let DMAX = 0;
function heights() {
  DEN.fill(0);
  for (let k = 0; k < N; k++) { const w = items[k].w; if (w <= 0) continue; const {idx, val} = kern[k]; for (let q = 0; q < idx.length; q++) DEN[idx[q]] += w * val[q]; }
  if (!DMAX) for (let q = 0; q < DEN.length; q++) DMAX = Math.max(DMAX, DEN[q]);
  for (let q = 0; q < DEN.length; q++) { const t = DEN[q] / DMAX; HB[q * 3] = -AMP * 2 * t / (t + 1); }
  for (let j = 1; j < NY - 1; j++) for (let i = 1; i < NX - 1; i++) { const q = j * NX + i;
    HB[q * 3 + 1] = (HB[(q + 1) * 3] - HB[(q - 1) * 3]) / (2 * CELL); HB[q * 3 + 2] = (HB[(q + NX) * 3] - HB[(q - NX) * 3]) / (2 * CELL); }
}
function zAt(x, y) {
  const fx = (x - GX0) / CELL, fy = (y - GY0) / CELL, i = fx | 0, j = fy | 0, a = fx - i, b = fy - j, q = j * NX + i;
  return (HB[q * 3] * (1 - a) + HB[(q + 1) * 3] * a) * (1 - b) + (HB[(q + NX) * 3] * (1 - a) + HB[(q + NX + 1) * 3] * a) * b;
}

/* ---------- WebGL ---------- */
function shader(type, src) { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; }
function program(vs, fs) { const p = gl.createProgram(); gl.attachShader(p, shader(gl.VERTEX_SHADER, vs)); gl.attachShader(p, shader(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); return p; }
const surf = program(`#version 300 es
in vec2 aP; in vec3 aH; uniform mat4 uM; out vec3 vW; out vec3 vN;
void main(){ vW=vec3(aP,aH.x); vN=vec3(-aH.y,-aH.z,1.); gl_Position=uM*vec4(vW,1.); }`, `#version 300 es
precision highp float;
in vec3 vW; in vec3 vN; uniform vec3 uBg,uInk,uDeep,uEye; uniform float uAmp,uCell; uniform vec2 uC,uR; uniform vec3 uSel; out vec4 o;
float lines(vec2 g){ vec2 fw=fwidth(g); vec2 a=abs(fract(g-.5)-.5)/fw; return (1.-clamp(min(a.x,a.y),0.,1.))*(1.-smoothstep(.22,.5,max(fw.x,fw.y))); }
void main(){
  vec3 n=normalize(vN); float d=clamp(-vW.z/uAmp,0.,1.);
  vec3 L=normalize(vec3(-.62,.42,.40)); float lam=max(dot(n,L),0.);  /* one low light from the upper left */
  vec3 V=normalize(uEye-vW); float sp=pow(max(dot(n,normalize(L+V)),0.),48.);
  vec3 col=vec3(.050,.070,.105)*(.72+lam*lam*3.2);                       /* glass body: bright wall, shadowed wall */
  col+=vec3(.55,.68,1.)*sp*.30;
  col+=uDeep*pow(d,2.)*.16;                                           /* light from the floor of a deep basin */
  vec2 g=vW.xy/uCell; col+=mix(uInk,uDeep,.5)*lines(g)*(.05+.16*lam*lam)*(1.+d*2.);
  float fade=1.-smoothstep(.62,1.12,length((vW.xy-uC)/uR));
  col=mix(uBg,col,fade);
  col=mix(col,uBg,smoothstep(.115,.26,length(vW.xy-uSel.xy))*.72*uSel.z);
  o=vec4(max(col,0.),1.);
}`);
const dots = program(`#version 300 es
in vec3 aX; in vec3 aS; uniform mat4 uM; uniform float uPx,uMax; out vec2 vS;
void main(){ gl_Position=uM*vec4(aX,1.); gl_PointSize=clamp(aS.x*uPx/gl_Position.w,7.,uMax); vS=aS.yz; }`, `#version 300 es
precision highp float;
in vec2 vS; uniform vec3 uInk,uDeep; out vec4 o;
void main(){ float r=length(gl_PointCoord-.5)*2.; float a=(smoothstep(.27,.17,r)+exp(-r*r*5.5)*.42*(1.-smoothstep(.8,1.,r)))*vS.x; o=vec4(mix(uInk,uDeep,vS.y)*a,1.); }`);
const U = (p, n) => gl.getUniformLocation(p, n);
const pos = new Float32Array(NX * NY * 2);
for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) { pos[(j * NX + i) * 2] = GX0 + i * CELL; pos[(j * NX + i) * 2 + 1] = GY0 + j * CELL; }
const ind = new Uint32Array((NX - 1) * (NY - 1) * 6);
for (let j = 0, k = 0; j < NY - 1; j++) for (let i = 0; i < NX - 1; i++) { const q = j * NX + i; ind[k++] = q; ind[k++] = q + 1; ind[k++] = q + NX + 1; ind[k++] = q; ind[k++] = q + NX + 1; ind[k++] = q + NX; }
const vaoS = gl.createVertexArray(); gl.bindVertexArray(vaoS);
const bP = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bP); gl.bufferData(gl.ARRAY_BUFFER, pos, gl.STATIC_DRAW);
gl.enableVertexAttribArray(gl.getAttribLocation(surf, "aP")); gl.vertexAttribPointer(gl.getAttribLocation(surf, "aP"), 2, gl.FLOAT, false, 0, 0);
const bH = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bH); gl.bufferData(gl.ARRAY_BUFFER, HB, gl.DYNAMIC_DRAW);
gl.enableVertexAttribArray(gl.getAttribLocation(surf, "aH")); gl.vertexAttribPointer(gl.getAttribLocation(surf, "aH"), 3, gl.FLOAT, false, 0, 0);
gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, gl.createBuffer()); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, ind, gl.STATIC_DRAW);
const vaoD = gl.createVertexArray(); gl.bindVertexArray(vaoD);
const DB = new Float32Array(N * 6), bD = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bD); gl.bufferData(gl.ARRAY_BUFFER, DB, gl.DYNAMIC_DRAW);
gl.enableVertexAttribArray(gl.getAttribLocation(dots, "aX")); gl.vertexAttribPointer(gl.getAttribLocation(dots, "aX"), 3, gl.FLOAT, false, 24, 0);
gl.enableVertexAttribArray(gl.getAttribLocation(dots, "aS")); gl.vertexAttribPointer(gl.getAttribLocation(dots, "aS"), 3, gl.FLOAT, false, 24, 12);
gl.bindVertexArray(null);
const BG = [4 / 255, 7 / 255, 11 / 255], INK = [0.92, 0.94, 0.96], DEEP = [0.62, 0.73, 1.0];

/* ---------- camera ---------- */
const FOV = 0.5, persp = (asp) => { const t = 1 / Math.tan(FOV / 2), n = 0.05, f = 30, m = new Float32Array(16); m[0] = t / asp; m[5] = t; m[10] = (f + n) / (n - f); m[11] = -1; m[14] = 2 * f * n / (n - f); return m; };
function lookAt(e, c) { let zx = e[0] - c[0], zy = e[1] - c[1], zz = e[2] - c[2], l = Math.hypot(zx, zy, zz); zx /= l; zy /= l; zz /= l;
  let xx = -zy, xy = zx, xz = 0; l = Math.hypot(xx, xy); xx /= l; xy /= l;
  const yx = zy * xz - zz * xy, yy = zz * xx - zx * xz, yz = zx * xy - zy * xx;
  return new Float32Array([xx, yx, zx, 0, xy, yy, zy, 0, xz, yz, zz, 0, -(xx * e[0] + xy * e[1] + xz * e[2]), -(yx * e[0] + yy * e[1] + yz * e[2]), -(zx * e[0] + zy * e[1] + zz * e[2]), 1]); }
const mul = (a, b) => { const o = new Float32Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) o[c * 4 + r] = a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3]; return o; };
function matrix(c, yaw, pitch) {
  const e = [c.x + c.d * Math.sin(yaw) * Math.cos(pitch), c.y - c.d * Math.cos(yaw) * Math.cos(pitch), c.z + c.d * Math.sin(pitch)];
  EYE = e; const P = persp(W / H); P[8] = -c.ox; P[9] = -c.oy;   /* shifts the picture on screen without turning the camera */
  return mul(P, lookAt(e, [c.x, c.y, c.z]));
}
let W = 1, H = 1, DPR = 1, M = null, wide = true, EYE = [0, 0, 1];
const proj = (x, y, z, m = M) => { const w = m[3] * x + m[7] * y + m[11] * z + m[15]; return [((m[0] * x + m[4] * y + m[8] * z + m[12]) / w * 0.5 + 0.5) * W, (0.5 - (m[1] * x + m[5] * y + m[9] * z + m[13]) / w * 0.5) * H, w]; };
const PITCH = 0.97, cam = {x: 0.5, y: WH / 2, z: -0.03, d: 2, ox: 0, oy: 0}, goal = {...cam}, home = {...cam};
function fit() {
  wide = W > 820;
  const lim = wide ? [0.19, 0.93, 0.13, 0.9] : [0.03, 0.97, 0.26, 0.84];   /* left, right, top, bottom of the picture, as shares of the screen */
  let lo = 0.4, hi = 9; const c = {x: 0.5, y: WH / 2, z: -0.03, d: 2, ox: 0, oy: 0};
  const box = d => { c.d = d; const m = matrix(c, 0, PITCH); let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    for (const [x, y] of [[0.04, 0.05], [0.96, 0.05], [0.04, WH - 0.05], [0.96, WH - 0.05]]) { const p = proj(x, y, 0, m); x0 = Math.min(x0, p[0] / W); x1 = Math.max(x1, p[0] / W); y0 = Math.min(y0, p[1] / H); y1 = Math.max(y1, p[1] / H); }
    return [x0, x1, y0, y1]; };
  for (let k = 0; k < 28; k++) { const d = (lo + hi) / 2, b = box(d); (b[1] - b[0] <= lim[1] - lim[0] && b[3] - b[2] <= lim[3] - lim[2]) ? hi = d : lo = d; }
  const b = box(hi);
  home.d = hi; home.ox = ((lim[0] + lim[1]) - (b[0] + b[1])); home.oy = -((lim[2] + lim[3]) - (b[2] + b[3]));
  aim();
}
function aim() {
  if (sel.b == null) { Object.assign(goal, home); if ((sel.method || sel.dir) && wide) goal.ox = home.ox - 0.2; }
  else { const b = BZ[sel.b]; Object.assign(goal, {x: b.x, y: b.y, z: -AMP * 0.45, d: home.d * (wide ? 0.5 : 0.62), ox: wide ? -0.22 : 0, oy: wide ? -0.06 : 0.3}); }
}
const ov = $("#ov"), ctx = ov.getContext("2d");
function resize() {
  W = cv.clientWidth; H = cv.clientHeight; if (!W || !H) return; DPR = Math.min(2, devicePixelRatio || 1);
  for (const c of [cv, ov]) { c.width = Math.round(W * DPR); c.height = Math.round(H * DPR); }
  fit(); Object.assign(cam, goal); labs.forEach(l => l.w = 0);
}
new ResizeObserver(resize).observe(cv);

/* ---------- state ---------- */
let simU = 1, playing = false, zDirty = true, sel = {b: null, item: null, dir: null, method: false}, nActive = -1;
let lean = [0, 0], leanT = [0, 0], orbit = [0, 0], drag = null, tourAt = 0, tour = 0;
const labs = basins.map(b => { const el = document.createElement("button"); el.className = "lab"; el.type = "button"; el.innerHTML = `${esc(b.short)}<i></i>`; el.onclick = () => select({b: b.b}); $("#labs").appendChild(el); return {b, el, n: -1}; });
const pinEl = $("#pin");

function frame(now) {
  const dt = Math.min(0.05, (now - (frame.t || now)) / 1000); frame.t = now;
  if (playing) { simU = Math.min(1, simU + dt / 20); $("#scrub").value = simU; if (simU >= 1) setPlaying(false); }
  for (const n of items) { const tgt = n.u <= simU + 1e-9 ? 1 : 0; if (n.w !== tgt) { n.w = reduce ? tgt : tgt > n.w ? Math.min(1, n.w + dt / 0.9) : Math.max(0, n.w - dt / 0.25); zDirty = true; } }
  if (zDirty) { heights(); gl.bindBuffer(gl.ARRAY_BUFFER, bH); gl.bufferSubData(gl.ARRAY_BUFFER, 0, HB); zDirty = false; }
  readout();
  const k = Math.min(1, dt * 2.6); for (const f in cam) cam[f] += (goal[f] - cam[f]) * (reduce ? 1 : k);
  lean[0] += (leanT[0] - lean[0]) * Math.min(1, dt * 3); lean[1] += (leanT[1] - lean[1]) * Math.min(1, dt * 3);
  if (!drag) { orbit[0] *= 1 - Math.min(1, dt * 0.9); orbit[1] *= 1 - Math.min(1, dt * 0.9); }
  const t = reduce ? 0 : now / 1000;
  M = matrix(cam, 0.12 * Math.sin(t / 8) + 0.07 * lean[0] + orbit[0], PITCH + 0.03 * Math.sin(t / 12.5) + 0.04 * lean[1] + orbit[1]);

  gl.viewport(0, 0, cv.width, cv.height); gl.clearColor(BG[0], BG[1], BG[2], 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
  gl.enable(gl.DEPTH_TEST); gl.disable(gl.BLEND);
  gl.useProgram(surf); gl.uniformMatrix4fv(U(surf, "uM"), false, M);
  gl.uniform3fv(U(surf, "uEye"), EYE); gl.uniform3fv(U(surf, "uBg"), BG); gl.uniform3fv(U(surf, "uInk"), INK); gl.uniform3fv(U(surf, "uDeep"), DEEP);
  gl.uniform1f(U(surf, "uAmp"), AMP); gl.uniform1f(U(surf, "uCell"), 0.025); gl.uniform2f(U(surf, "uC"), 0.5, WH / 2); gl.uniform2f(U(surf, "uR"), 0.66, WH / 2 + 0.14);
  const sb = sel.b != null ? BZ[sel.b] : null; frame.dim = (frame.dim || 0) + ((sb ? 1 : 0) - (frame.dim || 0)) * k; if (sb) frame.sx = sb.x, frame.sy = sb.y;
  gl.uniform3f(U(surf, "uSel"), frame.sx || 0, frame.sy || 0, frame.dim);
  gl.bindVertexArray(vaoS); gl.drawElements(gl.TRIANGLES, ind.length, gl.UNSIGNED_INT, 0);

  /* board items: points of light; a new one falls in from above */
  let c = 0;
  for (const n of items) { if (n.w <= 0) continue;
    const z = zAt(n.x, n.y) + 0.004 + (1 - n.w) ** 2 * 0.42, dim = sel.b != null && sel.b !== n.b ? 0.16 : 1, on = sel.item === n.id, big = n.kind === "result";
    DB.set([n.x, n.y, z, (big ? 0.036 : 0.026) * (on ? 1.9 : 1 + (1 - n.w) * 1.4), (big ? 1 : 0.72) * dim * Math.min(1, n.w * 4), on ? 1 : (1 - n.w) * 0.9], c * 6); c++; }
  gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);
  gl.useProgram(dots); gl.uniformMatrix4fv(U(dots, "uM"), false, M); gl.uniform1f(U(dots, "uPx"), cv.height / 2 / Math.tan(FOV / 2)); gl.uniform1f(U(dots, "uMax"), 30 * DPR);
  gl.uniform3fv(U(dots, "uInk"), INK); gl.uniform3fv(U(dots, "uDeep"), DEEP);
  gl.bindVertexArray(vaoD); gl.bindBuffer(gl.ARRAY_BUFFER, bD); gl.bufferSubData(gl.ARRAY_BUFFER, 0, DB.subarray(0, c * 6)); gl.drawArrays(gl.POINTS, 0, c);

  /* pins: the directions nobody has worked on yet */
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.clearRect(0, 0, W, H);
  const act = Math.round(simU * (N - 1)), rest = simU >= 1 && !playing;
  if (rest && !sel.dir && !reduce && now - tourAt > 3400) { tourAt = now; tour = (tour + 1) % untried.length; }
  let named = null;
  for (const d of dirs) {
    const tgt = d.first <= act && items[d.first].w > 0.3 ? 0 : 1; d.a += (tgt - d.a) * (reduce ? 1 : Math.min(1, dt * 3)); if (d.a < 0.02) continue;
    const zs = zAt(d.x, d.y), p0 = proj(d.x, d.y, zs), p1 = proj(d.x, d.y, zs + 0.11 * d.a); d.sx = p1[0]; d.sy = p1[1];
    const hot = sel.dir ? sel.dir === d.id : rest && sel.b == null && untried[tour] === d, a = d.a * (sel.b != null && sel.b !== d.b ? 0.18 : 1) * (hot ? 1 : 0.8);
    const g = ctx.createLinearGradient(p0[0], p0[1], p1[0], p1[1]); g.addColorStop(0, "rgba(255,176,87,0)"); g.addColorStop(1, `rgba(255,176,87,${a})`);
    ctx.beginPath(); ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]); ctx.strokeStyle = g; ctx.lineWidth = hot ? 1.5 : 1; ctx.stroke();
    ctx.shadowColor = "rgba(255,176,87,.9)"; ctx.shadowBlur = hot ? 16 : 8; ctx.beginPath(); ctx.arc(p1[0], p1[1], hot ? 3.4 : 2.3, 0, 6.2832); ctx.fillStyle = `rgba(255,190,110,${a})`; ctx.fill(); ctx.shadowBlur = 0;
    if (hot) named = d;
  }
  if (named) { if (pinEl.textContent !== named.name) pinEl.textContent = named.name;
    const right = named.sx > W * (wide ? 0.72 : 0.5); pinEl.style.transform = `translate(${named.sx + (right ? -12 : 12)}px,${named.sy - 9}px)` + (right ? " translate(-100%,0)" : ""); }
  pinEl.style.opacity = named ? 1 : 0;

  /* names stand behind their basin, upright */
  for (const l of labs) { const p = proj(l.b.x, l.b.y - 0.082, 0);
    if (!l.w) l.w = l.el.offsetWidth; const x = Math.max(l.w / 2 + 6, Math.min(W - l.w / 2 - 6, p[0]));
    l.el.style.transform = `translate(${x.toFixed(1)}px,${p[1].toFixed(1)}px) translate(-50%,0)`;
    l.el.style.opacity = sel.b != null ? (sel.b === l.b.b ? 1 : 0.16) : l.n ? 0.92 : 0.3; }
  requestAnimationFrame(frame);
}

/* ---------- the words ---------- */
function readout() {
  const act = items.filter(n => n.u <= simU + 1e-9).length; if (act === nActive) return; nActive = act;
  const left = dirs.filter(d => d.first >= act).length;
  $("#h1").innerHTML = `Nobody has tried <b>${left}</b> of the ${dirs.length} possible directions.`;
  $("#clock").textContent = act ? `${items[act - 1].hm} UTC · ${act} items` : "";
  for (const l of labs) { const n = items.filter(x => x.b === l.b.b && x.u <= simU + 1e-9).length; if (n !== l.n) { l.n = n; l.el.lastChild.textContent = n || ""; } }
}
const panel = $("#panel");
function render() {
  labs.forEach(l => l.el.classList.toggle("on", sel.b === l.b.b));
  const open = sel.b != null || sel.dir || sel.method; panel.hidden = !open; document.body.classList.toggle("open", !!open);
  if (!open) return;
  let h = `<button class="x" type="button" data-x="1">Close</button>`;
  if (sel.method) h += `<h2>Method</h2><p class="sub">A judge model (${esc(D.judge)}) compared the methods of the board items three at a time and said which two are closer. A map fitted to its answers predicts ${Math.round(D.tste * 100)} % of held-out answers, against ${Math.round(D.null * 100)} % when the items are shuffled.</p><p class="sub">The judge's groups are the basins. A basin gets deeper with every item in it. Basin centres come from the map and are spread apart so the basins do not overlap.</p><p class="sub">Before it saw the board, the judge listed ${dirs.length} possible directions from the research direction alone. A pin marks each one that no board item has worked on.</p><p class="sub">Board of ${esc(D.day)}, ${N} items. Best base score ${D.base.toFixed(1)} %, RL ${D.rl.toFixed(1)} % on MATH-500.</p>`;
  else if (sel.dir && sel.b == null) { const d = dirs.find(x => x.id === sel.dir); h += `<p class="tag">Not tried</p><h2>${esc(d.name)}</h2><p class="sub">${esc(d.text)}</p><p class="sub">The judge placed it next to ${esc(BZ[d.b].name.toLowerCase())}.</p>`; }
  else { const b = BZ[sel.b], its = items.filter(n => n.b === b.b), ds = dirs.filter(d => d.b === b.b), un = ds.filter(d => d.first > N);
    h += `<h2>${esc(b.name)}</h2><p class="sub">${its.length} board items. ${ds.length ? `${ds.length - un.length} of its ${ds.length} possible directions tried.` : "The judge listed no possible direction here."}${b.best ? ` Best base score from this basin: ${b.best.toFixed(1)} % on MATH-500.` : ""}</p>` +
      un.map(d => `<button class="dirrow" type="button" data-dir="${d.id}">Not tried: ${esc(d.name.toLowerCase())}${sel.dir === d.id ? `<span class="sub" style="display:block;margin:4px 0 0">${esc(d.text)}</span>` : ""}</button>`).join("") +
      its.map(n => `<button class="item" type="button" data-item="${n.id}" aria-expanded="${sel.item === n.id}"><span class="meta">${n.hm} · ${n.kind === "knowledge" ? "note" : n.kind} · ${esc(n.who)}</span><span class="tx">${esc(n.text)}</span></button>`).join(""); }
  panel.innerHTML = h; const ex = panel.querySelector('[aria-expanded="true"]'); if (ex) ex.scrollIntoView({block: "nearest"});
}
function select(s, push = true) {
  sel = {b: null, item: null, dir: null, method: false, ...s};
  if (sel.item) sel.b = items[byId[sel.item]].b;
  render(); aim();
  const h = sel.method ? "method" : sel.item ? "item-" + sel.item : sel.dir ? sel.dir : sel.b != null ? "basin-" + sel.b : "";
  if (push && location.hash.slice(1) !== h) history.pushState(null, "", h ? "#" + h : location.pathname + location.search);
}
function fromHash() {
  const h = location.hash.slice(1);
  if (h === "method") select({method: true}, false);
  else if (h.startsWith("item-") && h.slice(5) in byId) select({item: h.slice(5)}, false);
  else if (h.startsWith("basin-") && BZ[+h.slice(6)]) select({b: +h.slice(6)}, false);
  else if (dirs.some(d => d.id === h)) select({dir: h}, false);
  else select({}, false);
}
panel.addEventListener("click", e => { const el = e.target.closest("button"); if (!el) return;
  if (el.dataset.x) select({}); else if (el.dataset.dir) select({b: sel.b, dir: sel.dir === el.dataset.dir ? null : el.dataset.dir});
  else if (el.dataset.item) select({b: sel.b, item: sel.item === el.dataset.item ? null : el.dataset.item}); });
$("#method").onclick = () => select(sel.method ? {} : {method: true});
cv.addEventListener("pointerdown", e => { drag = {x: e.clientX, y: e.clientY, o: [...orbit], moved: false}; cv.setPointerCapture(e.pointerId); cv.style.cursor = "grabbing"; });
cv.addEventListener("pointermove", e => {
  const r = cv.getBoundingClientRect(); leanT = [((e.clientX - r.left) / r.width - 0.5) * 2, ((e.clientY - r.top) / r.height - 0.5) * 2];
  if (drag) { const dx = e.clientX - drag.x, dy = e.clientY - drag.y; if (Math.hypot(dx, dy) > 5) drag.moved = true;
    if (drag.moved) { orbit[0] = Math.max(-1.3, Math.min(1.3, drag.o[0] - dx * 0.005)); orbit[1] = Math.max(-0.45, Math.min(0.5, drag.o[1] + dy * 0.004)); } } });
cv.addEventListener("pointerup", e => { const d = drag; drag = null; cv.style.cursor = "grab"; if (!d || d.moved) return;
  const r = cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top; let best = null, bd = 16;
  for (const p of dirs) if (p.a > 0.5) { const q = Math.hypot(p.sx - x, p.sy - y); if (q < bd) { bd = q; best = {dir: p.id}; } }
  if (!best) { bd = 11; for (const n of items) { if (n.w < 1 || (sel.b != null && sel.b !== n.b)) continue; const p = proj(n.x, n.y, zAt(n.x, n.y)), q = Math.hypot(p[0] - x, p[1] - y); if (q < bd) { bd = q; best = {item: n.id}; } } }
  if (!best) for (const b of basins) { const p = proj(b.x, b.y, zAt(b.x, b.y)), e2 = proj(b.x + 0.085, b.y, 0); if (Math.hypot(p[0] - x, p[1] - y) < Math.abs(e2[0] - p[0])) best = {b: b.b}; }
  select(best || {}); });
cv.addEventListener("pointerleave", () => { leanT = [0, 0]; });
addEventListener("keydown", e => { if (e.key === "Escape") select(sel.item || (sel.dir && sel.b != null) ? {b: sel.b} : {}); if (e.key === " " && e.target === document.body) { e.preventDefault(); $("#play").click(); } });
addEventListener("hashchange", fromHash); addEventListener("popstate", fromHash);
const playBtn = $("#play");
function setPlaying(p) { playing = p; playBtn.textContent = p ? "Pause" : simU >= 1 ? "Replay" : "Play"; }
playBtn.onclick = () => { if (playing) return setPlaying(false); if (simU >= 1) { simU = 0; items.forEach(n => n.w = 0); zDirty = true; } if (reduce) { simU = 1; $("#scrub").value = 1; return; } setPlaying(true); };
$("#scrub").oninput = e => { simU = +e.target.value; setPlaying(false); };
$("#snap").textContent = `Board of ${D.day}`;
heights(); resize(); fromHash(); requestAnimationFrame(frame);
if (!reduce && !location.hash) setTimeout(() => { if (simU >= 1 && !playing && sel.b == null && !sel.method) playBtn.click(); }, 1600);
})();
</script>
"""
out = d / "swarm_landscape.html"
out.write_text(PAGE.replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
print(out)
