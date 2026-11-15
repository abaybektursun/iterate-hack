"""The picture of the deck's slide "gap": the base model and the RL-trained model as two glass pillars, and a bridge.

demo_deck.py embeds page(lo, rl, bench) as /demo/fig/gap; the slide has no words, so this page is the picture alone.
Two glass pillars stand on one floor, each as high as its model's score on the benchmark (lo and rl, percents, read by
demo_deck.py from demo_ali_data.DATA['climb']: the plain base's first score and RL's best). The same small robot stands
on each: unlit on the base pillar, lit and flexing on the RL pillar. On load the pillars rise, the robots drop on, the
planks of a staircase bridge appear between the two tops as dashed outlines, and the base robot hops onto the first two,
which turn solid. Then the base robot bobs, the RL robot blinks and a blue spark runs up the planks still to be built.
With prefers-reduced-motion and in print it is the settled frame. Only CSS animations move; no script runs per frame.
"""
import json

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Bridging the gap</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* Tokens of demo_fixes.py: one light from the upper left, --blue only for the bridge and the trained robot's light. */
:root {
  color-scheme: light;
  --paper: #eceef0; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de; --blue: #1f43d6;
  --glass-hi: #ffffff; --glass: #f6f8f9; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --shadow: rgba(16, 24, 32, .22); --glow: 0;
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
.cap { font-size: 17px; font-weight: 500; fill: var(--mute); text-anchor: middle; }
.floor { stroke: var(--rule); stroke-width: 1; }
.shade { fill: var(--shadow); opacity: calc(1 - var(--glow) * .4); }
.bloom { opacity: calc(var(--glow) * .55); }
.front { stroke: var(--rim-b); stroke-width: .8; }
.top { stroke: var(--rim-a); stroke-width: .8; }
.side { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: .8; }
.score { font-size: 64px; font-weight: 300; letter-spacing: -.01em; fill: var(--ink); text-anchor: middle; }
.name { font-size: 20px; font-weight: 560; fill: var(--mute); text-anchor: middle; }
/* the planks: a dashed blue outline still to be built, solid lit glass with a blue rim once stepped on */
.todo { fill: var(--blue); fill-opacity: .06; stroke: var(--blue); stroke-width: 1.3; stroke-dasharray: 3 3.5; stroke-linejoin: round; opacity: .85; }
.todo.edge { fill: none; }
.done .rimb { fill: none; stroke: var(--blue); stroke-width: 1.3; stroke-linejoin: round; }
.done .halo { fill: none; stroke: var(--blue); stroke-width: 6; stroke-linejoin: round; opacity: calc(.1 + var(--glow) * .16); }
/* the robot */
.glass { stroke: var(--rim-a); stroke-width: .9; }
.plate { stroke: var(--rim-b); stroke-width: .8; }
.armrim { fill: none; stroke: var(--rim-a); stroke-width: 11.8; stroke-linecap: round; stroke-linejoin: round; }
.arm { fill: none; stroke: var(--glass); stroke-width: 10; stroke-linecap: round; stroke-linejoin: round; }
.stick { stroke: var(--rim-b); stroke-width: 2; stroke-linecap: round; }
.dot { fill: var(--ink); }
.ball { fill: var(--glass-lo); stroke: var(--rim-a); stroke-width: .9; }
.lit { fill: var(--blue); }
.litline { fill: none; stroke: var(--blue); stroke-width: 3.2; stroke-linecap: round; }
.glowline { fill: none; stroke: var(--blue); stroke-width: 9; stroke-linecap: round; opacity: calc(.14 + var(--glow) * .2); }
.glowball { fill: var(--blue); opacity: calc(.16 + var(--glow) * .22); }
.sheen { fill: none; stroke: var(--glass-hi); stroke-width: 2.4; stroke-linecap: round; opacity: .75; }
.spark .core { fill: var(--blue); }
.spark .aura { fill: var(--blue); opacity: calc(.2 + var(--glow) * .15); }

/* the entrance, once, then three quiet loops (each element's resting style is the settled frame) */
.rise { transform-box: fill-box; transform-origin: 50% 100%; animation: rise .9s cubic-bezier(.2, .7, .2, 1) both; animation-delay: var(--d); }
.ap { animation: show .4s both; animation-delay: var(--d); }
.drop { animation: drop .6s both; animation-delay: var(--d); }
.flex { animation: flex .7s ease-in-out both; animation-delay: var(--d); }
.plank { animation: plank .35s ease-out both; animation-delay: var(--d); }
.tilt { transform: rotate(6deg); animation: tilt .5s ease-out both; animation-delay: var(--d); }
.bob { animation: bob 2.4s ease-in-out infinite; animation-delay: var(--d); }
.blink { transform-box: fill-box; transform-origin: 50% 50%; animation: blink 4.2s infinite; animation-delay: var(--d); }
.spark { opacity: 0; animation: spark 3.2s linear infinite; animation-delay: var(--d); }
@keyframes rise { from { transform: scaleY(0); } }
@keyframes show { from { opacity: 0; } }
@keyframes drop {
  0% { transform: translateY(-90px); opacity: 0; animation-timing-function: cubic-bezier(.5, 0, 1, .6); }
  12% { opacity: 1; }
  58% { transform: translateY(0); animation-timing-function: cubic-bezier(0, .5, .5, 1); }
  76% { transform: translateY(-11px); animation-timing-function: cubic-bezier(.5, 0, 1, .5); }
  100% { transform: translateY(0); }
}
@keyframes flex { 0%, 100% { transform: rotate(0); } 30% { transform: rotate(var(--r)); } 60% { transform: rotate(calc(var(--r) * -.4)); } }
@keyframes plank { from { opacity: 0; transform: translateY(7px); } }
@keyframes tilt { from { transform: rotate(0); } }
@keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
@keyframes blink { 0%, 90%, 97%, 100% { transform: scaleY(1); } 93.5% { transform: scaleY(.1); } }
@media (prefers-reduced-motion: reduce) { .rise, .ap, .drop, .flex, .plank, .tilt, .bob, .blink, .hop { animation: none !important; } .spark { display: none; } }
@media print { .rise, .ap, .drop, .flex, .plank, .tilt, .bob, .blink, .hop { animation: none !important; } .spark { display: none; } }
</style>
</head>
<body>
<svg id="pic" viewBox="0 0 1000 560" role="img" aria-label="__LABEL__"></svg>
<script>
"use strict";
const DATA = __DATA__;
const NS = "http://www.w3.org/2000/svg", svg = document.getElementById("pic");
const el = (p, tag, attrs, text) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (text != null) e.textContent = text; p.appendChild(e); return e; };
const f = v => (+v).toFixed(1);

