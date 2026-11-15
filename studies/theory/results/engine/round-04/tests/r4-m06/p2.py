"""r4-m06 prediction 2: D = (r_W(T2) - r_W(T1)) - (r_R(T2) - r_R(T1)), re-check flag after non-final candidates.

Run from the repository root: python3 <this script>. Standard library plus the repository's own grader code
(studies/rlneurons/lib/rln4_lib.py, the code behind grader/rln4_grader_v3.py and score_v3), which needs math_verify.
"""
import json
import os
import re
import subprocess
import sys
import types

ROOT = os.getcwd()
DATA = os.path.join(ROOT, "runs", "theory-tests", "s3")
FILES = {
    "T2": ("s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t2-01/t2/T2.jsonl", os.path.join(DATA, "T2.jsonl")),
    "T1": ("s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl", os.path.join(DATA, "T1.jsonl")),
}


def out(d):
    print(json.dumps(d, ensure_ascii=False))
    sys.exit(0)


def not_computable(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": reason, "example_row": None})


# ------------------------------------------------------------------ files
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


# ------------------------------------------------------------------ grader v3 equivalence
def load_grader():
    sys.path.insert(0, ROOT)
    try:
        import numpy  # noqa: F401
    except ImportError:
        # numpy is imported at module level by n13_score / alwayson_edit but not used by grade/norm_v3; a stub lets the
        # grader import without it. math_verify (the equivalence itself) is required.
        sys.modules["numpy"] = types.ModuleType("numpy")
    try:
        import math_verify  # noqa: F401
    except ImportError:
        not_computable("grader v3 equivalence (n13_score.grade) needs the math_verify package, which this python3 does not have; "
                       "the standard library cannot reproduce it")
    from studies.rlneurons.lib import rln4_lib as R
    return R


R = load_grader()
_cache = {}


def equiv(gold, cand):
    """The equivalence step of grade_v3: S.grade(norm_v3(gold), norm_v3(candidate)). Empty strings are wrong."""
    if cand is None or cand.strip() == "":
        return 0
    k = (gold, cand)
    if k not in _cache:
        _cache[k] = int(R.S.grade(R.norm_v3(gold), R.norm_v3(cand))["score"])
    return _cache[k]


def final_v3(row):
    return int(R.grade_v3(row["gold"], row["text"])["score_v3"])


# ------------------------------------------------------------------ candidates (prediction 1 recipe)
BOXED = "\\boxed{"
RE_B = re.compile(r"answer is:?\s*", re.IGNORECASE)
RE_C = re.compile(r"^\s*\**Answer:?\**\s*(.+)$")
RE_FLAG = re.compile(r"\b(wait|hmm|let me (double[- ]?)?check|let me verify|double[- ]?check)\b", re.IGNORECASE)
WINDOW = 800


def clean(s):
    s = s.replace("$", "").replace("\\(", "").replace("\\)", "").replace("*", "")
    if s.endswith("."):
        s = s[:-1]
    return s


def boxes(text):
    res, i = [], text.find(BOXED)
    while i >= 0:
        depth, j = 1, i + len(BOXED)
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        if depth == 0:
            res.append({"kind": "box", "start": i, "end": j, "span": (i, j), "cand": text[i + len(BOXED):j - 1]})
        i = text.find(BOXED, i + 1)
    return res


def b_cands(text):
    res = []
    for m in RE_B.finditer(text):
        s = m.end()
        stops = [p for p in (text.find("\n", s), text.find(". ", s)) if p >= 0]
        e = min(stops) if stops else len(text)
        res.append({"kind": "answer_is", "start": m.start(), "end": e, "span": (s, e), "cand": clean(text[s:e])})
    return res


def c_cands(text):
    res, pos = [], 0
    for line in text.split("\n"):
        m = RE_C.match(line)
        if m:
            s, e = pos + m.start(1), pos + m.end(1)
            res.append({"kind": "answer_line", "start": pos, "end": e, "span": (s, e), "cand": clean(m.group(1))})
        pos += len(line) + 1
    return res


def candidates(text, dedupe_bc=False):
    """Main reading: boxes, (b) and (c) candidates; a (b)/(c) candidate whose span contains a box start is dropped (the box
    counts once, as the box). dedupe_bc (alt reading): also drop a (c) candidate whose span overlaps a kept (b) candidate."""
    bx = boxes(text)
    starts = [b["start"] for b in bx]
    bc = []
    for c in b_cands(text) + c_cands(text):
        s, e = c["span"]
        if any(s <= p < e for p in starts):
            continue
        bc.append(c)
    if dedupe_bc:
        bs = [c for c in bc if c["kind"] == "answer_is"]
        bc = bs + [c for c in bc if c["kind"] == "answer_line"
                   and not any(c["start"] < b["end"] and b["start"] < c["end"] for b in bs)]
    return sorted(bx + bc, key=lambda c: (c["start"], c["end"]))


def nonfinal(row, dedupe_bc=False):
    """Non-final candidates of one row, graded and flagged."""
    text, gold = row["text"], row["gold"]
    res = []
    for c in candidates(text, dedupe_bc):
        if len(text) - c["end"] < WINDOW:
            continue
        window = text[c["end"]:c["end"] + WINDOW]
        m = RE_FLAG.search(window)
        res.append({"problem_index": row["problem_index"], "gold": gold, "kind": c["kind"], "candidate": c["cand"],
                    "start": c["start"], "end": c["end"], "right": equiv(gold, c["cand"]), "flagged": int(m is not None),
                    "flag_match": m.group(0) if m else None, "text_after_end_first_200": window[:200]})
    return res


def rates(rows, dedupe_bc=False):
    allc = [c for r in rows for c in nonfinal(r, dedupe_bc)]
    W = [c for c in allc if not c["right"]]
    Rr = [c for c in allc if c["right"]]
    rW = sum(c["flagged"] for c in W) / len(W) if W else None
    rR = sum(c["flagged"] for c in Rr) / len(Rr) if Rr else None
    return {"r_W": rW, "r_R": rR, "n_W": len(W), "n_R": len(Rr), "cands": allc}


# ------------------------------------------------------------------ prediction 2
def z(x):
    return 0.0 if x is None else x   # recipe: zero non-final candidates in a class -> that rate is 0


def D(t2, t1):
    return (z(t2["r_W"]) - z(t1["r_W"])) - (z(t2["r_R"]) - z(t1["r_R"]))


def main():
    rl, base = fetch("T2"), fetch("T1")
    m2, m1 = rates(rl), rates(base)
    a2, a1 = rates(rl, dedupe_bc=True), rates(base, dedupe_bc=True)
    for nm, st in (("T2 main", m2), ("T1 main", m1), ("T2 alt", a2), ("T1 alt", a1)):
        print(nm, {k: st[k] for k in ("r_W", "r_R", "n_W", "n_R")}, file=sys.stderr)
    m = D(m2, m1)
    ex = next((c for c in m2["cands"] if not c["right"] and c["flagged"]), m2["cands"][0] if m2["cands"] else None)
    out({"measured": m, "refuted_by_met": bool(m > 0.18), "alt_measured": D(a2, a1), "not_computable": None,
         "example_row": dict(ex, file="T2") if ex else None})


if __name__ == "__main__":
    main()
