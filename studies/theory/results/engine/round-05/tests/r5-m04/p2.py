import json, os, subprocess

SFT = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"
T12 = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def path_for(rel):
    # committed file: read in place; if absent from the working tree, restore it from git HEAD into runs/theory-tests/
    if os.path.exists(rel):
        return rel
    out = os.path.join("runs/theory-tests", rel)
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        data = subprocess.run(["git", "show", "HEAD:" + rel], capture_output=True, check=True).stdout
        with open(out, "wb") as f:
            f.write(data)
    return out


def load_first(rel):
    """problem_index -> first row in file order."""
    with open(path_for(rel)) as f:
        rows = json.load(f)
    by = {}
    for r in rows:
        i = r.get("problem_index")
        if i is not None and i not in by:
            by[i] = r
    return by


def emit(measured, refuted, alt, example):
    print(json.dumps({"measured": measured, "refuted_by_met": bool(refuted), "alt_measured": alt,
                      "not_computable": None, "example_row": example}))


def not_computable(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": reason, "example_row": None}))


def q4_by_rank(t12):
    """Sort the problems by t2_generated_tokens ascending, ties by problem_index; Q4 = 1-based ranks 376-500."""
    order = sorted(t12, key=lambda i: (t12[i]["t2_generated_tokens"], i))
    return set(order[375:500]), order


def q4_by_value(t12, order):
    """Alt: every problem whose t2_generated_tokens is >= the value at rank 376 (boundary ties all included)."""
    thr = t12[order[375]]["t2_generated_tokens"]
    return {i for i in t12 if t12[i]["t2_generated_tokens"] >= thr}


# P2: (wrong rows with cap_hit true) / (wrong rows); wrong = score_v3 == 0, missing or null. Absent problems left out.
try:
    sft = load_first(SFT)
except Exception as e:
    not_computable(f"cannot read {SFT}: {e}")
    raise SystemExit
rows = [sft[i] for i in sorted(sft)]


def wrong(r):
    s = r.get("score_v3")
    return s is None or s == 0


W = [r for r in rows if wrong(r)]
if not W:
    not_computable("no wrong rows: the fraction has an empty denominator")
    raise SystemExit
Wc = [r for r in W if r.get("cap_hit") is True]
measured = len(Wc) / len(W)
# alt: a cap hit counts as a wrong answer whatever score_v3 says (a truncated answer is not a finished answer);
# share = cap hits / (wrong-by-score union cap hits)
U = [r for r in rows if wrong(r) or r.get("cap_hit") is True]
alt = sum(1 for r in U if r.get("cap_hit") is True) / len(U)
refuted = measured < 0.50
example = Wc[0] if Wc else W[0]
emit(measured, refuted, alt, example)
