"""r7-m08 prediction 2: mean D_code31 over items whose label contains 'plan'."""
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
    b, c = models.get("base") or {}, models.get("code31") or {}
    four = [b.get("lp_span"), b.get("lp_control"), c.get("lp_span"), c.get("lp_control")]
    if not all(num(v) for v in four):
        continue
    label = it.get("label")
    if not (isinstance(label, str) and "plan" in label.lower()):
        continue
    d = (c["lp_span"] - c["lp_control"]) - (b["lp_span"] - b["lp_control"])
    # other reading: the head-5-token D (lp_head - lp_head_control), if present
    hb, hc = b.get("lp_head"), c.get("lp_head")
    hbc, hcc = b.get("lp_head_control"), c.get("lp_head_control")
    dh = (hc - hcc) - (hb - hbc) if all(num(v) for v in (hb, hc, hbc, hcc)) else None
    kept.append({"D": d, "D_head": dh, "row": it})

if not kept:
    refuted_without_number()
    raise SystemExit


def stat(rows):
    return sum(r["D"] for r in rows) / len(rows)


m = stat(kept)
heads = [r["D_head"] for r in kept if r["D_head"] is not None]
alt = sum(heads) / len(heads) if heads else None
ex = {k: kept[0]["row"][k] for k in ("problem_index", "sample", "label", "span_tokens", "position") if k in kept[0]["row"]}
ex["models"] = {mm: kept[0]["row"]["models"][mm] for mm in ("base", "code31")}
report(m, len(kept), bootstrap(stat, kept), "bootstrap", refuted_by_met=(m < -0.35 or m > 0.35), alt_measured=alt,
       example_row=ex)
