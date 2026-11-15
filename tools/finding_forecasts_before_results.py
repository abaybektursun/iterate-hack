"""Theories and two readers with no theory forecast numbers that running GPU jobs had not reported yet: who was nearer?

The page of one finding, served at /finding/forecasts-before-results (view.py serves every tools/finding_<slug>.py) and
reached from its tile on /findings, which ICON draws. It is the sequel of tools/finding_theories_on_trial.py. After
seven rounds of the theory engine on stored rows left no standing theory, studies/theory/lib/forecast.py (README of
studies/theory, section "Forecast runs") had each theory not refuted in round 7, six mechanisms written to disagree
(run 2) and two readers with no theory (the same model, the same board and work items, no theory) forecast the numbers
the open work items would report, each a value and a 90 % interval, before the results were posted. The picture is one
lit plate with one row per target, grouped by work item; a target asked in two runs is one row. Every row is drawn on
its own scale: 0 is the readers' average forecast, 1 the average half-width of their 90 % intervals. Each forecast is a
line (its interval) with a dot (its value): readers grey, theories blue; a theory's dot is filled when its forecast was
nearer the reported number than both readers of its run. A reported number is a bright bar that drops onto its row; an
open target shows "not reported yet". The large number counts the filled dots among the theory forecasts of reported
targets. The one control shows All, Landed or Open rows; rows travel and regroup. A click on a row shows its work item,
every forecast with its interval, the mechanism of each theory and the reason it gave, the commit time of each run and
the reported number with its board item. Address: /finding/forecasts-before-results#<landed|open>/<row id or panel>.
The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md).

    uv run tools/finding_forecasts_before_results.py           checks RUNS, THEORIES, ROWS and COUNTS against the files
    uv run tools/finding_forecasts_before_results.py --write   rewrites them from every forecast run folder that exists

Targets land every hour. After new scores: uv run tools/finding_forecasts_before_results.py --write
(then run it once more without --write: the check). A new run-<nn> folder needs nothing else; its targets show the
first words of their description until a label is added to _SAME (the check lists them), and a new work item shows its
id until GROUPS names it. Both modes run git and tools/board.py (for the time each result was posted). The deployed
site ships only tools/*.py, so the page reads nothing from studies/ at run time: the literals below are the copy.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from finding_theories_on_trial import NAMES as _ENGINE_NAMES  # noqa: E402  the engine's theories' short names, one source

F = "studies/theory/results/forecast/"
READERS = ["reader-1", "reader-2"]

TITLE = "Forecasts before results"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Can a theory forecast a number before the experiment reports it?"


def _cut(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1].rstrip(" ,;:") + "…"


def _sentence(s, n=240):  # the first sentence of a statement
    s = " ".join(str(s).split())
    m = re.search(r"(?<=[a-z0-9)%'])\.\s+(?=[A-Z])", s[30:])
    return _cut(s[:30 + m.start() + 1] if m else s, n)


def _git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout.strip()


def _utc(iso):  # "2026-11-15T06:50:58-08:00" -> "2026-11-15T14:50:58"
    return datetime.fromisoformat(iso).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _posted(item):  # the time a board item was posted, from the first line of board.py show
    out = subprocess.run(["uv", "run", "tools/board.py", "show", item], capture_output=True, text=True, check=True).stdout
    return re.search(r" at (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)Z", out.splitlines()[0]).group(1)


def _build():
    """RUNS, THEORIES and ROWS from the forecast run folders (every run-<nn> under F); run from the repository root.

    RUNS: [run, board snapshot UTC, commit that added forecasts.json, its time UTC, targets, scored UTC or None,
           the engine round whose theories forecast]
    THEORIES: [key "<run>/<forecaster>", forecaster id, first sentence of its statement]
    ROWS: one per target; a target asked in two runs (same work item, same label in _SAME) is one row.
      [row id, work item, label, unit, description, reported number or None, result item, posted UTC, quote,
       forecasts [[run, target id, forecaster, value, low, high, gain in nats from scores.json or None, reason]]]
    """
    runs = sorted(d for d in os.listdir(F) if re.fullmatch(r"run-\d\d", d))
    RUNS, THEORIES, rows, posted = [], [], {}, {}
    for run in runs:
        d = F + run + "/"
        rj = json.load(open(d + "run.json"))
        targets = json.load(open(d + "targets.json"))["targets"]
        forecasts = json.load(open(d + "forecasts.json"))
        scores = json.load(open(d + "scores.json")) if os.path.exists(d + "scores.json") else None
        mech = {m["id"]: m for m in json.load(open(d + "mechanisms.json"))["mechanisms"]} if os.path.exists(d + "mechanisms.json") else {}
        h, at = _git("log", "--diff-filter=A", "--format=%h %cI", "--", d + "forecasts.json").split("\n")[-1].split()
        RUNS.append([run, rj["utc"], h, _utc(at), len(targets), scores["scored_utc"] if scores else None, rj["round"]])
        for name in forecasts:
            if name not in READERS:
                st = mech[name]["statement"] if name in mech else json.load(open(f"{rj['round']}/theories/{name}.json"))["statement"]
                THEORIES.append([f"{run}/{name}", name, _sentence(st)])
        measured = {m["id"]: m for m in scores["measured"]} if scores else {}
        gain = {(n, r["id"]): r["gain"] for n, p in (scores["forecasters"].items() if scores else []) for r in p["rows"]}
        for t in targets:
            key = f"{run}/{t['id']}"
            label = LABELS.get(key) or _cut(t["what"], 44)
            row = rows.setdefault((t["item"], label), [key.replace("run-0", "r").replace("/", "-"), t["item"], label, t["unit"],
                                                       _cut(t["what"], 300), None, None, None, None, []])
            m = measured.get(t["id"])
            if m and m["value"] is not None:
                if row[5] is not None:
                    assert row[5] == m["value"], f"{key}: measured {m['value']} here, {row[5]} in an earlier run"
                else:
                    if m["item"] not in posted:
                        posted[m["item"]] = _posted(m["item"])
                    row[5:9] = [m["value"], m["item"], posted[m["item"]], _cut(m["quote"], 200)]
            for name, fs in forecasts.items():
                f = next(x for x in fs if x["id"] == t["id"])
                if f["value"] is not None:
                    row[9].append([run, t["id"], name, f["value"], f["low"], f["high"], gain.get((name, t["id"])),
                                   _cut(f["reason"], 260)])
    # Rows grouped by work item: items with a reported number first, then in the order the runs list them.
    order = [i for run in runs for i in json.load(open(F + run + "/run.json"))["work_items"]]
    landed = {r[1] for r in rows.values() if r[5] is not None}
    items = sorted({r[1] for r in rows.values()}, key=lambda i: (i not in landed, order.index(i)))
    return RUNS, THEORIES, sorted(rows.values(), key=lambda r: items.index(r[1]))


def _near(row):
    """Each forecast of a reported row against the two readers of its own run: "n" nearer the reported number than both,
    "t" as near as the nearer reader, "f" farther; None for a reader or an open target."""
    out = []
    for run, tid, who, v, lo, hi, g, why in row[9]:
        if row[5] is None or who in READERS:
            out.append(None)
            continue
        rd = min(abs(x[3] - row[5]) for x in row[9] if x[0] == run and x[1] == tid and x[2] in READERS)
        d = abs(v - row[5])
        out.append("n" if d < rd else "t" if d == rd else "f")
    return out


def _count(RUNS, ROWS):
    """DATA's counts.
    targets, landed, open: rows (a target asked in two runs is one row); asked: [target-run pairs, landed, open]
    theory: the theory forecasts of landed rows [count, nearer the reported number than both readers of their run, ties,
      reported number inside their own 90 % interval, total gain in nats from scores.json]
    reader: [inside reader 1's interval, inside reader 2's, landed target-run pairs]
    apart: theory forecasts of landed rows whose value lies outside both readers' intervals [count, inside their own]
    before: theory forecasts of landed rows whose run's forecasts.json was committed before the result was posted
    rows_any: landed rows with a theory forecast [count, rows where some theory was nearer than both readers]
    waiting: theory forecasts on open rows
    commit: the last commit that changed the forecast run folders"""
    run_at = {r[0]: r[3] for r in RUNS}
    th, rd, rows_any, pairs, waiting = [], [0, 0], [0, 0], set(), 0
    for row in ROWS:
        if row[5] is None:
            waiting += sum(f[2] not in READERS for f in row[9])
            continue
        mine = [(f, n) for f, n in zip(row[9], _near(row)) if n]
        if mine:
            rows_any[0] += 1
            rows_any[1] += any(n == "n" for f, n in mine)
        for f, n in mine:
            run, tid, who, v, lo, hi, g, why = f
            r = [x for x in row[9] if x[0] == run and x[1] == tid and x[2] in READERS]
            th.append([n, lo <= row[5] <= hi, g, all(not x[4] <= v <= x[5] for x in r), run_at[run] < row[7]])
        for x in row[9]:
            if x[2] in READERS:
                pairs.add((x[0], x[1]))
                rd[READERS.index(x[2])] += x[4] <= row[5] <= x[5]
    asked = sum(r[4] for r in RUNS)
    return {
        "targets": len(ROWS), "landed": sum(r[5] is not None for r in ROWS), "open": sum(r[5] is None for r in ROWS),
        "asked": [asked, len(pairs), asked - len(pairs)],
        "theory": [len(th), sum(x[0] == "n" for x in th), sum(x[0] == "t" for x in th), sum(x[1] for x in th),
                   round(sum(x[2] for x in th), 2)],
        "reader": rd + [len(pairs)],
        "apart": [sum(x[3] for x in th), sum(x[3] and x[1] for x in th)],
        "before": sum(x[4] for x in th),
        "rows_any": rows_any,
        "waiting": waiting,
        "commit": _git("log", "-1", "--format=%h", "--", F),
    }


# A label per target in plain words: the setting within its work item (GROUPS names the item). Targets of two runs with
# the same work item and the same label are one row. A target missing here (a new run) shows the first words of its
# description; the check lists the missing ones.
_SAME = {
    "MATH-500, plain prompt, one sample": ["run-01/t01", "run-02/t01"],
    "MATH-500, cue minus plain, in problems": ["run-01/t02"],
    "MATH-500, cue minus plain, in points": ["run-02/t02"],
    "MATH-500, vote over 9 samples": ["run-01/t03", "run-02/t03"],
    "MATH-500, vote over 12 samples": ["run-01/t04", "run-02/t04"],
    "328 harder problems, one sample": ["run-01/t05", "run-02/t05"],
    "Points gained over 16,384 tokens": ["run-01/t06"],
    "2026 problems, mean of 4 samples": ["run-01/t07", "run-02/t07"],
    "2026 problems, vote over 4 samples": ["run-02/t06", "run-02/t17"],
    "328 harder problems, vote over 4 samples": ["run-01/t08", "run-02/t08", "run-01/t11", "run-02/t11", "run-02/t16"],
    "MATH-500, one sample": ["run-01/t09", "run-02/t09", "run-01/t12", "run-02/t12"],
    "328 harder problems, mean of 4 samples": ["run-01/t10", "run-02/t10"],
    "400 MATH-500 problems it did not tune on": ["run-01/t13", "run-02/t14"],
    "328 harder problems": ["run-01/t14", "run-02/t15"],
    "Best on the 100 problems it tuned on": ["run-02/t13"],
    "Think-SFT + cue, mean of 4 samples": ["run-01/t15"],
    "Think-SFT + cue, vote over 4 samples": ["run-01/t16"],
    "RL, mean of 4 samples": ["run-01/t17"],
    "RL, vote over 4 samples": ["run-01/t18"],
    "Base + cue, mean of 4 samples": ["run-01/t19"],
    "Base + cue, vote over 4 samples": ["run-01/t20"],
}
LABELS = {k: label for label, keys in _SAME.items() for k in keys}
# The name of each work item, in two lines: the model and setting its rows share.
GROUPS = {
    "work-ab0f72": ["Base + cue +", "8 RL directions at 1.5x"],
    "work-7c069c": ["Three models on 136", "problems from 2026"],
    "work-480b1f": ["RL after 100 steps", "of training"],
    "work-60f040": ["Base + cue,", "vote over more samples"],
    "work-ceccc0": ["Base + cue, cut off", "at 32,768 tokens"],
    "work-8b4030": ["Think-SFT + RL's", "weight change at a = 2"],
    "work-ce7583": ["Base, settings", "chosen by an agent"],
    "work-dc9359": ["Think-SFT + cue, cut", "off at 32,768 tokens"],
}
# Short names of the forecasters: the engine's theories from finding_theories_on_trial.NAMES, the mechanisms of a run by
# "<run>/<id>". A theory missing here shows the first words of its statement; the check lists those.
NAMES = {
    "reader-1": "Reader 1", "reader-2": "Reader 2",
    "run-02/f2-m01": "Agent trades length for votes",
    "run-02/f2-m02": "Wrong answers scatter",
    "run-02/f2-m03": "Top-8 directions set stopping",
    "run-02/f2-m04": "Cut-off samples abstain",
    "run-02/f2-m05": "RL ends with a guess",
    "run-02/f2-m06": "Derivation plus a stop rule",
}

# Written by --write from the run folders: COUNTS (keys in _count's docstring), one run, one theory and one row per line
# (fields in _build's docstring).
COUNTS = {'targets': 25, 'landed': 9, 'open': 16, 'asked': [37, 12, 25], 'theory': [18, 7, 3, 10, -12.11], 'reader': [9, 11, 12], 'apart': [4, 0], 'before': 3, 'rows_any': [3, 2], 'waiting': 65, 'commit': '4eabd4e'}

RUNS = [
    ['run-01', '2026-11-15T14:45:56', 'c95e0f7', '2026-11-15T14:50:58', 20, '2026-11-15T15:03:15', 'studies/theory/results/engine/round-07'],
    ['run-02', '2026-11-15T14:53:16', '4eabd4e', '2026-11-15T15:07:24', 17, '2026-11-15T15:07:08', 'studies/theory/results/engine/round-07'],
]

THEORIES = [
    ['run-01/r5-m03-rival', 'r5-m03-rival', 'The top-8 edit is an incomplete switch that happens or fails sample by sample.'],
    ['run-01/r6-account-rival', 'r6-account-rival', "There is no RL-specific policy of finishing before the cap: at T 1.0 the cued base's cap hits are simply the hard, long end of the one difficulty axis, and any arm that is stronger on that axis fixes them at the rate its overall strength p…"],
    ['run-01/r6-m06', 'r6-m06', "The cued base's wrong steps come from the head of its own distribution, and Math-RL raises accuracy by changing which head token wins at a minority of positions, not by cutting probability from low-probability tokens, so RL's sampled text…"],
    ['run-01/r7-m05', 'r7-m05', "The cued base's misread and slip steps are what its language prior writes for a generic problem of the same kind, not for this problem: the problem text lowers them, removing it raises them relative to the rest of the answer, and they sit…"],
    ['run-01/r7-m08', 'r7-m08', "The Olmo-3.1 Code-RL weight change raises cued MATH-500 accuracy mainly by vetoing: it lowers the probability of the base's own located misread and slip steps on the same items where Math-RL 3.1 lowers them, while keeping the base's top to…"],
    ['run-01/r7-m11', 'r7-m11', 'When the cued Olmo-3 base answers a MATH-500 problem wrongly, the wrong value is set mostly by the shared prompt-plus-opening context (the same misreading or slip is the likely continuation in every sample under that context), so wrong ans…'],
    ['run-02/r5-m03-rival', 'r5-m03-rival', 'The top-8 edit is an incomplete switch that happens or fails sample by sample.'],
    ['run-02/r6-account-rival', 'r6-account-rival', "There is no RL-specific policy of finishing before the cap: at T 1.0 the cued base's cap hits are simply the hard, long end of the one difficulty axis, and any arm that is stronger on that axis fixes them at the rate its overall strength p…"],
    ['run-02/r6-m06', 'r6-m06', "The cued base's wrong steps come from the head of its own distribution, and Math-RL raises accuracy by changing which head token wins at a minority of positions, not by cutting probability from low-probability tokens, so RL's sampled text…"],
    ['run-02/r7-m05', 'r7-m05', "The cued base's misread and slip steps are what its language prior writes for a generic problem of the same kind, not for this problem: the problem text lowers them, removing it raises them relative to the rest of the answer, and they sit…"],
    ['run-02/r7-m08', 'r7-m08', "The Olmo-3.1 Code-RL weight change raises cued MATH-500 accuracy mainly by vetoing: it lowers the probability of the base's own located misread and slip steps on the same items where Math-RL 3.1 lowers them, while keeping the base's top to…"],
    ['run-02/r7-m11', 'r7-m11', 'When the cued Olmo-3 base answers a MATH-500 problem wrongly, the wrong value is set mostly by the shared prompt-plus-opening context (the same misreading or slip is the likely continuation in every sample under that context), so wrong ans…'],
    ['run-02/f2-m01', 'f2-m01', 'The autobench agent works under a fixed generation time per experiment, so it buys votes by shortening each sample (its best config: 10 samples at about 1,100 tokens each).'],
    ['run-02/f2-m02', 'f2-m02', "The cued base's wrong answers on a problem rarely share a value: slips are per-sample chance events that land on scattered numbers, while right answers coincide."],
    ['run-02/f2-m03', 'f2-m03', "The top singular directions of the RL-Math difference set when the base stops, not whether its reasoning is right: their dose sets the cap-hit rate, while right answers per finished answer stay near the base's 0.65; RL's correctness lives…"],
    ['run-02/f2-m04', 'f2-m04', 'A capped sample gives no answer, so in a plurality vote it abstains instead of adding a wrong value.'],
    ['run-02/f2-m05', 'f2-m05', "The RL-Math difference carries RL's habit of ending a long unsolved attempt with an asserted, underived number (per 1,312 hard328 samples RL finishes long and wrong 381 times, the base 281)."],
    ['run-02/f2-m06', 'f2-m06', "Think-SFT's difference from the base carries long derivation; the RL-Math difference carries a controller that stops once an answer is derived."],
]

ROWS = [
    ['r1-t10', 'work-ab0f72', '328 harder problems, mean of 4 samples', 'mean right answers per sample of 328', 'Mean number right per sample (over 4 samples) of the 328 harder problems for the base plus the 8 top RL-Math directions per matrix at 1.5x, with the cue at T 1.0, grader v3.', 200.25, 'result-95a4dc', '2026-11-15T15:00:31', '207, 198, 199, 197 right, mean 200.25', [['run-01', 't10', 'reader-1', 197, 188, 206, 0.0, 'Sizes 1 and 2 gave 192 and 190, and 203 at 1.5 was picked from seven sizes, so I expect regression toward about 197.'], ['run-01', 't10', 'reader-2', 197, 188, 206, 0.0, 'The single 203 was the best of seven sizes (1x 192, 2x 190), so expect regression toward ~197 over four samples.'], ['run-01', 't10', 'r5-m03-rival', 195, 186, 204, -0.284, "Theory: the top-8 edit puts the base on a weak dose of RL's own policy (longer, checked answers, errors only on hard problems); with the cue removing the plain-base register and 1.5x strengthening the dose, the per-sample mean sits just under RL's 200 single-…"], ['run-02', 't10', 'reader-1', 197, 189, 205, 0.0761, '203 at 1.5x was the best of seven sizes in one sample (192 at 1x, 190 at 2x), so the 4-sample mean regresses to about 197.'], ['run-02', 't10', 'reader-2', 196, 188, 204, -0.0824, '203 was the best of seven sizes; neighbours 1x 192 and 2x 190 suggest a true mean of ~196.'], ['run-02', 't10', 'r5-m03-rival', 197, 188, 206, 0.0052, "The theory says the top-8 edit puts the base on a weak dose of RL's own policy (longer answers, checking, few quick wrong answers), and the cue removes the plain-base register. A larger 1.5x dose should then bring the single-sample mean close to RL's 4-sample…"], ['run-02', 't10', 'f2-m03', 186, 179, 193, -3.0, 'Under a flat dial, 1.5x scores like 1x (192) and 2x (190); those single draws share a seed on which the base itself scored ~5 above its mean, so fresh seeds give ~186.'], ['run-02', 't10', 'f2-m05', 187, 180, 194, -3.0, 'At 2x the edit finished all 77 base cap-hit problems with 14 right: added dose adds assertions, so the 4-seed mean sits at the 1x level.'], ['run-02', 't10', 'f2-m06', 193, 186, 200, -1.0184, "On the base the controller lacks Think-SFT's derivations; 1.5x is near 1x's 192."]]],
    ['r1-t11', 'work-ab0f72', '328 harder problems, vote over 4 samples', 'right answers of 328', 'How many of the 328 harder problems the base plus the 8 top RL-Math directions per matrix at 1.5x gets right by majority vote over 4 samples, cue, T 1.0, grader v3.', 214, 'result-95a4dc', '2026-11-15T15:00:31', 'Under the vote over 4 the edit has 214', [['run-01', 't11', 'reader-1', 219, 207, 230, 0.0499, 'Single mean about 197 plus a vote gain of about 22 (base +33, RL +21; the edit has RL-like cap hits).'], ['run-01', 't11', 'reader-2', 220, 208, 230, -0.0525, 'Single mean ~197 plus an RL-like vote gain of ~+22 since cap hits are low (25).'], ['run-01', 't11', 'r5-m03-rival', 216, 206, 226, 0.3913, "Same weak-RL-dose reading: answers behave like RL's (few cap hits, 25 at 1.5x), so the vote adds about RL's +21 over its single mean rather than the base's +31, giving ~195+21, below RL's vote of 221."], ['run-02', 't11', 'reader-1', 219, 208, 229, 0.0652, 'Single mean about 197 plus an RL-like vote gain of about +22 (base +33, RL +21) because cap hits fall to about 25.'], ['run-02', 't11', 'reader-2', 220, 209, 230, -0.0698, 'Single mean ~196 plus an RL-like vote gain of ~+24, since the edit cuts cap hits (base +33 and RL +21 under the vote).'], ['run-02', 't11', 'r5-m03-rival', 219, 208, 230, 0.046, "If the 1.5x edit with the cue gives RL-like answers (few cap hits, errors only on hard problems), the 4-sample vote should gain about what RL's does (200 -> 221, +21), not the cued base's larger +33 from many cap hits: 197 + ~22 = 219."], ['run-02', 't11', 'f2-m02', 217, 208, 226, 0.3758, "Single mean ~194 plus an RL-like vote gain (~+22), since the edit's wrong values are also scattered."], ['run-02', 't11', 'f2-m03', 205, 197, 213, -1.0684, "Single mean ~186 plus RL's vote gain (+19-21), as the edit leaves few cap-hit abstentions and base-level precision."], ['run-02', 't11', 'f2-m04', 210, 202, 218, 0.3057, "The base's +33 vote gain came from its 77 cap abstentions; with 25 left the edit gains like RL (+20) on a ~190 mean."], ['run-02', 't11', 'f2-m05', 209, 201, 217, 0.1154, 'Mean ~187 plus a vote gain of ~+22, since asserted wrong values rarely agree.'], ['run-02', 't11', 'f2-m06', 215, 207, 223, 0.6228, 'Mean ~193 plus an RL-like vote gain.']]],
    ['r1-t12', 'work-ab0f72', 'MATH-500, one sample', 'right answers of 500', 'How many of the 500 MATH-500 problems the base plus the 8 top RL-Math directions per matrix at 1.5x answers right in one sample with the cue at T 1.0, grader v3.', 456, 'result-95a4dc', '2026-11-15T15:00:31', 'On MATH-500 one sample has 456 of 500', [['run-01', 't12', 'reader-1', 440, 427, 453, -0.5725, "Top-8 at 1x plain scored 427; adding the cue and the 1.5x size moves it toward the theta blends' 441-457 cue cells, with RL cue at 457."], ['run-01', 't12', 'reader-2', 445, 433, 456, 0.3618, 'Between base cue 410 and RL cue 457; hard328 effect sits near theta0.5 (452 on MATH-500) and top8 plain 1x gave 427.'], ['run-01', 't12', 'r5-m03-rival', 455, 445, 465, 1.7259, "Theory's mixture on top8 plain 427 = ~12.5% plain-base answers at ~50% right plus ~87.5% RL-like answers at ~90.5% right; the cue turns all answers RL-like (~453), and the stronger 1.5x dose adds a little, near RL cue 457 and theta-1.5 cue 453."], ['run-02', 't12', 'reader-1', 444, 432, 456, 0.3937, 'Top-8 at 1x plain is 427 and theta cue cells are 441-453; with the cue and 1.5x it should land in the mid-440s.'], ['run-02', 't12', 'reader-2', 440, 428, 452, -0.6586, 'Between base cue 410 and RL 457: top-8 plain gave 427 and theta-0.25 cue 441; MATH-500 has few cap hits for the edit to remove.'], ['run-02', 't12', 'r5-m03-rival', 452, 440, 462, 1.6548, "Fit the theory's mixture to top8 plain 427/500: 12.5% plain-base answers right about half the time, so the RL-like answers are right about 90.5% of the time. With the cue every answer is RL-like, giving 0.905 x 500 = 452, in line with theta 1.5 cue at 453."], ['run-02', 't12', 'f2-m01', 438, 429, 447, -3.0, "MATH-500 answers fit inside the 16k budget, so the edit's finishing adds only on the base's 27 cap hits, on top of top8's 427."], ['run-02', 't12', 'f2-m03', 426, 416, 436, -3.0, '8 directions alone gave 427 plain; the cue adds nothing to an installed opening, and finishing ~15 of 27 cap hits at ~0.4 precision is offset by guesses.'], ['run-02', 't12', 'f2-m05', 436, 426, 446, -3.0, "Few long unsolved attempts on MATH-500; the edit gives roughly top8's 427 plus a small cue and finish gain."], ['run-02', 't12', 'f2-m06', 445, 436, 454, 0.0132, "The controller boxes and finishes the cued base's answers: top8 427 plus cue and finishing."]]],
    ['r1-t15', 'work-7c069c', 'Think-SFT + cue, mean of 4 samples', 'mean right answers per sample of 136', 'Mean number right per sample (over 4 samples) of the 136 post-cutoff fresh2026 problems for Think-SFT with the opening cue, grader v3.', 60.0, 'result-5251c9', '2026-11-15T14:49:51', 'one sample 60.0 vs 50.5 vs 29.5', [['run-01', 't15', 'reader-1', 46, 33, 60, -0.7192, 'Think-SFT is slightly above RL on the hard328 single sample and leads on hard, long problems; I estimate about 50 % on AIME 2026, about 28 % on HMMT Feb and about 50 % on HMMT Nov under the 16k cap.'], ['run-01', 't15', 'reader-2', 54, 39, 69, 0.414, 'No fresh-set rate posted; Think-SFT about 1.4x the cued base on hard problems, assumed ~40 % on post-cutoff AIME/HMMT at a 16k cap.']]],
    ['r1-t16', 'work-7c069c', 'Think-SFT + cue, vote over 4 samples', 'right answers of 136', 'How many of the 136 post-cutoff fresh2026 problems Think-SFT with the opening cue gets right by majority vote over 4 samples, grader v3.', 75, 'result-5251c9', '2026-11-15T14:49:51', 'vote over 4 = 75 of 136', [['run-01', 't16', 'reader-1', 52, 38, 66, -2.2402, "Think-SFT's vote is near pass@4 because it abstains by hitting the cap (hard328 single 209 to vote 241); scaled to the lower fresh accuracy, that is about +6."], ['run-01', 't16', 'reader-2', 64, 48, 80, 0.6385, "Think-SFT's vote gains a lot because it abstains via cap hits (hard328 +10 pts); a smaller gain is assumed on the harder fresh set."]]],
    ['r1-t17', 'work-7c069c', 'RL, mean of 4 samples', 'mean right answers per sample of 136', 'Mean number right per sample (over 4 samples) of the 136 post-cutoff fresh2026 problems for Olmo-3.1 RL-Zero-Math with the plain prompt, grader v3.', 50.5, 'result-5251c9', '2026-11-15T14:49:51', 'one sample 60.0 vs 50.5 vs 29.5', [['run-01', 't17', 'reader-1', 39, 28, 51, -0.6731, 'RL beats the cued base by 12 points on AIME-like problems (Wang AIME24 35 vs 23); I estimate about 35 % on AIME, 18 % on HMMT Feb and 40 % on HMMT Nov.'], ['run-01', 't17', 'reader-2', 47, 33, 61, 0.3987, 'RL ~1.3x the cued base on hard sets (AIME24 35 vs 23 in Wang); assumed ~35 % on fresh2026.']]],
    ['r1-t18', 'work-7c069c', 'RL, vote over 4 samples', 'right answers of 136', 'How many of the 136 post-cutoff fresh2026 problems Olmo-3.1 RL-Zero-Math with the plain prompt gets right by majority vote over 4 samples, grader v3.', 57, 'result-5251c9', '2026-11-15T14:49:51', 'rl fresh2026 57/136', [['run-01', 't18', 'reader-1', 43, 31, 55, -1.0612, "RL's vote gain is modest (hard328 +21 of 328, about 6 points); scaled to fresh2026 that is about +4."], ['run-01', 't18', 'reader-2', 54, 39, 69, 0.5032, "RL's vote gain on hard328 was +6 pts per 100; about +7 problems assumed here."]]],
    ['r1-t19', 'work-7c069c', 'Base + cue, mean of 4 samples', 'mean right answers per sample of 136', 'Mean number right per sample (over 4 samples) of the 136 post-cutoff fresh2026 problems for the untrained Olmo 3 base with the opening cue, grader v3.', 29.5, 'result-5251c9', '2026-11-15T14:49:51', 'one sample 60.0 vs 50.5 vs 29.5', [['run-01', 't19', 'reader-1', 27, 18, 37, 0.1623, 'The base cue smoke got 3 of 10 AIME 2026; I estimate about 22 % on AIME, 11 % on HMMT Feb and 30 % on HMMT Nov.'], ['run-01', 't19', 'reader-2', 34, 22, 47, -0.1938, 'Smoke run gave 3/10 on AIME 2026; HMMT Feb is harder and Nov easier, so ~25 % overall.']]],
    ['r1-t20', 'work-7c069c', 'Base + cue, vote over 4 samples', 'right answers of 136', 'How many of the 136 post-cutoff fresh2026 problems the untrained Olmo 3 base with the opening cue gets right by majority vote over 4 samples, grader v3.', 38, 'result-5251c9', '2026-11-15T14:49:51', 'base fresh2026 38/136', [['run-01', 't20', 'reader-1', 32, 21, 43, -0.0691, 'The base gains the most from voting (hard328 +33, MATH-500 +36-41), so I add about 5 at this accuracy.'], ['run-01', 't20', 'reader-2', 40, 26, 54, 0.0647, 'Vote helps less at low per-sample accuracy; about +6 over the single-sample mean.']]],
    ['r1-t01', 'work-480b1f', 'MATH-500, plain prompt, one sample', 'right answers of 500', 'How many of the 500 MATH-500 problems the Olmo-3.1 RL-Zero-Math step-100 checkpoint answers right with the plain prompt, one sample at T 1.0 / top-p 1.0, graded by grader v3.', None, None, None, None, [['run-01', 't01', 'reader-1', 423, 410, 436, None, "Interim 405 of 478 (84.7 %) scaled to 500 is about 424; this is a new sample on a new box, so I use binomial noise around the step-400 plain 436 and the spec's 428."], ['run-01', 't01', 'reader-2', 421, 408, 433, None, 'Interim 405 of 478 (84.7 %) with the unfinished problems likely the long, harder ones; between base cue 410 and step-400 plain 436, spec predicted 428.'], ['run-02', 't01', 'reader-1', 420, 408, 432, None, 'Partial 405/478 plus about 15 of the remaining 22 harder problems (base cue got 13 of them), with rerun noise because the full rerun is a new sample.'], ['run-02', 't01', 'reader-2', 418, 405, 431, None, 'Partial 405/478 plus ~13 of the 22 held-back (longer) problems, as the base cue got 13/22 on them, with ~7-problem rerun noise on a new box.'], ['run-02', 't01', 'f2-m01', 419, 410, 428, None, '405/478 plus ~13 of the 22 long problems that were cut, rerun noise ~6.'], ['run-02', 't01', 'f2-m03', 420, 411, 429, None, 'Step 100 already finishes like the cued base; 405/478 plus ~14 of 22.'], ['run-02', 't01', 'f2-m06', 421, 412, 430, None, 'Step 100 has part of the controller: 405/478 plus ~15 of 22.']]],
    ['r1-t02', 'work-480b1f', 'MATH-500, cue minus plain, in problems', 'difference in right answers of 500 (cue minus plain)', 'At the Olmo-3.1 RL-Zero-Math step-100 checkpoint on MATH-500 (one sample, T 1.0 / top-p 1.0, grader v3), the right-answer count with the opening cue (427) minus the count with the plain prompt.', None, None, None, None, [['run-01', 't02', 'reader-1', 4, -10, 18, None, 'Cue cell 427 minus about 423 plain; the cue added -5 at step 400 and the spec predicted +0.5, and the noise of two single samples is about 8 problems.'], ['run-01', 't02', 'reader-2', 6, -7, 19, None, '427 cue minus a plain forecast of about 421; the cue added nothing at step 400 (431 vs 436) and step 100 already opens with Okay on 478/500.']]],
    ['r2-t02', 'work-480b1f', 'MATH-500, cue minus plain, in points', 'points (cue minus plain, of 500)', 'At RL-Zero-Math step 100 on MATH-500 (one sample, T 1.0 / top-p 1.0, grader v3), the score with the opening cue minus the score with the plain prompt, in percentage points.', None, None, None, None, [['run-02', 't02', 'reader-1', 1.4, -1.8, 4.6, None, 'Step-100 cue 427 minus an expected plain score of about 420, giving about 7 problems = 1.4 percentage points; step 400 showed the cue adding nothing.'], ['run-02', 't02', 'reader-2', 1.8, -1.0, 4.6, None, 'Step-100 cue 427 minus a forecast plain ~418 = ~9 problems = 1.8 points; noise comes from the plain rerun.']]],
    ['r1-t03', 'work-60f040', 'MATH-500, vote over 9 samples', 'right answers of 500', 'How many of the 500 MATH-500 problems the untrained Olmo 3 base with the opening cue gets right by majority vote over 9 samples at T 1.0, graded by grader v3.', None, None, None, None, [['run-01', 't03', 'reader-1', 454, 445, 462, None, "Vote over 4 is 446-450; Wang et al.'s majority curve (88.5 at 4, 91 at 8) suggests +2 to +3 points at 9, and pass@4 is 467; slightly below the theory's 456 because the grouping rule is uncertain."], ['run-01', 't03', 'reader-2', 453, 446, 460, None, "Vote over 4 is 446 (450 with restart), pass@4 467; Wang's majority curve gives about +2.5 points from 4 to 8 votes; theory predicted 456."], ['run-01', 't03', 'r6-account-rival', 456, 449, 462, None, "The rival's closing sentence says a base-only vote over more samples recovers part of the sharpening share and predicts 456/500 (interval 449-462 from result-c637b2), up from the vote-over-4 baseline of 446."], ['run-01', 't03', 'r7-m05', 453, 445, 461, None, "Inside the theory's scope cell (cued base, MATH-500, T 1.0, v3): misreads and slips depend on the path, so siblings are mostly right (afc423: 39 of 48), and a vote recovers them; wrong plans depend on the problem and repeat, which caps the vote. That puts vot…"], ['run-01', 't03', 'r7-m08', 453, 446, 460, None, "The theory's no_intervention clause says selection among base samples is the only veto the base can do on its own, measured at 446-450 for a vote over 4, and its no-new-path logic means problems the base never solves stay lost; so a vote over 9 adds only a fe…"], ['run-01', 't03', 'r7-m11', 451, 444, 458, None, "The theory's statement says wrong samples drawn under the one shared cue agree with each other and keep the vote below the independent-slip prediction (about 10 problems short at k=4, result-e41d94); more samples under the same opening do not break those wron…"], ['run-02', 't03', 'reader-1', 454, 447, 461, None, "Vote over 4 is 446 and pass@4 is 467; Wang's majority curve adds about 2.5 points from 4 to 8 votes, and 9 votes have fewer ties."], ['run-02', 't03', 'reader-2', 454, 447, 461, None, 'Vote over 4 = 446, with diminishing vote gains (Wang maj@4 to maj@8 +2.5 pts) and pass@4 467, so the vote over 9 lands around 454.'], ['run-02', 't03', 'r6-account-rival', 456, 449, 462, None, "The rival's closing sentence predicts that a base-only vote over more cued samples recovers part of the open sharpening share, giving 456/500 (interval 449-462 as filed in result-c637b2), up from the stored vote over 4 of 446."], ['run-02', 't03', 'r7-m05', 449, 443, 455, None, "The theory places the cued base's misread and slip steps near the mode of its generic-problem prior, so extra samples tend to repeat them rather than outvote them; the vote should then level off just above the stored vote over 4 (446, 450 after restart) inste…"], ['run-02', 't03', 'r7-m08', 453, 445, 461, None, "The theory's no_intervention clause says selecting among base samples can't reproduce the veto, because the vetoed slips and misreads are high-probability under the base; so the vote should level off a few points above the stored vote over 4 (446-450) and sta…"], ['run-02', 't03', 'r7-m11', 452, 445, 459, None, "The theory's scope is the cued base on MATH-500 at T 1.0 with grader v3, and it says wrong answers drawn under the same opening agree with each other. So adding more cued samples mostly adds to the same wrong groups, and the vote should level off: a few probl…"], ['run-02', 't03', 'f2-m01', 456, 450, 462, None, "Full-length samples are not budget-limited; going from 4 to 9 votes follows Wang's maj@4 to maj@8 step (+2.5 points) above 446."], ['run-02', 't03', 'f2-m02', 463, 457, 469, None, 'The 4-sample vote (446) loses 36 tied problems; 9 odd votes resolve most ties, and problems with a 1-2 of 4 solve rate win against scattered wrong values.'], ['run-02', 't03', 'f2-m04', 457, 451, 463, None, 'MATH-500 has few cap hits, so the vote grows normally: ~+11 from 4 to 9.']]],
    ['r1-t04', 'work-60f040', 'MATH-500, vote over 12 samples', 'right answers of 500', 'How many of the 500 MATH-500 problems the untrained Olmo 3 base with the opening cue gets right by majority vote over 12 samples at T 1.0, graded by grader v3.', None, None, None, None, [['run-01', 't04', 'reader-1', 456, 447, 464, None, 'The vote curve flattens past 9 samples (Wang et al.: 91 at 8, 93 at 16), so about 1-2 more problems than vote over 9.'], ['run-01', 't04', 'reader-2', 455, 447, 462, None, 'Small further gain over vote of 9 as the vote saturates below pass@k (~470).'], ['run-01', 't04', 'r6-account-rival', 458, 450, 466, None, "Same sharpening part as t03: the vote recovers the base's 1-2-of-k problems with diminishing returns, so 12 samples add about 2 over the theory's 456 for 9 (pass@4 467 is the ceiling scale)."], ['run-01', 't04', 'r7-m05', 455, 447, 463, None, "Same mechanism as t03: votes keep recovering errors that depend on the path, with shrinking returns, while wrong plans that depend on the problem stay. So vote-12 sits about 2 above vote-9, consistent with Wang's majority@8-16 curve (91-93 %) and the base's 4…"], ['run-01', 't04', 'r7-m08', 455, 447, 462, None, 'Same no_intervention clause: base-side selection only gets back problems where the base already has a right path, so the vote flattens out; 12 samples add about 2 more than 9, still below pass@4 467.'], ['run-01', 't04', 'r7-m11', 452, 445, 459, None, "Same mechanism: under the fixed cue the vote plateaus near the base's 446-450 at k=4 because agreeing wrong groups keep outvoting the right answer, so going from 9 to 12 samples adds at most about 1 problem."], ['run-02', 't04', 'reader-1', 456, 449, 463, None, 'Vote keeps rising slowly past 9 samples (Wang majority@8 91 %, @16 93 %), so about 2 more than the vote over 9.'], ['run-02', 't04', 'reader-2', 456, 448, 463, None, 'A small further gain over the vote over 9 as the vote curve plateaus below pass@k.'], ['run-02', 't04', 'r6-account-rival', 457, 450, 463, None, 'Same base-only vote clause of the rival: sharpening problems (base right 1-2 of 3) are on one difficulty axis, so going from 9 to 12 votes adds at most about one more problem beyond the predicted 456 plateau, while reach problems (kB = 0, ~0.1 of the gap) sta…'], ['run-02', 't04', 'r7-m05', 450, 444, 456, None, 'Same mode claim: the near-mode misread and slip errors recur across samples, so going from 9 to 12 votes adds at most about a problem over the plateau near the vote over 4 (446).'], ['run-02', 't04', 'r7-m08', 455, 447, 463, None, "Same no_intervention clause: the base keeps re-sampling its likely wrong steps, so 12 samples add only about 2 problems over the vote over 9 and still sit at or below RL's single sample (456-463), well short of base pass@4 (467)."], ['run-02', 't04', 'r7-m11', 453, 446, 460, None, 'Same part of the theory: wrong groups set by the opening grow along with the right group as samples are added, so going from 9 to 12 cued samples adds about one problem.'], ['run-02', 't04', 'f2-m01', 458, 452, 464, None, 'About 2 more problems than the 9-vote as the curve flattens.'], ['run-02', 't04', 'f2-m02', 466, 460, 472, None, 'The vote follows pass@k growth (pass@4 467, pass@12 ~480) at a fixed lag.'], ['run-02', 't04', 'f2-m04', 459, 453, 465, None, '+2 over the 9-vote.']]],
    ['r1-t05', 'work-ceccc0', '328 harder problems, one sample', 'right answers of 328', 'How many of the 328 harder problems the untrained Olmo 3 base with the opening cue answers right with the token cap raised to 32,768, one sample at T 1.0, grader v3.', None, None, None, None, [['run-01', 't05', 'reader-1', 167, 155, 180, None, "Base cue at 16k is 155-168 on this seed; its 77 cap hits are mostly failures to solve (forced commit right on 0-2, long answers right about 8 %), so the cap gives only a few more problems, unlike Think-SFT's +23."], ['run-01', 't05', 'reader-2', 167, 154, 180, None, 'Base cue single samples at 16k are 158-164 with ~77 cap hits; extra tokens recover a few (restart gave +3.4 pts, RL +2, base cap hits are mostly unsolved).'], ['run-01', 't05', 'r6-account-rival', 169, 156, 182, None, "The theory says the cued base's cap hits are just the hard, long end of the one difficulty axis, so a longer cap lets it finish them only at its own low rate for that difficulty (about +8 problems on ~70 cap hits, base long answers right ~15%), added to the b…"], ['run-02', 't05', 'reader-1', 168, 155, 181, None, 'Base cue single is 158-164 at 16k with 77 cap hits; a 32k cap lets roughly 8-10 of those finish right (Think-SFT gained 23, RL 2).'], ['run-02', 't05', 'reader-2', 172, 160, 184, None, 'Base cue 164 at 16k (155-168 across reruns) plus ~8-10 of 77 cap hits finishing right at 32k; base cap hits are mostly failures to solve, so it gains less than Think-SFT (+23) but more than RL (+2).'], ['run-02', 't05', 'f2-m01', 153, 144, 162, None, 'The 16k level of this sharded rerun is ~151-155 (earlier 4-shard replay 155; cap32 runs came in low at 16k), and the second 16k tokens buy ~2.'], ['run-02', 't05', 'f2-m03', 162, 153, 171, None, "A longer cap is a stop change at base precision: ~+4 over the base's 16k level of ~158."], ['run-02', 't05', 'f2-m04', 163, 154, 172, None, 'Single-sample cell: finishing ~70 caps at ~10 % precision adds ~5 to ~158.']]],
    ['r1-t06', 'work-ceccc0', 'Points gained over 16,384 tokens', 'points (score at cap 32,768 minus score at 16,384, same run)', 'For the untrained Olmo 3 base with the cue on the 328 harder problems (one sample, T 1.0, grader v3), how many points the score at a 32,768-token cap exceeds the score of the same answers counted at 16,384 tokens.', None, None, None, None, [['run-01', 't06', 'reader-1', 5, 1, 11, None, 'About 77 base cap hits; maybe half finish in the extra tokens at a low right rate (tokens 8k-16k bought 12 problems); RL gained 2 and Think-SFT 23.'], ['run-01', 't06', 'reader-2', 6, 1, 12, None, 'About 75 cap-hit answers can continue; base long answers are right ~15 % of the time and many keep rambling, so a handful flip right.'], ['run-01', 't06', 'r6-account-rival', 2.5, 0.6, 5.5, None, "Cap hits are the hard end of the difficulty axis rather than an unfinished-but-right policy gap, so the extra 16k tokens convert only ~8 of ~70 base cap hits at its matched-difficulty solve rate: about 2.5 percentage points (between RL's +0.6 and Think-SFT's…"]]],
    ['r1-t07', 'work-8b4030', '2026 problems, mean of 4 samples', 'mean right answers per sample of 136', 'Mean number right per sample (over 4 samples) of the 136 post-cutoff fresh2026 problems for the weight-edited model Think-SFT + 2 x (RL-Math minus base).', None, None, None, None, [['run-01', 't07', 'reader-1', 50, 36, 65, None, 'The a=2 transplant was about 10 % above Think-SFT on hard328 (with selection on that set), applied to my estimate of about 46 for Think-SFT cue on fresh2026.'], ['run-01', 't07', 'reader-2', 58, 42, 73, None, 'No fresh2026 base rate posted; post-cutoff AIME/HMMT assumed ~40 % for Think-SFT and the a=2 transplant adds ~3 points as on hard328 (232 vs 209).'], ['run-02', 't07', 'reader-1', 66, 57, 75, None, 'Think-SFT single 60.0 plus a hard328-like a=2 gain of about +7 points (cap hits 46 % leave room to finish).'], ['run-02', 't07', 'reader-2', 66, 58, 74, None, "Think-SFT single 60.0 plus a shrunken version of a=2's +6.9-point hard328 gain (a was chosen on hard328, so I regressed the gain toward zero)."], ['run-02', 't07', 'f2-m03', 64, 57, 71, None, "Finishing more of Think-SFT's 46 % capped samples at reduced precision adds ~4."], ['run-02', 't07', 'f2-m04', 67, 60, 74, None, 'Singles do rise: Think-SFT 60 plus ~7 from finishing.'], ['run-02', 't07', 'f2-m05', 56, 49, 63, None, "On 2026 problems the transplant cuts Think-SFT's long derivations into RL-style assertions (precision ~43 %), losing more right answers than it adds."], ['run-02', 't07', 'f2-m06', 78, 70, 86, None, "Fresh2026 is where Think-SFT caps most (46 %); stopping like RL with Think-SFT's derivations adds ~18 at its finished precision."]]],
    ['r1-t08', 'work-8b4030', '328 harder problems, vote over 4 samples', 'right answers of 328', 'How many of the 328 harder problems Think-SFT + 2 x (RL-Math minus base) gets right by majority vote over 4 samples (two new samples added to the two posted seeds, 234 and 229).', None, None, None, None, [['run-01', 't08', 'reader-1', 247, 237, 257, None, "Single samples 234 and 229; with fewer cap hits than Think-SFT (54 vs 94) the vote gain should sit between RL's +21 and Think-SFT's +32."], ['run-01', 't08', 'reader-2', 248, 238, 258, None, "Samples 234 and 229; with fewer cap hits than Think-SFT its vote gain looks more like RL's (+21) than Think-SFT's (+32), above Think-SFT's 241 vote."], ['run-02', 't08', 'reader-1', 248, 238, 258, None, "a=2 singles 234 and 229; the vote gain is smaller than Think-SFT's +32 because precision falls to about 72 %, so about +17."], ['run-02', 't08', 'reader-2', 249, 240, 258, None, "Singles 234/229, with a vote gain (+15-20) between RL's +21 and Think-SFT's near-pass@4 regime, reduced by lower precision."], ['run-02', 't08', 'f2-m02', 251, 242, 260, None, 'Singles ~230 plus a vote gain of ~+21, as for RL.'], ['run-02', 't08', 'f2-m03', 244, 235, 253, None, 'a=2 on Think-SFT mostly adds finishing; the vote gain shrinks as precision falls toward 0.8.'], ['run-02', 't08', 'f2-m04', 236, 227, 245, None, 'New-seed singles ~228; with caps cut from 94.5 to ~54 per sample the vote gain falls to ~+8.'], ['run-02', 't08', 'f2-m05', 241, 232, 250, None, "hard328 sits near the transplant's training distribution; new seeds ~228 plus a reduced vote gain."], ['run-02', 't08', 'f2-m06', 261, 252, 270, None, "Singles replicate (~231) and precision stays ~85 %, so the vote gains like Think-SFT's own (+30)."]]],
    ['r1-t09', 'work-8b4030', 'MATH-500, one sample', 'right answers of 500', 'How many of the 500 MATH-500 problems Think-SFT + 2 x (RL-Math minus base) answers right in one sample.', None, None, None, None, [['run-01', 't09', 'reader-1', 465, 455, 474, None, 'Think-SFT single 454-462 and a=1 transplant 467 on MATH-500; a=2 should be near those.'], ['run-01', 't09', 'reader-2', 466, 456, 474, None, 'a=1 scored 467 on MATH-500; Think-SFT single 457-462, RL 456-463; a=2 roughly flat with small degradation risk.'], ['run-02', 't09', 'reader-1', 465, 455, 474, None, 'a=1 scored 467 on MATH-500 and Think-SFT/RL singles are 454-463; a=2 should sit near that plateau.'], ['run-02', 't09', 'reader-2', 465, 455, 474, None, 'a=1 scored 467 on MATH-500 and Think-SFT/RL singles are 454-463; a=2 should land near the same ceiling.'], ['run-02', 't09', 'f2-m03', 463, 456, 470, None, "MATH-500 has few cap hits for extra stopping dose to convert; a=2 sits at a=1's level or just below."], ['run-02', 't09', 'f2-m05', 462, 455, 469, None, "MATH-500 problems are solvable, so assertions rarely occur: about a=1's level or slightly below."], ['run-02', 't09', 'f2-m06', 476, 468, 484, None, "a=1 already 467; at full controller strength Think-SFT's 25 MATH-500 cap hits and its v3-rejected answer lines (~4 per sample) become boxed finishes."]]],
    ['r2-t06', 'work-8b4030', '2026 problems, vote over 4 samples', 'right answers of 136', 'How many of the 136 fresh2026 competition problems the transplant model Think-SFT + 2 x (RL-Math - base) gets right by majority vote over 4 samples.', None, None, None, None, [['run-02', 't06', 'reader-1', 76, 65, 87, None, 'Think-SFT vote 75 and RL 57 on fresh2026; a=2 raises singles but lowers finished-answer precision, so the vote gains less than the single sample does.'], ['run-02', 't06', 'reader-2', 77, 68, 86, None, 'Think-SFT vote 75 at 46% cap hits; a=2 cuts cap hits but lowers precision, so the single rises to ~66 while the vote gain over the single shrinks.'], ['run-02', 't06', 'f2-m02', 78, 70, 86, None, 'Singles ~66 plus a vote gain of ~+12 from coinciding right answers.'], ['run-02', 't06', 'f2-m03', 73, 65, 81, None, "Singles up ~4, vote gain shrinks: about Think-SFT's 75."], ['run-02', 't06', 'f2-m04', 70, 62, 78, None, "Fewer abstentions on fresh problems dilute the vote: below Think-SFT's 75."], ['run-02', 't06', 'f2-m05', 63, 55, 71, None, "Asserted wrong values replace abstentions and fewer right derivations survive: the vote falls below Think-SFT's 75."], ['run-02', 't06', 'f2-m06', 86, 78, 94, None, 'Singles ~78 at high precision; the vote adds ~8.']]],
    ['r1-t13', 'work-ce7583', '400 MATH-500 problems it did not tune on', 'right answers of 400', 'How many of the 400 held-out MATH-500 problems the final configuration found by one headless autobench agent over 40 experiments on dev100 gets right with the untrained Olmo 3 base.', None, None, None, None, [['run-01', 't13', 'reader-1', 350, 325, 368, None, "The agent's dev best was 86/100 with a 10-sample vote (swarm cue 84 on dev); a 10-sample cued vote would score about 89-91 % on the full set, minus some dev overfitting and the time-budget token limit."], ['run-01', 't13', 'reader-2', 340, 318, 360, None, 'Agent best 86/100 on dev100 midway (cue config scores 84 there, 81.5 % on the other 400); expect ~85 % held out after dev overfitting.'], ['run-02', 't14', 'reader-1', 362, 345, 375, None, 'A vote over about 10 cue samples is near 90-91 % on MATH-500 (vote over 4 is 89.2 %), minus some overfit to dev100.'], ['run-02', 't14', 'reader-2', 356, 342, 368, None, 'A 10-sample cue vote on MATH-500 is ~89-91%, dev100 runs ~2 points easy and the config was selected on dev, so ~89% of 400.'], ['run-02', 't14', 'f2-m01', 338, 325, 351, None, 'Short-sample config is worth ~85.5 % on dev100 once selection is removed; dev100 runs ~2 points easy (cue 84 vs 82 %), so ~84.5 % of 400.'], ['run-02', 't14', 'f2-m02', 372, 362, 382, None, 'A ~10-sample vote on the other 400 converts most tied and low-rate problems: ~93 %.'], ['run-02', 't14', 'f2-m04', 356, 344, 368, None, 'Vote of cue-like samples on MATH problems, minus dev overfit.']]],
    ['r1-t14', 'work-ce7583', '328 harder problems', 'right answers of 328', 'How many of the 328 harder problems the final configuration found by one headless autobench agent over 40 experiments on dev100 gets right with the untrained Olmo 3 base.', None, None, None, None, [['run-01', 't14', 'reader-1', 190, 162, 210, None, "Base cue vote over 4 on hard328 is 192 (single 158-164); a dev-chosen vote config under a token budget probably lands near that, with wide doubt about the agent's prompt and cap."], ['run-01', 't14', 'reader-2', 170, 140, 200, None, 'Swarm cue single ~160, vote 192; a short-answer vote config tuned on MATH dev likely transfers partially to hard problems.'], ['run-02', 't15', 'reader-1', 190, 165, 210, None, 'Base cue vote over 4 is 192 on hard328; a bigger vote helps a little, but a token or time budget tuned on MATH-500 may cut long answers.'], ['run-02', 't15', 'reader-2', 197, 180, 210, None, 'Base cue vote over 4 on the 328 is 192 (pass@4 207), and a ~10-sample vote adds a few problems.'], ['run-02', 't15', 'f2-m01', 120, 80, 160, None, 'One full base sample gets 81 hard328 problems within 4,000 tokens; at ~1,100-1,500 tokens per sample far fewer finish, and a vote over ~10 such samples gives ~120.'], ['run-02', 't15', 'f2-m02', 200, 182, 218, None, 'Base 4-vote 192 on hard328; ~10 dispersed samples add ~8.']]],
    ['r2-t13', 'work-ce7583', 'Best on the 100 problems it tuned on', 'right answers of 100', 'The best dev100 score (right of 100) the single headless autobench agent reaches after all 40 experiments starting from the plain prompt.', None, None, None, None, [['run-02', 't13', 'reader-1', 89, 86, 93, None, 'Best was 86 after 15 of 40 experiments, and the maximum over 25 more noisy tries on dev100 usually creeps up by 2-4.'], ['run-02', 't13', 'reader-2', 89, 86, 93, None, 'Best-so-far was already 86 at 15 of 40 experiments and can only rise, with max-of-noise gains of a few points.'], ['run-02', 't13', 'f2-m01', 87, 86, 90, None, '86 at 15 of 40 came from ~1,100-token samples; short samples saturate on dev100, so later tries add only 1-2.'], ['run-02', 't13', 'f2-m02', 94, 91, 97, None, 'On dev100 a vote over 10+ cue samples alone is worth ~93-94 (cue single 84), and the search keeps the best of 40.']]],
    ['r2-t16', 'work-dc9359', '328 harder problems, vote over 4 samples', 'right answers of 328', 'How many of the 328 harder problems Think-SFT with the cue gets right by majority vote over 4 samples with the token cap at 32,768.', None, None, None, None, [['run-02', 't16', 'reader-1', 252, 242, 262, None, '16k vote 241 is near pass@4 (244), and a 32k cap adds +23 right per sample, so pass@4 and the vote rise by about 10.'], ['run-02', 't16', 'reader-2', 250, 240, 260, None, "32k single 230 (mean ~228); with cap hits gone the vote no longer equals pass@4, so it gains ~+22 like RL's vote."], ['run-02', 't16', 'f2-m01', 251, 242, 260, None, "Think-SFT's long answers are productive: +23 per sample at 32k, so pass@4 and the vote rise by ~10."], ['run-02', 't16', 'f2-m02', 254, 245, 263, None, 'At 32k the newly finished wrong answers are scattered and do not outvote coinciding right ones, so the vote rises with pass@4.'], ['run-02', 't16', 'f2-m03', 250, 241, 259, None, 'Single +23 at 32k; vote gain +8-10.'], ['run-02', 't16', 'f2-m04', 238, 229, 247, None, 'At 32k, 68 of 91 newly finished answers are wrong; problems won at 16k by one right sample plus caps now tie or lose, roughly cancelling the new rights.'], ['run-02', 't16', 'f2-m05', 247, 238, 257, None, 'Think-SFT finishing at 32k derives rather than asserts (36 % asserted), so its vote still gains ~+6.'], ['run-02', 't16', 'f2-m06', 252, 243, 261, None, 'A longer cap without the controller: +23 per sample, vote +11.']]],
    ['r2-t17', 'work-dc9359', '2026 problems, vote over 4 samples', 'right answers of fresh2026 problems', 'How many fresh2026 problems Think-SFT with the cue gets right by majority vote over 4 samples with the token cap at 32,768.', None, None, None, None, [['run-02', 't17', 'reader-1', 85, 74, 96, None, '16k vote 75 of 136 with 46 % cap hits; the 32k cap lets many of them finish at about 80 % precision, so about +10.'], ['run-02', 't17', 'reader-2', 84, 74, 94, None, '16k vote 75 / single 60 at 46% cap hits; at 32k most cap hits finish and ~20% are right, giving a single of ~72 and a vote of ~84.'], ['run-02', 't17', 'f2-m01', 82, 74, 90, None, '46 % of samples are capped at 16k; at 32k ~20 % of them finish right, adding ~7 to the vote.'], ['run-02', 't17', 'f2-m02', 85, 77, 93, None, 'Single rises ~13 at 32k; dispersed wrong values keep the vote gain intact.'], ['run-02', 't17', 'f2-m04', 72, 64, 80, None, '46 % of fresh samples abstain at 16k, which is why the vote sits 15 above the single; converting them at ~20 % precision costs the vote about what it adds to singles.'], ['run-02', 't17', 'f2-m05', 78, 70, 86, None, 'Newly finished fresh answers are mostly derived but wrong; +3 to the vote.'], ['run-02', 't17', 'f2-m06', 84, 76, 92, None, 'Fresh caps finish at 32k; vote +9.']]],
]

_STATEMENT = {k: s for k, _, s in THEORIES}
_name = lambda run, who: NAMES.get(who) or NAMES.get(f"{run}/{who}") or _ENGINE_NAMES.get(who) or \
    " ".join(_STATEMENT[f"{run}/{who}"].split()[:4])
_hm = lambda s: (datetime.fromisoformat(s) + timedelta(seconds=30)).strftime("%H:%M") + " UTC"  # to the nearest minute
_min = lambda a, b: (datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds() / 60  # minutes from a to b
_runname = lambda run: "Run " + str(int(run[4:]))
_m = lambda x: str(x).replace("-", "−")
_RUN = {r[0]: r for r in RUNS}
_ROW = {r[0]: r for r in ROWS}
TH, RD = COUNTS["theory"], COUNTS["reader"]
_chance = TH[0] / 3
_sd = (TH[0] * 2 / 9) ** .5
VERDICT = "about chance" if abs(TH[1] - _chance) <= 2 * _sd else "more than chance" if TH[1] > _chance else "less than chance"
_last = max(r[5] for r in RUNS if r[5])
_runs_txt = " and ".join(_hm(r[1]) for r in RUNS)

LINE = f"Theories were nearer the reported number than both no-theory readers in {TH[1]} of {TH[0]}: {VERDICT}."


def _fc(row, run, who):  # one forecast of a row
    return next(f for f in row[9] if f[0] == run and f[2] == who)


# The two examples in the side column, read from the rows (the check fails if they change).
_c1, _c2 = _ROW["r1-t12"], _ROW["r1-t11"]
_t1, _t2 = _fc(_c1, "run-01", "r5-m03-rival"), _fc(_c2, "run-02", "f2-m03")
_r1 = [_fc(_c1, "run-01", r)[3] for r in READERS]
_r2 = [_fc(_c2, "run-02", r)[3] for r in READERS]
CASES = {
    "r1-t12": f"Example, board item result-05cf4d. Before {_c1[6]} was posted, theory r5-m03-rival ({_name('run-01', 'r5-m03-rival')}) "
              f"forecast {_t1[3]} of 500 ({_t1[4]} to {_t1[5]}) for this cell; the two readers said {_r1[0]} and {_r1[1]}. "
              f"Reported: {_c1[5]}. Run 1 was committed at {_hm(_RUN['run-01'][3])}, {round(_min(_RUN['run-01'][3], _c1[7]))} "
              f"minutes before the result.",
    "r1-t11": f"Example: a mechanism written to disagree. f2-m03 ({_name('run-02', 'f2-m03')}) put this vote at {_t2[3]} "
              f"({_t2[4]} to {_t2[5]}), outside both readers' intervals; the readers said {_r2[0]} and {_r2[1]}. Reported: "
              f"{_c2[5]}, outside its interval and inside theirs.",
}
EXAMPLES = [["r1-t12", f"Example: {_t1[3]} forecast, {_c1[5]} reported"], ["r1-t11", "Example: a forecast written to disagree"]]

# The commit of each run against the results that reported its targets.
_timing = []
for _run in RUNS:
    _items = sorted({(r[6], r[7]) for r in ROWS if r[5] is not None and any(f[0] == _run[0] for f in r[9])})
    if _items:
        _timing.append(f"{_runname(_run[0]).lower()}, committed at {_hm(_run[3])}: " + ", ".join(
            f"{abs(round(_min(_run[3], at)))} min {'before' if _min(_run[3], at) > 0 else 'after'} {it}" for it, at in _items))
_engine = {}  # the engine's theories (not a run's mechanisms): targets forecast, per run
for _run in RUNS:
    for _k, _who, _ in THEORIES:
        if _k.startswith(_run[0]) and not re.fullmatch(r"f\d+-m\d\d", _who):
            _engine.setdefault(_run[0], []).append(sum(f[0] == _run[0] and f[2] == _who for r in ROWS for f in r[9]))
_e1 = _engine[RUNS[0][0]]
_landed_items = sorted({r[1] for r in ROWS if r[5] is not None and any(n for n in _near(r))})
_bare = sum(r[5] is not None and all(f[2] in READERS for f in r[9]) for r in ROWS)  # reported targets no theory forecast
_most = max(sum(1 for f in r[9] if f[0] == run and f[2] not in READERS) for r in ROWS if r[5] is not None for run in {f[0] for f in r[9]})
_round = int(RUNS[-1][6][-2:])  # the engine round whose theories forecast
_mech = sum(bool(re.fullmatch(r"f\d+-m\d\d", who)) for _, who, _ in THEORIES)
_word = lambda n: ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"][n] if n <= 10 else str(n)
_gain = TH[4]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences.
PANELS = [
    ["new", "What is new",
     f"{_word(_round).capitalize()} rounds of the theory engine tested theories on numbers that already existed when the theories were written. "
     "Here the theories forecast numbers that GPU jobs had not reported yet.",
     [f"{_word(len(RUNS)).capitalize()} runs read the board at {_runs_txt} and turned the open work items into {COUNTS['asked'][0]} targets: "
      f"{COUNTS['targets']} different numbers, a value and a 90 % interval forecast for each.",
      f"The forecasters: every theory not refuted in round {_round}, {_word(_mech)} mechanisms written to disagree with the "
      "readers, and two readers with no theory (the same model, the same board and work items, no theory).",
      "Bansal et al. (arXiv 2610.22599, Figure 1) asked five models to predict the effect of 288 machine-learning ideas "
      "before training; the best explained about half the variance (R² 0.49). Here the comparison is a theory against a "
      "reader without one, on one team's running jobs."]],
    ["why", "Why it matters",
     f"A theory that explains the results should forecast the next ones better than a careful reader of the same board. "
     f"So far the theories were nearer than both readers in {TH[1]} of {TH[0]} forecasts; one in three, "
     f"{_chance:.0f}, is chance.",
     [f"The reported number fell inside the theory's own 90 % interval {TH[3]} times in {TH[0]}; inside reader 1's "
      f"{RD[0]} and reader 2's {RD[1]} times in {RD[2]}.",
      f"The engine's score, which also rewards narrow intervals, gave the reported numbers less probability under the "
      f"theories than under the readers: {_m(_gain)} nats over the {TH[0]} forecasts.",
      f"{COUNTS['apart'][0]} theory forecasts lay outside both readers' intervals, where a theory could show what the "
      f"readers missed; {COUNTS['apart'][1]} of them held the reported number."]],
    ["how", "How we know",
     "Each run froze a copy of the board, turned the open work items into targets, and had every forecaster write its "
     "forecasts in an empty directory with only the Read and Write tools.",
     [f"Nearer: the forecast is closer to the reported number than both readers of the same run. A tie with a reader counts "
      f"as not nearer ({TH[2]} ties).",
      "A later step found each reported number in a board result posted after the snapshot, with a quote from that result; "
      "the quote is shown with its target.",
      "Each row is drawn on its own scale: 0 is the average of the readers' forecasts and 1 the average half-width of their "
      "90 % intervals. The numbers themselves are in the side column."]],
    ["limits", "What it does not show",
     f"{TH[0]} forecasts on {_word(COUNTS['rows_any'][0])} targets of {_word(len(_landed_items))} experiment"
     f"{'s' if len(_landed_items) > 1 else ''} cannot tell a good theory from a lucky one. {COUNTS['open']} targets are "
     "still open.",
     [f"Only {COUNTS['before']} of the {TH[0]} theory forecasts were committed to git before their result was posted. "
      + "; ".join(_timing)[:1].upper() + "; ".join(_timing)[1:] + ". The others were written from the frozen board copy.",
      f"The engine's theories said nothing about most targets: in run 1 each forecast {min(_e1)} to {max(_e1)} of "
      f"{RUNS[0][4]}. {_word(_bare).capitalize()} reported targets had no theory forecast at all.",
      f"On {COUNTS['rows_any'][1]} of the {COUNTS['rows_any'][0]} reported targets with a theory forecast, at least one "
      f"theory was nearer than both readers. With up to {_word(_most)} theories per target, one of them is often nearest by chance, "
      "so the count above is per forecast."]],
    ["run", "How to reproduce it",
     "uv run tools/finding_forecasts_before_results.py, from the repository root, rebuilds every row from the forecast run "
     "folders and checks the copy on this page; after new scores, run it with --write.",
     [f"Run folders: {F}{RUNS[0][0]} to {RUNS[-1][0]} (targets.json, forecasts.json, scores.json, mechanisms.json), as of "
      f"commit {COUNTS['commit']}.",
      "Forecasts and scores: studies/theory/lib/forecast.py make and score; README of studies/theory, section Forecast runs.",
      "Board items: result-564441 (the forecasts), result-05cf4d (the first theory forecast reported), and the results "
      "that reported the numbers: " + ", ".join(sorted({r[6] for r in ROWS if r[6]})) + "."]],
]

# The words beside the large number, per state of the control: All, Landed, Open. Desktop and phone.
_read = [f"theory forecasts nearer the reported number than both readers",
         f"on {_word(COUNTS['rows_any'][0])} reported targets; {_chance:.0f} of {TH[0]} would be chance, one in three",
         "Readers: the same model and the same board, with no theory."]
_open = [f"targets not reported yet, with {COUNTS['waiting']} theory forecasts waiting",
         f"Board read at {_runs_txt}; scored again as results post.",
         f"Last scored at {_hm(_last)}."]
READ = {"desk": [_read, _read, _open],
        "phone": [[f"theory forecasts nearer than both readers", f"on {_word(COUNTS['rows_any'][0])} reported targets; {_chance:.0f} is chance",
                   "Readers: the same model and board,", "with no theory."]] * 2 +
                 [[f"targets not reported yet", f"{COUNTS['waiting']} theory forecasts are waiting", f"Board read at {_runs_txt};",
                   f"last scored at {_hm(_last)}."]]}

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
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table
   with a cast shadow in place of the glow. The light comes from the upper left in both. Blue is a theory's forecast,
   filled when it was nearer the reported number than both readers; grey is a reader with no theory; the bright bar is
   the reported number. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --rd: #8a96a0; --band: rgba(16, 24, 32, .05);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --rd: #6c7984; --band: rgba(233, 239, 243, .045);
  }
}
:root[data-theme="dark"] {
  --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
  --blue: #8fb1ff; --red: #ff6b7c;
  --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
  --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
  --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
  --rd: #6c7984; --band: rgba(233, 239, 243, .045);
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

/* The picture: one plate holding the readout and one row per target, and the one switch under it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg { width: 100%; max-height: calc(100vh - 170px); display: block; overflow: visible; touch-action: pan-y; user-select: none; -webkit-user-select: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
svg .hit { pointer-events: all; fill: var(--ink); fill-opacity: 0; stroke: none; cursor: pointer; outline: none; }
svg .hit:hover { fill-opacity: .035; }
svg .hit:focus-visible { stroke: var(--blue); stroke-width: 1.5; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.band { fill: var(--band); }
.grid { stroke: var(--ink); stroke-width: 1; opacity: .07; fill: none; }
.zero { stroke: var(--ink); stroke-width: 1; opacity: .2; stroke-dasharray: 2 3; }
.sep { stroke: var(--ink); stroke-width: 1; opacity: .09; fill: none; }
.tick { fill: var(--mute); font-weight: 500; }
.ctitle { fill: var(--mute); font-weight: 560; }
.gname { font-weight: 660; font-stretch: 104%; }
.lab { fill: var(--ink); font-weight: 470; font-stretch: 94%; }
.lab.on { font-weight: 660; }
.val { fill: var(--ink); font-weight: 660; }
.nv { fill: var(--mute); font-weight: 470; }
.iv { stroke-width: 1.5; stroke-linecap: round; fill: none; }
.iv.rd { stroke: var(--rd); opacity: .95; }
.iv.th { stroke: var(--blue); opacity: .5; }
.pt.rd { fill: var(--rd); }
.pt.th { fill: var(--sheet); stroke: var(--blue); stroke-width: 1.3; transition: fill .35s ease; }
.pt.th.win { fill: var(--blue); }
.far { fill: var(--blue); opacity: .6; }
.mglow { stroke: var(--ink); stroke-width: 6; stroke-linecap: round; opacity: calc(var(--bloom) * .12); }
.mbar { stroke: var(--ink); stroke-width: 2.2; stroke-linecap: round; }
.ripple { fill: none; stroke: var(--ink); stroke-width: 1.3; }
.selbox { fill: var(--blue); fill-opacity: .06; stroke: var(--blue); stroke-opacity: .55; stroke-width: 1.2; }
.big { fill: var(--ink); font-weight: 640; letter-spacing: -.035em; font-stretch: 100%; }
.l1 { fill: var(--ink); font-weight: 520; }
.l2, .ccap, .cci { fill: var(--mute); font-weight: 500; }
.cnum { fill: var(--ink); font-weight: 600; letter-spacing: -.02em; opacity: .78; font-stretch: 100%; }
.cname { fill: var(--ink); font-weight: 560; }
.vrule { stroke: var(--ink); stroke-width: 1; opacity: .12; }
.klab, .note { fill: var(--mute); font-weight: 520; }
.switch { display: inline-flex; align-self: center; margin-top: 14px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 20px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; text-align: center; transition: background .15s ease, color .15s ease; }
.switch button span { font-weight: 480; opacity: .7; margin-left: 6px; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button[aria-pressed="true"]:hover { color: var(--paper); }
.hint { align-self: center; margin: 9px 0 0; font-size: 13px; color: var(--mute); text-align: center; }

/* One drawn entrance, then only the slow sway, the replayed reported numbers and what the reader changes */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .frame { animation: fade .7s .45s both; }
.enter .read { animation: fade .7s .6s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); padding-bottom: 24px; }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.more.ex { margin-top: 18px; border-top: 0; }
.more.ex button { font-size: 15px; color: var(--mute); padding: 9px 0; }
.more.ex button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.dhead h2 span { display: block; color: var(--mute); font-size: 13px; font-weight: 540; font-stretch: 106%; letter-spacing: 0; margin-bottom: 2px; }
.close { font-size: 13px; color: var(--mute); flex: none; }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.share { margin: 18px 0 0; display: flex; align-items: baseline; gap: 12px; }
.share b { flex: none; white-space: nowrap; font-size: 40px; font-weight: 640; letter-spacing: -.03em; line-height: 1; }
.share b.open { font-size: 24px; font-weight: 520; color: var(--mute); letter-spacing: -.01em; }
.share span { color: var(--mute); font-size: 14px; line-height: 1.3; }
.case { margin: 16px 0 0; padding: 10px 0 10px 12px; border-left: 2px solid var(--blue); font-size: 14.5px; line-height: 1.45; max-width: 44ch; }
.quote { margin: 14px 0 0; padding: 2px 0 2px 12px; border-left: 2px solid var(--rule); font-size: 14px; color: var(--mute); max-width: 44ch; }
.quote b { color: var(--ink); font-weight: 600; }
.facts { list-style: none; margin: 16px 0 0; padding: 0; font-size: 14px; color: var(--mute); max-width: 44ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.facts li b { color: var(--ink); font-weight: 620; }
.zoom { width: 100%; max-width: 340px; height: auto; max-height: none; margin: 16px 0 0; overflow: visible; }
.z-ax { stroke: var(--rule); stroke-width: 1; }
.z-rd { stroke: var(--rd); stroke-width: 1.6; stroke-linecap: round; }
.z-th { stroke: var(--blue); stroke-width: 1.6; stroke-linecap: round; opacity: .6; }
.z-prd { fill: var(--rd); }
.z-pth { fill: var(--sheet); stroke: var(--blue); stroke-width: 1.3; }
.z-pth.win { fill: var(--blue); }
.z-me { stroke: var(--ink); stroke-width: 1.8; }
.z-t { fill: var(--mute); font-size: 11px; font-weight: 500; }
.z-mt { fill: var(--ink); font-size: 11.5px; font-weight: 660; }
h3 { margin: 22px 0 0; font-size: 14px; font-weight: 660; font-stretch: 110%; padding-bottom: 6px; border-bottom: 1px solid var(--rule); }
h3 span { display: block; color: var(--mute); font-size: 13px; font-weight: 480; font-stretch: 100%; margin-top: 2px; }
.fcs { list-style: none; margin: 0; padding: 0; max-width: 44ch; }
.fcs li { padding: 9px 0 9px 10px; border-bottom: 1px solid var(--rule); border-left: 2px solid transparent; font-size: 13.5px; color: var(--mute); }
.fcs li.th { border-left-color: color-mix(in oklab, var(--blue) 35%, transparent); }
.fcs li.w { border-left-color: var(--blue); }
.fcs .fn { display: flex; justify-content: space-between; gap: 10px; }
.fcs .fn b { color: var(--ink); font-weight: 640; }
.fcs .pv b { color: var(--ink); font-weight: 640; }
.fcs .pm { color: var(--ink); margin-top: 3px; line-height: 1.4; overflow-wrap: anywhere; }
.fcs .pr { font-size: 12.5px; margin-top: 3px; line-height: 1.4; overflow-wrap: anywhere; }
.steps { display: flex; justify-content: space-between; margin-top: 14px; font-size: 13px; color: var(--mute); }
.steps button:hover { color: var(--ink); }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; display: flex; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
  .switch { order: -1; display: flex; margin: 0 0 14px; }
  .switch button { flex: 1; padding: 10px 4px; font-size: 14px; }
  .hint { order: -1; margin: 0 0 10px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a, .pt.th { transition: none; }
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
    <svg id="svg" role="group"></svg>
    <div class="switch" id="switch" role="group" aria-label="Which targets"></div>
    <p class="hint" id="hint"></p>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v)), ease = p => p < .5 ? 4 * p * p * p : 1 - (-2 * p + 2) ** 3 / 2;
const avg = a => a.reduce((x, y) => x + y, 0) / a.length;
const hm = s => s ? new Date(Date.parse(s + "Z") + 30000).toISOString().slice(11, 16) + " UTC" : "";  // to the nearest minute
const mins = (a, b) => (Date.parse(b + "Z") - Date.parse(a + "Z")) / 60000;
/* A number as the files hold it: counts with a thousands comma, others to at most two decimals, a true minus sign. */
function fv(x) {
  if (x == null) return "";
  const a = Math.abs(x), s = Number.isInteger(a) ? a.toLocaleString("en-US") : String(+a.toFixed(2));
  return (x < 0 ? "−" : "") + s;
}

/* The rows: one per target, each forecast placed on the row's own scale (0 = the readers' average forecast, 1 = the
   average half-width of their 90 % intervals). Readers first, then theories, in the order of the runs. */
const STATES = [{ id: "", name: "All" }, { id: "landed", name: "Landed" }, { id: "open", name: "Open" }];
const DOM = [-2.5, 2.5], TICKS = [-2, -1, 0, 1, 2];
const RUN = Object.fromEntries(C.runs.map(r => [r[0], r]));
const ROWS = C.rows.map((r, i) => {
  const rd = r.fc.filter(x => x.reader), c = avg(rd.map(x => x.v)), s = avg(rd.map(x => (x.hi - x.lo) / 2)) || 1;
  const z = v => (v - c) / s;
  const fc = [...rd, ...r.fc.filter(x => !x.reader)].map(x => ({ ...x, z: z(x.v), zl: z(x.lo), zh: z(x.hi) }));
  return { ...r, i, fc, zm: r.m == null ? null : z(r.m), cur: { y: 0, op: 0, p: 16 }, from: null, to: null, t0: 0, show: false, arr: 1e12, rip: -1e9, won: false };
});
const RID = Object.fromEntries(ROWS.map(r => [r.id, r]));
const ITEMS = [...new Set(ROWS.map(r => r.item))];
const member = (r, s) => s === 0 || (s === 1 ? r.m != null : r.m == null);
const S = { s: 0, open: null, g: null, el: {}, last: 0, t: 0, txt: {}, groups: ITEMS.map(() => ({ y: 0, op: 0, from: null, to: null, t0: 0 })),
  nums: null, h: null, rove: 0, moving: true, rp: null, rpNext: 0, rpAt: 0 };

/* Geometry, in the units of the viewBox. Desktop: the work item and the target at the left, the scale, the reported
   number at the right. Phone: each target's words above its row, and the plate grows with the number of rows. */
function geo() {
  return narrow.matches
    ? { w: 480, phone: true, a0: 6, r: 22, deep: 28, blur: 12, cx: 240, D: 1800, X: [34, 300], gx: 30, vx: 448, fs: 17,
        big: [28, 86, 70], l: [118, 142, 166, 190], ref: 232, top: 250, pitch: 52, gh: 34, gap: 14, tail: [34, 64, 96, 128, 160, 196] }
    : { w: 1000, phone: false, a0: 14, r: 30, deep: 40, blur: 16, cx: 500, D: 2200, X: [474, 862], gx: 52, lx: 456, vx: 880, fs: 13,
        big: [56, 102, 76], l: [134, 156, 178], con: [668, 56, 104, 134, 156], vr: 640, ref: 216, top: 230, bottom: 704, pmax: 50, gap: 10,
        note: 730, key: 758, h: 782 };
}
const sx = (g, z) => mix(g.X[0], g.X[1], (clamp(z, DOM[0], DOM[1]) - DOM[0]) / (DOM[1] - DOM[0]));

/* The layout of state s: the y of every shown row and work item, the row pitch and the plate's height. */
function layout(s) {
  const g = S.g, rows = ROWS.filter(r => member(r, s)), used = ITEMS.filter(i => rows.some(r => r.item === i));
  const ys = {}, gy = {};
  if (g.phone) {
    let y = g.top;
    used.forEach((item, k) => {
      if (k) y += g.gap;
      gy[item] = y + 22; y += g.gh;
      rows.filter(r => r.item === item).forEach(r => { ys[r.i] = y; y += g.pitch; });
    });
    return { ys, gy, pitch: g.pitch, bottom: y + 4, h: y + g.tail[5] + 20 };
  }
  const n = used.map(i => rows.filter(r => r.item === i).length), avail = g.bottom - g.top - g.gap * (used.length - 1);
  let pitch = Math.min(g.pmax, avail / rows.length);
  for (let k = 0; k < 3; k++) pitch = Math.min(g.pmax, (avail - n.reduce((a, m) => a + Math.max(0, 32 - m * pitch), 0)) / rows.length);
  let y = g.top;
  used.forEach((item, k) => {
    if (k) y += g.gap;
    gy[item] = y;
    const y0 = y;
    rows.filter(r => r.item === item).forEach(r => { ys[r.i] = y; y += pitch; });
    y = Math.max(y, y0 + 32);  // room for the work item's two-line name
  });
  return { ys, gy, pitch, bottom: y, h: g.h };
}
/* The y of each forecast within its row, from the row's centre: readers above, theories below, closer together when the
   row is short. */
function offs(r, pitch) {
  const n = r.fc.length, sp = Math.min(5.2, pitch * .74 / (n + .8)), tot = (n - 1 + .8) * sp;
  return r.fc.map((x, j) => -tot / 2 + j * sp + (x.reader ? 0 : .8 * sp));
}

const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z, cy) {
  const X = x - g.cx, Y = y - cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, cy + y1 * k];
}
function slab(g, h, z) {
  const x0 = g.a0, y0 = g.a0 - (g.phone ? 0 : 6), x1 = g.w - g.a0, y1 = h - g.a0, r = g.r, p = [], cy = h / 2;
  const corner = (cx, cyy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cyy + r * Math.sin((a0 + 15 * i) * RAD), z, cy)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}

/* The picture, built once per layout. Everything on the plate sits in one group #face; the sway moves the plate in
   perspective and the face with it by a shift and a scale, so words never tilt. */
function build() {
  const g = S.g = geo(), svg = $("svg"), fs = g.fs, sm = g.phone ? 17 : 12.5;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const T = (id, cls, size, anchor, text) => `<text${id ? ` id="${id}"` : ""} class="${cls}" font-size="${size}"${anchor ? ` text-anchor="${anchor}"` : ""}>${text || ""}</text>`;
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" id="glow" fill="url(#atmo)"/><rect class="shade" id="shade" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/><ellipse class="spec" id="shine" fill="url(#spec)"/>` +
    `<g id="face"><g class="read">` +
    T("big", "big", g.big[2]) + g.l.map((_, k) => T("l" + k, k ? "l2" : "l1", g.phone ? 17 : k ? 14 : 16.5)).join("") +
    (g.phone ? "" : `<line class="vrule" x1="${g.vr}" x2="${g.vr}" y1="36" y2="184"/>` +
      T("ccap", "ccap", 14, "", "Targets reported") + T("cnum", "cnum", 40) + T("cname", "cname", 14.5) + T("cci", "cci", 14)) + `</g>` +
    `<g class="frame"><rect class="band" id="band"/><path class="grid" id="grid"/><line class="zero" id="zero"/><path class="sep" id="sep"/>` +
    TICKS.map(v => T("tk" + v, "tick", sm, "middle", (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v))).join("") +
    T("vt", "ctitle", sm, g.phone ? "end" : "", "Reported") +
    ITEMS.map((it, k) => `<g id="g${k}">` + (g.phone ? T("ga" + k, "gname", fs, "", esc(C.groups[it].join(" ")))
      : T("ga" + k, "gname", fs, "", esc(C.groups[it][0])) + T("gb" + k, "gname", fs, "", esc(C.groups[it][1]))) + `</g>`).join("") +
    `<g id="key"><line class="iv rd" id="ki0"/><circle class="pt rd" id="kp0" r="3"/>${T("kt0", "klab", sm, "", "Reader, no theory")}` +
    `<line class="iv th" id="ki1"/><circle class="pt th" id="kp1" r="3"/>${T("kt1", "klab", sm, "", "Theory")}` +
    `<circle class="pt th win" id="kp2" r="3"/>${T("kt2", "klab", sm, "", "Theory nearer than both readers")}` +
    `<line class="mbar" id="km"/>${T("kt3", "klab", sm, "", "Reported number")}</g>` +
    T("note", "note", sm, "", "") + (g.phone ? T("note2", "note", sm, "", "") : "") + `</g>` +
    `<rect class="selbox" id="selbox" rx="6" style="display:none"/><g class="marks">` +
    ROWS.map(r => `<g id="r${r.i}" style="display:none">` + T("lb" + r.i, "lab", fs, g.phone ? "" : "end", esc(r.label)) +
      T("vl" + r.i, r.m == null ? "nv" : "val", r.m == null ? sm : fs + .5, g.phone ? "end" : "", r.m == null ? "not reported yet" : fv(r.m)) +
      r.fc.map((x, j) => `<line class="iv ${x.reader ? "rd" : "th"}" id="i${r.i}_${j}"/><circle class="pt ${x.reader ? "rd" : "th"}" id="p${r.i}_${j}"/>`).join("") +
      `<path class="far" id="fa${r.i}"/>` +
      (r.m == null ? "" : `<line class="mglow" id="mg${r.i}"/><line class="mbar" id="mb${r.i}"/><circle class="ripple" id="rp${r.i}" r="0"/>`) + `</g>`).join("") +
    `</g><g class="rows" role="group" aria-label="The targets of this view. Arrow keys move between them, Enter opens one.">` +
    ROWS.map(r => `<rect class="hit" id="h${r.i}" data-row="${r.i}" tabindex="-1" role="button" rx="6" style="display:none"/>`).join("") + `</g></g>`;
  S.el = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  S.txt = {};
  ROWS.forEach(r => { r.won = false; });
}
const setText = (id, v) => { if (S.txt[id] !== v) S.el[id].textContent = S.txt[id] = v; };
const at = (el, x, y) => { el.setAttribute("x", f(x)); el.setAttribute("y", f(y)); };
const ln = (el, x1, y1, x2, y2) => { el.setAttribute("x1", f(x1)); el.setAttribute("y1", f(y1)); el.setAttribute("x2", f(x2)); el.setAttribute("y2", f(y2)); };

/* A change of state: every row gets a target (its row, shown or not), reached over 750 ms, rows starting a few ms apart
   from top to bottom. A reported number arrives when its row appears; on Landed every reported number rings once. */
function target(s, now, entrance) {
  const L = layout(s), quick = still.matches;
  let n = 0;
  ROWS.forEach(r => {
    const show = member(r, s), y = show ? L.ys[r.i] : r.cur.y;
    const to = show ? { y, op: 1, p: L.pitch } : { ...r.cur, op: 0 };
    const fresh = show && !r.cur.op;
    if (fresh) Object.assign(r.cur, { y, p: L.pitch });
    r.from = { ...r.cur }; r.to = to; r.show = show;
    r.dur = show ? 750 : 280;
    r.t0 = quick ? -1e9 : !show ? now : now + (entrance ? 26 : 12) * n + (entrance ? 500 : fresh ? 200 : 0);
    if (r.m != null) {
      if (!show) { r.arr = 1e12; r.won = false; }
      else if (fresh || entrance) r.arr = quick ? -1e9 : now + (entrance ? 1100 + 90 * n : 650 + 40 * n);
      else if (s === 1) r.rip = quick ? -1e9 : now + 350 + 70 * n;
    }
    if (show) n++;
  });
  ITEMS.forEach((it, k) => {
    const G = S.groups[k], y = L.gy[it];
    G.from = { y: G.y, op: G.op }; G.to = { y: y ?? G.y, op: y == null ? 0 : 1 };
    if (y != null && !G.op) G.from.y = y;
    G.t0 = quick ? -1e9 : now + (entrance ? 450 : 0);
  });
  S.hfrom = S.h ?? L.h; S.hto = L.h; S.ht0 = quick ? -1e9 : now;
  S.bfrom = S.L ? S.bnow : L.bottom;
  S.L = L;
  const goal = s === 2 ? [C.counts.open, 0] : [C.counts.theory[1], C.counts.theory[0]];
  const start = S.nums && !entrance ? S.nums.now : entrance ? [0, goal[1]] : goal;
  S.nums = { from: start, to: goal, now: start, t0: quick ? -1e9 : now + (entrance ? 1100 : 0) };
  readText(s);
}
function readText(s) {
  const lines = C.read[S.g.phone ? "phone" : "desk"][s];
  S.g.l.forEach((_, k) => setText("l" + k, lines[k] || ""));
  if (!S.g.phone) {
    setText("cnum", `${C.counts.landed} of ${C.counts.targets}`);
    setText("cname", `${C.counts.open} not reported yet`);
    setText("cci", `Last scored at ${hm(C.last)}`);
  }
  setText("note", S.g.phone ? "Each row on its own scale: 0 is the readers'" : "Each row on its own scale: 0 is the readers' average forecast, ±1 the average edge of their 90 % intervals.");
  if (S.g.phone) setText("note2", "average forecast, ±1 the edge of their intervals.");
}

/* Every frame: the sway, the plate, and whatever is still moving. */
function place(now) {
  const g = S.g, E = S.el;
  const h = S.h = mix(S.hfrom, S.hto, ease(clamp((now - S.ht0) / 800, 0, 1))), cy = h / 2;
  if (g.phone) $("svg").setAttribute("viewBox", `0 0 ${g.w} ${f(h)}`);
  else if (!S.vb) { $("svg").setAttribute("viewBox", `0 0 ${g.w} ${g.h}`); S.vb = 1; }
  E.back.setAttribute("d", slab(g, h, -g.deep));
  E.plate.setAttribute("d", slab(g, h, 0));
  const aw = g.w - 2 * g.a0, ah = h - 2 * g.a0;
  E.glow.setAttribute("cx", g.cx); E.glow.setAttribute("cy", f(cy)); E.glow.setAttribute("rx", f(aw * .8)); E.glow.setAttribute("ry", f(Math.min(ah * .9, aw * 1.3)));
  E.shade.setAttribute("x", f(g.a0 + aw * .012)); E.shade.setAttribute("y", f(g.a0 + ah * .03)); E.shade.setAttribute("width", f(aw)); E.shade.setAttribute("height", f(ah)); E.shade.setAttribute("rx", g.r);
  const spx = g.a0 + aw * .3, spy = g.a0 + Math.min(ah * .2, 180);
  E.shine.setAttribute("cx", f(spx)); E.shine.setAttribute("cy", f(spy)); E.shine.setAttribute("rx", f(aw * .26)); E.shine.setAttribute("ry", f(Math.min(ah * .16, 130)));
  const c = proj(g, g.cx, cy, 0, cy), r1 = proj(g, g.cx + 100, cy, 0, cy), d1 = proj(g, g.cx, cy + 100, 0, cy);
  const kx = (r1[0] - c[0]) / 100, ky = (d1[1] - c[1]) / 100;
  E.face.setAttribute("transform", `matrix(${kx.toFixed(4)} 0 0 ${ky.toFixed(4)} ${f(c[0] - kx * g.cx)} ${f(c[1] - ky * cy)})`);
  if (S.moving || S.first) frameMarks(now);
  else if (!still.matches) replay(now);
  const p = ease(clamp((now - S.nums.t0) / 900, 0, 1));
  S.nums.now = S.nums.from.map((v, i) => mix(v, S.nums.to[i], p));
  const [a, b] = S.nums.now;
  setText("big", S.s === 2 ? `${Math.round(a)}` : `${Math.round(a)} of ${Math.round(b)}`);
}
function frameMarks(now) {
  const g = S.g, E = S.el, L = S.L;
  let moving = false;
  const tw = (o, d) => ease(clamp((now - o.t0) / d, 0, 1));
  const bottom = S.bnow = mix(S.bfrom, L.bottom, ease(clamp((now - S.ht0) / 800, 0, 1)));
  if (now - S.ht0 < 800) moving = true;
  // The readout, the band of the readers' intervals, the grid, the ticks, the key.
  at(E.big, g.big[0] - 3, g.big[1]);
  g.l.forEach((y, k) => at(E["l" + k], g.big[0], y));
  if (!g.phone) { at(E.ccap, g.con[0], g.con[1]); at(E.cnum, g.con[0] - 2, g.con[2]); at(E.cname, g.con[0], g.con[3]); at(E.cci, g.con[0], g.con[4]); }
  const yt = g.ref + 8, yb = bottom + 4, b0 = sx(g, -1), b1 = sx(g, 1);
  E.band.setAttribute("x", f(b0)); E.band.setAttribute("width", f(b1 - b0)); E.band.setAttribute("y", f(yt)); E.band.setAttribute("height", f(yb - yt));
  E.grid.setAttribute("d", [-2, 2].map(v => `M${f(sx(g, v))} ${f(yt)}V${f(yb)}`).join(""));
  ln(E.zero, sx(g, 0), yt, sx(g, 0), yb);
  TICKS.forEach(v => at(E["tk" + v], sx(g, v), g.ref));
  at(E.vt, g.phone ? g.vx : g.vx, g.ref);
  const ky = g.phone ? yb + g.tail[0] : g.key, kx = g.phone ? [g.gx + 6, g.gx + 220, g.gx + 6, g.gx + 6] : [g.gx + 6, 230, 330, 600];
  const kyy = g.phone ? [ky, ky, ky + 30, ky + 60] : [ky, ky, ky, ky];
  ln(E.ki0, kx[0] - 7, kyy[0] - 4.5, kx[0] + 7, kyy[0] - 4.5); E.kp0.setAttribute("cx", f(kx[0])); E.kp0.setAttribute("cy", f(kyy[0] - 4.5));
  ln(E.ki1, kx[1] - 7, kyy[1] - 4.5, kx[1] + 7, kyy[1] - 4.5); E.kp1.setAttribute("cx", f(kx[1])); E.kp1.setAttribute("cy", f(kyy[1] - 4.5));
  E.kp2.setAttribute("cx", f(kx[2])); E.kp2.setAttribute("cy", f(kyy[2] - 4.5));
  ln(E.km, kx[3], kyy[3] - 11, kx[3], kyy[3] + 2);
  [0, 1, 2, 3].forEach(k => at(E["kt" + k], kx[k] + (k === 3 ? 9 : 14), kyy[k]));
  if (g.phone) { at(E.note, g.gx, ky + g.tail[2]); at(E.note2, g.gx, ky + g.tail[2] + 24); }
  else at(E.note, g.gx, g.note);
  // The work items' names and the hairlines between them.
  let sep = "";
  const first = ITEMS.findIndex((_, k) => S.groups[k].to && S.groups[k].to.op > 0);
  ITEMS.forEach((it, k) => {
    const G = S.groups[k], p = tw(G, 750);
    G.y = mix(G.from.y, G.to.y, p); G.op = mix(G.from.op, G.to.op, p);
    if (p < 1) moving = true;
    E["g" + k].setAttribute("opacity", G.op.toFixed(2));
    E["g" + k].style.display = G.op < .01 ? "none" : "";
    if (g.phone) {
      at(E["ga" + k], g.gx, G.y);
      if (G.op > .01 && k !== first) sep += `M${g.gx} ${f(G.y - 28)}H${g.vx}`;
    } else {
      const half = L.pitch / 2;
      at(E["ga" + k], g.gx, G.y + half + 4.5);
      at(E["gb" + k], g.gx, G.y + half + 20);
      if (G.op > .01 && k !== first) sep += `M${g.gx} ${f(G.y - g.gap / 2)}H${g.vx + 106}`;
    }
  });
  E.sep.setAttribute("d", sep);
  // The rows.
  const sel = S.open && RID[S.open];
  ROWS.forEach(r => {
    if (!r.to) return;
    const p = tw(r, r.dur || 750), c = r.cur;
    for (const k in r.to) c[k] = mix(r.from[k], r.to[k], p);
    if (p < 1) moving = true;
    const grp = E["r" + r.i], hit = E["h" + r.i];
    if (c.op < .01 && !r.show) { grp.style.display = "none"; hit.style.display = "none"; return; }
    grp.style.display = ""; grp.setAttribute("opacity", c.op.toFixed(2));
    const my = g.phone ? c.y + 34 : c.y + c.p / 2, ly = g.phone ? c.y + 14 : my + 4.4;
    at(E["lb" + r.i], g.phone ? g.gx : g.lx, ly);
    at(E["vl" + r.i], g.vx, g.phone ? my + 6 : ly);
    const o = offs(r, g.phone ? 26 : c.p), rr = g.phone ? 3.2 : clamp(Math.min(5.2, c.p * .74 / (r.fc.length + .8)) * .62, 1.8, 3.3);
    let far = "";
    r.fc.forEach((x, j) => {
      const y = my + o[j], xa = sx(g, x.zl), xb = sx(g, x.zh), xm = sx(g, x.z);
      ln(E[`i${r.i}_${j}`], xa, y, xb, y);
      const pt = E[`p${r.i}_${j}`];
      pt.setAttribute("cx", f(xm)); pt.setAttribute("cy", f(y)); pt.setAttribute("r", f(rr));
      if (x.zl < DOM[0]) far += `M${f(xa + 1)} ${f(y - 2.6)}L${f(xa - 4)} ${f(y)}L${f(xa + 1)} ${f(y + 2.6)}Z`;
      if (x.zh > DOM[1]) far += `M${f(xb - 1)} ${f(y - 2.6)}L${f(xb + 4)} ${f(y)}L${f(xb - 1)} ${f(y + 2.6)}Z`;
    });
    E["fa" + r.i].setAttribute("d", far);
    if (r.m != null) {
      const a = clamp((now - r.arr) / 520, 0, 1), e = ease(a), hh = g.phone ? 10 : clamp(c.p * .4, 5.5, 15), xm = sx(g, r.zm);
      const dy = -(1 - e) * (g.phone ? 26 : Math.max(10, c.p * .8));
      ln(E["mb" + r.i], xm, my - hh + dy, xm, my + hh + dy); ln(E["mg" + r.i], xm, my - hh + dy, xm, my + hh + dy);
      E["mb" + r.i].style.opacity = E["mg" + r.i].style.opacity = e.toFixed(2);
      E["vl" + r.i].style.opacity = e.toFixed(2);
      if (a < 1 && r.show) moving = true;
      const won = a >= .75;
      if (won !== r.won) { r.won = won; r.fc.forEach((x, j) => { if (x.near === "n") E[`p${r.i}_${j}`].classList.toggle("win", won); }); }
      r.bx = xm; r.by = my; r.bh = hh;
      if (ripple(r, now)) moving = true;
    }
    E["lb" + r.i].setAttribute("class", "lab" + (sel === r ? " on" : ""));
    hit.style.display = r.show ? "" : "none";
    if (r.show) {
      const top = g.phone ? c.y - 4 : c.y, hh = g.phone ? g.pitch : c.p;
      hit.setAttribute("x", f(g.gx - 8)); hit.setAttribute("width", f((g.phone ? g.vx + 8 : g.vx + 112) - g.gx + 8));
      hit.setAttribute("y", f(top)); hit.setAttribute("height", f(hh));
      hit.setAttribute("aria-label", `${C.groups[r.item].join(" ")}: ${r.label}. ` + (r.m == null ? "Not reported yet." : `Reported ${fv(r.m)}.`));
    }
    if (sel === r) {
      const sb = E.selbox, top = g.phone ? c.y - 4 : c.y + 1, hh = (g.phone ? g.pitch : c.p) - 2;
      sb.style.display = r.show && c.op > .5 ? "" : "none";
      sb.setAttribute("x", f(g.phone ? g.gx - 8 : 210)); sb.setAttribute("width", f((g.phone ? g.vx + 8 : g.vx + 108) - (g.phone ? g.gx - 8 : 210)));
      sb.setAttribute("y", f(top)); sb.setAttribute("height", f(hh));
    }
  });
  if (!sel) E.selbox.style.display = "none";
  S.moving = moving;
  S.first = false;
}
/* The ring that opens around a reported number once it has landed, and again when it is replayed. */
function ripple(r, now) {
  const el = S.el["rp" + r.i];
  if (!el || still.matches) return false;
  const start = Math.max(r.arr + 520, r.rip), q = (now - start) / 900;
  if (q < 0 || q > 1 || !r.show) { el.setAttribute("r", "0"); return q < 0 && r.show && start < 1e11; }
  el.setAttribute("cx", f(r.bx)); el.setAttribute("cy", f(r.by));
  el.setAttribute("r", f(r.bh * .5 + 16 * ease(q)));
  el.style.opacity = (.6 * (1 - q)).toFixed(2);
  return true;
}
/* The replay: about every 2.6 s one reported number, in the order of the rows, rings again. */
function replay(now) {
  if (!S.rp && now > S.rpNext && !S.open && S.s !== 2) {
    const pool = ROWS.filter(r => r.m != null && r.show);
    if (pool.length) { S.rp = pool[S.rpAt++ % pool.length]; S.rp.rip = now; }
    else S.rpNext = now + 2600;
  }
  if (!S.rp) return;
  if (!ripple(S.rp, now)) { S.rp = null; S.rpNext = now + 1700; }
}

function frame(now) {
  requestAnimationFrame(frame);
  if (now - S.last < 30) return;
  S.last = now;
  S.t = now / 1000;
  if (still.matches) aim(0, 0);
  else {
    V.px += (V.tx - V.px) * .08;
    V.py += (V.ty - V.py) * .08;
    aim(2.4 * Math.sin(S.t * .13) + 2.2 * V.px, 1.1 * Math.sin(S.t * .09) - 1.2 * V.py);
  }
  place(now);
}

/* The control and the address: #<landed|open>/<row or panel>. */
function setState(s, push) {
  if (s === S.s && S.L) return;
  S.s = s;
  if (S.open && RID[S.open] && !member(RID[S.open], s)) S.open = null;  // a row that leaves closes with the address
  if (S.rp) { S.rp = null; }
  target(s, performance.now(), false);
  S.moving = true;
  controls();
  pane();
  address(push);
}
function controls() {
  [...$("switch").children].forEach((b, i) => b.setAttribute("aria-pressed", String(i === S.s)));
  $("hint").textContent = "Click a row for every forecast, its interval and the reported number.";
  $("svg").setAttribute("aria-label", `${STATES[S.s].name} targets. Theory forecasts were nearer the reported number than both readers with no theory in ` +
    `${C.counts.theory[1]} of ${C.counts.theory[0]}; ${C.counts.landed} of ${C.counts.targets} targets are reported.`);
  rovable();
}
function address(push) {
  const parts = [STATES[S.s].id, S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const s = Math.max(0, STATES.findIndex((x, k) => k && parts.includes(x.id)));
  const key = parts.find(x => (RID[x] && member(RID[x], s)) || C.panels.some(p => p[0] === x));
  S.open = key || null;
  if (first) { S.s = s; return; }
  if (s !== S.s) { S.s = s; target(s, performance.now(), false); }
  S.moving = true;
  controls();
  pane();
}

/* The side column: the five panels and two examples, or one target. */
function zoom(r) {  // the row in its own units: every forecast, and the reported number
  const xs = r.fc.flatMap(x => [x.lo, x.hi]).concat(r.m == null ? [] : [r.m]);
  let lo = Math.min(...xs), hi = Math.max(...xs);
  if (hi === lo) { lo -= 1; hi += 1; }
  const pad = (hi - lo) * .04, X = v => 8 + 324 * (v - lo + pad) / (hi - lo + 2 * pad), H = 26 + 9 * r.fc.length;
  let s = `<svg class="zoom" viewBox="0 0 340 ${H}" aria-hidden="true"><path class="z-ax" d="M8 ${H - 13}H332"/>`;
  r.fc.forEach((x, j) => {
    const y = 16 + 9 * j, k = x.reader ? "rd" : "th";
    s += `<path class="z-${k}" d="M${f(X(x.lo))} ${y}H${f(X(x.hi))}"/><circle class="z-p${k}${x.near === "n" ? " win" : ""}" cx="${f(X(x.v))}" cy="${y}" r="2.8"/>`;
  });
  if (r.m != null) s += `<path class="z-me" d="M${f(X(r.m))} 8V${H - 13}"/><text class="z-mt" x="${f(X(r.m))}" y="5" text-anchor="middle">${fv(r.m)}</text>`;
  s += `<text class="z-t" x="8" y="${H}">${fv(Math.round(lo))}</text><text class="z-t" x="332" y="${H}" text-anchor="end">${fv(Math.round(hi))}</text>`;
  return s + "</svg>";
}
const VERD = { n: "nearer than both readers", t: "as near as the nearer reader", f: "farther than a reader" };
function fcItem(r, x) {
  const name = esc(x.name), who = x.reader ? "no theory" : "theory " + esc(x.who);
  let res = "";
  if (r.m != null) {
    res = ` · ${x.lo <= r.m && r.m <= x.hi ? "inside" : "outside"} its interval` + (x.near ? ` · ${VERD[x.near]}` : "") +
      (x.g != null ? ` · ${x.g >= 0 ? "+" : "−"}${Math.abs(x.g).toFixed(2)} nats` : "");
  }
  return `<li class="${x.reader ? "" : x.near === "n" ? "th w" : "th"}"><div class="fn"><b>${name}</b><span>${who}</span></div>` +
    `<div class="pv">Forecast <b>${fv(x.v)}</b> (${fv(x.lo)} to ${fv(x.hi)})${res}</div>` +
    (x.reader ? "" : `<div class="pm">${esc(C.theory[x.run + "/" + x.who])}</div>`) +
    `<div class="pr">Its reason: ${esc(x.why)}</div></li>`;
}
function rowPane(r) {
  let h = `<div class="dhead"><h2><span>${esc(C.groups[r.item].join(" "))}</span>${esc(r.label)}</h2><button class="close" data-open="">Close</button></div>`;
  if (C.cases[r.id]) h += `<p class="case">${esc(C.cases[r.id])}</p>`;
  h += r.m != null
    ? `<div class="share"><b>${fv(r.m)}</b><span>${esc(r.unit)}<br>reported in ${esc(r.res)} at ${hm(r.posted)}</span></div>` +
      `<p class="quote">From the result: <b data-math>“${esc(r.quote)}”</b></p>`
    : `<div class="share"><b class="open">Not reported yet</b><span>${esc(r.unit)}<br>no result reports it (last scored ${hm(C.last)})</span></div>`;
  h += zoom(r);
  h += `<ul class="facts"><li>Target, as the forecasters read it: ${esc(r.what)}</li><li>Work item <b>${esc(r.item)}</b>. Grey: readers with no theory; blue: theories, filled when nearer than both readers.</li></ul>`;
  const runs = [...new Set(r.fc.map(x => x.run))];
  runs.forEach(run => {
    const R = RUN[run], d = r.m != null ? mins(R[3], r.posted) : null;
    const when = d == null ? "" : `, ${Math.abs(Math.round(d))} min ${d > 0 ? "before" : "after"} the result`;
    h += `<h3>${"Run " + Number(run.slice(4))}<span>Board read at ${hm(R[1])}; forecasts committed at ${hm(R[3])}${when} (${esc(R[2])})</span></h3>` +
      `<ul class="fcs">${r.fc.filter(x => x.run === run).map(x => fcItem(r, x)).join("")}</ul>`;
  });
  return h + `<div class="steps"><button data-step="-1">‹ Previous target</button><button data-step="1">Next target ›</button></div>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open), r = S.open && RID[S.open];
  $("pane").innerHTML = r ? rowPane(r)
    : p ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>` +
      `<ul class="more ex">${C.examples.map(x => `<li><button data-open="${x[0]}">${esc(x[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
  S.moving = true;
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ block: "start", behavior: still.matches ? "auto" : "smooth" }); };
function open(key) {
  const was = S.open;
  if (key && RID[key] && !member(RID[key], S.s)) { S.s = 0; target(0, performance.now(), false); controls(); }
  S.open = key || null;
  S.moving = true;
  address(true);
  pane();
  if (key && RID[key]) rove(RID[key]);
  const back = !key && was && RID[was] ? S.el["h" + RID[was].i] : null;
  const to = key ? $("pane").querySelector(".close") : back || $("pane").querySelector(`[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  if (key) show();
}
/* The rows are one stop in the tab order; the arrow keys move along them from top to bottom. */
const visible = () => ROWS.filter(r => member(r, S.s));
function rove(r) {
  ROWS.forEach(o => S.el["h" + o.i].setAttribute("tabindex", "-1"));
  S.rove = r.i;
  S.el["h" + r.i].setAttribute("tabindex", "0");
}
function rovable() {
  const vis = visible();
  rove(vis.find(r => r.i === S.rove) || vis[0]);
}

$("switch").innerHTML = STATES.map((st, i) => `<button data-state="${i}" aria-pressed="false">${st.name}<span>${[C.counts.targets, C.counts.landed, C.counts.open][i]}</span></button>`).join("");
$("switch").addEventListener("click", e => { const b = e.target.closest("[data-state]"); if (b) setState(Number(b.dataset.state), true); });
document.addEventListener("click", e => {
  const o = e.target.closest("[data-open]"), st = e.target.closest("[data-step]");
  if (o) open(o.dataset.open);
  if (st) {
    const vis = visible(), k = vis.indexOf(RID[S.open]), next = vis[(k + Number(st.dataset.step) + vis.length) % vis.length];
    open(next.id);
    $("pane").querySelector(`[data-step="${st.dataset.step}"]`).focus({ preventScroll: true });
  }
});
const svg = $("svg");
svg.addEventListener("click", e => { const h = e.target.closest(".hit"); if (h) open(ROWS[Number(h.dataset.row)].id); });
svg.addEventListener("keydown", e => {
  const h = e.target.closest(".hit");
  if (!h) return;
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(ROWS[Number(h.dataset.row)].id); return; }
  const step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
  if (!step) return;
  e.preventDefault();
  const vis = visible(), k = vis.findIndex(r => r.i === Number(h.dataset.row)), r = vis[(k + step + vis.length) % vis.length];
  rove(r);
  S.el["h" + r.i].focus();
});
document.addEventListener("keydown", e => { if (e.key === "Escape" && S.open) open(""); });
addEventListener("popstate", () => fromHash(false));
addEventListener("hashchange", () => fromHash(false));
narrow.addEventListener("change", () => { build(); S.gw = null; S.vb = 0; S.h = null; S.L = null; target(S.s, -1e9, false); S.first = true; controls(); });
still.addEventListener("change", () => { target(S.s, performance.now(), false); S.moving = true; });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1;
  V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
aim(0, 0);
build();
fromHash(true);
/* On load the forecasts are drawn first; then each reported number drops onto its row and the large number counts. */
target(S.s, performance.now(), !still.matches);
S.first = true; S.moving = true;
S.rpNext = performance.now() + 5200;
controls();
pane();
place(performance.now());
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
"""


