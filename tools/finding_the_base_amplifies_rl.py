"""When only one layer gets RL's edit, the later, unedited layers of the base enlarge the activation change from RL's
paired directions 46.6 times by layer 24 (edit at layer 0), against 8.2 times when the same edit writes in random output
directions.

The page of one finding, served at /finding/the-base-amplifies-rl (view.py serves every tools/finding_<slug>.py) and reached
from its tile on /findings, which ICON draws. It is the fourth page about one weight edit, after /finding/the-finish-dial,
/finding/rl-directions-move-activations (the same edits in the activations at layer 24) and /finding/two-jobs-in-the-edit
(its parts on the answers): RL's 8 largest directions per weight matrix at size 1.5, here restricted to the two matrices of
one layer that write into the residual stream (attention output o and feed-forward down), at layer 0 or layer 8. Every
later layer is the base. Board items result-8b1904 (this run), result-5d12ff (all layers' writing matrices) and
result-bfe93c (the layer bands add up); result-e91adc and result-0d54f3 for the unpaired edits.

The picture is one lit plate. x is the layer (0 to 31), with a row of 32 small tiles under the axis, the edited one lit;
y is the RMS shift of the residual stream after each layer (log scale), measured on 48 stored Base + cue answers. Three
lines leave the edited layer: RL's paired directions, RL's input directions with random outputs, random directions. They
draw themselves layer by layer while the large number (the paired line's growth from the edited layer to layer 24)
counts with them. The one control is the edited layer (0 or 8): the old lines fade, the lit tile slides, the lines draw
again from the new start. A click on a point opens that edit at that layer in the side column (its shift, its growth so
far, what the edit was, the other two edits there, the base's own RMS); a click on a tile or anywhere in a layer's column
opens that layer with all three.
Address: /finding/the-base-amplifies-rl#[l8/][<panel key>|paired-<layer>|rin-<layer>|rand-<layer>|layer-<layer>]; the
default (layer 0 edited) is left out. The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of
tools/architecture.py (.claude/skills/site-ui/SKILL.md).

DATA is copied from the artifacts (the deployed site ships only tools/*.py, so the copy is a literal). The run's files are
on the branch sharedsub only (main was frozen), at commit DATA["commit"]. Run this file from the repository root to compare
every number with those files; each group of files that is not present is reported as skipped:

    uv run python tools/finding_the_base_amplifies_rl.py
"""
import json
import os
import sys

X = "studies/rlneurons/results/xshift/"
RUN = X + "run-04/"

# Every number is copied from the artifacts named here. None is typed from memory.
DATA = {
    "metrics": RUN + "metrics.json", "readout": RUN + "readout.json", "run": RUN + "run.json",
    "spec": "studies/rlneurons/specs/SPEC_xshift.md, amendment 4", "spec_file": "studies/rlneurons/specs/SPEC_xshift.md",
    "readme": "studies/rlneurons/README.md, sections 'xshift run-03', 'xshift run-04' and 'xshift additivity'",
    "branch": "sharedsub", "commit": "e35a7d1c20f2cafc488106cbde0bb19a2fb5cb00",  # the commit that added run-04
    "job": "abaybektursun-1115-165351-05ce", "job_commit": "d08038bea5a7f93494586d63a7de7fc721544ba8",  # run.json; spec too
    "wall_s": 310.5, "base_model": "allenai/Olmo-3-1025-7B", "answers_job": "abaybektursun-1114-151534-e72c",
    "inputs": 48, "cap_hit_inputs": 24, "positions": 6144, "answer_tokens": 2048, "step": 16,  # metrics
    # metrics base.rms: the RMS norm of the base's residual stream after each layer 0 to 31 (5 significant digits)
    "base_rms": [3.6263, 3.7536, 4.0183, 4.2647, 4.659, 5.3644, 6.1613, 7.058, 7.7641, 8.7896, 9.8996, 10.832, 11.775,
                 13.176, 15.159, 16.986, 19.24, 21.767, 24.591, 27.28, 29.892, 32.185, 35.451, 38.456, 41.218, 44.002,
                 46.695, 49.824, 52.861, 57.822, 67.151, 84.117],
    # metrics edits.<key>: n_edited, add_rel (7 decimals) and shift.all.rms from the edited layer to layer 31 (5 significant
    # digits): the RMS over 6,144 positions of the edited-minus-base residual stream after each layer
    "edits": {
        "0": {
            "paired": {"key": "top8x1.5_write_L0_math31", "n_edited": 2, "add_rel": 0.0013225, "rms": [
                0.018648, 0.026695, 0.031217, 0.03497, 0.038159, 0.04133, 0.045507, 0.048219, 0.051823, 0.057599, 0.062113,
                0.07303, 0.084983, 0.12983, 0.20165, 0.33788, 0.44075, 0.50708, 0.54875, 0.65659, 0.69199, 0.73855, 0.78682,
                0.82705, 0.86988, 0.90512, 0.94234, 0.98535, 0.98443, 1.0024, 1.0484, 1.0586]},
            "rin": {"key": "rinx1.5_write_L0_math31", "n_edited": 2, "add_rel": 0.0013225, "rms": [
                0.014313, 0.014216, 0.014634, 0.014401, 0.0142, 0.01436, 0.014735, 0.014605, 0.014597, 0.014885, 0.015358,
                0.015877, 0.016943, 0.01921, 0.030018, 0.043324, 0.059749, 0.072716, 0.078285, 0.092213, 0.095706, 0.1017,
                0.1059, 0.11123, 0.11763, 0.12218, 0.12503, 0.12834, 0.12484, 0.1283, 0.13214, 0.14053]},
            "rand": {"key": "rand8x1.5_write_L0_math31", "n_edited": 2, "add_rel": 0.0013225, "rms": [
                0.0012207, 0.001177, 0.0011865, 0.00116, 0.0011269, 0.0011168, 0.0011338, 0.0011418, 0.0011787, 0.0012573,
                0.00128, 0.0013317, 0.0013383, 0.0015082, 0.0045176, 0.0076756, 0.011202, 0.014329, 0.015204, 0.019016,
                0.019299, 0.020828, 0.021413, 0.021868, 0.022194, 0.022449, 0.022608, 0.022943, 0.021035, 0.02109, 0.020686,
                0.021014]},
        },
        "8": {
            "paired": {"key": "top8x1.5_write_L8_math31", "n_edited": 2, "add_rel": 0.0010139, "rms": [
                0.043309, 0.056029, 0.067658, 0.073179, 0.079798, 0.095596, 0.12435, 0.16243, 0.20362, 0.23612, 0.26071,
                0.31739, 0.33216, 0.35598, 0.38091, 0.40539, 0.44307, 0.46772, 0.48963, 0.51728, 0.53212, 0.55172, 0.58655,
                0.61427]},
            "rin": {"key": "rinx1.5_write_L8_math31", "n_edited": 2, "add_rel": 0.0010139, "rms": [
                0.033745, 0.032882, 0.033479, 0.032744, 0.032837, 0.034527, 0.043178, 0.048868, 0.057152, 0.072597, 0.076921,
                0.090197, 0.093882, 0.098888, 0.10269, 0.10787, 0.1127, 0.11644, 0.12005, 0.12499, 0.12642, 0.13363, 0.14056,
                0.14896]},
            "rand": {"key": "rand8x1.5_write_L8_math31", "n_edited": 2, "add_rel": 0.0010139, "rms": [
                0.0036284, 0.0035078, 0.0034696, 0.0034141, 0.0034576, 0.0035932, 0.0042196, 0.0049065, 0.0052429, 0.0055895,
                0.0058879, 0.0065496, 0.0068606, 0.0072198, 0.0076131, 0.0080444, 0.0084461, 0.0087949, 0.0091565, 0.0095625,
                0.009809, 0.010234, 0.010844, 0.011753]},
        },
    },
    # readout edits.<key>.growth_to_24 (3 decimals): RMS shift at layer 24 over that at the edited layer
    "growth_to_24": {"0": {"paired": 46.647, "rin": 8.218, "rand": 18.182}, "8": {"paired": 10.231, "rin": 3.34, "rand": 2.328}},
    "predicted": 3, "refuted_below": 1.5,  # spec amendment 4, T1: the paired growth at least 3 times the input-only growth
    # Related runs (same 48 answers, same settings). run-03 readout edits.<key>.rms["24"]: the four 1.5 edits restricted to
    # the writing matrices (o, down) of all 32 layers, 64 matrices
    "run03": {"path": X + "run-03/readout.json", "job": "abaybektursun-1115-164458-836e",
              "paired": 3.8043, "rin": 0.57799, "perm": 1.164, "rand": 0.080341},
    # additivity-01 readout layers["31"]: the norm of the mean shift of the whole 1.5 edit (all layers, all matrices) and the
    # sum of the shifts of the same edit restricted to layers 0-10, 11-21 and 22-31; ratio and cosine
    "additivity": {"path": X + "additivity-01/readout.json", "full": 10.009, "sum": 8.2921, "ratio": 1.207, "cos": 0.99489},
    # Background, the same edit on the answers: Base + cue and RL's 8 directions at 1.5 on the 328 harder problems, T 1.0,
    # one answer each (studies/rlneurons/results/xreward/edits/readout.json cells.<cell>.right_v3, on main); the three edits
    # with the pairs broken (xreward/edits/<cell>-01/metrics.json counts.correct_v3, branch sharedsub)
    "n": 328, "base_cue_right": 164, "rl8_right": 203,
    "broken_right": {"rinx1.5_math31": 158, "routx1.5_math31": 163, "permx1.5_math31": 160},
}

