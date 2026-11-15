"""Problem dependence of the early answer text against right/wrong (specs/SPEC_probdep.md).

    uv run --no-project --with numpy --with scikit-learn python -m studies.rlneurons.analysis.probdep <job-id>

Run from the repository root. Input (not committed): runs/<job-id>/ of jobs/probdep_tokens.py. Writes
results/wrongstep/probdep-02/ (metrics.json, examples.json, run.json). d_t = lp_base - lp_noprob per answer token. Within-problem
AUROC of right against wrong as in analysis/critic_probe.py (pairs inside a problem, bootstrap over problems).
"""
import json
import pathlib
import sys

import numpy as np

from studies.rlneurons.analysis.critic_probe import within_auroc

STUDY = pathlib.Path(__file__).resolve().parents[1]
OUT = STUDY / "results" / "wrongstep" / "probdep-02"   # -01: examples held two right samples and no feature without the first 50 tokens
KS = (250, 500, 1000)


def main():
    job = sys.argv[1]
    run = pathlib.Path("runs") / job
    m = json.loads((run / "metrics.json").read_text())
    assert m["status"] == "done" and m["answers"] == 2000, m
    index = json.loads((run / "index.json").read_text())
    base, noprob = np.load(run / "base.npz")["lp_tok"], np.load(run / "noprob.npz")["lp_tok"]
    d = base - noprob
    y = np.array([r["score_v3"] for r in index])
    prob = np.array([r["problem_index"] for r in index])
    n_new = np.array([r["n_new"] for r in index], dtype=float)
    rng = np.random.default_rng(0)
    res = {"job": job, "answers": len(index), "right": int(y.sum()), "mean_d_nats_per_token": float(d.mean()), "features": {}}
    feats = {}
    for k in KS:
        seg = [slice(r["offset"], r["offset"] + min(k, r["length"])) for r in index]
        feats[f"mean_d_{k}"] = np.array([d[s].mean() for s in seg])
        feats[f"share_negative_{k}"] = -np.array([(d[s] < 0).mean() for s in seg])
        feats[f"low_decile_mean_{k}"] = np.array([np.sort(d[s])[: max(1, (s.stop - s.start) // 10)].mean() for s in seg])
        feats[f"mean_lp_base_{k}"] = np.array([base[s].mean() for s in seg])
        feats[f"mean_lp_noprob_{k}"] = np.array([noprob[s].mean() for s in seg])
    feats["shorter_answer"] = -n_new
    feats["mean_d_50_to_1000"] = np.array([d[r["offset"] + 50: r["offset"] + r["length"]].mean() if r["length"] > 50 else 0.0 for r in index])
    sh = feats["mean_d_1000"].copy()
    for p in np.unique(prob):
        i = np.where(prob == p)[0]
        sh[i] = sh[rng.permutation(i)]
    feats["mean_d_1000_shuffled_within_problem"] = sh
    for name, s in feats.items():
        res["features"][name] = within_auroc(s, y, prob, rng)
    long = n_new > 1000
    res["features"]["mean_d_1000_both_longer_than_1000"] = within_auroc(feats["mean_d_1000"][long], y[long], prob[long], rng)
    res["features"]["shorter_answer_both_longer_than_1000"] = within_auroc(-n_new[long], y[long], prob[long], rng)
    labels = {(x["problem_index"], x["sample"]): x["passA"]["label"] for x in json.loads((STUDY / "results" / "anatomy" / "judge-01" / "labels.json").read_text()) if x["kind"] == "base"}
    by = {}
    for i, r in enumerate(index):
        lab = labels.get((r["problem_index"], r["sample"]))
        if lab:
            by.setdefault(lab, []).append(float(feats["mean_d_1000"][i]))
    res["judged_wrong_mean_d_1000"] = {k: {"n": len(v), "mean": float(np.mean(v))} for k, v in by.items()}
    res["mean_d_1000"] = {"right": float(feats["mean_d_1000"][y == 1].mean()), "wrong": float(feats["mean_d_1000"][y == 0].mean())}
    order = np.argsort(feats["mean_d_1000"])                                  # the lowest-d right sample and the lowest-d wrong sample
    ex = [{**index[i], "mean_d_1000": float(feats["mean_d_1000"][i])} for i in (next(j for j in order if y[j] == 1), next(j for j in order if y[j] == 0))]
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(res, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    (OUT / "run.json").write_text(json.dumps({"command": "python -m studies.rlneurons.analysis.probdep " + job, "job": job, "job_metrics": m}, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
