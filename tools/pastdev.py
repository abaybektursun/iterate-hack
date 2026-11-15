"""How the team used past.dev as its shared memory, on one page.

Served at /pastdev by view.py; not a header tab. A static page with no data read: the first screen is one real recall
(the query, the entry past.dev returned, the agent's next sentence), then the usage numbers read from the past.dev
usage API on 2026-11-15 15:40 UTC, four more recalls quoted from the team's Claude Code transcripts, the recall pilot
(studies/metaharness/results/recall_pilot/recall_vs_grep-01), and what the page does not show. Its
look is its own (white paper, black ink, one blue for what past.dev returned), at the person's request.

The four recalls are replayed in a 3D scene of the memory: a porcelain disc holding 854 source dots in three sectors
(616 paper findings, 227 board posts, 11 sessions), the writers behind it and the readers in front. Each replay shows
one agent's write landing as a dot and a different agent's recall lifting that dot in blue. The recall pilot is drawn
as slab towers, one slab per 2,000 tokens the agent has to read, beside one cube per question. Both scenes use their
own perspective projection in SVG (dots and cubes on a canvas), with no library.
"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>past.dev: the memory our agents asked first</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root { --paper: #FFFFFF; --ink: #0B0B0C; --grey: #5E6166; --rule: #0B0B0C; --hair: #D4D5D8; --blue: #1D3BF2; --u: 8px; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--paper); color: var(--ink); font: 400 17px/1.5 Archivo, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
.page { max-width: 1320px; margin: 0 auto; padding: 0 calc(var(--u) * 5); }
.cond { font-stretch: 62%; font-weight: 800; letter-spacing: -0.01em; line-height: 0.92; }
.mono { font: 400 15px/1.55 'JetBrains Mono', 'Courier New', monospace; }
.blue { color: var(--blue); }
.grey { color: var(--grey); }

/* masthead */
.mast { display: flex; justify-content: space-between; gap: 24px; padding: calc(var(--u) * 3) 0; border-bottom: 2px solid var(--rule); font-size: 14px; font-weight: 600; }

/* first screen */
.first { display: grid; grid-template-columns: 5fr 7fr; gap: calc(var(--u) * 8); padding: calc(var(--u) * 9) 0 calc(var(--u) * 10); border-bottom: 2px solid var(--rule); }
h1.cond { font-size: clamp(64px, 8.6vw, 136px); line-height: 1.04; }
.first .sub { margin-top: calc(var(--u) * 4); font-size: 20px; line-height: 1.45; max-width: 420px; }
.ex { align-self: end; }
.ex .row { display: grid; grid-template-columns: 96px 1fr; gap: calc(var(--u) * 3); padding: calc(var(--u) * 3) 0; border-top: 1px solid var(--hair); }
.ex .row:first-child { border-top: 2px solid var(--rule); }
.ex .k { font-size: 13px; font-weight: 600; line-height: 1.9; }
.ex .k span { display: block; font-weight: 400; color: var(--grey); }
.ex .asked { font: 500 clamp(15px, 1.35vw, 19px)/1.5 'JetBrains Mono', monospace; }
.ex .got { color: var(--blue); font-size: clamp(19px, 1.9vw, 27px); line-height: 1.32; font-weight: 500; }
.ex .got small { display: block; margin-top: 12px; font: 400 13px/1.5 'JetBrains Mono', monospace; }
.ex .then { font-size: clamp(19px, 1.9vw, 27px); line-height: 1.32; font-weight: 500; }
.ex .cap { padding-top: calc(var(--u) * 2); border-top: 1px solid var(--hair); font-size: 13px; color: var(--grey); }
.ex .row:nth-child(2) { position: relative; }
.ex .row:nth-child(2)::before { content: ""; position: absolute; left: -20px; top: 24px; bottom: 24px; width: 4px; background: var(--blue); transform-origin: top; }
@keyframes draw { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@media (prefers-reduced-motion: no-preference) { .ex .row:nth-child(2)::before { animation: draw 0.9s 0.4s cubic-bezier(.2,.7,.2,1) backwards; } }

/* sections */
section { display: grid; grid-template-columns: 5fr 7fr; gap: calc(var(--u) * 8); padding: calc(var(--u) * 10) 0; border-bottom: 2px solid var(--rule); }
section.wide { display: block; }
h2 { font-size: clamp(40px, 4.6vw, 68px); text-wrap: balance; }
section > div:first-child { align-self: start; position: sticky; top: 40px; }
section.wide > div:first-child { position: static; }
section .say { margin-top: calc(var(--u) * 3); font-size: 18px; max-width: 420px; }
section.wide .say { max-width: 640px; }

/* ledger table */
table { width: 100%; border-collapse: collapse; }
td { padding: calc(var(--u) * 2) 0; border-top: 1px solid var(--hair); vertical-align: baseline; }
tr:first-child td { border-top: 2px solid var(--rule); }
td.n { font-stretch: 62%; font-weight: 800; font-size: clamp(40px, 4.4vw, 64px); line-height: 1; width: 1%; white-space: nowrap; padding-right: calc(var(--u) * 4); font-variant-numeric: tabular-nums; }
td.w { font-size: 20px; font-weight: 600; width: 34%; }
td.d { color: var(--grey); font-size: 16px; }

/* the two scenes: one SVG under, an optional canvas for the many small dots, one SVG over */
.scene { position: relative; width: 100%; overflow: hidden; touch-action: pan-y; }
.scene svg, .scene canvas { position: absolute; left: 0; top: 0; width: 100%; height: 100%; display: block; }
.scene text { font: 600 13px/1 Archivo, Arial, sans-serif; fill: var(--ink); }
.scene text.g { font-weight: 400; fill: var(--grey); }
.scene text.b, .scene tspan.b { fill: var(--blue); }
.scene tspan.n, .scene text.n { font-stretch: 62%; font-weight: 800; font-size: 15px; font-variant-numeric: tabular-nums; }
.scene text.tag { font-size: 13px; font-weight: 600; stroke: var(--paper); stroke-width: 4px; stroke-linejoin: round; paint-order: stroke; }
.scene text.ml { font-size: 13px; font-weight: 500; fill: var(--grey); }
.scene text.ml.on { font-weight: 600; fill: var(--ink); }
.key { margin-top: calc(var(--u) * 2); font-size: 14px; color: var(--grey); max-width: 600px; }

/* the memory, with real reads replayed */
.mem { display: grid; grid-template-columns: 7fr 5fr; gap: calc(var(--u) * 7); margin-top: calc(var(--u) * 6); align-items: start; }
#mem { height: 560px; }
.cases { display: grid; }
.case { grid-area: 1 / 1; visibility: hidden; }
.case.on { visibility: visible; }
.case .when { font-size: 15px; font-weight: 600; padding-bottom: calc(var(--u) * 2.5); }
.case .when span { display: block; font-weight: 400; color: var(--grey); }
.case .blk { padding: calc(var(--u) * 2.5) 0; border-top: 1px solid var(--hair); }
.case .lab { font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.case .ret { color: var(--blue); font-size: 18px; line-height: 1.42; font-weight: 500; }
.case .then { font-size: 18px; line-height: 1.42; font-weight: 500; }
.case b { font-weight: 700; }
.picks { display: flex; gap: calc(var(--u) * 1.5); padding-top: calc(var(--u) * 3); border-top: 1px solid var(--hair); }
.picks button { width: 48px; height: 48px; padding: 0; border-radius: 50%; border: 1.5px solid var(--ink); background: var(--paper); color: var(--ink); font: 800 22px/1 Archivo, Arial, sans-serif; font-stretch: 62%; font-variant-numeric: tabular-nums; cursor: pointer; }
.picks button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.picks button:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; }

/* recall against grep, as towers */
#tw { height: 640px; }
#tw text.cnt { font-stretch: 62%; font-weight: 800; font-size: 30px; font-variant-numeric: tabular-nums; }
#tw text.lane { font-size: 14px; }
#tw tspan.tn { font-stretch: 62%; font-weight: 800; font-size: 30px; font-variant-numeric: tabular-nums; }
#tw tspan.tw { font-size: 13px; font-weight: 600; }

/* limits */
.lim p { padding: calc(var(--u) * 2.5) 0; border-top: 1px solid var(--hair); font-size: 17px; }
.lim p:first-child { border-top: 2px solid var(--rule); }
.lim b { font-weight: 600; }

/* close */
.end { background: var(--ink); color: #fff; margin-top: -2px; }
.end .page { padding-top: calc(var(--u) * 12); padding-bottom: calc(var(--u) * 8); }
.end h2 { font-size: clamp(72px, 12vw, 190px); }
.end p { margin-top: calc(var(--u) * 4); font-size: 22px; max-width: 620px; }
.end .src { margin-top: calc(var(--u) * 10); padding-top: calc(var(--u) * 2); border-top: 1px solid #ffffff66; font-size: 13px; max-width: none; }

@media (max-width: 900px) {
  .page { padding: 0 20px; }
  .first, section { grid-template-columns: 1fr; gap: calc(var(--u) * 5); padding: calc(var(--u) * 6) 0; }
  .mast span:last-child { text-align: right; }
  .ex .row { grid-template-columns: 1fr; gap: 6px; }
  .ex .k span { display: inline; margin-left: 8px; }
  .mem { grid-template-columns: 1fr; gap: calc(var(--u) * 4); }
  #mem { height: 340px; }
  #tw { height: 400px; }
  section > div:first-child { position: static; }  /* in one column a sticky heading would slide over its own figure */
  #tw text.cnt { font-size: 22px; }
  #tw text.lane { font-size: 12px; }
  #tw tspan.tn { font-size: 22px; }
  #tw tspan.tw { font-size: 11px; }
  .scene text { font-size: 10px; }
  .scene text.tag { display: none; }  /* the caption below names the source */
  td.d { display: block; border-top: 0; padding-top: 0; }
  td.n, td.w { display: inline-block; border-top: 0; padding-bottom: 4px; width: auto; }
  td.n { padding-right: 12px; font-size: 44px; }
  tr { display: block; border-top: 1px solid var(--hair); }
  tr:first-child { border-top: 2px solid var(--rule); }
  tr:first-child td { border-top: 0; }
}
</style>
</head>
<body>
<div class="page">

  <div class="mast"><span>past.dev, used by iterate-hack</span><span>SF AI Research Hackathon · Nov 14–15, 2026</span></div>

  <div class="first">
    <div>
      <h1 class="cond">Our agents asked first.</h1>
      <p class="sub">Three people ran dozens of Claude Code agents on one research question. Before an agent started an idea, it asked past.dev what the team had already read and found. This is one of those questions.</p>
    </div>
    <div class="ex">
      <div class="row">
        <p class="k">Asked<span>02:16 UTC</span></p>
        <p class="asked">recall.py "power distribution sampling sharpening base model matches RL; likelihood ratio log p_RL minus log p_base on base samples"</p>
      </div>
      <div class="row">
        <p class="k blue">Returned<span>by past.dev</span></p>
        <p class="got">sameraslan: Replacing only tokens with large negative log p_RL − log p_base by tokens sampled from the RL model reaches the RL model’s AIME24 Avg@32.
        <small>On the Direction of RLVR Updates for LLM Reasoning, Section 3.2, Figure 2, p. 4–5 [arxiv-2603.22117:fde433402c]</small></p>
      </div>
      <div class="row">
        <p class="k">Then<span>the agent</span></p>
        <p class="then">“My first candidate (RL as distribution sharpening) is already published and in team memory, so I’m checking a second one.”</p>
      </div>
      <p class="cap">Nov 15, 2026. The finding had been stored by a teammate’s agent that read the paper in full. Text in blue on this page is what past.dev returned.</p>
    </div>
  </div>

  <section>
    <div>
      <h2 class="cond">Nineteen hours, on the meter.</h2>
      <p class="say">Read from the past.dev usage API on Nov 15 at 15:40 UTC.</p>
    </div>
    <table>
      <tr><td class="n">15,944</td><td class="w">memories</td><td class="d">extracted by past.dev from 854 stored sources</td></tr>
      <tr><td class="n">0.4 s</td><td class="w">median recall</td><td class="d">409 ms server side; 95% under 1.2 seconds</td></tr>
      <tr><td class="n">1 s</td><td class="w">write to indexed</td><td class="d">median over 854 sources; the slowest took 8 seconds</td></tr>
      <tr><td class="n">$1.09</td><td class="w">for all of it</td><td class="d">3,648 credits; dollars derived from an earlier bill</td></tr>
    </table>
  </section>

  <section class="wide">
    <h2 class="cond">Four more from the log.</h2>
    <p class="say">Taken from the team’s Claude Code transcripts. In the ones we hold, two of every three recalls returned something a teammate wrote.</p>
    <div class="mem">
      <div>
        <div class="scene" id="mem" role="img" aria-label="The past.dev memory drawn as a disc of 854 dots, one per stored source: 616 paper findings, 227 board posts and 11 sessions. Paper readers, research agents and the session plugin write into it from behind. A research agent and the theory generator read from it in front; the theory generator reads paper findings only. Each replay shows one agent's write and a different agent's recall returning it.">
          <svg id="mem-back" aria-hidden="true"></svg>
          <canvas id="mem-dots" aria-hidden="true"></canvas>
          <svg id="mem-front" aria-hidden="true"></svg>
        </div>
        <p class="key">Each dot is one of the 854 sources stored in past.dev. Blue is what a recall returned.</p>
      </div>
      <div class="cap">
        <div class="cases">
          <article class="case on" data-case="1">
            <p class="when">Nov 15 · 03:13 UTC<span>across two people</span></p>
            <div class="blk"><p class="lab">Asked</p><p class="mono">"Goodfire interpretability weight space programming papers read"</p></div>
            <div class="blk"><p class="lab blue">Returned</p><p class="ret">Board item knowledge-e6bc68: the Goodfire paper, read in full by a teammate’s agent 5.5 hours earlier.</p></div>
            <div class="blk"><p class="lab">Then</p><p class="then">The agent opened that item 11 seconds later. <b>Its reading sweep left that paper out.</b></p></div>
          </article>
          <article class="case" data-case="2" aria-hidden="true">
            <p class="when">Nov 15 · 09:25 UTC<span>an analysis subagent</span></p>
            <div class="blk"><p class="lab">Asked</p><p class="mono">"Think-SFT training set overlap with the 328 harder problems check outcome"</p></div>
            <div class="blk"><p class="lab blue">Returned</p><p class="ret">sameraslan: The 328 examples are clean against the RL training prompts only; overlap with the Think-SFT training set is unchecked, and a check is running. [board:result-d9d6f3]</p></div>
            <div class="blk"><p class="lab">Then</p><p class="then">The agent found the finished check, pulled the teammate’s flags file from his branch, and <b>built its readout on it instead of redoing it.</b></p></div>
          </article>
          <article class="case" data-case="3" aria-hidden="true">
            <p class="when">Nov 15 · 03:27 UTC<span>a proposing subagent</span></p>
            <div class="blk"><p class="lab">Asked</p><p class="mono">"handoff: RL model writes first N tokens then base continues, token-level switching between base and RL"</p></div>
            <div class="blk"><p class="lab blue">Returned</p><p class="ret">Sparse but Critical (arXiv 2603.22446), Sec 3.2: generate with base; where base and RL diverge, sample that one token from the RL model; continue with base.</p></div>
            <div class="blk"><p class="lab">Then</p><p class="then">“One idea died on the novelty check before I wrote it up … Do not let anyone re-propose it.” <b>No GPU time was spent.</b></p></div>
          </article>
          <article class="case" data-case="4" aria-hidden="true">
            <p class="when">Nov 14 · 21:31 UTC<span>before a reading sweep</span></p>
            <div class="blk"><p class="lab">Asked</p><p class="mono">"2603.22117 direction of RLVR updates"</p></div>
            <div class="blk"><p class="lab blue">Returned</p><p class="ret">sameraslan: Mentioned RLVR updates for LLM reasoning (On the Direction of RLVR Updates…)</p></div>
            <div class="blk"><p class="lab">Then</p><p class="then">“Ten papers are already in memory, so I’m searching for the relevant ones that are not.” <b>No paper was read twice.</b></p></div>
          </article>
        </div>
        <div class="picks" role="group" aria-label="Choose a recall">
          <button type="button" data-case="1" aria-pressed="true" aria-label="Recall 1">1</button>
          <button type="button" data-case="2" aria-pressed="false" aria-label="Recall 2">2</button>
          <button type="button" data-case="3" aria-pressed="false" aria-label="Recall 3">3</button>
          <button type="button" data-case="4" aria-pressed="false" aria-label="Recall 4">4</button>
        </div>
      </div>
    </div>
  </section>

  <section>
    <div>
      <h2 class="cond">Recall against grep.</h2>
      <p class="say">Twenty questions whose answer was already on the team board. One was asked of past.dev, the other of a grep over 271 session transcripts (446 MB). One run, templated questions, retrieval only.</p>
    </div>
    <div>
      <div class="scene" id="tw" role="img" aria-label="past.dev recall put the answer inside the first 2,000 tokens for 20 of 20 questions, and grep for 6 of 20. The median number of tokens the agent has to read is 1,985 with past.dev recall and 121,074 with grep.">
        <svg id="tw-back" aria-hidden="true"></svg>
        <canvas id="tw-cubes" aria-hidden="true"></canvas>
        <svg id="tw-front" aria-hidden="true"></svg>
      </div>
      <p class="key">One slab is 2,000 tokens, the most one recall returns. One cube is one question; filled means the answer was inside the first 2,000 tokens.</p>
    </div>
  </section>

  <section>
    <div>
      <h2 class="cond">Small enough to copy.</h2>
      <p class="say">About 215 lines of Python on two endpoints, recall and ingest, plus one rule in the agents’ instructions: search the team’s memory before you start an idea.</p>
    </div>
    <div class="lim">
      <p><b>Papers in.</b> A subagent reads one paper in full and stores each finding; one is refused unless its quote is found in the paper’s text. 616 findings from 129 papers.</p>
      <p><b>Board posts in.</b> Every result and piece of knowledge is stored in the same call that posts it. 227 posts.</p>
      <p><b>Sessions in.</b> The past.dev plugin sends a Claude Code session’s prompts and prose replies when it ends. 11 sources from 9 sessions.</p>
      <p><b>Repeats caught.</b> 39 writes of identical content were answered “unchanged” and stored nothing new.</p>
      <p><b>One question out.</b> <span class="mono">python3 tools/recall.py "has anyone tried this?"</span> returns at most 2,000 tokens, each entry with its date and source.</p>
    </div>
  </section>

  <section>
    <div>
      <h2 class="cond">What this does not show.</h2>
    </div>
    <div class="lim">
      <p><b>No control arm.</b> No agent ran without memory, so its effect on the research result is not measured.</p>
      <p><b>No empty answer.</b> Asked about something nobody did, recall returned loosely related entries. The agent has to judge.</p>
      <p><b>Ranking.</b> Asked about one of our own experiments, recall put two papers above our result.</p>
      <p><b>Ingestion under load.</b> With 30 to 40 items queued on Saturday night, ingestion ran 10 to 15 minutes behind.</p>
    </div>
  </section>

</div>

<div class="end">
  <div class="page">
    <h2 class="cond">Ask before you run.</h2>
    <p>For about a dollar, every agent on the team could check what the others had read and found, in its own words, in about a second.</p>
    <p class="src">Usage: past.dev API, Nov 15 2026, 15:40 UTC. Log entries: the team’s Claude Code transcripts. Pilot: studies/metaharness/results/recall_pilot/recall_vs_grep-01.</p>
  </div>
</div>
<script>
(() => {
"use strict";
/* pure:start  (no DOM below this line until pure:end; tools test these in node) */
const RAD = Math.PI / 180;
const CASE_MS = 10500;  // the replay ends at 7 s; the finished frame (write, blue dot, return) then holds
const SECTORS = [["Board", 227], ["Sessions", 11], ["Papers", 616]];
const view = (yaw, pitch) => ({ c1: Math.cos(yaw * RAD), s1: Math.sin(yaw * RAD), c2: Math.cos(pitch * RAD), s2: Math.sin(pitch * RAD) });
/* World: x right, y up, z toward the viewer. The camera turns by yaw about y, then looks down by pitch.
   g = {cx, cy, s, D}. Returns [screen x, screen y, perspective scale k, depth]; a larger depth is nearer. */
function proj(V, g, p) {
  const x1 = p[0] * V.c1 + p[2] * V.s1, z1 = p[2] * V.c1 - p[0] * V.s1;
  const up = p[1] * V.c2 - z1 * V.s2, z = z1 * V.c2 + p[1] * V.s2, k = g.D / (g.D - z);
  return [g.cx + x1 * k * g.s, g.cy - up * k * g.s, k, z];
}
/* One dot per stored source on a disc of radius R: a sunflower spiral, cut into wedges by angle so that each
   sector holds exactly its count. Angles run from `start` (degrees; -90 is the far side). */
function layoutDots(counts, R, start) {
  const N = counts.reduce((s, c) => s + c[1], 0), pts = [];
  for (let i = 0; i < N; i++) {
    const r = R * 0.93 * Math.sqrt(0.02 + 0.98 * (i + 0.5) / N);
    const a = (((i * 137.50776 - start) % 360) + 360) % 360 + start;
    pts.push({ r, a });
  }
  pts.sort((p, q) => p.a - q.a);
  const dots = [], bounds = [];
  let j = 0;
  counts.forEach(([name, n], sec) => {
    for (let m = 0; m < n; m++, j++) {
      const p = pts[j];
      dots.push({ sec, name, r: p.r, a: p.a, x: p.r * Math.cos(p.a * RAD), z: p.r * Math.sin(p.a * RAD) });
    }
    bounds.push(j < N ? (pts[j - 1].a + pts[j].a) / 2 : start + 360);
  });
  return { dots, bounds, start };
}
function pickDot(L, sec, r, deg) {  // the dot of a sector nearest to a point given in polar form
  const tx = r * Math.cos(deg * RAD), tz = r * Math.sin(deg * RAD);
  let best = -1, bd = Infinity;
  L.dots.forEach((d, i) => { if (d.sec !== sec) return; const e = (d.x - tx) ** 2 + (d.z - tz) ** 2; if (e < bd) { bd = e; best = i; } });
  return best;
}
/* One replayed recall, in ms: the write lands, the ask goes in, a ripple crosses the dots, the dot lifts in blue
   and a blue pulse returns to the reader. */
const PH = { write: [400, 1800], tag: [1800, 2200], ask: [2500, 3600], ripple: [3600, 4900], lift: [4900, 5400], back: [5300, 6500], trail: [6400, 7000] };
const prog = (t, s) => Math.min(1, Math.max(0, (t - s[0]) / (s[1] - s[0])));
const during = (t, s) => (t >= s[0] && t < s[1] ? prog(t, s) : null);
const ease = x => (x < 0.5 ? 2 * x * x : 1 - (-2 * x + 2) ** 2 / 2);
function timeline(t) {
  return {
    write: during(t, PH.write), written: t >= PH.write[1], tag: prog(t, PH.tag), ask: during(t, PH.ask),
    ripple: during(t, PH.ripple), blue: t >= PH.lift[0], lift: ease(prog(t, PH.lift)), back: during(t, PH.back), trail: prog(t, PH.trail),
  };
}
/* Slabs of `per` tokens: n slabs, the top one a fraction `top` of a full slab. */
function slabStack(tokens, per) { const total = tokens / per, n = Math.ceil(total); return { n, top: total - (n - 1), total }; }
const slabHeights = (st, U) => Array.from({ length: st.n }, (_, i) => (i < st.n - 1 ? U : st.top * U));
const cubeRow = (hit, total) => Array.from({ length: total }, (_, i) => i < hit);
/* The faces of a box, each listed counter-clockwise as seen from outside. */
function boxFaces(x0, x1, y0, y1, z0, z1) {
  return [
    { n: "left", p: [[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]] },
    { n: "front", p: [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]] },
    { n: "right", p: [[x1, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1]] },
    { n: "back", p: [[x1, y0, z0], [x0, y0, z0], [x0, y1, z0], [x1, y1, z0]] },
    { n: "top", p: [[x0, y1, z1], [x1, y1, z1], [x1, y1, z0], [x0, y1, z0]] },
  ];
}
const area = q => { let a = 0; for (let i = 0; i < q.length; i++) { const p = q[i], r = q[(i + 1) % q.length]; a += p[0] * r[1] - r[0] * p[1]; } return a / 2; };
const facing = q => area(q) < 0;  // screen y points down, so a face seen from outside winds negative
function hull(P) {
  const p = P.map(q => [q[0], q[1]]).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const q of p) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (let i = p.length - 1; i >= 0; i--) { const q = p[i]; while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}
/* The largest scale at which every item (a world point plus a box of pixels around it) fits in w x h. */
function fitView(V, D, items, w, h, m) {
  const at = s => {
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (const it of items) {
      const q = proj(V, { cx: 0, cy: 0, s, D }, it.p);
      x0 = Math.min(x0, q[0] - (it.l || 0)); x1 = Math.max(x1, q[0] + (it.r || 0));
      y0 = Math.min(y0, q[1] - (it.t || 0)); y1 = Math.max(y1, q[1] + (it.b || 0));
    }
    return [x0, x1, y0, y1];
  };
  let lo = 0.02, hi = 8;
  for (let i = 0; i < 40; i++) { const s = (lo + hi) / 2, b = at(s); if (b[1] - b[0] <= w - 2 * m && b[3] - b[2] <= h - 2 * m) lo = s; else hi = s; }
  const b = at(lo);
  return { s: lo, cx: (w - b[0] - b[1]) / 2, cy: (h - b[2] - b[3]) / 2, D };
}
/* pure:end */

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const f1 = v => v.toFixed(1);
const set = (el, k, v) => { const c = el.__c || (el.__c = {}); if (c[k] !== v) { c[k] = v; el.setAttribute(k, v); } };
const pt = q => f1(q[0]) + " " + f1(q[1]);
const poly = q => (q.length ? "M" + q.map(pt).join("L") + "Z" : "");
const pline = q => (q.length ? "M" + q.map(pt).join("L") : "");
const width = t => (t.getComputedTextLength ? t.getComputedTextLength() : 0);
function runs(q, ok) {  // the parts of a closed ring where ok[i] holds, as one open path
  const n = q.length;
  let s = 0;
  while (s < n && ok[s]) s++;
  if (s === n) return pline(q.concat([q[0]]));
  let d = "", on = false;
  for (let j = 1; j <= n; j++) {
    const i = (s + j) % n;
    if (ok[i]) { d += on ? "L" + pt(q[i]) : "M" + pt(q[(i - 1 + n) % n]) + "L" + pt(q[i]); on = true; }
    else if (on) { d += "L" + pt(q[i]); on = false; }
  }
  return d;
}
function ribbon(p, w) {  // a stroke whose width changes along it
  const n = p.length, L = [], R = [];
  for (let i = 0; i < n; i++) {
    const a = p[Math.max(0, i - 1)], b = p[Math.min(n - 1, i + 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, half = w(p[i], i) / 2;
    L.push(f1(p[i][0] - dy / d * half) + " " + f1(p[i][1] + dx / d * half));
    R.push(f1(p[i][0] + dy / d * half) + " " + f1(p[i][1] - dx / d * half));
  }
  return "M" + L.join("L") + "L" + R.reverse().join("L") + "Z";
}
function pathOf(pts) {
  const c = [0];
  for (let i = 1; i < pts.length; i++) c.push(c[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1], pts[i][2] - pts[i - 1][2]));
  return { pts, c, len: c[c.length - 1] || 1 };
}
function along(P, f) {
  const d = Math.max(0, Math.min(1, f)) * P.len;
  let i = 1;
  while (i < P.c.length - 1 && P.c[i] < d) i++;
  const a = P.pts[i - 1], b = P.pts[i], s = Math.min(1, (d - P.c[i - 1]) / ((P.c[i] - P.c[i - 1]) || 1));
  return [a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s, a[2] + (b[2] - a[2]) * s];
}
function sizeOf(el, cvs) {
  const r = el.getBoundingClientRect(), w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
  if (cvs) {
    const d = Math.min(2, window.devicePixelRatio || 1);
    cvs.width = Math.round(w * d); cvs.height = Math.round(h * d);
    cvs.getContext("2d").setTransform(d, 0, 0, d, 0, 0);
  }
  return { w, h };
}
/* A loop that runs only while its figure is on screen and the tab is visible. */
function loop(el, step, onFirstView) {
  let vis = false, run = false, last = 0, seen = false;
  const tick = now => { if (!run) return; const dt = Math.min(1000, now - last); last = now; step(dt, now); requestAnimationFrame(tick); };
  const sync = () => {
    const go = vis && !document.hidden && !reduce;
    if (go && !run) { run = true; last = performance.now(); requestAnimationFrame(tick); }
    if (!go) run = false;
  };
  new IntersectionObserver(es => {
    const e = es[es.length - 1];
    vis = e.isIntersecting;
    if (e.intersectionRatio >= 0.3 && !seen) { seen = true; if (onFirstView) onFirstView(); }
    sync();
  }, { threshold: [0, 0.3] }).observe(el);
  /* The same test from the box itself on scroll, so a figure still starts where the observer is late or never fires. */
  const check = () => {
    const r = el.getBoundingClientRect(), shown = Math.min(r.bottom, innerHeight) - Math.max(r.top, 0);
    vis = shown > 0;
    if (shown >= 0.3 * Math.min(r.height, innerHeight) && !seen) { seen = true; if (onFirstView) onFirstView(); }
    sync();
  };
  addEventListener("scroll", check, { passive: true }); addEventListener("resize", check); check();
  document.addEventListener("visibilitychange", sync);
}
function leaning(el) {  // a few degrees toward the pointer, eased; it settles back when the pointer leaves
  const L = { x: 0, y: 0, tx: 0, ty: 0 };
  el.addEventListener("pointermove", e => { const r = el.getBoundingClientRect(); L.tx = (e.clientX - r.left) / r.width - 0.5; L.ty = (e.clientY - r.top) / r.height - 0.5; });
  el.addEventListener("pointerleave", () => { L.tx = 0; L.ty = 0; });
  L.step = dt => { const a = Math.min(1, dt / 500); L.x += (L.tx - L.x) * a; L.y += (L.ty - L.y) * a; };
  return L;
}
const stop = (at, color, alpha) => `<stop offset="${at}" stop-color="${color}"${alpha == null ? "" : ` stop-opacity="${alpha}"`}/>`;

/* Figure 1: the memory, with four real recalls replayed. */
function memory() {
  const el = document.getElementById("mem");
  if (!el) return;
  const back = document.getElementById("mem-back"), front = document.getElementById("mem-front");
  const cvs = document.getElementById("mem-dots"), ctx = cvs.getContext("2d");
  const R = 150, YB = 26, YT = 50, D = 1500, YAW = 0, PITCH = 31;
  const L = layoutDots(SECTORS, R, -140);
  const span = i => [i ? L.bounds[i - 1] : L.start, L.bounds[i]];
  const face = (r, a, y) => [r * Math.cos(a * RAD), y == null ? YT : y, r * Math.sin(a * RAD)];
  const WR = [["Paper readers", 2, -150, -150, 0.72], ["Research agents", 0, -90, -90, 0.72], ["Session plugin", 1, -30, (span(1)[0] + span(1)[1]) / 2, 0.8]]
    .map(([name, sec, a, aa, ar]) => ({ name, sec, foot: face(240, a, 0), head: face(240, a, 80), to: face(ar * R, aa) }));
  const RD = [["Research agent", 50, face(R, 50)], ["Theory generator", 130, face(0.6 * R, 122)]]
    .map(([name, a, to]) => ({ name, foot: face(232, a, 0), head: face(232, a, 60), to }));
  const SL = [[0, -120, 1.2, "middle"], [1, -5, 1.16, "start"], [2, 165, 1.2, "end"]];
  const CASES = [
    { sec: 0, r: 0.5, a: -108, tag: "board knowledge-e6bc68", wrote: "sameraslan’s agent wrote, 21:45", reader: "abaybektursun’s agent read, 03:13" },
    { sec: 0, r: 0.86, a: -66, tag: "board result-d9d6f3", wrote: "sameraslan’s agent wrote", reader: "an analysis subagent read, 09:25" },
    { sec: 2, r: 0.62, a: 196, tag: "arXiv 2603.22446", wrote: "a paper reader wrote", reader: "a proposing subagent read, 03:27" },
    { sec: 2, r: 0.42, a: 160, tag: "arXiv 2603.22117", wrote: "a paper reader wrote", reader: "an agent read, 21:31" },
  ].map(c => ({ ...c, dot: pickDot(L, c.sec, c.r * R, c.a) }));
  const RING = Array.from({ length: 96 }, (_, i) => i * 360 / 96);
  const TONE = ["#6c6f75", "#36383c", "#9c9fa5"], BAND = [0.5, 0.72, 0.95];

  back.innerHTML = "<defs>" +
    `<radialGradient id="m-sh">${stop(0, "#0B0B0C", 0.17)}${stop(0.55, "#0B0B0C", 0.09)}${stop(1, "#0B0B0C", 0)}</radialGradient>` +
    `<linearGradient id="m-side" x1="0" y1="0" x2="1" y2="0">${stop(0, "#f7f8f9")}${stop(0.5, "#dcdee1")}${stop(1, "#b5b8bd")}</linearGradient>` +
    `<radialGradient id="m-top" cx=".32" cy=".26" r=".95">${stop(0, "#ffffff")}${stop(0.6, "#f3f4f5")}${stop(1, "#e2e4e7")}</radialGradient>` +
    "</defs>" +
    '<path data-k="shadow" fill="url(#m-sh)"/><path data-k="wall" fill="url(#m-side)"/>' +
    '<path data-k="low" fill="none" stroke="#0B0B0C" stroke-opacity=".3" stroke-width=".8"/>' +
    '<path data-k="face" fill="url(#m-top)"/>' +
    '<path data-k="rimb" fill="none" stroke="#0B0B0C" stroke-opacity=".16" stroke-width=".6"/>' +
    '<path data-k="rimf" fill="none" stroke="#0B0B0C" stroke-opacity=".55" stroke-width="1.1"/>';
  const mark = cls => `<g class="${cls}"><path class="wire" fill="none"/><ellipse class="foot" fill="url(#m-ft)"/>` +
    '<line class="stem" stroke="#0B0B0C" stroke-opacity=".7" stroke-width="1.2"/><circle class="head" fill="url(#m-mk)"/><text class="lab ml" text-anchor="middle"></text></g>';
  front.innerHTML = "<defs>" +
    `<radialGradient id="m-hk" cx=".36" cy=".3" r=".7">${stop(0, "#a9acb1")}${stop(0.55, "#0B0B0C")}</radialGradient>` +
    `<radialGradient id="m-gk">${stop(0, "#0B0B0C", 0.22)}${stop(1, "#0B0B0C", 0)}</radialGradient>` +
    `<radialGradient id="m-hb" cx=".36" cy=".3" r=".7">${stop(0, "#ffffff")}${stop(0.5, "#1D3BF2")}</radialGradient>` +
    `<radialGradient id="m-gb">${stop(0, "#1D3BF2", 0.32)}${stop(1, "#1D3BF2", 0)}</radialGradient>` +
    `<radialGradient id="m-mk" cx=".36" cy=".3" r=".75">${stop(0, "#8d9095")}${stop(0.6, "#1c1d1f")}${stop(1, "#0B0B0C")}</radialGradient>` +
    `<radialGradient id="m-ft">${stop(0, "#0B0B0C", 0.22)}${stop(1, "#0B0B0C", 0)}</radialGradient>` +
    "</defs>" +
    '<path data-k="hair" fill="none" stroke="#0B0B0C" stroke-opacity=".35" stroke-width=".8"/>' +
    `<g data-k="writers">${WR.map(() => mark("wr")).join("")}</g>` +
    '<text data-k="wrote" class="on" text-anchor="middle"></text>' +
    '<path data-k="tw" fill="none" stroke="#0B0B0C" stroke-opacity=".4" stroke-width="1"/>' +
    `<g data-k="secl">${SL.map(() => '<text><tspan class="sn"></tspan><tspan class="n" dx="5"></tspan></text>').join("")}</g>` +
    `<g data-k="readers">${RD.map(() => mark("rd")).join("")}<text data-k="who" text-anchor="middle"></text>` +
    '<text data-k="only" class="ml" text-anchor="end">papers only</text></g>' +
    '<path data-k="tb" fill="none" stroke="#1D3BF2" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>' +
    '<g data-k="pulse" opacity="0"><circle class="bloom"/><path class="tail"/><circle class="head"/></g>' +
    '<text data-k="tag" class="tag" text-anchor="start"></text>';
  const $ = (root, k) => root.querySelector(`[data-k="${k}"]`);
  const B = {}; ["shadow", "wall", "low", "face", "rimb", "rimf"].forEach(k => { B[k] = $(back, k); });
  const F = {}; ["hair", "tw", "tb", "who", "wrote", "only", "tag", "pulse"].forEach(k => { F[k] = $(front, k); });
  const nodes = g => ({ g, wire: g.querySelector(".wire"), foot: g.querySelector(".foot"), stem: g.querySelector(".stem"), head: g.querySelector(".head"), lab: g.querySelector(".lab") });
  const wEl = [...$(front, "writers").children].map(nodes), rEl = [...$(front, "readers").querySelectorAll("g")].map(nodes);
  wEl.forEach((m, i) => { m.lab.textContent = WR[i].name; set(m.wire, "stroke", "#8b8e93"); set(m.wire, "stroke-width", ".8"); });
  rEl.forEach((m, i) => { m.lab.textContent = RD[i].name; set(m.wire, "stroke", "#0B0B0C"); set(m.wire, "stroke-opacity", ".55"); set(m.wire, "stroke-width", "1"); });
  rEl[0].lab.classList.add("on");
  [rEl[1].head, rEl[1].stem, rEl[1].wire].forEach(n => set(n, "opacity", ".5"));  // the theory generator: no traced read of its own to replay, so it stays quiet
  const sEl = [...$(front, "secl").children];
  sEl.forEach((t, i) => { t.firstChild.textContent = SECTORS[SL[i][0]][0]; t.lastChild.textContent = String(SECTORS[SL[i][0]][1]); set(t, "text-anchor", SL[i][3]); });
  const P0 = { bloom: F.pulse.querySelector(".bloom"), tail: F.pulse.querySelector(".tail"), head: F.pulse.querySelector(".head") };

  let W = 1, H = 1, G = { cx: 0, cy: 0, s: 1, D }, cur = 0, caseT = 0, auto = !reduce, clock = 0, tagW = 0;
  const lean = leaning(el);

  function layout() {
    const sz = sizeOf(el, cvs); W = sz.w; H = sz.h;
    const items = [];
    RING.forEach((a, i) => { if (i % 4) return; items.push({ p: face(R, a) }, { p: face(R, a, YB) }, { p: face(1.1 * R, a, 0) }); });
    let wr = 0;
    CASES.forEach(c => { F.wrote.textContent = c.wrote; wr = Math.max(wr, width(F.wrote)); });
    F.wrote.textContent = CASES[cur].wrote;
    WR.forEach((w, i) => { const lw = Math.max(width(wEl[i].lab), wr) / 2 + 2; items.push({ p: w.head, l: lw, r: lw, t: 40 }, { p: w.foot }); });
    let who = 0;
    CASES.forEach(c => { F.who.textContent = c.reader; who = Math.max(who, width(F.who)); });
    F.who.textContent = CASES[cur].reader;
    RD.forEach((r, i) => { const lw = Math.max(width(rEl[i].lab), i ? 0 : who) / 2 + 2; items.push({ p: r.foot, l: lw, r: lw, b: i ? 26 : 42 }, { p: r.head }); });
    SL.forEach((l, i) => {
      const lw = width(sEl[i]), an = l[3];
      items.push({ p: face(l[2] * R, l[1]), l: an === "end" ? lw : an === "middle" ? lw / 2 : 0, r: an === "start" ? lw : an === "middle" ? lw / 2 : 0, t: 12, b: 8 });
    });
    G = fitView(view(YAW, PITCH), D, items, W, H, 16);
    tagW = width(F.tag);
  }

  function pulse(Pr, path, f, blue) {
    if (f == null) { set(F.pulse, "opacity", "0"); return; }
    const fe = ease(f), tf = Math.min(0.4, 90 / path.len), N = 12, q = [];
    for (let i = 0; i < N; i++) q.push(Pr(along(path, fe - tf + tf * i / (N - 1))));
    const h = q[N - 1], hr = Math.max(2.4, 3.4 * h[2] * G.s);
    set(F.pulse, "opacity", f1(Math.min(1, f * 10, (1 - f) * 8 + 0.25)));
    set(P0.tail, "d", ribbon(q, (_, i) => 2 * hr * Math.pow(i / (N - 1), 1.4)));
    set(P0.tail, "fill", blue ? "#1D3BF2" : "#0B0B0C");
    set(P0.tail, "fill-opacity", ".55");
    set(P0.head, "cx", f1(h[0])); set(P0.head, "cy", f1(h[1])); set(P0.head, "r", f1(hr));
    set(P0.head, "fill", blue ? "url(#m-hb)" : "url(#m-hk)");
    set(P0.bloom, "cx", f1(h[0])); set(P0.bloom, "cy", f1(h[1])); set(P0.bloom, "r", f1(hr * 5));
    set(P0.bloom, "fill", blue ? "url(#m-gb)" : "url(#m-gk)");
  }

  function placeMark(m, M, Pr, above) {
    const f = Pr(M.foot), h = Pr(M.head), t = Pr(M.to), hr = Math.max(2.6, 4.8 * h[2] * G.s);
    set(m.foot, "cx", f1(f[0])); set(m.foot, "cy", f1(f[1])); set(m.foot, "rx", f1(11 * f[2] * G.s)); set(m.foot, "ry", f1(3.6 * f[2] * G.s));
    set(m.stem, "x1", f1(f[0])); set(m.stem, "y1", f1(f[1])); set(m.stem, "x2", f1(h[0])); set(m.stem, "y2", f1(h[1]));
    set(m.head, "cx", f1(h[0])); set(m.head, "cy", f1(h[1])); set(m.head, "r", f1(hr));
    set(m.wire, "d", pline([h, t]));
    set(m.lab, "x", f1(h[0])); set(m.lab, "y", f1(above ? h[1] - hr - 9 : f[1] + 19));
    return { f, h, t };
  }

  function draw(t, yaw, pitch) {
    const V = view(yaw, pitch), Pr = p => proj(V, G, p), s = G.s, tl = timeline(t), C = CASES[cur], d0 = L.dots[C.dot];
    /* the body */
    const sh = RING.map(a => Pr([0.13 * R + 1.1 * R * Math.cos(a * RAD), 0, 0.1 * R + 1.1 * R * Math.sin(a * RAD)]));
    set(B.shadow, "d", poly(sh));
    const top = RING.map(a => Pr(face(R, a))), bot = RING.map(a => Pr(face(R, a, YB)));
    set(B.wall, "d", poly(hull(top.concat(bot))));
    set(B.face, "d", poly(top));
    const zt = Pr([0, YT, 0])[3], zb = Pr([0, YB, 0])[3];
    const near = top.map(q => q[3] > zt);
    set(B.rimf, "d", runs(top, near));
    set(B.rimb, "d", runs(top, near.map(v => !v)));
    set(B.low, "d", runs(bot, bot.map(q => q[3] > zb)));
    const c0 = Pr(face(0, 0));
    set(F.hair, "d", [L.start, L.bounds[0], L.bounds[1]].map(a => "M" + pt(c0) + "L" + pt(Pr(face(R, a)))).join(""));

    /* the dots */
    ctx.clearRect(0, 0, W, H);
    const paths = Array.from({ length: 9 }, () => new Path2D()), hot = [];
    const rr = tl.ripple == null ? -1 : tl.ripple * 2.15 * R, ox = RD[0].to[0], oz = RD[0].to[2];
    for (let i = 0; i < L.dots.length; i++) {
      if (i === C.dot && tl.written) continue;
      const d = L.dots[i], q = Pr([d.x, YT + 0.3, d.z]), r = Math.max(0.7, 2.1 * q[2] * s), j = d.sec * 3 + (d.z < -50 ? 0 : d.z < 50 ? 1 : 2);
      paths[j].moveTo(q[0] + r, q[1]); paths[j].arc(q[0], q[1], r, 0, 2 * Math.PI);
      if (rr > 0) { const e = Math.hypot(d.x - ox, d.z - oz) - rr, k = Math.exp(-(e * e) / 500); if (k > 0.06) hot.push([q, r, k]); }
    }
    paths.forEach((p, j) => { ctx.globalAlpha = BAND[j % 3]; ctx.fillStyle = TONE[(j / 3) | 0]; ctx.fill(p); });
    if (rr > 0) {
      ctx.fillStyle = "#0B0B0C";
      for (const [q, r, k] of hot) { ctx.globalAlpha = 0.7 * k; ctx.beginPath(); ctx.arc(q[0], q[1], r * (1 + 0.8 * k), 0, 2 * Math.PI); ctx.fill(); }
      const ring = Array.from({ length: 120 }, (_, i) => [ox + rr * Math.cos(i * 3 * RAD), YT + 0.3, oz + rr * Math.sin(i * 3 * RAD)]);
      ctx.globalAlpha = 0.24 * (1 - tl.ripple); ctx.strokeStyle = "#0B0B0C"; ctx.lineWidth = 1; ctx.beginPath();
      let on = false;
      for (const p of ring) { if (Math.hypot(p[0], p[2]) < 0.98 * R) { const q = Pr(p); if (on) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]); on = true; } else on = false; }
      ctx.stroke();
    }
    const dFace = [d0.x, YT + 0.3, d0.z], dLift = [d0.x, YT + 0.3 + 24 * tl.lift, d0.z];
    const qf = Pr(dFace), ql = Pr(dLift), dr = Math.max(1, 2.1 * qf[2] * s);
    if (tl.written && !tl.blue) {
      ctx.globalAlpha = 1; ctx.fillStyle = "#0B0B0C"; ctx.beginPath(); ctx.arc(qf[0], qf[1], dr * 1.8, 0, 2 * Math.PI); ctx.fill();
    } else if (tl.blue) {
      ctx.globalAlpha = 0.16 * tl.lift; ctx.fillStyle = "#0B0B0C"; ctx.beginPath(); ctx.ellipse(qf[0], qf[1], dr * 2.4, dr * 1.1, 0, 0, 2 * Math.PI); ctx.fill();
      const br = Math.max(4.5, dr * 2.6) * (0.75 + 0.25 * tl.lift), hr = br * 3.4;
      ctx.globalAlpha = 0.9; ctx.strokeStyle = "#1D3BF2"; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(qf[0], qf[1]); ctx.lineTo(ql[0], ql[1]); ctx.stroke();
      ctx.globalAlpha = 1; ctx.fillStyle = "#1D3BF2"; ctx.beginPath(); ctx.arc(qf[0], qf[1], Math.max(1, dr * 0.9), 0, 2 * Math.PI); ctx.fill();
      const gl = ctx.createRadialGradient(ql[0], ql[1], br * 0.6, ql[0], ql[1], hr);
      gl.addColorStop(0, "rgba(29,59,242,0.3)"); gl.addColorStop(1, "rgba(29,59,242,0)");
      ctx.fillStyle = gl; ctx.beginPath(); ctx.arc(ql[0], ql[1], hr, 0, 2 * Math.PI); ctx.fill();
      ctx.fillStyle = "#1D3BF2"; ctx.beginPath(); ctx.arc(ql[0], ql[1], br, 0, 2 * Math.PI); ctx.fill();
      ctx.fillStyle = "rgba(255,255,255,0.55)"; ctx.beginPath(); ctx.arc(ql[0] - br * 0.35, ql[1] - br * 0.35, br * 0.3, 0, 2 * Math.PI); ctx.fill();
    }
    ctx.globalAlpha = 1;

    /* writers, readers, labels */
    wEl.forEach((m, i) => placeMark(m, WR[i], Pr, true));
    const ai = WR.findIndex(w => w.sec === C.sec);
    set(F.wrote, "x", wEl[ai].lab.__c.x); set(F.wrote, "y", f1(parseFloat(wEl[ai].lab.__c.y) - 16));
    const rp = rEl.map((m, i) => placeMark(m, RD[i], Pr, false));
    set(F.who, "x", f1(rp[0].f[0])); set(F.who, "y", f1(rp[0].f[1] + 34));
    set(F.only, "x", f1((rp[1].h[0] + rp[1].t[0]) / 2 - 8)); set(F.only, "y", f1((rp[1].h[1] + rp[1].t[1]) / 2 + 4));
    sEl.forEach((tx, i) => { const q = Pr(face(SL[i][2] * R, SL[i][1])); set(tx, "x", f1(q[0])); set(tx, "y", f1(q[1] + 4)); });

    /* the replay */
    const wr = WR.find(w => w.sec === C.sec), wPath = pathOf([wr.head, wr.to, dFace]);
    set(F.tw, "d", tl.written ? pline(wPath.pts.map(Pr)) : "");
    set(F.tb, "d", tl.trail > 0 ? pline([dLift, RD[0].to, RD[0].head].map(Pr)) : "");
    set(F.tb, "stroke-opacity", f1(0.9 * tl.trail));
    if (tl.write != null) pulse(Pr, wPath, tl.write, false);
    else if (tl.ask != null) pulse(Pr, pathOf([RD[0].head, RD[0].to]), tl.ask, false);
    else if (tl.back != null) pulse(Pr, pathOf([dLift, RD[0].to, RD[0].head]), tl.back, true);
    else pulse(Pr, null, null, false);
    const tagAt = tl.blue ? ql : qf, tagX = tagAt[0] + Math.max(4.5, dr * 2.6) + 7;  // beside the dot, so it stays clear of the sector label behind it
    set(F.tag, "x", f1(Math.max(6, Math.min(W - tagW - 6, tagX)))); set(F.tag, "y", f1(tagAt[1] + 4));
    set(F.tag, "opacity", f1(tl.tag));
  }

  const cases = [...document.querySelectorAll(".case")], picks = [...document.querySelectorAll(".picks button")];
  function paintStill() { draw(reduce ? CASE_MS : caseT, YAW, PITCH); }
  function select(n, user) {
    cur = n; caseT = 0;
    if (user) auto = false;
    cases.forEach((c, i) => { c.classList.toggle("on", i === n); if (i === n) c.removeAttribute("aria-hidden"); else c.setAttribute("aria-hidden", "true"); });
    picks.forEach((b, i) => b.setAttribute("aria-pressed", i === n ? "true" : "false"));
    const C = CASES[n];
    F.who.textContent = C.reader; F.wrote.textContent = C.wrote; F.tag.textContent = C.tag; tagW = width(F.tag);
    wEl.forEach((m, i) => {
      const on = WR[i].sec === C.sec;
      m.lab.classList.toggle("on", on);
      set(m.wire, "stroke", on ? "#0B0B0C" : "#8b8e93"); set(m.wire, "stroke-width", on ? "1.1" : ".8");
      [m.head, m.stem, m.foot].forEach(n => set(n, "opacity", on ? "1" : ".4"));
    });
    if (reduce) paintStill();
  }
  picks.forEach((b, i) => b.addEventListener("click", () => {
    select(i, true);
    if (location.hash !== "#read-" + (i + 1)) location.hash = "read-" + (i + 1);
  }));
  document.querySelector(".picks").addEventListener("keydown", e => {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    e.preventDefault();
    const n = (cur + (e.key === "ArrowRight" ? 1 : 3)) % 4;
    picks[n].focus(); picks[n].click();
  });
  const fromHash = () => { const m = /^#read-([1-4])$/.exec(location.hash); return m ? Number(m[1]) - 1 : -1; };
  window.addEventListener("hashchange", () => { const n = fromHash(); if (n >= 0 && n !== cur) select(n, true); });

  layout();
  const h0 = fromHash();
  select(h0 >= 0 ? h0 : 0, h0 >= 0);
  paintStill();
  new ResizeObserver(() => { layout(); paintStill(); }).observe(el);
  if (document.fonts) document.fonts.ready.then(() => { layout(); paintStill(); });
  loop(el, dt => {
    clock += dt; caseT += dt; lean.step(dt);
    if (caseT >= CASE_MS) { if (auto) select((cur + 1) % 4, false); else caseT %= CASE_MS; }
    const yaw = YAW + 4 * Math.sin(clock / 9000 * 2 * Math.PI) + lean.x * 6;
    const pitch = PITCH + 1.2 * Math.sin(clock / 13000 * 2 * Math.PI) - lean.y * 4;
    draw(caseT, yaw, pitch);
  });
}

/* Figure 2: recall against grep, as slab towers and question cubes. */
function towers() {
  const el = document.getElementById("tw");
  if (!el) return;
  const back = document.getElementById("tw-back"), front = document.getElementById("tw-front");
  const cvs = document.getElementById("tw-cubes"), ctx = cvs.getContext("2d");
  const U = 6.6, FP = 42, Z0 = -102, Z1 = -18, D = 1500, YAW = 32, PITCH = 18, CUBE = 11, GAP = 3, CZ = [40, 54], ENTER = 2000;
  const LANES = [
    { x: -120, st: slabStack(1985, 2000), row: cubeRow(20, 20), blue: true, name: "past.dev recall", cnt: "20 of 20", tok: "1,985" },
    { x: 120, st: slabStack(121074, 2000), row: cubeRow(6, 20), blue: false, name: "grep", cnt: "6 of 20", tok: "121,074" },
  ];
  LANES.forEach(ln => { ln.hs = slabHeights(ln.st, U); ln.H = ln.hs.reduce((a, b) => a + b, 0); });
  const cubes = [];
  LANES.forEach(ln => ln.row.forEach((on, i) => {
    const row = i < 10 ? 1 : 0, x0 = ln.x - 68.5 + (i % 10) * (CUBE + GAP);
    cubes.push({ on, blue: ln.blue, x0, x1: x0 + CUBE, z0: CZ[row], z1: CZ[row] + CUBE });
  }));
  const CB = { left: "#4A62F5", front: "#1D3BF2", right: "#1A33D0", back: "#1A33D0", top: "#8393F8" };
  const CK = { left: "#3a3c40", front: "#1c1d20", right: "#0B0B0C", back: "#0B0B0C", top: "#6b6e73" };
  const FILL = [
    { left: "#4A62F5", front: "#1D3BF2", right: "#1A33D0", back: "#1A33D0", top: "#8393F8" },
    { left: "url(#t-dl)", front: "url(#t-df)", right: "#121315", back: "#121315", top: "url(#t-dt)" },
  ];
  const facesG = i => `<g data-k="box${i}">${["left", "front", "right", "back", "top"].map(n => `<path data-f="${n}" fill="${FILL[i][n]}"/>`).join("")}` +
    `<path data-f="strata" fill="none" stroke="#ffffff" stroke-opacity="${i ? ".2" : ".35"}" stroke-width=".7"/>` +
    `<path data-f="rim" fill="none" stroke="#ffffff" stroke-opacity="${i ? ".3" : ".55"}" stroke-width=".8"/></g>`;
  back.innerHTML = "<defs>" +
    `<radialGradient id="t-sh">${stop(0, "#0B0B0C", 0.2)}${stop(0.55, "#0B0B0C", 0.1)}${stop(1, "#0B0B0C", 0)}</radialGradient>` +
    `<linearGradient id="t-dl" x1="0" y1="0" x2="0" y2="1">${stop(0, "#7d8085")}${stop(1, "#4d5054")}</linearGradient>` +
    `<linearGradient id="t-df" x1="0" y1="0" x2="0" y2="1">${stop(0, "#2a2c2f")}${stop(1, "#141517")}</linearGradient>` +
    `<linearGradient id="t-cast" x1="0" y1="0" x2="1" y2=".6">${stop(0, "#0B0B0C", 0.2)}${stop(0.45, "#0B0B0C", 0.08)}${stop(1, "#0B0B0C", 0)}</linearGradient>` +
    `<linearGradient id="t-dt" x1="0" y1="0" x2="1" y2="1">${stop(0, "#8c8f94")}${stop(1, "#66696e")}</linearGradient>` +
    "</defs>" +
    '<path data-k="lanes" fill="none" stroke="#D4D5D8" stroke-width="1"/>' +
    '<path data-k="ca0" fill="url(#t-cast)"/><path data-k="ca1" fill="url(#t-cast)"/><path data-k="sh0" fill="url(#t-sh)"/><path data-k="sh1" fill="url(#t-sh)"/><path data-k="cs0" fill="url(#t-sh)" opacity=".6"/><path data-k="cs1" fill="url(#t-sh)" opacity=".6"/>' +
    facesG(1) + facesG(0);
  front.innerHTML = LANES.map((ln, i) =>
    `<text data-k="cnt${i}" class="cnt${ln.blue ? " b" : ""}" text-anchor="middle">${ln.cnt}</text>` +
    `<text data-k="lane${i}" class="lane${ln.blue ? " b" : ""}" text-anchor="middle">${ln.name}</text>` +
    `<text data-k="tok${i}" class="tok${ln.blue ? " b" : ""}" text-anchor="middle"><tspan class="tn">${ln.tok}</tspan><tspan class="tw" dx="5">tokens to read</tspan></text>`).join("");
  const $ = (root, k) => root.querySelector(`[data-k="${k}"]`);
  const box = [0, 1].map(i => { const g = $(back, "box" + i), o = { g }; g.querySelectorAll("[data-f]").forEach(p => { o[p.dataset.f] = p; }); return o; });
  const T = [0, 1].map(i => ({ cnt: $(front, "cnt" + i), lane: $(front, "lane" + i), tok: $(front, "tok" + i), sh: $(back, "sh" + i), ca: $(back, "ca" + i), cs: $(back, "cs" + i) }));
  const lanesEl = $(back, "lanes");

  let W = 1, H = 1, G = { cx: 0, cy: 0, s: 1, D }, clock = 0, e0 = -1, cnt = 30;
  const lean = leaning(el);

  function layout() {
    const sz = sizeOf(el, cvs); W = sz.w; H = sz.h;
    cnt = parseFloat(getComputedStyle(T[0].cnt).fontSize) || 30;
    const items = [];
    LANES.forEach((ln, i) => {
      [ln.x - FP, ln.x + FP].forEach(x => [Z0, Z1].forEach(z => { items.push({ p: [x, 0, z] }, { p: [x, ln.H, z] }); }));
      [ln.x - 80, ln.x + 80].forEach(x => [-122, 72].forEach(z => items.push({ p: [x, 0, z] })));
      const lw = Math.max(width(T[i].cnt), width(T[i].lane)) / 2 + 2, tw = width(T[i].tok) / 2 + 2;
      items.push({ p: [ln.x, 0, 80], l: lw, r: lw, b: cnt + 26 }, { p: [ln.x, ln.H, Z0], l: tw, r: tw, t: cnt + 14 });
    });
    G = fitView(view(YAW, PITCH), D, items, W, H, 14);
  }

  function drawBox(o, Pr, x, y0, hs, n, show) {
    if (!show) { set(o.g, "opacity", "0"); return; }
    set(o.g, "opacity", "1");
    const Ht = hs.slice(0, n).reduce((a, b) => a + b, 0), fs = boxFaces(x - FP, x + FP, y0, y0 + Ht, Z0, Z1);
    let strata = "";
    for (const fc of fs) {
      const q = fc.p.map(Pr), vis = facing(q);
      set(o[fc.n], "d", vis ? poly(q) : "");
      if (fc.n === "top") set(o.rim, "d", poly(q));
      else if (vis) {
        let y = y0;
        for (let k = 0; k < n - 1; k++) {
          y += hs[k];
          const a = Pr([fc.p[0][0], y, fc.p[0][2]]), b = Pr([fc.p[1][0], y, fc.p[1][2]]);
          strata += "M" + pt(a) + "L" + pt(b);
        }
      }
    }
    set(o.strata, "d", strata);
  }

  function draw(yaw, pitch, e) {
    const V = view(yaw, pitch), Pr = p => proj(V, G, p), s = G.s;
    set(lanesEl, "d", LANES.map(ln => poly([[ln.x - 80, 0, -122], [ln.x + 80, 0, -122], [ln.x + 80, 0, 72], [ln.x - 80, 0, 72]].map(Pr))).join(""));
    const started = e >= 0, drop = started ? 1 - Math.min(1, e * ENTER / 650) : 1, land = 90 * (1 - Math.pow(1 - (1 - drop), 3));
    LANES.forEach((ln, i) => {
      const n = ln.blue ? (started ? 1 : 0) : started ? Math.min(ln.st.n, Math.ceil(e * ln.st.n)) : 0;
      const y0 = ln.blue ? 90 - land : 0;
      drawBox(box[i ? 1 : 0], Pr, ln.x, y0, ln.hs, n, n > 0);
      const Ht = ln.hs.slice(0, n).reduce((a, b) => a + b, 0);
      set(T[i].sh, "d", n > 0 ? poly([[ln.x - FP - 10, 0, Z0 - 6], [ln.x + FP + 34, 0, Z0 - 6], [ln.x + FP + 34, 0, Z1 + 10], [ln.x - FP - 10, 0, Z1 + 10]].map(Pr)) : "");
      set(T[i].cs, "d", poly([[ln.x - 76, 0, CZ[0] - 6], [ln.x + 80, 0, CZ[0] - 6], [ln.x + 80, 0, CZ[1] + CUBE + 8], [ln.x - 76, 0, CZ[1] + CUBE + 8]].map(Pr)));
      /* the cast shadow: light from the upper left, so it falls to the right and toward the viewer, longer for a taller body */
      const sx = 26 + 0.3 * Ht, sz = 10 + 0.06 * Ht, fp = [[ln.x - FP, Z0], [ln.x + FP, Z0], [ln.x + FP, Z1], [ln.x - FP, Z1]];
      set(T[i].ca, "d", n > 0 ? poly(hull(fp.map(([x, z]) => Pr([x, 0, z])).concat(fp.map(([x, z]) => Pr([x + sx, 0, z + sz]))))) : "");
      const a = Pr([ln.x, 0, 80]);
      set(T[i].cnt, "x", f1(a[0])); set(T[i].cnt, "y", f1(a[1] + cnt));
      set(T[i].lane, "x", f1(a[0])); set(T[i].lane, "y", f1(a[1] + cnt + 20));
      const tp = Pr([ln.x, y0 + Ht, Z0]);
      set(T[i].tok, "x", f1(tp[0])); set(T[i].tok, "y", f1(tp[1] - 10)); set(T[i].tok, "opacity", n > 0 ? "1" : "0");
    });
    /* the cubes, far to near */
    ctx.clearRect(0, 0, W, H);
    const list = cubes.map(c => ({ c, z: Pr([(c.x0 + c.x1) / 2, CUBE / 2, (c.z0 + c.z1) / 2])[3] })).sort((a, b) => a.z - b.z);
    for (const { c } of list) {
      for (const fc of boxFaces(c.x0, c.x1, 0, CUBE, c.z0, c.z1)) {
        const q = fc.p.map(Pr);
        if (!facing(q)) continue;
        ctx.beginPath(); q.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.closePath();
        if (c.on) {
          const col = (c.blue ? CB : CK)[fc.n];
          ctx.fillStyle = col; ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = 0.5; ctx.stroke();
          if (fc.n === "top") { ctx.strokeStyle = "rgba(255,255,255,0.45)"; ctx.lineWidth = 0.6; ctx.stroke(); }
        } else { ctx.strokeStyle = "rgba(94,97,102,0.42)"; ctx.lineWidth = Math.max(0.6, 0.8 * s); ctx.stroke(); }
      }
    }
  }

  const still = () => draw(YAW, PITCH, reduce ? 1 : e0 < 0 ? -1 : Math.min(1, (performance.now() - e0) / ENTER));
  layout(); still();
  new ResizeObserver(() => { layout(); still(); }).observe(el);
  if (document.fonts) document.fonts.ready.then(() => { layout(); still(); });
  loop(el, (dt, now) => {
    clock += dt; lean.step(dt);
    const yaw = YAW + 3.5 * Math.sin(clock / 10000 * 2 * Math.PI) + lean.x * 6;
    const pitch = PITCH + 1 * Math.sin(clock / 14000 * 2 * Math.PI) - lean.y * 4;
    draw(yaw, pitch, e0 < 0 ? -1 : Math.min(1, (now - e0) / ENTER));
  }, () => { if (e0 < 0) e0 = performance.now(); });
}

memory();
towers();
})();
</script>
</body>
</html>
"""
