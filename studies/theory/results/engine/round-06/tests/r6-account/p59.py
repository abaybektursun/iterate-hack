"""r6-account prediction 59: fraction of math500-s0400cue-T06 loop-part problems with kB >= 1 (recipe: offline.json k=59)."""
K = 59
CELL = "s0400"         # cell: null | rl | top8 | plainbase | minp | s0400 | fr
KIND = "cross"         # share | net | cross
PART = "loop"          # share: the part counted; cross: the part whose problems form the denominator
COUNT = "kb_ge1"       # cross only: "pp_t1" (per_problem.json t1_right true and t1_cap_hit not true) | "kb_ge1"
REFUTE = ("bounds", 0.78, None)  # ("bounds", lo, hi) | ("none",) | ("rulea_all",) | ("positive",)
ALT_R3 = False         # alt_measured: the same statistic with the other reading of R3

# ---------------------------------------------------------------------------------------------- shared body (r6-account)
import json, os, re, subprocess, zlib
from studies.theory.lib.noise import bootstrap, binomial, report, not_computable, refuted_without_number

ROOT = "runs/theory-tests/r6-account"
RES = "s3://pg-lineage-769063704696/results/"
PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
DAY = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
TOP8 = "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
KEYS = {"T1": "rlneurons/r4/base_rl-02/out/T1.jsonl", "T3": "rlneurons/r4/modal_t3-01/t3/T3.jsonl",
        "FB": "rlneurons/r3/base-01/out/F_math500.jsonl", "F400": "rlneurons/r3/s0400_s0100-01/out/s0400/F_math500.jsonl",
        "FFR": "rlneurons/r3/fr-01/out/F_math500.jsonl"}
VOLS = {"minp_b": "frustea-1114-180849-456c/answers.jsonl", "minp_r": "frustea-1114-180857-8f87/answers.jsonl"}
CELLS = {"null": ("t1", "s3"), "rl": ("t1", "t2"), "top8": ("t1", "top8"), "plainbase": ("T3", "t2"),
         "minp": ("minp_b", "minp_r"), "s0400": ("FB", "F400"), "fr": ("FB", "FFR")}
RAW = {}


def fetch_s3(key):
    p = f"{ROOT}/s3k/{key}"
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", RES + key, p, "--profile", "iterate-ecr", "--only-show-errors"], check=True)
    return p


def fetch_vol(path):
    p = f"{ROOT}/vol/{path}"
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", path, p], check=True)
    return p


def jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def first(rows, keep=lambda r: True):
    out = {}
    for r in rows:
        if keep(r) and r.get("problem_index") is not None and r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return out


def is_cap(r):
    """cap_hit true, or cap_hit missing and finish_reason 'length'."""
    v = r.get("cap_hit")
    return v is True if v is not None else r.get("finish_reason") == "length"


def side(kind):
    """problem_index -> {right, cap, row}; problems the recipe excludes are absent."""
    if kind in ("t1", "t2"):
        out = {}
        for i, r in first(json.load(open(PP))).items():
            if r.get(kind + "_right") is None:
                continue                                    # null: excluded
            c = r.get(kind + "_cap_hit") is True
            out[i] = {"right": r[kind + "_right"] == 1 and not c, "cap": c, "row": r}
        return out
    if kind == "s3":
        rows = first(jsonl(DAY), lambda r: r.get("attempt") == 0 and r.get("sample") == 3)
        return {i: {"right": r.get("score_v3") == 1 and not is_cap(r), "cap": is_cap(r), "row": r} for i, r in rows.items()}
    if kind in ("top8", "minp_b", "minp_r"):
        if kind == "top8":
            rows = first(json.load(open(TOP8)))
        else:
            rows = first(jsonl(fetch_vol(VOLS[kind])), lambda r: r.get("attempt", 0) == 0)
        RAW[kind] = rows
        return {i: {"right": r["score_v3"] == 1 and not is_cap(r), "cap": is_cap(r), "row": r}
                for i, r in rows.items() if r.get("score_v3") is not None}      # null score_v3: excluded
    from studies.rlneurons.lib import rln4_lib                                  # grader v3, regrade on text vs gold
    rows = first(jsonl(fetch_s3(KEYS[kind])), (lambda r: True) if kind == "T3" else (lambda r: r.get("sample") == 0))
    RAW[kind] = rows
    out = {}
    for i, r in rows.items():
        if r.get("text") is None or r.get("gold") is None:
            continue                                        # null row: excluded
        v = rln4_lib.grade_v3(r["gold"], r["text"])["score_v3"]
        out[i] = {"right": v == 1 and not is_cap(r), "cap": is_cap(r), "row": r}
    return out


def rule_a(text):
    """Fires if a window of 8,000 chars starting at 0 or after a '\\n' (with >= 8,000 chars to the end) has zlib ratio < 0.10."""
    if not text:
        return False
    for p in [0] + [j + 1 for j, ch in enumerate(text) if ch == "\n"]:
        if len(text) - p < 8000:
            break
        w = text[p:p + 8000].encode()
        if len(zlib.compress(w)) / len(w) < 0.10:
            return True
    return False


def N(s):
    s = re.sub(r"\s", "", s)
    for d in ("$", "*", "#", "\\left", "\\right"):
        s = s.replace(d, "")
    return s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")