def _config():
    """What the page's script reads: the rows with their forecasts, the words and the counts."""
    rows = []
    for r in ROWS:
        fc = [{"run": run, "tid": tid, "who": who, "name": _name(run, who), "reader": who in READERS, "v": v, "lo": lo,
               "hi": hi, "g": g, "why": why, "near": n} for (run, tid, who, v, lo, hi, g, why), n in zip(r[9], _near(r))]
        rows.append({"id": r[0], "item": r[1], "label": r[2], "unit": r[3], "what": r[4], "m": r[5], "res": r[6],
                     "posted": r[7], "quote": r[8], "fc": fc})
    return {"problem": PROBLEM, "line": LINE, "panels": PANELS, "examples": EXAMPLES, "cases": CASES, "rows": rows,
            "runs": RUNS, "theory": _STATEMENT, "groups": {i: GROUPS.get(i, [i, ""]) for i in {r[1] for r in ROWS}},
            "counts": COUNTS, "read": READ, "last": _last}


PAGE = PAGE.replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps(_config(), ensure_ascii=False).replace("</", "<\\/"))

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's picture, reduced.
# A glass slab with four rows: a grey reader interval and a blue theory interval each; on two rows a bright bar drops
# onto the row now and then, and one theory dot fills when its bar lands.
ICON = r"""(kit, t, tilt) => {
  const th = 5, w = th / 2, k = Number(t) || 0, X = z => 12 * z, n = v => v.toFixed(1);
  const seg = (u0, v0, u1, v1, c, sw, o) => { const p = kit.at(u0, v0, w), q = kit.at(u1, v1, w);
    return `<line x1="${n(p[0])}" y1="${n(p[1])}" x2="${n(q[0])}" y2="${n(q[1])}" stroke="${c}" stroke-width="${sw}" stroke-linecap="round" opacity="${o}"/>`; };
  const dot = (u, v, fill, r) => { const p = kit.at(u, v, w); return `<circle cx="${n(p[0])}" cy="${n(p[1])}" r="${r}" fill="${fill}" stroke="${kit.token.blue}" stroke-width="1"/>`; };
  let out = kit.slab(44, 38, th);
  [[0, .9, 1.1], [.1, -1.1, -.3], [-.1, .4, null], [0, -.5, null]].forEach(([rz, tz, mz], i) => {
    const v = -24 + i * 15, e = Math.min(1, ((k * .45 + i * .8) % 3) / .5), lit = mz != null && e >= 1 && Math.abs(tz - mz) < .5;
    out += seg(X(rz - 1), v - 2.6, X(rz + 1), v - 2.6, kit.token.mute, 1.4, .7);
    out += seg(X(tz - 1), v + 2.6, X(tz + 1), v + 2.6, kit.token.blue, 1.4, .6) + dot(X(tz), v + 2.6, lit ? kit.token.blue : kit.token.paper, 2.2);
    if (mz != null) out += seg(X(mz), v - 6 - (1 - e) * 7, X(mz), v + 6 - (1 - e) * 7, kit.token.ink, 1.8, e.toFixed(2));
  });
  return out;
}"""

