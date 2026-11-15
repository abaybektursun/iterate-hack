"""The presentation page of the team site: the talk about Nanolab as one stepped story, for a first-time reader.

view.py serves PAGE at /demo. It is not a tab in the header. The page shows the lab of the Design page (architecture.py),
drawn by the same code from the same /data: the board as a lit disc in the centre, each person's swarm of agents
around it with threads to the board, the Chat ring and the Retro loop. Beside it a column of words is always open:
the section, a progress row of 12 steps, one large sentence, one smaller fact line with where and when its numbers were
measured, up to three quiet rows that open detail, and Back and Next at the bottom.

A step lights some parts and dims the rest, shows one figure on the face of the board (a chart drawn in place of the
item dots), and sometimes moves the view in for a closer look (steps 4 to 6). Entered with Next (or the right arrow,
Space, PageDown), a step plays its short motion: a pulse along a thread, bars that grow, four pulses that leave for
Modal and come back. Entered any other way (Back, a progress segment, Home, End, a typed address, a reload) it shows
its settled state at once. A key press at any moment retargets every motion from where it is. Every step has its
address (/demo#result), and every detail too (/demo#result/cue); Esc closes a detail. Where the lab is lit, real
events of the board are replayed as on the Design page.

Every number comes from demo_facts.FACTS (shipped as JSON with only its value, count, source and time) or live from
/data; the detail panels come from demo_panels.py (PANEL_CSS and PANELS_JS) and are written into the page here.
Nothing here writes to the board.
"""
import json

import demo_facts
import demo_panels


def shipped(facts):
    """FACTS as the browser gets it: per key only v, n, src and at (the notes are for the presenters)."""
    return {k: ({f: x.get(f) for f in ("v", "n", "src", "at")} if isinstance(x, dict) and "v" in x else x) for k, x in facts.items()}


def as_js(value):
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Nanolab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens of the Design page (architecture.py), unchanged: dark is a lit glass body in a dark room, light the same
   object as white porcelain on a cool grey table. The light comes from the upper left in both. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34; --on-blue: #fff;
  --pl: .56; --pc: .15; --dim: .16;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue); --lift: 38%;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18); --btn-drop: rgba(16, 24, 32, .42);
  --fbar1: #b3bdc6;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --pl: .78; --pc: .13; --dim: .24;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff; --lift: 55%;
    --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7); --btn-drop: rgba(0, 0, 0, .6);
    --fbar1: #4a5763;
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
.hue { --c: oklch(var(--pl) var(--pc) var(--h)); }
@keyframes fadein { from { opacity: 0; } }
.page.load { animation: fadein .3s ease both; }

.page {
  display: grid; grid-template-columns: minmax(0, 1fr) clamp(380px, 31vw, 620px); grid-template-rows: auto minmax(0, 1fr);
  height: 100vh; height: 100dvh; min-height: 620px; max-width: 2200px; margin: 0 auto;
  padding: 20px clamp(28px, 2.8vw, 56px) 24px;
}
.top { grid-column: 1 / -1; grid-row: 1; display: flex; align-items: center; gap: 26px; font-size: clamp(13px, .9vw, 17px); padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 1.15em; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.status { margin-left: auto; color: var(--mute); white-space: nowrap; display: flex; align-items: center; gap: 10px; }
.status::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--blue); box-shadow: 0 0 0 4px color-mix(in srgb, var(--blue) 20%, transparent); }
.status.bad { color: var(--red); }
.status.bad::before { background: var(--red); box-shadow: 0 0 0 4px color-mix(in srgb, var(--red) 20%, transparent); }
@keyframes heart { from { box-shadow: 0 0 0 0 color-mix(in srgb, var(--blue) 70%, transparent); } }
.status.read::before { animation: heart 1.1s ease-out; }

/* The picture. In the close framing nothing may leave the stage, and the swarms it crops fade into the room. */
.stage { grid-column: 1; grid-row: 2; position: relative; min-width: 0; min-height: 0; display: flex; padding: 8px 0 0;
  clip-path: inset(-40px 0 -24px -40px); transition: clip-path .4s ease; }
.stage.near { clip-path: inset(0); }
.stage::after { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: 0; transition: opacity .4s ease;
  background: linear-gradient(to right, var(--paper), transparent 6%, transparent 94%, var(--paper)),
              linear-gradient(to bottom, var(--paper), transparent 5%, transparent 95%, var(--paper)); }