_E, _B = DATA["edits"], DATA["base_rms"]
ARMS = ["paired", "rin", "rand"]
_v = lambda L, arm, layer: _E[str(L)][arm]["rms"][layer - L]                      # RMS shift after a layer
GROWTH = {L: {a: _v(L, a, 24) / _v(L, a, L) for a in ARMS} for L in (0, 8)}        # to layer 24: 46.6, 8.2, 18.2; 10.2, 3.3, 2.3
OVER = {L: GROWTH[L]["paired"] / GROWTH[L]["rin"] for L in (0, 8)}                 # paired over input-only: 5.7, 3.1
HEADLINE = round(GROWTH[0]["paired"], 1)                                            # 46.6, the large number of the first view
_R3, _AD = DATA["run03"], DATA["additivity"]
_br = sorted(DATA["broken_right"].values())
_m = lambda x: str(x).replace("-", "−")  # the minus sign of the site

TITLE = "The base enlarges what RL writes"  # the name on its tile on /findings and in the browser tab
PROBLEM = "When one early layer gets RL's edit, do later layers enlarge it?"
LINE = (f"With only layer 0 edited, later unedited layers enlarge the activation change from RL's paired directions "
        f"{HEADLINE} times by layer 24; with random outputs, {GROWTH[0]['rin']:.1f} times.")

NAMES = {"paired": "RL's paired directions", "rin": "RL's inputs, random outputs", "rand": "Random directions"}
SHORT = {"paired": "RL's paired directions", "rin": "RL's inputs only", "rand": "Random directions"}  # on a phone


def _what(L):
    pct = f"{100 * _E[str(L)]['paired']['add_rel']:.3f} %"
    two = f"the two matrices of layer {L} that write into the running vector"
    return {
        "paired": f"RL's 8 largest directions in {two}, each input direction with its own output direction, at size 1.5: "
                  f"{pct} of their weight norm. Every later layer is the base.",
        "rin": f"RL's 8 input directions and their strengths in {two}, each joined to a random output direction: the same "
               "weight norm, written in another direction.",
        "rand": f"8 random directions in {two}, at the same weight norm.",
    }


# The readout beside the picture, one per edited layer: the large number, two lines under it, the baseline beside it, then
# the lines of the state. Computed from DATA.
def _read(L):
    p, r, d = (_E[str(L)][a]["rms"] for a in ARMS)
    return {"big": round(GROWTH[L]["paired"], 1),
            "u": [f"growth of the shift from layer {L} to 24", "for RL's paired directions"],
            "base": f"{GROWTH[L]['rin']:.1f}× with random outputs",
            "lines": [f"Similar start: {_v(L, 'paired', L):.3g} and {_v(L, 'rin', L):.3g} RMS",
                      f"{GROWTH[L]['paired']:.1f} ÷ {GROWTH[L]['rin']:.1f} = {OVER[L]:.1f}×; predicted ≥ {DATA['predicted']}×",
                      f"At layer 24: {_v(L, 'paired', 24):.3f} against {_v(L, 'rin', 24):.3f} RMS",
                      f"Random: {d[0]:.2g} → {_v(L, 'rand', 24):.2g} ({GROWTH[L]['rand']:.1f}×)",
                      f"{DATA['inputs']} Base + cue answers, no sampling"]}


READ = {"0": _read(0), "8": _read(8)}
HINT = {
    "0": "Only layer 0 is edited. The paired shift grows from the very next layer; the two shifts with random outputs stay "
         "flat until about layer 12.",
    "8": f"Only layer 8 is edited. The paired shift again grows at once: {GROWTH[8]['paired']:.1f} times by layer 24, against "
         f"{GROWTH[8]['rin']:.1f} with random outputs.",
}

