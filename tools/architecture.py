"""The architecture page of the board site: one interactive picture of the shared work setup, for a first-time reader.

view.py serves PAGE at /architecture. The page reads the same /data as the board page every 10 s and draws the
setup as a small three-dimensional object seen from slightly above. The board is the dome in the centre with one
dot per live item. Each person has a swarm of agents beside it with threads to the board: one mark per agent
session, the Claude mark for Claude Code and the OpenAI mark for Codex, in the person's color of the board page.
The Chat ring (messages) runs through every swarm, and the Retro loop (self-review) with its comet goes around
everything. What moves is real data, replayed: a message leaves its sender's swarm for the others, a post
travels to the board and a ripple returns to every swarm. A larger dot with a halo is happening now. The picture
stands alone in the middle of the page with one button at the bottom right. A click on a part dims the rest, moves the picture
over and explains the part in a column beside it (address /architecture#<part>); the button "Follow one result"
steps through the path of one result (arrow keys, Esc). Nothing here writes to the board.
"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: how the harness works</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* Orbital depth. Dark is the hero: one lit glass body in a dark room. Light is the same object as white porcelain
   on a cool grey table, with a cast shadow in place of the glow. The light comes from the upper left in both. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338; --on-blue: #fff;
  --pl: .56; --pc: .15; --dim: .16;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue); --lift: 38%;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18); --btn-drop: rgba(16, 24, 32, .42);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --pl: .78; --pc: .13; --dim: .24;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff; --lift: 55%;
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
.hue { --c: oklch(var(--pl) var(--pc) var(--h)); }

.page {
  display: grid; grid-template-columns: minmax(0, 1fr) 0px; grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 0; height: 100vh; min-height: 620px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 24px;
  transition: grid-template-columns .45s cubic-bezier(.3, 0, .2, 1);
}
.page.open { grid-template-columns: minmax(0, 1fr) minmax(320px, 26vw); }  /* a selection opens the words column; the picture moves over */
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }
.status { margin-left: auto; color: var(--mute); white-space: nowrap; display: flex; align-items: center; gap: 10px; }
.status::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--blue); box-shadow: 0 0 0 4px color-mix(in srgb, var(--blue) 20%, transparent); }
.status.bad { color: var(--red); }
.status.bad::before { background: var(--red); box-shadow: 0 0 0 4px color-mix(in srgb, var(--red) 20%, transparent); }

/* The picture */
.stage { grid-column: 1; grid-row: 2; min-height: 0; min-width: 0; display: flex; padding: 8px 0 0; }
.foot { grid-column: 1; grid-row: 3; display: flex; justify-content: flex-end; padding-top: 6px; }
.page.open .foot { visibility: hidden; }
svg { width: 100%; height: 100%; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); text-anchor: middle; font-stretch: 112%; letter-spacing: .012em; }
.label { font-weight: 600; paint-order: stroke fill; stroke: var(--paper); stroke-width: 10px; stroke-linejoin: round; }
.label.plain { stroke: none; }
.who { font-weight: 560; fill: var(--c); paint-order: stroke fill; stroke: var(--paper); stroke-width: 7px; stroke-linejoin: round; }
.part { transition: opacity .28s ease; }
[data-go] { cursor: pointer; }
svg [data-go]:focus-visible { outline: none; }
svg [data-go]:focus-visible .ring { stroke: var(--blue); stroke-width: 3; }
svg [data-go]:focus-visible .rib { fill: var(--ink); }
.has-focus .part { opacity: var(--dim); }
.has-focus .part.on { opacity: 1; }
.hit { fill: none; stroke: transparent; pointer-events: stroke; }
.pad { fill: transparent; }
.atmo, .shade, .spec, .bloom, .pulse, .ripple, .arrive { pointer-events: none; }
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
.agent { fill: var(--c); stroke: none; }
.person { fill: var(--c); stroke: var(--paper); stroke-width: 3; }
.dot { fill: var(--c); }
.dot.note { opacity: .6; }
.dot.work { fill: var(--glass); stroke: var(--c); stroke-width: 2; }
.key .dot.work { fill: var(--paper); }
.dot.stale { stroke: var(--red); }
.sub { fill: var(--mute); font-weight: 460; }
.dot.off { opacity: .12; }
.ptail { fill: var(--c); opacity: .5; }
.phead { fill: var(--c); }
.ripple { fill: none; stroke: var(--c); stroke-width: 1.8; stroke-linecap: round; }
.arrive { fill: none; stroke: var(--c); stroke-width: 1.6; }
#fx { pointer-events: none; }
.fly { fill: var(--c); }
.halo { fill: none; stroke: var(--c); stroke-width: 1.5; opacity: .45; }

/* One drawn entrance, then only real events move */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
@keyframes pop { from { transform: scale(0); } }
@keyframes ping { 35% { transform: scale(2.2); } }
.dot, .agent, .person { transform-box: fill-box; transform-origin: center; }
.enter .draw { stroke-dasharray: 1; animation: draw 1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec { animation: fade 1.6s .2s both; }
.enter .rib, .enter .chev { animation: fade .9s .5s both; }
.enter .thread, .enter .tie, .enter .beads, .enter .label, .enter .who, .enter .sub, .enter .key .dot, .enter .key .agent {
  animation: fade .6s .55s both;
}
.enter .comet { animation: fade .8s 1.3s both; }
.enter .part:not(.key) .agent, .enter .person { animation: pop .45s cubic-bezier(.3, 1.5, .5, 1) both; animation-delay: calc(.25s + var(--i, 0) * 18ms); }
.enter .dot { animation: pop .4s cubic-bezier(.3, 1.4, .5, 1) both; animation-delay: calc(.7s + var(--i, 0) * 7ms); }
.dot.arrived { animation: pop .5s cubic-bezier(.3, 1.6, .5, 1) .9s both; }
.dot.ping { animation: ping .8s ease-out; }

/* The words */
.side {
  grid-column: 2; grid-row: 2 / 4; min-width: 0; min-height: 0; overflow: hidden auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
  opacity: 0; visibility: hidden; transition: opacity .3s ease .12s, visibility 0s .42s;
}
.page.open .side { opacity: 1; visibility: visible; transition: opacity .3s ease .12s; }
.pane { min-width: 270px; }
.walk {
  padding: 12px 22px; border-radius: 999px; background: var(--btn); color: var(--btn-ink);
  font-weight: 620; font-size: 15px; font-stretch: 106%; letter-spacing: .004em;
  box-shadow: inset 0 1px 0 var(--btn-edge), 0 14px 28px -14px var(--btn-drop); transition: transform .18s ease, box-shadow .18s ease;
}
.walk:hover { transform: translateY(-1px); box-shadow: inset 0 1px 0 var(--btn-edge), 0 0 0 1.5px var(--blue), 0 18px 32px -12px var(--btn-drop); }

.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.dhead h2.hue { color: var(--c); }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.rows { margin-top: 20px; }
.rows h3 { margin: 0 0 4px; font-size: 13px; font-weight: 600; color: var(--mute); }
.rows a { display: block; padding: 8px 0 8px 12px; border-top: 1px solid var(--rule); text-decoration: none; position: relative; font-size: 13.5px; line-height: 1.42; }
.rows a::before { content: ""; position: absolute; left: 0; top: 11px; bottom: 11px; width: 2px; border-radius: 2px; background: var(--c); }
.rows a:hover { background: linear-gradient(to right, var(--sheet), transparent); }
.rows .t { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 1; overflow: hidden; overflow-wrap: anywhere; }
.rows .m { color: var(--mute); font-size: 12.5px; }
.rows .m b { color: var(--c); font-weight: 600; }

.steps { display: flex; gap: 5px; }
.steps i { flex: 1; height: 2px; border-radius: 2px; background: var(--rule); }
.steps i.done { background: var(--ink); }
.cap { margin: 24px 0 0; font-size: clamp(26px, 2.3vw, 42px); line-height: 1.12; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 14ch; min-height: 4.6em; }
.nav { display: flex; align-items: center; gap: 10px; margin-top: 20px; }
.nav button { padding: 9px 18px; border-radius: 999px; border: 1px solid var(--faint); font-weight: 600; font-size: 14px; transition: background .15s ease, border-color .15s ease, color .15s ease; }
.nav button.next { background: var(--btn); color: var(--btn-ink); border-color: transparent; box-shadow: inset 0 1px 0 var(--btn-edge); }
.nav button:hover { border-color: var(--blue); background: var(--blue); color: var(--on-blue); box-shadow: none; }
.nav button[disabled] { opacity: .3; pointer-events: none; }
.nav span { margin-left: auto; font-size: 13px; color: var(--mute); }

@media (max-width: 900px) {
  .page { display: block; height: auto; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; }
  .name { font-stretch: 112%; margin-right: 0; }
  .stage { margin-top: 10px; padding: 0; }
  svg { height: auto; }
  .foot { padding-top: 14px; justify-content: center; }
  .page.open .foot { display: none; }
  .side { padding: 12px 0 0; overflow: visible; border-left: 0; }
  .pane { min-width: 0; }
}
@media (prefers-reduced-motion: reduce) {
  .enter *, .dot.arrived, .dot.ping { animation: none !important; }
  .part, .walk { transition: none; }
}
</style>
</head>
<body>
<div class="page" id="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture" aria-current="page">How it works</a>
    <span id="finds" style="display: contents"></span>
    <span class="status" id="status" role="status">Reading the board</span>
  </header>
  <div class="stage"><svg id="svg" role="group" aria-label="The harness: people and their agents around one shared board"></svg></div>
  <div class="foot"><button class="walk" data-go="walk-1">Follow one result</button></div>
  <div class="side" id="side">
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const $ = id => document.getElementById(id);
const HUES = [300, 155, 70, 215, 340, 115, 255, 35];  // the board page's colors: the same person has the same color on both
const S = { data: null, m: null, g: null, error: null, readAt: 0, sel: null, key: "", seen: null, entered: false, token: 0, queue: [], flying: false };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1);
const msgNs = m => Number(m.sk.slice(0, 20));
const mins = ns => Math.max(0, Math.floor((Date.now() * 1e6 - Number(ns)) / 60e9));
const ago = ns => { const m = mins(ns); return m < 1 ? "now" : m < 60 ? m + " min ago" : m < 2880 ? Math.floor(m / 60) + " h ago" : Math.floor(m / 1440) + " d ago"; };

/* What each part says: one sentence, then at most three more. Plain sentences in the words of README.md and
   DIRECTION.md, no slogans and no bold lead-ins. The rows under them are live. */
const TEXT = {
  board: {
    name: "Board",
    lead: "The board holds ideas, work in progress, results and knowledge, with votes and comments. Every agent reads it before starting and posts to it while working.",
    facts: ["An agent claims work by posting it. If another open claim names the same idea, the tool says so.", "Everything posted here can also be searched, together with findings from papers and past agent sessions. That search is the team's memory.", "Work that has been idle for 60 minutes can be taken over by another agent, after asking.", "Each dot is one item: hollow is open work, solid is a result, small is an idea or a note."],
    rows: m => ({ title: `${cnt(m.n.result)} results, ${cnt(m.n.work)} open, ${cnt(m.n.idea)} ideas`, list: m.results }),
  },
  msg: {
    name: "Chat",
    lead: "Agents send each other short messages: to everyone, to one person's agents, or about one board item.",
    facts: ["In Claude Code, a hook adds new messages to an agent's context after its tool calls, so the agent does not have to check for them.", "A message reaches a waiting agent in 0.2 s (measured)."],
    rows: m => ({ title: `${m.msgs.length} messages to everyone in the last ${m.hours} h`, list: m.msgs }),
  },
  review: {
    name: "Retro",
    lead: "Every tool command is logged with its time, person, agent and commit. After each finished result, an agent reviews these logs.",
    facts: ["The review measures how long each step took, from claiming the work to posting the result.", "It then makes one change to the tools or the rules, to remove the slowest step or a failure that repeats.", "Whether these changes help has not been measured yet."],
  },
  team: {
    name: "People and agents",
    lead: "Each person runs several coding agents (Claude Code or Codex). Each agent has subagents and works on its own git branch.",
    facts: ["All agents follow one rules file.", "The people decide the direction. The agents coordinate through the board and the messages.", "Each agent runs its own experiments as GPU jobs. A job can only start from code that is pushed to GitHub."],
  },
};
const WALK = [
  "An agent posts an idea on the board.",
  "It searches the board, its memory and the literature.",
  "It claims the work on the board.",
  "It writes the code on its own branch.",
  "It starts a GPU job from the pushed commit.",
  "It posts the result with its number, sample size and file path.",
  "A review reads the logs for inefficiencies and optimizes the research harness.",
];
const cnt = n => n >= 60 ? "60+" : n;  // /data returns the newest 60 of each kind
/* An agent is drawn as the mark of the product it runs on: Claude Code or Codex. Outlines from Bootstrap Icons
   1.13.1 (MIT), each in a 16 by 16 box. Any other agent is a rounded square. */
const MARKS = {
  claude: "m3.127 10.604 3.135-1.76.053-.153-.053-.085H6.11l-.525-.032-1.791-.048-1.554-.065-1.505-.08-.38-.081L0 7.832l.036-.234.32-.214.455.04 1.009.069 1.513.105 1.097.064 1.626.17h.259l.036-.105-.089-.065-.068-.064-1.566-1.062-1.695-1.121-.887-.646-.48-.327-.243-.306-.104-.67.435-.48.585.04.15.04.593.456 1.267.981 1.654 1.218.242.202.097-.068.012-.049-.109-.181-.9-1.626-.96-1.655-.428-.686-.113-.411a2 2 0 0 1-.068-.484l.496-.674L4.446 0l.662.089.279.242.411.94.666 1.48 1.033 2.014.302.597.162.553.06.17h.105v-.097l.085-1.134.157-1.392.154-1.792.052-.504.25-.605.497-.327.387.186.319.456-.045.294-.19 1.23-.37 1.93-.243 1.29h.142l.161-.16.654-.868 1.097-1.372.484-.545.565-.601.363-.287h.686l.505.751-.226.775-.707.895-.585.759-.839 1.13-.524.904.048.072.125-.012 1.897-.403 1.024-.186 1.223-.21.553.258.06.263-.218.536-1.307.323-1.533.307-2.284.54-.028.02.032.04 1.029.098.44.024h1.077l2.005.15.525.346.315.424-.053.323-.807.411-3.631-.863-.872-.218h-.12v.073l.726.71 1.331 1.202 1.667 1.55.084.383-.214.302-.226-.032-1.464-1.101-.565-.497-1.28-1.077h-.084v.113l.295.432 1.557 2.34.08.718-.112.234-.404.141-.444-.08-.911-1.28-.94-1.44-.759-1.291-.093.053-.448 4.821-.21.246-.484.186-.403-.307-.214-.496.214-.98.258-1.28.21-1.016.19-1.263.112-.42-.008-.028-.092.012-.953 1.307-1.448 1.957-1.146 1.227-.274.109-.477-.247.045-.44.266-.39 1.586-2.018.956-1.25.617-.723-.004-.105h-.036l-4.212 2.736-.75.096-.324-.302.04-.496.154-.162 1.267-.871z",
  openai: "M14.949 6.547a3.94 3.94 0 0 0-.348-3.273 4.11 4.11 0 0 0-4.4-1.934A4.1 4.1 0 0 0 8.423.2 4.15 4.15 0 0 0 6.305.086a4.1 4.1 0 0 0-1.891.948 4.04 4.04 0 0 0-1.158 1.753 4.1 4.1 0 0 0-1.563.679A4 4 0 0 0 .554 4.72a3.99 3.99 0 0 0 .502 4.731 3.94 3.94 0 0 0 .346 3.274 4.11 4.11 0 0 0 4.402 1.933c.382.425.852.764 1.377.995.526.231 1.095.35 1.67.346 1.78.002 3.358-1.132 3.901-2.804a4.1 4.1 0 0 0 1.563-.68 4 4 0 0 0 1.14-1.253 3.99 3.99 0 0 0-.506-4.716m-6.097 8.406a3.05 3.05 0 0 1-1.945-.694l.096-.054 3.23-1.838a.53.53 0 0 0 .265-.455v-4.49l1.366.778q.02.011.025.035v3.722c-.003 1.653-1.361 2.992-3.037 2.996m-6.53-2.75a2.95 2.95 0 0 1-.36-2.01l.095.057L5.29 12.09a.53.53 0 0 0 .527 0l3.949-2.246v1.555a.05.05 0 0 1-.022.041L6.473 13.3c-1.454.826-3.311.335-4.15-1.098m-.85-6.94A3.02 3.02 0 0 1 3.07 3.949v3.785a.51.51 0 0 0 .262.451l3.93 2.237-1.366.779a.05.05 0 0 1-.048 0L2.585 9.342a2.98 2.98 0 0 1-1.113-4.094zm11.216 2.571L8.747 5.576l1.362-.776a.05.05 0 0 1 .048 0l3.265 1.86a3 3 0 0 1 1.173 1.207 2.96 2.96 0 0 1-.27 3.2 3.05 3.05 0 0 1-1.36.997V8.279a.52.52 0 0 0-.276-.445m1.36-2.015-.097-.057-3.226-1.855a.53.53 0 0 0-.53 0L6.249 6.153V4.598a.04.04 0 0 1 .019-.04L9.533 2.7a3.07 3.07 0 0 1 3.257.139c.474.325.843.778 1.066 1.303.223.526.289 1.103.191 1.664zM5.503 8.575 4.139 7.8a.05.05 0 0 1-.026-.037V4.049c0-.57.166-1.127.476-1.607s.752-.864 1.275-1.105a3.08 3.08 0 0 1 3.234.41l-.096.054-3.23 1.838a.53.53 0 0 0-.265.455zm.742-1.577 1.758-1 1.762 1v2l-1.755 1-1.762-1z",
};

/* Geometry: everything hangs on one centre, and the moving parts live in a small 3D space around it (x right,
   y down, z toward the viewer). The board faces the viewer. The swarms sit on one circle in the people's plane,
   seen from a little above; that circle is the messages path, so it passes through every swarm. The self-review
   loop is a larger circle in its own plane. A plane is [inclination, turn on the screen]. sw is the radius of the
   largest swarm; a mark is at most `mark` wide, and marks stand `pack` times their width apart or more, so that
   they never cover each other while the swarm turns. */
const RAD = Math.PI / 180;
function plane(inc, turn) { return { c: Math.cos(inc * RAD), s: Math.sin(inc * RAD), co: Math.cos(turn * RAD), so: Math.sin(turn * RAD) }; }
function geo() {
  const g = narrow.matches
    ? { w: 720, h: 660, cx: 360, cy: 284, rb: 100, rq: 200, rp: 274, rr: 338, fs: 25, fw: 20, D: 1900, sw: 50, over: 26, cmax: 23, mark: 21, pack: 1.01, pp: [34, 0], pr: [36, -4] }
    : { w: 1140, h: 985, cx: 570, cy: 404, rb: 164, rq: 340, rp: 446, rr: 540, fs: 24, fw: 18.5, D: 2100, sw: 88, over: 45, cmax: 27, mark: 25, pack: 1.06, pp: [40, 0], pr: [36, -4] };
  g.PP = plane(...g.pp); g.PR = plane(...g.pr);
  return g;
}
const pt = (g, r, a) => [g.cx + r * Math.cos(a * Math.PI / 180), g.cy + r * Math.sin(a * Math.PI / 180)];
const xy = p => `${f(p[0])} ${f(p[1])}`;
function angles(n) {  // people around the board; the top stays free for the labels
  if (n < 2) return [90];
  if (n === 2) return [150, 30];
  const first = n % 2 ? 90 : 90 + 180 / n;
  return Array.from({ length: n }, (_, k) => (first + k * 360 / n) % 360);
}
const arc = (g, r, a0, a1) => `M${xy(pt(g, r, a0))}A${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${xy(pt(g, r, a1))}`;
const spiral = (i, c) => [c * Math.sqrt(i + .6) * Math.cos(i * 2.39996), c * Math.sqrt(i + .6) * Math.sin(i * 2.39996)];

/* The view: a slow sway, plus a few degrees toward the pointer. With reduced motion it stays at rest. */
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
S.t = 21;  // the still frame: the comet on the near side
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
const world = (P, u, v) => [u * P.co - v * P.c * P.so, u * P.so + v * P.c * P.co, v * P.s];  // a point (u, v) of a plane; v > 0 is the near side
const onRing = (P, r, deg) => world(P, r * Math.cos(deg * RAD), r * Math.sin(deg * RAD));
function proj(g, p) {  // to the screen: [x, y, scale, depth]
  const x = p[0] * V.c1 + p[2] * V.s1, z1 = p[2] * V.c1 - p[0] * V.s1;
  const y = p[1] * V.c2 - z1 * V.s2, z = z1 * V.c2 + p[1] * V.s2, k = g.D / (g.D - z);
  return [g.cx + x * k, g.cy + y * k, k, z];
}
function ribbon(p, w) {  // a stroke whose width changes along it: w(point, index) is its full width there
  const n = p.length, L = [], R = [], h = v => v.toFixed(2);
  for (let i = 0; i < n; i++) {
    const a = p[Math.max(0, i - 1)], b = p[Math.min(n - 1, i + 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, half = w(p[i], i) / 2;
    L.push(h(p[i][0] - dy / d * half) + " " + h(p[i][1] + dx / d * half));
    R.push(h(p[i][0] + dy / d * half) + " " + h(p[i][1] - dx / d * half));
  }
  return "M" + L.join("L") + "L" + R.reverse().join("L") + "Z";
}

function model(d) {
  const all = [...d.items, ...d.messages];
  const people = [...new Set(all.map(r => r.who))].sort();
  const agents = people.map(p => [...new Set(all.filter(r => r.who === p && r.session).map(r => r.session))].sort().slice(0, 30));
  const product = s => {  // what a session runs on: the agent name of any of its rows (tools/events.py)
    const a = (all.find(r => r.session === s && r.agent) || {}).agent || "";
    return a.startsWith("claude-code") ? "claude" : a.startsWith("codex") ? "openai" : "";
  };
  const live = d.items.filter(i => i.listed !== "work-closed").sort((a, b) => a.at_ns - b.at_ns);
  const of = k => live.filter(i => i.listed === k);
  const newest = l => [...l].sort((a, b) => b.at_ns - a.at_ns);
  const results = newest(of("result")), msgs = [...d.messages].reverse();
  const last = Math.max(0, ...d.items.map(i => Number(i.at_ns)), ...d.messages.map(msgNs));
  return {
    people, agents, marks: agents.map(l => l.map(product)), live, results, msgs, last, hours: d.hours, scores: (d.scores || []).length,
    notes: newest(live.filter(i => i.listed === "knowledge" || i.listed === "skill")),
    n: { result: results.length, work: of("work").length, idea: of("idea").length, note: of("knowledge").length + of("skill").length },
    nAgents: agents.reduce((s, a) => s + a.length, 0),
    lead: Math.max(0, people.indexOf(results[0]?.who)),
  };
}

/* The picture. The parts are built when the people or their agents change; place() then sets every position that
   depends on the view; the item dots are drawn on every read. Back to front: the light around the board, the
   self-review loop, the messages path, the threads, the board, the swarms. An agent is the mark of its product in
   its person's colour, so it cannot be read as a board item, which is a dot. The pulses of the replay live inside the part they travel on,
   so they dim with it. */
function draw() {
  const g = S.g = geo(), m = S.m, n = m ? m.people.length : 0, th = n ? angles(n) : [];
  const svg = $("svg"), hue = i => HUES[i % HUES.length];
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  const part = (name, go, body, label) =>
    `<g class="part" data-part="${name}"${go ? ` data-go="${go}"` : ""}${label ? ` role="button" tabindex="0" aria-label="${label}"` : ""}>${body}</g>`;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  let out = "<defs>" +
    `<radialGradient id="body" cx=".36" cy=".3" r=".86">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".12" y1=".08" x2=".9" y2=".94">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.6, "var(--ink)", .22)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<radialGradient id="glo-b">${stop(0, "var(--blue)", .6)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<linearGradient id="rvfade" gradientUnits="userSpaceOnUse">${stop(0, "var(--blue)", .4)}${stop(1, "var(--blue)", 1)}</linearGradient>` +
    `<linearGradient id="msgfade" gradientUnits="userSpaceOnUse">${stop(0, "var(--mute)", .5)}${stop(1, "var(--ink)", .95)}</linearGradient>` +
    Object.keys(MARKS).map(k => `<symbol id="mark-${k}" viewBox="0 0 16 16"><path d="${MARKS[k]}"/></symbol>`).join("") +
    th.map((_, i) =>
      `<radialGradient id="orb-${i}" class="hue" style="--h:${hue(i)}" cx=".34" cy=".3" r=".8">${stop(0, "color-mix(in oklch, var(--c), white var(--lift))")}${stop(1, "var(--c)")}</radialGradient>` +
      `<radialGradient id="glo-${i}" class="hue" style="--h:${hue(i)}">${stop(0, "var(--c)", .55)}${stop(1, "var(--c)", 0)}</radialGradient>`).join("") +
    "</defs>";
  const pulse = i => `<g class="pulse" opacity="0"><circle class="bloom"${i == null ? "" : ` fill="url(#glo-${i})"`}/><path class="ptail"/>` +
    `<circle class="phead"${i == null ? "" : ` style="fill:url(#orb-${i}) var(--c)"`}/></g>`;

  out += `<g class="part" data-part="board"><circle class="atmo" cx="${g.cx}" cy="${g.cy}" r="${g.rb * 2}" fill="url(#atmo)"/>` +
    `<circle class="shade" cx="${f(g.cx + g.rb * .07)}" cy="${f(g.cy + g.rb * .15)}" r="${f(g.rb * 1.22)}" fill="url(#shade)"/></g>`;
  const chevron = i => `<path class="chev" id="rv-c${i}" d="M-10 -8.5L5 0L-10 8.5"/>`;
  out += part("review", "review",
    `<path class="hit" id="rv-hit" stroke-width="26"/><path class="rib" id="rv-rib"/>${chevron(0)}${chevron(1)}` +
    `<g class="comet" id="comet"><circle class="bloom" id="cm-glow" fill="url(#glo-b)"/><path class="comet-tail" id="cm-long" opacity=".3"/>` +
    `<path class="comet-tail" id="cm-short" opacity=".85"/><circle class="comet-core" id="cm-core"/></g>` +
    `<text class="label" id="rv-label" font-size="${g.fs}">Retro</text>`, "Retro");
  out += part("msg", "msg",  // the path through every swarm; on it, a message runs from its sender to the other swarms
    `<path class="hit" id="ms-hit" stroke-width="22"/><path class="beads ring" id="ms-ring"/>` +
    `<g class="hue" id="ms-fx">${th.map(() => `<ellipse class="arrive" opacity="0"/>`).join("")}${pulse()}${pulse()}</g>` +
    `<text class="label" id="ms-label" font-size="${g.fs}">Chat</text>`, "Chat");
  th.forEach((a, i) => {  // the threads of one person, the post that runs down one of them, and the read that comes back up all of them
    out += part("thread-" + i, "", `<path class="thread hue" style="--h:${hue(i)}"/><path class="ripple hue" opacity="0"/><g class="hue" style="--h:${hue(i)}">${pulse(i)}</g>`);
  });

  const top = g.rb + g.fs * .82, sx = g.cx - g.rb * .3, sy = g.cy - g.rb * .46;  // the board's name along its top; the light on its upper left
  out += part("board", "board",
    `<circle class="board-ring ring draw" pathLength="1" cx="${g.cx}" cy="${g.cy}" r="${g.rb}"/>` +
    `<ellipse class="spec" cx="${f(sx)}" cy="${f(sy)}" rx="${f(g.rb * .56)}" ry="${f(g.rb * .34)}" transform="rotate(-34 ${f(sx)} ${f(sy)})" fill="url(#spec)"/>` +
    `<g id="dots"></g><path id="on-board" fill="none" stroke="none" d="${arc(g, top, -150, -30)}"/>` +
    `<text class="label plain" font-size="${g.fs}" dy="${f(g.fs * .34)}"><textPath href="#on-board" startOffset="50%">Board</textPath></text>`, "Board");
  th.forEach((a, i) => {
    out += part("swarm-" + i, "p-" + m.people[i],
      `<g class="hue" style="--h:${hue(i)}"><circle class="pad" r="${g.sw + 16}"/><path class="tie"/>` +
      m.marks[i].map((mark, k) => mark ? `<use class="agent" href="#mark-${mark}" style="--i:${k}"/>` : `<rect class="agent" style="--i:${k}"/>`).join("") +
      `<circle class="person ring" style="fill:url(#orb-${i}) var(--c)"/>` +
      `<text class="who" font-size="${g.fw}">${esc(m.people[i])}</text></g>`,
      `${esc(m.people[i])}, ${m.agents[i].length} agents`);
  });
  const k = g.fw * .92, ky = g.h - 14, keys = [["agent", "agent"], ["work", "open work"], ["", "result"], ["note", "idea or note"]];
  const here = m ? ["claude", "openai", ""].filter(x => m.marks.some(l => l.includes(x))) : ["claude"];  // the marks on this page
  const widths = keys.map(([cls, t]) => 26 + t.length * k * .54 + 22 + (cls === "agent" ? (here.length - 1) * 19 : 0)), total = widths.reduce((a, b) => a + b, 0) - 22;
  let kx = narrow.matches ? (g.w - total) / 2 : 6;
  out += `<g class="part key" data-part="key" style="--c:var(--mute)">` + keys.map(([cls, t], i) => {
    const x = kx, y = ky - k * .32; kx += widths[i];
    const one = (mark, j) => mark ? `<use class="agent" href="#mark-${mark}" x="${f(x - 1 + j * 19)}" y="${f(y - 8)}" width="16" height="16"/>`
      : `<rect class="agent" x="${f(x + j * 19)}" y="${f(y - 6.5)}" width="13" height="13" rx="3.6"/>`;
    return (cls === "agent" ? here.map(one).join("") : `<circle class="dot ${cls}" cx="${f(x + 7)}" cy="${f(y)}" r="${cls === "note" ? 3.4 : 6}"/>`) +
      `<text class="sub" x="${f(x + 20 + (cls === "agent" ? (here.length - 1) * 19 : 0))}" y="${f(ky)}" font-size="${f(k)}" style="text-anchor:start">${t}</text>`;
  }).join("") + "</g>";
  svg.innerHTML = out + '<g id="fx"></g>';

  const el = {}, unit = e => ({ el: e, glow: e.children[0], tail: e.children[1], head: e.children[2] });
  ["rv-hit", "rv-rib", "rv-c0", "rv-c1", "comet", "cm-glow", "cm-long", "cm-short", "cm-core", "rv-label", "rvfade",
    "ms-hit", "ms-ring", "ms-label", "ms-fx", "msgfade"].forEach(id => { el[id] = $(id); });
  const open = (name, r) => (name.length * g.fs * .33 + 16) / (r * RAD * .9);  // a ring is open under its name, by this many degrees each side
  S.th = th;
  S.play = {};
  S.r = {
    el, gap: open("Retro", g.rr), mgap: open("Chat", g.rq),
    beads: Math.round(g.rq * 2 * Math.PI / 14),
    arrive: [...svg.querySelectorAll("#ms-fx .arrive")], legs: [...svg.querySelectorAll("#ms-fx .pulse")].map(unit),
    swarms: th.map((a, i) => {  // the agents of one person circle their own centre, in the people's plane
      const p = svg.querySelector(`[data-part="swarm-${i}"]`), t = svg.querySelector(`[data-part="thread-${i}"]`), count = m.agents[i].length;
      const c = Math.min(g.cmax, g.sw / Math.sqrt(count + .6)), who = p.querySelector(".who");
      return { a, c, size: Math.min(g.mark, c / g.pack), below: Math.sin(a * RAD) >= 0, side: Math.abs(Math.cos(a * RAD)) > .3 ? Math.sign(Math.cos(a * RAD)) : 0,
        wide: who.getComputedTextLength(), pad: p.querySelector(".pad"), tie: p.querySelector(".tie"), dots: [...p.querySelectorAll(".agent")],
        person: p.querySelector(".person"), who, thread: t.querySelector(".thread"), ripple: t.querySelector(".ripple"), pulse: unit(t.querySelector(".pulse")) };
    }),
  };
  place(S.t);
  if (m && !S.entered) {
    S.entered = true;
    svg.classList.add("enter");
    setTimeout(() => svg.classList.remove("enter"), 2600);
  }
}

function dots() {  // the items sit on a shallow dome: evenly spread on it, so closer together toward its rim
  const g = S.g, m = S.m, n = m.live.length, R = g.rb - 16, c = Math.min(15, R / Math.sqrt(n + 1));
  const cap = 62 * RAD, K = 1 - Math.cos(cap), Rs = R / Math.sin(cap);
  $("dots").innerHTML = m.live.map((it, i) => {
    const [dx, dy] = spiral(i, c), big = it.listed === "result" || it.listed === "work";
    const u = Math.min(1, Math.hypot(dx, dy) / R), tilt = Math.acos(1 - u * u * K), q = u ? Rs * Math.sin(tilt) / (u * R) : 1;
    const stale = it.listed === "work" && mins(it.active_ns ?? it.at_ns) >= 60;
    const cls = ["dot hue", it.listed === "work" ? "work" : big ? "" : "note", stale && "stale", S.seen && !S.seen.has(it.id) && "arrived"];
    return `<circle class="${cls.filter(Boolean).join(" ")}" style="--h:${HUES[Math.max(0, m.people.indexOf(it.who)) % HUES.length]};--i:${i}" ` +
      `data-who="${esc(it.who)}" cx="${f(g.cx + dx * q)}" cy="${f(g.cy + dy * q)}" r="${f(c * (big ? .4 : .27) * (.62 + .5 * Math.cos(tilt)))}"><title>${esc(it.id)}: ${esc(it.text.slice(0, 120))}</title></circle>`;
  }).join("");
}

/* Motion that is always on: agents circle in their swarm, a comet runs the self-review loop, the board turns
   slowly, and the whole view sways by a few degrees. What is near is larger and brighter; what is far is smaller
   and fainter. On top of that the replay (below) shows real messages and real posts, one at a time. */
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
function place(t) {
  const g = S.g, R = S.r;
  if (!R) return;
  const E = R.el, set = (el, o) => { for (const k in o) el.setAttribute(k, o[k]); };
  const at = (P, r, deg) => proj(g, onRing(P, r, deg));
  const ring = (P, r, a0, a1, n) => Array.from({ length: n + 1 }, (_, i) => at(P, r, a0 + (a1 - a0) * i / n));
  const line = p => "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L");
  const near = (P, r, q) => Math.min(1, Math.max(0, .5 + q[3] / (2 * r * P.s)));  // 0 at the far side of a ring, 1 at the near side
  const fade = (grad, P, r) => { const a = at(P, r, -90), b = at(P, r, 90); set(grad, { x1: f(a[0]), y1: f(a[1]), x2: f(b[0]), y2: f(b[1]) }); };

  // The self-review loop: a line that is thin and faint at the back, heavier in front.
  const loop = ring(g.PR, g.rr, -90 + R.gap, 270 - R.gap, 100);
  E["rv-rib"].setAttribute("d", ribbon(loop, q => 1 + 2.3 * near(g.PR, g.rr, q)));
  E["rv-hit"].setAttribute("d", line(loop) + "Z");
  fade(E.rvfade, g.PR, g.rr);
  [60, 240].forEach((a, i) => {
    const p = at(g.PR, g.rr, a), p0 = at(g.PR, g.rr, a - 2), p1 = at(g.PR, g.rr, a + 2);
    E["rv-c" + i].setAttribute("transform", `translate(${f(p[0])} ${f(p[1])}) rotate(${f(Math.atan2(p1[1] - p0[1], p1[0] - p0[0]) / RAD)}) scale(${(.5 + .65 * near(g.PR, g.rr, p)).toFixed(2)})`);
  });
  const ca = t * 20, head = at(g.PR, g.rr, ca), cn = near(g.PR, g.rr, head), cw = 2.4 + 4.4 * cn;
  E["cm-long"].setAttribute("d", ribbon(ring(g.PR, g.rr, ca - 52, ca, 16), (q, i) => cw * i / 16));
  E["cm-short"].setAttribute("d", ribbon(ring(g.PR, g.rr, ca - 14, ca, 6), (q, i) => cw * (.3 + .7 * i / 6)));
  set(E["cm-core"], { cx: f(head[0]), cy: f(head[1]), r: f(cw * .6) });
  set(E["cm-glow"], { cx: f(head[0]), cy: f(head[1]), r: f(cw * 4.4) });
  E.comet.setAttribute("opacity", (.5 + .5 * cn).toFixed(2));
  const apex = at(g.PR, g.rr, -90);
  set(E["rv-label"], { x: f(apex[0]), y: f(apex[1] + g.fs * .34) });

  // The messages path: fine dashes on the circle that passes through every swarm, open under its name.
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

  // The swarms: each a small disc of agents in the people's plane, with threads to the nearest point of the board.
  R.swarms.forEach(o => {
    const u0 = g.rq * Math.cos(o.a * RAD), v0 = g.rq * Math.sin(o.a * RAD);
    const c = proj(g, world(g.PP, u0, v0)), p = at(g.PP, g.rp, o.a), to = Math.atan2(c[1] - g.cy, c[0] - g.cx);
    const end = [g.cx + (g.rb + 2) * Math.cos(to), g.cy + (g.rb + 2) * Math.sin(to)], ends = f(end[0]) + " " + f(end[1]);
    let web = o.dots.length ? "" : `M${f(c[0])} ${f(c[1])}L${ends}`, fan = o.dots.length ? "" : `M${ends}L${f(c[0])} ${f(c[1])}`;
    o.c0 = c; o.end = end; o.at = []; o.reach = Math.hypot(c[0] - end[0], c[1] - end[1]);
    o.dots.forEach((d, k) => {
      const r = o.c * Math.sqrt(k + .6), a = k * 2.39996 + t * .22;  // the swarm turns as one, so its agents never cover each other
      const q = proj(g, world(g.PP, u0 + r * Math.cos(a), v0 + r * Math.sin(a))), side = o.size * q[2] * (d.tagName === "rect" ? .78 : 1), here = f(q[0]) + " " + f(q[1]);
      set(d, { x: f(q[0] - side / 2), y: f(q[1] - side / 2), width: f(side), height: f(side), rx: f(side * .28) });  // upright, facing the viewer
      web += `M${here}L${ends}`;
      fan += `M${ends}L${here}`;
      o.at.push(q);
      o.reach = Math.max(o.reach, Math.hypot(q[0] - end[0], q[1] - end[1]));
    });
    o.fan = fan;  // the same threads, drawn from the board outward: a read travels this way
    o.thread.setAttribute("d", web);
    set(o.pad, { cx: f(c[0]), cy: f(c[1]) });
    o.tie.setAttribute("d", `M${f(c[0])} ${f(c[1])}L${f(p[0])} ${f(p[1])}`);
    set(o.person, { cx: f(p[0]), cy: f(p[1]), r: f(13 * p[2]) });
    set(o.who, { x: f(p[0] - o.side * Math.max(0, o.wide / 2 - g.over)), y: f(p[1] + (o.below ? g.fw * 1.9 : -g.fw * 1.15) * p[2]) });
  });
  const turn = $("dots");
  if (turn) turn.setAttribute("transform", `rotate(${f(t * 1.5 % 360)} ${g.cx} ${g.cy})`);
  posted(t);
  sent(t, at, ring, near);
}
function spin(now) {
  const t = S.t = 21 + now / 1000;
  V.px += (V.tx - V.px) * .06;
  V.py += (V.ty - V.py) * .06;
  aim(6 * Math.sin((t - 21) * .13) + 5 * V.px, 2.5 * Math.sin((t - 21) * .09) - 2.5 * V.py);
  beat(t);
  place(t);
  requestAnimationFrame(spin);
}

/* The replay: about every 2.5 s one real event, a message and a post in turn, from the newest 40 of each, looped.
   A message is a pulse in its sender's colour that leaves the sender's swarm along the messages path, both ways,
   and reaches every other swarm. A post is a pulse in its poster's colour that runs down one thread to the board;
   when it lands, a faint ripple leaves the board along all threads, because every agent reads the board. An event
   that happens now (S.queue) plays next, as a larger dot with a halo. Nothing plays during the walk, or with
   reduced motion. */
S.play = {}; S.due = 25; S.turn = false; S.nth = { msg: 0, post: 0 }; S.busy = false;
function comet(u, pts, r, opacity) {  // a pulse: a small lit head, a tapered tail along pts behind it, a soft light around it
  const n = pts.length - 1, h = pts[n];
  u.head.setAttribute("cx", f(h[0])); u.head.setAttribute("cy", f(h[1])); u.head.setAttribute("r", f(r));
  u.glow.setAttribute("cx", f(h[0])); u.glow.setAttribute("cy", f(h[1])); u.glow.setAttribute("r", f(r * 3.6));
  u.tail.setAttribute("d", n ? ribbon(pts, (q, i) => r * 1.5 * i / n) : "");
  u.el.setAttribute("opacity", opacity.toFixed(2));
}
function hush() {  // stop the replay where it is
  const R = S.r;
  S.play = {};
  if (!R) return;
  R.swarms.forEach(o => { o.pulse.el.setAttribute("opacity", 0); o.ripple.setAttribute("opacity", 0); });
  R.legs.forEach(u => u.el.setAttribute("opacity", 0));
  R.arrive.forEach(e => e.setAttribute("opacity", 0));
}
function beat(t) {
  const m = S.m;
  if (!m || !S.r || t < S.due || S.busy || step()) return;
  S.due = t + 2.5;
  const now = S.queue.shift();
  if (now) {  // happening now
    const i = m.people.indexOf(now.who);
    if (i < 0) return;
    S.busy = true;
    fly(route(S.g, now.kind, S.th[i]), HUES[i % HUES.length], now.kind === "msg" ? 2600 : 1100).then(() => {
      S.busy = false; S.due = S.t + 1.5;
      if (now.kind === "board" && !step()) S.play.post = { i, k: -1, at: -1, t0: S.t - 1 };  // the read that follows the post
    });
    return;
  }
  const msgs = S.data.messages.slice(-40).filter(x => m.people.includes(x.who)), posts = m.live.slice(-40);
  S.turn = !S.turn;
  if (S.turn && m.people.length > 1 && msgs.length) {
    const i = m.people.indexOf(msgs[S.nth.msg++ % msgs.length].who), a0 = S.th[i];
    const away = S.th.map((a, j) => ({ j, d: ((a - a0) % 360 + 360) % 360 })).filter(x => x.j !== i);  // degrees to each other swarm, clockwise
    const reach = dir => Math.max(0, ...away.map(x => dir > 0 ? x.d : 360 - x.d).filter(d => d <= 180 && (dir > 0 || d < 180)));
    S.play.msg = { i, t0: t, legs: [1, -1].map(dir => ({ dir, span: reach(dir), time: .9 + reach(dir) / 110 })),
      hits: away.map(x => x.d <= 180 ? { j: x.j, dir: 1, d: x.d, t: 0 } : { j: x.j, dir: -1, d: 360 - x.d, t: 0 }) };
    S.r.el["ms-fx"].setAttribute("style", `--h:${HUES[i % HUES.length]}`);
    S.r.legs.forEach(u => { u.glow.setAttribute("fill", `url(#glo-${i})`); u.head.setAttribute("style", `fill:url(#orb-${i}) var(--c)`); });
  } else if (posts.length) {
    const it = posts[S.nth.post++ % posts.length], i = Math.max(0, m.people.indexOf(it.who)), count = m.agents[i].length;
    const k = count ? (m.agents[i].indexOf(it.session) + count) % count : -1;  // the thread of the agent session that posted it, when that is known
    S.play.post = { i, k, at: m.live.indexOf(it), t0: t };
  }
}
function posted(t) {
  const P = S.play.post, R = S.r;
  if (!P || !R.swarms[P.i]) return;
  const o = R.swarms[P.i], age = t - P.t0, r = 3.8 * o.c0[2];
  if (age < 1) {  // down one thread
    const from = o.at[P.k] || o.c0, on = q => [from[0] + (o.end[0] - from[0]) * q, from[1] + (o.end[1] - from[1]) * q], e = ease(age);
    return comet(o.pulse, [on(Math.max(0, e - .24)), on(Math.max(0, e - .12)), on(e)], r, Math.min(1, age / .12));
  }
  if (!P.landed) {  // on the board: its own dot answers, and the read starts in the poster's colour
    P.landed = true;
    const dot = P.at < 0 ? null : $("dots").children[P.at];
    if (dot) { dot.classList.remove("ping"); dot.getBBox(); dot.classList.add("ping"); }
    R.swarms.forEach(s => s.ripple.setAttribute("style", `--h:${HUES[P.i % HUES.length]}`));
  }
  const q = (age - 1) / 1.3, flash = Math.min(1, (age - 1) / .35);
  comet(o.pulse, [o.end], r * (1 - flash), 1 - flash);
  if (q >= 1) { R.swarms.forEach(s => s.ripple.setAttribute("opacity", 0)); S.play.post = null; return; }
  R.swarms.forEach(s => {  // back up every thread
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
  P.hits.forEach(h => {  // where it arrives, a ring opens around that swarm, flat in the people's plane
    const e = R.arrive[h.j], o = R.swarms[h.j], q = h.t ? (t - h.t) / .9 : 2;
    if (q >= 1) return e.setAttribute("opacity", 0);
    live = true;
    const r = (12 + (g.sw + 10) * (1 - (1 - q) ** 2)) * o.c0[2];
    e.setAttribute("cx", f(o.c0[0])); e.setAttribute("cy", f(o.c0[1])); e.setAttribute("rx", f(r)); e.setAttribute("ry", f(r * g.PP.c));
    e.setAttribute("opacity", (.8 * (1 - q)).toFixed(2));
  });
  if (!live) S.play.msg = null;
}

/* Motion: a dot travels along the drawn lines, for a post or message that happens now, or for a step of the walk.
   A point with three numbers lies in the 3D space and follows the view; a point with two is fixed on the screen. */
function route(g, kind, a) {
  const loop = (P, r, a0) => Array.from({ length: 91 }, (_, i) => onRing(P, r, a0 + i * 4));
  const home = onRing(g.PP, g.rq, a), s = proj(g, home), sa = Math.atan2(s[1] - g.cy, s[0] - g.cx) / RAD;  // the swarm, and where it is on the screen
  if (kind === "board") return [home, pt(g, g.rb + 3, sa)];
  if (kind === "msg") return loop(g.PP, g.rq, a);  // once round the messages path, past every swarm
  if (kind === "swarm") {  // once round the swarm itself
    const u = g.rq * Math.cos(a * RAD), v = g.rq * Math.sin(a * RAD), r = g.sw + 12;
    return Array.from({ length: 61 }, (_, i) => world(g.PP, u + r * Math.cos((i * 6 - 90) * RAD), v + r * Math.sin((i * 6 - 90) * RAD)));
  }
  return loop(g.PR, g.rr, -82);  // the self-review loop
}
function fly(points, hue, ms) {
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
      const k = (along - len[i - 1]) / ((len[i] - len[i - 1]) || 1), a = at(points[i - 1]), b = at(points[i]), mix = j => a[j] + (b[j] - a[j]) * k;
      const x = mix(0), y = mix(1), hidden = mix(3) < 0 && Math.hypot(x - S.g.cx, y - S.g.cy) < S.g.rb;  // behind the board
      el.setAttribute("transform", `translate(${f(x)} ${f(y)}) scale(${mix(2).toFixed(3)})`);
      el.setAttribute("opacity", hidden ? .1 : 1);
      if (p < 1) requestAnimationFrame(tick); else { el.remove(); done(); }
    };
    requestAnimationFrame(tick);
  });
}
async function act(step) {
  const g = S.g, i = S.m.lead, a = S.th[i], h = HUES[i % HUES.length], back = p => [...p].reverse();
  const token = ++S.token, go = (p, ms) => token === S.token ? fly(p, h, ms) : null;
  hush();
  if (step === 1 || step === 3 || step === 6) await go(route(g, "board", a), 1000);  // a post: swarm to board
  if (step === 2) await go(back(route(g, "board", a)), 1100);  // a read: board to swarm
  if (step === 5) await go(route(g, "swarm", a), 1900);  // the experiment happens inside the swarm
  if (step === 7) await go(route(g, "review", a), 3000);
}

/* Selection: one value, mirrored in the address. */
const step = () => /^walk-[1-7]$/.test(S.sel || "") ? Number(S.sel.slice(5)) : 0;
function lit() {
  const m = S.m, all = k => (m ? m.people : []).map((_, i) => k + i), me = m ? m.lead : 0, s = S.sel;
  if (!s) return null;
  if (s.startsWith("p-")) { const i = m ? m.people.indexOf(s.slice(2)) : -1; return ["swarm-" + i, "thread-" + i, "board"]; }
  const mine = ["swarm-" + me], post = ["swarm-" + me, "thread-" + me, "board"];
  return ({
    board: ["board", "key", ...all("thread-")], msg: ["msg", ...all("swarm-")], review: ["review"], team: all("swarm-"),
    "walk-1": post, "walk-2": post, "walk-3": post, "walk-4": mine, "walk-5": mine, "walk-6": post, "walk-7": ["review"],
  })[s] || null;
}
function known(s) { return s in TEXT || /^walk-[1-7]$/.test(s) || (s.startsWith("p-") && (!S.m || S.m.people.includes(s.slice(2)))); }
function fromHash() {
  const s = decodeURIComponent(location.hash.slice(1));
  const next = s && known(s) ? s : null, changed = next !== S.sel;
  S.sel = next;
  show();
  if (changed) { S.token++; if (step() && S.m) act(step()); }
}
function go(s, replace) {
  if (s === S.sel) s = "";
  const url = s ? "#" + encodeURIComponent(s) : location.pathname;
  replace ? history.replaceState(null, "", url) : history.pushState(null, "", url);
  fromHash();
}

function rows(title, list, m) {
  if (!list || !list.length) return "";
  return `<div class="rows"><h3>${esc(title)}</h3>` + list.slice(0, 2).map(r => {
    const id = r.id || "", ns = r.id ? r.at_ns : msgNs(r), h = HUES[Math.max(0, m.people.indexOf(r.who)) % HUES.length];
    return `<a class="hue" style="--h:${h}" href="/${id ? "#" + id : ""}"><span class="t">${esc(r.text)}</span><span class="m"><b>${esc(r.who)}</b> ${ago(ns)}</span></a>`;
  }).join("") + "</div>";
}
function pane() {
  const m = S.m, s = S.sel, n = step();
  if (n) {
    const real = n === 6 && m && m.results[0] ? rows("The newest result", [m.results[0]], m) : "";
    return `<div class="steps" aria-hidden="true">${WALK.map((_, i) => `<i class="${i < n ? "done" : ""}"></i>`).join("")}</div>` +
      `<p class="cap">${WALK[n - 1]}</p>${real}<div class="nav">` +
      `<button data-step="${n - 1}"${n === 1 ? " disabled" : ""}>Back</button>` +
      `<button class="next" data-step="${n + 1}">${n === 7 ? "Done" : "Next"}</button><span>${n} of 7</span></div>`;
  }
  if (!s) return "";
  const head = (name, hue) => `<div class="dhead"><h2${hue == null ? "" : ` class="hue" style="--h:${hue}"`}>${esc(name)}</h2><button class="close" data-go="${esc(s)}">Close</button></div>`;
  if (s.startsWith("p-")) {
    const who = s.slice(2), i = m.people.indexOf(who), mine = m.live.filter(r => r.who === who).sort((a, b) => b.at_ns - a.at_ns);
    const branches = new Set(S.data.items.filter(r => r.who === who && r.branch).map(r => r.branch)).size;
    return head(who, HUES[i % HUES.length]) +
      `<p class="lead">${m.agents[i].length} agent sessions on ${branches} git ${branches === 1 ? "branch" : "branches"}, all posting to one board.</p>` +
      rows(`${mine.length} items on the board`, mine, m);
  }
  const t = TEXT[s], r = t.rows && m ? t.rows(m) : null;
  return head(t.name) + `<p class="lead">${t.lead}</p><ul class="facts">${t.facts.map(x => `<li>${x}</li>`).join("")}</ul>` + (r ? rows(r.title, r.list, m) : "");
}
function show() {
  const on = lit(), svg = $("svg"), m = S.m;
  svg.classList.toggle("has-focus", !!on);
  svg.querySelectorAll(".part").forEach(p => p.classList.toggle("on", !!on && on.includes(p.dataset.part)));
  $("page").classList.toggle("open", !!S.sel);
  const who = S.sel && S.sel.startsWith("p-") ? S.sel.slice(2) : null;  // one person selected: only that person's items stay lit
  svg.querySelectorAll(".dot").forEach(d => d.classList.toggle("off", !!who && d.dataset.who !== who));
  $("finds").innerHTML = (S.data && S.data.findings || []).map(x => `<a href="/finding/${esc(x.slug)}" title="${esc(x.line)}">${esc(x.title)}</a>`).join("");
  $("pane").innerHTML = pane();
  $("status").className = "status" + (S.error ? " bad" : "");
  $("status").textContent = S.error ? (S.readAt ? `Offline, last read ${new Date(S.readAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : "Offline")
    : S.data ? (m.last && !narrow.matches ? `Live, last post ${ago(m.last)}` : "Live") : "Reading the board";
}

function read(d) {
  const first = !S.data;
  S.data = d; S.m = model(d);
  const key = narrow.matches + "|" + S.m.people.map((p, i) => p + ":" + S.m.agents[i].length + ":" + S.m.marks[i].join("")).join(",");
  if (key !== S.key) { S.key = key; draw(); }
  dots();
  if (S.seen) {
    d.items.filter(i => i.listed !== "work-closed" && !S.seen.has(i.id)).forEach(i => S.queue.push({ kind: "board", who: i.who }));
    d.messages.filter(x => !S.seen.has(x.sk)).forEach(x => S.queue.push({ kind: "msg", who: x.who }));
    S.queue = S.queue.slice(-8);
  }
  S.seen = new Set([...d.items.map(i => i.id), ...d.messages.map(x => x.sk)]);
  if (first) fromHash(); else show();
}
function poll() {
  fetch("/data").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(d => { S.error = null; S.readAt = Date.now(); read(d); })
    .catch(e => { S.error = e; console.error(e); show(); })
    .finally(() => setTimeout(poll, 10000));
}

document.addEventListener("click", e => {
  const b = e.target.closest("[data-step]");
  if (b) { const n = Number(b.dataset.step); return go(n >= 1 && n <= 7 ? "walk-" + n : "", true); }
  const t = e.target.closest("[data-go]");
  if (t) { e.preventDefault(); go(t.dataset.go); }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const n = step(), t = e.target.closest?.("svg [data-go]");
  if (t && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); return go(t.dataset.go); }
  if (e.key === "Escape" && S.sel) return go(S.sel);
  if (e.key === "ArrowRight" && (n || !S.sel)) { e.preventDefault(); go(n === 7 ? "" : "walk-" + (n + 1), !!n); }
  if (e.key === "ArrowLeft" && n > 1) { e.preventDefault(); go("walk-" + (n - 1), true); }
});
addEventListener("hashchange", fromHash);
narrow.addEventListener("change", () => { S.key = ""; if (S.data) read(S.data); else { draw(); show(); } });
const stage = document.querySelector(".stage");  // the view leans a few degrees toward a mouse, and settles back
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1;
  V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });
draw();
show();
poll();
if (!still.matches) requestAnimationFrame(spin);
</script>
</body>
</html>
"""
