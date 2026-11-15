"""The home page of the team site: one dial that leads to every page.

view.py serves PAGE as the page / of invariant.team (and at /home on monitor.invariant.team and locally); every link
leads to monitor.invariant.team, where the pages are. The picture is a lit glass body with a ring around it, seen from slightly above, and one
bead on the ring per page of the site. The bead at the front is the selected page: the body shows its name and,
where one is counted, its live number. A click on a bead or the arrow keys turn the dial to it (address /#<page>; Up and Down only where the page does not scroll);
a click on the body or the button opens it. The words column beside the picture holds one sentence with the
live MATH-500 scores of the Board (the first and the best untrained-base score and the best RL score among the `scores`
rows of /data, computed as `benches` in view.py does, with the method words taken from the best base row's
configuration; no numbers before the first read), one line that says who the team is with the live number of people,
the button, and the same pages as a plain list of links in three labelled groups (Results, How we work, Also), so that
the list alone is enough to get anywhere. A bead's name is drawn outside
the ring: beside the bead at the sides, below it at the front, above it at the back. On a phone the list comes before the picture. What moves
is real data: about every 2.5 s one of the newest 40 board posts runs to the Board bead as a pulse in its author's
color, and the line under the picture says who posted it, when and what. A post that arrived since the last read of
/data plays next, larger and with a halo. The numbers of findings, proofs and lab pictures are written into the page
by view.py (`__COUNTS__`); the board's numbers come from /data every 10 s. Nothing here writes to the board.
"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant</title>
<meta name="description" content="Invariant is a small team of people and their coding agents at the SF AI Research Hackathon. This site shows their findings, their papers and the board they work from, live.">
<meta property="og:title" content="Invariant">
<meta property="og:description" content="Invariant is a small team of people and their coding agents at the SF AI Research Hackathon. This site shows their findings, their papers and the board they work from, live.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens, the light and the type of the Design page (architecture.py). */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34; --on-blue: #fff;
  --pl: .50; --pc: .15; --far: .72;  /* --far: the opacity of a bead and its name at the back of the dial */
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18); --btn-drop: rgba(16, 24, 32, .42);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --pl: .78; --pc: .13; --far: .6;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1;
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
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.hue { --c: oklch(var(--pl) var(--pc) var(--h)); }

.page {
  display: grid; grid-template-columns: minmax(320px, 27vw) minmax(0, 1fr); grid-template-rows: auto minmax(0, 1fr) auto;
  column-gap: 48px; height: 100vh; min-height: 640px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 22px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.status { margin-left: auto; color: var(--mute); white-space: nowrap; display: flex; align-items: center; gap: 10px; }
.status::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--blue); box-shadow: 0 0 0 4px color-mix(in srgb, var(--blue) 20%, transparent); }
.status.bad { color: var(--red); }
.status.bad::before { background: var(--red); box-shadow: 0 0 0 4px color-mix(in srgb, var(--red) 20%, transparent); }
@keyframes heart { from { box-shadow: 0 0 0 0 color-mix(in srgb, var(--blue) 70%, transparent); } }
.status.read::before { animation: heart 1.1s ease-out; }

/* The words: the sentence, the pages, one button */
.words { grid-column: 1; grid-row: 2 / 4; min-height: 0; overflow: hidden auto; scrollbar-width: none; padding: clamp(12px, 12vh - 74px, 52px) 0 0; }
.cap { margin: 0; font-size: clamp(20px, 1.56vw, 27px); line-height: 1.22; font-weight: 300; font-stretch: 102%; letter-spacing: -.012em; text-wrap: balance; }
.who { margin: clamp(6px, 1.2vh, 12px) 0 0; font-size: 13px; line-height: 1.35; color: var(--mute); }
.index { list-style: none; margin: clamp(10px, 8vh - 46px, 26px) 0 0; padding: 0; border-bottom: 1px solid var(--rule); line-height: 1.35; }
.index a {
  display: grid; grid-template-columns: 6.4em minmax(0, 1fr); align-items: baseline; column-gap: 12px;
  padding: clamp(2.5px, 2.1vh - 12.6px, 7.5px) 0 clamp(2.5px, 2.1vh - 12.6px, 7.5px) 14px; border-top: 1px solid var(--rule); text-decoration: none; position: relative;
}
.index a::before { content: ""; position: absolute; left: 0; top: 6px; bottom: 6px; width: 2px; border-radius: 2px; background: var(--blue); opacity: 0; transition: opacity .2s ease; }
/* Three groups, each under its label; the third is quieter */
.index li.lab { margin-top: clamp(5px, 4vh - 22px, 16px); padding: 0 0 2px 14px; font-size: 12.5px; font-weight: 560; color: var(--mute); }
.index li.lab:first-child { margin-top: 0; }
.index li:has(+ li.lab) a { border-bottom: 1px solid var(--rule); }
.index li.q b { font-weight: 480; font-size: 13.5px; color: var(--mute); }
.index li.q span { font-size: 12.5px; }
.index li.q a:hover b, .index li.q a.on b { color: var(--ink); }
.index a.on::before { opacity: 1; }
.index b { font-weight: 600; font-stretch: 108%; white-space: nowrap; }
.index span { color: var(--mute); font-size: 13.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.index a:hover span, .index a.on span { color: var(--ink); }
.index a:focus-visible { outline-offset: -2px; }  /* inside the row: the column clips what is outside it */
.go {
  display: inline-block; margin: clamp(10px, 8vh - 47px, 22px) 0 0; padding: 11px 22px; border-radius: 999px; background: var(--btn); color: var(--btn-ink);
  font-weight: 620; font-size: 15px; font-stretch: 106%; text-decoration: none;
  box-shadow: inset 0 1px 0 var(--btn-edge), 0 14px 28px -14px var(--btn-drop); transition: transform .18s ease, box-shadow .18s ease;
}
.go:hover { transform: translateY(-1px); box-shadow: inset 0 1px 0 var(--btn-edge), 0 0 0 1.5px var(--blue), 0 18px 32px -12px var(--btn-drop); }

/* The picture */
.stage { grid-column: 2; grid-row: 2; min-height: 0; min-width: 0; display: flex; padding: 6px 0 0; }
.foot { grid-column: 2; grid-row: 3; display: flex; align-items: baseline; gap: 24px; font-size: 13px; color: var(--mute); min-height: 21px; }
.said { display: block; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; transition: opacity .3s ease; }
.said b { color: var(--c); font-weight: 600; }
.said .now { color: var(--blue); }
.key { margin-left: auto; white-space: nowrap; }
svg { width: 100%; height: 100%; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); text-anchor: middle; font-stretch: 110%; letter-spacing: .012em; }
.atmo, .shade, .spec, .ring, .ticks, .mark, #fx, .read { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.spec { opacity: var(--spec); }
.body { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; cursor: pointer; }
.body:focus { outline: none; }
.body:focus-visible { stroke: var(--blue); stroke-width: 3; }
.read .n { font-weight: 300; letter-spacing: -.01em; }
.read .c { fill: var(--mute); font-weight: 480; }
.ring, .ticks { fill: none; stroke: var(--ink); stroke-linecap: round; }
.ring.back { stroke-width: .7; opacity: .3; }
.ring.front { stroke-width: 1.5; opacity: .85; }
.ring.front.thin { stroke-width: .8; opacity: .5; }
.ticks.back { stroke-width: .6; opacity: .26; }
.ticks.front { stroke-width: 1.1; opacity: .62; }
.mark { fill: none; stroke: var(--blue); stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }
.bead { cursor: pointer; }
.bead:focus { outline: none; }
.bead circle.b { fill: url(#body) var(--sheet); stroke: var(--ink); stroke-width: 1.3; }
.bead.on circle.b { stroke: var(--blue); stroke-width: 2.4; }
.bead:focus-visible circle.b { stroke: var(--blue); stroke-width: 3.2; }
.bead circle.pad { fill: transparent; }
.bead text { font-weight: 560; paint-order: stroke fill; stroke: var(--paper); stroke-width: 6px; stroke-linejoin: round; }
.bead.on text { font-weight: 680; }
.ptail { fill: var(--c); opacity: .5; }
.phead { fill: var(--c); }
.pglow { fill: var(--c); opacity: .16; }
.halo { fill: none; stroke: var(--c); stroke-width: 1.5; opacity: .5; }
.arrive { fill: none; stroke: var(--c); stroke-width: 1.6; }

/* One entrance, then only real posts move */
@keyframes fade { from { opacity: 0; } }
@keyframes pop { from { transform: scale(0); } }
.bead circle.b { transform-box: fill-box; transform-origin: center; }
.enter .atmo, .enter .shade, .enter .spec { animation: fade 1.6s .2s both; }
.enter .body, .enter .read { animation: fade .9s both; }
.enter .ring, .enter .ticks, .enter .mark { animation: fade 1s .35s both; }
.enter .bead circle.b { animation: pop .45s cubic-bezier(.3, 1.5, .5, 1) both; animation-delay: calc(.45s + var(--i) * 45ms); }
.enter .bead text { animation: fade .6s both; animation-delay: calc(.6s + var(--i) * 45ms); }

@media (max-width: 900px) {
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 6px 16px 36px; }
  .top { gap: 0 13px; padding-bottom: 2px; flex-wrap: wrap; }
  .top a { display: inline-flex; align-items: center; min-height: 40px; }  /* a finger's height */
  .name { font-stretch: 112%; margin-right: 0; }
  .words { display: contents; }  /* on a phone: the sentence, the button, the pages, then the picture and what is arriving */
  .cap { order: 1; margin-top: 20px; font-size: 22px; max-width: none; }
  .who { order: 1; }
  .go { order: 2; align-self: flex-start; margin-top: 18px; }
  .index { order: 3; margin-top: 20px; }
  .index a { padding: 11px 0 11px 14px; }
  .index span { white-space: normal; }
  .stage { order: 4; margin-top: 22px; padding: 0; display: block; }
  svg { height: auto; }
  .foot { order: 5; display: block; margin-top: 2px; min-height: 39px; }
  .said { white-space: normal; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }  /* two lines */
  .key { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .status.read::before { animation: none; }
  .go, .said, .index a::before { transition: none; }
}
</style>
</head>
<body>
<div class="page" id="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="https://monitor.invariant.team/">Board</a>
    <a href="https://monitor.invariant.team/architecture">Design</a>
    <a href="https://monitor.invariant.team/proof">Proof</a>
    <a href="https://monitor.invariant.team/findings">Findings</a>
    <span class="status" id="status">Reading the board</span>
  </header>
  <div class="words">
    <p class="cap" id="cap">We measure how far the Olmo 3 base model gets on MATH-500 with no training, against the RL-trained model.</p>
    <p class="who" id="who">Several people and their coding agents, at the SF AI Research Hackathon.</p>
    <a class="go" id="go" href="https://monitor.invariant.team/findings">Open Findings</a>
    <ul class="index" id="index"></ul>
  </div>
  <div class="stage"><svg id="svg" role="group" aria-label="A dial with one bead for each page of the site"></svg></div>
  <div class="foot"><span class="said hue" id="said"></span><span class="key">Each pulse is one post arriving on the board.</span></div>
</div>
<script>
const $ = id => document.getElementById(id);
const COUNTS = __COUNTS__;  // written in by view.py: the numbers of finding pages, proof pages, papers and lab pictures it serves
const HUES = [325, 150, 65, 195, 105, 45, 175, 350];  // a person's color, the same as on every other page
/* Every page of the site, in the order of the dial and of the list. g is its group in the list (GROUPS holds the
   labels): 0 the results, 1 how the team works, 2 the rest. line is the list's few words; count(m) is the number the
   body shows under the name, from the counts above or from the newest read of /data, and absent where nothing is
   counted (on a phone the body is 103 px wide, so the two long counts are shorter there). out marks a page that is
   not on this site. */
const GROUPS = ["Results", "How we work", "Also"];
const PAGES = [
  { id: "findings", g: 0, name: "Findings", href: "/findings", line: "One page for each finding", count: () => COUNTS.findings + " pages" },
  { id: "papers", g: 0, name: "Papers", href: "/papers", line: "The paper loop and what it wrote", count: () => COUNTS.papers + " papers" },
  { id: "talk", g: 0, name: "Talk", href: "/demo", line: "The talk, as slides" },
  { id: "board", g: 1, name: "Board", href: "/", line: "Ideas, open work and results", count: m => m ? `${m.open} open ${narrow.matches ? "" : "work "}items` : "" },
  { id: "design", g: 1, name: "Design", href: "/architecture", line: "How people and agents coordinate", count: m => m ? (narrow.matches ? "" : `${m.people.length} people, `) + `${m.agents} ${narrow.matches ? "" : "agent "}sessions` : "" },
  { id: "proof", g: 1, name: "Proof", href: "/proof", line: "Tests of the team's own method", count: () => COUNTS.proof + (COUNTS.proof === 1 ? " page" : " pages") },
  { id: "values", g: 1, name: "Values", href: "/values", line: "The six values the team works by" },
  { id: "team", g: 1, name: "Team", href: "/team", line: "Who we are" },
  { id: "lab", g: 2, name: "Lab", href: "/lab/", line: "3D pictures of the team's work", count: () => COUNTS.lab + " pictures" },
  { id: "exa", g: 2, name: "Exa", href: "/exa", line: "How the agents used web search" },
  { id: "pastdev", g: 2, name: "past.dev", href: "/pastdev", line: "How the agents used shared memory" },
  { id: "gpu", g: 2, name: "GPU prices", href: "https://gpu.invariant.team", line: "Forecasts of GPU rental prices", out: true },
  { id: "psychosis", g: 2, name: "Psychosis", href: "/psychosis", line: "A joke about ourselves, as a game" },
];
const SITE = /(^|\.)invariant\.team$/.test(location.hostname) ? "https://monitor.invariant.team" : "";  // where the pages are; a local copy links to itself
PAGES.forEach(p => { if (p.href[0] === "/") p.href = SITE + p.href; });
const N = PAGES.length, STEP = 360 / N, RAD = Math.PI / 180;
const S = { m: null, sel: 0, rot: 0, to: 0, t: 21, last: 0, seen: null, queue: [], loop: 0, fly: null, nextAt: 0, readAt: 0, error: null, mx: 0, my: 0, lx: 0, ly: 0 };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1);
const ago = ns => { const m = Math.max(0, Math.floor((Date.now() * 1e6 - Number(ns)) / 60e9)); return m < 1 ? "now" : m < 60 ? m + " min ago" : m < 2880 ? Math.floor(m / 60) + " h ago" : Math.floor(m / 1440) + " d ago"; };

/* Geometry: the ring lies flat around the body and is seen from above (pitch). R is the ring of beads, the ticks
   run from rt to rt + 8 (every sixth to rt + 15) inside it on a fine inner ring, rb is the body. fs is the size of a name at the front and min the
   smallest a name is drawn (on a phone 26 of 720 units, which is 12 px on a 375 px screen).
   The picture is wider than the ring by the longest name on each side. Names with q under far are not drawn. */
function geo() {
  return narrow.matches
    ? { w: 720, h: 548, cx: 360, cy: 262, R: 272, rt: 214, rb: 108, D: 1700, pitch: 36, bead: 12, fs: 27, min: 26, fn: 34, fc: 26, far: .86 }
    : { w: 1060, h: 660, cx: 530, cy: 290, R: 400, rt: 334, rb: 150, D: 2300, pitch: 36, bead: 8, fs: 17, min: 0, fn: 38, fc: 14.5, far: 0 };
}
let G = geo();
const FAR = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--far")) || .6;  // read once
/* The smallest name is 11.5 px on the screen, whatever size the picture is drawn at. */
function fit() { const b = $("svg").getBoundingClientRect(), k = Math.min(b.width / G.w, b.height / G.h); G.min = Math.max(G.min, k > 0 ? 11.5 / k : 0); }
const V = { cy: 1, sy: 0, cp: 1, sp: 0, yaw: 0 };
function aim(yaw, pitch) { V.yaw = yaw; V.cy = Math.cos(yaw * RAD); V.sy = Math.sin(yaw * RAD); V.cp = Math.cos(pitch * RAD); V.sp = Math.sin(pitch * RAD); }
function proj(x, y, z) {  // to the screen: [x, y, scale, depth]; z > 0 is the near side and lands lower
  const x1 = x * V.cy + z * V.sy, z1 = z * V.cy - x * V.sy, y2 = y * V.cp + z1 * V.sp, z2 = z1 * V.cp - y * V.sp, k = G.D / (G.D - z2);
  return [G.cx + x1 * k, G.cy + y2 * k, k, z2];
}
const onRing = (r, deg) => proj(r * Math.cos(deg * RAD), 0, r * Math.sin(deg * RAD));
const beadAt = k => 90 + (k - S.rot) * STEP;  // the selected bead is at 90 degrees, the front
function arcPath(r, a0, a1) {
  let d = "";
  for (let a = a0; a <= a1 + .01; a += 6) { const p = onRing(r, a); d += (d ? "L" : "M") + f(p[0]) + " " + f(p[1]); }
  return d;
}

function build() {
  G = geo();
  const stop = (o, c, a = 1) => `<stop offset="${o}" stop-color="${c}" stop-opacity="${a}"/>`;
  const svg = $("svg");
  svg.setAttribute("viewBox", `0 0 ${G.w} ${G.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".36" cy=".3" r=".86">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".12" y1=".08" x2=".9" y2=".94">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.3, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    "</defs>" +
    `<circle class="atmo" cx="${G.cx}" cy="${G.cy}" r="${G.rb * 2.1}" fill="url(#atmo)"/>` +
    `<ellipse class="shade" cx="${G.cx + G.rb * .2}" cy="${G.cy + G.rb * 1.02}" rx="${G.rb * 1.25}" ry="${G.rb * .3}" fill="url(#shade)"/>` +
    `<g id="back"><path class="ring back" id="ring-b"/><path class="ring back" id="in-b"/><path class="ticks back" id="ticks-b"/></g>` +
    `<circle class="body" id="body-c" cx="${G.cx}" cy="${G.cy}" r="${G.rb}" tabindex="0" role="link"/>` +
    `<ellipse class="spec" cx="${G.cx - G.rb * .34}" cy="${G.cy - G.rb * .44}" rx="${G.rb * .44}" ry="${G.rb * .26}" transform="rotate(-32 ${G.cx - G.rb * .34} ${G.cy - G.rb * .44})" fill="url(#spec)"/>` +
    `<g class="read"><text class="n" id="read-n" x="${G.cx}" font-size="${G.fn}"></text><text class="c" id="read-c" x="${G.cx}" y="${G.cy + G.fn * .92}" font-size="${G.fc}"></text></g>` +
    `<g id="front"><path class="ring front" id="ring-f"/><path class="ring front thin" id="in-f"/><path class="ticks front" id="ticks-f"/><path class="mark" id="mark"/></g>` +
    `<g id="fx"></g>`;
  PAGES.forEach((p, k) => {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttribute("class", "bead"); g.setAttribute("tabindex", "-1"); g.setAttribute("role", "button");  // a click or a script can focus it; Tab goes through the list, which holds the same pages
    g.setAttribute("aria-label", "Turn the dial to " + p.name); g.dataset.k = k; g.style.setProperty("--i", k);
    g.innerHTML = `<circle class="pad"/><circle class="b"/><text>${esc(p.name)}</text>`;
    p.el = g; p.front = null;
  });
  $("index").innerHTML = PAGES.map((p, k) => {
    const first = k === 0 || p.g !== PAGES[k - 1].g;  // the first page of a group comes after the group's label
    return (first ? `<li class="lab">${GROUPS[p.g]}</li>` : "") +
      `<li class="${p.g === 2 ? "q" : ""}"><a href="${p.href}" data-k="${k}"><b>${esc(p.name)}${p.out ? " \u2197" : ""}</b><span>${esc(p.line)}</span></a></li>`;
  }).join("");
  fit();
  readout();
}

/* The body's two lines, the button and the list's marker follow the selection. */
function readout() {
  const p = PAGES[S.sel], c = p.count ? p.count(S.m) : "";
  $("read-n").textContent = p.name; $("read-n").setAttribute("y", f(G.cy + (c ? -G.fn * .05 : G.fn * .34)));
  $("read-c").textContent = c;
  $("go").textContent = "Open " + p.name; $("go").href = p.href;
  $("body-c").setAttribute("aria-label", "Open " + p.name);
  $("index").querySelectorAll("a").forEach((a, k) => a.classList.toggle("on", k === S.sel));
  PAGES.forEach((q, k) => q.el.classList.toggle("on", k === S.sel));
}
function select(k, link) {
  k = (k % N + N) % N;
  let d = k - (S.to % N + N) % N; if (d > N / 2) d -= N; if (d < -N / 2) d += N;  // the short way around
  S.to += d; S.sel = k;
  if (link) history.replaceState(null, "", "#" + PAGES[k].id);
  readout();
  if (still.matches) { S.rot = S.to; draw(); }
}

function draw() {
  const sway = still.matches ? 0 : 1;
  aim(sway * (3.2 * Math.sin(S.t / 7) + 4 * S.lx), G.pitch + sway * (1.4 * Math.sin(S.t / 9.5) + 3 * S.ly));
  const y = V.yaw;  // the ring crosses from back to front where a point's angle equals the yaw
  $("ring-f").setAttribute("d", arcPath(G.R, y, y + 180)); $("ring-b").setAttribute("d", arcPath(G.R, y + 180, y + 360));
  $("in-f").setAttribute("d", arcPath(G.rt - 9, y, y + 180)); $("in-b").setAttribute("d", arcPath(G.rt - 9, y + 180, y + 360));
  let tf = "", tb = "";
  const drift = S.t * -1.1;  // the ticks turn at their own slow rate
  for (let j = 0; j < 72; j++) {
    const a = j * 5 + drift, p = onRing(G.rt, a), q = onRing(G.rt + (j % 6 ? 8 : 15), a), s = `M${f(p[0])} ${f(p[1])}L${f(q[0])} ${f(q[1])}`;
    if (Math.sin((a - y) * RAD) >= 0) tf += s; else tb += s;
  }
  $("ticks-f").setAttribute("d", tf); $("ticks-b").setAttribute("d", tb);
  const m0 = onRing(G.rt - 9, 90), m1 = onRing(G.R - 26, 90);  // the index mark, fixed at the front
  $("mark").setAttribute("d", `M${f(m0[0])} ${f(m0[1])}L${f(m1[0])} ${f(m1[1])}`);
  PAGES.forEach((p, k) => {
    const a = beadAt(k), [x, yy, s] = onRing(G.R, a), near = Math.sin((a - y) * RAD), q = (near + 1) / 2;
    const on = k === S.sel, r = (G.bead * (.62 + .58 * q) + (on ? 2.5 : 0)) * s, fs = Math.max(G.min, G.fs * (.7 + .3 * q) * (on ? 1.12 : 1));
    const front = near >= 0;
    if (front !== p.front) {
      const had = document.activeElement === p.el;  // moving an element drops its focus
      $(front ? "front" : "back").appendChild(p.el); p.front = front;
      if (had) p.el.focus({ preventScroll: true });
    }
    const [c0, c1, t] = p.el.children;
    t.setAttribute("font-size", f(fs));
    if (!p.w) p.w = t.getComputedTextLength() / fs;  // the name's width at size 1, measured once
    /* The name lies outside the ring: its box is pushed along the ring's outward normal (nx, ny) until it clears the
       bead, so it is beside the bead at the sides, below it at the front, above it at the back, and changes smoothly. */
    let nx = Math.cos((a - y) * RAD) * V.sp, ny = near; const len = Math.hypot(nx, ny); nx /= len; ny /= len;
    const lim = v => Math.max(-1, Math.min(1, v * 2.5)), d = r + 10;
    const tx = x + nx * d + lim(nx) * p.w * fs / 2, ty = yy + ny * d + (lim(ny) + 1) * fs * .36;
    c0.setAttribute("cx", f(x)); c0.setAttribute("cy", f(yy)); c0.setAttribute("r", f(r + 26));
    c1.setAttribute("cx", f(x)); c1.setAttribute("cy", f(yy)); c1.setAttribute("r", f(r));
    t.setAttribute("x", f(tx)); t.setAttribute("y", f(ty));
    p.el.setAttribute("opacity", (FAR + (1 - FAR) * q).toFixed(2));
    t.setAttribute("opacity", q < G.far ? 0 : 1);  // on a phone only the three names at the front fit; the list holds them all
    p.at = [x, yy, s, near, r]; p.box = [tx, ty, p.w * fs / 2, fs, t];
  });
  const b = PAGES[S.sel].box;  // a name that would touch the selected name is not drawn
  PAGES.forEach(p => { const c = p.box; if (c !== b && Math.abs(c[0] - b[0]) < c[2] + b[2] + c[3] * .6 && Math.abs(c[1] - b[1]) < (c[3] + b[3]) / 2) c[4].setAttribute("opacity", 0); });
  pulse();
}

/* One post in flight: from far behind the dial to the Board bead, in its author's color. */
const BOARD = PAGES.findIndex(p => p.id === "board");
function pulse() {
  const fx = $("fx"), F = S.fly;
  if (!F) { if (fx.firstChild) fx.innerHTML = ""; return; }
  const u = (S.t - F.t0) / F.dur;
  if (u >= 1.45) { S.fly = null; fx.innerHTML = ""; return; }
  const b = beadAt(BOARD), end = [G.R * Math.cos(b * RAD), 0, G.R * Math.sin(b * RAD)];
  const at = v => { const e = v * v * (3 - 2 * v); return proj(F.from[0] + (end[0] - F.from[0]) * e, F.from[1] + (end[1] - F.from[1]) * e - 90 * Math.sin(Math.PI * e), F.from[2] + (end[2] - F.from[2]) * e); };
  let out = "";
  if (u < 1) {
    const h = at(u), big = F.live ? 1.6 : 1, r = 4.2 * h[2] * big, pts = [];
    for (let j = 0; j <= 8; j++) pts.push(at(Math.max(0, u - j * .028)));
    let L = "", R = "";
    pts.forEach((p, j) => {
      const a = pts[Math.max(0, j - 1)], c = pts[Math.min(8, j + 1)], dx = c[0] - a[0], dy = c[1] - a[1], d = Math.hypot(dx, dy) || 1, w = r * (1 - j / 8);
      L += `${f(p[0] - dy / d * w)} ${f(p[1] + dx / d * w)} `; R = `${f(p[0] + dy / d * w)} ${f(p[1] - dx / d * w)} ` + R;
    });
    out = `<circle class="pglow" cx="${f(h[0])}" cy="${f(h[1])}" r="${f(r * 3.4)}"/><polygon class="ptail" points="${L}${R}"/><circle class="phead" cx="${f(h[0])}" cy="${f(h[1])}" r="${f(r)}"/>` +
      (F.live ? `<circle class="halo" cx="${f(h[0])}" cy="${f(h[1])}" r="${f(r * 2.3)}"/>` : "");
    const back = h[3] < 0 && Math.hypot(h[0] - G.cx, h[1] - G.cy) < G.rb * 1.5;  // behind the body it is hidden
    if (back !== F.back) { $("svg").insertBefore(fx, back ? $("body-c") : null); F.back = back; }
  } else {
    const v = (u - 1) / .45, p = PAGES[BOARD].at;
    out = `<circle class="arrive" cx="${f(p[0])}" cy="${f(p[1])}" r="${f(p[4] + 2 + 7 * v)}" opacity="${f(1 - v)}"/>`;
  }
  fx.innerHTML = out;
}
function launch() {
  const m = S.m; if (!m || !m.posts.length) return;
  const live = S.queue.shift(), it = live || m.posts[S.loop++ % m.posts.length], i = Math.max(0, m.people.indexOf(it.who));
  const side = m.people.length > 1 ? i / (m.people.length - 1) * 2 - 1 : 0;  // each person's posts come from their own direction
  S.fly = { t0: S.t, dur: 1.9, live: !!live, back: null, from: [side * 1.1 * G.R, -.15 * G.R, -1.55 * G.R] };
  $("fx").setAttribute("class", "hue"); $("fx").style.setProperty("--h", HUES[i % HUES.length]);
  say(it, !!live);
}
function say(it, live) {
  const m = S.m, i = Math.max(0, m.people.indexOf(it.who)), el = $("said");
  el.style.setProperty("--h", HUES[i % HUES.length]);
  el.innerHTML = `<b>${esc(it.who)}</b> posted ${live ? '<span class="now">now</span>' : ago(it.at_ns)}: ${esc(m.plain[it.id]?.title || it.text.replace(/\s+/g, " ").slice(0, 110))}`;
}

function frame(now) {
  const dt = Math.min(.1, (now - S.last) / 1000 || 0); S.last = now;
  S.t += dt;
  S.rot += (S.to - S.rot) * (1 - Math.exp(-dt * 6));
  S.lx += (S.mx - S.lx) * (1 - Math.exp(-dt * 3)); S.ly += (S.my - S.ly) * (1 - Math.exp(-dt * 3));
  if (!S.fly && S.m && S.t >= S.nextAt) { launch(); S.nextAt = S.t + 2.5; }
  draw();
  requestAnimationFrame(frame);
}

/* The board: what the body counts and what the pulses replay. */
function model(d) {
  const pct = s => s ? 100 * s.right / s.n : NaN;
  const of = model => (d.scores || []).filter(s => s.benchmark === "MATH-500" && s.model === model);
  const best = rows => rows.reduce((a, s) => !a || pct(s) > pct(a) ? s : a, null);
  const base = of("base"), top = best(base);
  const items = d.items, posts = items.filter(i => i.listed !== "work-closed").sort((a, b) => Number(b.at_ns) - Number(a.at_ns)).slice(0, 40);
  return {
    people: [...new Set(items.map(i => i.who))].sort(), posts, plain: d.plain || {},
    open: items.filter(i => i.listed === "work").length,
    agents: new Set(items.filter(i => i.session).map(i => i.session)).size,
    /* The Board's numbers (benches in view.py), in percent: the first untrained-base score posted, the best one with
       its configuration (the method, such as "cue, T 1.0, vote over 4"), and the best RL score. */
    start: pct(base[0]), base: pct(top), how: top ? top.config : "", rl: pct(best(of("rl"))),
  };
}
/* The sentence states the scores of the newest read: where the base started, where it is now and by which method (the
   words "cue" and "vote" of the best row's configuration), and the RL score. With no base score it keeps its words
   without numbers. The line under it states the number of people. */
function headline() {
  const m = S.m; if (!m) return;
  $("who").textContent = `${m.people.length} people and their coding agents, at the SF AI Research Hackathon.`;
  if (!isFinite(m.base)) return;
  const how = [/\bcue\b/.test(m.how) && "a prompt cue", /\bvote\b/.test(m.how) && "a vote"].filter(Boolean);
  $("cap").textContent = (how.length ? `With ${how.join(" and ")}, and no training, ` : "With no training, ") + "the Olmo 3 base model " +
    (m.start < m.base ? `goes from ${f(m.start)}\u00a0% to ${f(m.base)}\u00a0%` : `reaches ${f(m.base)}\u00a0%`) + " on MATH-500." +
    (isFinite(m.rl) ? ` The RL-trained model scores ${f(m.rl)}\u00a0%.` : "");
}
async function read() {
  try {
    const r = await fetch("/data"); if (!r.ok) throw new Error(r.status);
    const m = model(await r.json());
    const ids = new Set(m.posts.map(p => p.id));
    if (S.seen) S.queue.push(...m.posts.filter(p => !S.seen.has(p.id)).reverse());
    S.seen = ids; S.m = m; S.error = null; S.readAt = Date.now();
    readout(); headline();
    if (still.matches && m.posts.length) say(m.posts[0], false);
    const st = $("status"); st.classList.remove("read"); void st.offsetWidth; st.classList.add("read");
  } catch (e) { S.error = e; }
  status();
}
function status() {
  const st = $("status"), hm = t => new Date(t).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
  st.classList.toggle("bad", !!S.error);
  if (S.error) st.textContent = S.readAt ? "Offline, last read " + hm(S.readAt) : "Offline";
  else if (S.m && S.m.posts.length) st.textContent = "Last post " + ago(S.m.posts[0].at_ns);
}

build();
const start = PAGES.findIndex(p => "#" + p.id === location.hash);
if (start > 0) { S.sel = start; S.to = S.rot = start; readout(); }
$("svg").addEventListener("click", e => {
  const b = e.target.closest(".bead");
  if (b) select(Number(b.dataset.k), true); else if (e.target.id === "body-c") location.href = PAGES[S.sel].href;
});
$("svg").addEventListener("keydown", e => {
  if (e.key !== "Enter" && e.key !== " ") return;
  const b = e.target.closest(".bead");
  if (b) { e.preventDefault(); select(Number(b.dataset.k), true); } else if (e.target.id === "body-c") location.href = PAGES[S.sel].href;
});
$("index").addEventListener("focusin", e => { const a = e.target.closest("a"); if (a) select(Number(a.dataset.k), false); });
$("index").addEventListener("pointerover", e => { const a = e.target.closest("a"); if (a && e.pointerType === "mouse") select(Number(a.dataset.k), false); });
addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
  if (d) {
    const upDown = e.key === "ArrowDown" || e.key === "ArrowUp";
    if (upDown && document.documentElement.scrollHeight > innerHeight) return;  // the page scrolls: Up and Down are the browser's
    e.preventDefault(); select(S.sel + d, true);
    if ($("index").contains(document.activeElement)) $("index").querySelectorAll("a")[S.sel].focus();  // focus follows the selection in the list
  }
  else if (e.key === "Enter" && (document.activeElement === document.body)) location.href = PAGES[S.sel].href;
});
addEventListener("hashchange", () => { const k = PAGES.findIndex(p => "#" + p.id === location.hash); if (k >= 0 && k !== S.sel) select(k, false); });
addEventListener("pointermove", e => { if (e.pointerType === "mouse") { S.mx = e.clientX / innerWidth * 2 - 1; S.my = e.clientY / innerHeight * 2 - 1; } });
narrow.addEventListener("change", () => { build(); draw(); });
addEventListener("resize", () => { G.min = geo().min; fit(); });
$("svg").classList.add("enter");
draw();
document.fonts.ready.then(() => { PAGES.forEach(p => { p.w = 0; }); draw(); });  // measure the names again in the loaded typeface
if (!still.matches) requestAnimationFrame(now => { S.last = now; requestAnimationFrame(frame); });
read(); setInterval(read, 10000); setInterval(status, 15000);
</script>
</body>
</html>
"""