.stage.near::after { opacity: 1; }
svg { width: 100%; height: 100%; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); text-anchor: middle; font-stretch: 112%; letter-spacing: .012em; }
.label { font-weight: 600; paint-order: stroke fill; stroke: var(--paper); stroke-width: 10px; stroke-linejoin: round; }
.label.plain { stroke: none; }
.who { font-weight: 560; fill: var(--c); paint-order: stroke fill; stroke: var(--paper); stroke-width: 7px; stroke-linejoin: round; }
.part { transition: opacity .45s ease; }
[data-go] { cursor: pointer; }
svg [data-go]:focus { outline: none; }
svg [data-go]:focus-visible .ring { stroke: var(--blue); stroke-width: 3; }
svg [data-go]:focus-visible .rib { fill: var(--ink); }
.has-focus .part { opacity: var(--dim); }
.has-focus .part.on { opacity: 1; }
.hit { fill: none; stroke: transparent; pointer-events: stroke; }
.pad { fill: transparent; }
.atmo, .shade, .spec, .bloom, .pulse, .ripple, .arrive, .tick, .trace, .nhalo { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.spec { opacity: var(--spec); }
.bloom { opacity: var(--bloom); }
.board-ring { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.rib { fill: url(#rvfade) var(--blue); }
.chev { fill: none; stroke: var(--blue); stroke-width: 2.3; stroke-linecap: round; stroke-linejoin: round; }
[data-part="review"] .label { fill: var(--blue); }
.comet-tail { fill: var(--blue); }
.comet-core { fill: var(--core); }
.beads { fill: none; stroke: url(#msgfade) var(--mute); stroke-width: 1.5; }
.thread { fill: none; stroke: var(--c); stroke-width: .9; opacity: .5; }
.tie { fill: none; stroke: var(--c); stroke-width: 1.1; opacity: .7; }
.agent { fill: var(--c); stroke: none; transition: opacity .45s ease; }
.solo .agent:not([data-k="0"]) { opacity: .12; }
.person { fill: var(--c); stroke: var(--paper); stroke-width: 3; }
.dot { fill: var(--c); }
.dot.note { opacity: .6; }
.dot.work { fill: var(--glass); stroke: var(--c); stroke-width: 2; }
.key .dot.work { fill: var(--paper); }
.dot.stale { stroke: var(--red); }
.sub { fill: var(--mute); font-weight: 460; }
.said { font-weight: 470; fill: var(--c); text-anchor: start; pointer-events: none; paint-order: stroke fill; stroke: var(--paper); stroke-width: 7px; stroke-linejoin: round; }
.said .when { fill: var(--mute); }
.said .when.now { fill: var(--blue); }
.ptail { fill: var(--c); opacity: .5; }
.phead { fill: var(--c); }
.ripple { fill: none; stroke: var(--c); stroke-width: 1.8; stroke-linecap: round; }
.arrive { fill: none; stroke: var(--c); stroke-width: 1.6; }
#fx { pointer-events: none; }
.fly { fill: var(--c); }
.halo { fill: none; stroke: var(--c); stroke-width: 1.5; opacity: .45; }
.nhalo { fill: none; stroke: var(--blue); stroke-width: 2; opacity: 0; transition: opacity .4s ease; }
.nhalo.on { opacity: .95; }
.tick { fill: var(--paper); stroke: var(--c); stroke-width: 1.4; opacity: 0; transition: opacity .35s ease; }
.tick.on { opacity: 1; }
#dotwrap { transition: opacity .3s ease; }
#dotwrap.off { opacity: 0; }
#dotwrap.off .dot { pointer-events: none; }

/* The points outside the lab (Modal, Exa), each shown only in its own step and its own panel */
.ext { opacity: 0; visibility: hidden; transition: opacity .3s ease, visibility 0s .3s; }
.ext.show { opacity: 1; visibility: visible; transition: opacity .3s ease; }
.has-focus .ext.show:not(.on) { opacity: var(--dim); }
.xring { fill: var(--paper); stroke: var(--mute); stroke-width: 1.5; }
.xdot { fill: var(--ink); }
.trace { fill: none; stroke: var(--c); stroke-width: 1; opacity: 0; transition: opacity .4s ease; }
.trace.on { opacity: .4; }

/* The figures on the face of the board. Units: 164 is the board's radius. */
.fig { opacity: 0; visibility: hidden; transition: opacity .25s ease, visibility 0s .25s; }
.fig.on { opacity: 1; visibility: visible; transition: opacity .35s ease .15s; }
.fig text { text-anchor: middle; }
.fnum { font-weight: 560; font-stretch: 112%; letter-spacing: -.01em; }
.flab { font-weight: 540; }
.fsub { font-weight: 460; fill: var(--mute) !important; }
.fcount { font-weight: 600; fill: var(--paper) !important; }
.fcount.onblue { fill: var(--on-blue) !important; }
.fcount.onfaint { fill: var(--ink) !important; }
.fbar { transition: fill .5s ease; }
.f-faint { fill: var(--fbar1); }
.f-mute { fill: var(--mute); }
.f-ink { fill: var(--ink); }
.f-blue { fill: var(--blue); }
.ft { opacity: 0; transition: opacity .35s ease, transform .35s ease; }
.ft.rise { transform: translateY(8px); }
.ft.on { opacity: 1; transform: none; }
.mutedtext { fill: var(--mute); transition: fill .3s ease; }
.strike { fill: none; stroke: var(--red); stroke-width: 3; stroke-linecap: round; stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset .3s ease; }
.strike.on { stroke-dashoffset: 0; }
.flink { fill: none; stroke: var(--faint); stroke-width: 1; }
.fdot { transform-box: fill-box; transform-origin: center; transform: scale(0); transition: transform .45s cubic-bezier(.3, 1.5, .5, 1); }
.fdot.on { transform: none; }
.bk { transition: opacity .25s ease; }
.why .bk { opacity: 0; }
.why .sl-l { fill: var(--ink); }
.why .sl-r { fill: var(--fbar1); }
.src-link { fill: var(--blue) !important; font-weight: 560; }
.src-link:hover { text-decoration: underline; }

/* One drawn entrance, then only real events move */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
@keyframes pop { from { transform: scale(0); } }
@keyframes ping { 35% { transform: scale(2.2); } }
.dot, .agent, .person, .xm { transform-box: fill-box; transform-origin: center; }
.enter .draw { stroke-dasharray: 1; animation: draw 1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec { animation: fade 1.6s .2s both; }
.enter .rib, .enter .chev { animation: fade .9s .5s both; }
.enter .thread, .enter .tie, .enter .beads, .enter .label, .enter .who, .enter .sub, .enter .key .dot, .enter .key .agent { animation: fade .6s .55s both; }
.enter .comet { animation: fade .8s 1.3s both; }
.enter .part:not(.key) .agent, .enter .person { animation: pop .45s cubic-bezier(.3, 1.5, .5, 1) both; animation-delay: calc(.25s + var(--i, 0) * 18ms); }
.enter .dot { animation: pop .4s cubic-bezier(.3, 1.4, .5, 1) both; animation-delay: calc(.7s + var(--i, 0) * 7ms); }
.dot.arrived { animation: pop .5s cubic-bezier(.3, 1.6, .5, 1) .9s both; }
.dot.ping, .xdot.ping { animation: ping .8s ease-out; }
.xdot { transform-box: fill-box; transform-origin: center; }

/* The words column: always open, so the picture never moves sideways */
.side { grid-column: 2; grid-row: 2; min-width: 0; min-height: 0; display: flex; flex-direction: column;
  border-left: 1px solid var(--rule); padding: clamp(20px, 5vh, 64px) 0 0 clamp(28px, 2.8vw, 56px); }
.kick { display: flex; justify-content: space-between; font-size: clamp(13px, 1vw, 19px); font-weight: 600; color: var(--mute); margin-bottom: 8px; }
.steps { display: flex; gap: 5px; }
.steps a { flex: 1; height: 28px; display: flex; align-items: center; }
.steps a.g { margin-left: 9px; }
.steps i { flex: 1; height: 3px; border-radius: 2px; background: var(--rule); transition: background .2s ease; }
.steps a.done i { background: var(--ink); }
.steps a[aria-current] i { background: var(--blue); }
.pane { flex: 1; min-height: 0; overflow: hidden auto; scrollbar-width: none; margin-top: clamp(14px, 2.4vh, 40px); }
.pane::-webkit-scrollbar { display: none; }
@keyframes rise { from { opacity: 0; transform: translateY(10px); } }
.say { margin: 0; font-size: clamp(30px, min(3.1vw, 5.2vh), 68px); line-height: 1.1; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; min-height: 4.4em; text-wrap: balance;
  animation: rise .3s cubic-bezier(.23, 1, .32, 1) both; }
.say b { font-weight: 560; }
.seq b { display: inline-block; animation: rise .45s both; animation-delay: calc(.3s + var(--n) * .4s); }
.fact { margin: clamp(16px, 2.6vh, 30px) 0 0; font-size: clamp(17px, min(1.45vw, 2.45vh), 31px); line-height: 1.36; max-width: 38ch; }
.fact b { font-weight: 600; }
.fact a { text-decoration-color: var(--rule); text-underline-offset: 3px; }
.fact .who-c { color: var(--c); font-weight: 600; }
.src { display: block; margin-top: .45em; font-size: .7em; font-weight: 460; color: var(--mute); }
.src a { color: inherit; }
.open { margin: .9em 0 0; font-size: clamp(17px, min(1.45vw, 2.45vh), 31px); line-height: 1.36; color: var(--mute); max-width: 34ch; }
.open::before { content: ""; display: inline-block; width: 10px; height: 10px; border-radius: 50%; border: 1.5px solid var(--mute); margin-right: .5em; vertical-align: .05em; }
.recap { list-style: none; margin: clamp(16px, 2.6vh, 30px) 0 0; padding: 0; max-width: 36ch; }
.recap li { border-top: 1px solid var(--rule); }
.recap a { display: block; padding: .45em 0; text-decoration: none; font-size: clamp(15px, min(1.15vw, 2vh), 26px); line-height: 1.3; }
.recap a b { font-weight: 600; }
.recap a:hover { color: var(--blue); }
.url { display: inline-block; margin-top: clamp(16px, 2.6vh, 30px); font-size: clamp(20px, min(1.9vw, 3.2vh), 40px); font-weight: 560; font-stretch: 106%; color: var(--blue); text-decoration: none; }
.fact, .open, .recap, .walk, .url { animation: rise .3s cubic-bezier(.23, 1, .32, 1) .25s both; }
.walk { display: inline-block; margin-top: 24px; padding: .7em 1.4em; border-radius: 999px; background: var(--btn); color: var(--btn-ink); text-decoration: none;
  font-weight: 620; font-size: clamp(15px, 1.15vw, 22px); font-stretch: 106%; letter-spacing: .004em;
  box-shadow: inset 0 1px 0 var(--btn-edge), 0 14px 28px -14px var(--btn-drop); }
.walk:hover { box-shadow: inset 0 1px 0 var(--btn-edge), 0 0 0 1.5px var(--blue), 0 18px 32px -12px var(--btn-drop); }
.more { margin-top: clamp(12px, 2vh, 34px); max-width: 36ch; }
.q { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: .5em 0; border-top: 1px solid var(--rule);
  font-size: clamp(14px, 1.1vw, 21px); font-weight: 560; color: var(--mute); animation: rise .3s cubic-bezier(.23, 1, .32, 1) both; animation-delay: calc(.4s + var(--i) * 60ms); }
.q:hover, .q:focus-visible { color: var(--ink); }
.quiet *, .quiet { animation: none !important; }
.nav { margin-top: auto; padding-top: 16px; display: flex; align-items: center; gap: 10px; }
.nav button { padding: .62em 1.3em; border-radius: 999px; border: 1px solid var(--faint); font-weight: 600; font-size: clamp(14px, 1.05vw, 20px); transition: background .15s ease, border-color .15s ease, color .15s ease; }
.nav button.next { background: var(--btn); color: var(--btn-ink); border-color: transparent; box-shadow: inset 0 1px 0 var(--btn-edge); }
.nav button.next.plain { background: none; color: var(--ink); border-color: var(--faint); box-shadow: none; }
.nav button:hover { border-color: var(--blue); background: var(--blue); color: var(--on-blue); box-shadow: none; }
.nav button[disabled] { opacity: .3; pointer-events: none; }
.hint { margin-left: auto; font-size: clamp(13px, .95vw, 18px); color: var(--mute); }

/* Detail, in the Design page's classes at the sizes of the talk */
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--ink);
  position: sticky; top: 0; background: var(--paper); z-index: 1; animation: rise .22s cubic-bezier(.23, 1, .32, 1) both; }
.dhead h2 { margin: 0; font-size: clamp(17px, 1.3vw, 25px); font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.dhead h2:focus { outline: none; }
.dhead h2.hue { color: var(--c); }
.close { font-size: clamp(13px, .95vw, 17px); color: var(--mute); }
.close:hover { color: var(--ink); }
.dbody { animation: rise .22s cubic-bezier(.23, 1, .32, 1) .05s both; }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.35vw, 26px); line-height: 1.36; font-weight: 380; max-width: 30ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: clamp(14.5px, 1.1vw, 21px); color: var(--mute); max-width: 40ch; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.facts b { color: var(--ink); font-weight: 600; }
.rows { margin-top: 20px; }
.rows h3 { margin: 0 0 4px; font-size: clamp(13px, .95vw, 18px); font-weight: 600; color: var(--mute); }
.rows a { display: block; padding: 8px 0 8px 12px; border-top: 1px solid var(--rule); text-decoration: none; position: relative; font-size: clamp(13.5px, 1vw, 19px); line-height: 1.42; }
.rows a::before { content: ""; position: absolute; left: 0; top: 11px; bottom: 11px; width: 2px; border-radius: 2px; background: var(--c, var(--mute)); }
.rows a:hover { background: linear-gradient(to right, var(--sheet), transparent); }
.rows .t { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 1; overflow: hidden; overflow-wrap: anywhere; }
.rows .m { color: var(--mute); font-size: .92em; }
.rows .m b { color: var(--c); font-weight: 600; }
/*__PANEL_CSS__*/

@media (max-width: 900px) {
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 0; }
  .top { gap: 13px; padding-bottom: 12px; }
  .top a.tab { display: none; }
  .name { font-stretch: 112%; margin-right: 0; }
  .stage { order: 1; margin-top: 10px; padding: 0; clip-path: inset(0); }
  svg { height: auto; }
  .side { order: 2; display: block; border-left: 0; padding: 14px 0 0; }
  .pane { overflow: visible; }
  .say { font-size: clamp(26px, 7.4vw, 34px); min-height: 0; }
  .fact, .open { font-size: 17px; }
  .recap a { font-size: 16px; }
  .nav { position: sticky; bottom: 0; padding: 10px 0 max(10px, env(safe-area-inset-bottom)); background: var(--paper); border-top: 1px solid var(--rule); margin-top: 18px; }
  .nav button { flex: 1; text-align: center; }
  .hint { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .enter *, .dot.arrived, .dot.ping, .xdot.ping, .status.read::before, .pane *, .page.load { animation: none !important; }
  .pane *, .part, .fig, .fbar, #dotwrap, .stage, .stage::after, .trace, .tick, .ext, .ft, .strike, .fdot, .bk, .nhalo, .agent { transition: none !important; }
}
</style>
</head>
<body>
<div class="page" id="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a class="tab" href="/">Board</a>
    <a class="tab" href="/architecture">Design</a>
    <a class="tab" href="/proof">Proof</a>
    <a class="tab" href="/findings">Findings</a>
    <span class="status" id="status">Reading the board</span>
  </header>
  <aside class="side" id="side">
    <div class="kick"><span id="sec"></span><span id="count"></span></div>
    <nav class="steps" id="steps" aria-label="Steps"></nav>
    <div class="pane" id="pane" aria-live="polite"></div>
    <div class="nav"><button id="back" data-step="-1">Back</button><button id="next" class="next" data-step="1">Next</button><span class="hint" id="hint"></span></div>
  </aside>
  <div class="stage" id="stage"><svg id="svg" role="group" aria-label="The lab: people and their agents around one shared board"></svg></div>
</div>
<script>
/* Data shipped from tools/demo_facts.py: for each key only v (value), n (count), src (where) and at (when). */
const FACTS = __FACTS__;
const SOURCES = __SOURCES__;
const $ = id => document.getElementById(id);
const HUES = [325, 150, 65, 195, 105, 45, 175, 350];  // the board page's colors: the same person has the same color on every page
const S = { data: null, m: null, g: null, error: null, readAt: 0, key: "", seen: null, entered: false, token: 0, queue: [],
  n: 0, panel: null, actor: -1, replay: "on", fast: [], cues: [], instant: false, crawl: false, face: "dots", ext: new Set(), opener: null, scored: new Set() };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1);
const msgNs = m => Number(m.sk.slice(0, 20));
const mins = ns => Math.max(0, Math.floor((Date.now() * 1e6 - Number(ns)) / 60e9));
const since = ns => { const s = Math.max(0, Math.floor(Date.now() / 1000 - Number(ns) / 1e9)); return s < 60 ? s + " s ago" : s < 3600 ? `${Math.floor(s / 60)} min ${String(s % 60).padStart(2, "0")} s ago` : ago(ns); };
const ago = ns => { const m = mins(ns); return m < 1 ? "now" : m < 60 ? m + " min ago" : m < 2880 ? Math.floor(m / 60) + " h ago" : Math.floor(m / 1440) + " d ago"; };
const fv = key => FACTS[key] ? FACTS[key].v : null;
function hueOf(person) { const i = S.m ? S.m.people.indexOf(person) : -1; return i < 0 ? null : HUES[i % HUES.length]; }

/* Reading FACTS for display. A missing value is shown as "?" and named in the console, so it is never guessed. */
const MISSING = new Set();
function need(key, path) {
  let x = FACTS[key] ? FACTS[key].v : null;
  for (const p of path ? path.split(".") : []) x = x == null ? null : x[p];
  if (x == null) { const k = key + (path ? "." + path : ""); if (!MISSING.has(k)) { MISSING.add(k); console.error(`demo: FACTS has no value for ${k}`); } return "?"; }
  return x;
}
const nf = x => typeof x === "number" ? x.toLocaleString("en-US") : x;
const pct = (key, path) => { const v = need(key, path), n = FACTS[key] && FACTS[key].n; return typeof v === "number" && n ? Math.round(100 * v / n) : "?"; };
const WORD = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"];
const word = x => typeof x === "number" && WORD[x] ? WORD[x] : nf(x);
const cap = s => String(s).charAt(0).toUpperCase() + String(s).slice(1);
const MONTH = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
function when(at) {  // "2026-11-15 05:37 UTC" -> "Nov 15, 05:37 UTC"
  const r = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/.exec(String(at || ""));
  return r ? `${MONTH[Number(r[2]) - 1]} ${Number(r[3])}, ${r[4]}:${r[5]} UTC` : "";
}
function where(src) {  // the short name of where a number was measured: its board items, else its file, else the first words
  const ids = [...new Set(String(src || "").match(/\b(?:result|knowledge|idea|work|skill)-[0-9a-f]{6}\b/g) || [])];
  if (ids.length) return "board " + ids.slice(0, 2).map(id => `<a href="/#${id}">${id}</a>`).join(", ");
  const p = /(?:studies|tools|infra|meta)\/[\w./+-]+/.exec(src || "");
  if (p) return esc(p[0].split("/").slice(-2).join("/"));
  return esc(String(src || "").split(/[:(;,]/)[0].trim().slice(0, 34));
}
function tail(keys) {  // where and when the numbers of a line were measured, in one quiet line
  const by = new Map();
  keys.forEach(k => { const x = FACTS[k]; if (!x || !x.at) return; const w = where(x.src), t = when(x.at), list = by.get(t) || []; if (!list.includes(w)) list.push(w); by.set(t, list); });
  const parts = [...by].map(([t, ws]) => `${ws.join(", ")}, ${t}`);
  return parts.length ? `<span class="src">${parts.slice(0, 3).join("; ")}</span>` : "";
}
const b = (x, n) => n == null ? `<b>${x}</b>` : `<b style="--n:${n}">${x}</b>`;

/* The four parts of the lab, in the words of the Design page (tools/architecture.py, TEXT), with its live rows. The
   Chat text leaves out the Design page's "0.2 s" line, which no FACTS key records. */
const TEXT = {
  board: {
    name: "Board",
    lead: "The board holds ideas, work in progress, results and knowledge, with votes and comments. Every agent reads it before starting and posts to it while working.",
    facts: ["An agent claims work by posting it. If another open claim names the same idea, the tool says so.", "Everything posted here can also be searched, together with findings from papers and past agent sessions. That search is the team's memory.", "Work that has been idle for 60 minutes can be taken over by another agent, after asking.", "Each dot is one item: hollow is open work, solid is a result, small is an idea or a note."],
    rows: m => ({ title: `${cnt(m.n.result)} results, ${cnt(m.n.work)} open, ${cnt(m.n.idea)} ideas`, list: m.results }),
  },
  chat: {
    name: "Chat",
    lead: "Agents send each other short messages: to everyone, to one person's agents, or about one board item.",
    facts: ["In Claude Code, a hook adds new messages to an agent's context after its tool calls, so the agent does not have to check for them."],
    rows: m => ({ title: `${m.msgs.length} messages to everyone in the last ${m.hours} h`, list: m.msgs }),
  },
  retro: {
    name: "Retro",
    lead: "Every tool command is logged with its time, person, agent and commit. After each finished result, an agent reviews these logs.",
    facts: ["The review measures how long each step took, from claiming the work to posting the result.", "It then makes one change to the tools or the rules, to remove the slowest step or a failure that repeats.", "Whether these changes help has not been measured yet."],
  },
};
const cnt = n => n >= 60 ? "60+" : n;  // /data returns the newest 60 of each kind
/* An agent is drawn as the mark of the product it runs on: Claude Code or Codex. Outlines from Bootstrap Icons
   1.13.1 (MIT), each in a 16 by 16 box. Any other agent is a rounded square. */
const MARKS = {
  claude: "m3.127 10.604 3.135-1.76.053-.153-.053-.085H6.11l-.525-.032-1.791-.048-1.554-.065-1.505-.08-.38-.081L0 7.832l.036-.234.32-.214.455.04 1.009.069 1.513.105 1.097.064 1.626.17h.259l.036-.105-.089-.065-.068-.064-1.566-1.062-1.695-1.121-.887-.646-.48-.327-.243-.306-.104-.67.435-.48.585.04.15.04.593.456 1.267.981 1.654 1.218.242.202.097-.068.012-.049-.109-.181-.9-1.626-.96-1.655-.428-.686-.113-.411a2 2 0 0 1-.068-.484l.496-.674L4.446 0l.662.089.279.242.411.94.666 1.48 1.033 2.014.302.597.162.553.06.17h.105v-.097l.085-1.134.157-1.392.154-1.792.052-.504.25-.605.497-.327.387.186.319.456-.045.294-.19 1.23-.37 1.93-.243 1.29h.142l.161-.16.654-.868 1.097-1.372.484-.545.565-.601.363-.287h.686l.505.751-.226.775-.707.895-.585.759-.839 1.13-.524.904.048.072.125-.012 1.897-.403 1.024-.186 1.223-.21.553.258.06.263-.218.536-1.307.323-1.533.307-2.284.54-.028.02.032.04 1.029.098.44.024h1.077l2.005.15.525.346.315.424-.053.323-.807.411-3.631-.863-.872-.218h-.12v.073l.726.71 1.331 1.202 1.667 1.55.084.383-.214.302-.226-.032-1.464-1.101-.565-.497-1.28-1.077h-.084v.113l.295.432 1.557 2.34.08.718-.112.234-.404.141-.444-.08-.911-1.28-.94-1.44-.759-1.291-.093.053-.448 4.821-.21.246-.484.186-.403-.307-.214-.496.214-.98.258-1.28.21-1.016.19-1.263.112-.42-.008-.028-.092.012-.953 1.307-1.448 1.957-1.146 1.227-.274.109-.477-.247.045-.44.266-.39 1.586-2.018.956-1.25.617-.723-.004-.105h-.036l-4.212 2.736-.75.096-.324-.302.04-.496.154-.162 1.267-.871z",
  openai: "M14.949 6.547a3.94 3.94 0 0 0-.348-3.273 4.11 4.11 0 0 0-4.4-1.934A4.1 4.1 0 0 0 8.423.2 4.15 4.15 0 0 0 6.305.086a4.1 4.1 0 0 0-1.891.948 4.04 4.04 0 0 0-1.158 1.753 4.1 4.1 0 0 0-1.563.679A4 4 0 0 0 .554 4.72a3.99 3.99 0 0 0 .502 4.731 3.94 3.94 0 0 0 .346 3.274 4.11 4.11 0 0 0 4.402 1.933c.382.425.852.764 1.377.995.526.231 1.095.35 1.67.346 1.78.002 3.358-1.132 3.901-2.804a4.1 4.1 0 0 0 1.563-.68 4 4 0 0 0 1.14-1.253 3.99 3.99 0 0 0-.506-4.716m-6.097 8.406a3.05 3.05 0 0 1-1.945-.694l.096-.054 3.23-1.838a.53.53 0 0 0 .265-.455v-4.49l1.366.778q.02.011.025.035v3.722c-.003 1.653-1.361 2.992-3.037 2.996m-6.53-2.75a2.95 2.95 0 0 1-.36-2.01l.095.057L5.29 12.09a.53.53 0 0 0 .527 0l3.949-2.246v1.555a.05.05 0 0 1-.022.041L6.473 13.3c-1.454.826-3.311.335-4.15-1.098m-.85-6.94A3.02 3.02 0 0 1 3.07 3.949v3.785a.51.51 0 0 0 .262.451l3.93 2.237-1.366.779a.05.05 0 0 1-.048 0L2.585 9.342a2.98 2.98 0 0 1-1.113-4.094zm11.216 2.571L8.747 5.576l1.362-.776a.05.05 0 0 1 .048 0l3.265 1.86a3 3 0 0 1 1.173 1.207 2.96 2.96 0 0 1-.27 3.2 3.05 3.05 0 0 1-1.36.997V8.279a.52.52 0 0 0-.276-.445m1.36-2.015-.097-.057-3.226-1.855a.53.53 0 0 0-.53 0L6.249 6.153V4.598a.04.04 0 0 1 .019-.04L9.533 2.7a3.07 3.07 0 0 1 3.257.139c.474.325.843.778 1.066 1.303.223.526.289 1.103.191 1.664zM5.503 8.575 4.139 7.8a.05.05 0 0 1-.026-.037V4.049c0-.57.166-1.127.476-1.607s.752-.864 1.275-1.105a3.08 3.08 0 0 1 3.234.41l-.096.054-3.23 1.838a.53.53 0 0 0-.265.455zm.742-1.577 1.758-1 1.762 1v2l-1.755 1-1.762-1z",
};

/* Geometry, as on the Design page: everything hangs on one centre, and the moving parts live in a small 3D space
   around it (x right, y down, z toward the viewer). The labels are a little larger here, for the back row. */
const RAD = Math.PI / 180;
function plane(inc, turn) { return { c: Math.cos(inc * RAD), s: Math.sin(inc * RAD), co: Math.cos(turn * RAD), so: Math.sin(turn * RAD) }; }
function geo() {
  const g = narrow.matches
    ? { w: 720, h: 660, cx: 360, cy: 284, rb: 100, rq: 200, rp: 274, rr: 338, fs: 25, fw: 20, D: 1900, sw: 50, over: 26, cmax: 23, mark: 21, pack: 1.01, fq: 18, chars: 16, age: 0, pp: [34, 0], pr: [36, -4] }
    : { w: 1140, h: 985, cx: 570, cy: 404, rb: 164, rq: 340, rp: 446, rr: 540, fs: 26, fw: 21, D: 2100, sw: 88, over: 45, cmax: 27, mark: 25, pack: 1.06, fq: 16.5, chars: 30, age: 1, pp: [40, 0], pr: [36, -4] };
  g.PP = plane(...g.pp); g.PR = plane(...g.pr); g.u = g.rb / 164;
  return g;
}
const pt = (g, r, a) => [g.cx + r * Math.cos(a * Math.PI / 180), g.cy + r * Math.sin(a * Math.PI / 180)];
const xy = p => `${f(p[0])} ${f(p[1])}`;
function angles(n) {
  if (n < 2) return [90];
  if (n === 2) return [150, 30];
  const first = n % 2 ? 90 : 90 + 180 / n;
  return Array.from({ length: n }, (_, k) => (first + k * 360 / n) % 360);
}
const arc = (g, r, a0, a1) => `M${xy(pt(g, r, a0))}A${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${xy(pt(g, r, a1))}`;
const spiral = (i, c) => [c * Math.sqrt(i + .6) * Math.cos(i * 2.39996), c * Math.sqrt(i + .6) * Math.sin(i * 2.39996)];

const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
S.t = 21;
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
const world = (P, u, v) => [u * P.co - v * P.c * P.so, u * P.so + v * P.c * P.co, v * P.s];
const onRing = (P, r, deg) => world(P, r * Math.cos(deg * RAD), r * Math.sin(deg * RAD));
function proj(g, p) {
  const x = p[0] * V.c1 + p[2] * V.s1, z1 = p[2] * V.c1 - p[0] * V.s1;
  const y = p[1] * V.c2 - z1 * V.s2, z = z1 * V.c2 + p[1] * V.s2, k = g.D / (g.D - z);
  return [g.cx + x * k, g.cy + y * k, k, z];
}
function ribbon(p, w) {
  const n = p.length, L = [], R = [], h = v => v.toFixed(2);
  for (let i = 0; i < n; i++) {
    const a = p[Math.max(0, i - 1)], c = p[Math.min(n - 1, i + 1)];
    const dx = c[0] - a[0], dy = c[1] - a[1], d = Math.hypot(dx, dy) || 1, half = w(p[i], i) / 2;
    L.push(h(p[i][0] - dy / d * half) + " " + h(p[i][1] + dx / d * half));
    R.push(h(p[i][0] + dy / d * half) + " " + h(p[i][1] - dx / d * half));
  }
  return "M" + L.join("L") + "L" + R.reverse().join("L") + "Z";
}

function model(d) {
  const all = [...d.items, ...d.messages];
  const people = [...new Set(all.map(r => r.who))].sort();
  const agents = people.map(p => [...new Set(all.filter(r => r.who === p && r.session).map(r => r.session))].sort().slice(0, 30));
  const product = s => {
    const a = (all.find(r => r.session === s && r.agent) || {}).agent || "";
    return a.startsWith("claude-code") ? "claude" : a.startsWith("codex") ? "openai" : "";
  };
  const live = d.items.filter(i => i.listed !== "work-closed").sort((a, c) => a.at_ns - c.at_ns);
  const of = k => live.filter(i => i.listed === k);
  const newest = l => [...l].sort((a, c) => c.at_ns - a.at_ns);
  const results = newest(of("result")), msgs = [...d.messages].reverse();
  const last = Math.max(0, ...d.items.map(i => Number(i.at_ns)), ...d.messages.map(msgNs));
  return {
    people, agents, marks: agents.map(l => l.map(product)), live, results, msgs, last, hours: d.hours,
    n: { result: results.length, work: of("work").length, idea: of("idea").length },
    nAgents: agents.reduce((s, a) => s + a.length, 0),
    lead: Math.max(0, people.indexOf(results[0]?.who)),
  };
}

/* The figures on the face of the board, one per step that shows one. Coordinates in face units: origin at the
   board's centre, y down, 164 = the board's radius. Every number is read from FACTS here. A text with data-max is
   shrunk to that width if the font makes it wider (fit()); data-t names the texts a step's cues turn on. */
const BAR = { y0: 78, full: 150, w: 58, xs: [-84, 0, 84] };
function tx(cls, x, y, size, body, o = {}) {
  return `<text class="${cls}${o.t ? " ft" + (o.rise ? " rise" : "") : ""}" x="${x}" y="${y}" font-size="${size}" data-fs="${size}"` +
    `${o.anchor ? ` style="text-anchor:${o.anchor}"` : ""}${o.t ? ` data-t="${o.t}"` : ""}${o.max ? ` data-max="${o.max}"` : ""}${o.id ? ` id="${o.id}"` : ""}>${body}</text>`;
}
const per = (n, size) => `${n}<tspan font-size="${f(size * .61)}">%</tspan>`;
function hourRows() {  // complete UTC hours only: the hour in which the count was read is partial
  const h = FACTS.results_per_hour_by_utc_hour, at = h && h.at ? String(h.at).slice(11, 13) : "";
  return (h && h.v ? h.v : []).filter(([hour]) => hour !== at);
}
function faceSVG() {
  const out = [];
  // Step 1: three names, the stops on the way from an idea to an answer.
  out.push(`<g class="fig" data-fig="stops">` +
    ["validates like a paper", "waits for a GPU", "repeats a run"].map((s, i) => tx("flab", 0, -36 + 44 * i, 24, s, { t: "stop" + i, rise: 1, max: 296 })).join("") + "</g>");
  // Step 3: results per hour.
  const hrs = hourRows(), nb = hrs.length, pitch = 234 / Math.max(1, nb), bw = pitch - 8, top = Math.max(1, ...hrs.map(r => r[1]));
  const sc = Math.min(4, 100 / top);
  out.push(`<g class="fig" data-fig="rate">` +
    tx("fnum", -116, -34, 60, nf(need("results_on_board")), { t: "rate-head", anchor: "start", id: "rate-hero" }) +
    tx("flab", 16, -58, 22, "results", { t: "rate-head", anchor: "start", id: "rate-l1" }) +
    tx("fsub", 16, -34, 22, `in ${nf(Math.round(need("board_hours")))} hours`, { t: "rate-head", anchor: "start", id: "rate-l2" }) +
    hrs.map(([, v], i) => `<rect class="fbar ${i === nb - 1 ? "f-blue" : "f-mute"}" data-rate="${i}" data-h="${f(v * sc)}" x="${f(-113 + pitch * i)}" y="84" width="${f(bw)}" height="0" rx="2"/>`).join("") +
    (nb ? tx("flab", f(-113 + pitch * (nb - 1) + bw / 2), f(84 - hrs[nb - 1][1] * sc - 8), 22, hrs[nb - 1][1], { t: "rate-late" }) +
      tx("fsub", -110, 104, 19, `${hrs[0][0]}:00`, { t: "rate-late", anchor: "start" }) + tx("fsub", 0, 104, 19, "per hour", { t: "rate-late" }) +
      tx("fsub", 110, 104, 19, `${hrs[nb - 1][0]}:00`, { t: "rate-late", anchor: "end" }) : "") + "</g>");
  // Steps 4 and 5: three bars, then the gap above the cue split in two. The slab is the same two rects in both steps.
  const vals = ["math500_base_plain", "math500_base_cue", "math500_rl"].map(k => need(k)), N = FACTS.math500_rl ? FACTS.math500_rl.n : 500;
  const H = vals.map(v => typeof v === "number" ? v / N * BAR.full : 0), share = (typeof fv("reliability_share_pct") === "number" ? fv("reliability_share_pct") : 50) / 100;
  const fills = ["f-faint", "f-blue", "f-mute"], names = ["base", "base + cue", "RL"], x0 = i => BAR.xs[i] - BAR.w / 2;
  const left = 245 * share, rd = need("math500_base_cue_redraws");
  out.push(`<g class="fig" data-fig="bars" id="fig-bars"><g class="bk">` +
    [0, 1].map(i => `<rect class="fbar ${fills[i]}" data-bar="${i}" x="${x0(i)}" y="${BAR.y0}" width="${BAR.w}" height="0" rx="2"/>`).join("") +
    `<rect class="fbar f-mute" data-bar="2" x="${x0(2)}" y="${BAR.y0}" width="${BAR.w}" height="0" rx="2"/>` +
    vals.map((v, i) => tx("fnum", BAR.xs[i], f(BAR.y0 - H[i] - 8), 36, per(pct(["math500_base_plain", "math500_base_cue", "math500_rl"][i]), 36), { t: "pct" + i })).join("") +
    vals.map((v, i) => tx("fcount" + (i === 1 ? " onblue" : i === 0 ? " onfaint" : ""), BAR.xs[i], BAR.y0 - 9, 16, nf(v), { t: "bars-late" })).join("") +
    names.map((s, i) => tx("flab", BAR.xs[i], BAR.y0 + 22, 16, s, { t: "bars-late" })).join("") +
    tx("fsub", 0, 122, 15, `of ${nf(N)} problems`, { t: "bars-late" }) + "</g>" +
    `<rect class="fbar f-mute sl-l" id="sl-l" x="0" y="0" width="0" height="0" rx="1"/><rect class="fbar f-mute sl-r" id="sl-r" x="0" y="0" width="0" height="0" rx="1"/>` +
    tx("fnum", -124, -36, 56, per(nf(need("reliability_share_pct")), 56), { t: "why-a", anchor: "start" }) +
    tx("fnum", 124, -36, 30, per(nf(need("new_problems_share_pct")), 30), { t: "why-b", anchor: "end" }) +
    tx("flab", -124, 42, 14, "problems the base", { t: "why-c", anchor: "start", max: 130 }) + tx("flab", -124, 60, 14, "sometimes solves", { t: "why-c", anchor: "start", max: 130 }) +
    tx("flab", 124, 42, 14, "problems it", { t: "why-c", anchor: "end", max: 100 }) + tx("flab", 124, 60, 14, "never solves", { t: "why-c", anchor: "end", max: 100 }) +
    tx("fsub", 0, -92, 15, "RL's gain over base + cue", { t: "why-d", max: 220 }) +
    tx("fsub", 0, 92, 15, `${nf(FACTS.reliability_share_pct ? FACTS.reliability_share_pct.n : "?")} problems, ${nf(need("anatomy_right_samples") === "?" ? "?" : FACTS.anatomy_right_samples.n / FACTS.reliability_share_pct.n)} samples each`, { t: "why-d", max: 240 }) +
    "</g>");
  // Under the disc, below bars 1 and 2: when they were measured.
  out.push(`<g class="fig" data-fig="bars-tag">` + tx("fsub", -113, 196, 16, "measured before the event;", { t: "bars-late", anchor: "start" }) +
    tx("fsub", -113, 216, 16, `re-measured during it: ${nf(rd === "?" ? "?" : rd.lo)} to ${nf(rd === "?" ? "?" : rd.hi)} of ${nf(FACTS.math500_base_cue_redraws ? FACTS.math500_base_cue_redraws.n : "?")}`, { t: "bars-late", anchor: "start" }) + "</g>");
  // Step 6: a gain and its second draw.
  const A = need("retraction_claim"), B = need("retraction_correction"), signed = v => typeof v === "number" ? (v < 0 ? "−" + Math.abs(v) : "+" + v) : v;
  out.push(`<g class="fig hue" data-fig="draw" id="fig-draw">` + tx("fsub", 0, -96, 15, "gain on MATH-500, in points", { max: 250 }) +
    `<circle class="dot fdot" data-t="rowA" cx="-120" cy="-40" r="10"/>` +
    tx("fnum", -98, -22, 54, signed(A.points), { t: "rowA", anchor: "start", id: "draw-a" }) +
    tx("flab", 28, -44, 15, "first draw", { t: "rowA", anchor: "start" }) + tx("fsub", 28, -25, 15, `${nf(A.right)} of ${nf(A.n)}`, { t: "rowA", anchor: "start" }) +
    `<path class="flink ft" data-t="rowB" d="M-120 -28L-120 28"/>` +
    `<circle class="dot fdot" data-t="rowB" cx="-120" cy="40" r="10"/>` +
    tx("fnum", -98, 58, 54, signed(B.points), { t: "rowB", anchor: "start" }) +
    tx("flab", 28, 36, 15, "second draw", { t: "rowB", anchor: "start" }) + tx("fsub", 28, 55, 15, `${nf(B.right)} of ${nf(B.n)}`, { t: "rowB", anchor: "start" }) +
    tx("fsub", 28, 74, 15, `${nf(need("retraction_minutes_between"))} min later`, { t: "rowB", anchor: "start" }) +
    `<path class="strike" data-t="strike" pathLength="1" d="M-102 -41L16 -41"/></g>`);
  // Steps 7 and 9: before and after, on one scale per figure.
  const ba = (name, pre, preNote, post, postNote, preV, postV, count, caption) => {
    const wPost = typeof preV === "number" && typeof postV === "number" ? 220 * postV / preV : 0;
    return `<g class="fig" data-fig="${name}">` +
      tx("fnum", -110, -64, 40, pre, { t: name + "-pre", anchor: "start" }) + tx("fsub", 110, -64, 22, preNote, { t: name + "-pre", anchor: "end" }) +
      `<rect class="fbar f-faint" data-pre="${name}" x="-110" y="-52" width="0" height="22" rx="2"/>` +
      tx("fnum", -110, 22, 40, post, { t: name + "-post", anchor: "start" }) + tx("fsub", 110, 22, 22, postNote, { t: name + "-post", anchor: "end" }) +
      Array.from({ length: count }, (_, i) => `<rect class="fbar f-blue" data-post="${name}" data-w="${f(wPost)}" x="-110" y="${count > 1 ? 34 + 17 * i : 34}" width="0" height="${count > 1 ? 12 : 22}" rx="2"/>`).join("") +
      (caption ? tx("fsub", 0, 92, 20, caption, { t: name + "-post", max: 250 }) : "") + "</g>";
  };
  const shards = need("shard_detail", "shards"), unit = (n, u) => `${nf(n)}<tspan class="flab" font-size="22"> ${u}</tspan>`;
  out.push(ba("shard", unit(need("shard_whole_minutes"), "min"), "1 H100", unit(need("shard_4_minutes"), "min"), `${nf(shards)} H100s`,
    fv("shard_whole_minutes"), fv("shard_4_minutes"), typeof shards === "number" ? shards : 1, ""));
  const before = need("h100_wait_before_min"), after = need("h100_wait_after_s");
  out.push(ba("wait", unit(before, "min"), `${nf(FACTS.h100_wait_before_min ? FACTS.h100_wait_before_min.n : "?")} jobs`, unit(after, "s"),
    `${nf(FACTS.h100_wait_after_s ? FACTS.h100_wait_after_s.n : "?")} jobs`, typeof before === "number" ? before * 60 : null, after, 1, "median wait for an H100"));
  // Step 8: what came back from Exa.
  const ex = need("exa_case_best"), title = String(ex.paper_title || "?").split(":")[0].split(" "), half = Math.ceil(title.length / 2);
  const url = String(ex.paper_url || "");
  out.push(`<g class="fig" data-fig="source">` + tx("fnum", 0, -34, 30, esc(title.slice(0, half).join(" ")), { t: "src", max: 290 }) +
    tx("fnum", 0, 0, 30, esc(title.slice(half).join(" ")), { t: "src", max: 290 }) +
    `<a href="${esc(url)}" target="_blank" rel="noopener">${tx("src-link", 0, 38, 22, esc(url.replace(/^https?:\/\//, "")), { t: "src", max: 290 })}</a></g>`);
  return out.join("");
}

/* The picture: the Design page's scene, with three additions: the camera group #cam (the only thing the view's move in
   changes), the face layer on the board, and the two points outside the lab. */
function draw() {
  const g = S.g = geo(), m = S.m, n = m ? m.people.length : 0, th = n ? angles(n) : [];
  const svg = $("svg"), hue = i => HUES[i % HUES.length];
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  const part = (name, go, body, label, extra = "") =>
    `<g class="part${extra}" data-part="${name}"${go ? ` data-go="${go}"` : ""}${label ? ` role="button" tabindex="0" aria-label="${label}"` : ""}>${body}</g>`;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  let defs = "<defs>" +
    `<radialGradient id="body" cx=".36" cy=".3" r=".86">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".12" y1=".08" x2=".9" y2=".94">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.6, "var(--ink)", .22)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<radialGradient id="glo-b">${stop(0, "var(--blue)", .6)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<linearGradient id="rvfade" gradientUnits="userSpaceOnUse">${stop(0, "var(--blue)", .4)}${stop(1, "var(--blue)", 1)}</linearGradient>` +
    `<linearGradient id="msgfade" gradientUnits="userSpaceOnUse">${stop(0, "var(--mute)", .5)}${stop(1, "var(--ink)", .95)}</linearGradient>` +
    `<clipPath id="faceclip"><circle cx="0" cy="0" r="161"/></clipPath>` +
    Object.keys(MARKS).map(k => `<symbol id="mark-${k}" viewBox="0 0 16 16"><path d="${MARKS[k]}"/></symbol>`).join("") +
    th.map((_, i) =>
      `<radialGradient id="orb-${i}" class="hue" style="--h:${hue(i)}" cx=".34" cy=".3" r=".8">${stop(0, "color-mix(in oklch, var(--c), white var(--lift))")}${stop(1, "var(--c)")}</radialGradient>` +
      `<radialGradient id="glo-${i}" class="hue" style="--h:${hue(i)}">${stop(0, "var(--c)", .55)}${stop(1, "var(--c)", 0)}</radialGradient>`).join("") +
    "</defs>";
  const pulse = i => `<g class="pulse" opacity="0"><circle class="bloom"${i == null ? "" : ` fill="url(#glo-${i})"`}/><path class="ptail"/>` +
    `<circle class="phead"${i == null ? "" : ` style="fill:url(#orb-${i}) var(--c)"`}/></g>`;

  let out = `<g class="part" data-part="board"><circle class="atmo" cx="${g.cx}" cy="${g.cy}" r="${g.rb * 2}" fill="url(#atmo)"/>` +
    `<circle class="shade" cx="${f(g.cx + g.rb * .07)}" cy="${f(g.cy + g.rb * .15)}" r="${f(g.rb * 1.22)}" fill="url(#shade)"/></g>`;
  const chevron = i => `<path class="chev" id="rv-c${i}" d="M-10 -8.5L5 0L-10 8.5"/>`;
  out += part("review", "retro",
    `<path class="hit" id="rv-hit" stroke-width="26"/><path class="rib ring" id="rv-rib"/>${chevron(0)}${chevron(1)}` +
    `<g class="comet" id="comet"><circle class="bloom" id="cm-glow" fill="url(#glo-b)"/><path class="comet-tail" id="cm-long" opacity=".3"/>` +
    `<path class="comet-tail" id="cm-short" opacity=".85"/><circle class="comet-core" id="cm-core"/></g>` +
    `<text class="label" id="rv-label" font-size="${g.fs}">Retro</text>`, "Retro");
  out += part("msg", "chat",
    `<path class="hit" id="ms-hit" stroke-width="22"/><path class="beads ring" id="ms-ring"/>` +
    `<g class="hue" id="ms-fx">${th.map(() => `<ellipse class="arrive" opacity="0"/>`).join("")}${pulse()}${pulse()}</g>` +
    `<text class="label" id="ms-label" font-size="${g.fs}">Chat</text>`, "Chat");
  th.forEach((a, i) => {
    out += part("thread-" + i, "", `<g class="hue" style="--h:${hue(i)}"><path class="thread"/><path class="ripple" opacity="0"/>` +
      `<circle class="tick" r="3.2"/><circle class="tick" r="3.2"/><circle class="tick" r="3.2"/>${pulse(i)}</g>`);
  });
  const top = g.rb + g.fs * .82, sx = g.cx - g.rb * .3, sy = g.cy - g.rb * .46;
  out += part("board", "board",
    `<circle class="board-ring ring draw" pathLength="1" cx="${g.cx}" cy="${g.cy}" r="${g.rb}"/>` +
    `<ellipse class="spec" cx="${f(sx)}" cy="${f(sy)}" rx="${f(g.rb * .56)}" ry="${f(g.rb * .34)}" transform="rotate(-34 ${f(sx)} ${f(sy)})" fill="url(#spec)"/>` +
    `<g id="dotwrap"><g id="dots"></g><g id="dotfx" class="hue"><circle class="arrive" opacity="0"/><circle class="arrive" opacity="0"/><circle class="arrive" opacity="0"/><circle class="nhalo"/></g></g>` +
    `<g id="face" clip-path="url(#faceclip)" transform="translate(${g.cx} ${g.cy}) scale(${g.u.toFixed(4)})">${faceSVG()}</g>` +
    `<path id="on-board" fill="none" stroke="none" d="${arc(g, top, -150, -30)}"/>` +
    `<text class="label plain" font-size="${g.fs}" dy="${f(g.fs * .34)}"><textPath href="#on-board" startOffset="50%">Board</textPath></text>`, "Board");
  th.forEach((a, i) => {
    out += part("swarm-" + i, "p-" + m.people[i],
      `<g class="hue" style="--h:${hue(i)}"><circle class="pad" r="${g.sw + 16}"/><path class="tie"/>` +
      m.marks[i].map((mark, k) => mark ? `<use class="agent" data-k="${k}" href="#mark-${mark}" style="--i:${k}"/>` : `<rect class="agent" data-k="${k}" style="--i:${k}"/>`).join("") +
      `<circle class="person ring" style="fill:url(#orb-${i}) var(--c)"/>` +
      `<text class="who" font-size="${g.fw}">${esc(m.people[i])}</text>` +
      `<text class="said" font-size="${g.fq}" opacity="0" aria-hidden="true"><tspan></tspan><tspan class="when"></tspan></text></g>`,
      `${esc(m.people[i])}, ${m.agents[i].length} agents`);
  });
  // The face's captions that sit below the disc (unclipped), in face units.
  out += `<g class="part" data-part="board-under"><g transform="translate(${g.cx} ${g.cy}) scale(${g.u.toFixed(4)})" id="face2"></g></g>`;
  const ext = (name, label, lanes) => part("ext-" + name, "ext-" + name,
    `<g class="hue xbody">${Array.from({ length: lanes }, () => `<path class="trace"/>`).join("")}${Array.from({ length: lanes }, () => pulse()).join("")}` +
    `<g class="xm"><circle class="pad" r="34"/><circle class="xring ring" r="9"/><circle class="xdot" r="2.6"/></g>` +
    `<text class="label" font-size="${g.fs}">${label}</text></g>`, label, " ext");
  out += ext("modal", "Modal", 4) + ext("exa", "Exa", 1);
  const k = g.fw * .92, ky = g.h - 14, keys = [["agent", "agent"], ["work", "open work"], ["", "result"], ["note", "idea or note"]];
  const here = m ? ["claude", "openai", ""].filter(x => m.marks.some(l => l.includes(x))) : ["claude"];
  const widths = keys.map(([cls, t]) => 26 + t.length * k * .54 + 22 + (cls === "agent" ? (here.length - 1) * 19 : 0)), total = widths.reduce((a, c) => a + c, 0) - 22;
  let kx = narrow.matches ? (g.w - total) / 2 : 6;
  out += `<g class="part key" data-part="key" style="--c:var(--mute)">` + keys.map(([cls, t], i) => {
    const x = kx, y = ky - k * .32; kx += widths[i];
    const one = (mark, j) => mark ? `<use class="agent" href="#mark-${mark}" x="${f(x - 1 + j * 19)}" y="${f(y - 8)}" width="16" height="16"/>`
      : `<rect class="agent" x="${f(x + j * 19)}" y="${f(y - 6.5)}" width="13" height="13" rx="3.6"/>`;
    return (cls === "agent" ? here.map(one).join("") : `<circle class="dot ${cls}" cx="${f(x + 7)}" cy="${f(y)}" r="${cls === "note" ? 3.4 : 6}"/>`) +
      `<text class="sub" x="${f(x + 20 + (cls === "agent" ? (here.length - 1) * 19 : 0))}" y="${f(ky)}" font-size="${f(k)}" style="text-anchor:start">${t}</text>`;
  }).join("") + "</g>";
  svg.innerHTML = defs + `<g id="cam">${out}<g id="fx"></g></g>`;
  // The tag under bars 1 and 2 lives in the unclipped layer; move it there.
  const tag = svg.querySelector('[data-fig="bars-tag"]');
  $("face2").append(tag);

  const el = {}, unit = e => ({ el: e, glow: e.children[0], tail: e.children[1], head: e.children[2] });
  ["rv-hit", "rv-rib", "rv-c0", "rv-c1", "comet", "cm-glow", "cm-long", "cm-short", "cm-core", "rv-label", "rvfade",
    "ms-hit", "ms-ring", "ms-label", "ms-fx", "msgfade", "cam", "dotwrap", "dotfx"].forEach(id => { el[id] = $(id); });
  const open = (name, r) => (name.length * g.fs * .33 + 16) / (r * RAD * .9);
  S.th = th;
  S.play = {};
  S.FV = {};
  S.cam = "";
  S.r = {
    el, gap: open("Retro", g.rr), mgap: open("Chat", g.rq),
    beads: Math.round(g.rq * 2 * Math.PI / 14),
    arrive: [...svg.querySelectorAll("#ms-fx .arrive")], legs: [...svg.querySelectorAll("#ms-fx .pulse")].map(unit),
    rings: [...svg.querySelectorAll("#dotfx .arrive")].map(e => ({ el: e, t0: -9 })), halo: svg.querySelector("#dotfx .nhalo"),
    figs: Object.fromEntries([...svg.querySelectorAll(".fig")].map(e => [e.dataset.fig, e])),
    ext: Object.fromEntries(["modal", "exa"].map(name => {
      const p = svg.querySelector(`[data-part="ext-${name}"]`);
      return [name, { el: p, body: p.querySelector(".xbody"), xm: p.querySelector(".xm"), dot: p.querySelector(".xdot"), label: p.querySelector(".label"),
        traces: [...p.querySelectorAll(".trace")], pulses: [...p.querySelectorAll(".pulse")].map(unit) }];
    })),
    swarms: th.map((a, i) => {
      const p = svg.querySelector(`[data-part="swarm-${i}"]`), t = svg.querySelector(`[data-part="thread-${i}"]`), count = m.agents[i].length;
      const c = Math.min(g.cmax, g.sw / Math.sqrt(count + .6)), who = p.querySelector(".who");
      return { a, c, size: Math.min(g.mark, c / g.pack), below: Math.sin(a * RAD) >= 0, side: Math.abs(Math.cos(a * RAD)) > .3 ? Math.sign(Math.cos(a * RAD)) : 0,
        wide: who.getComputedTextLength(), part: p, pad: p.querySelector(".pad"), tie: p.querySelector(".tie"), dots: [...p.querySelectorAll(".agent")],
        person: p.querySelector(".person"), who, said: p.querySelector(".said"), thread: t.querySelector(".thread"), ripple: t.querySelector(".ripple"),
        ticks: [...t.querySelectorAll(".tick")], pulse: unit(t.querySelector(".pulse")) };
    }),
  };
  fit();
  place(S.t);
  if (m && !S.entered) {
    S.entered = true;
    if (S.n === 0 && !S.panel) {
      svg.classList.add("enter");
      setTimeout(() => svg.classList.remove("enter"), 2600);
    }
  }
}

/* Fit inside the disc: a text wider than its data-max shrinks by the ratio, so a changed label or a fallback font
   cannot cross the rim. The block of the hero count of step 3 is centred once its width is known. */
function fit() {
  const svg = $("svg");
  svg.querySelectorAll("text[data-max]").forEach(t => {
    t.setAttribute("font-size", t.dataset.fs);
    const w = t.getComputedTextLength(), max = Number(t.dataset.max);
    if (w > max) t.setAttribute("font-size", (Number(t.dataset.fs) * max / w).toFixed(2));
  });
  const hero = $("rate-hero"), l1 = $("rate-l1"), l2 = $("rate-l2");
  if (hero && l1 && l2) {
    const hw = hero.getComputedTextLength(), lw = Math.max(l1.getComputedTextLength(), l2.getComputedTextLength()), x = -(hw + 16 + lw) / 2;
    hero.setAttribute("x", f(x)); l1.setAttribute("x", f(x + hw + 16)); l2.setAttribute("x", f(x + hw + 16));
  }
}

function dots() {
  const g = S.g, m = S.m, n = m.live.length, R = g.rb - 16, c = Math.min(15, R / Math.sqrt(n + 1));
  const capA = 62 * RAD, K = 1 - Math.cos(capA), Rs = R / Math.sin(capA);
  $("dots").innerHTML = m.live.map((it, i) => {
    const [dx, dy] = spiral(i, c), big = it.listed === "result" || it.listed === "work";
    const u = Math.min(1, Math.hypot(dx, dy) / R), tilt = Math.acos(1 - u * u * K), q = u ? Rs * Math.sin(tilt) / (u * R) : 1;
    const stale = it.listed === "work" && mins(it.active_ns ?? it.at_ns) >= 60;
    const cls = ["dot hue", it.listed === "work" ? "work" : big ? "" : "note", stale && "stale", S.seen && !S.seen.has(it.id) && "arrived"];
    return `<circle class="${cls.filter(Boolean).join(" ")}" style="--h:${HUES[Math.max(0, m.people.indexOf(it.who)) % HUES.length]};--i:${i}" ` +
      `data-who="${esc(it.who)}" data-id="${esc(it.id)}" cx="${f(g.cx + dx * q)}" cy="${f(g.cy + dy * q)}" r="${f(c * (big ? .4 : .27) * (.62 + .5 * Math.cos(tilt)))}"><title>${esc(it.id)}: ${esc(it.text.slice(0, 120))}</title></circle>`;
  }).join("");
  halo();
}

/* Motion that is always on (Design): agents circle in their swarm, a comet runs the Retro loop, the board turns
   slowly, and the whole view sways by a few degrees. */
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
function place(t) {
  const g = S.g, R = S.r;
  if (!R) return;
  const E = R.el, set = (el, o) => { for (const k in o) el.setAttribute(k, o[k]); };
  const at = (P, r, deg) => proj(g, onRing(P, r, deg));
  const ring = (P, r, a0, a1, n) => Array.from({ length: n + 1 }, (_, i) => at(P, r, a0 + (a1 - a0) * i / n));
  const line = p => "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L");
  const near = (P, r, q) => Math.min(1, Math.max(0, .5 + q[3] / (2 * r * P.s)));
  const fade = (grad, P, r) => { const a = at(P, r, -90), c = at(P, r, 90); set(grad, { x1: f(a[0]), y1: f(a[1]), x2: f(c[0]), y2: f(c[1]) }); };

  const loop = ring(g.PR, g.rr, -90 + R.gap, 270 - R.gap, 100);
  E["rv-rib"].setAttribute("d", ribbon(loop, q => 1 + 2.3 * near(g.PR, g.rr, q)));
  E["rv-hit"].setAttribute("d", line(loop) + "Z");
  fade(E.rvfade, g.PR, g.rr);
  [60, 240].forEach((a, i) => {
    const p = at(g.PR, g.rr, a), p0 = at(g.PR, g.rr, a - 2), p1 = at(g.PR, g.rr, a + 2);
    E["rv-c" + i].setAttribute("transform", `translate(${f(p[0])} ${f(p[1])}) rotate(${f(Math.atan2(p1[1] - p0[1], p1[0] - p0[0]) / RAD)}) scale(${(.5 + .65 * near(g.PR, g.rr, p)).toFixed(2)})`);
  });
  const ca = t * 20 + val("comet.extra"), head = at(g.PR, g.rr, ca), cn = near(g.PR, g.rr, head), cw = 2.4 + 4.4 * cn;
  E["cm-long"].setAttribute("d", ribbon(ring(g.PR, g.rr, ca - 52, ca, 16), (q, i) => cw * i / 16));
  E["cm-short"].setAttribute("d", ribbon(ring(g.PR, g.rr, ca - 14, ca, 6), (q, i) => cw * (.3 + .7 * i / 6)));
  set(E["cm-core"], { cx: f(head[0]), cy: f(head[1]), r: f(cw * .6) });
  set(E["cm-glow"], { cx: f(head[0]), cy: f(head[1]), r: f(cw * 4.4) });
  E.comet.setAttribute("opacity", (.5 + .5 * cn).toFixed(2));
  const apex = at(g.PR, g.rr, -90);
  set(E["rv-label"], { x: f(apex[0]), y: f(apex[1] + g.fs * .34) });

  let dash = "";
  for (let j = 0, step = 360 / R.beads; j < R.beads; j++) {
    const a = j * step - t * 1.5;
    if (Math.abs((((a + 90) % 360) + 540) % 360 - 180) < R.mgap) continue;
    const p = at(g.PP, g.rq, a - step * .21), q = at(g.PP, g.rq, a + step * .21);
    dash += `M${f(p[0])} ${f(p[1])}L${f(q[0])} ${f(q[1])}`;
  }
  E["ms-ring"].setAttribute("d", dash);
  E["ms-hit"].setAttribute("d", line(ring(g.PP, g.rq, 0, 360, 48)) + "Z");
  fade(E.msgfade, g.PP, g.rq);
  const crown = at(g.PP, g.rq, -90);
  set(E["ms-label"], { x: f(crown[0]), y: f(crown[1] + g.fs * .34) });

  const Y = S.play.say;
  R.swarms.forEach((o, n) => {
    const u0 = g.rq * Math.cos(o.a * RAD), v0 = g.rq * Math.sin(o.a * RAD);
    const c = proj(g, world(g.PP, u0, v0)), p = at(g.PP, g.rp, o.a), to_ = Math.atan2(c[1] - g.cy, c[0] - g.cx);
    const end = [g.cx + (g.rb + 2) * Math.cos(to_), g.cy + (g.rb + 2) * Math.sin(to_)], ends = f(end[0]) + " " + f(end[1]);
    let web = o.dots.length ? "" : `M${f(c[0])} ${f(c[1])}L${ends}`, fan = o.dots.length ? "" : `M${ends}L${f(c[0])} ${f(c[1])}`;
    o.c0 = c; o.end = end; o.at = []; o.reach = Math.hypot(c[0] - end[0], c[1] - end[1]);
    o.dots.forEach((d, k) => {
      const r = o.c * Math.sqrt(k + .6), a = k * 2.39996 + t * .22;
      const q = proj(g, world(g.PP, u0 + r * Math.cos(a), v0 + r * Math.sin(a))), here = f(q[0]) + " " + f(q[1]);
      const swell = Y && Y.i === n && Y.k === k ? 1 + .8 * Math.sin(Math.PI * Math.min(1, (t - Y.t0) / .7)) : 1;
      const side = o.size * q[2] * (d.tagName === "rect" ? .78 : 1) * swell;
      set(d, { x: f(q[0] - side / 2), y: f(q[1] - side / 2), width: f(side), height: f(side), rx: f(side * .28) });
      web += `M${here}L${ends}`;
      fan += `M${ends}L${here}`;
      o.at.push(q);
      o.reach = Math.max(o.reach, Math.hypot(q[0] - end[0], q[1] - end[1]));
    });
    o.fan = fan;
    o.thread.setAttribute("d", web);
    set(o.pad, { cx: f(c[0]), cy: f(c[1]) });
    o.tie.setAttribute("d", `M${f(c[0])} ${f(c[1])}L${f(p[0])} ${f(p[1])}`);
    set(o.person, { cx: f(p[0]), cy: f(p[1]), r: f(13 * p[2]) });
    o.nx = p[0] - o.side * Math.max(0, o.wide / 2 - g.over); o.ny = p[1] + (o.below ? g.fw * 1.9 : -g.fw * 1.15) * p[2]; o.nk = p[2];
    set(o.who, { x: f(o.nx), y: f(o.ny) });
  });
  E.dotwrap.setAttribute("transform", `rotate(${f(t * 1.5 % 360)} ${g.cx} ${g.cy})`);
  posted(t);
  sent(t, at, ring, near);
  said(t);
}

/* The replay (Design): about every 2.5 s one real event from the newest 40, looped. It runs only in the steps whose
   record says so (S.replay "on"); "fast" plays real posts only, one every 450 ms, in step 2. */
S.play = {}; S.due = 25; S.turn = false; S.nth = { msg: 0, post: 0 }; S.busy = false;
function comet(u, pts, r, opacity) {
  const n = pts.length - 1, h = pts[n];
  u.head.setAttribute("cx", f(h[0])); u.head.setAttribute("cy", f(h[1])); u.head.setAttribute("r", f(r));
  u.glow.setAttribute("cx", f(h[0])); u.glow.setAttribute("cy", f(h[1])); u.glow.setAttribute("r", f(r * 3.6));
  u.tail.setAttribute("d", n ? ribbon(pts, (q, i) => r * 1.5 * i / n) : "");
  u.el.setAttribute("opacity", opacity.toFixed(2));
}
function say(i, k, text, ns, t, hold) {
  const o = S.r.swarms[i], g = S.g, s = String(text ?? "").replace(/\s+/g, " ").trim();
  if (!o || !s) return;
  S.r.swarms.forEach(x => x.said.setAttribute("opacity", 0));
  const head = s.slice(0, g.chars), whole = head.replace(/\s+\S*$/, "");
  const cut = s.length > g.chars ? (whole.length * 2 > g.chars ? whole : head).replace(/[,;:(\-]+$/, "") + "…" : s;
  const [ln, wh] = o.said.children, age = g.age ? " " + ago(ns) : "";
  ln.textContent = cut; wh.textContent = age;
  wh.setAttribute("class", "when" + (mins(ns) < 1 ? " now" : ""));
  S.play.say = { i, k, cut, age, t0: t, hold, wide: o.said.getComputedTextLength(), n: -1 };
}
function said(t) {
  const Y = S.play.say, g = S.g;
  if (!Y) return;
  const o = S.r.swarms[Y.i], age = t - Y.t0;
  if (!o || age >= Y.hold) { if (o) o.said.setAttribute("opacity", 0); S.play.say = null; return; }
  const n = Math.min(Y.cut.length, Math.ceil(age * 55)), [ln, wh] = o.said.children;
  if (n !== Y.n) { Y.n = n; ln.textContent = Y.cut.slice(0, n); wh.textContent = n < Y.cut.length ? "" : Y.age; }
  const x = o.side < 0 ? o.nx - o.wide / 2 : o.side > 0 ? o.nx + o.wide / 2 - Y.wide : o.nx - Y.wide / 2;
  o.said.setAttribute("x", f(Math.max(8, Math.min(g.w - 8 - Y.wide, x))));
  o.said.setAttribute("y", f(o.ny + (o.below ? g.fq * 1.45 : -g.fw * 1.08) * o.nk));
  o.said.setAttribute("opacity", Math.max(0, Math.min(1, age / .15, (Y.hold - age) / .4)).toFixed(2));
}
function hush() {  // stop every travel where it is: the replay, the fast posts, the rings on the board
  const R = S.r;
  S.play = {}; S.fast = []; S.busy = false;
  if (!R) return;
  R.swarms.forEach(o => { o.pulse.el.setAttribute("opacity", 0); o.ripple.setAttribute("opacity", 0); o.said.setAttribute("opacity", 0); });
  R.legs.forEach(u => u.el.setAttribute("opacity", 0));
  R.arrive.forEach(e => e.setAttribute("opacity", 0));
  R.rings.forEach(r => { r.t0 = -9; r.el.setAttribute("opacity", 0); });
  Object.values(R.ext).forEach(x => x.pulses.forEach(u => u.el.setAttribute("opacity", 0)));
}
function beat(t) {
  const m = S.m;
  if (!m || !S.r || t < S.due || S.busy || S.replay !== "on") return;
  S.due = t + 2.5;
  const now = S.queue.shift();
  if (now) {
    const i = m.people.indexOf(now.who);
    if (i < 0) return;
    S.busy = true;
    const ms = now.kind === "msg" ? 2600 : 1100, token = S.token;
    say(i, m.agents[i].indexOf(now.session), now.text, now.ns, t, ms / 1000 + 1.3);
    fly(route(S.g, now.kind, S.th[i]), HUES[i % HUES.length], ms).then(() => {
      if (token !== S.token) return;
      S.busy = false; S.due = S.t + 1.5;
      if (now.kind === "board" && S.replay === "on") S.play.post = { i, k: -1, at: -1, t0: S.t - 1 };
    });
    return;
  }
  const msgs = S.data.messages.slice(-40).filter(x => m.people.includes(x.who)), posts = m.live.slice(-40);
  S.turn = !S.turn;
  if (S.turn && m.people.length > 1 && msgs.length) {
    const x = msgs[msgs.length - 1 - S.nth.msg++ % msgs.length], i = m.people.indexOf(x.who), a0 = S.th[i];
    const away = S.th.map((a, j) => ({ j, d: ((a - a0) % 360 + 360) % 360 })).filter(y => y.j !== i);
    const reach = dir => Math.max(0, ...away.map(y => dir > 0 ? y.d : 360 - y.d).filter(d => d <= 180 && (dir > 0 || d < 180)));
    S.play.msg = { i, t0: t, legs: [1, -1].map(dir => ({ dir, span: reach(dir), time: .9 + reach(dir) / 110 })),
      hits: away.map(y => y.d <= 180 ? { j: y.j, dir: 1, d: y.d, t: 0 } : { j: y.j, dir: -1, d: 360 - y.d, t: 0 }) };
    say(i, m.agents[i].indexOf(x.session), x.text, msgNs(x), t, Math.max(...S.play.msg.legs.map(l => l.time)) + .6);
    S.r.el["ms-fx"].setAttribute("style", `--h:${HUES[i % HUES.length]}`);
    S.r.legs.forEach(u => { u.glow.setAttribute("fill", `url(#glo-${i})`); u.head.setAttribute("style", `fill:url(#orb-${i}) var(--c)`); });
  } else if (posts.length) {
    const it = posts[posts.length - 1 - S.nth.post++ % posts.length], i = Math.max(0, m.people.indexOf(it.who)), count = m.agents[i].length;
    const k = count ? (m.agents[i].indexOf(it.session) + count) % count : -1;
    S.play.post = { i, k, at: m.live.indexOf(it), t0: t };
    if (m.people.includes(it.who)) say(i, m.agents[i].indexOf(it.session), it.text, it.at_ns, t, 2.4);
  }
}
function fastBeat(t) {  // step 2: real posts, one every 450 ms, each from another swarm than the last when there is one
  const m = S.m;
  if (!m || !S.r || S.replay !== "fast") return;
  const posts = m.live.slice(-40);
  if (S.fastLeft > 0 && t >= S.fastDue && posts.length) {
    S.fastDue = t + .45; S.fastLeft--;
    let it = null;
    for (let j = 0; j < posts.length; j++) {
      const c = posts[posts.length - 1 - (S.nth.post + j) % posts.length];
      if (c.who !== S.lastWho || j === posts.length - 1) { it = c; S.nth.post += j + 1; break; }
    }
    const i = m.people.indexOf(it.who);
    if (i >= 0) {
      S.lastWho = it.who;
      const count = m.agents[i].length, k = count ? (m.agents[i].indexOf(it.session) + count) % count : -1;
      S.fast = S.fast.filter(x => x.i !== i);
      S.fast.push({ i, k, at: m.live.indexOf(it), t0: t, scored: S.scored.has(it.id) });
    }
  }
  if ((S.fastLeft <= 0 || !posts.length) && !S.fast.length) { S.replay = "on"; S.due = t + 1; }
}
function fastFrame(t) {
  const R = S.r;
  if (!R) return;
  S.fast = S.fast.filter(P => {
    const o = R.swarms[P.i], age = (t - P.t0) / .6;
    if (!o) return false;
    const r = 3.8 * o.c0[2];
    if (age < 1) {
      const from = o.at[P.k] || o.c0, on = q => [from[0] + (o.end[0] - from[0]) * q, from[1] + (o.end[1] - from[1]) * q], e = ease(age);
      comet(o.pulse, [on(Math.max(0, e - .24)), on(Math.max(0, e - .12)), on(e)], r, Math.min(1, age / .12));
      return true;
    }
    o.pulse.el.setAttribute("opacity", 0);
    const dot = P.at < 0 ? null : $("dots").children[P.at];
    if (dot) { ping(dot); if (P.scored) ringAt(dot, HUES[P.i % HUES.length], t); }
    return false;
  });
  R.rings.forEach(x => {  // a ring opens around a result that has a score row
    const q = (t - x.t0) / .7;
    if (q < 0 || q >= 1) { if (x.shown) { x.el.setAttribute("opacity", 0); x.shown = false; } return; }
    x.shown = true;
    x.el.setAttribute("r", f(x.r0 + (16 - x.r0) * (1 - (1 - q) ** 3)));
    x.el.setAttribute("opacity", (.8 * (1 - q)).toFixed(2));
  });
}
function ringAt(dot, hue, t) {
  const R = S.r, x = R.rings.reduce((a, c) => c.t0 < a.t0 ? c : a);
  x.t0 = t; x.r0 = Number(dot.getAttribute("r"));
  x.el.setAttribute("cx", dot.getAttribute("cx")); x.el.setAttribute("cy", dot.getAttribute("cy"));
  x.el.setAttribute("style", `--h:${hue}`);
}
const ping = el => { el.classList.remove("ping"); el.getBBox(); el.classList.add("ping"); };
function posted(t) {
  const P = S.play.post, R = S.r;
  if (!P || !R.swarms[P.i]) return;
  const o = R.swarms[P.i], age = t - P.t0, r = 3.8 * o.c0[2];
  if (age < 0) return;
  if (age < 1) {
    const from = o.at[P.k] || o.c0, on = q => [from[0] + (o.end[0] - from[0]) * q, from[1] + (o.end[1] - from[1]) * q], e = ease(age);
    return comet(o.pulse, [on(Math.max(0, e - .24)), on(Math.max(0, e - .12)), on(e)], r, Math.min(1, age / .12));
  }
  if (P.quiet) { o.pulse.el.setAttribute("opacity", 0); S.play.post = null; return; }  // a post with no read after it
  if (!P.landed) {
    P.landed = true;
    const dot = P.at < 0 ? null : $("dots").children[P.at];
    if (dot) ping(dot);
    R.swarms.forEach(s => s.ripple.setAttribute("style", `--h:${HUES[P.i % HUES.length]}`));
  }
  const q = (age - 1) / 1.3, flash = Math.min(1, (age - 1) / .35);
  comet(o.pulse, [o.end], r * (1 - flash), 1 - flash);
  if (q >= 1) { R.swarms.forEach(s => s.ripple.setAttribute("opacity", 0)); S.play.post = null; return; }
  R.swarms.forEach((s, j) => {
    if (P.only != null && j !== P.only) return;
    const seg = s.reach * .22;
    s.ripple.setAttribute("d", s.fan);
    s.ripple.setAttribute("stroke-dasharray", `${f(seg)} 9999`);
    s.ripple.setAttribute("stroke-dashoffset", f(seg - ease(q) * (s.reach + seg)));
    s.ripple.setAttribute("opacity", (.75 * Math.min(1, 4 * q, 2.5 * (1 - q))).toFixed(2));
  });
}
function sent(t, at, ring, near) {
  const P = S.play.msg, R = S.r, g = S.g;
  if (!P || !R.swarms[P.i]) return;
  const a0 = S.th[P.i], age = t - P.t0;
  let live = false;
  P.legs.forEach((leg, n) => {
    const u = R.legs[n], q = age / leg.time;
    if (!leg.span || q >= 1) return u.el.setAttribute("opacity", 0);
    live = true;
    const gone = leg.span * ease(q), a = a0 + leg.dir * gone, p = at(g.PP, g.rq, a), d = near(g.PP, g.rq, p);
    comet(u, ring(g.PP, g.rq, a - leg.dir * Math.min(20, gone), a, 8), 3.4 + 3.2 * d, Math.min(1, q / .08, (1 - q) / .1) * (.6 + .4 * d));
    P.hits.forEach(h => { if (!h.t && h.dir === leg.dir && gone >= h.d - 1) h.t = t; });
  });
  P.hits.forEach(h => {
    const e = R.arrive[h.j], o = R.swarms[h.j], q = h.t ? (t - h.t) / .9 : 2;
    if (q >= 1) return e.setAttribute("opacity", 0);
    live = true;
    const r = (12 + (g.sw + 10) * (1 - (1 - q) ** 2)) * o.c0[2];
    e.setAttribute("cx", f(o.c0[0])); e.setAttribute("cy", f(o.c0[1])); e.setAttribute("rx", f(r)); e.setAttribute("ry", f(r * g.PP.c));
    e.setAttribute("opacity", (.8 * (1 - q)).toFixed(2));
  });
  if (!live) S.play.msg = null;
}
function route(g, kind, a) {
  const loop = (P, r, a0) => Array.from({ length: 91 }, (_, i) => onRing(P, r, a0 + i * 4));
  const home = onRing(g.PP, g.rq, a), s = proj(g, home), sa = Math.atan2(s[1] - g.cy, s[0] - g.cx) / RAD;
  if (kind === "board") return [home, pt(g, g.rb + 3, sa)];
  return loop(g.PP, g.rq, a);
}
function fly(points, hue, ms) {  // an event that happens now: a larger dot with a halo
  return new Promise(done => {
    if (still.matches || !points.length) return done();
    const token = S.token, fx = $("fx"), NS = "http://www.w3.org/2000/svg";
    const at = p => p.length > 2 ? proj(S.g, p) : [p[0], p[1], 1, 1];
    const first = points.map(at), len = [0];
    for (let i = 1; i < first.length; i++) len.push(len[i - 1] + Math.hypot(first[i][0] - first[i - 1][0], first[i][1] - first[i - 1][1]));
    const el = document.createElementNS(NS, "g");
    el.setAttribute("class", "hue");
    el.setAttribute("style", `--h:${hue}`);
    el.innerHTML = '<circle class="halo" r="17"/><circle class="fly" r="9"/>';
    fx.append(el);
    const t0 = performance.now();
    const tick = now => {
      if (token !== S.token || !el.isConnected) { el.remove(); return done(); }
      const p = Math.min(1, (now - t0) / ms), e = p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, along = e * len[len.length - 1];
      let i = 1;
      while (i < len.length - 1 && len[i] < along) i++;
      const k = (along - len[i - 1]) / ((len[i] - len[i - 1]) || 1), a = at(points[i - 1]), c = at(points[i]), mix = j => a[j] + (c[j] - a[j]) * k;
      const x = mix(0), y = mix(1), hidden = mix(3) < 0 && Math.hypot(x - S.g.cx, y - S.g.cy) < S.g.rb;
      el.setAttribute("transform", `translate(${f(x)} ${f(y)}) scale(${mix(2).toFixed(3)})`);
      el.setAttribute("opacity", hidden ? .1 : 1);
      if (p < 1) requestAnimationFrame(tick); else { el.remove(); done(); }
    };
    requestAnimationFrame(tick);
  });
}

/* The engine. Every visible change is a tween toward a target, so a key press at any moment retargets from where
   things are. A step entered by Next plays its cues; entered any other way it runs them all at once (S.instant). */
const T = {};
const io = p => p < .5 ? 4 * p * p * p : 1 - (-2 * p + 2) ** 3 / 2;
const out = p => 1 - (1 - p) ** 3;
function val(n, now = performance.now()) {
  const w = T[n];
  if (!w) return 0;
  if (!w.ms) return w.b;
  const p = Math.min(1, Math.max(0, (now - w.t0) / w.ms));
  return w.a + (w.b - w.a) * w.e(p);
}
function to(n, b, ms, delay = 0, e = io, always = false) {
  const now = performance.now(), quick = (S.instant && !always) || still.matches;
  T[n] = { a: val(n, now), b, t0: now + (quick ? 0 : delay), ms: quick ? 0 : ms, e };
  kick();
}
const put = (n, b) => { T[n] = { a: b, b, t0: 0, ms: 0, e: io }; };
const FACE = () => $("face");
const ft = (tag, on = true) => document.querySelectorAll(`#svg [data-t="${tag}"]`).forEach(e => e.classList.toggle("on", on));
const travel = () => !S.instant && !still.matches;  // a cue may start a travel only in a forward entry

function setFace(name) {
  S.face = name;
  const R = S.r;
  if (!R) return;
  Object.entries(R.figs).forEach(([k, e]) => e.classList.toggle("on", k === name || (k === "bars-tag" && name === "bars" && S.n === 4)));
  R.el.dotwrap.classList.toggle("off", name !== "dots");
  kick();
}
function ticks(on, j) { const o = S.r && S.r.swarms[S.actor]; if (o) o.ticks.forEach((e, i) => { if (j == null || i === j) e.classList.toggle("on", on); }); }
function allTicksOff() { if (S.r) S.r.swarms.forEach(o => o.ticks.forEach(e => e.classList.remove("on"))); }
function extTraces(name, on) { if (S.r) S.r.ext[name].traces.forEach(e => e.classList.toggle("on", on)); }
function halo(on) {
  const R = S.r;
  if (!R) return;
  if (on != null) S.halo = on;
  const it = S.m && S.m.results[0], dot = it ? $("dots").querySelector(`[data-id="${CSS.escape(it.id)}"]`) : null;
  R.halo.classList.toggle("on", !!S.halo && !!dot);
  if (dot) { R.halo.setAttribute("cx", dot.getAttribute("cx")); R.halo.setAttribute("cy", dot.getAttribute("cy")); R.halo.setAttribute("r", f(Number(dot.getAttribute("r")) + 5)); }
  return dot;
}

/* The twelve steps. sec: the section word; lit(A): the parts that stay lit (A = the actor's swarm), null for all;
   face: the board's face; cam: the framing; replay: whether real events play; ext: the outside point; who: the actor;
   reset(): the state before the cues; cues: [ms after the key press, what happens]; more: the detail rows. */
const all = (k, m) => (m ? m.people : []).map((_, i) => k + i);
const STEPS = [
  { hash: "nanolab", sec: "Nanolab", title: "Nanolab", cam: "wide", lit: null, face: "dots", replay: "on",
    say: m => `Nanolab is ${b(m ? m.people.length : need("people"))} people and their coding agents working on one research question.`,
    fact: () => "The question: how much of a published RL gain does an untrained base model reach with no training?" },
  { hash: "problem", sec: "Problem", title: "Problem", cam: "wide", lit: A => ["board", "thread-" + A, "swarm-" + A], solo: true, face: "stops", replay: "off",
    say: () => "Research output is set by cycle time: how fast an idea becomes an answer.",
    fact: () => `In our first hours one run took ${b(nf(need("day1_cell_minutes")))} minutes on one GPU, and agents generated it ${b(nf(need("day1_cell_repeats")))} times.` + tail(["day1_cell_minutes"]),
    more: [["problem/day1", "Our first hours, measured"]],
    reset() { S.crawl = true; put("crawl", 0); allTicksOff(); [0, 1, 2].forEach(i => ft("stop" + i, false)); },
    cues: [[600, () => to("crawl", .25, 1100)], [1700, () => { ticks(true, 0); ft("stop0"); }], [3200, () => to("crawl", .5, 1100)],
      [4300, () => { ticks(true, 1); ft("stop1"); }], [5800, () => to("crawl", .75, 1100)], [6900, () => { ticks(true, 2); ft("stop2"); }]] },
  { hash: "claim", sec: "Claim", title: "Claim", cam: "wide", lit: null, face: "dots", replay: "off",
    say: () => "Nanolab makes agents fail fast, so most ideas get an answer within the hour.",
    fact: () => "Only what shows a signal gets the careful validation.",
    cues: [[0, () => { if (travel() && S.crawl) to("crawl", 1, 350); else crawlOff(); }], [200, () => allTicksOff()],
      [600, () => { if (travel()) { S.replay = "fast"; S.fastLeft = 12; S.fastDue = S.t; } else S.replay = "on"; }]] },
  { hash: "proof", sec: "Proof", title: "Proof", cam: "wide", lit: null, face: "rate", replay: "off",
    say: m => { const p = m ? m.people.length : need("people"); return `<span class="seq">${cap(word(p))} people and their agents posted ${b(nf(need("results_on_board")), 0)} results in ${b(nf(Math.round(need("board_hours"))), 1)} hours.</span>`; },
    fact: () => `Median ${b(nf(need("claim_to_close_median_min")))} minutes from claiming an idea to its result, over ${b(nf(FACTS.claim_to_close_median_min ? FACTS.claim_to_close_median_min.n : "?"))} work items.` + tail(["results_on_board", "claim_to_close_median_min"]),
    open: () => "Against one agent on the same budget: not measured yet.",
    more: [["proof/turnaround", "From claim to result"]],
    reset() { ft("rate-head", false); ft("rate-late", false); put("f.rate", 0); },
    cues: [[300, () => ft("rate-head")], [500, () => to("f.rate", 1, 1400, 0, out)], [1900, () => ft("rate-late")]] },
  { hash: "result", sec: "Proof", title: "Result", cam: "near", lit: () => ["board", "board-under"], face: "bars", replay: "off",
    say: () => `With no training, a ${word(FACTS.cue_text ? FACTS.cue_text.n : "?")}-token cue takes the base model from ${b(pct("math500_base_plain") + "%")} to ${b(pct("math500_base_cue") + "%")} on MATH-500.`,
    fact: () => `The RL-trained model scores ${b(pct("math500_rl") + "%")} (${nf(FACTS.math500_rl ? FACTS.math500_rl.n : "?")} problems, one sample each, same sampling). We measured this before the event; during it the swarm confirmed it on ${nf(FACTS.hard328_base_cue ? FACTS.hard328_base_cue.n : "?")} harder problems: ${pct("hard328_base_plain")}% to ${pct("hard328_base_cue")}%, RL ${pct("hard328_rl")}%.` + tail(["math500_base_cue", "math500_rl", "hard328_base_cue"]),
    more: [["result/cue", "The cue"], ["result/harder", "Harder problems and code"], ["result/vote", "Under a vote"]],
    reset() { $("fig-bars") && $("fig-bars").classList.remove("why"); ["pct0", "pct1", "pct2", "bars-late", "why-a", "why-b", "why-c", "why-d"].forEach(t => ft(t, false)); put("f.bars", 0); put("f.why", 0); S.FV = {}; },
    cues: [[350, () => to("f.bars", 1, 820, 0, out)], [1250, () => ft("bars-late")]] },
  { hash: "why", sec: "Proof", title: "Why", cam: "near", lit: () => ["board"], face: "bars", replay: "off",
    say: () => "RL mostly makes the model reliable on problems it could already solve.",
    fact: () => { const n = FACTS.reliability_share_pct ? FACTS.reliability_share_pct.n : "?", k = FACTS.anatomy_right_samples && typeof n === "number" ? FACTS.anatomy_right_samples.n / n : "?";
      return `${b(nf(need("reliability_share_pct")) + "%")} of the gap that the cue leaves is on problems the base solves in at least 1 of ${k} samples (${nf(n)} problems, ${k} samples each).` + tail(["reliability_share_pct"]); },
    more: [["why/control", "How we know"], ["why/findings", "Other findings"]],
    reset() { ["why-a", "why-b", "why-c", "why-d"].forEach(t => ft(t, false)); to("f.bars", 1, 300); ["pct0", "pct1", "pct2", "bars-late"].forEach(t => ft(t)); },
    cues: [[0, () => { $("fig-bars") && $("fig-bars").classList.add("why"); to("f.why", 1, 700, 150); }], [850, () => ft("why-a")], [1000, () => ft("why-b")], [1050, () => ft("why-c")], [1100, () => ft("why-d")]] },
  { hash: "rules", sec: "How", title: "Speed rules", cam: "near", lit: A => ["board", "thread-" + A, "swarm-" + A], face: "draw", replay: "off", who: () => fv("retraction_who"),
    say: () => "A cheap test comes first, and only a result that stands out is validated.",
    fact: () => { const a = need("retraction_claim"); return `A gain of ${b("+" + nf(a.points))} points failed its own second draw ${b(nf(need("retraction_minutes_between")))} minutes later, and the agent retracted it.` + tail(["retraction_claim", "retraction_correction"]); },
    more: [["rules/thread", "The thread"], ["rules/audit", "The audit of our chart"], ["rules/rejected", "What the swarm rejected"]],
    reset() { ["rowA", "rowB", "strike"].forEach(t => ft(t, false)); $("draw-a") && $("draw-a").classList.remove("mutedtext"); },
    cues: [[300, () => ft("rowA")], [1500, () => { if (travel() && S.actor >= 0) S.play.post = { i: S.actor, k: -1, at: -1, t0: S.t, quiet: true }; }],
      [2500, () => ft("rowB")], [2650, () => { ft("strike"); $("draw-a") && $("draw-a").classList.add("mutedtext"); }]] },
  { hash: "infra", sec: "How", title: "Infrastructure", cam: "wide", lit: A => ["board", "swarm-" + A, "ext-modal"], face: "shard", ext: "modal", replay: "off", who: () => fv("exa_case_best") && fv("exa_case_best").who,
    say: () => `Agents start their own Modal GPU jobs: ${b(nf(need("gpu_submit_commands")))} launches, ${fv("gpu_submit_by_person_shell") === 0 ? "none" : nf(need("gpu_submit_by_person_shell"))} typed by a person.`,
    fact: () => { const d = need("shard_detail"), extra = typeof d.gpu_min_shard4 === "number" ? Math.round(100 * (d.gpu_min_shard4 / d.gpu_min_whole - 1)) : "?";
      return `Splitting one run across ${nf(need("shard_detail", "shards"))} GPUs cut it from ${b(nf(need("shard_whole_minutes")))} to ${b(nf(need("shard_4_minutes")))} minutes (measured once each way, ${extra}% more GPU minutes).` + tail(["gpu_submit_commands", "shard_4_minutes"]); },
    more: [["infra/modal", "On Modal"]],
    reset() { ft("shard-pre", false); ft("shard-post", false); put("f.shardPre", 0); put("f.shard", 0); put("lane.modal", 0); extTraces("modal", false); },
    cues: [[300, () => { ft("shard-pre"); to("f.shardPre", 1, 500, 0, out); }], [1000, () => to("lane.modal", 1, 900)],
      [1900, () => { if (travel() && S.r) ping(S.r.ext.modal.dot); to("f.shard", 1, 500, 0, out); }], [2200, () => to("lane.modal", 2, 800)],
      [2400, () => ft("shard-post")], [3000, () => extTraces("modal", true)]] },
  { hash: "brain", sec: "How", title: "Shared brain", cam: "wide", lit: (A, m) => ["board", ...all("thread-", m), ...all("swarm-", m), "ext-exa"], face: "dots", ext: "exa", replay: "off", who: () => fv("exa_case_best") && fv("exa_case_best").who,
    say: () => "Agents see what everyone has tried and found, and build on it.",
    fact: () => `One Exa search found published tables that closed ${b(word(need("exa_case_best", "method_families")))} planned methods with ${need("exa_case_best", "gpu_jobs") === 0 ? "no GPU job" : nf(need("exa_case_best", "gpu_jobs")) + " GPU jobs"}.` + tail(["exa_case_best"]),
    more: [["brain/sources", "Sources"], ["brain/memory", "Shared memory"]],
    reset() { ft("src", false); put("lane.exa", 0); extTraces("exa", false); },
    cues: [[400, () => { if (travel() && S.actor >= 0) S.play.post = { i: S.actor, k: -1, at: -1, t0: S.t - 1 }; }],
      [2100, () => to("lane.exa", 1, 900)], [3000, () => { if (travel() && S.r) ping(S.r.ext.exa.dot); }], [3200, () => to("lane.exa", 2, 900)],
      [4100, () => { if (travel() && S.actor >= 0) S.play.post = { i: S.actor, k: 0, at: -1, t0: S.t, quiet: true }; }],
      [5100, () => { setFace("source"); ft("src"); extTraces("exa", true); }]] },
  { hash: "retro", sec: "How", title: "Retro", cam: "wide", lit: () => ["review", "board"], face: "wait", replay: "off",
    say: () => "The lab times itself and fixes its slowest step.",
    fact: () => `One review raised the container limit from ${nf(need("max_containers_change", "from"))} to ${nf(need("max_containers_change", "to"))}, and the median wait for an H100 fell from ${b(nf(need("h100_wait_before_min")))} minutes to ${b(nf(need("h100_wait_after_s")))} seconds (${nf(FACTS.h100_wait_before_min ? FACTS.h100_wait_before_min.n : "?")} jobs before, ${nf(FACTS.h100_wait_after_s ? FACTS.h100_wait_after_s.n : "?")} after).` + tail(["max_containers_change", "h100_wait_after_s"]),
    more: [["retro/changes", "What the reviews changed"]],
    reset() { ft("wait-pre", false); ft("wait-post", false); put("f.waitPre", 0); put("f.wait", 0); },
    cues: [[300, () => { ft("wait-pre"); to("f.waitPre", 1, 500, 0, out); }], [600, () => { if (travel()) to("comet.extra", val("comet.extra") + 360, 3200); }],
      [3800, () => to("f.wait", 1, 500, 0, out)], [4300, () => ft("wait-post")]] },
  { hash: "watch", sec: "How", title: "Live", cam: "wide", lit: null, face: "dots", replay: "on", button: true,
    say: () => "People watch the research evolve live on this site.",
    fact: m => { const it = m && m.results[0]; if (!it) return null; const s = String(it.text).replace(/\s+/g, " ").trim(), cut = s.length > 120 ? s.slice(0, 120).replace(/\s+\S*$/, "") + "…" : s;
      return `Newest result: <a href="/#${esc(it.id)}">${esc(cut)}</a>, <span class="who-c hue" style="--h:${hueOf(it.who) ?? 0}">${esc(it.who)}</span>, ${ago(it.at_ns)}.`; },
    reset() { halo(false); S.due = S.t; },
    cues: [[600, () => { const dot = halo(true); if (dot && travel()) ping(dot); }]] },
  { hash: "close", sec: "Summary", title: "Summary", cam: "wide", lit: null, face: "dots", replay: "on",
    say: () => "Nanolab makes agents fail fast, so most ideas get an answer within the hour.",
    recap: () => [
      ["proof", `Speed: ${b(nf(need("results_on_board")))} results in ${b(nf(Math.round(need("board_hours"))))} hours, median ${b(nf(need("claim_to_close_median_min")))} minutes from claim to result.`],
      ["result", `Result: the cue's gain holds on ${nf(FACTS.hard328_base_cue ? FACTS.hard328_base_cue.n : "?")} harder problems and on code, and a vote takes the base to ${b(pct("vote4_restart_base") + "%")} (RL ${pct("vote4_restart_rl")}%).`],
      ["why", `Reason: ${b(nf(need("reliability_share_pct")) + "%")} of the remaining gap is reliability.`]],
    url: "monitor.invariant.team" },
];
const HASH = Object.fromEntries(STEPS.map((s, i) => [s.hash, i]));
const SECTION_START = new Set([0, 1, 2, 3, 6, 11]);

function crawlOff() { S.crawl = false; const o = S.r && S.r.swarms[S.actor]; if (o) o.pulse.el.setAttribute("opacity", 0); }
function actorOf(n) {
  const m = S.m;
  if (!m) return -1;
  const who = STEPS[n].who ? STEPS[n].who() : null, i = who ? m.people.indexOf(who) : -1;
  return i >= 0 ? i : m.lead;
}

/* Entering a step: stop every travel, set the step's state, then play its cues (Next) or run them all at once. */
function enter(n, forward) {
  S.token++; hush(); S.cues = []; S.t0 = performance.now();
  const prev = S.n;
  S.n = n;
  const st = STEPS[n];
  S.actor = actorOf(n);
  if (n !== 1 && n !== 2) crawlOff();
  if (n === 2 && !(forward && prev === 1)) crawlOff();
  if (n !== 2) allTicksOff();
  if (n !== 10) halo(false);
  S.replay = st.replay;
  if (S.r) {  // the actor's colour on the parts that take it
    const h = S.actor >= 0 ? HUES[S.actor % HUES.length] : 0;
    Object.values(S.r.ext).forEach(x => {
      x.body.setAttribute("style", `--h:${h}`);
      x.pulses.forEach(u => { u.glow.setAttribute("fill", `url(#glo-${S.actor})`); u.head.setAttribute("style", `fill:url(#orb-${S.actor}) var(--c)`); });
    });
    const d = $("fig-draw"); if (d) d.setAttribute("style", `--h:${h}`);
  }
  setFace(st.face);
  extTraces("modal", false); extTraces("exa", false);
  S.instant = true; if (st.reset) st.reset(); S.instant = false;
  camera(n);
  const list = st.cues || [];
  if (forward && !still.matches) S.cues = list.map(([at, fn]) => ({ at, fn, done: false }));
  else { S.instant = true; list.forEach(([, fn]) => fn()); S.instant = false; }
  show(true);
  kick();
}
function camera(n) {
  const g = S.g, wantNear = STEPS[n].cam === "near" || (narrow.matches && STEPS[n].face !== "dots");
  S.camWant = wantNear ? "near" : "wide";
  const ms = 450;
  to("cam.z", wantNear ? (narrow.matches ? 3.1 : 1.6) : 1, STEPS[n].cam === "near" && n === 4 ? 700 : n === 7 ? 700 : ms, 0, io, true);
  to("cam.oy", wantNear ? g.h / 2 - g.cy : 0, n === 4 || n === 7 ? 700 : ms, 0, io, true);
}

/* Per frame: the camera, the cue clock, the figures that grow, the crawl of step 1, the lanes to Modal and Exa. */
function paint(now) {
  const g = S.g, R = S.r;
  for (const c of S.cues) if (!c.done && now - S.t0 >= c.at) { c.done = true; c.fn(); }
  if (S.replay === "fast") { fastBeat(S.t); }
  if (R) {
    const z = val("cam.z", now), oy = val("cam.oy", now), key = z.toFixed(4) + "|" + oy.toFixed(2);
    if (key !== S.cam) { S.cam = key; R.el.cam.setAttribute("transform", `translate(${f(g.cx * (1 - z))} ${f(g.cy * (1 - z) + oy)}) scale(${z.toFixed(4)})`); }
    $("stage").classList.toggle("near", S.camWant === "near" || z > 1.001);
  }
  place(S.t);
  fastFrame(S.t);
  crawl(now);
  lanes(now);
  figures(now);
}
function crawl(now) {
  if (!S.crawl || !S.r) return;
  const o = S.r.swarms[S.actor];
  if (!o) return;
  const v = val("crawl", now), from = o.at[0] || o.c0, on = q => [from[0] + (o.end[0] - from[0]) * q, from[1] + (o.end[1] - from[1]) * q];
  o.ticks.forEach((e, i) => { const p = on((i + 1) * .25); e.setAttribute("cx", f(p[0])); e.setAttribute("cy", f(p[1])); });
  if (S.n === 2 && v >= 1) {  // the pulse that stopped in step 1 lands, and the newest result answers
    crawlOff();
    const dot = halo(); if (dot) ping(dot);
    return;
  }
  comet(o.pulse, [on(Math.max(0, v - .07)), on(Math.max(0, v - .035)), on(v)], 3.8 * o.c0[2], 1);
}
function lanes(now) {
  const R = S.r, g = S.g;
  if (!R) return;
  ["modal", "exa"].forEach(name => {
    if (!S.ext.has(name)) return;
    const X = R.ext[name], o = R.swarms[S.actor];
    const side = o ? (o.c0[0] >= g.cx ? 1 : -1) : 1, p = proj(g, [side * 506 * g.u, (name === "exa" ? -340 : 330) * g.u, 0]);
    X.xm.setAttribute("transform", `translate(${f(p[0])} ${f(p[1])}) scale(${p[2].toFixed(3)})`);
    X.label.setAttribute("x", f(p[0])); X.label.setAttribute("y", f(p[1] + 30 + g.fs * .34));
    if (!o) return;
    const M = o.at[0] || o.c0, dx = p[0] - M[0], dy = p[1] - M[1], d = Math.hypot(dx, dy) || 1, nx = -dy / d, ny = dx / d;
    const v = val("lane." + name, now), offs = name === "modal" ? [-24, -8, 8, 24] : [0];
    offs.forEach((off, j) => {
      const C = [(M[0] + p[0]) / 2 + nx * off, (M[1] + p[1]) / 2 + ny * off];
      const B = s => [(1 - s) * (1 - s) * M[0] + 2 * (1 - s) * s * C[0] + s * s * p[0], (1 - s) * (1 - s) * M[1] + 2 * (1 - s) * s * C[1] + s * s * p[1]];
      X.traces[j].setAttribute("d", `M${f(M[0])} ${f(M[1])}Q${f(C[0])} ${f(C[1])} ${f(p[0])} ${f(p[1])}`);
      const u = X.pulses[j];
      if (v <= 0 || v >= 2) { if (u.el.getAttribute("opacity") !== "0") u.el.setAttribute("opacity", 0); return; }
      const s = v <= 1 ? io(v) : 1 - io(v - 1), dir = v <= 1 ? 1 : -1;
      comet(u, [B(Math.min(1, Math.max(0, s - dir * .08))), B(Math.min(1, Math.max(0, s - dir * .04))), B(s)], 4.2, 1);
    });
  });
}
function figures(now) {
  const R = S.r, F = S.FV;
  if (!R) return;
  const fig = S.face, svg = $("svg");
  if (fig === "rate") {
    const v = val("f.rate", now);
    if (v !== F.rate) {
      F.rate = v;
      const bars = svg.querySelectorAll("[data-rate]"), nb = bars.length, step = nb > 1 ? .64 / (nb - 1) : 0;
      bars.forEach((r, i) => { const p = Math.min(1, Math.max(0, (v - i * step) / .36)), h = Number(r.dataset.h) * p; r.setAttribute("y", f(84 - h)); r.setAttribute("height", f(h)); });
    }
  }
  if (fig === "bars") {
    const bv = val("f.bars", now), wv = val("f.why", now), key = bv.toFixed(4) + "|" + wv.toFixed(4);
    if (key !== F.bars) {
      F.bars = key;
      const N = FACTS.math500_rl ? FACTS.math500_rl.n : 500, H = ["math500_base_plain", "math500_base_cue", "math500_rl"].map(k => (typeof fv(k) === "number" ? fv(k) : 0) / N * BAR.full);
      const p = [Math.min(1, bv / .6), Math.min(1, Math.max(0, (bv - .2) / .6)), Math.min(1, Math.max(0, (bv - .4) / .6))];
      const rects = svg.querySelectorAll("[data-bar]");
      [0, 1].forEach(i => { const h = H[i] * p[i]; rects[i].setAttribute("y", f(BAR.y0 - h)); rects[i].setAttribute("height", f(h)); });
      const hh = H[2] * p[2], body = Math.min(hh, H[1]), sh = Math.max(0, hh - H[1]);
      rects[2].setAttribute("y", f(BAR.y0 - body)); rects[2].setAttribute("height", f(body));
      const share = (typeof fv("reliability_share_pct") === "number" ? fv("reliability_share_pct") : 50) / 100, x3 = BAR.xs[2] - BAR.w / 2;
      const ov = sh > 0 ? .8 : 0, Lw = 245 * share, from = [[x3, BAR.y0 - hh, BAR.w * share + ov, sh + ov], [x3 + BAR.w * share, BAR.y0 - hh, BAR.w * (1 - share), sh + ov]];  // overlap a hair, so no seam shows while they look like one bar
      const dest = [[-124, -22, Lw, 44], [-124 + Lw + 3, -22, 245 - Lw, 44]];
      [$("sl-l"), $("sl-r")].forEach((r, j) => {
        const a = from[j], c = dest[j], mix = q => a[q] + (c[q] - a[q]) * wv;
        r.setAttribute("x", f(mix(0))); r.setAttribute("y", f(mix(1))); r.setAttribute("width", f(mix(2))); r.setAttribute("height", f(mix(3)));
      });
      p.forEach((q, i) => { if ((F["pct" + i] || false) !== q >= 1) { F["pct" + i] = q >= 1; ft("pct" + i, q >= 1); } });
    }
  }
  if (fig === "shard" || fig === "wait") {
    const pre = val("f." + fig + "Pre", now), post = val("f." + fig, now), key = fig + pre.toFixed(4) + "|" + post.toFixed(4);
    if (key !== F.ba) {
      F.ba = key;
      svg.querySelectorAll(`[data-pre="${fig}"]`).forEach(r => r.setAttribute("width", f(220 * pre)));
      svg.querySelectorAll(`[data-post="${fig}"]`).forEach(r => r.setAttribute("width", f(Number(r.dataset.w) * post)));
    }
  }
}
function frame(now) {
  S.t = 21 + now / 1000;
  V.px += (V.tx - V.px) * .06;
  V.py += (V.ty - V.py) * .06;
  aim(6 * Math.sin((S.t - 21) * .13) + 5 * V.px, 2.5 * Math.sin((S.t - 21) * .09) - 2.5 * V.py);
  beat(S.t);
  paint(now);
  requestAnimationFrame(frame);
}
function kick() {  // with reduced motion nothing runs per frame: draw the one still frame of the new state
  if (!still.matches || S.kicked) return;
  S.kicked = true;
  queueMicrotask(() => { S.kicked = false; paint(performance.now()); });
}

/* Selection: the step and its open detail, mirrored in the address (#result, #result/cue). */
const LAB = ["board", "chat", "retro"];
function panelOf(n, d) {
  if (!d) return null;
  const key = STEPS[n].hash + "/" + d;
  if (PANELS[key]) return key;
  if (LAB.includes(d)) return d;
  if (d.startsWith("p-") && (!S.m || S.m.people.includes(d.slice(2)))) return d;
  return null;
}
function parse() {
  const s = decodeURIComponent(location.hash.slice(1)), [h, ...rest] = s.split("/"), n = h in HASH ? HASH[h] : 0;
  return { n, panel: panelOf(n, rest.join("/")) };
}
function url(n, panel) {
  const d = panel ? (panel.includes("/") ? panel.split("/").slice(1).join("/") : panel) : "";
  return "#" + STEPS[n].hash + (d ? "/" + encodeURIComponent(d).replace(/%2F/g, "/") : "");
}
function fromHash(forward) {
  const p = parse(), stepChanged = p.n !== S.n || !S.started, panelChanged = p.panel !== S.panel;
  S.started = true;
  S.panel = p.panel;
  if (stepChanged) enter(p.n, !!forward);
  else if (panelChanged) show(true);
  if (panelChanged && S.panel) { const h = document.querySelector(".dhead h2"); if (h) h.focus({ preventScroll: true }); }
  if (panelChanged && !S.panel && S.opener && S.opener.isConnected) { S.opener.focus({ preventScroll: true }); S.opener = null; }
}
function go(n, panel, forward) {
  n = Math.max(0, Math.min(STEPS.length - 1, n));
  const target = url(n, panel);
  if (target !== location.hash) history.pushState(null, "", target);
  fromHash(forward);
}
function next() { if (S.n < STEPS.length - 1) go(S.n + 1, null, true); }
function prev() { if (S.panel) return go(S.n, null); if (S.n > 0) go(S.n - 1, null); }
function openPanel(key, from) {
  if (key === S.panel) return go(S.n, null);
  S.opener = from || null;
  go(S.n, key);
}
function resolve(target) {  // what a click on a part of the picture opens in this step
  const st = STEPS[S.n], first = (st.more || []).map(r => r[0]).find(k => PANELS[k]);
  if (target === "board" && S.face !== "dots") return first || "board";
  if (target === "retro" && S.n === 9 && PANELS["retro/changes"]) return "retro/changes";
  if (target === "ext-modal") return PANELS["infra/modal"] ? "infra/modal" : null;
  if (target === "ext-exa") return PANELS["brain/sources"] ? "brain/sources" : null;
  return target;
}

/* What stays lit: the open panel's parts, else the step's. A panel's symbols are resolved here. */
function litNow() {
  const m = S.m, A = S.actor, st = STEPS[S.n], k = S.panel;
  if (k) {
    if (k === "board") return ["board", "key", ...all("thread-", m)];
    if (k === "chat") return ["msg", ...all("swarm-", m)];
    if (k === "retro") return ["review"];
    if (k.startsWith("p-")) { const i = m ? m.people.indexOf(k.slice(2)) : -1; return ["swarm-" + i, "thread-" + i, "board"]; }
    const P = PANELS[k];
    if (P && Array.isArray(P.lit)) {
      return P.lit.flatMap(s => {
        if (s === "board") return ["board", "board-under"];
        if (s === "chat") return ["msg"];
        if (s === "retro") return ["review"];
        if (s === "all-swarms") return all("swarm-", m);
        if (s === "all-threads") return all("thread-", m);
        if (s === "actor") return ["swarm-" + A, "thread-" + A];
        if (s === "ext-exa" || s === "ext-modal") return [s];
        if (s.startsWith("p:")) { const i = m ? m.people.indexOf(s.slice(2)) : -1; return ["swarm-" + i, "thread-" + i]; }
        return [];
      });
    }
  }
  return st.lit ? st.lit(A, m) : null;
}
function show(changed) {
  const svg = $("svg"), on = litNow(), st = STEPS[S.n];
  svg.classList.toggle("has-focus", !!on);
  svg.querySelectorAll(".part").forEach(p => p.classList.toggle("on", !!on && on.includes(p.dataset.part)));
  const solo = st.solo && !S.panel;
  if (S.r) S.r.swarms.forEach((o, i) => o.part.classList.toggle("solo", !!solo && i === S.actor));
  S.ext = new Set([st.ext, ...(on || []).filter(p => p.startsWith("ext-")).map(p => p.slice(4))].filter(Boolean));
  if (S.r) Object.entries(S.r.ext).forEach(([name, x]) => {
    x.el.classList.toggle("show", S.ext.has(name));
    if (S.ext.has(name) && name !== st.ext) extTraces(name, true);
  });
  words(changed);
  const title = S.n === 0 ? "Invariant: Nanolab" : `Nanolab: ${st.title}`, P = S.panel ? panelName(S.panel) : "";
  document.title = title + (P ? ", " + P : "");
  clock();
  kick();
}
function panelName(k) {
  if (TEXT[k]) return TEXT[k].name;
  if (k.startsWith("p-")) return k.slice(2);
  return PANELS[k] ? PANELS[k].name : "";
}

/* The words column. */
function rows(title, list, m) {
  if (!list || !list.length) return "";
  return `<div class="rows"><h3>${esc(title)}</h3>` + list.slice(0, 2).map(r => {
    const id = r.id || "", ns = r.id ? r.at_ns : msgNs(r), h = HUES[Math.max(0, m.people.indexOf(r.who)) % HUES.length];
    return `<a class="hue" style="--h:${h}" href="/${id ? "#" + id : ""}"><span class="t">${esc(r.text)}</span><span class="m"><b>${esc(r.who)}</b> ${ago(ns)}</span></a>`;
  }).join("") + "</div>";
}
function labPanel(k) {
  const m = S.m;
  if (k.startsWith("p-")) {
    const who = k.slice(2), i = m ? m.people.indexOf(who) : -1, mine = m ? m.live.filter(r => r.who === who).sort((a, c) => c.at_ns - a.at_ns) : [];
    const branches = S.data ? new Set(S.data.items.filter(r => r.who === who && r.branch).map(r => r.branch)).size : 0;
    const pp = fv("per_person") && fv("per_person")[who];
    return { name: who, hue: i < 0 ? null : HUES[i % HUES.length],
      html: (m ? `<p class="lead">${m.agents[i].length} agent sessions on ${branches} git ${branches === 1 ? "branch" : "branches"}, all posting to one board.</p>` : "") +
        (pp ? `<ul class="facts"><li>${nf(pp.agent_sessions)} agent sessions, ${nf(pp.results)} results, ${nf(pp.gpu_jobs)} GPU jobs in all (${when(FACTS.per_person.at)}).</li></ul>` : "") +
        (m ? rows(`${mine.length} items on the board`, mine, m) : "") };
  }
  const t = TEXT[k], r = t.rows && m ? t.rows(m) : null;
  return { name: t.name, html: `<p class="lead">${t.lead}</p><ul class="facts">${t.facts.map(x => `<li>${x}</li>`).join("")}</ul>` + (r ? rows(r.title, r.list, m) : "") };
}
function panelHTML() {
  const k = S.panel, lab = !PANELS[k] || LAB.includes(k) || k.startsWith("p-");
  const p = lab ? labPanel(k) : { name: PANELS[k].name, html: PANELS[k].html(FACTS, S.m) };
  return `<div class="dhead"><h2 tabindex="-1"${p.hue == null ? "" : ` class="hue" style="--h:${p.hue}"`}>${esc(p.name)}</h2><button class="close" data-close>Close</button></div>` +
    `<div class="dbody">${p.html}</div>`;
}
function storyHTML() {
  const st = STEPS[S.n], m = S.m, fact = st.fact ? st.fact(m) : null;
  let h = `<p class="say">${st.say(m)}</p>`;
  if (fact) h += `<p class="fact">${fact}</p>`;
  if (st.open) h += `<p class="open">${st.open()}</p>`;
  if (st.recap) h += `<ul class="recap">${st.recap().map(([hash, s]) => `<li><a href="#${hash}" data-jump="${HASH[hash]}">${s}</a></li>`).join("")}</ul>`;
  if (st.url) h += `<a class="url" href="/">${st.url}</a>`;
  if (st.button) h += `<div><a class="walk" href="/">Open the board</a></div>`;
  const more = (st.more || []).filter(([k]) => PANELS[k]);
  if (more.length) h += `<div class="more">${more.map(([k, label], i) => `<button class="q" style="--i:${i}" data-open="${k}">${esc(PANELS[k].name || label)}<span aria-hidden="true">›</span></button>`).join("")}</div>`;
  return h;
}
function words(changed) {
  const pane = $("pane"), st = STEPS[S.n], html = S.panel ? panelHTML() : storyHTML();
  if (html !== S.paneHTML) {
    pane.classList.toggle("quiet", !changed);
    pane.innerHTML = html; S.paneHTML = html;
    if (changed) pane.scrollTop = 0;
  }
  $("sec").textContent = st.sec;
  $("count").textContent = `${S.n + 1} of ${STEPS.length}`;
  $("steps").querySelectorAll("a").forEach((a, i) => {
    a.classList.toggle("done", i < S.n);
    if (i === S.n) a.setAttribute("aria-current", "step"); else a.removeAttribute("aria-current");
  });
  $("back").disabled = S.n === 0 && !S.panel;
  $("next").disabled = S.n === STEPS.length - 1;
  $("next").classList.toggle("plain", !!st.button && !S.panel);
  $("hint").textContent = S.n === 0 && !S.panel ? "or use the arrow keys" : "";
}
function clock() {
  const m = S.m;
  $("status").classList.toggle("bad", !!S.error);
  $("status").textContent = S.error ? (S.readAt ? `Offline, last read ${new Date(S.readAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : "Offline")
    : S.data ? (m.last && !narrow.matches ? `Live, last post ${since(m.last)}` : "Live") : "Reading the board";
}

function read(d) {
  S.data = d; S.m = model(d);
  S.scored = new Set((d.scores || []).map(s => s.result));
  const key = narrow.matches + "|" + S.m.people.map((p, i) => p + ":" + S.m.agents[i].length + ":" + S.m.marks[i].join("")).join(",");
  const redraw = key !== S.key;
  if (redraw) { S.key = key; draw(); }
  dots();
  if (S.seen) {
    d.items.filter(i => i.listed !== "work-closed" && !S.seen.has(i.id)).forEach(i => S.queue.push({ kind: "board", who: i.who, session: i.session, text: i.text, ns: i.at_ns }));
    d.messages.filter(x => !S.seen.has(x.sk)).forEach(x => S.queue.push({ kind: "msg", who: x.who, session: x.session, text: x.text, ns: msgNs(x) }));
    S.queue = S.queue.slice(-8);
  }
  S.seen = new Set([...d.items.map(i => i.id), ...d.messages.map(x => x.sk)]);
  if (redraw) enter(S.n, false); else show(false);
}
function poll() {
  fetch("/data").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(d => { S.error = null; S.readAt = Date.now(); read(d); const s = $("status"); s.classList.remove("read"); s.offsetWidth; s.classList.add("read"); })
    .catch(e => { S.error = e; console.error(e); clock(); })
    .finally(() => setTimeout(poll, 10000));
}

/* Keys and clicks. A held key does not run through the steps; Space on a button or link activates it instead. */
document.addEventListener("click", e => {
  const pointer = e.detail > 0;
  const seg = e.target.closest("#steps a");
  if (seg) { e.preventDefault(); const n = Number(seg.dataset.n); if (pointer) seg.blur(); return n === S.n && !S.panel ? enter(n, true) : go(n, null); }
  const jump = e.target.closest("[data-jump]");
  if (jump) { e.preventDefault(); return go(Number(jump.dataset.jump), null); }
  const nav = e.target.closest("[data-step]");
  if (nav) { if (pointer) nav.blur(); return Number(nav.dataset.step) > 0 ? next() : prev(); }
  if (e.target.closest("[data-close]")) return go(S.n, null);
  const q = e.target.closest("[data-open]");
  if (q) return openPanel(q.dataset.open, q);
  if (e.target.closest("a")) return;
  const t = e.target.closest("svg [data-go]");
  if (t) {
    e.preventDefault();
    if (pointer) document.activeElement?.blur?.();
    const k = resolve(t.dataset.go);
    if (k && (PANELS[k] || LAB.includes(k) || k.startsWith("p-"))) openPanel(k, t);
    return;
  }
  if (e.target.closest("#stage") && S.panel) go(S.n, null);  // a click on empty scene closes the detail
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key, onControl = e.target.closest?.("button, a, [role=button], input, textarea, select");
  const part = e.target.closest?.("svg [data-go]");
  if (part && (k === "Enter" || k === " ")) { e.preventDefault(); const r = resolve(part.dataset.go); if (r && (PANELS[r] || LAB.includes(r) || r.startsWith("p-"))) openPanel(r, part); return; }
  if (e.repeat && ["ArrowRight", "ArrowLeft", "PageDown", "PageUp", " ", "Home", "End"].includes(k)) { e.preventDefault(); return; }
  if (k === "Escape") { if (S.panel) go(S.n, null); return; }
  if (k === " " && onControl) return;
  if (k === "ArrowRight" || k === "PageDown" || (k === " " && !e.shiftKey)) { e.preventDefault(); next(); }
  else if (k === "ArrowLeft" || k === "PageUp" || (k === " " && e.shiftKey)) { e.preventDefault(); prev(); }
  else if (k === "Home") { e.preventDefault(); go(0, null); }
  else if (k === "End") { e.preventDefault(); go(STEPS.length - 1, null); }
});
addEventListener("popstate", () => fromHash(false));
addEventListener("hashchange", () => fromHash(false));
narrow.addEventListener("change", () => { S.key = ""; if (S.data) read(S.data); else { draw(); enter(S.n, false); } });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const r = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - r.left) / r.width - 1;
  V.ty = 2 * (e.clientY - r.top) / r.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

/*__PANELS_JS__*/

$("steps").innerHTML = STEPS.map((s, i) => `<a href="#${s.hash}" data-n="${i}" class="${SECTION_START.has(i) && i ? "g" : ""}" aria-label="${i + 1}: ${esc(s.title)}"><i></i></a>`).join("");
if (parse().n !== 0) $("page").classList.add("load");
draw();
fromHash(false);
if (document.fonts) document.fonts.ready.then(() => { fit(); S.FV = {}; kick(); });
poll();
setInterval(clock, 1000);
if (!still.matches) requestAnimationFrame(frame);
</script>
</body>
</html>
"""

FACTS_JSON = as_js(shipped(demo_facts.FACTS))
SOURCES_JSON = as_js(demo_facts.SOURCES)
PAGE = (TEMPLATE.replace("__FACTS__", FACTS_JSON).replace("__SOURCES__", SOURCES_JSON)
        .replace("/*__PANEL_CSS__*/", demo_panels.PANEL_CSS).replace("/*__PANELS_JS__*/", demo_panels.PANELS_JS))
