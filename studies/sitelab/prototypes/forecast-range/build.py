"""data.json for the forecast range, from the theory engine's files only.

  python3 studies/sitelab/prototypes/forecast-range/build.py      (from anywhere in the repository)

Sources: studies/theory/results/engine/round-<nn>/ through tools/finding_theories_on_trial.py's _build and _count
(the same reader the page /finding/theories-on-trial is checked with), studies/theory/README.md (round headers) and
studies/theory/results/forecast/run-<nn>/ (targets.json, forecasts.json, scores.json, mechanisms.json, run.json).
No number is typed here.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../../.."))
os.chdir(ROOT)
sys.path.insert(0, "tools")
import finding_theories_on_trial as F  # noqa: E402

T, P = F._build()
C = F._count(T, P)
norm = lambda t: ("r1-" + t[2]) if t[1] == 1 else t[2]
name = lambda nid, st: F.NAMES.get(nid) or nid
heads = {int(m.group(1)): m.group(2) for line in open("studies/theory/README.md")
         if (m := re.match(r"## Round (\d\d) \((.*)\)", line))}

stages = []
for rd in sorted({t[1] for t in T}):
    ths, shots = [], []
    for t in [t for t in T if t[1] == rd]:
        i = len(ths)
        ths.append({"id": norm(t), "name": name(norm(t), t[3]), "statement": t[3], "state": t[4], "fate": t[5],
                    "why": t[6], "review": t[7], "duel": t[8], "kind": "theory"})
        for p in [p for p in P if p[0] == t[0]]:
            shots.append({"th": i, "id": p[1], "what": p[2], "unit": p[3], "v": p[4], "lo": p[5], "hi": p[6], "m": p[7],
                          "mark": p[8], "readers": p[9], "gain": p[10], "note": p[11]})
        if t[9]:  # the GPU experiment both sides of a duel forecast (round 5 the theory, round 6 its rival)
            g = t[9]
            mine, other = (g[4], g[5]) if rd == 5 else (g[5], g[4])
            shots.append({"th": i, "id": "GPU", "what": f"GPU experiment, measured by {g[0]}: right of {g[2]}, 95 % interval "
                          f"of the measurement {g[3]}. Artifact {g[7]}", "unit": f"right of {g[2]}", "v": mine[0],
                          "lo": mine[1], "hi": mine[2], "m": g[1], "mark": "g", "readers": [], "gain": None,
                          "note": "o:" + json.dumps(other), "item": g[0]})
    stages.append({"key": str(rd), "label": f"Round {rd}", "sub": heads.get(rd, ""), "kind": "round",
                   "src": f"{F.E}round-{rd:02d}/", "theories": ths, "shots": shots})

statement = {norm(t): t[3] for t in T}
for run in sorted(os.listdir("studies/theory/results/forecast")):
    d = f"studies/theory/results/forecast/{run}/"
    ld = lambda f: json.load(open(d + f))
    tg = {x["id"]: x for x in ld("targets.json")["targets"]}
    fc, sc, rn = ld("forecasts.json"), ld("scores.json"), ld("run.json")
    meas = {m["id"]: m for m in sc["measured"]}
    mech = {m["id"]: m["statement"] for m in ld("mechanisms.json")["mechanisms"]} if os.path.exists(d + "mechanisms.json") else {}
    ths, shots = [], []
    for who, rows in fc.items():
        reader = who.startswith("reader")
        s = sc["forecasters"].get(who, {})
        st = ("A reader with no theory: a model run given the same board items and the same question."
              if reader else statement.get(who) or mech.get(who, ""))
        i = len(ths)
        ths.append({"id": who, "name": ("Reader " + who[-1]) if reader else name(who, st), "statement": st,
                    "state": "", "fate": "", "review": "", "duel": None, "kind": "reader" if reader else "theory",
                    "why": (f"{s['scored']} of its forecasts measured so far, {s['inside']} inside its interval, "
                            f"{s['total_gain']:+.2f} nats against the two readers.") if s.get("scored") else
                           "None of its forecasts has been measured yet."})
        gains = {r["id"]: r for r in s.get("rows", [])}
        for x in rows:
            if x["value"] is None:  # "theory says nothing"
                continue
            m, g = meas[x["id"]], gains.get(x["id"])
            rd = [[r[k] for k in ("value", "low", "high")] for r in g["nulls"]] if g else \
                 [[r["value"], r["low"], r["high"]] for w in ("reader-1", "reader-2") for r in fc[w] if r["id"] == x["id"]]
            mark = "x" if m["value"] is None else "c"
            if m["value"] is not None and not reader:
                a, b = abs(x["value"] - m["value"]), abs(sum(r[0] for r in rd) / len(rd) - m["value"])
                mark = "w" if a < b else "t" if a == b else "l"
            shots.append({"th": i, "id": x["id"], "what": tg[x["id"]]["what"], "unit": tg[x["id"]]["unit"], "v": x["value"],
                          "lo": x["low"], "hi": x["high"], "m": m["value"], "mark": mark, "readers": [] if reader else rd,
                          "gain": g["gain"] if g else None, "note": "", "reason": x["reason"],
                          "item": m["item"] or tg[x["id"]]["item"], "quote": m["quote"]})
    stages.append({"key": "F" + run[-1], "label": f"Forecast run {int(run[-2:])}", "kind": "forecast", "src": d,
                   "sub": f"board snapshot {rn['utc'].replace('T', ' ')} UTC, scored {sc['scored_utc'].replace('T', ' ')} UTC",
                   "theories": ths, "shots": shots})

for s in stages:  # a forecast with a zero-width interval has no scale of its own
    s["shots"] = [x for x in s["shots"] if x["hi"] > x["lo"]]
out = {"line": F.LINE if (T, P) == (F.THEORIES, F.PREDS) else None, "counts": C, "stages": stages}
if out["line"] is None:
    n = C["nearer"]["all"]
    out["line"] = (f"Our theories were nearer the measured number than readers with no theory in {n[0]} of {n[1]} "
                   "predictions: no better.")
json.dump(out, open(os.path.join(HERE, "data.json"), "w"), ensure_ascii=False, separators=(",", ":"))
print(os.path.getsize(os.path.join(HERE, "data.json")), "bytes;",
      [(s["key"], len(s["theories"]), len(s["shots"]), sum(x["m"] is None for x in s["shots"])) for s in stages])
