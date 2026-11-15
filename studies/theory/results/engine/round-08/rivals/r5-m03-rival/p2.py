"""p2: T3 wrong rate on Q (top8 quick wrong) minus T3 wrong rate on C (top8 right, cued base >= 3 of 4 attempt-0 right)."""
import collections
import json
import os
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

ROOT = pathlib.Path.cwd()
TOP8 = ROOT / "studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json"
CUE = ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
T3 = ROOT / "runs/theory-tests/s3/r4/modal_t3-01/t3/T3.jsonl"


def fetch(s3, local):
    if not local.exists():
        local.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, str(local), "--profile", os.environ.get("AWS_PROFILE", "iterate-ecr")], check=True)


def first_per_problem(rows):
    out = {}
    for r in rows:
        out.setdefault(int(r["problem_index"]), r)
    return out


def main():
    fetch(T3_S3, T3)
    for f in (TOP8, CUE, T3):
        if not f.exists():
            return not_computable("row file missing: " + str(f))
    top8_all = json.loads(TOP8.read_text())
    top8 = first_per_problem(r for r in top8_all if r.get("score_v3") is not None)
    q = {i for i, r in top8.items() if r["score_v3"] == 0 and r["cap_hit"] is False and r["n_generated"] <= 2000}

    cue_rows = [json.loads(l) for l in open(CUE) if l.strip()]
    att0 = collections.defaultdict(list)
    by_sample = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in cue_rows:
        i = int(r["problem_index"])
        if r["attempt"] == 0:
            att0[i].append(r)
        by_sample[i][r["sample"]].append(r)
    # main: exactly 4 attempt-0 rows, >= 3 of them score_v3 == 1
    cue_ok = {i for i, rs in att0.items() if len(rs) == 4 and sum(x["score_v3"] == 1 for x in rs) >= 3}
    # alt: a sample counts as solved by its final attempt (highest attempt, after restarts); 4 samples, >= 3 solved
    cue_ok_alt = set()
    for i, ss in by_sample.items():
        finals = [max(rs, key=lambda x: x["attempt"]) for rs in ss.values()]
        if len(finals) == 4 and sum(x["score_v3"] == 1 for x in finals) >= 3:
            cue_ok_alt.add(i)
    top8_right = {i for i, r in top8.items() if r["score_v3"] == 1 and r["cap_hit"] is False}
    c, c_alt = top8_right & cue_ok, top8_right & cue_ok_alt

    t3 = first_per_problem(json.loads(l) for l in open(T3) if l.strip())
    wrong = {}
    for i in q | c | c_alt:
        if i in t3:
            r = t3[i]
            g = R.grade_v3(r["gold"], r["text"])  # extracted None -> score 0
            wrong[i] = int(g["score_v3"] == 0 or bool(r["cap_hit"]))
    qs = [("Q", i, wrong[i]) for i in sorted(q) if i in wrong]
    cs = [("C", i, wrong[i]) for i in sorted(c) if i in wrong]
    cs_alt = [("C", i, wrong[i]) for i in sorted(c_alt) if i in wrong]
    if not qs or not cs:
        return not_computable("empty group after dropping problems without a T3 row: |Q| %d, |C| %d" % (len(qs), len(cs)))

    def stat(s):
        a = [w for g, _, w in s if g == "Q"]
        b = [w for g, _, w in s if g == "C"]
        # a resample with an empty group counts that group's fraction as 0 (only in the bootstrap; the main number has both)
        return (sum(a) / len(a) if a else 0.0) - (sum(b) / len(b) if b else 0.0)

    problems = qs + cs  # Q and C are disjoint (top8 score_v3 0 vs 1)
    alt = stat(qs + cs_alt) if cs_alt else None
    i0 = qs[0][1]
    r0 = t3[i0]
    ex = {"group": "Q", "top8": top8[i0], "t3": {k: v for k, v in r0.items() if k not in ("text", "answer_tokens", "prefill_ids")},
          "t3_text_tail": r0["text"][-300:], "wrong": wrong[i0], "n_Q": len(qs), "n_C": len(cs), "n_C_alt": len(cs_alt)}
    report(stat(problems), len(problems), bootstrap(stat, problems), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=ex)


main()
