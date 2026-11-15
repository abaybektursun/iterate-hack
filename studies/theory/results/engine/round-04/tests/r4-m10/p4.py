"""r4-m10 prediction 4: where step 400's accuracy on finished answers lies between base and step 2,800 (grader v3),
plain MATH-500, T 0.6 / top-p 0.95. Statistic (acc_M - acc_B) / (acc_E - acc_B).

Run from the repository root: python3 <this script>. Standard library plus the repository's own grader v3 code
(studies/rlneurons/lib/rln4_lib.grade_v3, which grader/rln4_grader_v3.py calls), which needs the math_verify package.
"""
import json
import os
import subprocess
import sys
import types

ROOT = os.getcwd()
DATA = os.path.join(ROOT, "runs", "theory-tests", "r4m10")
S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/"
FILES = {
    "B": (S3 + "base-01/out/P_math500.jsonl", os.path.join(DATA, "base_P_math500.jsonl")),
    "M": (S3 + "s0400_s0100-01/out/s0400/P_math500.jsonl", os.path.join(DATA, "s0400_P_math500.jsonl")),
    "E": (S3 + "s2800-01/out/P_math500.jsonl", os.path.join(DATA, "s2800_P_math500.jsonl")),
}
REFUTE_BELOW = 0.5


def out(d, details=None):
    if details:
        print(json.dumps({"details": details}, ensure_ascii=False))
    print(json.dumps(d, ensure_ascii=False))
    sys.exit(0)


def not_computable(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": reason, "example_row": None})


def fetch(name):
    uri, path = FILES[name]
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr", "--only-show-errors"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            not_computable(f"could not fetch {uri}: {r.stderr.strip()[:300]}")
    rows = []
    with open(path) as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_grader():
    sys.path.insert(0, ROOT)
    try:
        import numpy  # noqa: F401
    except ImportError:
        # numpy is imported at module level by n13_score / alwayson_edit but grade_v3 does not use it; a stub lets the grader
        # import. math_verify (the equivalence check inside grade_v3) is required.
        sys.modules["numpy"] = types.ModuleType("numpy")
    try:
        import math_verify  # noqa: F401
    except ImportError:
        not_computable("grader v3 (rln4_lib.grade_v3 -> n13_score.grade) needs the math_verify package, which this python3 "
                       "does not have; the standard library cannot reproduce grader v3")
    from studies.rlneurons.lib import rln4_lib as R
    return R


def first_sample0(rows, name):
    keep = {}
    for r in rows:
        for k in ("sample", "problem_index", "text", "gold"):
            if k not in r:
                not_computable(f"file {name} has rows without '{k}'")
        if r["sample"] != 0:
            continue
        if r["problem_index"] not in keep:
            keep[r["problem_index"]] = r
    return keep


def finished(r, name):
    """cap_hit false; cap_hit missing counts as finished only if finish_reason == 'stop'."""
    if "cap_hit" in r and r["cap_hit"] is not None:
        return r["cap_hit"] is False
    return r.get("finish_reason") == "stop"


def slim(r, v3):
    d = {k: v for k, v in r.items() if k not in ("text", "prefill_ids")}
    d["text_len"] = len(r.get("text") or "")
    d["text_tail"] = (r.get("text") or "")[-300:]
    d.update(v3)
    return d


def main():
    R = load_grader()
    D = {n: first_sample0(fetch(n), n) for n in ("B", "M", "E")}
    S = sorted(set(D["B"]) & set(D["M"]) & set(D["E"]))
    if not S:
        out({"measured": None, "refuted_by_met": True, "alt_measured": None, "not_computable": None, "example_row": None})
    grades, fin = {}, {}
    for n in ("B", "M", "E"):
        grades[n], fin[n] = {}, {}
        for i in S:
            r = D[n][i]
            text = r["text"] or ""
            if text.strip() == "":
                g = {"mode_v3": "none", "extracted_v3": None, "score_v3": 0}     # empty answer: wrong
            else:
                g = R.grade_v3(r["gold"], text)
                if g["extracted_v3"] is None:
                    g["score_v3"] = 0                                          # no answer found: wrong
            grades[n][i] = g
            fin[n][i] = finished(r, n)

    def acc(n, ids):
        f = [i for i in ids if fin[n][i]]
        return (sum(int(grades[n][i]["score_v3"]) for i in f) / len(f)) if f else None, len(f)

    a = {n: acc(n, S) for n in ("B", "M", "E")}
    accB, accM, accE = a["B"][0], a["M"][0], a["E"][0]

    # alt: finished set paired across files - only problems finished in all three files
    S_all = [i for i in S if fin["B"][i] and fin["M"][i] and fin["E"][i]]
    b = {n: acc(n, S_all) for n in ("B", "M", "E")}
    alt = None
    if None not in (b["B"][0], b["M"][0], b["E"][0]) and b["E"][0] - b["B"][0] > 0:
        alt = (b["M"][0] - b["B"][0]) / (b["E"][0] - b["B"][0])

    details = {"n_S": len(S), "acc": {n: a[n][0] for n in a}, "n_finished": {n: a[n][1] for n in a},
               "alt_n_paired_finished": len(S_all), "alt_acc": {n: b[n][0] for n in b}}
    ex_i = next((i for i in S if fin["M"][i]), S[0])
    ex = slim(D["M"][ex_i], grades["M"][ex_i])
    if None in (accB, accM, accE) or accE - accB <= 0:
        # recipe: undefined -> refuted_by says "or undefined"
        out({"measured": None, "refuted_by_met": True, "alt_measured": None, "not_computable": None, "example_row": None},
            dict(details, alt_measured_if_defined=alt))
    measured = (accM - accB) / (accE - accB)
    out({"measured": measured, "refuted_by_met": measured < REFUTE_BELOW, "alt_measured": alt, "not_computable": None,
         "example_row": ex}, details)


main()
