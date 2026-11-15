"""The theory engine's theories against two readers with no theory, on numbers neither had seen: about half nearer, no better.

The page of one finding, served at /finding/theories-on-trial (view.py serves every tools/finding_<slug>.py) and reached
from its tile on /findings, which ICON draws. The subject is the team's theory engine (.claude/skills/theory/SKILL.md,
studies/theory/README.md): in each round, agents wrote theories of why RL beats the base model, and each theory filed
numeric predictions with intervals before the number was computed; two readers with no theory (two model runs given the
same board items and the same question) predicted the same numbers. The picture is one lit plate. On it every
prediction is one mark: its interval scaled to one height (a short vertical line on a faint band) and the measured
number as a dot, so a dot inside the band landed inside the interval. A dot is blue when the theory's forecast was
nearer the measured number than the average of the two readers' forecasts, a ring when the readers' was nearer or
equal, grey when no reader predicted it. Marks are grouped by theory; refuted theories, and theories that lost to their
rival, are dimmed and struck; "no gain" (no better than the readers) is a fate of its own and is not struck. The control
steps through the rounds (1 to the last, and All): marks travel from one strip per round to one row per theory, with
its short name (NAMES) at the left and its fate at the end, and the large number counts. A click on a theory shows its
mechanism, each prediction (target, forecast, measured, readers), its fate and its duel in the side column. Address:
/finding/theories-on-trial#<round, or nothing for All>/<panel or <round>.<theory>>.
The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md).

    uv run tools/finding_theories_on_trial.py           checks DATA, THEORIES and PREDS against the round files
    uv run tools/finding_theories_on_trial.py --write   rewrites DATA's counts, THEORIES and PREDS from the round files

A new round: once studies/theory/results/engine/round-<nn>/ and its README section "## Round <nn> (" are on main, run
--write, then the check. The rounds are the round-<nn> folders that exist; the control, the per-round list, LINE and the
totals in PANELS follow from the written counts. Add the new theories' short names to NAMES (the check lists those
missing; until then the first words of the statement are shown). A round whose files change layout (the engine
version in its run.json) may need _build adapted: the check compares computed, inside and filed with metrics_v4.json.
"""
import json
import os
import re
import subprocess
import sys

E = "studies/theory/results/engine/"

# Every number is computed from the files named here by _build() and _count() at the end of this file. None is typed
# from memory. The deployed site ships only tools/*.py, so the copy below is a literal; run this file to compare.
DATA = {
    "sources": {
        "rounds": E + "round-<nn>, one folder per round",
        "round 1": E + "round-01/metrics.json, predictions_measured.json (the 7 interval predictions held-out items measured)",
        "rounds 2-3": E + "round-0<n>/metrics_v2.json, metrics_v3.json, targets.jsonl, reviews/",
        "rounds 4 on": E + "round-<nn>/metrics_v4.json (predictions), metrics_v5.json (duels), tests_blind.jsonl, theories/",
        "gpu": E + "round-05/experiments.json, experiments_measured.json; studies/theory/results/experiments/selfopen-01/",
        "statements": "studies/theory/README.md (the Statement and What decided it columns)",
        "names": "NAMES below, a few words of each statement",
    },
}

TITLE = "Theories on trial"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Do our theories predict unseen numbers better than readers with no theory?"


def _load(p):
    return json.load(open(E + p))


def _jsonl(p):
    return [json.loads(line) for line in open(E + p) if line.strip()]


def _cut(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1].rstrip(" ,;:") + "…"


def _sentence(s, n=260):  # the first sentence of a statement
    s = " ".join(str(s).split())
    m = re.search(r"(?<=[a-z0-9)%'])\.\s+(?=[A-Z])", s[40:])
    return _cut(s[:40 + m.start() + 1] if m else s, n)


def _readme():  # the README's table rows by section: {section: {first cell: cells}}
    out, sec = {}, None
    for line in open("studies/theory/README.md"):
        if line.startswith("#"):
            sec = line.strip("# \n")
        elif line.startswith("| ") and sec:
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            out.setdefault(sec, {}).setdefault(cells[0], cells)
    return out


def _build():
    """THEORIES and PREDS from the round files; run from the repository root.

    THEORIES: [key "<round>.<theory>", round, theory id, statement, state, fate, why, review, duel, gpu]
      fate: s survives or passed, r refuted, l lost to its rival, n no gain over the readers, o anything else (failed,
            untested)
      duel: [rival's first sentence, total gain in nats, state, tests that separate, tests computed,
             tests [[experiment, measured, theory [v, lo, hi], rival [v, lo, hi], gain]]]
      gpu: [board item, measured, n, measured interval, theory [v, lo, hi], rival [v, lo, hi], rival id, artifact]
    PREDS: [key, label, target, unit, forecast, low, high, measured or None, mark, readers [[v, lo, hi] or [v]],
            gain in nats or None, note]
      mark: w the theory's forecast is nearer the measured number than the readers' average, t a tie, l the readers'
            is nearer, c carried (compared with the theory it replaced, not with readers), x not computed; a trailing u
            marks an unexpected win (inside its interval while every reader's centre lies outside it)
      note: n outside but within the measurement's noise, c:[v, lo, hi] the replaced theory's prediction, x:<why>
    """
    rounds = sorted(int(d[-2:]) for d in os.listdir(E) if re.fullmatch(r"round-\d\d", d))
    rm = _readme()
    rsec = {int(m.group(1)): v for k, v in rm.items() if (m := re.match(r"Round (\d\d) \(", k))}
    tab = rm["Theories"]

    def statement(name):  # the newest README row of the theory that is not a stub of a carried theory
        rows = [rsec[r][name][1] for r in sorted(rsec, reverse=True) if r >= 4 and name in rsec[r]] + \
               ([tab[name][1]] if name in tab else [])
        full = [x for x in rows if "carried" not in x]
        return full[0] if full else rows[0].replace(" (carried)", "")
    theories, preds = [], []

    # Round 1: the theories' own interval predictions that the held-out items measured.
    m1 = _load("round-01/metrics.json")
    for t, v in m1["theories"].items():
        if t == "planted":  # the control: every effect of a real theory reversed
            continue
        a, b = v["vs_null_1"], v["vs_null_2"]
        why = (f"A forecaster given this theory was nearer than reader 1 on {a['closer']} of the {m1['targets']} held-out "
               f"numbers and farther on {a['farther']}; against reader 2, {b['closer']} and {b['farther']}. A planted "
               "theory with every effect reversed scored the same, so no theory beat the readers.")
        theories.append([f"1.{t}", 1, t, statement("r1-" + t), "did not beat the readers", "o", why, "", None, None])
    for x in _load("round-01/predictions_measured.json"):
        preds.append([f"1.{x['theory']}", x["targets"][0], _cut(x["experiment"], 170), x["unit"], x["predicted"],
                      x["low"], x["high"], x["measured"], "", [[x["null_1"]], [x["null_2"]]], None, ""])

    # Rounds 2 and 3: claims on numbers that other agents posted to the board after the cutoff.
    for rd, f in ((2, "round-02/metrics_v2.json"), (3, "round-03/metrics_v3.json")):
        tg = {x["id"]: x for x in _jsonl(f"round-0{rd}/targets.jsonl")}
        for t, v in _load(f)["theories"].items():
            path = f"round-0{rd}/reviews/{t}.json"
            rv = _load(path) if os.path.exists(E + path) else {}
            verdict = str(rv.get("verdict", ""))
            if rd == 2:
                why = (f"Round 2 score: {v['wins']} wins and {v['losses']} losses on the claims where both readers' "
                       f"numbers lay outside its interval, of {v['claims']} claims.")
            else:
                why = (f"Round 3 score: {v['total_gain']:+.2f} nats against the readers over {v['claims']} claims"
                       + (" (90 % interval reaches 0)." if v["claims"] and v["interval"][0] < 0 < v["interval"][1] else "."))
            fate = "r" if verdict.startswith("refuted") else "s" if v["state"] == "passes" else "o"
            state = "refuted by its review" if fate == "r" else {"passes": "passed the score", "fails": "failed the score"}[v["state"]]
            theories.append([f"{rd}.{t}", rd, t, statement(t), state, fate, why,
                             _cut(rv.get("verdict_sentence") or verdict, 420), None, None])
            for x in v["rows"]:
                rdrs = [[n] if not isinstance(n, dict) else [n["value"], n["low"], n["high"]] for n in x["nulls"]]
                preds.append([f"{rd}.{t}", x["id"], _cut(tg[x["id"]]["what"], 170), tg[x["id"]]["unit"], x["value"],
                              x["low"], x["high"], x["measured"], "", rdrs, x.get("gain"), ""])

    # Rounds 4 on: offline predictions, computed from stored per-problem rows by scripts written before any row was
    # read. A carried rival's record is its duel tests of the round it came from, compared with the theory it replaced,
    # when the engine counts them (round 6); from round 7 (engine 7.1) the engine files none for a carried theory.
    gpu_m = {x["id"]: x for x in _load("round-05/experiments_measured.json")}
    gpu = []
    for e in _load("round-05/experiments.json")["experiments"]:
        if e["id"] in gpu_m:
            g, p, o = gpu_m[e["id"]], e["proposer_prediction"], e["other_prediction"]
            gpu.append([e["proposer"], e["other"], [g["item"], g["measured"], g["n"], g["interval"],
                        [p["value"], p["low"], p["high"]], [o["value"], o["low"], o["high"]], e["other"], g["artifact"]]])
    for rd in [r for r in rounds if r >= 4]:
        v4 = _load(f"round-{rd:02d}/metrics_v4.json")["theories"]
        v5 = _load(f"round-{rd:02d}/metrics_v5.json")["theories"]
        blind = {x["id"]: x for x in _jsonl(f"round-{rd:02d}/tests_blind.jsonl")}
        for t, v in v4.items():
            duel = None
            if t in v5:
                d = v5[t]
                duel = [_sentence(d["rival"]), d["total_gain"], d["state"], d["separating"], d["computed"],
                        [[_cut(r["experiment"], 160), r["measured"], [r["theory"][k] for k in ("value", "low", "high")],
                          [r["rival"][k] for k in ("value", "low", "high")], r["gain"]] for r in d["rows"]]]
            st = v["state"]
            fate = ("r" if st == "refuted" else "l" if duel and duel[2] == "loses to rival" else "s" if st == "survives"
                    else "n" if st == "no gain" else "o")
            state = {"r": "refuted", "l": "lost to its rival", "s": "survives", "n": "no gain"}.get(fate, st)
            row = rsec.get(rd, {}).get(t) if rd >= 5 else None
            why = row[-1] if row else v["reasons"][0] if v["reasons"] else v["verdict"]
            if not row and st == "untested":
                why = f"{v['computed']} of {v['offline']} predictions computed, so it is untested; carried to round {rd + 1}."
            g = next((x[2] for x in gpu if (rd == 5 and x[0] == t) or (rd == 6 and x[1] == t)), None)
            theories.append([f"{rd}.{t}", rd, t, statement(t), state, fate, _cut(why, 640), _cut(v["verdict"], 640), duel, g])
            carried = v.get("carried_from")
            tfile = None if carried else json.load(open(f"{E}round-{rd:02d}/theories/{t}.json"))
            for x in v["rows"] if not carried or v["offline"] else []:
                if x.get("not_scored"):  # 0 by construction, a fit to a claimed cell, or differs from its replication
                    continue
                k = x["k"]
                pid = x.get("id") or f"{t}:p{k}"
                if carried:
                    src = _load(f"{carried}/metrics_v5.json")["theories"][t[:-len("-rival")]]["rows"][k - 1]
                    assert abs(src["measured"] - x["measured"]) < 1e-9 and src["rival"]["value"] == x["value"]
                    what, unit, rdrs = _cut(src["experiment"], 170), "", []
                    note = "c:" + json.dumps([x["nulls"][0][q] for q in ("value", "low", "high")])
                elif "value" in x:
                    what, unit = _cut(blind[pid]["experiment"], 170), blind[pid]["unit"]
                    rdrs = [[n["value"], n["low"], n["high"]] for n in x["nulls"]]
                    note = "n" if x.get("within_noise") else ""
                else:
                    p = tfile["predictions"][k - 1]
                    what, unit, rdrs = _cut(p["experiment"], 170), p["unit"], []
                    note = "x:" + _cut(x.get("not_computable") or "refuted without a number: " + x["refuted_without_number"], 230)
                    x = dict(x, value=p["value"], low=p["low"], high=p["high"], measured=None)
                preds.append([f"{rd}.{t}", f"p{k}", what, unit, x["value"], x["low"], x["high"], x.get("measured"), "",
                              rdrs, x.get("gain"), note])

    for p in preds:  # the mark: who was nearer, and whether it was an unexpected win
        v, lo, hi, m, rdrs, note = p[4], p[5], p[6], p[7], p[9], p[11]
        if m is None:
            p[8] = "x"
        elif note.startswith("c:"):
            p[8] = "c"
        else:
            d, dr = abs(v - m), abs(sum(r[0] for r in rdrs) / len(rdrs) - m)
            p[8] = "w" if d < dr else "t" if d == dr else "l"
            if lo <= m <= hi and all(not lo <= r[0] <= hi for r in rdrs):
                p[8] += "u"
    return theories, preds


def _count(theories, preds):
    """DATA's counts. Per state (one per round, "1" … "<last>", then "all"):
    nearer: [predictions where the theory's forecast is nearer the measured number than the readers' average, predictions
             compared with readers, ties]; carried predictions are not compared with readers and not counted
    inside: [inside the theory's interval, computed predictions shown] (carried included, as the engine counts them)
    readers: [theory inside, reader 1 inside, reader 2 inside, predictions] on the compared predictions where both readers
             gave an interval (rounds 3 on)
    computed: [computed, filed] predictions; gain: total log gain in nats against the readers (rounds 3 on)
    theories: one per theory id (a round-1 theory and its r1- copy of round 2 are one), the fate of its last round:
      proposed, refuted (ever), lost (to a rival, never refuted), nogain (last fate no gain, never refuted or lost),
      survive (ids that survive in the last round), standing (of those, the ones that beat their rival with at least 2
      separating tests: the duel rule of engine 7.1), per_round
    account: [predictions of round 6's account, nearer], [round 6's other compared predictions, nearer]
    commit: the last commit that changed the round files or studies/theory/README.md"""
    rounds = sorted({t[1] for t in theories})
    out = {"nearer": {}, "inside": {}, "readers": {}, "computed": {}, "gain": {}}
    for s in [str(r) for r in rounds] + ["all"]:
        ps = [p for p in preds if s == "all" or p[0].split(".")[0] == s]
        done = [p for p in ps if p[7] is not None]
        cmp = [p for p in done if p[8][0] in "wtl"]
        ri = [p for p in cmp if all(len(r) == 3 for r in p[9])]
        inside = lambda lo, hi, m: lo <= m <= hi
        out["nearer"][s] = [sum(p[8][0] == "w" for p in cmp), len(cmp), sum(p[8][0] == "t" for p in cmp)]
        out["inside"][s] = [sum(inside(p[5], p[6], p[7]) for p in done), len(done)]
        out["readers"][s] = [sum(inside(p[5], p[6], p[7]) for p in ri)] + \
                            [sum(inside(p[9][j][1], p[9][j][2], p[7]) for p in ri) for j in (0, 1)] + [len(ri)]
        out["computed"][s] = [len(done), len(ps)]
        out["gain"][s] = round(sum(p[10] for p in ri if p[10] is not None), 2) if ri else None
    norm = lambda t: ("r1-" + t[2]) if t[1] == 1 else t[2]
    last, ever = {}, {}
    for t in theories:
        last[norm(t)] = t
        ever.setdefault(norm(t), set()).add(t[5])
    acc = [p for p in preds if p[0] == "6.r6-account" and p[8][0] in "wtl"]
    six = [p for p in preds if p[0].startswith("6.") and p[8][0] in "wtl" and p[0] != "6.r6-account"]
    survive = [t for t in last.values() if t[1] == rounds[-1] and t[5] == "s"]
    out["theories"] = {
        "proposed": len(last),
        "refuted": sum("r" in f for f in ever.values()),
        "lost": sum("l" in f and "r" not in f for f in ever.values()),
        "nogain": sum(last[k][5] == "n" and not {"r", "l"} & f for k, f in ever.items()),
        "survive": sorted(t[2] for t in survive),
        "standing": sorted(t[2] for t in survive if t[8] and t[8][2] == "beats rival" and t[8][3] >= 2),
        "per_round": {str(r): sum(t[1] == r for t in theories) for r in rounds},
    }
    out["account"] = [len(acc), sum(p[8][0] == "w" for p in acc), len(six), sum(p[8][0] == "w" for p in six)]
    out["commit"] = subprocess.run(["git", "log", "-1", "--format=%h", "--", E, "studies/theory/README.md"],
                                   capture_output=True, text=True, check=True).stdout.strip()
    return out


# Written by --write from the round files: DATA's counts (keys in _count's docstring), one theory per line, one
# prediction per line (fields in _build's docstring).
COUNTS = {'nearer': {'1': [6, 7, 0], '2': [74, 151, 7], '3': [40, 80, 3], '4': [10, 29, 0], '5': [17, 45, 1], '6': [35, 58, 7], '7': [8, 24, 2], 'all': [190, 394, 20]}, 'inside': {'1': [5, 7], '2': [86, 151], '3': [60, 80], '4': [18, 29], '5': [22, 45], '6': [56, 67], '7': [16, 24], 'all': [263, 403]}, 'readers': {'1': [0, 0, 0, 0], '2': [0, 0, 0, 0], '3': [60, 69, 74, 80], '4': [18, 25, 24, 29], '5': [22, 33, 34, 45], '6': [48, 50, 49, 58], '7': [16, 20, 21, 24], 'all': [164, 197, 202, 236]}, 'computed': {'1': [7, 7], '2': [151, 151], '3': [80, 80], '4': [29, 42], '5': [45, 48], '6': [67, 71], '7': [24, 27], 'all': [403, 426]}, 'gain': {'1': None, '2': None, '3': -25.55, '4': -17.32, '5': -25.45, '6': 22.41, '7': -12.93, 'all': -58.85}, 'theories': {'proposed': 63, 'refuted': 23, 'lost': 4, 'nogain': 7, 'survive': ['r5-m03-rival'], 'standing': [], 'per_round': {'1': 6, '2': 16, '3': 14, '4': 10, '5': 13, '6': 9, '7': 10}}, 'account': [44, 31, 14, 4], 'commit': '8d210f9'}

