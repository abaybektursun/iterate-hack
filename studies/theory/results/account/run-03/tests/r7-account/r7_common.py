"""Shared code for the r7-account test scripts p1.py ... p66.py (same directory).

Every script names its cell, part and refuted_by condition explicitly; this module holds the parts the recipes share: the file
list and fetch commands, the per-side grade rules, rule A, the answer-statement rule R3, the ordered rules R1..R5, and the
statistic + report calls. Uses only the standard library, the team's grader v3 (studies/rlneurons/lib/rln4_lib.py) and the
team's noise helper (studies/theory/lib/noise.py).
"""
import json
import os
import re
import subprocess
import zlib

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, binomial, report, not_computable, refuted_without_number  # noqa: F401

DIR = "runs/theory-tests/r7-account"
S3 = "s3://pg-lineage-769063704696/results/rlneurons/"

# key: (kind, source, local name). kind "git" = committed file read in place.
FILES = {
    "PP": ("git", "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json", None),
    "CUE2": ("git", "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl", None),
    "T1": ("s3", "r4/base_rl-02/out/T1.jsonl", "r4_T1.jsonl"),
    "T3": ("s3", "r4/modal_t3-01/t3/T3.jsonl", "r4_T3.jsonl"),
    "P_BASE": ("s3", "r3/base-01/out/P_math500.jsonl", "r3_base_P_math500.jsonl"),
    "F_BASE": ("s3", "r3/base-01/out/F_math500.jsonl", "r3_base_F_math500.jsonl"),
    "P_HARD": ("s3", "r3/base-01/out/P_hard.jsonl", "r3_base_P_hard.jsonl"),
    "S2800": ("s3", "r3/s2800-01/out/P_math500.jsonl", "r3_s2800_P_math500.jsonl"),
    "S0400": ("s3", "r3/s0400_s0100-01/out/s0400/P_math500.jsonl", "r3_s0400_P_math500.jsonl"),
    "S0100": ("s3", "r3/s0400_s0100-01/out/s0100/P_math500.jsonl", "r3_s0100_P_math500.jsonl"),
    "FR": ("s3", "r3/fr-01/out/P_math500.jsonl", "r3_fr_P_math500.jsonl"),
    "E72C": ("s3", "r5/day1_hard328-01/abaybektursun-1114-151534-e72c/answers.jsonl", "r5_e72c.jsonl"),
    "R86EF": ("s3", "r5/day1_hard328-01/abaybektursun-1114-151540-86ef/answers.jsonl", "r5_86ef.jsonl"),
    "B7BA0": ("s3", "r5/day1_hard328-01/abaybektursun-1114-132922-7ba0/answers.jsonl", "r5_7ba0.jsonl"),
    "TH34AD": ("s3", "r5/day1_wdiff328-01/abaybektursun-1114-181228-34ad/answers.jsonl", "r5_34ad.jsonl"),
    "CODE": ("modal", "abaybektursun-1114-162452-0203/answers.jsonl", "vol_162452-0203.jsonl"),
}


class Unreadable(Exception):
    pass


def fpath(key):
    kind, src, local = FILES[key]
    if kind == "git":
        if not os.path.exists(src):
            raise Unreadable(f"{src} is not readable")
        return src
    p = os.path.join(DIR, local)
    if not (os.path.exists(p) and os.path.getsize(p) > 0):
        os.makedirs(DIR, exist_ok=True)
        if kind == "s3":
            subprocess.run(["aws", "s3", "cp", S3 + src, p, "--profile", "iterate-ecr", "--only-show-errors"], check=False)
        else:
            subprocess.run(["modal", "volume", "get", "iterate-runs", src, p], check=False, stdout=subprocess.DEVNULL)
    if not (os.path.exists(p) and os.path.getsize(p) > 0):
        raise Unreadable(f"{kind}:{src} could not be fetched")
    return p


_ROWS = {}


def rows(key):
    if key not in _ROWS:
        p = fpath(key)
        try:
            if p.endswith(".json"):
                _ROWS[key] = json.load(open(p))
            else:
                _ROWS[key] = [json.loads(l) for l in open(p) if l.strip()]
        except (ValueError, OSError) as e:
            raise Unreadable(f"{p}: {e}")
    return _ROWS[key]


_FIRST = {}


def _all(r):
    return True


def first_by(key, field="problem_index", where=_all):
    """First row in file order per value of `field` among rows satisfying `where` (cached per key, field, where)."""
    ck = (key, field, where)
    if ck in _FIRST:
        return _FIRST[ck]
    out = {}
    for r in rows(key):
        if field in r and where(r) and r[field] not in out:
            out[r[field]] = r
    _FIRST[ck] = out
    return out


def s0(r):
    return r.get("sample") == 0


def cap(r):
    """Cap hit = cap_hit true, or cap_hit missing and finish_reason == 'length'."""
    c = r.get("cap_hit")
    return c is True or (c is None and r.get("finish_reason") == "length")


_GRADE = {}


