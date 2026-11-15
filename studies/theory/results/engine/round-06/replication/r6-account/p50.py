"""r6-account p50: share of math500-frcue-T06 gap problems in the budget part (offline recipe, implemented as written).

Main number: (gap problems whose first firing rule of R1 loop, R2 budget, R3 answer-statement, R4 slip, R5 sharpening,
R6 reach is budget) / (gap problems). Gap = other side right and B wrong, over problems where neither side is excluded.
alt_measured: the same statistic with E (and, in math500-null-T1, the other side's sample 3) read after restarts: for
each sample the row with the highest attempt in day1_3 rows.jsonl instead of attempt 0.
Run from the repository root: PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 \
    --with antlr4-python3-runtime==4.11 python <this file>
"""
import json
import pathlib
import re
import subprocess
import zlib

from studies.theory.lib.noise import bootstrap, binomial, report, not_computable, refuted_without_number

K = 50
CELL = "math500-frcue-T06"
PART = "budget"
PARTS = ("loop", "budget", "answer-statement", "slip", "sharpening", "reach")

ROOT = pathlib.Path.cwd()
CACHE = ROOT / "runs" / "theory-tests" / "repl-r6-account"
S3 = "s3://pg-lineage-769063704696/results/"
PP_RLN4 = ROOT / "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
DAY1 = ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
TOP8 = ROOT / "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
KEY_T1 = "rlneurons/r4/base_rl-02/out/T1.jsonl"
KEY_T3 = "rlneurons/r4/modal_t3-01/t3/T3.jsonl"
KEY_BASE_F = "rlneurons/r3/base-01/out/F_math500.jsonl"
KEY_S0400_F = "rlneurons/r3/s0400_s0100-01/out/s0400/F_math500.jsonl"
KEY_FR_F = "rlneurons/r3/fr-01/out/F_math500.jsonl"
VOL_MINP_BASE = "frustea-1114-180849-456c/answers.jsonl"
VOL_MINP_RL = "frustea-1114-180857-8f87/answers.jsonl"


# ---------------------------------------------------------------- files

def s3file(key):
    p = CACHE / "s3k" / key
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3 + key, str(p), "--profile", "iterate-ecr", "--only-show-errors"], check=True)
    return p


def volfile(path):
    p = CACHE / "vol" / path
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", path, str(p)], check=True)
    return p


def jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def first_by_pi(rows, keep=lambda r: True):
    out = {}
    for r in rows:
        if keep(r) and r.get("problem_index") is not None and r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return out


def is_cap(r):
    """Cap hit = cap_hit true, or cap_hit missing and finish_reason 'length'."""
    c = r.get("cap_hit")
    return c is True or (c is None and r.get("finish_reason") == "length")


def truthy(v):
    return v is True or v == 1


# ---------------------------------------------------------------- E (cued base day1_3 samples 0-2)

DAY1_ROWS = jsonl(DAY1)


def day1_sample_rows(restart):
    """{(problem_index, sample): row}. restart False: first row with attempt 0. True: the row with the highest attempt."""
    out = {}
    for r in DAY1_ROWS:
        key = (r["problem_index"], r["sample"])
        if not restart:
            if r.get("attempt") == 0 and key not in out:
                out[key] = r
        else:
            if key not in out or (r.get("attempt") or 0) > (out[key].get("attempt") or 0):
                out[key] = r
    return out


def e_right(r):
    return r is not None and r.get("score_v3") == 1 and not is_cap(r)


def kB_of(samples, pi):
    return sum(1 for s in (0, 1, 2) if e_right(samples.get((pi, s))))   # missing = not right


# ---------------------------------------------------------------- RULES

def rule_a(text):
    """Fires if some window w = text[p:p+8000], p = 0 or right after '\n' with >= 8000 chars to the end,
    has len(zlib.compress(w.encode())) / len(w.encode()) < 0.10. Missing text: no."""
    if text is None:
        return False
    n = len(text)
    starts = [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]
    seen = set()
    for p in starts:
        if p in seen or n - p < 8000:
            continue
        seen.add(p)
        b = text[p:p + 8000].encode()
        if len(zlib.compress(b)) / len(b) < 0.10:
            return True
    return False


def N(s):
    s = re.sub(r"\s", "", s)
    for d in ("$", "*", "#", "\\left", "\\right"):
        s = s.replace(d, "")
    return s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")


def answer_statement(text, gold):
    if text is None:
        return True                                                     # missing text is taken
    lines = [N(l) for l in text.split("\n")]
    none_stated = not any("\\boxed{" in l for l in lines) and not any(l.startswith("Answer:") for l in lines)
    if none_stated:
        return True
    if gold is None:
        return False
    g = N(gold)
    return any(("\\boxed{" + g + "}") in l or l == "Answer:" + g or l == "Answer:" + g + "." for l in lines)


_RULE_A_CACHE = {}


def assign(b, kB):
    """Ordered RULES on B (the side that is wrong in a gap problem)."""
    if b["cap"]:
        key = b["pi"]
        if key not in _RULE_A_CACHE:
            _RULE_A_CACHE[key] = rule_a(b["text"])
        if _RULE_A_CACHE[key]:
            return "loop"
        return "budget"
    if answer_statement(b["text"], b["gold"]):
        return "answer-statement"
    if kB == 3:
        return "slip"
    if kB in (1, 2):
        return "sharpening"
    if kB == 0:
        return "reach"
    return None                                                         # unassigned


# ---------------------------------------------------------------- cells

