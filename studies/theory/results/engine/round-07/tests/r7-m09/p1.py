"""r7-m09 prediction 1: recurrence across prompts.
Among E4 problems (cued base 4/4 at attempt 0, no cap hits) where Think-SFT cue gives a finished v3-wrong answer (W),
fraction whose Think-SFT plain row is also wrong (score_v3 == 0 or cap hit)."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, refuted_without_number

BASE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
CUE = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"
PLAIN = "studies/rlneurons/results/wsp1/full500/sft1_plain-01/per_problem.json"


def path_of(p):
    """Use the file in the checkout; if missing, fetch it from git HEAD into runs/theory-tests/."""
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
    plain = first_per_problem(PLAIN)
    E4 = e4_set(base)
    # W: cue row exists, score_v3 == 0, not a cap hit (null/missing score_v3 non-cap rows excluded automatically)
    W = [pi for pi in E4 if pi in cue and cue[pi].get("score_v3") == 0 and cue[pi].get("cap_hit") is not True]
    kept = []
    for pi in W:
        pr = plain.get(pi)
        if pr is None:
            continue
        if pr.get("score_v3") is None and pr.get("cap_hit") is not True:
            continue
        kept.append((cue[pi], pr))
    if not kept:
        refuted_without_number()
        return

    def wrong(pr):
        return pr.get("score_v3") == 0 or pr.get("cap_hit") is True

    def stat(sample):
        return sum(wrong(pr) for _, pr in sample) / len(sample)

    def stat_alt(sample):
        # other reading: recurrence counts only a finished v3-wrong plain answer (plain cap hits not counted as wrong)
        return sum(pr.get("score_v3") == 0 and pr.get("cap_hit") is not True for _, pr in sample) / len(sample)

    m = stat(kept)
    ex = {"cue": kept[0][0], "plain": kept[0][1]}
    report(m, len(kept), bootstrap(stat, kept), "bootstrap", refuted_by_met=m < 0.30,
           alt_measured=stat_alt(kept), example_row=ex)


main()
