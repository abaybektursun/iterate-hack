"""Log-probability the model gives to the cue opening by itself, after each MATH-500 prompt.

    python -m studies.tinkerpair.jobs.cue_logprob --out cue_logprob/base-01 [--model-path tinker://...] [--n 500]

For every problem: the summed log-probability of the cue's tokens placed after the plain prompt (compute_logprobs on
prompt + cue, last len(cue) positions). Writes results/<out>/run.json, metrics.json (mean, median, per token) and
per_problem.json.
"""
import argparse
import statistics

import tinker
from tinker import types

from studies.tinkerpair.lib import tk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--model-path")
    ap.add_argument("--n", type=int)
    a = ap.parse_args()
    items = tk.load_set("math500")[:a.n]
    res, _ = tk.new_run_dir(a.out)
    client = tk.sampler(tinker.ServiceClient(), a.model_path)
    tok = client.get_tokenizer()
    cue = tok.encode(tk.CUE, add_special_tokens=False)
    tk.dump(f"{res}/run.json", tk.run_record({"model_path": a.model_path, "n": len(items), "cue_ids": cue,
                                               "cue_tokens": [tok.decode([i]) for i in cue]}))
    futs = [client.compute_logprobs(types.ModelInput.from_ints(tk.prompt_ids(tok, it["problem"], True)), prompt_logprobs_last_n=len(cue))
            for it in items]
    rows = []
    for it, f in zip(items, futs):
        lp = f.result()[-len(cue):]
        assert len(lp) == len(cue) and all(x is not None for x in lp), lp
        rows.append({"index": it["index"], "logprobs": lp, "sum": sum(lp)})
    sums = [r["sum"] for r in rows]
    tk.dump(f"{res}/metrics.json", {"n": len(rows), "mean_sum_logprob": statistics.fmean(sums), "median_sum_logprob": statistics.median(sums),
                                    "mean_logprob_per_token": [statistics.fmean(r["logprobs"][j] for r in rows) for j in range(len(cue))]})
    tk.dump(f"{res}/per_problem.json", rows)
    print(open(f"{res}/metrics.json").read())


if __name__ == "__main__":
    main()
