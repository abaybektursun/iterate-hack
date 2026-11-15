"""ckptcue readout (specs/SPEC_ckptcue.md): RL steps 100 and 400 at T 1.0, plain and cue, against the base cue (T1) and the
final RL model (T2) per problem. Laptop, no model.

    python -m studies.rlneurons.analysis.ckptcue --runs runs s0100_plain=<job> s0400_plain=<job> s0100_cue=<job> s0400_cue=<job>

For each <cell>=<job-id> it reads runs/<job-id>/answers.jsonl and metrics.json and writes results/ckptcue/<cell>-01/
(run.json, metrics.json, per_problem.json, examples.json; refuses an existing folder), then results/ckptcue/readout.json.
T1 and T2 per problem come from results/rln4/t1_t2_items-01/per_problem.json (grader v3).
"""
import argparse
import json
import pathlib

import numpy as np

from studies.rlneurons.lib.n13_score import paired_bootstrap, wilson

HERE = pathlib.Path(__file__).resolve().parents[1]
OUT = HERE / "results" / "ckptcue"
EX = ("problem_index", "unique_id", "seed", "prompt", "text", "gold", "extracted_v3", "mode_v3", "score_v3", "n_generated", "cap_hit")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("cells", nargs="+")
    a = ap.parse_args()
    ref = sorted(json.load(open(HERE / "results/rln4/t1_t2_items-01/per_problem.json")), key=lambda r: r["problem_index"])
    x = {"base_cue_T1": np.array([r["t1_right"] for r in ref]), "rl_final_T2": np.array([r["t2_right"] for r in ref])}
    rows_out = {k: {"right": int(v.sum()), "n": len(v)} for k, v in x.items()}
    for spec in a.cells:
        cell, job = spec.split("=")
        src = pathlib.Path(a.runs) / job
        m = json.load(open(src / "metrics.json"))
        assert m["status"] == "done", (cell, m["status"])
        rows = sorted((json.loads(line) for line in open(src / "answers.jsonl")), key=lambda r: r["problem_index"])
        assert [r["problem_index"] for r in rows] == list(range(500)), cell
        d = OUT / f"{cell}-01"
        d.mkdir(parents=True)
        cfg = m["config"]
        json.dump({"job_id": job, "commit": m["commit"], "runner": "tools/vast.py run or ih submit (see job id prefix)",
                   "model_path": cfg["model_path"], "model_label": cfg["model_label"], "prompt": cfg["prompt"], "seed": cfg["seed"],
                   "temperature": cfg["temperature"], "top_p": cfg["top_p"], "max_tokens": cfg["max_tokens"],
                   "model_dir": m["engine"]["model_dir"], "raw_answers": f"runs/{job}/answers.jsonl (submitter's laptop)",
                   "started_utc": m["started_utc"], "updated_utc": m["updated_utc"]}, open(d / "run.json", "w"), indent=1)
        json.dump(m, open(d / "metrics.json", "w"), indent=1)
        json.dump([{"problem_index": r["problem_index"], "score_v3": r["score_v3"], "cap_hit": r["cap_hit"], "n_generated": r["n_generated"],
                    "extracted_v3": r["extracted_v3"], "opening": r["text"][:30]} for r in rows], open(d / "per_problem.json", "w"), indent=1)
        json.dump({"right": next(({k: r[k] for k in EX} for r in rows if r["score_v3"] == 1), None),
                   "wrong": next(({k: r[k] for k in EX} for r in rows if r["score_v3"] == 0 and not r["cap_hit"] and r["text"]), None)},
                  open(d / "examples.json", "w"), indent=1)
        x[cell] = np.array([r["score_v3"] for r in rows])
        k = int(x[cell].sum())
        rows_out[cell] = {"right": k, "n": 500, "wilson95_pct": wilson(k, 500), "cap_hits": sum(r["cap_hit"] for r in rows),
                          "empty_answers": sum(not r["text"] for r in rows), "okay_in_first_30": sum("Okay" in r["text"][:30] for r in rows),
                          "tokens_per_problem": sum(r["n_generated"] for r in rows) / 500, "job_id": job}

    def diff(p, q):
        return {"points": float(100 * (x[p].mean() - x[q].mean())), "ci95": paired_bootstrap(x[p], x[q], n_boot=5000)}
    pairs = [("s0100_plain", "base_cue_T1"), ("s0400_plain", "base_cue_T1"), ("s0100_cue", "s0100_plain"), ("s0400_cue", "s0400_plain"),
             ("s0100_cue", "base_cue_T1"), ("s0400_cue", "base_cue_T1"), ("rl_final_T2", "s0400_plain"), ("rl_final_T2", "s0400_cue"),
             ("s0400_plain", "s0100_plain")]
    out = {"cells": rows_out, "differences": {f"{p} minus {q}": diff(p, q) for p, q in pairs if p in x and q in x}}
    json.dump(out, open(OUT / "readout.json", "w"), indent=1)
    for k, v in rows_out.items():
        print(f"{k:<14} {v['right']:>3}/500  " + "  ".join(f"{kk} {vv}" for kk, vv in v.items() if kk in ("cap_hits", "empty_answers", "okay_in_first_30")))
    for k, v in out["differences"].items():
        print(f"{k:<36} {v['points']:+5.1f} [{v['ci95'][0]:+.1f}, {v['ci95'][1]:+.1f}]")


if __name__ == "__main__":
    main()