# Not from our runs: the closest published result, fetched with tools/exa.py (arXiv 2606.15161, "Beyond Layer Importance in
# Layer-wise Sparsity", sections 3.2 to 3.4): Gaussian perturbations injected at one layer of LLaMA-2-7B; under small
# perturbations "all layers exhibit accumulation: relative drift grows monotonically with depth regardless of injection
# point", while pruning-sized ones are absorbed by middle and late layers. They probe random directions only.
_FIN, _ACT, _TWO = "/finding/the-finish-dial", "/finding/rl-directions-move-activations", "/finding/two-jobs-in-the-edit"
_g = lambda L, a: f"{GROWTH[L][a]:.1f}"
_s = lambda L, a, layer: f"{_v(L, a, layer):.3g}"
PANELS = [
    ["new", "What is new",
     "A small change at one layer is known to grow through the later layers: arXiv 2606.15161 (sections 3.3 and 3.4) injects "
     "random noise into LLaMA-2-7B and finds small perturbations grow with depth. New here: at the same starting size, what "
     "RL's paired directions write grows several times more than a write in a random direction.",
     [f"Layer 0 edited: RL's paired directions move the activations by {_s(0, 'paired', 0)} RMS there and "
      f"{_v(0, 'paired', 24):.3f} at layer 24 ({_g(0, 'paired')} times); RL's inputs with random outputs from "
      f"{_s(0, 'rin', 0)} to {_s(0, 'rin', 24)} ({_g(0, 'rin')} times).",
      f"Layer 8 edited: {_s(8, 'paired', 8)} to {_s(8, 'paired', 24)} ({_g(8, 'paired')} times) against {_s(8, 'rin', 8)} to "
      f"{_s(8, 'rin', 24)} ({_g(8, 'rin')} times).",
      f"The paired shift grows in the very next layer ({_s(0, 'paired', 0)} to {_s(0, 'paired', 1)}; {_s(8, 'paired', 8)} to "
      f"{_s(8, 'paired', 9)}); the shifts with random outputs stay flat until about layer 12."],
     [_ACT, "RL directions move activations: the whole edit at layer 24 ›"],
     [_TWO + "#pairs", "Two jobs in one edit: the broken pairs on the answers ›"]],
    ["why", "Why it matters",
     "RL's change is a tiny part of each weight matrix. This shows one way it becomes large in the activations: the base's own "
     "later layers enlarge what it writes, along RL's output directions and much less along random ones.",
     [f"The same holds with all 32 layers' writing matrices edited: at layer 24 the paired directions move the activations by "
      f"{_R3['paired']:.3f} RMS, RL's inputs with random outputs by {_R3['rin']:.3f} ({_R3['paired'] / _R3['rin']:.1f} times "
      f"less), random directions by {_R3['rand']:.3f} ({_R3['paired'] / _R3['rand']:.0f} times less).",
      f"The edited layers barely enlarge each other: the shifts of three layer bands (0 to 10, 11 to 21, 22 to 31) nearly add "
      f"up to the whole edit's shift, {_AD['ratio']:.2f} times their sum at layer 31 (cosine {_AD['cos']:.3f}). The growth "
      "comes from the base layers after each write.",
      "Still open: why the base enlarges these directions. A test of how the next layers' reading matrices respond to them is "
      "running."]],
    ["how", "How we know",
     f"We edited only the two matrices of one layer that write into the running vector (attention output and "
     f"feed-forward down projection) and ran {DATA['inputs']} stored "
     f"Base + cue answers to the {DATA['n']} harder problems through the edited base, without sampling, comparing every "
     "layer with the unedited base.",
     [f"Three edits of the same weight norm at size 1.5: RL's paired directions, RL's input directions with random outputs, "
      f"random directions. The prediction, fixed before the run: paired growth at least {DATA['predicted']} times the "
      f"random-output growth at both layers. It held: {OVER[0]:.1f} and {OVER[8]:.1f} times.",
      f"Shift: edited minus base activations after each layer, at every {DATA['step']}th of the first "
      f"{DATA['answer_tokens']:,} answer tokens ({DATA['positions']:,} positions); its size is the root-mean-square of its "
      "length over positions.",
      f"The running vector itself grows {_B[24] / _B[0]:.1f} times from layer 0 to 24 (RMS {_B[0]:.2f} to {_B[24]:.1f}). "
      f"RL's paired write grows faster than it ({_g(0, 'paired')} times); the write with random outputs slower "
      f"({_g(0, 'rin')}).",
      "Self-tests on the real model passed first: a zero edit shifts nothing, the weights are restored exactly, the added "
      "change equals its target, and a planted direction is found with cosine 1.0000."]],
    ["limits", "What it does not show",
     "That the growth makes answers right. No scored model uses these one-layer edits: this shows how the shift grows, not "
     "that it causes right answers.",
     [f"One run on {DATA['inputs']} stored answers, in the activations only, with the base in 32-bit floating point.",
      f"Random directions edited at layer 0 grow {_g(0, 'rand')} times, more than the write with random outputs, but from a "
      f"start {_v(0, 'rin', 0) / _v(0, 'rand', 0):.0f} times smaller ({_s(0, 'rand', 0)} RMS): that growth rests on shifts "
      f"of 0.001 to 0.02. Edited at layer 8 they grow {_g(8, 'rand')} times.",
      "Why the base enlarges RL's directions is not known yet; a test of the next layers' reading matrices is running.",
      "Two edited layers (0 and 8) and one size (1.5); other layers are untested."]],
    ["run", "How to reproduce it",
     f"One GPU job computes every number: python -m studies.rlneurons.jobs.xshift --commit {DATA['job_commit'][:7]} with the "
     "six arms of run-04 (in run.json), on the branch sharedsub.",
     [f"Job {DATA['job']}, one H100, {DATA['wall_s'] / 60:.0f} minutes; the plan, written before the run: {DATA['spec']} "
      f"(commit {DATA['job_commit'][:7]}).",
      f"Files: {DATA['readout']}, {DATA['metrics']} (every layer) and {DATA['run']}, branch {DATA['branch']}, commit "
      f"{DATA['commit'][:7]}; {DATA['readme']}.",
      "uv run python tools/finding_the_base_amplifies_rl.py checks every number on this page against those files."]],
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
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table with
   a cast shadow in place of the glow. The light comes from the upper left in both. RL's paired directions are lit (blue). */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --base-tone: #6b7882; --grid: rgba(16, 24, 32, .08);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --base-tone: #b7c2ca; --grid: rgba(255, 255, 255, .06);
  }
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
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 27vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0; height: 100vh; min-height: 620px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture: one plate, the layers left to right, three measured lines, the readout beside them, the control under it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
.cap0 { margin: 0 0 4px 2.4%; font-size: 13px; line-height: 1.4; color: var(--mute); max-width: 84ch; }
svg { width: 100%; max-height: calc(100vh - 250px); display: block; overflow: visible; touch-action: pan-y; cursor: default; user-select: none; -webkit-user-select: none; }
svg:focus:not(:focus-visible) { outline: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.frame { fill: none; stroke: var(--faint); stroke-width: 1; opacity: .55; }
.grid { fill: none; stroke: var(--grid); stroke-width: 1; }
.tick { fill: var(--faint) !important; font-weight: 520; }
.tick.on { fill: var(--blue) !important; font-weight: 680; }
.title { fill: var(--mute) !important; font-weight: 600; }
.g24 { fill: none; stroke: var(--mute); stroke-width: 1; stroke-dasharray: 3 5; opacity: .6; }
.g24t { fill: var(--mute) !important; font-weight: 600; }
.blk { fill: var(--grid); stroke: var(--faint); stroke-width: .8; opacity: .55; }
.blkon { fill: var(--blue); }
.blkh { fill: var(--blue); opacity: calc(var(--bloom) * .18); filter: url(#soft2); }
.edt { fill: var(--blue) !important; font-weight: 680; }
.ln { fill: none; stroke-linecap: round; stroke-linejoin: round; }
.ln.paired { stroke: var(--blue); stroke-width: 2.6; }
.ln.glow { stroke: var(--blue); stroke-width: 10; opacity: calc(var(--bloom) * .13); }
.ln.rin { stroke: var(--base-tone); stroke-width: 1.9; }
.ln.rand { stroke: var(--base-tone); stroke-width: 1.5; stroke-dasharray: 5 4; opacity: .85; }
.pt { stroke: none; }
.pt.paired { fill: var(--blue); }
.pt.rin { fill: var(--base-tone); }
.pt.rand { fill: var(--sheet); stroke: var(--base-tone); stroke-width: 1.2; }
.pt0 { stroke-width: 2; }
.pt0.paired { fill: var(--blue); stroke: var(--sheet); }
.pt0.rin { fill: var(--base-tone); stroke: var(--sheet); }
.pt0.rand { fill: var(--sheet); stroke: var(--base-tone); }
.tip { fill: var(--blue); opacity: calc(var(--bloom) * .3); }
.pulse { fill: var(--blue); opacity: 0; }
.ll { font-weight: 640; }
.ll.paired { fill: var(--blue) !important; }
.ll.rin, .ll.rand { fill: var(--mute) !important; }
.selg { fill: none; stroke: var(--blue); stroke-width: 1; stroke-dasharray: 2 4; opacity: .7; }
.sel { fill: none; stroke: var(--ink); stroke-width: 1.6; }
.selh { fill: var(--blue); opacity: calc(var(--bloom) * .2); }
.big { font-weight: 660; letter-spacing: -.035em; font-stretch: 100%; }
.lab { fill: var(--mute) !important; font-weight: 520; }
.lab.em { fill: var(--ink) !important; font-weight: 620; }
.lab.vs { fill: var(--ink) !important; font-weight: 600; }

/* The control: which layer is edited */
.control { align-self: center; display: flex; flex-direction: column; align-items: center; margin-top: 14px; }
.switch { display: inline-flex; border: 1px solid var(--ink); border-radius: 999px; padding: 3px; }
.switch button { padding: 7px 20px; border-radius: 999px; font-weight: 600; font-size: 14.5px; white-space: nowrap; transition: background .2s ease, color .2s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button[aria-pressed="true"]:hover { color: var(--paper); }
.hint { margin: 10px 0 0; font-size: 13.5px; color: var(--mute); text-align: center; max-width: 70ch; min-height: 2.8em; }

/* One drawn entrance, then only the slow sway and what the reader changes */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .axes, .enter .strip { animation: fade .8s .3s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 18ch; }
.say b { font-weight: 620; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.paper { margin: 18px 0 0; font-size: 15px; }
.paper a { color: var(--mute); text-decoration: none; border-bottom: 1px solid currentColor; padding-bottom: 1px; }
.paper a:hover, .paper a:focus-visible { color: inherit; }
.paper + .paper { margin-top: 10px; }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 0 6px 12px 0; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.lead.q { font-size: 15.5px; line-height: 1.45; color: var(--mute); max-width: 44ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.vals { list-style: none; margin: 16px 0 0; padding: 0; font-size: 14px; color: var(--mute); max-width: 44ch; }
.vals li { display: grid; grid-template-columns: 9.5em 1fr; align-items: baseline; gap: 12px; padding: 7px 0; border-top: 1px solid var(--rule); }
.vals li.here span:first-child { color: var(--ink); font-weight: 600; }
.vals b { color: var(--ink); font-weight: 650; }
.vals b.rl { color: var(--blue); }
.sub { margin: 18px 0 0; font-size: 13px; color: var(--mute); max-width: 44ch; }
.steps { display: flex; justify-content: space-between; margin-top: 16px; font-size: 13px; color: var(--mute); }
.steps button:hover { color: var(--ink); }
.steps button:disabled { opacity: .35; cursor: default; }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; display: block; }
  .cap0 { margin: 0 0 8px; }
  .pane { order: 4; margin-top: 22px; }
  .paper { order: 5; }
  svg { max-height: none; }
  .control { width: 100%; }
  .switch { display: grid; grid-template-columns: 1fr 1fr; border-radius: 22px; width: 100%; }
  .switch button { text-align: center; padding: 8px 6px; font-size: 14px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a { transition: none; }
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
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <div class="stage" id="stage">
    <p class="cap0" id="cap0"></p>
    <svg id="svg" role="img" tabindex="0"></svg>
    <div class="control">
      <div class="switch" role="group" aria-label="Which layer is edited">
        <button data-layer="0" aria-pressed="true">Edit layer 0</button>
        <button data-layer="8" aria-pressed="false">Edit layer 8</button>
      </div>
      <p class="hint" id="hint"></p>
    </div>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
    <p class="paper"><a href="/finding/rl-directions-move-activations">RL directions move activations: the whole edit at layer 24 ›</a></p>
    <p class="paper"><a href="/finding/two-jobs-in-the-edit#pairs">Two jobs in one edit: the broken pairs on the answers ›</a></p>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q, LOG = Math.log10;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const ARMS = ["paired", "rin", "rand"], N = 32, LAST = N - 1, STATES = ["0", "8"];
const val = (L, arm, l) => l < +L ? null : D.edits[L][arm].rms[l - L];           // the RMS shift after layer l
const grow = (L, arm, l) => val(L, arm, l) / val(L, arm, +L);                      // its growth since the edited layer
const MSPL = 40, FADE = 300;  // ms per layer while a line draws itself; the old lines' fade when the control changes

/* Geometry: the plate and the chart in a small 3D space around the plate's centre (x right, y down, z toward the viewer).
   The chart on the left, the readout on the right (on a phone, the readout above the chart). */
function geo() {
  const ph = narrow.matches;
  const g = ph
    ? { w: 480, h: 900, cx: 240, D: 2400, r: 22, deep: 30, blur: 12, X0: 76, X1: 448, Y0: 356, Y1: 704, strip: 728, tickY: 766,
        edY: 792, titleY: 832, ylY: 322, fs: 18, fsm: 17, fb: 84, mr: 1.3, rx: 30, bigY: 104, uY: [140, 164], vsY: 206,
        lY: [242, 268], phone: true, hit: 26 }
    : { w: 1000, h: 640, cx: 500, D: 2200, r: 30, deep: 40, blur: 16, X0: 108, X1: 630, Y0: 76, Y1: 452, strip: 474, tickY: 506,
        edY: 528, titleY: 560, ylY: 52, fs: 15, fsm: 13, fb: 96, mr: 1, rx: 682, bigY: 176, uY: [208, 228], vsY: 268,
        lY: [308, 331, 354, 377, 400], hit: 16 };
  g.cy = g.h / 2;
  g.a = ph ? [6, 8, g.w - 6, g.h - 8] : [24, 18, g.w - 24, g.h - 18];
  g.yd = [LOG(.0007), LOG(2.2)];
  g.X = l => g.X0 + l / LAST * (g.X1 - g.X0);
  g.Y = v => g.Y1 - (clamp(LOG(v), ...g.yd) - g.yd[0]) / (g.yd[1] - g.yd[0]) * (g.Y1 - g.Y0);
  return g;
}
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z) {
  const X = x - g.cx, Y = y - g.cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, g.cy + y1 * k];
}
function rounded(g, [x0, y0, x1, y1], r, z) {  // a rounded rectangle at depth z
  const p = [], corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}
const line = pts => pts.length ? "M" + pts.map(q => f(q[0]) + " " + f(q[1])).join("L") : "";
const quad = pts => line(pts) + "Z";
const YT = [.001, .01, .1, 1], XT = [0, 8, 16, 24, 31];

/* The state: the edited layer L, the layer it came from, when the old lines began to fade (ts) and when the new ones began
   to draw (tb). open: a panel key, or a selection "<arm>-<layer>" / "layer-<layer>". */
const S = { L: "0", prev: "0", ts: -1e9, tb: -1e9, open: null, g: null, el: {}, shown: {}, scr: {}, last: 0, t: 0 };

function build() {
  const g = S.g = geo(), svg = $("svg"), [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  const ytitle = g.phone ? "Activation change, RMS (log: each step is 10×)" : "How far the activations move, RMS (log scale: each step up is 10 times larger)";
  const xtitle = g.phone ? "Layer; after the lit one, all are the base" : "Layer of the model. Only the lit one is edited; every layer after it is the base, unchanged.";
  const pts = ARMS.map(a => Array.from({ length: N }, (_, l) => `<circle class="pt ${a}" id="p-${a}-${l}" r="0"/>`).join("")).join("");
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter><filter id="soft2" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${f(g.cy)}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .04)}" width="${aw}" height="${f(ah)}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .3)}" cy="${f(ay0 + ah * .24)}" rx="${f(aw * .3)}" ry="${f(ah * .2)}" transform="rotate(-14 ${f(ax0 + aw * .3)} ${f(ay0 + ah * .24)})" fill="url(#spec)"/>` +
    `<g class="axes"><path class="frame" id="frame"/><path class="grid" id="grid"/>` +
    YT.map((v, i) => `<text class="tick" id="ty${i}" font-size="${g.fsm}" text-anchor="end">${v}</text>`).join("") +
    XT.map((v, i) => `<text class="tick" id="tx${i}" font-size="${g.fsm}" text-anchor="middle">${v}</text>`).join("") +
    `<path class="g24" id="g24"/><text class="g24t" id="g24t" font-size="${g.fsm}" text-anchor="end">Layer 24</text>` +
    `<text class="title" id="yl" font-size="${g.fsm}">${esc(ytitle)}</text>` +
    `<text class="title" id="xl" font-size="${g.fsm}" text-anchor="middle">${esc(xtitle)}</text></g>` +
    `<g class="strip">${Array.from({ length: N }, (_, l) => `<path class="blk" id="b${l}"/>`).join("")}` +
    `<path class="blkh" id="bh"/><path class="blkon" id="bon"/><text class="edt" id="edt" font-size="${g.fsm}" text-anchor="middle">edited</text></g>` +
    `<g class="data"><path class="selg" id="selg"/><path class="ln glow" id="lg"/><path class="ln rand" id="l-rand"/><path class="ln rin" id="l-rin"/><path class="ln paired" id="l-paired"/>` +
    pts + ARMS.map(a => `<circle class="pt0 ${a}" id="s-${a}" r="0"/>`).join("") +
    `<circle class="tip" id="tip" r="0"/><circle class="pulse" id="pulse" r="0"/>` +
    `<circle class="selh" id="selh" r="0"/>` + ARMS.map(a => `<circle class="sel" id="sel-${a}" r="0"/>`).join("") +
    ARMS.map(a => `<text class="ll ${a}" id="ll-${a}" font-size="${g.fsm}" text-anchor="end">${esc((g.phone ? C.short : C.names)[a])}</text>`).join("") + `</g>` +
    `<g class="read" id="read"><text class="big" id="big" font-size="${g.fb}"></text>` +
    `<text class="lab em" id="u0" font-size="${g.fs}"></text><text class="lab" id="u1" font-size="${g.fs}"></text>` +
    `<text class="lab vs" id="vs" font-size="${f(g.fs * 1.32)}"></text>` +
    g.lY.map((_, i) => `<text class="lab" id="r${i}" font-size="${f(g.fs * .96)}"></text>`).join("") + `</g>`;
  S.el = {}; S.shown = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
}

/* Where the drawing is: during the fade (ts to ts + FADE) the old lines of S.prev, then the new lines of S.L, drawn up to
   head layers after the edited layer. */
function phase(now) {
  const pa = clamp((now - S.ts) / FADE, 0, 1);
  if (pa < 1) return { L: S.prev, head: LAST, op: 1 - ease(pa), slide: ease(pa), fresh: false };
  const head = still.matches ? LAST : Math.max(0, (now - S.tb) / MSPL);
  return { L: S.L, head, op: 1, slide: 1, fresh: true };
}
function tipOf(L, arm, h) {  // the end of a line drawn h layers past the edited layer, interpolated in log space
  const l0 = +L, top = Math.min(LAST, l0 + h), i = Math.floor(top), q = top - i;
  const v = i >= LAST ? val(L, arm, LAST) : 10 ** mix(LOG(val(L, arm, i)), LOG(val(L, arm, i + 1)), q);
  return { l: top, v };
}
const fmtV = v => v >= .1 ? v.toFixed(3) : v.toPrecision(3);
const fmtG = x => x >= 10 ? x.toFixed(1) : x.toPrecision(2);

function place(t, now) {
  const g = S.g, E = S.el, at = (el, q, dy) => { el.setAttribute("x", f(q[0])); el.setAttribute("y", f(q[1] + (dy || 0))); };
  const text = (id, v) => { if (S.shown[id] !== v) { E[id].textContent = S.shown[id] = v; } };
  const P = (x, y, z = 6) => proj(g, x, y, z);
  E.back.setAttribute("d", rounded(g, g.a, g.r, -g.deep));
  E.plate.setAttribute("d", rounded(g, g.a, g.r, 0));
  E.frame.setAttribute("d", line([P(g.X0, g.Y0 - 8), P(g.X0, g.Y1), P(g.X1 + 8, g.Y1)]));
  E.grid.setAttribute("d", YT.map(v => line([P(g.X0, g.Y(v), 4), P(g.X1, g.Y(v), 4)])).join(""));
  YT.forEach((v, i) => at(E["ty" + i], P(g.X0 - 10, g.Y(v)), g.fsm * .35));
  const ph = phase(now), L = ph.L, l0 = +L, Lm = mix(+S.prev, +S.L, ph.slide);
  XT.forEach((v, i) => { at(E["tx" + i], P(g.X(v), g.tickY)); E["tx" + i].classList.toggle("on", v === +S.L && ph.fresh); });
  E.g24.setAttribute("d", line([P(g.X(24), g.Y1, 4), P(g.X(24), g.Y(val(L, "paired", 24)) + 7 * g.mr, 4)]));  // up to the paired line
  at(E.g24t, P(g.X(24) - 6, g.Y1 - 8, 4));
  at(E.yl, P(g.phone ? 14 : 44, g.ylY));
  at(E.xl, P((g.X0 + g.X1) / 2, g.titleY));

  // The strip of 32 layers; the lit tile slides to the edited layer while the old lines fade.
  const cw = (g.X1 - g.X0) / LAST, bw = cw * .5, bh = 10 * g.mr;
  const tile = (x, z) => quad([P(x - bw / 2, g.strip - bh / 2, z), P(x + bw / 2, g.strip - bh / 2, z), P(x + bw / 2, g.strip + bh / 2, z), P(x - bw / 2, g.strip + bh / 2, z)]);
  for (let l = 0; l < N; l++) E["b" + l].setAttribute("d", tile(g.X(l), 4));
  const lit = g.X(Lm);
  E.bon.setAttribute("d", tile(lit, 10));
  E.bh.setAttribute("d", quad([P(lit - bw, g.strip - bh, 8), P(lit + bw, g.strip - bh, 8), P(lit + bw, g.strip + bh, 8), P(lit - bw, g.strip + bh, 8)]));
  at(E.edt, P(lit, g.edY));

  // The three lines, drawn up to the head; a point per layer they have reached.
  const sel = selection(), selArm = sel && sel.arm, dim = a => selArm && selArm !== a ? .28 : 1;
  ARMS.forEach(a => {
    const tp = tipOf(L, a, ph.head), pts = [];
    S.scr[a] = [];
    for (let l = 0; l < N; l++) {
      const c = E[`p-${a}-${l}`];
      if (l < l0 || l > tp.l) { c.setAttribute("r", "0"); S.scr[a][l] = null; continue; }
      const s = P(g.X(l), g.Y(val(L, a, l)), 8);
      pts.push(s); S.scr[a][l] = s;
      c.setAttribute("cx", f(s[0])); c.setAttribute("cy", f(s[1]));
      c.setAttribute("r", l === l0 ? "0" : f((a === "paired" ? 2.7 : 2.3) * g.mr));
      c.style.opacity = String(ph.op * dim(a));
    }
    if (tp.l > Math.floor(tp.l)) pts.push(P(g.X(tp.l), g.Y(tp.v), 8));
    E["l-" + a].setAttribute("d", line(pts));
    E["l-" + a].style.opacity = String(ph.op * dim(a));
    if (a === "paired") { E.lg.setAttribute("d", line(pts)); E.lg.style.opacity = String(ph.op * dim(a)); }
    const s0 = S.scr[a][l0];  // the start: the push the edit makes at its own layer
    E["s-" + a].setAttribute("r", s0 ? f(5 * g.mr) : "0");
    if (s0) { E["s-" + a].setAttribute("cx", f(s0[0])); E["s-" + a].setAttribute("cy", f(s0[1])); E["s-" + a].style.opacity = String(ph.op * dim(a)); }
    if (a === "paired") {  // the lit head of the line while it draws itself
      const drawing = ph.fresh && tp.l < LAST && !still.matches, e = pts[pts.length - 1];
      E.tip.setAttribute("r", drawing && e ? f(9 * g.mr) : "0");
      if (e) { E.tip.setAttribute("cx", f(e[0])); E.tip.setAttribute("cy", f(e[1])); }
    }
    // the name above the end of the line, once the line has reached it
    const end = S.scr[a][LAST], ll = E["ll-" + a];
    if (end) { at(ll, [end[0] + 2, end[1] - 11 * g.mr]); }
    ll.style.opacity = end ? String(ph.op * dim(a)) : "0";
  });

  // About every 6 s after the drawing, a soft light runs along the paired line from the edited layer to the last.
  { const run = 1700, per = 6000, since = now - S.tb - (LAST - l0) * MSPL - 900, el = E.pulse;
    if (!still.matches && ph.fresh && since > 0 && !selArm) {
      const k = (since % per) / run;
      if (k < 1) { const tp = tipOf(L, "paired", ease(k) * (LAST - l0)), s = P(g.X(tp.l), g.Y(tp.v), 9);
        el.setAttribute("cx", f(s[0])); el.setAttribute("cy", f(s[1])); el.setAttribute("r", f((3 + 4 * k) * g.mr));
        el.style.opacity = String(.55 * Math.sin(Math.PI * k)); }
      else el.style.opacity = "0";
    } else el.style.opacity = "0"; }

  // The selection: a guide at its layer and a ring on its point(s).
  const selLayer = sel && sel.layer >= l0 && ph.fresh && S.scr.paired[sel.layer] ? sel.layer : -1;
  E.selg.setAttribute("d", selLayer >= 0 ? line([P(g.X(selLayer), g.strip - bh, 5), P(g.X(selLayer), g.Y0, 5)]) : "");
  ARMS.forEach(a => {
    const c = E["sel-" + a], s = selLayer >= 0 && (!selArm || selArm === a) ? S.scr[a][selLayer] : null;
    c.setAttribute("r", s ? f(9 * g.mr) : "0");
    if (s) { c.setAttribute("cx", f(s[0])); c.setAttribute("cy", f(s[1])); }
  });
  { const s = selLayer >= 0 && selArm ? S.scr[selArm][selLayer] : null;
    E.selh.setAttribute("r", s ? f(g.mr * (still.matches ? 15 : 15 + 2 * Math.sin(t * 1.6))) : "0");
    if (s) { E.selh.setAttribute("cx", f(s[0])); E.selh.setAttribute("cy", f(s[1])); } }

  // The readout: the old state's words fade with its lines; the new words arrive with the drawing, and the large number
  // counts the paired line's growth up to layer 24, then stops.
  const R = C.read[L], pb = ph.fresh ? clamp((now - S.tb) / 300, 0, 1) : 1;
  const big = ph.fresh ? (tipOf(L, "paired", Math.min(ph.head, 24 - l0)).v / val(L, "paired", l0)) : R.big;
  const done = !ph.fresh || ph.head >= 24 - l0;
  text("big", `${(done ? R.big : big).toFixed(1)}×`);
  E.read.style.opacity = String(ph.fresh ? pb : ph.op);
  at(E.big, P(g.rx, g.bigY, 10));
  text("u0", R.u[0]); text("u1", R.u[1]); text("vs", R.base);
  at(E.u0, P(g.rx + 4, g.uY[0], 10)); at(E.u1, P(g.rx + 4, g.uY[1], 10)); at(E.vs, P(g.rx + 3, g.vsY, 10));
  g.lY.forEach((y, i) => { text("r" + i, R.lines[i]); at(E["r" + i], P(g.rx + 4, y, 10)); });
  if (ph.fresh && S.shown.hint !== L) {
    S.shown.hint = L; $("hint").textContent = C.hint[L];
    if (!still.matches) $("hint").animate([{ opacity: 0 }, { opacity: 1 }], { duration: 450, easing: "ease-out" });
  }
}

/* Always on: the plate sways by a few degrees and leans toward the mouse. About 30 frames a second. With reduced motion
   the page shows one still frame per state. */
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 30) return;
  S.last = now;
  const t = S.t = now / 1000;
  V.px += (V.tx - V.px) * .1; V.py += (V.ty - V.py) * .1;
  aim(4 * Math.sin(t * .13) + 3.5 * V.px, 2 * Math.sin(t * .09) - 2 * V.py);
  place(t, now);
}