THEORIES = [
    ['1.across-1', 1, 'across-1', "The base's loops and cap hits come from early-to-mid-layer circuits that copy its own earlier text; RL's cap-hit gain weakens that pathway in layers 0-15.", 'did not beat the readers', 'o', 'A forecaster given this theory was nearer than reader 1 on 21 of the 58 held-out numbers and farther on 14; against reader 2, 19 and 17. A planted theory with every effect reversed scored the same, so no theory beat the readers.', '', None, None],
    ['1.across-2', 1, 'across-2', "RL's lead is a learned token-budget controller, trained because 3.1 scores truncated rollouts as failures; it is not new math skill.", 'did not beat the readers', 'o', 'A forecaster given this theory was nearer than reader 1 on 23 of the 58 held-out numbers and farther on 17; against reader 2, 22 and 20. A planted theory with every effect reversed scored the same, so no theory beat the readers.', '', None, None],
    ['1.all-1', 1, 'all-1', "The cued base has RL's per-step skill; the gap is the base degrading as its own long solution grows, which RL repaired by training truncated rollouts as failures.", 'did not beat the readers', 'o', 'A forecaster given this theory was nearer than reader 1 on 24 of the 58 held-out numbers and farther on 17; against reader 2, 18 and 15. A planted theory with every effect reversed scored the same, so no theory beat the readers.', '', None, None],
    ['1.all-2', 1, 'all-2', 'Most of the RL gain is one answer-mode switch (deliberate, box the answer, stop), stored redundantly along a diffuse direction, so any small unbiased fraction of the delta flips it.', 'did not beat the readers', 'o', 'A forecaster given this theory was nearer than reader 1 on 22 of the 58 held-out numbers and farther on 20; against reader 2, 18 and 21. A planted theory with every effect reversed scored the same, so no theory beat the readers.', '', None, None],
    ['1.surprises-1', 1, 'surprises-1', 'The gain is a general deliberation shift that the cue, Code-RL and 3.0 share, plus stopping calibration that only 3.1 learned; the cued-base gap is the second part.', 'did not beat the readers', 'o', 'A forecaster given this theory was nearer than reader 1 on 21 of the 58 held-out numbers and farther on 21; against reader 2, 16 and 24. A planted theory with every effect reversed scored the same, so no theory beat the readers.', '', None, None],
    ['1.surprises-2', 1, 'surprises-2', 'The working part of the weight change is low-rank and near-linear; the high-rank remainder, which holds most of its energy, is optimizer noise.', 'did not beat the readers', 'o', 'A forecaster given this theory was nearer than reader 1 on 15 of the 58 held-out numbers and farther on 22; against reader 2, 17 and 22. A planted theory with every effect reversed scored the same, so no theory beat the readers.', '', None, None],
    ['2.r1-across-1', 2, 'r1-across-1', "The base's loops and cap hits come from early-to-mid-layer circuits that copy its own earlier text; RL's cap-hit gain weakens that pathway in layers 0-15.", 'failed the score', 'o', "Round 2 score: 2 wins and 2 losses on the claims where both readers' numbers lay outside its interval, of 13 claims.", '', None, None],
    ['2.r1-across-2', 2, 'r1-across-2', "RL's lead is a learned token-budget controller, trained because 3.1 scores truncated rollouts as failures; it is not new math skill.", 'failed the score', 'o', "Round 2 score: 1 wins and 1 losses on the claims where both readers' numbers lay outside its interval, of 16 claims.", '', None, None],
    ['2.r1-all-1', 2, 'r1-all-1', "The cued base has RL's per-step skill; the gap is the base degrading as its own long solution grows, which RL repaired by training truncated rollouts as failures.", 'refuted by its review', 'r', "Round 2 score: 2 wins and 1 losses on the claims where both readers' numbers lay outside its interval, of 12 claims.", 'Its own refutation rule for forward prediction P1 is met (half the RL weight difference with the cue on the 328: 190 right with 73 cap hits, against a claimed 45 [30, 60]; MATH-500 shows +42 right with only 5 fewer cap hits), a context-independent constant vector closes 23-31 % of the KL it says is confined to deep long contexts, and its two backtest wins are explained as well by per-problem difficulty and tail-trun…', None, None],
    ['2.r1-all-2', 2, 'r1-all-2', 'Most of the RL gain is one answer-mode switch (deliberate, box the answer, stop), stored redundantly along a diffuse direction, so any small unbiased fraction of the delta flips it.', 'passed the score', 's', "Round 2 score: 3 wins and 2 losses on the claims where both readers' numbers lay outside its interval, of 13 claims.", '', None, None],
    ['2.r1-surprises-1', 2, 'r1-surprises-1', 'The gain is a general deliberation shift that the cue, Code-RL and 3.0 share, plus stopping calibration that only 3.1 learned; the cued-base gap is the second part.', 'failed the score', 'o', "Round 2 score: 0 wins and 0 losses on the claims where both readers' numbers lay outside its interval, of 8 claims.", '', None, None],
    ['2.r1-surprises-2', 2, 'r1-surprises-2', 'The working part of the weight change is low-rank and near-linear; the high-rank remainder, which holds most of its energy, is optimizer noise.', 'passed the score', 's', "Round 2 score: 3 wins and 2 losses on the claims where both readers' numbers lay outside its interval, of 19 claims.", '', None, None],
    ['2.r2-across-1', 2, 'r2-across-1', "The weight change lowers next-token entropy only at the base's high-entropy fork tokens, so RL ignores temperature while the base loops when cooled and errs when heated.", 'failed the score', 'o', "Round 2 score: 1 wins and 1 losses on the claims where both readers' numbers lay outside its interval, of 6 claims.", '', None, None],
    ['2.r2-across-2', 2, 'r2-across-2', "The delta's effect sits in its coherent sign pattern, with hundreds to thousands of times a random direction's Fisher curvature; DARE fails near keep 0.01-0.05 %.", 'passed the score', 's', "Round 2 score: 3 wins and 2 losses on the claims where both readers' numbers lay outside its interval, of 15 claims.", "weak: the three wins follow from a saturating dose curve without leverage or signs, the claims about leverage and signs for these models are already in 2610.37719, and the theory's own inferences fail on the counter-examples it chose (Code-RL 450/390 against its 412/245; word salad rising to 34/500 at a = 1.5). Only the DARE-cliff and sign-only predictions are left to test.", None, None],
    ['2.r2-all-1', 2, 'r2-all-1', 'The delta acts through coherent signs along high-curvature directions, about 700 times a random direction; unbiased resampling keeps the gain, random signs remove it, SFT deltas break.', 'failed the score', 'o', "Round 2 score: 0 wins and 1 losses on the claims where both readers' numbers lay outside its interval, of 5 claims.", '', None, None],
    ['2.r2-all-2', 2, 'r2-all-2', 'Base accuracy at a sampler setting depends on the per-token surprise of its text (too low: loops; too high: drift); the cue lowers entropy, so truncation hurts the cued base.', 'passed the score', 's', "Round 2 score: 2 wins and 0 losses on the claims where both readers' numbers lay outside its interval, of 8 claims.", 'No team result refutes it by its own thresholds, but its two wins are explained as well by noise (t51) and by a grader format artefact (t09, which also explains its t10 miss); its loop half is published (2007.14966, 2512.12895, 2610.24715) and its entropy-to-optimal-temperature half is published across models (2502.05234), leaving only the untested prompt-level sign flip of top-p (plain base at T 1.0 / top-p 0.95) a…', None, None],
    ['2.r2-external-1', 2, 'r2-external-1', 'The delta moves output 700 times more per unit energy than a random direction; DARE holds to keep 0.1 % and collapses near 0.01 %; random weight noise reduces loops.', 'failed the score', 'o', "Round 2 score: 1 wins and 1 losses on the claims where both readers' numbers lay outside its interval, of 5 claims.", '', None, None],
    ['2.r2-external-2', 2, 'r2-external-2', 'One global temperature acts on two kinds of positions: low temperature starts loops at rare fork tokens, high temperature causes slips elsewhere; a per-position temperature would fix the base.', 'failed the score', 'o', "Round 2 score: 1 wins and 2 losses on the claims where both readers' numbers lay outside its interval, of 6 claims.", '', None, None],
    ['2.r2-revise-1', 2, 'r2-revise-1', 'Accuracy is carried by the dense sign pattern of many small entries; an edit recovers accuracy in proportion to the share of it kept; Code-RL gives no math gain.', 'failed the score', 'o', "Round 2 score: 1 wins and 0 losses on the claims where both readers' numbers lay outside its interval, of 10 claims.", '', None, None],
    ['2.r2-revise-2', 2, 'r2-revise-2', "The cued base's gap is a weak error detector, not weaker per-step math: RL notices and re-derives errors more often, so a 4-sample vote closes about half the base's gap.", 'failed the score', 'o', "Round 2 score: 0 wins and 0 losses on the claims where both readers' numbers lay outside its interval, of 2 claims.", '', None, None],
    ['2.r2-surprises-1', 2, 'r2-surprises-1', 'Loops and slips are two ends of one axis, the per-token surprise of sampled text; the cue lowers entropy, RL sits far from both ends, and raising surprise cuts loops.', 'failed the score', 'o', "Round 2 score: 0 wins and 1 losses on the claims where both readers' numbers lay outside its interval, of 4 claims.", '', None, None],
    ['2.r2-surprises-2', 2, 'r2-surprises-2', 'The base and optimizer set which entries move, and how far; the task is written only in the signs, which act on any math text and leave general text alone.', 'failed the score', 'o', "Round 2 score: 0 wins and 1 losses on the claims where both readers' numbers lay outside its interval, of 9 claims.", '', None, None],
    ['3.r1-all-2', 3, 'r1-all-2', 'Most of the RL gain is one answer-mode switch (deliberate, box the answer, stop), stored redundantly along a diffuse direction, so any small unbiased fraction of the delta flips it.', 'failed the score', 'o', 'Round 3 score: +2.62 nats against the readers over 12 claims (90 % interval reaches 0).', '', None, None],
    ['3.r1-surprises-2', 3, 'r1-surprises-2', 'The working part of the weight change is low-rank and near-linear; the high-rank remainder, which holds most of its energy, is optimizer noise.', 'failed the score', 'o', 'Round 3 score: -4.60 nats against the readers over 8 claims (90 % interval reaches 0).', '', None, None],
    ['3.r2-across-2', 3, 'r2-across-2', "The delta's effect sits in its coherent sign pattern, with hundreds to thousands of times a random direction's Fisher curvature; DARE fails near keep 0.01-0.05 %.", 'failed the score', 'o', 'Round 3 score: -3.20 nats against the readers over 7 claims (90 % interval reaches 0).', '', None, None],
    ['3.r2-all-2', 3, 'r2-all-2', 'Base accuracy at a sampler setting depends on the per-token surprise of its text (too low: loops; too high: drift); the cue lowers entropy, so truncation hurts the cued base.', 'failed the score', 'o', 'Round 3 score: +0.00 nats against the readers over 0 claims.', '', None, None],
    ['3.r3-across-1', 3, 'r3-across-1', 'The RL delta has a general reliability part, shared with Code-RL and saturated at a = 0.25, and a dose-growing math part needed only on problems the base rarely solves.', 'failed the score', 'o', 'Round 3 score: -0.35 nats against the readers over 6 claims (90 % interval reaches 0).', '', None, None],
    ['3.r3-across-2', 3, 'r3-across-2', "The cued base leaves loops only through low-probability tail tokens that T < 1 and truncation delete; RL adds a constant push toward probable 'Wait'/'Hmm', so it ignores temperature.", 'passed the score', 's', 'Round 3 score: +0.67 nats against the readers over 1 claims.', "weak: its single winning claim (t13, +0.67 nats) comes from the 'constant push' reading that was already on the board and that the reversal shared, not from the tail-escape mechanism. The loop-locking half is published (2610.24715), the core predictions (P1, P2 and the offline hold-on ratios) are untested, and result-6de887 shows T 0.6 loops can be cut by neuron ablation with no accuracy gain.", None, None],
    ['3.r3-all-1', 3, 'r3-all-1', "RL's gain over the cued base is two stopping habits: a general commit-and-box habit (Code-RL shares it, a = 0.25 holds it) and a math-specific check-before-stopping habit for long problems.", 'failed the score', 'o', 'Round 3 score: -2.67 nats against the readers over 4 claims (90 % interval reaches 0).', '', None, None],
    ['3.r3-all-2', 3, 'r3-all-2', 'On hard problems the base spreads probability at progress steps; low temperature turns the spread into self-reinforcing loops, T 1.0 into wrong turns; RL is concentrated, so temperature barely matters.', 'failed the score', 'o', 'Round 3 score: -1.36 nats against the readers over 3 claims (90 % interval reaches 0).', '', None, None],
    ['3.r3-external-1', 3, 'r3-external-1', 'Over-truncated sampling sends a pretrained-style policy into repetition basins; 3.1, trained at exact T 1.0 with truncated rollouts as negatives, suppressed them, so 3.1 ignores temperature and 3.0 does not.', 'failed the score', 'o', 'Round 3 score: -1.43 nats against the readers over 2 claims (90 % interval reaches 0).', '', None, None],
    ['3.r3-external-2', 3, 'r3-external-2', 'The delta is an early sharpening part, overshot several-fold and fully expressed at a = 0.25, plus a late part, growing with a, that solves what the base rarely solves.', 'failed the score', 'o', 'Round 3 score: -7.95 nats against the readers over 11 claims (90 % interval reaches 0).', '', None, None],
    ['3.r3-revise-1', 3, 'r3-revise-1', "The RL-Zero gain is a general 'deliberate, then commit' part (every RL-Zero delta has it, saturated at a = 0.25, replaceable by the cue) plus a math-specific part linear in a.", 'failed the score', 'o', 'Round 3 score: -2.69 nats against the readers over 11 claims (90 % interval reaches 0).', '', None, None],
    ['3.r3-revise-2', 3, 'r3-revise-2', 'A loop is an absorbing hazard that opens at impasses; T 0.6 traps finishable medium-length solutions, while at T >= 1 only fixed long, mostly lost problems loop.', 'failed the score', 'o', 'Round 3 score: +0.00 nats against the readers over 0 claims.', '', None, None],
    ['3.r3-surprises-1', 3, 'r3-surprises-1', "The cued base's T 1.0 deficit is low-probability tail tokens that derail steps, adding up with length; RL shrinks the tail; label-free tail cuts also remove loop escapes, netting zero.", 'failed the score', 'o', 'Round 3 score: -0.24 nats against the readers over 4 claims (90 % interval reaches 0).', '', None, None],
    ['3.r3-surprises-2', 3, 'r3-surprises-2', 'Any outcome-reward RL delta has a shared low-dose part gating settle, verify and stop (saturated at a = 0.25) and a math-specific part paying only on long, hard problems.', 'failed the score', 'o', 'Round 3 score: -4.35 nats against the readers over 11 claims (90 % interval reaches 0).', '', None, None],
    ['4.r4-m01', 4, 'r4-m01', "The cued base's T 0.6 loops feed on its own text: loop hazard grows with how compressible (zlib) the text so far is; the base finishes from RL's prefix because RL's text is less self-similar.", 'survives', 's', "weak: it survives offline, but nearly all its gain is one descriptive premise (base openings compress better than RL's). Its causal tests are at or below the no-theory readers (p2 +0.58, p4 -0.76), the within-problem and deletion tests that would separate it from the impasse rival were not run, its held-out claims on the neuron ablation (loops 71 -> 19, cap hits 98 -> 39) missed by -3 nats each, and its self-reinforcement core is published (Xu 2022; Duan 2026).", "weak: it survives offline, but nearly all its gain is one descriptive premise (base openings compress better than RL's). Its causal tests are at or below the no-theory readers (p2 +0.58, p4 -0.76), the within-problem and deletion tests that would separate it from the impasse rival were not run, its held-out claims on the neuron ablation (loops 71 -> 19, cap hits 98 -> 39) missed by -3 nats each, and its self-reinforcement core is published (Xu 2022; Duan 2026).", ["The cued base's loop hazard at T 0.6 is a property of the problem rather than of its own text so far: under truncated low-temperature sampling a stuck model locks into a repeat at a roughly steady rate per token (2610.24715), so problems whose solutions must…", 1.111, 'not separated from rival', 0, 5, [['Within one problem, cued base at T 0.6 / top-p 0.95: is the opening of a sample that hit the cap more compressible than the opening of a fresh restart of the s…', 0.8043478260869565, [0.63, 0.51, 0.75], [0.53, 0.41, 0.65], 3.0], ["Does problem difficulty, measured by RL's answer length on the same problem, predict a later rule-A loop in the cued base at T 0.6 / top-p 1.0, on the same row…", 0.6433452168746286, [0.67, 0.58, 0.76], [0.72, 0.61, 0.83], 0.739], ['Does early compressibility still predict a rule-A loop once problems are matched on difficulty (AUROC computed within quartiles of RL answer length)?', 0.6447368421052632, [0.66, 0.56, 0.76], [0.57, 0.46, 0.68], 0.6884], ["On the 78-problem K pool, restricted to problems where the RL-prefix continuation's opening text is at least as compressible as the own-prefix continuation's…", 0.375, [0.12, -0.07, 0.31], [0.25, 0.06, 0.44], -1.8515], ["Among the cued base's rule-A loops at T 0.6 / top-p 1.0, does a more compressible opening bring the loop onset earlier (rank correlation of opening compressibi…", -0.07436226738183375, [0.2, -0.03, 0.43], [0.06, -0.16, 0.28], -1.4651]]], None],
    ['4.r4-m02', 4, 'r4-m02', "Within a problem, a longer finished base sample means abandoned attempts, so length reads out failure for the base; RL's extra tokens are habitual checks, so RL length carries little signal.", 'refuted', 'r', 'p2 The same pooled within-problem concordance for the RL model.: measured 0.717948717948718, predicted 0.55 [0.43, 0.67]; refuting condition met: computed fraction above 0.68', '', None, None],
    ['4.r4-m04', 4, 'r4-m04', "base + a(RL - base) is a per-answer mixture of the two endpoint modes, so the RL share implied by accuracy also shows in 'Wait' rate, format and boxed accuracy.", 'refuted', 'r', 'p1 Wait-rate-based share estimate in theta0.25_plain against the plain base and RL : measured 0.327, predicted 0.76 [0.6, 0.9]; refuting condition met: S below 0.60 or above 0.92', '', None, None],
    ['4.r4-m06', 4, 'r4-m06', 'RL added a constant hold-on bias and no error detector.', 'untested', 'o', '0 of 3 predictions computed, so it is untested; carried to round 5.', '', None, None],
    ['4.r4-m07', 4, 'r4-m07', "Base wrong answers are shared attractors plus scattered slips; RL removes the slips and keeps the attractors, so RL's wrong answers mostly equal the base's.", 'refuted', 'r', "p1 MATH-500: share of RL's wrong finished samples whose answer equals one of the ba: measured 0.26717557251908397, predicted 0.5 [0.36, 0.65]; refuting condition met: measured below 0.36", '', None, None],
    ['4.r4-m08', 4, 'r4-m08', "Part of the cued base's accuracy is recall from pretraining, so at matched difficulty the RL-minus-base gap is larger on problems published after the base's data cutoff.", 'lost to its rival', 'l', "weak: it survives formally, but its only gain (p1) is a noisy 60-problem estimate the readers also bracketed, its distinctive test (p2) came out with the opposite sign at the edge of the interval, p3 is a generic difficulty effect, and board result-afc423 plus the theory's own sources (Wang AIME 2024 vs 2025; Olmo-3's low recall flags in 2611.10307) favour the termination/difficulty rival.", "weak: it survives formally, but its only gain (p1) is a noisy 60-problem estimate the readers also bracketed, its distinctive test (p2) came out with the opposite sign at the edge of the interval, p3 is a generic difficulty effect, and board result-afc423 plus the theory's own sources (Wang AIME 2024 vs 2025; Olmo-3's low recall flags in 2611.10307) favour the termination/difficulty rival.", ['Exposure plays no part: the RL-minus-cued-base gap is set only by how long and hard a problem is, because the base fails to commit or terminate on long chains.', -2.652, 'loses to rival', 0, 5, [['Independent replication at T 0.6 of the stratified post-minus-pre paired gap (RL plain minus base cue) on the clean harder 328, matched on RL answer length, us…', -5.63942436083997, [4.0, -9.0, 17.0], [1.0, -10.0, 12.0], -0.418], ['Independent replication at T 0.6 of the both-right base/RL length comparison: median log length ratio, pre-cutoff minus post-cutoff, on the clean harder 328.', -0.19431648776581323, [-0.25, -1.0, 0.5], [0.0, -0.5, 0.5], -0.2086], ["MATH-500: per-token entropy of the RL model's own short right answers relative to its own long right answers (the RL-side counterpart of test 3).", 0.7662885079105015, [0.9, 0.75, 1.05], [0.82, 0.68, 0.96], -0.945], ["MATH-500, 4 independent samples per model at T 1.0: on problems that both models solve every time and where the base's typical answer is short, how much the ba…", 0.5180097906045676, [0.05, -0.35, 0.45], [0.2, -0.15, 0.55], -0.8688], ['MATH-500, same 4-sample rows: base-versus-RL length variability on short problems minus the same on long problems (difference in median log CV ratios).', -0.020345857212325513, [-0.15, -0.55, 0.25], [0.1, -0.2, 0.4], -0.2121]]], None],
    ['4.r4-m09', 4, 'r4-m09', "Code-RL 3.1's math gain is only an ending policy (finish under the cap with one answer, then stop); it adds nothing where the base finishes wrongly.", 'refuted', 'r', 'p2 MATH-500: Code-RL cue fix rate minus random-difference cue fix rate on base clea: measured 0.14285714285714285, predicted 0.0 [-0.12, 0.1]; refuting condition met: measured above 0.12', '', None, None],
    ['4.r4-m10', 4, 'r4-m10', "Early RL (steps 100-400) lowers entropy, so T 0.6 / top-p 0.95 sampling loops more and cap hits rise above the base's; truncation-as-failure training later removes the loops.", 'lost to its rival', 'l', "weak: the rise-then-fall of T 0.6 cap hits (base 65 -> step 100 103 / step 400 98 -> step 2,800 about 16) is real and beat both readers, but the theory's mechanism (entropy collapse pushing sampling past top-p's lock threshold) was never tested, an untested length-growth rival explains the same numbers, the accuracy prediction could not be computed, and one import is misread.", "weak: the rise-then-fall of T 0.6 cap hits (base 65 -> step 100 103 / step 400 98 -> step 2,800 about 16) is real and beat both readers, but the theory's mechanism (entropy collapse pushing sampling past top-p's lock threshold) was never tested, an untested length-growth rival explains the same numbers, the accuracy prediction could not be computed, and one import is misread.", ["By step 100, RL-Zero-Math has mainly taught the base to open in the RL model's own deliberation mode (the ' line!\\n\\nOkay' opening that the cue forces in the base), not a sharper, lower-entropy policy; at T 0.6 / top-p 0.95 this long-deliberation mode loops e…", -7.809, 'loses to rival', 2, 6, [["Share of RL step-100 plain MATH-500 answers (T 0.6 / top-p 0.95) that open in the 'Okay' deliberation format.", 0.956, [0.65, 0.38, 0.92], [0.72, 0.48, 0.93], -0.4317], ['Paired cap-hit rate difference at RL step 400, cued prompt minus plain prompt, MATH-500 at T 0.6 / top-p 0.95.', -0.027999999999999997, [0.025, -0.03, 0.085], [0.01, -0.04, 0.06], -0.5078], ['Ratio of median generated length of finished answers, RL step 100 over base, plain MATH-500 at T 0.6 / top-p 0.95.', 2.251572327044025, [1.8, 1.0, 3.0], [2.0, 1.3, 2.9], -0.3652], ['Per-token sharpness of RL step-100 finished answers relative to the cued base: share of step-100 plain finished answers whose mean_logprob exceeds the median m…', 0.5541561712846348, [0.63, 0.49, 0.78], [0.53, 0.41, 0.65], -0.5046], ["Same sharpness share at RL step 400: share of step-400 plain finished answers whose mean_logprob exceeds the median mean_logprob of the cued base's finished an…", 0.48009950248756217, [0.76, 0.62, 0.89], [0.58, 0.45, 0.71], -3.0], ["Where step 400's median per-token log-prob on finished answers lies between the cued base and step 2,800, plain prompt for RL checkpoints, MATH-500, T 0.6 / to…", 0.06726598846379954, [0.75, 0.42, 1.08], [0.25, -0.15, 0.65], -3.0]]], None],
    ['4.r4-m11', 4, 'r4-m11', 'The cued base keeps writing after its answer and the last-marker grader scores a later, wrong one.', 'untested', 'o', '0 of 5 predictions computed, so it is untested; carried to round 5.', '', None, None],
    ['4.r4-m12', 4, 'r4-m12', "Part of the hard328 gap is grader v3 false negatives on the base's non-canonical answers to non-integer problems.", 'untested', 'o', '1 of 4 predictions computed, so it is untested; carried to round 5.', '', None, None],
    ['5.r4-m06', 5, 'r4-m06', 'RL added a constant hold-on bias and no error detector.', 'no gain', 'n', "RL's re-check rate after wrong against right candidates is 1.24 and the base-RL difference is -0.087, both as predicted and as the readers said; the share of final-right answers with a re-checked right candidate is 0.44 higher in RL (predicted 0.12).", '', None, None],
    ['5.r4-m11', 5, 'r4-m11', 'The cued base keeps writing after its answer and the last-marker grader scores a later, wrong one.', 'refuted', 'r', "Of the cued base's v3-wrong answers, 0 have a right first answer marker.", '', None, None],
    ['5.r4-m12', 5, 'r4-m12', "Part of the hard328 gap is grader v3 false negatives on the base's non-canonical answers to non-integer problems.", 'refuted', 'r', "Numeric equivalence recovers 0 of the cued base's finished v3-wrong non-integer answers; the gap after regrading stays 12.8 points.", '', None, None],
    ['5.r5-m02', 5, 'r5-m02', "The cued base's wrong finished samples are shorter than their right siblings on Levels 1-3 and longer on Level 5.", 'refuted', 'r', 'On Levels 1-3 wrong samples are longer, not shorter (median log length ratio +0.193; predicted -0.2).', '', None, None],
    ['5.r5-m03', 5, 'r5-m03', 'The top-8 singular directions of the RL-Math weight change act like the opening cue and nothing more.', 'lost to its rival', 'l', "Its gain is one test, the count of quick finished-wrong answers of top8 plain (22; predicted 11 [5, 21]), which lies outside its own interval. Rival: top8 is a per-sample mixture of RL-like answers and plain-base answers. top8's quick wrong answers fall on problems the cued base solves at a mean rate of 0.818 (theory 0.5, rival 0.76); 0.773 of them have at most 1,000 tokens (theory 0.4, rival 0.63).", "weak: duel state 'loses to rival' (-8.77, all 3 tests favour the rival's mixture account); its only offline gain rests on one test whose value fell outside its interval; and result-284db5 (top8 adds +8.5 on top of the cue, with RL-level Wait rates) contradicts its 'nothing more than the cue' core, although hard328 is formally outside its scope.", ['The top-8 edit is an incomplete switch that happens or fails sample by sample.', -8.767, 'loses to rival', 3, 3, [["Among top8-plain wrong problems, the fraction that the cued base solves in all 4 of its Day-1 #3 samples: are top8's errors on problems the cued base finds rel…", 0.25, [0.13, 0.06, 0.22], [0.27, 0.17, 0.37], -2.767], ['Mean cued-base solve rate (4 Day-1 #3 samples) on the problems where top8 plain gives a quick finished-wrong answer (wrong under v3, not a cap hit, at most 2,0…', 0.8181818181818182, [0.5, 0.3, 0.7], [0.76, 0.64, 0.88], -3.0], ["Share of top8 plain's quick finished-wrong answers that are very short (at most 1,000 generated tokens).", 0.7727272727272727, [0.4, 0.18, 0.62], [0.63, 0.43, 0.83], -3.0]]], None],
    ['5.r5-m04', 5, 'r5-m04', "Think-SFT's remaining errors are mostly cap hits on the problems where RL writes longest.", 'refuted', 'r', '25 cap hits of 500 (predicted 38 [28, 55]); in the longest quartile Think-SFT is 6 problems ahead of RL, not behind.', '', None, None],
    ['5.r5-m05', 5, 'r5-m05', 'The base flags a doubtful step as well as RL but restates its value after the hold-on token, while RL re-derives it.', 'refuted', 'r', 'Base and RL revise the value after a hold-on at the same rate (ratio 1.04; predicted 0.55).', '', None, None],
    ['5.r5-m06', 5, 'r5-m06', 'The problems RL solves and the cued base misses 4 of 4 are ones the base already solves a few percent of the time per sample.', 'refuted', 'r', 'A pool of other samples solves 11 of these 17 problems at least once (0.647), 0.522 more than of the 16 that RL also misses, as predicted. Correction after the audit of result-07f566: the pool is not base-only (it holds cap-hit restarts, the base with a random weight edit, the base with 3 examples, a T 1.5 min-p cell and a T 0.6 cell); 4 of the 11 are solved only by the edited or example-prompted base, and the base\'s own restarts solve 7 of 17. Refuted on the size: the per-sample rate is 0.237, not "a few percent" (predicted 0.09 [0.03, 0.18]).', '', None, None],
    ['5.r5-m07', 5, 'r5-m07', 'By RL step 100 the policy differs from the base almost only in opening with the RL cue.', 'refuted', 'r', "3.4 % of step-100 plain answers at T 0.6 open with 'line' (predicted 0.68); 4.5 % of finished ones keep the base's 'Answer:' line (predicted 0.30).", '', None, None],
    ['5.r5-m08', 5, 'r5-m08', "Code 3.0 learned a runaway long-generation mode, so at T 1.0 it keeps Code 3.1's gain on short MATH-500 problems and loses it on the longest quartile through cap hits.", 'refuted', 'r', "The length pattern holds: 0.795 of Code 3.1's lead is in the longest quartile; on the short half Code 3.0 is 3 problems ahead of Code 3.1 (246 against 243 of 250) and 7.25 ahead of the cued base; in the longest quartile it is 11.25 behind the cued base. The cause does not: the scored Code 3.0 cell has 5 cap hits of 500 (base 27, Code 3.1 7).", "refuted: duel state beats rival and its offline quartile predictions hold, but its stated mechanism (Code 3.0's longest MATH-500 problems driven to the 16,384 cap at T 1.0) is contradicted by the scored cell itself, which has 5 cap hits on 500 problems (base 27, Code 3.1 7), so the length-confined deficit it predicted comes from something other than cap hits.", ["Code 3.0's RL taught it only a commit-and-stop habit (short answers, about 3,069 tokens a problem, with a clean final answer) and not the math reasoning that Code 3.1 gained, so on easy problems it removes the base's drift and answer-statement failures, and o…", 8.748, 'beats rival', 3, 5, [['Code 3.0 cue accuracy on the longest-quartile MATH-500 problems that the cued base solves in all 4 samples (long but easy for the base).', 0.7241379310344828, [0.78, 0.64, 0.9], [0.86, 0.75, 0.95], 1.9853], ["Mean cued-base solve rate (of 4 samples) on the Q4 problems that Code 3.0 cue gets wrong: whether Code 3.0's long-problem failures fall on base-hard problems o…", 0.4014084507042254, [0.42, 0.3, 0.55], [0.31, 0.22, 0.4], 1.0373], ['Code 3.0 cue accuracy minus held-out base accuracy, on Q4 problems that base cue samples 0 and 1 both solve.', -0.1847826086956521, [-0.08, -0.17, 0.01], [-0.02, -0.09, 0.05], 3.0], ["Share of Code 3.0's Q4 deficit to the held-out base that lies on Q4 problems where base cue samples 0 and 1 are not both right.", 0.41379310344827586, [0.2, -0.6, 1.0], [1.0, 0.62, 1.4], 2.2418], ['Code 3.0 cue accuracy minus held-out base accuracy, on short-half (Q1+Q2) problems where base cue samples 0 and 1 are not both right.', 0.07894736842105265, [0.13, -0.02, 0.28], [-0.02, -0.15, 0.11], 0.484]]], None],
    ['5.r5-m09', 5, 'r5-m09', "About a quarter of the cued base's finished-wrong samples on usually-solved problems box a number from the problem statement.", 'refuted', 'r', 'Base minus RL share of wrong finals equal to a problem-statement number is -0.043 (predicted +0.14). Its p1 and p2 are 0 by data layout (the field they read is null on real items) and decide nothing.', '', None, None],
    ['5.r5-m10', 5, 'r5-m10', "At T 1.0 the plain base picks one of two whole answer modes in its first tokens; the cue's gain is the mode share times the accuracy difference, and nothing after the opening adds.", 'refuted', 'r', "Self-opened plain answers do score like cued ones (difference 0.00) and are 1.21 times as long. But plain answers that do not self-open and contain 'Wait' or 'Hmm' later score +0.356 above the other non-self-opened answers and only 0.075 below cued answers on the same problems (theory -0.47). The standing part is in Wang et al. 2610.06851, App. C.8.", "refuted: duel state 'loses to rival' (-8.84 nats). In scope, on its own T3 file, plain answers that do not self-open but self-check later score +0.36 above other plain answers and come within 0.075 of cued answers on the same problems, which contradicts 'nothing after the opening adds'. Result-460e0a's 410 -> 372 drop under a fixed cue points the same way, and the part that survives (self-opened answers score like cued ones) is largely in Wang et al. App C.8.", ["The cue's +37-point gain at T 1.0 / top-p 1.0 comes from robustness to sampling noise, not from choosing between two modes of fixed accuracy: the plain base's terse, non-deliberative answers are reasonably accurate (about 60 % at T 0.6) but at full temperatur…", -8.844, 'loses to rival', 3, 6, [['Temperature sensitivity of the non-self-opened plain register: accuracy of non-self-opened plain base answers at T 0.6 minus accuracy of non-self-opened plain…', 0.15767634854771778, [0.28, 0.16, 0.4], [0.29, 0.17, 0.41], 0.2393], ['How weak the non-self-opened plain register is when sampling is cooler: accuracy of non-self-opened plain base answers at T 0.6 minus accuracy of cued base ans…', -0.15540540540540537, [-0.1, -0.19, -0.01], [-0.1, -0.2, 0.0], 0.0079], ['Accuracy gap between self-opened and non-self-opened plain base answers at T 0.6, within one file.', 0.20574986751457336, [0.11, 0.02, 0.2], [0.09, -0.04, 0.22], -0.091], ["On MATH-500 at T 1.0, plain base answers that do not self-open but contain a self-check marker later ('Wait' or 'Hmm'): their accuracy minus cued base accuracy…", -0.07462686567164178, [-0.47, -0.6, -0.33], [-0.14, -0.3, 0.02], -3.0], ["On MATH-500 at T 1.0, within the plain base answers that do not self-open: accuracy of those containing 'Wait' or 'Hmm' minus accuracy of those containing neit…", 0.35583146215823536, [-0.03, -0.15, 0.1], [0.24, 0.07, 0.41], -3.0], ["On the harder clean 328 at T 1.0, plain base answers that do not self-open but contain 'Wait' or 'Hmm': their accuracy minus cued base accuracy on the same pro…", -0.10000000000000003, [-0.33, -0.47, -0.19], [-0.1, -0.26, 0.06], -3.0]]], ['result-3a3af3', 411, 500, [397, 424], [375, 348, 400], [405, 386, 422], 'r5-m10-rival', 'studies/theory/results/experiments/selfopen-01/metrics.json']],
    ['5.r5-m11', 5, 'r5-m11', "Code-RL 3.1 reaches Math-RL's MATH-500 total through a code-style habit that pays on discrete subjects.", 'refuted', 'r', "Code-style markers are no more frequent in Code-RL's hard328 answers than in the cued base's (difference 0.00); marked answers score 0.123 below unmarked ones.", '', None, None],
    ['6.r5-m03-rival', 6, 'r5-m03-rival', "The top-8 edit of the RL-Math weight change is an incomplete switch per sample: most base+top8 plain answers follow a weak dose of RL's policy, 10-15 % stay in the plain-base register.", 'survives', 's', 'Fresh rival: the quick wrong answers are a per-problem plain-prompt failure. On top8\'s quick-wrong problems the plain base\'s wrong rate is 0.455 (n 22; theory 0.52, rival 0.68) and, against top8-right easy problems, -0.057 higher (n 401; theory 0.03, rival 0.25). The review asks to drop "whatever the difficulty": plain-register accuracy does depend on difficulty (0.232 and 0.491 contrasts).', "stands: duel state beats rival (+6.70, separated by k2 with k1/k3/k6 agreeing) on a correctly implemented script, and nothing in scope refutes it. Its held-out loss (t65) comes from an out-of-scope 2x dose claim, and its 'whatever the difficulty' clause is contradicted by duel tests k4/k5 and should be dropped.", ["The top-8 edit installs a weak dose of RL's policy on every sample, but on a fixed subset of prompts the plain prompt still keys the plain base's own short, committed answer, so top8 plain's quick wrong answers are a per-problem plain-prompt failure: they fal…", 6.699, 'beats rival', 1, 6, [['Plain-base T 1.0 wrong rate on the problems where top8 plain gives a quick finished-wrong answer.', 0.45454545454545453, [0.52, 0.34, 0.7], [0.68, 0.5, 0.86], 1.9437], ["Difficulty-controlled contrast: plain-base T 1.0 wrong rate on top8's quick-wrong problems minus its wrong rate on top8-right problems that the cued base solve…", -0.05732789637802832, [0.03, -0.17, 0.23], [0.25, 0.06, 0.44], 3.0], ['Plain-base T 0.6 wrong rate (a second, independent plain sample) on the problems where top8 plain gives a quick finished-wrong answer.', 0.3181818181818182, [0.37, 0.2, 0.54], [0.55, 0.37, 0.73], 2.1756], ['Difficulty dependence of the plain register at T 1.0. Among plain-base T 1.0 answers that do not self-open, accuracy on problems the cued base solves in all 4…', 0.23184531765125188, [0.41, 0.29, 0.53], [0.42, 0.27, 0.57], -0.6302], ["Difficulty dependence of the plain register at T 0.6. The same contrast on the plain base's T 0.6 / top-p 0.95 answers that do not self-open: accuracy on cued-…", 0.4912280701754387, [0.63, 0.5, 0.76], [0.55, 0.38, 0.72], -1.1118], ['Per-problem persistence of plain-base failures at fixed difficulty. On problems the cued base solves in all 4 samples, the plain-base T 1.0 wrong rate when the…', 0.08159779614325069, [0.08, -0.06, 0.22], [0.22, 0.08, 0.36], 1.3221]]], None],
    ['6.r5-m10-rival', 6, 'r5-m10-rival', "The cue's gain at T 1.0 is robustness to sampling noise: the terse plain register is derailed after its opening by tail tokens; the deliberative register checks itself.", 'survives', 's', "Fresh rival (a stopping and last-marker grading failure) fails: 0.8 % of the plain base's wrong non-self-opened answers have a right first marker (n 260), run-on share 0.089 (n 259). Weak because one test separates (n 25), the defender missed 5 of 6 intervals, the Wait/Hmm tests are confounded with late self-opening, and its own temperature prediction missed (0.158 against 0.29).", "weak: duel state beats rival (+13.2 nats), but only one duel test separates the two (k2, n=25), and the defender's intervals from the theory alone missed that one and 4 of the other 5; the offline gain rests on p4 to p6, whose 60-character self-open filter puts late-opened deliberative answers into the 'terse with Wait/Hmm' group (p5's own example row), so the self-check claim is confounded with choosing a mode, and the theory's core temperature prediction p1 missed (0.158 against 0.29 [0.17, 0.41]).", ["The plain base's terse register is intrinsically weaker than the deliberative '\\nOkay' register by about 15-20 points at any temperature, and the extra loss at T 1.0 / top-p 1.0 is mostly a stopping-and-grading failure, not derailed reasoning: after writing i…", 13.195, 'beats rival', 1, 6, [["First-marker regrade of the plain base's wrong non-self-opened answers at T 1.0: among non-self-opened T3 rows graded wrong by grader v3 on the full text, the…", 0.007692307692307693, [0.07, 0.01, 0.15], [0.17, 0.07, 0.29], 2.3257], ["Direction of first/last disagreement in the plain base's non-self-opened T 1.0 answers: among rows where the first-marker grade differs from the v3 last-marker…", 0.08, [0.45, 0.2, 0.72], [0.72, 0.55, 0.88], 3.0], ["Run-on share among the plain base's finished, wrong, non-self-opened T 1.0 answers: the fraction that keep going for more than 300 characters after their first…", 0.0888030888030888, [0.3, 0.12, 0.5], [0.4, 0.25, 0.55], 3.0], ["Within the cued base's MATH-500 answers at T 1.0 / top-p 1.0: accuracy of answers containing 'Wait' or 'Hmm' minus accuracy of answers containing neither.", 0.07056451612903225, [-0.06, -0.18, 0.06], [-0.14, -0.25, -0.03], 3.0], ["The same contrast on the harder clean 328: within cued base answers at T 1.0 / top-p 1.0, accuracy of answers containing 'Wait' or 'Hmm' minus accuracy of answ…", 0.0, [-0.22, -0.4, -0.04], [-0.33, -0.52, -0.14], 2.1144], ["Gold-in-text excess at T 1.0 over T 0.6 for the plain base's finished, wrong, non-self-opened answers on problems with an integer gold of absolute value >= 10…", 0.10286935286935286, [0.12, -0.03, 0.27], [0.13, 0.02, 0.24], -0.2455]]], ['result-3a3af3', 411, 500, [397, 424], [375, 348, 400], [405, 386, 422], 'r5-m10-rival', 'studies/theory/results/experiments/selfopen-01/metrics.json']],
    ['6.r6-account', 6, 'r6-account', 'Six ordered rules split the problems an RL-side model gets right and the base side wrong: loop, budget, answer-statement, slip, sharpening, reach; one null cell (cued base against another cued-base sample).', 'lost to its rival', 'l', 'Shares of the 65 RL-only problems on MATH-500 at T 1.0: budget 0.246, slip 0.185, sharpening 0.446, reach 0.092, answer-statement 0.031, loop 0; the null cell (46 problems) has 0.152, 0.261, 0.478, 0.065, 0.043, 0. Plain base against RL (247 problems): answer-statement 0.514. At min-p 0.1 loop is 0.406, at T 0.6 0.52-0.57. Rival: no RL-specific finishing policy, one difficulty axis; its win is one test (-2.14).', "weak: the rival beats the theory (-3.107 nats, loses to rival), but its win rests mainly on one test (Think-SFT budget share 0.246, -2.14 of -3.11, with 0 tests marked separating), and result-51a0e7 contradicts its 'no RL-specific policy of finishing' wording. RL's cap-hit avoidance sits in its top-8 directions (90 cap hits with them removed vs 33 for random rank-8), although right answers on cap hits still follow strength, as the rival claims.", ["There is no RL-specific policy of finishing before the cap: at T 1.0 the cued base's cap hits are simply the hard, long end of the one difficulty axis, and any arm that is stronger on that axis fixes them at the rate its overall strength predicts for problems…", -3.107, 'loses to rival', 0, 5, [["MATH-500, claimed cell: RL's solve rate on the cued base's T1 cap-hit problems minus the solve rate expected for problems of the same base difficulty, using RL…", -0.010905349794238739, [-0.05, -0.21, 0.11], [0.02, -0.15, 0.19], 0.0246], ["hard328: RL plain's solve rate on the cued base's cap-hit problems minus the solve rate expected for problems of the same base difficulty, using RL's rate on t…", -0.05976305529211637, [-0.06, -0.2, 0.08], [-0.06, -0.18, 0.06], -0.1541], ["Budget share of the gap when the other side is the reward-free Think-SFT model with the cue: among problems Think-SFT cue gets right and the cued base's T1 get…", 0.24615384615384617, [0.13, 0.05, 0.22], [0.2, 0.12, 0.28], -2.1369], ["MATH-500, T 1.0: on the cued base's T1 cap-hit problems, Think-SFT cue's right count minus Math-RL's (T2) right count", 0, [-2, -7, 3], [-1, -5.5, 3.5], -0.255], ["MATH-500, T 1.0: Think-SFT cue's solve rate on the cued base's T1 cap-hit problems minus its solve rate on T1 finished-wrong problems of the same 4-sample base…", -0.03438418577307478, [-0.1, -0.35, 0.15], [-0.07, -0.21, 0.07], -0.5855]]], None],
    ['6.r6-m01', 6, 'r6-m01', "The cued base's deliberative register fades with distance from the cue; long answers slide into textbook continuation.", 'refuted', 'r', '0.7 % of hard328 base answers of at least 12,000 tokens have a textbook header in their second half (n 136; predicted 0.25).', '', None, None],
    ['6.r6-m04', 6, 'r6-m04', 'On base + a(Think-SFT - base) the length policy arrives at a small dose, so intermediate models hit the cap more than either end.', 'refuted', 'r', 'No cap-hit bump (-2 against the endpoints); at a = 0.25 only 0.065 of the log length change has arrived (predicted 0.8).', '', None, None],
    ['6.r6-m05', 6, 'r6-m05', "RL's extra 'Wait' and 'Hmm' come from a timer: their excess grows with the text since the last stated result.", 'refuted', 'r', 'The RL/base hold-on ratio far from a result over near it is 0.97 (predicted 1.7); near a result it is already 1.38.', '', None, None],
    ['6.r6-m06', 6, 'r6-m06', "The cued base's wrong steps come from head tokens; RL's text has as many p < 0.01 tokens as the base's.", 'untested', 'o', 'The stored hard328 rows have no per-token probability field.', '', None, None],
    ['6.r6-m10', 6, 'r6-m10', 'The first 100 RL steps install the opening, format and length; the lower error rate on finished answers comes after step 400.', 'refuted', 'r', "Step 100's finished answers are already 4.6 points more often right than the cued base's on the same problems (n 345, 90 % [-6.7, -2.6]).", '', None, None],
    ['6.r6-m11', 6, 'r6-m11', 'The cued base often writes its answer marker early and then justifies it; these early commitments are wrong more often.', 'refuted', 'r', "Of the cued base's quick finished-wrong answers, 0 of 13 are early-marker answers (predicted 0.45). p1 not scored: differs from its replication.", '', None, None],
    ['7.r5-m03-rival', 7, 'r5-m03-rival', "The top-8 edit of the RL-Math weight change is an incomplete switch per sample: most base+top8 plain answers follow a weak dose of RL's policy, 10-15 % stay in the plain-base register.", 'survives', 's', 'One separating duel test of 6; its "whatever the difficulty" clause is contradicted by duel tests p4 and p5.', "weak: the duel state is 'not separated from rival'. The theory wins only one separating duel test (p2, n 401; stands needs two), and its own clause that plain-register errors ignore difficulty is contradicted by duel tests p4/p5 (gaps 0.23 and 0.49, intervals excluding 0).", ["The top-8 edit installs a weak dose of RL's policy on every sample, but on a fixed subset of prompts the plain prompt still keys the plain base's own short, committed answer, so top8 plain's quick wrong answers are a per-problem plain-prompt failure: they fal…", 3.0, 'not separated from rival', 1, 6, [['Plain-base T 1.0 wrong rate on the problems where top8 plain gives a quick finished-wrong answer.', 0.45454545454545453, [0.52, 0.34, 0.7], [0.68, 0.5, 0.86], 1.9437], ["Difficulty-controlled contrast: plain-base T 1.0 wrong rate on top8's quick-wrong problems minus its wrong rate on top8-right problems that the cued base solve…", -0.05732789637802832, [0.03, -0.17, 0.23], [0.25, 0.06, 0.44], 3.0], ['Plain-base T 0.6 wrong rate (a second, independent plain sample) on the problems where top8 plain gives a quick finished-wrong answer.', 0.3181818181818182, [0.37, 0.2, 0.54], [0.55, 0.37, 0.73], 2.1756], ['Difficulty dependence of the plain register at T 1.0. Among plain-base T 1.0 answers that do not self-open, accuracy on problems the cued base solves in all 4…', 0.23184531765125188, [0.41, 0.29, 0.53], [0.42, 0.27, 0.57], -0.6302], ["Difficulty dependence of the plain register at T 0.6. The same contrast on the plain base's T 0.6 / top-p 0.95 answers that do not self-open: accuracy on cued-…", 0.4912280701754387, [0.63, 0.5, 0.76], [0.55, 0.38, 0.72], -1.1118], ['Per-problem persistence of plain-base failures at fixed difficulty. On problems the cued base solves in all 4 samples, the plain-base T 1.0 wrong rate when the…', 0.08159779614325069, [0.08, -0.06, 0.22], [0.22, 0.08, 0.36], 1.3221]]], None],
    ['7.r6-account-rival', 7, 'r6-account-rival', 'No RL-specific finishing policy: cap hits are the hard end of one difficulty axis.', 'no gain', 'n', 'Total gain above 0, but no prediction won where the readers were outside its interval.', '', None, None],
    ['7.r6-m06', 7, 'r6-m06', "The cued base's wrong steps come from head tokens; RL's text has as many p < 0.01 tokens as the base's.", 'untested', 'o', 'The stored rows still have no per-token probability field.', '', None, None],
    ['7.r7-m03', 7, 'r7-m03', "Many of the cued base's arithmetic slips are single T 1.0 draws of a wrong number token; cooling removes them.", 'refuted', 'r', 'The self-inconsistent-equation rate at T 1.0 is 0.36 times the rate at T 0.6 (n 377; predicted 3).', '', None, None],
    ['7.r7-m05', 7, 'r7-m05', "The cued base's misread and slip steps are what its language prior writes for a generic problem of the kind.", 'no gain', 'n', 'Inside, but the readers predicted the same.', '', None, None],
    ['7.r7-m07', 7, 'r7-m07', 'The 3.0 RL-Zero releases learned to stop before about 12k tokens and close long problems early and unchecked.', 'no gain', 'n', 'p3 -0.371 against -0.12 predicted (n 80).', '', None, None],
    ['7.r7-m08', 7, 'r7-m08', "Code-RL 3.1 raises accuracy by lowering the base's own misread and slip steps, without replacement tokens.", 'no gain', 'n', 'Groups of 16 to 33 items; intervals too wide to gain.', '', None, None],
    ['7.r7-m09', 7, 'r7-m09', "Think-SFT's excess wrong answers on easy problems are final formats that grader v3 rejects.", 'no gain', 'n', 'Groups of 6 to 9 items.', '', None, None],
    ['7.r7-m11', 7, 'r7-m11', "The cued base's wrong value is set by the shared prompt and opening, so wrong answers under one opening agree.", 'no gain', 'n', 'p2 0.164 against 0 predicted, within noise (n 28).', '', None, None],
    ['7.r7-m12', 7, 'r7-m12', "RL-written examples in context help only on problems of the examples' subject.", 'refuted', 'r', 'Same-subject minus other-subject gain is -0.018 (n 223, 90 % [-0.058, 0.022]; predicted +0.08).', '', None, None],
]

