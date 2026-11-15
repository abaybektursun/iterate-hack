"""Ali's part of the talk: three slides, at /demo/ali/slide1, /demo/ali/slide2 and /demo/ali/slide3 (view.py serves
PAGES; /demo/ali leads to the first). They are not linked from the header. Each has the header of the site, one picture
on the left and a column of words on the right with its place in the three, Back and Next. The arrow keys change the
slide, t changes the theme (the stored choice of /demo), and with prefers-reduced-motion every picture is one still frame.

slide1, Idea map (DISC, view "map"). The board items of one snapshot as a relief on a lit glass disc: each cluster of
ideas is a hill whose height is the number of items posted there so far, each item a dot in its person's colour, and
each person's agents one Claude mark that travels to the next item they post, with their last hops as a tapered tail.
Around the disc a ring of board time with one tick per item and a comet at the present. The replay runs by itself;
the ring and the slider under the picture move the time, and the button beside the clock sets the speed (1x, 2x, 5x).
The column counts the items, the clusters reached and the moves between clusters at the time shown, and shows the
latest item, or the selected one after a click on a dot (the address holds it: /demo/ali/slide1#<item id>).

slide2, Idea tree (DISC, view "tree"). The same items on a disc seen from above: the first at the centre, the last at
the rim, each in the sector of its cluster, with a line to every item it builds on. A click on a dot lights what it
builds on (blue) and what builds on it; the slide opens on the result that set the board's latest record of the
untrained base. The column gives that item's text, the board's score rows of it and the two counts.

slide3, Accuracy (STEPS). The best MATH-500 score of the untrained base as a lit step line over board time, with the
best score of the RL-Zero-Math model as a dotted line over it, floating above the disc of slide1. When a record is set
the clock holds, a light runs from the result that set it on the disc up to the line, and the step rises. The other
base scores of the window are hollow dots. The column shows the score as one large number with RL's best and RL's
lead, and the record steps as rows in the board's plain words; a row opens the board's what and caveat of that step
(/demo/ali/slide3#step-<n>; the down and up keys walk them).

Every number comes from tools/demo_ali_data.py, written by studies/basins/analysis/slide_data.py: the items, their
positions, clusters and links from one run of the swarm idea map (studies/basins), and the board's score rows read
from /data at the time each slide names under "How ... is made" or "Where the numbers come from". The pages read
nothing after they load and never write. To refresh the numbers, run that script again and redeploy.
"""
import json

import demo_ali_data

SLIDES = [("slide1", "Idea map"), ("slide2", "Idea tree"), ("slide3", "Accuracy")]

HEAD = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<script>
/* The theme before the first paint, as on /demo: ?theme=light or dark wins (and is stored), else the stored choice, else the system. */
(() => {
  let t = new URLSearchParams(location.search).get("theme");
  try { if (t === "light" || t === "dark") localStorage.setItem("demo-theme", t); else t = localStorage.getItem("demo-theme"); } catch (e) { /* storage blocked: the address or the system decides */ }
  if (t === "light" || t === "dark") document.documentElement.dataset.theme = t;
})();
</script>
"""

# slide1 and slide2: the idea map and the idea tree, one view each (__VIEW__)
DISC = r"""<style>
/* Layout: the look of the team site (monitor.invariant.team). One lit glass disc in a dark room on the left, with a
   fine ring around it; a flat column of words on the right behind one hairline, as on the site's talk page.
   Tokens are those of tools/architecture.py, unchanged: one light from the upper left, --blue the one accent,
   a person's colour is oklch(var(--pl) var(--pc) <hue>). One typeface, Archivo. */
