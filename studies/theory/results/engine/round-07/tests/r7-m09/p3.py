"""r7-m09 prediction 3: share of cap hits among Think-SFT cue's wrong answers on E4 problems."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, refuted_without_number

BASE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
CUE = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"
CAP = 16384


def path_of(p):
    if os.path.exists(p):
        return p
    dst = os.path.join("runs/theory-tests/r7-m09", p)
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(subprocess.run(["git", "show", "HEAD:" + p], check=True, capture_output=True).stdout)
    return dst


def load_jsonl(p):
    with open(path_of(p)) as f:
        return [json.loads(l) for l in f if l.strip()]


def first_per_problem(p):
    with open(path_of(p)) as f:
        rows = json.load(f)
    out = {}
    for r in rows:
        if r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return out


def e4_set(base_rows):
    by = {}
    for r in base_rows:
        if r.get("attempt") == 0:
            by.setdefault(r["problem_index"], []).append(r)
    return sorted(pi for pi, rs in by.items()
                  if len(rs) == 4 and all(x.get("score_v3") == 1 and x.get("cap_hit") is not True for x in rs))


def main():
    base = load_jsonl(BASE)
    cue = first_per_problem(CUE)
    E4 = e4_set(base)
    wrong = []
    for pi in E4:
        r = cue.get(pi)
        if r is None:
            continue
        cap = r.get("cap_hit") is True
        if r.get("score_v3") is None and not cap:
            continue  # excluded per recipe
        if r.get("score_v3") == 0 or cap:
            wrong.append(r)
    if not wrong:
        refuted_without_number()
        return

    def stat(sample):
        return sum(r.get("cap_hit") is True for r in sample) / len(sample)

    def cap_alt(r):
        return r.get("cap_hit") is True or (r.get("n_generated") or 0) >= CAP

    # other reading: a cap hit is also any row whose n_generated reached the 16,384 cap (flag or length)
    wrong_alt = list(wrong)
    for pi in E4:
        r = cue.get(pi)
        if r is not None and r not in wrong_alt and cap_alt(r):
            wrong_alt.append(r)
    alt = sum(cap_alt(r) for r in wrong_alt) / len(wrong_alt)

    m = stat(wrong)
    report(m, len(wrong), bootstrap(stat, wrong), "bootstrap", refuted_by_met=m > 0.45,
           alt_measured=alt, example_row=wrong[0])


main()
