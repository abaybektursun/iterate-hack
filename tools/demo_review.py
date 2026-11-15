"""The picture of the deck's slide "proof": the compute one batch costs, cut down by three review rounds.

demo_deck.py embeds PAGE as /demo/fig/review; the slide carries the title, so this page is the picture alone. Four
glass columns stand on a glass slab seen from slightly above, one per review round of the team-meta-review skill
(Before, Round 1 to 3). A column is as high as the container minutes one batch costs after that round. Its lit foot is
the part of those minutes that produced one of the 4 answers (the one key under the slab); the plain glass above it produced none. A fifth column,
hollow with a dotted outline, stands at the end of the row: the same model after three rounds with a plain instruction
in place of the skill. On load all four columns rise to the height before any review, then each round cuts the columns
to its right and the hollow column appears; after that the view sways slowly. With prefers-reduced-motion and in print
it is the settled frame.

Every number is read at import from proof_review_cuts_waste.DATA (the proof page /proof/review-cuts-waste, whose
numbers come from studies/metaharness/results/planted/summary-01/metrics.json): the skill arm's minutes and answer
minutes per round, and the plain arm's minutes after round 3.
"""
import json

import proof_review_cuts_waste

SKILL, PLAIN = proof_review_cuts_waste.SKILL, proof_review_cuts_waste.PLAIN
ROUNDS = proof_review_cuts_waste.DATA["rounds"]
assert len(ROUNDS) == len(SKILL["minutes"]) == len(SKILL["answer"]) == 4, ROUNDS

DATA = {
    "rounds": ROUNDS,
    "minutes": SKILL["minutes"],  # container minutes per batch after each round, mean of 3 runs
    "answer": SKILL["answer"],  # the part of those minutes that produced an answer
    "plain": PLAIN["minutes"][-1],  # the plain instruction after round 3
    "unit": "Container minutes per batch",
}

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Review cuts waste</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* Tokens of the Design page: one light from the upper left, --blue the one accent. --wash is how strongly the lit
   foot of a column takes the accent. */
:root {
  color-scheme: light;
  --paper: #eceef0; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de; --blue: #1f43d6;
  --glass-hi: #ffffff; --glass: #f6f8f9; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --glow: 0; --wash: .3;
  --f: "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --paper: #080c11; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630; --blue: #8fb1ff;
  --glass-hi: #2c3e52; --glass: #121b24; --glass-lo: #090e14;
  --rim-a: rgba(255, 255, 255, .8); --rim-b: rgba(255, 255, 255, .12); --glow: 1; --wash: .46;
}
html, body { margin: 0; height: 100%; overflow: hidden; background: var(--paper); }
svg { display: block; width: 100vw; height: 100vh; font-family: var(--f); font-variant-numeric: tabular-nums; }
path { stroke-linejoin: round; }
.atmo { opacity: var(--glow); }
.shade { opacity: calc(1 - var(--glow)); }
.edge { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: .8; }
.top { stroke: var(--rim-a); stroke-width: .9; }
.front { stroke: var(--rim-b); stroke-width: .8; }
.side { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: .8; }
.wash { fill: var(--blue); opacity: var(--wash); }
.band { fill: none; stroke: var(--blue); stroke-width: 1.8; stroke-linecap: round; }
.band.halo { stroke-width: 8; opacity: calc(var(--glow) * .22); }
.ghost { fill: var(--glass); fill-opacity: .16; stroke: var(--mute); stroke-width: 1.5; stroke-dasharray: 1.5 6; stroke-linecap: round; }
.num { text-anchor: middle; font-weight: 300; fill: var(--mute); }
.num.end { fill: var(--ink); letter-spacing: -.01em; }
.num.now { fill: var(--blue); font-weight: 400; }
.round { text-anchor: middle; font-weight: 560; fill: var(--mute); }
.round.now { fill: var(--ink); }
.unit { font-size: 20px; font-weight: 600; fill: var(--ink); }
.key { font-size: 20px; font-weight: 500; fill: var(--mute); }
.keylit { fill: var(--blue); opacity: calc(var(--wash) + .25); }
</style>
</head>
<body>
<svg id="pic" viewBox="0 0 1000 600" role="img" aria-label="__LABEL__"></svg>
<script>
"use strict";
const D = __DATA__;
const NS = "http://www.w3.org/2000/svg", svg = document.getElementById("pic");
const el = (p, tag, attrs, text) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (text != null) e.textContent = text; p.appendChild(e); return e; };
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
const f = n => n.toFixed(1), clamp = x => Math.max(0, Math.min(1, x)), ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;

/* The scene, in world units: u to the right, v away from the viewer, w up. The row of columns is turned by YAW, so the
   right side of each column shows and the last round stands nearest; what is near is larger. One minute is UNIT high. */