function setLayer(L, opts = {}) {
  const now = performance.now(), quick = still.matches || opts.instant;
  S.prev = quick ? L : S.L; S.L = L;
  if (quick) { S.ts = -1e9; S.tb = -1e9; }
  else if (opts.enter) { S.ts = -1e9; S.tb = now + 650; }
  else { S.ts = now; S.tb = now + FADE; }
  document.querySelectorAll("[data-layer]").forEach(b => b.setAttribute("aria-pressed", b.dataset.layer === L));
  const R = C.read[L];
  $("svg").setAttribute("aria-label", `The model's 32 layers left to right; layer ${L} is edited. Three lines show how far the ` +
    `activations move after each layer (log scale). ${R.big}× ${R.u.join(" ")}; ${R.base}. ${R.lines.join(". ")}. ` +
    "Enter opens RL's paired directions at layer 24; arrow keys change the edited layer.");
  if (still.matches) { aim(0, 0); place(0, now); }
}

/* The side column: the five panels, or one layer (with one of the three edits, or all three). */
function selection() {
  const m = /^(paired|rin|rand|layer)-(\d+)$/.exec(S.open || "");
  return m ? { arm: m[1] === "layer" ? null : m[1], layer: +m[2] } : null;
}
function layerPane(sel) {
  const L = S.L, l0 = +L, l = sel.layer, arm = sel.arm, order = arm ? [arm, ...ARMS.filter(a => a !== arm)] : ARMS;
  const title = arm ? `${C.names[arm]}, layer ${l}` : l === l0 ? `Layer ${l}, the edited layer` : l < l0 ? `Layer ${l}, before the edit` : `Layer ${l}, the base`;
  const lead = arm ? C.what[L][arm] : l === l0 ? `This layer carries the edit: ${C.what[L].paired}` : l < l0
    ? `Layer ${l} comes before the edited layer ${l0}, so nothing changes here.`
    : `Layer ${l} is the base model's own layer, unchanged. It only passes on, and transforms, the change it receives from layer ${l0}.`;
  const rows = [];
  if (l >= l0) order.forEach(a => {
    const v = val(L, a, l), gr = grow(L, a, l), here = a === arm || (!arm && a === "paired");
    rows.push([C.names[a], `<b class="${a === "paired" ? "rl" : ""}">${fmtV(v)}</b>` + (l === l0 ? ": the push itself" : ` · <b>${fmtG(gr)}×</b> since layer ${l0}`), here]);
  });
  const base = D.base_rms[l];
  rows.push(["The running vector here", `<b>${base.toFixed(base < 10 ? 2 : 1)}</b>` + (l > 0 ? ` · ${fmtG(base / D.base_rms[0])}× since layer 0` : ""), false]);
  if (l >= l0) rows.push(["Paired shift, share of it", `<b>${(100 * val(L, "paired", l) / base).toFixed(2)} %</b>`, false]);
  return `<div><div class="dhead"><h2>${esc(title)}</h2><button class="close" data-open="">Close</button></div>` +
    `<p class="lead q">${esc(lead)}</p>` +
    `<ul class="vals">${rows.map(([a, b, h]) => `<li class="${h ? "here" : ""}"><span>${esc(a)}</span><span>${b}</span></li>`).join("")}</ul>` +
    `<p class="sub">Each value is an RMS shift: how far the activations move, a root-mean-square over the vector, after layer ${l}. Base in 32-bit floating point, no sampling; ${D.inputs} stored Base + cue answers, ${D.positions.toLocaleString("en-US")} positions.</p>` +
    `<div class="steps"><button data-step="-1"${l <= 0 ? " disabled" : ""}>‹ Layer ${Math.max(0, l - 1)}</button><button data-step="1"${l >= LAST ? " disabled" : ""}>Layer ${Math.min(LAST, l + 1)} ›</button></div></div>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open), sel = selection();
  $("pane").innerHTML = sel ? layerPane(sel) : p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>` + p.slice(4).map(l => `<p class="paper"><a href="${esc(l[0])}">${esc(l[1])}</a></p>`).join("")
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
/* The edited layer and what is open are one value in the address: #[l8/][<panel>|<arm>-<layer>|layer-<layer>]. */
function address(push) {
  const parts = [S.L === "0" ? "" : "l" + S.L, S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
const valid = x => C.panels.some(p => p[0] === x) || (/^(paired|rin|rand|layer)-(\d+)$/.test(x) && +x.split("-")[1] <= LAST);
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const L = parts.includes("l8") ? "8" : "0";
  S.open = parts.find(valid) || null;
  const s = selection(), drop = s && s.arm && s.layer < +L;  // an edit has no point before its edited layer
  if (drop) S.open = "layer-" + s.layer;
  if (first === true) setLayer(L, { instant: !!S.open, enter: !S.open });
  else if (L !== S.L) setLayer(L);
  if (drop) address(false);
  pane();
  if (still.matches) place(0, performance.now());
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "start" }); };
function open(key) {
  const was = S.open;
  S.open = key || null;
  address(true);
  pane();
  if (still.matches) place(0, performance.now());
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  else if (!key) $("svg").focus({ preventScroll: true });
}
function go(L) {
  if (L === S.L) return;
  setLayer(L);
  const s = selection();
  if (s && s.arm && s.layer < +L) S.open = "layer-" + s.layer;  // the edit has no point there now: show the layer instead
  pane();
  address(false);
}

