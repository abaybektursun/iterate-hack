"""RL training changed almost every neuron a little: the best 1 % of neurons carry only 16 % of the change.

The page of one finding, served at /finding/rl-every-neuron: view.py serves every tools/finding_<slug>.py and links
it in the header of the site. The picture is a trend on one lit plate: the share of the difference between the base
model and its RL version that closes when a share of RL's neurons is copied into the base, for the best, the most
changed and random neurons. The reader drags one slider along the share of neurons and the curves are drawn up to
it. The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md). The numbers are those of studies/cleanneurons/README.md, Parts T2 and T3.
"""
import json

# Every number is copied from the artifacts named here, rounded to four decimals. None is typed from memory.
# A pair is [text written by the base (cell T1), text written by RL (cell T2)]; the page shows the mean of a pair.
DATA = {
    "artifact": "studies/cleanneurons/results/transplant/curve_attr-01/metrics.json",
    "commit": "51b022a72c865057911e83260d2b5661adad0e59",
    "command": "python -m studies.cleanneurons.jobs.transplant_curve --rank attr --commit 51b022a72c865057911e83260d2b5661adad0e59",
    "key": "closure_decisive_after_cue_half_B",  # arms.<arm>.cells.<cell>.<key>
    "metric": "share of the KL divergence from RL's next-word predictions, at the 4 % of positions where it is largest, "
              "that disappears when the neurons are copied from RL into the base; scored on the held-out half of the answers",
    "models": {"base": "allenai/Olmo-3-1025-7B", "rl": "allenai/Olmo-3.1-7B-RL-Zero-Math"},  # models.<name>.repo
    "answers": [40, 40],  # len(cells.<cell>.rows); half of each ranks the neurons, the other half scores them
    "positions": [1163, 1509],  # cells.<cell>.decisive_positions_after_cue_half_B
    # What the reader slides along: the share of the 352,256 neurons copied from RL. The first is shown on load.
    # best = arm attr<share> (ranked by effect on the other half), changed = arm top<share> (ranked by weight
    # change), random = arms rnd<share>_s0 and rnd<share>_s1 (two draws).
    "series": [["best", "Best"], ["changed", "Most changed"], ["random", "Random"]],
    "points": [
        {"share": 0.1, "neurons": 352, "best": [0.0535, 0.0733], "changed": [0.0104, 0.0194], "random": [[0.0015, 0.0024], [0.0021, 0.0018]]},
        {"share": 0.3, "neurons": 1057, "best": [0.085, 0.1132], "changed": [0.0223, 0.0331], "random": [[0.0037, 0.0032], [0.0035, 0.0036]]},
        {"share": 1, "neurons": 3523, "best": [0.1371, 0.1858], "changed": [0.0423, 0.058], "random": [[0.0073, 0.0103], [0.008, 0.0097]]},
        {"share": 3, "neurons": 10568, "best": [0.2101, 0.2957], "changed": [0.0776, 0.1056], "random": [[0.0225, 0.0296], [0.0241, 0.0299]]},
        {"share": 10, "neurons": 35226, "best": [0.3356, 0.4891], "changed": [0.1554, 0.2091], "random": [[0.0735, 0.0985], [0.0746, 0.0999]]},
    ],
    "all": {"share": 100, "neurons": 352256, "value": [0.6772, 0.8635]},  # arm mlp: every feed-forward neuron
    # studies/cleanneurons/results/transplant/curve_attr-01/rank_attr_readout.json
    "score": {"positive": 0.8822, "predicted": 0.5417, "measured": 0.5486, "of": 0.7083},
    # The run with one constant vector per layer, same key. bias_layer adds the vector to the layer's output;
    # bias_mlp_rnd is a random vector per layer with the norm of the vector of the feed-forward block alone.
    "vector": {
        "artifact": "studies/cleanneurons/results/transplant/curve_bias-01/metrics.json",
        "commit": "a2ec2c9a0a69686d274b4e1ed8172dfbe1fb37bc",
        "bias_layer": [0.2342, 0.3118],
        "bias_mlp_rnd": [-0.0162, -0.0475],
    },
}


def mean(v):
    """Per cent, the mean of a pair or of several pairs."""
    flat = [x for p in v for x in p] if isinstance(v[0], list) else v
    return 100 * sum(flat) / len(flat)


