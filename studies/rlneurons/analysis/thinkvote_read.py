"""Readout of specs/SPEC_thinkvote.md beyond day1_vote and frontier: the filed predictions scored, the vote on the problems
without a Think-SFT training-prompt match, and the counts read from the raw rows (cap hits, finished answers, answer format,
problems one model solves and the other never does).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.thinkvote_read \
        --out studies/rlneurons/results/thinkvote/scored-01

Inputs: results/thinkvote/<set>_sft1_cue_s4-01/readout.json, results/day1_3/{hard328_rl_plain_s4r2,math500_rl}-01/readout.json,
the joined raw rows runs/thinkvote_<set>_sft1_cue_s4/answers.jsonl and the RL jobs' runs/<job>/answers.jsonl (this
workspace), and the overlap flags of result-f6a8bc (FLAGS, read from git). Fail loud.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess

from studies.rlneurons.lib import rln4_lib as R

RES = pathlib.Path("studies/rlneurons/results")
FLAGS = "origin/claude/weight-space-programming-research-ddd44e:studies/rlneurons/results/wsp1/sft_overlap-02/flags.json"
SETS = {"hard328": ("hard", "day1_3/hard328_rl_plain_s4r2-01", "runs/abaybektursun-1114-200505-5ff2"),
        "math500": ("math500", "day1_3/math500_rl-01", "runs/abaybektursun-1114-183640-e828")}
# filed before any job of this study finished: SPEC_thinkvote.md H1, H2 (commit a1822c8), results/rate/predict-0*, results/hazard/predict-01
PREDICTED = {"math500 vote over 4": {"Rasch (results/rate)": 473.1, "hazard (results/hazard/predict-01)": 472.1},
             "hard328 vote over 4": {"Rasch Lc, base vote shift": 243.8, "Rasch Lc, RL vote shift": 238.6, "point rule, MATH-500 gain": 245.9,
                                     "point rule, 328 gain": 234.0, "author": 238.0},
             "hard328 single (mean of 4)": {"profile": 217.6, "profile_corrected": 209.2, "Lc": 196.3, "L1": 201.1, "P": 190.5}}


def last_line_is_gold(r):
    """A finished wrong answer whose last non-empty line, without 'Answer:', $ and \\boxed, agrees with the gold (rln4_lib.agree)."""
    lines = [l.strip() for l in r["text"].split("\n") if l.strip()]
    x = re.sub(r"^\\boxed\{(.*)\}$", r"\1", re.sub(r"^Answer:\s*", "", lines[-1]).strip().strip("$").strip()) if lines else ""
    return bool(x) and bool(R.agree(R.norm_v3(x), R.norm_v3(r["gold"])))


def raw(path):
    rows = [r for r in map(json.loads, open(pathlib.Path(path) / "answers.jsonl")) if r["attempt"] == 0]
    caps = [r for r in rows if r["cap_hit"]]
    wrong = [r for r in rows if not r["cap_hit"] and not r["score_v3"]]
    fmt = [r for r in wrong if last_line_is_gold(r)]
    return rows, {"rows_attempt_0": len(rows), "cap_hits": len(caps), "cap_hits_rule_A": sum(r["loop_A"] for r in caps), "cap_hits_right": sum(r["score_v3"] for r in caps),
                  "cap_hits_with_over_20_CJK_characters": sum(len(re.findall(r"[一-鿿]", r["text"])) > 20 for r in caps),
                  "finished": len(rows) - len(caps), "finished_wrong": len(wrong), "finished_right_share": 1 - len(wrong) / (len(rows) - len(caps)),
                  "finished_wrong_without_extracted_answer": sum(r["extracted_v3"] is None for r in wrong),
                  "finished_wrong_last_line_is_gold": len(fmt), "last_line_is_gold_examples": [{"problem_index": r["problem_index"], "sample": r["sample"], "gold": r["gold"],
                                                                                                 "extracted_v3": r["extracted_v3"], "text_last_120": r["text"][-120:]} for r in fmt[:6]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    flags = json.loads(subprocess.run(["git", "show", FLAGS], capture_output=True, text=True, check=True).stdout)
    res = {"flags": FLAGS, "sets": {}}
    for name, (key, rl_dir, rl_run) in SETS.items():
        s, r = (json.loads((RES / d / "readout.json").read_text()) for d in (f"thinkvote/{name}_sft1_cue_s4-01", rl_dir))
        idx = s["problem_indices"]
        assert idx == r["problem_indices"]
        keep = [k for k, i in enumerate(idx) if flags[key][str(i)]["flag"] == "none"]
        clean = {row: {"think_sft": sum(s["per_problem"][row][k] for k in keep), "rl": sum(r["per_problem"][row][k] for k in keep)} for row in ("single", "vote")}
        s_rows, s_raw = raw(f"runs/thinkvote_{name}_sft1_cue_s4")
        r_rows, r_raw = raw(rl_run)
        ok = lambda rows: {i: sum(x["score_v3"] for x in rows if x["problem_index"] == i) for i in idx}
        s_ok, r_ok = ok(s_rows), ok(r_rows)
        sv, rv = dict(zip(idx, s["per_problem"]["vote"])), dict(zip(idx, r["per_problem"]["vote"]))
        res["sets"][name] = {
            "n": len(idx), "think_sft_single_each_sample": s["each_sample"]["single_right"], "rl_single_each_sample": r["each_sample"]["single_right"],
            "vote": {"think_sft": s["rows"]["vote"]["right"], "rl": r["rows"]["vote"]["right"], "rl_after_restart": r["rows"]["vote_after_restart"]["right"],
                     "think_sft_minus_rl": s["minus"]["differences_points"]["vote"]},
            "pass_at_4": {"think_sft": s["rows"]["pass_at_k"]["right"], "rl": r["rows"]["pass_at_k"]["right"]},
            "without_training_prompt_match": {"n": len(keep), "flagged": len(idx) - len(keep), **clean},
            "raw": {"think_sft": s_raw, "rl": r_raw},
            "vote_right_only": {"think_sft": sum(sv[i] and not rv[i] for i in idx), "rl": sum(rv[i] and not sv[i] for i in idx), "both": sum(sv[i] and rv[i] for i in idx)},
            "think_sft_vote_right_rl_no_sample_right": sorted(i for i in idx if sv[i] and not r_ok[i]),
            "rl_vote_right_think_sft_no_sample_right": sorted(i for i in idx if rv[i] and not s_ok[i])}
    obs = {"math500 vote over 4": res["sets"]["math500"]["vote"]["think_sft"], "hard328 vote over 4": res["sets"]["hard328"]["vote"]["think_sft"],
           "hard328 single (mean of 4)": sum(res["sets"]["hard328"]["think_sft_single_each_sample"]) / 4}
    res["predictions"] = {c: {"observed": obs[c], "rules": {k: {"predicted": v, "miss": round(obs[c] - v, 1)} for k, v in p.items()},
                              "nearest": min(p, key=lambda k: abs(obs[c] - p[k]))} for c, p in PREDICTED.items()}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    out.mkdir(parents=True)
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": "python -m studies.rlneurons.analysis.thinkvote_read --out " + a.out,
                                              "job_id": None, "gpu": "none (laptop)", "spec": "studies/rlneurons/specs/SPEC_thinkvote.md"}, indent=1) + "\n")
    print(json.dumps({"predictions": res["predictions"], **{n: {k: v for k, v in d.items() if k != "raw"} for n, d in res["sets"].items()}}, indent=1))
    print(json.dumps({n: {m: {k: v for k, v in d["raw"][m].items() if "examples" not in k} for m in d["raw"]} for n, d in res["sets"].items()}, indent=1))


if __name__ == "__main__":
    main()