def v3_right(r):
    from studies.rlneurons.lib import rln4_lib
    text = r.get("text")
    if text is None or r.get("gold") is None:
        return False
    return rln4_lib.grade_v3(r["gold"], text)["score_v3"] == 1


def short(r):
    if r is None:
        return None
    o = dict(r)
    if isinstance(o.get("text"), str):
        o["text_len"] = len(o["text"])
        o["text"] = o["text"][:300]
    if isinstance(o.get("prompt"), str):
        o["prompt"] = o["prompt"][:120]
    return o


def b_t1():
    """Cued base T1: right/cap from per_problem.json (null t1_right excluded); text and gold from T1.jsonl."""
    pp = first_by_pi(json.load(open(PP_RLN4)))
    t1 = first_by_pi(jsonl(s3file(KEY_T1)))
    out = {}
    for pi, e in pp.items():
        if e.get("t1_right") is None:
            continue
        row = t1.get(pi)
        out[pi] = {"pi": pi, "right": truthy(e["t1_right"]) and e.get("t1_cap_hit") is not True,
                   "cap": e.get("t1_cap_hit") is True, "text": row.get("text") if row else None,
                   "gold": row.get("gold") if row else None, "row": {"per_problem": e, "T1_row": short(row)}}
    return out


def b_from_rows(rows, regrade):
    out = {}
    for pi, r in rows.items():
        if regrade:
            right = v3_right(r) and not is_cap(r)
        else:
            if r.get("score_v3") is None:
                continue                                                # null score_v3: excluded
            right = r["score_v3"] == 1 and not is_cap(r)
        out[pi] = {"pi": pi, "right": right, "cap": is_cap(r), "text": r.get("text"), "gold": r.get("gold"), "row": short(r)}
    return out


def other_rl_t2():
    pp = first_by_pi(json.load(open(PP_RLN4)))
    return {pi: {"right": truthy(e["t2_right"]) and e.get("t2_cap_hit") is not True, "row": e}
            for pi, e in pp.items() if e.get("t2_right") is not None}


def other_day1_s3(restart):
    samples = day1_sample_rows(restart)
    out = {}
    for (pi, s), r in samples.items():
        if s == 3:
            out[pi] = {"right": e_right(r), "row": r}
    return out


def other_top8():
    pp = first_by_pi(json.load(open(TOP8)))
    return {pi: {"right": e["score_v3"] == 1 and e.get("cap_hit") is not True, "row": e}
            for pi, e in pp.items() if e.get("score_v3") is not None}


def sides(restart):
    """{pi: (B, other)} over problems where neither side is excluded."""
    if CELL == "math500-null-T1":
        B, O = b_t1(), other_day1_s3(restart)
    elif CELL == "math500-rl-T1":
        B, O = b_t1(), other_rl_t2()
    elif CELL == "math500-top8-T1":
        B, O = b_t1(), other_top8()
    elif CELL == "math500-plainbase-T1":
        B, O = b_from_rows(first_by_pi(jsonl(s3file(KEY_T3))), True), other_rl_t2()
    elif CELL == "math500-minp-T1":
        keep = lambda r: r.get("attempt", 0) in (0, None)
        B = b_from_rows(first_by_pi(jsonl(volfile(VOL_MINP_BASE)), keep), False)
        O = {pi: {"right": b["right"], "row": b["row"]}
             for pi, b in b_from_rows(first_by_pi(jsonl(volfile(VOL_MINP_RL)), keep), False).items()}
    elif CELL in ("math500-s0400cue-T06", "math500-frcue-T06"):
        keep = lambda r: r.get("sample") == 0
        B = b_from_rows(first_by_pi(jsonl(s3file(KEY_BASE_F)), keep), True)
        okey = KEY_S0400_F if CELL == "math500-s0400cue-T06" else KEY_FR_F
        O = {pi: {"right": b["right"], "row": b["row"]}
             for pi, b in b_from_rows(first_by_pi(jsonl(s3file(okey)), keep), True).items()}
    else:
        raise SystemExit("unknown cell " + CELL)
    return {pi: (B[pi], O[pi]) for pi in sorted(set(B) & set(O))}


_SIDES = {}


def entries(restart):
    """One entry per included problem: (pi, gap, part)."""
    if restart not in _SIDES:
        # only the null-T1 other side (day1_3 sample 3) depends on the restart reading; other cells reuse the main sides
        _SIDES[restart] = sides(restart) if (CELL == "math500-null-T1" or not _SIDES) else _SIDES[False]
    S = _SIDES[restart]
    samples = day1_sample_rows(restart)
    out = []
    for pi, (b, o) in S.items():
        gap = o["right"] and not b["right"]
        out.append((pi, gap, assign(b, kB_of(samples, pi)) if gap else None))
    return out


def stat(sample):
    gap = [e for e in sample if e[1]]
    if not gap:
        return 0.0
    return sum(1 for e in gap if e[2] == PART) / len(gap)


def main():
    main_entries = entries(False)
    gap = [e for e in main_entries if e[1]]
    if not gap:
        not_computable("no gap problems in " + CELL + ": the share is undefined")
        return
    measured = stat(main_entries)
    alt = stat(entries(True)) if any(e[1] for e in entries(True)) else None
    S = _SIDES[False]
    pick = next((e for e in gap if e[2] == PART), gap[0])
    b, o = S[pick[0]]
    example = {"problem_index": pick[0], "part": pick[2], "B": b["row"], "other": short(o["row"])}
    report(measured, len(gap), bootstrap(stat, main_entries), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=example)


if __name__ == "__main__":
    main()
