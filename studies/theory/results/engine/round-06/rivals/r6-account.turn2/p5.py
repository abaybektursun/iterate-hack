"""p5: Think-SFT cue solve rate on the cued base's T1 cap-hit problems minus its solve rate on T1 finished-wrong
problems matched on the 4-sample base count k4 (strata 0, 1, 2, {3,4})."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

T12 = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
SFT = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"
ROWS = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"


def is_true(x):
    # JSON true, or the integer 1 the file uses for t1_right
    if x is True:
        return True
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == 1


def first_by_index(rows):
    out = {}
    for r in rows:
        if "problem_index" in r:
            out.setdefault(r["problem_index"], r)
    return out


def row_cap(r):
    if r.get("cap_hit") is True:
        return True
    return "cap_hit" not in r and r.get("finish_reason") == "length"


def row_right(r):
    return r is not None and r.get("score_v3") == 1 and not row_cap(r)


def stratum(k):
    return 3 if k >= 3 else k


def sft_right(s):
    if s is None or s.get("score_v3") is None:
        return False
    return s.get("score_v3") == 1 and s.get("cap_hit") is not True


def main():
    for p in (T12, SFT, ROWS):
        if not os.path.exists(p):
            return not_computable(f"file not found: {p}")
    try:
        t12 = json.load(open(T12))
        sft = json.load(open(SFT))
        rows = [json.loads(line) for line in open(ROWS) if line.strip()]
    except Exception as e:  # noqa: BLE001
        return not_computable(f"file not readable: {e}")
    for f in ("problem_index", "t1_right", "t1_cap_hit"):
        if not any(f in r for r in t12):
            return not_computable(f"field {f} missing from {T12}")
    for f in ("problem_index", "score_v3", "cap_hit"):
        if not any(f in r for r in sft):
            return not_computable(f"field {f} missing from {SFT}")
    for f in ("problem_index", "attempt", "sample", "score_v3"):
        if not any(f in r for r in rows):
            return not_computable(f"field {f} missing from {ROWS}")

    t12_by = first_by_index(t12)
    sft_by = first_by_index(sft)

    # first row in file order per (problem, sample) with attempt 0; and (alt) the last attempt per (problem, sample)
    first0 = {}
    last_att = {}
    for r in rows:
        key = (r.get("problem_index"), r.get("sample"))
        if r.get("attempt") == 0:
            first0.setdefault(key, r)
        a = r.get("attempt")
        if isinstance(a, int) and (key not in last_att or a > last_att[key].get("attempt")):
            last_att[key] = r

    kept = []
    for pi, r in t12_by.items():
        if r.get("t1_right") is None:
            continue
        t1_right = is_true(r.get("t1_right")) and r.get("t1_cap_hit") is not True
        if t1_right:
            continue
        k4 = sum(row_right(first0.get((pi, s))) for s in range(4))
        k4_alt = sum(row_right(last_att.get((pi, s))) for s in range(4))
        kept.append({"problem_index": pi, "C": r.get("t1_cap_hit") is True,
                     "sft": sft_right(sft_by.get(pi)), "st": stratum(k4), "st_alt": stratum(k4_alt),
                     "_t12": r, "_sft": sft_by.get(pi)})

    def compute(sample, key):
        F = {}
        for p in sample:
            if not p["C"]:
                F.setdefault(p[key], []).append(p["sft"])
        rF = {st: sum(v) / len(v) for st, v in F.items()}
        Cs = [p for p in sample if p["C"] and p[key] in rF]
        if not Cs:
            return None, 0
        return sum(p["sft"] for p in Cs) / len(Cs) - sum(rF[p[key]] for p in Cs) / len(Cs), len(Cs)

    measured, n_c = compute(kept, "st")
    if measured is None:
        return not_computable("no C problem remains after dropping strata with no F problem")
    alt, _ = compute(kept, "st_alt")

    def stat(sample):
        v, _ = compute(sample, "st")
        return measured if v is None else v  # resample with no usable C problem (vanishingly rare)

    ex = next(p for p in kept if p["C"])
    report(measured, len(kept), bootstrap(stat, kept), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row={"t1_t2_items": ex["_t12"], "sft1_cue": ex["_sft"],
                        "rows_attempt0": [first0.get((ex["problem_index"], s)) for s in range(4)],
                        "n_C_used": n_c})


main()