def pct(v):
    return f"{v:.1f} %" if abs(v) < 10 else f"{round(v)} %"


STOPS = [{"share": p["share"], "neurons": p["neurons"], **{k: round(mean(p[k]), 2) for k, _ in DATA["series"]}} for p in DATA["points"]]
STOPS.append({"share": 100, "neurons": DATA["all"]["neurons"], **{k: round(mean(DATA["all"]["value"]), 2) for k, _ in DATA["series"]}})
ONE = DATA["points"][2]  # the best, most changed and random 1 %
VEC = DATA["vector"]

TITLE = "RL changed most neurons"  # the link text in the site header and the browser tab
PROBLEM = "Which neurons did RL training change?"
LINE = f"Almost all, a little each: the best 1 % carry only {pct(mean(ONE['best']))} of the change."

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["how", "How we know",
     "We copied neurons from RL (the base model after reinforcement-learning training on math) into the base and measured how much "
     "of the difference between their next-word predictions closed.",
     [f"It was measured on {sum(DATA['answers'])} stored answers to MATH-500 problems, at the {sum(DATA['positions']):,} positions where the "
      "two models differ most: the best neurons are those whose copying closes the most on half of the answers, and every set is scored "
      "on the other half; most changed means the largest weight change.",
      f"Controls: a random 1 % of neurons closes {pct(mean(ONE['random']))}, copying every weight gives exactly RL, and a first-order "
      f"estimate gives {round(100 * DATA['score']['positive'])} % of the {DATA['all']['neurons']:,} neurons a small effect toward RL; "
      f"summed, these predict {DATA['score']['predicted']:.3f} nats and {DATA['score']['measured']:.3f} were measured, of {DATA['score']['of']:.3f}.",
      "Closest published results: RL weight updates spread over all layers (Mukherjee et al., arXiv 2505.11711); a reward-trained mask "
      "that zeroes under 0.05 % of weights matches fine-tuning (Lu et al., arXiv 2611.10866); our board result-d2933e finds that 8 "
      "directions per weight matrix carry most of the RL gain."]],
    ["limits", "What it does not show",
     "It measures how close the predictions come to RL's rather than accuracy on the math benchmark.",
     ["Another way of ranking the neurons could find a better 1 %.",
      f"Only one pair of models was tested, and all of its feed-forward neurons together close {pct(mean(DATA['all']['value']))}: "
      "the rest needs the other weights, mostly attention.",
      f"The change still has structure: one fixed vector added to each layer, with no weight changed, closes {pct(mean(VEC['bias_layer']))} "
      f"({100 * VEC['bias_layer'][0]:.1f} % and {100 * VEC['bias_layer'][1]:.1f} %), and a random vector, matched in size to the "
      f"feed-forward part of that vector, makes the difference {pct(-mean(VEC['bias_mlp_rnd']))} larger."]],
    ["run", "How to reproduce it",
     "On one H100 GPU, run " + DATA["command"] + ".",
     ["The neuron curves ran at commit " + DATA["commit"][:7] + "; their numbers are in " + DATA["artifact"] + ", under " + DATA["key"] + ".",
      "Each point in the picture is the mean of two sets of text: for the best 1 %, "
      f"{100 * ONE['best'][0]:.1f} % on text written by the base and {100 * ONE['best'][1]:.1f} % on text written by RL.",
      "The fixed-vector run added --bias at commit " + VEC["commit"][:7] + "; its numbers are in " + VEC["artifact"] + ". The models are "
      + DATA["models"]["base"] + " (base) and " + DATA["models"]["rl"] + " (RL)."]],
]

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --lift: 38%;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --lift: 55%;
  }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(300px, 27vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0 48px; height: 100vh; min-height: 600px; max-width: 1840px; margin: 0 auto; padding: 24px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 22px; font-size: 13px; }
