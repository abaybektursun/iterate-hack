"""r5-m05 prediction 3: hard-328 hold-on density, wrong/right, base (cue, e72c) relative to RL (plain, 86ef).

Main: R = mean over rows of per-row density (wrong) / mean over rows of per-row density (right).
alt_measured: pooled density per group (total matches / (total chars / 1000)), then the same ratios.
"""
import json
import os
import re
import subprocess

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01"
JOBS = {"base": "abaybektursun-1114-151534-e72c", "rl": "abaybektursun-1114-151540-86ef"}
HOLD = re.compile(r"(?<![A-Za-z])(Wait|Hmm)(?![A-Za-z])")


def emit(d):
    print(json.dumps(d))
    raise SystemExit(0)


def fail(reason):
    emit({"measured": None, "refuted_by_met": False, "alt_measured": None,
          "not_computable": reason, "example_row": None})


def fetch(job):
    local = f"runs/theory-tests/{job}/answers.jsonl"
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{job}/answers.jsonl", local, "--profile",
                            "iterate-ecr", "--only-show-errors"], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(local):
            fail(f"could not fetch {job}: {r.stderr.strip()[:300]}")
    with open(local) as f:
        return [json.loads(l) for l in f if l.strip()]


def model_R(rows):
    dens = {"right": [], "wrong": []}
    pooled = {"right": [0, 0], "wrong": [0, 0]}  # matches, chars
    example = None
    for r in rows:
        if r is None or "cap_hit" not in r:
            continue
        if "score_v3" not in r:
            fail("row without score_v3")
        if r["cap_hit"] is not False:
            continue
        text = r.get("text") or ""
        n = len(HOLD.findall(text))
        d = 0.0 if len(text) == 0 else n / (len(text) / 1000.0)
        g = "right" if r["score_v3"] == 1 else "wrong"
        dens[g].append(d)
        pooled[g][0] += n
        pooled[g][1] += len(text)
        if example is None:
            example = r
    if not dens["wrong"] or not dens["right"]:
        return None, None, example
    mr = sum(dens["right"]) / len(dens["right"])
    mw = sum(dens["wrong"]) / len(dens["wrong"])
    R = None if mr == 0 else mw / mr
    pr = pooled["right"][0] / (pooled["right"][1] / 1000.0) if pooled["right"][1] else 0.0
    pw = pooled["wrong"][0] / (pooled["wrong"][1] / 1000.0) if pooled["wrong"][1] else 0.0
    Ralt = None if pr == 0 else pw / pr
    print(f"# n_right {len(dens['right'])} n_wrong {len(dens['wrong'])}")
    return R, Ralt, example


Rb, Rb_alt, ex = model_R(fetch(JOBS["base"]))
Rr, Rr_alt, _ = model_R(fetch(JOBS["rl"]))

alt = None
if Rb_alt is not None and Rr_alt not in (None, 0):
    alt = Rb_alt / Rr_alt

if Rb is None or Rr is None or Rr == 0:
    # recipe: no finished-wrong rows or a right-row mean of 0 -> undefined, counts as refuted
    emit({"measured": None, "refuted_by_met": True, "alt_measured": None, "not_computable": None,
          "example_row": None})

measured = Rb / Rr
print(json.dumps({"measured": measured, "refuted_by_met": bool(measured < 0.62 or measured > 1.5),
                  "alt_measured": alt, "not_computable": None, "example_row": ex}))
