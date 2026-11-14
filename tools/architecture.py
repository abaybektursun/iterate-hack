"""The architecture page of the board site: one interactive picture of the harness, for a first-time reader.

view.py serves PAGE at /architecture. The page reads the same /data as the board page every 10 s and draws:
the board in the centre with one dot per live item, one swarm per person (a dot per agent session, in the
person's color of the board page), the messages ring, memory, runs, and the review loop around everything.
A click on a part dims the rest and explains it in the side column (address /architecture#<part>);
"Follow one result" steps through the path of one result (arrow keys, Esc). Nothing here writes to the board.
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
:root {
  color-scheme: light dark;
  --paper: #eef2ec; --sheet: #f8faf7; --ink: #17201b; --mute: #5f6b64; --faint: #8e9a93; --rule: #d5ddd6;
  --blue: #2448d8; --red: #d2283c;
  --pl: .55; --pc: .13; --dim: .18;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #0e1311; --sheet: #151c19; --ink: #e4ebe6; --mute: #95a39b; --faint: #66736c; --rule: #25302a;
    --blue: #8aa4ff; --red: #ff6577;
    --pl: .76; --pc: .11; --dim: .34;
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
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(300px, 25vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0 48px; height: 100vh; min-height: 620px; max-width: 1840px; margin: 0 auto; padding: 24px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 22px; font-size: 13px; }
.name { font-weight: 700; font-stretch: 112%; font-size: 15px; letter-spacing: .01em; margin: 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }
.status { margin-left: auto; color: var(--mute); white-space: nowrap; display: flex; align-items: center; gap: 8px; }
.status::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--blue); }
.status.bad { color: var(--red); }
.status.bad::before { background: var(--red); }

/* The picture */
.stage { min-height: 0; min-width: 0; display: flex; }
svg { width: 100%; height: 100%; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); text-anchor: middle; font-stretch: 108%; }
.label { font-weight: 620; paint-order: stroke fill; stroke: var(--paper); stroke-width: 12px; stroke-linejoin: round; }
.who { font-weight: 580; fill: var(--c); paint-order: stroke fill; stroke: var(--paper); stroke-width: 8px; stroke-linejoin: round; }
.part { transition: opacity .28s ease; }
[data-go] { cursor: pointer; }
svg [data-go]:focus-visible { outline: none; }
svg [data-go]:focus-visible .ring { stroke: var(--blue); stroke-width: 3; }
.has-focus .part { opacity: var(--dim); }
.has-focus .part.on { opacity: 1; }
.hit { fill: none; stroke: transparent; pointer-events: stroke; }
.pad { fill: transparent; }
.line { fill: none; stroke: var(--ink); stroke-width: 1.5; }
.board-ring { fill: var(--sheet); stroke: var(--ink); stroke-width: 2.4; }
.msg-ring { fill: none; stroke: var(--mute); stroke-width: 1.8; stroke-dasharray: 2 8; stroke-linecap: round; }
[data-part="review"] path { fill: none; stroke: var(--blue); stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
[data-part="review"] .label { fill: var(--blue); }
.thread { stroke: var(--c); stroke-width: 1.3; opacity: .65; }
.tie { stroke: var(--c); stroke-width: 1.2; opacity: .7; }
.agent { fill: var(--c); }
.person { fill: var(--c); stroke: var(--paper); stroke-width: 3; }
.dot { fill: var(--c); }
.dot.note { opacity: .6; }
.dot.work { fill: var(--sheet); stroke: var(--c); stroke-width: 2; }
.dot.stale { stroke: var(--red); }
.glyph { fill: var(--sheet); stroke: var(--ink); stroke-width: 1.8; }
.glyph-ink { fill: var(--ink); stroke: none; }
.gate { fill: var(--ink); stroke: var(--paper); stroke-width: 4; }
.tick { fill: none; stroke: var(--paper); stroke-width: 2.4; stroke-linecap: round; stroke-linejoin: round; }
.sub { fill: var(--mute); font-weight: 480; }
.dot.off { opacity: .12; }
.quote { font-family: Georgia, "Times New Roman", serif; font-weight: 400; }
#fx { pointer-events: none; }
.fly { fill: var(--c); }
.halo { fill: none; stroke: var(--c); stroke-width: 1.5; opacity: .45; }

/* One drawn entrance, then only real events move */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
@keyframes pop { from { transform: scale(0); } }
.dot, .agent, .person { transform-box: fill-box; transform-origin: center; }
.enter .draw { stroke-dasharray: 1; animation: draw 1s cubic-bezier(.6, 0, .2, 1) both; }
.enter [data-part="review"] .draw { animation-delay: .5s; }
.enter .thread, .enter .tie, .enter .msg-ring, .enter .label, .enter .who, .enter .glyph, .enter .glyph-ink, .enter .quote, .enter .line, .enter .gate, .enter .tick, .enter .sub {
  animation: fade .6s .55s both;
}
.enter .agent, .enter .person { animation: pop .45s cubic-bezier(.3, 1.5, .5, 1) both; animation-delay: calc(.25s + var(--i, 0) * 18ms); }
.enter .dot { animation: pop .4s cubic-bezier(.3, 1.4, .5, 1) both; animation-delay: calc(.7s + var(--i, 0) * 7ms); }
.dot.arrived { animation: pop .5s cubic-bezier(.3, 1.6, .5, 1) .9s both; }

/* The words */
.side { min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none; padding-top: clamp(16px, 7vh, 96px); }
.say { margin: 0; font-size: clamp(30px, 2.75vw, 50px); line-height: 1.08; font-weight: 320; font-stretch: 106%; letter-spacing: -.015em; }
.say button { display: block; border-radius: 4px; }
.say b { font-weight: 660; }
.say button:hover, .say button.on { color: var(--blue); }
.ask { display: block; margin-top: 16px; font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; color: var(--mute); max-width: 24ch; }
.ask:hover, .ask.on { color: var(--blue); }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.why { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.why button {
  display: flex; width: 100%; align-items: baseline; justify-content: space-between; gap: 16px;
  padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; font-stretch: 104%;
}
.why button span { color: var(--faint); font-size: 20px; line-height: 1; font-weight: 400; }
.why button:hover { color: var(--blue); }
.walk {
  margin-top: 22px; padding: 10px 18px; border-radius: 999px; background: var(--ink); color: var(--paper);
  font-weight: 600; font-size: 15px; font-stretch: 104%;
}
.walk:hover { background: var(--blue); }

.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 112%; }
.dhead h2.hue { color: var(--c); }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 16px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 420; max-width: 30ch; }
.facts { list-style: none; margin: 16px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; }
.facts li { padding: 7px 0; border-top: 1px solid var(--rule); }
.facts b { color: var(--ink); font-weight: 640; }
.rows { margin-top: 18px; }
.rows h3 { margin: 0 0 2px; font-size: 13px; font-weight: 600; color: var(--mute); }
.rows a { display: block; padding: 8px 0 8px 12px; border-top: 1px solid var(--rule); text-decoration: none; position: relative; font-size: 13.5px; line-height: 1.42; }
.rows a::before { content: ""; position: absolute; left: 0; top: 11px; bottom: 11px; width: 3px; border-radius: 2px; background: var(--c); }
.rows a:hover { background: linear-gradient(to right, var(--sheet), transparent); }
.rows .t { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 1; overflow: hidden; overflow-wrap: anywhere; }
.rows .m { color: var(--mute); font-size: 12.5px; }
.rows .m b { color: var(--c); font-weight: 600; }
.more { display: inline-block; margin-top: 14px; font-size: 13px; color: var(--mute); }
.more:hover { color: var(--ink); }

.steps { display: flex; gap: 6px; }
.steps i { flex: 1; height: 4px; border-radius: 2px; background: var(--rule); }
.steps i.done { background: var(--ink); }
.cap { margin: 22px 0 0; font-size: clamp(30px, 2.75vw, 50px); line-height: 1.08; font-weight: 320; font-stretch: 106%; letter-spacing: -.015em; max-width: 13ch; min-height: 4.4em; }
.walking .say, .walking .ask { display: none; }
.walking .pane { margin-top: 0; }
.nav { display: flex; align-items: center; gap: 10px; margin-top: 20px; }
.nav button { padding: 9px 18px; border-radius: 999px; border: 1px solid var(--ink); font-weight: 600; font-size: 14px; }
.nav button.next { background: var(--ink); color: var(--paper); }
.nav button:hover { border-color: var(--blue); background: var(--blue); color: #fff; }
.nav button[disabled] { opacity: .3; pointer-events: none; }
.nav span { margin-left: auto; font-size: 13px; color: var(--mute); }

@media (max-width: 900px) {
  .page { display: block; height: auto; padding: 18px 16px 40px; }
  .top { gap: 16px; }
  .stage { margin-top: 8px; }
  svg { height: auto; }
  .side { padding: 8px 0 0; overflow: visible; }
}
@media (prefers-reduced-motion: reduce) {
  .enter *, .dot.arrived { animation: none !important; }
  .part { transition: none; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture" aria-current="page">How it works</a>
    <span class="status" id="status" role="status">Reading the board</span>
  </header>
  <div class="stage"><svg id="svg" role="group" aria-label="The harness: people and their agents around one shared board"></svg></div>
  <div class="side" id="side">
    <p class="say" id="say"></p>
    <button class="ask" id="ask" data-go="question"></button>
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

/* What each part says. One sentence, then at most three facts; the rows under them are live. */
const TEXT = {
  board: {
    name: "Board",
    lead: "The team's shared state. Agents post ideas, claim work and report results here, and read it before they start.",
    facts: ["<b>Claim first.</b> A second claim that names the same idea is reported at once.", "<b>Idle 60 min:</b> another agent may ask to take the work over.", "<b>Dots:</b> hollow is open work, solid is a result, small is an idea or a note."],
    rows: m => ({ title: `${cnt(m.n.result)} results, ${cnt(m.n.work)} open, ${cnt(m.n.idea)} ideas`, list: m.results }),
  },
  msg: {
    name: "Messages",
    lead: "A hook puts new messages into an agent's context while it works, so agents hear each other without polling.",
    facts: ["<b>0.2 s</b> to a waiting agent, measured. A working agent gets it after its next tool call.", "<b>Three channels:</b> everyone, one person's agents, one board item."],
    rows: m => ({ title: `${m.msgs.length} messages to everyone in the last ${m.hours} h`, list: m.msgs }),
  },
  mem: {
    name: "Memory",
    lead: "What the team already knows: papers read in full, every board result, every agent session.",
    facts: ["<b>Quote or nothing.</b> The tool refuses a finding whose quote is missing from the paper's text.", "<b>Search first.</b> Agents search memory and the literature before any new measurement."],
    rows: m => ({ title: `${cnt(m.n.note)} knowledge items on the board`, list: m.notes }),
  },
  run: {
    name: "GPU runs",
    lead: "A GPU job runs one committed, pushed version of the code. The tool refuses anything else, so every number traces to code.",
    facts: ["<b>Each run folder</b> holds its commit, command, metrics, and one example scored right and one scored wrong.", "<b>Each result</b> states its number, sample size and file path.", "<b>4 H100 and 2 B200</b> at once per person, on their own credits."],
    rows: m => ({ title: `${m.scores} scored configurations`, list: m.results }),
  },
  review: {
    name: "Self-review",
    lead: "The harness records itself. After each closed result, a review reads the timings and makes one change.",
    facts: ["<b>Every command is logged:</b> time, person, agent, commit.", "<b>Turnaround is measured</b> per job and per work item, from claim to close.", "<b>Honest status:</b> whether these changes help is a study in progress."],
  },
  team: {
    name: "People and agents",
    lead: "Each person steers several coding agents. Each agent has subagents and its own git branch.",
    facts: ["<b>One rules file</b> for two agent products, Claude Code and Codex.", "<b>People set the direction.</b> Agents coordinate through the board and the messages."],
  },
  question: {
    name: "One question",
    lead: "How much of a published reinforcement-learning gain does the untrained base model reach with no training?",
    facts: m => [m && m.best ? `<b>MATH-500 now:</b> untrained base ${m.best.base}, RL-trained ${m.best.rl}.` : "", "<b>One file</b> states the direction. Every agent reads it before choosing work.", "<b>Same conditions</b> for both models, in every comparison."],
    link: ["/", "See every score on the board"],
  },
  "why-boss": {
    name: "No boss agent",
    lead: "Nothing assigns the work. Every line from an agent ends at the board, and none at another agent.",
    facts: ["<b>Agents choose</b> work from the shared state. People steer.", "<b>Not new by itself:</b> other swarms share a board too. The three points below are what differs."],
  },
  "why-people": {
    name: "People steer every swarm",
    lead: "Published agent swarms run alone toward one score. Here each person steers a swarm the whole way, on an open research question.",
    facts: ["<b>The board holds</b> ideas, claims, results and knowledge, with votes.", "<b>Closest published:</b> autoresearch@home and Anthropic's automated researchers."],
  },
  "why-evidence": {
    name: "Two checks agents cannot skip",
    lead: "Both are code. An agent that tries to skip one gets an error.",
    facts: ["<b>Memory</b> refuses a finding whose quote is missing from the paper.", "<b>GPU runs</b> refuse uncommitted or unpushed code."],
  },
  "why-self": {
    name: "It reviews and changes itself",
    lead: "The loop around the picture is real: logged timings go in, and one change to the harness comes out.",
    facts: ["<b>Triggered</b> by every closed result and every fifth GPU job.", "<b>Each change</b> is written down with the measurement behind it.", "<b>Effect:</b> not yet measured. That study is running."],
  },
};
const WHY = [["why-people", "People steer every swarm"], ["why-evidence", "Two checks agents cannot skip"], ["why-self", "It reviews and changes itself"]];
const ASK = "How much of an RL gain needs no training?";
const WALK = [
  "An agent posts an idea.",
  "It searches memory and papers first.",
  "It claims the work on the board.",
  "It writes code on its own branch.",
  "The GPU runs only a pushed commit.",
  "The result carries its number, sample size and file.",
  "A review reads the logs and changes the harness.",
];
const cnt = n => n >= 60 ? "60+" : n;  // /data returns the newest 60 of each kind

/* Geometry: everything hangs on one centre. Wide: memory left, runs right. Narrow: both below. */
function geo() {
  return narrow.matches
    ? { w: 720, h: 900, cx: 360, cy: 388, rb: 138, rm: 194, rq: 240, rp: 292, rr: 350, out: 470, mem: 128, run: 52, fs: 29, fw: 21 }
    : { w: 1240, h: 852, cx: 620, cy: 426, rb: 160, rm: 222, rq: 272, rp: 328, rr: 398, out: 526, mem: 180, run: 0, fs: 24, fw: 18.5 };
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

function best(scores) {  // the best MATH-500 score of each model, as "410/500"
  const top = k => scores.filter(x => x.benchmark === "MATH-500" && x.model === k).sort((a, b) => b.right / b.n - a.right / a.n)[0];
  const base = top("base"), rl = top("rl");
  return base && rl ? { base: `${base.right}/${base.n}`, rl: `${rl.right}/${rl.n}` } : null;
}
function model(d) {
  const all = [...d.items, ...d.messages];
  const people = [...new Set(all.map(r => r.who))].sort();
  const agents = people.map(p => [...new Set(all.filter(r => r.who === p && r.session).map(r => r.session))].sort().slice(0, 30));
  const live = d.items.filter(i => i.listed !== "work-closed").sort((a, b) => a.at_ns - b.at_ns);
  const of = k => live.filter(i => i.listed === k);
  const newest = l => [...l].sort((a, b) => b.at_ns - a.at_ns);
  const results = newest(of("result")), msgs = [...d.messages].reverse();
  const last = Math.max(0, ...d.items.map(i => Number(i.at_ns)), ...d.messages.map(msgNs));
  return {
    people, agents, live, results, msgs, last, hours: d.hours, scores: (d.scores || []).length,
    notes: newest(live.filter(i => i.listed === "knowledge" || i.listed === "skill")),
    n: { result: results.length, work: of("work").length, idea: of("idea").length, note: of("knowledge").length + of("skill").length },
    nAgents: agents.reduce((s, a) => s + a.length, 0),
    lead: Math.max(0, people.indexOf(results[0]?.who)),
    best: best(d.scores || []),
  };
}

/* The picture. Static parts are drawn when the people or their agents change; the item dots on every read. */
function draw() {
  const g = S.g = geo(), m = S.m, n = m ? m.people.length : 0, th = n ? angles(n) : [];
  const svg = $("svg");
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  const part = (name, go, body, label) =>
    `<g class="part" data-part="${name}"${go ? ` data-go="${go}" role="button" tabindex="0" aria-label="${label}"` : ""}>${body}</g>`;
  const chevron = a => `<path d="M-11 -9.5L5 0L-11 9.5" transform="translate(${xy(pt(g, g.rr, a))}) rotate(${a + 90})"/>`;
  const far = (a, b) => Math.abs(((a - b + 540) % 360) - 180);
  const clear = a => Math.min(...[...th, g.mem, g.run, -90].map(b => far(a, b)));  // the Messages label goes where the ring is emptiest
  const gap = narrow.matches ? 14 : 11, top = pt(g, g.rr, -90), at = [30, 150, 60, 120, -45, -135].sort((a, b) => clear(b) - clear(a))[0], ring = pt(g, g.rm, at);
  const lean = Math.cos(at * Math.PI / 180), hang = lean > .3 ? "start" : lean < -.3 ? "end" : "middle";  // the label grows away from the board
  let out = part("review", "review",
    `<circle class="hit" cx="${g.cx}" cy="${g.cy}" r="${g.rr}" stroke-width="26"/>` +
    `<path class="draw" pathLength="1" d="${arc(g, g.rr, -90 + gap, 270 - gap)}"/>${chevron(60)}${chevron(240)}` +
    `<text class="label" x="${f(top[0])}" y="${f(top[1] + g.fs * .34)}" font-size="${g.fs}">Self-review</text>`, "Self-review");
  out += part("msg", "msg",
    `<circle class="hit" cx="${g.cx}" cy="${g.cy}" r="${g.rm}" stroke-width="22"/><circle class="msg-ring" cx="${g.cx}" cy="${g.cy}" r="${g.rm}"/>` +
    `<text class="label" x="${f(ring[0] + Math.sign(Math.round(lean * 3)) * 10)}" y="${f(ring[1] + g.fs * .34)}" font-size="${g.fs}" style="text-anchor:${hang}">Messages</text>`, "Messages");
  const link = a => {  // a line from the agents to an outside part, with the mark of a check the tool enforces
    const c = pt(g, (g.out - 40 + g.rr) / 2, a);
    return `<path class="line" d="M${xy(pt(g, g.rb + 3, a))}L${xy(pt(g, g.out - 40, a))}"/><circle class="gate" cx="${f(c[0])}" cy="${f(c[1])}" r="11"/>` +
      `<path class="tick" d="M${f(c[0] - 5)} ${f(c[1] + .5)}l3.6 3.8l6.4 -7.6"/>`;
  };
  out += part("memlink", "", link(g.mem));
  out += part("runlink", "", link(g.run));

  const spots = th.map((a, i) => (m.agents[i].length ? m.agents[i] : [""]).map((_, k) => {
    const [dx, dy] = spiral(k, 11.5), q = pt(g, g.rq, a);
    return [q[0] + dx, q[1] + dy];
  }));
  th.forEach((a, i) => {
    out += part("thread-" + i, "", `<g class="hue" style="--h:${HUES[i % HUES.length]}">` +
      spots[i].map(p => `<path class="thread" d="M${xy(p)}L${xy(pt(g, g.rb + 3, a))}"/>`).join("") + "</g>");
  });
  out += part("board", "board",
    `<circle class="board-ring ring draw" pathLength="1" cx="${g.cx}" cy="${g.cy}" r="${g.rb}"/><g id="dots"></g>` +
    `<text class="label" x="${g.cx}" y="${f(g.cy - g.rb - g.fs * .72)}" font-size="${g.fs}">Board</text>`, "Board");
  th.forEach((a, i) => {
    const q = pt(g, g.rq, a), p = pt(g, g.rp, a), below = Math.sin(a * Math.PI / 180) >= 0;
    out += part("swarm-" + i, "p-" + m.people[i],
      `<g class="hue" style="--h:${HUES[i % HUES.length]}"><circle class="pad" cx="${f(q[0])}" cy="${f(q[1])}" r="62"/>` +
      `<path class="tie" d="M${xy(q)}L${xy(p)}"/>` +
      spots[i].map((s, k) => m.agents[i].length ? `<circle class="agent" style="--i:${k}" cx="${f(s[0])}" cy="${f(s[1])}" r="4.8"/>` : "").join("") +
      `<circle class="person ring" cx="${f(p[0])}" cy="${f(p[1])}" r="12"/>` +
      `<text class="who" x="${f(p[0])}" y="${f(p[1] + (below ? g.fw * 1.75 : -g.fw * 1.05))}" font-size="${g.fw}">${esc(m.people[i])}</text></g>`,
      `${esc(m.people[i])}, ${m.agents[i].length} agents`);
  });
  const mem = pt(g, g.out, g.mem), run = pt(g, g.out, g.run);
  const names = (c, name, sub, edge) => {  // the name under a part, and under it what the tool enforces there
    const side = narrow.matches ? edge : 0, x = side < 0 ? 18 : side > 0 ? g.w - 18 : c[0], anchor = side < 0 ? "start" : side > 0 ? "end" : "middle";
    return `<text class="label" x="${f(c[0])}" y="${f(c[1] + 44 + g.fs)}" font-size="${g.fs}">${name}</text>` +
      `<text class="sub" x="${f(x)}" y="${f(c[1] + 44 + g.fs + g.fw * 1.35)}" font-size="${f(g.fw * .92)}" style="text-anchor:${anchor}">${sub}</text>`;
  };
  out += part("mem", "mem",
    `<circle class="glyph ring" cx="${f(mem[0])}" cy="${f(mem[1])}" r="36"/>` +
    `<text class="quote" x="${f(mem[0])}" y="${f(mem[1] + 35)}" font-size="74">\u201C</text>` + names(mem, "Memory", "paper quotes verified", -1), "Memory");
  const pins = [-14, 0, 14].map(o => `M${f(run[0] + o)} ${f(run[1] - 36)}v8M${f(run[0] + o)} ${f(run[1] + 28)}v8M${f(run[0] - 36)} ${f(run[1] + o)}h8M${f(run[0] + 28)} ${f(run[1] + o)}h8`).join("");
  out += part("run", "run",
    `<path class="line" d="${pins}"/><rect class="glyph ring" x="${f(run[0] - 28)}" y="${f(run[1] - 28)}" width="56" height="56" rx="8"/>` +
    `<rect class="glyph-ink" x="${f(run[0] - 12)}" y="${f(run[1] - 12)}" width="24" height="24" rx="3.5"/>` + names(run, "GPU runs", "pushed commits only", 1), "GPU runs");
  svg.innerHTML = out + '<g id="fx"></g>';
  S.th = th;
  if (m && !S.entered) {
    S.entered = true;
    svg.classList.add("enter");
    setTimeout(() => svg.classList.remove("enter"), 2600);
  }
}

function dots() {
  const g = S.g, m = S.m, n = m.live.length, c = Math.min(15, (g.rb - 16) / Math.sqrt(n + 1));
  $("dots").innerHTML = m.live.map((it, i) => {
    const [dx, dy] = spiral(i, c), big = it.listed === "result" || it.listed === "work";
    const stale = it.listed === "work" && mins(it.active_ns ?? it.at_ns) >= 60;
    const cls = ["dot hue", it.listed === "work" ? "work" : big ? "" : "note", stale && "stale", S.seen && !S.seen.has(it.id) && "arrived"];
    return `<circle class="${cls.filter(Boolean).join(" ")}" style="--h:${HUES[Math.max(0, m.people.indexOf(it.who)) % HUES.length]};--i:${i}" ` +
      `data-who="${esc(it.who)}" cx="${f(g.cx + dx)}" cy="${f(g.cy + dy)}" r="${f(c * (big ? .4 : .27))}"><title>${esc(it.id)}: ${esc(it.text.slice(0, 120))}</title></circle>`;
  }).join("");
}

/* Motion: a dot travels along the drawn lines, for a real new post or for a step of the walk. */
function route(g, kind, a) {
  const line = (...p) => p, sweep = (r, a0, a1) => {
    const d = a1 - a0, k = Math.max(2, Math.ceil(Math.abs(d) / 4));
    return Array.from({ length: k + 1 }, (_, i) => pt(g, r, a0 + d * i / k));
  };
  const turn = (a0, a1) => a0 + ((a1 - a0 + 540) % 360) - 180;  // the short way round
  if (kind === "board") return line(pt(g, g.rq, a), pt(g, g.rb + 3, a));
  if (kind === "msg") return sweep(g.rm, a, a + 360);
  if (kind === "review") return sweep(g.rr, -82, 278);
  const to = kind === "mem" ? g.mem : g.run;
  return [pt(g, g.rq, a), ...sweep(g.rb + 3, a, turn(a, to)), pt(g, g.out - 40, to)];
}
function fly(points, hue, ms) {
  return new Promise(done => {
    if (still.matches || !points.length) return done();
    const token = S.token, fx = $("fx"), NS = "http://www.w3.org/2000/svg";
    const len = [0];
    for (let i = 1; i < points.length; i++) len.push(len[i - 1] + Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]));
    const el = document.createElementNS(NS, "g");
    el.setAttribute("class", "hue");
    el.setAttribute("style", `--h:${hue}`);
    el.innerHTML = '<circle class="halo" r="17"/><circle class="fly" r="9"/>';
    fx.append(el);
    const t0 = performance.now();
    const tick = now => {
      if (token !== S.token || !el.isConnected) { el.remove(); return done(); }
      const p = Math.min(1, (now - t0) / ms), e = p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, at = e * len[len.length - 1];
      let i = 1;
      while (i < len.length - 1 && len[i] < at) i++;
      const k = (at - len[i - 1]) / ((len[i] - len[i - 1]) || 1);
      el.setAttribute("transform", `translate(${f(points[i - 1][0] + (points[i][0] - points[i - 1][0]) * k)} ${f(points[i - 1][1] + (points[i][1] - points[i - 1][1]) * k)})`);
      if (p < 1) requestAnimationFrame(tick); else { el.remove(); done(); }
    };
    requestAnimationFrame(tick);
  });
}
async function pump() {  // real posts and messages, one at a time, never during the walk
  if (S.flying) return;
  S.flying = true;
  while (S.queue.length) {
    const ev = S.queue.shift(), i = S.m.people.indexOf(ev.who);
    if (i < 0 || String(S.sel).startsWith("walk")) continue;
    await fly(route(S.g, ev.kind, S.th[i]), HUES[i % HUES.length], ev.kind === "msg" ? 2200 : 1100);
    await new Promise(r => setTimeout(r, 500));
  }
  S.flying = false;
}
async function act(step) {
  const g = S.g, i = S.m.lead, a = S.th[i], h = HUES[i % HUES.length], back = p => [...p].reverse();
  const token = ++S.token, go = (p, ms) => token === S.token ? fly(p, h, ms) : null;
  if (step === 1 || step === 3) await go(route(g, "board", a), 1000);
  if (step === 2) { await go(route(g, "mem", a), 1300); await go(back(route(g, "mem", a)), 1300); }
  if (step === 5) await go(route(g, "run", a), 1300);
  if (step === 6) { await go(back(route(g, "run", a)), 1200); await go(route(g, "board", a), 900); }
  if (step === 7) await go(route(g, "review", a), 3000);
}

/* Selection: one value, mirrored in the address. */
const step = () => /^walk-[1-7]$/.test(S.sel || "") ? Number(S.sel.slice(5)) : 0;
function lit() {
  const m = S.m, all = k => (m ? m.people : []).map((_, i) => k + i), me = m ? m.lead : 0, s = S.sel;
  if (!s) return null;
  if (s.startsWith("p-")) { const i = m ? m.people.indexOf(s.slice(2)) : -1; return ["swarm-" + i, "thread-" + i, "board"]; }
  return ({
    board: ["board", ...all("thread-")], msg: ["msg", ...all("swarm-")], mem: ["mem", "memlink", ...all("swarm-")],
    run: ["run", "runlink", ...all("swarm-")], review: ["review"], team: all("swarm-"), question: [...all("swarm-"), "board"],
    "why-boss": ["board", ...all("thread-"), ...all("swarm-")], "why-people": [...all("swarm-"), ...all("thread-")],
    "why-evidence": ["mem", "run", "memlink", "runlink"], "why-self": ["review"],
    "walk-1": ["swarm-" + me, "thread-" + me, "board"], "walk-2": ["swarm-" + me, "mem", "memlink"],
    "walk-3": ["swarm-" + me, "thread-" + me, "board"], "walk-4": ["swarm-" + me],
    "walk-5": ["swarm-" + me, "run", "runlink"], "walk-6": ["run", "runlink", "swarm-" + me, "thread-" + me, "board"],
    "walk-7": ["review"],
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
  if (!s) {
    return `<ul class="why">${WHY.map(([k, t]) => `<li><button data-go="${k}">${t}<span aria-hidden="true">\u203A</span></button></li>`).join("")}</ul>` +
      `<button class="walk" data-go="walk-1">Follow one result</button>`;
  }
  const head = (name, hue) => `<div class="dhead"><h2${hue == null ? "" : ` class="hue" style="--h:${hue}"`}>${esc(name)}</h2><button class="close" data-go="${esc(s)}">Close</button></div>`;
  if (s.startsWith("p-")) {
    const who = s.slice(2), i = m.people.indexOf(who), mine = m.live.filter(r => r.who === who).sort((a, b) => b.at_ns - a.at_ns);
    const branches = new Set(S.data.items.filter(r => r.who === who && r.branch).map(r => r.branch)).size;
    return head(who, HUES[i % HUES.length]) +
      `<p class="lead">${m.agents[i].length} agent sessions on ${branches} git ${branches === 1 ? "branch" : "branches"}, all posting to one board.</p>` +
      rows(`${mine.length} items on the board`, mine, m);
  }
  const t = TEXT[s], r = t.rows && m ? t.rows(m) : null;
  return head(t.name) + `<p class="lead">${t.lead}</p><ul class="facts">${t.facts.map(x => `<li>${x}</li>`).join("")}</ul>` +
    (r ? rows(r.title, r.list, m) : "") + (t.link ? `<a class="more" href="${t.link[0]}">${t.link[1]}</a>` : "");
}
function show() {
  const on = lit(), svg = $("svg"), m = S.m;
  svg.classList.toggle("has-focus", !!on);
  svg.querySelectorAll(".part").forEach(p => p.classList.toggle("on", !!on && on.includes(p.dataset.part)));
  const say = (k, text) => `<button data-go="${k}" class="${S.sel === k ? "on" : ""}">${text}</button>`;
  $("say").innerHTML = say("team", m ? `<b>${m.people.length}</b> people.` : "People.") + say("team", m ? `<b>${m.nAgents}</b> agents.` : "Agents.") +
    say("question", "One question.") + say("why-boss", "No boss.");
  $("ask").textContent = ASK;
  $("ask").classList.toggle("on", S.sel === "question");
  $("side").classList.toggle("walking", !!step());
  const who = S.sel && S.sel.startsWith("p-") ? S.sel.slice(2) : null;  // one person selected: only that person's items stay lit
  svg.querySelectorAll(".dot").forEach(d => d.classList.toggle("off", !!who && d.dataset.who !== who));
  $("pane").innerHTML = pane();
  $("status").className = "status" + (S.error ? " bad" : "");
  $("status").textContent = S.error ? (S.readAt ? `Offline, last read ${new Date(S.readAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : "Offline")
    : S.data ? (m.last && !narrow.matches ? `Live, last post ${ago(m.last)}` : "Live") : "Reading the board";
}

function read(d) {
  const first = !S.data;
  S.data = d; S.m = model(d);
  const key = narrow.matches + "|" + S.m.people.map((p, i) => p + ":" + S.m.agents[i].length).join(",");
  if (key !== S.key) { S.key = key; draw(); }
  dots();
  if (S.seen) {
    d.items.filter(i => i.listed !== "work-closed" && !S.seen.has(i.id)).forEach(i => S.queue.push({ kind: "board", who: i.who }));
    d.messages.filter(x => !S.seen.has(x.sk)).forEach(x => S.queue.push({ kind: "msg", who: x.who }));
    S.queue = S.queue.slice(-8);
    pump();
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
draw();
show();
poll();
</script>
</body>
</html>
"""
