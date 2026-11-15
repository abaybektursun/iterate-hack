"""Shared engine for the repl-r7-account gap-taxonomy scripts (p<k>.py next to this file).

Each recipe defines a cell (base side B, other side, evidence E) and the same ordered rules
R1 loop, R2 budget, R3 answer-statement, R4 reliability, R5 deliberation, else unassigned.
The statistic is (gap problems assigned to <category>) / (gap problems).
Implemented exactly as written in the recipes; see notes.json for the readings taken.
"""
import json
import os
import subprocess
import zlib

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable

DIR = "runs/theory-tests/repl-r7-account"
S3 = "s3://pg-lineage-769063704696/results/rlneurons/"

# local name -> (kind, source)
SOURCES = {
    "r4_T1.jsonl": ("s3", S3 + "r4/base_rl-02/out/T1.jsonl"),
    "r3_base_P_math500.jsonl": ("s3", S3 + "r3/base-01/out/P_math500.jsonl"),
    "r3_base_F_math500.jsonl": ("s3", S3 + "r3/base-01/out/F_math500.jsonl"),
    "r3_base_P_hard.jsonl": ("s3", S3 + "r3/base-01/out/P_hard.jsonl"),
    "r4_T3.jsonl": ("s3", S3 + "r4/modal_t3-01/t3/T3.jsonl"),
    "r5_e72c.jsonl": ("s3", S3 + "r5/day1_hard328-01/abaybektursun-1114-151534-e72c/answers.jsonl"),
    "r5_86ef.jsonl": ("s3", S3 + "r5/day1_hard328-01/abaybektursun-1114-151540-86ef/answers.jsonl"),
    "r5_7ba0.jsonl": ("s3", S3 + "r5/day1_hard328-01/abaybektursun-1114-132922-7ba0/answers.jsonl"),
    "r5_34ad.jsonl": ("s3", S3 + "r5/day1_wdiff328-01/abaybektursun-1114-181228-34ad/answers.jsonl"),
    "r3_s2800_P_math500.jsonl": ("s3", S3 + "r3/s2800-01/out/P_math500.jsonl"),
    "r3_s0400_P_math500.jsonl": ("s3", S3 + "r3/s0400_s0100-01/out/s0400/P_math500.jsonl"),
    "r3_s0100_P_math500.jsonl": ("s3", S3 + "r3/s0400_s0100-01/out/s0100/P_math500.jsonl"),
    "r3_fr_P_math500.jsonl": ("s3", S3 + "r3/fr-01/out/P_math500.jsonl"),
    "modal_0203.jsonl": ("modal", "abaybektursun-1114-162452-0203/answers.jsonl"),
}
PER_PROBLEM = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
DAY1_BASE_CUE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"


def fetch(name):
    path = os.path.join(DIR, name)
    if not os.path.exists(path):
        os.makedirs(DIR, exist_ok=True)
        kind, src = SOURCES[name]
        if kind == "s3":
            subprocess.run(["aws", "s3", "cp", src, path, "--profile", "iterate-ecr", "--only-show-errors"], check=True)
        else:
            subprocess.run(["modal", "volume", "get", "iterate-runs", src, path], check=True)
    return path


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def first_by(rows, key="problem_index", cond=lambda r: True):
    """First row in file order per key value, among rows satisfying cond."""
    out = {}
    for r in rows:
        if cond(r) and r.get(key) not in out:
            out[r.get(key)] = r
    return out


def cap_hit(r):
    """cap_hit true, or cap_hit missing and finish_reason == 'length'."""
    if r.get("cap_hit") is None:
        return r.get("finish_reason") == "length"
    return r.get("cap_hit") is True


def v3_regrade(r):
    """Grader v3 of the row's text against its gold; None when text or gold is missing."""
    if r is None or r.get("text") is None or r.get("gold") is None:
        return None
    return rln4_lib.grade_v3(r["gold"], r["text"])["score_v3"]