PREDS = [
    ['1.all-2', 't49', 'base + 0.25*(RL - base), plain prompt, T 1.0 / top-p 1.0, cap 16,384, grader v3, MATH-500 one sample', 'right of 500', 375, 330, 415, 405, 'wu', [[300], [300]], None, ''],
    ['1.all-2', 't50', 'base + 0.5*(RL - base), plain prompt, T 1.0 / top-p 1.0, cap 16,384, grader v3, MATH-500 one sample', 'right of 500', 432, 415, 450, 443, 'w', [[430], [420]], None, ''],
    ['1.all-2', 't47', 'base + 0.5*(RL - base) with the opening cue minus the same model with the plain prompt, T 1.0, MATH-500', 'right of 500 (difference)', 3, -10, 15, 9, 'wu', [[20], [25]], None, ''],
    ['1.all-2', 't51', 'base + 1.0*(Code-RL - base) (Olmo-3.1-7B-RL-Zero-Code final), plain prompt, T 1.0 / top-p 1.0, grader v3, MATH-500 one sample', 'right of 500', 320, 270, 375, 390, 'w', [[270], [300]], None, ''],
    ['1.across-2', 't47', "Base + 0.5*(RL - base), opening cue, T 1.0 / top-p 1.0, MATH-500 n=500, cap 16,384, grader v3: right (with mean tokens per problem expected between the base's 3,933 and…", 'right of 500', 447, 436, 457, 452, 'l', [[450], [445]], None, ''],
    ['1.surprises-1', 't51', 'Olmo-3.1-7B-RL-Zero-Code (final checkpoint, = base + Code-RL delta), plain prompt (no cue), MATH-500 n=500, T 1.0 / top-p 1.0, cap 16,384, grader v3', 'right of 500', 340, 280, 400, 390, 'w', [[270], [300]], None, ''],
    ['1.surprises-1', 't52', 'Olmo-3.1-7B-RL-Zero-Code with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, cap 16,384, grader v3', 'right of 500', 410, 390, 432, 450, 'w', [[400], [400]], None, ''],
    ['2.r1-across-1', 't36', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 418, 410, 426, 450, 'w', [[420], [415]], None, ''],
    ['2.r1-across-1', 't37', 'Base Olmo-3-1025-7B plus a random difference of matched norm to the RL-minus-base difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: nu…', 'right of 500', 407, 399, 415, 417, 'l', [[408], [408]], None, ''],
    ['2.r1-across-1', 't47', 'Base Olmo-3-1025-7B plus a random matched-norm difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3: mean generated tokens per problem', 'tokens per problem', 3950, 3750, 4150, 3944, 't', [[3950], [3950]], None, ''],
    ['2.r1-across-1', 't46', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the opening cue: weights base + 0.25*(RL-Zero-Math minus base): mean generated tokens per problem', 'tokens per problem', 3700, 3450, 3930, 4036, 'l', [[4000], [4050]], None, ''],
    ['2.r1-across-1', 't55', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1: number of answers flagged as rule-A loops (an 8,000-character window starting at a line start with zlib…', 'answers of 500', 40, 25, 60, 34, 'wu', [[10], [12]], None, ''],
    ['2.r1-across-1', 't56', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1 (v3): number of answers that hit the token cap', 'cap hits of 500', 62, 45, 80, 58, 'w', [[40], [45]], None, ''],
    ['2.r1-across-1', 't51', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 392, 378, 404, 404, 'lu', [[415], [412]], None, ''],
    ['2.r1-across-1', 't52', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.5 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 404, 394, 414, 412, 'w', [[400], [395]], None, ''],
    ['2.r1-across-1', 't53', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 0.95 (no min-p, v3, one sample): number right', 'right of 500', 402, 394, 410, 409, 'w', [[395], [398]], None, ''],
    ['2.r1-across-1', 't54', 'Olmo-3.1-7B-RL-Zero-Math with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 462, 455, 469, 460, 'w', [[462], [463]], None, ''],
    ['2.r1-across-1', 't57', 'cleanneurons Part T3, Olmo-3-1025-7B base vs RL-Zero-Math, teacher-forced on held-out 2,672 decisive positions after the cue, on stored cue-base (T1) text: percent of KL…', 'percent', 8, 2, 14, 23.4, 'l', [[15], [12]], None, ''],
    ['2.r1-across-1', 't58', 'Same constant-vector-per-layer arm (32 vectors, mean of RL-layer minus base-layer output), held-out 2,672 decisive positions, but on stored RL-model (T2) text: percent o…', 'percent', 9, 3, 16, 31.2, 'l', [[20], [18]], None, ''],
    ['2.r1-across-1', 't59', 'Olmo-3 base, T1 (cued-base) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by adding a constant vector on the MLP output only (mean of RL minus…', 'percent', 5, 0, 11, 14.0, 'l', [[10], [7]], None, ''],
    ['2.r1-across-2', 't32', 'MATH-500 n=500, T 1.0 / top-p 1.0, grader v3, one sample, with the opening cue: weights base Olmo-3-1025-7B + a*(Olmo-3.1-7B-RL-Zero-Math minus base) with a = 0.25 (call…', 'right of 500', 428, 420, 436, 441, 'w', [[425], [422]], None, ''],
    ['2.r1-across-2', 't33', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 0.5 (theta0.5), number right', 'right of 500', 447, 438, 456, 452, 'w', [[440], [440]], None, ''],
    ['2.r1-across-2', 't43', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the opening cue, one sample: weights base + 0.75*(RL-Zero-Math minus base), number right', 'right of 500', 457, 450, 464, 451, 'l', [[455], [453]], None, ''],
    ['2.r1-across-2', 't34', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 1.5 (theta1.5, extrapolation past RL), numbe…', 'right of 500', 450, 438, 460, 453, 'wu', [[400], [380]], None, ''],
    ['2.r1-across-2', 't45', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the cue: weights base + 1.5*(RL-Zero-Math minus base): number of the 500 answers that end in a word-salad tail', 'answers of 500', 8, 0, 20, 34, 'l', [[30], [40]], None, ''],
    ['2.r1-across-2', 't46', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the opening cue: weights base + 0.25*(RL-Zero-Math minus base): mean generated tokens per problem', 'tokens per problem', 4150, 3980, 4350, 4036, 'l', [[4000], [4050]], None, ''],
    ['2.r1-across-2', 't39', 'Weights base + 0.5*(RL-Zero-Math minus base) with the cue (MATH-500, T 1.0, v3): among the problems the cued base got wrong in its 410/500 cell, the number this cell get…', 'problems', 50, 42, 58, 53, 'w', [[42], [40]], None, ''],
    ['2.r1-across-2', 't36', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 428, 418, 438, 450, 'w', [[420], [415]], None, ''],
    ['2.r1-across-2', 't37', 'Base Olmo-3-1025-7B plus a random difference of matched norm to the RL-minus-base difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: nu…', 'right of 500', 407, 399, 415, 417, 'l', [[408], [408]], None, ''],
    ['2.r1-across-2', 't47', 'Base Olmo-3-1025-7B plus a random matched-norm difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3: mean generated tokens per problem', 'tokens per problem', 3950, 3750, 4150, 3944, 't', [[3950], [3950]], None, ''],
    ['2.r1-across-2', 't19', 'MATH-500 n=500, cued base Olmo-3-1025-7B at T 1.0: AUROC of answer length in tokens as a predictor that the base answer is wrong', 'AUROC', 0.81, 0.77, 0.86, 0.831, 'w', [[0.8], [0.8]], None, ''],
    ['2.r1-across-2', 't22', "J-lens difference between base Olmo-3-1025-7B and RL-Zero-Math (layer 24, same text, n=500 MATH-500 problems): in a reader's check of 90 peaks of the difference, the num…", 'peaks of 90', 10, 3, 20, 10, 'w', [[8], [6]], None, ''],
    ['2.r1-across-2', 't57', 'cleanneurons Part T3, Olmo-3-1025-7B base vs RL-Zero-Math, teacher-forced on held-out 2,672 decisive positions after the cue, on stored cue-base (T1) text: percent of KL…', 'percent', 25, 15, 35, 23.4, 'w', [[15], [12]], None, ''],
    ['2.r1-across-2', 't58', 'Same constant-vector-per-layer arm (32 vectors, mean of RL-layer minus base-layer output), held-out 2,672 decisive positions, but on stored RL-model (T2) text: percent o…', 'percent', 30, 20, 42, 31.2, 'w', [[20], [18]], None, ''],
    ['2.r1-across-2', 't15', "Jacobian lens (J-lens) at layer 24 read on the same stored MATH-500 answer text for 500 problems: share of positions at which the Olmo-3.1-7B-RL-Zero-Math model's readou…", 'percent', 3.0, 1.5, 5.0, 5.64, 'l', [[4], [3.0]], None, ''],
    ['2.r1-across-2', 't16', "Jacobian lens (J-lens) at layer 24 read on the same stored MATH-500 answer text for 500 problems: share of positions at which the base Olmo-3-1025-7B model's readout hol…", 'percent', 1.2, 0.5, 2.0, 4.56, 'l', [[3], [1.5]], None, ''],
    ['2.r1-all-1', 't19', 'MATH-500 n=500, cued base Olmo-3-1025-7B at T 1.0: AUROC of answer length in tokens as a predictor that the base answer is wrong', 'AUROC', 0.85, 0.8, 0.91, 0.831, 'w', [[0.8], [0.8]], None, ''],
    ['2.r1-all-1', 't25', 'Same base+cue hard328 cell (T 1.0 / top-p 1.0, v3): number right under length rule R with cutoff L = 12,000 tokens, as defined in studies/rlneurons/specs/SPEC_day1_lengt…', 'right of 328', 167, 160, 173, 169, 'l', [[172], [167]], None, ''],
    ['2.r1-all-1', 't27', 'Base+cue hard328, T 1.0 / top-p 1.0, v3: number right under a vote over 4 samples per problem (vote@4)', 'right of 328', 170, 163, 178, 179, 'l', [[180], [177]], None, ''],
    ['2.r1-all-1', 't28', 'Base+cue hard328, T 1.0 / top-p 1.0, v3: number of problems with at least one right answer among 4 samples (pass@4, oracle)', 'right of 328', 205, 195, 214, 205, 'wu', [[225], [220]], None, ''],
    ['2.r1-all-1', 't51', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 395, 382, 405, 404, 'wu', [[415], [412]], None, ''],
    ['2.r1-all-1', 't53', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 0.95 (no min-p, v3, one sample): number right', 'right of 500', 397, 385, 406, 409, 'w', [[395], [398]], None, ''],
    ['2.r1-all-1', 't55', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1: number of answers flagged as rule-A loops (an 8,000-character window starting at a line start with zlib…', 'answers of 500', 12, 4, 30, 34, 'w', [[10], [12]], None, ''],
    ['2.r1-all-1', 't56', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1 (v3): number of answers that hit the token cap', 'cap hits of 500', 50, 35, 70, 58, 'w', [[40], [45]], None, ''],
    ['2.r1-all-1', 't57', 'cleanneurons Part T3, Olmo-3-1025-7B base vs RL-Zero-Math, teacher-forced on held-out 2,672 decisive positions after the cue, on stored cue-base (T1) text: percent of KL…', 'percent', 8, 2, 15, 23.4, 'l', [[15], [12]], None, ''],
    ['2.r1-all-1', 't58', 'Same constant-vector-per-layer arm (32 vectors, mean of RL-layer minus base-layer output), held-out 2,672 decisive positions, but on stored RL-model (T2) text: percent o…', 'percent', 8, 2, 15, 31.2, 'l', [[20], [18]], None, ''],
    ['2.r1-all-1', 't59', 'Olmo-3 base, T1 (cued-base) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by adding a constant vector on the MLP output only (mean of RL minus…', 'percent', 6, 1, 12, 14.0, 'l', [[10], [7]], None, ''],
    ['2.r1-all-1', 't60', 'Olmo-3 base, T2 (RL-model) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by adding a constant vector on the MLP output only (mean of RL minus b…', 'percent', 6, 1, 12, 15.1, 'l', [[14], [11]], None, ''],
    ['2.r1-all-2', 't06', "Base Olmo-3-1025-7B, plain prompt, MATH-500 n=500, T 0.6: number of the 500 answers that open on their own with the cue string '.', blank line, 'Okay'", 'answers of 500', 3, 0, 10, 168, 'w', [[2], [2]], None, ''],
    ['2.r1-all-2', 't32', 'MATH-500 n=500, T 1.0 / top-p 1.0, grader v3, one sample, with the opening cue: weights base Olmo-3-1025-7B + a*(Olmo-3.1-7B-RL-Zero-Math minus base) with a = 0.25 (call…', 'right of 500', 415, 405, 428, 441, 'l', [[425], [422]], None, ''],
    ['2.r1-all-2', 't33', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 0.5 (theta0.5), number right', 'right of 500', 435, 422, 448, 452, 'l', [[440], [440]], None, ''],
    ['2.r1-all-2', 't35', 'Olmo-3.1-7B-RL-Zero-Math with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 463, 455, 470, 457, 'l', [[462], [461]], None, ''],
    ['2.r1-all-2', 't36', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 408, 395, 420, 450, 'l', [[420], [415]], None, ''],
    ['2.r1-all-2', 't37', 'Base Olmo-3-1025-7B plus a random difference of matched norm to the RL-minus-base difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: nu…', 'right of 500', 405, 390, 418, 417, 'l', [[408], [408]], None, ''],
    ['2.r1-all-2', 't40', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, plain prompt (no cue), one sample: weights base Olmo-3-1025-7B + 0.25*(RL-Zero-Math minus base), number right', 'right of 500', 370, 340, 400, 405, 'w', [[300], [290]], None, ''],
    ['2.r1-all-2', 't41', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, plain prompt (no cue), one sample: weights base + 0.5*(RL-Zero-Math minus base), number right', 'right of 500', 432, 415, 450, 443, 'wu', [[400], [380]], None, ''],
    ['2.r1-all-2', 't42', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the plain prompt (no cue), MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 315, 275, 355, 390, 'w', [[280], [290]], None, ''],
    ['2.r1-all-2', 't57', 'cleanneurons Part T3, Olmo-3-1025-7B base vs RL-Zero-Math, teacher-forced on held-out 2,672 decisive positions after the cue, on stored cue-base (T1) text: percent of KL…', 'percent', 25, 15, 35, 23.4, 'w', [[15], [12]], None, ''],
    ['2.r1-all-2', 't58', 'Same constant-vector-per-layer arm (32 vectors, mean of RL-layer minus base-layer output), held-out 2,672 decisive positions, but on stored RL-model (T2) text: percent o…', 'percent', 35, 25, 45, 31.2, 'wu', [[20], [18]], None, ''],
    ['2.r1-all-2', 't59', 'Olmo-3 base, T1 (cued-base) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by adding a constant vector on the MLP output only (mean of RL minus…', 'percent', 20, 12, 30, 14.0, 'lu', [[10], [7]], None, ''],
    ['2.r1-all-2', 't60', 'Olmo-3 base, T2 (RL-model) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by adding a constant vector on the MLP output only (mean of RL minus b…', 'percent', 28, 18, 38, 15.1, 'l', [[14], [11]], None, ''],
    ['2.r1-surprises-1', 't05', "Olmo-3.1-7B-RL-Zero-Math, MATH-500 n=500, T 0.6: number of the 500 answers that begin with one of four opening tokens (' line', '!' plus blank line, 'Okay', ',')", 'answers of 500', 485, 455, 500, 494, 'w', [[470], [465]], None, ''],
    ['2.r1-surprises-1', 't22', "J-lens difference between base Olmo-3-1025-7B and RL-Zero-Math (layer 24, same text, n=500 MATH-500 problems): in a reader's check of 90 peaks of the difference, the num…", 'peaks of 90', 8, 0, 15, 10, 'w', [[8], [6]], None, ''],
    ['2.r1-surprises-1', 't27', 'Base+cue hard328, T 1.0 / top-p 1.0, v3: number right under a vote over 4 samples per problem (vote@4)', 'right of 328', 186, 176, 198, 179, 'l', [[180], [177]], None, ''],
    ['2.r1-surprises-1', 't28', 'Base+cue hard328, T 1.0 / top-p 1.0, v3: number of problems with at least one right answer among 4 samples (pass@4, oracle)', 'right of 328', 218, 206, 235, 205, 'w', [[225], [220]], None, ''],
    ['2.r1-surprises-1', 't35', 'Olmo-3.1-7B-RL-Zero-Math with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 463, 454, 471, 457, 'l', [[462], [461]], None, ''],
    ['2.r1-surprises-1', 't36', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 410, 395, 428, 450, 'l', [[420], [415]], None, ''],
    ['2.r1-surprises-1', 't42', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the plain prompt (no cue), MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 340, 285, 400, 390, 'w', [[280], [290]], None, ''],
    ['2.r1-surprises-1', 't54', 'Olmo-3.1-7B-RL-Zero-Math with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 462, 453, 471, 460, 'w', [[462], [463]], None, ''],
    ['2.r1-surprises-2', 't22', "J-lens difference between base Olmo-3-1025-7B and RL-Zero-Math (layer 24, same text, n=500 MATH-500 problems): in a reader's check of 90 peaks of the difference, the num…", 'peaks of 90', 6, 0, 14, 10, 'l', [[8], [6]], None, ''],
    ['2.r1-surprises-2', 't32', 'MATH-500 n=500, T 1.0 / top-p 1.0, grader v3, one sample, with the opening cue: weights base Olmo-3-1025-7B + a*(Olmo-3.1-7B-RL-Zero-Math minus base) with a = 0.25 (call…', 'right of 500', 430, 419, 442, 441, 'w', [[425], [422]], None, ''],
    ['2.r1-surprises-2', 't33', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 0.5 (theta0.5), number right', 'right of 500', 446, 436, 456, 452, 'w', [[440], [440]], None, ''],
    ['2.r1-surprises-2', 't43', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the opening cue, one sample: weights base + 0.75*(RL-Zero-Math minus base), number right', 'right of 500', 456, 447, 466, 451, 'l', [[455], [453]], None, ''],
    ['2.r1-surprises-2', 't34', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 1.5 (theta1.5, extrapolation past RL), numbe…', 'right of 500', 450, 432, 466, 453, 'wu', [[400], [380]], None, ''],
    ['2.r1-surprises-2', 't45', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the cue: weights base + 1.5*(RL-Zero-Math minus base): number of the 500 answers that end in a word-salad tail', 'answers of 500', 4, 0, 15, 34, 'l', [[30], [40]], None, ''],
    ['2.r1-surprises-2', 't40', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, plain prompt (no cue), one sample: weights base Olmo-3-1025-7B + 0.25*(RL-Zero-Math minus base), number right', 'right of 500', 310, 270, 350, 405, 'w', [[300], [290]], None, ''],
    ['2.r1-surprises-2', 't41', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, plain prompt (no cue), one sample: weights base + 0.5*(RL-Zero-Math minus base), number right', 'right of 500', 398, 370, 425, 443, 'w', [[400], [380]], None, ''],
    ['2.r1-surprises-2', 't46', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the opening cue: weights base + 0.25*(RL-Zero-Math minus base): mean generated tokens per problem', 'tokens per problem', 4120, 3950, 4350, 4036, 'l', [[4000], [4050]], None, ''],
    ['2.r1-surprises-2', 't37', 'Base Olmo-3-1025-7B plus a random difference of matched norm to the RL-minus-base difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: nu…', 'right of 500', 410, 398, 422, 417, 'w', [[408], [408]], None, ''],
    ['2.r1-surprises-2', 't38', 'Base plus a random matched-norm difference with the cue (MATH-500, T 1.0, v3): among the problems the cued base Olmo-3-1025-7B got wrong in its 410/500 cell, the number…', 'problems', 25, 16, 34, 42, 'l', [[28], [30]], None, ''],
    ['2.r1-surprises-2', 't39', 'Weights base + 0.5*(RL-Zero-Math minus base) with the cue (MATH-500, T 1.0, v3): among the problems the cued base got wrong in its 410/500 cell, the number this cell get…', 'problems', 50, 40, 61, 53, 'w', [[42], [40]], None, ''],
    ['2.r1-surprises-2', 't47', 'Base Olmo-3-1025-7B plus a random matched-norm difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3: mean generated tokens per problem', 'tokens per problem', 3930, 3700, 4180, 3944, 'l', [[3950], [3950]], None, ''],
    ['2.r1-surprises-2', 't57', 'cleanneurons Part T3, Olmo-3-1025-7B base vs RL-Zero-Math, teacher-forced on held-out 2,672 decisive positions after the cue, on stored cue-base (T1) text: percent of KL…', 'percent', 30, 18, 45, 23.4, 'wu', [[15], [12]], None, ''],
    ['2.r1-surprises-2', 't58', 'Same constant-vector-per-layer arm (32 vectors, mean of RL-layer minus base-layer output), held-out 2,672 decisive positions, but on stored RL-model (T2) text: percent o…', 'percent', 40, 26, 55, 31.2, 'wu', [[20], [18]], None, ''],
    ['2.r1-surprises-2', 't59', 'Olmo-3 base, T1 (cued-base) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by adding a constant vector on the MLP output only (mean of RL minus…', 'percent', 20, 10, 32, 14.0, 'l', [[10], [7]], None, ''],
    ['2.r1-surprises-2', 't60', 'Olmo-3 base, T2 (RL-model) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by adding a constant vector on the MLP output only (mean of RL minus b…', 'percent', 28, 16, 40, 15.1, 'l', [[14], [11]], None, ''],
    ['2.r1-surprises-2', 't61', 'Olmo-3 base, T1 (cued-base) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by copying the 472 always-on neurons (0.13 % of 352,256 MLP neurons)…', 'percent', 3, 0.5, 7, 2.6, 'w', [[2.5], [4]], None, ''],
    ['2.r1-surprises-2', 't62', 'Olmo-3 base, T2 (RL-model) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by copying the 472 always-on neurons (0.13 % of 352,256 MLP neurons) f…', 'percent', 4, 0.5, 9, 3.4, 'w', [[3.5], [5]], None, ''],
    ['2.r2-across-1', 't51', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 398, 383, 410, 404, 'wu', [[415], [412]], None, ''],
    ['2.r2-across-1', 't52', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.5 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 370, 340, 392, 412, 'l', [[400], [395]], None, ''],
    ['2.r2-across-1', 't53', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 0.95 (no min-p, v3, one sample): number right', 'right of 500', 400, 389, 409, 409, 'w', [[395], [398]], None, ''],
    ['2.r2-across-1', 't54', 'Olmo-3.1-7B-RL-Zero-Math with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 463, 454, 471, 460, 'l', [[462], [463]], None, ''],
    ['2.r2-across-1', 't55', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1: number of answers flagged as rule-A loops (an 8,000-character window starting at a line start with zlib…', 'answers of 500', 20, 8, 45, 34, 'w', [[10], [12]], None, ''],
    ['2.r2-across-1', 't56', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1 (v3): number of answers that hit the token cap', 'cap hits of 500', 50, 35, 75, 58, 'w', [[40], [45]], None, ''],
    ['2.r2-across-2', 't37', 'Base Olmo-3-1025-7B plus a random difference of matched norm to the RL-minus-base difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: nu…', 'right of 500', 409, 397, 421, 417, 'w', [[408], [408]], None, ''],
    ['2.r2-across-2', 't38', 'Base plus a random matched-norm difference with the cue (MATH-500, T 1.0, v3): among the problems the cued base Olmo-3-1025-7B got wrong in its 410/500 cell, the number…', 'problems', 25, 16, 34, 42, 'l', [[28], [30]], None, ''],
    ['2.r2-across-2', 't47', 'Base Olmo-3-1025-7B plus a random matched-norm difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3: mean generated tokens per problem', 'tokens per problem', 3950, 3650, 4250, 3944, 't', [[3950], [3950]], None, ''],
    ['2.r2-across-2', 't32', 'MATH-500 n=500, T 1.0 / top-p 1.0, grader v3, one sample, with the opening cue: weights base Olmo-3-1025-7B + a*(Olmo-3.1-7B-RL-Zero-Math minus base) with a = 0.25 (call…', 'right of 500', 440, 428, 452, 441, 'wu', [[425], [422]], None, ''],
    ['2.r2-across-2', 't33', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 0.5 (theta0.5), number right', 'right of 500', 452, 443, 461, 452, 'wu', [[440], [440]], None, ''],
    ['2.r2-across-2', 't43', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the opening cue, one sample: weights base + 0.75*(RL-Zero-Math minus base), number right', 'right of 500', 460, 452, 468, 451, 'l', [[455], [453]], None, ''],
    ['2.r2-across-2', 't34', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 1.5 (theta1.5, extrapolation past RL), numbe…', 'right of 500', 458, 444, 470, 453, 'wu', [[400], [380]], None, ''],
    ['2.r2-across-2', 't45', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the cue: weights base + 1.5*(RL-Zero-Math minus base): number of the 500 answers that end in a word-salad tail', 'answers of 500', 4, 0, 15, 34, 'l', [[30], [40]], None, ''],
    ['2.r2-across-2', 't40', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, plain prompt (no cue), one sample: weights base Olmo-3-1025-7B + 0.25*(RL-Zero-Math minus base), number right', 'right of 500', 360, 330, 390, 405, 'w', [[300], [290]], None, ''],
    ['2.r2-across-2', 't41', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, plain prompt (no cue), one sample: weights base + 0.5*(RL-Zero-Math minus base), number right', 'right of 500', 415, 395, 435, 443, 'w', [[400], [380]], None, ''],
    ['2.r2-across-2', 't39', 'Weights base + 0.5*(RL-Zero-Math minus base) with the cue (MATH-500, T 1.0, v3): among the problems the cued base got wrong in its 410/500 cell, the number this cell get…', 'problems', 52, 42, 62, 53, 'w', [[42], [40]], None, ''],
    ['2.r2-across-2', 't36', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 412, 393, 428, 450, 'l', [[420], [415]], None, ''],
    ['2.r2-across-2', 't42', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the plain prompt (no cue), MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 245, 200, 295, 390, 'l', [[280], [290]], None, ''],
    ['2.r2-across-2', 't61', 'Olmo-3 base, T1 (cued-base) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by copying the 472 always-on neurons (0.13 % of 352,256 MLP neurons)…', 'percent', 1.0, 0.2, 4.0, 2.6, 'l', [[2.5], [4]], None, ''],
    ['2.r2-across-2', 't62', 'Olmo-3 base, T2 (RL-model) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by copying the 472 always-on neurons (0.13 % of 352,256 MLP neurons) f…', 'percent', 1.2, 0.2, 4.0, 3.4, 'l', [[3.5], [5]], None, ''],
    ['2.r2-all-1', 't37', 'Base Olmo-3-1025-7B plus a random difference of matched norm to the RL-minus-base difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: nu…', 'right of 500', 409, 399, 419, 417, 'w', [[408], [408]], None, ''],
    ['2.r2-all-1', 't38', 'Base plus a random matched-norm difference with the cue (MATH-500, T 1.0, v3): among the problems the cued base Olmo-3-1025-7B got wrong in its 410/500 cell, the number…', 'problems', 30, 21, 40, 42, 'w', [[28], [30]], None, ''],
    ['2.r2-all-1', 't47', 'Base Olmo-3-1025-7B plus a random matched-norm difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3: mean generated tokens per problem', 'tokens per problem', 3950, 3700, 4200, 3944, 't', [[3950], [3950]], None, ''],
    ['2.r2-all-1', 't42', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the plain prompt (no cue), MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 230, 205, 255, 390, 'l', [[280], [290]], None, ''],
    ['2.r2-all-1', 't36', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 408, 394, 420, 450, 'l', [[420], [415]], None, ''],
    ['2.r2-all-2', 't53', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 0.95 (no min-p, v3, one sample): number right', 'right of 500', 398, 386, 408, 409, 'w', [[395], [398]], None, ''],
    ['2.r2-all-2', 't51', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 390, 372, 404, 404, 'lu', [[415], [412]], None, ''],
    ['2.r2-all-2', 't55', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1: number of answers flagged as rule-A loops (an 8,000-character window starting at a line start with zlib…', 'answers of 500', 22, 10, 40, 34, 'w', [[10], [12]], None, ''],
    ['2.r2-all-2', 't56', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1 (v3): number of answers that hit the token cap', 'cap hits of 500', 55, 40, 80, 58, 'w', [[40], [45]], None, ''],
    ['2.r2-all-2', 't52', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.5 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 400, 385, 415, 412, 'w', [[400], [395]], None, ''],
    ['2.r2-all-2', 't54', 'Olmo-3.1-7B-RL-Zero-Math with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 462, 453, 471, 460, 'w', [[462], [463]], None, ''],
    ['2.r2-all-2', 't09', 'Grader v1/v2 applied to plain-prompt base Olmo-3-1025-7B answers on MATH-500 n=500 at T 1.0: number of the 500 answers in which the grader found no extractable answer', 'answers of 500', 130, 95, 170, 166, 'wu', [[45], [60]], None, ''],
    ['2.r2-all-2', 't10', 'Grader v1/v2 applied to plain-prompt base Olmo-3-1025-7B answers on MATH-500 n=500 at T 0.6: number of the 500 answers in which the grader found no extractable answer', 'answers of 500', 75, 58, 95, 127, 'l', [[70], [85]], None, ''],
    ['2.r2-external-1', 't37', 'Base Olmo-3-1025-7B plus a random difference of matched norm to the RL-minus-base difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: nu…', 'right of 500', 410, 397, 422, 417, 'w', [[408], [408]], None, ''],
    ['2.r2-external-1', 't38', 'Base plus a random matched-norm difference with the cue (MATH-500, T 1.0, v3): among the problems the cued base Olmo-3-1025-7B got wrong in its 410/500 cell, the number…', 'problems', 31, 21, 42, 42, 'w', [[28], [30]], None, ''],
    ['2.r2-external-1', 't47', 'Base Olmo-3-1025-7B plus a random matched-norm difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3: mean generated tokens per problem', 'tokens per problem', 3930, 3650, 4250, 3944, 'l', [[3950], [3950]], None, ''],
    ['2.r2-external-1', 't34', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 1.5 (theta1.5, extrapolation past RL), numbe…', 'right of 500', 445, 425, 465, 453, 'wu', [[400], [380]], None, ''],
    ['2.r2-external-1', 't45', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the cue: weights base + 1.5*(RL-Zero-Math minus base): number of the 500 answers that end in a word-salad tail', 'answers of 500', 8, 0, 25, 34, 'l', [[30], [40]], None, ''],
    ['2.r2-external-2', 't51', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 424, 414, 438, 404, 'l', [[415], [412]], None, ''],
    ['2.r2-external-2', 't52', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.5 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 412, 398, 428, 412, 'w', [[400], [395]], None, ''],
    ['2.r2-external-2', 't53', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / top-p 0.95 (no min-p, v3, one sample): number right', 'right of 500', 418, 409, 430, 409, 'wu', [[395], [398]], None, ''],
    ['2.r2-external-2', 't54', 'Olmo-3.1-7B-RL-Zero-Math with cue, MATH-500 n=500, T 1.0 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 463, 455, 471, 460, 'l', [[462], [463]], None, ''],
    ['2.r2-external-2', 't55', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1: number of answers flagged as rule-A loops (an 8,000-character window starting at a line start with zlib…', 'answers of 500', 2, 0, 8, 34, 'l', [[10], [12]], None, ''],
    ['2.r2-external-2', 't56', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1 (v3): number of answers that hit the token cap', 'cap hits of 500', 21, 12, 30, 58, 'l', [[40], [45]], None, ''],
    ['2.r2-revise-1', 't32', 'MATH-500 n=500, T 1.0 / top-p 1.0, grader v3, one sample, with the opening cue: weights base Olmo-3-1025-7B + a*(Olmo-3.1-7B-RL-Zero-Math minus base) with a = 0.25 (call…', 'right of 500', 427, 420, 434, 441, 'w', [[425], [422]], None, ''],
    ['2.r2-revise-1', 't33', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 0.5 (theta0.5), number right', 'right of 500', 442, 435, 449, 452, 'w', [[440], [440]], None, ''],
    ['2.r2-revise-1', 't43', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, with the opening cue, one sample: weights base + 0.75*(RL-Zero-Math minus base), number right', 'right of 500', 453, 446, 460, 451, 'w', [[455], [453]], None, ''],
    ['2.r2-revise-1', 't34', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample, with the opening cue: weights base + a*(RL-Zero-Math minus base) with a = 1.5 (theta1.5, extrapolation past RL), numbe…', 'right of 500', 466, 452, 478, 453, 'wu', [[400], [380]], None, ''],
    ['2.r2-revise-1', 't40', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, plain prompt (no cue), one sample: weights base Olmo-3-1025-7B + 0.25*(RL-Zero-Math minus base), number right', 'right of 500', 308, 278, 340, 405, 'w', [[300], [290]], None, ''],
    ['2.r2-revise-1', 't41', 'MATH-500 n=500, T 1.0 / top-p 1.0, v3, plain prompt (no cue), one sample: weights base + 0.5*(RL-Zero-Math minus base), number right', 'right of 500', 380, 358, 402, 443, 'l', [[400], [380]], None, ''],
    ['2.r2-revise-1', 't36', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 406, 392, 420, 450, 'l', [[420], [415]], None, ''],
    ['2.r2-revise-1', 't42', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the plain prompt (no cue), MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 245, 212, 285, 390, 'l', [[280], [290]], None, ''],
    ['2.r2-revise-1', 't37', 'Base Olmo-3-1025-7B plus a random difference of matched norm to the RL-minus-base difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: nu…', 'right of 500', 408, 394, 422, 417, 't', [[408], [408]], None, ''],
    ['2.r2-revise-1', 't47', 'Base Olmo-3-1025-7B plus a random matched-norm difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3: mean generated tokens per problem', 'tokens per problem', 3930, 3680, 4180, 3944, 'l', [[3950], [3950]], None, ''],
    ['2.r2-revise-2', 't27', 'Base+cue hard328, T 1.0 / top-p 1.0, v3: number right under a vote over 4 samples per problem (vote@4)', 'right of 328', 189, 180, 198, 179, 'l', [[180], [177]], None, ''],
    ['2.r2-revise-2', 't28', 'Base+cue hard328, T 1.0 / top-p 1.0, v3: number of problems with at least one right answer among 4 samples (pass@4, oracle)', 'right of 328', 222, 210, 235, 205, 'w', [[225], [220]], None, ''],
    ['2.r2-surprises-1', 't09', 'Grader v1/v2 applied to plain-prompt base Olmo-3-1025-7B answers on MATH-500 n=500 at T 1.0: number of the 500 answers in which the grader found no extractable answer', 'answers of 500', 95, 65, 140, 166, 'w', [[45], [60]], None, ''],
    ['2.r2-surprises-1', 't52', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.5 / top-p 1.0 / min-p 0.1 (v3, one sample): number right', 'right of 500', 388, 365, 404, 412, 'l', [[400], [395]], None, ''],
    ['2.r2-surprises-1', 't55', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1: number of answers flagged as rule-A loops (an 8,000-character window starting at a line start with zlib…', 'answers of 500', 10, 3, 30, 34, 'l', [[10], [12]], None, ''],
    ['2.r2-surprises-1', 't56', 'Base Olmo-3-1025-7B with cue, MATH-500 n=500, T 1.0 / min-p 0.1 (v3): number of answers that hit the token cap', 'cap hits of 500', 42, 31, 65, 58, 'l', [[40], [45]], None, ''],
    ['2.r2-surprises-2', 't57', 'cleanneurons Part T3, Olmo-3-1025-7B base vs RL-Zero-Math, teacher-forced on held-out 2,672 decisive positions after the cue, on stored cue-base (T1) text: percent of KL…', 'percent', 8, 2, 16, 23.4, 'l', [[15], [12]], None, ''],
    ['2.r2-surprises-2', 't58', 'Same constant-vector-per-layer arm (32 vectors, mean of RL-layer minus base-layer output), held-out 2,672 decisive positions, but on stored RL-model (T2) text: percent o…', 'percent', 10, 3, 19, 31.2, 'l', [[20], [18]], None, ''],
    ['2.r2-surprises-2', 't59', 'Olmo-3 base, T1 (cued-base) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by adding a constant vector on the MLP output only (mean of RL minus…', 'percent', 6, 1, 14, 14.0, 'l', [[10], [7]], None, ''],
    ['2.r2-surprises-2', 't60', 'Olmo-3 base, T2 (RL-model) text, held-out 2,672 decisive positions: percent of KL(RL||base) closed by adding a constant vector on the MLP output only (mean of RL minus b…', 'percent', 8, 2, 16, 15.1, 'l', [[14], [11]], None, ''],
    ['2.r2-surprises-2', 't42', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the plain prompt (no cue), MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 235, 205, 265, 390, 'l', [[280], [290]], None, ''],
    ['2.r2-surprises-2', 't36', 'Olmo-3.1-7B-RL-Zero-Code (Code-RL) with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: number right', 'right of 500', 405, 390, 422, 450, 'l', [[420], [415]], None, ''],
    ['2.r2-surprises-2', 't37', 'Base Olmo-3-1025-7B plus a random difference of matched norm to the RL-minus-base difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3, one sample: nu…', 'right of 500', 408, 396, 420, 417, 't', [[408], [408]], None, ''],
    ['2.r2-surprises-2', 't47', 'Base Olmo-3-1025-7B plus a random matched-norm difference, with the opening cue, MATH-500 n=500, T 1.0 / top-p 1.0, v3: mean generated tokens per problem', 'tokens per problem', 3950, 3750, 4150, 3944, 't', [[3950], [3950]], None, ''],
    ['2.r2-surprises-2', 't22', "J-lens difference between base Olmo-3-1025-7B and RL-Zero-Math (layer 24, same text, n=500 MATH-500 problems): in a reader's check of 90 peaks of the difference, the num…", 'peaks of 90', 6, 1, 14, 10, 'l', [[8], [6]], None, ''],
    ['3.r1-all-2', 't01', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + top 8 singular directions per layer matrix of the RL-Math (Olmo…', 'right of 100', 77, 64, 89, 88, 'w', [[62, 42, 84], [68, 45, 87]], 1.0346, ''],
    ['3.r1-all-2', 't44', 'MATH-500 n=500, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + top 8 singular directions per layer matrix of the RL-Math delta, right of 500', 'right of 500', 380, 330, 425, 427, 'w', [[300, 210, 415], [330, 230, 425]], 1.0519, ''],
    ['3.r1-all-2', 't49', 'MATH-500 n=500, T 1.0 / top-p 1.0, plain, v3, base + top 8 singular directions per matrix of RL-Math delta, tokens per problem', 'tokens per problem', 3600, 3000, 4300, 3962, 'w', [[3000, 1800, 4500], [3800, 2600, 5200]], 0.5857, ''],
    ['3.r1-all-2', 't03', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, RL-Math model with its top 8 singular directions per layer matrix of the delt…', 'right of 100', 91, 85, 97, 91, 'w', [[88, 77, 96], [86, 72, 95]], 0.7383, ''],
    ['3.r1-all-2', 't48', 'first 100 MATH-500, T 1.0 / top-p 1.0, plain, v3, base + bulk64 (RL delta minus top 64 directions) screen, right of 100', 'right of 100', 89, 81, 96, 86, 'wu', [[80, 60, 93], [80, 55, 93]], 0.7983, ''],
    ['3.r1-all-2', 't04', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + top 3 singular directions of the RL-Math delta in late MLP matr…', 'right of 100', 48, 36, 61, 41, 'w', [[47, 33, 62], [51, 38, 68]], 0.1373, ''],
    ['3.r1-all-2', 't43', 'MATH-500 n=500, grader v3 minus grader v1 on the same answers, Olmo-3.1-7B-RL-Zero-Math: extra problems counted right', 'problems', 4, 0, 9, 5, 'w', [[4, 0, 9], [3, 0, 9]], 0.0952, ''],
    ['3.r1-all-2', 't39', 'MATH-500 n=500, plain prompt, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Mix, right of 500', 'right of 500', 438, 405, 462, 372, 'l', [[415, 350, 460], [415, 330, 460]], -3.0, ''],
    ['3.r1-all-2', 't40', 'MATH-500 n=500, plain prompt, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Code, right of 500', 'right of 500', 365, 295, 425, 360, 'w', [[340, 250, 410], [355, 270, 430]], 0.2438, ''],
    ['3.r1-all-2', 't34', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Math (3.0 release), right of 500', 'right of 500', 443, 418, 462, 448, 'w', [[405, 360, 445], [430, 393, 457]], 1.172, ''],
    ['3.r1-all-2', 't35', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Mix, right of 500', 'right of 500', 445, 418, 463, 440, 'w', [[430, 390, 460], [438, 403, 462]], 0.3384, ''],
    ['3.r1-all-2', 't37', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Code (3.0), right of 500', 'right of 500', 435, 405, 458, 411, 'l', [[420, 370, 455], [425, 380, 455]], -0.5754, ''],
    ['3.r1-surprises-2', 't01', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + top 8 singular directions per layer matrix of the RL-Math (Olmo…', 'right of 100', 82, 70, 92, 88, 'wu', [[62, 42, 84], [68, 45, 87]], 1.8076, ''],
    ['3.r1-surprises-2', 't44', 'MATH-500 n=500, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + top 8 singular directions per layer matrix of the RL-Math delta, right of 500', 'right of 500', 412, 370, 445, 427, 'wu', [[300, 210, 415], [330, 230, 425]], 2.3965, ''],
    ['3.r1-surprises-2', 't02', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + matched random rank-8 control delta (same layer matrices as top…', 'right of 100', 46, 36, 57, 36, 'w', [[46, 33, 59], [48, 36, 61]], -0.0301, ''],
    ['3.r1-surprises-2', 't03', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, RL-Math model with its top 8 singular directions per layer matrix of the delt…', 'right of 100', 55, 42, 70, 91, 'l', [[88, 77, 96], [86, 72, 95]], -3.0, ''],
    ['3.r1-surprises-2', 't48', 'first 100 MATH-500, T 1.0 / top-p 1.0, plain, v3, base + bulk64 (RL delta minus top 64 directions) screen, right of 100', 'right of 100', 50, 37, 63, 86, 'l', [[80, 60, 93], [80, 55, 93]], -3.0, ''],
    ['3.r1-surprises-2', 't47', 'first 100 MATH-500, T 1.0 / top-p 1.0, plain, v3, base + only top 1 singular direction per matrix of RL-Math delta, right of 100', 'right of 100', 70, 55, 85, 42, 'l', [[50, 36, 68], [55, 40, 76]], -3.0, ''],
    ['3.r1-surprises-2', 't04', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + top 3 singular directions of the RL-Math delta in late MLP matr…', 'right of 100', 52, 38, 66, 41, 'l', [[47, 33, 62], [51, 38, 68]], -0.387, ''],
    ['3.r1-surprises-2', 't49', 'MATH-500 n=500, T 1.0 / top-p 1.0, plain, v3, base + top 8 singular directions per matrix of RL-Math delta, tokens per problem', 'tokens per problem', 4300, 3600, 5000, 3962, 'w', [[3000, 1800, 4500], [3800, 2600, 5200]], 0.6158, ''],
    ['3.r2-across-2', 't01', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + top 8 singular directions per layer matrix of the RL-Math (Olmo…', 'right of 100', 58, 44, 72, 88, 'l', [[62, 42, 84], [68, 45, 87]], -3.0, ''],
    ['3.r2-across-2', 't44', 'MATH-500 n=500, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + top 8 singular directions per layer matrix of the RL-Math delta, right of 500', 'right of 500', 305, 250, 360, 427, 'l', [[300, 210, 415], [330, 230, 425]], -3.0, ''],
    ['3.r2-across-2', 't02', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + matched random rank-8 control delta (same layer matrices as top…', 'right of 100', 45, 33, 57, 36, 'w', [[46, 33, 59], [48, 36, 61]], 0.3026, ''],
    ['3.r2-across-2', 't03', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, RL-Math model with its top 8 singular directions per layer matrix of the delt…', 'right of 100', 90, 84, 96, 91, 'w', [[88, 77, 96], [86, 72, 95]], 0.7007, ''],
    ['3.r2-across-2', 't04', 'right of first 100 MATH-500 problems, T 1.0 / top-p 1.0, plain prompt, grader v3, 1 sample, Olmo-3 base + top 3 singular directions of the RL-Math delta in late MLP matr…', 'right of 100', 46, 34, 58, 41, 'w', [[47, 33, 62], [51, 38, 68]], 0.3676, ''],
    ['3.r2-across-2', 't47', 'first 100 MATH-500, T 1.0 / top-p 1.0, plain, v3, base + only top 1 singular direction per matrix of RL-Math delta, right of 100', 'right of 100', 48, 36, 60, 42, 'w', [[50, 36, 68], [55, 40, 76]], 0.5012, ''],
    ['3.r2-across-2', 't48', 'first 100 MATH-500, T 1.0 / top-p 1.0, plain, v3, base + bulk64 (RL delta minus top 64 directions) screen, right of 100', 'right of 100', 87, 79, 95, 86, 'w', [[80, 60, 93], [80, 55, 93]], 0.9291, ''],
    ['3.r3-across-1', 't26', 'hard328 (328 harder problems), T 1.0 / top-p 1.0, cue, grader v3, 1 sample, theta(0.25) = base + 0.25 (RL - base)', 'right of 328', 180, 170, 190, 182, 'w', [[186, 170, 201], [186, 171, 201]], 0.4608, ''],
    ['3.r3-across-1', 't27', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, theta(0.5) = base + 0.5 (RL - base)', 'right of 328', 187, 177, 197, 190, 'w', [[196, 181, 210], [196, 182, 210]], 0.4723, ''],
    ['3.r3-across-1', 't28', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, Olmo-3.1-7B-RL-Zero-Code', 'right of 328', 176, 166, 187, 187, 'lu', [[188, 170, 205], [188, 170, 205]], -0.9697, ''],
    ['3.r3-across-1', 't31', 'hard328, T 1.0, cue, v3, theta(0.5) minus RL plain (paired difference)', 'points', -5.8, -9.5, -2.0, -4.9, 'w', [[-3.0, -8.0, 2.0], [-3.0, -7.5, 1.5]], 0.3749, ''],
    ['3.r3-across-1', 't32', 'hard328, T 1.0, cue, v3, Olmo-3.1-7B-RL-Zero-Code minus RL plain (paired difference)', 'points', -9.1, -13.0, -5.0, -5.8, 'l', [[-5.5, -11.5, 0.5], [-5.5, -11, -0.5]], -0.5805, ''],
    ['3.r3-across-1', 't33', 'hard328, T 1.0, cue, v3, Code-RL minus theta(0.5) (paired difference)', 'points', -3.4, -7.0, 0.5, -0.9, 'l', [[-2.5, -8.0, 3.0], [-2.5, -8, 3]], -0.1038, ''],
    ['3.r3-across-2', 't13', 'wrong-result twins n=300: RL minus base difference in hold-on log-prob rise after wrong arithmetic result', 'nats', 0.0, -0.25, 0.25, 0.066, 'w', [[0.15, -0.3, 0.6], [0.2, -0.35, 0.8]], 0.6672, ''],
    ['3.r3-all-1', 't26', 'hard328 (328 harder problems), T 1.0 / top-p 1.0, cue, grader v3, 1 sample, theta(0.25) = base + 0.25 (RL - base)', 'right of 328', 176, 166, 187, 182, 'l', [[186, 170, 201], [186, 171, 201]], 0.0243, ''],
    ['3.r3-all-1', 't28', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, Olmo-3.1-7B-RL-Zero-Code', 'right of 328', 173, 163, 184, 187, 'l', [[188, 170, 205], [188, 170, 205]], -1.8901, ''],
    ['3.r3-all-1', 't32', 'hard328, T 1.0, cue, v3, Olmo-3.1-7B-RL-Zero-Code minus RL plain (paired difference)', 'points', -10, -14, -6, -5.8, 'l', [[-5.5, -11.5, 0.5], [-5.5, -11, -0.5]], -1.1513, ''],
    ['3.r3-all-1', 't29', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, Olmo-3.1-7B-RL-Zero-Code, tokens per problem', 'tokens per problem', 7900, 6600, 9200, 7613, 'l', [[7900, 6000, 9800], [7200, 5500, 9200]], 0.3493, ''],
    ['3.r3-all-2', 't17', 'MATH-500 n=500, T 1.0 / top-p 1.0, cue, one self-review pass, grader v3 raw, Olmo-3.1-7B-RL-Zero-Math, right of 500 after review (before review 457)', 'right of 500', 457, 452, 462, 446, 'l', [[455, 440, 468], [446, 405, 464]], -1.6271, ''],
    ['3.r3-all-2', 't24', 'MATH-500 n=500, T 1.0, v3, Olmo-3.1-7B-RL-Zero-Math plain, 4-sample vote with ties to the shortest finished sample, right of 500', 'right of 500', 474, 470, 478, 475, 'l', [[475, 467, 482], [475, 467, 481]], -0.0201, ''],
    ['3.r3-all-2', 't25', 'MATH-500 n=500, T 1.0, v3, Olmo-3.1-7B-RL-Zero-Math plain, 4-sample vote with ties to the longest sample (control), right of 500', 'right of 500', 472, 467, 477, 476, 'w', [[470, 460, 478], [471, 462, 478]], 0.2901, ''],
    ['3.r3-external-1', 't34', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Math (3.0 release), right of 500', 'right of 500', 412, 388, 436, 448, 'l', [[405, 360, 445], [430, 393, 457]], -1.8894, ''],
    ['3.r3-external-1', 't37', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Code (3.0), right of 500', 'right of 500', 418, 392, 444, 411, 'w', [[420, 370, 455], [425, 380, 455]], 0.4554, ''],
    ['3.r3-external-2', 't26', 'hard328 (328 harder problems), T 1.0 / top-p 1.0, cue, grader v3, 1 sample, theta(0.25) = base + 0.25 (RL - base)', 'right of 328', 174, 165, 184, 182, 'lu', [[186, 170, 201], [186, 171, 201]], -0.3933, ''],
    ['3.r3-external-2', 't27', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, theta(0.5) = base + 0.5 (RL - base)', 'right of 328', 185, 175, 195, 190, 'wu', [[196, 181, 210], [196, 182, 210]], 0.2558, ''],
    ['3.r3-external-2', 't28', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, Olmo-3.1-7B-RL-Zero-Code', 'right of 328', 171, 160, 182, 187, 'l', [[188, 170, 205], [188, 170, 205]], -2.3938, ''],
    ['3.r3-external-2', 't31', 'hard328, T 1.0, cue, v3, theta(0.5) minus RL plain (paired difference)', 'points', -6.5, -10.5, -2.5, -4.9, 'w', [[-3.0, -8.0, 2.0], [-3.0, -7.5, 1.5]], 0.1718, ''],
    ['3.r3-external-2', 't32', 'hard328, T 1.0, cue, v3, Olmo-3.1-7B-RL-Zero-Code minus RL plain (paired difference)', 'points', -10.7, -14.5, -7.0, -5.8, 'l', [[-5.5, -11.5, 0.5], [-5.5, -11, -0.5]], -1.9052, ''],
    ['3.r3-external-2', 't33', 'hard328, T 1.0, cue, v3, Code-RL minus theta(0.5) (paired difference)', 'points', -4.0, -8.0, 0.0, -0.9, 'l', [[-2.5, -8.0, 3.0], [-2.5, -8, 3]], -0.3797, ''],
    ['3.r3-external-2', 't34', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Math (3.0 release), right of 500', 'right of 500', 447, 435, 459, 448, 'wu', [[405, 360, 445], [430, 393, 457]], 1.8387, ''],
    ['3.r3-external-2', 't35', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Mix, right of 500', 'right of 500', 446, 432, 458, 440, 't', [[430, 390, 460], [438, 403, 462]], 0.6656, ''],
    ['3.r3-external-2', 't36', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-General, right of 500', 'right of 500', 441, 424, 456, 429, 'l', [[415, 370, 450], [425, 388, 455]], 0.146, ''],
    ['3.r3-external-2', 't37', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Code (3.0), right of 500', 'right of 500', 440, 422, 456, 411, 'l', [[420, 370, 455], [425, 380, 455]], -2.959, ''],
    ['3.r3-external-2', 't38', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-IF, right of 500', 'right of 500', 436, 416, 454, 377, 'l', [[415, 370, 450], [415, 370, 450]], -3.0, ''],
    ['3.r3-revise-1', 't26', 'hard328 (328 harder problems), T 1.0 / top-p 1.0, cue, grader v3, 1 sample, theta(0.25) = base + 0.25 (RL - base)', 'right of 328', 181, 172, 190, 182, 'w', [[186, 170, 201], [186, 171, 201]], 0.6036, ''],
    ['3.r3-revise-1', 't27', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, theta(0.5) = base + 0.5 (RL - base)', 'right of 328', 187, 178, 196, 190, 'w', [[196, 181, 210], [196, 182, 210]], 0.5491, ''],
    ['3.r3-revise-1', 't28', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, Olmo-3.1-7B-RL-Zero-Code', 'right of 328', 187, 178, 196, 187, 'w', [[188, 170, 205], [188, 170, 205]], 0.6694, ''],
    ['3.r3-revise-1', 't29', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, Olmo-3.1-7B-RL-Zero-Code, tokens per problem', 'tokens per problem', 7000, 5700, 8300, 7613, 'l', [[7900, 6000, 9800], [7200, 5500, 9200]], 0.1145, ''],
    ['3.r3-revise-1', 't31', 'hard328, T 1.0, cue, v3, theta(0.5) minus RL plain (paired difference)', 'points', -5.8, -9.0, -2.6, -4.9, 'w', [[-3.0, -8.0, 2.0], [-3.0, -7.5, 1.5]], 0.5044, ''],
    ['3.r3-revise-1', 't32', 'hard328, T 1.0, cue, v3, Olmo-3.1-7B-RL-Zero-Code minus RL plain (paired difference)', 'points', -5.8, -9.2, -2.4, -5.8, 'w', [[-5.5, -11.5, 0.5], [-5.5, -11, -0.5]], 0.5029, ''],
    ['3.r3-revise-1', 't33', 'hard328, T 1.0, cue, v3, Code-RL minus theta(0.5) (paired difference)', 'points', 0, -3.3, 3.3, -0.9, 'w', [[-2.5, -8.0, 3.0], [-2.5, -8, 3]], 0.5247, ''],
    ['3.r3-revise-1', 't35', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Mix, right of 500', 'right of 500', 450, 437, 462, 440, 'l', [[430, 390, 460], [438, 403, 462]], 0.1271, ''],
    ['3.r3-revise-1', 't36', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-General, right of 500', 'right of 500', 444, 427, 459, 429, 'lu', [[415, 370, 450], [425, 388, 455]], -0.2821, ''],
    ['3.r3-revise-1', 't37', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Code (3.0), right of 500', 'right of 500', 446, 431, 459, 411, 'l', [[420, 370, 455], [425, 380, 455]], -3.0, ''],
    ['3.r3-revise-1', 't38', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-IF, right of 500', 'right of 500', 444, 427, 459, 377, 'l', [[415, 370, 450], [415, 370, 450]], -3.0, ''],
    ['3.r3-surprises-1', 't22', 'MATH-500 base+cue 4-sample vote, T 1.0, v3, in the 36 tied problems: number right when ties broken by shortest finished sample', 'right of 36', 19, 14, 24, 12, 'w', [[22, 14, 29], [18, 11, 25]], -0.8333, ''],
    ['3.r3-surprises-1', 't20', 'MATH-500 n=500, T 1.0, v3, base+cue, 4 stored samples, vote with ties broken by shortest finished sample, right of 500', 'right of 500', 450, 444, 456, 453, 'w', [[447, 438, 456], [448, 437, 458]], 0.5019, ''],
    ['3.r3-surprises-1', 't24', 'MATH-500 n=500, T 1.0, v3, Olmo-3.1-7B-RL-Zero-Math plain, 4-sample vote with ties to the shortest finished sample, right of 500', 'right of 500', 475, 471, 479, 475, 't', [[475, 467, 482], [475, 467, 481]], 0.0, ''],
    ['3.r3-surprises-1', 't25', 'MATH-500 n=500, T 1.0, v3, Olmo-3.1-7B-RL-Zero-Math plain, 4-sample vote with ties to the longest sample (control), right of 500', 'right of 500', 471, 466, 476, 476, 'w', [[470, 460, 478], [471, 462, 478]], 0.0878, ''],
    ['3.r3-surprises-2', 't26', 'hard328 (328 harder problems), T 1.0 / top-p 1.0, cue, grader v3, 1 sample, theta(0.25) = base + 0.25 (RL - base)', 'right of 328', 176, 165, 188, 182, 'l', [[186, 170, 201], [186, 171, 201]], 0.0069, ''],
    ['3.r3-surprises-2', 't28', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, Olmo-3.1-7B-RL-Zero-Code', 'right of 328', 177, 165, 189, 187, 'l', [[188, 170, 205], [188, 170, 205]], -0.5579, ''],
    ['3.r3-surprises-2', 't27', 'hard328, T 1.0 / top-p 1.0, cue, grader v3, 1 sample, theta(0.5) = base + 0.5 (RL - base)', 'right of 328', 185, 172, 197, 190, 'w', [[196, 181, 210], [196, 182, 210]], 0.1544, ''],
    ['3.r3-surprises-2', 't32', 'hard328, T 1.0, cue, v3, Olmo-3.1-7B-RL-Zero-Code minus RL plain (paired difference)', 'points', -8.8, -13.5, -4.5, -5.8, 'l', [[-5.5, -11.5, 0.5], [-5.5, -11, -0.5]], -0.3787, ''],
    ['3.r3-surprises-2', 't31', 'hard328, T 1.0, cue, v3, theta(0.5) minus RL plain (paired difference)', 'points', -6.4, -11, -2, -4.9, 'w', [[-3.0, -8.0, 2.0], [-3.0, -7.5, 1.5]], 0.1202, ''],
    ['3.r3-surprises-2', 't33', 'hard328, T 1.0, cue, v3, Code-RL minus theta(0.5) (paired difference)', 'points', -2.5, -7, 2, -0.9, 't', [[-2.5, -8.0, 3.0], [-2.5, -8, 3]], 0.1441, ''],
    ['3.r3-surprises-2', 't34', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Math (3.0 release), right of 500', 'right of 500', 448, 434, 461, 448, 'wu', [[405, 360, 445], [430, 393, 457]], 1.7303, ''],
    ['3.r3-surprises-2', 't35', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Mix, right of 500', 'right of 500', 448, 434, 461, 440, 'l', [[430, 390, 460], [438, 403, 462]], 0.4409, ''],
    ['3.r3-surprises-2', 't36', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-General, right of 500', 'right of 500', 442, 426, 457, 429, 'lu', [[415, 370, 450], [425, 388, 455]], -0.0129, ''],
    ['3.r3-surprises-2', 't37', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-Code (3.0), right of 500', 'right of 500', 445, 430, 459, 411, 'l', [[420, 370, 455], [425, 380, 455]], -3.0, ''],
    ['3.r3-surprises-2', 't38', 'MATH-500 n=500, cue, T 1.0 / top-p 1.0, grader v3, Olmo-3-7B-RL-Zero-IF, right of 500', 'right of 500', 440, 424, 456, 377, 'l', [[415, 370, 450], [415, 370, 450]], -3.0, ''],
    ['4.r4-m01', 'p2', 'Does pre-loop compressibility predict a later rule-A loop in cued base answers at T 0.6 / top-p 1.0?', 'AUROC', 0.7, 0.6, 0.79, 0.6705288175876412, 'w', [[0.6, 0.47, 0.73], [0.6, 0.48, 0.72]], 0.5762, ''],
    ['4.r4-m01', 'p3', "Is the cued base's opening text at T 0.6 more self-similar than RL's opening text on the same problem?", 'fraction of problems', 0.64, 0.55, 0.73, 0.6334405144694534, 'wu', [[0.54, 0.38, 0.68], [0.43, 0.28, 0.58]], 1.5905, ''],
    ['4.r4-m01', 'p4', 'Within each prefix kind of the RLN-4 K continuations, does compressibility of the stored text predict a cap hit?', 'AUROC', 0.66, 0.54, 0.77, 0.5584900564423672, 'l', [[0.59, 0.44, 0.74], [0.57, 0.42, 0.72]], -0.755, ''],
    ['4.r4-m01', 'p1', 'Within-problem early compressibility, cued base at T 0.6: does the sample that later hits the cap have a more compressible opening than a sample of the same problem that…', 'fraction of problems', 0.65, 0.54, 0.76, None, 'x', [], None, 'x:no problem qualifies: the file holds 500 rows, samples present [0] (one row per problem), so no problem has both a cap_hit true row and a cap_hit false row; the within-problem pair the recipe asks for does not exist in the stored…'],
    ['4.r4-m02', 'p1', 'Pooled within-problem concordance of length with wrongness for the cued base: over all (right, wrong) pairs of finished attempt-0 samples of the same problem, the fracti…', 'fraction of pairs', 0.7, 0.61, 0.79, 0.6222222222222222, 'l', [[0.66, 0.57, 0.75], [0.7, 0.6, 0.8]], -0.487, ''],
    ['4.r4-m02', 'p2', 'The same pooled within-problem concordance for the RL model.', 'fraction of pairs', 0.55, 0.43, 0.67, 0.717948717948718, 'l', [[0.67, 0.53, 0.8], [0.68, 0.55, 0.8]], -2.4252, ''],
    ['4.r4-m02', 'p3', 'Mean within-problem Spearman correlation of n_new with score_v3 for the cued base, over problems whose finished attempt-0 samples include at least one right and one wron…', 'mean Spearman correlation', -0.36, -0.52, -0.2, -0.2005220257109175, 'l', [[-0.25, -0.42, -0.08], [-0.35, -0.55, -0.15]], -0.8458, ''],
    ['4.r4-m04', 'p1', 'Wait-rate-based share estimate in theta0.25_plain against the plain base and RL plain endpoints', 'fraction (share estimate)', 0.76, 0.6, 0.9, 0.327, 'l', [[0.38, 0.08, 0.72], [0.5, 0.2, 0.85]], -3.0, ''],
    ['4.r4-m04', 'p2', 'Answer-format-based share estimate in theta0.25_plain against the plain base', 'fraction (share estimate)', 0.76, 0.6, 0.9, 0.716, 'l', [[0.75, 0.45, 0.97], [0.75, 0.45, 0.98]], 0.4658, ''],
    ['4.r4-m04', 'p3', 'Accuracy of theta0.25_plain boxed answers against RL plain on the same problems', 'difference in fraction right', -0.05, -0.095, 0.0, -0.0462, 'w', [[-0.07, -0.14, -0.01], [-0.04, -0.09, 0.01]], 0.2527, ''],
    ['4.r4-m04', 'p4', 'Wait-rate-based share estimate in theta0.25_cue against the cued base and RL cue endpoints', 'fraction (share estimate)', 0.66, 0.44, 0.88, 0.212, 'l', [[0.42, 0.05, 0.82], [0.45, 0.15, 0.8]], -3.0, ''],
    ['4.r4-m06', 'p1', "Re-check rate after wrong vs right non-final candidate answers in RL's T2 texts, as a ratio", 'ratio of rates', 1.05, 0.8, 1.45, None, 'x', [], None, 'x:grader v3 equivalence (n13_score.grade) needs the math_verify package, which this python3 does not have; the standard library cannot reproduce it'],
    ['4.r4-m06', 'p2', 'Difference-in-differences of re-check rates, RL (T2) minus base (T1), wrong minus right non-final candidates', 'difference of fractions', 0.0, -0.15, 0.15, None, 'x', [], None, 'x:grader v3 equivalence (n13_score.grade) needs the math_verify package, which this python3 does not have; the standard library cannot reproduce it'],
    ['4.r4-m06', 'p3', 'Share of final-right answers containing a right non-final candidate followed by a re-check: RL minus base', 'difference of fractions of problems', 0.12, 0.03, 0.25, None, 'x', [], None, 'x:grader v3 equivalence (n13_score.grade) needs the math_verify package, which this python3 does not have; the standard library cannot reproduce it'],
    ['4.r4-m07', 'p1', "MATH-500: share of RL's wrong finished samples whose answer equals one of the base's wrong finished answers on the same problem", 'fraction of RL wrong finished samples', 0.5, 0.36, 0.65, 0.26717557251908397, 'l', [[0.35, 0.2, 0.5], [0.3, 0.18, 0.45]], -3.0, ''],
    ['4.r4-m07', 'p2', "MATH-500: on problems where the base repeats a wrong value, share of RL's wrong finished samples that equal the base's most frequent wrong value", 'fraction of RL wrong finished samples on attractor problems', 0.65, 0.5, 0.82, 0.34615384615384615, 'l', [[0.4, 0.2, 0.6], [0.4, 0.22, 0.58]], -3.0, ''],
    ['4.r4-m07', 'p3', 'MATH-500: RL vote fix rate on base-vote-wrong problems where the base has a repeated wrong value', 'fraction of problems', 0.3, 0.12, 0.5, 0.75, 'l', [[0.45, 0.22, 0.68], [0.35, 0.15, 0.6]], -3.0, ''],
    ['4.r4-m07', 'p4', 'MATH-500: RL vote fix rate on base-vote-wrong problems without a repeated base wrong value', 'fraction of problems', 0.75, 0.55, 0.92, 0.47368421052631576, 'l', [[0.55, 0.33, 0.76], [0.6, 0.4, 0.8]], -2.5601, ''],
    ['4.r4-m07', 'p5', 'hard328: when both single samples are wrong and finished, share where base and RL give the same answer', 'fraction of problems', 0.33, 0.2, 0.48, 0.19047619047619047, 'l', [[0.25, 0.11, 0.4], [0.25, 0.12, 0.4]], -1.09, ''],
    ['4.r4-m08', 'p1', 'Standardised paired gap (RL plain minus base cue, grader v3) on the clean harder 328, post-cutoff problems minus pre-cutoff problems, matched on RL answer length.', 'points', 7, -3, 17, 6.880146785807161, 'w', [[-2.0, -22.0, 18.0], [2.0, -12.0, 16.0]], 0.7041, ''],
    ['4.r4-m08', 'p2', "On harder-328 problems both models solve, the base's answer length relative to RL's, pre-cutoff minus post-cutoff.", 'difference of median log length ratios', -0.3, -0.9, 0.15, 0.14265940956097878, 'l', [[0.0, -0.5, 0.5], [-0.1, -0.6, 0.4]], -0.8017, ''],
    ['4.r4-m08', 'p3', "MATH-500: per-token entropy of the cued base's own short right answers relative to its long right answers.", 'ratio', 0.85, 0.6, 1.0, 0.8447792982569907, 'w', [[0.92, 0.72, 1.15], [0.9, 0.7, 1.15]], 0.2175, ''],
    ['4.r4-m09', 'p1', 'MATH-500: Code-RL cue accuracy on problems where the cued base hit the cap and was wrong', 'fraction of problems', 0.62, 0.42, 0.8, 0.48148148148148145, 'l', [[0.48, 0.28, 0.68], [0.5, 0.3, 0.7]], -0.662, ''],
    ['4.r4-m09', 'p2', 'MATH-500: Code-RL cue fix rate minus random-difference cue fix rate on base clean-finished-wrong problems', 'fraction of problems (difference)', 0.0, -0.12, 0.1, 0.14285714285714285, 'l', [[0.14, -0.02, 0.3], [0.1, -0.05, 0.25]], -1.8844, ''],
    ['4.r4-m09', 'p3', 'MATH-500: cap-hit rate of Code-RL cue answers', 'fraction of problems', 0.008, 0.0, 0.022, 0.014, 'w', [[0.022, 0.006, 0.048], [0.025, 0.008, 0.05]], 0.3442, ''],
    ['4.r4-m09', 'p4', 'hard328: Code-RL cue accuracy on problems where the cued base hit the cap and was wrong', 'fraction of problems', 0.33, 0.2, 0.47, 0.13513513513513514, 'l', [[0.25, 0.13, 0.38], [0.25, 0.13, 0.38]], -1.7535, ''],
    ['4.r4-m09', 'p5', 'hard328: Code-RL cue accuracy on problems where the cued base finished without a cap hit and was wrong', 'fraction of problems', 0.15, 0.07, 0.25, 0.3, 'l', [[0.28, 0.15, 0.42], [0.32, 0.2, 0.45]], -3.0, ''],
    ['4.r4-m09', 'p6', 'hard328: cap-hit rate of Code-RL cue answers', 'fraction of problems', 0.067, 0.03, 0.11, 0.07621951219512195, 'l', [[0.09, 0.04, 0.17], [0.07, 0.03, 0.12]], 0.253, ''],
    ['4.r4-m10', 'p1', 'Paired cap-hit rate difference, RL step 100 minus base, plain MATH-500 at T 0.6 / top-p 0.95.', 'fraction of problems', 0.03, 0.002, 0.08, 0.07599999999999998, 'wu', [[-0.025, -0.08, 0.03], [-0.03, -0.09, 0.03]], 2.8898, ''],
    ['4.r4-m10', 'p2', 'Paired cap-hit rate difference, RL step 400 minus base, plain MATH-500 at T 0.6 / top-p 0.95.', 'fraction of problems', 0.06, 0.015, 0.12, 0.066, 'wu', [[-0.06, -0.13, 0.01], [-0.07, -0.13, 0.0]], 3.0, ''],
    ['4.r4-m10', 'p3', 'Paired cap-hit rate difference, RL step 400 minus base, plain prompt, clean harder 328 at T 0.6 / top-p 0.95.', 'fraction of problems', 0.06, 0.01, 0.13, 0.0701219512195122, 'wu', [[-0.12, -0.26, 0.02], [-0.12, -0.25, 0.02]], 3.0, ''],
    ['4.r4-m10', 'p5', 'Share of step-400 cap hits that are rule-A loops, plain MATH-500 at T 0.6 / top-p 0.95.', 'fraction of cap-hit answers', 0.85, 0.68, 0.97, 0.7959183673469388, 'wu', [[0.65, 0.38, 0.9], [0.6, 0.3, 0.85]], 0.9677, ''],
    ['4.r4-m10', 'p4', "Where step 400's accuracy on finished answers lies between base and step 2,800, plain MATH-500 at T 0.6 / top-p 0.95, grader v3.", 'fraction of the base-to-step-2800 distance', 0.7, 0.5, 0.95, None, 'x', [], None, 'x:grader v3 (rln4_lib.grade_v3 -> n13_score.grade) needs the math_verify package, which this python3 does not have; the standard library cannot reproduce grader v3'],
    ['4.r4-m11', 'p1', "First-marker regrade of the base's wrong T1 answers: among T1 rows graded wrong by grader v3 on the full text, the fraction whose first answer marker is right.", 'fraction of problems', 0.11, 0.04, 0.22, None, 'x', [], None, "x:grader v3 (rln4_lib.grade_v3 -> n13_score.grade) needs the math_verify package, which this python3 does not have; the standard library cannot reproduce grader v3's equivalence test"],
    ['4.r4-m11', 'p2', 'Direction of first/last disagreement on T1: among rows where the first-marker grade differs from the last-marker grade, the share that are first-right and last-wrong.', 'fraction of discordant problems', 0.72, 0.45, 0.93, None, 'x', [], None, "x:grader v3 (rln4_lib.grade_v3 -> n13_score.grade) needs the math_verify package, which this python3 does not have; the standard library cannot reproduce grader v3's equivalence test"],
    ['4.r4-m11', 'p3', 'Net first-marker gain for the base on the four Day-1 #3 samples: (first-marker right count minus stored v3 right count) over all attempt-0 rows.', 'fraction of answers', 0.012, 0.002, 0.025, None, 'x', [], None, "x:grader v3 (rln4_lib.grade_v3 -> n13_score.grade) needs the math_verify package, which this python3 does not have; the standard library cannot reproduce grader v3's equivalence test"],
    ['4.r4-m11', 'p4', 'The same net first-marker gain for the RL model on its four Day-1 #3 samples.', 'fraction of answers', 0.0, -0.01, 0.004, None, 'x', [], None, "x:grader v3 (rln4_lib.grade_v3 -> n13_score.grade) needs the math_verify package, which this python3 does not have; the standard library cannot reproduce grader v3's equivalence test"],
    ['4.r4-m11', 'p5', 'Wrong rate among base answers that keep going and state a new answer after the first one: among finished T1 answers with more than 300 characters and at least one furthe…', 'fraction of problems', 0.4, 0.2, 0.65, None, 'x', [], None, "x:grader v3 (rln4_lib.grade_v3 -> n13_score.grade) needs the math_verify package, which this python3 does not have; the standard library cannot reproduce grader v3's equivalence test"],
    ['4.r4-m12', 'p3', 'Exact-string match to gold among answers that v3 grades right, RL minus base, on non-integer-gold problems that both models got right.', 'fraction of problems', 0.1, 0.02, 0.22, 0.03125, 'l', [[0.02, -0.1, 0.14], [0.0, -0.15, 0.15]], -0.3194, ''],
    ['4.r4-m12', 'p1', "Numeric-equivalence recovery rate of the cued base's finished, v3-wrong answers on non-integer-gold hard328 problems.", 'fraction of problems', 0.12, 0.05, 0.25, None, 'x', [], None, "x:The recipe's equivalence E(a, g) requires sympy.parsing.latex.parse_latex (with its antlr4 backend) and numpy.random.default_rng(0) sample points; test scripts are restricted to the standard library, and a substitute LaTeX parser…"],
    ['4.r4-m12', 'p2', "The same numeric-equivalence recovery rate for RL's finished, v3-wrong answers on non-integer-gold hard328 problems.", 'fraction of problems', 0.03, 0.0, 0.09, None, 'x', [], None, "x:The recipe's equivalence E(a, g) requires sympy.parsing.latex.parse_latex (with its antlr4 backend) and numpy.random.default_rng(0) sample points; test scripts are restricted to the standard library, and a substitute LaTeX parser…"],
    ['4.r4-m12', 'p4', 'The hard328 gap, RL plain minus base cue, after both are regraded with v3 OR numeric equivalence.', 'points of 328', 11.9, 10.4, 12.5, None, 'x', [], None, "x:The recipe's equivalence E(a, g) requires sympy.parsing.latex.parse_latex (with its antlr4 backend) and numpy.random.default_rng(0) sample points; test scripts are restricted to the standard library, and a substitute LaTeX parser…"],
    ['5.r4-m06', 'p1', "Re-check rate after wrong vs right non-final candidate answers in RL's T2 texts, as a ratio", 'ratio of rates', 1.05, 0.8, 1.45, 1.2357922660952962, 'l', [[1.1, 0.75, 1.65], [1.15, 0.8, 1.65]], -0.0581, ''],
    ['5.r4-m06', 'p2', 'Difference-in-differences of re-check rates, RL (T2) minus base (T1), wrong minus right non-final candidates', 'difference of fractions', 0.0, -0.15, 0.15, -0.08671144434629674, 'w', [[0.04, -0.15, 0.24], [0.03, -0.15, 0.2]], 0.3419, ''],
    ['5.r4-m06', 'p3', 'Share of final-right answers containing a right non-final candidate followed by a re-check: RL minus base', 'difference of fractions of problems', 0.12, 0.03, 0.25, 0.440048569316862, 'l', [[0.15, -0.05, 0.35], [0.12, 0.0, 0.26]], -3.0, ''],
    ['5.r4-m11', 'p1', "First-marker regrade of the base's wrong T1 answers: among T1 rows graded wrong by grader v3 on the full text, the fraction whose first answer marker is right.", 'fraction of problems', 0.11, 0.04, 0.22, 0.0, 'w', [[0.12, 0.04, 0.25], [0.12, 0.04, 0.25]], -0.0998, ''],
    ['5.r4-m11', 'p2', 'Direction of first/last disagreement on T1: among rows where the first-marker grade differs from the last-marker grade, the share that are first-right and last-wrong.', 'fraction of discordant problems', 0.72, 0.45, 0.93, 0.0, 'l', [[0.4, 0.15, 0.7], [0.3, 0.1, 0.55]], -3.0, ''],
    ['5.r4-m11', 'p5', 'Wrong rate among base answers that keep going and state a new answer after the first one: among finished T1 answers with more than 300 characters and at least one furthe…', 'fraction of problems', 0.4, 0.2, 0.65, 0.17063492063492064, 'l', [[0.25, 0.1, 0.45], [0.25, 0.1, 0.45]], -1.3791, ''],
    ['5.r4-m11', 'p3', 'Net first-marker gain for the base on the four Day-1 #3 samples: (first-marker right count minus stored v3 right count) over all attempt-0 rows.', 'fraction of answers', 0.012, 0.002, 0.025, None, 'x', [], None, 'x:iterate-runs:abaybektursun-1114-153825-208b/answers.jsonl is not readable from this workspace (modal volume get: Error: No such file or directory)'],
    ['5.r4-m11', 'p4', 'The same net first-marker gain for the RL model on its four Day-1 #3 samples.', 'fraction of answers', 0.0, -0.01, 0.004, None, 'x', [], None, 'x:iterate-runs:abaybektursun-1114-183640-e828/answers.jsonl is not readable from this workspace (modal volume get: Error: No such file or directory)'],
    ['5.r4-m12', 'p1', "Numeric-equivalence recovery rate of the cued base's finished, v3-wrong answers on non-integer-gold hard328 problems.", 'fraction of problems', 0.12, 0.05, 0.25, 0.0, 'l', [[0.08, 0.0, 0.25], [0.08, 0.0, 0.2]], -1.1277, ''],
    ['5.r4-m12', 'p2', "The same numeric-equivalence recovery rate for RL's finished, v3-wrong answers on non-integer-gold hard328 problems.", 'fraction of problems', 0.03, 0.0, 0.09, 0.0, 'w', [[0.08, 0.0, 0.25], [0.07, 0.0, 0.2]], 0.9157, ''],
    ['5.r4-m12', 'p3', 'Exact-string match to gold among answers that v3 grades right, RL minus base, on non-integer-gold problems that both models got right.', 'fraction of problems', 0.1, 0.02, 0.22, 0.03125, 'l', [[0.0, -0.1, 0.1], [0.03, -0.1, 0.16]], -0.4443, ''],
    ['5.r4-m12', 'p4', 'The hard328 gap, RL plain minus base cue, after both are regraded with v3 OR numeric equivalence.', 'points of 328', 11.9, 10.4, 12.5, 12.804878048780488, 'l', [[12.8, 11.3, 14.2], [12.5, 10.3, 14.6]], -0.4935, ''],
    ['5.r5-m02', 'p1', 'Base+cue, Levels 1-3: median over problems of the within-problem log length ratio of finished-wrong samples to their right siblings.', 'natural-log ratio', -0.2, -0.5, -0.03, 0.19285520124940034, 'l', [[0.1, -0.4, 0.6], [0.05, -0.4, 0.5]], -2.9874, ''],
    ['5.r5-m02', 'p2', 'Base+cue, Level 5: the same within-problem log length ratio.', 'natural-log ratio', 0.3, 0.08, 0.65, 0.15549604757875102, 'l', [[0.2, -0.2, 0.6], [0.15, -0.3, 0.6]], 0.0572, ''],
    ['5.r5-m02', 'p3', 'Mechanism test, base+cue Levels 1-3: the share of finished-wrong samples shorter than every right sibling. The nearest rival (slips accumulate with length, r3-surprises-…', 'fraction of finished-wrong samples', 0.55, 0.38, 0.72, 0.29411764705882354, 'l', [[0.33, 0.15, 0.55], [0.33, 0.18, 0.5]], -2.9636, ''],
    ['5.r5-m02', 'p4', 'RL plain, all levels: the within-problem log length ratio of finished-wrong to right siblings.', 'natural-log ratio', 0.35, 0.08, 0.75, 0.24082829519679472, 'l', [[0.3, -0.1, 0.7], [0.2, -0.2, 0.6]], 0.0555, ''],
    ['5.r5-m03', 'p1', 'Per-problem log length ratio of top8 plain to the cued base, ln(top8 n_generated / T1 tokens), taken as the median over problems. This tests the mechanism. This theory s…', 'natural-log ratio (median over problems)', 0.12, -0.08, 0.32, 0.2529517647514732, 'l', [[0.15, -0.15, 0.5], [0.2, -0.15, 0.55]], 0.0079, ''],
    ['5.r5-m03', 'p2', "Count of quick finished-wrong answers in top8 plain: answers wrong under v3, not cap hits, and at most 2,000 generated tokens. This tests whether the edit carries RL's c…", 'problems (count of 500)', 11, 5, 21, 22, 'w', [[8, 2, 16], [9, 3, 18]], 1.8899, ''],
    ['5.r5-m03', 'p3', "Fraction of the cued base's wrong problems (T1 wrong) that top8 plain also gets wrong.", 'fraction of problems', 0.46, 0.35, 0.57, 0.35555555555555557, 'w', [[0.5, 0.35, 0.65], [0.45, 0.33, 0.58]], -0.0415, ''],
    ['5.r5-m04', 'p1', 'Count of Think-SFT cue answers that hit the 16,384 cap on MATH-500.', 'problems of 500', 38, 28, 55, 25, 'l', [[28, 10, 50], [30, 12, 55]], -0.7753, ''],
    ['5.r5-m04', 'p2', "Mechanism test: share of Think-SFT's wrong answers that are cap hits. The nearest rival (Think-SFT as a uniformly stronger solver on the base's difficulty axis) predicts…", 'fraction of wrong problems', 0.72, 0.55, 0.88, 0.5217391304347826, 'l', [[0.6, 0.35, 0.85], [0.6, 0.35, 0.85]], -1.4054, ''],
    ['5.r5-m04', 'p3', "Share of Think-SFT cap hits that fall in the top quartile of RL's answer length on MATH-500. Random placement gives 0.25.", 'fraction of Think-SFT cap hits', 0.6, 0.42, 0.78, 0.68, 't', [[0.6, 0.38, 0.8], [0.6, 0.4, 0.8]], 0.0688, ''],
    ['5.r5-m04', 'p4', "Where Think-SFT's deficit to RL lies: Think-SFT right minus RL (T2) right within the top RL-length quartile.", 'problems (Think-SFT minus RL, Q4)', -7, -15, 0, 6, 'l', [[-6, -16, 3], [-7, -16, 2]], -1.4106, ''],
    ['5.r5-m04', 'p5', "Mean generated tokens per problem of Think-SFT cue on MATH-500, against RL plain's 4,694 at the same setting.", 'tokens per problem', 6800, 5000, 9500, 4887.964, 'l', [[5800, 3800, 8500], [6000, 3500, 9000]], -0.6463, ''],
    ['5.r5-m05', 'p1', 'Per-hold-on revision rate, base vs RL, on stored MATH-500 text: the fraction of hold-on occurrences where the first number after the token differs from the last number b…', 'ratio of per-occurrence revision rates (base / RL)', 0.55, 0.35, 0.78, 1.0400414574092287, 'l', [[1.0, 0.8, 1.25], [1.0, 0.8, 1.25]], -3.0, ''],
    ['5.r5-m05', 'p2', "Among the base's finished-wrong MATH-500 answers that contain at least one hold-on, the fraction whose final answer was already written before the last hold-on.", 'fraction of problems', 0.8, 0.66, 0.93, 0.5833333333333334, 'l', [[0.6, 0.38, 0.82], [0.65, 0.45, 0.85]], -2.9657, ''],
    ['5.r5-m05', 'p3', 'Detection parity in generated text on hard-328: how much denser hold-ons are in wrong finished answers than in right ones, base relative to RL. This theory (equal detect…', 'ratio of wrong/right hold-on density ratios (base / RL)', 0.95, 0.65, 1.4, 1.0147852281544179, 'l', [[1.0, 0.7, 1.4], [0.95, 0.7, 1.3]], -0.1548, ''],
    ['5.r5-m06', 'p1', 'Pool fresh base samples with seeds independent of Day-1 #3 sample 0 and count how many of the 17 RL-solved base-0/4 problems get at least one right answer.', 'fraction of problems', 0.53, 0.29, 0.76, 0.6470588235294118, 'w', [[0.35, 0.12, 0.6], [0.4, 0.15, 0.65]], 1.341, ''],
    ['5.r5-m06', 'p2', 'Mechanism test against the dose-scaling / new-solution rival: the pooled solve fraction on the 17 RL-solved base-0/4 problems minus the same fraction on the 16 base-0/4…', 'fraction of problems', 0.28, 0.0, 0.56, 0.5220588235294118, 'w', [[0.22, -0.03, 0.48], [0.28, 0.0, 0.5]], 0.417, ''],
    ['5.r5-m06', 'p3', "Per-sample base success rate in the independent pool on the 17 RL-solved base-0/4 problems: the mechanism says 'a few percent' per sample, not about 0 and not near the b…", 'fraction of samples', 0.09, 0.03, 0.18, 0.23684210526315788, 'w', [[0.06, 0.02, 0.13], [0.08, 0.03, 0.16]], 3.0, ''],
    ['5.r5-m07', 'p1', "Share of step-100 plain MATH-500 answers at T 0.6 / top-p 0.95 that open with the RL cue's first token 'line'. The sharpening rival (r4-m10) and the length rival leave t…", 'fraction of problems', 0.68, 0.4, 0.95, 0.034, 'l', [[0.3, 0.02, 0.75], [0.3, 0.02, 0.75]], -3.0, ''],
    ['5.r5-m07', 'p3', "Mechanism test on the plain base itself: in base-01's plain MATH-500 answers at T 0.6 / top-p 0.95, the cap-hit rate of answers that open in the cue's register ('Okay' w…", 'difference in fraction of problems', 0.13, 0.04, 0.24, 0.14826723829939265, 'w', [[0.08, -0.03, 0.2], [0.08, -0.03, 0.2]], 0.5714, ''],
    ['5.r5-m07', 'p4', "Share of step-100's finished plain T 0.6 answers that still state the result on an 'Answer:' line (the base's format). This mechanism expects a base-like share. A format…", 'fraction of finished answers', 0.3, 0.17, 0.47, 0.04534005037783375, 'w', [[0.35, 0.1, 0.55], [0.35, 0.1, 0.55]], -1.0137, ''],
    ['5.r5-m07', 'p2', "Mechanism test: within the step-100 plain T 0.6 answers, the cap-hit rate of answers that open with 'line' minus the cap-hit rate of answers that do not. This mechanism…", 'difference in fraction of problems', 0.11, 0.03, 0.2, None, 'x', [], None, 'x:refuted without a number: measured below 0.02, or either group has fewer than 20 rows'],
    ['5.r5-m08', 'p1', "Share of Code 3.1's lead over Code 3.0 (MATH-500, cue, T 1.0) that lies in the top quartile of RL answer length. The nearest rival (Code 3.0 is a base-like model lacking…", "fraction of Code 3.1's lead", 0.62, 0.45, 0.88, 0.7948717948717948, 'w', [[0.45, 0.2, 0.72], [0.45, 0.2, 0.7]], 1.75, ''],
    ['5.r5-m08', 'p2', 'Code 3.0 cue minus the cued base in the top RL-length quartile of MATH-500. The rival (Code 3.0 behaves like a resampled base) predicts about 0; this mechanism predicts…', 'problems (of 125)', -6, -14, 0.5, -11.25, 'w', [[-3, -12, 6], [-3, -12, 6]], 0.6436, ''],
    ['5.r5-m08', 'p3', 'Code 3.1 cue minus Code 3.0 cue on the shorter half (Q1+Q2) of MATH-500 by RL length. The rival predicts a gap of about 12-15 problems there (the base-like deficit sprea…', 'problems (of 250)', 1.5, -4, 5, -3, 'wu', [[10, 2, 20], [15, 5, 26]], 2.6168, ''],
    ['5.r5-m08', 'p4', "Code 3.0 cue minus the cued base on the shorter half (Q1+Q2). The rival predicts about 0; this mechanism predicts Code 3.0 ahead, because it keeps Code 3.1's short-probl…", 'problems (of 250)', 5, 0, 11, 7.25, 'w', [[2, -6, 9], [2, -6, 9]], 0.7467, ''],
    ['5.r5-m09', 'p1', 'Share of base finished-wrong judged items flagged answer_from_problem in the anatomy judge labels.', 'fraction of problems', 0.25, 0.15, 0.37, 0.0, 'l', [[0.1, 0.02, 0.25], [0.12, 0.03, 0.25]], -3.0, ''],
    ['5.r5-m09', 'p2', 'Share of RL finished-wrong judged items flagged answer_from_problem in the anatomy judge labels.', 'fraction of problems', 0.03, 0.0, 0.1, 0.0, 'w', [[0.07, 0.0, 0.2], [0.07, 0.0, 0.2]], 0.869, ''],
    ['5.r5-m09', 'p3', 'Mechanism test: base minus RL share of numeric finished-wrong finals that equal a number written in the problem statement. The rival (uniform noise reduction) predicts 0…', 'fraction of problems', 0.14, 0.05, 0.25, -0.04266831038969934, 'l', [[0.05, -0.08, 0.18], [0.04, -0.06, 0.14]], -3.0, ''],
    ['5.r5-m09', 'p4', 'Excess over coincidence: base numeric finished-wrong match share minus the share of numeric golds that equal a problem-statement number. A coincidence account predicts a…', 'fraction of problems', 0.15, 0.06, 0.26, -0.03404678563914232, 'l', [[0.03, -0.08, 0.14], [0.03, -0.06, 0.12]], -3.0, ''],
    ['5.r5-m10', 'p1', 'Accuracy of self-opened plain answers minus cued accuracy on the same problems. This theory predicts about 0. The continuous-entropy / easy-problem-marker rival predicts…', 'difference of fractions of problems', -0.02, -0.09, 0.05, 0.0, 'w', [[-0.05, -0.18, 0.07], [-0.05, -0.15, 0.04]], 0.6261, ''],
    ['5.r5-m10', 'p2', "Length of self-opened plain answers relative to cued answers on the same problems. Whole-mode theory: ratio about 1.0. The rival (the spontaneous 'Okay' only marks easy…", 'ratio of median tokens', 1.0, 0.78, 1.3, 1.2127264282396655, 'w', [[0.9, 0.55, 1.3], [0.9, 0.6, 1.3]], 0.436, ''],
    ['5.r5-m10', 'p3', "Whether a problem's base log-probability of the cue predicts whether the plain base self-opens on it. Theory: the mode choice has a per-problem propensity that the cue's…", 'AUROC', 0.62, 0.54, 0.74, 0.5426055968975998, 'l', [[0.6, 0.49, 0.72], [0.6, 0.5, 0.72]], -0.3402, ''],
    ['5.r5-m11', 'p1', "MATH-500 subject contrast, Code-RL 3.1 cue against Math-RL. For each problem d = Code-RL cue score minus the mean of RL's 4 plain samples. S = mean d over Number Theory…", 'fraction of problems', 0.045, -0.01, 0.1, 0.021241830065359478, 'l', [[0.02, -0.03, 0.07], [0.025, -0.03, 0.08]], -0.2978, ''],
    ['5.r5-m11', 'p2', 'Share of hard328 answers that contain code-style markers, Code-RL 3.1 cue minus base cue. The rival (shared commit habit) predicts a difference near 0 (within +-0.02); t…', 'fraction of problems', 0.12, 0.04, 0.35, 0.0, 'l', [[0.1, 0.0, 0.3], [0.1, -0.02, 0.3]], -0.2466, ''],
    ['5.r5-m11', 'p3', 'Within Code-RL 3.1 cue answers on hard328, the accuracy of marked (code-style) answers minus unmarked ones, with problems stratified by difficulty (RL answer-length quar…', 'fraction of problems', 0.08, -0.05, 0.25, -0.12345679012345678, 'l', [[-0.03, -0.2, 0.15], [-0.03, -0.2, 0.12]], -1.9562, ''],
    ['6.r5-m03-rival', 'p1', "Among top8-plain wrong problems, the fraction that the cued base solves in all 4 of its Day-1 #3 samples: are top8's errors on problems the cued base finds reliably easy?", '', 0.27, 0.17, 0.37, 0.25, 'c', [], 2.767, 'c:[0.13, 0.06, 0.22]'],
    ['6.r5-m03-rival', 'p2', 'Mean cued-base solve rate (4 Day-1 #3 samples) on the problems where top8 plain gives a quick finished-wrong answer (wrong under v3, not a cap hit, at most 2,000 tokens).', '', 0.76, 0.64, 0.88, 0.8181818181818182, 'c', [], 3.0, 'c:[0.5, 0.3, 0.7]'],
    ['6.r5-m03-rival', 'p3', "Share of top8 plain's quick finished-wrong answers that are very short (at most 1,000 generated tokens).", '', 0.63, 0.43, 0.83, 0.7727272727272727, 'c', [], 3.0, 'c:[0.4, 0.18, 0.62]'],
    ['6.r5-m10-rival', 'p1', 'Temperature sensitivity of the non-self-opened plain register: accuracy of non-self-opened plain base answers at T 0.6 minus accuracy of non-self-opened plain base answe…', '', 0.29, 0.17, 0.41, 0.15767634854771778, 'c', [], -0.2393, 'c:[0.28, 0.16, 0.4]'],
    ['6.r5-m10-rival', 'p2', 'How weak the non-self-opened plain register is when sampling is cooler: accuracy of non-self-opened plain base answers at T 0.6 minus accuracy of cued base answers at T…', '', -0.1, -0.2, 0.0, -0.15540540540540537, 'c', [], -0.0079, 'c:[-0.1, -0.19, -0.01]'],
    ['6.r5-m10-rival', 'p3', 'Accuracy gap between self-opened and non-self-opened plain base answers at T 0.6, within one file.', '', 0.09, -0.04, 0.22, 0.20574986751457336, 'c', [], 0.091, 'c:[0.11, 0.02, 0.2]'],
    ['6.r5-m10-rival', 'p4', "On MATH-500 at T 1.0, plain base answers that do not self-open but contain a self-check marker later ('Wait' or 'Hmm'): their accuracy minus cued base accuracy on the sa…", '', -0.14, -0.3, 0.02, -0.07462686567164178, 'c', [], 3.0, 'c:[-0.47, -0.6, -0.33]'],
    ['6.r5-m10-rival', 'p5', "On MATH-500 at T 1.0, within the plain base answers that do not self-open: accuracy of those containing 'Wait' or 'Hmm' minus accuracy of those containing neither.", '', 0.24, 0.07, 0.41, 0.35583146215823536, 'c', [], 3.0, 'c:[-0.03, -0.15, 0.1]'],
    ['6.r5-m10-rival', 'p6', "On the harder clean 328 at T 1.0, plain base answers that do not self-open but contain 'Wait' or 'Hmm': their accuracy minus cued base accuracy on the same problems.", '', -0.1, -0.26, 0.06, -0.10000000000000003, 'c', [], 3.0, 'c:[-0.33, -0.47, -0.19]'],
    ['6.r6-account', 'p2', 'Share of math500-null-T1 gap problems in budget', 'fraction of gap problems', 0.11, 0.03, 0.22, 0.15217391304347827, 'w', [[0.22, 0.08, 0.38], [0.28, 0.1, 0.48]], 0.7124, ''],
    ['6.r6-account', 'p3', 'Share of math500-null-T1 gap problems in answer-statement', 'fraction of gap problems', 0.035, 0.0, 0.11, 0.043478260869565216, 'w', [[0.1, 0.0, 0.25], [0.12, 0.0, 0.3]], 1.1861, ''],
    ['6.r6-account', 'p4', 'Share of math500-null-T1 gap problems in slip', 'fraction of gap problems', 0.22, 0.1, 0.36, 0.2608695652173913, 'l', [[0.28, 0.1, 0.48], [0.28, 0.08, 0.5]], 0.3071, ''],
    ['6.r6-account', 'p5', 'Share of math500-null-T1 gap problems in sharpening', 'fraction of gap problems', 0.52, 0.36, 0.68, 0.4782608695652174, 'wu', [[0.3, 0.12, 0.5], [0.2, 0.03, 0.42]], 1.7783, ''],
    ['6.r6-account', 'p6', 'Share of math500-null-T1 gap problems in reach', 'fraction of gap problems', 0.115, 0.03, 0.22, 0.06521739130434782, 'l', [[0.08, 0.0, 0.22], [0.07, 0.0, 0.22]], -0.2115, ''],
    ['6.r6-account', 'p8', 'Gap problems minus base-only problems in math500-null-T1 (gross about 28 and 27)', 'problems', 1, -8, 9, 8, 't', [[1, -3, 5], [1, -8, 10]], 0.5734, ''],
    ['6.r6-account', 'p16', 'RL-only minus base-only in math500-rl-T1 (gross about 65 and 13)', 'problems', 52, 51, 53, 52, 'w', [[52.5, 50, 55], [53, 48, 57]], 1.2262, ''],
    ['6.r6-account', 'p18', 'Share of math500-plainbase-T1 gap problems in budget', 'fraction of gap problems', 0.045, 0.015, 0.09, 0.008097165991902834, 'w', [[0.07, 0.02, 0.14], [0.1, 0.02, 0.22]], 0.701, 'n'],
    ['6.r6-account', 'p19', 'Share of math500-plainbase-T1 gap problems in answer-statement', 'fraction of gap problems', 0.38, 0.22, 0.55, 0.5141700404858299, 'wu', [[0.18, 0.06, 0.35], [0.15, 0.03, 0.38]], 3.0, ''],
    ['6.r6-account', 'p20', 'Share of math500-plainbase-T1 gap problems in slip', 'fraction of gap problems', 0.38, 0.25, 0.52, 0.2793522267206478, 'w', [[0.45, 0.25, 0.65], [0.48, 0.2, 0.72]], 0.6667, ''],
    ['6.r6-account', 'p21', 'Share of math500-plainbase-T1 gap problems in sharpening', 'fraction of gap problems', 0.165, 0.09, 0.25, 0.1659919028340081, 'w', [[0.22, 0.1, 0.36], [0.18, 0.05, 0.35]], 0.6787, ''],
    ['6.r6-account', 'p22', 'Share of math500-plainbase-T1 gap problems in reach', 'fraction of gap problems', 0.03, 0.005, 0.07, 0.032388663967611336, 'w', [[0.06, 0.01, 0.13], [0.04, 0.0, 0.1]], 0.6498, ''],
    ['6.r6-account', 'p24', 'RL-only minus plain-base-only (gross about 250 and 11)', 'problems', 239, 234, 243, 239, 't', [[239, 233, 245], [239, 225, 252]], 0.6131, ''],
    ['6.r6-account', 'p26', 'Share of math500-top8-T1 gap problems in budget', 'fraction of gap problems', 0.17, 0.08, 0.28, 0.2, 'w', [[0.26, 0.12, 0.4], [0.25, 0.08, 0.45]], 0.5257, ''],
    ['6.r6-account', 'p27', 'Share of math500-top8-T1 gap problems in answer-statement', 'fraction of gap problems', 0.034, 0.0, 0.09, 0.03636363636363636, 'wu', [[0.1, 0.0, 0.22], [0.12, 0.0, 0.28]], 1.4693, ''],
    ['6.r6-account', 'p28', 'Share of math500-top8-T1 gap problems in slip', 'fraction of gap problems', 0.19, 0.1, 0.3, 0.2, 'w', [[0.25, 0.1, 0.42], [0.28, 0.08, 0.5]], 0.7426, ''],
    ['6.r6-account', 'p29', 'Share of math500-top8-T1 gap problems in sharpening', 'fraction of gap problems', 0.47, 0.34, 0.6, 0.41818181818181815, 'wu', [[0.27, 0.12, 0.44], [0.22, 0.05, 0.42]], 1.3862, ''],
    ['6.r6-account', 'p30', 'Share of math500-top8-T1 gap problems in reach', 'fraction of gap problems', 0.136, 0.05, 0.23, 0.14545454545454545, 'w', [[0.1, 0.02, 0.22], [0.09, 0.0, 0.22]], 0.4466, ''],
    ['6.r6-account', 'p32', 'top8-only minus base-only (gross about 58 and 41)', 'problems', 17, 13, 19, 14, 't', [[17, 12, 22], [17, 10, 24]], -0.3073, ''],
    ['6.r6-account', 'p33', 'Share of math500-minp-T1 gap problems in loop', 'fraction of gap problems', 0.37, 0.25, 0.5, 0.40625, 'w', [[0.28, 0.14, 0.44], [0.32, 0.12, 0.52]], 0.7956, ''],
    ['6.r6-account', 'p34', 'Share of math500-minp-T1 gap problems in budget', 'fraction of gap problems', 0.21, 0.11, 0.32, 0.21875, 'w', [[0.17, 0.07, 0.3], [0.17, 0.04, 0.32]], 0.3818, ''],
    ['6.r6-account', 'p35', 'Share of math500-minp-T1 gap problems in answer-statement', 'fraction of gap problems', 0.03, 0.0, 0.08, 0.0, 'w', [[0.08, 0.0, 0.18], [0.08, 0.0, 0.2]], 1.0688, ''],
    ['6.r6-account', 'p36', 'Share of math500-minp-T1 gap problems in slip', 'fraction of gap problems', 0.12, 0.05, 0.21, 0.0625, 'w', [[0.18, 0.06, 0.32], [0.2, 0.05, 0.38]], 0.9275, ''],
    ['6.r6-account', 'p37', 'Share of math500-minp-T1 gap problems in sharpening', 'fraction of gap problems', 0.21, 0.12, 0.32, 0.234375, 'w', [[0.19, 0.07, 0.33], [0.15, 0.02, 0.32]], 0.5252, ''],
    ['6.r6-account', 'p38', 'Share of math500-minp-T1 gap problems in reach', 'fraction of gap problems', 0.06, 0.01, 0.13, 0.078125, 'l', [[0.1, 0.02, 0.2], [0.07, 0.0, 0.18]], 0.3269, ''],
    ['6.r6-account', 'p40', 'RL-only minus base-only at min-p 0.1 (gross about 70 and 14)', 'problems', 56, 50, 58, 55, 't', [[56, 51, 61], [56, 48, 64]], 0.3875, ''],
    ['6.r6-account', 'p41', 'Share of math500-s0400cue-T06 gap problems in loop', 'fraction of gap problems', 0.55, 0.42, 0.67, 0.52, 'l', [[0.6, 0.4, 0.8], [0.4, 0.18, 0.62]], 0.7394, ''],
    ['6.r6-account', 'p42', 'Share of math500-s0400cue-T06 gap problems in budget', 'fraction of gap problems', 0.15, 0.07, 0.25, 0.2, 'w', [[0.12, 0.03, 0.25], [0.12, 0.02, 0.26]], 0.485, ''],
    ['6.r6-account', 'p43', 'Share of math500-s0400cue-T06 gap problems in answer-statement', 'fraction of gap problems', 0.017, 0.0, 0.06, 0.013333333333333334, 'w', [[0.04, 0.0, 0.12], [0.07, 0.0, 0.18]], 1.2217, ''],
    ['6.r6-account', 'p44', 'Share of math500-s0400cue-T06 gap problems in slip', 'fraction of gap problems', 0.09, 0.03, 0.17, 0.12, 'l', [[0.1, 0.02, 0.2], [0.18, 0.04, 0.36]], 0.3592, ''],
    ['6.r6-account', 'p45', 'Share of math500-s0400cue-T06 gap problems in sharpening', 'fraction of gap problems', 0.15, 0.07, 0.25, 0.14666666666666667, 'w', [[0.1, 0.02, 0.2], [0.15, 0.02, 0.32]], 0.4331, ''],
    ['6.r6-account', 'p46', 'Share of math500-s0400cue-T06 gap problems in reach', 'fraction of gap problems', 0.043, 0.0, 0.1, 0.0, 'w', [[0.04, 0.0, 0.1], [0.06, 0.0, 0.16]], 0.0312, ''],
    ['6.r6-account', 'p48', 'Step-400-cue-only minus base-only at T 0.6 (gross about 60 and 30)', 'problems', 30, 8, 52, 50, 't', [[30, 23, 37], [30, 20, 40]], 3.0, ''],
    ['6.r6-account', 'p49', 'Share of math500-frcue-T06 gap problems in loop', 'fraction of gap problems', 0.58, 0.45, 0.7, 0.5697674418604651, 'w', [[0.55, 0.38, 0.72], [0.38, 0.16, 0.6]], 0.7571, ''],
    ['6.r6-account', 'p50', 'Share of math500-frcue-T06 gap problems in budget', 'fraction of gap problems', 0.15, 0.07, 0.25, 0.1744186046511628, 'w', [[0.12, 0.03, 0.24], [0.12, 0.02, 0.26]], 0.4419, ''],
    ['6.r6-account', 'p51', 'Share of math500-frcue-T06 gap problems in answer-statement', 'fraction of gap problems', 0.015, 0.0, 0.06, 0.011627906976744186, 'w', [[0.05, 0.0, 0.13], [0.08, 0.0, 0.2]], 1.4804, ''],
    ['6.r6-account', 'p52', 'Share of math500-frcue-T06 gap problems in slip', 'fraction of gap problems', 0.085, 0.03, 0.16, 0.10465116279069768, 'w', [[0.12, 0.03, 0.23], [0.18, 0.04, 0.36]], 0.6415, ''],
    ['6.r6-account', 'p53', 'Share of math500-frcue-T06 gap problems in sharpening', 'fraction of gap problems', 0.13, 0.06, 0.22, 0.13953488372093023, 'l', [[0.11, 0.03, 0.22], [0.16, 0.03, 0.33]], 0.4437, ''],
    ['6.r6-account', 'p54', 'Share of math500-frcue-T06 gap problems in reach', 'fraction of gap problems', 0.04, 0.0, 0.1, 0.0, 'w', [[0.05, 0.0, 0.12], [0.07, 0.0, 0.18]], 0.3881, ''],
    ['6.r6-account', 'p56', 'First-release-cue-only minus base-only at T 0.6 (gross about 68 and 48)', 'problems', 20, -5, 45, 33, 't', [[20, 13, 27], [20, 9, 31]], 1.3027, ''],
    ['6.r6-account', 'p57', "Fraction of math500-minp-T1 loop-part problems on which the cued base's untruncated T1 sample is right", 'fraction of problems', 0.7, 0.5, 0.87, 0.7692307692307693, 'w', [[0.55, 0.33, 0.77], [0.6, 0.35, 0.85]], 0.9858, ''],
    ['6.r6-account', 'p58', "Fraction of math500-minp-T1 budget-part problems on which the cued base's T1 sample is right", 'fraction of problems', 0.28, 0.08, 0.5, 0.2857142857142857, 'w', [[0.45, 0.2, 0.7], [0.4, 0.12, 0.7]], 0.6384, ''],
    ['6.r6-account', 'p59', 'Fraction of math500-s0400cue-T06 loop-part problems with kB >= 1 (at least one of the 3 cued T 1.0 evidence samples right)', 'fraction of problems', 0.9, 0.78, 0.97, 0.8974358974358975, 'w', [[0.75, 0.58, 0.9], [0.85, 0.65, 0.98]], 1.0445, ''],
    ['6.r6-account', 'p60', "Fraction of math500-plainbase-T1 answer-statement-part problems that the cued base's T1 sample gets right", 'fraction of problems', 0.84, 0.72, 0.93, 0.8661417322834646, 't', [[0.83, 0.65, 0.97], [0.85, 0.62, 1.0]], 0.4611, ''],
    ['6.r6-m01', 'p1', 'Late-vs-early deliberation density on long answers, base minus RL: the median over rows of r = (M_late + 1) / (M_early + 1), cued base minus RL, on hard328 answers of at…', 'difference of median ratios', -0.45, -0.8, -0.18, -0.2981493553527452, 'l', [[-0.25, -0.7, 0.15], [-0.12, -0.5, 0.25]], 0.0863, ''],
    ['6.r6-m01', 'p2', 'Late onset of textbook blocks in long cued-base answers: the share of hard328 base answers of at least 12,000 tokens that contain a textbook header line in their second…', 'fraction of problems', 0.25, 0.12, 0.42, 0.007352941176470588, 'l', [[0.15, 0.03, 0.35], [0.1, 0.01, 0.25]], -2.7171, ''],
    ['6.r6-m01', 'p3', 'Mechanism test, register decay in long base answers that end right. The failure-drift rival (deliberation is lost only when the base fails and gives up) predicts these a…', 'median ratio', 0.68, 0.45, 0.9, 0.6, 'wu', [[0.95, 0.6, 1.3], [0.95, 0.55, 1.4]], 1.4959, ''],
    ['6.r6-m04', 'p1', 'Cap-hit bump on the first 100 MATH-500: max cap hits of the two intermediate cue arms minus max cap hits of the two endpoint cue arms. The linear-path rival (WiSE-FT) pr…', 'problems of 100', 4, 1, 9, -2, 'l', [[3, -3, 10], [3, -3, 11]], -1.7764, 'n'],
    ['6.r6-m04', 'p2', 'Mechanism test, how early the length policy arrives: f = ln(M(sft025_cue)/M(base_cue)) / ln(M(sft1_cue)/M(base_cue)), M = median generated tokens of finished answers. Th…', 'fraction of the log length change', 0.8, 0.45, 1.3, 0.06468979820134287, 'l', [[0.4, -0.05, 0.9], [0.5, 0.05, 1.0]], -3.0, ''],
    ['6.r6-m04', 'p3', "Where the mechanism says the effect should not appear: share of the intermediate arms' cap hits that fall on problems that are short for Think-SFT (at or below sft1_cue'…", 'fraction of intermediate-arm cap hits', 0.12, 0.0, 0.35, 0.0, 'w', [[0.3, 0.05, 0.6], [0.25, 0.03, 0.52]], 1.255, ''],
    ['6.r6-m05', 'p1', 'Mechanism test: ratio of the RL/base hold-on rate ratio far from the last numeric result to the same ratio near it, R(d >= 1500) / R(d < 200), on finished MATH-500 answe…', 'ratio of rate ratios', 1.7, 1.15, 2.8, 0.9725264665193447, 'l', [[1.1, 0.7, 1.7], [1.1, 0.65, 1.75]], -1.4256, ''],
    ['6.r6-m05', 'p2', 'Case where the effect should not appear: the RL/base hold-on rate ratio within 200 characters after a stated numeric result (bin B1 alone). The overall written ratio is…', 'ratio of rates (RL / base)', 1.05, 0.8, 1.3, 1.3791965709443248, 'l', [[1.3, 0.9, 1.9], [1.3, 0.9, 1.85]], -1.643, 'n'],
    ['6.r6-m05', 'p3', 'Cause test against a position rival: the same far/near contrast R(d >= 1500) / R(d < 200), computed only on character positions in the first half of each answer. The riv…', 'ratio of rate ratios', 1.6, 1.1, 2.8, 0.9024747907285835, 'l', [[1.05, 0.6, 1.7], [1.1, 0.6, 1.85]], -1.1697, ''],
    ['6.r6-m06', 'p1', 'Paired tail-rate ratio on hard328: the pooled rate of sampled tokens with p < 0.01 per generated token, RL plain over base cue, on problems both models finished. This te…', 'ratio of pooled rates (RL / base)', 1.08, 0.86, 1.35, None, 'x', [], None, 'x:field n_tok_p_lt_1e2 does not exist in any of the 328 rows of e72c answers.jsonl (the day1_hard328-01 jobs predate the min-p change that added it)'],
    ['6.r6-m06', 'p2', "Cause: whether the cued base's wrong answers carry more low-probability tokens than its right ones at matched length, on hard328. This mechanism (errors are drawn from t…", 'ratio of pooled rates (wrong / right), wrong-count-weighted over length quartiles', 1.05, 0.85, 1.3, None, 'x', [], None, 'x:field n_tok_p_lt_1e2 does not exist in any of the 328 rows of e72c answers.jsonl (the day1_hard328-01 jobs predate the min-p change that added it)'],
    ['6.r6-m06', 'p3', "Where the effect should not appear: on hard328 problems where the cued base finished wrong and RL finished, whether RL's tail-rate change relative to the base differs be…", 'difference of mean natural-log rate ratios', 0.0, -0.18, 0.18, None, 'x', [], None, 'x:field n_tok_p_lt_1e2 does not exist in any of the 328 rows of e72c answers.jsonl (the day1_hard328-01 jobs predate the min-p change that added it)'],
    ['6.r6-m10', 'p1', 'Mechanism test. Paired finished-answer error rate, RL step 100 plain minus cued base, MATH-500 at T 0.6 / top-p 0.95, on problems where both answers finished. This mecha…', 'difference of fractions of problems', 0.0, -0.025, 0.025, -0.0463768115942029, 'l', [[-0.015, -0.05, 0.02], [0.0, -0.035, 0.035]], -2.7827, ''],
    ['6.r6-m10', 'p2', "Cause: whose deliberative length step 100 has. Median per-problem log ratio of step-100 finished length to the cued base's finished length, same problems. This mechanism…", 'natural-log ratio (median over problems)', 0.05, -0.15, 0.25, 0.30830135965451666, 'l', [[0.15, -0.1, 0.42], [0.08, -0.18, 0.35]], -1.2657, ''],
    ['6.r6-m10', 'p3', "Case where an effect should not appear: the opening cue's value at step 100. On the base the cue is worth many points; if step 100 already writes the cue's opening by it…", 'difference of fractions of problems', 0.0, -0.035, 0.035, -0.01904761904761909, 'w', [[0.0, -0.045, 0.045], [0.01, -0.03, 0.05]], 0.2541, ''],
    ['6.r6-m11', 'p3', "Cause share: of the cued base's quick finished-wrong T1 answers (at most 2,000 generated tokens), the fraction that are early-marker answers. The rival (slow-reasoning s…", 'fraction of problems', 0.45, 0.2, 0.75, 0.0, 'l', [[0.35, 0.08, 0.65], [0.3, 0.05, 0.6]], -1.8066, ''],
    ['6.r6-m11', 'p4', "Where the effect should be absent: share of RL's finished plain T 1.0 answers (T2) that are early-marker answers.", 'fraction of finished answers', 0.06, 0.0, 0.15, 0.04251012145748988, 'w', [[0.2, 0.04, 0.45], [0.15, 0.03, 0.35]], 1.4891, ''],
    ['6.r6-m11', 'p2', "Mechanism test: among the cued base's early-marker finished-wrong T1 answers, the share whose final answer equals the first-marker value. Answer-first commitment predict…", 'fraction of problems', 0.8, 0.6, 0.95, None, 'x', [], None, 'x:refuted without a number: statistic below 0.6, or fewer than 8 kept rows'],
    ['7.r6-m06', 'p1', 'Paired tail-rate ratio on hard328: the pooled rate of sampled tokens with p < 0.01 per generated token, RL plain over base cue, on problems both models finished. This te…', 'ratio of pooled rates (RL / base)', 1.08, 0.86, 1.35, None, 'x', [], None, 'x:field n_tok_p_lt_1e2 does not exist in any of the 328 rows of abaybektursun-1114-151534-e72c answers.jsonl'],
    ['7.r6-m06', 'p2', "Cause: whether the cued base's wrong answers carry more low-probability tokens than its right ones at matched length, on hard328. This mechanism (errors are drawn from t…", 'ratio of pooled rates (wrong / right), wrong-count-weighted over length quartiles', 1.05, 0.85, 1.3, None, 'x', [], None, 'x:field n_tok_p_lt_1e2 does not exist in any of the 328 rows of abaybektursun-1114-151534-e72c answers.jsonl'],
    ['7.r6-m06', 'p3', "Where the effect should not appear: on hard328 problems where the cued base finished wrong and RL finished, whether RL's tail-rate change relative to the base differs be…", 'difference of mean natural-log rate ratios', 0.0, -0.18, 0.18, None, 'x', [], None, 'x:field n_tok_p_lt_1e2 does not exist in any of the 328 rows of abaybektursun-1114-151534-e72c answers.jsonl'],
    ['7.r7-m03', 'p1', 'Mechanism test: ratio of the self-inconsistent-equation rate of the cued base at T 1.0 to the same rate at T 0.6 / top-p 0.95, on problems where both answers finished. T…', 'ratio of wrong-equation rates (T 1.0 / T 0.6)', 3.0, 1.5, 9.0, 0.3612012987012987, 'l', [[1.6, 0.8, 3.0], [1.5, 0.8, 2.8]], -0.2091, ''],
    ['7.r7-m03', 'p2', "Cause (RL sharpened the result positions): ratio of RL's self-inconsistent-equation rate at T 1.0 to the cued base's at T 1.0, on problems where both finished.", 'ratio of wrong-equation rates (RL / base)', 0.35, 0.12, 0.8, 1.3591903274011683, 'l', [[0.55, 0.25, 1.1], [0.5, 0.25, 1.0]], -3.0, 'n'],
    ['7.r7-m03', 'p3', 'Effect in accuracy: paired finished-answer error, plain T 1.0 minus the entropy-gated arm that samples at T 0.6 where entropy <= 0.9 nats (confident positions, which inc…', 'difference of fractions of samples', 0.013, -0.002, 0.032, 0.017293233082706763, 'l', [[0.015, -0.01, 0.04], [0.025, 0.005, 0.045]], 0.2938, ''],
    ['7.r7-m03', 'p4', 'Where the effect should not appear: the same paired finished-answer error difference for the arm that samples at T 0.6 only where entropy > 0.9 nats (forks). Result toke…', 'difference of fractions of samples', 0.0, -0.02, 0.017, -0.003293084522502737, 'w', [[0.0, -0.03, 0.03], [0.008, -0.015, 0.03]], 0.4751, ''],
    ['7.r7-m05', 'p1', 'Mechanism test, problem dependence of misread and slip steps. Among the wrongstep items labelled misread or slip, the fraction with g > 0, where g = (lp_span - lp_contro…', 'fraction of items', 0.67, 0.48, 0.84, 0.6857142857142857, 'w', [[0.55, 0.33, 0.77], [0.63, 0.42, 0.82]], 0.4211, ''],
    ['7.r7-m05', 'p2', 'Cause test, mode vs tail. On all 51 wrongstep items, the fraction whose wrong step gains on control text when the base is rescored at T 0.6: (lp_span - lp_control) under…', 'fraction of items', 0.62, 0.44, 0.8, 0.6078431372549019, 'w', [[0.58, 0.4, 0.75], [0.55, 0.38, 0.72]], 0.0455, ''],
    ['7.r7-m05', 'p3', 'Case where the effect should not appear: wrong-plan items. The fraction of wrongstep items labelled as a wrong plan with g > 0 (g defined as in the first prediction: nop…', 'fraction of items', 0.43, 0.15, 0.68, 0.6875, 'l', [[0.5, 0.25, 0.75], [0.55, 0.3, 0.8]], -0.766, 'n'],
    ['7.r7-m07', 'p1', 'Phenomenon on Math: Math 3.1 cue minus Math 3.0 cue right answers in the longest quartile of MATH-500 by RL (T2) answer length, T 1.0 / top-p 1.0, one sample each.', 'problems (of 125)', 7, -1, 15, 3, 'l', [[6, -1, 13], [6, -2, 13]], -0.205, ''],
    ['7.r7-m07', 'p2', 'Where the effect should not appear: Math 3.1 cue minus Math 3.0 cue right answers on the shorter half (Q1+Q2 by T2 length) of MATH-500, T 1.0. A stop-early policy loses…', 'problems (of 250)', 0, -5, 4, 1, 'l', [[1, -5, 6], [1, -5, 6]], 0.1339, ''],
    ['7.r7-m07', 'p3', 'Mechanism test (length shortening confined to long problems), Math 3.0 first release vs Math 3.1 step 2,800, plain MATH-500, T 0.6 / top-p 0.95: median log ratio of fini…', 'difference of natural-log ratios', -0.12, -0.3, 0.0, -0.3708847115189001, 'w', [[-0.05, -0.3, 0.2], [-0.15, -0.45, 0.12]], -1.8815, 'n'],
    ['7.r7-m07', 'p4', 'Cause test, the 12k cliff: among finished MATH-500 answers at T 0.6 / top-p 0.95 (plain and cue pooled), the ratio of answers of at least 12,000 tokens to answers of 8,0…', 'ratio of tail ratios', 0.35, 0.1, 0.75, 0.5019834114677245, 'l', [[0.6, 0.25, 1.2], [0.4, 0.12, 1.0]], 0.11, ''],
    ['7.r7-m08', 'p1', "Mechanism test, concentration of Code 3.1's wrong-step lowering on Math 3.1's strongest-veto items: the share of the summed Code 3.1 D that falls on the third of items w…", 'fraction of summed D', 0.72, 0.48, 1.05, 0.9786482311969817, 'w', [[0.7, 0.35, 1.05], [0.6, 0.25, 1.05]], 0.1633, ''],
    ['7.r7-m08', 'p2', "Where the effect should not appear: Code 3.1's mean wrong-step lowering on items labelled wrong plan. A reader who spreads Code 3.1's overall -0.45 evenly expects about…", 'nats (mean D over items)', 0.0, -0.3, 0.3, -0.27313356644510706, 'l', [[-0.2, -0.7, 0.2], [-0.1, -0.6, 0.35]], -0.5862, ''],
    ['7.r7-m08', 'p3', 'Where a veto cannot create a path: Code 3.1 cue single-sample accuracy on the MATH-500 problems where the cued base is right in none of its 4 stored samples. A veto remo…', 'fraction of problems', 0.18, 0.06, 0.33, 0.2727272727272727, 'l', [[0.18, 0.06, 0.33], [0.2, 0.06, 0.38]], -0.0989, ''],
    ['7.r7-m09', 'p1', 'Mechanism test, recurrence across prompts. On problems the cued base solves 4 of 4, take the problems where Think-SFT with the cue gives a finished wrong answer, and com…', 'fraction of problems', 0.55, 0.3, 0.85, 0.16666666666666666, 'l', [[0.4, 0.1, 0.75], [0.4, 0.12, 0.7]], -1.7328, 'n'],
    ['7.r7-m09', 'p2', 'Cause, answer-type dependence. Among the problems in W (cued base 4 of 4, Think-SFT cue finished wrong), the share whose gold is not a plain integer. Format misses fall…', 'fraction of problems', 0.7, 0.45, 0.95, 0.3333333333333333, 'l', [[0.55, 0.25, 0.85], [0.55, 0.3, 0.8]], -1.9604, 'n'],
    ['7.r7-m09', 'p3', "A case where Think-SFT's dominant failure should not appear: the share of cap hits among Think-SFT cue's wrong answers on problems the cued base solves 4 of 4. Over all…", 'fraction of wrong problems', 0.22, 0.0, 0.45, 0.3333333333333333, 'l', [[0.33, 0.1, 0.6], [0.3, 0.1, 0.55]], -0.2764, ''],
    ['7.r7-m09', 'p4', "Mechanism test, normal length. On problems the cued base solves 4 of 4, compare Think-SFT cue's finished-wrong and finished-right answers by their length relative to RL'…", 'natural-log ratio (difference of medians)', 0.0, -0.4, 0.4, 0.19084698150089882, 'l', [[0.15, -0.4, 0.7], [0.15, -0.35, 0.65]], -0.0301, ''],
    ['7.r7-m11', 'p1', 'Mechanism test: within-cue wrong-answer agreement minus cue-vs-plain wrong-answer agreement on MATH-500 at T 1.0, A - B. The problem-driven-attractor rival predicts abou…', 'difference of agreement fractions', 0.1, 0.02, 0.22, 0.13463203463203466, 'w', [[0.1, -0.05, 0.25], [0.08, -0.03, 0.2]], 0.2989, ''],
    ['7.r7-m11', 'p2', 'Case where the effect should not appear: changing only the sampling rule under the same cue (T 1.0 / min-p 0.1) should keep the wrong values. Cross-file agreement C betw…', 'difference of agreement fractions', 0.0, -0.08, 0.08, 0.16378066378066375, 'w', [[0.0, -0.12, 0.1], [-0.02, -0.1, 0.06]], -1.6814, 'n'],
    ['7.r7-m11', 'p3', 'Cause of the vote shortfall: among MATH-500 problems where the cued base has at least one right sample of 4 but the plurality vote is wrong, the share where the winning…', 'fraction of vote-failure problems', 0.45, 0.28, 0.65, 0.42857142857142855, 'w', [[0.45, 0.25, 0.65], [0.55, 0.33, 0.77]], 0.2914, ''],
    ['7.r7-m12', 'p1', 'Mechanism test: per-problem gain of the RL-written-examples arm (draw 1) over the mean of the 4 cued-base samples, averaged over problems in the subjects of example prob…', 'difference of fractions of problems', 0.08, 0.035, 0.13, -0.018489574809335205, 'l', [[0.02, -0.03, 0.07], [0.01, -0.06, 0.08]], -3.0, ''],
    ['7.r7-m12', 'p2', 'Case where the effect should not appear: the same matched-minus-unmatched contrast for the base-written-examples arm, which uses the same three example problems and so t…', 'difference of fractions of problems', 0.0, -0.045, 0.045, -0.02192645085267258, 't', [[0.0, -0.05, 0.05], [0.0, -0.07, 0.07]], 0.1434, ''],
    ['7.r7-m12', 'p3', 'Cause: the examples only let the base copy a routine on problems it can already solve. On problems the cued base solved in 0 of its 4 samples, the RL-written-examples ar…', 'problems', 5, 1, 9, 5, 't', [[5, 1, 10], [5, 1, 10]], 0.1178, ''],
]

# A short name of each theory, 3 to 5 words from its statement (at most 26 characters), shown at the left of its row
# in a round. A theory missing here (a new round) shows the first words of its statement; the check prints which ones
# lack a name.
NAMES = {
    'r1-across-1': 'Self-copying circuits',
    'r1-across-2': 'Token-budget controller',
    'r1-all-1': 'Base decays as text grows',
    'r1-all-2': 'One answer-mode switch',
    'r1-surprises-1': 'Deliberation and stopping',
    'r1-surprises-2': 'Only low-rank part works',
    'r2-across-1': 'Entropy drops at forks',
    'r2-across-2': 'Sign pattern carries it',
    'r2-all-1': 'High-curvature signs',
    'r2-all-2': 'Surprise sets accuracy',
    'r2-external-1': '700 times a random edit',
    'r2-external-2': 'Per-position temperature',
    'r2-revise-1': 'Many small sign entries',
    'r2-revise-2': 'Weak base error detector',
    'r2-surprises-1': 'Loops, slips on one axis',
    'r2-surprises-2': 'Task lives in the signs',
    'r3-across-1': 'General plus math part',
    'r3-across-2': 'Tail tokens end loops',
    'r3-all-1': 'Two stopping habits',
    'r3-all-2': 'Spread at progress steps',
    'r3-external-1': 'Truncation causes repeats',
    'r3-external-2': 'Sharpening, then late part',
    'r3-revise-1': 'Deliberate, then commit',
    'r3-revise-2': 'Loops open at impasses',
    'r3-surprises-1': 'Tail tokens derail steps',
    'r3-surprises-2': 'Shared low-dose stop gate',
    'r4-m01': 'Loops feed on own text',
    'r4-m02': 'Length reads out failure',
    'r4-m04': 'Mix of two endpoint modes',
    'r4-m06': 'Constant hold-on bias',
    'r4-m07': 'Shared wrong attractors',
    'r4-m08': 'Recall from pretraining',
    'r4-m09': 'Code-RL as ending policy',
    'r4-m10': 'Early RL lowers entropy',
    'r4-m11': 'Writing past the answer',
    'r4-m12': 'Grader false negatives',
    'r5-m02': 'Wrong samples run short',
    'r5-m03': 'Top-8 edit acts as cue',
    'r5-m04': 'Think-SFT cap hits',
    'r5-m05': 'Restate, not re-derive',
    'r5-m06': 'Gain on rarely solved',
    'r5-m07': 'Step 100 is the opening',
    'r5-m08': 'Code 3.0 runaway length',
    'r5-m09': 'Boxing a given number',
    'r5-m10': 'Two modes from the start',
    'r5-m11': 'Code habit, discrete math',
    'r5-m03-rival': 'Top-8: incomplete switch',
    'r5-m10-rival': 'Robust to sampling noise',
    'r6-account': 'Six rules split the gap',
    'r6-m01': 'Cue register fades',
    'r6-m04': 'Length policy comes early',
    'r6-m05': 'Hold-on words on a timer',
    'r6-m06': 'Wrong steps, head tokens',
    'r6-m10': 'Step 100 sets opening',
    'r6-m11': 'Commit early, justify',
    'r6-account-rival': 'One difficulty axis',
    'r7-m03': 'Wrong number-token draws',
    'r7-m05': 'Slips from generic prior',
    'r7-m07': '3.0 stops before 12k',
    'r7-m08': 'Code-RL cuts slips',
    'r7-m09': 'Formats grader rejects',
    'r7-m11': 'Opening sets wrong value',
    'r7-m12': 'Examples help own subject',
}
_norm = lambda t: ("r1-" + t[2]) if t[1] == 1 else t[2]
_NAME = {t[0]: NAMES.get(_norm(t)) or " ".join(t[3].split()[:4]) for t in THEORIES}

DATA.update(COUNTS)
N, RD, G, T, A = DATA["nearer"]["all"], DATA["readers"]["all"], DATA["gain"]["all"], DATA["theories"], DATA["account"]
ROUNDS = [int(r) for r in T["per_round"]]
R = ROUNDS[-1]  # the last round
_word = lambda n: ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
                   "twelve"][n] if n <= 12 else str(n)
_m = lambda x: f"{x}".replace("-", "−")
LINE = f"Our theories were nearer the measured number than readers with no theory in {N[0]} of {N[1]} predictions: no better."

_p = {(p[0], p[1]): p for p in PREDS}
_c1, _c2 = _p[("4.r4-m10", "p1")], _p[("4.r4-m10", "p2")]
_g = next(t for t in THEORIES if t[0] == "5.r5-m10")[9]
_f = lambda x: _m(f"{x:.3f}".rstrip("0").rstrip("."))
CASES = {
    "4.r4-m10": f"Example, board item result-32b7a8. This theory said RL's first 100 to 400 steps raise the share of "
                f"answers cut off at 16,384 tokens (T 0.6); both readers said the share would fall. Measured: up "
                f"{_f(_c1[7])} at step 100 and {_f(_c2[7])} at step 400, inside the theory's intervals. The theory still "
                "lost to a rival that explains the rise by the opening RL learns.",
    "5.r5-m10": f"Example, board item {_g[0]}: the first GPU experiment the engine chose. The base drew its own openings "
                f"and continued the first that starts a line with Okay. This theory predicted {_g[4][0]} of {_g[2]} right "
                f"({_g[4][1]} to {_g[4][2]}); its rival {_g[5][0]} ({_g[5][1]} to {_g[5][2]}). Measured: {_g[1]}, "
                "outside this theory's interval and inside the rival's.",
}
EXAMPLES = [["4.r4-m10", "Example: cut-offs rise early in RL"], ["5.r5-m10", "Example: the first GPU test"]]

_filed, _done = DATA["computed"]["all"][1], DATA["computed"]["all"][0]
_new = [t for t in THEORIES if t[1] == R and t[2].startswith(f"r{R}-")]  # the last round's new theories
_newfate = lambda f: sum(t[5] == f for t in _new)
_carried = {r: sum(p[8] == "c" for p in PREDS if p[0].startswith(f"{r}.")) for r in ROUNDS}
PANELS = [
    ["new", "What is new",
     f"{_word(R).capitalize()} rounds of the theory engine scored every theory on numbers it had not seen, against two "
     "readers with no theory: two model runs given the same board items and the same question.",
     [f"Rounds 1 to 3 predicted numbers that other agents posted to the board after a cutoff. Rounds 4 to {R} predicted "
      "numbers that scripts, written before any row was read, then computed from stored per-problem rows.",
      f"{T['proposed']} theories filed {_filed} predictions, each a number with an interval; {_done} were computed and {N[1]} were "
      "also predicted by the readers.",
      "Language-model forecasters have been compared with human crowds (Halawi et al., arXiv 2402.18563). Here the "
      "baseline is a reader of the same board with no theory, so a win measures what the theory adds."]],
    ["why", "Why it matters",
     f"A theory that is no nearer than a reader with no theory adds nothing a careful reader of the board does not "
     f"already know. So far the theories were nearer in {N[0]} of {N[1]} predictions, about half.",
     [f"Where the readers also gave intervals ({RD[3]} predictions, rounds 3 to {R}), the theories' 90 % intervals held "
      f"the measured number {RD[0]} times, the two readers' {RD[1]} and {RD[2]} times.",
      f"The engine's own score, which also rewards narrow intervals, gave the measured numbers less probability under "
      f"the theories than under the readers: {_m(G)} nats in total over those {RD[3]}.",
      f"Of {T['proposed']} theories, {T['refuted']} were refuted by a measured number or a review and {T['lost']} lost to "
      f"a rival theory; {T['nogain']} gained nothing over the readers. After round {R} "
      + (f"{len(T['standing'])} stand" if T["standing"] else "no theory stands")
      + ": a theory stands when it survives its tests and beats a fresh rival on at least 2 tests that separate the two "
      "(engine 7.1)."
      + (f" Survives its tests but does not beat its rival: {', '.join(sorted(set(T['survive']) - set(T['standing'])))}."
         if set(T["survive"]) - set(T["standing"]) else ""),
      f"Round {R}: of {len(_new)} new theories, {_newfate('r')} were refuted by their own predictions and "
      f"{_newfate('n')} gained nothing over the readers: none of their predictions landed inside its interval where "
      "both readers' forecasts were outside it, or their total score against the readers was not above 0.",
      "Engine 6.3 said two theories stood after round 6. Re-scored under the 7.1 rule, neither does: each beat its "
      "rival on 1 separating test of 6 (studies/theory/README.md, Round 06, correction)."]],
    ["how", "How we know",
     f"Every mark is read from the committed metrics files of the {_word(R)} rounds; no number on the page is typed by "
     "hand.",
     ["A mark is one prediction. Its interval is drawn at one fixed height, so a dot inside the band means the "
      "measured number fell inside the interval; above the band, it was higher than predicted.",
      f"Blue: the theory's forecast was nearer the measured number than the average of the two readers' forecasts. "
      f"Ring: the readers' average was nearer, or equally near ({N[2]} ties).",
      f"{_filed - _done} predictions were never computed (a missing package, an unreadable file, a group too small) and "
      "are drawn as faint lines without a dot. Rows the engine does not score (shares that are 0 by construction, fits "
      "to claimed cells, one number that differs from its replication) are left out.",
      "Fates: refuted (a measured number met its refuting condition, or a review), lost to its rival, no gain (no "
      "better than the readers by the engine's score), untested (no prediction computed), survives. Refuted and lost "
      "rows are struck."]],
    ["limits", "What it does not show",
     "It does not show that the theories are wrong. A theory can lose on its numbers and still name a true mechanism, "
     "and a win on one number does not prove a mechanism.",
     [f"Round 6's lead comes from one account of the gap: its {A[0]} predicted shares were nearer in {A[1]}. Without it, "
      f"round 6's theories were nearer in {A[3]} of {A[2]}.",
      "Rounds 1 and 2 used the same held-out board numbers, so the six round-1 theories predicted some of them twice. "
      "Their readers gave single numbers, so those rounds have no interval comparison.",
      f"Round 6 holds {_carried[6]} predictions carried from round 5: duel tests compared with the theory they replaced, "
      "not with readers. They are grey and not counted. From round 7 (engine 7.1) a carried theory files no prediction, "
      "so its row has no mark. GPU predictions are left out, except the one that was run, shown under its theory."]],
    ["run", "How to reproduce it",
     "uv run tools/finding_theories_on_trial.py, from the repository root, rebuilds every mark from the round files and "
     "checks the copy on this page and every count.",
     [f"Round files: {E}round-01 to round-{R:02d} (metrics, targets, test recipes, reviews, duels), as of commit "
      f"{DATA['commit']}. Statements: the tables of studies/theory/README.md.",
      "The engine and its score: studies/theory/lib/round.py and .claude/skills/theory/SKILL.md.",
      "Board items: result-8b0706 (round 6), result-5115c5 (round 7), result-32b7a8 (cut-offs rise early), "
      "result-3a3af3 (the first GPU test)."]],
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
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table
   with a cast shadow in place of the glow. The light comes from the upper left in both. Blue marks a prediction where
   the theory was nearer than the readers; a ring, one where the readers were nearer. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --tick: #8b97a1; --band: rgba(16, 24, 32, .075); --ring: #56636d; --grey: #a3adb5;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --tick: #66737e; --band: rgba(233, 239, 243, .07); --ring: #9aa7b2; --grey: #56626c;
  }
}
:root[data-theme="dark"] {
  --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
  --blue: #8fb1ff; --red: #ff6b7c;
  --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
  --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
  --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
  --tick: #66737e; --band: rgba(233, 239, 243, .07); --ring: #9aa7b2; --grey: #56626c;
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

/* The picture: one plate with every prediction, the count and the one control */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg { width: 100%; max-height: calc(100vh - 210px); display: block; overflow: visible; cursor: default; user-select: none; -webkit-user-select: none; }
svg:focus:not(:focus-visible) { outline: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.base { transition: opacity .3s ease; }
.base.dim { opacity: .28; }
.k-band { fill: var(--band); }
.k-tick { fill: none; stroke: var(--tick); stroke-linecap: round; }
.k-rdr { fill: none; stroke: var(--ring); stroke-width: 1.1; opacity: .7; stroke-linecap: round; }
.k-ghost { fill: none; stroke: var(--tick); stroke-dasharray: 1.6 1.8; stroke-width: 1; }
.k-win { fill: var(--blue); }
.k-halo { fill: none; stroke: var(--blue); opacity: calc(var(--bloom) * .3); }
.k-lose { fill: var(--sheet); stroke: var(--ring); stroke-width: 1.1; }
.k-carr { fill: var(--grey); }
.k-strike { fill: none; stroke: var(--mute); stroke-width: 1.3; stroke-linecap: round; }
.selbox { fill: none; stroke: var(--ink); stroke-width: 1.2; }
.burst { fill: none; stroke: var(--blue); }
.cap { font-weight: 640; }
.big { font-weight: 660; letter-spacing: -.035em; font-stretch: 100%; }
.lab { fill: var(--mute) !important; font-weight: 520; }
.set { fill: var(--ink) !important; font-weight: 640; }
.rl { fill: var(--mute) !important; font-weight: 600; transition: opacity .35s ease; }
.fl { fill: var(--mute) !important; font-weight: 520; transition: opacity .3s ease; }
.nm { fill: var(--ink) !important; font-weight: 560; transition: opacity .3s ease; }
.nm.off { fill: var(--mute) !important; }
.blab { fill: var(--mute) !important; font-weight: 520; transition: fill .3s ease; }
.blab.on { fill: var(--ink) !important; font-weight: 660; }
.btrack { stroke: var(--faint); stroke-width: 1; opacity: .4; }
.bfill { stroke: var(--mute); stroke-width: 3; stroke-linecap: round; opacity: .55; transition: opacity .3s ease; }
.bfill.on { stroke: var(--blue); opacity: 1; }
.bhalf { stroke: var(--ink); stroke-width: 1.2; opacity: .55; }
.kt { fill: var(--mute) !important; font-weight: 520; }
.ctl { display: flex; align-items: center; gap: 12px; align-self: center; margin-top: 16px; }
.ctl .lbl { font-size: 13px; color: var(--mute); }
.switch { display: inline-flex; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { min-width: 40px; padding: 8px 14px; border-radius: 999px; font-weight: 600; font-size: 14.5px; text-align: center; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button[aria-pressed="true"]:hover { color: var(--paper); }
.hint { align-self: center; margin: 10px 0 0; font-size: 13px; color: var(--mute); }

/* One drawn entrance, then only the slow sway, one replayed prediction at a time, and what the reader changes */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .field { animation: fade .9s .45s both; }
.enter .read, .enter .key { animation: fade .7s .8s both; }

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
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 0 6px 12px 0; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.lead.st { font-size: clamp(16px, 1.15vw, 19px); max-width: 34ch; }
.case { margin: 16px 0 0; padding: 10px 0 10px 12px; border-left: 2px solid var(--blue); font-size: 14.5px; line-height: 1.45; max-width: 44ch; }
.tag { margin: 10px 0 0; font-size: 13.5px; color: var(--mute); }
.tag b { color: var(--ink); font-weight: 640; }
.tag s { text-decoration-thickness: 1px; }
.why { margin: 10px 0 0; font-size: 14px; line-height: 1.45; color: var(--mute); max-width: 44ch; overflow-wrap: anywhere; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
h3 { margin: 22px 0 0; font-size: 14px; font-weight: 660; font-stretch: 110%; padding-bottom: 6px; border-bottom: 1px solid var(--rule); }
.preds { list-style: none; margin: 0; padding: 0; max-width: 44ch; }
.preds li { padding: 10px 0 10px 10px; border-bottom: 1px solid var(--rule); border-left: 2px solid transparent; font-size: 13.5px; color: var(--mute); }
.preds li.w { border-left-color: var(--blue); }
.preds .pw { color: var(--ink); line-height: 1.4; overflow-wrap: anywhere; }
.preds svg { width: 100%; max-width: 300px; height: 30px; margin: 6px 0 2px; max-height: none; }
.preds .pv b { color: var(--ink); font-weight: 640; }
.preds .pr { font-size: 12.5px; }
.m-th { stroke: var(--ink); stroke-width: 2.4; stroke-linecap: round; }
.m-rd { stroke: var(--faint); stroke-width: 1.4; stroke-linecap: round; opacity: .8; }
.m-c { fill: var(--faint); }
.m-me { stroke: var(--blue); stroke-width: 1.6; }
.m-ax { stroke: var(--rule); stroke-width: 1; }
.duel { font-size: 13.5px; color: var(--mute); max-width: 44ch; }
.duel p { margin: 8px 0 0; }
.duel b { color: var(--ink); font-weight: 640; }
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
  .stage { order: 3; margin-top: 22px; padding: 0; display: block; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
  .ctl { flex-direction: column; gap: 8px; margin-top: 14px; }
  .switch { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); width: 100%; border-radius: 18px; }
  .switch button { min-width: 0; padding: 10px 0; font-size: 14px; border-radius: 14px; }
  .hint { text-align: center; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a, .base, .blab, .bfill, .rl, .fl, .nm { transition: none; }
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
    <svg id="svg" role="img" tabindex="0"></svg>
    <div class="ctl">
      <span class="lbl" id="ctllbl">Round</span>
      <div class="switch" id="switch" role="group" aria-labelledby="ctllbl">
      </div>
    </div>
    <p class="hint">Click a theory's marks, or press Enter on the picture, to see its predictions.</p>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const fmt = n => Math.round(n).toLocaleString("en-US");
const minus = s => String(s).replace(/^-/, "−");
/* A forecast or a measured number as the files hold it, at a precision that keeps it readable. */
function fv(x) {
  if (x == null) return "none";
  const a = Math.abs(x);
  let s = a >= 100 ? Math.round(a).toLocaleString("en-US") : a >= 10 ? String(+a.toFixed(1)) : a === 0 ? "0" : String(+a.toPrecision(3));
  return (x < 0 ? "−" : "") + s;
}
const pct = (a, b) => (100 * a / b).toFixed(1) + " %";

/* The states of the control: one per round, then all of them. */
const STATES = [...C.rounds.map(String), "all"], ALL = C.rounds.length;
const SNAME = s => s === ALL ? "All rounds" : "Round " + STATES[s];
const KIND = r => r <= 3 ? "posted to the board later" : "computed from stored rows";
const FATE_ORDER = { s: 0, n: 1, o: 2, l: 3, r: 4 };
const SHORT = { "did not beat the readers": "beat no reader", "passed the score": "passed", "failed the score": "failed the score",
  "refuted by its review": "refuted", "lost to its rival": "lost to its rival" };
/* A survivor stands only when it beat its rival on at least 2 separating tests (the duel rule of engine 7.1). */
const noWin = t => t.fate === "s" && t.duel && !(t.duel[2] === "beats rival" && t.duel[3] >= 2);
const fateLabel = t => noWin(t) ? "survives, no duel win" : (SHORT[t.state] || t.state);
const struck = t => t.fate === "r" || t.fate === "l";

/* THEORIES and PREDS of tools/finding_theories_on_trial.py; the fields are in its _build() docstring. */
const TH = C.theories.map(([key, round, id, st, state, fate, why, review, duel, gpu], i) =>
  ({ i, key, round, id, st, state, fate, why, review, duel, gpu, name: C.names[key], preds: [] }));
const TK = Object.fromEntries(TH.map(t => [t.key, t]));
const PR = C.preds.map(([key, label, what, unit, v, lo, hi, m, mark, rd, gain, note], i) => {
  const t = TK[key], half = (hi - lo) / 2, mid = (lo + hi) / 2;
  const z = m == null ? 0 : half > 0 ? (m - mid) / half : m === mid ? 0 : Math.sign(m - mid) * 9;
  const zz = x => half > 0 ? (x - mid) / half : x === mid ? 0 : Math.sign(x - mid) * 9;
  const p = { i, t, label, what, unit, v, lo, hi, m, mark: mark[0], u: mark.length > 1, rd, gain, note, z, rz: rd.map(r => zz(r[0])), inside: m != null && lo <= m && m <= hi };
  t.preds.push(p);
  return p;
});
const N = PR.length;
const BYROUND = C.rounds.map(r => TH.filter(t => t.round === r)
  .sort((a, b) => FATE_ORDER[a.fate] - FATE_ORDER[b.fate] || b.preds.length - a.preds.length || a.i - b.i));
const ORDER = BYROUND.flat().flatMap(t => t.preds);  // the order of the stagger
ORDER.forEach((p, k) => { p.o = k; });
const ROWS = Math.max(...BYROUND.map(ts => ts.length));  // the most theories in one round
const S = { s: ALL, open: null, g: null, el: {}, shown: {}, t: 0, last: 0, t0: -1e9, n0: 0, n1: 0, d0: 0, d1: 0, dirty: true, from: null, rp: null, rpNext: 0, rpAt: 0, m: [1, 0, 0, 1, 0, 0] };

/* Geometry, in a small 3D space around the plate's centre (x right, y down, z toward the viewer). The field of marks is
   laid out flat, in its own units, and drawn through one affine map of the projection. */
function geo() {
  return narrow.matches
    ? { w: 480, cx: 240, D: 2000, r: 22, deep: 30, blur: 12, fs: 17.5, fc: 17, phone: true,
        fx: 26, fy: 104, W: 428, H: 640, nameW: 0, fateW: 0, top: 22, capX: 26, capY: [48, 72], cap: ["Each mark is one prediction: its interval", "(line) and the measured number (dot)"],
        keyY: [786, 816], setY: 900, bigX: 26, bigY: 988, fb: 100, labX: 28, labY: [1028, 1052, 1076, 1108], barX: [28, 452], barY: 1156, barH: 36,
        noteY: [1454, 1480], fl: 17, fn: 17, fr: 17, h: 1512, a: [6, 8, 474, 1504] }
    : { w: 1000, cx: 500, D: 2200, r: 30, deep: 40, blur: 16, fs: 15, fc: 13.5,
        fx: 50, fy: 96, W: 572, H: 424, nameW: 184, fateW: 146, top: 0, capX: 50, capY: [64], cap: ["Each mark is one prediction: its interval (line) and the measured number (dot)"],
        keyY: [556], setY: 104, bigX: 652, bigY: 196, fb: 104, labX: 655, labY: [228, 247, 266, 290], barX: [655, 940], barY: 318, barH: 23,
        noteY: [514, 532], fl: 14, fn: 13, fr: 13, h: 600, a: [24, 18, 976, 582] };
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

/* The target of every mark and every theory in each state, in field units. All: one strip per round, the theories side
   by side. A round: one row per theory, the marks of the other rounds fading back to their strips. */
function layouts(g) {
  const W = g.W, H = g.H, L = [];
  const all = { P: [], G: [], lab: [] }, sh = H / ALL, lab = g.phone ? 22 : 16;
  BYROUND.forEach((ts, k) => {
    const marks = ts.reduce((a, t) => a + t.preds.length, 0), withM = ts.filter(t => t.preds.length).length;
    const pitch = Math.min(9, W / (marks + 2.4 * (withM - 1))), y = k * sh + lab + (sh - lab) / 2, b = Math.min(6, (sh - lab) * .13);
    all.lab.push([0, k * sh + lab - 6]);
    let x = pitch / 2;
    ts.forEach(t => {
      const x0 = x;
      t.preds.forEach(p => { all.P[p.i] = { x, y, b, Z: 2.6, r: Math.min(2.4, pitch * .5), a: 1, rd: 0 }; x += pitch; });
      all.G[t.i] = { x0, x1: Math.max(x0, x - pitch), y, yc: y, n0: x0, b, h: sh - lab, pitch, a: t.preds.length ? 1 : 0 };
      if (t.preds.length) x += 1.4 * pitch;
    });
  });
  for (let s = 0; s < ALL; s++) {  // a round: one row per theory; its name at the left (on a phone above the row)
    const ts = BYROUND[s], n = ts.length, rh = Math.min(g.phone ? 64 : 50, H / n), most = Math.max(...ts.map(t => t.preds.length));
    const room = W - g.nameW - g.fateW, pitch = Math.min(64, room / Math.max(most, 1)), mh = rh - g.top;
    const b = Math.min(9, mh * .2), Z = Math.min(3, mh * .47 / b), x0 = g.nameW + pitch / 2;
    const st = { P: all.P.map(q => ({ ...q, a: 0 })), G: all.G.map(q => ({ ...q, a: 0 })), lab: all.lab };
    ts.forEach((t, i) => {
      const yc = (i + .5) * rh + (H - n * rh) / 2, y = yc + g.top / 2;
      t.preds.forEach((p, j) => { st.P[p.i] = { x: x0 + j * pitch, y, b, Z, r: Math.min(3.8, pitch * .3), a: 1, rd: 1 }; });
      st.G[t.i] = { x0, x1: x0 + Math.max(0, t.preds.length - 1) * pitch, y, yc, n0: 0, b, h: rh, pitch, a: 1 };
    });
    L.push(st);
  }
  L.push(all);
  return L;
}

const LV = [0, .16, .32, .5, .68, .84, 1];  // the opacity levels marks are drawn at
const KINDS = ["band", "rdr", "tick", "ghost", "strike", "halo", "lose", "carr", "win"];
function build() {
  const g = S.g = geo(), svg = $("svg");
  S.L = layouts(g);
  g.cy = g.h / 2;
  const [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const paths = (pre, levels) => levels.map(l => KINDS.map(k => `<path class="k-${k}" id="${pre}${k}${l}" style="opacity:${LV[l]}"/>`).join("")).join("");
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${g.cy}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .04)}" width="${aw}" height="${ah}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .3)}" cy="${f(ay0 + ah * .24)}" rx="${f(aw * .3)}" ry="${f(ah * .2)}" transform="rotate(-14 ${f(ax0 + aw * .3)} ${f(ay0 + ah * .24)})" fill="url(#spec)"/>` +
    g.cap.map((t, k) => `<text class="cap" id="cap${k}" font-size="${g.fs}">${t}</text>`).join("") +
    `<g class="field" id="fg"><g class="base" id="base">${paths("b", [1, 2, 3, 4, 5, 6])}</g>` +
    `<g id="topg">${paths("t", [6])}<path class="selbox" id="sbox"/></g><circle class="burst" id="bu" r="0"/></g>` +
    `<g class="field">` + C.rounds.map((r, k) => `<text class="rl" id="rl${k}" font-size="${g.fc}">Round ${r}</text>`).join("") +
    [...Array(ROWS)].map((_, k) => `<text class="fl" id="fl${k}" font-size="${g.fr}" text-anchor="end"></text>` +
      `<text class="nm" id="nm${k}" font-size="${g.fr}"></text>`).join("") + `</g>` +
    `<g class="read"><text class="set" id="set" font-size="${g.fs}"></text><text class="big" id="big" font-size="${g.fb}"></text>` +
    [0, 1, 2, 3].map(k => `<text class="${k === 2 ? "set" : "lab"}" id="bl${k}" font-size="${k === 3 ? g.fn : g.fl}"></text>`).join("") +
    STATES.map((_, s) => `<text class="blab" id="bn${s}" font-size="${g.fc}">${SNAME(s)}</text><text class="blab" id="bv${s}" font-size="${g.fc}" text-anchor="end"></text>` +
      `<path class="btrack" id="bt${s}"/><path class="bfill" id="bf${s}"/><path class="bhalf" id="bh${s}"/>`).join("") +
    [0, 1].map(k => `<text class="lab" id="nt${k}" font-size="${g.fn}"></text>`).join("") + `</g>` +
    `<g class="key"><path class="k-band" id="kband"/><path class="k-tick" id="ktick" stroke-width="1.3"/><path class="k-win" id="kwin"/><path class="k-lose" id="klose"/>` +
    `<path class="k-rdr" id="kdash"/><path class="k-ghost" id="kghost"/><path class="k-strike" id="kstrike"/>` +
    ["Interval", "Theory nearer", "Readers nearer", "A reader's forecast", "Not computed", "Refuted or lost"].map((t, k) => `<text class="kt" id="kt${k}" font-size="${g.fc}">${t}</text>`).join("") + `</g>`;
  S.el = {}; S.shown = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  S.from = null; S.dirty = true;
}

/* Where each mark and theory is in a change: from S.from to the targets of state S.s, starting at t0, 0.7 ms later per
   mark in reading order, over 0.6 s. */
const ITEMS = ["x", "y", "b", "Z", "r", "a"];
function at(k, kind, now) {
  const to = S.L[S.s][kind][k];
  if (!S.from) return to;
  const from = S.from[kind][k], o = kind === "P" ? PR[k].o : TH[k].preds.length ? TH[k].preds[0].o : 0;
  const p = clamp((now - S.t0 - .7 * o) / 600, 0, 1);
  if (p >= 1) return to;
  const e = ease(p), q = {};
  for (const key in to) q[key] = typeof to[key] === "number" ? mix(from[key], to[key], e) : to[key];
  q.a = Math.max(from.a * (1 - Math.min(1, p * 2.2)), to.a * clamp((p - .25) / .75, 0, 1));
  return q;
}
const circ = (x, y, r) => `M${f(x - r)} ${f(y)}a${f(r)} ${f(r)} 0 1 0 ${f(2 * r)} 0a${f(r)} ${f(r)} 0 1 0 ${f(-2 * r)} 0`;
function selected() { return S.open && TK[S.open] ? TK[S.open] : null; }
function marks(now) {
  const E = S.el, sel = selected(), out = {};
  const put = (top, kind, l, d) => { const id = (top ? "t" : "b") + kind + (top ? 6 : l); out[id] = (out[id] || "") + d; };
  const lev = a => Math.round(clamp(a, 0, 1) * 6);
  let moving = S.from && now - S.t0 < 600 + .7 * N;
  const G = TH.map(t => at(t.i, "G", now));
  TH.forEach((t, i) => {
    const q = G[i], top = sel === t, dim = struck(t) ? .38 : 1, l = top ? 6 : lev(q.a * dim);
    if (!l || !t.preds.length) return;
    const pad = q.pitch * .55;
    put(top, "band", l, `M${f(q.x0 - pad)} ${f(q.y - q.b)}H${f(q.x1 + pad)}V${f(q.y + q.b)}H${f(q.x0 - pad)}Z`);
    if (dim < 1) put(top, "strike", l, `M${f(q.x0 - pad - 2)} ${f(q.y)}H${f(q.x1 + pad + 2)}`);
  });
  PR.forEach(p => {
    const q = at(p.i, "P", now), t = p.t, top = sel === t, dim = struck(t) ? .38 : 1, l = top ? 6 : lev(q.a * dim);
    p.q = q;
    if (!l) return;
    if (p.mark === "x") { put(top, "ghost", l, `M${f(q.x)} ${f(q.y - q.b)}V${f(q.y + q.b)}`); return; }
    put(top, "tick", l, `M${f(q.x)} ${f(q.y - q.b)}V${f(q.y + q.b)}`);
    const lr = top ? 6 : lev(q.a * dim * q.rd);  // the readers' forecasts, on the same scale, in a round's rows
    if (lr && p.mark !== "c") p.rz.forEach(z => { const y = q.y - clamp(z, -q.Z, q.Z) * q.b, w = Math.min(4.5, q.r * 1.4); put(top && q.rd > .5, "rdr", top ? 6 : lr, `M${f(q.x - w)} ${f(y)}H${f(q.x + w)}`); });
    const y = q.y - clamp(p.z, -q.Z, q.Z) * q.b;
    p.dy = y;
    if (p.mark === "w") { put(top, "win", l, circ(q.x, y, q.r)); if (p.u) put(top, "halo", l, circ(q.x, y, q.r + 1.6)); }
    else if (p.mark === "c") put(top, "carr", l, circ(q.x, y, q.r * .85));
    else put(top, "lose", l, circ(q.x, y, q.r * .9));
  });
  for (const id in E) if (/^[bt](band|rdr|tick|ghost|strike|halo|lose|carr|win)\d$/.test(id)) {
    const d = out[id] || "";
    if (S.shown[id] !== d) { E[id].setAttribute("d", d); S.shown[id] = d; }
  }
  const tw = S.s === ALL ? (S.g.phone ? .7 : .9) : 1.8;
  for (const id in E) if (/tick\d$/.test(id)) E[id].setAttribute("stroke-width", tw);
  E.base.classList.toggle("dim", !!sel);
  if (sel) {
    const q = G[sel.i], pad = q.pitch * .55 + 5, x0 = Math.min(q.x0 - pad, q.n0 - 6), x1 = q.x1 + pad + (sel.preds.length ? 0 : 40), y0 = q.yc - q.h * .46, y1 = q.yc + q.h * .46;
    E.sbox.setAttribute("d", `M${f(x0 + 4)} ${f(y0)}H${f(x1 - 4)}Q${f(x1)} ${f(y0)} ${f(x1)} ${f(y0 + 4)}V${f(y1 - 4)}Q${f(x1)} ${f(y1)} ${f(x1 - 4)} ${f(y1)}H${f(x0 + 4)}Q${f(x0)} ${f(y1)} ${f(x0)} ${f(y1 - 4)}V${f(y0 + 4)}Q${f(x0)} ${f(y0)} ${f(x0 + 4)} ${f(y0)}Z`);
  } else E.sbox.setAttribute("d", "");
  S.G = G;
  return moving;
}

/* The replay: about every 2.6 s one real prediction the theory won while both readers expected otherwise (its interval
   holds the measured number, no reader's centre is inside it) is lit again with a ring that opens around its dot. */
function replay(now) {
  const E = S.el;
  if (!S.rp && now > S.rpNext && !selected() && now - S.t0 > 1200) {
    const pool = PR.filter(p => p.u && (S.s === ALL || p.t.round === C.rounds[S.s]));
    if (pool.length) S.rp = { p: pool[(S.rpAt++ * 7) % pool.length], t0: now };
    else S.rpNext = now + 2600;
  }
  if (!S.rp) return;
  const p = S.rp.p, t = clamp((now - S.rp.t0) / 1100, 0, 1), q = p.q;
  if (!q) { S.rp = null; return; }
  E.bu.setAttribute("cx", f(q.x)); E.bu.setAttribute("cy", f(p.dy));
  E.bu.setAttribute("r", f(q.r + 12 * ease(t)));
  E.bu.style.opacity = (1 - t).toFixed(2);
  E.bu.setAttribute("stroke-width", f(1.6 * (1 - t) + .3));
  if (t >= 1) { S.rp = null; S.rpNext = now + 1500; E.bu.setAttribute("r", "0"); }
}
function stopReplay() { S.rp = null; S.rpNext = performance.now() + 2000; if (S.el.bu) S.el.bu.setAttribute("r", "0"); }

/* The counts of a state, from DATA (checked against the round files by running the module). */
const NEAR = s => D.nearer[STATES[s]], RDR = s => D.readers[STATES[s]];
function place(now) {
  const g = S.g, E = S.el, put = (el, q, dy) => { el.setAttribute("x", f(q[0])); el.setAttribute("y", f(q[1] + (dy || 0))); };
  const text = (id, v) => { if (S.shown[id] !== v) E[id].textContent = S.shown[id] = v; };
  E.back.setAttribute("d", rounded(g, g.a, g.r, -g.deep));
  E.plate.setAttribute("d", rounded(g, g.a, g.r, 0));
  g.cap.forEach((_, k) => put(E["cap" + k], proj(g, g.capX, g.capY[k], 8)));
  // The field: one affine map of the projection at its corners.
  const z = 8, A = proj(g, g.fx, g.fy, z), B = proj(g, g.fx + g.W, g.fy, z), Cc = proj(g, g.fx, g.fy + g.H, z);
  const m = S.m = [(B[0] - A[0]) / g.W, (B[1] - A[1]) / g.W, (Cc[0] - A[0]) / g.H, (Cc[1] - A[1]) / g.H, A[0], A[1]];
  E.fg.setAttribute("transform", `matrix(${m.map(v => v.toFixed(4)).join(" ")})`);
  const fp = (u, v) => [m[0] * u + m[2] * v + m[4], m[1] * u + m[3] * v + m[5]];
  if (S.dirty) S.dirty = marks(now);
  if (!still.matches) replay(now);
  // Round names over the strips of All; the fate of each theory at the end of its row in a round.
  S.L[ALL].lab.forEach((q, k) => { put(E["rl" + k], fp(q[0], q[1])); E["rl" + k].style.opacity = S.s === ALL ? 1 : 0; });
  // In a round: each theory's name at the left of its row and its fate at the end; on a phone both above the row.
  const rows = S.s < ALL ? BYROUND[S.s] : [], settled = !S.dirty;
  for (let k = 0; k < ROWS; k++) {
    const el = E["fl" + k], nm = E["nm" + k], t = rows[k];
    if (!t) { el.style.opacity = nm.style.opacity = 0; continue; }
    const q = S.L[S.s].G[t.i], fate = fateLabel(t) + (t.preds.length ? "" : " · no number"), a = settled ? (struck(t) ? .6 : 1) : 0;
    if (g.phone) {  // a row without marks is plain to see here, so its fate stands alone
      text("nm" + k, `${t.name} · ${fateLabel(t)}`);
      put(nm, fp(0, q.yc - q.h / 2 + 16));
      el.style.opacity = 0;
    } else {
      text("nm" + k, t.name);
      text("fl" + k, fate);
      put(nm, fp(0, q.y), 4.4);
      put(el, fp(g.W, q.y), 4.4);
      el.style.opacity = a;
    }
    nm.style.opacity = a;
    nm.classList.toggle("off", struck(t));
  }
  // The count, with the state's setting above it.
  const e = ease(clamp((now - S.t0) / 900, 0, 1)), n = mix(S.n0, S.n1, e), dn = Math.round(mix(S.d0, S.d1, e));
  text("set", S.s === ALL ? C.all : `${SNAME(S.s)} · ${KIND(C.rounds[S.s])}`);
  text("big", fmt(n));
  text("bl0", `of ${dn}: the theory nearer the measured`);
  text("bl1", "number than readers with no theory.");
  text("bl2", `${String(dn / 2)} would be a tie${S.s === ALL ? ": no better" : ""}.`);
  text("bl3", "Readers: two models, same question, no theory.");
  put(E.set, proj(g, g.bigX + 3, g.setY, 10));
  put(E.big, proj(g, g.bigX, g.bigY, 10));
  [0, 1, 2, 3].forEach(k => put(E["bl" + k], proj(g, g.labX, g.labY[k], 10)));
  const line = (x0, y0, x1, y1) => { const p = proj(g, x0, y0, 10), q = proj(g, x1, y1, 10); return `M${f(p[0])} ${f(p[1])}L${f(q[0])} ${f(q[1])}`; };
  STATES.forEach((_, s) => {
    const y = g.barY + s * g.barH + (s === ALL ? 6 : 0), [x0, x1] = g.barX, c = NEAR(s);
    text("bv" + s, `${c[0]} of ${c[1]}`);
    put(E["bn" + s], proj(g, x0, y, 10)); put(E["bv" + s], proj(g, x1, y, 10));
    E["bt" + s].setAttribute("d", line(x0, y + 8, x1, y + 8));
    E["bf" + s].setAttribute("d", line(x0, y + 8, mix(x0, x1, c[0] / c[1]), y + 8));
    E["bh" + s].setAttribute("d", line(mix(x0, x1, .5), y + 4, mix(x0, x1, .5), y + 12));
  });
  const r = RDR(S.s), ins = D.inside[STATES[S.s]];
  if (r[3]) {  // where both readers gave intervals (rounds 3 on)
    text("nt0", "Measured number inside the 90 % interval:");
    text("nt1", `theory ${r[0]} of ${r[3]}, readers ${r[1]} and ${r[2]}.`);
  }
  else { text("nt0", `Inside the theory's interval: ${ins[0]} of ${ins[1]}.`); text("nt1", "Readers gave single numbers here."); }
  [0, 1].forEach(k => put(E["nt" + k], proj(g, g.labX, g.noteY[k], 10)));
  // The key, under the field.
  const ky = g.keyY, xs = g.phone ? [30, 250, 30, 250, 30, 250] : [52, 126, 236, 358, 502, 616];
  const ys = g.phone ? [ky[0], ky[0], ky[1], ky[1], ky[1] + 30, ky[1] + 30] : xs.map(() => ky[0]);
  const kq = (x, y) => proj(g, x, y, 6), P = (x, y) => { const q = kq(x, y); return `${f(q[0])} ${f(q[1])}`; };
  E.kband.setAttribute("d", `M${P(xs[0] - 4, ys[0] - 6)}L${P(xs[0] + 8, ys[0] - 6)}L${P(xs[0] + 8, ys[0] + 6)}L${P(xs[0] - 4, ys[0] + 6)}Z`);
  E.ktick.setAttribute("d", `M${P(xs[0], ys[0] - 6)}L${P(xs[0], ys[0] + 6)}M${P(xs[0] + 4, ys[0] - 6)}L${P(xs[0] + 4, ys[0] + 6)}`);
  const c1 = kq(xs[1], ys[1]), c2 = kq(xs[2], ys[2]);
  E.kwin.setAttribute("d", circ(c1[0], c1[1], 3.3)); E.klose.setAttribute("d", circ(c2[0], c2[1], 3));
  E.kdash.setAttribute("d", `M${P(xs[3] - 4, ys[3])}L${P(xs[3] + 4, ys[3])}`); E.kdash.style.opacity = 1;
  E.kghost.setAttribute("d", `M${P(xs[4], ys[4] - 6)}L${P(xs[4], ys[4] + 6)}`);
  E.kstrike.setAttribute("d", `M${P(xs[5] - 4, ys[5])}L${P(xs[5] + 10, ys[5])}`);
  xs.forEach((_, k) => put(E["kt" + k], kq(xs[k] + (k === 0 ? 15 : k === 5 ? 17 : 10), ys[k]), g.fc * .36));
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
  place(now);
}
function snapshot(now) {  // where everything is now, as the start of the next change
  return { P: PR.map(p => ({ ...at(p.i, "P", now) })), G: TH.map(t => ({ ...at(t.i, "G", now) })) };
}
function setState(s, opts = {}) {
  const now = performance.now(), quick = still.matches || opts.instant;
  const e = ease(clamp((now - S.t0) / 900, 0, 1)), n = mix(S.n0, S.n1, e), dn = mix(S.d0, S.d1, e);
  S.from = quick ? null : snapshot(now);
  S.s = s;
  S.n1 = NEAR(s)[0]; S.n0 = quick ? S.n1 : n;
  S.d1 = NEAR(s)[1]; S.d0 = quick ? S.d1 : dn;
  S.t0 = quick ? -1e9 : now;
  S.dirty = true;
  stopReplay();
  STATES.forEach((_, k) => ["bn", "bv", "bf"].forEach(id => S.el[id + k].classList.toggle("on", k === s)));
  $("switch").querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-pressed", k === s));
  const nr = NEAR(s);
  $("svg").setAttribute("aria-label", `${SNAME(s)}: each mark is one prediction, its interval and the measured number. ` +
    `The theory was nearer the measured number than readers with no theory in ${nr[0]} of ${nr[1]} predictions. ` +
    "Arrow keys change the round; Enter opens a theory.");
  if (still.matches) { aim(0, 0); place(now); }
}

/* The side column: the five panels and two examples, or one theory: its mechanism, fate, predictions and duel. */
const rng = q => q.length === 3 ? `${fv(q[0])} (${fv(q[1])} to ${fv(q[2])})` : fv(q[0]);
function strip(vals, theory, readers, m, grey) {  // one prediction in its own units: theory, readers, measured
  const xs = [theory[1], theory[2], m, ...readers.flatMap(r => r.length === 3 ? [r[1], r[2]] : [r[0]])].filter(v => v != null);
  let lo = Math.min(...xs), hi = Math.max(...xs);
  if (hi === lo) { lo -= 1; hi += 1; }
  const pad = (hi - lo) * .06, X = v => f(6 + 288 * (v - lo + pad) / (hi - lo + 2 * pad));
  let s = `<svg viewBox="0 0 300 30" aria-hidden="true"><path class="m-ax" d="M6 29.5H294"/>`;
  s += `<path class="${grey ? "m-rd" : "m-th"}" d="M${X(theory[1])} 8H${X(theory[2])}"/><path class="${grey ? "m-rd" : "m-th"}" d="M${X(theory[0])} 4V12"/>`;
  readers.forEach((r, k) => {
    const y = 17 + 7 * k;
    if (r.length === 3) s += `<path class="m-rd" d="M${X(r[1])} ${y}H${X(r[2])}"/>`;
    s += `<circle class="m-c" cx="${X(r[0])}" cy="${y}" r="2"/>`;
  });
  if (m != null) s += `<path class="m-me" d="M${X(m)} 1V29"/>`;
  return s + "</svg>";
}
function predItem(p) {
  const carried = p.note.startsWith("c:"), alt = carried ? JSON.parse(p.note.slice(2)) : null;
  const unit = p.unit ? ` <span>(${esc(p.unit)})</span>` : "";
  let res;
  if (p.m == null) res = `Not computed: ${esc(p.note.slice(2))}`;
  else {
    const where = p.inside ? "inside" : p.note === "n" ? "outside, within noise" : "outside";
    const who = { w: "nearer than the readers", t: "as near as the readers", l: "the readers nearer", c: "" }[p.mark];
    res = `Measured <b>${fv(p.m)}</b>${unit}: ${where} the interval${who ? ", " + who : ""}.`;
  }
  const rd = carried ? `Carried from round 5: a duel test it won as the rival. The theory it replaced predicted ${rng(alt)}.`
    : p.rd.length ? `Readers with no theory: ${p.rd.map(rng).join("; ")}.` : "";
  return `<li class="${p.mark === "w" ? "w" : ""}"><div class="pw">${esc(p.what)}</div>` +
    (p.m != null ? strip(null, [p.v, p.lo, p.hi], carried ? [alt] : p.rd, p.m) : "") +
    `<div class="pv">Forecast <b>${fv(p.v)}</b> (${fv(p.lo)} to ${fv(p.hi)}). ${res}</div>` + (rd ? `<div class="pr">${rd}</div>` : "") + `</li>`;
}
function theoryPane(t) {
  const done = t.preds.filter(p => p.m != null), ins = done.filter(p => p.inside).length, cmp = done.filter(p => "wtl".includes(p.mark));
  const wins = cmp.filter(p => p.mark === "w").length;
  const fateTxt = struck(t) ? `<s>${esc(t.state)}</s>` : esc(noWin(t) ? "survives, no duel win" : t.state);
  let h = `<div class="dhead"><h2>${esc(t.name)}</h2><button class="close" data-open="">Close</button></div>`;
  if (C.cases[t.key]) h += `<p class="case">${esc(C.cases[t.key])}</p>`;
  h += `<p class="lead st">${esc(t.st)}</p>`;
  h += `<p class="tag">Round ${t.round} · ${esc(t.id)} · <b>${fateTxt}</b> · ${done.length ? `${ins} of ${done.length} inside` : "no prediction measured"}` +
    (cmp.length ? `, nearer than the readers in ${wins} of ${cmp.length}` : "") + `</p>`;
  if (t.why) h += `<p class="why">${esc(minus(t.why))}</p>`;
  if (t.review && t.review !== t.why) h += `<p class="why">Review: ${esc(t.review)}</p>`;
  if (t.gpu) {
    const g = t.gpu, mine = t.id === g[6] ? g[5] : g[4], other = t.id === g[6] ? g[4] : g[5], inside = mine[1] <= g[1] && g[1] <= mine[2];
    h += `<h3>A GPU experiment, predicted before it ran</h3><div class="duel"><p>Board item ${esc(g[0])}. This theory: <b>${rng(mine)}</b> of ${g[2]} right; ` +
      `${t.id === g[6] ? "the theory it replaced" : "its rival"}: ${rng(other)}. Measured: <b>${g[1]}</b>, ${inside ? "inside" : "outside"} this theory's interval.</p></div>` +
      `<ul class="preds"><li class="${inside ? "w" : ""}">${strip(null, mine, [other], g[1])}<div class="pr">Black: this theory. Grey: the other. Blue: measured.</div></li></ul>`;
  }
  h += `<h3>Predictions (${t.preds.length})</h3>`;
  h += t.preds.length ? `<ul class="preds">${t.preds.map(predItem).join("")}</ul>`
    : `<p class="why">None of its interval predictions was measured in this round.</p>`;
  if (t.duel) {
    const d = t.duel, sign = d[1] >= 0 ? "+" : "−";
    h += `<h3>Against a rival theory</h3><div class="duel"><p>Rival: ${esc(d[0])}</p>` +
      `<p>On ${d[4]} tests where the two differ, the theory scored <b>${sign}${Math.abs(d[1]).toFixed(2)} nats</b> against the rival ` +
      `(${d[3]} of them separate${d[3] === 1 ? "s" : ""} the two): <b>${esc(d[2])}</b>.</p></div><ul class="preds">` +
      d[5].map(r => `<li class="${r[4] > 0 ? "w" : ""}"><div class="pw">${esc(r[0])}</div>${strip(null, r[2], [r[3]], r[1])}` +
        `<div class="pv">Measured <b>${fv(r[1])}</b>. Theory ${rng(r[2])}; rival ${rng(r[3])}. Gain ${minus(r[4].toFixed(2))} nats.</div></li>`).join("") + `</ul>`;
  }
  return h + `<div class="steps"><button data-step="-1">‹ Previous theory</button><button data-step="1">Next theory ›</button></div>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open), t = selected();
  $("pane").innerHTML = t ? `<div>${theoryPane(t)}</div>` : p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>` +
      `<ul class="more ex">${C.examples.map(x => `<li><button data-open="${x[0]}" data-round="1">${esc(x[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
  S.dirty = true;
}
/* The round and what is open are one value in the address: #<round>, then /<panel> or /<round>.<theory>. */
function address(push) {
  const parts = [S.s < ALL ? STATES[S.s] : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
const visible = (t, s) => s === ALL ? t.preds.length > 0 : t.round === C.rounds[s];
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const s = STATES.indexOf(parts[0]) >= 0 && parts[0] !== "all" ? STATES.indexOf(parts[0]) : ALL;
  const rest = parts.find(x => C.panels.some(p => p[0] === x) || TK[x]);
  S.open = rest && (!TK[rest] || visible(TK[rest], s) || s === ALL) ? rest : null;
  if (first === true || s !== S.s) setState(s, { instant: first === true });
  pane();
  if (still.matches) place(performance.now());
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "start" }); };
function open(key, toRound) {
  const was = S.open;
  if (key && TK[key] && toRound && C.rounds[S.s] !== TK[key].round) setState(C.rounds.indexOf(TK[key].round));
  S.open = key || null;
  if (key && TK[key]) stopReplay();
  address(true);
  pane();
  if (still.matches) place(performance.now());
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  else if (!key) $("svg").focus({ preventScroll: true });
}
function choose(s) {
  if (s === S.s) return;
  setState(s);
  const t = selected();
  if (t && !visible(t, s)) { S.open = null; pane(); }
  address(false);
}

/* The picture's control: click a theory's marks to open it. The point is mapped into field units. */
const svg = $("svg");
function nearest(e) {
  const m = S.el.fg.getScreenCTM().inverse(), u = m.a * e.clientX + m.c * e.clientY + m.e, v = m.b * e.clientX + m.d * e.clientY + m.f;
  let best = null, bd = Infinity;
  TH.forEach(t => {
    const q = S.L[S.s].G[t.i];
    if (!q.a) return;
    const x1 = q.x1 + (S.s < ALL && !t.preds.length ? 60 : 0), pad = q.pitch * .6 + 3, x0 = Math.min(q.x0 - pad, q.n0);
    const du = u < x0 ? x0 - u : u > x1 + pad ? u - x1 - pad : 0, dv = Math.max(0, Math.abs(v - q.yc) - q.h * .46);
    const d = du * du + dv * dv * 4;
    if (d < bd && du < 10 && dv < 6) { bd = d; best = t; }
  });
  return best;
}
svg.addEventListener("pointermove", e => { if (e.pointerType === "mouse") svg.style.cursor = nearest(e) ? "pointer" : "default"; });
svg.addEventListener("click", e => { const t = nearest(e); if (t) { open(t.key); show(); } });
const LIST = () => (S.s === ALL ? BYROUND.flat().filter(t => t.preds.length) : BYROUND[S.s]);
document.addEventListener("click", e => {
  const b = e.target.closest("[data-state]"), o = e.target.closest("[data-open]"), st = e.target.closest("[data-step]");
  if (b) choose(Number(b.dataset.state));
  if (o) open(o.dataset.open, !!o.dataset.round);
  if (st) {
    const L = LIST(), k = L.indexOf(selected()), next = L[(k + Number(st.dataset.step) + L.length) % L.length];
    open(next.key);
    $("pane").querySelector(`[data-step="${st.dataset.step}"]`).focus({ preventScroll: true });
  }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) open("");
  if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
    choose(clamp(S.s + (e.key === "ArrowRight" ? 1 : -1), 0, STATES.length - 1));
  }
  if (e.key === "Enter" && document.activeElement === svg) {  // the first example
    e.preventDefault();
    open(C.examples[0][0], true);
    show();
  }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); setState(S.s, { instant: true }); place(performance.now()); });
still.addEventListener("change", () => { if (still.matches) { stopReplay(); setState(S.s, { instant: true }); aim(0, 0); place(performance.now()); } });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1; V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("switch").innerHTML = STATES.map((r, k) => `<button data-state="${k}" aria-label="${k === ALL ? "All rounds" : "Round " + r}">${k === ALL ? "All" : r}</button>`).join("");
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
build();
aim(0, 0);
fromHash(true);
place(performance.now());
S.rpNext = performance.now() + 2600;
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
"""

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with a band of seven interval lines; four dots land inside the band, one of them lit, three
# outside it, and they drift a little.
ICON = r"""(kit, t, tilt) => {
  const th = 5, top = th / 2, k = Number(t) || 0;
  let out = kit.slab(44, 38, th);
  const zs = [.2, -1.9, .5, 2.3, -.4, 1.7, .1];
  for (let j = 0; j < 7; j++) {
    const u = -27 + 9 * j;
    out += kit.line(kit.at(u, -7, top), kit.at(u, 7, top), 1.5, "plain", .6);
    const v = 7 * zs[j] + .8 * Math.sin(k * .9 + j), d = kit.at(u, v, top), lit = j === 4;
    out += lit ? `<circle cx="${d[0].toFixed(1)}" cy="${d[1].toFixed(1)}" r="3.4" fill="${kit.token.blue}"/>`
      : `<circle cx="${d[0].toFixed(1)}" cy="${d[1].toFixed(1)}" r="2.8" fill="${Math.abs(zs[j]) <= 1 ? kit.token.ink : "none"}" stroke="${kit.token.ink}" stroke-width="1.1"/>`;
  }
  return out;
}"""

PAGE = PAGE.replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "examples": EXAMPLES, "cases": CASES,
    "theories": THEORIES, "preds": PREDS, "rounds": ROUNDS, "names": _NAME, "all": f"All {_word(R)} rounds",
    "data": {k: DATA[k] for k in ("nearer", "inside", "readers", "computed")}}, ensure_ascii=False).replace("</", "<\\/"))

if __name__ == "__main__":  # run from the repository root
    theories, preds = _build()
    counts = _count(theories, preds)
    if sys.argv[1:] == ["--write"]:
        src = open(__file__).read()
        lines = lambda rows: "[\n" + "".join("    " + repr(r) + ",\n" for r in rows) + "]"
        for name, body in (("COUNTS", repr(counts)), ("THEORIES", lines(theories)), ("PREDS", lines(preds))):
            start = src.index("\n" + name + " = ") + 1
            src = src[:start] + name + " = " + body + src[src.index("\n\n", start):]
        open(__file__, "w").write(src)
        sys.exit(f"wrote {len(theories)} theories and {len(preds)} predictions")
    assert THEORIES == theories and PREDS == preds, "THEORIES or PREDS differ from the round files: run with --write"
    assert COUNTS == counts, "COUNTS differ from the round files: run with --write"
    # Against the engine's own tables: computed, inside and filed per round from 4, and round 3's total gain.
    for rd in [r for r in map(int, counts["theories"]["per_round"]) if r >= 4]:
        v4 = json.load(open(f"{E}round-{rd:02d}/metrics_v4.json"))["theories"]
        comp = sum(v["computed"] for v in v4.values())
        assert counts["computed"][str(rd)][0] == comp, (rd, comp)
        assert counts["inside"][str(rd)][0] == sum(v["inside"] for v in v4.values()), rd
        assert counts["computed"][str(rd)][1] == sum(v["offline"] for v in v4.values()), rd
    v3 = json.load(open(E + "round-03/metrics_v3.json"))["theories"]
    assert abs(counts["gain"]["3"] - round(sum(v["total_gain"] for v in v3.values()), 2)) < .02
    missing = sorted({_norm(t) for t in THEORIES} - set(NAMES))
    if missing:
        print("no name in NAMES (the first words of the statement are shown):", ", ".join(missing))
    print("THEORIES, PREDS and COUNTS match the round files;", f"nearer {counts['nearer']['all']}, readers {counts['readers']['all']}")
