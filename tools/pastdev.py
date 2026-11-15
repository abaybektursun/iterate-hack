"""How the team used past.dev as its shared memory, on one page.

Served at /pastdev by view.py; not a header tab. A static page with no data read: the first screen is one real recall
(the query, the entry past.dev returned, the agent's next sentence), then the usage numbers read from the past.dev
usage API on 2026-11-15 15:40 UTC, four more recalls quoted from the team's Claude Code transcripts, the recall pilot
(studies/metaharness/results/recall_pilot/recall_vs_grep-01), recalls per hour, and what the page does not show. Its
look is its own (white paper, black ink, one blue for what past.dev returned), at the person's request.
"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>past.dev: the memory 846 questions went to</title>
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

/* log */
.log { margin-top: calc(var(--u) * 6); }
.entry { display: grid; grid-template-columns: 140px 1fr 1fr 1fr; gap: calc(var(--u) * 4); padding: calc(var(--u) * 3.5) 0; border-top: 1px solid var(--hair); }
.entry.head { border-top: 2px solid var(--rule); padding: calc(var(--u) * 1.5) 0; font-size: 13px; font-weight: 600; }
.entry time { font-size: 14px; font-weight: 600; }
.entry time span { display: block; font-weight: 400; color: var(--grey); }
.entry .a { font: 400 14px/1.55 'JetBrains Mono', monospace; }
.entry .r { color: var(--blue); font-size: 16px; }
.entry .t { font-size: 16px; }
.entry b { font-weight: 600; }

/* bars */
.bar { display: grid; grid-template-columns: 220px 1fr 120px; gap: calc(var(--u) * 3); align-items: center; padding: calc(var(--u) * 2) 0; border-top: 1px solid var(--hair); font-size: 16px; }
.bar.top { border-top: 2px solid var(--rule); }
.bar i { display: block; height: 28px; background: var(--ink); }
.bar.pd i { background: var(--blue); }
.bar.pd { color: var(--blue); font-weight: 600; }
.bar em { font-style: normal; font-stretch: 62%; font-weight: 800; font-size: 30px; text-align: right; font-variant-numeric: tabular-nums; }
.bars-h { margin-top: calc(var(--u) * 5); font-size: 18px; font-weight: 600; }
.bars-h:first-child { margin-top: 0; }
.bars-h + .bar { margin-top: calc(var(--u) * 1.5); }

/* hours */
.hours { margin-top: calc(var(--u) * 7); }
.cols { display: grid; grid-template-columns: repeat(20, 1fr); gap: 4px; align-items: end; height: 280px; border-bottom: 2px solid var(--rule); }
.cols div { background: var(--ink); position: relative; }
.cols div span { position: absolute; left: 0; right: 0; top: -22px; text-align: center; font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; }
.axis { display: grid; grid-template-columns: repeat(20, 1fr); gap: 4px; margin-top: 8px; font-size: 13px; color: var(--grey); text-align: center; font-variant-numeric: tabular-nums; }
.axis-note { margin-top: 10px; font-size: 13px; color: var(--grey); display: flex; justify-content: space-between; }

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
  .entry { grid-template-columns: 1fr; gap: 10px; }
  .entry.head { display: none; }
  .entry time span { display: inline; margin-left: 8px; }
  td.d { display: block; border-top: 0; padding-top: 0; }
  td.n, td.w { display: inline-block; border-top: 0; padding-bottom: 4px; width: auto; }
  td.n { padding-right: 12px; font-size: 44px; }
  tr { display: block; border-top: 1px solid var(--hair); }
  tr:first-child { border-top: 2px solid var(--rule); }
  tr:first-child td { border-top: 0; }
  .bar { grid-template-columns: 1fr 104px; }
  .bar em { font-size: 24px; white-space: nowrap; }
  .bar span { grid-column: 1 / -1; }
  .cols { height: 180px; gap: 2px; }
  .axis { gap: 2px; }
  .cols div span { font-size: 0; }
  .cols div.pk span { font-size: 12px; }
  .axis span:nth-child(even) { visibility: hidden; }
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
      <tr><td class="n">846</td><td class="w">recalls</td><td class="d">every one answered; 5 came back empty</td></tr>
      <tr><td class="n">854</td><td class="w">sources stored</td><td class="d">past.dev extracted 15,944 memories from them</td></tr>
      <tr><td class="n">0.4 s</td><td class="w">median recall</td><td class="d">409 ms server side; 95% under 1.2 seconds</td></tr>
      <tr><td class="n">1 s</td><td class="w">write to indexed</td><td class="d">median over 854 sources; the slowest took 8 seconds</td></tr>
      <tr><td class="n">$1.09</td><td class="w">for all of it</td><td class="d">3,648 credits; dollars derived from an earlier bill</td></tr>
    </table>
  </section>

  <section class="wide">
    <h2 class="cond">Four more from the log.</h2>
    <p class="say">Taken from the team’s Claude Code transcripts. In the ones we hold, 146 agents and subagents ran 270 recall commands, and 180 returned something a teammate wrote.</p>
    <div class="log">
      <div class="entry head"><span>UTC</span><span>Asked</span><span class="blue">Returned</span><span>Then</span></div>
      <div class="entry">
        <time>Nov 14 · 21:31<span>before a reading sweep</span></time>
        <p class="a">"2603.22117 direction of RLVR updates"</p>
        <p class="r">sameraslan: Mentioned RLVR updates for LLM reasoning (On the Direction of RLVR Updates…)</p>
        <p class="t">“Ten papers are already in memory, so I’m searching for the relevant ones that are not.” <b>No paper was read twice.</b></p>
      </div>
      <div class="entry">
        <time>Nov 15 · 03:13<span>across two people</span></time>
        <p class="a">"Goodfire interpretability weight space programming papers read"</p>
        <p class="r">Board item knowledge-e6bc68: the Goodfire paper, read in full by a teammate’s agent 5.5 hours earlier.</p>
        <p class="t">The agent opened that item 11 seconds later. <b>Its reading sweep left that paper out.</b></p>
      </div>
      <div class="entry">
        <time>Nov 15 · 03:27<span>a proposing subagent</span></time>
        <p class="a">"handoff: RL model writes first N tokens then base continues, token-level switching between base and RL"</p>
        <p class="r">Sparse but Critical (arXiv 2603.22446), Sec 3.2: generate with base; where base and RL diverge, sample that one token from the RL model; continue with base.</p>
        <p class="t">“One idea died on the novelty check before I wrote it up … Do not let anyone re-propose it.” <b>No GPU time was spent.</b></p>
      </div>
      <div class="entry">
        <time>Nov 15 · 09:25<span>an analysis subagent</span></time>
        <p class="a">"Think-SFT training set overlap with the 328 harder problems check outcome"</p>
        <p class="r">sameraslan: The 328 examples are clean against the RL training prompts only; overlap with the Think-SFT training set is unchecked, and a check is running. [board:result-d9d6f3]</p>
        <p class="t">The agent found the finished check, pulled the teammate’s flags file from his branch, and <b>built its readout on it instead of redoing it.</b></p>
      </div>
    </div>
  </section>

  <section>
    <div>
      <h2 class="cond">Recall against grep.</h2>
      <p class="say">Twenty questions whose answer was already on the team board. One was asked of past.dev, the other of a grep over 271 session transcripts (446 MB). One run, templated questions, retrieval only.</p>
    </div>
    <div>
      <p class="bars-h">Answer inside the first 2,000 tokens</p>
      <div class="bar top pd"><span>past.dev recall</span><i style="width:100%"></i><em>20 of 20</em></div>
      <div class="bar"><span>grep</span><i style="width:30%"></i><em>6 of 20</em></div>
      <p class="bars-h">Tokens the agent has to read (median)</p>
      <div class="bar top pd"><span>past.dev recall</span><i style="width:1.64%"></i><em>1,985</em></div>
      <div class="bar"><span>grep</span><i style="width:100%"></i><em>121,074</em></div>
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

  <section class="wide">
    <h2 class="cond">Asked all night.</h2>
    <p class="say">Recalls per hour, from Saturday 20:00 UTC to Sunday 15:37. The busiest hour also stored 218 new sources.</p>
    <div class="hours">
      <div class="cols">
        <div style="height:3.8%"><span>10</span></div><div style="height:28.4%"><span>75</span></div><div style="height:4.2%"><span>11</span></div><div class="pk" style="height:100%"><span>264</span></div><div style="height:11.7%"><span>31</span></div><div style="height:0.8%"><span>2</span></div><div style="height:4.5%"><span>12</span></div><div class="pk" style="height:39%"><span>103</span></div><div style="height:22.3%"><span>59</span></div><div style="height:23.1%"><span>61</span></div><div style="height:9.1%"><span>24</span></div><div style="height:10.2%"><span>27</span></div><div style="height:4.5%"><span>12</span></div><div style="height:10.6%"><span>28</span></div><div style="height:5.7%"><span>15</span></div><div style="height:5.3%"><span>14</span></div><div style="height:0"><span>0</span></div><div style="height:1.9%"><span>5</span></div><div style="height:2.7%"><span>7</span></div><div class="pk" style="height:32.6%"><span>86</span></div>
      </div>
      <div class="axis"><span>20</span><span>21</span><span>22</span><span>23</span><span>00</span><span>01</span><span>02</span><span>03</span><span>04</span><span>05</span><span>06</span><span>07</span><span>08</span><span>09</span><span>10</span><span>11</span><span>12</span><span>13</span><span>14</span><span>15</span></div>
      <div class="axis-note"><span>Nov 14</span><span>hour, UTC</span><span>Nov 15 (last hour partial)</span></div>
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
</body>
</html>
"""
