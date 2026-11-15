"""commit1 readout (specs/SPEC_commit1.md): the closing cue as a policy over a whole problem set. For each (N, form): answers of
at most N stored tokens count as stored, longer ones as their committed continuation (rows.jsonl of jobs/commit_cue.py).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.commit1 <model> <commit job>

Inputs: runs/<commit job>/ and the stored rows named in commit_cue.SOURCES, in runs/<job>/answers.jsonl. The configuration is
chosen on MATH-500 by the spec's rule and is the headline on the 328. Writes results/commit1/<model>-01/ (run.json,
metrics.json, readout.json, examples.json).
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

from studies.rlneurons.jobs.commit_cue import CUTS, FORMS, SOURCES
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")


def main():
    model, job = sys.argv[1], sys.argv[2]
    out = STUDY / "results" / "commit1" / f"{model}-01"
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    m = json.loads((RUNS / job / "metrics.json").read_text())
    assert m["status"] == "done" and m["config"]["model"] == model and m["config"]["n"] is None
    new = {}
    for r in map(json.loads, open(RUNS / job / "rows.jsonl")):
        new[(r["bench"], r["problem_index"], r["cut"], r["form"])] = r
    ro = {"spec": "studies/rlneurons/specs/SPEC_commit1.md", "model": model, "job_id": job, "sets": {}}
    for bench, src in SOURCES[model].items():
        st = {r["problem_index"]: r for r in map(json.loads, open(RUNS / src / "answers.jsonl")) if r["sample"] == 0 and r.get("attempt", 0) == 0}
        idx = sorted(st)
        base = [st[i]["score_v3"] for i in idx]
        cells = {"stored": {"right": sum(base), "n": len(idx), "tokens": round(sum(st[i]["n_new"] for i in idx) / len(idx), 1),
                            "cap_hits": sum(st[i]["cap_hit"] for i in idx), "source_job": src}}
        for n in CUTS:
            for form in FORMS:
                long = [i for i in idx if st[i]["n_new"] > n]
                pol = [new[(bench, i, n, form)]["score_v3"] if st[i]["n_new"] > n else st[i]["score_v3"] for i in idx]
                tok = [n + new[(bench, i, n, form)]["n_new"] if st[i]["n_new"] > n else st[i]["n_new"] for i in idx]
                lo, hi = S.paired_bootstrap(pol, base, n_boot=10000, seed=0)
                was_right = [i for i in long if st[i]["score_v3"]]
                caps = [i for i in long if st[i]["cap_hit"]]
                cells[f"{form}_{n}"] = {
                    "right": sum(pol), "tokens": round(sum(tok) / len(idx), 1),
                    "minus_stored": {"points": round(100 * (sum(pol) - sum(base)) / len(idx), 2), "ci95": [round(lo, 2), round(hi, 2)]},
                    "long_answers": len(long), "long_right_stored": len(was_right), "long_right_committed": sum(new[(bench, i, n, form)]["score_v3"] for i in long),
                    "kept_of_stored_right": sum(new[(bench, i, n, form)]["score_v3"] for i in was_right),
                    "right_of_stored_cap_hits": [sum(new[(bench, i, n, form)]["score_v3"] for i in caps), len(caps)],
                    "committed_without_answer": sum(new[(bench, i, n, form)]["extracted_v3"] is None for i in long)}
        ro["sets"][bench] = cells
    cand = {k: v for k, v in ro["sets"]["math500"].items() if k != "stored"}
    best = max(v["right"] for v in cand.values())
    chosen = min((k for k, v in cand.items() if v["right"] >= best - 2), key=lambda k: cand[k]["tokens"])
    ro["chosen_on_math500"] = chosen
    ro["headline_hard328"] = {"configuration": chosen, **ro["sets"]["hard328"][chosen], "stored": ro["sets"]["hard328"]["stored"]}
    out.mkdir(parents=True)
    shutil.copy(RUNS / job / "metrics.json", out / "metrics.json")
    (out / "run.json").write_text(json.dumps({"job_id": job, "commit": m["commit"], "config": m["config"],
                                              "raw_rows": f"runs/{job}/rows.jsonl (uv run tools/gpu.py get {job})"}, indent=1) + "\n")
    (out / "readout.json").write_text(json.dumps(ro, indent=1) + "\n")
    form, n = chosen.split("_")
    rows = [r for (b, i, c, f), r in sorted(new.items()) if b == "hard328" and c == int(n) and f == form]
    ex = lambda r: {k: r[k] for k in ("problem_index", "cut", "form", "gold", "extracted_v3", "score_v3", "n_new", "stored", "before_cut_tail", "continuation")}
    (out / "examples.json").write_text(json.dumps({"right": ex(next(r for r in rows if r["score_v3"])),
                                                   "wrong": ex(next(r for r in rows if not r["score_v3"] and r["extracted_v3"] is not None))}, indent=1) + "\n")
    for b, cells in ro["sets"].items():
        for k, v in cells.items():
            print(b, k, v["right"], v["tokens"], v.get("minus_stored", ""), "kept", v.get("kept_of_stored_right"), "/", v.get("long_right_stored"),
                  "caps", v.get("right_of_stored_cap_hits"))
    print("chosen on MATH-500:", chosen)


if __name__ == "__main__":
    main()
