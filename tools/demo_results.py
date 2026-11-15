"""Two result pictures of the talk deck, each on a lit glass slab: PAGES["beyond"] and PAGES["efficiency"].

demo_deck.py embeds them as /demo/fig/beyond and /demo/fig/efficiency; the slide carries the words, so a page here is
the picture alone. The blue marks draw themselves once when the page loads (the deck reloads the frame when its slide
is shown); with prefers-reduced-motion and in print they are still.

beyond: percent right of the plain base (Olmo 3 7B, one sample) and of the configuration chosen on MATH-500 (the
three-token opening cue, T 1.0 / top-p 1.0), used unchanged on three sets it was never tuned on. The picture says one
thing, so each lane carries one number, its gain in points: large and blue on the three untouched sets, small and grey
on MATH-500, where the configuration was chosen. Sources: MATH-500 224 and 410 of 500 (result-c36598); hard328 76 and
164 of 328, and code (HumanEval+ and MBPP+, 538 problems) 222 and 326, in studies/rlneurons/README.md; general
questions (500 MMLU-Pro and BBH items) 136 and 286, in studies/ood on branch ali/ood (commit 99b2d5d; +30.0 points
[24.6, 35.4], and +12.5 [4.9, 19.7] on the 264 items both arms answer).

efficiency: percent right against generated tokens per problem, Karpathy's autoresearch loop against the swarm's cue
with one sample, on problems neither had used. Source: studies/autobench/README.md, table "Finals on problems no
experiment used"; the hard328 row is checked against demo_facts.FACTS["auto_research_comparison"] at import.
"""
import json

import demo_facts

# right of n in percent: the plain base and the configuration chosen on MATH-500
BEYOND = [
    {"name": "MATH-500", "sub": "500 problems", "plain": 44.8, "ours": 82.0},
    {"name": "Harder math", "sub": "328 problems", "plain": 23.2, "ours": 50.0},
    {"name": "Code", "sub": "HumanEval+ and MBPP+", "plain": 41.3, "ours": 60.6},
    {"name": "General questions", "sub": "MMLU-Pro and BBH", "plain": 27.2, "ours": 57.2},
]

# [right, n, tokens per problem] of autoresearch (k) and of our harness (o)
EFFICIENCY = [
    {"name": "400 unseen MATH-500 problems", "k": [338, 400, 11254], "o": [338, 400, 4097]},
    {"name": "328 harder problems", "k": [139, 328, 20407], "o": [160, 328, 9351]},
]
_F = demo_facts.FACTS["auto_research_comparison"]
assert [_F["v"]["autoresearch"]["right"], _F["n"], _F["v"]["autoresearch"]["tokens_per_problem"]] == EFFICIENCY[1]["k"], _F
assert [_F["v"]["nanolab"]["right"], _F["n"], _F["v"]["nanolab"]["tokens_per_problem"]] == EFFICIENCY[1]["o"], _F
TOKEN_RATIO = EFFICIENCY[0]["k"][2] / EFFICIENCY[0]["o"][2]  # at the same score on math400
HARD_GAIN = -_F["v"]["difference_points"]  # points, ours minus autoresearch, on hard328

