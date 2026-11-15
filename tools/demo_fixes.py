"""The picture of the deck's slide "finding": one MATH-500 problem answered four ways, on a rising glass staircase.

demo_deck.py embeds PAGE as /demo/fig/fixes; the slide carries the words, so this page is the picture alone. Four glass
sheets stand on four steps. Each sheet is the base model's answer (Olmo 3 7B) to MATH-500 problem 21 in one
configuration, and its height stands for the cap of 16,384 generated tokens: the text fills it from the top in
proportion to the tokens generated. The height of each step is the configuration's MATH-500 score, so the stairs are
the hill climb; a dotted level marks the RL-trained model. On load the sheets fill one after another and a blue line
climbs the steps; then the view sways slowly. With prefers-reduced-motion and in print it is the settled frame.

Scores (right of 500), read at import:
  Base model   finding_opening_cue.PLAIN (plain prompt, T 1.0)
  Start        finding_opening_cue.DATA["t06_p10"]["right"] (the three-token cue, T 0.6 / top-p 1.0)
  Don't loop   finding_opening_cue.CUE (the cue, T 1.0 / top-p 1.0)
  Finish       finding_the_finish_dial.DATA["rep"]["m500"] (the cue at T 1.0 plus 8 directions at size 1.5)
  RL-trained   finding_opening_cue.RL
The answers, problem 21 of studies/rlneurons/data/rln4/math500.json (reference answer 13535):
  Base model   studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json, t3_start (14 tokens, wrong)
  Start        job sameraslan-1114-184603-9d69 (the cue at T 0.6 / top-p 1.0, the run behind t06_p10): its
               answers.jsonl, git-ignored, is fetched into runs/ with `uv run tools/gpu.py get sameraslan-1114-184603-9d69`.
               The looping sentence occurs 28 times; finish_reason length at 16,384 tokens; loop_A true.
  Don't loop   per_problem.json t1_start (the opening); the last words from finding_where_the_gap_goes.ROWS["T1"]["21"]
               ["tail"]; cut off at 16,384 tokens, failure_type cap_no_loop in
               studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json.
  Finish       studies/rlneurons/results/xreward/dial15_math500-01/rows.jsonl, problem 21: stop after 6,354 tokens,
               extracted 13535, right. No text of this answer is stored, so the sheet shows only the cue's "Okay" and the
               boxed answer.
The cue is the three tokens ' line!\\n\\nOkay' (studies/rlneurons/README.md "Definitions", data/rln4/frozen4.json
prefill_text), so every cued answer starts with "Okay".

    PYTHONPATH=.:tools python3 tools/demo_fixes.py   checks every literal against those files
"""
import json

import finding_opening_cue
import finding_the_finish_dial

N = finding_opening_cue.N
PLAIN, CUE, RL = finding_opening_cue.PLAIN, finding_opening_cue.CUE, finding_opening_cue.RL
START = finding_opening_cue.DATA["t06_p10"]["right"]
FINISH = finding_the_finish_dial.DATA["rep"]["m500"]

CAP = 16384  # generated-token cap of every run here (studies/rlneurons/README.md "Definitions")
PROBLEM = 21
# studies/rlneurons/data/rln4/math500.json, index 21: problem and answer
STATEMENT = "Find the greatest integer less than $(\\sqrt{7} + \\sqrt{5})^6.$  (Do not use a calculator!)"
GOLD = "13535"
CUE_TEXT = " line!\n\nOkay"  # data/rln4/frozen4.json prefill_text
# per_problem.json item 21, t3_start: the whole plain answer, 14 tokens (t3_generated_tokens), t3_right 0
BASE_TEXT = " for me so I know that which line is an answer line!"
BASE_TOK = 14
# the words after the cue, the same in t1_start and in the job's answer (they differ after "than")
OPENING = ", so I need to find the greatest integer less than"
# runs/sameraslan-1114-184603-9d69/answers.jsonl, problem_index 21: this sentence 28 times, finish_reason length, loop_A
LOOP = "Wait, this is impossible. There must be a mistake in one of the calculations."
LOOP_COUNT = 28
# finding_where_the_gap_goes.ROWS["T1"]["21"]["tail"] ends with these words (tok 16384, cap true)
TAIL = "So, A^6≈13,484.0000\n\nBut according to recurrence, A^6 + B"
# dial15_math500-01/rows.jsonl problem 21: n_new, extracted_v3 (score_v3 1, finish_reason stop)
FINISH_TOK = 6354