const svg = $("svg");
function svgPoint(e) { const m = svg.getScreenCTM().inverse(); return [m.a * e.clientX + m.c * e.clientY + m.e, m.b * e.clientX + m.d * e.clientY + m.f]; }
function hit([x, y]) {  // the nearest drawn point, else the layer whose column holds the pointer
  const g = S.g;
  let best = null, bd = g.hit ** 2;
  ARMS.forEach(a => (S.scr[a] || []).forEach((q, l) => { if (!q) return; const d = (q[0] - x) ** 2 + (q[1] - y) ** 2; if (d < bd) { bd = d; best = `${a}-${l}`; } }));
  if (best) return best;
  const cw = (g.X1 - g.X0) / LAST;
  if (x < g.X0 - cw / 2 || x > g.X1 + cw / 2 || y < g.Y0 - 10 || y > g.strip + 20) return null;
  return "layer-" + clamp(Math.round((x - g.X0) / cw), 0, LAST);
}
svg.addEventListener("pointermove", e => { if (e.pointerType === "mouse") svg.style.cursor = hit(svgPoint(e)) ? "pointer" : "default"; });
svg.addEventListener("click", e => { const k = hit(svgPoint(e)); if (k) { open(k); show(); } });
function step(d) {
  const s = selection();
  if (!s) return;
  const l = clamp(s.layer + d, 0, LAST), arm = s.arm && l >= +S.L ? s.arm : null;
  open(arm ? `${arm}-${l}` : `layer-${l}`);
}
document.addEventListener("click", e => {
  const b = e.target.closest("[data-layer]"), o = e.target.closest("[data-open]"), s = e.target.closest("[data-step]");
  if (b) go(b.dataset.layer);
  if (o) open(o.dataset.open);
  if (s) { step(Number(s.dataset.step)); const n = $("pane").querySelector(`[data-step="${s.dataset.step}"]:not(:disabled)`); if (n) n.focus({ preventScroll: true }); }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey || /INPUT|TEXTAREA/.test(document.activeElement.tagName)) return;
  if (e.key === "Escape" && S.open) open("");
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
    if (selection()) step(e.key === "ArrowRight" ? 1 : -1);
    else go(S.L === "0" ? "8" : "0");
  }
  if (e.key === "Enter" && document.activeElement === svg) { e.preventDefault(); open("paired-24"); show(); }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); place(S.t, performance.now()); });
