"""Ideas converge: the picture of the slide "ideas" of the talk deck (demo_deck.py), served at /demo/fig/converge.

One self-playing canvas, 1600 x 900 CSS px, the size of a slide. The glass slab of /proof/idea-basins in its basins
look (the same projection, relief and basins, proof_idea_basins.py) holds the board items as dots, each in its
basin. The idea tree grows over it in the order the items were posted: each item pops in, and from each earlier item
it builds on a lit head runs along an arc above the slab and leaves the arc behind. An arc inside one basin is low
and faint; an arc between two basins is tall and blue. A count under the slab adds up the links that have landed and
ends at the numbers of proof_idea_basins.DATA['tree']. Then the picture keeps replaying real links: a head runs along
one cross-basin link about every 0.3 s, and about every 4.5 s the links into one item whose parents lie in three or
more basins light together and land at once. After about 32 s the tree fades and grows again. The view sways slowly
all the time. With prefers-reduced-motion the page is one still frame of the finished tree.

Every number comes from proof_idea_basins.DATA; the tokens are those of demo.py (demo.LIGHT, demo.DARK), so the
paper matches the deck's, plus --wash of proof_idea_basins.py. The deck sets data-theme from outside; the page
watches it and reads its colors again.
"""
import json
import re

import demo
import proof_idea_basins

DATA = proof_idea_basins.DATA
LAYOUT = DATA["layout"]
ITEMS = LAYOUT["items"]

# The links of the idea tree, from the earlier item (parent) to the later one (child), and whether they join two
# basins. The page draws exactly these, so its final counts are these counts.
LINKS = [[p, i, int(ITEMS[p]["c"] != n["c"])] for i, n in enumerate(ITEMS) for p in n["p"]]
assert all(p < i for p, i, _ in LINKS), "a parent is posted after its child"
assert len(LINKS) == DATA["tree"]["links"], (len(LINKS), DATA["tree"])
assert sum(x for _, _, x in LINKS) == DATA["tree"]["cross"], DATA["tree"]

# The items whose parents lie in at least 3 different basins: the convergence bursts after the build, the most
# basins first, then in posting order.
_SPREAD = {i: len({ITEMS[p]["c"] for p in n["p"]}) for i, n in enumerate(ITEMS)}
BURSTS = sorted((i for i, k in _SPREAD.items() if k >= 3), key=lambda i: (-_SPREAD[i], i))
assert BURSTS, "no item builds on 3 basins"

# --wash (how strongly a basin takes the accent) is not among demo.py's tokens: take it from proof_idea_basins.py,
# the light value first. The other glass tokens are in demo.LIGHT and demo.DARK.
_WASH = re.findall(r"--wash: ([\d.]+);", proof_idea_basins.PAGE)
assert len(_WASH) == 2, "the --wash tokens of proof_idea_basins.py changed"
for _k in ("paper", "ink", "mute", "blue", "glass-hi", "glass", "glass-lo", "rim-a", "rim-b", "rim-c", "glow", "shadow", "spec", "bloom", "core"):
    assert f"--{_k}:" in demo.LIGHT and f"--{_k}:" in demo.DARK, f"demo.py lost the token --{_k}"
_LIGHT = demo.LIGHT + f" --wash: {_WASH[0]};"
_DARK = demo.DARK + f" --wash: {_WASH[1]};"
TOKENS = (':root {\n  color-scheme: light;\n  ' + _LIGHT + '\n}\n@media (prefers-color-scheme: dark) {\n'
          '  :root:not([data-theme="light"]) {\n    color-scheme: dark;\n    ' + _DARK + '\n  }\n}\n'
          ':root[data-theme="dark"] {\n  color-scheme: dark;\n  ' + _DARK + '\n}\n')

