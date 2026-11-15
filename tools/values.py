"""The page /values: the six values the team works by, with the words of the people they come from.

view.py serves PAGE at /values; it is not a header tab and is reached from the home dial. The picture is a hexagonal
glass prism seen from slightly above, one face per value. One beam of light enters the top of the prism and leaves
it as six rays, one through each face, to a bead on a ring around it; each bead names a value. The selected value's
face turns to the front and shows its number and name, and the column beside the picture holds the value: its
sentence, its quotes with their sources, and the line of AGENTS.md that states it for the agents; above it, one
sentence says what the six values are and what AGENTS.md is. A click on a bead,
a name or a face, the arrow keys or the buttons at the bottom of the column select a value (address /values#speed).
The prism sways a few degrees and leans toward the mouse; the tick ring drifts at its own slow rate. Nothing on the
page is data and nothing replays. The text of each value is the person's own (2026-11-15), with typing errors fixed; the
lead of Speed is the first sentence of its line in AGENTS.md, with cycle time explained, because nothing on the site supports the sentence it
replaced.
"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Values</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens, the light and the type of the Design page (architecture.py). --face is how much of a glass face hides
   what is behind it: porcelain hides all of it, glass lets the inner rays show. --far is the opacity of the farthest
   bead and its name (the script reads it): higher on the light page, where a faint name loses its contrast. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #cbd2d8;
  --blue: #1f43d6; --red: #c41e34; --on-blue: #fff;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue); --face: .97; --sheen: #ffffff; --sink: #101820; --far: .66;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18); --btn-drop: rgba(16, 24, 32, .42);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff; --face: .74; --sheen: #ffffff; --sink: #000000; --far: .5;
    --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7); --btn-drop: rgba(0, 0, 0, .6);
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
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(360px, 31vw); grid-template-rows: auto minmax(0, 1fr) auto;
  column-gap: 0; height: 100vh; min-height: 660px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 22px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top .name a, .top .name a:hover { color: var(--ink); }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.here { color: var(--ink); font-weight: 600; white-space: nowrap; }  /* the current page, after the last link */

/* The picture */
.stage { grid-column: 1; grid-row: 2; min-height: 0; min-width: 0; display: flex; padding: 8px 24px 0 0; }
svg { width: 100%; height: 100%; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); text-anchor: middle; font-stretch: 110%; letter-spacing: .012em; }
.atmo, .shade, .bloom, .refl, .ring, .ticks, .inner, .beam, .sheen, .spec, .edge, .facetext, .ray { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.bloom { opacity: var(--bloom); }
.refl { opacity: calc(var(--glow) * .16); }
.ring, .ticks { fill: none; stroke: var(--ink); stroke-linecap: round; }
.ring.back { stroke-width: .7; opacity: .26; }
.ring.front { stroke-width: 1.3; opacity: .7; }
.ticks.back { stroke-width: .6; opacity: .22; }
.ticks.front { stroke-width: 1; opacity: .55; }
.face { cursor: pointer; }
.face .fill { fill-opacity: var(--face); stroke: none; }
.face.back .fill { fill-opacity: calc(var(--face) * .5); }
.face.back .sheen { display: none; }
.sheen { fill: url(#sheen); }
.spec { fill: url(#specg); opacity: var(--spec); }
.cap { fill-opacity: var(--face); }
.edge { fill: none; stroke-linejoin: round; stroke-linecap: round; }
.edge.back { stroke: var(--ink); stroke-width: .7; opacity: .28; }
.edge.front { stroke: url(#rim) var(--ink); stroke-width: 1.5; }
.inner { fill: none; stroke: var(--core); stroke-linecap: round; opacity: calc(var(--glow) * .5); }
.inner.on { stroke: var(--blue); opacity: calc(var(--glow) * .9); }
.beam { fill: url(#beamg); }
.spot { pointer-events: none; opacity: calc(.35 + var(--glow) * .65); }
.ray { fill: none; stroke: var(--ink); stroke-linecap: round; }
.ray.on { stroke: var(--blue); }
.facetext .n { font-weight: 200; letter-spacing: -.02em; }
.bead { cursor: pointer; }
.bead:focus { outline: none; }
.bead circle.b { fill: url(#body) var(--sheet); stroke: var(--ink); stroke-width: 1.2; }
.bead.on circle.b { stroke: var(--blue); stroke-width: 2.4; }
.bead:focus-visible circle.b { stroke: var(--blue); stroke-width: 3.2; }
.bead circle.pad { fill: transparent; }
.bead text { font-weight: 540; paint-order: stroke fill; stroke: var(--paper); stroke-width: 6px; stroke-linejoin: round; }
.bead.on text { font-weight: 680; fill: var(--blue); }

/* One entrance: the prism fades up, the rays draw out from it, the beads arrive in order */
@keyframes fade { from { opacity: 0; } }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } }
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes pop { from { transform: scale(0); } }
.bead circle.b { transform-box: fill-box; transform-origin: center; }
.enter #prism { animation: rise 1.2s cubic-bezier(.2, .7, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .refl, .enter .bloom { animation: fade 1.8s .2s both; }
.enter .ring, .enter .ticks { animation: fade 1s .4s both; }
.enter .beam, .enter .spot { animation: fade 1.2s .9s both; }
.enter .ray { stroke-dasharray: 1; animation: draw .9s cubic-bezier(.6, 0, .2, 1) both; animation-delay: calc(1.1s + var(--i) * 70ms); }
.enter .bead circle.b { animation: pop .45s cubic-bezier(.3, 1.5, .5, 1) both; animation-delay: calc(1.5s + var(--i) * 70ms); }
.enter .bead text { animation: fade .6s both; animation-delay: calc(1.6s + var(--i) * 70ms); }

/* The words */
.side {
  grid-column: 2; grid-row: 2 / 4; min-width: 0; min-height: 0; overflow: hidden auto; scrollbar-width: thin;
  padding: clamp(20px, 5vh, 64px) 4px 24px 40px; border-left: 1px solid var(--rule);
}
.about { margin: 0 0 22px; padding-bottom: 14px; border-bottom: 1px solid var(--rule); font-size: 13.5px; line-height: 1.45; color: var(--mute); text-wrap: pretty; }
.about, .quotes, .rule { max-width: 396px; }  /* one width, so the column's hairlines end at the same place */
.card { animation: rise .5s cubic-bezier(.2, .7, .2, 1) both; }
.kick { margin: 0; font-size: 13px; color: var(--mute); font-weight: 500; }
.kick b { color: var(--blue); font-weight: 650; }
.title { margin: 6px 0 0; font-size: clamp(40px, 3.5vw, 62px); line-height: 1.02; font-weight: 300; font-stretch: 100%; letter-spacing: -.024em; max-width: 12ch; text-wrap: balance; }
.lead { margin: 20px 0 0; font-size: clamp(17px, 1.24vw, 20px); line-height: 1.42; font-weight: 360; max-width: 34ch; text-wrap: pretty; }
.lead + .lead { margin-top: 12px; }
.quotes { list-style: none; margin: 26px 0 0; padding: 0; }
.quotes li { padding: 16px 0 17px; border-top: 1px solid var(--rule); }
.quotes .k { margin: 0 0 6px; font-size: 12.5px; font-weight: 600; color: var(--mute); }
.quotes blockquote { margin: 0; font-size: 15.5px; line-height: 1.55; font-weight: 400; text-wrap: pretty; }
.quotes blockquote.q { text-indent: -.42em; }
.quotes .by { margin: 8px 0 0; font-size: 13px; color: var(--mute); }
.quotes .by b { color: var(--ink); font-weight: 600; }
.quotes .by a { text-decoration-thickness: 1px; text-underline-offset: 3px; text-decoration-color: var(--faint); }
.quotes .by a:hover { color: var(--ink); text-decoration-color: var(--blue); }
.rule { margin: 4px 0 0; padding: 16px 0 0; border-top: 1px solid var(--rule); }
.rule h3 { margin: 0; font-size: 12.5px; font-weight: 600; color: var(--mute); }
.rule p { margin: 4px 0 0; font-size: 14.5px; line-height: 1.5; color: var(--mute); }
.nav { display: flex; align-items: center; gap: 10px; margin: 26px 0 8px; flex-wrap: wrap; }
.nav button { padding: 9px 18px; border-radius: 999px; border: 1px solid var(--faint); font-weight: 600; font-size: 14px; white-space: nowrap; transition: background .15s ease, border-color .15s ease, color .15s ease; }
.nav button.next { background: var(--btn); color: var(--btn-ink); border-color: transparent; box-shadow: inset 0 1px 0 var(--btn-edge), 0 14px 28px -14px var(--btn-drop); }
.nav button:hover { border-color: var(--blue); background: var(--blue); color: var(--on-blue); box-shadow: none; }

@media (max-width: 900px) {
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .stage { padding: 4px 0 0; display: block; margin-inline: -16px; }  /* the picture runs to the screen's edges, so its names reach 12 px */
  svg { height: auto; }
  .side { border-left: 0; padding: 18px 0 0; overflow: visible; }
  .title { font-size: 42px; }
  .lead { font-size: 18px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter *, .card { animation: none !important; }
  .nav button { transition: none; }
}
</style>
</head>
<body>
<div class="page" id="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings">Findings</a>
    <span class="here">Values</span>
  </header>
  <div class="stage"><svg id="svg" role="group" aria-label="A glass prism with one face for each of the six values; one beam enters it and leaves as six rays, one to each value"></svg></div>
  <aside class="side" id="side">
    <p class="about">These are the six values the team works by. They are the first section of AGENTS.md, the rules file that every agent of the team reads at the start of a session.</p>
    <div id="card" aria-live="polite"></div>
  </aside>
</div>
<script>
const $ = id => document.getElementById(id);
/* The six values, in the order of AGENTS.md. short is the bead's name; lead is the person's own sentences; each quote
   has its text, who said it and where; q: false marks a paraphrase that carries its own quotation marks; rule is the
   line of AGENTS.md that states the value for the agents, word for word. */
const VALUES = [
  { id: "speed", short: "Speed", title: "Speed",
    lead: ["Cycle time, the time from an idea to its measured result, decides research output."],
    quotes: [{ q: "By far the best researchers I've seen, they all have the ability to try experiments really, really, really, really, really fast. That's cycle time at smaller scales. Cycle time separates people.", who: "Sholto Douglas" }],
    rule: "Cycle time decides research output. Prefer the experiment that answers in minutes over the one that answers in hours, and run it now." },
  { id: "enthusiasm", short: "Enthusiasm", title: "Enthusiasm",
    lead: ["Neuroscience, psychology and three religious traditions describe the same thing: joy in the pursuit is itself a source of strength."],
    quotes: [
      { q: "Dopamine is not about the happiness of reward. It’s about the happiness of the pursuit of reward… It is about the motivation arising from those dopaminergic projections to the prefrontal cortex that is needed to do the harder thing (i.e., to work).", who: "Robert Sapolsky", src: "Behave: The Biology of Humans at Our Best and Worst" },
      { k: "The law of deep reserves", q: "Everyone knows on any given day that there are energies slumbering in him which the incitements of that day do not call forth… Excitements, ideas, and efforts, in a word, are what carry us over the dam… We tap a level of new energy, masked until then by the fatigue-obstacle usually obeyed.", who: "William James", src: "father of American psychology, The Energies of Men (1907)" },
      { q: "The joy of the Lord is your strength.", who: "Nehemiah 8:10" },
      { q: "Those who “strive hard in Our cause” are effortlessly “guided to Our ways.”", plain: true, who: "Qur’an 29:69" },
      { q: "What is enthusiasm? It is joy in virtue… Without enthusiasm, there is no merit, just as there is no movement without the wind.", who: "Shantideva", src: "Bodhicaryāvatāra 7.1–2" },
    ],
    rule: "Pursue the work with energy." },
  { id: "novelty", short: "Novelty", title: "Practicality, novelty and interestingness",
    lead: ["The ultimate goal is a novel practical win. But practical wins are extremely hard.",
           "While a practical win is the ultimate goal, genuine novelty can be an intermediate win. And the path to novelty is interestingness."],
    quotes: [{ k: "Recommended reading", q: "Why Greatness Cannot Be Planned: The Myth of the Objective", plain: true, who: "Kenneth O. Stanley and Joel Lehman", src: "2015. Stanley is the AI scientist behind NEAT (a method that evolves neural networks) and novelty search." }],
    rule: "The goal is a novel practical win. A genuinely novel result is an intermediate win, and interesting results are the path to novelty." },
  { id: "bitter-lesson", short: "Bitter lesson", title: "The bitter lesson",
    lead: ["Smarter models and scale always win."],
    quotes: [{ q: "The biggest lesson that can be read from 70 years of AI research is that general methods that leverage computation are ultimately the most effective, and by a large margin.", who: "Rich Sutton", src: "The Bitter Lesson (2019)", href: "http://www.incompleteideas.net/IncIdeas/BitterLesson.html" }],
    rule: "Larger models and more compute win. Prefer methods that improve with scale over hand-engineered ones." },
  { id: "asymmetry", short: "Asymmetry", title: "Asymmetry",
    lead: ["When facing a larger, established player, such as institutions, labs, organizations and corporations, your choices are either total obedience or escape from its rules, using the advantages it lacks.",
           "As a small team with very limited resources, we have to use every advantage a small team has over a large one: flexibility, versatility, speed and innovation, overlooked opportunities and good ol’ hustle."],
    quotes: [],
    rule: "We are a small team. Use flexibility, speed and overlooked opportunities that large labs pass over." },
  { id: "clean-context", short: "Clean context", title: "Clean context",
    lead: ["This value is specific to large language models (LLMs). Because of how attention works, real estate in the context window is more valuable than penthouses in downtown SF.",
           "The smaller and cleaner, the better the performance. A tongue-in-cheek heuristic: performance scales quadratically with how clean the context is."],
    quotes: [],
    rule: "Keep every agent's context small: read papers, long logs and large files in subagents, and bring back only what the task needs." },
];
const N = VALUES.length, STEP = 360 / N, RAD = Math.PI / 180;
const still = matchMedia("(prefers-reduced-motion: reduce)");
const narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1);
const S = { sel: 0, rot: 0, to: 0, t: 30, last: 0, mx: 0, my: 0, lx: 0, ly: 0 };

/* Geometry, in the units of the viewBox. The prism stands with its middle at the ring's height: a is the distance from
   its axis to a face, h half its height, R the ring of beads. The pitch is high enough that the ring passes wholly
   above and below the prism, so no name and no line ever crosses it. */
function geo() {
  return narrow.matches
    ? { w: 720, h: 486, cx: 360, cy: 258, a: 78, hh: 80, R: 222, D: 1700, pitch: 40, bead: 13, fs: 26, fn: 88, edge: -8 }
    : { w: 1000, h: 700, cx: 500, cy: 340, a: 106, hh: 108, R: 336, D: 2300, pitch: 37, bead: 8.5, fs: 16, fn: 84, edge: 1e4 };
}
let G = geo();
const V = { cy: 1, sy: 0, cp: 1, sp: 0, yaw: 0 };
function aim(yaw, pitch) { V.yaw = yaw; V.cy = Math.cos(yaw * RAD); V.sy = Math.sin(yaw * RAD); V.cp = Math.cos(pitch * RAD); V.sp = Math.sin(pitch * RAD); }
function proj(x, y, z) {  // to the screen: [x, y, scale, depth]; z > 0 is the near side, y > 0 is down
  const x1 = x * V.cy + z * V.sy, z1 = z * V.cy - x * V.sy, y2 = y * V.cp + z1 * V.sp, z2 = z1 * V.cp - y * V.sp, k = G.D / (G.D - z2);
  return [G.cx + x1 * k, G.cy + y2 * k, k, z2];
}
function turn(x, y, z) {  // a direction in the view, without perspective: for the light
  const x1 = x * V.cy + z * V.sy, z1 = z * V.cy - x * V.sy;
  return [x1, y * V.cp + z1 * V.sp, z1 * V.cp - y * V.sp];
}
const LIGHT = (() => { const l = [-.56, -.64, .52], n = Math.hypot(...l); return l.map(v => v / n); })();  // from the upper left, toward the viewer
const angleOf = k => 90 - (k - S.rot) * STEP;  // value k's face and bead; the selected one is at 90 degrees, the front
const pt = p => f(p[0]) + "," + f(p[1]);
const NS = "http://www.w3.org/2000/svg";
const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };

let E = {};
function build() {
  G = geo();
  G.far = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--far")) || .5;
  const svg = $("svg");
  svg.setAttribute("viewBox", `0 0 ${G.w} ${G.h}`);
  const stop = (o, c, a = 1) => `<stop offset="${o}" stop-color="${c}" stop-opacity="${a}"/>`;
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".36" cy=".3" r=".86">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".12" y1=".08" x2=".9" y2=".94">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.2, "var(--blue)", .16)}${stop(.6, "var(--blue)", .05)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shadeg">${stop(.25, "var(--ink)", .22)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="bloomg">${stop(0, "var(--core)", .7)}${stop(.3, "var(--blue)", .22)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">${stop(0, "var(--sheen)", .16)}${stop(.42, "var(--sheen)", 0)}${stop(.7, "var(--sink)", 0)}${stop(1, "var(--sink)", .16)}</linearGradient>` +
    `<linearGradient id="specg" x1="0" y1="0" x2="0" y2="1">${stop(0, "#fff", 0)}${stop(.18, "#fff", .5)}${stop(.6, "#fff", .14)}${stop(1, "#fff", 0)}</linearGradient>` +
    `<linearGradient id="beamg" gradientUnits="userSpaceOnUse">${stop(0, "var(--core)", 0)}${stop(.7, "var(--core)", .22)}${stop(1, "var(--core)", .6)}</linearGradient>` +
    `<linearGradient id="reflfade" gradientUnits="userSpaceOnUse" x1="0" x2="0">${stop(0, "#fff", 1)}${stop(1, "#fff", 0)}</linearGradient>` +
    `<mask id="reflm" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="5000" height="5000"><rect x="-2000" y="-2000" width="5000" height="5000" fill="url(#reflfade)"/></mask>` +
    "</defs>";
  E = {};
  E.atmo = el("ellipse", { class: "atmo", fill: "url(#atmo)" }, svg);
  E.shade = el("ellipse", { class: "shade", fill: "url(#shadeg)" }, svg);
  E.refl = el("g", { class: "refl", mask: "url(#reflm)" }, svg);
  E.reflFaces = VALUES.map(() => el("polygon", {}, E.refl));
  E.ringB = el("path", { class: "ring back" }, svg);
  E.tickB = el("path", { class: "ticks back" }, svg);
  E.behind = el("g", {}, svg);  // rays and beads on the far side of the prism
  E.prism = el("g", { id: "prism" }, svg);
  E.backFaces = el("g", {}, E.prism);
  E.edgeB = el("path", { class: "edge back" }, E.prism);
  E.bloom = el("ellipse", { class: "bloom", fill: "url(#bloomg)" }, E.prism);
  E.inner = VALUES.map(() => el("path", { class: "inner" }, E.prism));
  E.shaft = el("path", { class: "inner", "stroke-width": 1.4 }, E.prism);
  E.frontFaces = el("g", {}, E.prism);
  E.cap = el("polygon", { class: "cap" }, E.prism);
  E.capSheen = el("polygon", { class: "sheen" }, E.prism);
  E.spec = el("polygon", { class: "spec" }, E.prism);
  E.edgeF = el("path", { class: "edge front" }, E.prism);
  E.faceText = el("g", { class: "facetext" }, E.prism);
  E.num = el("text", { class: "n" }, E.faceText);
  E.ringF = el("path", { class: "ring front" }, svg);
  E.tickF = el("path", { class: "ticks front" }, svg);
  E.front = el("g", {}, svg);
  E.beam = el("polygon", { class: "beam" }, svg);
  E.spot = el("ellipse", { class: "spot", fill: "url(#bloomg)" }, svg);
  E.beamG = svg.querySelector("#beamg");
  E.reflG = svg.querySelector("#reflfade");
  E.faces = VALUES.map((v, k) => {
    const g = el("g", { class: "face" }, E.backFaces);
    g.dataset.k = k;
    return { g, fill: el("polygon", { class: "fill" }, g), sheen: el("polygon", { class: "sheen" }, g), front: false };
  });
  E.beads = VALUES.map((v, k) => {
    const g = el("g", { class: "bead", tabindex: 0, role: "button", "aria-label": "Show the value " + v.title }, E.front);
    g.dataset.k = k; g.style.setProperty("--i", k);
    const ray = el("path", { class: "ray", pathLength: 1 }, g);
    ray.style.setProperty("--i", k);
    const b = { g, ray, pad: el("circle", { class: "pad" }, g), dot: el("circle", { class: "b" }, g), text: el("text", {}, g), near: true, w: 0 };
    b.text.textContent = v.short;
    return b;
  });
  E.beads.forEach(b => { b.text.setAttribute("font-size", G.fs); b.w = b.text.getComputedTextLength(); });
  mark();
  draw();
}

/* One frame: the light on each face, which faces and beads are in front, every position. */
function draw() {
  const sway = still.matches ? 0 : 1;
  aim(sway * (3.4 * Math.sin(S.t / 7) + 5 * S.lx), G.pitch + sway * (1.5 * Math.sin(S.t / 9.5) + 3 * S.ly));
  const { a, hh, R } = G, rv = a / Math.cos(30 * RAD);
  const top = [], bot = [], ang = [];
  for (let k = 0; k < N; k++) {  // vertex k sits between face k and face k + 1
    const th = (angleOf(k) - STEP / 2) * RAD;
    ang.push(th);
    top.push(proj(rv * Math.cos(th), -hh, rv * Math.sin(th)));
    bot.push(proj(rv * Math.cos(th), hh, rv * Math.sin(th)));
  }
  const corners = k => [top[(k + N - 1) % N], top[k], bot[k], bot[(k + N - 1) % N]];  // face k: from vertex k - 1 to vertex k
  const lit = n => { const v = turn(...n); return Math.max(0, v[0] * LIGHT[0] + v[1] * LIGHT[1] + v[2] * LIGHT[2]); };
  const facing = [];
  let best = -1, bestLam = -1;
  E.faces.forEach((F, k) => {
    const c = corners(k);
    const area = (c[1][0] - c[0][0]) * (c[2][1] - c[0][1]) - (c[2][0] - c[0][0]) * (c[1][1] - c[0][1]);
    const front = area > 0;
    facing.push(front);
    if (front !== F.front) { F.front = front; (front ? E.frontFaces : E.backFaces).appendChild(F.g); F.g.classList.toggle("back", !front); }
    const th = angleOf(k) * RAD, lam = lit([Math.cos(th), 0, Math.sin(th)]);
    if (front && lam > bestLam) { bestLam = lam; best = k; }
    const p = c.map(pt).join(" ");
    F.fill.setAttribute("points", p);
    F.fill.style.fill = `color-mix(in oklab, var(--glass-hi) ${f(8 + 90 * Math.pow(lam, .8))}%, var(--glass-lo))`;
    if (front) F.sheen.setAttribute("points", p);
    E.reflFaces[k].style.display = front ? "" : "none";
    if (front) {  // the face mirrored in the floor under the prism
      const m = [-1, 0].map(o => { const th2 = ang[(k + N + o) % N]; return [rv * Math.cos(th2), rv * Math.sin(th2)]; });
      const r = [proj(m[0][0], hh, m[0][1]), proj(m[1][0], hh, m[1][1]), proj(m[1][0], 3 * hh, m[1][1]), proj(m[0][0], 3 * hh, m[0][1])];
      E.reflFaces[k].setAttribute("points", r.map(pt).join(" "));
      E.reflFaces[k].style.fill = F.fill.style.fill;
    }
  });
  const capP = top.map(pt).join(" ");
  E.cap.setAttribute("points", capP);
  E.cap.style.fill = `color-mix(in oklab, var(--glass-hi) ${f(18 + 78 * lit([0, -1, 0]))}%, var(--glass-lo))`;
  E.capSheen.setAttribute("points", capP);

  /* Edges: an edge is drawn in front when a face beside it faces the viewer; the top rim always does. */
  let fe = "M" + top.map(pt).join("L") + "Z", be = "";
  for (let k = 0; k < N; k++) {
    const vert = "M" + pt(top[k]) + "L" + pt(bot[k]);
    if (facing[k] || facing[(k + 1) % N]) fe += vert; else be += vert;
    const base = "M" + pt(bot[(k + N - 1) % N]) + "L" + pt(bot[k]);
    if (facing[k]) fe += base; else be += base;
  }
  E.edgeF.setAttribute("d", fe);
  E.edgeB.setAttribute("d", be);

  /* The highlight: a narrow band down the brightest face, near its edge toward the light. */
  if (best >= 0) {
    const c = corners(best), mix = (p, q, t) => [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t];
    const u0 = .1, u1 = .2, tl = c[0], tr = c[1], br = c[2], bl = c[3];
    const s = [mix(tl, tr, u0), mix(tl, tr, u1), mix(bl, br, u1), mix(bl, br, u0)];
    E.spec.setAttribute("points", s.map(pt).join(" "));
    E.spec.style.opacity = `calc(var(--spec) * ${f(.25 + .75 * bestLam)})`;
  }

  /* Light: one beam from the upper left into the top, a shaft down the axis, six spokes out to the faces. */
  const centre = proj(0, 0, 0), topC = proj(0, -hh, 0);
  E.shaft.setAttribute("d", "M" + pt(topC) + "L" + pt(centre));
  const src = proj(-R * 1.25, -hh - R * .95, -R * .3);
  const dx = topC[0] - src[0], dy = topC[1] - src[1], len = Math.hypot(dx, dy), nx = -dy / len, ny = dx / len, wa = .3, wb = 2.6 * topC[2];
  E.beam.setAttribute("points", [[src[0] + nx * wa, src[1] + ny * wa], [topC[0] + nx * wb, topC[1] + ny * wb], [topC[0] - nx * wb, topC[1] - ny * wb], [src[0] - nx * wa, src[1] - ny * wa]].map(pt).join(" "));
  E.beamG.setAttribute("x1", f(src[0])); E.beamG.setAttribute("y1", f(src[1])); E.beamG.setAttribute("x2", f(topC[0])); E.beamG.setAttribute("y2", f(topC[1]));
  E.spot.setAttribute("cx", f(topC[0])); E.spot.setAttribute("cy", f(topC[1])); E.spot.setAttribute("rx", f(a * .32 * topC[2])); E.spot.setAttribute("ry", f(a * .32 * V.sp * topC[2]));
  E.bloom.setAttribute("cx", f(centre[0])); E.bloom.setAttribute("cy", f(centre[1]));
  E.bloom.setAttribute("rx", f(a * .9 * centre[2])); E.bloom.setAttribute("ry", f(hh * .95 * centre[2]));

  /* The ring and its ticks, split at the line where the ring passes behind the prism's axis. */
  const arc = (a0, a1, r) => { let d = ""; for (let t = a0; t <= a1 + .01; t += 5) { const p = proj(r * Math.cos(t * RAD), 0, r * Math.sin(t * RAD)); d += (d ? "L" : "M") + pt(p); } return d; };
  E.ringF.setAttribute("d", arc(V.yaw, V.yaw + 180, R));
  E.ringB.setAttribute("d", arc(V.yaw + 180, V.yaw + 360, R));
  let tf = "", tb = "";
  const drift = S.t * 1.6;
  for (let i = 0; i < 72; i++) {
    const t = i * 5 + drift, long = i % 6 === 0, r0 = R - (long ? 14 : 7), r1 = R - 2;
    const p0 = proj(r0 * Math.cos(t * RAD), 0, r0 * Math.sin(t * RAD)), p1 = proj(r1 * Math.cos(t * RAD), 0, r1 * Math.sin(t * RAD));
    const d = "M" + pt(p0) + "L" + pt(p1);
    if (Math.sin((t - V.yaw) * RAD) > 0) tf += d; else tb += d;
  }
  E.tickF.setAttribute("d", tf);
  E.tickB.setAttribute("d", tb);

  /* Glow, shadow, reflection */
  const floor = proj(0, hh, 0);
  E.atmo.setAttribute("cx", f(centre[0])); E.atmo.setAttribute("cy", f(centre[1])); E.atmo.setAttribute("rx", f(R * 1.15)); E.atmo.setAttribute("ry", f(R * .9));
  const sh = proj(a * .45, hh, -a * .15);
  E.shade.setAttribute("cx", f(sh[0])); E.shade.setAttribute("cy", f(sh[1])); E.shade.setAttribute("rx", f(a * 1.55 * sh[2])); E.shade.setAttribute("ry", f(a * 1.55 * V.sp * sh[2]));
  E.reflG.setAttribute("y1", f(floor[1] - a * .3 * V.sp)); E.reflG.setAttribute("y2", f(floor[1] + hh * 1.1));

  /* Beads, rays and spokes */
  E.beads.forEach((b, k) => {
    const deg = angleOf(k), th = deg * RAD, c = Math.cos(th), s = Math.sin(th);
    const p = proj(R * c, 0, R * s), q = proj(a * c, 0, a * s), near = Math.sin(th - V.yaw * RAD) > -.12;
    if (near !== b.near) { b.near = near; (near ? E.front : E.behind).appendChild(b.g); }
    const depth = (Math.sin(th - V.yaw * RAD) + 1) / 2, on = k === S.sel;
    E.inner[k].setAttribute("d", "M" + pt(centre) + "L" + pt(q));
    E.inner[k].setAttribute("stroke-width", on ? 1.6 : .8);
    b.ray.setAttribute("d", "M" + pt(q) + "L" + pt(p));
    b.ray.setAttribute("stroke-width", f((on ? 1.9 : .6 + .7 * depth) * p[2]));
    b.ray.style.opacity = on ? 1 : f(.2 + .45 * depth);
    const r = G.bead * p[2] * (on ? 1.35 : 1);
    b.dot.setAttribute("cx", f(p[0])); b.dot.setAttribute("cy", f(p[1])); b.dot.setAttribute("r", f(r));
    b.pad.setAttribute("cx", f(p[0])); b.pad.setAttribute("cy", f(p[1])); b.pad.setAttribute("r", f(r + 18));
    let ux = p[0] - centre[0], uy = p[1] - centre[1];
    const ul = Math.hypot(ux, uy) || 1; ux /= ul; uy /= ul;
    const fs = G.fs * p[2], gap = r + 9, w = b.w * p[2];
    const tx = p[0] + ux * (gap + w / 2), cx = Math.max(w / 2 - G.edge, Math.min(G.w + G.edge - w / 2, tx));  // a name stays inside the page's edge
    const clear = Math.sign(uy || 1) * Math.min(1, Math.abs(cx - tx) / gap) * (r + fs);  // and, pushed in over its bead, moves above or below it
    b.text.setAttribute("x", f(cx));
    b.text.setAttribute("y", f(p[1] + uy * (gap + fs * .55) + fs * .34 + clear));
    b.text.setAttribute("font-size", f(fs));
    b.g.style.opacity = (G.far + (1 - G.far) * depth).toFixed(2);
  });

  /* The front face shows the selected value's number and name once the prism has turned to it. */
  const settle = Math.max(0, 1 - Math.abs(S.rot - S.to) * 5);
  const th = angleOf(S.sel) * RAD;
  const at = (y) => proj(a * Math.cos(th), y, a * Math.sin(th));
  const pn = at(-hh * .2);
  E.num.setAttribute("x", f(pn[0])); E.num.setAttribute("y", f(pn[1])); E.num.setAttribute("font-size", f(G.fn * pn[2]));
  E.faceText.style.opacity = f(settle);
}

function frame(now) {
  const dt = Math.min(.05, (now - S.last) / 1000 || 0);
  S.last = now;
  S.t += dt;
  S.rot += (S.to - S.rot) * (1 - Math.exp(-dt * 3.6));
  S.lx += (S.mx - S.lx) * (1 - Math.exp(-dt * 2));
  S.ly += (S.my - S.ly) * (1 - Math.exp(-dt * 2));
  draw();
  requestAnimationFrame(frame);
}

/* The column: the selected value in full. */
function quote(x) {
  const text = x.plain ? esc(x.q) : "“" + esc(x.q) + "”";
  const src = x.src ? (x.href ? `, <a href="${esc(x.href)}" rel="noopener">${esc(x.src)}</a>` : ", " + esc(x.src)) : "";
  return `<li>${x.k ? `<p class="k">${esc(x.k)}</p>` : ""}<blockquote class="${x.plain ? "" : "q"}">${text}</blockquote><p class="by"><b>${esc(x.who)}</b>${src}</p></li>`;
}
function show() {
  const v = VALUES[S.sel], prev = VALUES[(S.sel + N - 1) % N], next = VALUES[(S.sel + 1) % N];
  $("card").innerHTML = `<div class="card">
    <p class="kick"><b>${S.sel + 1}</b> of ${N}</p>
    <h2 class="title">${esc(v.title)}</h2>
    ${v.lead.map(s => `<p class="lead">${esc(s)}</p>`).join("")}
    ${v.quotes.length ? `<ul class="quotes">${v.quotes.map(quote).join("")}</ul>` : ""}
    <div class="rule"${v.quotes.length ? "" : ' style="margin-top:26px"'}><h3>In AGENTS.md, the agents’ rules file</h3><p>${esc(v.rule)}</p></div>
    <div class="nav"><button data-k="${(S.sel + N - 1) % N}">← ${esc(prev.short)}</button><button class="next" data-k="${(S.sel + 1) % N}">${esc(next.short)} →</button></div>
  </div>`;
  $("side").scrollTop = 0;
}
function mark() {
  E.beads.forEach((b, k) => b.g.classList.toggle("on", k === S.sel));
  E.inner.forEach((p, k) => p.classList.toggle("on", k === S.sel));
  E.beads.forEach((b, k) => b.ray.classList.toggle("on", k === S.sel));
  E.num.textContent = S.sel + 1;
}
function select(k, push = true) {
  k = ((k % N) + N) % N;
  S.to = k + N * Math.round((S.rot - k) / N);  // the shorter way round
  if (still.matches) S.rot = S.to;
  if (k === S.sel && $("card").firstChild) { draw(); return; }
  S.sel = k;
  mark(); show();
  if (push) history.pushState(null, "", "#" + VALUES[k].id);
  if (still.matches) draw();
}
const fromHash = () => { const k = VALUES.findIndex(v => "#" + v.id === location.hash); return k < 0 ? 0 : k; };

$("svg").addEventListener("click", e => { const g = e.target.closest("[data-k]"); if (g) select(Number(g.dataset.k)); });
$("svg").addEventListener("keydown", e => { const g = e.target.closest(".bead"); if (g && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); select(Number(g.dataset.k)); } });
$("side").addEventListener("click", e => { const b = e.target.closest("button[data-k]"); if (b) select(Number(b.dataset.k)); });
addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); select(S.sel + 1); }
  if (e.key === "ArrowLeft" || e.key === "ArrowUp") { e.preventDefault(); select(S.sel - 1); }
});
addEventListener("popstate", () => select(fromHash(), false));
addEventListener("pointermove", e => { if (e.pointerType === "mouse") { S.mx = e.clientX / innerWidth * 2 - 1; S.my = e.clientY / innerHeight * 2 - 1; } });
narrow.addEventListener("change", build);
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", build);

S.sel = fromHash(); S.rot = S.to = S.sel;
build(); show();
document.fonts.ready.then(() => { E.beads.forEach(b => { b.text.setAttribute("font-size", G.fs); b.w = b.text.getComputedTextLength(); }); draw(); });
if (!still.matches) {
  $("svg").classList.add("enter");
  setTimeout(() => $("svg").classList.remove("enter"), 2800);  // moving a bead between the front and back layers would replay its entrance
  requestAnimationFrame(now => { S.last = now; requestAnimationFrame(frame); });
}
</script>
</body>
</html>
"""