def r3(text, gold, alt=False):
    """Main: no N(line) has '\\boxed{' and none starts with 'Answer:', or some N(line) contains '\\boxed{g}' or equals 'Answer:g'
    ('.' allowed). Alt: an answer line is any N(line) containing 'Answer:' (so 'FinalAnswer:' counts) and the gold statement
    may end such a line."""
    if text is None:
        return True                                         # missing text is taken
    g = N(gold) if gold is not None else None
    L = [N(l) for l in text.split("\n")]
    if alt:
        noline = not any("\\boxed{" in l or "Answer:" in l for l in L)
        stated = g is not None and any("\\boxed{" + g + "}" in l or l.endswith("Answer:" + g) or l.endswith("Answer:" + g + ".") for l in L)
    else:
        noline = not any("\\boxed{" in l for l in L) and not any(l.startswith("Answer:") for l in L)
        stated = g is not None and any("\\boxed{" + g + "}" in l or l == "Answer:" + g or l == "Answer:" + g + "." for l in L)
    return noline or stated


def load_E():
    E = {}
    for r in jsonl(DAY):
        if r.get("attempt") == 0 and r.get("sample") in (0, 1, 2):
            E.setdefault(r["problem_index"], {}).setdefault(r["sample"], r)   # first per sample
    return E


def kB(erows):
    return sum(1 for s in (0, 1, 2) if s in erows and erows[s].get("score_v3") == 1 and not is_cap(erows[s]))  # missing: not right


def trim(r):
    if r is None:
        return None
    out = {k: v for k, v in r.items() if k not in ("prompt", "prefill_ids", "answer_tokens", "cut_ids")}
    t = out.get("text")
    if isinstance(t, str) and len(t) > 400:
        out["text"] = t[:200] + f" ...[{len(t)} chars, middle cut for the report]... " + t[-200:]
    return out


def refuted(m):
    if REFUTE[0] == "bounds":
        lo, hi = REFUTE[1], REFUTE[2]
        return (lo is not None and m < lo) or (hi is not None and m > hi)
    if REFUTE[0] == "positive":
        return m > 0
    return False


def main():
    bk, ok = CELLS[CELL]
    B, O = side(bk), side(ok)
    both = sorted(set(B) & set(O))
    if KIND == "net":
        ents = [(i, B[i], O[i]) for i in both]
        stat = lambda s: sum(e[2]["right"] and not e[1]["right"] for e in s) - sum(e[1]["right"] and not e[2]["right"] for e in s)
        g = sum(e[2]["right"] and not e[1]["right"] for e in ents)
        bo = sum(e[1]["right"] and not e[2]["right"] for e in ents)
        m = stat(ents)
        print(json.dumps({"k": K, "gap_count": g, "base_only_count": bo, "net": m, "n_problems": len(both)}))
        report(m, len(ents), bootstrap(stat, ents), "bootstrap", refuted_by_met=refuted(m),
               example_row={"problem_index": both[0], "B": trim(B[both[0]]["row"]), "other": trim(O[both[0]]["row"])})
        return
    TX = first(jsonl(fetch_s3(KEYS["T1"]))) if bk == "t1" else RAW[bk]   # B's text and gold
    E = load_E()
    cache = {}

    def part(i, alt=False):
        if (i, alt) not in cache:
            b, t = B[i], TX.get(i)
            text = t.get("text") if t else None
            gold = t.get("gold") if t else None
            if b["cap"] and rule_a(text):
                p = "loop"
            elif b["cap"]:
                p = "budget"
            elif r3(text, gold, alt):
                p = "answer-statement"
            else:
                k = kB(E.get(i, {}))
                p = "slip" if k == 3 else "sharpening" if k in (1, 2) else "reach" if k == 0 else "unassigned"
            cache[(i, alt)] = p
        return cache[(i, alt)]

    def example(i):
        ex = {"problem_index": i, "B": trim(B[i]["row"]), "other": trim(O[i]["row"]),
              "E": {str(s): r for s, r in sorted(E.get(i, {}).items())}}
        if bk == "t1":
            ex["B_text_row"] = trim(TX.get(i))
        return ex

    gap = [i for i in both if O[i]["right"] and not B[i]["right"]]
    if not gap:
        return not_computable("no gap problems (other side right and B wrong) in this cell")
    if KIND == "share":
        ents = [(i, B[i]["row"], O[i]["row"]) for i in gap]
        stat = lambda s: sum(part(e[0]) == PART for e in s) / len(s)
        m = stat(ents)
        alt = sum(part(i, True) == PART for i in gap) / len(gap) if ALT_R3 else None
        if REFUTE[0] == "rulea_all":
            met = any(rule_a(r.get("text")) for r in TX.values())    # the 500 B texts of the cell's file
        else:
            met = refuted(m)
        pick = next((i for i in gap if part(i) == PART), gap[0])
        report(m, len(ents), bootstrap(stat, ents), "bootstrap", refuted_by_met=met, alt_measured=alt, example_row=example(pick))
        return
    # cross
    if COUNT == "pp_t1":
        P = first(json.load(open(PP)))
        cnt = lambda i: P.get(i) is not None and P[i].get("t1_right") is not None and P[i]["t1_right"] == 1 and P[i].get("t1_cap_hit") is not True
    else:
        cnt = lambda i: kB(E.get(i, {})) >= 1
    pts = [i for i in gap if part(i) == PART]
    if not pts:
        return not_computable(f"no {PART}-part problems in this cell, so the fraction has no denominator")
    ents = [(i, B[i]["row"]) for i in pts]
    stat = lambda s: sum(cnt(e[0]) for e in s) / len(s)
    m = stat(ents)
    alt = None
    if ALT_R3:
        pa = [i for i in gap if part(i, True) == PART]
        alt = sum(cnt(i) for i in pa) / len(pa) if pa else None
    report(m, len(ents), bootstrap(stat, ents), "bootstrap", refuted_by_met=refuted(m), alt_measured=alt, example_row=example(pts[0]))


main()