/* The scene: two pillars on one floor, each a front face, a top face receding by the depth vector (DX, DY) and a right
   side face; between their tops a staircase of N planks with the same depth. Pillar height: K px per point. */
const FLOOR = 470, K = 3.35, PW = 190, XL = 150, XR = 660, DX = 22, DY = -16;
const N = 7, BW = 42, BT = 8;  // planks: number, width, thickness
const T_RISE = .1, T_DROP = 1.0, T_FLEX = 1.6, T_PLANK = 1.8, DT_PLANK = .24, T_HOP = 3.6, HOP = .4, HOLD = .3;
const yL = FLOOR - K * DATA.lo, yR = FLOOR - K * DATA.rl;
const step = (yL - yR) / (N + 1), pitch = (XR - (XL + PW)) / N;
const plank = i => ({ x: XL + PW + i * pitch + (pitch - BW) / 2, y: yL - (i + 1) * step });
const standPlank = i => { const p = plank(i); return [p.x + BW / 2 + DX / 2, p.y + DY / 2]; };
const standPillar = x0 => [x0 + PW / 2 + DX / 2, (x0 === XL ? yL : yR) + DY / 2];
const hop1 = T_HOP + HOP, hop2 = hop1 + HOLD + HOP;  // the times the base robot lands on plank 0 and plank 1

