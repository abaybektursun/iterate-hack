"""Restart on a cap hit against a longer cap, for the delta transplant on hard328 (specs/SPEC_transplant.md, amendment 3).

    python3 -m studies.rlneurons.analysis.transplant_restart <run> --cap32 runs/<job-id>/hard328_cap32

Reads the committed rows of results/transplant/hard328-01 and hard328-02 (one sample per model and seed, cap 16,384) and the
answers of the M(2) run at cap 32,768. Writes results/transplant/<run>/readout.json:

  chains   a chain is a list of stored samples; per problem the answer is that of the first sample that did not hit the cap
           (the last one's if all did), and the tokens are those of every sample used. Each chain is averaged over all
           assignments of distinct stored samples to its stages. Stage names: think, m1, m2, m3, m4, rl.
  cap32    the M(2) run at cap 32,768: right, cap hits, tokens per problem, and the same answers counted at 16,384 (an
           answer longer than 16,384 tokens counts as a cap hit and as wrong, tokens 16,384).
"""
import argparse
import collections
import itertools
import json
import pathlib

STUDY = pathlib.Path(__file__).resolve().parents[1]
ARMS = {"think": "think", "rl": "rl", "m1": "sft1_rl10", "m2": "sft1_rl20", "m3": "sft1_rl30", "m4": "sft1_rl40"}
CHAINS = ["think", "m2", "think>think", "think>think>think", "m2>m2", "m2>m2>m2", "think>m2", "m2>m3", "m2>m4", "m2>rl",
          "m2>m3>m4", "think>m2>m4", "m1>m2>m3>m4"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--cap32", required=True)
    a = ap.parse_args()
    out = STUDY / "results" / "transplant" / a.run
    out.mkdir(parents=True)
    samples = collections.defaultdict(dict)   # (arm, sample or seed of the cell) -> problem -> row
    for f in ("hard328-01", "hard328-02"):
        for r in map(json.loads, open(STUDY / "results" / "transplant" / f / "rows.jsonl")):
            samples[(r["arm"], r["seed"] - r["problem_index"])][r["problem_index"]] = r
    by_arm = collections.defaultdict(list)
    for (arm, s), rows in sorted(samples.items()):
        assert len(rows) == 328, (arm, s)
        by_arm[arm].append(rows)
    problems = sorted(by_arm["think"][0])
    ro = {"run": a.run, "samples": {k: len(by_arm[v]) for k, v in ARMS.items()}, "chains": {}}
    for chain in CHAINS:
        stages = chain.split(">")
        res = []
        for pick in itertools.product(*(range(len(by_arm[ARMS[s]])) for s in stages)):
            if len({(s, i) for s, i in zip(stages, pick)}) < len(stages):
                continue
            right = cap = tok = 0
            for p in problems:
                for k, (s, i) in enumerate(zip(stages, pick)):
                    r = by_arm[ARMS[s]][i][p]
                    tok += r["n_new"]
                    if not r["cap_hit"]:
                        break
                right, cap = right + r["score_v3"], cap + r["cap_hit"]
            res.append((right, cap, tok / len(problems)))
        ro["chains"][chain] = {"assignments": len(res), "right": sum(r[0] for r in res) / len(res), "right_min": min(r[0] for r in res),
                               "right_max": max(r[0] for r in res), "cap_hits": sum(r[1] for r in res) / len(res),
                               "tokens_per_problem": sum(r[2] for r in res) / len(res)}
    d = pathlib.Path(a.cap32)
    m = json.loads((d / "metrics.json").read_text())
    assert m["status"] == "done" and m["config"]["max_tokens"] == 32768
    rows = [r for r in map(json.loads, open(d / "answers.jsonl")) if r.get("attempt", 0) == 0]
    assert sorted(r["problem_index"] for r in rows) == problems
    late = [r for r in rows if r["n_new"] > 16384]
    ro["cap32"] = {"job": d.parent.name, "seed": m["config"]["seed"], "commit": m["config"]["commit"], "n": len(rows),
                   "right": sum(r["score_v3"] for r in rows), "cap_hits": sum(r["cap_hit"] for r in rows),
                   "tokens_per_problem": sum(r["n_new"] for r in rows) / len(rows),
                   "answers_past_16384": len(late), "right_past_16384": sum(r["score_v3"] for r in late),
                   "at_16384": {"right": sum(r["score_v3"] for r in rows if r["n_new"] <= 16384), "cap_hits": len(late),
                                "tokens_per_problem": sum(min(r["n_new"], 16384) for r in rows) / len(rows)}}
    fin = sorted((r for r in late if not r["cap_hit"]), key=lambda r: r["n_new"])
    ex = {k: next(({f: r[f] for f in ("problem_index", "seed", "prompt", "text", "extracted_v3", "gold", "score_v3", "n_new")}
                   for r in fin if r["score_v3"] == v), None) for k, v in (("right", 1), ("wrong", 0))}
    slim = [{k: r[k] for k in ("problem_index", "seed", "n_new", "cap_hit", "loop_A", "extracted_v3", "score_v3", "gold")} for r in rows]
    (out / "metrics.json").write_text(json.dumps(m, indent=1))
    (out / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in slim))
    (out / "examples.json").write_text(json.dumps(ex, indent=1))
    (out / "readout.json").write_text(json.dumps(ro, indent=1))
    print(json.dumps(ro, indent=1))


if __name__ == "__main__":
    main()