still.addEventListener("change", () => { if (still.matches) { setLayer(S.L, { instant: true }); aim(0, 0); place(0, performance.now()); } });
document.fonts.ready.then(() => { S.shown = { hint: S.shown.hint }; place(S.t, performance.now()); });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1; V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("cap0").textContent = C.cap;
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(\d+\.\d+)/g, "<b>$1</b>");
build();
aim(0, 0);
fromHash(true);
place(0, performance.now());
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
"""

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's picture reduced to a
# glass slab with a lit tile at the left edge and three lines leaving it: a lit one that climbs, two plain ones that stay
# low. The lines draw themselves from the left about every 9 s.
ICON = r"""(kit, t, tilt) => {
  const th = 5, T = Number(t) || 0, k = Math.min(1, ((T % 9) / 3)), n = 10;
  let out = kit.slab(44, 38, th) + kit.line(kit.at(-34, 24, th / 2), kit.at(34, 24, th / 2), .7, "plain", .8);
  out += kit.line(kit.at(-33, 27, th / 2), kit.at(-29, 27, th / 2), 3, "lit", 1);
  const ys = [[14, 16, 13, 6, -4, -12, -17, -20, -22, -23], [17, 17, 17, 16, 13, 11, 10, 9, 9, 8], [21, 21, 21, 21, 20, 19, 19, 18, 18, 18]];
  ys.forEach((y, j) => {
    for (let i = 0; i < n - 1; i++) {
      if (i / (n - 1) > k) break;
      const u0 = -31 + i * 7, u1 = u0 + 7;
      out += kit.line(kit.at(u0, y[i], th / 2), kit.at(u1, y[i + 1], th / 2), j ? 1.4 : 2.2, j ? "plain" : "lit", j ? .7 : 1);
    }
  });
  return out;
}"""

CAP = (f"Background: RL's change to each weight matrix is mostly 8 directions, each an input direction paired with an output "
       f"direction. Added at size 1.5 they lift Base + cue from {DATA['base_cue_right']} to {DATA['rl8_right']} of {DATA['n']} "
       f"harder problems right; with the pairs broken, {_br[0]} to {_br[-1]}. Here only one layer is edited.")

PAGE = PAGE.replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "cap": CAP, "panels": PANELS, "read": READ, "hint": HINT, "names": NAMES,
    "short": SHORT, "what": {"0": _what(0), "8": _what(8)},
    "data": {"edits": {L: {a: {"rms": _E[L][a]["rms"]} for a in ARMS} for L in _E}, "base_rms": _B,
             "inputs": DATA["inputs"], "positions": DATA["positions"]}}, ensure_ascii=False))


if __name__ == "__main__":  # run from the repository root: every number of DATA against the files; fails on a change
    g5 = lambda x: float(f"{x:.5g}")
    assert len(_B) == 32 and all(len(_E[L][a]["rms"]) == 32 - int(L) for L in _E for a in ARMS)
    # the headline numbers, computed from the literal
    assert (HEADLINE, round(GROWTH[0]["rin"], 1), round(GROWTH[0]["rand"], 1)) == (46.6, 8.2, 18.2), GROWTH[0]
    assert (round(GROWTH[8]["paired"], 1), round(GROWTH[8]["rin"], 1), round(GROWTH[8]["rand"], 1)) == (10.2, 3.3, 2.3), GROWTH[8]
    assert (round(OVER[0], 1), round(OVER[8], 1)) == (5.7, 3.1) and min(OVER.values()) >= DATA["predicted"]
    for L in _E:
        for a in ARMS:
            assert abs(GROWTH[int(L)][a] - DATA["growth_to_24"][L][a]) < 2e-3 * DATA["growth_to_24"][L][a], (L, a)
        assert len({_E[L][a]["add_rel"] for a in ARMS}) == 1  # the three edits of a layer have the same weight norm
    # the background: Base + cue and RL's 8 directions at 1.5 on the 328 harder problems (main and this branch)
    cells = "studies/rlneurons/results/xreward/edits/readout.json"
    if os.path.exists(cells):
        c = json.load(open(cells))["cells"]
        assert (c["base_cue_T1"]["right_v3"], c["top8x1.5_math31"]["right_v3"]) == (DATA["base_cue_right"], DATA["rl8_right"])
        print("background matches", cells)
    else:
        print("skipped:", cells, "is not here")
    broken = {k: f"studies/rlneurons/results/xreward/edits/{k}-01/metrics.json" for k in DATA["broken_right"]}
    if all(os.path.exists(p) for p in broken.values()):
        for k, p in broken.items():
            assert json.load(open(p))["counts"]["correct_v3"] == DATA["broken_right"][k], k
        print("broken pairs match", ", ".join(broken.values()))
    else:
        print(f"skipped: the broken-pair cells are not here (branch {DATA['branch']} only)")
    # run-04: every per-layer value against metrics.json, and the readout, run.json, spec and README
    if os.path.exists(DATA["metrics"]):
        me, ro, run = json.load(open(DATA["metrics"])), json.load(open(DATA["readout"])), json.load(open(DATA["run"]))
        j = run["job"]
        assert (ro["job"], j["job_id"], j["commit"], round(j["wall_s"], 1), j["models"]["base"]["repo"]) == \
            (DATA["job"], DATA["job"], DATA["job_commit"], DATA["wall_s"], DATA["base_model"]), j
        assert DATA["answers_job"] in j["answers"]
        assert (len(me["inputs"]), sum(i["cap_hit"] for i in me["inputs"]), me["positions"]["all"], me["max_tokens"], me["step"]) == \
            (DATA["inputs"], DATA["cap_hit_inputs"], DATA["positions"], DATA["answer_tokens"], DATA["step"])
        assert all(s["pass"] for s in me["selftest"].values()), me["selftest"]
        assert [g5(x) for x in me["base"]["rms"]] == _B
        keys = {d["key"] for L in _E for d in _E[L].values()}
        assert keys == set(me["edits"]) == set(ro["edits"]), keys
        for L in _E:
            for a in ARMS:
                d = _E[L][a]; m, r = me["edits"][d["key"]], ro["edits"][d["key"]]
                assert f"--layers {L}-{L}" in m["args"] and "--mods o,down" in m["args"] and "--scale 1.5" in m["args"], m["args"]
                assert r["edited_layer"] == int(L) and m["n_edited"] == d["n_edited"] and round(m["add_rel"], 7) == d["add_rel"], d["key"]
                rms = m["shift"]["all"]["rms"]
                assert all(x == 0 for x in rms[:int(L)]) and [g5(x) for x in rms[int(L):]] == d["rms"], d["key"]
                assert round(r["growth_to_24"], 3) == DATA["growth_to_24"][L][a], d["key"]
                assert all(abs(r["rms"][k] - rms[int(k)]) < 1e-12 for k in r["rms"]), d["key"]
        spec = open(DATA["spec_file"]).read()
        assert "the paired edit's growth is at least 3 times the input-only edit's" in spec and "Refuted if below 1.5" in spec
        readme = open("studies/rlneurons/README.md").read()
        assert "the paired edit's growth is 5.7 times the input-only edit's for layer 0 and 3.1 times for layer 8" in readme
        assert "stay\n  flat until about layer 12" in readme or "flat until about layer 12" in readme.replace("\n  ", " ")
        # run-03 and the additivity readout
        r3 = json.load(open(_R3["path"]))
        assert r3["job"] == _R3["job"]
        for a, k in (("paired", "top8x1.5"), ("rin", "rinx1.5"), ("perm", "permx1.5"), ("rand", "rand8x1.5")):
            assert g5(r3["edits"][f"{k}_write_math31"]["rms"]["24"]) == _R3[a], a
        ad = json.load(open(_AD["path"]))["layers"]["31"]
        assert (round(ad["full"], 3), g5(ad["sum_of_bands"]), round(ad["ratio"], 3), g5(ad["cos"])) == \
            (_AD["full"], _AD["sum"], _AD["ratio"], _AD["cos"]), ad
        print("DATA matches", DATA["metrics"], DATA["readout"], DATA["run"], _R3["path"], _AD["path"], "and the spec and README")
    else:
        print(f"skipped: the run's files ({RUN}, {_R3['path']}, {_AD['path']}) are not here; DATA was copied from branch "
              f"{DATA['branch']}, commit {DATA['commit'][:7]}")
    sys.exit(0)
