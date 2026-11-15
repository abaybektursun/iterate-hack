"""One scored cell: a model (the base or a saved checkpoint), plain or cued prompt, one problem set, on Tinker.

    python -m studies.tinkerpair.jobs.eval_cell --out stage1/base_plain-01 --set math500 [--cue] [--model-path tinker://...]
        [--cap 16384] [--samples 1] [--seed 1000000] [--n 500]

Writes results/<out>/run.json, metrics.json, per_problem.json, examples.json and runs/tinkerpair/<out>/rows.jsonl (the
texts, not committed). Grader v3. With --derange the golds are shifted by one problem: the grader's negative control.
"""
import argparse
import json

import tinker

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R
from studies.tinkerpair.lib import tk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--set", required=True, choices=["math500", "hard328"])
    ap.add_argument("--cue", action="store_true")
    ap.add_argument("--model-path")
    ap.add_argument("--cap", type=int, default=16384)
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1_000_000)
    ap.add_argument("--n", type=int)
    ap.add_argument("--derange", action="store_true")
    a = ap.parse_args()

    items = tk.load_set(a.set)[:a.n]
    golds = [it["answer"] for it in items]
    if a.derange:
        golds = golds[1:] + golds[:1]
    res, raw = tk.new_run_dir(a.out)
    service = tinker.ServiceClient()
    client = tk.sampler(service, a.model_path)
    tok = client.get_tokenizer()
    rec = tk.run_record({"set": a.set, "cue": a.cue, "model_path": a.model_path, "cap": a.cap, "samples": a.samples,
                         "seed": a.seed, "n": len(items), "derange": a.derange, "grader": "v3",
                         "raw_answers": f"runs/tinkerpair/{a.out}/rows.jsonl (submitter's laptop)"})
    tk.dump(f"{res}/run.json", rec)

    outs = tk.sample(client, tok, [tk.prompt_ids(tok, it["problem"], a.cue) for it in items], a.samples, a.cap, a.seed)
    rows = []
    with open(f"{raw}/rows.jsonl", "w") as f:
        for it, gold, seqs in zip(items, golds, outs):
            for k, s in enumerate(seqs):
                text = tk.answer_text(s["text"], a.cue)
                g = R.grade_v3(gold, text)
                row = {"index": it["index"], "sample": k, "score": g["score_v3"], "extracted": g["extracted_v3"],
                       "tokens": len(s["tokens"]), "cap": s["cap"], "opening": s["text"][:24]}
                rows.append(row)
                f.write(json.dumps({**row, "problem": it["problem"], "gold": gold, "text": text}) + "\n")

    right, n = sum(r["score"] for r in rows), len(rows)
    tk.dump(f"{res}/metrics.json", {
        "right": right, "n": n, "accuracy_pct": 100 * right / n, "wilson95_pct": S.wilson(right, n),
        "cap_hits": sum(r["cap"] for r in rows), "no_answer": sum(r["extracted"] is None for r in rows),
        "tokens_per_answer": sum(r["tokens"] for r in rows) / n, "sampled_tokens": sum(r["tokens"] for r in rows)})
    tk.dump(f"{res}/per_problem.json", rows)
    full = [json.loads(line) for line in open(f"{raw}/rows.jsonl")]
    tk.dump(f"{res}/examples.json", {"right": next((r for r in full if r["score"] == 1), None),
                                     "wrong": next((r for r in full if r["score"] == 0), None)})
    print(json.dumps(json.load(open(f"{res}/metrics.json"))))


if __name__ == "__main__":
    main()
