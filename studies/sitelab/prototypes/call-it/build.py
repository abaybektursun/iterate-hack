"""Build data.json for the call-it prototype: 10 experiments of the theory engine's forecast runs that have a measured
value, each with its stored description, every stored forecast (value, 90 % interval, reason) and the gain the engine
stored for it. The gain rule is copied from studies/theory/lib/round.py (log_density, clip3, capped, gain_rows) and every
gain is recomputed here: the build fails when one differs from the stored gain.

    python3 studies/sitelab/prototypes/call-it/build.py
"""
import json, math, pathlib, re, statistics

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
F = ROOT / "studies/theory/results/forecast"

# (run, target, scale low, scale high, detent step, lead sentence written for this page, reference numbers).
# Each reference is (label, numbers): every number must occur in the target's stored description or in a stored reason of
# a forecaster of this target, which is the proof that the forecasters had it. The last list holds the reference numbers
# printed on the scale, under the same check.
ROUNDS = [
    ("run-02", "t01", 0, 500, 1, "An early checkpoint of the RL run, 100 steps in, is tested on the standard set with no opening cue.",
     [("An unfinished run of the same test had 405 right of the first 478", ["405", "478"]),
      ("22 long problems were still missing; the cued base got 13 of those", ["22", "13"])], []),
    ("run-05", "t10", 0, 500, 0.25, "A later checkpoint of the RL run, 400 steps in, is sampled four times and the four scores are averaged.",
     [("The one sample already posted scored 436", ["436"])], [(436, "one sample")]),
    ("run-05", "t04", 0, 538, 1, "A control: the untrained base gets a random weight edit of the same size as the real one, then writes code.",
     [("The base with the Code cue and no edit passes 317", ["317"]),
      ("On math, random edits scored 158 to 167 against the base's 164", ["158", "167", "164"])], [(317, "base")]),
    ("run-02", "t11", 0, 328, 1, "The untrained base gets eight directions of the RL weight change at 1.5 times their size, and four samples vote.",
     [("Under the same vote the cued base gets 192 and the RL model 221", ["192", "221"]),
      ("One sample of the edited base averages about 197", ["197"])], [(192, "base vote"), (221, "RL vote"), (197, "one sample")]),
    ("run-02", "t05", 0, 328, 1, "The untrained base is allowed answers twice as long: the token cap goes from 16,384 to 32,768.",
     [("At the old cap it scored 164 (155 to 168 over reruns)", ["164", "155", "168"]),
      ("77 of its answers hit the old cap", ["77"]),
      ("The longer cap gave Think-SFT 23 more and the RL model 2 more", ["23"])], [(164, "old cap")]),
    ("run-05", "t05", 0, 538, 1, "Eight directions learned by RL on math are added to the untrained base, and it is tested on code.",
     [("The base with the Code cue and no edit passes 317", ["317"]),
      ("The Math cue alone lifts it to 326 on this set", ["326"])], [(317, "base"), (326, "Math cue")]),
    ("run-05", "t02", 0, 538, 1, "Eight directions learned by RL on code are added to the untrained base at 1.5 times their size.",
     [("The base with the Code cue passes 317, the RL-Code model 401", ["317", "401"]),
      ("On math the same edit matched RL: 456 against 457", ["456", "457"])], [(317, "base"), (401, "RL-Code")]),
    ("run-02", "t12", 0, 500, 1, "The same eight math directions at 1.5 times their size, one sample, on the standard set.",
     [("The cued base scores 410, the RL model 457", ["410", "457"]),
      ("The eight directions at 1 times, plain prompt, scored 427", ["427"])], [(410, "cued base"), (457, "RL"), (427, "1x plain")]),
    ("run-02", "t14", 0, 400, 1, "An agent ran 40 experiments on 100 practice problems to tune the untrained base; its final recipe is run on 400 held-out problems.",
     [("A vote over 4 cued samples reaches 89.2 % on the full set", ["89.2"]),
      ("The 100 practice problems run about 2 points easy", ["2 points easy"])], []),
    ("run-02", "t15", 0, 328, 1, "The same agent-tuned recipe, never tuned on them, is run on the 328 harder problems.",
     [("The cued base with a vote over 4 gets 192 of these", ["192"]),
      ("One of its four samples is right on 207", ["207"])], [(192, "base vote"), (207, "any of 4")]),
]


# A short name written for this page for each theory; its stored statement is shown beside it.
TAGS = {"run-02/f2-m01": "Short samples", "run-02/f2-m02": "Scattered slips", "run-02/f2-m03": "Stopping dose", "run-02/f2-m04": "Capped abstains",
        "run-02/f2-m05": "Asserted guesses", "run-02/f2-m06": "Stop controller", "run-02/r5-m03-rival": "Incomplete switch",
        "run-05/f2-m01": "Termination dial", "run-05/f2-m02": "Error reducer", "run-05/f2-m03": "Input subspace",
        "run-05/f2-m04": "Staged change", "run-05/f2-m06": "bf16 rounding"}
RIVAL = ROOT / "studies/theory/results/engine/round-08/theories/r5-m03-rival.json"


def log_density(x, c):
    """round.py: log density at x of the normal a claim stands for: mean value, sd = width of its 90 % interval / 3.29."""
    sd = max((c["high"] - c["low"]) / 3.29, 0.01 * max(abs(c["value"]), 1))
    return -0.5 * ((x - c["value"]) / sd) ** 2 - math.log(sd) - 0.5 * math.log(2 * math.pi)