def right_stored(r):
    """Right from stored score_v3 and the cap rule; None if the grade is null."""
    g = r.get("score_v3")
    if g is None:
        return None
    return bool(g == 1 and not cap_hit(r))


def right_regrade(r):
    g = v3_regrade(r)
    if g is None:
        return None
    return bool(g == 1 and not cap_hit(r))


# ------------------------------------------------------------------ rules
def rule_a(text):
    """Line-start 8,000-character windows, zlib (default level) ratio < 0.10. Missing/shorter text: no fire."""
    if text is None:
        return False
    n = len(text)
    for p in range(n):
        if p == 0 or text[p - 1] == "\n":
            if n - p < 8000:
                break  # later positions have even fewer characters to the end
            b = text[p:p + 8000].encode("utf-8")
            if len(zlib.compress(b)) / len(b) < 0.10:
                return True
    return False


def N(s):
    """Deletes all whitespace, '$', '*', '#', '\\left', '\\right' (in that order), then '\\dfrac'/'\\tfrac' -> '\\frac'."""
    s = "".join(ch for ch in s if not ch.isspace())
    for tok in ("$", "*", "#", "\\left", "\\right"):
        s = s.replace(tok, "")
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    return s


def rule_r3(text, gold):
    if text is None:
        return True
    lines = [N(l) for l in text.split("\n")]
    no_statement = not any("\\boxed{" in l for l in lines) and not any(l.startswith("Answer:") for l in lines)
    if no_statement:
        return True
    if gold is None:
        return False
    g = N(gold)
    return any(("\\boxed{" + g + "}") in l or l == "Answer:" + g or l == "Answer:" + g + "." for l in lines)


def classify(b_cap, b_text, b_gold, e_rights):
    """e_rights: list of booleans (right) for the E rows present."""
    if b_cap and rule_a(b_text):
        return "loop"
    if b_cap:
        return "budget"
    if rule_r3(b_text, b_gold):
        return "answer-statement"
    kB = sum(1 for x in e_rights if x)
    if kB >= 1:
        return "reliability"
    if len(e_rights) > 0 and kB == 0:
        return "deliberation"
    return "unassigned"


# ------------------------------------------------------------------ evidence
def evidence_math500():
    pa = first_by(load_jsonl(fetch("r3_base_P_math500.jsonl")), cond=lambda r: r.get("sample") == 0)
    pb = first_by(load_jsonl(fetch("r4_T3.jsonl")))

    def e(pi):
        out = []
        for src in (pa, pb):
            r = src.get(pi)
            if r is not None:
                out.append(bool(right_regrade(r)))  # present row; null grade counts as not right
        return out
    return e


def evidence_hard328():
    pa = first_by(load_jsonl(fetch("r3_base_P_hard.jsonl")), key="unique_id", cond=lambda r: r.get("sample") == 0)
    pb = first_by(load_jsonl(fetch("r5_7ba0.jsonl")))

    def e(pi, uid):
        out = []
        ra = pa.get(uid)
        if ra is not None:
            out.append(bool(right_regrade(ra)))
        rb = pb.get(pi)
        if rb is not None:
            out.append(bool(right_stored(rb)))
        return out
    return e


# ------------------------------------------------------------------ cells
def _strip(r):
    return None if r is None else {k: v for k, v in r.items() if k not in ("text", "prompt")}