const RAD = Math.PI / 180, CX = 484, CY = 408, YAW = -20, EL = 20, GAP = 164, HALF = 50, UNIT = 17, RU = 428, RV = 86, TH = 14;
const N = D.minutes.length, LAST = N - 1, U0 = -338, UG = U0 + N * GAP + 22;  // the first column, and the hollow one set a little apart
const V = { yaw: YAW, el: EL };
function proj(u, v, w) {
  const a = V.yaw * RAD, e = V.el * RAD, x = u * Math.cos(a) - v * Math.sin(a), d = u * Math.sin(a) + v * Math.cos(a);
  const k = 1100 / (1100 + d * .5);
  return [CX + x * k, CY - k * (d * Math.sin(e) + w * Math.cos(e)), k];
}
const pts = p => p.map(q => f(q[0]) + " " + f(q[1])).join("L");
const set = (e, p, open) => e.setAttribute("d", "M" + pts(p) + (open ? "" : "Z"));
const at = (list, q) => { const i = Math.min(list.length - 2, Math.floor(q)); return list[i] + (list[i + 1] - list[i]) * (q - i); };  // between two rounds

/* The entrance: all columns rise to the height before any review (RISE), then round r cuts every column from r on. */
const RISE = 1.0, T0 = 1.5, STEP = 1.15, CUT = .8, END = T0 + (LAST - 1) * STEP + CUT;
const S = { grow: 1, q: LAST, ghost: 1 };  // q: how many rounds have been made, 0 to LAST

const defs = el(svg, "defs", {});
const grad = (id, stops, x2, y2) => { const g = el(defs, "linearGradient", { id, x1: 0, y1: 0, x2, y2 }); for (const [o, c] of stops) el(g, "stop", { offset: o, style: `stop-color:var(${c})` }); };
grad("gFront", [[0, "--glass-hi"], [.55, "--glass"], [1, "--glass-lo"]], 1, 1);
grad("gTop", [[0, "--glass-hi"], [1, "--glass"]], 1, 0);
const radial = (id, stops) => { const g = el(defs, "radialGradient", { id }); for (const [o, c, a] of stops) el(g, "stop", { offset: o, style: `stop-color:var(${c});stop-opacity:${a}` }); };
radial("gAtmo", [[.2, "--blue", .16], [.65, "--blue", .05], [1, "--blue", 0]]);
radial("gShade", [[.5, "--ink", .2], [1, "--ink", 0]]);

el(svg, "ellipse", { cx: CX, cy: CY - 110, rx: 470, ry: 300, fill: "url(#gAtmo)", class: "atmo" });
el(svg, "ellipse", { cx: CX + 26, cy: CY + 52, rx: 470, ry: 104, fill: "url(#gShade)", class: "shade" });
const slab = { front: el(svg, "path", { class: "edge" }), right: el(svg, "path", { class: "edge" }), top: el(svg, "path", { class: "top", fill: "url(#gTop)" }) };
const cols = D.minutes.map((m, i) => {
  const g = el(svg, "g", {}), now = i === LAST ? " now" : "";
  return { i, u: U0 + i * GAP,
    side: el(g, "path", { class: "side" }), front: el(g, "path", { class: "front", fill: "url(#gFront)" }), wash: el(g, "path", { class: "wash" }),
    top: el(g, "path", { class: "top", fill: "url(#gTop)" }), halo: el(g, "path", { class: "band halo" }), band: el(g, "path", { class: "band" }),
    num: el(g, "text", { class: "num" + (i === 0 ? " end" : now) }), round: el(svg, "text", { class: "round" + now }, D.rounds[i]) };
});
const ghost = el(svg, "g", {}), gSide = el(ghost, "path", { class: "ghost" }), gFront = el(ghost, "path", { class: "ghost" }), gTop = el(ghost, "path", { class: "ghost" });
const gNum = el(ghost, "text", { class: "num" }, f(D.plain)), gName = el(ghost, "text", { class: "round" }, "Plain instruction");

/* under the slab, one centred row: the unit, and what the lit foot is */
const unit = el(svg, "text", { y: 586, class: "unit" }, D.unit), keyLit = el(svg, "rect", { y: 570, width: 17, height: 17, rx: 2, class: "keylit" });
const key = el(svg, "text", { y: 586, class: "key" }, "produced an answer");
function row() {  // after the font has loaded
  const a = unit.getComputedTextLength(), b = key.getComputedTextLength(), x = 500 - (a + 44 + 26 + b) / 2;
  unit.setAttribute("x", f(x)); keyLit.setAttribute("x", f(x + a + 44)); key.setAttribute("x", f(x + a + 70));
}