def regrade(r):
    """Grader v3 on the row's own text and gold; None when text or gold is missing."""
    if r.get("text") is None or r.get("gold") is None:
        return None
    k = id(r)
    if k not in _GRADE:
        _GRADE[k] = rln4_lib.grade_v3(r["gold"], r["text"])["score_v3"]
    return _GRADE[k]


def is_right(grade, capped):
    return grade is not None and grade == 1 and not capped


# ------------------------------------------------------------------------------------------------ rule A, R3
def rule_a(text):
    """Fires if a window of 8,000 characters starting at position 0 or right after a '\\n' (with at least 8,000 characters
    to the end) has zlib ratio (UTF-8 bytes, default level) < 0.10. Missing or shorter text does not fire."""
    if text is None:
        return False
    n, p = len(text), 0
    while p is not None and n - p >= 8000:
        w = text[p:p + 8000].encode("utf-8")
        if len(zlib.compress(w)) / len(w) < 0.10:
            return True
        q = text.find("\n", p)
        p = None if q < 0 else q + 1
    return False


def N(s):
    s = "".join(s.split())
    for t in ("$", "*", "#", "\\left", "\\right"):
        s = s.replace(t, "")
    return s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")


def r3(text, gold):
    if text is None:
        return True
    g = N(gold if gold is not None else "")
    lines = [N(l) for l in text.split("\n")]
    if not any("\\boxed{" in l for l in lines) and not any(l.startswith("Answer:") for l in lines):
        return True
    if any("\\boxed{" + g + "}" in l for l in lines):
        return True
    return any(l == "Answer:" + g or l == "Answer:" + g + "." for l in lines)


# ------------------------------------------------------------------------------------------------ sides
def side_pp(which):
    """per_problem.json: grade = t<which>_right, cap hit = t<which>_cap_hit == true."""
    out = {}
    for r in rows("PP"):
        if r.get("problem_index") is not None and r["problem_index"] not in out:
            out[r["problem_index"]] = (r.get(f"t{which}_right"), r.get(f"t{which}_cap_hit") is True, r)
    return out


def side_stored(key, where=_all):
    return {pi: (r.get("score_v3"), cap(r), r) for pi, r in first_by(key, where=where).items()}


def side_regrade_s0(key):
    out = {}
    for pi, r in first_by(key, where=s0).items():
        c = cap(r)
        # a cap hit is always wrong, so its grade is only needed to know whether it is null (text or gold missing)
        g = (None if r.get("text") is None or r.get("gold") is None else 0) if c else regrade(r)
        out[pi] = (g, c, r)
    return out


def a0s0(r):
    return r.get("attempt") == 0 and r.get("sample") == 0


CELLS = {
    "math500-null-T1": dict(B="pp", R=lambda: side_stored("CUE2", where=a0s0), E="math500"),
    "math500-rl-T1": dict(B="pp", R=lambda: side_pp(2), E="math500"),
    "math500-code-T1": dict(B="pp", R=lambda: side_stored("CODE"), E="math500"),
    "hard328-rl-T1": dict(B="E72C", R=lambda: side_stored("R86EF"), E="hard"),
    "hard328-theta05-T1": dict(B="E72C", R=lambda: side_stored("TH34AD"), E="hard"),
    "math500-s2800-T06": dict(B="F_BASE", R=lambda: side_regrade_s0("S2800"), E="math500"),
    "math500-s0400-T06": dict(B="F_BASE", R=lambda: side_regrade_s0("S0400"), E="math500"),
    "math500-s0100-T06": dict(B="F_BASE", R=lambda: side_regrade_s0("S0100"), E="math500"),
    "math500-fr-T06": dict(B="F_BASE", R=lambda: side_regrade_s0("FR"), E="math500"),
}


def build_cell(cell):
    """One dict per included problem (in both sides, non-null grade on both)."""
    cfg = CELLS[cell]
    if cfg["B"] == "pp":
        bside = side_pp(1)
        t1 = first_by("T1")                        # text and gold: first row with the problem_index (missing row: text missing)
        btext = {pi: t1.get(pi) for pi in bside}
    elif cfg["B"] == "E72C":
        bside = side_stored("E72C")
        btext = {pi: r for pi, (_, _, r) in bside.items()}
    else:
        bside = side_regrade_s0(cfg["B"])
        btext = {pi: r for pi, (_, _, r) in bside.items()}
    rside = cfg["R"]()
    probs = []
    for pi in sorted(set(bside) & set(rside)):
        bg, bc, brow = bside[pi]
        rg, rc, rrow = rside[pi]
        if bg is None or rg is None:
            continue
        tr = btext[pi]
        b_ok, r_ok = is_right(bg, bc), is_right(rg, rc)
        probs.append(dict(pi=pi, b_cap=bc, b_row=brow, r_row=rrow, text_row=tr,
                          text=None if tr is None else tr.get("text"), gold=None if tr is None else tr.get("gold"),
                          uid=None if tr is None else tr.get("unique_id"),
                          b_loopA=None if tr is None else tr.get("loop_A"),
                          gap=r_ok and not b_ok, bonly=b_ok and not r_ok))
    return probs, cfg["E"]


