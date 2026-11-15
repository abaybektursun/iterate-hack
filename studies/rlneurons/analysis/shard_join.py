"""Joins the N runs of `run_cell --shard k/N` into the run folder that the same command without --shard would have
written, so every analysis script reads it unchanged.

    python -m studies.rlneurons.analysis.shard_join --runs runs/<job of shard 0> runs/<job of shard 1> ... --out runs/<name>

The runs may be given in any order. Checked here: every run is done; the shards are 0..N-1 of one N, each once; the config
(seed and commit included) is the same otherwise; no problem is in two runs; every run has its planned number of problems.
metrics.json is shard 0's with shard removed, the job ids of all runs, summed counts, and the longest generation and wall
time (the runs ran at once). Fail loud.
"""
from __future__ import annotations

import argparse
import json
import pathlib

DIFFER = ("shard", "n_problems", "out")
SUM = ("n", "correct_v3", "correct_v1", "cap_hits", "loop_A", "generated_tokens", "restarts", "n_planned", "tok_p_lt_1e2", "tok_p_lt_1e3")


def join(runs: list) -> tuple:
    """runs: [(metrics, rows)] in any order -> (metrics of the joined run, rows in shard order)."""
    for m, _ in runs:
        assert m["status"] == "done", f"{m['job_id']}: status {m['status']!r}, not done"
        assert m["config"].get("shard"), f"{m['job_id']}: not a --shard run"
    runs = sorted(runs, key=lambda r: int(r[0]["config"]["shard"].split("/")[0]))
    n_shards = len(runs)
    assert [m["config"]["shard"] for m, _ in runs] == [f"{k}/{n_shards}" for k in range(n_shards)], \
        f"shards {[m['config']['shard'] for m, _ in runs]} are not 0..{n_shards - 1} of {n_shards}, each once"
    m0 = runs[0][0]
    c0 = m0["config"]
    seen, out = {}, []
    for m, rows in runs:
        c = m["config"]
        differ = [k for k in c0 if k not in DIFFER and c[k] != c0[k]]
        assert not differ and m["commit"] == m0["commit"], f"shard {c['shard']}: differs from shard 0 in {differ or 'commit'}"
        idx = {r["problem_index"] for r in rows}
        assert len(idx) == c["n_problems"], f"shard {c['shard']}: {len(idx)} problems in the rows, {c['n_problems']} planned"
        both = idx & seen.keys()
        assert not both, f"shard {c['shard']}: problems {sorted(both)[:5]} are also in shard {seen[min(both)]}"
        seen.update({i: c["shard"] for i in idx})
        out += rows
    m = {**m0, "config": {**c0, "shard": None, "n_problems": len(seen)}, "job_id": "+".join(m["job_id"] for m, _ in runs),
         "joined_from": [{"job_id": m["job_id"], "shard": m["config"]["shard"], "counts": m["counts"], "wall_s": m["wall_s"]} for m, _ in runs],
         "counts": {k: sum(m["counts"][k] for m, _ in runs) for k in SUM}, "wall_s": max(m["wall_s"] for m, _ in runs)}
    m["counts"]["mean_generated_tokens"] = m["counts"]["generated_tokens"] / m["counts"]["n"]
    m["counts"]["generation_s"] = max(m["counts"]["generation_s"] for m, _ in runs)
    m["counts"]["tokens_per_s"] = sum(m["counts"]["tokens_per_s"] for m, _ in runs)
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
    print(f"{len(runs)} shards, {m['config']['n_problems']} problems, {len(rows)} rows, {m['counts']['correct_v3']} right -> {out}")


if __name__ == "__main__":
    main()
