"""r7-m08 prediction 1: share of summed Code 3.1 D on the third of items where Math 3.1's D is most negative."""
import json
import math
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

REL = "studies/rlneurons/results/wrongstep/math500-01/items.json"


def load(rel):
    if os.path.exists(rel):
        return json.load(open(rel))
    local = os.path.join("runs/theory-tests", rel)
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        out = subprocess.run(["git", "show", "HEAD:" + rel], capture_output=True)
        if out.returncode != 0:
            return None
        open(local, "wb").write(out.stdout)
    return json.load(open(local))


def num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


items = load(REL)
if not isinstance(items, list):
    not_computable(f"{REL} is not readable as a list of items")
    raise SystemExit

kept = []
for it in items:
    models = it.get("models") or {}
    vals = {}
    ok = True
    for m in ("base", "code31", "math31"):
        mm = models.get(m) or {}
        for f in ("lp_span", "lp_control"):
            v = mm.get(f)
            if not num(v):
                ok = False
            vals[(m, f)] = v
    if not ok:
        continue
    db = vals[("base", "lp_span")] - vals[("base", "lp_control")]
    d_code = (vals[("code31", "lp_span")] - vals[("code31", "lp_control")]) - db
    d_math = (vals[("math31", "lp_span")] - vals[("math31", "lp_control")]) - db
    kept.append({"problem_index": it.get("problem_index"), "sample": it.get("sample"), "label": it.get("label"),
                 "D_code31": d_code, "D_math31": d_math, "row": it})

if not kept:
    not_computable("no item has all six lp_span / lp_control numbers")
    raise SystemExit


def order(rows):
    return sorted(rows, key=lambda r: (r["D_math31"], r["problem_index"], r["sample"]))


def C(rows):
    """Main reading; None if undefined (denominator >= 0)."""
    den = sum(r["D_code31"] for r in rows)
    if den >= 0:
        return None
    t = order(rows)[: len(rows) // 3]
    return sum(r["D_code31"] for r in t) / den


def C_neg(rows):
    """Other reading: share of Code 3.1's lowering (negative D only) on T."""
    den = sum(min(r["D_code31"], 0.0) for r in rows)
    if den >= 0:
        return None
    t = order(rows)[: len(rows) // 3]
    return sum(min(r["D_code31"], 0.0) for r in t) / den


def stat(rows):
    v = C(rows)
    return -math.inf if v is None else v  # undefined counts as refuted (C low side)


n = len(kept)
nT = n // 3
print(json.dumps({"groups": {"T (lowest third by D_math31)": nT, "all kept items": n}}))
c = C(kept)
if c is None:
    refuted_without_number()
    raise SystemExit
interval = bootstrap(stat, kept)
ex = dict(order(kept)[0]["row"])
ex = {k: ex[k] for k in ("problem_index", "sample", "label", "span_tokens", "position", "models") if k in ex}
ex["models"] = {m: ex["models"][m] for m in ("base", "code31", "math31")}
report(c, nT, interval, "bootstrap", refuted_by_met=(c < 0.45), alt_measured=C_neg(kept), example_row=ex)
