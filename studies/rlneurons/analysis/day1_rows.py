"""Day-1 rows from jobs/run_cell.py: one run folder per job and one readout.

  python -m studies.rlneurons.analysis.day1_rows --runs <dir holding <job-id>/answers.jsonl, metrics.json> \
      --out studies/rlneurons/results/day1 <folder>=<job-id> ...

For each <folder>=<job-id> it writes <out>/<folder>/ (refuses an existing folder): run.json (commit, command, job id),
metrics.json (the job's own file) and examples.json (the real prompt, answer and scores of one problem scored right, one
scored wrong and one cap hit, grader v3). <out>/readout.json holds per row: right with v3 and v1, Wilson 95 % interval,
cap hits, rule-A loops, generated tokens per problem, tokens per second; for hard328 the RL minus base-with-cue paired
difference (paired bootstrap, 5,000 resamples, seed 0); for the MATH-500 cue row at T 0.6 / top-p 1.0 the unpaired
differences against the two cue rows of results/rln4/grader_v3/readout.json (only their totals are in the repository).
"""
import argparse
import json
import math
import pathlib

from studies.rlneurons.lib.n13_score import mcnemar, paired_bootstrap, wilson

HERE = pathlib.Path(__file__).resolve().parents[1]
COMMAND = ("bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell "
           "--model {model} --prompt {prompt} --set {set} --temperature {temperature} --top-p {top_p} --seed {seed}{n} "
           "--commit {commit}")


def example(r):
    return {k: r[k] for k in ("problem_index", "unique_id", "seed", "prompt", "text", "gold", "extracted", "score",
                              "extracted_v3", "mode_v3", "score_v3", "n_generated", "cap_hit", "finish_reason", "loop_A")}


def unpaired(k1, n1, k2, n2):
    """Difference of two proportions in points with a normal 95 % interval that treats the rows as independent."""
    p1, p2 = k1 / n1, k2 / n2
    h = 1.959964 * math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return {"diff_points": 100 * (p1 - p2), "ci95_unpaired": [100 * (p1 - p2 - h), 100 * (p1 - p2 + h)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("cells", nargs="+")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    readout, vec = {"grader": "v3", "rows": {}, "differences_v3": {}}, {}
    for cell in a.cells:
        name, job = cell.split("=")
        src = pathlib.Path(a.runs) / job
        m = json.loads((src / "metrics.json").read_text())
        rows = sorted((json.loads(l) for l in (src / "answers.jsonl").read_text().splitlines()), key=lambda r: r["problem_index"])
        c, n = m["config"], len(rows)
        assert m["status"] == "done" and n == m["counts"]["n_planned"], (job, m["status"], n)
        assert len({r["problem_index"] for r in rows}) == n
        right = sum(r["score_v3"] for r in rows)
        assert right == m["counts"]["correct_v3"]
        caps = [r for r in rows if r["cap_hit"]]
        gen = [r["n_generated"] for r in rows]
        readout["rows"][name] = {
            "job_id": job, "commit": m["commit"], "model": c["model"], "prompt": c["prompt"], "set": c["set"],
            "temperature": c["temperature"], "top_p": c["top_p"], "seed": c["seed"], "n": n,
            "right_v3": right, "percent_v3": 100 * right / n, "wilson95_v3": list(wilson(right, n)),
            "right_v1": sum(r["score"] for r in rows), "nothing_extracted_v3": sum(r["mode_v3"] == "none" for r in rows),
            "cap_hits": len(caps), "cap_hits_right_v3": sum(r["score_v3"] for r in caps),
            "loops_A": sum(bool(r["loop_A"]) for r in rows), "loops_A_among_cap_hits": sum(bool(r["loop_A"]) for r in caps),
            "mean_generated_tokens": sum(gen) / n, "median_generated_tokens": sorted(gen)[n // 2],
            "generated_tokens": sum(gen), "generation_s": m["counts"]["generation_s"],
            "tokens_per_s": m["counts"]["tokens_per_s"], "wall_s": m["wall_s"], "gpu": m["memory"]["gpu"]}
        vec[name] = {r["problem_index"]: r["score_v3"] for r in rows}
        d = out / name
        d.mkdir(parents=True)                      # fails on an existing run folder
        (d / "metrics.json").write_text(json.dumps(m, indent=1))
        (d / "run.json").write_text(json.dumps({
            "job_id": job, "commit": m["commit"], "runner": "tools/gpu.py submit h100",
            "command": COMMAND.format(n=f" --n {c['n']}" if c.get("n") else "", commit=m["commit"],
                                      **{k: c[k] for k in ("model", "prompt", "set", "temperature", "top_p", "seed")}),
            "raw_answers": f"runs/{job}/answers.jsonl after `uv run tools/gpu.py get {job}` (the submitter's Modal workspace)",
            "started_utc": m["started_utc"], "updated_utc": m["updated_utc"]}, indent=1))
        ex = {"right_v3": example(next(r for r in rows if r["score_v3"])),
              "wrong_v3": example(next(r for r in rows if not r["score_v3"] and not r["cap_hit"]))}
        if caps:
            ex["cap_hit"] = example(caps[0])
            ex["cap_hit"]["text"] = ex["cap_hit"]["text"][:2000] + "\n[... cut ...]\n" + ex["cap_hit"]["text"][-2000:]
        (d / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False))

    hard = sorted(k for k in vec if k.startswith("hard328"))
    rl, base = [k for k in hard if "_rl_" in k], [k for k in hard if "_base_" in k]
    if rl and base:
        idx = sorted(vec[rl[0]])
        assert idx == sorted(vec[base[0]])
        x, y = [vec[rl[0]][i] for i in idx], [vec[base[0]][i] for i in idx]
        readout["differences_v3"][f"{rl[0]} - {base[0]}"] = {
            "n": len(idx), "diff_points": 100 * (sum(x) - sum(y)) / len(idx),
            "ci95": list(paired_bootstrap(x, y, n_boot=5000, seed=0)),
            "both_right": sum(p and q for p, q in zip(x, y)), "rl_only": sum(p and not q for p, q in zip(x, y)),
            "base_only": sum(q and not p for p, q in zip(x, y)), "neither": sum(not p and not q for p, q in zip(x, y)),
            "mcnemar": mcnemar(x, y)}
    old = json.loads((HERE / "results/rln4/grader_v3/readout.json").read_text())["cells"]
    for name, r in readout["rows"].items():
        if (r["set"], r["model"], r["prompt"], r["temperature"], r["top_p"]) == ("math500", "base", "cue", 0.6, 1.0):
            for other in ("base_opener_0.6", "base_opener_1.0"):
                readout["differences_v3"][f"{name} - {other}"] = {
                    "n": r["n"], "other_right_v3": old[other]["right_v3"], "other_cap_hits": old[other]["cap_hits"],
                    **unpaired(r["right_v3"], r["n"], old[other]["right_v3"], old[other]["n"]),
                    "note": "unpaired: per-problem scores of the other row are not in the repository"}
    (out / "readout.json").write_text(json.dumps(readout, indent=1))
    print(json.dumps(readout, indent=1))


if __name__ == "__main__":
    main()
