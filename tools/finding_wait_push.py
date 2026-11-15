"""Pushing the base model to think "Wait" as often as the RL model does not raise its MATH-500 score.

The page of one finding, served at /finding/wait-push (copied from tools/finding_rl_wait_habit.py; draw() has three states of
one push and a dashed line for the RL model). Unlisted: UNLISTED keeps it out of the site header.
Study: studies/jspace (README.md, specs/SPEC3_steer.md).
"""
import json

TITLE = "Pushing Wait"
PROBLEM = "Is thinking Wait more often why the RL model scores higher?"
LINE = "Pushed to the RL model's Wait rate, the base model still solves 413 of 500."
UNLISTED = True  # reachable by its link only

# Every number is copied from the artifacts named here. None is typed from memory.
DATA = {
    "commit": "7caf451",
    "states": [
        {
            "name": "No push",
            "note": "The base model, Olmo 3 7B, solving MATH-500 as it is."
        },
        {
            "name": "RL's Wait rate",
            "note": "A vector added inside the model makes it write Wait about as often as the RL model does."
        },
        {
            "name": "Harder push",
            "note": "The same vector at one and a half times the strength."
        }
    ],
    "rows": [
        {
            "name": "Wait written",
            "value": [
                6.3,
                8.3,
                11.2
            ],
            "rl": 8.81,
            "rl_artifact": "the stored T2 answers of studies/rlneurons (Volume iterate-runs, inputs/rln5/T2.jsonl), counted with studies/jspace/lib/steer.py HOLD_WORDS",
            "unit": "rate",
            "of": "times the model writes Wait or Hmm per 1,000 tokens of its solutions",
            "delta": [
                "",
                "+33 %",
                "+79 %"
            ],
            "artifact": "studies/jspace/results/steer/main-01/metrics.json",
            "key": "arms.*.hold_words_per_1k_tokens"
        },
        {
            "name": "Problems solved",
            "value": [
                421,
                413,
                381
            ],
            "rl": 457,
            "rl_artifact": "studies/rlneurons/results/day1_wdiff/rl_cue-01/metrics.json, counts.correct_v3",
            "value_note": "No push is the mean of the two unsteered runs, 430 and 411 (arms.none and arms['none, second seed']), rounded up from 420.5",
            "unit": "of",
            "total": 500,
            "of": "MATH-500 problems solved, of 500",
            "delta": [
                "",
                "−8 problems, within the spread of repeated runs",
                "−40 problems"
            ],
            "artifact": "studies/jspace/results/steer/main-01/metrics.json",
            "key": "arms.*.right_v3"
        }
    ]
}

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    [
        "how",
        "How we know",
        "The base model solved the 500 problems of MATH-500 with and without a push toward Wait inside the model.",
        [
            "The push is one fixed vector added to the output of layer 24 of 32 at every position. Its direction is the one along which a lens reads Wait and Hmm, and its size is 6.8 % of the layer's usual output.",
            "Pushed, the model wrote Wait or Hmm 8.3 times per 1,000 tokens (RL model 8.81) and solved 413 problems. Without a push it solved 430 and 411 in two runs (mean 420.5, shown as 421). The change against four stored runs without a push is +0.5 points (95 % interval -2.2 to +3.0); the RL model solves 457.",
            "Controls: a random vector of the same size solved 409, and the same preference added to the scores of the output words solved 421. The closest published test (arXiv 2610.24663) forced the word Wait into another base model's text and lost accuracy; it did not push inside the model."
        ]
    ],
    [
        "limits",
        "What it does not show",
        "It does not show that the RL model's own extra Wait is useless to the RL model.",
        [
            "The push adds Wait everywhere. The RL model may write Wait at the places where it helps, and this test cannot tell.",
            "Inside the model the push overshoots: the lens then sees Wait at 31 % of positions, against 4.7 % without a push and 6.3 % in the RL model. A push a sixth as large matches the RL model inside and changes the written text little; its score was not measured.",
            "One pair of models, one benchmark, one sample per problem and arm."
        ]
    ],
    [
        "run",
        "How to reproduce it",
        "The study studies/jspace reproduces the numbers from a clean checkout with one GPU job per arm.",
        [
            "Generation: python -m studies.jspace.jobs.steer_gen --arms steer:hold:L24:0.068 (31 to 35 minutes per arm on one H100), inside the vLLM engine the team uses for every score.",
            "Readout: python -m studies.jspace.analysis.steer_analyze, and jobs/steer_readout.py for the numbers read inside the model.",
            "The numbers are in studies/jspace/results/steer/main-01/metrics.json and studies/jspace/results/steer/readout-01/readout.json (commit 7caf451)."
        ]
    ]
]

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Invariant: __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
:root {
  color-scheme: light dark;
  --paper: #eef2ec; --sheet: #f8faf7; --ink: #17201b; --mute: #5f6b64; --faint: #8e9a93; --rule: #d5ddd6;
  --blue: #2448d8; --red: #d2283c;
}
@media (prefers-color-scheme: dark) {
  :root { --paper: #0e1311; --sheet: #151c19; --ink: #e4ebe6; --mute: #95a39b; --faint: #66736c; --rule: #25302a; --blue: #8aa4ff; --red: #ff6577; }
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
.page {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(300px, 27vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0 48px; height: 100vh; min-height: 600px; max-width: 1840px; margin: 0 auto; padding: 24px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 22px; font-size: 13px; }
.name { font-weight: 700; font-stretch: 112%; font-size: 15px; letter-spacing: .01em; margin: 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture, and the one control that changes it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
svg { width: 100%; max-height: 62vh; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
.bar { fill: var(--blue); transform-box: fill-box; transform-origin: left center; transition: transform .7s cubic-bezier(.3, 0, .2, 1); }
.bar.same { fill: var(--faint); }
.mark { transition: transform .7s cubic-bezier(.3, 0, .2, 1); }
.rowname { font-size: 24px; font-weight: 520; }
.value { font-size: 38px; font-weight: 660; }
.of { font-size: 17px; fill: var(--mute); }
.ref { stroke: var(--ink); stroke-width: 2; }
.ref.rl { stroke: var(--red); stroke-dasharray: 6 5; }
.reftext { font-size: 18px; font-weight: 600; text-anchor: middle; }
.delta { font-size: 20px; fill: var(--mute); }
.switch { display: inline-flex; align-self: center; margin-top: 18px; border: 1px solid var(--ink); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 20px; border-radius: 999px; font-weight: 600; font-size: 15px; }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.note { align-self: center; margin: 12px 0 0; color: var(--mute); font-size: 15px; text-align: center; max-width: 52ch; min-height: 1.5em; }

/* The words */
.side { min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none; padding-top: clamp(16px, 7vh, 96px); }
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(28px, 2.5vw, 46px); line-height: 1.1; font-weight: 320; font-stretch: 106%; letter-spacing: -.015em; max-width: 14ch; }
.say b { font-weight: 660; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 112%; }
.close { font-size: 13px; color: var(--mute); }
.lead { margin: 16px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 420; max-width: 30ch; }
.facts { list-style: none; margin: 16px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 7px 0; border-top: 1px solid var(--rule); }
@media (max-width: 900px) {
  .page { display: block; height: auto; padding: 18px 16px 40px; }
  .stage { margin-top: 16px; }
  .side { overflow: visible; padding-top: 24px; }
}
@media (prefers-reduced-motion: reduce) { .bar, .mark { transition: none; } }
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">How it works</a>
    <a href="" aria-current="page">__TITLE__</a>
  </header>
  <div class="stage">
    <svg id="svg" viewBox="0 0 1000 480" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="Push"></div>
    <p class="note" id="note"></p>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const S = { state: 0, open: null };
/* Each row is one measure. Its bar is drawn relative to the base model without a push (the solid line); the dashed line is
   the RL model's value. The switch sets how hard the base model is pushed toward Wait. */
const X0 = 60, BASE = 470, W = BASE - X0;
const len = (r, s) => W * r.value[s] / r.value[0], show = (r, v) => r.unit === "of" ? `${v} of ${r.total}` : `${v}`;
function draw() {
  if (!$("svg").firstChild) $("svg").innerHTML = D.rows.map((r, i) => {
    const y = 60 + i * 190, xr = X0 + W * r.rl / r.value[0];
    return `<text class="rowname" x="${X0}" y="${y}">${r.name}</text>` +
      `<text class="of" x="${X0}" y="${y + 26}">${r.of}</text>` +
      `<rect class="bar" id="bar${i}" x="${X0}" y="${y + 42}" width="${W * 2}" height="56"/>` +
      `<line class="ref" x1="${BASE}" y1="${y + 34}" x2="${BASE}" y2="${y + 132}"/>` +
      `<line class="ref rl" x1="${xr}" y1="${y + 34}" x2="${xr}" y2="${y + 108}"/>` +
      `<line class="ref rl" x1="${xr}" y1="${y + 108}" x2="${xr}" y2="${y + 132}"/><text class="of" x="${xr + 10}" y="${y + 150}">RL model: ${show(r, r.rl)}</text>` +
      `<g class="mark" id="mark${i}"><text class="value" id="value${i}" x="16" y="${y + 84}"></text>` +
      `<text class="delta" id="delta${i}" x="16" y="${y + 112}"></text></g>`;
  }).join("") + `<text class="reftext" x="${BASE}" y="${60 + (D.rows.length - 1) * 190 + 150}" style="text-anchor:end" dx="-10">No push</text>`;
  const st = D.states[S.state];
  D.rows.forEach((r, i) => {
    $("bar" + i).style.transform = `scaleX(${len(r, S.state) / (W * 2)})`;
    $("bar" + i).classList.toggle("same", S.state === 0);
    $("mark" + i).style.transform = `translateX(${X0 + Math.max(len(r, S.state), W * r.rl / r.value[0])}px)`;
    $("value" + i).textContent = show(r, r.value[S.state]);
    $("delta" + i).textContent = r.delta[S.state];
  });
  $("svg").setAttribute("aria-label", D.rows.map(r => `${r.name}: ${show(r, r.value[S.state])}, ${st.name.toLowerCase()}`).join("; "));
  $("note").textContent = st.note;
  $("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}" aria-pressed="${i === S.state}">${s.name}</button>`).join("");
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${p[1]}</h2><button class="close" data-open="">Close</button></div><p class="lead">${p[2]}</p>` +
      `<ul class="facts">${p[3].map(f => `<li>${f}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${p[1]}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
function fromHash() { const h = location.hash.slice(1); S.open = C.panels.some(p => p[0] === h) ? h : null; pane(); }
document.addEventListener("click", e => {
  const s = e.target.closest("[data-state]"), o = e.target.closest("[data-open]");
  if (s) { S.state = Number(s.dataset.state); draw(); }
  if (o) { history.pushState(null, "", o.dataset.open ? "#" + o.dataset.open : location.pathname); fromHash(); }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) { history.pushState(null, "", location.pathname); fromHash(); }
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") { S.state = (S.state + (e.key === "ArrowRight" ? 1 : D.states.length - 1)) % D.states.length; draw(); }
});
addEventListener("hashchange", fromHash);
$("problem").textContent = C.problem;
$("say").innerHTML = C.line.replace(/(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
draw();
fromHash();
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}))