pct = lambda r: 100 * r / N

DATA = {
    "cap": CAP,
    "caption": f'One problem, four answers: "{STATEMENT.split(" $")[0]} (√7 + √5)⁶"',
    "rl": {"right": RL, "pct": pct(RL)},
    "steps": [
        {"label": "Base model", "sub": "", "pct": pct(PLAIN), "tag": "Never starts", "tag2": f"{BASE_TOK} tokens, no answer"},
        {"label": "Start", "sub": "3 opening tokens", "pct": pct(START), "tag": "Loops", "tag2": f"cut off at {CAP:,} tokens"},
        {"label": "Don't loop", "sub": "sampling, T 0.6 → 1.0", "pct": pct(CUE), "tag": "Runs out", "tag2": f"still working at {CAP:,} tokens"},
        {"label": "Finish", "sub": "8 directions in the weights", "pct": pct(FINISH), "tag": "Finishes", "tag2": f"right, in {FINISH_TOK:,} tokens"},
    ],
    "base": BASE_TEXT.strip(),
    "okay": CUE_TEXT.split("\n")[-1],
    "opening": OPENING + "…",
    "loop": LOOP, "loopCount": LOOP_COUNT,
    "tail": TAIL.split("\n\n"),
    "finishFrac": FINISH_TOK / CAP,
    "gold": GOLD,
}

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: One problem, four answers</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* Tokens of the Design page: one light from the upper left, --blue the fixes, --red the failures. */
:root {
  color-scheme: light;
  --paper: #eceef0; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de; --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f6f8f9; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --shadow: rgba(16, 24, 32, .22); --glow: 0;
  --f: "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --paper: #080c11; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630; --blue: #8fb1ff; --red: #ff6b7c;
  --glass-hi: #2c3e52; --glass: #121b24; --glass-lo: #090e14;
  --rim-a: rgba(255, 255, 255, .8); --rim-b: rgba(255, 255, 255, .12); --shadow: rgba(0, 0, 0, .6); --glow: 1;
}
html, body { margin: 0; height: 100%; overflow: hidden; background: var(--paper); }
svg { display: block; width: 100vw; height: 100vh; font-family: var(--f); font-variant-numeric: tabular-nums; }
.cap { font-size: 16px; font-weight: 500; fill: var(--mute); }
.shade { fill: var(--shadow); opacity: calc(1 - var(--glow) * .4); }
.bloom { opacity: calc(var(--glow) * .55); }
.front { stroke: var(--rim-b); stroke-width: .8; }
.tread { stroke: var(--rim-a); stroke-width: .8; }
.side { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: .8; }
.rl { stroke: var(--mute); stroke-width: 1.4; stroke-dasharray: 1.5 5; stroke-linecap: round; fill: none; }
.rlt { font-size: 15px; font-weight: 560; fill: var(--mute); }
.rlv { font-size: 21px; font-weight: 300; fill: var(--ink); }
.what { font-size: 16px; font-weight: 620; fill: var(--blue); }
.what.ink { fill: var(--ink); }
.how { font-size: 13px; font-weight: 500; fill: var(--faint); }
.score { font-size: 30px; font-weight: 300; fill: var(--ink); text-anchor: end; }
.sheet { stroke: var(--rim-a); stroke-width: .8; }
.thick { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: .8; }
.tag { font-size: 16px; font-weight: 640; fill: var(--red); }
.tag.ok { fill: var(--blue); }
.tag2 { font-size: 13px; font-weight: 500; fill: var(--mute); }
.txt { font-size: 12.5px; fill: var(--ink); }
.okay { font-size: 17px; font-weight: 600; fill: var(--ink); }
.okay.fix { fill: var(--blue); }
.times { font-size: 13px; font-weight: 640; fill: var(--red); text-anchor: end; }
.ln { stroke: var(--faint); stroke-width: 2.3; stroke-linecap: round; opacity: calc(.5 + var(--glow) * .2); }
.box { fill: var(--blue); fill-opacity: .1; stroke: var(--blue); stroke-width: 1.4; }
.halo { fill: none; stroke: var(--blue); stroke-width: 7; opacity: calc(.12 + var(--glow) * .14); }
.ans { font-size: 17px; font-weight: 640; fill: var(--blue); }
.tick { fill: none; stroke: var(--blue); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.climb { fill: none; stroke: var(--blue); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 1; }
.climb.glow { stroke-width: 7; opacity: calc(.1 + var(--glow) * .16); }
.head { fill: var(--blue); }
.head.halo2 { opacity: calc(.18 + var(--glow) * .14); }
.ap { animation: show .35s both; animation-delay: var(--d); }
.lit { animation: show .6s both; animation-delay: var(--d); }
.climb { animation: draw 1.2s both linear; animation-delay: var(--d); }
@keyframes draw { from { stroke-dashoffset: 1; } }
@keyframes show { from { opacity: 0; } }
@media (prefers-reduced-motion: reduce) { .ap, .lit, .climb { animation: none; } }
@media print { .ap, .lit, .climb { animation: none; } }
</style>
</head>
<body>
<svg id="pic" viewBox="0 0 1000 560" role="img" aria-label="__LABEL__"></svg>
<script>
"use strict";
const DATA = __DATA__;
const NS = "http://www.w3.org/2000/svg", svg = document.getElementById("pic");
const el = (p, tag, attrs, text) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (text != null) e.textContent = text; p.appendChild(e); return e; };
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

