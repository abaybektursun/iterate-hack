"""The home page of the team site: one dial that leads to every page.

view.py serves PAGE as the page / of invariant.team (and at /home on monitor.invariant.team and locally); every link
leads to monitor.invariant.team, where the pages are. The picture is a lit glass body with a ring around it, seen from slightly above, and one
bead on the ring per page of the site. The bead at the front is the selected page: the body shows its name and,
where one is counted, its live number. A click on a bead or the arrow keys turn the dial to it (address /#<page>; Up and Down only where the page does not scroll);
a click on the body or the button opens it. The words column beside the picture holds one sentence with the
live MATH-500 scores of the Board (the first and the best untrained-base score and the best RL score among the `scores`
rows of /data, computed as `benches` in view.py does, with the method words taken from the best base row's
configuration; no numbers before the first read), one line that says who the team is with the live number of people,
the button, and the same pages as links in three labelled groups (Results, How we work, Also), so that the links alone
are enough to get anywhere. Each group has a theme: a hue (TH) at the lightness and chroma of a person's color, and each
page a small lit picture (ART, a 120 x 90 SVG with one slow motion). The body shows the selected page's picture above its
name, the ring is tinted by group, and the glow and the index mark take the selected group's hue. Below the dial, three
sections, one per group in its theme, hold one tile per page: picture, name, line and live count. A bead's name is drawn outside
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
.words { grid-column: 1; grid-row: 2 / 4; min-height: 0; overflow: hidden auto; scrollbar-width: none; padding: clamp(12px, 12vh - 74px, 52px) 0 0; }
.cap { margin: 0; font-size: clamp(21px, 1.75vw, 30px); line-height: 1.22; font-weight: 300; font-stretch: 102%; letter-spacing: -.012em; text-wrap: balance; }
.who { margin: clamp(6px, 1.2vh, 12px) 0 0; font-size: 13px; line-height: 1.35; color: var(--mute); }
/* The pages in three groups, each in its theme */
.groups { margin: clamp(12px, 6vh - 24px, 30px) 0 0; }
.grp { padding: clamp(8px, 1.6vh, 13px) 0; border-top: 1px solid var(--rule); }
.grp:last-child { border-bottom: 1px solid var(--rule); }
.glab { margin: 0 0 3px; font-size: 12.5px; font-weight: 600; color: var(--mute); display: flex; align-items: center; gap: 8px; }
.glab i { width: 14px; height: 3px; border-radius: 2px; background: var(--t); }
.glinks { margin: 0; display: flex; flex-wrap: wrap; gap: 0 18px; }
.glinks a { text-decoration: none; font-weight: 560; font-size: 15.5px; font-stretch: 106%; padding: 3px 0 2px; border-bottom: 2px solid transparent; transition: border-color .2s ease; }
.glinks a:hover { border-bottom-color: color-mix(in srgb, var(--t) 45%, transparent); }
.glinks a.on { border-bottom-color: var(--t); }
.down { display: inline-block; margin: clamp(10px, 2.4vh, 20px) 0 0; font-size: 14px; font-weight: 560; color: var(--ink); text-decoration: none; }
.down:hover { color: var(--t, var(--ink)); text-decoration: underline; text-underline-offset: 3px; }
.glab a { color: inherit; text-decoration: none; }
.glab a:hover { color: var(--ink); }
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
.read .n { font-weight: 360; letter-spacing: -.01em; }
.read .c { fill: var(--mute); font-weight: 480; }
.ring, .ticks { fill: none; stroke: var(--ink); stroke-linecap: round; }
.ring.back { stroke-width: .7; opacity: .3; }
.ring.front { stroke-width: 1.5; opacity: .85; }
.ring.front.thin { stroke-width: .8; opacity: .5; }
.ticks.back { stroke-width: .6; opacity: .26; }
.ticks.front { stroke-width: 1.1; opacity: .62; }
.mark { fill: none; stroke: var(--t); stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }
.bead { cursor: pointer; }
.bead:focus { outline: none; }
.bead circle.b { fill: url(#body) var(--sheet); stroke: var(--t); stroke-width: 1.5; }
.bead.on circle.b { stroke: var(--t); stroke-width: 2.8; }
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

/* Themes: one hue per group of pages (TH in the script), at the lightness and chroma of a person's color. The dial
   takes the hue of the selected page's group and eases to the next one. */
@property --th { syntax: "<number>"; inherits: true; initial-value: 255; }
.th, #svg { --t: oklch(var(--pl) var(--pc) var(--th)); }
#svg { --tg: oklch(var(--pl) .08 var(--th)); }
#svg { transition: --th .9s ease; }
.garc { fill: none; stroke: var(--t); stroke-linecap: round; pointer-events: none; }
.garc.front { stroke-width: 2.8; opacity: 1; }
.garc.back { stroke-width: 1.3; opacity: .4; }
#art { pointer-events: none; }
@keyframes artin { from { opacity: 0; transform: translateY(8px) scale(.96); } }
#art.swap { animation: artin .55s cubic-bezier(.2, .7, .2, 1) both; transform-box: fill-box; transform-origin: center; }

/* The pictures: glass bodies lit from the upper left, fine lines, the group's hue as the one accent */
.gb { fill: url(#gg) var(--glass); stroke: var(--ink); stroke-width: 1; stroke-opacity: .5; stroke-linejoin: round; }
.gb.f1 { fill: var(--glass-hi); } .gb.f2 { fill: var(--glass); } .gb.f3 { fill: var(--glass-lo); }
.gl { fill: none; stroke: var(--ink); stroke-width: .9; stroke-opacity: .42; stroke-linecap: round; stroke-linejoin: round; }
.gi { fill: var(--ink); opacity: .24; }
.ga { fill: var(--t); }
.gs { fill: none; stroke: var(--t); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.gf { fill: var(--t); opacity: .2; }
.gw { fill: var(--glass); stroke: var(--t); stroke-width: 1.6; }
.gp { fill: oklch(var(--pl) var(--pc) var(--h)); }
.gpr { fill: none; stroke: oklch(var(--pl) var(--pc) var(--h)); stroke-width: 1.6; }
.gfloor { fill: color-mix(in oklab, var(--t) calc(var(--glow) * 100%), var(--ink)); opacity: calc(.07 + var(--glow) * .12); }
.an { transform-box: fill-box; }
@keyframes g-grow { 0%, 100% { transform: scaleY(.8); } 50% { transform: scaleY(1); } }
@keyframes g-float { 50% { transform: translateY(-2.5px); } }
@keyframes g-ping { 0% { transform: scale(1); opacity: .9; } 70%, 100% { transform: scale(2.7); opacity: 0; } }
@keyframes g-draw { 0% { stroke-dashoffset: 1; } 35%, 82% { stroke-dashoffset: 0; opacity: 1; } 100% { stroke-dashoffset: 0; opacity: 0; } }
@keyframes g-breathe { 0%, 100% { transform: scale(.82); } 50% { transform: scale(1.05); } }
@keyframes g-sweep { 0% { transform: scaleX(0); } 40%, 85% { transform: scaleX(1); opacity: .5; } 100% { transform: scaleX(1); opacity: 0; } }
@keyframes g-glow { 50% { opacity: .35; } }
@keyframes g-blink { 50% { opacity: .3; } }
.grow { transform-origin: 50% 100%; animation: g-grow 6s ease-in-out infinite; }
.float { animation: g-float 7s ease-in-out infinite; }
.ping { transform-origin: center; animation: g-ping 3.2s ease-out infinite; }
.draw { stroke-dasharray: 1; animation: g-draw 5s ease-in-out infinite; }
.breathe { transform-origin: center; animation: g-breathe 8s ease-in-out infinite; }
.breathe.lag { animation-delay: -.7s; }
.sweep { transform-origin: 0 50%; animation: g-sweep 5s ease-in-out infinite; }
.pulse { animation: g-glow 4s ease-in-out infinite; }
.blink { animation: g-blink 2.4s ease-in-out infinite; }
@keyframes g-spin { to { transform: rotate(360deg); } }
.spin { transform-box: fill-box; transform-origin: center; animation: g-spin 40s linear infinite; }

/* The sections below the dial: one per group, in its theme, one tile per page */
.sec { border-top: 1px solid var(--rule); background: radial-gradient(1100px 460px at 16% 38%, color-mix(in oklab, var(--t) calc(5% + var(--glow) * 5%), transparent), transparent 70%); }
.sec-in { max-width: 1840px; margin: 0 auto; padding: 64px 40px 44px; display: grid; grid-template-columns: minmax(320px, 27vw) minmax(0, 1fr); column-gap: 48px; }
.sec-head h2 { margin: 0; font-size: clamp(28px, 2.1vw, 36px); line-height: 1.05; font-weight: 300; letter-spacing: -.02em; }
.sec-head h2::before { content: ""; display: block; width: 32px; height: 3px; border-radius: 2px; background: var(--t); margin-bottom: 18px; }
.sec-head p { margin: 14px 0 0; color: var(--mute); font-size: 16px; line-height: 1.45; max-width: 30ch; }
.tiles { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px 28px; align-content: start; }
@media (max-width: 1250px) and (min-width: 901px) { .tiles { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
#s-results .tiles { grid-template-columns: repeat(3, minmax(0, 300px)); }
#s-results .tile svg.art { max-width: 300px; }
.tile { display: flex; flex-direction: column; text-decoration: none; padding: 18px 0 22px; border-top: 1px solid var(--rule); position: relative; }
.tile::before { content: ""; position: absolute; left: 0; top: -1px; height: 2px; width: 0; border-radius: 2px; background: var(--t); transition: width .35s cubic-bezier(.3, 0, .2, 1); }
.tile:hover::before, .tile:focus-visible::before { width: 56px; }
.tile:focus-visible { outline-offset: 4px; }
.tile svg.art { width: 100%; max-width: 250px; height: auto; aspect-ratio: 4 / 3; margin: 2px 0 12px; transition: transform .35s cubic-bezier(.3, 0, .2, 1); }
.tile:hover svg.art { transform: translateY(-4px); }
.tile b { font-size: 18px; font-weight: 620; font-stretch: 106%; }
.tile span { color: var(--mute); font-size: 14px; line-height: 1.4; margin-top: 3px; }
.tile .ct { font-style: normal; color: color-mix(in oklab, var(--t) 80%, var(--ink)); font-size: 13px; font-weight: 600; margin-top: 6px; min-height: 1.2em; }

@media (max-width: 900px) {
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 6px 16px 36px; }
  .top { gap: 0 13px; padding-bottom: 2px; flex-wrap: wrap; }
  .top a { display: inline-flex; align-items: center; min-height: 40px; }  /* a finger's height */
  .name { font-stretch: 112%; margin-right: 0; }
  .words { display: contents; }  /* on a phone: the sentence, the button, the pages, then the picture and what is arriving */
  .cap { order: 1; margin-top: 20px; font-size: 22px; max-width: none; }
  .who { order: 1; }
  .go { order: 2; align-self: flex-start; margin-top: 18px; }
  .groups { display: none; }
  .down { order: 3; align-self: flex-start; margin-top: 16px; }
  .sec-in { display: block; padding: 44px 16px 26px; }
  .sec-head { margin-bottom: 18px; }
  .sec-head h2 { font-size: 28px; }
  .tiles { grid-template-columns: 1fr 1fr; gap: 0 18px; }
  .tile svg.art, #s-results .tile svg.art { max-width: 150px; }
  #s-results .tiles { grid-template-columns: 1fr 1fr; }
  .tile b { font-size: 16px; }
  .tile span { font-size: 13px; }
  .stage { order: 4; margin-top: 22px; padding: 0; display: block; }
  svg { height: auto; }
  .foot { order: 5; display: block; margin-top: 2px; min-height: 39px; }
  .said { white-space: normal; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }  /* two lines */
  .key { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .status.read::before { animation: none; }
  .go, .said, .glinks a, .tile::before, .tile svg.art, #svg { transition: none; }
  .an, .spin, #art.swap { animation: none !important; }
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
    <p class="cap" id="cap">We measure how far the Olmo 3 base model gets on MATH-500 with no training, against the RL-trained model.</p>
    <p class="who" id="who">Several people and their coding agents, at the SF AI Research Hackathon.</p>
    <a class="go" id="go" href="https://monitor.invariant.team/findings">Open Findings</a>
    <nav class="groups" id="index" aria-label="Pages by section"></nav>
    <a class="down" href="#s-results">Each page, with a picture ↓</a>
  </div>
  <div class="stage"><svg id="svg" role="group" aria-label="A dial with one bead for each page of the site"></svg></div>
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
  { id: "lab", g: 2, name: "AI Psychosis maxxing", href: "/lab/", line: "3D pictures of our own work, because of course", count: () => COUNTS.lab + " pictures" },
  { id: "exa", g: 2, name: "Exa", href: "/exa", line: "How the agents used web search" },
  { id: "pastdev", g: 2, name: "past.dev", href: "/pastdev", line: "How the agents used shared memory" },
  { id: "gpu", g: 2, name: "GPU prices", href: "https://gpu.invariant.team", line: "Forecasts of GPU rental prices", out: true },
  { id: "psychosis", g: 2, name: "AI Psychosis detox", href: "/psychosis", line: "The cure for the maxxing: log off and breathe, as a game" },
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

/* Themes and pictures. Each group of pages has a hue (TH), at the lightness and chroma of a person's color, and each
   page a small lit picture in a 120 x 90 box, drawn in the site's glass and lines with its group's hue as the accent.
   Each picture has one slow motion. The same picture fills the dial's body and the page's tile below. */
const TH = [255, 172, 62];
const hex = (cx, cy, rx, ry, a0 = 0) => [0, 1, 2, 3, 4, 5].map(i => { const a = (a0 + i * 60) * RAD; return [cx + rx * Math.cos(a), cy + ry * Math.sin(a)]; });
const petals = () => Array.from({ length: 10 }, (_, k) => { const a = k * 36 - 90, x = 60 + 35 * Math.cos(a * RAD), y = 45 + 35 * Math.sin(a * RAD);
  return `<ellipse class="gw" cx="${f(x)}" cy="${f(y)}" rx="5.2" ry="2.6" transform="rotate(${a} ${f(x)} ${f(y)})"/>`; }).join("");
const bust = (x, y, s, h) => `<g transform="translate(${x} ${y}) scale(${s})" style="--h:${h}"><path class="gb f2" d="M-19 42V36C-19 26 -11 22 0 22C11 22 19 26 19 36V42Z"/><path class="gpr" d="M-17 40V36C-17 27 -10 23.5 0 23.5C10 23.5 17 27 17 36V40"/><circle class="gb f1" cx="0" cy="8" r="10.5"/></g>`;
const slab = (y, o) => `<g opacity="${o}"><path class="gb f3" d="M28 ${y}V${y + 4}L60 ${y + 14}L92 ${y + 4}V${y}L60 ${y + 10}Z"/><path class="gb f1" d="M60 ${y - 10}L92 ${y}L60 ${y + 10}L28 ${y}Z"/><circle class="gi" cx="50" cy="${y - 1}" r="1.6"/><circle class="gi" cx="66" cy="${y + 2}" r="1.6"/><circle class="gi" cx="72" cy="${y - 3}" r="1.6"/></g>`;
const ART = {
  findings: `<rect class="gb" x="40" y="8" width="62" height="44" rx="4" opacity=".45"/><rect class="gb" x="30" y="17" width="62" height="44" rx="4" opacity=".72"/>
    <rect class="gb" x="20" y="26" width="64" height="48" rx="4"/><path class="gl" d="M28 66.5H76"/>
    <rect class="gi" x="30" y="56" width="7" height="10" rx="1"/><rect class="gi" x="41" y="50" width="7" height="16" rx="1"/><rect class="gi" x="52" y="45" width="7" height="21" rx="1"/>
    <rect class="ga an grow" x="63" y="35" width="7" height="31" rx="1"/>`,
  papers: `<rect class="gb" x="34" y="12" width="46" height="60" rx="3" opacity=".5" transform="rotate(-11 60 80)"/><rect class="gb" x="38" y="10" width="46" height="60" rx="3" opacity=".72" transform="rotate(7 60 80)"/>
    <g class="an float"><rect class="gb" x="36" y="14" width="48" height="62" rx="3"/><path class="gs" d="M43 24H69"/><path class="gl" d="M43 32H77M43 37H77M43 42H70"/>
    <rect class="gf" x="43" y="48" width="34" height="14" rx="1.5"/><path class="gs" stroke-width="1.3" d="M46 59L52 54L58 57L66 50L74 54"/><path class="gl" d="M43 68H74"/></g>`,
  talk: `<path class="gl" d="M60 66V81M49 82H71" stroke-opacity=".7" stroke-width="1.4"/><rect class="gb" x="14" y="10" width="92" height="56" rx="4"/>
    <rect class="ga" x="24" y="19" width="40" height="5" rx="1.5"/><circle class="gi" cx="27" cy="34" r="2"/><circle class="gi" cx="27" cy="44" r="2"/><circle class="gi" cx="27" cy="54" r="2"/>
    <path class="gl" stroke-opacity=".6" d="M33 34H80M33 44H74M33 54H66"/>
    <circle class="ga" r="2.6" opacity=".9"><animateMotion dur="7s" repeatCount="indefinite" path="M84 34L76 44L68 54L84 34"/></circle>`,
  board: `<rect class="gb f2" x="12" y="14" width="96" height="62" rx="5"/>` + [..."wrirwriwrriirrn"].map((c, i) => {
      const x = 28 + (i % 5) * 16, y = 29 + Math.floor(i / 5) * 16;
      return c === "w" ? `<circle class="gw" cx="${x}" cy="${y}" r="4.4"/>` : c === "i" ? `<circle class="gi" cx="${x}" cy="${y}" r="2.2"/>` :
        `<circle class="ga" cx="${x}" cy="${y}" r="4.4"/>` + (c === "n" ? `<circle class="gs an ping" cx="${x}" cy="${y}" r="4.4" stroke-width="1.4"/>` : "");
    }).join(""),
  proof: `<rect class="gb" x="30" y="8" width="60" height="74" rx="3"/><path class="gl" d="M39 20H81M39 27H76M39 34H80M39 41H70M39 48H78"/>
    <path class="gs an draw" pathLength="1" stroke-width="2.4" d="M40 62L47 69L60 56"/><rect class="ga" x="71" y="62" width="10" height="10" rx="1"/>`,
  values: (() => { const t = hex(60, 30, 30, 10.5), b = t.map(v => [v[0], v[1] + 34]), p = q => q.map(v => f(v[0]) + " " + f(v[1])).join("L"), c = [60, 30];
    return `<path class="gb f1" d="M${p([t[3], t[2], b[2], b[3]])}Z"/><path class="gb f2" d="M${p([t[2], t[1], b[1], b[2]])}Z"/><path class="gb f3" d="M${p([t[1], t[0], b[0], b[1]])}Z"/>
      <path class="gb f1" d="M${p(t)}Z"/><path class="ga an pulse" d="M${p([c, t[3], t[4]])}Z"/>${t.map(v => `<path class="gl" d="M60 30L${f(v[0])} ${f(v[1])}"/>`).join("")}
      <path class="gs" stroke-width="1.2" opacity=".7" d="M14 4L60 30"/><path class="gs" stroke-width="1.2" opacity=".45" d="M39 58L22 64M60 73V84M81 58L98 64"/>`; })(),
  team: bust(33, 38, .8, 150) + bust(87, 38, .8, 65) + `<g class="an float">${bust(60, 33, 1, 325)}</g>`,
  lab: `<ellipse class="gl" stroke-opacity=".3" cx="60" cy="47" rx="50" ry="13"/><path class="gl" d="M60 46L28 62M60 46L92 62M60 46V12" stroke-dasharray="2 3"/>
    <circle class="ga" cx="60" cy="45" r="8.5" opacity=".85"/><circle cx="57" cy="42" r="2.6" fill="var(--glass-hi)" opacity=".7"/>
    <path class="gb f1" fill-opacity=".4" d="M60 12L92 28L60 44L28 28Z"/><path class="gb f2" fill-opacity=".4" d="M28 28L60 44V78L28 62Z"/><path class="gb f3" fill-opacity=".4" d="M60 44L92 28V62L60 78Z"/>
    <circle class="ga" r="2.4"><animateMotion dur="8s" repeatCount="indefinite" path="M10 47A50 13 0 1 0 110 47A50 13 0 1 0 10 47"/></circle>`,
  exa: `<rect class="gb f2" x="68" y="54" width="28" height="7" rx="3.5" transform="rotate(45 68 57.5)"/><circle class="gb" cx="50" cy="40" r="25"/><circle class="gl" cx="50" cy="40" r="20.5"/>
    <rect class="ga an sweep" x="35" y="37" width="27" height="6" rx="1.5" opacity=".5"/><path class="gl" stroke-opacity=".7" d="M35 31H62M35 40H65M35 49H57"/>
    <path class="gl" d="M75 33L93 22M76 40L100 38M75 47L93 56"/><circle class="ga" cx="95" cy="21" r="3"/><circle class="ga" cx="103" cy="38" r="3"/><circle class="ga" cx="95" cy="57" r="3"/>`,
  pastdev: slab(62, 1) + slab(44, .88) + slab(26, .76) + `<path class="gs" stroke-width="1.1" stroke-dasharray="2 3" opacity=".6" d="M60 66V22"/>
    <circle class="ga" r="3"><animateMotion dur="6s" repeatCount="indefinite" path="M60 64L60 24L60 64"/></circle>`,
  gpu: `<path class="gl" d="M16 76H106M16 12V76"/><path class="gf" d="M62 50L76 40L90 37L104 28V48L90 53L76 54L62 50Z"/>
    <polyline class="gl" stroke-opacity=".85" stroke-width="1.6" points="16,63 26,58 36,61 46,52 54,55 62,50"/><path class="gl" stroke-dasharray="2 3" d="M62 16V76"/>
    <polyline class="gs" stroke-dasharray="3 3" points="62,50 76,47 90,45 104,38"/><circle class="ga an blink" cx="104" cy="38" r="3.2"/>
    <g transform="translate(26 22)"><rect class="gb" width="18" height="18" rx="2.5"/><rect class="gw" x="5" y="5" width="8" height="8" rx="1"/>
    <path class="gl" d="M4 -3V0M9 -3V0M14 -3V0M4 18V21M9 18V21M14 18V21M-3 4H0M-3 9H0M-3 14H0M18 4H21M18 9H21M18 14H21"/></g>`,
  psychosis: `<g class="spin">${petals()}</g>` + `<circle class="gs an breathe" cx="60" cy="45" r="25"/><circle class="gl an breathe lag" stroke-opacity=".75" stroke-width="1.4" cx="60" cy="45" r="21"/><circle class="gb" cx="60" cy="45" r="10"/>`,
};
const art = id => `<ellipse class="gfloor" cx="63" cy="84" rx="42" ry="4.5"/>` + ART[id];

/* Geometry: the ring lies flat around the body and is seen from above (pitch). R is the ring of beads, the ticks
   run from rt to rt + 8 (every sixth to rt + 15) inside it on a fine inner ring, rb is the body. fs is the size of a name at the front and min the
   smallest a name is drawn (on a phone 26 of 720 units, which is 12 px on a 375 px screen).
   The picture is wider than the ring by the longest name on each side. Names with q under far are not drawn. */
function geo() {
  return narrow.matches
    ? { w: 720, h: 548, cx: 360, cy: 262, R: 272, rt: 214, rb: 108, D: 1700, pitch: 36, bead: 12, fs: 27, min: 26, fn: 28, fc: 21, far: .86, art: 1.36, at: .76, ny: .6 }
    : { w: 1060, h: 660, cx: 530, cy: 290, R: 400, rt: 334, rb: 150, D: 2300, pitch: 36, bead: 8, fs: 17, min: 0, fn: 29, fc: 14.5, far: 0, art: 1.7, at: .8, ny: .5 };
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
    `<radialGradient id="shade">${stop(.3, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    "</defs>" +
    `<circle class="atmo" cx="${G.cx}" cy="${G.cy}" r="${G.rb * 2.1}" fill="url(#atmo)"/>` +
    `<ellipse class="shade" cx="${G.cx + G.rb * .2}" cy="${G.cy + G.rb * 1.02}" rx="${G.rb * 1.25}" ry="${G.rb * .3}" fill="url(#shade)"/>` +
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
    g.innerHTML = `<circle class="pad"/><circle class="b"/><text>${esc(p.name)}</text>`;
    p.el = g; p.front = null;
  });
  const link = (p, k) => `<a href="${p.href}" data-k="${k}">${esc(p.name)}${p.out ? " \u2197" : ""}</a>`;
  $("index").innerHTML = GROUPS.map((name, g) => `<div class="grp th" role="group" aria-labelledby="gl${g}" style="--th:${TH[g]}"><p class="glab" id="gl${g}"><i></i><a href="#${SEC[g][0]}">${name}</a></p><p class="glinks">` +
    PAGES.map((p, k) => p.g === g ? link(p, k) : "").join("") + "</p></div>").join("");
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
  document.querySelectorAll(".tile").forEach(t => { const q = PAGES[t.dataset.k]; t.querySelector(".ct").textContent = q.count ? q.count(S.m) : ""; });
  $("go").textContent = "Open " + p.name; $("go").href = p.href;
  $("body-c").setAttribute("aria-label", "Open " + p.name);
  $("index").querySelectorAll("a").forEach(a => a.classList.toggle("on", Number(a.dataset.k) === S.sel));
  PAGES.forEach((q, k) => q.el.classList.toggle("on", k === S.sel));
}
function select(k, link) {
  k = (k % N + N) % N;
  let d = k - (S.to % N + N) % N; if (d > N / 2) d -= N; if (d < -N / 2) d += N;  // the short way around
  S.to += d; S.sel = k;
  if (link) { S.pick = k; history.replaceState(null, "", "#" + PAGES[k].id); }
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
  const n = (m.how.match(/vote over (\d+)/) || [])[1];
  const how = [/\bcue\b/.test(m.how) && "a prompt cue", n && `a majority vote over ${n} samples`].filter(Boolean);
  $("cap").textContent = (how.length ? `With ${how.join(" and ")}, and no training, ` : "With no training, ") + "the Olmo 3 base model " +
    (m.start < m.base ? `goes from ${f(m.start)}\u00a0% to ${f(m.base)}\u00a0%` : `reaches ${f(m.base)}\u00a0%`) + " on MATH-500" +
    (isFinite(m.rl) ? (m.rl > m.base ? `, ${f(m.rl - m.base)} points below the RL-trained model's ${f(m.rl)}\u00a0%.` : `. The RL-trained model scores ${f(m.rl)}\u00a0%.`) : ".");
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

/* The sections below the dial, one per group, with a tile for each page. */
const SEC = [
  ["s-results", "What the team measured, wrote up and presented."],
  ["s-how", "How several people and their coding agents work on one research direction together."],
  ["s-also", "3D pictures, how the agents used web search and shared memory, GPU price forecasts, and a game about ourselves."],
];
$("sections").innerHTML = GROUPS.map((name, g) => `<section class="sec th" id="${SEC[g][0]}" style="--th:${TH[g]}" aria-labelledby="${SEC[g][0]}-h"><div class="sec-in">` +
  `<header class="sec-head"><h2 id="${SEC[g][0]}-h">${name}</h2><p>${SEC[g][1]}</p></header><div class="tiles">` +
  PAGES.map((p, k) => p.g !== g ? "" : `<a class="tile" href="${p.href}" data-k="${k}"><svg class="art" viewBox="0 0 120 90" aria-hidden="true">${art(p.id)}</svg>` +
    `<b>${esc(p.name)}${p.out ? " \u2197" : ""}</b><span>${esc(p.line)}</span><em class="ct"></em></a>`).join("") + "</div></div></section>").join("");
if (still.matches) document.querySelectorAll("svg").forEach(v => v.pauseAnimations && v.pauseAnimations());

build();
const start = PAGES.findIndex(p => "#" + p.id === location.hash);
if (start > 0) { S.sel = start; S.to = S.rot = start; readout(); }
S.pick = S.sel;
$("svg").addEventListener("click", e => {
  const b = e.target.closest(".bead");
  if (b) select(Number(b.dataset.k), true); else if (e.target.id === "body-c") location.href = PAGES[S.sel].href;
});
$("svg").addEventListener("keydown", e => {
  if (e.key !== "Enter" && e.key !== " ") return;
  const b = e.target.closest(".bead");
  if (b) { e.preventDefault(); select(Number(b.dataset.k), true); } else if (e.target.id === "body-c") location.href = PAGES[S.sel].href;
});
$("index").addEventListener("focusin", e => { const a = e.target.closest("a[data-k]"); if (a) select(Number(a.dataset.k), true); });
$("index").addEventListener("pointerover", e => { const a = e.target.closest("a[data-k]"); if (a && e.pointerType === "mouse") select(Number(a.dataset.k), false); });
$("index").addEventListener("pointerleave", e => { if (e.pointerType === "mouse" && S.sel !== S.pick) select(S.pick, false); });
addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey || scrollY > innerHeight / 2) return;  // the dial is off screen: the keys are the browser's
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
