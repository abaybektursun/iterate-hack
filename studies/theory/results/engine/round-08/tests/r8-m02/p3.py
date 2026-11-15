"""r8-m02 prediction 3: within-problem switch-marker rate, finished-wrong over right, RL-Zero-Math plain, MATH-500, T 1.0."""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

JOB = "abaybektursun-1114-183640-e828"
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
    """attempt == 0, sample in 0..3, first row per (problem_index, sample) in file order, cap hits dropped."""
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
        rows = kept_rows(path_for(JOB))
    except Exception as e:
        not_computable(f"cannot read {JOB}/answers.jsonl: {e}")
        return
    by_p = {}
    for r in rows:
        right = r.get("score_v3") == 1
        s = len(SW.findall(r.get("text") or ""))
        t = r["n_new"]
        by_p.setdefault(r["problem_index"], {"w": [], "r": []})["r" if right else "w"].append((s, t))
    elig = [(pi, d["w"], d["r"]) for pi, d in sorted(by_p.items()) if d["w"] and d["r"]]
    if not elig:
        refuted_without_number()
        return

    def stat(sample):
        sw = sum(s for _, w, _ in sample for s, _ in w)
        tw = sum(t for _, w, _ in sample for _, t in w)
        sr = sum(s for _, _, rr in sample for s, _ in rr)
        tr = sum(t for _, _, rr in sample for _, t in rr)
        if sr == 0 or tw == 0:
            return float("inf")
        return (sw / tw) / (sr / tr)

    def alt(sample):
        # ratio of the mean, over eligible problems, of each problem's per-token rate (macro average)
        rw = [sum(s for s, _ in w) / sum(t for _, t in w) for _, w, _ in sample]
        rr = [sum(s for s, _ in r) / sum(t for _, t in r) for _, _, r in sample]
        mr = sum(rr) / len(rr)
        return (sum(rw) / len(rw)) / mr if mr > 0 else None

    sr_total = sum(s for _, _, rr in elig for s, _ in rr)
    n_w = sum(len(w) for _, w, _ in elig)
    n_r = sum(len(r) for _, _, r in elig)
    print(json.dumps({"groups": {"eligible problems (finished-wrong side)": len(elig),
                                 "eligible problems (right side)": len(elig),
                                 "finished-wrong rows": n_w, "right rows": n_r}}))
    if sr_total == 0:
        refuted_without_number()
        return
    R = stat(elig)
    ex = next(r for r in rows if r["problem_index"] == elig[0][0] and r.get("score_v3") != 1)
    report(R, len(elig), bootstrap(stat, elig), "bootstrap", refuted_by_met=R > 1.40, alt_measured=alt(elig),
           example_row=slim(ex))


main()
