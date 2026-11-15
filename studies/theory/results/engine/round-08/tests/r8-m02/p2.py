"""r8-m02 prediction 2: switch-marker rate per token on finished MATH-500 answers, cued base over RL plain, T 1.0."""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

BASE = "abaybektursun-1114-153825-208b"
RL = "abaybektursun-1114-183640-e828"
SW = re.compile(r"(?<![A-Za-z])(Alternatively|Another approach|Another way|Let me try (?:a )?(?:different|another)"
                r"|Let's try (?:a )?(?:different|another)|Instead, let)")


def path_for(job):
    p = f"runs/theory-rows/{job}/answers.jsonl"
    if os.path.exists(p):
        return p
    q = f"runs/theory-tests/{job}/answers.jsonl"
    if not os.path.exists(q):
        os.makedirs(os.path.dirname(q), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", q], check=True)
    return q


def kept_rows(path):
    """attempt == 0, sample in 0..3, first row per (problem_index, sample) in file order, finished only."""
    seen, out = set(), []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("attempt") != 0 or r.get("sample") not in (0, 1, 2, 3):
                continue
            key = (r["problem_index"], r["sample"])
            if key in seen:
                continue
            seen.add(key)
            if r.get("cap_hit") is True or r.get("finish_reason") == "length":
                continue
            out.append(r)
    return out


def slim(r):
    d = {k: r.get(k) for k in ("cell", "problem_index", "sample", "attempt", "n_new", "cap_hit", "finish_reason",
                               "extracted_v3", "gold", "score_v3")}
    d["text_head"] = r["text"][:200]
    d["S"] = len(SW.findall(r["text"]))
    return d


def main():
    try:
        base = kept_rows(path_for(BASE))
        rl = kept_rows(path_for(RL))
    except Exception as e:
        not_computable(f"cannot read a row file: {e}")
        return

    def st(rows):
        return [(len(SW.findall(r.get("text") or "")), r["n_new"]) for r in rows]

    pb, pr = {}, {}
    for r, (s, t) in zip(base, st(base)):
        pb.setdefault(r["problem_index"], []).append((s, t))
    for r, (s, t) in zip(rl, st(rl)):
        pr.setdefault(r["problem_index"], []).append((s, t))
    problems = [(pb.get(p, []), pr.get(p, [])) for p in sorted(set(pb) | set(pr))]

    def stat(sample):
        sb = sum(s for b, _ in sample for s, _ in b)
        tb = sum(t for b, _ in sample for _, t in b)
        sr = sum(s for _, q in sample for s, _ in q)
        tr = sum(t for _, q in sample for _, t in q)
        if sr == 0 or tb == 0:
            return float("inf")
        return (sb / tb) / (sr / tr)

    def alt(sample):
        # ratio of mean per-row rates S/T (each row weighted equally) instead of pooled sums
        rb = [s / t for b, _ in sample for s, t in b if t]
        rr = [s / t for _, q in sample for s, t in q if t]
        if not rb or not rr or sum(rr) == 0:
            return None
        return (sum(rb) / len(rb)) / (sum(rr) / len(rr))

    print(json.dumps({"groups": {"base problems with a finished row": len(pb), "rl problems with a finished row": len(pr),
                                 "base finished rows": len(base), "rl finished rows": len(rl)}}))
    SB = sum(s for b, _ in problems for s, _ in b)
    SR = sum(s for _, q in problems for s, _ in q)
    n = min(len(pb), len(pr))
    if SR == 0:
        if SB == 0:
            refuted_without_number()
        else:
            report(float("inf"), n, None, "none", refuted_by_met=False, alt_measured=None, example_row=slim(rl[0]))
        return
    val = stat(problems)
    report(val, n, bootstrap(stat, problems), "bootstrap", refuted_by_met=val < 1.15, alt_measured=alt(problems),
           example_row=slim(base[0]))


main()