HEAD = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* Tokens of the Design page: one light from the upper left, --blue the one accent (ours), the other side in ink. */
:root {
  color-scheme: light;
  --paper: #eceef0; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de; --blue: #1f43d6;
  --glass-hi: #ffffff; --glass: #f6f8f9; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --shadow: rgba(16, 24, 32, .18); --glow: 0;
  --f: "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --paper: #080c11; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630; --blue: #8fb1ff;
  --glass-hi: #2c3e52; --glass: #121b24; --glass-lo: #090e14;
  --rim-a: rgba(255, 255, 255, .8); --rim-b: rgba(255, 255, 255, .12); --shadow: rgba(0, 0, 0, .6); --glow: 1;
}
html, body { margin: 0; height: 100%; overflow: hidden; background: var(--paper); }
svg { display: block; width: 100vw; height: 100vh; font-family: var(--f); font-variant-numeric: tabular-nums; }
.slab { filter: drop-shadow(0 22px 26px var(--shadow)); }
.slab-top { stroke: var(--rim-a); stroke-width: .8; }
.slab-edge { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: .8; }
.grid { stroke: var(--rule); stroke-width: .7; }
.lane { stroke: var(--rule); stroke-width: 1; }
.ax { font-size: 14px; fill: var(--faint); }
.name { font-size: 18px; font-weight: 620; fill: var(--ink); text-anchor: middle; }
.sub { font-size: 14px; fill: var(--faint); text-anchor: middle; }
.gain { font-size: 19px; font-weight: 620; fill: var(--blue); }
.big { font-size: 40px; font-weight: 560; letter-spacing: -.02em; fill: var(--blue); }
.unit { font-size: 14px; fill: var(--mute); }
.quiet { opacity: .45; }  /* the lane the configuration was chosen on */
.quiet .ours, .quiet .rise { filter: none; }
.quiet .ours { fill: var(--ink); } .quiet .rise { stroke: var(--ink); }
.small { font-size: 20px; font-weight: 560; fill: var(--ink); }
.tuned { font-size: 16px; font-weight: 560; fill: var(--mute); text-anchor: middle; }
.never { font-size: 16px; font-weight: 620; fill: var(--blue); text-anchor: middle; }
.brace { fill: none; stroke: var(--mute); stroke-width: 1; }
.brace.b { stroke: var(--blue); }
.lab { font-size: 16px; font-weight: 560; fill: var(--ink); text-anchor: middle; }
.lab2 { font-size: 14px; fill: var(--mute); text-anchor: middle; }
.who { font-size: 14px; font-weight: 560; fill: var(--mute); text-anchor: middle; }
.who.b { fill: var(--blue); }
.base { fill: var(--glass); stroke: var(--ink); stroke-width: 2; }
.ours { fill: var(--blue); filter: drop-shadow(0 0 calc(var(--glow) * 7px) var(--blue)); animation: show .5s both; animation-delay: calc(1.25s + var(--i, 0) * .22s); }
.rise { fill: none; stroke: var(--blue); stroke-width: 2.4; stroke-linecap: round; stroke-dasharray: 1; animation: draw 1.1s both cubic-bezier(.3, 0, .2, 1); animation-delay: calc(.25s + var(--i, 0) * .22s); }
.head { fill: var(--blue); animation: show .4s 1.4s both; }
@keyframes draw { from { stroke-dashoffset: 1; } }
@keyframes show { from { opacity: 0; } }
@media (prefers-reduced-motion: reduce) { .rise, .ours, .head { animation: none; } }
@media print { .rise, .ours, .head { animation: none; } }
</style>
</head>
<body>
<svg id="pic" viewBox="0 0 1000 560" role="img" aria-label="__LABEL__"></svg>
<script>
"use strict";
const DATA = __DATA__;
const NS = "http://www.w3.org/2000/svg", svg = document.getElementById("pic");
const el = (p, tag, attrs, text) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (text != null) e.textContent = text; p.appendChild(e); return e; };
const fmt = n => n.toLocaleString("en-US");
const X0 = 150, X1 = 880;
const g = el(el(svg, "defs", {}), "linearGradient", { id: "gSlab", x1: 0, y1: 0, x2: 1, y2: 1 });
for (const [o, c] of [[0, "--glass-hi"], [.55, "--glass"], [1, "--glass-lo"]]) el(g, "stop", { offset: o, style: `stop-color:var(${c})` });
const body = el(svg, "g", { class: "slab" });
el(body, "rect", { x: 72, y: 46, width: 880, height: 478, rx: 20, class: "slab-edge" });
el(body, "rect", { x: 60, y: 32, width: 880, height: 478, rx: 20, class: "slab-top", fill: "url(#gSlab)" });
"""

# One lane per benchmark: the plain base as a hollow dot, the chosen configuration above it, and the gain in points.
BEYOND_JS = r"""
const Y0 = 118, Y1 = 428, y = p => Y1 - (p - 10) / 80 * (Y1 - Y0);
for (const p of [20, 40, 60, 80]) {
  el(svg, "line", { x1: X0, x2: X1, y1: y(p), y2: y(p), class: "grid" });
  el(svg, "text", { x: X0 - 12, y: y(p) + 5, class: "ax", "text-anchor": "end" }, p + " %");
}
const w = (X1 - X0) / DATA.length, cx = i => X0 + (i + .5) * w;
el(svg, "path", { d: `M${cx(0) - 62} 88v-8h124v8`, class: "brace" });
el(svg, "text", { x: cx(0), y: 70, class: "tuned" }, "Climbed here (validation)");
el(svg, "path", { d: `M${cx(1) - 62} 88v-8H${cx(DATA.length - 1) + 62}v8`, class: "brace b" });
el(svg, "text", { x: (cx(1) + cx(DATA.length - 1)) / 2, y: 70, class: "never" }, "Never climbed (test)");
DATA.forEach((s, i) => {
  const x = cx(i), lane = el(svg, "g", i ? {} : { class: "quiet" }), mid = (y(s.plain) + y(s.ours)) / 2;
  el(lane, "line", { x1: x, x2: x, y1: y(90), y2: y(10), class: "lane" });
  el(lane, "path", { d: `M${x} ${y(s.plain) - 10}L${x} ${y(s.ours)}`, class: "rise", pathLength: 1, style: `--i:${i}` });
  el(lane, "circle", { cx: x, cy: y(s.plain), r: 8, class: "base" });
  el(lane, "circle", { cx: x, cy: y(s.ours), r: i ? 11 : 9, class: "ours", style: `--i:${i}` });
  el(lane, "text", { x: x + 20, y: mid + (i ? 8 : 7), class: i ? "big" : "small" }, "+" + (s.ours - s.plain).toFixed(1));
  if (i) el(lane, "text", { x: x + 22, y: mid + 28, class: "unit" }, "points");
  el(svg, "text", { x, y: Y1 + 38, class: "name" }, s.name);
  el(svg, "text", { x, y: Y1 + 58, class: "sub" }, s.sub);
});
</script>
</body>
</html>
"""

# Percent right against tokens per problem: an arrow from autoresearch to ours for each set.
EFFICIENCY_JS = r"""
const Y0 = 96, Y1 = 440, x = t => X0 + t / 22000 * (X1 - X0), y = p => Y1 - (p - 30) / 65 * (Y1 - Y0);
for (const p of [40, 60, 80]) { el(svg, "line", { x1: X0, x2: X1, y1: y(p), y2: y(p), class: "grid" }); el(svg, "text", { x: X0 - 12, y: y(p) + 5, class: "ax", "text-anchor": "end" }, p + " %"); }
for (const t of [0, 5000, 10000, 15000, 20000]) el(svg, "text", { x: x(t), y: Y1 + 28, class: "ax", "text-anchor": "middle" }, fmt(t));
el(svg, "text", { x: (X0 + X1) / 2, y: Y1 + 54, class: "ax", "text-anchor": "middle" }, "Generated tokens per problem");
el(svg, "text", { x: X0 - 12, y: Y0 - 22, class: "ax", "text-anchor": "end" }, "Right");
DATA.forEach((s, i) => {
  const pct = m => 100 * m[0] / m[1], kx = x(s.k[2]), ky = y(pct(s.k)), ox = x(s.o[2]), oy = y(pct(s.o));
  const len = Math.hypot(kx - ox, ky - oy), ux = (ox - kx) / len, uy = (oy - ky) / len;
  el(svg, "path", { d: `M${kx + ux * 14} ${ky + uy * 14}L${ox - ux * 22} ${oy - uy * 22}`, class: "rise", pathLength: 1 });
  const hx = ox - ux * 13, hy = oy - uy * 13, nx = -uy, ny = ux;
  el(svg, "path", { d: `M${hx} ${hy}L${hx - ux * 12 + nx * 6} ${hy - uy * 12 + ny * 6}L${hx - ux * 12 - nx * 6} ${hy - uy * 12 - ny * 6}Z`, class: "head" });
  el(svg, "circle", { cx: kx, cy: ky, r: 8, class: "base" });
  el(svg, "circle", { cx: ox, cy: oy, r: 9.5, class: "ours" });
  for (const [px, py, m, who, cls] of [[kx, ky, s.k, "Autoresearch", "who"], [ox, oy, s.o, "Invariant (ours)", "who b"]]) {
    if (!i) el(svg, "text", { x: px, y: py - 66, class: cls }, who);
    el(svg, "text", { x: px, y: py - 42, class: "lab" }, `${m[0]} of ${m[1]}`);
    el(svg, "text", { x: px, y: py - 23, class: "lab2" }, fmt(m[2]) + " tokens");
  }
  const mx = (kx + ox) / 2, my = (ky + oy) / 2, ratio = (s.k[2] / s.o[2]).toFixed(1) + "× fewer tokens", up = pct(s.o) - pct(s.k);
  el(svg, "text", { x: mx, y: my + 34, class: "gain", "text-anchor": "middle" }, up > .05 ? `+${up.toFixed(1)} points, ${ratio}` : ratio);
  el(svg, "text", { x: mx, y: my + 54, class: "sub" }, s.name);
});
</script>
</body>
</html>
"""


def page(title, label, data, script):
    return (HEAD.replace("__TITLE__", title).replace("__LABEL__", label)
            .replace("__DATA__", json.dumps(data).replace("</", "<\\/")) + script)


PAGES = {
    "beyond": page("Beyond MATH-500", "Percent right for the plain base model and for the configuration chosen on MATH-500, on four benchmarks: "
                   + "; ".join(f'{s["name"]} {s["plain"]} to {s["ours"]}' for s in BEYOND), BEYOND, BEYOND_JS),
    "efficiency": page("Harness efficiency", "Percent right against generated tokens per problem, Karpathy's autoresearch and our harness: "
                       + "; ".join(f'{s["name"]}: autoresearch {s["k"][0]} of {s["k"][1]} at {s["k"][2]:,} tokens, ours {s["o"][0]} at {s["o"][2]:,}'
                                   for s in EFFICIENCY), EFFICIENCY, EFFICIENCY_JS),
}