def evidence(p, ekind):
    """List of booleans (right or not), one per E row present. A null-grade row counts as present and not right."""
    out = []
    if ekind == "math500":
        a = first_by("P_BASE", where=s0).get(p["pi"])
        b = first_by("T3").get(p["pi"])
        for r in (a, b):
            if r is not None:
                out.append(is_right(None if cap(r) else regrade(r), cap(r)))
    else:
        a = first_by("P_HARD", field="unique_id", where=s0).get(p["uid"]) if p["uid"] is not None else None
        if a is not None:
            out.append(is_right(None if cap(a) else regrade(a), cap(a)))
        b = first_by("B7BA0").get(p["pi"])
        if b is not None:
            out.append(is_right(b.get("score_v3"), cap(b)))
    return out


def assign(p, ekind, loop_fn=None):
    loop_fn = loop_fn or (lambda q: rule_a(q["text"]))
    if p["b_cap"] and loop_fn(p):
        return "loop"
    if p["b_cap"]:
        return "budget"
    if r3(p["text"], p["gold"]):
        return "answer-statement"
    E = evidence(p, ekind)
    if E and sum(E) >= 1:
        return "reliability"
    if E and sum(E) == 0:
        return "deliberation"
    return "unassigned"


# ------------------------------------------------------------------------------------------------ outputs
def trim(r):
    if r is None:
        return None
    return {k: (v[:300] + "...[truncated]" if isinstance(v, str) and len(v) > 300 else v)
            for k, v in r.items() if k not in ("prompt", "prefill_ids", "cut_ids")}


def share_main(cell, part, refuted, loop_only=False):
    """Statistic: (gap problems assigned to `part`) / (gap problems). Bootstrap over gap problems."""
    try:
        probs, ekind = build_cell(cell)
        gaps = [p for p in probs if p["gap"]]
        if not gaps:
            return not_computable(f"{cell}: no gap problems, the share is undefined")
        if loop_only:
            labs = ["loop" if p["b_cap"] and rule_a(p["text"]) else "other" for p in gaps]
        else:
            labs = [assign(p, ekind) for p in gaps]
        alt = None
        if all(p["text_row"] is None or "loop_A" in p["text_row"] for p in gaps) and any(p["text_row"] is not None for p in gaps):
            if loop_only:
                alabs = ["loop" if p["b_cap"] and p["b_loopA"] is True else "other" for p in gaps]
            else:
                alabs = [assign(p, ekind, loop_fn=lambda q: q["b_loopA"] is True) for p in gaps]
            alt = sum(l == part for l in alabs) / len(gaps)
    except Unreadable as e:
        return not_computable(str(e))
    entries = list(zip(labs, range(len(gaps))))
    stat = lambda s: sum(l == part for l, _ in s) / len(s)
    m = stat(entries)
    print(json.dumps({"info": {"cell": cell, "gap_problems": len(gaps), "included_problems": len(probs),
                               "counts": {k: labs.count(k) for k in sorted(set(labs))}}}))
    ex = next((p for p, l in zip(gaps, labs) if l == part), gaps[0])
    report(m, len(gaps), bootstrap(stat, entries), "bootstrap", refuted_by_met=refuted(m), alt_measured=alt,
           example_row=trim(ex["b_row"]))


def net_main(cell, refuted):
    """Statistic: gap count minus base-only count. Bootstrap over included problems."""
    try:
        probs, _ = build_cell(cell)
    except Unreadable as e:
        return not_computable(str(e))
    if not probs:
        return not_computable(f"{cell}: no included problems")
    entries = [(p["gap"], p["bonly"]) for p in probs]
    stat = lambda s: sum(g for g, _ in s) - sum(b for _, b in s)
    m = stat(entries)
    g, b = sum(x for x, _ in entries), sum(y for _, y in entries)
    print(json.dumps({"info": {"cell": cell, "gap_count": g, "base_only_count": b, "included_problems": len(probs)}}))
    report(m, len(probs), bootstrap(stat, entries), "bootstrap", refuted_by_met=refuted(m), alt_measured=None,
           example_row=trim(probs[0]["b_row"]))


def cue_rows_s0to3(pi, any_attempt=False):
    """Rows of math500_base_cue-01 with that problem_index, attempt == 0 and sample in {0,1,2,3}, first per sample.
    any_attempt=True (alt reading): every row of samples 0-3, any attempt."""
    rs = [r for r in rows("CUE2") if r.get("problem_index") == pi and r.get("sample") in (0, 1, 2, 3)]
    if any_attempt:
        return rs
    out = {}
    for r in rs:
        if r.get("attempt") == 0 and r["sample"] not in out:
            out[r["sample"]] = r
    return list(out.values())


def fraction_report(group, counted, refuted, alt=None, info=None, empty_reason="the group is empty"):
    if not group:
        return not_computable(empty_reason)
    entries = list(zip(counted, range(len(counted))))
    stat = lambda s: sum(c for c, _ in s) / len(s)
    m = stat(entries)
    if info is not None:
        print(json.dumps({"info": info}))
    report(m, len(group), bootstrap(stat, entries), "bootstrap", refuted_by_met=refuted(m), alt_measured=alt,
           example_row=trim(group[0]["b_row"]))
