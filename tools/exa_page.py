"""The page /exa: how the team's agents used Exa search, counted from the session transcripts.

Numbers: studies/metaharness/results/exa_count-01/summary.json (studies/metaharness/analysis/exa_count.py).
Not a header tab, and its look is its own (white paper, one cyan marker), by the person's choice.
The first screen is the 3D scene plus five numbers, each read from studies/metaharness/results/exa_count-01/summary.json
or the theory rounds as before. The scene replays four real cases, and its dot count 677 comes from
summary.json `distinct_urls_in_search_results`.
"""
PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Exa in the Swarm</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>
/* Idea: the query is the headline, and the only color on the page is the marker on the passage Exa returned.
   Refused: stat tiles, tagged cards, a blue accent. One rule weight, no radius, one motion (the marker stroke). */
:root {
  color-scheme: light;
  --paper: #fbfcfc; --ink: #0b0d0e; --soft: #555d61; --rule: #0b0d0e; --hair: #cfd5d7; --marker: #6fe6f7;
  --porc-hi: #ffffff; --porc: #eff2f3; --porc-mid: #e1e6e8; --porc-lo: #c4ccd0; --porc-rim: #8c979b; --porc-edge: #5d686d;
  --display: "Familjen Grotesk", "Helvetica Neue", Arial, sans-serif;
  --text: "Newsreader", Georgia, "Times New Roman", serif;
  --code: ui-monospace, Menlo, Consolas, monospace;
  --gut: max(20px, env(safe-area-inset-left, 0px));
}
* { box-sizing: border-box }
html { scroll-behavior: smooth }
body { margin: 0; background: var(--paper); color: var(--ink); font: 400 19px/1.5 var(--text) }
.wrap { max-width: 1280px; margin: 0 auto; padding-left: max(20px, env(safe-area-inset-left, 0px)); padding-right: max(20px, env(safe-area-inset-right, 0px)) }
a { color: inherit; text-decoration-thickness: 1px; text-underline-offset: 3px }
a:focus-visible { outline: 3px solid var(--marker); outline-offset: 3px }
mark { color: inherit; background: linear-gradient(var(--marker), var(--marker)) no-repeat 0 0 / 100% 100%; padding: 0.04em 0.12em; margin: 0 -0.12em; -webkit-box-decoration-break: clone; box-decoration-break: clone }
h1, h2, h3, .d { font-family: var(--display); margin: 0; letter-spacing: -0.02em; text-wrap: balance }
p { margin: 0 }
code { font: 0.78em var(--code) }
.soft { color: var(--soft) }

nav { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 28px; padding-block: 18px; border-bottom: 2px solid var(--rule); font: 500 0.84rem var(--display) }
nav b { font-weight: 700 }
nav div { display: flex; flex-wrap: wrap; gap: 6px 22px }
nav a { text-decoration: none }
nav a:hover { text-decoration: underline }

.hero { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 44px 56px; padding-block: 44px 40px }
.hero .ask p { font: 600 1.5rem/1.2 var(--display); letter-spacing: -0.015em; margin-bottom: 22px; max-width: 26em }
.hero h2 { margin-bottom: 0; max-width: none; text-indent: -0.45em; padding-left: 0.45em; font-size: clamp(1.9rem, 3.5vw, 3.1rem); line-height: 1.04; font-weight: 600; overflow-wrap: anywhere }
.answer { display: flex; flex-direction: column; gap: 22px; align-self: end }
.step { border-top: 2px solid var(--rule); padding-top: 12px; display: flex; flex-direction: column; gap: 8px }
.step .t { font: 600 0.92rem var(--display); font-variant-numeric: tabular-nums }
.step .big { font-size: clamp(1.6rem, 2.5vw, 2.3rem); line-height: 1.2 }
.step .src { font: 500 0.92rem var(--display) }
.thesis { grid-column: 1 / -1; border-top: 2px solid var(--rule); padding-top: 18px; font: 600 clamp(1.5rem, 2.9vw, 2.5rem)/1.12 var(--display); letter-spacing: -0.02em }
.hero mark { animation: stroke 0.9s 0.35s cubic-bezier(.3,.7,.2,1) backwards }
@keyframes stroke { from { background-size: 0% 100% } }
@media (prefers-reduced-motion: reduce) { .hero mark { animation: none } html { scroll-behavior: auto } .case, .case.on { transition: none } }

section { padding-block: 56px; border-top: 2px solid var(--rule) }
h2 { font-size: clamp(1.7rem, 3vw, 2.5rem); font-weight: 600; line-height: 1.08; margin-bottom: 28px; max-width: 32ch }

.note { margin-top: 22px; max-width: 62ch; font-size: 1rem; color: var(--soft) }

/* The first screen: the claim, five numbers on fine top rules, then the scene. Paddings stay tight so all of it fits 860px. */
.top { padding-block: 22px 24px }
.top h1 { font-size: clamp(1.9rem, 3.4vw, 3rem); font-weight: 600; line-height: 1.05; margin-bottom: 18px }
.nums { list-style: none; margin: 0 0 22px; padding: 0; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0 28px }
.nums li { border-top: 1px solid var(--rule); padding-top: 9px; display: flex; flex-direction: column; gap: 4px; min-width: 0 }
.nums b { font: 600 clamp(1.8rem, 3vw, 2.7rem)/1 var(--display); letter-spacing: -0.02em; font-variant-numeric: tabular-nums }
.nums span { font: 400 0.9rem/1.3 var(--display); color: var(--soft) }
.top .note { margin-top: 14px; max-width: 70ch; font-size: 0.9rem; line-height: 1.45 }
.lbl { font: 600 0.84rem var(--display) }


/* The replay: one porcelain gate on a floor track, the 677 returned pages as a dot cloud above it. Drawn with our
   own projection; the caption column beside it holds the words. */
