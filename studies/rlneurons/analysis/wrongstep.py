"""Do the RL models make the base's own wrong steps less likely? Readout (specs/SPEC_wrongstep.md).

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.wrongstep <job-id>

Run from the repository root. Input (not committed): runs/<job-id>/ of `jobs/score_tokens.py --labels ...` (`uv run tools/gpu.py
get <job-id>`). Writes results/wrongstep/math500-01/ (metrics.json, items.json, run.json).
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

import numpy as np

RUNS = pathlib.Path("runs")
OUT = pathlib.Path(__file__).resolve().parents[1] / "results" / "wrongstep" / "math500-01"
N_CONTROL, HEAD = 200, 5


def main():
    job = sys.argv[1]
    d = RUNS / job
    meta = json.loads((d / "metrics.json").read_text())
    assert meta["status"] == "done", meta.get("status")
    index = json.loads((d / "index.json").read_text())
    lp = {m: np.load(d / f"{m}.npz")["lp_tok"].astype(np.float64) for m in meta["models"]}
    cs = {m: np.concatenate([[0.0], np.cumsum(v)]) for m, v in lp.items()}       # prefix sums over all positions
    rng = np.random.default_rng(0)
    items = []
    for x in index:
        w = x["wrong_step"]
        n_ans = x["length"] - (0 if x["cap_hit"] else 1)                         # without the stop id
        if not w["found"]:
            continue
        s, e = w["tok_start"], w["tok_end"]
        L = e - s
        starts = np.array([k for k in range(0, n_ans - L + 1) if k + L <= s or k >= e])
        if len(starts) < 20:
            continue
        ctrl = rng.choice(starts, N_CONTROL)
        o = x["offset"]
        it = {"problem_index": x["problem_index"], "sample": x["sample"], "label": w["label"], "whole_quote": w["whole_quote"], "span_tokens": L,
              "position": round(s / n_ans, 3), "quote": w["quote"][:160], "models": {}}

        def tot(m, a, b):
            return cs[m][o + b] - cs[m][o + a]

        for m in lp:
            span, c = tot(m, s, e), np.array([tot(m, k, k + L) for k in ctrl])
            head, ch = tot(m, s, min(e, s + HEAD)), np.array([tot(m, k, k + min(L, HEAD)) for k in ctrl])
            it["models"][m] = {"lp_span": span, "lp_control": float(c.mean()), "lp_head": head, "lp_head_control": float(ch.mean())}
        items.append(it)
    n = len(items)
    bs = rng.integers(0, n, (5000, n))

    def stat(v):
        v = np.asarray(v)
        b = v[bs].mean(1)
        return {"mean": round(float(v.mean()), 3), "ci95": [round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)],
                "median": round(float(np.median(v)), 3), "share_below_0": round(float((v < 0).mean()), 3)}

    def D(m, it, key="lp_span", ckey="lp_control"):
        a, b = it["models"][m], it["models"]["base"]
        return (a[key] - b[key]) - (a[ckey] - b[ckey])

    res = {"job": job, "items": n, "items_in_job": len(index), "wrong_steps_found": meta["wrong_steps_found"],
           "labels": dict(collections.Counter(it["label"] for it in items)),
           "span_tokens_median": float(np.median([it["span_tokens"] for it in items])), "position_median": float(np.median([it["position"] for it in items])),
           "base_logprob_span_minus_control": stat([it["models"]["base"]["lp_span"] - it["models"]["base"]["lp_control"] for it in items]),
           "base_logprob_per_token_span": round(float(np.mean([it["models"]["base"]["lp_span"] / it["span_tokens"] for it in items])), 3),
           "base_logprob_per_token_control": round(float(np.mean([it["models"]["base"]["lp_control"] / it["span_tokens"] for it in items])), 3),
           "D": {}}
    for m in lp:
        if m == "base":
            continue
        row = {"all": stat([D(m, it) for it in items]), "head_5_tokens": stat([D(m, it, "lp_head", "lp_head_control") for it in items]),
               "control_r_per_span": round(float(np.mean([it["models"][m]["lp_control"] - it["models"]["base"]["lp_control"] for it in items])), 3)}
        row["factor"] = round(float(np.exp(row["all"]["mean"])), 3)
        for lab in ("slip", "wrong_plan", "misread", "format"):
            v = [D(m, it) for it in items if it["label"] == lab]
            row[lab] = {"n": len(v), "mean": round(float(np.mean(v)), 3)}
        res["D"][m] = row
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(res, indent=1) + "\n")
    (OUT / "items.json").write_text(json.dumps(items, indent=1) + "\n")
    (OUT / "run.json").write_text(json.dumps({"job": job, "command": f"python -m studies.rlneurons.analysis.wrongstep {job}", "raw": f"runs/{job}/ (uv run tools/gpu.py get {job})"}, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "D"}, indent=1))
    for m, row in res["D"].items():
        print(f"{m:10s} D {row['all']['mean']:7.3f} {row['all']['ci95']} median {row['all']['median']:6.3f} below0 {row['all']['share_below_0']:.2f} factor {row['factor']:.2f} | head5 {row['head_5_tokens']['mean']:6.3f} {row['head_5_tokens']['ci95']} | control r {row['control_r_per_span']:6.3f} | " + " ".join(f"{l} {row[l]['mean']:.2f}" for l in ('slip', 'wrong_plan', 'misread', 'format')))


if __name__ == "__main__":
    main()
