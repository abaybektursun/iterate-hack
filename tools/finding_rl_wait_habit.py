"""After RL the model is the same inside, except that it thinks "Wait" 24 % more often.

The page of one finding, served at /finding/rl-wait-habit (copied from .claude/skills/finding-page/template.py; draw() shows
two measures against the base model instead of one bar). It is reached from its tile on /findings, which ICON draws.
Study: studies/jspace (README.md, specs/SPEC1_lensdiff.md, specs/SPEC2_workspace.md).
"""
import json

TITLE = "What RL changed"
PROBLEM = "What does RL training change inside a model?"
LINE = "After RL the model is the same inside, but it thinks Wait 24 % more often."

# Every number is copied from the artifacts named here. None is typed from memory.
DATA = {
    "commit": "fe7e9f5",
    "states": [
        {"name": "Before RL", "note": "The base model, Olmo 3 7B, trained only to predict the next word."},
        {"name": "After RL", "note": "The same model after AI2 trained it with rewards on math problems."},
    ],
    # value[0] is the base model, value[1] the RL model, both in percent
    "rows": [
        {"name": "A hidden step can be swapped", "value": [36.4, 36.4], "of": "two-step questions where the answer follows a swapped middle step (of 44)",
         "artifact": "studies/jspace/results/workspace/pub-01/metrics.json", "key": "swap.probe-swap.*.pub.flip"},
        {"name": "Wait is in mind", "value": [4.56, 5.64], "of": "positions in math solutions where Wait is among the 8 words the model is about to write",
         "artifact": "studies/jspace/results/lensdiff/full-01/metrics.json", "key": "b_presence.T1_L24.hold_on"},
    ],
}

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new", "The closest published work compared the lenses of the two models and called RL a light change; it did not look at math text.",
     ["New here: on 500 math solutions the RL model has Wait or Hmm among the 8 words it is about to write 24 % more often than the base model.",
      "New here: swapping a hidden middle step changes the answer equally often in both models, so the inner machinery looks the same."]],
    # 45 % and 85 % are the states "untrained" (224 of 500) and "rl-directions" (427 of 500) of tools/finding_eight_directions.py.
    ["why", "Why it matters", "It narrows where the RL gain can come from: a habit of pausing to check, on top of the same inner machinery.",
     ['The page <a href="/finding/eight-directions">Eight directions</a> tests a related edit in the weights: adding the 8 strongest RL '
      "directions per matrix, some of which point at Wait and Okay, lifts the untrained model from 45 % to 85 %."]],
    ["how", "How we know", "Both models read the same text, and a lens showed which words each one was about to write.",
     ["On 500 MATH-500 solutions written by the base model, Wait or Hmm was among the top 8 words at 4.56 % of positions for the base model and 5.64 % for the RL model (95 % interval of the difference: 1.01 to 1.15 points).",
      "On 44 two-hop questions, swapping the hidden middle step inside the model changed the answer 16 times in each model. Swapping in an unrelated word did so 1 to 3 times.",
      "The closest published result (mhough/olmo3-jacobian-lenses) compared the lenses of the two models and called RL a light change. It did not look at math text."]],
    ["limits", "What it does not show", "It does not show that thinking Wait is why the RL model scores 11 points higher on MATH-500.",
     ["Nobody has yet pushed the base model toward Wait and measured its score.",
      "The extra Wait does not mark mistakes: it is no larger on the problems the base model gets wrong, and after a wrong line of arithmetic the pull toward writing Wait rises only a little more in the RL model (0.35 against 0.28 nats in its output).",
      "The 24 % comes from reading both models with one lens. With a lens fitted to each model the gap is larger: 4.63 % against 6.29 %."]],
    ["run", "How to reproduce it", "Two GPU jobs of the study studies/jspace reproduce both numbers from a clean checkout.",
     ["Wait in mind: python -m studies.jspace.jobs.lensdiff, then analysis/lensdiff_analyze.py (commit 3af965d, 23 minutes on one H100).",
      "Hidden step: python -m studies.jspace.jobs.workspace_tests, then analysis/workspace_analyze.py (commit 3208566, 6 minutes).",
      "The numbers are in " + DATA["rows"][1]["artifact"] + " and " + DATA["rows"][0]["artifact"] + "."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with the base model's line across it and the two measures as bars: the hidden step stops at
# the line, and Wait passes it by its measured share.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, top = th / 2, x0 = -a * .78, base = a * .22, more = x0 + (base - x0) * __MORE__;
  return kit.slab(a, b, th) +
    kit.line(kit.at(base, -b * .7, top), kit.at(base, b * .7, top), .7) +
    kit.line(kit.at(x0, -b * .32, top), kit.at(base, -b * .32, top), 3.4, "plain", .55) +
    kit.line(kit.at(x0, b * .32, top), kit.at(more, b * .32, top), 3.4 + .25 * Math.sin(t * .6), "lit");
}""".replace("__MORE__", str(round(DATA["rows"][1]["value"][1] / DATA["rows"][1]["value"][0], 3)))

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
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <div class="stage">
    <svg id="svg" viewBox="0 0 1000 470" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="Model"></div>
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
/* Each row is one measure. Its bar is drawn relative to the base model: the line marks the base model's value, so a bar
   that stops at the line means "no change" and a bar that passes it shows how much RL added. */
const X0 = 60, BASE = 560, pct = v => `${Math.round(v * 10) / 10} %`;
const len = (r, s) => (BASE - X0) * r.value[s] / r.value[0];
function draw() {
  if (!$("svg").firstChild) $("svg").innerHTML = D.rows.map((r, i) => {
    const y = 60 + i * 190;
    return `<text class="rowname" x="${X0}" y="${y}">${r.name}</text>` +
      `<text class="of" x="${X0}" y="${y + 26}">${r.of}</text>` +
      `<rect class="bar${r.value[0] === r.value[1] ? " same" : ""}" id="bar${i}" x="${X0}" y="${y + 42}" width="${len(r, 1)}" height="56"/>` +
      `<g class="mark" id="mark${i}"><text class="value" id="value${i}" x="16" y="${y + 84}"></text>` +
      `<text class="delta" id="delta${i}" x="16" y="${y + 112}"></text></g>`;
  }).join("") + D.rows.map((r, i) => `<line class="ref" x1="${BASE}" y1="${60 + i * 190 + 34}" x2="${BASE}" y2="${60 + i * 190 + 108}"/>`).join("") +
    `<text class="reftext" x="${BASE}" y="${60 + (D.rows.length - 1) * 190 + 134}">Before RL</text>` +
    `<text class="of" x="${BASE}" y="${60 + (D.rows.length - 1) * 190 + 158}" text-anchor="middle">each bar is drawn relative to this line</text>`;
  const st = D.states[S.state];
  D.rows.forEach((r, i) => {
    const d = r.value[S.state] / r.value[0] - 1;
    $("bar" + i).style.transform = `scaleX(${len(r, S.state) / len(r, 1)})`;
    $("mark" + i).style.transform = `translateX(${X0 + len(r, S.state)}px)`;
    $("value" + i).textContent = S.state === 0 ? pct(r.value[0]) : `${pct(r.value[0])} → ${pct(r.value[1])}`;
    $("delta" + i).textContent = S.state === 0 ? "" : Math.abs(d) < .005 ? "no change" : `${d > 0 ? "+" : ""}${Math.round(d * 100)} %`;
  });
  $("svg").setAttribute("aria-label", D.rows.map(r => `${r.name}: ${pct(r.value[S.state])} ${st.name.toLowerCase()}`).join("; "));
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
