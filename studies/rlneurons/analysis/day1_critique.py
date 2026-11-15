"""Draft-critique-revision readout (specs/SPEC_critique.md, board work-70152d): MATH-500, the stored T 1.0 cue drafts of base and RL,
each finished draft continued after a fixed review line (jobs/revise.py, 4 shards per model); grader v3 on the whole text.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_critique

Run from the repository root. Inputs (not committed): runs/<job-id>/answers.jsonl of the shards in JOBS (`uv run tools/gpu.py get <job-id>`)
and the drafts runs/critique/<name>.jsonl.gz (prep/critique_drafts.py). Drafts that hit the cap were not revised and keep their score.
Writes results/day1_critique/readout.json and results/day1_critique/<model>_revise-01/ (run.json, metrics.json of the shards, examples.json).
"""
from __future__ import annotations

import gzip
import json
import pathlib
import re

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

# v3-stated (post hoc, after reading the RL right -> wrong rows): v3 reads "the answer is correct." as the answer "correct.". Here the
# revision's own answer counts only when, with the "Answer is" form of the marker removed, v3 still finds a box or an "Answer:" line in
# the revision; otherwise the draft's answer stands. Grader v3 itself is unchanged.
IS_MARK = re.compile(r"(?:[Ff]inal [Aa]nswer|Answer)(?:\*\*|\*|__)?\s*\bis\b")


def stated(gold, draft_score, revision):
    clean = IS_MARK.sub(" ", revision)
    return draft_score if R.extract_v3(clean)[0] == "none" else R.grade_v3(gold, clean)["score_v3"]


STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "day1_critique"
COMMIT = "c14120cf2f8db7e568208b01146870f8b10c4d52"
DRAFTS = {"base": ("base_cue_T1", "a2a9f38bc2daa18293adcbbd64a46a4a0bae21388aee63a74ac6b58026fe98bc", 77000000, 410, 3932.0),
          "rl": ("rl_cue_T1", "f6e8ed77370a7fd7584ccd18f2fbfb4455517d0bf0ae29439b212bcf9af73df9", 78000000, 457, 4695.5)}
JOBS = {"base": ["frustea-1114-184334-2498", "frustea-1114-184338-5774", "frustea-1114-184342-5bf5", "frustea-1114-184346-96a7"],
        "rl": ["frustea-1114-184349-f7b6", "frustea-1114-184353-6fe6", "frustea-1114-184358-a57e", "frustea-1114-184402-3de3"]}
CMD = ("bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.revise --model {m} "
       "--drafts /runs/inputs/critique/{f}.jsonl.gz --drafts-sha256 {h} --seed {s} --shard <0-3> --shards 4 --commit " + COMMIT)


