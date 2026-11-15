"""One sentence says what a single neuron does: from the sentence alone, a blind reader finds its firings 91 % of the time.

The page of one finding, served at /finding/neurons-you-can-describe (view.py serves every tools/finding_<slug>.py)
and reached from its tile on /findings, which ICON draws.
The picture is the blind description test itself, on three of its 45 neurons: the reader sees the sentence written
for a neuron and 8 real snippets, picks the 4 where they expect the neuron to fire at the marked token, and reveals
the answer and their score next to the scores of the test. The dots around the sheet are the 45 tested neurons in
the order of their score. The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of
tools/architecture.py (.claude/skills/site-ui/SKILL.md).

    python3 tools/finding_neurons_you_can_describe.py    checks DATA against the two artifacts it was copied from
"""
import json

TITLE = "Neurons you can describe"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Can one sentence say what a neuron does?"

# Every number is copied from the two artifacts named here. None is typed from memory. The deployed site ships only
# tools/*.py, so the copy is a literal; run this file to compare it with the artifacts.
DATA = {
    "artifact": "studies/cleanneurons/results/describe/attr_top100-01/descriptions_test.json",
    "examples": "studies/cleanneurons/results/describe/attr_top100-01/page_examples.json",
    "run": "studies/cleanneurons/results/describe/attr_top100-01/run.json",
    "commit": "2dd4da7d5b66ae79c2841418085ea12656a26fcc",
    "job": "sameraslan-1114-154532-cdc8",
    "command": "python -m studies.cleanneurons.jobs.describe_neurons --commit 2dd4da7d5b66ae79c2841418085ea12656a26fcc --edit studies/cleanneurons/results/transplant/curve_attr-01/edit_attr_top100.json",
    # The protocol of studies/cleanneurons/analysis/describe_test.py: first10, then heldout10 and random10.
    "test": {"described_from": 10, "snippets": 20, "fire": 10},
    "chance": 0.5,
    "sets": {"selected": {"units": 30, "mean_accuracy": 0.9066666666666666, "ci95": [0.8600000000000001, 0.9466666666666667]},
             "reference": {"units": 15, "mean_accuracy": 0.7133333333333333, "ci95": [0.6000000000000001, 0.8133333333333334]}},
    # The 45 tested neurons, by accuracy and then key: key, set (s selected, r reference), accuracy. One dot each.
    "ring": [
        ["u01", "s", 1.0], ["u04", "s", 1.0], ["u06", "s", 1.0], ["u09", "s", 1.0], ["u20", "s", 1.0], ["u22", "s", 1.0], ["u24", "s", 1.0], ["u25", "s", 1.0], ["u29", "s", 1.0],
        ["u31", "s", 1.0], ["u33", "s", 1.0], ["u34", "s", 1.0], ["u37", "s", 1.0], ["u41", "s", 1.0], ["u44", "s", 1.0], ["u00", "s", 0.9], ["u02", "r", 0.9], ["u03", "s", 0.9],
        ["u05", "s", 0.9], ["u08", "s", 0.9], ["u12", "s", 0.9], ["u13", "s", 0.9], ["u14", "r", 0.9], ["u17", "r", 0.9], ["u18", "s", 0.9], ["u19", "r", 0.9], ["u32", "r", 0.9],
        ["u36", "s", 0.9], ["u40", "r", 0.9], ["u07", "s", 0.8], ["u10", "r", 0.8], ["u21", "r", 0.8], ["u26", "s", 0.8], ["u35", "s", 0.8], ["u11", "s", 0.7], ["u23", "r", 0.7],
        ["u27", "s", 0.7], ["u43", "r", 0.7], ["u15", "s", 0.6], ["u16", "r", 0.6], ["u28", "r", 0.6], ["u38", "s", 0.6], ["u39", "r", 0.5], ["u30", "r", 0.4], ["u42", "r", 0.2],
    ],
    # Three neurons to try, from page_examples.json: per snippet its id in the test, whether the neuron fires, the text
    # with the marked token between << and >>.
    "seed": 0,
    "units": [
        {"key": "u06", "set": "selected", "layer": 10, "neuron": 7275, "pole": "+", "blind_accuracy": 1.0,
         "description": "A hesitation word 'Hmm', 'Wait' or 'wait' starting a sentence right after a period or 'But', mostly just after the problem is restated in the opening reasoning.",
         "snippets": [
             [0, True, "… an expression x² - 4x + 4.<< Wait>> a second, that looks familiar. …"],
             [3, False, "… possibility that I misread the original problem<<?>> Let me check again. The …"],
             [4, True, "… 3i. Let me write that out properly.<< Wait>>, is the multiplication by …"],
             [5, False, "… an integer k where kⁿ = 2²⁴<<.>> So, essentially, we need to …"],
             [12, False, "… is f(-1) if g(x) = f(x +<< >>1), but in this case, …"],
             [14, True, "… \\( b \\) are positive real numbers.<< Hmm>>, let me think about …"],
             [16, False, "… is 2000 calories. So, the answer is<< >>2000. Answer: \\boxed{2000}<|endoftext|>"],
             [17, True, "… 1 make 2²⁴ a perfect nᵗʰ power.<< Hmm>>, so we need to …"],
         ]},
        {"key": "u23", "set": "reference", "layer": 10, "neuron": 5485, "pole": "+", "blind_accuracy": 0.7,
         "description": "The noun 'terms' (also 'parts', 'power', 'number') right after a modifier naming its kind, as in 't³ terms', 'common terms', 'real parts', 'highest power', 'mixed number'.",
         "snippets": [
             [0, True, "… 15.975. So, 15 and 39/40, since 39<</>>40 is 0.975. So, that's …"],
             [4, True, "… combine like terms. Start with the x^4<< term>>: 3x^4. x^3 term: -12x^3. …"],
             [10, True, "… +36i -15i². Combine like terms: The real<< parts>>: 48 -15i². Since i² …"],
             [15, False, "… since x = 0 and y > <<0>>, it's in the first …"],
             [16, False, "… since in math, fractions are preferred over<< repeating>> decimals. Let me check examples …"],
             [17, False, "… I can write each number as a<< decimal>> and perform the operations, then …"],
             [18, False, "… \\] Thus, the sum of the coefficients<< of>> \\( g(x) \\) is \\( …"],
             [19, True, "… need to break them down into prime<< factors>>. 3 is a prime …"],
         ]},
        {"key": "u42", "set": "reference", "layer": 9, "neuron": 2589, "pole": "-", "blind_accuracy": 0.2,
         "description": "A remainder or modulus token in modular arithmetic ('mod', '≡', the residue after '≡' or 'mod7 is'), or the repeating digits after a decimal point ('33.333') (weak)",
         "snippets": [
             [2, False, "… digit: 5 (after borrowing) - 6. Can<<'t>> do that, need to borrow …"],
             [3, True, "… so sqrt(45) is between 6 and 7.<< Specifically>>, 6.7^2 is 44.89, because …"],
             [7, True, "… θ since it's already in the correct<< quadrant>>. So the final answer …"],
             [8, True, "… be an isosceles triangle. But wait, how<< exactly>> do I calculate the area …"],
             [9, False, "… So that would be 7 units (<<1>> block + 6 girls) arrange …"],
             [12, False, "… then starting from day 3: 3, 6,<< >>9, 12, 15, 18, 21, …"],
             [14, False, "… of each prime factor: \\(2^2 \\times 3<< \\>>times 5\\). - Calculate \\(2^2 …"],
             [18, True, "… days. Therefore, 9*4=36. Alternatively, if she could<< start>> at day 1, but since …"],
         ]},
    ],
}