.replay { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 28px 56px; align-items: start }
.scene-wrap { margin: 0; min-width: 0 }
.scene { position: relative; height: clamp(340px, 52vh, 520px); touch-action: pan-y }
.scene canvas, .scene svg { position: absolute; inset: 0; width: 100%; height: 100%; display: block }
.key { margin-top: 10px; font: 400 0.9rem/1.45 var(--display); color: var(--soft); max-width: 60ch }
.cases { display: flex; flex-direction: column; gap: 16px; min-width: 0 }
.stack { display: grid }
.case { grid-area: 1 / 1; display: flex; flex-direction: column; min-width: 0; visibility: hidden; opacity: 0; transition: opacity .3s ease, visibility 0s .3s }
.case.on { visibility: visible; opacity: 1; transition: opacity .45s ease .1s, visibility 0s }
.case .when { font: 600 0.95rem/1.35 var(--display); font-variant-numeric: tabular-nums; padding-bottom: 10px }
.case .when span { display: block; font-weight: 400; color: var(--soft) }
.blk { border-top: 1px solid var(--rule); padding-block: 10px 12px; overflow-wrap: anywhere; font-size: 0.95rem; line-height: 1.45 }
.blk .cap { font: 600 0.84rem var(--display); margin-bottom: 4px }
.blk .asked { font: 500 1.1rem/1.25 var(--display); letter-spacing: -0.01em }
.pick { display: flex; gap: 10px }
.pick button { appearance: none; min-width: 48px; height: 48px; padding: 0 14px; border: 1px solid var(--ink); border-radius: 0; background: var(--paper); color: var(--ink); font: 600 1rem var(--display); font-variant-numeric: tabular-nums; cursor: pointer }
.pick button[aria-pressed="true"] { background: var(--ink); color: var(--paper) }
.pick button:focus-visible { outline: 3px solid var(--marker); outline-offset: 3px }
#sc text { font-family: var(--display); font-weight: 600; fill: var(--ink); paint-order: stroke; stroke: var(--paper); stroke-width: 4px; stroke-linejoin: round }
#sc .tube { fill: url(#sc-porc); stroke: var(--porc-rim); stroke-width: .7 }
#sc .hi { fill: var(--porc-hi); opacity: .9 }
#sc .sh { fill: var(--porc-lo); opacity: .4 }
#sc .band { fill: var(--marker) }
#sc .bandglow { fill: var(--marker); opacity: .25 }
#sc .track { fill: var(--ink); opacity: .5 }
#sc .pad { fill: none; stroke: var(--soft); stroke-width: .8 }
#sc .trace { fill: none; stroke: var(--soft); stroke-width: 1; stroke-dasharray: 1.5 4 }
#sc .shadow { fill: url(#sc-shade) }
#sc .tok path { stroke: var(--porc-edge); stroke-width: .9; stroke-linejoin: round }
#sc .tok.hollow path { stroke: var(--ink); stroke-width: 1.1; stroke-dasharray: 4 3 }
#sc .tok .f0 { fill: var(--porc-hi) } #sc .tok .f1 { fill: var(--porc) } #sc .tok .f2 { fill: var(--porc-lo) } #sc .tok .f3 { fill: var(--porc-lo) } #sc .tok .f4 { fill: var(--porc-mid) }
#sc .beam { fill: none; stroke: var(--marker); stroke-width: 3; stroke-linecap: round }
#sc .beamcore { fill: none; stroke: color-mix(in oklch, var(--marker), var(--ink) 40%); stroke-width: 1.5; stroke-linecap: round }
#sc .beamglow { fill: none; stroke: var(--marker); stroke-width: 7; stroke-linecap: round; opacity: .3 }
#sc .head, #sc .lit { fill: var(--marker); stroke: var(--ink); stroke-width: .7 }
#sc .glow { fill: url(#sc-glow) }

.asks { list-style: none; margin: 0; padding: 0; columns: 2; column-gap: 56px }
.asks li { display: flex; flex-direction: column-reverse; break-inside: avoid; border-top: 1px solid var(--rule); padding-block: 14px 18px; font: 500 1.14rem/1.28 var(--display); letter-spacing: -0.01em }
.asks time { display: block; font: 400 0.88rem var(--display); color: var(--soft); margin-top: 6px; font-variant-numeric: tabular-nums; letter-spacing: 0 }

.tw { overflow-x: auto }
table { border-collapse: collapse; width: 100%; min-width: 640px; font-size: 1rem }
th, td { text-align: left; vertical-align: top; padding: 14px 28px 14px 0; border-top: 1px solid var(--rule) }
th { font: 600 0.9rem var(--display); border-top: 0; padding-top: 0 }
td:first-child { font: 600 1.02rem var(--display); width: 22% }
td:last-child { width: 26%; padding-right: 0 }

.limits { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 56px }
.limits li { border-top: 1px solid var(--rule); padding-block: 14px 20px }
.limits b { display: block; font: 600 1.08rem var(--display); margin-bottom: 4px }
footer { border-top: 2px solid var(--rule); padding-block: 18px 48px; font: 400 0.84rem var(--display); color: var(--soft) }

@media (max-width: 860px) {
  body { font-size: 18px }
  .hero { grid-template-columns: 1fr; gap: 32px; padding-block: 28px 32px }
  .top { padding-block: 20px 28px }
  .nums { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px 20px }
  section { padding-block: 40px }
  .replay { grid-template-columns: 1fr; gap: 18px }
  .scene { height: 320px }
  table { min-width: 0 } tr { display: block; border-top: 1px solid var(--rule); padding-block: 12px } tr:first-child { display: none }
  td, td:first-child, td:last-child { display: block; width: auto; border: 0; padding: 2px 0; overflow-wrap: anywhere }
  .asks { columns: 1 }
  .limits { grid-template-columns: 1fr }
}
</style>
</head>
<body>
<div class="wrap">

<nav>
  <b>Exa in the Swarm</b>
  <div><a href="#searches">Four searches</a><a href="#story">One search</a><a href="#asked">How agents asked</a><a href="#wiring">Wiring</a><a href="#limits">Limits</a></div>
</nav>

