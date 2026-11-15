"""The home page of the team site: one dial that leads to every page.

view.py serves PAGE as the page / of invariant.team (and at /home on monitor.invariant.team and locally); every link
leads to monitor.invariant.team, where the pages are. The picture is a lit glass body with a ring around it, seen from slightly above, and one
bead on the ring per page of the site. The bead at the front is the selected page: the body shows its name and,
where one is counted, its live number. A click on a bead or the arrow keys turn the dial to it (address /#<page>; Up and Down only where the page does not scroll);
a click on the body or the button opens it. The words column beside the picture holds one sentence with the
live MATH-500 scores of the Board (the first and the best untrained-base score and the best RL score among the `scores`
rows of /data, computed as `benches` in view.py does, with the method words taken from the best base row's
configuration; no numbers before the first read), one line that says who the team is with the live number of people,
the button, and a numbered table of contents of the three sections below (01 Results, 02 How we work, 03 Tools and
extras). Each group has a muted hue (TH) used only for small marks, and each page an abstract object (ART: glass planes
and hairlines at the isometric angle in a 120 x 90 box, with one mark in its group's hue). The body shows the selected
page's object above its name, with one slow motion; the ring is tinted by group. Below the dial, each section has its
number, name, sentence, then one row per page: object, name, line, live count, arrow. A bead's name is drawn outside
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
/* The tokens, the light and the type of architecture.py. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34; --on-blue: #fff;
  --pl: .50; --pc: .15; --far: .72;  /* --far: the opacity of a bead and its name at the back of the dial */
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .10); --rim-b: rgba(16, 24, 32, .22); --rim-c: rgba(16, 24, 32, .38);
  --glow: 0; --shadow: 1; --spec: 0;
  --btn: #101820; --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18); --btn-drop: rgba(16, 24, 32, .42);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --pl: .78; --pc: .13; --far: .6;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1;
    --btn: #e9eff3; --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7); --btn-drop: rgba(0, 0, 0, .6);
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
  column-gap: 48px; height: calc(100vh - 56px); min-height: 600px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 22px;
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
.words { grid-column: 1; grid-row: 2 / 4; min-height: 0; overflow: hidden auto; scrollbar-width: none; padding: clamp(32px, 7vh, 64px) 0 0; }
.cap b { font-weight: 500; }
.cap { margin: 0; font-size: clamp(22px, 1.6vw, 28px); line-height: 1.24; font-weight: 320; font-stretch: 102%; letter-spacing: -.012em; text-wrap: balance; }
.who { margin: 16px 0 0; font-size: 14.5px; line-height: 1.45; color: var(--mute); max-width: 36ch; }
/* The three sections, numbered, as the hero's table of contents */
.toc { list-style: none; margin: clamp(24px, 5vh, 40px) 0 0; padding: 0; border-bottom: 1px solid var(--rule); }
.toc a { display: grid; grid-template-columns: 2.4em minmax(0, 1fr); grid-template-areas: "n b" ". em"; row-gap: 1px; align-items: baseline; padding: clamp(8px, 1.5vh, 12px) 0; border-top: 1px solid var(--rule); text-decoration: none; }
.toc .n { grid-area: n; color: var(--t); font-size: 12.5px; font-weight: 600; }
.toc b { grid-area: b; font-weight: 500; font-size: 16px; font-stretch: 104%; transition: color .2s ease; }
.toc em { grid-area: em; font-style: normal; color: var(--mute); font-size: 13px; }
.toc a:hover b { color: var(--t); }
.go {
  display: inline-block; margin: 28px 0 0; padding: 10px 20px; border-radius: 999px; background: var(--btn); color: var(--btn-ink);
  font-weight: 560; font-size: 14.5px; font-stretch: 104%; text-decoration: none;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .08), 0 1px 2px rgba(0, 0, 0, .25); transition: transform .18s ease, opacity .18s ease;
}
.go:hover { transform: translateY(-1px); opacity: .9; }

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
.body { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.1; cursor: pointer; }
.body:focus { outline: none; }
.body:focus-visible { stroke: var(--blue); stroke-width: 3; }
.read .n { font-weight: 360; letter-spacing: -.01em; }
.read .c { fill: var(--mute); font-weight: 480; }
.ring, .ticks { fill: none; stroke: var(--ink); stroke-linecap: round; }
.ring.back { stroke-width: .7; opacity: .3; }
.ring.front { stroke-width: 1.5; opacity: .85; }
.ring.front.thin { stroke-width: .8; opacity: .5; }
.ticks.back { stroke-width: .6; opacity: .26; }
.ticks.front { stroke-width: .8; opacity: .4; }
#in-f, #in-b { display: none; }
.mark { fill: none; stroke: var(--t); stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }
.bead { cursor: pointer; }
.bead:focus { outline: none; }
.bead circle.b { fill: url(#body) var(--sheet); stroke: var(--t); stroke-width: 1.5; }
.bead.on circle.b { stroke: var(--t); stroke-width: 2; }
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

/* Themes: one hue per group of pages (TH in the script), muted, used only for small marks. The dial takes the hue of
   the selected page's group and eases to the next one. */
@property --th { syntax: "<number>"; inherits: true; initial-value: 255; }
.th, #svg { --t: oklch(var(--pl) calc(var(--pc) * .78) var(--th)); }
#svg { --tg: oklch(var(--pl) .06 var(--th)); transition: --th .9s ease; }
.garc { fill: none; stroke: var(--t); stroke-linecap: round; pointer-events: none; }
.garc.front { stroke-width: 1.6; opacity: .9; }
.garc.back { stroke-width: 1.1; opacity: .35; }
#art { pointer-events: none; }
@keyframes artin { from { opacity: 0; transform: translateY(6px); } }
#art.swap { animation: artin .6s cubic-bezier(.2, .7, .2, 1) both; transform-box: fill-box; transform-origin: center; }

/* The objects: glass planes lit from the upper left, hairlines, one small mark in the group's hue */
.gb { fill: url(#gg) var(--glass); stroke: var(--ink); stroke-width: .8; stroke-opacity: .45; stroke-linejoin: round; }
.gb.f1 { fill: var(--glass-hi); } .gb.f2 { fill: var(--glass); } .gb.f3 { fill: var(--glass-lo); }
.gb.thin { fill-opacity: .35; }
.gb.acc { stroke: var(--t); stroke-width: 1.4; stroke-opacity: 1; }
.gl { fill: none; stroke: var(--ink); stroke-width: .8; stroke-opacity: .45; stroke-linecap: round; stroke-linejoin: round; }
.gl.gd { stroke-dasharray: 2 3; stroke-opacity: .28; }
.gi { fill: var(--ink); opacity: .3; }
.gw0 { fill: none; stroke: var(--ink); stroke-width: .7; stroke-opacity: .45; }
.ga { fill: var(--t); }
.gs { fill: none; stroke: var(--t); stroke-width: 1.4; stroke-linecap: round; stroke-linejoin: round; }
.gf { fill: var(--t); opacity: .14; }
.an { transform-box: fill-box; }
@keyframes g-float { 50% { transform: translateY(-3px); } }
@keyframes g-ping { 0% { transform: scale(1); opacity: .8; } 70%, 100% { transform: scale(3); opacity: 0; } }
@keyframes g-glow { 50% { opacity: .35; } }
@keyframes g-rise { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(36px); } }
#art .float { animation: g-float 7s ease-in-out infinite; }
#art .ping { transform-origin: center; animation: g-ping 3.6s ease-out infinite; }
#art .pulse { animation: g-glow 5s ease-in-out infinite; }
#art .rise { animation: g-rise 8s ease-in-out infinite; }
@media (prefers-color-scheme: dark) { .gb { fill-opacity: .6; } .gb.f1 { stroke: #fff; stroke-opacity: .35; } }

/* The sections below the dial: one per group, numbered, an object for the group and a row for each page */
.sec { border-top: 1px solid var(--rule); }
.sec-in { max-width: 1840px; margin: 0 auto; padding: clamp(56px, 9vh, 96px) 40px clamp(48px, 8vh, 80px); display: grid; grid-template-columns: minmax(320px, 27vw) minmax(0, 1fr); column-gap: 48px; }
.sec-n { margin: 0 0 14px; font-size: 13px; font-weight: 600; color: var(--t); }
.sec-head h2 { margin: 0; font-size: clamp(30px, 2.3vw, 40px); line-height: 1.06; font-weight: 300; letter-spacing: -.02em; }
.sec-head p { margin: 14px 0 0; text-wrap: pretty; color: var(--mute); font-size: 15.5px; line-height: 1.5; max-width: 30ch; }
.sec-head { position: sticky; top: 32px; align-self: start; }
.rows { list-style: none; margin: 0; padding: 0; border-bottom: 1px solid var(--rule); align-self: start; }
.row {
  display: grid; grid-template-columns: 96px minmax(9em, 15em) minmax(0, 1fr) auto 24px; grid-template-areas: "art name line ct go";
  align-items: center; column-gap: 28px; padding: 12px 8px 12px 0; border-top: 1px solid var(--rule); text-decoration: none;
  transition: background .3s ease;
}
.row svg.mini { grid-area: art; width: 96px; height: 72px; display: block; overflow: visible; }
.row b { grid-area: name; font-size: 18px; font-weight: 500; font-stretch: 104%; letter-spacing: -.004em; }
.row span { grid-area: line; color: var(--mute); font-size: 15px; line-height: 1.4; }
.row em { grid-area: ct; font-style: normal; color: var(--mute); font-size: 13.5px; white-space: nowrap; }
.row i { grid-area: go; font-style: normal; color: var(--faint); justify-self: end; transition: transform .3s cubic-bezier(.3, 0, .2, 1), color .3s ease; }
.row:hover { background: linear-gradient(90deg, transparent, color-mix(in oklab, var(--t) 7%, transparent) 40%, transparent); }
.row:hover i { transform: translateX(4px); color: var(--t); }
.row:focus-visible { outline-offset: -2px; }

@media (max-width: 900px) {
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 6px 16px 36px; }
  .top { gap: 0 13px; padding-bottom: 2px; flex-wrap: wrap; }
  .top a { display: inline-flex; align-items: center; min-height: 40px; }  /* a finger's height */
  .name { font-stretch: 112%; margin-right: 0; }
  .words { display: contents; }  /* on a phone: the sentence, the button, the pages, then the picture and what is arriving */
  .cap { order: 1; margin-top: 20px; font-size: 22px; max-width: none; }
  .who { order: 1; }
  .go { order: 2; align-self: flex-start; margin-top: 18px; }
  .status { display: none; }
  .toc { order: 3; }
  .toc a { padding: 12px 0; }
  .sec-in { display: block; padding: 52px 16px 36px; }
  .sec-head { margin-bottom: 22px; }
  .sec-head h2 { font-size: 30px; }
  .sec-head { position: static; }
  .row { grid-template-columns: 72px minmax(0, 1fr); grid-template-areas: "art name" "art line" "art ct"; column-gap: 16px; row-gap: 2px; padding: 14px 0; }
  .row svg.mini { width: 72px; height: 54px; }
  .row b { font-size: 17px; }
  .row span { font-size: 14px; }
  .row i { display: none; }
  .stage { order: 4; margin-top: 22px; padding: 0; display: block; }
  svg { height: auto; }
  .foot { order: 5; display: block; margin-top: 2px; min-height: 39px; }
  .said { white-space: normal; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }  /* two lines */
  .key { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .status.read::before { animation: none; }
  .go, .said, .toc b, .row, .row i, #svg { transition: none; }
  .an, #art.swap { animation: none !important; }
}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><linearGradient id="gg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="var(--glass-hi)"/><stop offset=".55" stop-color="var(--glass)"/><stop offset="1" stop-color="var(--glass-lo)"/></linearGradient></defs></svg>
<div class="page" id="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="https://monitor.invariant.team/">Board</a>
    <a href="https://monitor.invariant.team/proof">Proof</a>
    <a href="https://monitor.invariant.team/findings">Findings</a>
    <span class="status" id="status">Reading the board</span>
  </header>
  <div class="words">
    <p class="cap" id="cap">With no training, how far does the Olmo 3 base model get on MATH-500, against the RL-trained model?</p>
    <p class="who" id="who">Several people and their coding agents, at the SF AI Research Hackathon.</p>
    <a class="go" id="go" href="https://monitor.invariant.team/findings">Read the findings</a>
    <ol class="toc" id="index" aria-label="Sections of this page"></ol>
  </div>
  <div class="stage"><svg id="svg" aria-hidden="true"></svg></div>
  <div class="foot"><span class="said hue" id="said"></span><span class="key">Each pulse is one post arriving on the board. ← → turn the dial.</span></div>
</div>
<main id="sections"></main>
<script>
const $ = id => document.getElementById(id);
const COUNTS = __COUNTS__;  // written in by view.py: the numbers of finding pages, proof pages, papers and lab pictures it serves
const HUES = [325, 150, 65, 195, 105, 45, 175, 350];  // a person's color, the same as on every other page
/* Every page of the site, in the order of the dial and of the list. g is its group in the list (GROUPS holds the
   labels): 0 the results, 1 how the team works, 2 the rest. line is the list's few words; count(m) is the number the
   body shows under the name, from the counts above or from the newest read of /data, and absent where nothing is
   counted (on a phone the body is 103 px wide, so the two long counts are shorter there). out marks a page that is
   not on this site. */
const GROUPS = ["Results", "How we work", "Tools and extras"];
const PAGES = [
  { id: "findings", g: 0, name: "Findings", href: "/findings", line: "One page for each finding", count: () => COUNTS.findings + " pages" },
  { id: "papers", g: 0, name: "Papers", href: "/papers", line: "The paper loop and what it wrote", count: () => COUNTS.papers + " papers" },
  { id: "talk", g: 0, name: "Talk", href: "/demo", line: "The talk, as slides" },
  { id: "board", g: 1, name: "Board", href: "/", line: "Ideas, open work and results", count: m => m ? `${m.open} open ${narrow.matches ? "" : "work "}items` : "" },
  { id: "proof", g: 1, name: "Proof", href: "/proof", line: "Tests of the team's own method", count: () => COUNTS.proof + (COUNTS.proof === 1 ? " page" : " pages") },
  { id: "values", g: 1, name: "Values", href: "/values", line: "The six values the team works by" },
  { id: "team", g: 1, name: "Team", href: "/team", line: "Who we are" },
  { id: "lab", g: 2, name: "AI Psychosis maxxing", short: "Maxxing", href: "/lab/", line: "3D pictures of our own work, because of course", count: () => COUNTS.lab + " pictures" },
  { id: "exa", g: 2, name: "Exa", href: "/exa", line: "How the agents used web search" },
  { id: "pastdev", g: 2, name: "past.dev", href: "/pastdev", line: "How the agents used shared memory" },
  { id: "gpu", g: 2, name: "GPU prices", href: "https://gpu.invariant.team", line: "Forecasts of GPU rental prices", out: true },
  { id: "psychosis", g: 2, name: "AI Psychosis detox", short: "Detox", href: "/psychosis", line: "The cure for the maxxing: log off and breathe, as a game" },
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

/* Themes and pictures. Each group of pages has a hue (TH) and each page an abstract object in a 120 x 90 box: glass
   planes and hairlines in the site's light, seen from above at the isometric angle, with one small mark in the group's
   hue. The objects hold still in the list; in the dial's body each has one slow motion. */
const TH = [255, 172, 74];
const pt2 = p => f(p[0]) + " " + f(p[1]);
const Q = ps => "M" + ps.map(pt2).join("L") + "Z", Ln = ps => "M" + ps.map(pt2).join("L");
const iso = (x, y, z, s = 1, cx = 60, cy = 56) => [cx + (x - y) * .866 * s, cy + ((x + y) * .5 - z) * s];
/* A slab: half sizes w and d, from height z to z + t, centred at (x0, y0); its top and its two near sides. */
const slab = (w, d, z, t, x0 = 0, y0 = 0, s = 1, cx, cy, top = "gb f1") => {
  const P = (x, y, h) => iso(x0 + x, y0 + y, h, s, cx, cy);
  return `<path class="gb f3" d="${Q([P(w, -d, z + t), P(w, d, z + t), P(w, d, z), P(w, -d, z)])}"/>` +
    `<path class="gb f2" d="${Q([P(-w, d, z + t), P(w, d, z + t), P(w, d, z), P(-w, d, z)])}"/>` +
    `<path class="${top}" d="${Q([P(-w, -d, z + t), P(w, -d, z + t), P(w, d, z + t), P(-w, d, z + t)])}"/>`;
};
const prismHex = (r, h, s = 1, cx, cy) => {  // a hexagonal prism standing on the plane, its near faces lit by their angle
  const v = [0, 1, 2, 3, 4, 5].map(k => [r * Math.cos((k * 60 + 30) * RAD), r * Math.sin((k * 60 + 30) * RAD)]);
  let out = "";
  v.forEach((a, k) => {
    const b = v[(k + 1) % 6], m = (k * 60 + 60) * RAD, n = Math.cos(m - Math.PI / 4);
    if (n <= .05) return;
    const cls = Math.sin(m) > Math.cos(m) + .3 ? "f1" : Math.cos(m) > Math.sin(m) + .3 ? "f3" : "f2";
    out += `<path class="gb ${cls}" d="${Q([iso(a[0], a[1], h, s, cx, cy), iso(b[0], b[1], h, s, cx, cy), iso(b[0], b[1], 0, s, cx, cy), iso(a[0], a[1], 0, s, cx, cy)])}"/>`;
  });
  const top = v.map(a => iso(a[0], a[1], h, s, cx, cy)), c = iso(0, 0, h, s, cx, cy);
  return out + `<path class="gb f1" d="${Q(top)}"/><circle class="ga an float" cx="${f(c[0])}" cy="${f(c[1])}" r="2.4"/>`;
};
const ART = {
  findings: slab(28, 28, 0, 3) + slab(22, 22, 13, 3) + slab(16, 16, 26, 3, 0, 0, 1, 60, 56, "gb f1") +
    `<circle class="ga an float" cx="${f(iso(0, 0, 33)[0])}" cy="${f(iso(0, 0, 33)[1])}" r="2.6"/>`,
  papers: (() => { const sh = (y, x0, x1, cls) => `<path class="gb ${cls}" d="${Q([iso(x0, y, 46), iso(x1, y, 46), iso(x1, y, 0), iso(x0, y, 0)])}"/>`;
    return `<path class="gi" opacity=".14" d="${Q([iso(-30, -10, 0), iso(30, -10, 0), iso(30, 14, 0), iso(-30, 14, 0)])}"/>` + sh(-8, -26, 22, "f2") + sh(6, -22, 26, "f1") +
      `<path class="gs" stroke-width="1.4" d="${Ln([iso(-15, 6, 38), iso(4, 6, 38)])}"/>` + [31, 26, 21, 16, 11].map(z => `<path class="gl" d="${Ln([iso(-15, 6, z), iso(z === 11 ? 6 : 17, 6, z)])}"/>`).join(""); })(),
  talk: slab(10, 7, 0, 1.5) + slab(1.5, 1.5, 1.5, 10.5) + slab(27, 1.2, 12, 30) +
    [34, 28, 22].map((z, i) => `<path class="gl" d="${Ln([iso(-20, 1.2, z), iso(i === 2 ? 2 : 14, 1.2, z)])}"/>`).join("") +
    `<circle class="ga an float" cx="${f(iso(18, 1.2, 22)[0])}" cy="${f(iso(18, 1.2, 22)[1])}" r="2.4"/>`,
  board: slab(32, 22, 0, 3) + [[-20, -12], [-20, -2], [-20, 8], [0, -12], [0, -2], [20, -12], [20, -2, 1]].sort((a, b) => a[0] + a[1] - b[0] - b[1])
    .map(([x, y, on]) => slab(7, 3.5, 3, 1.2, x, y, 1, 60, 56, on ? "ga" : "gb f1")).join(""),
  proof: slab(22, 30, 0, 1.5) + [-22, -16, -10, -4, 2].map(y => `<path class="gl" d="${Ln([iso(-15, y, 1.5), iso(y === 2 ? 2 : 13, y, 1.5)])}"/>`).join("") +
    `<path class="ga" d="${Q([iso(10, 15, 1.5), iso(17, 15, 1.5), iso(17, 22, 1.5), iso(10, 22, 1.5)])}"/>`,
  values: prismHex(24, 10),
  team: slab(32, 20, 0, 2) + slab(5, 5, 2, 14, -16, -4) + slab(5, 5, 2, 20, 14, -6) + slab(5, 5, 2, 26, 0, 8, 1, 60, 56, "ga"),
  lab: (() => { const s = 21, V = (x, y, z) => iso(x * s, y * s, (z + 1) * s, 1, 60, 66), E = [[[-1, -1, -1], [1, -1, -1]], [[-1, -1, -1], [-1, 1, -1]], [[-1, -1, -1], [-1, -1, 1]]];
    const back = E.map(([a, b]) => `<path class="gl gd" d="${Ln([V(...a), V(...b)])}"/>`).join(""), c = iso(0, 0, s, 1, 60, 66);
    return back + `<circle class="ga" opacity=".9" cx="${f(c[0])}" cy="${f(c[1])}" r="7"/><circle cx="${f(c[0] - 2.3)}" cy="${f(c[1] - 2.3)}" r="2.2" fill="var(--glass-hi)" opacity=".7"/>` +
      `<path class="gb f1 thin" d="${Q([V(-1, -1, 1), V(1, -1, 1), V(1, 1, 1), V(-1, 1, 1)])}"/><path class="gb f3 thin" d="${Q([V(1, -1, 1), V(1, 1, 1), V(1, 1, -1), V(1, -1, -1)])}"/>` +
      `<path class="gb f2 thin" d="${Q([V(-1, 1, 1), V(1, 1, 1), V(1, 1, -1), V(-1, 1, -1)])}"/>`; })(),
  exa: (() => { const ring = Array.from({ length: 24 }, (_, k) => { const t = k / 24 * 2 * Math.PI; return iso(0, 20 * Math.cos(t), 24 + 20 * Math.sin(t)); }), d = iso(30, 0, 22);
    return `<path class="gl" d="${Ln([iso(-34, -8, 30), iso(0, -8, 30)])}"/><path class="gl" d="${Ln([iso(-34, 8, 14), iso(0, 8, 14)])}"/><path class="gb f1 thin" d="${Q(ring)}"/>` +
      `<path class="gs" stroke-width="1.1" d="${Ln([iso(0, -12, 22), d])}M${pt2(iso(0, 12, 22))}L${pt2(d)}"/><circle class="ga an pulse" cx="${f(d[0])}" cy="${f(d[1])}" r="2.6"/>`; })(),
  pastdev: `<path class="gl gd" d="M60 18V84"/>` + [68, 50, 32].map((y, i) => `<ellipse class="gb f3" cx="60" cy="${y + 3}" rx="28" ry="16"/><ellipse class="gb ${["f2", "f1", "f1"][i]}" cx="60" cy="${y}" rx="28" ry="16"/>` +
    `<circle class="gi" cx="${50 + i * 8}" cy="${y - 3}" r="1.5"/><circle class="gi" cx="${68 - i * 4}" cy="${y + 4}" r="1.5"/>`).join("") + `<circle class="ga an rise" cx="60" cy="32" r="2.6"/>`,
  gpu: (() => { const y = 1.2, H = [12, 14, 13, 20, 18, 22].map((z, i) => iso(-28 + i * 5.6, y, z)), F = [0, 9, 18, 27].map((x, i) => [x, 22 + i * 3]);
    const band = [...F.map(([x, z]) => iso(x, y, z + x / 4)), ...F.slice().reverse().map(([x, z]) => iso(x, y, z - x / 4))], end = iso(27, y, 31);
    return slab(14, 8, 0, 1.5) + slab(32, 1.2, 1.5, 38) + `<path class="gl gd" d="${Ln([iso(0, y, 6), iso(0, y, 38)])}"/><path class="gf" d="${Q(band)}"/>` +
      `<path class="gl" stroke-opacity=".8" stroke-width="1.1" d="${Ln(H)}"/><path class="gs" stroke-width="1.1" stroke-dasharray="3 3" d="${Ln(F.map(([x, z]) => iso(x, y, z)))}"/>` +
      `<circle class="ga an pulse" cx="${f(end[0])}" cy="${f(end[1])}" r="2.4"/>`; })(),
  psychosis: `<ellipse class="gl" stroke-opacity=".22" cx="60" cy="64" rx="40" ry="23"/><ellipse class="gl" stroke-opacity=".45" cx="60" cy="64" rx="28" ry="16"/>` +
    `<ellipse class="gi" opacity=".22" cx="60" cy="64" rx="9" ry="5"/><g class="an float"><circle class="gb" cx="60" cy="32" r="10"/><circle class="ga" cx="60" cy="32" r="2.2"/></g>`,
};
const art = id => ART[id];

/* Geometry: the ring lies flat around the body and is seen from above (pitch). R is the ring of beads, the ticks
   run from rt to rt + 8 (every sixth to rt + 15) inside it on a fine inner ring, rb is the body. fs is the size of a name at the front and min the
   smallest a name is drawn (on a phone 26 of 720 units, which is 12 px on a 375 px screen).
   The picture is wider than the ring by the longest name on each side. Names with q under far are not drawn. */
function geo() {
  return narrow.matches
    ? { w: 720, h: 548, cx: 360, cy: 262, R: 272, rt: 214, rb: 108, D: 1700, pitch: 36, bead: 12, fs: 27, min: 26, fn: 28, fc: 21, far: .86, art: 1.3, at: .76, ny: .6 }
    : { w: 1060, h: 660, cx: 530, cy: 290, R: 400, rt: 334, rb: 150, D: 2300, pitch: 36, bead: 8, fs: 17, min: 0, fn: 29, fc: 14.5, far: 0, art: 1.55, at: .8, ny: .5 };
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
    `<radialGradient id="atmo">${stop(.48, "var(--tg)", .15)}${stop(.68, "var(--tg)", .045)}${stop(1, "var(--tg)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.3, "var(--ink)", .14)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    "</defs>" +
    `<circle class="atmo" cx="${G.cx}" cy="${G.cy}" r="${G.rb * 2.1}" fill="url(#atmo)"/>` +
    `<ellipse class="shade" cx="${G.cx}" cy="${G.cy + G.rb * 1.04}" rx="${G.rb * .9}" ry="${G.rb * .16}" fill="url(#shade)"/>` +
    `<g id="back"><path class="ring back" id="ring-b"/><path class="ring back" id="in-b"/><path class="ticks back" id="ticks-b"/>${GROUPS.map((_, g) => `<path class="garc back th" id="arc-b${g}" style="--th:${TH[g]}"/>`).join("")}</g>` +
    `<circle class="body" id="body-c" cx="${G.cx}" cy="${G.cy}" r="${G.rb}" tabindex="-1" role="link"/>` +
    `<ellipse class="spec" cx="${G.cx - G.rb * .34}" cy="${G.cy - G.rb * .44}" rx="${G.rb * .44}" ry="${G.rb * .26}" transform="rotate(-32 ${G.cx - G.rb * .34} ${G.cy - G.rb * .44})" fill="url(#spec)"/>` +
    `<g id="art"></g>` +
    `<g class="read"><text class="n" id="read-n" x="${G.cx}" font-size="${G.fn}"></text><text class="c" id="read-c" x="${G.cx}" y="${G.cy + G.fn * .92}" font-size="${G.fc}"></text></g>` +
    `<g id="front"><path class="ring front" id="ring-f"/><path class="ring front thin" id="in-f"/><path class="ticks front" id="ticks-f"/>${GROUPS.map((_, g) => `<path class="garc front th" id="arc-f${g}" style="--th:${TH[g]}"/>`).join("")}<path class="mark" id="mark"/></g>` +
    `<g id="fx"></g>`;
  PAGES.forEach((p, k) => {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttribute("class", "bead"); g.setAttribute("tabindex", "-1"); g.setAttribute("role", "button");  // a click or a script can focus it; Tab goes through the list, which holds the same pages
    g.setAttribute("aria-label", "Turn the dial to " + p.name); g.dataset.k = k; g.style.setProperty("--i", k); g.style.setProperty("--th", TH[p.g]); g.classList.add("th");
    g.innerHTML = `<circle class="pad"/><circle class="b"/><text>${esc(narrow.matches && p.short ? p.short : p.name)}</text>`;  // a phone has room only for the short name
    p.el = g; p.front = null;
  });
  $("index").innerHTML = GROUPS.map((name, g) => `<li class="th" style="--th:${TH[g]}"><a href="#${SEC[g][0]}"><span class="n">0${g + 1}</span><b>${name}</b>` +
    `<em>${PAGES.filter(p => p.g === g).map(p => esc(p.short || p.name)).join(" \u00b7 ")}</em></a></li>`).join("");
  fit();
  readout();
}

/* The body's two lines, the button and the list's marker follow the selection. */
function readout() {
  const p = PAGES[S.sel], c = p.count ? p.count(S.m) : "", A = $("art"), sc = G.art;
  if (A.dataset.id !== p.id) {  // the selected page's picture fills the upper body, and comes in once
    A.dataset.id = p.id;
    A.innerHTML = `<g transform="translate(${f(G.cx - 60 * sc)} ${f(G.cy - G.rb * G.at)}) scale(${sc})">${ART[p.id]}</g>`;
    const g0 = A.firstChild, bb = g0.getBBox();  // centre the drawing itself, not its box
    g0.setAttribute("transform", `translate(${f(G.cx - (bb.x + bb.width / 2) * sc)} ${f(G.cy - G.rb * G.at)}) scale(${sc})`);
    A.classList.remove("swap"); void A.getBBox(); A.classList.add("swap");
  }
  $("svg").style.setProperty("--th", TH[p.g]);
  const rn = $("read-n"), wmax = 2 * G.rb * Math.sqrt(1 - G.ny * G.ny) * .84;  // a long name shrinks to the body's width
  rn.textContent = p.name; rn.setAttribute("font-size", G.fn); rn.setAttribute("y", f(G.cy + G.rb * (c ? G.ny : G.ny + .08)));
  const wn = rn.getComputedTextLength(); if (wn > wmax) rn.setAttribute("font-size", f(G.fn * wmax / wn));
  $("read-c").textContent = c; $("read-c").setAttribute("y", f(G.cy + G.rb * G.ny + G.fn * .8));
  document.querySelectorAll(".row").forEach(t => { const q = PAGES[t.dataset.k]; t.querySelector("em").textContent = q.count ? q.count(S.m) : ""; });
  $("body-c").setAttribute("aria-label", "Open " + p.name);
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
  GROUPS.forEach((_, g) => {  // each group's stretch of the ring, in its hue, split where it passes behind
    const ks = PAGES.map((p, k) => p.g === g ? k : -1).filter(k => k >= 0), a0 = beadAt(ks[0]) - STEP * .42, a1 = beadAt(ks[ks.length - 1]) + STEP * .42;
    let df = "", db = "", was = null;
    for (let a = a0; a <= a1 + .01; a += 3) {
      const p = onRing(G.R, Math.min(a, a1)), fr = Math.sin((a - y) * RAD) >= 0, s2 = f(p[0]) + " " + f(p[1]);
      if (fr) df += (was === true ? "L" : "M") + s2; else db += (was === false ? "L" : "M") + s2;
      was = fr;
    }
    $("arc-f" + g).setAttribute("d", df); $("arc-b" + g).setAttribute("d", db);
  });
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
  const t = m.plain[it.id]?.title;  // only a plain title; a raw post is named by who and when
  el.innerHTML = `<b>${esc(it.who)}</b> posted ${live ? '<span class="now">now</span>' : ago(it.at_ns)}${t ? ": " + esc(t) : ""}`;
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
  const who = `${m.people.length} people and their coding agents, at the SF AI Research Hackathon.`;
  if (!isFinite(m.base)) { $("who").textContent = who; return; }
  const n = (m.how.match(/vote over (\d+)/) || [])[1];
  const how = [/\bcue\b/.test(m.how) && "a prompt cue", n && `a majority vote over ${n} samples`].filter(Boolean);
  $("cap").innerHTML = `With no training, the Olmo 3 base model reaches <b>${f(m.base)}\u00a0%</b> on MATH-500.` + (isFinite(m.rl) ? ` The RL-trained model scores <b>${f(m.rl)}\u00a0%</b>.` : "");
  $("who").textContent = (m.start < m.base ? `Up from ${f(m.start)}\u00a0%` + (how.length ? `, with ${how.join(" and ")}. ` : ". ") : "") + who;
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

/* The sections below the dial, one per group: its number, name, sentence and object, then a row for each page. */
const SEC = [
  ["s-results", "Each finding on its own page, the papers written from them, and the talk."],
  ["s-how", "One board, one set of rules, many agents working in parallel."],
  ["s-also", "The tools the agents used, measured, and two pages made for fun."],
];
$("sections").innerHTML = GROUPS.map((name, g) => `<section class="sec th" id="${SEC[g][0]}" style="--th:${TH[g]}" aria-labelledby="${SEC[g][0]}-h"><div class="sec-in">` +
  `<header class="sec-head"><p class="sec-n">0${g + 1}</p><h2 id="${SEC[g][0]}-h">${name}</h2><p>${SEC[g][1]}</p>` +
  `</header><ol class="rows">` +
  PAGES.map((p, k) => p.g !== g ? "" : `<li><a class="row" href="${p.href}" data-k="${k}"><svg class="mini" viewBox="0 0 120 90" aria-hidden="true">${art(p.id)}</svg>` +
    `<b>${esc(p.name)}${p.out ? " \u2197" : ""}</b><span>${esc(p.line)}</span><em></em><i aria-hidden="true">\u2192</i></a></li>`).join("") + "</ol></div></section>").join("");
if (still.matches) document.querySelectorAll("svg").forEach(v => v.pauseAnimations && v.pauseAnimations());

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
addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey || scrollY > innerHeight / 2) return;  // the dial is off screen: the keys are the browser's
  const d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
  if (d) {
    const upDown = e.key === "ArrowDown" || e.key === "ArrowUp";
    if (upDown && document.documentElement.scrollHeight > innerHeight) return;  // the page scrolls: Up and Down are the browser's
    e.preventDefault(); select(S.sel + d, true);
  }
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