CONFIG = {
    "wh": LAYOUT["wh"], "s": LAYOUT["s"],
    "clusters": [{k: c[k] for k in ("name", "n", "x", "y", "r")} for c in LAYOUT["clusters"]],
    "items": [{"kind": n["kind"], "c": n["c"], "k": n["k"]} for n in ITEMS],
    "links": LINKS, "bursts": BURSTS, "tree": {"links": DATA["tree"]["links"], "cross": DATA["tree"]["cross"]},
}

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Ideas converge</title>
<script>
/* The theme before the first paint: ?theme=light|dark, else the system's. The deck sets data-theme later too. */
(() => { const t = new URLSearchParams(location.search).get("theme"); if (t === "light" || t === "dark") document.documentElement.dataset.theme = t; })();
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
__TOKENS__
html, body { margin: 0; height: 100%; overflow: hidden; background: var(--paper); }
body { font-family: "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif; }
canvas { display: block; width: 100vw; height: 100vh; }
</style>
</head>
<body>
<canvas id="c" role="img" aria-label="__LABEL__"></canvas>
<script>
"use strict";
const C = __CONFIG__;
const cv = document.getElementById("c"), ctx = cv.getContext("2d");
const W = 1600, H = 900, N = C.items.length, TAU = 2 * Math.PI;
const clamp = x => x < 0 ? 0 : x > 1 ? 1 : x, ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
const back = p => { const q = p - 1; return 1 + 2.70158 * q * q * q + 1.70158 * q * q; };  // overshoots a little, then settles
const fall = (dt, len) => dt >= 0 && dt < len ? (1 - dt / len) ** 2 : 0;  // a flash that starts at 1 and dies out over len s
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

/* Geometry: the slab of proof_idea_basins.py, scaled to this frame. x right, y down, z toward the viewer; the slab
   lies back by TILT degrees, u runs to its right, v toward the viewer and w out of its top face. */
const RAD = Math.PI / 180, TILT = 58, PC = Math.cos(TILT * RAD), PS = Math.sin(TILT * RAD);
const G = { cx: 800, cy: 470, a: 500, th: 25, r: 36, D: 2840, deep: 48, gx: 84, gy: 30, lw: 1.15, dot: 1.4, fs: 17 };
G.b = G.a * .92; G.unit = 2 * G.a / .88;  // one unit of the layout on the slab
const TOP = G.th / 2;
const SOFT = .32, RIM = SOFT * Math.exp(-.7);  // how far the ground around a basin slopes toward it, and how low its rim lies
const V = { c1: 1, s1: 0, c2: 1, s2: 0 };  // the view: yaw and pitch
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
let PX = 0, PY = 0, PK = 1, PZ = 0;  // the last projected point: screen x, y, scale and depth
function at(u, v, w) {  // world() then proj() of proof_idea_basins.py, without allocating
  const y0 = v * PC - w * PS, z0 = v * PS + w * PC;
  const x = u * V.c1 + z0 * V.s1, z1 = z0 * V.c1 - u * V.s1;
  const y = y0 * V.c2 - z1 * V.s2, z = z1 * V.c2 + y0 * V.s2, k = G.D / (G.D - z);
  PX = G.cx + x * k; PY = G.cy + y * k; PK = k; PZ = z;
}
function outline() {  // the rounded outline of the slab in its own plane, clockwise from the far right corner
  const pts = [], n = 6;
  [[1, -1, -90], [1, 1, 0], [-1, 1, 90], [-1, -1, 180]].forEach(([su, sv, a0]) => {
    for (let i = 0; i <= n; i++) { const a = (a0 + 90 * i / n) * RAD; pts.push([su * (G.a - G.r) + G.r * Math.cos(a), sv * (G.b - G.r) + G.r * Math.sin(a)]); }
  });
  return pts;
}
function hull(p) {  // the silhouette of a convex body is the convex hull of its projected points
  p = [...p].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const turn = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const half = list => { const out = []; for (const q of list) { while (out.length > 1 && turn(out[out.length - 2], out[out.length - 1], q) <= 0) out.pop(); out.push(q); } out.pop(); return out; };
  return [...half(p), ...half(p.reverse())];
}
const OUT = outline();

/* The basins: a bowl each, deepest at its centre, and the ground around it slopes gently toward it. */
const U = x => (x - .5) * G.unit, Vv = y => (y - C.wh / 2) * G.unit;
const MOST = Math.max(...C.clusters.map(c => c.n));
const RINGS = C.clusters.map(c => ({ u: U(c.x), v: Vv(c.y), R: c.r * G.unit, d: G.deep * Math.sqrt(c.n / MOST), s: C.s * G.unit }));
function depth(u, v) {
  let z = 0, soft = 0;
  for (const r of RINGS) { const q = ((u - r.u) ** 2 + (v - r.v) ** 2) / (r.R * r.R); if (q < 1) z = Math.min(z, -r.d * (1 - q)); soft -= SOFT * r.d * Math.exp(-.7 * q); }
  return z + soft;
}
// Each item lies in its basin, packed outward from the centre in posting order (inBowl of proof_idea_basins.py).
const DOTS = C.items.map(n => {
  const b = RINGS[n.c], r = b.s * Math.sqrt(n.k + .5), a = n.k * 2.39996323, u = b.u + r * Math.cos(a), v = b.v + r * Math.sin(a);
  return { kind: n.kind, c: n.c, u, v, w: TOP + depth(u, v) };
});
// The relief: lines across the slab, from the back to the front, that dip where a basin lies.
const LAND = (() => {
  const eu = G.a - G.r * .6, ev = G.b - G.r * .6;
  return Array.from({ length: G.gy }, (_, j) => {
    const v = -ev + 2 * ev * j / (G.gy - 1), us = Array.from({ length: G.gx }, (_, i) => -eu + 2 * eu * i / (G.gx - 1));
    return { v, us, zb: us.map(u => depth(u, v)) };
  });
})();

/* The timeline, in seconds from the start of a cycle: the slab comes in, then item i pops in at TI[i]; at that moment
   a head leaves each of its parents and lands on it dur seconds later. */
const INTRO = 1, BUILD = 8, IDLE = 32, FADE = 1, RUN_EVERY = .3, BURST_EVERY = 4.5;
const TI = C.items.map((n, i) => INTRO + BUILD * (i / (N - 1)) ** .75);
const LK = C.links.map(([p, c, x]) => {
  const P = DOTS[p], Q = DOTS[c], du = Q.u - P.u, dv = Q.v - P.v, dw = Q.w - P.w, dist = Math.hypot(du, dv);
  const h = x ? Math.max(24, Math.min(230, .4 * dist)) : Math.min(30, 6 + .22 * dist);
  const dur = .55 + .35 * clamp(dist / 700);
  return { p, c, x, P, du, dv, dw, h, n: Math.round(Math.max(8, Math.min(22, 8 + dist / 40))), dur, start: TI[c], land: TI[c] + dur };
});
const INTO = C.items.map(() => []);
LK.forEach((l, i) => INTO[l.c].push(i));
const CROSS = LK.map((l, i) => i).filter(i => LK[i].x);
const BUILD_END = Math.max(...LK.map(l => l.land)), IDLE0 = BUILD_END + .3, END = BUILD_END + IDLE;
if (LK.length !== C.tree.links || CROSS.length !== C.tree.cross) throw new Error("the page's counts differ from DATA['tree']");

function point(l, s) {  // a point of link l at s (0 at the parent, 1 at the child), lifted above the slab
  at(l.P.u + l.du * s, l.P.v + l.dv * s, l.P.w + l.dw * s + l.h * 4 * s * (1 - s));
}
function trace(path, l, s1) {  // the arc of link l from its parent to s1, into a path
  point(l, 0); path.moveTo(PX, PY);
  for (let i = 1; i <= l.n; i++) { point(l, s1 * i / l.n); path.lineTo(PX, PY); }
}

/* The colors, read from the CSS tokens once per theme change, never per frame. */
const probe = document.createElement("canvas").getContext("2d");
function rgbOf(s) {
  probe.fillStyle = "#010203"; probe.fillStyle = s;
  const v = probe.fillStyle;
  if (v === "#010203" && s.trim().toLowerCase() !== "#010203") throw new Error("not a color: " + s);
  if (v[0] === "#") return [parseInt(v.slice(1, 3), 16), parseInt(v.slice(3, 5), 16), parseInt(v.slice(5, 7), 16), 1];
  const m = v.match(/[\d.]+/g).map(Number);
  return [m[0], m[1], m[2], m.length > 3 ? m[3] : 1];
}
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${(c[3] * a).toFixed(3)})`;
let P = null;
const SPR = { head: document.createElement("canvas"), shine: document.createElement("canvas"), room: document.createElement("canvas") };
function theme() {
  const cs = getComputedStyle(document.documentElement);
  const col = k => rgbOf(cs.getPropertyValue("--" + k)), num = k => { const v = parseFloat(cs.getPropertyValue("--" + k)); if (!isFinite(v)) throw new Error("token --" + k); return v; };
  P = { ink: col("ink"), mute: col("mute"), blue: col("blue"), core: col("core"), glass: col("glass"), hi: col("glass-hi"), lo: col("glass-lo"),
        rimA: col("rim-a"), rimB: col("rim-b"), rimC: col("rim-c"), glow: num("glow"), shadow: num("shadow"), spec: num("spec"), bloom: num("bloom"), wash: num("wash") };
  P.dark = P.glow > .5;
  // The lit head: a white core (blue in light) inside a blue halo.
  let s = SPR.head; s.width = s.height = 128; let x = s.getContext("2d"), g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, rgba(P.core, 1)); g.addColorStop(.09, rgba(P.core, .95)); g.addColorStop(.2, rgba(P.blue, .55 * P.bloom + .1));
  g.addColorStop(.45, rgba(P.blue, .16 * P.bloom)); g.addColorStop(1, rgba(P.blue, 0));
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  // The shine on the glass, from the upper left (dark only, by --spec).
  s = SPR.shine; s.width = s.height = 64; x = s.getContext("2d"); g = x.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, "rgba(255,255,255,.2)"); g.addColorStop(1, "rgba(255,255,255,0)"); x.fillStyle = g; x.fillRect(0, 0, 64, 64);
  // The room: the glow around the slab (dark) or its cast shadow (light), drawn once at half size.
  s = SPR.room; s.width = W / 2; s.height = H / 2; x = s.getContext("2d"); x.scale(.5, .5);
  const blob = (cx, cy, rx, ry, stops) => {
    x.save(); x.translate(cx, cy); x.scale(rx, ry); const q = x.createRadialGradient(0, 0, 0, 0, 0, 1);
    stops.forEach(([o, c]) => q.addColorStop(o, c)); x.fillStyle = q; x.fillRect(-1, -1, 2, 2); x.restore();
  };
  if (P.glow > 0) blob(G.cx, G.cy + G.b * .08, G.a * 1.7, G.b * PC * 2.1, [[0, rgba(P.blue, .24 * .85 * P.glow)], [.42, rgba(P.blue, .24 * .85 * P.glow)], [.7, rgba(P.blue, .07 * .85 * P.glow)], [1, rgba(P.blue, 0)]]);
  if (P.shadow > 0) blob(G.cx + G.a * .07, G.cy + G.b * PC * .22 + G.th, G.a * 1.3, G.b * PC * 1.36, [[0, rgba(P.ink, .2 * P.shadow)], [.55, rgba(P.ink, .2 * P.shadow)], [1, rgba(P.ink, 0)]]);
  if (still) draw(FINAL_T, FINAL_LT);
}

/* The canvas: drawn in 1600 x 900 units, fitted to the window, its backing store at least twice the CSS size. */
let FIT = { k: 1, ox: 0, oy: 0, br: 2 };
function resize() {
  const iw = innerWidth, ih = innerHeight, br = Math.max(2, devicePixelRatio || 1), k = Math.min(iw / W, ih / H);
  FIT = { k, ox: (iw - W * k) / 2, oy: (ih - H * k) / 2, br };
  cv.width = Math.round(iw * br); cv.height = Math.round(ih * br);
  if (still && P) draw(FINAL_T, FINAL_LT);
}

/* Fonts: no text is drawn before Archivo is loaded. */
let fontsAt = Infinity;
const NAME_FONT = '560 17px "Archivo", ui-sans-serif, system-ui, sans-serif', NUM_FONT = '330 84px "Archivo", ui-sans-serif, system-ui, sans-serif', CAP_FONT = '500 20px "Archivo", ui-sans-serif, system-ui, sans-serif';

/* What runs after the build: heads along single cross-basin links, and convergence bursts. */
const S = { T0: 0, first: true, runs: [], nextRun: IDLE0, bursts: [], nextBurst: IDLE0 + .8, bi: 0 };
function restart(t) {
  S.T0 = t - INTRO; S.first = false; S.runs = []; S.bursts = []; S.nextRun = IDLE0; S.nextBurst = IDLE0 + .8;
}
function schedule(lt) {
  if (lt >= IDLE0 && lt < END) {
    while (S.nextRun <= lt) { S.runs.push({ li: CROSS[Math.floor(Math.random() * CROSS.length)], t0: S.nextRun }); S.nextRun += RUN_EVERY * (.6 + .8 * Math.random()); }
    while (S.nextBurst <= lt) {
      const it = C.bursts[S.bi++ % C.bursts.length], ins = INTO[it], arr = S.nextBurst + .15 + Math.max(...ins.map(i => LK[i].dur));
      S.bursts.push({ it, T: S.nextBurst, arr, ins }); S.nextBurst += BURST_EVERY;
    }
  }
  S.runs = S.runs.filter(r => lt < r.t0 + LK[r.li].dur + .5);
  S.bursts = S.bursts.filter(b => lt < b.arr + 1.9);
}
const dimOf = (b, lt) => clamp((lt - b.T) / .25) * clamp((b.arr + .55 - lt) / .4);  // how strongly a burst dims the other arcs

/* One frame. t: seconds since load (the camera and the entrance); lt: seconds since the start of this cycle. */
function draw(t, lt) {
  const c = ctx, k = FIT.k * FIT.br;
  c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, cv.width, cv.height);
  c.setTransform(k, 0, 0, k, FIT.ox * FIT.br, FIT.oy * FIT.br);
  c.lineCap = "round"; c.lineJoin = "round";
  const aBody = ease(clamp(t / .9)), aLand = ease(clamp((t - .2) / .9)), aRim = clamp((t - .3) / .9), aName = ease(clamp((t - Math.max(.4, fontsAt)) / .8));
  const fade = 1 - clamp((lt - END) / FADE);

  // The room, the body of the slab, its top face and the shine.
  c.globalAlpha = aBody; c.drawImage(SPR.room, 0, 0, W, H);
  const up = OUT.map(([u, v]) => { at(u, v, TOP); return [PX, PY]; }), down = OUT.map(([u, v]) => { at(u, v, -TOP); return [PX, PY]; });
  const poly = pts => { const p = new Path2D(); pts.forEach((q, i) => i ? p.lineTo(q[0], q[1]) : p.moveTo(q[0], q[1])); p.closePath(); return p; };
  const face = poly(up), body = poly(hull([...up, ...down]));
  c.fillStyle = rgba(P.lo, 1); c.fill(body); c.strokeStyle = rgba(P.rimB, 1); c.lineWidth = 1; c.stroke(body);
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const q of up) { x0 = Math.min(x0, q[0]); x1 = Math.max(x1, q[0]); y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); }
  // The face's gradient lies in the unit square of its bounding box, as the objectBoundingBox gradient of the page.
  const fg = c.createRadialGradient(.3, .16, 0, .3, .16, 1.05);
  fg.addColorStop(0, rgba(P.hi, 1)); fg.addColorStop(.5, rgba(P.glass, 1)); fg.addColorStop(1, rgba(P.lo, 1));
  c.save(); c.clip(face); c.translate(x0, y0); c.scale(x1 - x0, y1 - y0); c.fillStyle = fg; c.fillRect(0, 0, 1, 1); c.restore();
  if (P.spec > 0) { at(-G.a * .36, -G.b * .34, TOP); c.globalAlpha = aBody * P.spec; c.drawImage(SPR.shine, PX - G.a * .5, PY - G.b * PC * .4, G.a, G.b * PC * .8); }

  // The relief and the rims of the basins, faint at the back and full in front.
  at(0, -G.b, TOP); const fx = PX, fy = PY; at(0, G.b, TOP);
  const fadeN = c.createLinearGradient(fx, fy, PX, PY); fadeN.addColorStop(0, rgba(P.ink, .38)); fadeN.addColorStop(1, rgba(P.ink, .95));
  const land = new Path2D();
  for (const row of LAND) for (let i = 0; i < row.us.length; i++) { at(row.us[i], row.v, TOP + row.zb[i]); i ? land.lineTo(PX, PY) : land.moveTo(PX, PY); }
  c.globalAlpha = .2 * aLand; c.strokeStyle = fadeN; c.lineWidth = G.lw * .9; c.stroke(land);
  const rings = new Path2D();
  for (const r of RINGS) for (let i = 0; i <= 48; i++) { const a = i / 48 * TAU; at(r.u + r.R * Math.cos(a), r.v + r.R * Math.sin(a), TOP - RIM * r.d); i ? rings.lineTo(PX, PY) : rings.moveTo(PX, PY); }
  c.globalAlpha = aRim; c.fillStyle = rgba(P.blue, P.wash); c.fill(rings); c.lineWidth = G.lw; c.stroke(rings);

  // Ripples of the convergence bursts, on the slab's surface around the item where the heads landed.
  c.strokeStyle = rgba(P.blue, 1);
  for (const b of S.bursts) for (const lag of [0, .32]) {
    const p = (lt - b.arr - lag) / 1.5; if (p < 0 || p >= 1) continue;
    const d = DOTS[b.it], R = 8 + 130 * (1 - (1 - p) ** 3), ring = new Path2D();
    for (let i = 0; i <= 56; i++) { const a = i / 56 * TAU; at(d.u + R * Math.cos(a), d.v + R * Math.sin(a), d.w); i ? ring.lineTo(PX, PY) : ring.moveTo(PX, PY); }
    c.globalAlpha = .85 * (1 - p) ** 1.6 * fade; c.lineWidth = 1.8 * (1 - .5 * p); c.stroke(ring);
  }

  // The dots that have been posted: solid for a result, hollow for work, small for an idea or a note.
  const small = new Path2D(), hollow = new Path2D(), solid = new Path2D();
  for (let i = 0; i < N; i++) {
    const q = (lt - TI[i]) / .32; if (q < 0) continue;
    const o = DOTS[i], sc = q < 1 ? Math.max(0, back(q)) : 1; at(o.u, o.v, o.w); o.x = PX; o.y = PY; o.k = PK;
    const r = (o.kind === "result" ? 3.5 : o.kind === "work" ? 2.9 : 1.9) * G.dot * PK * sc;
    const path = o.kind === "result" ? solid : o.kind === "work" ? hollow : small;
    path.moveTo(PX + r, PY); path.arc(PX, PY, r, 0, TAU);
  }
  c.globalAlpha = fade; c.fillStyle = rgba(P.ink, 1); c.fill(small); c.fill(solid);
  c.fillStyle = rgba(P.glass, 1); c.fill(hollow); c.strokeStyle = rgba(P.ink, 1); c.lineWidth = G.lw * 1.3; c.stroke(hollow);

  // The arcs, in three depth buckets each: fainter and thinner at the back, heavier in front.
  let dim = 0; for (const b of S.bursts) dim = Math.max(dim, dimOf(b, lt));
  const dimK = 1 - .6 * dim, zr = G.b * PS * .33;
  const same = [new Path2D(), new Path2D(), new Path2D()], cross = [new Path2D(), new Path2D(), new Path2D()];
  const heads = [];  // [link, s, strength]
  let landed = 0, landedX = 0;
  for (let i = 0; i < LK.length; i++) {
    const l = LK[i]; if (lt < l.start) continue;
    const p = (lt - l.start) / l.dur, s1 = p >= 1 ? 1 : ease(p);
    if (p >= 1) { landed++; landedX += l.x; } else heads.push([l, s1, 1]);
    point(l, .5); const bk = PZ < -zr ? 0 : PZ < zr ? 1 : 2;
    trace(l.x ? cross[bk] : same[bk], l, s1);
  }
  const BK = [.55, .8, 1], BW = [.75, 1, 1.25];
  c.strokeStyle = rgba(P.ink, 1);
  for (let b = 0; b < 3; b++) { c.globalAlpha = (.12 + .1 * b) * dimK * fade; c.lineWidth = .8 * BW[b]; c.stroke(same[b]); }
  if (P.dark) {
    c.globalCompositeOperation = "lighter";
    for (let b = 0; b < 3; b++) {
      c.strokeStyle = rgba(P.blue, 1);
      c.globalAlpha = .07 * BK[b] * dimK * fade; c.lineWidth = 5 * BW[b]; c.stroke(cross[b]);
      c.globalAlpha = .5 * BK[b] * dimK * fade; c.lineWidth = 1.25 * BW[b]; c.stroke(cross[b]);
    }
    c.globalCompositeOperation = "source-over";
  } else {
    c.strokeStyle = rgba(P.blue, 1);
    for (let b = 0; b < 3; b++) { c.globalAlpha = (.42 + .2 * b) * dimK * fade; c.lineWidth = 1.45 * BW[b]; c.stroke(cross[b]); }
  }

  // The arcs lit by the replay: one run per link, and every parent link of a burst.
  const lit = [];  // [link, strength]
  for (const r of S.runs) {
    const l = LK[r.li], p = (lt - r.t0) / l.dur;
    if (p >= 0 && p < 1) heads.push([l, ease(p), 1]);
    const a = clamp(p / .15) * clamp((1.4 - p) / .4); if (a > 0) lit.push([l, a * .8]);
  }
  for (const b of S.bursts) {
    const a = dimOf(b, lt);
    for (const i of b.ins) {
      const l = LK[i], p = (lt - (b.arr - l.dur)) / l.dur;
      if (a > 0) lit.push([l, a]);
      if (p >= 0 && p < 1) heads.push([l, ease(p), 1.25]);
    }
  }
  if (lit.length) {
    if (P.dark) c.globalCompositeOperation = "lighter";
    for (const [l, a] of lit) {
      const path = new Path2D(); trace(path, l, 1);
      c.strokeStyle = rgba(P.blue, 1);
      c.globalAlpha = (P.dark ? .2 : .25) * a * fade; c.lineWidth = 6; c.stroke(path);
      c.strokeStyle = rgba(P.dark ? P.core : P.blue, 1);
      c.globalAlpha = (P.dark ? .75 : .95) * a * fade; c.lineWidth = P.dark ? 1.5 : 2.3; c.stroke(path);
    }
    c.globalCompositeOperation = "source-over";
  }

  // The heads: a lit sprite with a short tapered tail behind it.
  if (P.dark) c.globalCompositeOperation = "lighter";
  for (const [l, s, m] of heads) {
    let px = 0, py = 0;
    for (let j = 6; j >= 0; j--) {
      point(l, Math.max(0, s - j * .028));
      if (j < 6) { c.beginPath(); c.moveTo(px, py); c.lineTo(PX, PY); c.strokeStyle = rgba(j < 2 ? P.core : P.blue, 1); c.globalAlpha = .85 * (1 - j / 6) * fade; c.lineWidth = (3.2 - j * .45) * PK; c.stroke(); }
      px = PX; py = PY;
    }
    const R = 15 * m * PK; c.globalAlpha = fade; c.drawImage(SPR.head, PX - R, PY - R, 2 * R, 2 * R);
  }
  // Flashes on the dots: when an item pops in, when heads land on it, and on the replay's landings.
  const flash = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    let f = fall(lt - TI[i], .6);
    for (const li of INTO[i]) f = Math.max(f, .8 * fall(lt - LK[li].land, .5));
    flash[i] = f;
  }
  for (const r of S.runs) { const l = LK[r.li]; flash[l.c] = Math.max(flash[l.c], .7 * fall(lt - r.t0 - l.dur, .45)); }
  for (const b of S.bursts) {
    flash[b.it] = Math.max(flash[b.it], 1.5 * fall(lt - b.arr, .9));
    for (const i of b.ins) { const l = LK[i]; flash[l.p] = Math.max(flash[l.p], .6 * fall(lt - (b.arr - l.dur), .4)); }
  }
  for (let i = 0; i < N; i++) {
    if (flash[i] <= .01 || lt < TI[i]) continue;
    const o = DOTS[i], R = (10 + 12 * flash[i]) * o.k; c.globalAlpha = Math.min(1, flash[i]) * fade;
    c.drawImage(SPR.head, o.x - R, o.y - R, 2 * R, 2 * R);
  }
  c.globalCompositeOperation = "source-over";

  // The names, upright, each in front of its basin, and the count under the slab.
  if (aName > 0) {
    c.font = NAME_FONT; c.textAlign = "center"; c.textBaseline = "alphabetic"; c.lineWidth = 5; c.strokeStyle = rgba(P.glass, 1); c.fillStyle = rgba(P.ink, 1);
    c.globalAlpha = aName;
    RINGS.forEach((r, i) => { at(r.u, r.v + r.R, TOP); const y = PY + G.fs * 1.12; c.strokeText(C.clusters[i].name, PX, y); c.fillText(C.clusters[i].name, PX, y); });
  }
  if (fontsAt < Infinity) {
    const aCount = lt >= END ? fade : S.first ? aName : clamp((lt - INTRO) / .4);
    c.globalAlpha = aCount; c.textAlign = "center"; c.fillStyle = rgba(P.ink, 1);
    c.font = NUM_FONT; if ("letterSpacing" in c) c.letterSpacing = "-2.5px";
    c.fillText(String(landedX), 800, 836);
    if ("letterSpacing" in c) c.letterSpacing = "0px";
    c.font = CAP_FONT; c.fillStyle = rgba(P.mute, 1); c.fillText(`of ${landed} links join two different basins of ideas`, 800, 872);
  }
  c.globalAlpha = 1;
}

const FINAL_T = 10, FINAL_LT = BUILD_END + .01;  // the still frame: the finished tree, the entrance done
function frame(now) {
  const t = now / 1000;
  if (t - S.T0 > END + FADE) restart(t);
  const lt = t - S.T0;
  schedule(lt);
  aim(-6 + 15 * Math.sin(t * .11), 2.5 * Math.sin(t * .08));
  draw(t, lt);
  requestAnimationFrame(frame);
}

addEventListener("resize", resize);
new MutationObserver(theme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", theme);
resize();
if (still) aim(-6, 0);
theme();
Promise.all([NAME_FONT, NUM_FONT, CAP_FONT].map(f => document.fonts.load(f))).then(() => document.fonts.ready).then(() => {
  fontsAt = still ? 0 : performance.now() / 1000;
  if (still) draw(FINAL_T, FINAL_LT);
});
if (!still) requestAnimationFrame(frame);
</script>
</body>
</html>
"""
_LABEL = (f"The idea tree of {len(ITEMS)} board items on a glass slab with {len(LAYOUT['clusters'])} basins. "
          f"{DATA['tree']['cross']} of {DATA['tree']['links']} links join two basins.")
PAGE = (PAGE.replace("__TOKENS__", TOKENS).replace("__LABEL__", _LABEL)
        .replace("__CONFIG__", json.dumps(CONFIG, separators=(",", ":"))))