function place() {
  const rect = (ru, rv, w) => [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => proj(i * ru, j * rv, w));
  const a = rect(RU, RV, 0), b = rect(RU, RV, -TH);
  set(slab.top, a); set(slab.front, [a[0], a[1], b[1], b[0]]); set(slab.right, [a[1], a[2], b[2], b[1]]);
  for (const c of cols) {
    const q = Math.min(c.i, S.q), h = Math.max(2, at(D.minutes, q) * UNIT * S.grow), lit = Math.min(h, at(D.answer, q) * UNIT * S.grow);
    const P = (i, j, w) => proj(c.u + i * HALF, j * HALF, w);
    const up = [P(-1, -1, h), P(1, -1, h), P(1, 1, h), P(-1, 1, h)], foot = [P(-1, -1, 0), P(1, -1, 0), P(1, 1, 0)], mid = [P(-1, -1, lit), P(1, -1, lit), P(1, 1, lit)];
    set(c.front, [foot[0], foot[1], up[1], up[0]]);
    set(c.side, [foot[1], foot[2], up[2], up[1]]);
    set(c.top, up);
    set(c.wash, [foot[0], foot[1], foot[2], mid[2], mid[1], mid[0]]);
    set(c.band, mid, true); set(c.halo, mid, true);
    /* its number appears once the column has been cut to its own round */
    const big = c.i === 0 || c.i === LAST, k = up[0][2], shown = c.i === 0 ? S.grow : clamp((S.q - c.i + .35) / .35);
    c.num.textContent = f(D.minutes[c.i]);
    c.num.setAttribute("x", f((up[0][0] + up[2][0]) / 2)); c.num.setAttribute("y", f(up[3][1] - (big ? 16 : 13) * k));
    c.num.setAttribute("font-size", f((big ? 50 : 28) * k)); c.num.setAttribute("opacity", f(shown));
    const n = proj(c.u, -RV, -TH);
    c.round.setAttribute("x", f(n[0])); c.round.setAttribute("y", f(n[1] + 33 * n[2])); c.round.setAttribute("font-size", f(21 * n[2]));
  }
  /* the hollow column: the plain instruction after the last round */
  const G = (i, j, w) => proj(UG + i * HALF, j * HALF, w), h = D.plain * UNIT;
  const up = [G(-1, -1, h), G(1, -1, h), G(1, 1, h), G(-1, 1, h)], foot = [G(-1, -1, 0), G(1, -1, 0), G(1, 1, 0)], k = up[0][2], n = proj(UG, -RV, -TH);
  set(gFront, [up[0], foot[0], foot[1], up[1]], true); set(gSide, [foot[1], foot[2], up[2]], true); set(gTop, up);
  gNum.setAttribute("x", f((up[0][0] + up[2][0]) / 2)); gNum.setAttribute("y", f(up[3][1] - 13 * k)); gNum.setAttribute("font-size", f(28 * k));
  gName.setAttribute("x", f(n[0])); gName.setAttribute("y", f(n[1] + 33 * n[2])); gName.setAttribute("font-size", f(21 * n[2]));
  ghost.setAttribute("opacity", f(S.ghost));
}

function settle() { S.grow = 1; S.q = LAST; S.ghost = 1; V.yaw = YAW; V.el = EL; place(); }
let on = !still, t0 = null;
function frame(now) {
  if (!on) return;
  if (t0 == null) t0 = now;
  const t = (now - t0) / 1000, s = Math.max(0, t - END - .8), k = Math.min(1, s / 4);
  S.grow = ease(clamp(t / RISE));
  S.q = 0; for (let r = 0; r < LAST; r++) S.q += ease(clamp((t - T0 - r * STEP) / CUT));
  S.ghost = clamp((t - END - .1) / .6);
  V.yaw = YAW + k * 2.2 * Math.sin(2 * Math.PI * s / 18); V.el = EL + k * Math.sin(2 * Math.PI * s / 23);  // the slow sway
  place();
  requestAnimationFrame(frame);
}
addEventListener("beforeprint", () => { on = false; settle(); });
addEventListener("afterprint", () => { on = !still; if (on) requestAnimationFrame(frame); });
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => { row(); if (still) settle(); else requestAnimationFrame(frame); });
</script>
</body>
</html>
"""

LABEL = (f'{DATA["unit"]} over review rounds of the skill: '
         + "; ".join(f"{r} {m}, of which {a} produced an answer" for r, m, a in zip(ROUNDS, DATA["minutes"], DATA["answer"]))
         + f'. The same model with a plain instruction after {ROUNDS[-1].lower()}: {DATA["plain"]}.')
PAGE = PAGE.replace("__LABEL__", LABEL.replace('"', "&quot;")).replace("__DATA__", json.dumps(DATA).replace("</", "<\\/"))