/* The scene: four glass steps from left to right, each a front face, a tread receding by the depth vector (DX, DY)
   and a right side face; a sheet stands at the back of each tread. Step height = 56 + 3 px per point above 45 %. */
const X0 = 18, BW = 215, FLOOR = 545, SW = 188, SH = 262, P = 12, IW = SW - 2 * P;
const H = p => 56 + 3 * (p - 45);
let DX = 22, DY = -16;
const T0 = .3, STEP = 1.3, FILL = 1.2;  // s: start, time between sheets, time to fill one sheet
const start = i => T0 + i * STEP;

const defs = el(svg, "defs", {});
const grad = (id, stops, x2, y2) => { const g = el(defs, "linearGradient", { id, x1: 0, y1: 0, x2, y2 }); for (const [o, c] of stops) el(g, "stop", { offset: o, style: `stop-color:var(${c})` }); };
grad("gFront", [[0, "--glass-hi"], [.55, "--glass"], [1, "--glass-lo"]], 1, 1);
grad("gTread", [[0, "--glass-hi"], [1, "--glass"]], 1, 0);
grad("gSheet", [[0, "--glass-hi"], [.7, "--glass"], [1, "--glass"]], 1, 1);
const rg = el(defs, "radialGradient", { id: "gBloom" });
el(rg, "stop", { offset: 0, style: "stop-color:var(--glass-hi)" }); el(rg, "stop", { offset: 1, style: "stop-color:var(--glass-hi);stop-opacity:0" });
const blur = el(defs, "filter", { id: "fBlur", x: "-20%", y: "-200%", width: "140%", height: "500%" });
el(blur, "feGaussianBlur", { stdDeviation: 7 });

/* text wrapping by measured width, after the font has loaded */
const meter = el(svg, "text", { class: "txt", x: -999, y: -999 });
const width = (s, cls) => { meter.setAttribute("class", cls); meter.textContent = s; return meter.getComputedTextLength(); };
function wrap(text, cls, w, first) {
  const out = []; let line = "", lim = first == null ? w : first;
  for (const word of text.split(" ")) {
    const t = line ? line + " " + word : word;
    if (line && width(t, cls) > lim) { out.push(line); line = word; lim = w; } else line = t;
  }
  if (line) out.push(line);
  return out;
}