.name { font-weight: 700; font-stretch: 112%; font-size: 15px; letter-spacing: .01em; margin: 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture: one plate, the curves on it, and the one slider that draws them */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
svg { width: 100%; max-height: calc(100vh - 110px); display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; pointer-events: none; }
.atmo, .shade, .spec, .bloom, .back, .hint { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.bloom { opacity: var(--bloom); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.grid line { stroke: var(--rule); stroke-width: 1; }
.grid line.zero { stroke: var(--faint); stroke-width: 1.4; }
.num { fill: var(--faint); text-anchor: end; font-weight: 500; }
.rx, .ry { fill: var(--mute); font-weight: 520; }
.big { font-weight: 660; letter-spacing: -.02em; }
.curve { fill: none; stroke-linecap: round; stroke-linejoin: round; }
.dots { fill: none; stroke-linecap: round; }
.curve.random, .dots.random { stroke: var(--faint); stroke-width: 1.4; }
.curve.changed, .dots.changed { stroke: var(--mute); stroke-width: 2.1; }
.curve.best, .dots.best { stroke: var(--ink); stroke-width: 3.4; }
.dots.random { stroke-width: 5; } .dots.changed { stroke-width: 6.5; } .dots.best { stroke-width: 8.5; }
.pt { stroke: var(--glass); stroke-width: 2; }
.pt.random { fill: var(--faint); } .pt.changed { fill: var(--mute); } .pt.best { fill: var(--blue); }
.lab { fill: var(--mute); font-weight: 520; }
.lab.best { fill: var(--ink); font-weight: 640; }
.lab .vl { font-weight: 640; }
.track { stroke: var(--faint); stroke-width: 1.5; stroke-linecap: round; }
.tick { fill: var(--faint); }
.tnum { fill: var(--faint); text-anchor: middle; font-weight: 500; }
.tnum.sel { fill: var(--ink); font-weight: 680; }
.guide { stroke: var(--blue); stroke-width: 1.3; opacity: .6; }
.knob { fill: url(#orb) var(--blue); stroke: var(--glass); stroke-width: 2; }
.kring { fill: none; stroke: var(--ink); stroke-width: 2; opacity: 0; }
.hint { fill: none; stroke: var(--blue); stroke-width: 2.3; stroke-linecap: round; stroke-linejoin: round; animation: nudge 1.8s ease-in-out infinite; }
.moved .hint { display: none; }
.hit { fill: transparent; stroke: none; cursor: ew-resize; touch-action: pan-y; }
#slider:focus-visible { outline: none; }
#slider:focus-visible .kring { opacity: 1; }

/* One drawn entrance, then only the slow sway and what the reader moves */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
@keyframes nudge { 50% { transform: translateX(7px); } }
.enter .draw { stroke-dasharray: 1; animation: draw 1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec { animation: fade 1.4s .1s both; }
.enter .grid, .enter .read, .enter .axis { animation: fade .6s .45s both; }
.enter .curve, .enter .dots, .enter .pt, .enter .lab, .enter .guide, .enter .knobs { animation: fade .6s .8s both; }

/* The words */
.side { min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none; padding-top: clamp(16px, 7vh, 96px); }
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(28px, 2.5vw, 46px); line-height: 1.1; font-weight: 300; font-stretch: 106%; letter-spacing: -.015em; max-width: 15ch; }
.say b { font-weight: 660; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 112%; }
.close { font-size: 13px; color: var(--mute); }
.lead { margin: 16px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 420; max-width: 30ch; overflow-wrap: anywhere; }
.facts { list-style: none; margin: 16px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 7px 0; border-top: 1px solid var(--rule); }
@media (max-width: 900px) {
  /* On a phone the question and the finding come first, then the picture, then the panels. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 18px 16px 40px; }
  .top { flex-wrap: wrap; gap: 4px 14px; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 18ch; }
  .stage { order: 3; margin-top: 18px; display: block; }
  .pane { order: 4; margin-top: 20px; }
  svg { max-height: none; }
}
@media (prefers-reduced-motion: reduce) { .enter *, .hint { animation: none !important; } }
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">How it works</a>
    <a href="" aria-current="page">__TITLE__</a>
  </header>
  <div class="stage"><svg id="svg" role="group" aria-label="Share of the RL change carried by a share of the neurons"></svg></div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const RAD = Math.PI / 180, f = n => n.toFixed(1);
const pct = v => (v < 10 ? v.toFixed(1) : String(Math.round(v))) + " %";
/* A stop is one measured share of the neurons. Its place on the axis is logarithmic, counted in half decades. */
const STOPS = C.stops.map(s => ({ ...s, at: 2 * Math.log10(s.share / C.stops[0].share) })), LAST = STOPS[STOPS.length - 1].at;
const SERIES = [...C.series].reverse();  // back to front: random, most changed, best
const S = { stop: 0, u: 0, open: null, g: null, el: {}, drag: false, moved: false, entered: false, running: false };

/* Geometry: the plate faces the viewer, in a small 3D space around its centre (x right, y down, z toward the
   viewer). a is the plate, x0 to x1 the axis of the share of neurons, y0 (0 %) to y1 (100 %) the share of the
   change, yt the slider's track, yn its numbers. The three curves stand a little in front of the plate, the best
   one nearest (z). On a phone the numbers under the track carry no unit (bare), so that they do not touch; the
   line above the large number names the unit. */
function geo() {
  return narrow.matches
    ? { w: 480, h: 566, cx: 240, cy: 268, D: 1900, a: [6, 8, 474, 528], r: 22, deep: 30, x0: 40, x1: 276, gx: 458, y0: 402, y1: 60, yt: 450, yn: 496,
        fs: 17.5, fn: 16, fb: 72, bx: 40, by: [96, 166, 192], z: [5, 12, 20], kr: 14, blur: 12, bare: true }
    : { w: 1000, h: 696, cx: 500, cy: 330, D: 2100, a: [30, 24, 970, 636], r: 30, deep: 40, x0: 120, x1: 700, gx: 944, y0: 500, y1: 96, yt: 548, yn: 597,
        fs: 21, fn: 17, fb: 112, bx: 120, by: [136, 240, 272], z: [5, 12, 20], kr: 13, blur: 16 };
}
/* The view, as in architecture.py: a slow sway, plus a few degrees toward the pointer. */
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z) {  // to the screen: [x, y]
  const X = x - g.cx, Y = y - g.cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, g.cy + y1 * k];
}
const xy = q => f(q[0]) + " " + f(q[1]);
function slab(g, z) {  // the outline of the plate at depth z
  const [x0, y0, x1, y1] = g.a, r = g.r, p = [];
  const corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(xy).join("L") + "Z";
}
function val(key, u) {  // a curve between two measured stops is a straight line on this axis
  let i = 0;
  while (i < STOPS.length - 2 && u > STOPS[i + 1].at) i++;
  const a = STOPS[i], b = STOPS[i + 1], q = Math.min(1, Math.max(0, (u - a.at) / (b.at - a.at)));
  return a[key] + (b[key] - a[key]) * q;
}

/* The picture, built once per layout. place() then sets every position that depends on the view and on how far the
   curves are drawn; render() sets the numbers of the chosen stop. Back to front: the light and the shadow, the
   plate, the grid, the large number, the three curves, the slider. */
function build() {
  const g = S.g = geo(), svg = $("svg"), [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<radialGradient id="glo">${stop(0, "var(--blue)", .6)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="orb" cx=".34" cy=".3" r=".8">${stop(0, "color-mix(in oklch, var(--blue), white var(--lift))")}${stop(1, "var(--blue)")}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${g.cy}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .05)}" width="${aw}" height="${ah}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .32)}" cy="${f(ay0 + ah * .28)}" rx="${f(aw * .3)}" ry="${f(ah * .22)}" transform="rotate(-16 ${f(ax0 + aw * .32)} ${f(ay0 + ah * .28)})" fill="url(#spec)"/>` +
    `<g class="grid">${[0, 50, 100].map(v => `<line id="g${v}"${v ? "" : ' class="zero"'}/>`).join("")}` +
    [50, 100].map(v => `<text class="num" id="n${v}" font-size="${g.fn}">${v} %</text>`).join("") + "</g>" +
    `<g class="read"><text class="rx" id="rx" font-size="${g.fs + 1}"></text><text class="big" id="big" font-size="${g.fb}"></text>` +
    `<text class="ry" id="ry" font-size="${g.fs + 1}">of the change</text></g>` +
    SERIES.map(([key]) => `<path class="curve ${key}" id="c-${key}"/><path class="dots ${key}" id="m-${key}"/>`).join("") +
    `<g class="axis"><line class="track" id="track"/>` +
    STOPS.map((s, i) => `<circle class="tick" id="t${i}" r="3"/><text class="tnum" id="tn${i}" font-size="${g.fn}">${s.share}${g.bare ? "" : " %"}</text>`).join("") + "</g>" +
    `<line class="guide" id="guide"/>` +
    SERIES.map(([key], n) => `<circle class="pt ${key}" id="p-${key}" r="${[4.5, 5.5, 7.5][n]}"/>`).join("") +
    SERIES.map(([key, name]) => `<text class="lab ${key}" id="l-${key}" font-size="${g.fs}">${name} <tspan class="vl" id="v-${key}"></tspan></text>`).join("") +
    `<g id="slider" role="slider" tabindex="0" aria-label="Share of the neurons copied from RL" aria-valuemin="0" aria-valuemax="${STOPS.length - 1}">` +
    `<path class="hit" id="hit"/><g class="knobs"><circle class="bloom" id="kglow" r="${f(g.kr * 3.4)}" fill="url(#glo)"/>` +
    `<circle class="kring" id="kring" r="${g.kr + 6}"/><circle class="knob" id="knob" r="${g.kr}"/><g id="hint"><path class="hint" d="M-5 -8L4 0L-5 8"/></g></g></g>`;
  S.el = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  if (!S.entered) {
    S.entered = true;
    svg.classList.add("enter");
    setTimeout(() => svg.classList.remove("enter"), 2200);
  }
}
function render() {
  const s = STOPS[S.stop], E = S.el, all = S.stop === STOPS.length - 1;
  E.big.textContent = pct(s.best);
  E.rx.textContent = `${all ? "" : "Best "}${s.share} % of neurons`;
  SERIES.forEach(([key]) => { E["v-" + key].textContent = pct(s[key]); });
  STOPS.forEach((_, i) => E["tn" + i].classList.toggle("sel", i === S.stop));
  E.slider.setAttribute("aria-valuenow", S.stop);
  E.slider.setAttribute("aria-valuetext", `${s.share} % of neurons (${s.neurons.toLocaleString("en-US")}): ` +
    C.series.map(([key, name]) => `${name.toLowerCase()} ${pct(s[key])}`).join(", ") + " of the change");
  $("svg").classList.toggle("moved", S.moved);
}
function place() {
  const g = S.g, E = S.el, u = S.u, zk = g.z[2];
  const X = a => g.x0 + (g.x1 - g.x0) * a / LAST, Y = v => g.y0 + (g.y1 - g.y0) * v / 100;
  const set = (el, o) => { for (const k in o) el.setAttribute(k, o[k]); };
  const seg = (el, a, b) => set(el, { x1: f(a[0]), y1: f(a[1]), x2: f(b[0]), y2: f(b[1]) });
  const at = (el, q, dy) => set(el, { x: f(q[0]), y: f(q[1] + (dy || 0)) });
  const face = slab(g, 0);
  E.back.setAttribute("d", slab(g, -g.deep));
  E.plate.setAttribute("d", face);
  E.hit.setAttribute("d", face);
  [0, 50, 100].forEach(v => {
    seg(E["g" + v], proj(g, g.x0, Y(v), 0), proj(g, g.gx, Y(v), 0));
    if (v) at(E["n" + v], proj(g, g.gx, Y(v) - g.fn * .5, 0));
  });
  ["rx", "big", "ry"].forEach((id, i) => at(E[id], proj(g, g.bx, g.by[i], 0)));
  const end = {};
  SERIES.forEach(([key], n) => {  // each curve is drawn up to u; a dot marks each measured stop on the way
    const pts = STOPS.filter(s => s.at <= u).map(s => proj(g, X(s.at), Y(s[key]), g.z[n]));
    end[key] = proj(g, X(u), Y(val(key, u)), g.z[n]);
    E["c-" + key].setAttribute("d", "M" + pts.map(xy).join("L") + "L" + xy(end[key]));
    E["m-" + key].setAttribute("d", pts.map(q => "M" + xy(q) + "h0").join(""));
    set(E["p-" + key], { cx: f(end[key][0]), cy: f(end[key][1]) });
  });
  let ly = proj(g, X(u), g.y0 - g.fs * .68, zk)[1];  // a name sits beside its dot, above the axis and clear of the name below it
  SERIES.forEach(([key]) => {
    ly = Math.min(end[key][1], ly);
    at(E["l-" + key], [end.best[0] + g.fs * .8, ly], g.fs * .35);
    ly -= g.fs * 1.28;
  });
  seg(E.track, proj(g, X(0), g.yt, zk), proj(g, X(LAST), g.yt, zk));
  STOPS.forEach((s, i) => {
    const q = proj(g, X(s.at), g.yt, zk);
    set(E["t" + i], { cx: f(q[0]), cy: f(q[1]) });
    at(E["tn" + i], proj(g, X(s.at), g.yn, zk));
  });
  const k = proj(g, X(u), g.yt, zk);
  seg(E.guide, k, end.best);
  ["kglow", "kring", "knob"].forEach(id => set(E[id], { cx: f(k[0]), cy: f(k[1]) }));
  E.hint.setAttribute("transform", `translate(${f(k[0] + g.kr + 13)} ${f(k[1])})`);
}
/* Motion: the plate sways by a few degrees and leans toward the pointer, and the curves follow the slider. With
   reduced motion the page shows one still frame and the curves jump to the chosen stop. */
function frame(now) {
  if (still.matches) { S.running = false; return rest(); }
  const t = now / 1000, to = STOPS[S.stop].at, dt = Math.min(.25, t - (S.t || t));  // by the clock, so a slow tab still arrives
  S.t = t;
  V.px += (V.tx - V.px) * (1 - Math.exp(-dt * 3.7));
  V.py += (V.ty - V.py) * (1 - Math.exp(-dt * 3.7));
  aim(5 * Math.sin(t * .13) + 4 * V.px, 2 * Math.sin(t * .09) - 2 * V.py);
  S.u = Math.abs(to - S.u) < .004 ? to : S.u + (to - S.u) * (1 - Math.exp(-dt * 8));
  place();
  requestAnimationFrame(frame);
}
function rest() { aim(0, 0); S.u = STOPS[S.stop].at; place(); }
function start() { if (still.matches) rest(); else if (!S.running) { S.running = true; requestAnimationFrame(frame); } }
function go(i) {
  i = Math.min(STOPS.length - 1, Math.max(0, i));
  if (i === S.stop) return;
  S.stop = i; S.moved = true;
  render();
  if (still.matches) rest();
}
function pick(e) {  // the stop nearest to the pointer
  const p = new DOMPoint(e.clientX, e.clientY).matrixTransform($("svg").getScreenCTM().inverse()), g = S.g;
  let near = 0, d = Infinity;
  STOPS.forEach((s, i) => {
    const q = proj(g, g.x0 + (g.x1 - g.x0) * s.at / LAST, g.yt, g.z[2]);
    if (Math.abs(q[0] - p.x) < d) { d = Math.abs(q[0] - p.x); near = i; }
  });
  go(near);
}

function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${p[1]}</h2><button class="close" data-open="">Close</button></div><p class="lead">${p[2]}</p>` +
      `<ul class="facts">${p[3].map(f => `<li>${f}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${p[1]}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
function fromHash() { const h = location.hash.slice(1); S.open = C.panels.some(p => p[0] === h) ? h : null; pane(); }
document.addEventListener("click", e => {
  const o = e.target.closest("[data-open]");
  if (o) { history.pushState(null, "", o.dataset.open ? "#" + o.dataset.open : location.pathname); fromHash(); }
});
document.addEventListener("pointerdown", e => {
  if (!e.target.closest || !e.target.closest("#hit")) return;
  S.drag = true;
  e.target.setPointerCapture(e.pointerId);
  pick(e);
});
document.addEventListener("pointermove", e => {
  if (S.drag) pick(e);
  if (e.pointerType === "mouse") { V.tx = e.clientX / innerWidth * 2 - 1; V.ty = e.clientY / innerHeight * 2 - 1; }
});
["pointerup", "pointercancel"].forEach(n => document.addEventListener(n, () => { S.drag = false; }));
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) { history.pushState(null, "", location.pathname); fromHash(); }
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") { e.preventDefault(); go(S.stop + (e.key === "ArrowRight" ? 1 : -1)); }
  if ((e.key === "Home" || e.key === "End") && e.target.closest && e.target.closest("#slider")) { e.preventDefault(); go(e.key === "Home" ? 0 : STOPS.length - 1); }
});
addEventListener("hashchange", fromHash);
narrow.addEventListener("change", () => { build(); render(); place(); });
still.addEventListener("change", start);
$("problem").textContent = C.problem;
$("say").innerHTML = C.line.replace(/(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
build();
render();
place();
start();
fromHash();
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps(
    {"problem": PROBLEM, "line": LINE, "stops": STOPS, "series": DATA["series"], "data": DATA, "panels": PANELS}))