:root {
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --pl: .56; --pc: .15; --dim: .16;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue); --lift: 38%; --ridge: #101820;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18);
  --f: "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --pl: .78; --pc: .13; --dim: .24;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff; --lift: 55%; --ridge: #dfeaf6;
    --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
  --blue: #8fb1ff; --red: #ff6b7c;
  --pl: .78; --pc: .13; --dim: .24;
  --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
  --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
  --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff; --lift: 55%; --ridge: #dfeaf6;
  --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7);
  color-scheme: dark;
}
* { box-sizing: border-box; }
body {
  color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 var(--f); font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
a { color: inherit; text-decoration: none; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
p, h1, dl, dd { margin: 0; }
.hue { --c: oklch(var(--pl) var(--pc) var(--h)); }

.page {
  max-width: 1840px; margin: 0 auto; padding-block: 20px 24px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: flex; flex-direction: column;
}
@media (min-width: 900px) { .page { padding-left: max(40px, env(safe-area-inset-left, 0px)); padding-right: max(40px, env(safe-area-inset-right, 0px)); } }
.top { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin-right: 6px; }
.top a { color: var(--mute); }
.top a:hover { color: var(--ink); }
.status { color: var(--mute); white-space: nowrap; }

.view { display: grid; grid-template-columns: minmax(0, 1fr) minmax(300px, 26vw); align-items: stretch; }
@media (max-width: 899px) { .view { grid-template-columns: minmax(0, 1fr); } }
.stage { min-width: 0; display: flex; flex-direction: column; padding: 10px 0 0; }
.stage svg { display: block; width: 100%; height: auto; max-height: calc(100vh - 186px); overflow: visible; font-family: var(--f); }
#map { touch-action: manipulation; }
.foot { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 22px; font-size: 12.5px; color: var(--mute); padding: 6px 0 0; }
.foot .key { display: flex; flex-wrap: wrap; gap: 6px 16px; }
.foot .key span { display: inline-flex; align-items: center; gap: 6px; }
.foot svg { width: 14px; height: 14px; flex: none; }
.foot .p { color: var(--c); font-weight: 620; }
.foot .run { flex: 1 1 100%; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; padding-bottom: 4px; }
.foot .run b { font-weight: 560; color: var(--ink); min-width: 74px; text-align: right; }
.quiet { font-weight: 560; color: var(--ink); border: 1px solid var(--faint); border-radius: 999px; padding: 5px 16px; font-size: 13px; }
.quiet.speed { padding: 5px 0; width: 46px; text-align: center; }
/* the slider of board time: a hairline with the part already played in ink, and one lit knob */
.scrub { flex: 1 1 200px; min-width: 0; height: 24px; margin: 0; padding: 0; background: none; -webkit-appearance: none; appearance: none; cursor: pointer; --p: 0%; }
.scrub::-webkit-slider-runnable-track { height: 2px; border-radius: 1px; background: linear-gradient(to right, var(--ink) var(--p), var(--rule) var(--p)); }
.scrub::-moz-range-track { height: 2px; border-radius: 1px; background: var(--rule); }
.scrub::-moz-range-progress { height: 2px; border-radius: 1px; background: var(--ink); }
.scrub::-webkit-slider-thumb { -webkit-appearance: none; width: 14px; height: 14px; margin-top: -6px; border-radius: 50%; background: var(--core); border: 1.5px solid var(--blue); box-shadow: 0 0 calc(var(--glow) * 10px) var(--blue); }
.scrub::-moz-range-thumb { width: 11px; height: 11px; border-radius: 50%; background: var(--core); border: 1.5px solid var(--blue); box-shadow: 0 0 calc(var(--glow) * 10px) var(--blue); }

/* the words column: the same column as the site's talk page */
.side { min-width: 0; display: flex; flex-direction: column; gap: 15px; border-left: 1px solid var(--rule); padding: clamp(20px, 4vh, 48px) 0 0 clamp(28px, 2.8vw, 56px); margin-left: clamp(0px, 1.4vw, 28px); }
@media (max-width: 899px) { .side { border-left: 0; padding: 18px 0 0; margin-left: 0; } }
.head { display: flex; justify-content: space-between; font-size: 13px; color: var(--mute); font-weight: 560; }
.say { font-weight: 300; font-size: clamp(23px, 2.05vw, 33px); line-height: 1.18; letter-spacing: -.01em; color: var(--mute); text-wrap: balance; }
.say b { font-weight: 600; color: var(--ink); }
.rows > div { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; padding: 9px 0; border-top: 1px solid var(--rule); }
.rows > div:last-child { border-bottom: 1px solid var(--rule); }
.rows dt { color: var(--mute); font-size: 13.5px; }
.rows dd { text-align: right; white-space: nowrap; color: var(--faint); font-size: 13px; }
.rows dd b { font-weight: 620; font-size: 19px; color: var(--ink); margin-right: 4px; }
.lab { font-size: 12.5px; font-weight: 640; color: var(--mute); }
.item { display: flex; flex-direction: column; gap: 5px; min-height: 142px; }
.item .meta { font-size: 13px; color: var(--faint); display: flex; flex-wrap: wrap; gap: 4px 10px; }
.item .meta .who { color: var(--c); font-weight: 620; }
.item p { font-size: 14px; line-height: 1.45; overflow-wrap: anywhere; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 5; overflow: hidden; }
.item .more { font-size: 13px; color: var(--mute); }
.item .more b { color: var(--ink); font-weight: 620; }
.item .more.one { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
#tItem p { -webkit-line-clamp: 3; }
.links { display: flex; flex-wrap: wrap; gap: 6px 20px; font-size: 13.5px; }
.links button { font-weight: 560; color: var(--mute); border-bottom: 1px solid var(--rule); padding: 2px 0; }
.links button:hover { color: var(--ink); }
.how summary { font-size: 13.5px; font-weight: 560; color: var(--mute); cursor: pointer; padding: 9px 0; border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); list-style: none; display: flex; justify-content: space-between; }
.how summary::-webkit-details-marker { display: none; }
.how summary::after { content: "+"; color: var(--faint); font-weight: 400; }
.how[open] summary::after { content: "\2212"; }
.how .note { padding-top: 10px; }
.note { font-size: 12.5px; color: var(--faint); line-height: 1.45; max-width: 62ch; }

/* the lit body, shared by both pictures */
.atmo, .shade, .spec, .bloom { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.spec { opacity: var(--spec); }
.bloom { opacity: var(--bloom); }
.body { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.body-edge { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }

/* the relief */
.rf { fill: var(--glass); stroke: none; }
.rl { fill: none; stroke: var(--ridge); stroke-linejoin: round; }
.dot { fill: var(--c); }
.dot.work { fill: var(--glass); stroke: var(--c); stroke-width: 1.4; }
.trail { fill: none; stroke: var(--c); stroke-linecap: round; stroke-linejoin: round; }
.ptail { fill: var(--c); opacity: .75; }
.mark { fill: var(--c); }
.pn { font-size: 11.5px; font-weight: 620; fill: var(--c); text-anchor: middle; paint-order: stroke; stroke: var(--paper); stroke-width: 3.5px; stroke-linejoin: round; }
.bl line { stroke: var(--mute); stroke-width: .6; }
.bl text { font-size: 11.5px; font-weight: 400; fill: var(--faint); text-anchor: middle; paint-order: stroke; stroke: var(--glass-lo); stroke-width: 3px; stroke-linejoin: round; }
.bl .bn { fill: var(--ink); font-weight: 560; }
#selRing, #tSel { fill: none; stroke: var(--blue); stroke-width: 1.8; }

/* the ring of board time */
.ring-base { fill: none; stroke: var(--faint); stroke-width: .8; opacity: .55; }
.ring-past { fill: var(--ink); opacity: .8; }
.ring-hit { fill: none; stroke: transparent; stroke-width: 34; pointer-events: stroke; cursor: grab; }
.ring-hit:focus { outline: none; }
.ring-hit:focus-visible + .ring-base { stroke: var(--blue); stroke-width: 2.2; opacity: 1; }
.tick { fill: none; stroke: var(--c); stroke-width: 1.15; }
.tick.future { opacity: .28; }
.hr { font-size: 11px; fill: var(--faint); text-anchor: middle; }
.hr.end { fill: var(--ink); font-weight: 560; }
.chev { fill: none; stroke: var(--mute); stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }
.comet-tail { fill: var(--blue); }
.comet-core { fill: var(--core); }

/* the tree */
.spoke { stroke: var(--ridge); stroke-width: .6; opacity: .1; }
.sect { font-size: 12.5px; font-weight: 560; fill: var(--mute); }
.sect.on { fill: var(--ink); }
.lk { fill: none; stroke: var(--ridge); stroke-width: .7; opacity: .16; }
.lk.x { opacity: .26; }
.nd { fill: var(--c); }
.nd.work { fill: var(--glass); stroke: var(--c); stroke-width: 1.4; }
.hit { fill: transparent; cursor: pointer; }
.has-sel .lk { opacity: .05; }
.has-sel .nd { opacity: var(--dim); }
.has-sel .lk.anc { stroke: var(--blue); stroke-width: 1.6; opacity: .95; }
.has-sel .lk.desc { stroke: var(--ridge); stroke-width: 1; opacity: .5; }
.has-sel .nd.lit { opacity: 1; }
.flow { fill: none; stroke: var(--core); stroke-width: 1.6; stroke-linecap: round; stroke-dasharray: .035 .965; animation: flow 3.2s linear infinite; opacity: .95; }
@keyframes flow { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
.grow .lk, .grow .nd { animation: grow .5s both; animation-delay: calc(var(--r) * 7s); }
@keyframes grow { from { opacity: 0; } }
@media (prefers-reduced-motion: reduce) { .grow .lk, .grow .nd, .flow { animation: none; } .flow { display: none; } }
/* what the three slides share with the rest of the site: the theme control of /demo and the links between the slides */
html { background: var(--paper); }
body { margin: 0; }
[hidden] { display: none !important; }
.theme { margin-left: auto; color: var(--mute); font-weight: 500; padding: 2px 4px; border-radius: 3px; }
.theme:hover { color: var(--ink); }
.segs { display: flex; gap: 6px; margin-top: -8px; }
.segs a { flex: 1; height: 14px; position: relative; display: block; }
.segs a::after { content: ""; position: absolute; left: 0; right: 0; top: 6px; height: 2px; background: var(--rule); border-radius: 1px; }
.segs a[aria-current="page"]::after { background: var(--ink); }
.nav { display: flex; align-items: center; gap: 10px; margin-top: auto; padding-top: 8px; }
.nav a, .nav .off { font-weight: 620; font-size: 13.5px; padding: 8px 20px; border-radius: 999px; border: 1px solid var(--faint); }
.nav a.next { background: var(--btn); color: var(--btn-ink); border-color: transparent; box-shadow: inset 0 1px 0 var(--btn-edge); }
.nav .off { opacity: .35; }
.nav .hint { margin-left: auto; font-size: 12.5px; color: var(--faint); }
</style>
</head>
<body>

<svg id="defs" width="0" height="0" style="position:absolute" aria-hidden="true"></svg>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings">Findings</a>
    <button class="theme" id="theme" type="button">Light</button>
    <span class="status" id="status"></span>
  </header>

  <section class="view" id="viewMap">
    <div class="stage">
      <svg id="map" viewBox="0 0 1000 690" role="img" aria-label="A glass disc seen from above. Each cluster of ideas is a hill that rises as items are posted. Each person's agents travel between the hills. The ring around the disc is board time."></svg>
      <div class="foot">
        <div class="run"><button class="quiet" id="play">Pause</button><input class="scrub" id="scrub" type="range" min="0" max="1000" step="1" value="0" aria-label="Board time"><b id="clock"></b><button class="quiet speed" id="speed" aria-label="Replay speed: 1 times. Press to change.">1×</button></div>
        <div class="key" id="mKey"></div>
      </div>
    </div>
    <aside class="side">
      <div class="head"><span>Idea map</span><span data-count></span></div>
      <nav class="segs" data-segs aria-label="Slides"></nav>
      <p class="say" id="mSentence"></p>
      <dl class="rows">
        <div><dt>Items posted so far</dt><dd><b id="cItems">0</b><span id="cItemsOf"></span></dd></div>
        <div><dt>Clusters reached</dt><dd><b id="cBasins">0</b><span id="cBasinsOf"></span></dd></div>
        <div><dt>Moves between clusters</dt><dd><b id="cMoves">0</b><span id="cNew"></span></dd></div>
      </dl>
      <div class="item" id="mItem"></div>
      <details class="how"><summary>How the map is made</summary><p class="note" id="mNote"></p></details>
      <div class="nav" data-nav></div>
    </aside>
  </section>

  <section class="view" id="viewTree" hidden>
    <div class="stage">
      <svg id="tree" viewBox="0 0 1000 690" role="img" aria-label="The board as a disc. Each item is a dot, the first at the centre and the last at the rim, in the sector of its cluster, with a line to every item it builds on."></svg>
      <div class="foot"><div class="key" id="tKey"></div></div>
    </div>
    <aside class="side">
      <div class="head"><span>Idea tree</span><span data-count></span></div>
      <nav class="segs" data-segs aria-label="Slides"></nav>
      <p class="say" id="tSentence"></p>
      <dl class="rows">
        <div><dt>Items built on two or more</dt><dd><b id="tMerge"></b><span id="tMergeOf"></span></dd></div>
        <div><dt>Longest chain</dt><dd><b id="tDepth"></b><span>links</span></dd></div>
      </dl>
      <div class="item" id="tItem"></div>
      <div class="links"><button id="tBest">Latest base record</button><button id="tReplay">Replay growth</button><button id="tClear">Clear</button></div>
      <details class="how"><summary>How the tree is made</summary><p class="note" id="tNote"></p></details>
      <div class="nav" data-nav></div>
    </aside>
  </section>
</div>

<script>
(() => {
"use strict";
const R = __DATA__, SLIDES = __SLIDES__, SLIDE = __SLIDE__;
const MARK = R.mark;
const $ = s => document.querySelector(s);
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
/* the slides of this part of the talk, and the theme control of /demo (the same stored choice, the same key t) */
const slide = d => { const s = SLIDES[SLIDE + d]; if (s) location.href = s.href + location.search; };
document.querySelectorAll("[data-count]").forEach(el => { el.textContent = `${SLIDE + 1} of ${SLIDES.length}`; });
document.querySelectorAll("[data-segs]").forEach(el => { el.innerHTML = SLIDES.map((s, i) => `<a href="${s.href}" aria-label="${s.name}"${i === SLIDE ? ' aria-current="page"' : ""}></a>`).join(""); });
document.querySelectorAll("[data-nav]").forEach(el => {
  const a = (s, cls, word) => s ? `<a class="${cls}" href="${s.href}">${word}</a>` : `<span class="${cls} off">${word}</span>`;
  el.innerHTML = a(SLIDES[SLIDE - 1], "", "Back") + a(SLIDES[SLIDE + 1], "next", "Next") + `<span class="hint">or use the arrow keys</span>`;
});
const themeNow = () => document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
function themeLabel() { const other = themeNow() === "dark" ? "Light" : "Dark"; $("#theme").textContent = other; $("#theme").setAttribute("aria-label", `${other} colours`); }
function toggleTheme() {
  const t = themeNow() === "dark" ? "light" : "dark"; document.documentElement.dataset.theme = t;
  try { localStorage.setItem("demo-theme", t); } catch (e) { /* storage blocked: the choice lasts until the page closes */ }
  themeLabel();
}
$("#theme").addEventListener("click", toggleTheme); themeLabel();
const HUES = [325, 150, 65, 195, 105, 45, 175, 350];  // the site's person colours, by place in the sorted list of names
const N = R.nodes, B = R.basins, SPAN = R.span_h, RAD = Math.PI / 180;
const byId = new Map(N.map((n, i) => (n.i = i, [n.id, n])));
const people = [...new Set(N.map(n => n.who))].sort();
N.forEach(n => { n.pi = people.indexOf(n.who); n.h = HUES[n.pi % HUES.length]; });
const pad = v => String(v).padStart(2, "0");
const hm = t => { const m = Math.floor(R.t0_min + t * 60); return pad(Math.floor(m / 60) % 24) + ":" + pad(m % 60); };
const clock = t => hm(t) + " UTC";
const day = t => (R.t0_min + t * 60 >= 1440 ? "15 Nov" : "14 Nov");
const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const ease = x => x * x * (3 - 2 * x);
const RK = { result: 4.4, work: 3.6 }, rOf = n => RK[n.kind] || 2.5;
const f1 = v => v.toFixed(1);
const stop = (o, c, a) => `<stop offset="${o}" style="stop-color:${c}${a == null ? "" : `;stop-opacity:${a}`}"/>`;
const DEFS =  // the gradients of the site's lit body: light from the upper left, a rim that fades around it, a glow behind it
  `<radialGradient id="body" cx=".36" cy=".3" r=".86">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
  `<linearGradient id="rim" x1=".12" y1=".08" x2=".9" y2=".94">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
  `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
  `<radialGradient id="shade">${stop(.6, "var(--ink)", .22)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
  `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
  `<radialGradient id="glo-b">${stop(0, "var(--blue)", .6)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
  people.map((p, i) => `<radialGradient id="glo-${i}" class="hue" style="--h:${HUES[i % 8]}">${stop(0, "var(--c)", .55)}${stop(1, "var(--c)", 0)}</radialGradient>`).join("");
$("#defs").innerHTML = `<defs>${DEFS}<symbol id="mk" viewBox="0 0 16 16"><path d="${MARK}"/></symbol></defs>`;
function ribbon(p, w) {  // a stroke whose width changes along it
  const n = p.length, L = [], Rr = [];
  for (let i = 0; i < n; i++) {
    const a = p[Math.max(0, i - 1)], b = p[Math.min(n - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, half = w(p[i], i) / 2;
    L.push(f1(p[i][0] - dy / d * half) + " " + f1(p[i][1] + dx / d * half)); Rr.push(f1(p[i][0] + dy / d * half) + " " + f1(p[i][1] - dx / d * half));
  }
  return n < 2 ? "" : "M" + L.join("L") + "L" + Rr.reverse().join("L") + "Z";
}

/* cumulative counts in board order: clusters reached, moves of a person to another cluster, moves to one new to them */
{
  const seenAll = new Set(), last = {}, seen = {};
  let mv = 0, nw = 0;
  for (const n of N) {
    seenAll.add(n.b);
    const s = seen[n.who] || (seen[n.who] = new Set());
    if (n.who in last && last[n.who] !== n.b) { mv++; if (!s.has(n.b)) nw++; }
    s.add(n.b); last[n.who] = n.b;
    n.cB = seenAll.size; n.cM = mv; n.cN = nw;
  }
}
B.forEach((b, i) => { b.items = N.filter(n => n.b === i); b.first = b.items[0].t; });
const itemHtml = (n, extra) =>
  `<div class="meta"><span class="who hue" style="--h:${n.h}">${esc(n.who)}</span><span>${n.kind}</span><span>${clock(n.t)}, ${day(n.t)}</span><span>${esc(B[n.b].short)}</span></div>` +
  `<p>${esc(n.text)}${n.text.length >= 260 ? "…" : ""}</p>${extra || ""}`;
const keyHtml = extra =>
  `<span><svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="4.4" fill="var(--mute)"/></svg>result</span>` +
  `<span><svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="3.6" fill="none" stroke="var(--mute)" stroke-width="1.3"/></svg>open work</span>` +
  `<span><svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="2.4" fill="var(--mute)"/></svg>idea or note</span>` + extra;

$("#status").textContent = `Board at ${clock(SPAN)}, ${day(SPAN)}, ${N.length} items`;

/* ───────── the relief on the disc ───────── */
const GX = 66, GY = 48, KX = 5, KY = 4, SIG = .105, ZS = .13, RT = 1.2, A0 = -77, A1 = 257;
const du = 2 / (GX - 1), dv = 2 / (GY - 1), KW = 2 * KX + 1;
const K = new Float32Array(KW * (2 * KY + 1));
for (let j = -KY; j <= KY; j++) for (let i = -KX; i <= KX; i++) K[(j + KY) * KW + i + KX] = Math.exp(-((i * du) ** 2 + (j * dv) ** 2) / (2 * SIG * SIG));
{
  /* each axis: 60 % rank, 40 % the judge's coordinate, so that the dense corner of the embedding is readable; then the square is mapped onto the disc */
  const axis = k => { const vs = N.map(n => n[k]), lo = Math.min(...vs), hi = Math.max(...vs), order = N.map((n, i) => i).sort((a, b) => vs[a] - vs[b]), out = [];
    order.forEach((i, r) => { out[i] = (.6 * r / (N.length - 1) + .4 * (vs[i] - lo) / (hi - lo)) * 2 - 1; }); return out; };
  const au = axis("x"), av = axis("y");
  for (const n of N) {
    const a = au[n.i], b = av[n.i];
    n.u = a * Math.sqrt(1 - b * b / 2) * .84; n.v = b * Math.sqrt(1 - a * a / 2) * .84;
    n.gi = Math.round((n.u + 1) / du); n.gj = Math.round((n.v + 1) / dv); n.w = n.kind === "result" ? 1 : n.kind === "work" ? .7 : .5;
  }
}
B.forEach(b => { b.u = b.items.reduce((s, n) => s + n.u, 0) / b.items.length; b.v = b.items.reduce((s, n) => s + n.v, 0) / b.items.length; });
const H = new Float32Array(GX * GY), Z = new Float32Array(GX * GY);
function heights(T) {
  H.fill(0);
  for (const n of N) {
    if (n.t > T) break;
    const w = n.w * ease(clamp((T - n.t) / .09, 0, 1));
    for (let j = -KY; j <= KY; j++) {
      const y = n.gj + j; if (y < 0 || y >= GY) continue;
      for (let i = -KX; i <= KX; i++) { const x = n.gi + i; if (x >= 0 && x < GX) H[y * GX + x] += w * K[(j + KY) * KW + i + KX]; }
    }
  }
  for (let k = 0; k < H.length; k++) Z[k] = ZS * Math.log1p(H[k] * .9);
}
function zAt(u, v) {
  const fx = clamp((u + 1) / du, 0, GX - 1.001), fy = clamp((v + 1) / dv, 0, GY - 1.001), i = fx | 0, j = fy | 0, a = fx - i, b = fy - j, k = j * GX + i;
  return (Z[k] * (1 - a) + Z[k + 1] * a) * (1 - b) + (Z[k + GX] * (1 - a) + Z[k + GX + 1] * a) * b;
}
/* our own projection: u to the right, v toward the viewer, z up; seen from 43 degrees above, with a little perspective */
const VH = 690, CX = 500, CY = 352, S = 312, D = 2700, SE = Math.sin(43 * RAD), CE = Math.cos(43 * RAD);
let cyaw = 1, syaw = 0;
function proj(u, v, z) {
  const xr = u * cyaw - v * syaw, yr = u * syaw + v * cyaw, k = D / (D - yr * S * CE);
  return [CX + xr * S * k, CY + (yr * SE - z * CE) * S * k, k];
}
const onRing = (r, deg) => proj(r * Math.cos(deg * RAD), r * Math.sin(deg * RAD), 0);
const degOf = t => A0 + (A1 - A0) * t / SPAN;
const pt = p => f1(p[0]) + " " + f1(p[1]);
const line = ps => ps.map((p, i) => (i ? "L" : "M") + pt(p)).join("");

const map = $("#map");
{
  let hours = "";
  for (let m = Math.ceil(R.t0_min / 60) * 60; m <= R.t0_min + SPAN * 60; m += 60) hours += `<text class="hr" data-t="${(m - R.t0_min) / 60}">${pad(m / 60 % 24)}:00</text>`;
  map.innerHTML =
    `<ellipse class="atmo" cx="${CX}" cy="${CY}" rx="${S * 1.9}" ry="${f1(S * 1.9 * SE)}" fill="url(#atmo)"/>` +
    `<ellipse class="shade" cx="${CX + S * .07}" cy="${f1(CY + S * .15)}" rx="${S * 1.22}" ry="${f1(S * 1.22 * SE)}" fill="url(#shade)"/>` +
    `<path class="ring-hit" id="ringHit" role="slider" tabindex="0" aria-label="Board time" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"/><path class="ring-base" id="ringBase"/>` +
    `<path class="ring-past" id="ringPast"/><path class="chev" id="chev"/>` +
    `<g id="ticks">${people.map((p, i) => `<g class="hue" style="--h:${HUES[i % 8]}"><path class="tick"/><path class="tick future"/></g>`).join("")}</g>` +
    `<g id="hours"><text class="hr end" data-t="0">${hm(0)}</text>${hours}<text class="hr end" data-t="${SPAN}">${hm(SPAN)}</text></g>` +
    `<path class="body-edge" id="discEdge" transform="translate(0 11)"/><path class="body" id="disc"/>` +
    `<ellipse class="spec" id="spec" fill="url(#spec)"/>` +
    `<g id="rows">${Array.from({ length: GY }, () => `<path class="rf"/><path class="rl"/>`).join("")}</g>` +
    `<g id="dots">${N.map(n => `<circle class="dot hue ${n.kind}" style="--h:${n.h}" visibility="hidden"/>`).join("")}</g>` +
    `<g id="trails">${people.map((p, i) => `<g class="hue" style="--h:${HUES[i % 8]}"><path class="trail" opacity=".22" stroke-width="1"/><path class="trail" opacity=".5" stroke-width="1.3"/><path class="ptail"/></g>`).join("")}</g>` +
    `<g id="labels">${B.map(b => `<g class="bl" opacity="0"><line/><text><tspan class="bn">${esc(b.short)}</tspan><tspan dx="5"> </tspan></text></g>`).join("")}</g>` +
    `<g id="marks">${people.map((p, i) => `<g class="hue" style="--h:${HUES[i % 8]}" visibility="hidden"><circle class="bloom" fill="url(#glo-${i})"/><use class="mark" href="#mk"/><text class="pn">${esc(p)}</text></g>`).join("")}</g>` +
    `<g id="comet"><circle class="bloom" id="cmGlow" fill="url(#glo-b)"/><path class="comet-tail" id="cmTail" opacity=".55"/><circle class="comet-core" id="cmCore"/></g>` +
    `<circle id="selRing" visibility="hidden"/>`;
}
const rowEls = [...map.querySelectorAll("#rows path")], dotEls = [...map.querySelectorAll("#dots circle")];
const trailEls = [...map.querySelectorAll("#trails g")].map(g => [...g.children]);
const tickEls = [...map.querySelectorAll("#ticks g")].map(g => [...g.children]);
const hourEls = [...map.querySelectorAll("#hours text")].map(el => ({ el, t: +el.dataset.t }));
const labEls = [...map.querySelectorAll("#labels g")].map(g => ({ g, line: g.firstChild, text: g.lastChild, cnt: g.lastChild.lastChild }));
const markEls = [...map.querySelectorAll("#marks g")].map(g => ({ g, glow: g.children[0], use: g.children[1], name: g.children[2] }));
const selRing = $("#selRing"), ringHit = $("#ringHit");
const seq = people.map(p => N.filter(n => n.who === p));
N.forEach(n => { n.tl = n.kind === "result" ? .075 : n.kind === "work" ? .052 : .03; });

/* how far each cluster name is lifted so that names do not collide: fixed once, from the final relief seen straight on */
heights(SPAN + 1);
{
  const placed = [];
  B.map((b, i) => { b.zf = zAt(b.u, b.v); const p = proj(b.u, b.v, b.zf + .07); return { i, x: p[0], y: p[1], w: (b.short.length + 4) * 6.3 }; })
    .sort((a, c) => c.y - a.y).forEach(l => {
      let lift = 0;
      for (let tries = 0; tries < 12; tries++) {
        const hit = placed.some(q => Math.abs(q.x - l.x) < (q.w + l.w) / 2 && Math.abs(q.y - (l.y - lift)) < 15);
        if (!hit) break; lift += 15;
      }
      placed.push({ x: l.x, y: l.y - lift, w: l.w }); B[l.i].lift = lift;
    });
}

let T = reduce ? SPAN : 0, playing = !reduce, selMap = null, shownCount = -1, lastT = -1, lastYaw = 9, lean = 0, leanTo = 0;
const PLAY_S = 55, SPEEDS = [1, 2, 5];
let speed = 1;  // the replay runs this many times faster

function arc(a, b, s) {  // a point on the hop from item a to item b, lifted off the surface in the middle
  const u = a.u + (b.u - a.u) * s, v = a.v + (b.v - a.v) * s, d = Math.hypot(b.u - a.u, b.v - a.v);
  return proj(u, v, zAt(u, v) + .012 + (.03 + .16 * d) * Math.sin(Math.PI * s));
}
function hop(a, b, upTo) { const ps = []; for (let k = 0; k <= 9; k++) ps.push(arc(a, b, k / 9 * upTo)); return ps; }

function drawMap(now) {
  const yaw = reduce ? 0 : (2.2 * Math.sin(now / 6500) + lean) * RAD;
  if (T === lastT && Math.abs(yaw - lastYaw) < 1e-4) return;
  cyaw = Math.cos(yaw); syaw = Math.sin(yaw);
  if (T !== lastT) heights(T);
  lastT = T; lastYaw = yaw;

  const rim = []; for (let a = 0; a < 360; a += 5) rim.push(onRing(1, a));
  const dd = line(rim) + "Z"; $("#disc").setAttribute("d", dd); $("#discEdge").setAttribute("d", dd);
  if (!$("#spec").hasAttribute("rx")) { const s = proj(-.42, -.42, 0), e = $("#spec"); e.setAttribute("cx", f1(s[0])); e.setAttribute("cy", f1(s[1])); e.setAttribute("rx", f1(S * .5)); e.setAttribute("ry", f1(S * .2)); e.setAttribute("transform", `rotate(-14 ${f1(s[0])} ${f1(s[1])})`); }

  for (let j = 0; j < GY; j++) {  // ridgelines from the back to the front, cut at the rim; each one hides what lies behind it
    const v = -1 + j * dv, half = Math.sqrt(Math.max(0, 1 - v * v)) * .985, f = rowEls[2 * j], l = rowEls[2 * j + 1];
    if (half < .06) { f.setAttribute("d", ""); l.setAttribute("d", ""); continue; }
    const ps = [proj(-half, v, zAt(-half, v))];
    for (let i = 0; i < GX; i++) { const u = -1 + i * du; if (u > -half && u < half) ps.push(proj(u, v, Z[j * GX + i])); }
    ps.push(proj(half, v, zAt(half, v)));
    const d = line(ps), near = j / (GY - 1);
    f.setAttribute("d", d + `L${pt(proj(half, v, 0))}L${pt(proj(-half, v, 0))}Z`); l.setAttribute("d", d);
    if (!l.hasAttribute("stroke-width")) { l.setAttribute("stroke-width", (.4 + .7 * near).toFixed(2)); l.setAttribute("opacity", (.1 + .42 * near).toFixed(2)); }
  }

  /* the ring of board time: a tick for every item, the part already played is heavier, and a comet marks the present */
  const full = []; for (let a = A0; a <= A1 + .01; a += 4) full.push(onRing(RT, a));
  const fd = line(full); $("#ringBase").setAttribute("d", fd); ringHit.setAttribute("d", fd);
  const aNow = degOf(T), past = []; for (let a = A0; a < aNow; a += 3) past.push(onRing(RT, a)); past.push(onRing(RT, aNow));
  $("#ringPast").setAttribute("d", ribbon(past, q => .7 + 4.2 * (q[2] - .9)));
  const e0 = onRing(RT, A1 + 2.2), e1 = onRing(RT - .028, A1 - .4), e2 = onRing(RT + .028, A1 - .4);
  $("#chev").setAttribute("d", `M${pt(e1)}L${pt(e0)}L${pt(e2)}`);
  const td = people.map(() => ["", ""]);
  for (const n of N) { const a = degOf(n.t); td[n.pi][n.t > T ? 1 : 0] += `M${pt(onRing(RT + .014, a))}L${pt(onRing(RT + .014 + n.tl, a))}`; }
  td.forEach((d, i) => { tickEls[i][0].setAttribute("d", d[0]); tickEls[i][1].setAttribute("d", d[1]); });
  for (const h of hourEls) { const p = onRing(RT - .085, degOf(h.t)); h.el.setAttribute("x", f1(p[0])); h.el.setAttribute("y", f1(p[1] + 4)); }
  const tail = []; for (let k = 0; k <= 10; k++) tail.push(onRing(RT, Math.max(A0, aNow - 26 + 2.6 * k)));
  const hd = tail[10];
  $("#cmTail").setAttribute("d", ribbon(tail, (q, i) => 5.4 * hd[2] * i / 10));
  $("#cmCore").setAttribute("cx", f1(hd[0])); $("#cmCore").setAttribute("cy", f1(hd[1])); $("#cmCore").setAttribute("r", f1(3.3 * hd[2]));
  $("#cmGlow").setAttribute("cx", f1(hd[0])); $("#cmGlow").setAttribute("cy", f1(hd[1])); $("#cmGlow").setAttribute("r", f1(19 * hd[2]));

  let count = 0;
  for (const n of N) {
    const el = dotEls[n.i];
    if (n.t > T) { if (n.vis) { el.setAttribute("visibility", "hidden"); n.vis = false; } continue; }
    count++;
    if (!n.vis) { el.setAttribute("visibility", "visible"); n.vis = true; }
    const p = proj(n.u, n.v, zAt(n.u, n.v) + .004), g = ease(clamp((T - n.t) / .05, 0, 1));
    n.sx = p[0]; n.sy = p[1];
    el.setAttribute("cx", f1(p[0])); el.setAttribute("cy", f1(p[1])); el.setAttribute("r", (rOf(n) * p[2] * (.4 + .6 * g) * (1 + 1.2 * (1 - g))).toFixed(2));
  }

  people.forEach((_, pi) => {  // each person's agents: a mark that travels to the next item they post; its last hops are a tapered tail
    const s = seq[pi], m = markEls[pi]; let k = -1;
    while (k + 1 < s.length && s[k + 1].t <= T) k++;
    let part = null, pos = null;
    if (k + 1 < s.length) {
      const a = k >= 0 ? s[k] : null, b = s[k + 1], w = a ? Math.min(.12, (b.t - a.t) * .9) : 0;
      if (a && w > 0 && T > b.t - w) { part = [a, b, ease((T - (b.t - w)) / w)]; pos = arc(a, b, part[2]); }
    }
    if (!pos && k >= 0) pos = proj(s[k].u, s[k].v, zAt(s[k].u, s[k].v) + .012);
    const old = ["", ""]; let head = [];
    for (let h = Math.max(1, k - 9); h <= k; h++) {
      const ps = hop(s[h - 1], s[h], 1);
      if (k - h < 2) head = head.concat(ps); else old[k - h < 5 ? 1 : 0] += line(ps);
    }
    if (part) head = head.concat(hop(part[0], part[1], part[2]));
    trailEls[pi][0].setAttribute("d", old[0]); trailEls[pi][1].setAttribute("d", old[1]);
    trailEls[pi][2].setAttribute("d", ribbon(head, (q, i) => .5 + 3.4 * i / Math.max(1, head.length - 1)));
    if (!pos) { m.g.setAttribute("visibility", "hidden"); return; }
    m.g.setAttribute("visibility", "visible");
    const sz = 20 * pos[2], my = pos[1] - sz * .55;
    m.glow.setAttribute("cx", f1(pos[0])); m.glow.setAttribute("cy", f1(my)); m.glow.setAttribute("r", f1(sz * 1.35));
    m.use.setAttribute("x", f1(pos[0] - sz / 2)); m.use.setAttribute("y", f1(my - sz / 2)); m.use.setAttribute("width", f1(sz)); m.use.setAttribute("height", f1(sz));
    m.name.setAttribute("x", f1(pos[0])); m.name.setAttribute("y", f1(my - sz * .5 - 5));
  });

  B.forEach((b, i) => {
    const L = labEls[i], o = ease(clamp((T - b.first) / .08 + (T >= b.first ? .25 : 0), 0, 1));
    L.g.setAttribute("opacity", o.toFixed(2));
    if (!o) return;
    const p0 = proj(b.u, b.v, zAt(b.u, b.v)), p1 = proj(b.u, b.v, b.zf + .07), ty = p1[1] - b.lift;
    L.line.setAttribute("x1", f1(p0[0])); L.line.setAttribute("y1", f1(p0[1])); L.line.setAttribute("x2", f1(p1[0])); L.line.setAttribute("y2", f1(ty + 3));
    L.text.setAttribute("x", f1(p1[0])); L.text.setAttribute("y", f1(ty - 2));
  });

  const s = selMap && byId.get(selMap);
  if (s && s.vis) { selRing.setAttribute("visibility", "visible"); selRing.setAttribute("cx", f1(s.sx)); selRing.setAttribute("cy", f1(s.sy)); selRing.setAttribute("r", "9"); }
  else selRing.setAttribute("visibility", "hidden");

  if (count !== shownCount) { shownCount = count; mapWords(count); }
  $("#clock").textContent = clock(T);
  const played = Math.round(T / SPAN * 1000); if (+scrub.value !== played) scrub.value = played;
  scrub.style.setProperty("--p", played / 10 + "%"); scrub.setAttribute("aria-valuetext", clock(T));
  ringHit.setAttribute("aria-valuenow", Math.round(T / SPAN * 100)); ringHit.setAttribute("aria-valuetext", clock(T));
}

function mapWords(count) {
  const n = count ? N[count - 1] : null;
  $("#cItems").textContent = count;
  $("#cBasins").textContent = n ? n.cB : 0;
  $("#cMoves").textContent = n ? n.cM : 0;
  $("#cNew").textContent = `${n ? n.cN : 0} to a new one`;
  B.forEach((b, i) => { let c = 0; for (const it of b.items) { if (it.t > T) break; c++; } labEls[i].cnt.textContent = c; });
  const s = selMap && byId.get(selMap);
  $("#mItem").innerHTML = s ? `<div class="lab">Selected item</div>` + itemHtml(s) : n ? `<div class="lab">Latest item</div>` + itemHtml(n) : `<div class="lab">Latest item</div><p style="color:var(--faint)">The board is empty at ${clock(0)}.</p>`;
}

const playBtn = $("#play");
function setPlaying(p) { playing = p && !reduce; playBtn.textContent = playing ? "Pause" : T >= SPAN ? "Replay" : "Play"; }
function setT(t) { T = clamp(t, 0, SPAN); if (!playing) setPlaying(false); }
playBtn.onclick = () => { if (reduce) return; if (!playing && T >= SPAN) T = 0; setPlaying(!playing); };
if (reduce) playBtn.hidden = true;
const scrub = $("#scrub"), speedBtn = $("#speed");
scrub.addEventListener("input", () => { setPlaying(false); setT(scrub.value / 1000 * SPAN); });  // the slider and the ring move the same board time
speedBtn.onclick = () => {
  speed = SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length];
  speedBtn.textContent = speed + "×"; speedBtn.setAttribute("aria-label", `Replay speed: ${speed} times. Press to change.`);
};
if (reduce) speedBtn.hidden = true;
const at = ev => { const r = map.getBoundingClientRect(); return [(ev.clientX - r.left) / r.width * 1000, (ev.clientY - r.top) / r.height * VH]; };
function ringT(ev) {  // the board time under the pointer: the nearest point of the ring
  const [x, y] = at(ev); let best = 0, bd = 1e9;
  for (let k = 0; k <= 300; k++) { const p = onRing(RT, A0 + (A1 - A0) * k / 300), d = (p[0] - x) ** 2 + (p[1] - y) ** 2; if (d < bd) { bd = d; best = k; } }
  return SPAN * best / 300;
}
ringHit.addEventListener("pointerdown", ev => { ringHit.setPointerCapture(ev.pointerId); setPlaying(false); setT(ringT(ev)); ev.stopPropagation(); });
ringHit.addEventListener("pointermove", ev => { if (ringHit.hasPointerCapture(ev.pointerId)) setT(ringT(ev)); });
ringHit.addEventListener("click", ev => ev.stopPropagation());
function stepItem(dir) {
  setPlaying(false);
  let k = -1; while (k + 1 < N.length && N[k + 1].t <= T) k++;
  setT(N[clamp(k + dir, 0, N.length - 1)].t + .1);
}
ringHit.addEventListener("keydown", ev => { if (ev.key === "ArrowRight" || ev.key === "ArrowLeft") { stepItem(ev.key === "ArrowRight" ? 1 : -1); ev.preventDefault(); ev.stopPropagation(); } });
map.addEventListener("click", ev => {
  const [x, y] = at(ev); let best = null, bd = 16;
  for (const n of N) if (n.vis) { const d = Math.hypot(n.sx - x, n.sy - y); if (d < bd) { bd = d; best = n; } }
  go("map", best ? best.id : null);
});
map.addEventListener("pointermove", ev => { const r = map.getBoundingClientRect(); leanTo = ((ev.clientX - r.left) / r.width - .5) * 5; });
map.addEventListener("pointerleave", () => { leanTo = 0; });

$("#mSentence").innerHTML = `The agents of <b>${words[people.length] || people.length}</b> people posted <b>${N.length}</b> board items in ${SPAN.toFixed(1)} hours, and a judge model sorted them into <b>${B.length}</b> clusters of ideas.`;
$("#cItemsOf").textContent = `of ${N.length}`; $("#cBasinsOf").textContent = `of ${B.length}`;
$("#mKey").innerHTML = keyHtml(`<span><svg viewBox="0 0 16 16"><path d="${MARK}" fill="var(--mute)"/></svg>one person's agents</span>`);
$("#mNote").textContent = `Each hill is a cluster, and its height is the number of items posted there so far. The ring is board time: one tick for each item, and you can drag along it. Positions come from the judge model (${R.judge}): it compared items three at a time by method, the comparisons were embedded in two dimensions (t-STE), each axis was mostly rank-scaled, and the square was mapped onto the disc. Snapshot ${R.snapshot}.`;

/* ───────── the tree on the disc ───────── */
const tree = $("#tree"), TX = 500, TY = 345, TR = 262, SECT = 360 / B.length;
N.forEach(n => {
  n.tr = TR * (.1 + .86 * Math.pow(n.i / (N.length - 1), .72));  // the first item near the centre, the last at the rim
  n.ta = -90 + (n.b + .5) * SECT + (((n.i * 37) % 9) - 4) / 4 * SECT * .3;  // the sector of its cluster, spread a little
  n.tx = TX + n.tr * Math.cos(n.ta * RAD); n.ty = TY + n.tr * Math.sin(n.ta * RAD);
});
const kids = new Map(N.map(n => [n.id, []]));
N.forEach(n => n.parents.forEach(p => kids.get(p).push(n.id)));
const links = [];
N.forEach(n => n.parents.forEach(pid => {
  const p = byId.get(pid); let da = n.ta - p.ta; if (da > 180) da -= 360; if (da < -180) da += 360;
  const same = p.b === n.b, bulge = same ? ((n.i + p.i) % 2 ? 1 : -1) * Math.min(9, 3 + Math.abs(n.tr - p.tr) * .06) : 0;
  let d = "";
  for (let k = 0; k <= 14; k++) {  // a spiral: the radius and the angle both go evenly from the earlier item to the later one
    const s = k / 14, r = p.tr + (n.tr - p.tr) * s, a = (p.ta + da * s + bulge * Math.sin(Math.PI * s)) * RAD;
    d += (k ? "L" : "M") + f1(TX + r * Math.cos(a)) + " " + f1(TY + r * Math.sin(a));
  }
  links.push({ p: pid, c: n.id, x: !same, d, r: n.i / N.length });
}));
tree.innerHTML =
  `<circle class="atmo" cx="${TX}" cy="${TY}" r="${TR * 1.75}" fill="url(#atmo)"/><circle class="shade" cx="${f1(TX + TR * .07)}" cy="${f1(TY + TR * .15)}" r="${f1(TR * 1.22)}" fill="url(#shade)"/>` +
  `<circle class="body" cx="${TX}" cy="${TY}" r="${TR + 12}"/>` +
  `<ellipse class="spec" cx="${f1(TX - TR * .36)}" cy="${f1(TY - TR * .42)}" rx="${f1(TR * .56)}" ry="${f1(TR * .34)}" transform="rotate(-34 ${f1(TX - TR * .36)} ${f1(TY - TR * .42)})" fill="url(#spec)"/>` +
  B.map((b, i) => { const a = (-90 + i * SECT) * RAD, c = Math.cos(a), s = Math.sin(a); return `<line class="spoke" x1="${f1(TX + TR * .1 * c)}" y1="${f1(TY + TR * .1 * s)}" x2="${f1(TX + (TR + 12) * c)}" y2="${f1(TY + (TR + 12) * s)}"/>`; }).join("") +
  B.map((b, i) => { const a = (-90 + (i + .5) * SECT) * RAD, c = Math.cos(a), s = Math.sin(a);
    return `<text class="sect" x="${f1(TX + (TR + 30) * c)}" y="${f1(TY + (TR + 30) * s + 4)}" text-anchor="${Math.abs(c) < .2 ? "middle" : c > 0 ? "start" : "end"}">${esc(b.short)}</text>`; }).join("") +
  `<g id="tLinks">${links.map(l => `<path class="lk${l.x ? " x" : ""}" style="--r:${l.r.toFixed(3)}" d="${l.d}"/>`).join("")}</g><g id="tFlow"></g>` +
  `<g id="tNodes">${N.map(n => `<circle class="nd hue ${n.kind}" style="--h:${n.h};--r:${(n.i / N.length).toFixed(3)}" cx="${f1(n.tx)}" cy="${f1(n.ty)}" r="${rOf(n) * .92}"/>`).join("")}</g>` +
  `<circle id="tSel" r="9" visibility="hidden"/>` +
  `<g>${N.map(n => `<circle class="hit" data-id="${n.id}" cx="${f1(n.tx)}" cy="${f1(n.ty)}" r="8"/>`).join("")}</g>`;
const linkEls = [...tree.querySelectorAll(".lk")], nodeEls = [...tree.querySelectorAll(".nd")], sectEls = [...tree.querySelectorAll(".sect")], tLinks = $("#tLinks"), tFlow = $("#tFlow");
const walk = (id, next) => { const out = new Set(), todo = [id]; while (todo.length) for (const q of next(todo.pop())) if (!out.has(q)) { out.add(q); todo.push(q); } return out; };
const bestRow = R.climb.base.length ? { item: R.climb.base[R.climb.base.length - 1].id } : null;  // the result that set the board's latest record of the untrained base
let selTree = null;

function drawTree() {
  const s = selTree && byId.get(selTree);
  tree.classList.toggle("has-sel", !!s);
  const anc = s ? walk(s.id, id => byId.get(id).parents) : new Set(), desc = s ? walk(s.id, id => kids.get(id)) : new Set();
  const lit = new Set([...anc, ...desc]); if (s) lit.add(s.id);
  N.forEach(n => nodeEls[n.i].classList.toggle("lit", lit.has(n.id)));
  const front = []; let flow = "";
  links.forEach((l, i) => {
    const a = s && (l.c === s.id || anc.has(l.c)), d = s && (l.p === s.id || desc.has(l.p));
    linkEls[i].classList.toggle("anc", !!a); linkEls[i].classList.toggle("desc", !!d && !a);
    if (a) { front.push(linkEls[i]); flow += `<path class="flow" pathLength="1" style="animation-delay:${(-3.2 * (1 - l.r)).toFixed(2)}s" d="${l.d}"/>`; }
  });
  front.forEach(el => tLinks.appendChild(el));
  tFlow.innerHTML = flow;  // a small light runs along each link of the lineage, from the earlier item to the later one
  const lanes = new Set(s ? [s.b, ...[...anc].map(id => byId.get(id).b)] : []);
  sectEls.forEach((t, i) => t.classList.toggle("on", lanes.has(i)));
  const ring = $("#tSel");
  if (s) { ring.setAttribute("visibility", "visible"); ring.setAttribute("cx", f1(s.tx)); ring.setAttribute("cy", f1(s.ty)); } else ring.setAttribute("visibility", "hidden");
  $("#tClear").hidden = !s;
  if (!s) { $("#tItem").innerHTML = `<div class="lab">No item selected</div><p style="color:var(--faint)">Select a dot to light the items it builds on and the items that build on it.</p>`; return; }
  const rows = (R.scores[s.id] || []).slice().sort((a, b) => b.right / b.n - a.right / a.n).slice(0, 2)  // the board's two best score rows of this result
    .map(r => `<div class="more one"><b>${r.right} of ${r.n}</b> on ${esc(r.benchmark)}: ${esc(r.model === "rl" ? "RL" : r.model)}, ${esc(r.config)}</div>`).join("");
  const nb = new Set([...anc].map(id => byId.get(id).b)).size;
  $("#tItem").innerHTML = `<div class="lab">Selected item</div>` + itemHtml(s, rows +
    `<div class="more">Builds on <b>${anc.size}</b> earlier item${anc.size === 1 ? "" : "s"} from <b>${nb}</b> cluster${nb === 1 ? "" : "s"}. <b>${desc.size}</b> later item${desc.size === 1 ? " builds" : "s build"} on it.</div>`);
}
function growTree() { if (reduce) return; tree.classList.remove("grow"); void tree.getBoundingClientRect(); tree.classList.add("grow"); }
tree.addEventListener("click", ev => { const id = ev.target.dataset && ev.target.dataset.id; go("tree", id || null); });
$("#tBest").onclick = () => bestRow && go("tree", bestRow.item);
$("#tReplay").onclick = growTree; if (reduce) $("#tReplay").hidden = true;
$("#tClear").onclick = () => go("tree", null);
if (!bestRow) $("#tBest").hidden = true;

const nLinks = links.length, nCross = links.filter(l => l.x).length;
$("#tSentence").innerHTML = `<b>${nLinks}</b> links record which earlier items each item builds on, and <b>${nCross}</b> of them join two different clusters.`;
$("#tMerge").textContent = N.filter(n => n.parents.length > 1).length; $("#tMergeOf").textContent = `of ${N.length}`;
$("#tDepth").textContent = R.tree.max_depth;
$("#tKey").innerHTML = keyHtml(`<span><svg viewBox="0 0 14 14"><path d="M1 11C6 11 8 3 13 3" fill="none" stroke="var(--blue)" stroke-width="1.5"/></svg>built on</span>`) +
  people.map((p, i) => `<span class="p hue" style="--h:${HUES[i % HUES.length]}">${esc(p)}</span>`).join("");
$("#tNote").textContent = `The first item is at the centre and the last at the rim, each in the sector of its cluster. A line that crosses into another sector carries an idea from one cluster into another. ${R.tree.explicit_links} links are item ids that an item names in its own text; the rest were found by the judge model (${R.judge}) reading the items. Snapshot ${R.snapshot}.`;

/* ───────── views, the address, the keyboard ───────── */
const view = "__VIEW__"; let grown = false;  // slide 1 is the map and slide 2 the tree: the same page, one view each
function show() {
  $("#viewMap").hidden = view !== "map"; $("#viewTree").hidden = view !== "tree";
  if (view === "tree") { drawTree(); if (!grown) { grown = true; growTree(); } }
  else { shownCount = -1; lastT = -1; if (selMap) { const s = byId.get(selMap); if (s.t > T) T = Math.min(SPAN, s.t + .1); setPlaying(false); } }
}
/* the selected item is the address (/demo/ali/slide1#result-c36598), so every state has a link and Back works */
function go(v, id) {
  if (v !== view) return;
  const h = "#" + (id || "");
  if (location.hash !== h && (id || location.hash)) history.pushState(null, "", id ? h : location.pathname + location.search);
  read();
}
function read() {
  const id = byId.has(location.hash.slice(1)) ? location.hash.slice(1) : null;
  if (view === "map") selMap = id; else selTree = id;
  show();
}
addEventListener("hashchange", read); addEventListener("popstate", read);
addEventListener("keydown", ev => {
  if (ev.target.closest && ev.target.closest("button, summary, a") && (ev.key === " " || ev.key === "Enter")) return;
  if (ev.target === scrub) return;  // on the slider the arrow keys move the time
  if (ev.key === "ArrowRight" || ev.key === "PageDown") slide(1);
  else if (ev.key === "ArrowLeft" || ev.key === "PageUp") slide(-1);
  else if (ev.key === "Escape") go(view, null);
  else if (ev.key === "t") toggleTheme();
  else if (view === "map" && ev.key === " ") { playBtn.click(); ev.preventDefault(); }
});

read(); setPlaying(playing);
if (!selTree && bestRow) { selTree = bestRow.item; if (view === "tree") drawTree(); }  // the tree opens on the result that set the latest base record
let prev = performance.now();
function frame(now) {
  const dt = Math.min(.1, (now - prev) / 1000); prev = now;
  if (view === "map") {
    if (playing) { T = Math.min(SPAN, T + dt * speed * SPAN / PLAY_S); if (T >= SPAN) setPlaying(false); }
    lean += (leanTo - lean) * Math.min(1, dt * 3);
    drawMap(now);
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
})();
</script>
"""

# slide3: the climb of the best score over the idea disc
STEPS = r"""<style>
/* Layout: the look of the team site (monitor.invariant.team). On the left one picture with no frame inside it: the
   climb of the best score, drawn as a lit step line over board time, floats above the idea disc, and a fine line
   ties each record to the result that set it on the disc. On the right a flat column behind one hairline: the
   sentence, the score as one large number, and the record steps.
   Tokens are those of tools/architecture.py, unchanged: one light from the upper left, --blue the one accent,
   a person's colour is oklch(var(--pl) var(--pc) <hue>). One typeface, Archivo. */
:root {
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --pl: .56; --pc: .15; --dim: .16;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue); --lift: 38%; --ridge: #101820;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18);
  --f: "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --pl: .78; --pc: .13; --dim: .24;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff; --lift: 55%; --ridge: #dfeaf6;
    --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
  --blue: #8fb1ff; --red: #ff6b7c;
  --pl: .78; --pc: .13; --dim: .24;
  --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
  --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
  --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff; --lift: 55%; --ridge: #dfeaf6;
  --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7);
  color-scheme: dark;
}
* { box-sizing: border-box; }
body {
  color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 var(--f); font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
a { color: inherit; text-decoration: none; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
p, h1, ol, li { margin: 0; padding: 0; }
.hue { --c: oklch(var(--pl) var(--pc) var(--h)); }

.page {
  max-width: 1840px; margin: 0 auto; padding-block: 20px 24px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: flex; flex-direction: column;
}
@media (min-width: 900px) { .page { padding-left: max(40px, env(safe-area-inset-left, 0px)); padding-right: max(40px, env(safe-area-inset-right, 0px)); } }
.top { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin-right: 6px; }
.top a { color: var(--mute); }
.top a:hover { color: var(--ink); }
.status { color: var(--mute); white-space: nowrap; }

.view { display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 28vw); align-items: stretch; }
@media (max-width: 899px) { .view { grid-template-columns: minmax(0, 1fr); } }
.stage { min-width: 0; display: flex; flex-direction: column; padding: 4px 0 0; }
.stage svg { display: block; width: 100%; height: auto; max-height: calc(100vh - 176px); overflow: visible; font-family: var(--f); }
#map { touch-action: manipulation; }
.foot { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 22px; font-size: 12.5px; color: var(--mute); padding: 6px 0 0; }
.foot .key { display: flex; flex-wrap: wrap; gap: 6px 16px; }
.foot .key span { display: inline-flex; align-items: center; gap: 6px; }
.foot svg { width: 18px; height: 14px; flex: none; }
.foot .p { color: var(--c); font-weight: 620; }
.foot .run { flex: 1 1 100%; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; padding-bottom: 4px; }
.foot .run b { font-weight: 560; color: var(--ink); min-width: 74px; text-align: right; }
.quiet { font-weight: 560; color: var(--ink); border: 1px solid var(--faint); border-radius: 999px; padding: 5px 16px; font-size: 13px; }
.quiet.speed { padding: 5px 0; width: 46px; text-align: center; }
/* the slider of board time: a hairline with the part already played in ink, and one lit knob */
.scrub { flex: 1 1 200px; min-width: 0; height: 24px; margin: 0; padding: 0; background: none; -webkit-appearance: none; appearance: none; cursor: pointer; --p: 0%; }
.scrub::-webkit-slider-runnable-track { height: 2px; border-radius: 1px; background: linear-gradient(to right, var(--ink) var(--p), var(--rule) var(--p)); }
.scrub::-moz-range-track { height: 2px; border-radius: 1px; background: var(--rule); }
.scrub::-moz-range-progress { height: 2px; border-radius: 1px; background: var(--ink); }
.scrub::-webkit-slider-thumb { -webkit-appearance: none; width: 14px; height: 14px; margin-top: -6px; border-radius: 50%; background: var(--core); border: 1.5px solid var(--blue); box-shadow: 0 0 calc(var(--glow) * 10px) var(--blue); }
.scrub::-moz-range-thumb { width: 11px; height: 11px; border-radius: 50%; background: var(--core); border: 1.5px solid var(--blue); box-shadow: 0 0 calc(var(--glow) * 10px) var(--blue); }

/* the words column */
.side { min-width: 0; display: flex; flex-direction: column; gap: 13px; border-left: 1px solid var(--rule); padding: clamp(12px, 2vh, 28px) 0 0 clamp(28px, 2.8vw, 56px); margin-left: clamp(0px, 1.4vw, 28px); }
@media (max-width: 899px) { .side { border-left: 0; padding: 18px 0 0; margin-left: 0; } }
.head { display: flex; justify-content: space-between; font-size: 13px; color: var(--mute); font-weight: 560; }
.say { font-weight: 300; font-size: clamp(20px, 1.75vw, 28px); line-height: 1.22; letter-spacing: -.01em; color: var(--mute); text-wrap: balance; }
.say b { font-weight: 600; color: var(--ink); }
.fig { display: flex; flex-direction: column; gap: 4px; }
.big { font-weight: 250; font-size: clamp(60px, 5.5vw, 88px); line-height: .95; letter-spacing: -.03em; color: var(--ink); white-space: nowrap; }
.big small { font-size: .42em; font-weight: 300; color: var(--mute); letter-spacing: 0; margin-left: .12em; }
.big .up { font-size: .25em; font-weight: 620; letter-spacing: 0; color: var(--blue); margin-left: .5em; vertical-align: .9em; transition: opacity .5s; }
.cap { font-size: 13.5px; color: var(--mute); }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--rule); }
.pair b { display: block; font-weight: 400; font-size: 25px; line-height: 1.1; color: var(--ink); }
.pair span { font-size: 12.5px; color: var(--mute); }
.lab { font-size: 12.5px; font-weight: 640; color: var(--mute); margin-bottom: -8px; }
.steps { list-style: none; border-bottom: 1px solid var(--rule); }
.steps li { border-top: 1px solid var(--rule); transition: opacity .5s; }
.steps li.off { opacity: .32; }
.steps button { width: 100%; display: grid; grid-template-columns: 52px minmax(0, 1fr) auto; gap: 10px; align-items: baseline; padding: 6px 0; }
.steps .gain { font-weight: 620; color: var(--blue); font-size: 14.5px; }
.steps .gain.start { color: var(--faint); font-weight: 400; font-size: 13px; }
.steps .ttl { font-size: 13.5px; color: var(--mute); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.steps .pct { font-weight: 620; font-size: 15px; }
.steps li.sel .ttl { color: var(--ink); white-space: normal; }
.steps .more { display: none; padding: 0 0 10px 62px; font-size: 13px; color: var(--mute); line-height: 1.45; }
.steps .more p + p { margin-top: 6px; }
.steps li.sel .more { display: block; }
.steps .more b { font-weight: 600; color: var(--ink); }
.steps .more .who { color: var(--c); font-weight: 620; }
.steps .more .src { color: var(--faint); }
.how summary { font-size: 13.5px; font-weight: 560; color: var(--mute); cursor: pointer; padding: 2px 0 9px; border-bottom: 1px solid var(--rule); list-style: none; display: flex; justify-content: space-between; }
.how summary::-webkit-details-marker { display: none; }
.how summary::after { content: "+"; color: var(--faint); font-weight: 400; }
.how[open] summary::after { content: "\2212"; }
.note { font-size: 12.5px; color: var(--faint); line-height: 1.45; max-width: 62ch; padding-top: 10px; }

/* the lit body */
.atmo, .shade, .spec, .bloom { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.spec { opacity: var(--spec); }
.bloom { opacity: var(--bloom); }
.body { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.body-edge { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }

/* the relief */
.rf { fill: var(--glass); stroke: none; }
.rl { fill: none; stroke: var(--ridge); stroke-linejoin: round; }
.dot { fill: var(--c); }
.dot.work { fill: var(--glass); stroke: var(--c); stroke-width: 1.4; }
.trail { fill: none; stroke: var(--c); stroke-linecap: round; stroke-linejoin: round; }
.ptail { fill: var(--c); opacity: .75; }
.mark { fill: var(--c); }
.pn { font-size: 11.5px; font-weight: 620; fill: var(--c); text-anchor: middle; paint-order: stroke; stroke: var(--paper); stroke-width: 3.5px; stroke-linejoin: round; }
.bl line { stroke: var(--mute); stroke-width: .6; }
.bl text { font-size: 11.5px; font-weight: 400; fill: var(--faint); text-anchor: middle; paint-order: stroke; stroke: var(--glass-lo); stroke-width: 3px; stroke-linejoin: round; }
.bl .bn { fill: var(--ink); font-weight: 560; }
#selRing { fill: none; stroke: var(--blue); stroke-width: 1.8; }

/* the ring of board time */
.ring-base { fill: none; stroke: var(--faint); stroke-width: .8; opacity: .55; }
.ring-past { fill: var(--ink); opacity: .8; }
.ring-hit { fill: none; stroke: transparent; stroke-width: 34; pointer-events: stroke; cursor: grab; }
.ring-hit:focus { outline: none; }
.ring-hit:focus-visible + .ring-base { stroke: var(--blue); stroke-width: 2.2; opacity: 1; }
.tick { fill: none; stroke: var(--c); stroke-width: 1.15; }
.tick.future { opacity: .28; }
.hr { font-size: 11px; fill: var(--faint); text-anchor: middle; }
.hr.end { fill: var(--ink); font-weight: 560; }
.chev { fill: none; stroke: var(--mute); stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }
.comet-tail { fill: var(--blue); }
.comet-core { fill: var(--core); }

/* the climb above the disc: no frame and no axis lines; every level carries its own number */
.gap { fill: var(--blue); opacity: .07; }
.cl { fill: none; stroke-linejoin: round; stroke-linecap: round; }
.cl.rl-line { stroke: var(--ink); stroke-width: 1.4; stroke-dasharray: 1.5 5.5; opacity: .8; }
.cl.bs-glow { stroke: var(--blue); stroke-width: 10; opacity: calc(.18 * var(--bloom)); }
.cl.bs { stroke: var(--blue); stroke-width: 2.6; }
.cl.bs-core { stroke: var(--core); stroke-width: 1; }
.try { fill: var(--paper); stroke: var(--mute); stroke-width: 1; opacity: .8; }
.thread { stroke: var(--blue); stroke-width: .9; opacity: .5; }
.rec { fill: var(--core); stroke: var(--blue); stroke-width: 1.2; }
.pulse { fill: var(--core); }
.hit { fill: transparent; cursor: pointer; }
.ch { font-size: 11px; fill: var(--faint); text-anchor: middle; }
.jump { font-size: 13px; font-weight: 620; fill: var(--blue); paint-order: stroke; stroke: var(--paper); stroke-width: 4px; stroke-linejoin: round; }
.val { font-size: 24px; font-weight: 300; fill: var(--ink); paint-order: stroke; stroke: var(--paper); stroke-width: 5px; stroke-linejoin: round; }
.val .unit { font-size: 14px; fill: var(--mute); }
.val .who { font-size: 13px; font-weight: 560; fill: var(--blue); }
.rlv { font-size: 13px; font-weight: 400; fill: var(--mute); paint-order: stroke; stroke: var(--paper); stroke-width: 4px; stroke-linejoin: round; }
.rlv .n { font-weight: 640; fill: var(--ink); }
/* what the three slides share with the rest of the site: the theme control of /demo and the links between the slides */
html { background: var(--paper); }
body { margin: 0; }
[hidden] { display: none !important; }
.theme { margin-left: auto; color: var(--mute); font-weight: 500; padding: 2px 4px; border-radius: 3px; }
.theme:hover { color: var(--ink); }
.segs { display: flex; gap: 6px; margin-top: -8px; }
.segs a { flex: 1; height: 14px; position: relative; display: block; }
.segs a::after { content: ""; position: absolute; left: 0; right: 0; top: 6px; height: 2px; background: var(--rule); border-radius: 1px; }
.segs a[aria-current="page"]::after { background: var(--ink); }
.nav { display: flex; align-items: center; gap: 10px; margin-top: auto; padding-top: 8px; }
.nav a, .nav .off { font-weight: 620; font-size: 13.5px; padding: 8px 20px; border-radius: 999px; border: 1px solid var(--faint); }
.nav a.next { background: var(--btn); color: var(--btn-ink); border-color: transparent; box-shadow: inset 0 1px 0 var(--btn-edge); }
.nav .off { opacity: .35; }
.nav .hint { margin-left: auto; font-size: 12.5px; color: var(--faint); }
</style>
</head>
<body>

<svg id="defs" width="0" height="0" style="position:absolute" aria-hidden="true"></svg>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings">Findings</a>
    <button class="theme" id="theme" type="button">Light</button>
    <span class="status" id="status"></span>
  </header>

  <section class="view">
    <div class="stage">
      <svg id="map" viewBox="0 0 1000 790" role="img" aria-label="Above, a step line over board time: the best score of the untrained base, with the best score of the RL-trained model as a dotted line over it. Below, a glass disc: the idea map, where each cluster of ideas is a hill. A fine line ties each record of the base to the result that set it on the disc."></svg>
      <div class="foot">
        <div class="run"><button class="quiet" id="play">Pause</button><input class="scrub" id="scrub" type="range" min="0" max="1000" step="1" value="0" aria-label="Board time"><b id="clock"></b><button class="quiet speed" id="speed" aria-label="Replay speed: 1 times. Press to change.">1×</button></div>
        <div class="key" id="key"></div>
      </div>
    </div>
    <aside class="side">
      <div class="head"><span>Accuracy</span><span data-count></span></div>
      <nav class="segs" data-segs aria-label="Slides"></nav>
      <p class="say" id="sentence"></p>
      <div class="fig">
        <div class="big"><span id="vBase">–</span><small>%</small><span class="up" id="vUp" style="opacity:0"></span></div>
        <div class="cap">Untrained base, best score so far on <span id="bench"></span></div>
        <div class="pair">
          <div><b id="vRl">–</b><span>RL-trained model, best so far</span></div>
          <div><b id="vGap">–</b><span>RL's lead, in points</span></div>
        </div>
      </div>
      <div class="lab">Record steps of the base</div>
      <ol class="steps" id="steps"></ol>
      <details class="how"><summary>Where the numbers come from</summary><p class="note" id="note1"></p><p class="note" id="note2"></p></details>
      <div class="nav" data-nav></div>
    </aside>
  </section>
</div>

<script>
(() => {
"use strict";
const R = __DATA__, SLIDES = __SLIDES__, SLIDE = __SLIDE__;
const MARK = R.mark;
const $ = s => document.querySelector(s);
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
/* the slides of this part of the talk, and the theme control of /demo (the same stored choice, the same key t) */
const slide = d => { const s = SLIDES[SLIDE + d]; if (s) location.href = s.href + location.search; };
document.querySelectorAll("[data-count]").forEach(el => { el.textContent = `${SLIDE + 1} of ${SLIDES.length}`; });
document.querySelectorAll("[data-segs]").forEach(el => { el.innerHTML = SLIDES.map((s, i) => `<a href="${s.href}" aria-label="${s.name}"${i === SLIDE ? ' aria-current="page"' : ""}></a>`).join(""); });
document.querySelectorAll("[data-nav]").forEach(el => {
  const a = (s, cls, word) => s ? `<a class="${cls}" href="${s.href}">${word}</a>` : `<span class="${cls} off">${word}</span>`;
  el.innerHTML = a(SLIDES[SLIDE - 1], "", "Back") + a(SLIDES[SLIDE + 1], "next", "Next") + `<span class="hint">or use the arrow keys</span>`;
});
const themeNow = () => document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
function themeLabel() { const other = themeNow() === "dark" ? "Light" : "Dark"; $("#theme").textContent = other; $("#theme").setAttribute("aria-label", `${other} colours`); }
function toggleTheme() {
  const t = themeNow() === "dark" ? "light" : "dark"; document.documentElement.dataset.theme = t;
  try { localStorage.setItem("demo-theme", t); } catch (e) { /* storage blocked: the choice lasts until the page closes */ }
  themeLabel();
}
$("#theme").addEventListener("click", toggleTheme); themeLabel();
const HUES = [325, 150, 65, 195, 105, 45, 175, 350];  // the site's person colours, by place in the sorted list of names
const N = R.nodes, B = R.basins, SPAN = R.span_h, RAD = Math.PI / 180, C = R.climb;
const byId = new Map(N.map((n, i) => (n.i = i, [n.id, n])));
const people = [...new Set(N.map(n => n.who))].sort();
N.forEach(n => { n.pi = people.indexOf(n.who); n.h = HUES[n.pi % HUES.length]; });
const pad = v => String(v).padStart(2, "0");
const hm = t => { const m = Math.floor(R.t0_min + t * 60); return pad(Math.floor(m / 60) % 24) + ":" + pad(m % 60); };
const clock = t => hm(t) + " UTC";
const day = t => (R.t0_min + t * 60 >= 1440 ? "15 Nov" : "14 Nov");
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const ease = x => x * x * (3 - 2 * x);
const RK = { result: 4.4, work: 3.6 }, rOf = n => RK[n.kind] || 2.5;
const f1 = v => v.toFixed(1);
const stop = (o, c, a) => `<stop offset="${o}" style="stop-color:${c}${a == null ? "" : `;stop-opacity:${a}`}"/>`;
$("#defs").innerHTML = `<defs>` +  // the gradients of the site's lit body
  `<radialGradient id="body" cx=".36" cy=".3" r=".86">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
  `<linearGradient id="rim" x1=".12" y1=".08" x2=".9" y2=".94">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
  `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
  `<radialGradient id="shade">${stop(.6, "var(--ink)", .22)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
  `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
  `<linearGradient id="fall" gradientUnits="userSpaceOnUse" x1="0" y1="64" x2="0" y2="388">${stop(0, "var(--blue)", .2)}${stop(1, "var(--blue)", 0)}</linearGradient>` +
  `<radialGradient id="glo-b">${stop(0, "var(--blue)", .6)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
  people.map((p, i) => `<radialGradient id="glo-${i}" class="hue" style="--h:${HUES[i % 8]}">${stop(0, "var(--c)", .55)}${stop(1, "var(--c)", 0)}</radialGradient>`).join("") +
  `<symbol id="mk" viewBox="0 0 16 16"><path d="${MARK}"/></symbol></defs>`;
function ribbon(p, w) {  // a stroke whose width changes along it
  const n = p.length, L = [], Rr = [];
  for (let i = 0; i < n; i++) {
    const a = p[Math.max(0, i - 1)], b = p[Math.min(n - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, half = w(p[i], i) / 2;
    L.push(f1(p[i][0] - dy / d * half) + " " + f1(p[i][1] + dx / d * half)); Rr.push(f1(p[i][0] + dy / d * half) + " " + f1(p[i][1] - dx / d * half));
  }
  return n < 2 ? "" : "M" + L.join("L") + "L" + Rr.reverse().join("L") + "Z";
}

/* the record steps: the board's own score rows, by the rule of its chart. Steps that one result set at the same
   moment are played one after another, a few seconds of board time apart. */
function prepare(list) {
  let last = -1;
  list.forEach((s, k) => { s.pct = 100 * s.right / s.n; s.node = byId.get(s.id); s.at = Math.max(s.t, last + .004); last = s.at; s.prev = k ? list[k - 1].pct : null; s.on = false; s.trig = -1e9; });
  return list;
}
const steps = prepare(C.base), rlSteps = prepare(C.rl);
const tries = C.tries.map(s => ({ pct: 100 * s.right / s.n, t: s.t }));
const first = steps[0], best = steps[steps.length - 1], rlBest = rlSteps[rlSteps.length - 1];
B.forEach((b, i) => { b.items = N.filter(n => n.b === i); b.first = b.items[0].t; });
$("#status").textContent = `Board at ${clock(SPAN)}, ${day(SPAN)}, ${N.length} items`;
$("#bench").textContent = C.bench;

/* ───────── the relief on the disc ───────── */
const GX = 66, GY = 48, KX = 5, KY = 4, SIG = .105, ZS = .13, RT = 1.2, A0 = -77, A1 = 257;
const du = 2 / (GX - 1), dv = 2 / (GY - 1), KW = 2 * KX + 1;
const K = new Float32Array(KW * (2 * KY + 1));
for (let j = -KY; j <= KY; j++) for (let i = -KX; i <= KX; i++) K[(j + KY) * KW + i + KX] = Math.exp(-((i * du) ** 2 + (j * dv) ** 2) / (2 * SIG * SIG));
{
  /* each axis: 60 % rank, 40 % the judge's coordinate, so that the dense corner of the embedding is readable; then the square is mapped onto the disc */
  const axis = k => { const vs = N.map(n => n[k]), lo = Math.min(...vs), hi = Math.max(...vs), order = N.map((n, i) => i).sort((a, b) => vs[a] - vs[b]), out = [];
    order.forEach((i, r) => { out[i] = (.6 * r / (N.length - 1) + .4 * (vs[i] - lo) / (hi - lo)) * 2 - 1; }); return out; };
  const au = axis("x"), av = axis("y");
  for (const n of N) {
    const a = au[n.i], b = av[n.i];
    n.u = a * Math.sqrt(1 - b * b / 2) * .84; n.v = b * Math.sqrt(1 - a * a / 2) * .84;
    n.gi = Math.round((n.u + 1) / du); n.gj = Math.round((n.v + 1) / dv); n.w = n.kind === "result" ? 1 : n.kind === "work" ? .7 : .5;
  }
}
B.forEach(b => { b.u = b.items.reduce((s, n) => s + n.u, 0) / b.items.length; b.v = b.items.reduce((s, n) => s + n.v, 0) / b.items.length; });
const H = new Float32Array(GX * GY), Z = new Float32Array(GX * GY);
function heights(T) {
  H.fill(0);
  for (const n of N) {
    if (n.t > T) break;
    const w = n.w * ease(clamp((T - n.t) / .09, 0, 1));
    for (let j = -KY; j <= KY; j++) {
      const y = n.gj + j; if (y < 0 || y >= GY) continue;
      for (let i = -KX; i <= KX; i++) { const x = n.gi + i; if (x >= 0 && x < GX) H[y * GX + x] += w * K[(j + KY) * KW + i + KX]; }
    }
  }
  for (let k = 0; k < H.length; k++) Z[k] = ZS * Math.log1p(H[k] * .9);
}
function zAt(u, v) {
  const fx = clamp((u + 1) / du, 0, GX - 1.001), fy = clamp((v + 1) / dv, 0, GY - 1.001), i = fx | 0, j = fy | 0, a = fx - i, b = fy - j, k = j * GX + i;
  return (Z[k] * (1 - a) + Z[k + 1] * a) * (1 - b) + (Z[k + GX] * (1 - a) + Z[k + GX + 1] * a) * b;
}
/* our own projection: u to the right, v toward the viewer, z up; seen from 43 degrees above, with a little perspective */
const VH = 790, CX = 500, CY = 500, S = 290, D = 2700, SE = Math.sin(43 * RAD), CE = Math.cos(43 * RAD);
let cyaw = 1, syaw = 0;
function proj(u, v, z) {
  const xr = u * cyaw - v * syaw, yr = u * syaw + v * cyaw, k = D / (D - yr * S * CE);
  return [CX + xr * S * k, CY + (yr * SE - z * CE) * S * k, k];
}
const onRing = (r, deg) => proj(r * Math.cos(deg * RAD), r * Math.sin(deg * RAD), 0);
const degOf = t => A0 + (A1 - A0) * t / SPAN;
const pt = p => f1(p[0]) + " " + f1(p[1]);
const line = ps => ps.map((p, i) => (i ? "L" : "M") + pt(p)).join("");

/* the climb, in the flat of the screen above the disc: board time runs to the right over the width of the ring, and
   a score is a height, 5.4 units for each point, with 100 % near the top */
const XL = 150, XR = 850, Y100 = 64, PX = 5.4;
const cx = t => XL + (XR - XL) * t / SPAN, cy = pct => Y100 + (100 - pct) * PX;

const map = $("#map");
{
  let hours = "", top = `<text class="ch" x="${XL}" y="34">${hm(0)}</text><text class="ch" x="${XR}" y="34">${hm(SPAN)}</text>`;
  for (let m = Math.ceil(R.t0_min / 60) * 60; m <= R.t0_min + SPAN * 60; m += 60) {
    const t = (m - R.t0_min) / 60;
    hours += `<text class="hr" data-t="${t}">${pad(m / 60 % 24)}:00</text>`;
    if (t > .5 && SPAN - t > .5) top += `<text class="ch" x="${f1(cx(t))}" y="34">${pad(m / 60 % 24)}:00</text>`;
  }
  map.innerHTML =
    `<ellipse class="atmo" cx="${CX}" cy="${CY}" rx="${S * 1.9}" ry="${f1(S * 1.9 * SE)}" fill="url(#atmo)"/>` +
    `<ellipse class="shade" cx="${CX + S * .07}" cy="${f1(CY + S * .15)}" rx="${S * 1.22}" ry="${f1(S * 1.22 * SE)}" fill="url(#shade)"/>` +
    `<path class="ring-hit" id="ringHit" role="slider" tabindex="0" aria-label="Board time" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"/><path class="ring-base" id="ringBase"/>` +
    `<path class="ring-past" id="ringPast"/><path class="chev" id="chev"/>` +
    `<g id="ticks">${people.map((p, i) => `<g class="hue" style="--h:${HUES[i % 8]}"><path class="tick"/><path class="tick future"/></g>`).join("")}</g>` +
    `<g id="hours"><text class="hr end" data-t="0">${hm(0)}</text>${hours}<text class="hr end" data-t="${SPAN}">${hm(SPAN)}</text></g>` +
    `<path class="body-edge" id="discEdge" transform="translate(0 11)"/><path class="body" id="disc"/>` +
    `<ellipse class="spec" id="spec" fill="url(#spec)"/>` +
    `<g id="rows">${Array.from({ length: GY }, () => `<path class="rf"/><path class="rl"/>`).join("")}</g>` +
    `<g id="dots">${N.map(n => `<circle class="dot hue ${n.kind}" style="--h:${n.h}" visibility="hidden"/>`).join("")}</g>` +
    `<g id="trails">${people.map((p, i) => `<g class="hue" style="--h:${HUES[i % 8]}"><path class="trail" opacity=".22" stroke-width="1"/><path class="trail" opacity=".5" stroke-width="1.3"/><path class="ptail"/></g>`).join("")}</g>` +
    `<g id="labels">${B.map(b => `<g class="bl" opacity="0"><line/><text><tspan class="bn">${esc(b.short)}</tspan><tspan dx="5"> </tspan></text></g>`).join("")}</g>` +
    `<g id="marks">${people.map((p, i) => `<g class="hue" style="--h:${HUES[i % 8]}" visibility="hidden"><circle class="bloom" fill="url(#glo-${i})"/><use class="mark" href="#mk"/><text class="pn">${esc(p)}</text></g>`).join("")}</g>` +
    `<g id="comet"><circle class="bloom" id="cmGlow" fill="url(#glo-b)"/><path class="comet-tail" id="cmTail" opacity=".55"/><circle class="comet-core" id="cmCore"/></g>` +
    `<g id="climb">${top}` +
    `<g id="threads">${steps.map(() => `<line class="thread" visibility="hidden"/>`).join("")}</g>` +
    `<path id="fall" fill="url(#fall)" opacity="var(--bloom)" style="opacity:var(--bloom)"/><path class="gap" id="gap"/>` +
    `<g id="tries">${tries.map(a => `<circle class="try" cx="${f1(cx(a.t))}" cy="${f1(cy(a.pct))}" r="2.7" visibility="hidden"/>`).join("")}</g>` +
    `<path class="cl rl-line" id="rlLine"/><path class="cl bs-glow" id="bsGlow"/><path class="cl bs" id="bsLine"/><path class="cl bs-core" id="bsCore"/>` +
    `<g id="recs">${steps.map((s, i) => `<circle class="rec" cx="${f1(cx(s.at))}" cy="${f1(cy(s.pct))}" r="3.7" visibility="hidden"/>`).join("")}</g>` +
    `<g id="jumps">${steps.map((s, i) => { const big = i && s.pct - s.prev >= 2, left = cx(s.at) > 500;
      return big ? `<text class="jump" data-i="${i}" opacity="0" x="${f1(cx(s.at) + (left ? -9 : 9))}" y="${f1(cy((s.pct + s.prev) / 2) + 4)}" text-anchor="${left ? "end" : "start"}">+${(s.pct - s.prev).toFixed(1)}</text>` : ""; }).join("")}</g>` +
    `<circle class="pulse" id="pulse" r="3.4" visibility="hidden"/>` +
    `<g id="head" visibility="hidden"><circle class="bloom" id="hdGlow" r="20" fill="url(#glo-b)"/><circle class="comet-core" id="hdCore" r="4"/>` +
    `<text class="rlv" id="rlText"><tspan>RL </tspan><tspan class="n" id="rlNum"></tspan></text>` +
    `<text class="val" id="bsText"><tspan class="who">Base </tspan><tspan id="bsNum"></tspan><tspan class="unit"> %</tspan></text></g>` +
    `<g>${steps.map((s, i) => `<circle class="hit" data-step="${i}" cx="${f1(cx(s.at))}" cy="${f1(cy(s.pct))}" r="11"/>`).join("")}</g></g>` +
    `<circle id="selRing" visibility="hidden"/>`;
}
const rowEls = [...map.querySelectorAll("#rows path")], dotEls = [...map.querySelectorAll("#dots circle")];
const trailEls = [...map.querySelectorAll("#trails g")].map(g => [...g.children]);
const tickEls = [...map.querySelectorAll("#ticks g")].map(g => [...g.children]);
const hourEls = [...map.querySelectorAll("#hours text")].map(el => ({ el, t: +el.dataset.t }));
const labEls = [...map.querySelectorAll("#labels g")].map(g => ({ g, line: g.firstChild, text: g.lastChild, cnt: g.lastChild.lastChild }));
const markEls = [...map.querySelectorAll("#marks g")].map(g => ({ g, glow: g.children[0], use: g.children[1], name: g.children[2] }));
const threadEls = [...map.querySelectorAll("#threads line")], recEls = [...map.querySelectorAll("#recs circle")], tryEls = [...map.querySelectorAll("#tries circle")];
const jumpEls = [...map.querySelectorAll("#jumps text")].map(el => ({ el, s: steps[+el.dataset.i] }));
const selRing = $("#selRing"), ringHit = $("#ringHit"), pulse = $("#pulse");
const seq = people.map(p => N.filter(n => n.who === p));
N.forEach(n => { n.tl = n.kind === "result" ? .075 : n.kind === "work" ? .052 : .03; });

/* how far each cluster name is lifted so that names do not collide: fixed once, from the final relief seen straight on */
heights(SPAN + 1);
{
  const placed = [];
  B.map((b, i) => { b.zf = zAt(b.u, b.v); const p = proj(b.u, b.v, b.zf + .07); return { i, x: p[0], y: p[1], w: (b.short.length + 4) * 6.3 }; })
    .sort((a, c) => c.y - a.y).forEach(l => {
      let lift = 0;
      for (let tries = 0; tries < 12; tries++) {
        const hit = placed.some(q => Math.abs(q.x - l.x) < (q.w + l.w) / 2 && Math.abs(q.y - (l.y - lift)) < 15);
        if (!hit) break; lift += 15;
      }
      placed.push({ x: l.x, y: l.y - lift, w: l.w }); B[l.i].lift = lift;
    });
}

let T = reduce ? SPAN : 0, playing = !reduce, sel = -1, lastT = -1, lastYaw = 9, lean = 0, leanTo = 0, lastTrig = -1e9, shown = "", shownCount = -1;
let disp = null, rlDisp = null;  // the two levels as drawn, in percent; they ease toward the best score at the time shown
const PLAY_S = 40, JUMP_MS = 2100, RISE_MS = 620, SPEEDS = [1, 2, 5];
let speed = 1;  // the replay runs this many times faster; a record step then holds the clock for a shorter time, never under 0.7 s
const hold = () => Math.max(700, JUMP_MS / speed);

function arc(a, b, s) {  // a point on the hop from item a to item b, lifted off the surface in the middle
  const u = a.u + (b.u - a.u) * s, v = a.v + (b.v - a.v) * s, d = Math.hypot(b.u - a.u, b.v - a.v);
  return proj(u, v, zAt(u, v) + .012 + (.03 + .16 * d) * Math.sin(Math.PI * s));
}
function hop(a, b, upTo) { const ps = []; for (let k = 0; k <= 9; k++) ps.push(arc(a, b, k / 9 * upTo)); return ps; }
const topOn = list => { let s = null; for (const x of list) if (x.on) s = x; return s; };
function stairs(list, level, xEnd) {  // a step line: flat at each record's score until the next record, the newest record at the level drawn now
  const on = list.filter(s => s.on); if (!on.length || level == null) return [];
  const ps = [[cx(on[0].at), cy(on.length === 1 ? level : on[0].pct)]];
  for (let k = 1; k < on.length; k++) { const x = cx(on[k].at); ps.push([x, cy(on[k - 1].pct)], [x, cy(k === on.length - 1 ? level : on[k].pct)]); }
  ps.push([Math.max(xEnd, ps[ps.length - 1][0]), cy(level)]);
  return ps;
}

function draw(now, dt) {
  const yaw = reduce ? 0 : (2.2 * Math.sin(now / 6500) + lean) * RAD;
  /* the levels move on their own clock, so the picture is redrawn while they move */
  const bt = topOn(steps), rt = topOn(rlSteps);
  const bTarget = bt ? (now - bt.trig < RISE_MS && bt.prev != null ? bt.prev : bt.pct) : null, rTarget = rt ? rt.pct : null;
  const k = reduce ? 1 : Math.min(1, dt * 4.2);
  const move = (cur, target) => target == null ? null : cur == null ? target : Math.abs(target - cur) < .02 ? target : cur + (target - cur) * k;
  const nb = move(disp, bTarget), nr = move(rlDisp, rTarget);
  const moving = nb !== disp || nr !== rlDisp || now - lastTrig < JUMP_MS + 1800;
  disp = nb; rlDisp = nr;
  if (T === lastT && Math.abs(yaw - lastYaw) < 1e-4 && !moving) return;
  cyaw = Math.cos(yaw); syaw = Math.sin(yaw);
  if (T !== lastT) heights(T);
  lastT = T; lastYaw = yaw;

  const rim = []; for (let a = 0; a < 360; a += 5) rim.push(onRing(1, a));
  const dd = line(rim) + "Z"; $("#disc").setAttribute("d", dd); $("#discEdge").setAttribute("d", dd);
  if (!$("#spec").hasAttribute("rx")) { const s = proj(-.42, -.42, 0), e = $("#spec"); e.setAttribute("cx", f1(s[0])); e.setAttribute("cy", f1(s[1])); e.setAttribute("rx", f1(S * .5)); e.setAttribute("ry", f1(S * .2)); e.setAttribute("transform", `rotate(-14 ${f1(s[0])} ${f1(s[1])})`); }

  for (let j = 0; j < GY; j++) {  // ridgelines from the back to the front, cut at the rim; each one hides what lies behind it
    const v = -1 + j * dv, half = Math.sqrt(Math.max(0, 1 - v * v)) * .985, f = rowEls[2 * j], l = rowEls[2 * j + 1];
    if (half < .06) { f.setAttribute("d", ""); l.setAttribute("d", ""); continue; }
    const ps = [proj(-half, v, zAt(-half, v))];
    for (let i = 0; i < GX; i++) { const u = -1 + i * du; if (u > -half && u < half) ps.push(proj(u, v, Z[j * GX + i])); }
    ps.push(proj(half, v, zAt(half, v)));
    const d = line(ps), near = j / (GY - 1);
    f.setAttribute("d", d + `L${pt(proj(half, v, 0))}L${pt(proj(-half, v, 0))}Z`); l.setAttribute("d", d);
    if (!l.hasAttribute("stroke-width")) { l.setAttribute("stroke-width", (.4 + .7 * near).toFixed(2)); l.setAttribute("opacity", (.1 + .42 * near).toFixed(2)); }
  }

  /* the ring of board time */
  const full = []; for (let a = A0; a <= A1 + .01; a += 4) full.push(onRing(RT, a));
  const fd = line(full); $("#ringBase").setAttribute("d", fd); ringHit.setAttribute("d", fd);
  const aNow = degOf(T), past = []; for (let a = A0; a < aNow; a += 3) past.push(onRing(RT, a)); past.push(onRing(RT, aNow));
  $("#ringPast").setAttribute("d", ribbon(past, q => .7 + 4.2 * (q[2] - .9)));
  const e0 = onRing(RT, A1 + 2.2), e1 = onRing(RT - .028, A1 - .4), e2 = onRing(RT + .028, A1 - .4);
  $("#chev").setAttribute("d", `M${pt(e1)}L${pt(e0)}L${pt(e2)}`);
  const td = people.map(() => ["", ""]);
  for (const n of N) { const a = degOf(n.t); td[n.pi][n.t > T ? 1 : 0] += `M${pt(onRing(RT + .014, a))}L${pt(onRing(RT + .014 + n.tl, a))}`; }
  td.forEach((d, i) => { tickEls[i][0].setAttribute("d", d[0]); tickEls[i][1].setAttribute("d", d[1]); });
  for (const h of hourEls) { const p = onRing(RT - .085, degOf(h.t)); h.el.setAttribute("x", f1(p[0])); h.el.setAttribute("y", f1(p[1] + 4)); }
  const tail = []; for (let q = 0; q <= 10; q++) tail.push(onRing(RT, Math.max(A0, aNow - 26 + 2.6 * q)));
  const hd = tail[10];
  $("#cmTail").setAttribute("d", ribbon(tail, (q, i) => 5.4 * hd[2] * i / 10));
  $("#cmCore").setAttribute("cx", f1(hd[0])); $("#cmCore").setAttribute("cy", f1(hd[1])); $("#cmCore").setAttribute("r", f1(3.3 * hd[2]));
  $("#cmGlow").setAttribute("cx", f1(hd[0])); $("#cmGlow").setAttribute("cy", f1(hd[1])); $("#cmGlow").setAttribute("r", f1(19 * hd[2]));

  let count = 0;
  for (const n of N) {
    const el = dotEls[n.i];
    if (n.t > T) { if (n.vis) { el.setAttribute("visibility", "hidden"); n.vis = false; } continue; }
    count++;
    if (!n.vis) { el.setAttribute("visibility", "visible"); n.vis = true; }
    const p = proj(n.u, n.v, zAt(n.u, n.v) + .004), g = ease(clamp((T - n.t) / .05, 0, 1));
    n.sx = p[0]; n.sy = p[1];
    el.setAttribute("cx", f1(p[0])); el.setAttribute("cy", f1(p[1])); el.setAttribute("r", (rOf(n) * p[2] * (.4 + .6 * g) * (1 + 1.2 * (1 - g))).toFixed(2));
  }
  if (count !== shownCount) { shownCount = count; B.forEach((b, i) => { let c = 0; for (const it of b.items) { if (it.t > T) break; c++; } labEls[i].cnt.textContent = c; }); }

  people.forEach((_, pi) => {  // each person's agents: a mark that travels to the next item they post; its last hops are a tapered tail
    const s = seq[pi], m = markEls[pi]; let q = -1;
    while (q + 1 < s.length && s[q + 1].t <= T) q++;
    let part = null, pos = null;
    if (q + 1 < s.length) {
      const a = q >= 0 ? s[q] : null, b = s[q + 1], w = a ? Math.min(.12, (b.t - a.t) * .9) : 0;
      if (a && w > 0 && T > b.t - w) { part = [a, b, ease((T - (b.t - w)) / w)]; pos = arc(a, b, part[2]); }
    }
    if (!pos && q >= 0) pos = proj(s[q].u, s[q].v, zAt(s[q].u, s[q].v) + .012);
    const old = ["", ""]; let head = [];
    for (let h = Math.max(1, q - 9); h <= q; h++) {
      const ps = hop(s[h - 1], s[h], 1);
      if (q - h < 2) head = head.concat(ps); else old[q - h < 5 ? 1 : 0] += line(ps);
    }
    if (part) head = head.concat(hop(part[0], part[1], part[2]));
    trailEls[pi][0].setAttribute("d", old[0]); trailEls[pi][1].setAttribute("d", old[1]);
    trailEls[pi][2].setAttribute("d", ribbon(head, (p, i) => .5 + 3.4 * i / Math.max(1, head.length - 1)));
    if (!pos) { m.g.setAttribute("visibility", "hidden"); return; }
    m.g.setAttribute("visibility", "visible");
    const sz = 20 * pos[2], my = pos[1] - sz * .55;
    m.glow.setAttribute("cx", f1(pos[0])); m.glow.setAttribute("cy", f1(my)); m.glow.setAttribute("r", f1(sz * 1.35));
    m.use.setAttribute("x", f1(pos[0] - sz / 2)); m.use.setAttribute("y", f1(my - sz / 2)); m.use.setAttribute("width", f1(sz)); m.use.setAttribute("height", f1(sz));
    m.name.setAttribute("x", f1(pos[0])); m.name.setAttribute("y", f1(my - sz * .5 - 5));
  });

  B.forEach((b, i) => {
    const L = labEls[i], o = ease(clamp((T - b.first) / .08 + (T >= b.first ? .25 : 0), 0, 1));
    L.g.setAttribute("opacity", o.toFixed(2));
    if (!o) return;
    const p0 = proj(b.u, b.v, zAt(b.u, b.v)), p1 = proj(b.u, b.v, b.zf + .07), ty = p1[1] - b.lift;
    L.line.setAttribute("x1", f1(p0[0])); L.line.setAttribute("y1", f1(p0[1])); L.line.setAttribute("x2", f1(p1[0])); L.line.setAttribute("y2", f1(ty + 3));
    L.text.setAttribute("x", f1(p1[0])); L.text.setAttribute("y", f1(ty - 2));
  });

  /* the climb: the step line of the base, RL's dotted line over it, the gap between them, and the attempts that set no record */
  const xNow = cx(T), bp = stairs(steps, disp, xNow), rp = stairs(rlSteps, rlDisp, xNow), have = bp.length && rp.length;
  const bd = line(bp); $("#bsLine").setAttribute("d", bd); $("#bsCore").setAttribute("d", bd); $("#bsGlow").setAttribute("d", bd);
  $("#rlLine").setAttribute("d", line(rp));
  $("#gap").setAttribute("d", have ? line(bp) + "L" + rp.slice().reverse().map(pt).join("L") + "Z" : "");
  $("#fall").setAttribute("d", bp.length ? line(bp) + `L${f1(bp[bp.length - 1][0])} ${cy(40)}L${f1(bp[0][0])} ${cy(40)}Z` : "");
  tries.forEach((a, i) => tryEls[i].setAttribute("visibility", a.t <= T ? "visible" : "hidden"));
  let flying = false;
  steps.forEach((s, i) => {  // each record is tied to the result that set it; when it is set, a light runs up the line and the step rises
    const th = threadEls[i], rec = recEls[i], n = s.node, age = now - s.trig;
    if (!s.on) { th.setAttribute("visibility", "hidden"); rec.setAttribute("visibility", "hidden"); return; }
    const X = cx(s.at), Y = cy(s.pct), run = reduce ? 1 : ease(clamp(age / RISE_MS, 0, 1)), px = n.sx + (X - n.sx) * run, py = n.sy + (cy(s.prev == null ? s.pct : s.prev) - n.sy) * run;
    th.setAttribute("visibility", "visible"); th.setAttribute("x1", f1(n.sx)); th.setAttribute("y1", f1(n.sy));
    const arrived = disp != null && disp >= s.pct - .05 && run >= 1;
    th.setAttribute("x2", f1(run < 1 ? px : X)); th.setAttribute("y2", f1(run < 1 ? py : arrived ? Y : cy(Math.min(s.pct, disp == null ? s.pct : disp))));
    rec.setAttribute("visibility", arrived ? "visible" : "hidden");
    if (run < 1) { flying = true; pulse.setAttribute("cx", f1(px)); pulse.setAttribute("cy", f1(py)); }
  });
  pulse.setAttribute("visibility", flying ? "visible" : "hidden");
  for (const j of jumpEls) j.el.setAttribute("opacity", j.s.on && disp != null && disp >= j.s.pct - .3 ? 1 : 0);
  $("#head").setAttribute("visibility", have ? "visible" : "hidden");
  if (have) {
    const hx = bp[bp.length - 1][0], hy = cy(disp), ry = cy(rlDisp);
    $("#hdCore").setAttribute("cx", f1(hx)); $("#hdCore").setAttribute("cy", f1(hy)); $("#hdGlow").setAttribute("cx", f1(hx)); $("#hdGlow").setAttribute("cy", f1(hy));
    $("#bsText").setAttribute("x", f1(hx + 13)); $("#bsText").setAttribute("y", f1(hy + 21)); $("#bsNum").textContent = disp.toFixed(1);
    $("#rlText").setAttribute("x", f1(hx + 13)); $("#rlText").setAttribute("y", f1(ry - 8)); $("#rlNum").textContent = rlDisp.toFixed(1) + " %";
  }

  const s = sel >= 0 ? steps[sel].node : null;
  if (s && s.vis) { selRing.setAttribute("visibility", "visible"); selRing.setAttribute("cx", f1(s.sx)); selRing.setAttribute("cy", f1(s.sy)); selRing.setAttribute("r", "9"); }
  else selRing.setAttribute("visibility", "hidden");

  /* the words */
  $("#vBase").textContent = disp == null ? "–" : disp.toFixed(1);
  $("#vRl").textContent = rlDisp == null ? "–" : rlDisp.toFixed(1) + " %";
  $("#vGap").textContent = disp != null && rlDisp != null ? (rlDisp - disp).toFixed(1) : "–";
  const up = bt && bt.prev != null && now - bt.trig < JUMP_MS + 1600 && now - bt.trig >= RISE_MS;
  if (up) $("#vUp").textContent = "+" + (bt.pct - bt.prev).toFixed(1);
  $("#vUp").style.opacity = up ? 1 : 0;
  const state = steps.map(x => x.on ? 1 : 0).join("") + sel;
  if (state !== shown) { shown = state; stepEls.forEach((li, i) => { li.classList.toggle("off", !steps[i].on); li.classList.toggle("sel", i === sel); li.firstChild.setAttribute("aria-expanded", i === sel); }); }
  $("#clock").textContent = clock(T);
  const played = Math.round(T / SPAN * 1000); if (+scrub.value !== played) scrub.value = played;
  scrub.style.setProperty("--p", played / 10 + "%"); scrub.setAttribute("aria-valuetext", clock(T));
  ringHit.setAttribute("aria-valuenow", Math.round(T / SPAN * 100)); ringHit.setAttribute("aria-valuetext", clock(T));
}

/* the record steps as rows, named in the board's plain words; a row opens its detail and moves the picture to that step */
$("#steps").innerHTML = steps.map((s, i) => {
  const n = s.node;
  return `<li class="off"><button data-step="${i}" aria-expanded="false"><span class="gain${i ? "" : " start"}">${i ? "+" + (s.pct - s.prev).toFixed(1) : "start"}</span><span class="ttl">${esc(s.title || s.config)}</span><span class="pct">${s.pct.toFixed(1)} %</span></button>` +
    `<div class="more">${s.what ? `<p>${esc(s.what)}</p>` : ""}${s.caveat ? `<p>${esc(s.caveat)}</p>` : ""}` +
    `<p class="src"><b>${s.right} of ${s.n}</b>, ${esc(s.config)}${s.tokens ? `, ${s.tokens.toLocaleString("en-US")} tokens per problem` : ""}. ` +
    `<span class="who hue" style="--h:${n.h}">${esc(s.who)}</span>, ${clock(n.t)}, ${day(n.t)}, in the cluster ${esc(B[n.b].short)} (${esc(s.id)}).</p></div></li>`;
}).join("");
const stepEls = [...document.querySelectorAll("#steps li")];

const playBtn = $("#play");
function setPlaying(p) { playing = p && !reduce; playBtn.textContent = playing ? "Pause" : T >= SPAN ? "Replay" : "Play"; }
function sync() { for (const list of [steps, rlSteps]) for (const s of list) { const on = s.at <= T; if (on !== s.on) { s.on = on; s.trig = -1e9; } } }  // without a replay, the steps simply follow the time shown
function setT(t) { T = clamp(t, 0, SPAN); if (!playing) setPlaying(false); sync(); }
playBtn.onclick = () => { if (reduce) return; if (!playing && T >= SPAN) { setT(0); disp = rlDisp = null; } setPlaying(!playing); };
if (reduce) playBtn.hidden = true;
const scrub = $("#scrub"), speedBtn = $("#speed");
scrub.addEventListener("input", () => { setPlaying(false); setT(scrub.value / 1000 * SPAN); });  // the slider and the ring move the same board time
speedBtn.onclick = () => {
  speed = SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length];
  speedBtn.textContent = speed + "×"; speedBtn.setAttribute("aria-label", `Replay speed: ${speed} times. Press to change.`);
};
if (reduce) speedBtn.hidden = true;
/* For a page that shows this one in a frame (the talk deck): move the board time and go on playing, set the speed, read the time. */
window.replay = {
  seek(p) { setT(p * SPAN); if (T < SPAN) setPlaying(true); },
  speed(x) { speed = x; speedBtn.textContent = x + "×"; },
  at: () => T / SPAN,
};
const at = ev => { const r = map.getBoundingClientRect(); return [(ev.clientX - r.left) / r.width * 1000, (ev.clientY - r.top) / r.height * VH]; };
function ringT(ev) {  // the board time under the pointer: the nearest point of the ring
  const [x, y] = at(ev); let bestK = 0, bd = 1e9;
  for (let q = 0; q <= 300; q++) { const p = onRing(RT, A0 + (A1 - A0) * q / 300), d = (p[0] - x) ** 2 + (p[1] - y) ** 2; if (d < bd) { bd = d; bestK = q; } }
  return SPAN * bestK / 300;
}
ringHit.addEventListener("pointerdown", ev => { ringHit.setPointerCapture(ev.pointerId); setPlaying(false); setT(ringT(ev)); ev.stopPropagation(); });
ringHit.addEventListener("pointermove", ev => { if (ringHit.hasPointerCapture(ev.pointerId)) setT(ringT(ev)); });
ringHit.addEventListener("click", ev => ev.stopPropagation());
ringHit.addEventListener("keydown", ev => {
  if (ev.key !== "ArrowRight" && ev.key !== "ArrowLeft") return;
  setPlaying(false); setT(T + (ev.key === "ArrowRight" ? 1 : -1) * SPAN / 60); ev.preventDefault(); ev.stopPropagation();
});
map.addEventListener("click", ev => {  // a click on a record, on the line or on the disc, selects that step
  if (ev.target.dataset && ev.target.dataset.step != null) return go(+ev.target.dataset.step);
  const [x, y] = at(ev); let hit = -1, bd = 18;
  steps.forEach((s, i) => { if (s.on && s.node.vis) { const d = Math.hypot(s.node.sx - x, s.node.sy - y); if (d <= bd) { bd = d; hit = i; } } });
  go(hit);
});
map.addEventListener("pointermove", ev => { const r = map.getBoundingClientRect(); leanTo = ((ev.clientX - r.left) / r.width - .5) * 5; });
map.addEventListener("pointerleave", () => { leanTo = 0; });
$("#steps").addEventListener("click", ev => { const b = ev.target.closest("button"); if (b) go(+b.dataset.step === sel ? -1 : +b.dataset.step); });

$("#sentence").innerHTML = `With no training, the Olmo 3 base model went from <b>${first.pct.toFixed(1)}&nbsp;%</b> to <b>${best.pct.toFixed(1)}&nbsp;%</b> on ${esc(C.bench)} in <b>${words[steps.length - 1] || steps.length - 1}</b> steps, against <b>${rlBest.pct.toFixed(1)}&nbsp;%</b> for the RL-trained model.`;
$("#key").innerHTML =
  `<span><svg viewBox="0 0 18 14"><path d="M1 11H8V4H17" fill="none" stroke="var(--blue)" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/><circle cx="8" cy="4" r="2.3" fill="var(--core)" stroke="var(--blue)"/></svg>base, record</span>` +
  `<span><svg viewBox="0 0 18 14"><circle cx="9" cy="7" r="2.7" fill="none" stroke="var(--mute)"/></svg>base, other attempt</span>` +
  `<span><svg viewBox="0 0 18 14"><path d="M1 7H17" fill="none" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="1.5 4" stroke-linecap="round"/></svg>RL, best score</span>` +
  `<span><svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="4.4" fill="var(--mute)"/></svg>result</span>` +
  `<span><svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="3.6" fill="none" stroke="var(--mute)" stroke-width="1.3"/></svg>open work</span>` +
  `<span><svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="2.4" fill="var(--mute)"/></svg>idea or note</span>` +
  `<span><svg viewBox="0 0 16 16"><path d="${MARK}" fill="var(--mute)"/></svg>one person's agents</span>`;
$("#note1").textContent = `Scores are the board's score rows, read ${C.read}. A record step is a score of the untrained base that is strictly above every earlier one, in the order the results were posted; this is the rule of the board's chart (tools/climb.py), and the names of the steps are the board's. The ${tries.length} hollow dots are the other scores of the base posted in this window. RL's line follows the same rule for the RL-Zero-Math model. Its best, ${rlBest.right} of ${rlBest.n}, is "${rlBest.config}" (${rlBest.id}). The line runs over board time, ${hm(0)} to ${clock(SPAN)}, the same time as the ring around the disc.`;
$("#note2").textContent = `The disc is the idea map: each hill is a cluster of board items and each dot one item, placed by a judge model (${R.judge}). Snapshot ${R.snapshot}. Later on the board and not on this map: ${C.later.right} of ${C.later.n} for "${C.later.config}", a model trained by imitation, which is not the untrained base (${C.later.id}, ${C.later.at}).`;

/* ───────── the selected step, the address, the keyboard ───────── */
function go(i) { const h = i >= 0 ? "#step-" + (i + 1) : "#climb"; if (location.hash !== h) { try { location.hash = h; } catch (e) { /* the frame may refuse; the page still works */ } } read(h); }
function read(h) {
  const m = /^#step-(\d+)$/.exec(h || location.hash), i = m ? +m[1] - 1 : -1;
  sel = i >= 0 && i < steps.length ? i : -1;
  if (sel >= 0) { setPlaying(false); setT(steps[sel].at + .002); }
}
addEventListener("hashchange", () => read());
addEventListener("keydown", ev => {
  if (ev.target.closest && ev.target.closest("button, summary, a") && (ev.key === " " || ev.key === "Enter")) return;
  if (ev.target === scrub && ev.key !== "Escape") return;  // on the slider the arrow keys move the time
  if (ev.key === "Escape") go(-1);
  else if (ev.key === " ") { playBtn.click(); ev.preventDefault(); }
  else if (ev.key === "ArrowRight" || ev.key === "PageDown") slide(1);
  else if (ev.key === "ArrowLeft" || ev.key === "PageUp") slide(-1);
  else if (ev.key === "ArrowDown") { go(Math.min(steps.length - 1, sel + 1)); ev.preventDefault(); }  // down and up walk the record steps
  else if (ev.key === "ArrowUp") { go(Math.max(0, sel - 1)); ev.preventDefault(); }
  else if (ev.key === "t") toggleTheme();
});

read(); if (sel < 0) { sync(); setPlaying(playing); }
let prev = performance.now();
function frame(now) {
  const dt = Math.min(.1, (now - prev) / 1000); prev = now;
  if (playing) {
    /* a record step holds the clock: the next step that is due starts when the one before it has finished, and time moves on after that */
    const due = steps.find(s => !s.on && s.at <= T);
    if (due) { if (now - lastTrig > hold()) { due.on = true; due.trig = now; lastTrig = now; } }
    else if (now - lastTrig > hold()) { T = Math.min(SPAN, T + dt * speed * SPAN / PLAY_S); if (T >= SPAN) setPlaying(false); }
    for (const s of rlSteps) if (!s.on && s.at <= T) { s.on = true; s.trig = now; }
  }
  lean += (leanTo - lean) * Math.min(1, dt * 3);
  draw(now, dt);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
})();
</script>
"""


def as_js(value):
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def page(body, index, view=""):
    """One slide: the head, then its body with the data, the list of slides and its place in it written in."""
    slides = [{"href": f"/demo/ali/{slug}", "name": name} for slug, name in SLIDES]
    return (HEAD.replace("__TITLE__", SLIDES[index][1])
            + body.replace("__DATA__", as_js(demo_ali_data.DATA)).replace("__SLIDES__", as_js(slides)).replace("__SLIDE__", str(index)).replace("__VIEW__", view)
            + "</body>\n</html>\n")


PAGES = {"slide1": page(DISC, 0, "map"), "slide2": page(DISC, 1, "tree"), "slide3": page(STEPS, 2)}