def cell_per_problem(other):
    """B from per_problem.json (t1_*), text/gold from T1.jsonl. other: 'null' | 'rl' | 'code'."""
    pp = first_by(json.load(open(PER_PROBLEM)))
    t1 = first_by(load_jsonl(fetch("r4_T1.jsonl")))
    oth = None
    if other == "null":
        oth = first_by(load_jsonl(DAY1_BASE_CUE), cond=lambda r: r.get("attempt") == 0 and r.get("sample") == 0)
    elif other == "code":
        oth = first_by(load_jsonl(fetch("modal_0203.jsonl")))
    ev = evidence_math500()
    items = []
    for pi, b in pp.items():
        if b.get("t1_right") is None:
            continue
        b_cap = b.get("t1_cap_hit") is True
        b_right = bool(b["t1_right"] == 1 and not b_cap)
        if other == "rl":
            if b.get("t2_right") is None:
                continue
            o_right = bool(b["t2_right"] == 1 and not (b.get("t2_cap_hit") is True))
            o_row = {k: b.get(k) for k in ("problem_index", "t2_right", "t2_cap_hit")}
        else:
            o = oth.get(pi)
            if o is None:
                continue
            o_right = right_stored(o)
            if o_right is None:
                continue
            o_row = _strip(o)
        if not (o_right and not b_right):
            continue
        tr = t1.get(pi)
        text = tr.get("text") if tr else None
        gold = tr.get("gold") if tr else None
        cat = classify(b_cap, text, gold, ev(pi))
        items.append({"problem_index": pi, "category": cat, "B": dict(b), "B_text_row": _strip(tr), "other": o_row})
    return items


def cell_hard328(other_file):
    bm = first_by(load_jsonl(fetch("r5_e72c.jsonl")))
    om = first_by(load_jsonl(fetch(other_file)))
    ev = evidence_hard328()
    items = []
    for pi, b in bm.items():
        o = om.get(pi)
        if o is None:
            continue
        b_right, o_right = right_stored(b), right_stored(o)
        if b_right is None or o_right is None:
            continue
        if not (o_right and not b_right):
            continue
        cat = classify(cap_hit(b), b.get("text"), b.get("gold"), ev(pi, b.get("unique_id")))
        items.append({"problem_index": pi, "category": cat, "B": _strip(b), "other": _strip(o)})
    return items


def cell_t06(other_file):
    bm = first_by(load_jsonl(fetch("r3_base_F_math500.jsonl")), cond=lambda r: r.get("sample") == 0)
    om = first_by(load_jsonl(fetch(other_file)), cond=lambda r: r.get("sample") == 0)
    ev = evidence_math500()
    items = []
    for pi, b in bm.items():
        o = om.get(pi)
        if o is None:
            continue
        b_right, o_right = right_regrade(b), right_regrade(o)
        if b_right is None or o_right is None:
            continue
        if not (o_right and not b_right):
            continue
        cat = classify(cap_hit(b), b.get("text"), b.get("gold"), ev(pi))
        items.append({"problem_index": pi, "category": cat, "B": _strip(b), "other": _strip(o)})
    return items


CELLS = {
    "math500-null-T1": lambda: cell_per_problem("null"),
    "math500-rl-T1": lambda: cell_per_problem("rl"),
    "math500-code-T1": lambda: cell_per_problem("code"),
    "hard328-rl-T1": lambda: cell_hard328("r5_86ef.jsonl"),
    "hard328-theta05-T1": lambda: cell_hard328("r5_34ad.jsonl"),
    "math500-s2800-T06": lambda: cell_t06("r3_s2800_P_math500.jsonl"),
    "math500-s0400-T06": lambda: cell_t06("r3_s0400_P_math500.jsonl"),
    "math500-s0100-T06": lambda: cell_t06("r3_s0100_P_math500.jsonl"),
    "math500-fr-T06": lambda: cell_t06("r3_fr_P_math500.jsonl"),
}


def run(cell, category):
    """category: loop | budget | answer-statement | reliability | deliberation | unassigned."""
    items = CELLS[cell]()
    if not items:
        not_computable("no gap problems in cell %s: the ratio has a zero denominator" % cell)
        return

    def stat(sample):
        return sum(1 for it in sample if it["category"] == category) / len(sample)

    m = stat(items)
    ex = next((it for it in items if it["category"] == category), items[0])
    report(m, len(items), bootstrap(stat, items), "bootstrap", refuted_by_met=False, alt_measured=None,
           example_row=json.loads(json.dumps(ex, default=str)))
