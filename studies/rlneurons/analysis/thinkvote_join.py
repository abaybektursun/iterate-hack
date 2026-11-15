"""Joins k run_cell runs of one sample each into the run folder that one `run_cell --samples k` job would have written
(specs/SPEC_thinkvote.md), so analysis/day1_vote.py and analysis/frontier.py read it unchanged.

    python -m studies.rlneurons.analysis.thinkvote_join --runs runs/<job of sample 0> runs/<job of sample 1> ... --out runs/<name>

Run s must be `run_cell --samples 1 --restarts 0 --seed <seed of run 0> + 10000 * s`: its rows then have exactly the seeds
of sample s under run_cell's rule (seed + 10000 * sample + index). Checked here: status done, the seed offset, the same
config otherwise, the same problems, every row's seed. The rows are copied with `sample` set to s; metrics.json is run 0's
with samples = k, the job ids of all runs and summed counts. Fail loud.
"""
from __future__ import annotations

import argparse
import json
import pathlib

SAME = ("model", "prompt", "set", "temperature", "top_p", "min_p", "max_tokens", "n_problems", "restarts", "samples", "shots", "model_path")
SUM = ("n", "correct_v3", "correct_v1", "cap_hits", "loop_A", "generated_tokens", "restarts", "n_planned")


def join(runs: list) -> tuple:
    """runs: [(metrics, rows)] in sample order -> (metrics of the joined run, rows)."""
    m0, rows0 = runs[0]
    c0 = m0["config"]
    assert c0["samples"] == 1 and c0["restarts"] == 0, "each run is one sample without restarts"
    idx0 = sorted(r["problem_index"] for r in rows0)
    out = []
    for s, (m, rows) in enumerate(runs):
        c = m["config"]
        assert m["status"] == "done", f"run {s} ({m['job_id']}): status {m['status']!r}, not done"
        assert all(c[k] == c0[k] for k in SAME), f"run {s}: config differs from run 0 in {[k for k in SAME if c[k] != c0[k]]}"
        assert c["seed"] == c0["seed"] + 10000 * s, f"run {s}: seed {c['seed']}, expected {c0['seed'] + 10000 * s}"
        assert sorted(r["problem_index"] for r in rows) == idx0 and len(idx0) == c0["n_problems"], f"run {s}: other problems than run 0"
        for r in rows:
            assert r["sample"] == 0 and r["attempt"] == 0 and r["seed"] == c0["seed"] + 10000 * s + r["problem_index"], (s, r["problem_index"], r["seed"])
            out.append({**r, "sample": s})
    m = {**m0, "config": {**c0, "samples": len(runs)}, "job_id": "+".join(m["job_id"] for m, _ in runs),
         "joined_from": [{"job_id": m["job_id"], "commit": m["commit"], "seed": m["config"]["seed"], "counts": m["counts"]} for m, _ in runs],
         "counts": {k: sum(m["counts"][k] for m, _ in runs) for k in SUM}}
    m["counts"]["mean_generated_tokens"] = m["counts"]["generated_tokens"] / m["counts"]["n"]
    return m, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists"
    runs = [(json.loads((pathlib.Path(d) / "metrics.json").read_text()),
             [json.loads(l) for l in (pathlib.Path(d) / "answers.jsonl").read_text().splitlines()]) for d in a.runs]
    m, rows = join(runs)
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
    (out / "answers.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"{len(runs)} samples, {len(rows)} rows, right per sample {[m['counts']['correct_v3'] for m, _ in runs]} -> {out}")


if __name__ == "__main__":
    main()