<header class="top" id="searches">
  <h1>Our agents ask Exa before they run an experiment.</h1>
  <ul class="nums">
    <li><b>61</b><span>agents and subagents searched</span></li>
    <li><b>261</b><span>arXiv papers surfaced</span></li>
    <li><b>188</b><span>pages read in full</span></li>
    <li><b>$1.80</b><span>for the whole hackathon, $0.007 a search</span></li>
    <li><b>163</b><span>published findings written by the theory engine</span></li>
  </ul>
  <div class="replay">
    <figure class="scene-wrap">
      <div class="scene" id="scene">
        <canvas id="sc-dots" aria-hidden="true"></canvas>
        <svg id="sc" role="img" aria-label="Replay of search 1: three ideas reach Exa; two stop at the gate and one goes on to the board."></svg>
      </div>
      <figcaption class="key">Every agent's work cycle passes Exa before a GPU run (AGENTS.md, rule 2). A slab is an idea an agent was about to run.</figcaption>
    </figure>
    <div class="cases">
      <p class="lbl">Four searches that changed a decision</p>
      <div class="stack">
        <article class="case on" id="case-1">
          <p class="when">Nov 15, 15:28 UTC<span>novelty audit of the top finding</span></p>
          <div class="blk"><p class="cap">The agent asked</p><p class="asked">“top singular directions of the RL fine-tuning weight update recover most of the reasoning gain, low-rank RL parameter update”</p></div>
          <div class="blk"><p class="cap">Exa returned</p><p><a href="https://arxiv.org/abs/2510.00553" target="_blank" rel="noopener">arXiv 2510.00553</a>: <mark>“top singular subspace… captures over 99% of reasoning gains”</mark>. Two more searches in the same 13 seconds returned ExPO (<a href="https://arxiv.org/abs/2404.16792" target="_blank" rel="noopener">2404.16792</a>) and ThinkEdit.</p></div>
          <div class="blk"><p class="cap">What changed</p><p>Two novelty claims came off the finding and one stayed. Three searches, 13 seconds, about 2 cents.</p></div>
        </article>
        <article class="case" id="case-2" aria-hidden="true">
          <p class="when">Nov 14, 21:40 UTC<span>interpretability study</span></p>
          <div class="blk"><p class="cap">The agent asked</p><p class="asked">“Jacobian lens open source implementation github anthropic J-lens global workspace”</p></div>
          <div class="blk"><p class="cap">Exa returned</p><p>A published lens for our exact base model: <mark><a href="https://huggingface.co/neuronpedia/jacobian-lens" target="_blank" rel="noopener">huggingface.co/neuronpedia/jacobian-lens</a> and <a href="https://github.com/anthropics/jacobian-lens" target="_blank" rel="noopener">github.com/anthropics/jacobian-lens</a></mark>.</p></div>
          <div class="blk"><p class="cap">What changed</p><p>On the board six minutes later. The same session posted its result with no GPU job.</p></div>
        </article>
        <article class="case" id="case-3" aria-hidden="true">
          <p class="when">Nov 15, 08:01 UTC<span>before a 29 USD run</span></p>
          <div class="blk"><p class="cap">The agent asked</p><p class="asked">“add the weight difference of an RL-trained reasoning model (RL minus base) to a supervised fine-tuned sibling model from the same base, task arithmetic transplant of RLVR delta, math accuracy”</p></div>
          <div class="blk"><p class="cap">Exa returned</p><p><mark>“Decouple before Integration: Test-time Synthesis of SFT and RLVR Task Vectors”</mark>, <a href="https://arxiv.org/abs/2605.00610" target="_blank" rel="noopener">arXiv 2605.00610</a>.</p></div>
          <div class="blk"><p class="cap">What changed</p><p>A subagent read the paper in full. The run went ahead, and its result says what is ours: “Summing SFT and RL vectors is published (2605.00610); the dose curve and control are new”.</p></div>
        </article>
        <article class="case" id="case-4" aria-hidden="true">
          <p class="when">Nov 14, 21:12 UTC<span>literature sweep by 5 agents</span></p>
          <div class="blk"><p class="cap">The agent asked</p><p class="asked soft">The session that made this search is not in the trace store.</p></div>
          <div class="blk"><p class="cap">Exa returned</p><p><a href="https://arxiv.org/abs/2610.24663" target="_blank" rel="noopener">arXiv 2610.24663</a> and six more papers, cited on the board in knowledge-d692e4.</p></div>
          <div class="blk"><p class="cap">What changed</p><p>Seven method families were listed as already published. The team ran none of them.</p></div>
        </article>
      </div>
      <div class="pick" role="group" aria-label="Choose a search">
        <button type="button" data-n="0" aria-pressed="true" aria-label="Search 1">1</button><button type="button" data-n="1" aria-pressed="false" aria-label="Search 2" tabindex="-1">2</button><button type="button" data-n="2" aria-pressed="false" aria-label="Search 3" tabindex="-1">3</button><button type="button" data-n="3" aria-pressed="false" aria-label="Search 4" tabindex="-1">4</button>
      </div>
    </div>
  </div>
  <p class="note">Read from the session transcripts on this laptop and in the team trace store, Nov 14, 21:37 to Nov 15, 15:29 UTC. $0.62 of the bill is read from the tool's own cost lines; the rest is estimated at $0.007 per search and $0.001 per page. Most of one teammate's sessions and every theory-engine run left no transcript, so the true figures are higher.</p>
</header>

<section class="hero" id="story">
  <div class="ask">
    <p>Nov 15, 15:28:52 UTC. Our best result is about to go on a slide as new. An agent asks Exa:</p>
    <h2>“extrapolating the alignment weight difference beyond 1, scaling the RL checkpoint minus base delta by alpha greater than one improves reasoning”</h2>
  </div>
  <div class="answer">
    <div class="step">
      <p class="big">Exa returns a 2024 paper that gets its gain by <mark>“simply amplifying the parameter change”</mark>.</p>
      <p class="src">ExPO, arXiv 2404.16792</p>
    </div>
    <div class="step">
      <p>Four minutes later, at 15:32:18 UTC, the team board reads: “Scaling a fine-tuning delta past 1 is published (ExPO, 2404.16792) and so are length/halting directions (ThinkEdit) … New part: RL's top-8 directions set cap hits monotonically while a random edit stays flat.”</p>
    </div>
  </div>
  <p class="thesis">Four minutes from the question to a corrected claim. The search cost $0.007.</p>
</section>

<section id="asked">
  <h2>Agents described the page they wanted</h2>
  <ul class="asks">
    <li><time>Nov 14, 23:21 UTC</time>training-free power distribution sampling for LLM reasoning without MCMC, cheaper than Reasoning with Sampling, matches GRPO on MATH500</li>
    <li><time>Nov 15, 03:20 UTC</time>a prompt prefix that puts the base model into reasoning mode makes it robust to high temperature sampling while the plain prompt degrades into incoherence</li>
    <li><time>Nov 15, 04:08 UTC</time>raise sampling temperature only when the language model enters a repetition loop, otherwise sample at low temperature; adaptive temperature restart on degenerate repetition in reasoning</li>
    <li><time>Nov 15, 08:52 UTC</time>base model majority voting matches RL-trained model accuracy at equal inference compute, pass@k and maj@k comparison base versus RLVR</li>
    <li><time>Nov 15, 09:16 UTC</time>base model already contains reasoning mode; selecting samples that begin with self-reflection words like 'Okay' or 'Wait' raises MATH-500 accuracy</li>
    <li><time>Nov 15, 09:44 UTC</time>paper comparing supervised fine-tuning on long chain-of-thought traces versus zero RL with verifiable rewards from the same base model on AIME MATH-500 OlympiadBench</li>
    <li><time>Nov 15, 11:38 UTC</time>RL fine-tuned model assigns lower probability to the base model's erroneous reasoning steps, token log-probability of first error step</li>
    <li><time>Nov 15, 02:13 UTC, limited to modal.com</time>Modal docs: what happens to running containers and in-progress inputs when you redeploy an app with modal deploy</li>
  </ul>
  <p class="note">Verbatim. Each is the experiment the agent was about to run, written as the abstract of the paper that would make it unnecessary.</p>
</section>

