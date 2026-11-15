"""<The finding in one sentence, with its number.>

The page of one finding, served at /finding/<slug>: view.py serves every tools/finding_<slug>.py and links it in
the header of the site. Copy this file to tools/finding_<slug>.py, fill TITLE, PROBLEM, LINE, DATA and PANELS, and
change draw() in the page only when another picture shows the finding better. The rules are in
.claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py (.claude/skills/site-ui/SKILL.md).
"""
import json

TITLE = "Two to four words"  # the link text in the site header and the browser tab
PROBLEM = "The problem, as one question a newcomer understands?"
LINE = "The finding in one sentence, with its number."

# Every number is copied from the artifact named here. None is typed from memory.
DATA = {
    "artifact": "studies/<study>/results/<experiment>/<arm>-01/metrics.json",
    "commit": "<sha of the run>",
    "metric": "<what is measured, e.g. MATH-500 accuracy>",
    "unit": "%",
    "max": 100,
    # What the reader switches between. The first is shown on load: start from the problem, not from the answer.
    "states": [
        {"name": "Without", "value": 0.0, "note": "One line: what this condition is."},
        {"name": "With", "value": 0.0, "note": "One line: what changed."},
    ],
    # The strongest baseline or the target, drawn as a line. Never compare against zero.
    "reference": {"name": "<baseline>", "value": 0.0},
}

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["how", "How we know", "The measurement in one sentence: what was run, on what, how many items.",
     ["It was measured on 0 items with grader <version>.", "The control that rules out the simple explanation.", "The closest published result, and how this one differs."]],
    ["limits", "What it does not show", "The most important thing a reader could wrongly conclude.",
     ["The condition that nobody has run yet."]],
    ["run", "How to reproduce it", "The one command that reproduces the number from a clean checkout.",
     ["The run used commit " + DATA["commit"] + ".", "Its numbers are in " + DATA["artifact"] + "."]],
]

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
.axis { stroke: var(--rule); stroke-width: 1.5; }
.bar { fill: var(--blue); transform-box: fill-box; transform-origin: left center; transition: transform .7s cubic-bezier(.3, 0, .2, 1); }
.mark { transition: transform .7s cubic-bezier(.3, 0, .2, 1); }
.value { font-size: 64px; font-weight: 660; text-anchor: middle; }
.ref { stroke: var(--ink); stroke-width: 2; }
.reftext { font-size: 20px; font-weight: 600; text-anchor: middle; }
.gap { stroke: var(--mute); stroke-width: 1.5; stroke-dasharray: 3 6; }
.gaptext { font-size: 20px; fill: var(--mute); text-anchor: middle; }
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
    <svg id="svg" viewBox="0 0 1000 420" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="Condition"></div>
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
const x = v => 60 + 880 * v / D.max, show = v => `${Math.round(v * 10) / 10}${D.unit}`;

/* The picture: one bar for the chosen condition, one line for the baseline, and the distance between them.
   Replace this function when another picture shows the finding better; keep the switch and the side column. */
function draw() {
  const st = D.states[S.state], ref = D.reference, d = ref.value - st.value;
  if (!$("svg").firstChild) $("svg").innerHTML =
    `<line class="axis" x1="60" y1="300" x2="940" y2="300"/><rect class="bar" id="bar" x="60" y="230" width="880" height="70"/>` +
    `<line class="ref" x1="${x(ref.value)}" y1="150" x2="${x(ref.value)}" y2="316"/>` +
    `<text class="reftext" x="${x(ref.value)}" y="346">${ref.name} ${show(ref.value)}</text>` +
    `<g class="mark" id="mark"><text class="value" id="value" y="200"></text></g>` +
    `<line class="gap" id="gap" y1="265" y2="265"/><text class="gaptext" id="gaptext" y="130"></text>`;
  $("svg").setAttribute("aria-label", `${D.metric}: ${st.name} ${show(st.value)}, ${ref.name} ${show(ref.value)}`);
  $("bar").style.transform = `scaleX(${st.value / D.max})`;
  $("mark").style.transform = `translateX(${x(st.value)}px)`;
  $("value").textContent = show(st.value);
  $("gap").setAttribute("x1", x(st.value)); $("gap").setAttribute("x2", x(ref.value));
  $("gaptext").setAttribute("x", (x(st.value) + x(ref.value)) / 2);
  $("gaptext").textContent = Math.abs(d) < .05 ? "" : `${show(Math.abs(d)).replace("%", " points")} ${d > 0 ? "below" : "above"}`;
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