def gain(x, c, nulls):
    """round.py gain_rows: log density minus the log of the equal mixture of the two readers, clipped to [-3, 3] nats,
    at most 0 when x is outside the claim's own interval (version 9)."""
    a, b = (log_density(x, p) for p in nulls)
    g = min(3.0, max(-3.0, log_density(x, c) - (max(a, b) + math.log(0.5 * (1 + math.exp(-abs(a - b)))))))
    return g if c["low"] <= x <= c["high"] else min(g, 0.0)


def newest_scores(run):
    return max((json.loads(p.read_text()) for p in (F / run).glob("scores*.json")), key=lambda s: s["scored_utc"])


def short(statement):
    """The first sentence of a mechanism's statement."""
    s = re.split(r"(?<=[a-z0-9\)])[.:;] ", statement.strip(), maxsplit=1)[0].rstrip(".")
    return s if len(s) <= 230 else s[:227].rsplit(" ", 1)[0] + " ..."


runs, rounds, checked = {}, [], 0
for run, tid, lo, hi, step, lead, refs, marks in ROUNDS:
    if run not in runs:
        runs[run] = {"targets": {t["id"]: t for t in json.loads((F / run / "targets.json").read_text())["targets"]},
                     "forecasts": json.loads((F / run / "forecasts.json").read_text()), "scores": newest_scores(run),
                     "mechanisms": {m["id"]: m for m in json.loads((F / run / "mechanisms.json").read_text())["mechanisms"]}
                                   | {"r5-m03-rival": json.loads(RIVAL.read_text())}}
    r = runs[run]
    t, m = r["targets"][tid], next(x for x in r["scores"]["measured"] if x["id"] == tid)
    x = m["value"]
    assert x is not None and m["item"].startswith("result-"), (run, tid)
    assert lo < x < hi and abs(x / step - round(x / step)) < 1e-9, (run, tid, x)
    assert not re.search(rf"(?<![\d.]){re.escape(f'{x:g}')}(?![\d.])", t["what"]), f"{run} {tid}: the description holds the answer"
    fs = {n: next((f for f in v if f["id"] == tid), None) for n, v in r["forecasts"].items()}
    fs = {n: f for n, f in fs.items() if f and f["value"] is not None}  # a theory may abstain on a target
    nulls = [fs["reader-1"], fs["reader-2"]]
    text = t["what"] + " " + " ".join(f["reason"] for f in fs.values())
    for label, numbers in refs:
        for n in numbers:
            assert n in text, f"{run} {tid}: reference number {n} is in no stored reason"
            assert n.isdigit() is False or float(n) != x, f"{run} {tid}: a reference gives the answer"
    for v, tag in marks:
        assert str(v) in text and v != x and lo < v < hi, f"{run} {tid}: mark {v} is in no stored reason"
    out = []
    for n, f in fs.items():
        assert lo <= f["low"] <= f["value"] <= f["high"] <= hi, (run, tid, n)
        row = next(q for q in r["scores"]["forecasters"][n]["rows"] if q["id"] == tid)
        g = round(gain(x, f, nulls), 4)
        assert abs(g - row["gain"]) < 5e-4, f"{run} {tid} {n}: gain {g} differs from the stored {row['gain']}"
        assert row["inside"] == (f["low"] <= x <= f["high"])
        checked += 1
        reader = n.startswith("reader")
        out.append({"who": n if reader else f"{run}/{n}", "name": ("Reader " + n[-1]) if reader else TAGS[f"{run}/{n}"], "id": n,
                    "reader": reader, "value": f["value"], "low": f["low"], "high": f["high"], "gain": row["gain"], "inside": row["inside"],
                    "reason": f["reason"], "theory": None if reader else short(r["mechanisms"][n]["statement"])})
    theories = [f for f in out if not f["reader"]]
    assert len(theories) >= 2, (run, tid)
    n_set = int(re.search(r"of (\d+)", t["unit"]).group(1))
    rounds.append({"run": run, "target": tid, "item": m["item"], "lead": lead, "what": t["what"], "unit": t["unit"], "n": n_set,
                   "lo": lo, "hi": hi, "step": step, "refs": [label for label, _ in refs], "marks": [list(m) for m in marks], "measured": x, "quote": m["quote"],
                   "forecasts": out, "inside": sum(f["inside"] for f in out),
                   "miss": statistics.median(abs(f["value"] - x) for f in out) / n_set})

# Hardest last: fewer forecasters with the measured number inside their interval, then a larger median miss.
rounds.sort(key=lambda r: (-r["inside"] / len(r["forecasts"]), r["miss"]))
for r in rounds:
    r["miss"] = round(r["miss"], 4)

readers = [f for r in rounds for f in r["forecasts"] if f["reader"]]
theories = [f for r in rounds for f in r["forecasts"] if not f["reader"]]
assert len(rounds) == 10 and len(readers) == 20
data = {"rule": "studies/theory/lib/round.py gain_rows (version 9)", "rounds": rounds,
        "summary": {"readers": len(readers), "readers_inside": sum(f["inside"] for f in readers),
                    "theories": len(theories), "theories_inside": sum(f["inside"] for f in theories),
                    "theory_names": len({f["who"] for f in theories})}}
text = json.dumps(data, indent=1)
assert len(text) < 1_000_000 and "/home/" not in text and not re.search(r"@[\w-]+\.\w", text)
(HERE / "data.json").write_text(text)
s = data["summary"]
print(f"data.json: {len(rounds)} rounds, {checked} forecasts with the stored gain reproduced, {len(text)} bytes")
print(f"readers inside {s['readers_inside']}/{s['readers']}, theories inside {s['theories_inside']}/{s['theories']} ({s['theory_names']} theories)")
for r in rounds:
    print(f"  {r['run']} {r['target']} measured {r['measured']:g} of {r['n']}  inside {r['inside']}/{len(r['forecasts'])}  miss {r['miss']}")