def main():
    gold = {int(p["index"]): p["answer"] for p in json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())}
    idx = sorted(gold)
    cells, diffs = {}, {}
    for m, (f, h, seed, expect, draft_tok) in DRAFTS.items():
        drafts = {r["problem_index"]: r for r in map(json.loads, gzip.decompress((RUNS / "critique" / f"{f}.jsonl.gz").read_bytes()).decode().splitlines())}
        rev, metrics = {}, []
        for job in JOBS[m]:
            mt = json.loads((RUNS / job / "metrics.json").read_text())
            assert mt["status"] == "done" and mt["counts"]["n"] == mt["n_revised"] and mt["config"]["model"] == m, (job, mt["status"])
            metrics.append(mt)
            for r in map(json.loads, open(RUNS / job / "answers.jsonl")):
                assert r["problem_index"] not in rev, (m, r["problem_index"])
                rev[r["problem_index"]] = r
        assert set(rev) == {i for i in idx if not drafts[i]["cap_hit"]}, (m, "revised set is not the finished drafts")
        d0 = {i: R.grade_v3(gold[i], drafts[i]["text"])["score_v3"] for i in idx}
        assert sum(d0.values()) == expect, (m, sum(d0.values()), expect)
        d1 = {i: (rev[i]["score_v3"] if i in rev else d0[i]) for i in idx}
        d2 = {i: (stated(gold[i], d0[i], rev[i]["revision"]) if i in rev else d0[i]) for i in idx}
        assert all(rev[i]["draft_v3"] == d0[i] for i in rev), (m, "draft score in the job differs from the readout's")
        r2w = sorted(i for i in rev if d0[i] == 1 and d1[i] == 0)
        w2r = sorted(i for i in rev if d0[i] == 0 and d1[i] == 1)
        tok = sum(r["n_new"] for r in rev.values())
        cells[m] = {"n": 500, "draft_right_v3": expect, "revised_right_v3": sum(d1.values()), "n_revised": len(rev),
                    "draft_cap_hits_not_revised": 500 - len(rev), "right_to_wrong": r2w, "wrong_to_right": w2r,
                    "answer_changed": sum(r["answer_changed"] for r in rev.values()), "revision_cap_hits": sum(r["cap_hit"] for r in rev.values()),
                    "revision_tokens_per_revised": round(tok / len(rev), 1), "draft_tokens_per_problem": draft_tok,
                    "wrong_finished_drafts": sum(1 for i in rev if d0[i] == 0),
                    "stated_right_v3": sum(d2.values()), "stated_right_to_wrong": sorted(i for i in rev if d0[i] == 1 and d2[i] == 0),
                    "stated_wrong_to_right": sorted(i for i in rev if d0[i] == 0 and d2[i] == 1)}
        lo, hi = S.paired_bootstrap([d1[i] for i in idx], [d0[i] for i in idx], n_boot=5000, seed=0)
        diffs[f"{m} revised minus draft"] = {"points": round(100 * (sum(d1.values()) - expect) / 500, 2), "ci95_paired": [round(lo, 2), round(hi, 2)]}
        lo, hi = S.paired_bootstrap([d2[i] for i in idx], [d0[i] for i in idx], n_boot=5000, seed=0)
        diffs[f"{m} revised (v3-stated) minus draft"] = {"points": round(100 * (sum(d2.values()) - expect) / 500, 2), "ci95_paired": [round(lo, 2), round(hi, 2)]}
        d = OUT / f"{m}_revise-01"
        assert not d.exists(), f"{d} exists: a rerun gets the next number"
        d.mkdir(parents=True)
        (d / "run.json").write_text(json.dumps({"job_ids": JOBS[m], "commit": COMMIT, "command": CMD.format(m=m, f=f, h=h, s=seed),
                                                "runner": "uv run tools/gpu.py submit h100 --hours 1.5",
                                                "raw_answers": [f"runs/{j}/answers.jsonl (uv run tools/gpu.py get {j})" for j in JOBS[m]]}, indent=1) + "\n")
        (d / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
        changed = [i for i in sorted(rev) if rev[i]["answer_changed"]]
        keep = sorted(rev)[:1] + w2r[:1] + r2w[:1] + [i for i in changed if i not in w2r + r2w][:1]
        (d / "examples.json").write_text(json.dumps([{k: rev[i][k] for k in ("problem_index", "gold", "draft_extracted_v3", "draft_v3", "extracted_v3",
                                                                             "score_v3", "answer_changed", "n_new")} | {"draft_tail": rev[i]["draft"][-600:],
                                                                             "revision_head": rev[i]["revision"][:1500], "revision_tail": rev[i]["revision"][-400:]}
                                                     for i in keep], indent=1) + "\n")
    readout = {"spec": "studies/rlneurons/specs/SPEC_critique.md", "grader": "v3", "cells": cells, "diffs": diffs,
               "gap": {"draft": DRAFTS["rl"][3] - DRAFTS["base"][3], "revised": cells["rl"]["revised_right_v3"] - cells["base"]["revised_right_v3"],
                       "revised_v3_stated": cells["rl"]["stated_right_v3"] - cells["base"]["stated_right_v3"]}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "readout.json").write_text(json.dumps(readout, indent=1) + "\n")
    print(json.dumps(readout, indent=1))


if __name__ == "__main__":
    main()
