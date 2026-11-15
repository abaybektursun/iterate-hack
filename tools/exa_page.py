"""The page /exa: how the team's agents used Exa search, counted from the session transcripts.

Numbers: studies/metaharness/results/exa_count-01/summary.json (studies/metaharness/analysis/exa_count.py).
Not a header tab, and its look is its own (white paper, one cyan marker), by the person's choice.
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
.hero h1 { text-indent: -0.45em; padding-left: 0.45em; font-size: clamp(1.9rem, 3.5vw, 3.1rem); line-height: 1.04; font-weight: 600; overflow-wrap: anywhere }
.answer { display: flex; flex-direction: column; gap: 22px; align-self: end }
.step { border-top: 2px solid var(--rule); padding-top: 12px; display: flex; flex-direction: column; gap: 8px }
.step .t { font: 600 0.92rem var(--display); font-variant-numeric: tabular-nums }
.step .big { font-size: clamp(1.6rem, 2.5vw, 2.3rem); line-height: 1.2 }
.step .src { font: 500 0.92rem var(--display) }
.thesis { grid-column: 1 / -1; border-top: 2px solid var(--rule); padding-top: 18px; font: 600 clamp(1.5rem, 2.9vw, 2.5rem)/1.12 var(--display); letter-spacing: -0.02em }
.hero mark { animation: stroke 0.9s 0.35s cubic-bezier(.3,.7,.2,1) backwards }
@keyframes stroke { from { background-size: 0% 100% } }
@media (prefers-reduced-motion: reduce) { .hero mark { animation: none } html { scroll-behavior: auto } }

section { padding-block: 56px; border-top: 2px solid var(--rule) }
h2 { font-size: clamp(1.7rem, 3vw, 2.5rem); font-weight: 600; line-height: 1.08; margin-bottom: 28px; max-width: 32ch }

.count { font: 500 clamp(1.35rem, 2.35vw, 2.05rem)/1.3 var(--display); letter-spacing: -0.015em; max-width: 34em }
.count b { font-weight: 700 }
.note { margin-top: 22px; max-width: 62ch; font-size: 1rem; color: var(--soft) }

.chart { overflow-x: auto; margin-top: 40px }
.chart svg { display: block; width: 100%; min-width: 640px; height: auto; font-family: var(--display) }
.key { display: flex; flex-wrap: wrap; gap: 8px 26px; margin-top: 12px; font: 500 0.92rem var(--display) }
.key i { display: inline-block; width: 13px; height: 13px; margin-right: 7px; vertical-align: -2px; border: 1px solid var(--ink) }
.cap { font: 500 1.14rem var(--display); margin-top: 40px }
.chart { margin-top: 14px !important }

.ledger { display: flex; flex-direction: column }
.row, .head { display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 5fr) minmax(0, 4fr) minmax(0, 4fr); gap: 14px 32px }
.head { font: 600 0.9rem var(--display); padding-bottom: 10px }
.row { border-top: 1px solid var(--rule); padding-block: 22px }
.row > * { min-width: 0; overflow-wrap: anywhere }
.row .when { font: 600 0.9rem/1.35 var(--display); font-variant-numeric: tabular-nums }
.row .when span { display: block; font-weight: 400; font-size: 0.86rem; color: var(--soft) }
.row .asked { font: 500 1.22rem/1.25 var(--display); letter-spacing: -0.01em }
.row p + p { margin-top: 10px }
.row .check { font: 500 0.9rem var(--display); color: var(--soft) }
.lbl { display: none; font: 600 0.92em var(--display) }

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
  section { padding-block: 40px }
  .head { display: none }
  .row { grid-template-columns: 1fr; gap: 14px }
  .lbl { display: inline }
  table { min-width: 0 } tr { display: block; border-top: 1px solid var(--rule); padding-block: 12px } tr:first-child { display: none }
  td, td:first-child, td:last-child { display: block; width: auto; border: 0; padding: 2px 0; overflow-wrap: anywhere }
  .chart svg { min-width: 0 }
  .asks { columns: 1 }
  .limits { grid-template-columns: 1fr }
}
</style>
</head>
<body>
<div class="wrap">

<nav>
  <b>Exa in the Swarm</b>
  <div><a href="#count">The count</a><a href="#searches">Four searches</a><a href="#asked">How agents asked</a><a href="#wiring">Wiring</a><a href="#limits">Limits</a></div>
</nav>

<header class="hero">
  <div class="ask">
    <p>Nov 15, 15:28:52 UTC. Our best result is about to go on a slide as new. An agent asks Exa:</p>
    <h1>“extrapolating the alignment weight difference beyond 1, scaling the RL checkpoint minus base delta by alpha greater than one improves reasoning”</h1>
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
  <p class="thesis">61 agents did this 381 times in 18 hours. The whole bill was about $1.80.</p>
</header>

<section id="count">
  <h2>The count, from the session transcripts</h2>
  <p class="count">Between Nov 14, 21:37 and Nov 15, 15:29 UTC, <b>61 agents</b> and subagents of <b>3 people</b> made <b>381 Exa calls</b> that returned: <b>237 searches</b> and <b>144 page reads</b>. They wrote <b>426 different queries</b>, median <b>16 words</b>. Search surfaced <b>677 pages</b>, <b>261</b> of them arXiv papers, and the agents read <b>188</b> in full. A search cost <b>$0.007</b>. A headless theory engine, whose only route to the web is Exa, wrote <b>163 published findings</b> into its rounds.</p>
  <p class="note">Counted from 557 transcript files on this laptop and in the team trace store, each tool call once, shell loops expanded. $0.62 of the bill is read from the tool's cost lines on 91 calls; the rest is estimated at $0.007 per search and $0.001 per page. The count is low: most of one teammate's sessions and every theory-engine run left no transcript. The Exa dashboards hold the exact figure.</p>
  <p class="cap">Calls per hour, UTC. The busiest working hour was 04:00, with 110 of 118 returned.</p>
  <div class="chart"><svg id="hours" viewBox="0 0 1240 330" role="img" aria-label="Exa calls per UTC hour: returned and never sent"></svg></div>
  <div class="key"><span><i style="background:var(--ink)"></i>returned</span><span><i></i>never reached Exa: one laptop had no key</span></div>
</section>

<section id="searches">
  <h2>Four searches that changed a decision</h2>
  <div class="ledger">
    <div class="head"><div>When</div><div>The agent asked</div><div>Exa returned</div><div>What changed</div></div>

    <div class="row">
      <div class="when">Nov 15, 15:28<span>novelty audit of the top finding</span></div>
      <div class="asked">“top singular directions of the RL fine-tuning weight update recover most of the reasoning gain, low-rank RL parameter update”</div>
      <div><p><b class="lbl">Exa returned: </b>arXiv 2510.00553: <mark>“top singular subspace… captures over 99% of reasoning gains”</mark>. The next search, eight seconds later, returned ThinkEdit: <mark>“reasoning length is governed by a linear direction”</mark>.</p></div>
      <div><p><b class="lbl">What changed: </b>With the ExPO hit above, two novelty claims came off the finding and one stayed. Three searches, 13 seconds, about 2 cents.</p><p class="check">Checked at the transcript.</p></div>
    </div>

    <div class="row">
      <div class="when">Nov 14, 21:40<span>interpretability study</span></div>
      <div class="asked">“Jacobian lens open source implementation github anthropic J-lens global workspace”</div>
      <div><p><b class="lbl">Exa returned: </b>A published lens for our exact base model: <mark>huggingface.co/neuronpedia/jacobian-lens and github.com/anthropics/jacobian-lens</mark>.</p></div>
      <div><p><b class="lbl">What changed: </b>On the board six minutes later (knowledge-0220f1). <code>studies/jspace/lib/jlens_read.py</code> loads it, and the same session posted result-da11d0 with no GPU job.</p><p class="check">Checked at the transcript.</p></div>
    </div>

    <div class="row">
      <div class="when">Nov 15, 08:01<span>before a 29 USD run</span></div>
      <div class="asked">“add the weight difference of an RL-trained reasoning model (RL minus base) to a supervised fine-tuned sibling model from the same base, task arithmetic transplant of RLVR delta, math accuracy”</div>
      <div><p><b class="lbl">Exa returned: </b><mark>“Decouple before Integration: Test-time Synthesis of SFT and RLVR Task Vectors”</mark>, arXiv 2605.00610.</p></div>
      <div><p><b class="lbl">What changed: </b>A subagent read the paper in full for a go or no-go. The run went ahead, and its result says what is ours: “Summing SFT and RL vectors is published (2605.00610); the dose curve and control are new”.</p><p class="check">Checked at the transcript.</p></div>
    </div>

    <div class="row">
      <div class="when">Nov 14, 21:12<span>literature sweep by 5 agents</span></div>
      <div class="asked soft">The session that made this search is not in the trace store.</div>
      <div><p><b class="lbl">Exa returned: </b>arXiv 2610.24663 and six more papers, cited on the board in knowledge-d692e4.</p></div>
      <div><p><b class="lbl">What changed: </b>Seven method families were listed as already published. The team ran none of them.</p><p class="check">Board item checked. The earliest return of 2610.24663 we can show is 21:42 UTC.</p></div>
    </div>
  </div>
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
  <p class="note">Verbatim, eight of 426. Each is the experiment the agent was about to run, written as the abstract of the paper that would make it unnecessary.</p>
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
    <li><b>One laptop never had the key.</b>193 calls stopped at “EXA_API_KEY is not set” before reaching Exa, 149 of them in one session at 15:00 UTC on Nov 15. All 195 calls from that machine failed.</li>
    <li><b>The MCP route failed.</b>59 calls through the Exa MCP returned 401: the key was unset when the agent started. Commit af5fef1 replaced it with <code>tools/exa.py</code>, which reads the key at call time.</li>
    <li><b>One search missed.</b>The lens search did not return mhough/olmo3-jacobian-lenses, which holds lenses for the RL model. It turned up two hours later, after a fit job had started.</li>
    <li><b>No count of GPU jobs avoided.</b>No artifact supports a dollar figure for what the searches saved, so this page gives none.</li>
    <li><b>144 calls are counted from silence.</b>They wrote their output to a file, and count as returned because the transcript shows no error.</li>
  </ul>
</section>

<footer>iterate-hack, SF AI Research Hackathon, Nov 14–15, 2026. Counted Nov 15 at about 15:50 UTC. Counting script: <code>studies/metaharness/analysis/exa_count.py</code>. Its output: <code>studies/metaharness/results/exa_count-01/summary.json</code>.</footer>

</div>
<script>
const hours = ["14 21","14 22","14 23","15 00","15 01","15 02","15 03","15 04","15 05","15 06","15 07","15 08","15 09","15 10","15 11","15 12","15 13","15 14","15 15"];
const all = [33,0,24,0,14,29,69,118,9,36,19,16,15,27,3,0,0,2,172];
const ok  = [30,0,22,0,14,29,50,110,6,34,17,15,15,23,3,0,0,2,11];
const svg = document.getElementById("hours");
function draw() {
  const narrow = svg.parentNode.clientWidth < 620;
  const W = narrow ? 620 : 1240, H = narrow ? 380 : 330, L = 2, R = 2, T = 30, B = narrow ? 62 : 50, max = 180, fs = narrow ? 19 : 14;
  const pw = (W - L - R) / hours.length, y = v => T + (H - T - B) * (1 - v / max), pad = narrow ? 3 : 8;
  let s = "";
  hours.forEach((h, i) => {
    const x = L + i * pw + pad, w = pw - 2 * pad;
    if (all[i] > ok[i]) s += `<rect x="${x + 0.5}" y="${y(all[i])}" width="${w - 1}" height="${y(ok[i]) - y(all[i])}" fill="#fbfcfc" stroke="#0b0d0e" stroke-width="1"/>`;
    if (ok[i]) s += `<rect x="${x}" y="${y(ok[i])}" width="${w}" height="${y(0) - y(ok[i])}" fill="#0b0d0e"/>`;
    const label = narrow ? (all[i] >= 100 ? String(all[i]) : "") : (all[i] ? ok[i] + (all[i] > ok[i] ? " of " + all[i] : "") : "");
    if (label) s += `<text x="${x + w / 2}" y="${y(all[i]) - 7}" text-anchor="middle" font-size="${fs}" font-weight="600" fill="#0b0d0e">${label}</text>`;
    if (!narrow || i % 3 === 0) s += `<text x="${x + w / 2}" y="${H - B + fs + 6}" text-anchor="middle" font-size="${fs}" fill="#555d61">${h.slice(3)}${narrow ? "h" : ":00"}</text>`;
    if (i === 0 || h === "15 00") s += `<text x="${x}" y="${H - B + 2 * fs + 12}" font-size="${fs}" font-weight="600" fill="#0b0d0e">Nov ${h.slice(0, 2)}</text>`;
  });
  s += `<line x1="${L}" x2="${W - R}" y1="${y(0)}" y2="${y(0)}" stroke="#0b0d0e" stroke-width="2"/>`;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.innerHTML = s;
}
draw(); addEventListener("resize", draw);

</script>
</body>
</html>
"""
