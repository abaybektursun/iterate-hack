"""r4-m06 offline prediction 2: difference-in-differences of re-check rates, RL (T2) minus base (T1), wrong minus right.

Recipe (as written): prediction 1's candidate extraction, grading (equivalence test behind score_v3), non-final filter
(>= 800 characters after the candidate's end) and re-check flag (hold-on regex in the next 800 characters), applied to T2.jsonl
(RL) and T1.jsonl (base + cue), all 500 rows each, cap hits included. Per file r_W, r_R pooled over rows; a class with zero
non-final candidates has rate 0. D = (r_W(T2) - r_W(T1)) - (r_R(T2) - r_R(T1)); refuted if D > 0.18.
Main = literal reading ((b) and (c) both count when they overlap). alt_measured = overlapping (b)/(c) candidates count once.
"""
import json
import pathlib
import re
import subprocess

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

# ------------------------------------------------------------------------------------------------ shared (same in p1-p3)
BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r4/"
FILES = {"T2": "modal_t2-01/t2/T2.jsonl", "T1": "base_rl-02/out/T1.jsonl"}
LOCAL = pathlib.Path("runs/theory-tests")
WINDOW = 800
MARK_B = re.compile(r"answer is:?\s*", re.IGNORECASE)
LINE_C = re.compile(r"^\s*\**Answer:?\**\s*(.+)$")
RECHECK = re.compile(r"\b(wait|hmm|let me (double[- ]?)?check|let me verify|double[- ]?check)\b", re.IGNORECASE)
GRADE_ERRORS = [0]
_CACHE = {}


def fetch(name):
    p = LOCAL / f"{name}.jsonl"
    if not p.exists():
        LOCAL.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", BUCKET + FILES[name], str(p), "--profile", "iterate-ecr", "--only-show-errors"], check=True)
    return p


def load(name):
    rows = [json.loads(line) for line in open(fetch(name)) if line.strip()]
    idx = [r["problem_index"] for r in rows]
    if len(set(idx)) != len(idx):
        raise ValueError(f"{name}: duplicate problem_index")
    for r in rows:
        for k in ("text", "gold", "cap_hit", "problem_index"):
            if k not in r:
                raise KeyError(f"{name}: field {k} missing")
    return sorted(rows, key=lambda r: r["problem_index"])


def clean(s):
    for t in ("$", "\\(", "\\)", "*"):
        s = s.replace(t, "")
    s = s.strip()
    if s.endswith("."):
        s = s[:-1]
    return s.strip()


def grade(gold, cand):
    if cand == "":
        return 0
    key = (gold, cand)
    if key not in _CACHE:
        try:
            _CACHE[key] = int(S.grade(R.norm_v3(gold), R.norm_v3(cand))["score"])
        except Exception:
            GRADE_ERRORS[0] += 1
            _CACHE[key] = 0
    return _CACHE[key]


def candidates(text, dedupe_bc=False):
    """List of dicts: kind, start, end, cand. Main reading: boxes + (b) + (c), dropping a (b)/(c) span that holds a box start.
    dedupe_bc=True (alt): additionally, a (c) span that overlaps a kept (b) span is dropped (the pair counts once, as the (b))."""
    boxes = [{"kind": "a", "start": i, "end": j, "cand": c} for i, j, c in R._boxes(text)]
    box_starts = [b["start"] for b in boxes]
    has_box = lambda s, e: any(s <= x < e for x in box_starts)
    bs = []
    for m in MARK_B.finditer(text):
        s = m.end()
        ends = [x for x in (text.find("\n", s), text.find(". ", s)) if x >= 0]
        e = min(ends) if ends else len(text)
        if not has_box(s, e):
            bs.append({"kind": "b", "start": s, "end": e, "cand": clean(text[s:e])})
    cs, pos = [], 0
    for line in text.split("\n"):
        m = LINE_C.match(line)
        if m:
            s, e = pos + m.start(1), pos + len(line)
            if not has_box(s, e):
                cs.append({"kind": "c", "start": s, "end": e, "cand": clean(m.group(1)), "line_start": pos})
        pos += len(line) + 1
    if dedupe_bc:
        cs = [c for c in cs if not any(b["start"] < c["end"] and b["end"] > c["line_start"] for b in bs)]
    return sorted(boxes + bs + cs, key=lambda c: (c["start"], c["kind"]))


def nonfinal(text, gold, dedupe_bc=False):
    out = []
    for c in candidates(text, dedupe_bc):
        if len(text) - c["end"] >= WINDOW:
            win = text[c["end"]:c["end"] + WINDOW]
            c = dict(c, right=grade(gold, c["cand"]), flag=RECHECK.search(win) is not None)
            out.append(c)
    return out


def rates(rows, dedupe_bc=False):
    n = {(r, f): 0 for r in (0, 1) for f in (False, True)}
    first = None
    for row in rows:
        for c in nonfinal(row["text"], row["gold"], dedupe_bc):
            n[(c["right"], c["flag"])] += 1
            if first is None or (c["right"] == 0 and c["flag"] and not (first[1]["right"] == 0 and first[1]["flag"])):
                first = (row, c)
    nW, nR = n[(0, False)] + n[(0, True)], n[(1, False)] + n[(1, True)]
    return {"n_wrong": nW, "n_right": nR, "flag_wrong": n[(0, True)], "flag_right": n[(1, True)],
            "r_W": n[(0, True)] / nW if nW else None, "r_R": n[(1, True)] / nR if nR else None}, first


def example(name, pair):
    if pair is None:
        return None
    row, c = pair
    keep = {k: v for k, v in row.items() if k not in ("text", "answer_tokens", "parsed_gold", "parsed_answer")}
    keep.update({"file": FILES[name], "text_len": len(row["text"]), "candidate_kind": c["kind"], "candidate": c["cand"],
                 "candidate_start": c["start"], "candidate_end": c["end"], "candidate_right": c["right"], "recheck_flag": c["flag"],
                 "text_around_candidate": row["text"][max(0, c["start"] - 200):c["end"] + WINDOW]})
    return keep


def emit(measured, refuted, alt, reason, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": bool(refuted), "alt_measured": alt, "not_computable": reason,
                      "example_row": ex}, ensure_ascii=False))


# ------------------------------------------------------------------------------------------------ prediction 2
def d_of(st2, st1):
    z = lambda v: 0.0 if v is None else v
    return (z(st2["r_W"]) - z(st1["r_W"])) - (z(st2["r_R"]) - z(st1["r_R"]))


def main():
    try:
        rows = {n: load(n) for n in ("T2", "T1")}
    except Exception as e:
        emit(None, False, None, f"row file not readable: {e!r}", None)
        return
    st, alt, first = {}, {}, {}
    for n in ("T2", "T1"):
        st[n], first[n] = rates(rows[n])
        alt[n], _ = rates(rows[n], dedupe_bc=True)
    print(json.dumps({"diag_main": st, "diag_alt": alt, "grade_errors": GRADE_ERRORS[0]}))
    D = d_of(st["T2"], st["T1"])
    emit(D, D > 0.18, d_of(alt["T2"], alt["T1"]), None, example("T2", first["T2"]) or example("T1", first["T1"]))


if __name__ == "__main__":
    main()