_S, _R, _T = DATA["sets"]["selected"], DATA["sets"]["reference"], DATA["test"]
_p = lambda v: f"{100 * v:.1f}"  # a share as a percentage with one decimal
LINE = f"Yes: from the sentence alone, a blind reader finds its firings {round(100 * _S['mean_accuracy'])} % of the time."

# Depth, opened by a click: key, name, one or two sentences, then at most three more. Full plain sentences, no bold lead-ins.
# Not from our run: 352,256 neurons is studies/cleanneurons/README.md (32 layers x 11,008); the Goodfire numbers are
# from goodfire.com/research/neurons-as-an-interpretable-basis (95 % detection against random text, Qwen3.6-35B-A3B); the
# small-model report is andriybatutin.substack.com/p/we-tried-to-confirm-neural-networks (19 October 2026).
PANELS = [
    ["how", "How we know",
     f"One reader wrote a sentence from {_T['described_from']} snippets where a neuron fires most. A second reader, given only that sentence, picked which "
     f"{_T['fire']} of {_T['snippets']} new snippets fire; the other {_T['snippets'] - _T['fire']} are random places in the same texts.",
     [f"We tested {_S['units'] + _R['units']} neurons of the 7B model allenai/Olmo-3-1025-7B, the dots in the picture. The {_S['units']} that matter most for its RL-trained "
      f"version (solid) scored {_p(_S['mean_accuracy'])} % (95 % interval {_p(_S['ci95'][0])} to {_p(_S['ci95'][1])}), {_R['units']} random neurons (hollow) scored "
      f"{_p(_R['mean_accuracy'])} % ({_p(_R['ci95'][0])} to {_p(_R['ci95'][1])}), and guessing scores {round(100 * DATA['chance'])} %.",
      "Both readers were Claude subagents. The second never saw which snippets fire or which neurons were random.",
      "The closest published result is Goodfire, \"Neurons as an Interpretable Basis\" (10 November 2026): 95 % detection against random text, on a 35B "
      "mixture-of-experts model. A self-published report on Qwen3-0.6B and 1.7B (Batutin) found that labels described only the peak activations."]],
    ["limits", "What it does not show",
     "The test uses only each neuron's strongest firings. A sentence can pass it while the neuron's weaker firings follow no describable rule.",
     ["The reader that wrote the sentences and the reader that was tested are the same kind of model, so a person might score lower.",
      f"We tested {_S['units'] + _R['units']} of the model's 352,256 neurons.",
      "It says nothing yet about changing the model's behaviour with these neurons."]],
    ["run", "How to reproduce it",
     "Run studies/cleanneurons/analysis/describe_test.py with prep on the output of the GPU job, let two readers write descriptions.json and predictions.json, then run it with score.",
     [f"The GPU job was {DATA['job']} at commit {DATA['commit'][:7]}: {DATA['command'].replace(DATA['commit'], DATA['commit'][:7])}.",
      f"The scores and all {_S['units'] + _R['units']} sentences are in {DATA['artifact']}.",
      f"The snippets on this page are in {DATA['examples']}: 8 of each neuron's {_T['snippets']}, drawn with seed {DATA['seed']}."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab seen from slightly above with five snippets as lines of words, one of them bright: the
# snippet where the neuron fires.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, pick = 2;
  const rows = [[[-.8, -.36], [-.24, .1], [.22, .62]], [[-.8, -.12], [0, .42]], [[-.8, -.46], [-.34, .24], [.36, .7]],
    [[-.8, -.2], [-.08, .3], [.42, .8]], [[-.8, -.5], [-.38, .06]]];  // each row: its words, from and to, in half widths
  let out = kit.slab(a, b, th);
  rows.forEach((words, i) => {
    const v = b * .68 * (2 * i / (rows.length - 1) - 1), lit = i === pick;
    for (const [from, to] of words)
      out += kit.line(kit.at(a * from, v, th / 2), kit.at(a * to, v, th / 2), lit ? 1.4 + .16 * Math.sin(t * .6) : .9, lit ? "lit" : "plain", lit ? 1 : .7);
  });
  return out;
}"""

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
/* The tokens and the light of tools/architecture.py: one lit glass body in a dark room, the same object as white
   porcelain with a cast shadow in light. The light comes from the upper left in both. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #8b97a1; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338; --on-blue: #fff;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18); --btn-drop: rgba(16, 24, 32, .42);
  --line: color-mix(in srgb, var(--ink) 12%, transparent);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #5f6c77; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1;
    --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7); --btn-drop: rgba(0, 0, 0, .6);
  }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper); overflow-x: clip;
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
button:disabled { color: inherit; cursor: default; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.page {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 26vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0; height: 100vh; min-height: 850px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 24px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture: the test sheet of one neuron, standing in the ring of the tested neurons */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 18px 40px 0 0; }
.object { --padx: 64px; --padb: 50px; position: relative; isolation: isolate; width: min(100%, 850px); padding: 0 var(--padx) var(--padb); }
.object::before, .object::after { content: ""; position: absolute; z-index: -2; inset: 0 var(--padx) var(--padb); border-radius: 20px; pointer-events: none; }
.object::before { opacity: var(--glow); box-shadow: 0 0 130px 8px color-mix(in srgb, var(--blue) 20%, transparent); }
.object::after { opacity: var(--shadow); box-shadow: 18px 36px 70px -14px color-mix(in srgb, var(--ink) 22%, transparent); }
.orbit { position: absolute; z-index: -1; inset: 0; width: 100%; height: 100%; overflow: visible; pointer-events: none; }
.ring { fill: none; stroke: var(--ink); }
.ring.back { stroke-width: .8; opacity: .3; }
.ring.front { stroke-width: 1.5; opacity: .62; }
.n .d { fill: var(--ink); }
.n.ref .d { fill: var(--paper); stroke: var(--ink); stroke-width: 1.4; }
.n .halo { fill: none; stroke: var(--faint); stroke-width: 1.2; }
.n.sel .d { fill: var(--blue); stroke: none; }
.n.sel .halo { stroke: var(--blue); }
.slab {
  position: relative; overflow: hidden; border-radius: 20px; padding: 26px 32px 12px;
  background: radial-gradient(130% 120% at 30% 16%, var(--glass-hi), var(--glass) 46%, var(--glass-lo));
}
.slab::before {  /* the rim: bright toward the light */
  content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1.5px; pointer-events: none;
  background: linear-gradient(140deg, var(--rim-a), var(--rim-b) 56%, var(--rim-c));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask-composite: exclude;
}
.spec { position: absolute; left: -6%; top: -16%; width: 62%; height: 52%; transform: rotate(-24deg); opacity: var(--spec); pointer-events: none;
  background: radial-gradient(closest-side, rgba(255, 255, 255, .13), rgba(255, 255, 255, 0)); }
.sentence { position: relative; margin: 0 0 14px; min-height: 3.96em; font-size: clamp(17px, 1.45vw, 22px); line-height: 1.32; font-weight: 430; font-stretch: 104%; letter-spacing: -.004em; }
.sentence::before { content: "\201C"; }
.sentence::after { content: "\201D"; }
.snips { position: relative; list-style: none; margin: 0; padding: 0; }
.snip { display: flex; align-items: baseline; gap: 12px; width: 100%; padding: 9px 2px; border-top: 1px solid var(--line); font-size: 15.5px; line-height: 1.4; transition: opacity .2s ease; }
.tick { flex: none; width: 12px; height: 12px; border-radius: 50%; border: 1.5px solid var(--faint); transform: translateY(1px); transition: background .15s ease, border-color .15s ease; }
.txt { color: var(--mute); white-space: pre-wrap; overflow-wrap: anywhere; min-width: 0; transition: opacity .3s ease; }
.txt mark { color: var(--ink); font-weight: 640; background: var(--line); border-bottom: 1.5px solid var(--ink); border-radius: 4px 4px 0 0; padding: 1px 1px 0; transition: background .3s ease, color .3s ease; }
.txt mark.gap { padding: 1px 4px 0; }
.snip:hover .tick { border-color: var(--ink); }
.snip[aria-pressed="true"] .tick { background: var(--blue); border-color: var(--blue); }
.snip[aria-pressed="true"] .txt { color: var(--ink); }
.snip.spare { opacity: .5; }
.snip.fires .txt { color: var(--ink); }
.snip.fires mark { background: var(--blue); color: var(--on-blue); border-color: var(--blue); }
.snip.fires .tick { border-color: var(--ink); }
.snip.quiet .txt { opacity: .42; }
.snip.right .tick { background: var(--blue); border-color: var(--blue); }
.snip.wrong .tick { background: var(--red); border-color: var(--red); }

/* The one control under it, and what the reveal adds */
.acts { display: flex; align-items: center; gap: 10px; margin-top: 4px; }
.turn { width: 40px; height: 40px; border-radius: 50%; text-align: center; font-size: 24px; line-height: 1; color: var(--mute); transition: color .15s ease; }
.turn:hover { color: var(--ink); }
.act { min-width: 196px; padding: 12px 22px; border-radius: 999px; text-align: center; font-weight: 620; font-size: 15px; font-stretch: 106%; letter-spacing: .004em; border: 1px solid transparent; transition: transform .18s ease, box-shadow .18s ease; }
.act.wait { color: var(--mute); border-color: var(--rule); }
.act.go { background: var(--btn); color: var(--btn-ink); box-shadow: inset 0 1px 0 var(--btn-edge), 0 14px 28px -14px var(--btn-drop); }
.act.go:hover { transform: translateY(-1px); box-shadow: inset 0 1px 0 var(--btn-edge), 0 0 0 1.5px var(--blue), 0 18px 32px -12px var(--btn-drop); }
.act.next { border-color: var(--faint); }
.act.next:hover { border-color: var(--blue); background: var(--blue); color: var(--on-blue); }
.res { width: min(100%, 440px); min-height: 100px; margin-top: 14px; }
.row { display: grid; grid-template-columns: 138px minmax(0, 1fr) 48px; align-items: center; gap: 12px; height: 25px; font-size: 13.5px; color: var(--mute); }
.row .k { font-weight: 560; }
.row .v { text-align: right; font-weight: 600; color: var(--ink); }
.row .track { height: 1px; background: var(--rule); }
.row .track i { display: block; position: relative; top: -.5px; height: 2px; background: var(--mute); transform-origin: left center; animation: grow .7s cubic-bezier(.3, 0, .2, 1) both; }
.row .track i::after { content: ""; position: absolute; right: -4px; top: -3px; width: 8px; height: 8px; border-radius: 50%; background: inherit; }
.row.you { color: var(--blue); }
.row.you .k { font-weight: 700; }
.row.you .v { color: var(--blue); font-weight: 700; }
.row.you .track i { background: var(--blue); }
.note { margin: 6px 0 0; min-height: 3em; max-width: 56ch; color: var(--mute); font-size: 13.5px; text-align: center; }
@keyframes grow { from { transform: scaleX(0); } }
@keyframes rise { from { opacity: 0; transform: translateY(10px); } }
@keyframes fade { from { opacity: 0; } }
.enter .slab { animation: rise .8s cubic-bezier(.3, 0, .2, 1) both; }
.enter .orbit { animation: fade 1.4s .35s both; }

/* The words */
.side { min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none; padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule); }
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(23px, 1.95vw, 35px); line-height: 1.17; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 19ch; }
.say b { font-weight: 640; }
.pane { margin-top: clamp(24px, 4.4vh, 48px); }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(16px, 1.2vw, 19px); line-height: 1.38; font-weight: 380; max-width: 34ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 42ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
@media (max-width: 900px) {
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 4px 13px; flex-wrap: wrap; padding-bottom: 12px; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 18px; max-width: none; }
  .say { order: 2; margin-top: 8px; max-width: none; }
  .stage { order: 3; padding: 0; margin-top: 22px; }
  .pane { order: 4; margin-top: 10px; }
  .object { --padx: 0px; --padb: 36px; }
  .slab { padding: 18px 16px 8px; }
  .sentence { min-height: 0; }
  .snip { font-size: 14px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter .slab, .enter .orbit, .row .track i { animation: none; }
  .snip, .tick, .txt, .txt mark, .act { transition: none; }
}
</style>
</head>
<body class="enter">
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <div class="stage" id="stage">
    <div class="object" id="object" role="group" aria-label="The blind test on one neuron">
      <svg class="orbit" id="orbit" aria-hidden="true"></svg>
      <div class="slab" id="slab">
        <i class="spec"></i>
        <p class="sentence" id="sentence"></p>
        <ol class="snips" id="snips"></ol>
      </div>
    </div>
    <div class="acts">
      <button class="turn" data-turn="-1" aria-label="Previous neuron">‹</button>
      <button class="act wait" id="act" aria-live="polite"></button>
      <button class="turn" data-turn="1" aria-label="Next neuron">›</button>
    </div>
    <div class="res" id="res" aria-live="polite"></div>
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
const S = { unit: 0, picks: new Set(), shown: false, open: null };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const pct = v => Math.round(v * 100) + " %";
const unit = () => D.units[S.unit];
const need = () => unit().snippets.filter(s => s[1]).length;  // how many of the snippets shown fire

/* The picture: the sentence written for one neuron and 8 real snippets of its test, each with one marked token.
   The reader picks the snippets where they expect the neuron to fire at the marked token, then reveals the key. */
function sheet() {
  const u = unit();
  $("sentence").textContent = u.description;
  $("snips").innerHTML = u.snippets.map(([id, fires, text], i) => {
    const a = text.indexOf("<<"), b = text.indexOf(">>", a), tok = text.slice(a + 2, b);
    const lead = tok.trim() ? tok.match(/^\s*/)[0] : "";  // a token's leading space stays outside the highlight
    return `<li><button class="snip" data-snip="${i}" aria-pressed="false"><i class="tick"></i>` +
      `<span class="txt">${esc(text.slice(0, a) + lead)}<mark${tok.trim() ? "" : ' class="gap"'}>${esc(tok.slice(lead.length))}</mark>${esc(text.slice(b + 2))}</span><span class="sr"></span></button></li>`;
  }).join("");
  mark();
}
function mark() {
  const u = unit(), n = need(), left = n - S.picks.size;
  document.querySelectorAll(".snip").forEach((b, i) => {
    const on = S.picks.has(i), f = u.snippets[i][1];
    b.setAttribute("aria-pressed", on);
    b.className = "snip" + (S.shown ? (f ? " fires" : " quiet") + (on ? (f ? " right" : " wrong") : "") : !left && !on ? " spare" : "");
    b.disabled = S.shown;
    b.querySelector(".sr").textContent = S.shown ? (f ? " (fires)" : " (does not fire)") : "";
  });
  const act = $("act");
  act.textContent = S.shown ? "Next neuron" : left ? (S.picks.size ? `Pick ${left} more` : `Pick ${n} that fire`) : "Reveal";
  act.className = "act " + (S.shown ? "next" : left ? "wait" : "go");
  act.disabled = !S.shown && left > 0;
  const hits = [...S.picks].filter(i => u.snippets[i][1]).length;  // the share of the snippets shown that are classified right is hits / n
  const rows = [["You", hits / n, "you"], ["Blind reader", D.sets.selected.mean_accuracy, ""], ["On random neurons", D.sets.reference.mean_accuracy, ""], ["Chance", D.chance, ""]];
  $("res").innerHTML = !S.shown ? "" : rows.map(([k, v, cls]) =>
    `<div class="row ${cls}"><span class="k">${k}</span><span class="track"><i style="width:${(v * 100).toFixed(1)}%"></i></span><span class="v">${pct(v)}</span></div>`).join("");
  $("note").textContent = !S.shown ? "" : `On all ${D.test.snippets} test snippets of this neuron, the blind reader scored ${pct(u.blind_accuracy)}. It is ` +
    (u.set === "selected" ? `one of the ${D.sets.selected.units} neurons that matter most.` : "a random neuron.");
}
function turn(d) {
  S.unit = (S.unit + d + D.units.length) % D.units.length;
  S.picks.clear(); S.shown = false;
  sheet(); aim();
}

/* The ring: the tested neurons, one dot each, in the order of their score, on a circle on the floor around the
   sheet. Solid is a neuron that matters, hollow is a random one; the three that can be tried have a halo and the one
   on the sheet is blue and nearest. What is near is larger and brighter, and what passes behind the sheet is hidden.
   The view sways by a few degrees and leans toward the mouse. With reduced motion it stays at rest. */
const RAD = Math.PI / 180, N = D.ring.length;
const O = { g: null, dots: [], turn: 0, goal: 0, px: 0, py: 0, tx: 0, ty: 0, t: 0 };
const slot = () => D.ring.findIndex(r => r[0] === unit().key);
function orbit() {
  const box = $("object"), slab = $("slab"), w = box.clientWidth, small = w < 600;
  O.g = { cx: w / 2, cy: slab.offsetTop + slab.offsetHeight - 3, rx: w / 2 - (small ? 12 : 8), ry: small ? 25 : 38 };
  const tried = new Set(D.units.map(u => u.key));
  $("orbit").setAttribute("viewBox", `0 0 ${w} ${box.clientHeight}`);
  $("orbit").innerHTML = `<path class="ring back" id="ring-b"/><path class="ring front" id="ring-f"/>` + D.ring.map(([k, set]) =>
    `<g class="n${set === "s" ? "" : " ref"}">${tried.has(k) ? '<circle class="halo" r="9.5"/>' : ""}<circle class="d" r="${tried.has(k) ? 5 : 3.2}"/></g>`).join("");
  O.dots = [...$("orbit").querySelectorAll(".n")];
  lit(); place();
}
function lit() { const s = slot(); O.dots.forEach((el, i) => el.classList.toggle("sel", i === s)); }
function aim() {
  O.goal = O.turn + ((slot() - O.turn) % N + N * 1.5) % N - N / 2;  // the shorter way round
  lit();
  if (still.matches) { O.turn = O.goal; place(); }
}
function place() {
  const g = O.g;
  if (!g) return;
  const move = !still.matches, yaw = move ? 3 * Math.sin(O.t * .13) + 4 * O.px : 0, ry = g.ry * (move ? 1 + .1 * Math.sin(O.t * .09) - .14 * O.py : 1);
  const l = (g.cx - g.rx).toFixed(1), r = (g.cx + g.rx).toFixed(1), arc = `A${g.rx.toFixed(1)} ${ry.toFixed(1)} 0 0 1 `;
  $("ring-b").setAttribute("d", `M${l} ${g.cy}${arc}${r} ${g.cy}`);
  $("ring-f").setAttribute("d", `M${r} ${g.cy}${arc}${l} ${g.cy}`);
  O.dots.forEach((el, i) => {
    const a = (90 + (i - O.turn) * 360 / N + yaw) * RAD, near = (1 + Math.sin(a)) / 2, o = (.25 + .75 * near).toFixed(1);
    el.setAttribute("transform", `translate(${(g.cx + g.rx * Math.cos(a)).toFixed(1)} ${(g.cy + ry * Math.sin(a)).toFixed(1)}) scale(${(.55 + .6 * near).toFixed(2)})`);
    if (el.dataset.o !== o) el.setAttribute("opacity", el.dataset.o = o);
  });
}
function spin(now) {
  O.t = now / 1000;
  O.px += (O.tx - O.px) * .06; O.py += (O.ty - O.py) * .06; O.turn += (O.goal - O.turn) * .07;
  place();
  requestAnimationFrame(spin);
}

function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${p[1]}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(f => `<li>${esc(f)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${p[1]}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
function fromHash() { const h = location.hash.slice(1); S.open = C.panels.some(p => p[0] === h) ? h : null; pane(); }
document.addEventListener("click", e => {
  const s = e.target.closest("[data-snip]"), o = e.target.closest("[data-open]"), t = e.target.closest("[data-turn]");
  if (s && !S.shown) {
    const i = Number(s.dataset.snip);
    if (S.picks.has(i)) S.picks.delete(i); else if (S.picks.size < need()) S.picks.add(i);
    mark();
  }
  if (t) turn(Number(t.dataset.turn));
  if (e.target.closest("#act")) { if (S.shown) turn(1); else { S.shown = true; mark(); } }
  if (o) { history.pushState(null, "", o.dataset.open ? "#" + o.dataset.open : location.pathname); fromHash(); }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) { history.pushState(null, "", location.pathname); fromHash(); }
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") turn(e.key === "ArrowRight" ? 1 : -1);
});
addEventListener("hashchange", fromHash);
const stage = $("stage");  // the view leans a few degrees toward a mouse, and settles back
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  O.tx = 2 * (e.clientX - b.left) / b.width - 1;
  O.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { O.tx = O.ty = 0; });
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
sheet();
O.turn = O.goal = slot();
orbit();
new ResizeObserver(orbit).observe($("object"));  // the ring follows the size of the sheet
fromHash();
if (!still.matches) requestAnimationFrame(spin);
setTimeout(() => document.body.classList.remove("enter"), 2000);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}).replace("</", "<\\/"))


if __name__ == "__main__":  # DATA against its artifacts; run from the repository root
    test, page = json.load(open(DATA["artifact"])), json.load(open(DATA["examples"]))
    run = json.load(open(DATA["run"]))
    assert (DATA["chance"], DATA["sets"]) == (test["chance"], test["sets"]), "set means or intervals differ"
    assert DATA["ring"] == [[u["key"], u["set"][0], u["accuracy"]] for u in sorted(test["units"], key=lambda u: (-u["accuracy"], u["key"]))], "unit scores differ"
    assert (DATA["commit"], DATA["job"], DATA["command"]) == (run["commit"], run["job_id"], run["command"]), "run differs"
    assert DATA["seed"] == page["seed"] and len(DATA["units"]) == len(page["units"])
    for mine, u in zip(DATA["units"], page["units"]):
        scored = next(x for x in test["units"] if x["key"] == u["key"])
        for f in ("key", "set", "layer", "neuron", "pole", "description"):
            assert mine[f] == u[f] == scored[f], (u["key"], f)
        assert mine["blind_accuracy"] == u["blind_accuracy"] == scored["accuracy"], u["key"]
        assert mine["snippets"] == [[s["id"], s["fires"], s["text"]] for s in u["snippets"]], u["key"]
    print("DATA matches", DATA["artifact"], "and", DATA["examples"])
