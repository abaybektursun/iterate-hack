"""r4-m10 prediction 5: share of step-400 cap hits that are rule-A loops, plain MATH-500, T 0.6 / top-p 0.95.

Run from the repository root: python3 <this script>. Standard library only (zlib; aws via subprocess).
"""
import json
import os
import subprocess
import sys
import zlib

ROOT = os.getcwd()
DATA = os.path.join(ROOT, "runs", "theory-tests", "r4m10")
S3 = "s3://pg-lineage-769063704696/results/rlneurons/r3/"
FILES = {"M": (S3 + "s0400_s0100-01/out/s0400/P_math500.jsonl", os.path.join(DATA, "s0400_P_math500.jsonl"))}
W, THR = 8000, 0.10
REFUTE_BELOW = 0.65


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


def is_cap(r):
    if "cap_hit" in r and r["cap_hit"] is not None:
        return r["cap_hit"] is True
    if "finish_reason" not in r:
        not_computable("a row has neither cap_hit nor finish_reason")
    return r["finish_reason"] == "length"


def rule_a(text):
    """Loop if some window text[p:p+8000], p = 0 or right after a '\\n', with >= 8000 characters from p to the end, has
    zlib ratio (default level, utf-8 bytes) < 0.10. Returns (is_loop, min_ratio_seen)."""
    n = len(text)
    if n < W:
        return False, None
    best = None
    p = 0
    while p is not None and n - p >= W:
        b = text[p:p + W].encode("utf-8")
        r = len(zlib.compress(b)) / len(b)
        best = r if best is None else min(best, r)
        if r < THR:
            return True, r
        q = text.find("\n", p)
        p = q + 1 if q >= 0 else None
    return False, best


def slim(r, extra):
    d = {k: v for k, v in r.items() if k not in ("text", "prefill_ids")}
    d["text_len"] = len(r.get("text") or "")
    d["text_tail"] = (r.get("text") or "")[-300:]
    d.update(extra)
    return d


def main():
    keep = {}
    for r in fetch("M"):
        for k in ("sample", "problem_index", "text"):
            if k not in r:
                not_computable(f"rows without '{k}'")
        if r["sample"] != 0:
            continue
        if r["problem_index"] not in keep:
            keep[r["problem_index"]] = r
    caps = [keep[i] for i in sorted(keep) if is_cap(keep[i])]
    if not caps:
        out({"measured": None, "refuted_by_met": True, "alt_measured": None, "not_computable": None, "example_row": None},
            {"n_rows": len(keep), "n_cap": 0})
    res = [(r, *rule_a(r["text"] or "")) for r in caps]
    loops = sum(1 for _, lp, _ in res if lp)
    measured = loops / len(caps)
    # alt: cap-hit rows with fewer than 8,000 characters (rule A cannot be applied) left out of the denominator
    long_caps = [x for x in res if len(x[0]["text"] or "") >= W]
    alt = (sum(1 for _, lp, _ in long_caps if lp) / len(long_caps)) if long_caps else None
    ex = next(((r, lp, mr) for r, lp, mr in res if lp), res[0])
    out({"measured": measured, "refuted_by_met": measured < REFUTE_BELOW, "alt_measured": alt, "not_computable": None,
         "example_row": slim(ex[0], {"rule_a_loop": ex[1], "rule_a_ratio": ex[2]})},
        {"n_rows": len(keep), "n_cap": len(caps), "n_loop": loops, "n_cap_ge_8000_chars": len(long_caps)})


main()