const defs = el(svg, "defs", {});
const grad = (id, stops, x2, y2) => { const g = el(defs, "linearGradient", { id, x1: 0, y1: 0, x2, y2 }); for (const [o, c] of stops) el(g, "stop", { offset: o, style: `stop-color:var(${c})` }); };
grad("gFront", [[0, "--glass-hi"], [.55, "--glass"], [1, "--glass-lo"]], 1, 1);
grad("gTop", [[0, "--glass-hi"], [1, "--glass"]], 1, 0);
grad("gPlate", [[0, "--glass-lo"], [1, "--glass"]], 0, 1);
const rg = el(defs, "radialGradient", { id: "gBloom" });
el(rg, "stop", { offset: 0, style: "stop-color:var(--glass-hi)" }); el(rg, "stop", { offset: 1, style: "stop-color:var(--glass-hi);stop-opacity:0" });
const blur = el(defs, "filter", { id: "fBlur", x: "-20%", y: "-200%", width: "140%", height: "500%" });
el(blur, "feGaussianBlur", { stdDeviation: 7 });
const keyframes = el(document.head, "style", {});

/* a glass box: right side face, front face, top face */
function box(g, x, y, w, h, frontCls, topCls) {
  el(g, "path", { d: `M${f(x + w)} ${f(y)}l${DX} ${DY}v${f(h)}l${-DX} ${-DY}Z`, class: "side" });
  el(g, "path", { d: `M${f(x)} ${f(y)}h${f(w)}v${f(h)}h${f(-w)}Z`, class: frontCls, fill: "url(#gFront)" });
  el(g, "path", { d: `M${f(x)} ${f(y)}h${f(w)}l${DX} ${DY}h${f(-w)}Z`, class: topCls, fill: "url(#gTop)" });
}
const outline = (x, y, w, h) => `M${f(x)} ${f(y + h)}V${f(y)}l${DX} ${DY}h${f(w)}v${f(h)}l${-DX} ${-DY}H${f(x)}`;

/* The robot, feet at (0, 0): feet, body, arms, head with a face plate, two eyes and an antenna. lit: the trained one. */
function robot(g, lit) {
  el(g, "ellipse", { cx: 0, cy: 0, rx: 28, ry: 5, class: "shade", opacity: .7 });
  for (const s of [-1, 1]) el(g, "rect", { x: s > 0 ? 3 : -17, y: -9, width: 14, height: 9, rx: 4.5, class: "glass", fill: "url(#gFront)" });
  for (const s of [-1, 1]) {
    /* arms: down and a little out on the base robot; a flex (upper arm out, forearm up) on the trained one */
    const d = lit ? `M${s * 27} -38H${s * 41}V-56` : `M${s * 27} -40l${s * 6} 21`;
    const a = el(g, "g", lit ? { class: "flex", style: `--d:${T_FLEX}s;--r:${s * -14}deg;transform-origin:${s * 27}px -38px` } : {});
    el(a, "path", { d, class: "armrim" });
    el(a, "path", { d, class: "arm", stroke: "url(#gFront)" });
    if (lit) el(a, "circle", { cx: s * 41, cy: -59, r: 6.5, class: "glass", fill: "url(#gFront)" });
  }
  el(g, "rect", { x: -26, y: -49, width: 52, height: 41, rx: 13, class: "glass", fill: "url(#gFront)" });
  el(g, "rect", { x: -7, y: -38, width: 14, height: 4, rx: 2, class: lit ? "lit" : "dot", opacity: lit ? .9 : .35 });
  const head = el(g, "g", lit ? {} : { class: "tilt", style: `--d:${hop2 + .15}s;transform-origin:0 -50px` });
  el(head, "line", { x1: 0, y1: -98, x2: 0, y2: -111, class: "stick" });
  if (lit) el(head, "circle", { cx: 0, cy: -115, r: 11, class: "glowball" });
  el(head, "circle", { cx: 0, cy: -115, r: 5, class: lit ? "lit" : "ball" });
  el(head, "rect", { x: -32, y: -99, width: 64, height: 49, rx: 14, class: "glass", fill: "url(#gFront)" });
  el(head, "path", { d: "M-24 -93q2 -3 8 -3h10", class: "sheen" });
  if (lit) el(head, "path", { d: "M-31.4 -92.5H31.4", class: "litline", style: "stroke-width:2.6;stroke-linecap:butt" });
  el(head, "rect", { x: -24, y: -88, width: 48, height: 30, rx: 9, class: "plate", fill: "url(#gPlate)" });
  const eyes = el(head, "g", lit ? { class: "blink", style: `--d:${T_FLEX + 1.2}s` } : {});
  if (lit) {
    for (const s of [-1, 1]) {
      const d = `M${s * 9 - 6} -70q6 -8 12 0`;
      el(eyes, "path", { d, class: "glowline" });
      el(eyes, "path", { d, class: "litline" });
    }
  } else {
    for (const s of [-1, 1]) el(eyes, "circle", { cx: s * 9 + 3.2, cy: -76.5, r: 3.4, class: "dot" });
  }
}