<section id="wiring">
  <h2>Where Exa sits in the system</h2>
  <div class="tw"><table>
    <tr><th>Place</th><th>What happens there</th><th>File</th></tr>
    <tr><td>Every agent's work cycle</td><td>Search before a new measurement. If a published table answers the question, post it and run nothing.</td><td><code>AGENTS.md:53-55</code></td></tr>
    <tr><td>One 59-line tool</td><td><code>search</code> calls <code>/search</code> with highlights, <code>fetch</code> calls <code>/contents</code> for full text. Plain HTTP, so Claude Code, Codex and every subagent run the same two commands.</td><td><code>tools/exa.py</code></td></tr>
    <tr><td>Theory engine, external stage</td><td>A headless model may run one script, so Exa is its only route to the web. Rounds 02 to 07 wrote 25, 28, 29, 28, 30 and 23 published findings.</td><td><code>studies/theory/lib/round.py:734</code></td></tr>
    <tr><td>Theory engine, review stage</td><td>A novelty search in at least three phrasings before a theory survives.</td><td><code>studies/theory/lib/prompts/review.md</code></td></tr>
    <tr><td>Finding pages</td><td>A public finding needs a memory recall and an Exa search that found no earlier report.</td><td><code>.claude/skills/finding-page/SKILL.md:23</code></td></tr>
    <tr><td>Team site</td><td>125 pages read through Exa, each with its agent, its time and the board item that cites it.</td><td><code>tools/demo_facts.py</code></td></tr>
  </table></div>
</section>

<section id="limits">
  <h2>What failed, and what we do not claim</h2>
  <ul class="limits">
    <li><b>One laptop never had the key.</b>Every call from that machine stopped at “EXA_API_KEY is not set” before reaching Exa, most of them in one session at 15:00 UTC on Nov 15.</li>
    <li><b>The MCP route failed.</b>Calls through the Exa MCP returned 401: the key was unset when the agent started. Commit af5fef1 replaced it with <code>tools/exa.py</code>, which reads the key at call time.</li>
    <li><b>One search missed.</b>The lens search did not return mhough/olmo3-jacobian-lenses, which holds lenses for the RL model. It turned up two hours later, after a fit job had started.</li>
    <li><b>No count of GPU jobs avoided.</b>No artifact supports a dollar figure for what the searches saved, so this page gives none.</li>
  </ul>
</section>

<footer>iterate-hack, SF AI Research Hackathon, Nov 14–15, 2026. Counted Nov 15 at about 15:50 UTC. Counting script: <code>studies/metaharness/analysis/exa_count.py</code>. Its output: <code>studies/metaharness/results/exa_count-01/summary.json</code>.</footer>

