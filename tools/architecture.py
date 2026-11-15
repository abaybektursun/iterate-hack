"""One interactive picture of the shared work setup, for a first-time reader, and the site's visual reference.

It was the Design page (/architecture, a header tab) until 2026-11-15. Now demo_deck.py embeds PAGE as the deck's
picture /demo/fig/harness (the slide /demo#harness) with its header, words column and key hidden, and /architecture
leads there; the tokens, light and projection here are the ones the other pages copy. The page reads the same /data as the board page every 10 s and draws the
setup as a small three-dimensional object seen from slightly above. The board is the dome in the centre with one
dot per live item. Each person has a swarm of agents beside it with threads to the board: one mark per agent
session, the Claude mark for Claude Code and the OpenAI mark for Codex, in the person's color of the board page.
The Chat ring (messages) runs through every swarm, and the Retro loop (self-review) with its comet goes around
everything. What moves is real data, replayed: a message leaves its sender's swarm for the others, a post
travels to the board and a ripple returns to every swarm. While an event plays, its first words are typed beside the
person whose agent wrote it, with its age, and the mark of that agent swells once; the words are placed and cut so
that no ring passes through them. A larger dot with a halo is
happening now, and its age reads "now". The status at the top right counts the seconds since the last post, and its
dot beats on every read of /data. The picture
stands alone in the middle of the page with one button at the bottom right; one sentence (under the picture, above it
on a phone) says what the picture is, with the live number of people and of agent sessions. On a phone the picture
runs to the screen's edges. A click on a part dims the rest, moves the picture
over and explains the part in a column beside it (address /architecture#<part>); the button "Follow one result"
steps through the path of one result (arrow keys, Esc). The logos of past.dev (memory) and Exa (search) sit on the
key's row, and a click on either explains it in the same column. Nothing here writes to the board.
"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Design</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* Orbital depth. Dark is the hero: one lit glass body in a dark room. Light is the same object as white porcelain
   on a cool grey table, with a cast shadow in place of the glow. The light comes from the upper left in both. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #cbd2d8;
  --blue: #1f43d6; --red: #c41e34; --on-blue: #fff;
  --pl: .50; --pc: .15; --dim: .16;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue); --lift: 38%;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18); --btn-drop: rgba(16, 24, 32, .42);
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
@keyframes heart { from { box-shadow: 0 0 0 0 color-mix(in srgb, var(--blue) 70%, transparent); } }
.status.read::before { animation: heart 1.1s ease-out; }  /* one beat for every read of the board */

/* The picture */
.stage { grid-column: 1; grid-row: 2; min-height: 0; min-width: 0; display: flex; padding: 8px 0 0; }
.foot { grid-column: 1; grid-row: 3; display: flex; justify-content: flex-end; padding-top: 6px; }
.page.open .foot, .page.open .say { visibility: hidden; }
.say {  /* the page's one sentence: what the picture is. At most two lines, so that the picture never reflows */
  grid-column: 1; grid-row: 3; align-self: center; margin: 0 230px 0 0; max-height: 2.5em; overflow: hidden;
  font-size: clamp(16px, 1.3vw, 20px); line-height: 1.25; font-weight: 300; font-stretch: 102%; letter-spacing: -.008em; text-wrap: balance;
}
svg { width: 100%; height: 100%; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); text-anchor: middle; font-stretch: 112%; letter-spacing: .012em; }
.label { font-weight: 600; paint-order: stroke fill; stroke: var(--paper); stroke-width: 10px; stroke-linejoin: round; }
.label.plain { stroke: none; }
.who { font-weight: 560; fill: var(--c); paint-order: stroke fill; stroke: var(--paper); stroke-width: 7px; stroke-linejoin: round; }
.part { transition: opacity .28s ease; }
[data-go] { cursor: pointer; }
svg [data-go]:focus { outline: none; }  /* no rectangle around a clicked part; the keyboard focus shows on its ring */
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
.logo { fill: var(--ink); }
svg [data-go]:focus-visible .logo { fill: var(--blue); }
.said { font-weight: 470; fill: var(--c); text-anchor: start; pointer-events: none; paint-order: stroke fill; stroke: var(--paper); stroke-width: 7px; stroke-linejoin: round; }
.said .when { fill: var(--mute); }
.said .when.now { fill: var(--blue); }
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
.enter .thread, .enter .tie, .enter .beads, .enter .label, .enter .who, .enter .sub, .enter .key .dot, .enter .key .agent, .enter .tool {
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
  padding: clamp(20px, 7vh, 96px) 0 0 40px; box-shadow: inset 1px 0 var(--rule);  /* a border would make the closed column 41px wide, 1px more than the page's padding hides */
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
  .page { display: block; height: auto; padding: 16px 16px 40px; overflow-x: clip; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }  /* the status goes to a second line where the tabs fill the first */
  .name { font-stretch: 112%; margin-right: 0; }
  .stage { margin: 10px -16px 0; padding: 0; }  /* to the screen's edges, so that the picture's text reaches 11 to 12 px */
  .say, .page.open .say { visibility: visible; margin: 18px 0 0; max-height: none; font-size: 21px; line-height: 1.22; }
  svg { height: auto; }
  .foot { padding-top: 14px; justify-content: center; }
  .page.open .foot { display: none; }
  .side { padding: 12px 0 0; overflow: visible; box-shadow: none; }
  .pane { min-width: 0; }
}
@media (prefers-reduced-motion: reduce) {
  .enter *, .dot.arrived, .dot.ping, .status.read::before { animation: none !important; }
  .part, .walk { transition: none; }
}
</style>
</head>
<body>
<div class="page" id="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture" aria-current="page">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings">Findings</a>
    <span class="status" id="status">Reading the board</span>
  </header>
  <p class="say" id="say">People and their coding agents share one board: every agent reads it and posts to it.</p>
  <div class="stage"><svg id="svg" role="group" aria-label="The harness: people and their agents around one shared board"></svg></div>
  <div class="foot"><button class="walk" data-go="walk-1">Follow one result</button></div>
  <div class="side" id="side">
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const $ = id => document.getElementById(id);
const HUES = [325, 150, 65, 195, 105, 45, 175, 350];  // the board page's colors: the same person has the same color on both
const S = { data: null, m: null, g: null, error: null, readAt: 0, sel: null, key: "", seen: null, entered: false, token: 0, queue: [], flying: false };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1);
const msgNs = m => Number(m.sk.slice(0, 20));
const mins = ns => Math.max(0, Math.floor((Date.now() * 1e6 - Number(ns)) / 60e9));
const since = ns => { const s = Math.max(0, Math.floor(Date.now() / 1000 - Number(ns) / 1e9)); return s < 60 ? s + " s ago" : s < 3600 ? `${Math.floor(s / 60)} min ${String(s % 60).padStart(2, "0")} s ago` : ago(ns); };
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
  memory: {
    name: "Memory",
    lead: `The team's memory is one <a href="/pastdev">past.dev</a> project. An agent searches it before it starts an idea.`,
    facts: ["Every result and every knowledge post on the board is stored there.", "A finding from a paper is stored with a quote from it, and only if the quote appears in the paper's text.", "When a Claude Code session ends, its typed prompts and the agent's replies are stored. Tool output and file contents are not sent."],
  },
  search: {
    name: "Search",
    lead: `Agents search the web and the literature with <a href="/exa">Exa</a>, and read the pages they find.`,
    facts: ["Before a new measurement, an agent searches for published work on the same question.", "If a published table already answers the question, the agent posts that finding and does not run the experiment."],
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
/* The two services agents call, drawn as their logos on the key's row: past.dev's site header logo and exa.ai's
   logo, redrawn in one color. base is where the letters' baseline sits, as a fraction of the height; tall is the
   drawn height in key font sizes. */
const LOGOS = {
  past: { box: "154 88 406.09 73.39", w: 406.09, h: 73.39, base: .766, tall: 1.12, body: `<path d="M154 117h36.94v14.53H154zM205.47 117h14.53v14.53h-14.53zM536.195 144.213l-14.756-39.349h8.198l11.165 31.854 11.242-31.854h8.042l-14.678 39.349h-9.213ZM499.143 145.15c-3.747 0-7.078-.859-9.993-2.576s-5.205-4.112-6.871-7.183c-1.613-3.071-2.42-6.636-2.42-10.696 0-4.164.807-7.782 2.42-10.852 1.666-3.123 3.956-5.544 6.871-7.261 2.915-1.77 6.298-2.655 10.15-2.655 3.851 0 7.156.859 9.915 2.577s4.893 4.007 6.402 6.87c1.509 2.811 2.264 5.934 2.264 9.369 0 .52-.026 1.093-.078 1.718 0 .572-.026 1.223-.078 1.951h-32.166v-5.543h24.515c-.156-3.279-1.249-5.829-3.279-7.651-2.03-1.874-4.555-2.811-7.573-2.811-2.135 0-4.086.495-5.856 1.484-1.77.937-3.201 2.342-4.294 4.216-1.041 1.821-1.562 4.138-1.562 6.948v2.186c0 2.915.521 5.387 1.562 7.417 1.093 1.978 2.524 3.488 4.294 4.529 1.77.989 3.695 1.483 5.777 1.483 2.499 0 4.555-.546 6.168-1.639 1.614-1.094 2.811-2.577 3.592-4.451h7.807c-.677 2.395-1.822 4.555-3.435 6.48-1.614 1.874-3.618 3.358-6.012 4.451-2.342 1.093-5.049 1.639-8.12 1.639ZM449.196 145.15c-3.747 0-7.053-.885-9.915-2.654-2.863-1.822-5.101-4.268-6.715-7.339-1.561-3.123-2.342-6.663-2.342-10.618 0-4.008.781-7.548 2.342-10.618 1.614-3.071 3.852-5.492 6.715-7.261 2.914-1.822 6.246-2.733 9.993-2.733 3.071 0 5.778.625 8.12 1.874 2.342 1.197 4.164 2.915 5.465 5.153V88h7.808v56.213h-7.027l-.781-6.089c-.781 1.197-1.796 2.342-3.045 3.435-1.249 1.041-2.758 1.9-4.528 2.576s-3.8 1.015-6.09 1.015Zm1.249-6.792c2.447 0 4.607-.573 6.48-1.718s3.306-2.758 4.295-4.84c1.041-2.082 1.561-4.503 1.561-7.261s-.52-5.153-1.561-7.183c-.989-2.082-2.421-3.696-4.295-4.841-1.873-1.197-4.033-1.795-6.48-1.795-2.342 0-4.45.598-6.324 1.795-1.873 1.145-3.331 2.759-4.372 4.841-1.041 2.03-1.561 4.424-1.561 7.183s.52 5.179 1.561 7.261 2.499 3.695 4.372 4.84c1.874 1.145 3.982 1.718 6.324 1.718ZM418.057 144.604c-1.509 0-2.759-.469-3.748-1.406-.937-.989-1.405-2.16-1.405-3.513 0-1.405.468-2.576 1.405-3.513.989-.989 2.239-1.484 3.748-1.484s2.733.495 3.669 1.484c.937.937 1.406 2.108 1.406 3.513 0 1.353-.469 2.524-1.406 3.513-.936.937-2.16 1.406-3.669 1.406ZM399.532 144.213c-2.498 0-4.658-.39-6.48-1.171s-3.227-2.082-4.216-3.904c-.989-1.821-1.483-4.294-1.483-7.417V111.5h-6.793v-6.636h6.793l.936-9.837h6.871v9.837h11.165v6.636H395.16v20.3c0 2.238.468 3.773 1.405 4.606.937.781 2.551 1.171 4.841 1.171h4.528v6.636h-6.402ZM360.242 145.15c-3.331 0-6.246-.546-8.744-1.639s-4.476-2.629-5.934-4.607c-1.457-1.978-2.342-4.294-2.654-6.948h7.963c.261 1.249.755 2.394 1.484 3.435.781 1.041 1.822 1.874 3.123 2.498 1.353.625 2.941.937 4.762.937 1.718 0 3.123-.234 4.216-.702 1.145-.521 1.978-1.198 2.499-2.03.52-.885.78-1.822.78-2.811 0-1.457-.364-2.55-1.093-3.279-.676-.781-1.717-1.379-3.123-1.796-1.353-.468-2.992-.885-4.918-1.249-1.822-.312-3.592-.729-5.309-1.249-1.666-.573-3.175-1.275-4.529-2.108-1.301-.833-2.342-1.874-3.122-3.123-.781-1.301-1.172-2.889-1.172-4.763 0-2.238.599-4.242 1.796-6.011 1.197-1.822 2.889-3.227 5.075-4.216 2.238-1.041 4.867-1.562 7.885-1.562 4.373 0 7.886 1.041 10.54 3.123 2.655 2.082 4.216 5.023 4.685 8.822h-7.573c-.209-1.769-.989-3.123-2.343-4.059-1.353-.989-3.149-1.484-5.387-1.484s-3.955.443-5.153 1.327c-1.197.885-1.795 2.056-1.795 3.514 0 .937.338 1.769 1.015 2.498s1.665 1.353 2.967 1.874c1.353.468 2.992.911 4.918 1.327 2.759.521 5.231 1.171 7.417 1.952s3.93 1.926 5.231 3.435 1.952 3.67 1.952 6.48c.052 2.447-.573 4.607-1.874 6.481-1.249 1.873-3.045 3.331-5.387 4.372-2.29 1.041-5.023 1.561-8.198 1.561ZM314.597 145.15c-3.227 0-5.908-.546-8.042-1.639s-3.721-2.551-4.762-4.372c-1.041-1.874-1.562-3.878-1.562-6.012 0-2.603.677-4.815 2.03-6.636 1.354-1.874 3.279-3.306 5.778-4.295s5.491-1.483 8.978-1.483h10.228c0-2.29-.338-4.19-1.015-5.699-.677-1.51-1.691-2.629-3.045-3.358-1.301-.78-2.967-1.171-4.997-1.171-2.342 0-4.346.573-6.011 1.718-1.666 1.093-2.707 2.733-3.123 4.919h-7.808c.313-2.759 1.25-5.101 2.811-7.027 1.614-1.978 3.67-3.487 6.168-4.528 2.498-1.093 5.153-1.64 7.963-1.64 3.696 0 6.793.651 9.291 1.952s4.372 3.149 5.622 5.543c1.301 2.342 1.951 5.153 1.951 8.432v24.359h-6.792l-.625-6.636c-.572 1.041-1.249 2.03-2.029 2.967-.781.937-1.718 1.743-2.811 2.42-1.041.677-2.264 1.197-3.67 1.562-1.353.416-2.862.624-4.528.624Zm1.483-6.324c1.666 0 3.175-.338 4.529-1.015 1.353-.676 2.498-1.587 3.435-2.732.989-1.197 1.718-2.525 2.186-3.982.521-1.51.807-3.045.859-4.606v-.235h-9.291c-2.238 0-4.06.287-5.465.859-1.353.521-2.342 1.249-2.967 2.186-.624.937-.937 2.03-.937 3.279 0 1.302.286 2.421.859 3.357.625.885 1.509 1.588 2.655 2.108 1.145.521 2.524.781 4.137.781ZM252 161.39v-56.526h7.027l.78 6.09c.833-1.197 1.874-2.316 3.123-3.357 1.25-1.093 2.733-1.978 4.451-2.655 1.769-.677 3.825-1.015 6.167-1.015 3.748 0 7.027.911 9.838 2.733 2.862 1.821 5.075 4.294 6.636 7.417 1.614 3.071 2.42 6.584 2.42 10.54s-.806 7.495-2.42 10.618c-1.613 3.071-3.852 5.491-6.714 7.261-2.811 1.769-6.09 2.654-9.838 2.654-3.071 0-5.777-.598-8.119-1.796-2.343-1.249-4.19-2.966-5.544-5.152v23.188H252Zm20.221-23.032c2.394 0 4.502-.573 6.324-1.718 1.874-1.145 3.331-2.758 4.372-4.84 1.093-2.082 1.64-4.503 1.64-7.261s-.547-5.153-1.64-7.183c-1.041-2.082-2.498-3.696-4.372-4.841-1.822-1.197-3.93-1.795-6.324-1.795-2.446 0-4.606.598-6.48 1.795-1.822 1.145-3.253 2.759-4.294 4.841-1.041 2.03-1.562 4.424-1.562 7.183s.521 5.179 1.562 7.261 2.472 3.695 4.294 4.84c1.874 1.145 4.034 1.718 6.48 1.718Z"/>` },
  exa: { box: "0 0 413 129", w: 413, h: 129, base: .888, tall: .86, body: `<path fill-rule="evenodd" d="M106.417 9.30741C106.417 9.57392 106.324 9.83227 106.155 10.0388L61.5395 64.5L106.155 118.96C106.324 119.166 106.417 119.425 106.417 119.691V127.843C106.417 128.482 105.897 129 105.255 129H1.16175C0.520132 129 0 128.482 0 127.843V1.15695C0 0.517982 0.520131 0 1.16174 0H105.255C105.897 0 106.417 0.517984 106.417 1.15695V9.30741ZM19.0364 116.382H87.6921L53.363 74.4795L19.0364 116.382ZM12.6699 104.192L40.1426 70.6585H12.6699V104.192ZM12.6699 58.0409H39.8964L12.6699 24.8064V58.0409ZM53.363 54.5193L87.6921 12.6176H19.0364L53.363 54.5193Z"/><path d="M176.198 117.65C166.094 117.65 157.323 115.553 149.886 111.36C142.589 107.167 136.905 101.017 132.835 92.9109C128.906 84.8045 126.941 75.0208 126.941 63.5599C126.941 53.3569 128.976 44.2022 133.046 36.0957C137.256 27.9892 143.01 21.6298 150.307 17.0175C157.744 12.4052 166.024 10.099 175.146 10.099C185.109 10.099 193.599 12.3353 200.616 16.8078C207.633 21.1406 212.965 27.3602 216.614 35.4667C220.263 43.4334 222.087 52.8677 222.087 63.7695V66.1766C222.087 66.8156 221.567 67.3336 220.925 67.3336H145.044C145.185 74.881 146.588 81.3802 149.254 86.8311C152.061 92.282 155.78 96.475 160.411 99.4101C165.182 102.205 170.515 103.603 176.409 103.603C183.285 103.603 189.179 102.066 194.091 98.9908C198.779 95.9225 201.741 91.008 202.977 84.2471C203.08 83.6853 203.565 83.267 204.139 83.267H219.737C220.429 83.267 220.969 83.8669 220.871 84.5494C220.038 90.3376 217.988 95.6406 214.72 100.458C211.211 105.63 206.159 109.823 199.564 113.037C193.108 116.112 185.32 117.65 176.198 117.65ZM202.721 54.5449C202.721 45.3203 200.265 37.9825 195.354 32.5316C190.582 27.0807 183.846 24.3552 175.146 24.3552C166.866 24.3552 160.06 27.2205 154.727 32.9509C149.395 38.6814 146.377 45.8794 145.676 54.5449H202.721ZM364.585 117.65C358.13 117.65 352.236 116.392 346.903 113.876C341.571 111.36 337.361 107.796 334.273 103.184C331.186 98.4317 329.642 92.9808 329.642 86.8311C329.642 77.7462 332.73 70.688 338.904 65.6564C345.219 60.485 353.359 57.0607 363.322 55.3835L385.004 52.0291C387.67 51.6098 389.705 51.0507 391.108 50.3519C392.652 49.5133 393.704 48.465 394.266 47.2071C394.967 45.8095 395.318 44.0624 395.318 41.9659C395.318 36.515 393.424 32.2521 389.635 29.1772C385.846 25.9626 380.934 24.3552 374.9 24.3552C367.322 24.3552 361.498 26.2421 357.428 30.0158C353.595 33.4387 351.443 38.1016 350.971 44.0046C350.922 44.622 350.412 45.1106 349.79 45.1106H334.014C333.353 45.1106 332.823 44.5605 332.872 43.9032C333.312 38.0771 335.042 32.6792 338.062 27.7096C341.29 22.3985 345.921 18.1356 351.955 14.921C358.13 11.7063 365.287 10.099 373.426 10.099C381.706 10.099 388.793 11.6364 394.687 14.7113C400.721 17.7862 405.282 22.1888 408.369 27.9193C411.456 33.6497 413 40.4284 413 48.2554V113.348C413 113.987 412.48 114.505 411.838 114.505H396.901C396.259 114.505 395.739 113.987 395.739 113.348V109.473C395.739 108.076 395.739 106.678 395.739 105.28C395.739 103.743 395.739 102.275 395.739 100.878C393.213 106.189 389.214 110.312 383.741 113.247C378.408 116.182 372.023 117.65 364.585 117.65ZM367.111 103.603C372.444 103.603 377.215 102.485 381.425 100.249C385.775 97.8727 389.143 94.6581 391.529 90.6048C394.055 86.4118 395.318 81.6597 395.318 76.3486V61.4634C394.757 62.302 393.564 63.0707 391.74 63.7695C389.915 64.4684 387.389 65.1672 384.162 65.866L369.427 68.5915C362.971 69.8494 357.849 71.9459 354.06 74.881C350.271 77.8161 348.377 81.7995 348.377 86.8311C348.377 91.8627 350.131 95.916 353.639 98.9908C357.288 102.066 361.779 103.603 367.111 103.603ZM285.673 62.9573L325.127 112.948C325.726 113.707 325.183 114.82 324.213 114.82H305.929C305.572 114.82 305.235 114.657 305.015 114.378L275.053 76.414L245.093 114.378C244.872 114.657 244.536 114.82 244.179 114.82H225.893C224.924 114.82 224.381 113.707 224.98 112.948L264.433 62.9573L227.177 15.7512C226.578 14.9921 227.121 13.8793 228.091 13.8793H246.375C246.732 13.8793 247.068 14.0423 247.289 14.3214L275.053 49.5006L302.818 14.3214C303.038 14.0423 303.375 13.8793 303.731 13.8793H322.016C322.985 13.8793 323.528 14.9921 322.929 15.7512L285.673 62.9573Z"/>` },
};

/* Geometry: everything hangs on one centre, and the moving parts live in a small 3D space around it (x right,
   y down, z toward the viewer). The board faces the viewer. The swarms sit on one circle in the people's plane,
   seen from a little above; that circle is the messages path, so it passes through every swarm. The self-review
   loop is a larger circle in its own plane. A plane is [inclination, turn on the screen]. sw is the radius of the
   largest swarm; a mark is at most `mark` wide, and marks stand `pack` times their width apart or more, so that
   they never cover each other while the swarm turns. The first words of an event are set in size fq, at most
   `chars` characters (fewer where the room is smaller, see row); age says whether its age follows. fk is the size
   of the key. The phone's sizes are chosen to be 11 px or more on a screen 375 px wide. */
const RAD = Math.PI / 180;
function plane(inc, turn) { return { c: Math.cos(inc * RAD), s: Math.sin(inc * RAD), co: Math.cos(turn * RAD), so: Math.sin(turn * RAD) }; }
function geo() {
  const g = narrow.matches
    ? { w: 720, h: 742, cx: 360, cy: 290, rb: 100, rq: 200, rp: 274, rr: 338, fs: 25, fw: 23, fk: 22, D: 1900, sw: 50, over: 26, cmax: 23, mark: 21, pack: 1.01, fq: 22, chars: 16, age: 0, pp: [34, 0], pr: [30, -4] }  // a rounder Retro loop, so the lowest name fits inside it
    : { w: 1140, h: 985, cx: 570, cy: 404, rb: 164, rq: 340, rp: 446, rr: 540, fs: 24, fw: 18.5, fk: 17, D: 2100, sw: 88, over: 45, cmax: 27, mark: 25, pack: 1.06, fq: 16.5, chars: 30, age: 1, pp: [40, 0], pr: [36, -4] };
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
  const part = (name, go, body, label, cls) =>
    `<g class="part${cls ? " " + cls : ""}" data-part="${name}"${go ? ` data-go="${go}"` : ""}${label ? ` role="button" tabindex="0" aria-label="${label}"` : ""}>${body}</g>`;
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
    Object.keys(LOGOS).map(k => `<symbol id="logo-${k}" viewBox="${LOGOS[k].box}">${LOGOS[k].body}</symbol>`).join("") +
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
      `<text class="who" font-size="${g.fw}">${esc(m.people[i])}</text>` +
      `<text class="said" font-size="${g.fq}" opacity="0" aria-hidden="true"><tspan></tspan><tspan class="when"></tspan></text></g>`,
      `${esc(m.people[i])}, ${m.agents[i].length} agents`);
  });
  const k = g.fk, z = k / 17, ty = g.h - 14, ky = narrow.matches ? ty - k * 1.9 : ty, keys = [["agent", "agent"], ["work", "open work"], ["", "result"], ["note", "idea or note"]];
  const here = m ? ["claude", "openai", ""].filter(x => m.marks.some(l => l.includes(x))) : ["claude"];  // the marks on this page
  const widths = keys.map(([cls, t]) => 48 * z + t.length * k * .54 + (cls === "agent" ? (here.length - 1) * 19 * z : 0)), total = widths.reduce((a, b) => a + b, 0) - 22 * z;  // z: the glyphs grow with the key's text
  let kx = narrow.matches ? (g.w - total) / 2 : 6;
  out += `<g class="part key" data-part="key" style="--c:var(--mute)">` + keys.map(([cls, t], i) => {
    const x = kx, y = ky - k * .32; kx += widths[i];
    const one = (mark, j) => mark ? `<use class="agent" href="#mark-${mark}" x="${f(x + (j * 19 - 1) * z)}" y="${f(y - 8 * z)}" width="${f(16 * z)}" height="${f(16 * z)}"/>`
      : `<rect class="agent" x="${f(x + j * 19 * z)}" y="${f(y - 6.5 * z)}" width="${f(13 * z)}" height="${f(13 * z)}" rx="${f(3.6 * z)}"/>`;
    return (cls === "agent" ? here.map(one).join("") : `<circle class="dot ${cls}" cx="${f(x + 7 * z)}" cy="${f(y)}" r="${f((cls === "note" ? 3.4 : 6) * z)}"/>`) +
      `<text class="sub" x="${f(x + (20 + (cls === "agent" ? (here.length - 1) * 19 : 0)) * z)}" y="${f(ky)}" font-size="${f(k)}" style="text-anchor:start">${t}</text>`;
  }).join("") + "</g>";
  /* The services agents call: a label, then the logo, on the key's baseline. Laid out right to left from the right
     edge; on a phone they take their own row under the key, centred. Each has an invisible rectangle to click that
     is 40 px tall on the screen. */
  const box = svg.getBoundingClientRect(), tall = 40 / (Math.min(box.width / g.w, box.height / g.h) || .7);
  const tools = [["memory", "past", "Memory, past.dev"], ["search", "exa", "Search, Exa"]].map(([name, logo, label]) => {
    const L = LOGOS[logo], lh = L.tall * k;
    return { name, logo, label, L, lh, lw: lh * L.w / L.h, tw: name.length * k * .54 };
  });
  const span = tools.reduce((s, o) => s + o.tw + 8 * z + o.lw, 0) + 26 * z * (tools.length - 1);
  let tx = narrow.matches ? (g.w + span) / 2 : g.w - 6;
  const drawn = [];
  for (let i = tools.length - 1; i >= 0; i--) {
    const o = tools[i], lx = tx - o.lw, ly = ty - o.L.base * o.lh, sx = lx - 8 * z - o.tw, bot = Math.max(ty + k * .25, ly + o.lh) + 8, top = Math.min(ty - k * .8 - 8, ly - 8, bot - tall);
    drawn.unshift(part(o.name, o.name,
      `<rect class="pad" x="${f(sx - 8)}" y="${f(top)}" width="${f(tx - sx + 16)}" height="${f(bot - top)}"/>` +
      `<text class="sub" x="${f(lx - 8 * z)}" y="${f(ty)}" font-size="${f(k)}" style="text-anchor:end">${o.name}</text>` +
      `<use class="logo" href="#logo-${o.logo}" x="${f(lx)}" y="${f(ly)}" width="${f(o.lw)}" height="${f(o.lh)}"/>`, o.label, "tool"));
    tx = sx - 26 * z;
  }
  out += drawn.join("");
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
        person: p.querySelector(".person"), who, said: p.querySelector(".said"), thread: t.querySelector(".thread"), ripple: t.querySelector(".ripple"), pulse: unit(t.querySelector(".pulse")) };
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
  R.loop = loop; R.chat = ring(g.PP, g.rq, 0, 360, 48);  // row() keeps the first words of an event clear of these
  E["ms-hit"].setAttribute("d", line(R.chat) + "Z");
  fade(E.msgfade, g.PP, g.rq);
  const crown = at(g.PP, g.rq, -90);
  set(E["ms-label"], { x: f(crown[0]), y: f(crown[1] + g.fs * .34) });

  // The swarms: each a small disc of agents in the people's plane, with threads to the nearest point of the board.
  const Y = S.play.say;
  R.swarms.forEach((o, n) => {
    const u0 = g.rq * Math.cos(o.a * RAD), v0 = g.rq * Math.sin(o.a * RAD);
    const c = proj(g, world(g.PP, u0, v0)), p = at(g.PP, g.rp, o.a), to = Math.atan2(c[1] - g.cy, c[0] - g.cx);
    const end = [g.cx + (g.rb + 2) * Math.cos(to), g.cy + (g.rb + 2) * Math.sin(to)], ends = f(end[0]) + " " + f(end[1]);
    let web = o.dots.length ? "" : `M${f(c[0])} ${f(c[1])}L${ends}`, fan = o.dots.length ? "" : `M${ends}L${f(c[0])} ${f(c[1])}`;
    o.c0 = c; o.end = end; o.at = []; o.reach = Math.hypot(c[0] - end[0], c[1] - end[1]);
    o.dots.forEach((d, k) => {
      const r = o.c * Math.sqrt(k + .6), a = k * 2.39996 + t * .22;  // the swarm turns as one, so its agents never cover each other
      const q = proj(g, world(g.PP, u0 + r * Math.cos(a), v0 + r * Math.sin(a))), here = f(q[0]) + " " + f(q[1]);
      const swell = Y && Y.i === n && Y.k === k ? 1 + .8 * Math.sin(Math.PI * Math.min(1, (t - Y.t0) / .7)) : 1;  // the agent that is speaking
      const side = o.size * q[2] * (d.tagName === "rect" ? .78 : 1) * swell;
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
    o.nx = p[0] - o.side * Math.max(0, o.wide / 2 - g.over); o.ny = p[1] + (o.below ? g.fw * 1.9 : -g.fw * 1.15) * p[2]; o.nk = p[2];
    set(o.who, { x: f(o.nx), y: f(o.ny) });
  });
  const turn = $("dots");
  if (turn) turn.setAttribute("transform", `rotate(${f(t * 1.5 % 360)} ${g.cx} ${g.cy})`);
  posted(t);
  sent(t, at, ring, near);
  said(t);
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

/* The replay: about every 2.5 s one real event, a message and a post in turn, from the newest 40 of each, newest
   first, looped. While an event plays, its first words are typed beside the person whose agent wrote it, with its
   age ("4 min ago", or "now" in the accent), and the mark of that agent swells once.
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
function say(i, k, text, ns, t, hold) {  // the first words of a real message or post, beside whoever wrote it
  const o = S.r.swarms[i], g = S.g, s = String(text ?? "").replace(/\s+/g, " ").trim().replace(/^title:\s*/i, "").replace(/\s+what:.*$/, "");  // a result's text opens with its field names
  if (!o || !s) return;
  S.r.swarms.forEach(x => x.said.setAttribute("opacity", 0));
  const [line, when] = o.said.children, age = g.age ? "\u2002" + ago(ns) : "";  // a phone has no room for the age
  when.setAttribute("class", "when" + (mins(ns) < 1 ? " now" : ""));
  const box = $("svg").getBoundingClientRect(), spare = Math.max(0, box.width / Math.min(box.width / g.w, box.height / g.h) - g.w) / 2;  // the room beside the drawing, in its units
  const Y = { i, k, age, t0: t, hold, spare, wide: 0, n: -1 }, room = row(o, Y).room;
  for (let n = g.chars; ; n -= 2) {  // shorter, until the words fit their room
    const head = s.slice(0, n), whole = head.replace(/\s+\S*$/, "");  // cut at a word, unless that leaves less than half
    Y.cut = s.length > n ? (whole.length * 2 > n ? whole : head).replace(/[,;:(\-]+$/, "") + "…" : s;
    line.textContent = Y.cut; when.textContent = age;
    Y.wide = o.said.getComputedTextLength();  // measured whole, so it does not move while it is typed
    if (Y.wide <= room || n <= 8) break;
  }
  const at = row(o, Y);
  Y.out = at.out; Y.drop = at.drop;  // decided once, so the words do not jump while the view sways
  S.play.say = Y;
}
function crossing(pts, y, side) {  // where a ring crosses the row y on one side of the centre: its outermost x there, or null
  let x = null;
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1], b = pts[i];
    if ((a[1] - y) * (b[1] - y) > 0 || a[1] === b[1]) continue;
    const q = a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]);
    if ((q - S.g.cx) * side > 0 && (x == null || (q - x) * side > 0)) x = q;
  }
  return x;
}
/* Where the first words go: on the line beyond the name, where no ring passes through them. Beside a person at the
   side, the Retro loop crosses that line: the words stand outside the loop when the room there is the larger, and
   otherwise between the loop and the Chat ring (or the ring's name). Under a person at the bottom they move below
   the loop when it would pass through them. room is the width they may take. */
function row(o, Y) {
  const g = S.g, R = S.r, pad = 12, h = g.fq * o.nk, lo = 8 - Y.spare, hi = g.w - 8 + Y.spare, fit = x => Math.max(lo, Math.min(hi - Y.wide, x));
  let y = o.ny + (o.below ? g.fq * 1.5 : -g.fw * 1.3) * o.nk;
  if (!o.side) {
    const x = fit(o.nx - Y.wide / 2), under = R.loop.filter(q => q[0] > x - 30 && q[0] < x + Y.wide + 30).map(q => q[1]);
    const drop = Y.drop ?? under.some(v => v > y - h - 8 && v < y + h * .4 + 8);
    if (drop && under.length) y = Math.max(...under) + 7 + h * .85;
    return { x, y, room: hi - lo, drop };
  }
  const rows = [y - h * .85, y + h * .3], far = l => o.side * Math.max(...l.map(v => v * o.side)), near = l => o.side * Math.min(...l.map(v => v * o.side));
  const loop = rows.map(v => crossing(R.loop, v, o.side)).filter(v => v != null), chat = rows.map(v => crossing(R.chat, v, o.side)).filter(v => v != null);
  const base = o.side < 0 ? o.nx + o.wide / 2 - Y.wide : o.nx - o.wide / 2;  // from the name's inner edge, running away from the board
  if (!loop.length) return { x: fit(base), y, room: hi - lo };
  const edge = o.side > 0 ? hi : lo, a = far(loop) + o.side * pad, b = near(loop) - o.side * pad, c = chat.length ? far(chat) + o.side * pad : g.cx + o.side * 56;
  const outside = (edge - a) * o.side, inside = (b - c) * o.side, out = Y.out ?? outside >= inside;
  const x = out ? (o.side > 0 ? a : a - Y.wide) : o.side > 0 ? Math.min(base, b - Y.wide) : Math.max(base, b);
  return { x: fit(x), y, room: Math.max(outside, inside), out };
}
function said(t) {
  const Y = S.play.say;
  if (!Y) return;
  const o = S.r.swarms[Y.i], age = t - Y.t0;
  if (!o || age >= Y.hold) { if (o) o.said.setAttribute("opacity", 0); S.play.say = null; return; }
  const n = Math.min(Y.cut.length, Math.ceil(age * 55)), [line, when] = o.said.children;  // 55 characters a second
  if (n !== Y.n) { Y.n = n; line.textContent = Y.cut.slice(0, n); when.textContent = n < Y.cut.length ? "" : Y.age; }
  const at = row(o, Y);
  o.said.setAttribute("x", f(at.x));
  o.said.setAttribute("y", f(at.y));
  o.said.setAttribute("opacity", Math.max(0, Math.min(1, age / .15, (Y.hold - age) / .4)).toFixed(2));
}
function hush() {  // stop the replay where it is
  const R = S.r;
  S.play = {};
  if (!R) return;
  R.swarms.forEach(o => { o.pulse.el.setAttribute("opacity", 0); o.ripple.setAttribute("opacity", 0); o.said.setAttribute("opacity", 0); });
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
    const ms = now.kind === "msg" ? 2600 : 1100;
    say(i, m.agents[i].indexOf(now.session), now.text, now.ns, t, ms / 1000 + 1.3);
    fly(route(S.g, now.kind, S.th[i]), HUES[i % HUES.length], ms).then(() => {
      S.busy = false; S.due = S.t + 1.5;
      if (now.kind === "board" && !step()) S.play.post = { i, k: -1, at: -1, t0: S.t - 1 };  // the read that follows the post
    });
    return;
  }
  const msgs = S.data.messages.slice(-40).filter(x => m.people.includes(x.who)), posts = m.live.slice(-40);
  S.turn = !S.turn;
  if (S.turn && m.people.length > 1 && msgs.length) {
    const x = msgs[msgs.length - 1 - S.nth.msg++ % msgs.length], i = m.people.indexOf(x.who), a0 = S.th[i];
    const away = S.th.map((a, j) => ({ j, d: ((a - a0) % 360 + 360) % 360 })).filter(x => x.j !== i);  // degrees to each other swarm, clockwise
    const reach = dir => Math.max(0, ...away.map(x => dir > 0 ? x.d : 360 - x.d).filter(d => d <= 180 && (dir > 0 || d < 180)));
    S.play.msg = { i, t0: t, legs: [1, -1].map(dir => ({ dir, span: reach(dir), time: .9 + reach(dir) / 110 })),
      hits: away.map(x => x.d <= 180 ? { j: x.j, dir: 1, d: x.d, t: 0 } : { j: x.j, dir: -1, d: 360 - x.d, t: 0 }) };
    say(i, m.agents[i].indexOf(x.session), x.text, msgNs(x), t, Math.max(...S.play.msg.legs.map(l => l.time)) + .6);
    S.r.el["ms-fx"].setAttribute("style", `--h:${HUES[i % HUES.length]}`);
    S.r.legs.forEach(u => { u.glow.setAttribute("fill", `url(#glo-${i})`); u.head.setAttribute("style", `fill:url(#orb-${i}) var(--c)`); });
  } else if (posts.length) {
    const it = posts[posts.length - 1 - S.nth.post++ % posts.length], i = Math.max(0, m.people.indexOf(it.who)), count = m.agents[i].length;
    const k = count ? (m.agents[i].indexOf(it.session) + count) % count : -1;  // the thread of the agent session that posted it, when that is known
    S.play.post = { i, k, at: m.live.indexOf(it), t0: t };
    if (m.people.includes(it.who)) say(i, m.agents[i].indexOf(it.session), it.text, it.at_ns, t, 2.4);
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
    memory: ["memory", "board"], search: ["search", ...all("swarm-")],
    "walk-1": post, "walk-2": [...post, "memory", "search"], "walk-3": post, "walk-4": mine, "walk-5": mine, "walk-6": post, "walk-7": ["review"],
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
  $("pane").innerHTML = pane();
  if (m) $("say").textContent = `${m.people.length} ${m.people.length === 1 ? "person" : "people"} and their ${m.nAgents} agent sessions (the marks around each name) share the board in the centre: every agent reads it and posts to it.`;
  clock();
}
function clock() {  // every second: the time since the last post counts up
  const m = S.m;
  $("status").classList.toggle("bad", !!S.error);
  $("status").textContent = S.error ? (S.readAt ? `Offline, last read ${new Date(S.readAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : "Offline")
    : S.data ? (m.last && !narrow.matches ? `Live, last post ${since(m.last)}` : "Live") : "Reading the board";
}

function read(d) {
  const first = !S.data;
  S.data = d; S.m = model(d);
  const key = narrow.matches + "|" + S.m.people.map((p, i) => p + ":" + S.m.agents[i].length + ":" + S.m.marks[i].join("")).join(",");
  if (key !== S.key) { S.key = key; draw(); }
  dots();
  if (S.seen) {
    d.items.filter(i => i.listed !== "work-closed" && !S.seen.has(i.id)).forEach(i => S.queue.push({ kind: "board", who: i.who, session: i.session, text: i.text, ns: i.at_ns }));
    d.messages.filter(x => !S.seen.has(x.sk)).forEach(x => S.queue.push({ kind: "msg", who: x.who, session: x.session, text: x.text, ns: msgNs(x) }));
    S.queue = S.queue.slice(-8);
  }
  S.seen = new Set([...d.items.map(i => i.id), ...d.messages.map(x => x.sk)]);
  if (first) fromHash(); else show();
}
function poll() {
  fetch("/data").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(d => { S.error = null; S.readAt = Date.now(); read(d); const s = $("status"); s.classList.remove("read"); s.offsetWidth; s.classList.add("read"); })
    .catch(e => { S.error = e; console.error(e); show(); })
    .finally(() => setTimeout(poll, 10000));
}

document.addEventListener("click", e => {
  if (e.detail) document.activeElement?.blur?.();  // a mouse click leaves no focus behind, so a later key press draws no blue ring on the part
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
setInterval(clock, 1000);
if (!still.matches) requestAnimationFrame(spin);
</script>
</body>
</html>
"""