function draw() {
  el(svg, "ellipse", { cx: 520, cy: 300, rx: 520, ry: 300, fill: "url(#gBloom)", class: "bloom" });
  const xEnd = X0 + 4 * BW;
  el(svg, "path", { d: `M${X0 + 10} ${FLOOR - 4}L${xEnd + 30} ${FLOOR - 12}L${xEnd + 70} ${FLOOR + 8}L${X0 + 40} ${FLOOR + 12}Z`, class: "shade", filter: "url(#fBlur)" });
  el(svg, "text", { x: X0, y: 24, class: "cap" }, DATA.caption);

  /* the RL-trained level, behind the sheets */
  const yRL = FLOOR - H(DATA.rl.pct);
  el(svg, "path", { d: `M${X0} ${yRL}H${xEnd + 26}`, class: "rl" });
  el(svg, "text", { x: xEnd + 32, y: yRL - 5, class: "rlt" }, "RL-trained");
  el(svg, "text", { x: xEnd + 32, y: yRL + 17, class: "rlv" }, Math.round(DATA.rl.pct) + " %");

  const moving = [];  // [kind, element, step]: what the sway updates
  const tops = DATA.steps.map(s => FLOOR - H(s.pct));
  DATA.steps.forEach((s, i) => {
    const x0 = X0 + i * BW, x1 = x0 + BW, top = tops[i];
    moving.push(["side", el(svg, "path", { class: "side" }), i]);
    el(svg, "path", { d: `M${x0} ${top}H${x1}V${FLOOR}H${x0}Z`, class: "front", fill: "url(#gFront)" });
    moving.push(["tread", el(svg, "path", { class: "tread", fill: "url(#gTread)" }), i]);
    el(svg, "text", { x: x0 + 14, y: top + 24, class: i ? "what" : "what ink" }, s.label);
    if (s.sub) el(svg, "text", { x: x0 + 14, y: top + 44, class: "how" }, s.sub);
    el(svg, "text", { x: x1 - 14, y: top + 31, class: "score" }, Math.round(s.pct) + " %");
    const g = el(svg, "g", {});
    moving.push(["sheet", g, i]);
    sheet(g, i, s);
  });
  meter.remove();

  /* the climb: along the front edge of each tread and up the next riser, drawn in step with the sheets */
  const cx = i => X0 + (i + 1) * BW;
  const segs = [`M${X0 + 14} ${tops[0]}H${cx(0)}`];
  for (let i = 1; i < 4; i++) segs.push(`M${cx(i - 1)} ${tops[i - 1]}V${tops[i]}H${i < 3 ? cx(i) : cx(i) - 40}`);
  segs.forEach((d, i) => {
    for (const cls of ["climb glow", "climb"]) el(svg, "path", { d, class: cls, pathLength: 1, style: `--d:${start(i)}s` });
  });
  const hx = cx(3) - 40, hy = tops[3], hd = `--d:${start(3) + FILL}s`;
  el(svg, "circle", { cx: hx, cy: hy, r: 10, class: "head halo2 lit", style: hd });
  el(svg, "circle", { cx: hx, cy: hy, r: 4.5, class: "head lit", style: hd });

  const place = () => {
    for (const [kind, e, i] of moving) {
      const x0 = X0 + i * BW, x1 = x0 + BW, top = tops[i];
      if (kind === "side") e.setAttribute("d", `M${x1} ${top}l${DX} ${DY}V${FLOOR + DY}L${x1} ${FLOOR}Z`);
      else if (kind === "tread") e.setAttribute("d", `M${x0} ${top}H${x1}l${DX} ${DY}H${x0 + DX}Z`);
      else e.setAttribute("transform", `translate(${(x0 + DX + 2).toFixed(2)} ${(top + DY - SH).toFixed(2)})`);
    }
  };
  place();
  if (still) return;
  /* after the entrance the view sways slowly: the depth vector moves by a few px, nothing else */
  const t0 = performance.now() + (start(3) + FILL + .6) * 1000;
  let on = true;
  addEventListener("beforeprint", () => { on = false; DX = 22; DY = -16; place(); });
  addEventListener("afterprint", () => { on = true; requestAnimationFrame(frame); });
  function frame(now) {
    if (!on) return;
    const t = Math.max(0, now - t0) / 1000, k = Math.min(1, t / 4), a = 2 * Math.PI * t / 16;
    DX = 22 + k * 2.4 * Math.sin(a); DY = -16 + k * 1.4 * Math.sin(a + 1.1);
    place();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

/* abstract text: thin rounded strokes of varied length, from a fixed seed */
function lines(g, y0, y1, seed, d0, pattern) {
  let r = seed, n = 0;
  const rnd = () => (r = (r * 16807) % 2147483647) / 2147483647;
  for (let y = y0; y < y1; y += 8, n++) {
    let f = pattern ? pattern[n % pattern.length] : (n % 6 === 5 ? .25 + .35 * rnd() : .62 + .38 * rnd());
    el(g, "line", { x1: P, x2: P + f * IW, y1: y, y2: y, class: "ln ap", style: `--d:${d0(y)}s` });
    if (!pattern && n % 6 === 5) y += 5;
  }
}

function sheet(g, i, s) {
  const d0 = y => (start(i) + Math.min(1, Math.max(0, y / SH)) * FILL).toFixed(2);
  const ap = y => ({ style: `--d:${d0(y)}s` });
  el(g, "text", { x: 0, y: -26, class: i === 3 ? "tag ok" : "tag" }, s.tag);
  el(g, "text", { x: 0, y: -10, class: "tag2" }, s.tag2);
  el(g, "rect", { x: 3, y: -2.5, width: SW, height: SH, rx: 3, class: "thick" });
  el(g, "rect", { x: 0, y: 0, width: SW, height: SH, rx: 3, class: "sheet", fill: "url(#gSheet)" });
  const id = "clip" + i, cp = el(defs, "clipPath", { id });
  el(cp, "rect", { x: 0, y: 0, width: SW, height: SH, rx: 3 });
  const c = el(g, "g", { "clip-path": `url(#${id})` });
  const para = (text, y, cls, extra) => { for (const t of wrap(text, cls, IW)) { el(c, "text", { x: P, y, class: cls + " ap", ...ap(y), ...extra }, t); y += 15.5; } return y; };
  const opening = (fix) => {
    const okay = el(c, "text", { x: P, y: P + 16, class: (fix ? "okay fix" : "okay") + " ap", ...ap(P) }, DATA.okay);
    const ow = width(DATA.okay, "okay");
    const ls = wrap(DATA.opening, "txt", IW, IW - ow - 1);
    el(c, "text", { x: P + ow, y: P + 16, class: "txt ap", ...ap(P) }, ls[0]);
    let y = P + 33;
    for (const t of ls.slice(1)) { el(c, "text", { x: P, y, class: "txt ap", ...ap(y) }, t); y += 15.5; }
    return y;
  };
  if (i === 0) {
    para(DATA.base, P + 16, "txt");
  } else if (i === 1) {
    let y = opening(true) + 4;
    lines(c, y, y + 24, 7, d0); y += 32;
    const sent = wrap(DATA.loop, "txt", IW);
    [1, .62, .36].forEach((o, k) => {
      sent.forEach((t, j) => {
        el(c, "text", { x: P, y: y + 10, class: "txt ap", opacity: o, ...ap(y) }, t);
        if (k === 0 && j === sent.length - 1) el(c, "text", { x: SW - P, y: y + 10, class: "times ap", ...ap(y) }, "× " + DATA.loopCount);
        y += 15.5;
      });
      y += 3;
    });
    /* the same lines again, in the shape of the sentence, down past the bottom edge */
    lines(c, y + 4, SH + 8, 1, d0, sent.map(t => Math.min(1, width(t, "txt") / IW)));
  } else if (i === 2) {
    let y = opening(false) + 4;
    const tail = DATA.tail.map(t => wrap(t, "txt", IW));
    const tailH = tail.reduce((a, l) => a + l.length * 15.5 + 5, 0);
    let yt = SH - tailH + 6;
    lines(c, y, yt - 12, 11, d0);
    for (const ls of tail) { for (const t of ls) { el(c, "text", { x: P, y: yt + 6, class: "txt ap", ...ap(yt) }, t); yt += 15.5; } yt += 5; }
  } else {
    el(c, "text", { x: P, y: P + 16, class: "okay ap", ...ap(P) }, DATA.okay);
    const yEnd = DATA.finishFrac * SH;
    lines(c, P + 30, yEnd, 3, d0);
    const by = yEnd + 12, bw = 96, bh = 30, lit = { style: `--d:${(start(i) + DATA.finishFrac * FILL + .25).toFixed(2)}s` };
    el(c, "rect", { x: P - 3.5, y: by - 3.5, width: bw + 7, height: bh + 7, rx: 6, class: "halo lit", ...lit });
    el(c, "rect", { x: P, y: by, width: bw, height: bh, rx: 4, class: "box lit", ...lit });
    el(c, "text", { x: P + 10, y: by + 21, class: "ans lit", ...lit }, DATA.gold);
    el(c, "path", { d: `M${P + bw + 10} ${by + 15}l5 5l10 -11`, class: "tick lit", ...lit });
  }
}

(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(draw);
</script>
</body>
</html>
"""

LABEL = ("One MATH-500 problem answered by the base model in four configurations, each on a step as high as its score: "
         + "; ".join(f'{s["label"]} {round(s["pct"])} %: {s["tag"].lower()}, {s["tag2"]}' for s in DATA["steps"])
         + f'. RL-trained model {round(DATA["rl"]["pct"])} %.')
PAGE = (PAGE.replace("__LABEL__", LABEL.replace('"', "&quot;"))
        .replace("__DATA__", json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")))


if __name__ == "__main__":  # run from the repository root
    import os

    assert (PLAIN, START, CUE, FINISH, RL, N) == (224, 378, 410, 456, 463, 500), (PLAIN, START, CUE, FINISH, RL, N)
    assert [round(s["pct"]) for s in DATA["steps"]] + [round(DATA["rl"]["pct"])] == [45, 76, 82, 91, 93]
    prob = json.load(open("studies/rlneurons/data/rln4/math500.json"))[PROBLEM]
    assert (prob["index"], prob["problem"], prob["answer"]) == (PROBLEM, STATEMENT, GOLD), prob
    assert json.load(open("studies/rlneurons/data/rln4/frozen4.json"))["prefill_text"] == CUE_TEXT
    pp = next(r for r in json.load(open(finding_opening_cue.DATA["rows"])) if r["problem_index"] == PROBLEM)
    assert (pp["t3_start"], pp["t3_generated_tokens"], pp["t3_right"]) == (BASE_TEXT, BASE_TOK, 0), pp
    assert pp["t1_start"].startswith(CUE_TEXT + OPENING) and (pp["t1_generated_tokens"], pp["t1_cap_hit"], pp["t1_right"]) == (CAP, True, 0), pp
    ft = next(r for r in json.load(open("studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json")) if r["problem_index"] == PROBLEM)
    assert (ft["t1_generated_tokens"], ft["failure_type"]) == (CAP, "cap_no_loop"), ft
    import finding_where_the_gap_goes
    row = finding_where_the_gap_goes.ROWS["T1"][str(PROBLEM)]
    assert row["tail"].endswith(TAIL) and (row["tok"], row["cap"], row["gold"]) == (CAP, True, GOLD), row
    rows = [json.loads(l) for l in open("studies/rlneurons/results/xreward/dial15_math500-01/rows.jsonl")]
    assert finding_the_finish_dial.DATA["rep"]["m500_folder"] == "studies/rlneurons/results/xreward/dial15_math500-01/"
    assert sum(r["score_v3"] for r in rows) == FINISH
    r4 = next(r for r in rows if r["problem_index"] == PROBLEM)
    assert (r4["n_new"], r4["finish_reason"], r4["cap_hit"], r4["extracted_v3"], r4["score_v3"]) == (FINISH_TOK, "stop", False, GOLD, 1), r4
    job = "runs/sameraslan-1114-184603-9d69/answers.jsonl"
    if os.path.exists(job):
        rows2 = [json.loads(l) for l in open(job)]
        assert sum(r["score_v3"] for r in rows2) == START
        r2 = next(r for r in rows2 if r["problem_index"] == PROBLEM)
        assert r2["text"].startswith(CUE_TEXT + OPENING) and r2["text"].count(LOOP) == LOOP_COUNT, r2["text"][:200]
        assert (r2["n_new"], r2["finish_reason"], r2["loop_A"], r2["sampling"]["temperature"], r2["sampling"]["top_p"]) == (CAP, "length", True, 0.6, 1.0)
        print("sheet 2 checked against", job)
    else:
        print("note: sheet 2 text not checked:", job, "is absent (uv run tools/gpu.py get sameraslan-1114-184603-9d69)")
    print("demo_fixes: every literal matches its source")