</div>
<script>
(() => {
// <pure>
// Geometry and the replay timeline. No DOM here, so the same code can be checked outside a browser.
const RAD = Math.PI / 180;
const ST = { idea: -250, gate: -40, gpu: 110, board: 245 };       // stations along the floor track (x)
const RING = { R: 80, r: 13, cy: 57.6 };                          // the gate: ring radius, tube radius, centre height
const A0 = Math.acos(RING.cy / RING.R) / RAD;                     // where the ring meets the floor, degrees from its lowest point
const CL = { x: 10, y: 150, z: -200, rx: 240, rz: 110, h: 40, n: 677 };  // the dot cloud: 677 distinct pages in search results
const T = { appear: 500, slide: 400, slideDur: 1700, beam: 2300, beamGap: 650, beamDur: 500, extra: 3000, out: 4600, end: 7600, fade: 9000, len: 9600 };
const LBL = { side: 80, gate: 106 };                              // how far in front of the track the station names sit (z)
const CASES = [
  { n: 3, fate: ["stop", "pass", "stop"], beams: [["2404.16792", -175, 62], ["2510.00553", 10, 95], ["ThinkEdit", 205, 30]], extra: [],
    stopTag: "2 already published", goTag: "1 new",
    say: "three ideas reach Exa; two stop at the gate and one goes on to the board." },
  { n: 1, fate: ["skip"], beams: [["jacobian-lens", -60, 80]], extra: [], goTag: "no GPU job",
    say: "one idea passes Exa and goes to the board without a GPU run." },
  { n: 1, fate: ["pass"], trim: true, beams: [["2605.00610", 90, 80]], extra: [], goTag: "run, with a narrower claim",
    say: "one idea passes Exa trimmed, runs on the GPU and reaches the board." },
  { n: 7, fate: ["stop", "stop", "stop", "stop", "stop", "stop", "stop"], beams: [["2610.24663", -120, 88]],
    extra: [[-200, 10], [-60, -35], [45, 25], [150, -15], [200, 45], [10, -85]], stopTag: "7 already published, none run",
    say: "seven ideas stop at Exa; none goes on." },
];
const clamp = v => v < 0 ? 0 : v > 1 ? 1 : v;
const ease = v => { v = clamp(v); return v * v * (3 - 2 * v); };

function cloud() {  // phyllotaxis on a shallow dome, with a fixed seed: the same picture on every load
  let s = 677;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647, pts = [];
  for (let i = 0; i < CL.n; i++) {
    const f = Math.sqrt((i + .5) / CL.n), th = i * 2.39996323;
    pts.push([CL.x + CL.rx * f * Math.cos(th) + (rnd() - .5) * 10, CL.y + CL.h * (1 - f * f) + (rnd() - .5) * 14,
              CL.z + CL.rz * f * Math.sin(th) + (rnd() - .5) * 10]);
  }
  return pts;
}
function nearest(pts, dx, dz) {
  let best = 0, bd = Infinity;
  pts.forEach((p, i) => { const d = (p[0] - CL.x - dx) ** 2 + (p[2] - CL.z - dz) ** 2; if (d < bd) { bd = d; best = i; } });
  return best;
}
function aim(yaw, pitch) { return { c1: Math.cos(yaw * RAD), s1: Math.sin(yaw * RAD), c2: Math.cos(pitch * RAD), s2: Math.sin(pitch * RAD) }; }
function view(V, p) {  // world (y up, z toward the viewer) to view space: yaw about y, then pitch down
  const x = p[0] * V.c1 + p[2] * V.s1, z1 = p[2] * V.c1 - p[0] * V.s1;
  return [x, p[1] * V.c2 - z1 * V.s2, z1 * V.c2 + p[1] * V.s2];
}
function proj(V, g, p) {  // to the screen: [x, y, scale k, depth]
  const v = view(V, p), k = g.D / (g.D - v[2]);
  return [g.cx + v[0] * k * g.s, g.cy - v[1] * k * g.s, k, v[2]];
}
function slab(c, i) {  // a slab's size and its place: one row of up to 4 across the track, a second row behind it
  const C = CASES[c], small = C.n > 3, per = small ? 4 : 3, row = Math.floor(i / per), cnt = Math.min(per, C.n - row * per);
  const a = small ? 17 : 24, b = small ? 13 : 18, gap = 2 * b + (small ? 8 : 12);
  return { a, b, h: small ? 11 : 16, z: (i % per - (cnt - 1) / 2) * gap, row, dx: 2 * a + 14 };
}
function tokenAt(c, i, t) {
  const C = CASES[c], L = slab(c, i), fate = C.fate[i], u = t - T.out;
  const x0 = ST.idea - L.row * L.dx, x1 = ST.gate - RING.r - L.a - 12 - L.row * L.dx;
  let x = x0 + (x1 - x0) * ease((t - T.slide - i * 110) / T.slideDur), y = 8 * (1 - ease(t / T.appear)), sc = 1, hollow = 0;
  const op = ease(t / T.appear) * fadeOut(t);
  if (fate === "stop") hollow = ease(u / 700);
  if (fate === "pass") {
    x += (ST.gpu - x1) * ease(u / 1300) + (ST.board - ST.gpu) * ease((u - 1600) / 700);
    if (C.trim) sc = 1 - .42 * ease((x - ST.gate + 16) / 32);
  }
  if (fate === "skip") { x += (ST.board - x1) * ease(u / 2000); y += skipY(x); }
  return { x, y, z: L.z, sc, hollow, op, a: L.a, b: L.b, h: L.h, fate };
}
const fadeOut = t => 1 - ease((t - T.fade) / (T.len - T.fade));
function beamAt(j, t) {
  const s = T.beam + j * T.beamGap, f = fadeOut(t);
  return { p: ease((t - s) / T.beamDur), op: f * (1 - .5 * ease((t - s - 900) / 600)) * (t > s ? 1 : 0),
           lit: ease((t - s - T.beamDur + 80) / 300) * f, label: ease((t - s - T.beamDur) / 350) * f,
           pulse: Math.sin(Math.PI * clamp((t - s) / 800)) };
}
const extraAt = (m, t) => ease((t - T.extra - m * 140) / 300) * fadeOut(t);
function skipY(x) { return 70 * Math.sin(Math.PI * clamp((x - ST.gate - 34) / (ST.board - 30 - ST.gate - 34))); }
function corners(s) {  // the 8 corners of a slab
  const out = [];
  for (const X of [s.x - s.a * s.sc, s.x + s.a * s.sc]) for (const Y of [s.y, s.y + s.h * s.sc]) for (const Z of [s.z - s.b * s.sc, s.z + s.b * s.sc]) out.push([X, Y, Z]);
  return out;
}
const textW = (s, fs) => s.length * fs * .53;  // the width of a label in the display font, estimated
/* The outcome tags: anchored on where the slabs end, so they never chase a moving slab. Each is [text, x, y, anchor, opacity]. */
function tagsAt(c, t, V, g, fs) {
  const C = CASES[c], out = [], f = fadeOut(t), fit = (x, w, anchor) => {
    const lo = anchor === "end" ? 8 + w : anchor === "middle" ? 8 + w / 2 : 8, hi = anchor === "end" ? g.w - 8 : anchor === "middle" ? g.w - 8 - w / 2 : g.w - 8 - w;
    return Math.min(hi, Math.max(lo, x));
  };
  const ends = Array.from({ length: C.n }, (_, i) => tokenAt(c, i, T.end));
  if (g.w < 520) {  // a phone: no room beside the slabs, so the tags sit on one line under the scene, stopped left, passed right
    if (C.stopTag) out.push([C.stopTag, 8, g.h - 10, "start", ease((t - T.out - 500) / 400) * f]);
    if (C.goTag) out.push([C.goTag, g.w - 8, g.h - 10, "end", ease((t - T.out - 1400) / 400) * f]);
    return out;
  }
  const stopped = ends.filter(s => s.fate === "stop");
  if (stopped.length) {
    const P = stopped.flatMap(s => corners(s).map(p => proj(V, g, p)));
    const xs = P.map(p => p[0]), ys = P.map(p => p[1]), x = Math.min(...xs) - 12, w = textW(C.stopTag, fs), op = ease((t - T.out - 500) / 400) * f;
    if (x - w >= 8) out.push([C.stopTag, x, (Math.min(...ys) + Math.max(...ys)) / 2 + fs * .35, "end", op]);
    else {  // no room on the left: above the slabs, ending short of the gate's tube
      const y = Math.min(...ys) - fs * .6;
      let edge = Math.max(...xs);
      for (let d = A0; d <= 360 - A0; d += 4) {
        const q = proj(V, g, [ST.gate, RING.cy - RING.R * Math.cos(d * RAD), RING.R * Math.sin(d * RAD)]), rr = RING.r * q[2] * g.s;
        if (q[1] + rr > y - fs && q[1] - rr < y + fs * .3) edge = Math.min(edge, q[0] - rr - 8);
      }
      out.push([C.stopTag, fit(edge, w, "end"), y, "end", op]);
    }
  }
  const go = ends.find(s => s.fate !== "stop");
  if (go && go.fate === "skip") {
    const p = proj(V, g, [ST.gpu, skipY(ST.gpu) * .42, 0]);
    out.push([C.goTag, fit(p[0], textW(C.goTag, fs), "middle"), p[1] + fs * .35, "middle", ease((t - T.out - 1400) / 400) * f]);
  } else if (go) {
    const P = corners(go).map(p => proj(V, g, p)), x = (Math.min(...P.map(p => p[0])) + Math.max(...P.map(p => p[0]))) / 2;
    out.push([C.goTag, fit(x, textW(C.goTag, fs), "middle"), Math.min(...P.map(p => p[1])) - fs * .7, "middle", ease((t - T.out - 2200) / 400) * f]);
  }
  return out;
}
/* The points that must stay inside the box at every sway angle: the cloud, the track ends, the station names and
   the top of the gate. fitView() scales and centres the scene from them. */
function fitView(pts, w, h, fs) {
  const views = [[21, 17.5], [21, 26.5], [35, 17.5], [35, 26.5], [28, 22]].map(a => aim(a[0], a[1])), g = { cx: 0, cy: 0, s: 1, D: 1100 };
  const P = pts.concat([[ST.idea - 60, 0, 0], [ST.board + 60, 0, 0], [ST.gate, RING.cy + RING.R + RING.r, 0]],
    [ST.idea, ST.gpu, ST.board].map(x => [x, 0, LBL.side]), [[ST.gate, 0, LBL.gate]]);
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (const V of views) for (const p of P) { const q = proj(V, g, p); x0 = Math.min(x0, q[0]); x1 = Math.max(x1, q[0]); y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); }
  const padX = 2 * (10 + fs * 1.9), padT = 10, padB = fs * 1.5 + 8;
  const s = Math.min((w - padX) / (x1 - x0), (h - padT - padB) / (y1 - y0));
  return { w, h, s, D: 1100, cx: w / 2 - (x0 + x1) / 2 * s, cy: padT + (h - padT - padB) / 2 - (y0 + y1) / 2 * s };
}
// </pure>

const fig = document.getElementById("scene"), svg = document.getElementById("sc"), cvs = document.getElementById("sc-dots");
if (!fig || !svg || !cvs) return;
const ctx = cvs.getContext("2d"), NS = "http://www.w3.org/2000/svg", INK = "11,13,14";  // INK is the page's --ink
const RM = matchMedia("(prefers-reduced-motion: reduce)");
const PTS = cloud(), LIT = CASES.map(C => [...C.beams.map(b => nearest(PTS, b[1], b[2])), ...C.extra.map(e => nearest(PTS, e[0], e[1]))]);
const f1 = v => v.toFixed(1);
const put = (e, k, v) => { const c = e._c || (e._c = {}); if (c[k] !== v) { c[k] = v; e.setAttribute(k, v); } };
const mk = (tag, cls, parent) => { const e = document.createElementNS(NS, tag); if (cls) e.setAttribute("class", cls); parent.appendChild(e); return e; };
const stop = (at, color, a) => `<stop offset="${at}" style="stop-color:${color}${a == null ? "" : ";stop-opacity:" + a}"/>`;

svg.innerHTML = "<defs>" +
  `<radialGradient id="sc-porc" cx=".3" cy=".2" r=".95">${stop(0, "var(--porc-hi)")}${stop(.5, "var(--porc)")}${stop(1, "var(--porc-lo)")}</radialGradient>` +
  `<radialGradient id="sc-shade">${stop(0, "var(--ink)", .2)}${stop(.55, "var(--ink)", .08)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
  `<radialGradient id="sc-floor">${stop(0, "var(--ink)", .045)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
  `<radialGradient id="sc-glow">${stop(0, "var(--marker)", .7)}${stop(1, "var(--marker)", 0)}</radialGradient>` +
  "</defs>";
const G0 = {};
["floor", "low", "lit", "back", "far", "beams", "mid", "near", "front", "text"].forEach(n => G0[n] = mk("g", "", svg));
const floorEl = mk("ellipse", "", G0.floor); floorEl.setAttribute("fill", "url(#sc-floor)");
const ringShadow = mk("path", "shadow", G0.low), feet = [mk("path", "shadow", G0.low), mk("path", "shadow", G0.low)];
const pads = ["idea", "gpu", "board"].map(() => mk("path", "pad", G0.low));
const track = mk("path", "track", G0.low), trace = mk("path", "trace", G0.low);
const tokShadows = [], toks = [];
for (let i = 0; i < 7; i++) {
  tokShadows.push(mk("path", "shadow", G0.low));
  const g = mk("g", "tok", G0.front);
  toks.push({ g, faces: [0, 1, 2, 3, 4].map(k => mk("path", "f" + k, g)), where: G0.front });
}
const halfParts = g => ({ tube: mk("path", "tube", g), sh: mk("path", "sh", g), hi: mk("path", "hi", g), glow: mk("path", "bandglow", g), band: mk("path", "band", g) });
const ringFar = halfParts(G0.far), ringNear = halfParts(G0.near);
const glows = [], lits = [];
for (let i = 0; i < 7; i++) { glows.push(mk("circle", "glow", G0.lit)); lits.push(mk("circle", "lit", G0.lit)); }
const beams = [0, 1, 2].map(() => ({ glow: mk("path", "beamglow", G0.beams), band: mk("path", "beam", G0.beams), core: mk("path", "beamcore", G0.beams), head: mk("circle", "head", G0.beams) }));
const stations = [["Idea", ST.idea, LBL.side], ["Exa", ST.gate, LBL.gate], ["GPU run", ST.gpu, LBL.side], ["Board", ST.board, LBL.side]].map(([w, x, z]) => {
  const e = mk("text", "", G0.text); e.textContent = w; e.setAttribute("text-anchor", "middle"); return { e, x, z };
});
const dotLabels = [0, 1, 2].map(() => mk("text", "", G0.text)), tags = [0, 1].map(() => mk("text", "", G0.text));
const cloudLbl = mk("text", "", G0.text); cloudLbl.textContent = "677 pages Exa returned"; cloudLbl.setAttribute("text-anchor", "middle"); cloudLbl.style.fill = "var(--soft)"; cloudLbl.style.fontWeight = "500";  // names the cloud, so it is not read as decoration

function ribbon(p, w) {  // a stroke whose width changes along it (as in architecture.py): w(point, index) is its full width
  const n = p.length, L = [], R = [];
  for (let i = 0; i < n; i++) {
    const a = p[Math.max(0, i - 1)], b = p[Math.min(n - 1, i + 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, half = w(p[i], i) / 2;
    L.push(f1(p[i][0] - dy / d * half) + " " + f1(p[i][1] + dx / d * half));
    R.push(f1(p[i][0] + dy / d * half) + " " + f1(p[i][1] - dx / d * half));
  }
  return "M" + L.join("L") + "L" + R.reverse().join("L") + "Z";
}
const poly = P => "M" + P.map(p => f1(p[0]) + " " + f1(p[1])).join("L") + "Z";

let G = null, V = aim(28, 22), fs = 14;
function floorRing(cx, cz, rx, rz) {
  const P = [];
  for (let i = 0; i < 28; i++) { const a = i / 28 * 2 * Math.PI; P.push(proj(V, G, [cx + rx * Math.cos(a), 0, cz + rz * Math.sin(a)])); }
  return poly(P);
}

/* The gate. A tube along a circle in the y-z plane at x = gate; the floor cuts it below A0. The light comes from the
   upper left, so each point gets a highlight line on its lit side and a shade line on the other. */
const LGT = [-.55, .72, .42];
function drawHalf(parts, a0, a1, pulse) {
  const { R, r, cy } = RING, C = [], H = [], S = [], B = [];
  for (let i = 0; i <= 26; i++) {
    const a = (a0 + (a1 - a0) * i / 26) * RAD, ca = Math.cos(a), sa = Math.sin(a);
    const c = [ST.gate, cy - R * ca, R * sa], l1 = LGT[1] * -ca + LGT[2] * sa, l2 = LGT[0], ln = Math.hypot(l1, l2) || 1;
    const nb = [l2 / ln, -l1 * ca / ln, l1 * sa / ln];
    const at = (m, v) => proj(V, G, [c[0] + m * v[0], c[1] + m * v[1], c[2] + m * v[2]]);
    C.push(proj(V, G, c)); H.push(at(r * .6, nb)); S.push(at(-r * .62, nb)); B.push(at(-r * .74, [0, -ca, sa]));
  }
  const w = m => p => m * r * p[2] * G.s;
  put(parts.tube, "d", ribbon(C, w(2))); put(parts.sh, "d", ribbon(S, w(.55))); put(parts.hi, "d", ribbon(H, w(.3)));
  put(parts.band, "d", ribbon(B, w(.24))); put(parts.glow, "d", ribbon(B, w(.85)));
  put(parts.glow, "opacity", f1(.12 + .5 * pulse));
}

const FACES = [  // top, -x, +x, -z, +z: corner indices into [x, y, z] choices, and the outward normal
  { n: [0, 1, 0], v: [[0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1]] },
  { n: [-1, 0, 0], v: [[0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0]] },
  { n: [1, 0, 0], v: [[1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1]] },
  { n: [0, 0, -1], v: [[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]] },
  { n: [0, 0, 1], v: [[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]] },
];
function drawToken(tk, s) {
  const X = [s.x - s.a * s.sc, s.x + s.a * s.sc], Y = [s.y, s.y + s.h * s.sc], Z = [s.z - s.b * s.sc, s.z + s.b * s.sc];
  FACES.forEach((F, k) => {
    const pts = F.v.map(q => [X[q[0]], Y[q[1]], Z[q[2]]]);
    const c = pts.reduce((m, p) => [m[0] + p[0] / 4, m[1] + p[1] / 4, m[2] + p[2] / 4], [0, 0, 0]);
    const vc = view(V, c), vn = view(V, F.n);
    const seen = vn[0] * -vc[0] + vn[1] * -vc[1] + vn[2] * (G.D - vc[2]) > 0;
    put(tk.faces[k], "d", seen ? poly(pts.map(p => proj(V, G, p))) : "");
  });
  put(tk.g, "opacity", f1(s.op));
  put(tk.g, "fill-opacity", (1 - s.hollow).toFixed(2));
  put(tk.g, "class", s.hollow > .5 ? "tok hollow" : "tok");
}

let cur = 0, auto = true, clock = 0, ent = 0, ent0 = 0, vt = 0, last = 0, raf = 0, onScreen = false, still = RM.matches;
const lean = { x: 0, y: 0, tx: 0, ty: 0 };

function size() {
  const b = fig.getBoundingClientRect(), w = Math.max(1, b.width), h = Math.max(1, b.height), dpr = window.devicePixelRatio || 1;
  G = fitView(PTS, w, h, 14);
  fs = Math.max(11, Math.min(16, 14 * G.s));
  G = fitView(PTS, w, h, fs);
  const s = G.s;
  svg.setAttribute("viewBox", `0 0 ${f1(w)} ${f1(h)}`);
  cvs.width = Math.round(w * dpr); cvs.height = Math.round(h * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  put(floorEl, "cx", f1(G.cx)); put(floorEl, "cy", f1(G.cy - 10 * s)); put(floorEl, "rx", f1(420 * s)); put(floorEl, "ry", f1(130 * s));
  stations.forEach(st => put(st.e, "font-size", f1(fs)));
  put(cloudLbl, "font-size", f1(fs * .92));
  dotLabels.forEach(e => put(e, "font-size", f1(fs * .92)));
  tags.forEach(e => put(e, "font-size", f1(fs * .92)));
}

function drawDots(E) {
  ctx.clearRect(0, 0, G.w, G.h);
  const n = Math.floor(CL.n * clamp(E * 1.15)), P = [];
  let kmin = Infinity, kmax = -Infinity;
  for (let i = 0; i < n; i++) { const p = proj(V, G, PTS[i]); P.push(p); kmin = Math.min(kmin, p[2]); kmax = Math.max(kmax, p[2]); }
  const span = kmax - kmin || 1, rs = Math.max(.6, G.s);
  for (let b = 0; b < 6; b++) {
    const q = b / 5;
    ctx.fillStyle = `rgba(${INK},${(.13 + .45 * q).toFixed(3)})`;
    ctx.beginPath();
    for (const p of P) {
      if (Math.min(5, Math.round((p[2] - kmin) / span * 5)) !== b) continue;
      const r = (.85 + 1.15 * q) * rs;
      ctx.moveTo(p[0] + r, p[1]); ctx.arc(p[0], p[1], r, 0, 2 * Math.PI);
    }
    ctx.fill();
  }
}

function render(t, E) {
  if (!G) size();
  const C = CASES[cur], vis = ease((E - .15) / .6);
  drawDots(E);
  // floor: the track draws in on entrance, then the pads, the gate's shadow and its feet
  const xa = ST.idea - 60, xb = xa + (ST.board + 70 - xa) * ease(E / .8), TP = [];
  for (let x = xa; x < xb; x += 20) TP.push(proj(V, G, [x, 0, 0]));
  TP.push(proj(V, G, [xb, 0, 0]));
  put(track, "d", ribbon(TP, p => 1.3 * p[2] * G.s));
  [ST.idea, ST.gpu, ST.board].forEach((x, i) => { put(pads[i], "d", floorRing(x, 0, 22, 22)); put(pads[i], "opacity", f1(vis)); });
  const fz = RING.R * Math.sin(A0 * RAD);
  put(ringShadow, "d", floorRing(ST.gate + 26, 34, 42, 104)); put(ringShadow, "opacity", f1(vis));
  feet.forEach((e, i) => { put(e, "d", floorRing(ST.gate, i ? fz : -fz, 22, 22)); put(e, "opacity", f1(vis)); });
  // beams and lit pages
  let pulse = 0;
  const top = proj(V, G, [ST.gate, RING.cy + RING.R + RING.r * .3, 0]);
  beams.forEach((bm, j) => {
    const b = j < C.beams.length ? beamAt(j, t) : null;
    if (!b || b.op <= 0) { put(bm.core, "d", ""); put(bm.band, "d", ""); put(bm.glow, "d", ""); put(bm.head, "r", "0"); return; }
    pulse = Math.max(pulse, b.pulse);
    const d = proj(V, G, PTS[LIT[cur][j]]), ex = top[0] + (d[0] - top[0]) * b.p, ey = top[1] + (d[1] - top[1]) * b.p;
    const path = `M${f1(top[0])} ${f1(top[1])}L${f1(ex)} ${f1(ey)}`;
    put(bm.core, "d", path); put(bm.band, "d", path); put(bm.glow, "d", path); put(bm.core, "opacity", b.op.toFixed(2)); put(bm.band, "opacity", b.op.toFixed(2)); put(bm.glow, "opacity", (.3 * b.op).toFixed(2));
    put(bm.head, "cx", f1(ex)); put(bm.head, "cy", f1(ey)); put(bm.head, "r", b.p > 0 && b.p < 1 ? f1(2.6 * Math.max(.7, G.s)) : "0");
  });
  lits.forEach((e, m) => {
    const nb = C.beams.length, has = m < LIT[cur].length;
    const a = !has ? 0 : m < nb ? beamAt(m, t).lit : extraAt(m - nb, t);
    if (a <= 0) { put(e, "r", "0"); put(glows[m], "r", "0"); return; }
    const d = proj(V, G, PTS[LIT[cur][m]]), rs = Math.max(.65, G.s);
    put(e, "cx", f1(d[0])); put(e, "cy", f1(d[1])); put(e, "r", f1((1.8 + 2.4 * a) * rs)); put(e, "opacity", a.toFixed(2));
    put(glows[m], "cx", f1(d[0])); put(glows[m], "cy", f1(d[1])); put(glows[m], "r", f1(15 * a * rs));
  });
  dotLabels.forEach((e, j) => {
    const a = j < C.beams.length ? beamAt(j, t).label : 0;
    if (a <= 0) { put(e, "opacity", "0"); return; }
    const d = proj(V, G, PTS[LIT[cur][j]]);
    put(e, "x", f1(d[0] + 9 * Math.max(.7, G.s))); put(e, "y", f1(d[1] + fs * .32)); put(e, "opacity", a.toFixed(2));
  });
  // the gate
  drawHalf(ringFar, 180, 360 - A0, pulse); drawHalf(ringNear, A0, 180, pulse);
  put(G0.far, "opacity", f1(vis)); put(G0.near, "opacity", f1(vis));
  // the slabs: behind the gate, inside it, or in front of it (the view looks from the Idea side)
  const order = [];
  toks.forEach((tk, i) => {
    if (i >= C.n) { put(tk.g, "opacity", "0"); put(tokShadows[i], "d", ""); return; }
    const s = tokenAt(cur, i, t);
    const where = s.x < ST.gate - s.a - RING.r ? G0.front : s.x > ST.gate + s.a + RING.r ? G0.back : G0.mid;
    if (tk.where !== where) { where.appendChild(tk.g); tk.where = where; }
    drawToken(tk, s);
    put(tokShadows[i], "d", floorRing(s.x + 6, s.z + 8, s.a * s.sc * 1.5, s.b * s.sc * 1.6));
    put(tokShadows[i], "opacity", (s.op * (1 - s.hollow) / (1 + s.y / 25)).toFixed(2));
    order.push([view(V, [s.x, 0, s.z])[2], tk]);
  });
  order.sort((a, b) => a[0] - b[0]);
  const key = order.map(o => toks.indexOf(o[1])).join();
  if (key !== render.key) { render.key = key; order.forEach(o => o[1].where.appendChild(o[1].g)); }
  // the arc of a skipped GPU run
  if (C.fate.includes("skip")) {
    const P = [];
    for (let x = ST.gate + 34; x <= ST.board - 30; x += 12) P.push(proj(V, G, [x, skipY(x) + 6, 0]));
    put(trace, "d", "M" + P.map(p => f1(p[0]) + " " + f1(p[1])).join("L"));
    put(trace, "opacity", (.7 * ease((t - T.out) / 500) * fadeOut(t)).toFixed(2));
  } else put(trace, "d", "");
  // outcome tags
  const TG = tagsAt(cur, t, V, G, fs * .92);
  tags.forEach((e, j) => {
    const q = TG[j];
    if (!q || q[4] <= 0) { put(e, "opacity", "0"); return; }
    if (e.textContent !== q[0]) e.textContent = q[0];
    put(e, "x", f1(q[1])); put(e, "y", f1(q[2])); put(e, "text-anchor", q[3]); put(e, "opacity", q[4].toFixed(2));
  });
  // station names, upright, in front of the track
  stations.forEach(st => {
    const p = proj(V, G, [st.x, 0, st.z]);
    put(st.e, "x", f1(p[0])); put(st.e, "y", f1(p[1] + fs * .95)); put(st.e, "opacity", f1(ease((E - .5) / .5)));
  });
  const pc = proj(V, G, [CL.x - CL.rx * .72, CL.y - 52, CL.z]);
  put(cloudLbl, "x", f1(pc[0])); put(cloudLbl, "y", f1(pc[1])); put(cloudLbl, "opacity", f1(ease((E - .5) / .5)));
}

function frame(now) {
  raf = 0;
  if (still || !onScreen || document.hidden) { last = 0; return; }
  const dt = last ? Math.min(1000, now - last) : 16; last = now;  // real time, so a throttled tab or a slow projector laptop still plays a case in its 9.6 s
  vt += dt;
  if (!ent0) ent0 = now;  // the entrance runs on wall-clock time: however few frames arrive, the scene is whole 1.6 s after its first frame
  if (ent < 1600) ent = Math.min(1600, now - ent0 + 16); else clock += dt;
  if (clock >= T.len) { clock -= T.len; if (auto) setCase((cur + 1) % 4, false); }
  const e = Math.min(1, dt / 450);
  lean.x += (lean.tx - lean.x) * e; lean.y += (lean.ty - lean.y) * e;
  V = aim(28 + 3 * Math.sin(vt / 16000 * 2 * Math.PI) + 4 * lean.x, 22 + 1.2 * Math.sin(vt / 23000 * 2 * Math.PI) + 3 * lean.y);
  render(clock, ease(ent / 1600));
  raf = requestAnimationFrame(frame);
}
function go() { if (!raf && !still && onScreen && !document.hidden) raf = requestAnimationFrame(frame); }
function drawStill() { V = aim(28, 22); render(T.end, 1); }

const btns = [...document.querySelectorAll(".pick button")], cases = [...document.querySelectorAll(".case")];
function setCase(n, user) {
  cur = n; clock = 0; render.key = "";
  if (user) auto = false;
  btns.forEach((b, i) => { b.setAttribute("aria-pressed", i === n ? "true" : "false"); b.tabIndex = i === n ? 0 : -1; });
  cases.forEach((c, i) => { c.classList.toggle("on", i === n); if (i === n) c.removeAttribute("aria-hidden"); else c.setAttribute("aria-hidden", "true"); });
  svg.setAttribute("aria-label", `Replay of search ${n + 1}: ${CASES[n].say}`);
  dotLabels.forEach((e, j) => { e.textContent = CASES[n].beams[j] ? CASES[n].beams[j][0] : ""; });
  if (still) drawStill();
}
function choose(n) {
  setCase(n, true);
  if (location.hash !== "#search-" + (n + 1)) history.pushState(null, "", "#search-" + (n + 1));
}
btns.forEach((b, i) => b.addEventListener("click", () => choose(i)));
document.querySelector(".pick").addEventListener("keydown", e => {
  const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
  if (!d) return;
  e.preventDefault();
  const n = (cur + d + 4) % 4; choose(n); btns[n].focus();
});
const fromHash = () => { const m = /^#search-([1-4])$/.exec(location.hash); return m ? Number(m[1]) - 1 : -1; };
window.addEventListener("hashchange", () => { const n = fromHash(); if (n >= 0 && (n !== cur || auto)) setCase(n, true); });

fig.addEventListener("pointermove", e => {
  const b = fig.getBoundingClientRect();
  lean.tx = clamp((e.clientX - b.left) / b.width) * 2 - 1; lean.ty = clamp((e.clientY - b.top) / b.height) * 2 - 1;
});
fig.addEventListener("pointerleave", () => { lean.tx = 0; lean.ty = 0; });
new ResizeObserver(() => { size(); if (still) drawStill(); }).observe(fig);
new IntersectionObserver(es => { onScreen = es[es.length - 1].isIntersecting; go(); }, { threshold: 0.05 }).observe(fig);
document.addEventListener("visibilitychange", go);
/* The same test from the box itself on scroll, so the scene still starts where the observer is late or never fires. */
const seen = () => { const r = fig.getBoundingClientRect(); onScreen = r.bottom > 0 && r.top < innerHeight; go(); };
addEventListener("scroll", seen, { passive: true }); addEventListener("resize", seen); seen();
RM.addEventListener("change", () => { still = RM.matches; if (still) drawStill(); else go(); });

size();
const h0 = fromHash();
setCase(h0 >= 0 ? h0 : 0, h0 >= 0);
if (still) drawStill(); else render(0, 0);
})();
</script>
</body>
</html>
"""