if __name__ == "__main__":  # run from the repository root
    runs, theories, rows = _build()
    counts = _count(runs, rows)
    if sys.argv[1:] == ["--write"]:
        src = open(__file__).read()
        lines = lambda xs: "[\n" + "".join("    " + repr(x) + ",\n" for x in xs) + "]"
        for name, body in (("COUNTS", repr(counts)), ("RUNS", lines(runs)), ("THEORIES", lines(theories)), ("ROWS", lines(rows))):
            start = src.index("\n" + name + " = ") + 1
            src = src[:start] + name + " = " + body + src[src.index("\n\n", start):]
        open(__file__, "w").write(src)
        sys.exit(f"wrote {len(runs)} runs, {len(theories)} theories, {len(rows)} rows: {counts['theory']}")
    assert (RUNS, THEORIES, ROWS) == (runs, theories, rows), "RUNS, THEORIES or ROWS differ from the run folders: run with --write"
    assert COUNTS == counts, "COUNTS differ from the run folders: run with --write"
    # Against the forecast tool's own tables: per run and forecaster, the forecasts scored, inside their interval, outside
    # both readers' intervals and of those inside (scores.json), from this page's rows.
    for run in [r[0] for r in RUNS if r[5]]:
        sc = json.load(open(F + run + "/scores.json"))
        measured = {m["id"] for m in sc["measured"] if m["value"] is not None}
        for row in ROWS:
            ids = {f[1] for f in row[9] if f[0] == run}
            if row[5] is not None:
                assert ids <= measured, f"{run} scores.json lacks {sorted(ids - measured)}: run forecast.py score {F}{run}"
        for who, p in sc["forecasters"].items():
            mine = [(row, f) for row in ROWS if row[5] is not None for f in row[9] if f[0] == run and f[2] == who]
            rd = lambda row, f: [x for x in row[9] if x[0] == run and x[1] == f[1] and x[2] in READERS]
            apart = [(row, f) for row, f in mine if all(not x[4] <= f[3] <= x[5] for x in rd(row, f))]
            got = [len(mine), sum(f[4] <= row[5] <= f[5] for row, f in mine), len(apart), sum(f[4] <= row[5] <= f[5] for row, f in apart)]
            assert got == [p["scored"], p["inside"], p["disagree"], p["disagree_inside"]], (run, who, got)
            assert abs(sum(f[6] for row, f in mine) - p["total_gain"]) < .01, (run, who)
    # The sentences of the page, against the board results they repeat (result-05cf4d, result-564441).
    assert (_t1[3], _r1, _c1[5], _c1[6]) == (455, [440, 445], 456, "result-95a4dc"), (_t1, _r1, _c1[5])
    assert _t2[3] == 205 and not _t2[4] <= _c2[5] <= _t2[5]
    missing = sorted(k for r in ROWS for k in {f"{f[0]}/{f[1]}" for f in r[9]} if k not in LABELS)
    if missing:
        print("no label in _SAME (the first words of the description are shown):", ", ".join(missing))
    unnamed = sorted({f"{k}" for k, who, _ in THEORIES if not (NAMES.get(who) or NAMES.get(k) or _ENGINE_NAMES.get(who))})
    if unnamed:
        print("no short name in NAMES:", ", ".join(unnamed))
    if {r[1] for r in ROWS} - set(GROUPS):
        print("no name in GROUPS:", ", ".join(sorted({r[1] for r in ROWS} - set(GROUPS))))
    print(f"RUNS, THEORIES, ROWS and COUNTS match the run folders; theory nearer than both readers {TH[1]} of {TH[0]}, "
          f"{COUNTS['landed']} of {COUNTS['targets']} targets reported")
