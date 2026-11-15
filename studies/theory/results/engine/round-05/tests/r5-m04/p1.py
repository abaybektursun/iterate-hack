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


# P1: count of Think-SFT cue rows with cap_hit true (first row per problem_index); indices 0-499 missing = not cap hit.
try:
    sft = load_first(SFT)
except Exception as e:
    not_computable(f"cannot read {SFT}: {e}")
    raise SystemExit
if not all("cap_hit" in r for r in sft.values()):
    not_computable("field cap_hit missing from some rows")
    raise SystemExit
idx = [i for i in range(500) if i in sft]
cap = [i for i in idx if sft[i].get("cap_hit") is True]
measured = len(cap)
# alt: a cap hit as n_generated >= 16,384 (length at the cap) rather than the stored flag
alt = sum(1 for i in idx if isinstance(sft[i].get("n_generated"), (int, float)) and sft[i]["n_generated"] >= 16384)
refuted = measured < 28 or measured > 60
example = sft[cap[0]] if cap else sft[idx[0]]
emit(measured, refuted, alt, example)
