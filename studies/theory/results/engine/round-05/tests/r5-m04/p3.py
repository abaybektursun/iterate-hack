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


# P3: share of Think-SFT cap hits whose problem lies in Q4 of RL (T2) generated tokens.
try:
    sft = load_first(SFT)
    t12 = load_first(T12)
except Exception as e:
    not_computable(f"cannot read input: {e}")
    raise SystemExit
if not all(isinstance(r.get("t2_generated_tokens"), (int, float)) for r in t12.values()):
    not_computable("t2_generated_tokens missing or non-numeric in some T1/T2 rows")
    raise SystemExit
q4, order = q4_by_rank(t12)          # ranks over the 500 problems of the T1/T2 file
q4v = q4_by_value(t12, order)
common = sorted(set(sft) & set(t12))  # problems missing from either file dropped
caps = [i for i in common if sft[i].get("cap_hit") is True]
if not caps:
    not_computable("Think-SFT has no cap hits in the joined set: empty denominator")
    raise SystemExit
measured = sum(1 for i in caps if i in q4) / len(caps)
alt = sum(1 for i in caps if i in q4v) / len(caps)
refuted = measured < 0.40
ex = next((i for i in caps if i in q4), caps[0])
example = {"sft": sft[ex], "t1_t2": t12[ex]}
emit(measured, refuted, alt, example)
