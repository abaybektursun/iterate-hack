"""How the team used past.dev as its shared memory, on one page.

Served at /pastdev by view.py; not a header tab. A static page with no data read. The first screen is the title, four
usage numbers read from the past.dev usage API on 2026-11-15 15:40 UTC, and the two scenes side by side: four recalls
quoted from the team's Claude Code transcripts, replayed, and the recall pilot
(studies/metaharness/results/recall_pilot/recall_vs_grep-01); the caption of the selected recall runs under both.
One recall quoted in full follows (the query, the entry past.dev returned, the agent's next sentence), then how the
setup works and what the page does not show. It uses the site's tokens, header and type (architecture.py), in both
themes; the one accent, --blue, is what past.dev returned.

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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens, the header and the type of the Design page (architecture.py). The one accent is --blue: what past.dev
   returned. The towers and the cubes take four shades between ink and paper, lit from the upper left in both themes. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34; --on-blue: #fff;
  --pl: .56; --pc: .15; --dim: .16;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue); --lift: 38%;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18); --btn-drop: rgba(16, 24, 32, .42);
  --grey: var(--mute); --u: 8px;
  --tw-top: color-mix(in srgb, var(--ink) 50%, var(--paper)); --tw-left: color-mix(in srgb, var(--ink) 68%, var(--paper));
  --tw-front: color-mix(in srgb, var(--ink) 92%, var(--paper)); --tw-right: var(--ink);
  --bl-top: color-mix(in srgb, var(--blue) 55%, #fff); --bl-left: color-mix(in srgb, var(--blue) 80%, #fff); --bl-right: color-mix(in srgb, var(--blue) 86%, #000);
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
    --tw-top: color-mix(in srgb, var(--ink) 80%, var(--paper)); --tw-left: color-mix(in srgb, var(--ink) 58%, var(--paper));
    --tw-front: color-mix(in srgb, var(--ink) 40%, var(--paper)); --tw-right: color-mix(in srgb, var(--ink) 26%, var(--paper));
  }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-decoration-thickness: 1px; text-underline-offset: 3px; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.top { display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
p, h2, article, section { margin: 0; }
.page { max-width: 1840px; margin: 0 auto; padding: 20px 40px 0; }
.cond { margin: 0; text-wrap: balance; font-weight: 300; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-stretch: 102%; letter-spacing: -.016em; }
.mono { font-variant-numeric: tabular-nums; }
.blue { color: var(--blue); }
.grey { color: var(--grey); }

/* masthead */
.mast { display: flex; justify-content: space-between; gap: 24px; padding-top: 14px; font-size: 13px; color: var(--mute); }

/* first screen: title, four usage numbers, both scenes, the caption of the selected recall */
.first { padding: max(0px, clamp(28px, 7vh, 76px) - 34px) 0 40px; border-bottom: 1px solid var(--rule); }  /* the lead starts where it does on every page; 34px is the line above it */
.lede { display: flex; align-items: baseline; gap: calc(var(--u) * 5); }
h1.cond { white-space: nowrap; }
.lede .sub { font-size: 16px; line-height: 1.45; max-width: 560px; }
.nums { display: grid; grid-template-columns: repeat(4, 1fr); column-gap: 28px; margin-top: calc(var(--u) * 3); border-top: 1px solid var(--rule); }
.nums > div { padding: calc(var(--u) * 1.5) 0; }
.nums .n { display: block; font-weight: 300; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-stretch: 102%; letter-spacing: -.016em; line-height: 1; }
.nums .w { display: block; margin-top: 6px; font-weight: 600; line-height: 1.3; }
.nums .d { display: block; font-size: 13.5px; line-height: 1.4; color: var(--grey); }
.src-line { padding-top: calc(var(--u) * 1); border-top: 1px solid var(--rule); font-size: 13px; color: var(--grey); }
.figs { display: grid; grid-template-columns: 7fr 5fr; grid-template-areas: "mem tw" "strip strip"; column-gap: calc(var(--u) * 6); margin-top: calc(var(--u) * 3); }
.fig-mem { grid-area: mem; } .fig-tw { grid-area: tw; }
.figlab { font-size: 13px; font-weight: 600; padding-bottom: calc(var(--u) * 1); }
.figsay { margin-top: calc(var(--u) * 1); font-size: 13.5px; max-width: 70ch; }
.ex { align-self: start; }
.ex .row { display: grid; grid-template-columns: 96px 1fr; gap: calc(var(--u) * 3); padding: calc(var(--u) * 3) 0; border-top: 1px solid var(--rule); }
.ex .k { font-size: 13px; font-weight: 600; line-height: 1.9; }
.ex .k span { display: block; font-weight: 400; color: var(--grey); }
.ex .asked { font-size: 17px; line-height: 1.45; font-weight: 380; }
.ex .got, .ex .then { font-size: clamp(20px, 1.56vw, 27px); line-height: 1.26; font-weight: 300; font-stretch: 102%; letter-spacing: -.012em; }
.ex .got { color: var(--blue); }
.ex .got small { display: block; margin-top: 12px; font-size: 13px; line-height: 1.5; font-weight: 400; font-stretch: 100%; letter-spacing: 0; }
.ex .cap { padding-top: calc(var(--u) * 2); border-top: 1px solid var(--rule); font-size: 13px; color: var(--grey); }
.ex .row:nth-child(2) { position: relative; }
.ex .row:nth-child(2)::before { content: ""; position: absolute; left: -20px; top: 24px; bottom: 24px; width: 2px; background: var(--blue); transform-origin: top; }
@keyframes draw { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@media (prefers-reduced-motion: no-preference) { .ex .row:nth-child(2)::before { animation: draw 0.9s 0.4s cubic-bezier(.2,.7,.2,1) backwards; } }

/* sections */
section { display: grid; grid-template-columns: 5fr 7fr; gap: calc(var(--u) * 8); padding: 56px 0; border-bottom: 1px solid var(--rule); }
section > div:first-child { align-self: start; position: sticky; top: 40px; }
section .say { margin-top: calc(var(--u) * 3); font-size: 16px; max-width: 420px; }

/* the two scenes: one SVG under, an optional canvas for the many small dots, one SVG over */
.scene { position: relative; width: 100%; overflow: hidden; touch-action: pan-y; }
.scene svg, .scene canvas { position: absolute; left: 0; top: 0; width: 100%; height: 100%; display: block; }
.scene text { font-weight: 600; font-size: 13px; fill: var(--ink); }
.scene text.g { font-weight: 400; fill: var(--grey); }
.scene text.b, .scene tspan.b { fill: var(--blue); }
.scene tspan.n, .scene text.n { font-weight: 400; }
.scene text.tag { font-size: 13px; font-weight: 600; stroke: var(--paper); stroke-width: 4px; stroke-linejoin: round; paint-order: stroke; }
.scene text.ml { font-size: 13px; font-weight: 500; fill: var(--grey); }
.scene text.ml.on { font-weight: 600; fill: var(--ink); }
.key { margin-top: calc(var(--u) * 1.5); font-size: 13.5px; color: var(--grey); max-width: 70ch; }
#mem, #tw { height: clamp(340px, 46vh, 500px); }

/* the caption of the selected recall: a strip of four columns under both scenes; every case sits in the same cell,
   so the strip keeps the height of the longest one and nothing moves between cases */
.strip { --cols: 1fr 1.25fr 1.6fr 1.6fr; grid-area: strip; display: grid; grid-template-columns: var(--cols); column-gap: calc(var(--u) * 4); margin-top: calc(var(--u) * 4); padding-top: calc(var(--u) * 2.5); border-top: 1px solid var(--rule); }
.cases { display: grid; grid-column: 1 / -1; grid-row: 1; }
.case { grid-area: 1 / 1; visibility: hidden; display: grid; grid-template-columns: var(--cols); column-gap: calc(var(--u) * 4); }
.case.on { visibility: visible; }
.case .when { font-weight: 600; padding-bottom: 76px; }  /* room for the buttons below it */
.case .when span { display: block; font-weight: 400; color: var(--grey); }
.case .lab { font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.case .ret { color: var(--blue); line-height: 1.45; }
.case .then { line-height: 1.45; }
.case b { font-weight: 600; }
.picks { grid-column: 1; grid-row: 1; align-self: end; position: relative; z-index: 1; }
.picks { display: flex; gap: 8px; }
.picks button { appearance: none; min-width: 44px; height: 44px; padding: 0 12px; border: 0; border-bottom: 1px solid var(--rule); border-radius: 0; background: none; color: var(--mute); font: inherit; font-weight: 600; cursor: pointer; }
.picks button[aria-pressed="true"] { color: var(--ink); border-bottom: 2px solid var(--blue); }

/* recall against grep, as towers */
#tw text.cnt, #tw tspan.tn { font-weight: 300; font-size: 26px; font-stretch: 102%; letter-spacing: -.016em; }
#tw text.lane { font-size: 14px; }
#tw tspan.tw { font-size: 13px; font-weight: 600; letter-spacing: 0; }

/* limits */
.lim p { padding: calc(var(--u) * 2) 0; border-top: 1px solid var(--rule); }
.lim b { font-weight: 600; }

/* close */
.end .page { padding-top: 56px; padding-bottom: 56px; }
.end p { margin-top: calc(var(--u) * 3); font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 620px; }
.end .src { margin-top: 56px; padding-top: calc(var(--u) * 2); border-top: 1px solid var(--rule); font-size: 13px; line-height: 1.5; font-weight: 400; color: var(--grey); max-width: none; }

@media (max-width: 500px) {  /* no room: of the writers only the one that wrote is named, and the note "papers only" goes */
  #mem [data-k="writers"] .lab:not(.on), #mem [data-k="only"] { display: none; }
}
@media (max-width: 900px) {
  .page { padding: 14px 16px 0; }
  .end .page { padding-top: 40px; padding-bottom: 40px; }
  .top { gap: 0 13px; padding-bottom: 2px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  section { grid-template-columns: 1fr; gap: calc(var(--u) * 4); padding: 40px 0; }
  .mast span:last-child { text-align: right; }
  .ex .row { grid-template-columns: 1fr; gap: 6px; }
  .ex .row:nth-child(2)::before { left: -9px; }
  .ex .k span { display: inline; margin-left: 8px; }
  .first { padding: 20px 0 40px; }
  .lede { display: block; }
  h1.cond { white-space: normal; }
  .lede .sub { margin-top: calc(var(--u) * 2); }
  .nums { grid-template-columns: 1fr 1fr; }
  .nums > div:nth-child(n+3) { border-top: 1px solid var(--rule); }
  .figs { grid-template-columns: minmax(0, 1fr); grid-template-areas: "mem" "strip" "tw"; }
  .fig-tw { margin-top: calc(var(--u) * 5); }
  .strip { display: block; margin-top: calc(var(--u) * 3); }
  .case { display: block; }
  .case .when { padding-bottom: calc(var(--u) * 2); }
  .case .blk { padding: calc(var(--u) * 2) 0; border-top: 1px solid var(--rule); }
  .picks { padding-top: calc(var(--u) * 2.5); border-top: 1px solid var(--rule); }
  #mem { height: clamp(270px, 75vw, 340px); }  /* on a phone the width sets the disc's size, so a shorter box leaves no empty band */
  #tw { height: 400px; }
  section > div:first-child { position: static; }  /* in one column a sticky heading would slide over its own figure */
  #tw text.cnt, #tw tspan.tn { font-size: 20px; }
  #tw text.lane { font-size: 12px; }
  #tw tspan.tw { font-size: 12px; }
  .scene text, .scene text.ml { font-size: 12px; font-stretch: 82%; }  /* narrower labels leave the disc more room */
  .scene text.tag { display: none; }  /* the caption below names the source */
}
</style>
</head>
<body>
<div class="page">

  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings">Findings</a>
  </header>

  <div class="mast"><span>past.dev, used by iterate-hack</span><span>SF AI Research Hackathon · Nov 14–15, 2026</span></div>

  <div class="first">
    <div class="lede">
      <h1 class="cond">Our agents asked first.</h1>
      <p class="sub">Three people ran dozens of Claude Code agents on one research question. Before an agent started an idea, it asked past.dev what the team had already read and found.</p>
    </div>
    <div class="nums">
      <div><span class="n">15,944</span><span class="w">memories</span><span class="d">extracted by past.dev from 854 stored sources</span></div>
      <div><span class="n">0.4 s</span><span class="w">median recall</span><span class="d">409 ms server side; 95% under 1.2 seconds</span></div>
      <div><span class="n">1 s</span><span class="w">write to indexed</span><span class="d">median over 854 sources; the slowest took 8 seconds</span></div>
      <div><span class="n">$1.09</span><span class="w">for all of it</span><span class="d">3,648 credits; dollars derived from an earlier bill</span></div>
    </div>
    <p class="src-line">Read from the past.dev usage API on Nov 15 at 15:40 UTC.</p>
    <div class="figs">
      <div class="fig-mem">
        <p class="figlab">Four real recalls, replayed</p>
        <div class="scene" id="mem" role="img" aria-label="The past.dev memory drawn as a disc of 854 dots, one per stored source: 616 paper findings, 227 board posts and 11 sessions. Paper readers, research agents and the session plugin write into it from behind. A research agent and the theory generator read from it in front; the theory generator reads paper findings only. Each replay shows one agent's write and a different agent's recall returning it.">
          <svg id="mem-back" aria-hidden="true"></svg>
          <canvas id="mem-dots" aria-hidden="true"></canvas>
          <svg id="mem-front" aria-hidden="true"></svg>
        </div>
        <p class="key">Each dot is one of the 854 sources stored in past.dev. Blue is what a recall returned.</p>
        <p class="figsay">Taken from the team’s Claude Code transcripts. In the ones we hold, two of every three recalls returned something a teammate wrote.</p>
      </div>
      <div class="fig-tw">
        <p class="figlab">Recall against grep, 20 questions</p>
        <div class="scene" id="tw" role="img" aria-label="past.dev recall put the answer inside the first 2,000 tokens for 20 of 20 questions, and grep for 6 of 20. The median number of tokens the agent has to read is 1,985 with past.dev recall and 121,074 with grep.">
          <svg id="tw-back" aria-hidden="true"></svg>
          <canvas id="tw-cubes" aria-hidden="true"></canvas>
          <svg id="tw-front" aria-hidden="true"></svg>
        </div>
        <p class="key">One slab is 2,000 tokens, the most one recall returns. One cube is one question; filled means the answer was inside the first 2,000 tokens.</p>
        <p class="figsay">Twenty questions whose answer was already on the team board. One was asked of past.dev, the other of a grep over 271 session transcripts (446 MB). One run, templated questions, retrieval only.</p>
      </div>
      <div class="strip">
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
          <button type="button" data-case="2" aria-pressed="false" aria-label="Recall 2" tabindex="-1">2</button>
          <button type="button" data-case="3" aria-pressed="false" aria-label="Recall 3" tabindex="-1">3</button>
          <button type="button" data-case="4" aria-pressed="false" aria-label="Recall 4" tabindex="-1">4</button>
        </div>
      </div>
    </div>
  </div>

  <section>
    <div>
      <h2 class="cond">One recall in full.</h2>
      <p class="say">This is one of those questions.</p>
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
/* One loop for both figures. It steps a figure only while that figure is on screen, and runs only while one of them
   is and the tab is visible. */
const figs = [];
let raf = 0;
function tick(now) {
  raf = 0;
  if (document.hidden) return;
  let any = false;
  for (const g of figs) {
    if (!g.vis) { g.last = 0; continue; }
    const dt = g.last ? Math.min(1000, now - g.last) : 0; g.last = now; g.step(dt, now); any = true;
  }
  if (any) raf = requestAnimationFrame(tick);
}
function sync() {
  if (raf || reduce || document.hidden || !figs.some(g => g.vis)) return;
  figs.forEach(g => { g.last = 0; });
  raf = requestAnimationFrame(tick);
}
document.addEventListener("visibilitychange", sync);
function loop(el, step, onFirstView) {
  const g = { vis: false, last: 0, step };
  let seen = false;
  figs.push(g);
  new IntersectionObserver(es => {
    const e = es[es.length - 1];
    g.vis = e.isIntersecting;
    if (e.intersectionRatio >= 0.3 && !seen) { seen = true; if (onFirstView) onFirstView(); }
    sync();
  }, { threshold: [0, 0.3] }).observe(el);
  /* The same test from the box itself on scroll, so a figure still starts where the observer is late or never fires. */
  const check = () => {
    const r = el.getBoundingClientRect(), shown = Math.min(r.bottom, innerHeight) - Math.max(r.top, 0);
    g.vis = shown > 0;
    if (shown >= 0.3 * Math.min(r.height, innerHeight) && !seen) { seen = true; if (onFirstView) onFirstView(); }
    sync();
  };
  addEventListener("scroll", check, { passive: true }); addEventListener("resize", check); check();
}
function leaning(el) {  // a few degrees toward the pointer, eased; it settles back when the pointer leaves
  const L = { x: 0, y: 0, tx: 0, ty: 0 };
  el.addEventListener("pointermove", e => { const r = el.getBoundingClientRect(); L.tx = (e.clientX - r.left) / r.width - 0.5; L.ty = (e.clientY - r.top) / r.height - 0.5; });
  el.addEventListener("pointerleave", () => { L.tx = 0; L.ty = 0; });
  L.step = dt => { const a = Math.min(1, dt / 500); L.x += (L.tx - L.x) * a; L.y += (L.ty - L.y) * a; };
  return L;
}
const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : `;stop-opacity:${alpha}`}"/>`;
const SH = a => `calc(${a} * var(--shadow))`;  // a cast shadow: there in light, gone in dark, as on the Design page
/* The canvases cannot read a token, so K holds each one as the browser resolved it; it is read again when the theme changes. */
const K = {}, repaint = [], probe = document.body.appendChild(document.createElement("i"));
probe.style.display = "none";
function tint() {
  const names = { ink: "--ink", paper: "--paper", mute: "--mute", blue: "--blue", core: "--core",
    twleft: "--tw-left", twfront: "--tw-front", twright: "--tw-right", twback: "--tw-right", twtop: "--tw-top",
    blleft: "--bl-left", blfront: "--blue", blright: "--bl-right", blback: "--bl-right", bltop: "--bl-top" };
  for (const k in names) { probe.style.color = `var(${names[k]})`; K[k] = getComputedStyle(probe).color; }
}
tint();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { tint(); repaint.forEach(f => f()); });
const alpha = (c, a) => c.replace("rgb(", "rgba(").replace(")", `, ${a})`);

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
  const TONE = [0.62, 0.9, 0.42], BAND = [0.5, 0.72, 0.95];

  back.innerHTML = "<defs>" +
    `<radialGradient id="m-sh">${stop(0, "var(--ink)", SH(0.17))}${stop(0.55, "var(--ink)", SH(0.09))}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<linearGradient id="m-side" x1="0" y1="0" x2="1" y2="0">${stop(0, "var(--glass-hi)")}${stop(0.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</linearGradient>` +
    `<radialGradient id="m-top" cx=".32" cy=".26" r=".95">${stop(0, "var(--glass-hi)")}${stop(0.6, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    "</defs>" +
    '<path data-k="shadow" fill="url(#m-sh)"/><path data-k="wall" fill="url(#m-side)"/>' +
    '<path data-k="low" fill="none" style="stroke:var(--ink)" stroke-opacity=".3" stroke-width=".8"/>' +
    '<path data-k="face" fill="url(#m-top)"/>' +
    '<path data-k="rimb" fill="none" style="stroke:var(--ink)" stroke-opacity=".16" stroke-width=".6"/>' +
    '<path data-k="rimf" fill="none" style="stroke:var(--ink)" stroke-opacity=".55" stroke-width="1.1"/>';
  const mark = cls => `<g class="${cls}"><path class="wire" fill="none"/><ellipse class="foot" fill="url(#m-ft)"/>` +
    '<line class="stem" style="stroke:var(--ink)" stroke-opacity=".7" stroke-width="1.2"/><circle class="head" fill="url(#m-mk)"/><text class="lab ml" text-anchor="middle"></text></g>';
  front.innerHTML = "<defs>" +
    `<radialGradient id="m-hk" cx=".36" cy=".3" r=".7">${stop(0, "var(--mute)")}${stop(0.55, "var(--ink)")}</radialGradient>` +
    `<radialGradient id="m-gk">${stop(0, "var(--ink)", 0.22)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="m-hb" cx=".36" cy=".3" r=".7">${stop(0, "var(--core)")}${stop(0.5, "var(--blue)")}</radialGradient>` +
    `<radialGradient id="m-gb">${stop(0, "var(--blue)", 0.32)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="m-mk" cx=".36" cy=".3" r=".75">${stop(0, "var(--mute)")}${stop(0.6, "var(--ink)")}${stop(1, "var(--ink)")}</radialGradient>` +
    `<radialGradient id="m-ft">${stop(0, "var(--ink)", SH(0.22))}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    "</defs>" +
    '<path data-k="hair" fill="none" style="stroke:var(--ink)" stroke-opacity=".35" stroke-width=".8"/>' +
    `<g data-k="writers">${WR.map(() => mark("wr")).join("")}</g>` +
    '<text data-k="wrote" class="on" text-anchor="middle"></text>' +
    '<path data-k="tw" fill="none" style="stroke:var(--ink)" stroke-opacity=".4" stroke-width="1"/>' +
    `<g data-k="secl">${SL.map(() => '<text><tspan class="sn"></tspan><tspan class="n" dx="5"></tspan></text>').join("")}</g>` +
    `<g data-k="readers">${RD.map(() => mark("rd")).join("")}<text data-k="who" text-anchor="middle"></text>` +
    '<text data-k="only" class="ml" text-anchor="end">papers only</text></g>' +
    '<path data-k="tb" fill="none" style="stroke:var(--blue)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>' +
    '<g data-k="pulse" opacity="0"><circle class="bloom"/><path class="tail"/><circle class="head"/></g>' +
    '<text data-k="tag" class="tag" text-anchor="start"></text>';
  const $ = (root, k) => root.querySelector(`[data-k="${k}"]`);
  const B = {}; ["shadow", "wall", "low", "face", "rimb", "rimf"].forEach(k => { B[k] = $(back, k); });
  const F = {}; ["hair", "tw", "tb", "who", "wrote", "only", "tag", "pulse"].forEach(k => { F[k] = $(front, k); });
  const nodes = g => ({ g, wire: g.querySelector(".wire"), foot: g.querySelector(".foot"), stem: g.querySelector(".stem"), head: g.querySelector(".head"), lab: g.querySelector(".lab") });
  const wEl = [...$(front, "writers").children].map(nodes), rEl = [...$(front, "readers").querySelectorAll("g")].map(nodes);
  wEl.forEach((m, i) => { m.lab.textContent = WR[i].name; m.wire.style.stroke = "var(--mute)"; set(m.wire, "stroke-width", ".8"); });
  rEl.forEach((m, i) => { m.lab.textContent = RD[i].name; m.wire.style.stroke = "var(--ink)"; set(m.wire, "stroke-opacity", ".55"); set(m.wire, "stroke-width", "1"); });
  rEl[0].lab.classList.add("on");
  [rEl[1].head, rEl[1].stem, rEl[1].wire].forEach(n => set(n, "opacity", ".5"));  // the theory generator: no traced read of its own to replay, so it stays quiet
  const sEl = [...$(front, "secl").children];
  sEl.forEach((t, i) => { t.firstChild.textContent = SECTORS[SL[i][0]][0]; t.lastChild.textContent = String(SECTORS[SL[i][0]][1]); set(t, "text-anchor", SL[i][3]); });
  const P0 = { bloom: F.pulse.querySelector(".bloom"), tail: F.pulse.querySelector(".tail"), head: F.pulse.querySelector(".head") };

  let W = 1, H = 1, G = { cx: 0, cy: 0, s: 1, D }, cur = 0, caseT = 0, auto = !reduce, clock = 0, tagW = 0, phone = false, wroteW = 0, whoW = 0;
  const lean = leaning(el);

  function layout() {
    const sz = sizeOf(el, cvs); W = sz.w; H = sz.h;
    phone = W <= 500;  // no room to keep both long captions clear of the edges: the disc takes the width, and draw() holds the captions inside the box
    const items = [];
    RING.forEach((a, i) => { if (i % 4) return; items.push({ p: face(R, a) }, { p: face(R, a, YB) }, { p: face(1.1 * R, a, 0) }); });
    let wr = 0;
    CASES.forEach(c => { F.wrote.textContent = c.wrote; wr = Math.max(wr, width(F.wrote)); });
    WR.forEach((w, i) => {
      if (phone) F.wrote.textContent = w.name;  // a writer's name is hidden on a phone until it writes, so it is measured here
      const lw = (phone ? width(F.wrote) : Math.max(width(wEl[i].lab), wr)) / 2 + 2;
      items.push({ p: w.head, l: lw, r: lw, t: phone ? 46 : 40 }, { p: w.foot });
    });
    F.wrote.textContent = CASES[cur].wrote;
    let who = 0;
    CASES.forEach(c => { F.who.textContent = c.reader; who = Math.max(who, width(F.who)); });
    F.who.textContent = CASES[cur].reader;
    RD.forEach((r, i) => { const lw = Math.max(width(rEl[i].lab), i || phone ? 0 : who) / 2 + 2; items.push({ p: r.foot, l: lw, r: lw, b: i ? 26 : 42 }, { p: r.head }); });
    SL.forEach((l, i) => {
      const lw = width(sEl[i]), an = l[3];
      items.push({ p: face(l[2] * R, l[1]), l: an === "end" ? lw : an === "middle" ? lw / 2 : 0, r: an === "start" ? lw : an === "middle" ? lw / 2 : 0, t: 12, b: 8 });
    });
    G = fitView(view(YAW, PITCH), D, items, W, H, 16);
    tagW = width(F.tag); wroteW = width(F.wrote); whoW = width(F.who);
  }
  const inBox = (x, w) => (phone ? Math.max(8 + w / 2, Math.min(W - 8 - w / 2, x)) : x);  // a centred caption, kept inside the box on a phone

  function pulse(Pr, path, f, blue) {
    if (f == null) { set(F.pulse, "opacity", "0"); return; }
    const fe = ease(f), tf = Math.min(0.4, 90 / path.len), N = 12, q = [];
    for (let i = 0; i < N; i++) q.push(Pr(along(path, fe - tf + tf * i / (N - 1))));
    const h = q[N - 1], hr = Math.max(2.4, 3.4 * h[2] * G.s);
    set(F.pulse, "opacity", f1(Math.min(1, f * 10, (1 - f) * 8 + 0.25)));
    set(P0.tail, "d", ribbon(q, (_, i) => 2 * hr * Math.pow(i / (N - 1), 1.4)));
    P0.tail.style.fill = blue ? "var(--blue)" : "var(--ink)";
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
    set(m.lab, "x", f1(h[0])); set(m.lab, "y", f1(above ? h[1] - hr - (phone ? 15 : 9) : f[1] + 19));  // on a phone a writer's name stands higher, clear of "Board"
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
    ctx.fillStyle = K.ink;
    paths.forEach((p, j) => { ctx.globalAlpha = BAND[j % 3] * TONE[(j / 3) | 0]; ctx.fill(p); });
    if (rr > 0) {
      ctx.fillStyle = K.ink;
      for (const [q, r, k] of hot) { ctx.globalAlpha = 0.7 * k; ctx.beginPath(); ctx.arc(q[0], q[1], r * (1 + 0.8 * k), 0, 2 * Math.PI); ctx.fill(); }
      const ring = Array.from({ length: 120 }, (_, i) => [ox + rr * Math.cos(i * 3 * RAD), YT + 0.3, oz + rr * Math.sin(i * 3 * RAD)]);
      ctx.globalAlpha = 0.24 * (1 - tl.ripple); ctx.strokeStyle = K.ink; ctx.lineWidth = 1; ctx.beginPath();
      let on = false;
      for (const p of ring) { if (Math.hypot(p[0], p[2]) < 0.98 * R) { const q = Pr(p); if (on) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]); on = true; } else on = false; }
      ctx.stroke();
    }
    const dFace = [d0.x, YT + 0.3, d0.z], dLift = [d0.x, YT + 0.3 + 24 * tl.lift, d0.z];
    const qf = Pr(dFace), ql = Pr(dLift), dr = Math.max(1, 2.1 * qf[2] * s);
    if (tl.written && !tl.blue) {
      ctx.globalAlpha = 1; ctx.fillStyle = K.ink; ctx.beginPath(); ctx.arc(qf[0], qf[1], dr * 1.8, 0, 2 * Math.PI); ctx.fill();
    } else if (tl.blue) {
      ctx.globalAlpha = 0.16 * tl.lift; ctx.fillStyle = K.ink; ctx.beginPath(); ctx.ellipse(qf[0], qf[1], dr * 2.4, dr * 1.1, 0, 0, 2 * Math.PI); ctx.fill();
      const br = Math.max(4.5, dr * 2.6) * (0.75 + 0.25 * tl.lift), hr = br * 3.4;
      ctx.globalAlpha = 0.9; ctx.strokeStyle = K.blue; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(qf[0], qf[1]); ctx.lineTo(ql[0], ql[1]); ctx.stroke();
      ctx.globalAlpha = 1; ctx.fillStyle = K.blue; ctx.beginPath(); ctx.arc(qf[0], qf[1], Math.max(1, dr * 0.9), 0, 2 * Math.PI); ctx.fill();
      const gl = ctx.createRadialGradient(ql[0], ql[1], br * 0.6, ql[0], ql[1], hr);
      gl.addColorStop(0, alpha(K.blue, 0.3)); gl.addColorStop(1, alpha(K.blue, 0));
      ctx.fillStyle = gl; ctx.beginPath(); ctx.arc(ql[0], ql[1], hr, 0, 2 * Math.PI); ctx.fill();
      ctx.fillStyle = K.blue; ctx.beginPath(); ctx.arc(ql[0], ql[1], br, 0, 2 * Math.PI); ctx.fill();
      ctx.globalAlpha = 0.55; ctx.fillStyle = K.core; ctx.beginPath(); ctx.arc(ql[0] - br * 0.35, ql[1] - br * 0.35, br * 0.3, 0, 2 * Math.PI); ctx.fill();
    }
    ctx.globalAlpha = 1;

    /* writers, readers, labels */
    wEl.forEach((m, i) => placeMark(m, WR[i], Pr, true));
    const ai = WR.findIndex(w => w.sec === C.sec);
    set(F.wrote, "x", f1(inBox(parseFloat(wEl[ai].lab.__c.x), wroteW))); set(F.wrote, "y", f1(parseFloat(wEl[ai].lab.__c.y) - 16));
    const rp = rEl.map((m, i) => placeMark(m, RD[i], Pr, false));
    set(F.who, "x", f1(inBox(rp[0].f[0], whoW))); set(F.who, "y", f1(rp[0].f[1] + 34));
    set(F.only, "x", f1((rp[1].h[0] + rp[1].t[0]) / 2 - 8)); set(F.only, "y", f1((rp[1].h[1] + rp[1].t[1]) / 2 + 4));
    sEl.forEach((tx, i) => { const q = Pr(face(SL[i][2] * R, SL[i][1])); set(tx, "x", f1(q[0])); set(tx, "y", f1(q[1] + 4 - (!i && innerWidth <= 500 ? 7 : 0))); });  // on a phone "Board" stands clear of the back rim

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
    picks.forEach((b, i) => { b.setAttribute("aria-pressed", i === n ? "true" : "false"); b.tabIndex = i === n ? 0 : -1; });  // one tab stop; the arrow keys move between the four
    const C = CASES[n];
    F.who.textContent = C.reader; F.wrote.textContent = C.wrote; F.tag.textContent = C.tag; tagW = width(F.tag); wroteW = width(F.wrote); whoW = width(F.who);
    wEl.forEach((m, i) => {
      const on = WR[i].sec === C.sec;
      m.lab.classList.toggle("on", on);
      m.wire.style.stroke = on ? "var(--ink)" : "var(--mute)"; set(m.wire, "stroke-width", on ? "1.1" : ".8");
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
  repaint.push(paintStill);
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
  const FILL = [
    { left: "var(--bl-left)", front: "var(--blue)", right: "var(--bl-right)", back: "var(--bl-right)", top: "var(--bl-top)" },
    { left: "var(--tw-left)", front: "var(--tw-front)", right: "var(--tw-right)", back: "var(--tw-right)", top: "var(--tw-top)" },
  ];
  const facesG = i => `<g data-k="box${i}">${["left", "front", "right", "back", "top"].map(n => `<path data-f="${n}" style="fill:${FILL[i][n]}"/>`).join("")}` +
    `<path data-f="strata" fill="none" style="stroke:var(--paper)" stroke-opacity="${i ? ".2" : ".35"}" stroke-width=".7"/>` +
    `<path data-f="rim" fill="none" style="stroke:var(--paper)" stroke-opacity="${i ? ".3" : ".55"}" stroke-width=".8"/></g>`;
  back.innerHTML = "<defs>" +
    `<radialGradient id="t-sh">${stop(0, "var(--ink)", SH(0.2))}${stop(0.55, "var(--ink)", SH(0.1))}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<linearGradient id="t-cast" x1="0" y1="0" x2="1" y2=".6">${stop(0, "var(--ink)", SH(0.2))}${stop(0.45, "var(--ink)", SH(0.08))}${stop(1, "var(--ink)", 0)}</linearGradient>` +
    "</defs>" +
    '<path data-k="lanes" fill="none" style="stroke:var(--rule)" stroke-width="1"/>' +
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
          const col = K[(c.blue ? "bl" : "tw") + fc.n];
          ctx.fillStyle = col; ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = 0.5; ctx.stroke();
          if (fc.n === "top") { ctx.globalAlpha = 0.45; ctx.strokeStyle = K.paper; ctx.lineWidth = 0.6; ctx.stroke(); ctx.globalAlpha = 1; }
        } else { ctx.globalAlpha = 0.42; ctx.strokeStyle = K.mute; ctx.lineWidth = Math.max(0.6, 0.8 * s); ctx.stroke(); ctx.globalAlpha = 1; }
      }
    }
  }

  const still = () => draw(YAW, PITCH, reduce ? 1 : e0 < 0 ? -1 : Math.min(1, (performance.now() - e0) / ENTER));
  layout(); still();
  repaint.push(still);
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