function draw() {
  el(svg, "ellipse", { cx: 510, cy: 300, rx: 520, ry: 300, fill: "url(#gBloom)", class: "bloom" });
  el(svg, "path", { d: `M${XL + 10} ${FLOOR - 4}L${XR + PW + 30} ${FLOOR - 12}L${XR + PW + 70} ${FLOOR + 8}L${XL + 40} ${FLOOR + 12}Z`, class: "shade", filter: "url(#fBlur)" });
  el(svg, "path", { d: `M${XL - 60} ${FLOOR}H${XR + PW + 80}`, class: "floor" });
  el(svg, "text", { x: 510, y: FLOOR + 50, class: "cap" }, DATA.bench);

  /* the pillars rise from the floor, then their numbers appear */
  [[XL, yL, DATA.loText, "Base model"], [XR, yR, DATA.rlText, "RL-trained model"]].forEach(([x0, top, score, name], i) => {
    const g = el(svg, "g", { class: "rise", style: `--d:${T_RISE + i * .08}s` });
    box(g, x0, top, PW, FLOOR - top, "front", "top");
    el(svg, "text", { x: x0 + PW / 2, y: top + 72, class: "score ap", style: `--d:${T_RISE + .75}s` }, score + " %");
    el(svg, "text", { x: x0 + PW / 2, y: top + 104, class: "name ap", style: `--d:${T_RISE + .85}s` }, name);
  });

  /* the bridge: each plank first a dashed outline, the first two then solid lit glass as the robot lands */
  for (let i = 0; i < N; i++) {
    const { x, y } = plank(i);
    const g = el(svg, "g", { class: "plank", style: `--d:${(T_PLANK + i * DT_PLANK).toFixed(2)}s` });
    el(g, "path", { d: outline(x, y, BW, BT) + "Z", class: "todo" });
    el(g, "path", { d: `M${f(x)} ${f(y)}h${BW}l${DX} ${DY}M${f(x + BW)} ${f(y)}v${BT}`, class: "todo edge" });
    if (i < 2) {
      const s = el(svg, "g", { class: "done ap", style: `--d:${(i ? hop2 : hop1).toFixed(2)}s` });
      el(s, "path", { d: outline(x, y, BW, BT) + "Z", class: "halo" });
      box(s, x, y, BW, BT, "front", "top");
      el(s, "path", { d: outline(x, y, BW, BT) + "Z", class: "rimb" });
      el(s, "path", { d: `M${f(x)} ${f(y)}h${BW}l${DX} ${DY}M${f(x + BW)} ${f(y)}v${BT}`, class: "rimb", style: "stroke-width:.8" });
    }
  }

  /* the spark: up the planks still to be built, to the top of the RL pillar */
  const pts = [];
  for (let i = 2; i < N; i++) pts.push(standPlank(i));
  pts.push([XR + 16 + DX / 2, yR + DY / 2]);
  const sp = el(svg, "g", { class: "spark", style: `--d:${(hop2 + .9).toFixed(2)}s` });
  el(sp, "circle", { cx: 0, cy: 0, r: 9, class: "aura" });
  el(sp, "circle", { cx: 0, cy: 0, r: 3.6, class: "core" });
  const span = 42;  // percent of the cycle the run takes
  let kf = pts.map(([x, y], k) => `${(k / (pts.length - 1) * span).toFixed(1)}% { transform: translate(${f(x)}px, ${f(y - 4)}px);${k === 0 ? " opacity: 0;" : ""} }`);
  kf.splice(1, 0, `${(span * .06).toFixed(1)}% { opacity: 1; }`);
  kf.push(`${(span * .94).toFixed(1)}% { opacity: 1; }`, `${span + 4}%, 100% { opacity: 0; transform: translate(${f(pts.at(-1)[0])}px, ${f(pts.at(-1)[1] - 4)}px); }`);

  /* the trained robot, standing on its pillar */
  const [rx, ry] = standPillar(XR);
  const rg2 = el(svg, "g", { transform: `translate(${f(rx)} ${f(ry)})` });
  robot(el(rg2, "g", { class: "drop", style: `--d:${T_DROP + .08}s` }), true);

  /* the base robot: it rests on plank 1; before that it drops on its pillar and hops over plank 0 */
  const [bx, by] = standPlank(1), [px, py] = standPillar(XL), [qx, qy] = standPlank(0);
  const bg = el(svg, "g", { transform: `translate(${f(bx)} ${f(by)})` });
  const hop = el(bg, "g", { class: "hop" });
  const T = hop2 - T_HOP, at = t => (100 * (t - T_HOP) / T).toFixed(1) + "%";
  const tr = (x, y) => `transform: translate(${f(x - bx)}px, ${f(y - by)}px);`;
  const up = "animation-timing-function: cubic-bezier(.3, .6, .6, 1);", down = "animation-timing-function: cubic-bezier(.4, 0, .7, .4);";
  keyframes.textContent = `@keyframes spark { ${kf.join(" ")} }
@keyframes hop {
  0% { ${tr(px, py)} ${up} }
  ${at(T_HOP + HOP * .45)} { ${tr((px + qx) / 2, Math.min(py, qy) - 34)} ${down} }
  ${at(hop1)} { ${tr(qx, qy)} }
  ${at(hop1 + HOLD)} { ${tr(qx, qy)} ${up} }
  ${at(hop1 + HOLD + HOP * .45)} { ${tr((qx + bx) / 2, Math.min(qy, by) - 34)} ${down} }
  100% { transform: translate(0, 0); }
}
.hop { animation: hop ${T.toFixed(2)}s both; animation-delay: ${T_HOP}s; }`;
  robot(el(el(hop, "g", { class: "bob", style: `--d:${(hop2 + .7).toFixed(2)}s` }), "g", { class: "drop", style: `--d:${T_DROP}s` }), false);
}

(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(draw);
</script>
</body>
</html>
"""


def page(lo, rl, bench):
    """The picture-alone page: the base model at lo % and the RL-trained model at rl % on bench."""
    data = {"lo": lo, "rl": rl, "bench": bench, "loText": f"{round(lo)}", "rlText": f"{round(rl)}"}
    label = f"Base model {round(lo)} %, RL-trained model {round(rl)} % on {bench}, and a bridge between them being built"
    return (PAGE.replace("__LABEL__", label.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;"))
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
