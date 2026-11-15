"""Critic at decoding time, stage 1 readout and offline policy test (specs/SPEC_critic.md).

    uv run --no-project --with numpy --with scikit-learn --with math-verify==0.9.0 python -m studies.rlneurons.analysis.critic_probe <job-id>

Run from the repository root. Input (not committed): runs/<job-id>/ of jobs/critic_acts.py (`uv run tools/gpu.py get <job-id>`).
Writes results/critic/probe-02/ (metrics.json, examples.json, run.json). probe-01 used a flag that compared answer strings
(see critic_ceiling.plurality_flags) and C in (0.001, 0.01, 0.1).

Probe: logistic regression on standardized activations of one layer at one checkpoint, 5 folds by problem (problem index mod 5),
C chosen among 3 values by an inner split of the training problems. Trained on the label-free flag (the sample finished and its
answer is the most common answer among the problem's finished samples); scored against that flag and against correctness.
Within-problem AUROC: over the problems with both outcomes among the samples that reach the checkpoint, the share of
(good, bad) sample pairs ordered correctly, ties 0.5; interval by bootstrap over problems (2,000 resamples, seed 0).
"""
from __future__ import annotations

import collections
import itertools
import json
import pathlib
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression

from studies.rlneurons.analysis.critic_ceiling import plurality_flags

RUNS = pathlib.Path("runs")
OUT = pathlib.Path(__file__).resolve().parents[1] / "results" / "critic" / "probe-02"
CS = (0.0001, 0.001, 0.01)


def pairs_by_problem(score, y, prob):
    """Per problem with both outcomes: (pairs ordered correctly, pairs)."""
    out = {}
    for p in np.unique(prob):
        m = prob == p
        g, b = score[m][y[m] == 1], score[m][y[m] == 0]
        if len(g) and len(b):
            d = g[:, None] - b[None, :]
            out[int(p)] = (float((d > 0).sum() + 0.5 * (d == 0).sum()), d.size)
    return out


def within_auroc(score, y, prob, rng):
    pp = pairs_by_problem(score, y, prob)
    w = np.array(list(pp.values()))
    if not len(w):
        return None
    boots = [w[rng.integers(0, len(w), len(w))].sum(0) for _ in range(2000)]
    v = [b[0] / b[1] for b in boots]
    return {"value": round(float(w[:, 0].sum() / w[:, 1].sum()), 4), "ci95": [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)],
            "problems": len(w), "pairs": int(w[:, 1].sum())}


def pooled_auroc(score, y):
    g, b = score[y == 1], score[y == 0]
    order = np.argsort(np.concatenate([g, b]), kind="stable")
    ranks = np.empty(len(order))
    ranks[order] = np.arange(1, len(order) + 1)
    return round(float((ranks[: len(g)].sum() - len(g) * (len(g) + 1) / 2) / (len(g) * len(b))), 4)


def fit_predict(x, y, prob):
    """Held-out decision values, 5 folds by problem."""
    out = np.zeros(len(y))
    for f in range(5):
        tr, te = prob % 5 != f, prob % 5 == f
        mu, sd = x[tr].mean(0), x[tr].std(0) + 1e-6
        xtr, xte = (x[tr] - mu) / sd, (x[te] - mu) / sd
        inner = prob[tr] % 3 == 0                                              # inner split of the training problems, by problem
        best = max(CS, key=lambda c: pooled_auroc(LogisticRegression(C=c, max_iter=300).fit(xtr[~inner], y[tr][~inner]).decision_function(xtr[inner]), y[tr][inner]))
        out[te] = LogisticRegression(C=best, max_iter=300).fit(xtr, y[tr]).decision_function(xte)
    return out


def policy(score, thr, idx):
    """Stop-and-restart on stored samples: sample s of a problem is stopped at 1,000 tokens if it is that long and score < thr."""
    by = collections.defaultdict(dict)
    for i, x in enumerate(idx):
        by[x["problem_index"]][x["sample"]] = i
    right, tokens, n, stops = 0.0, 0.0, 0, 0
    per_problem = {}
    for p, ss in by.items():
        r_p, n_p = 0.0, 0
        for order in itertools.permutations(range(4)):
            n += 1; n_p += 1
            for j, s in enumerate(order):
                i = ss[s]
                long = idx[i]["n_tokens"] >= 1000
                if j == 3 or not long or score[i] >= thr:
                    right += idx[i]["score_v3"]; r_p += idx[i]["score_v3"]; tokens += idx[i]["n_tokens"]
                    break
                tokens += 1000; stops += 1
        per_problem[p] = r_p / n_p
    return {"right_of_500": round(500 * right / n, 1), "tokens_per_problem": round(tokens / n), "stops_per_problem": round(stops / n, 3)}, per_problem


def main():
    job = sys.argv[1]
    d = RUNS / job
    meta = json.loads((d / "metrics.json").read_text())
    assert meta["status"] == "done" and meta["samples"] == 2000, meta
    acts, feats, idx = np.load(d / "acts.npy", mmap_mode="r"), np.load(d / "feats.npy"), json.loads((d / "index.json").read_text())
    prob = np.array([x["problem_index"] for x in idx])
    ntok = np.array([x["n_tokens"] for x in idx])
    correct = np.array([x["score_v3"] for x in idx])
    flag = np.zeros(len(idx), dtype=int)
    for p in np.unique(prob):
        m = np.flatnonzero(prob == p)
        flag[m] = plurality_flags([idx[i] for i in m])
    rng = np.random.default_rng(0)
    res = {"job": job, "samples": len(idx), "flag_rate": round(float(flag.mean()), 4), "correct_rate": round(float(correct.mean()), 4), "checkpoints": {}}
    held = {}
    for c, t in enumerate(meta["checkpoints"]):
        m = ntok >= t
        row = {"samples_reaching": int(m.sum()), "flag_rate": round(float(flag[m].mean()), 4)}
        for name, col in (("mean_logprob", 0), ("mean_entropy", 1)):
            if t:
                s = feats[m, c, col] * (1 if col == 0 else -1)
                row[name] = {"within_flag": within_auroc(s, flag[m], prob[m], rng), "within_correct": within_auroc(s, correct[m], prob[m], rng),
                             "pooled_flag": pooled_auroc(s, flag[m])}
        for li, layer in enumerate(meta["layers"]):
            x = np.asarray(acts[m, c, li], dtype=np.float32)
            s = fit_predict(x, flag[m], prob[m])
            held[(t, layer)] = (m, s)
            row[f"probe_L{layer}"] = {"within_flag": within_auroc(s, flag[m], prob[m], rng), "within_correct": within_auroc(s, correct[m], prob[m], rng),
                                      "pooled_flag": pooled_auroc(s, flag[m]), "pooled_correct": pooled_auroc(s, correct[m])}
            if t:                                                              # upper bound: the same probe trained on the answer key
                row[f"probe_L{layer}"]["within_correct_trained_on_key"] = within_auroc(fit_predict(x, correct[m], prob[m]), correct[m], prob[m], rng)
            if t == 1000:                                                      # control: labels shuffled within problems
                sh = flag[m].copy()
                for p in np.unique(prob[m]):
                    q = np.flatnonzero(prob[m] == p)
                    sh[q] = sh[q][rng.permutation(len(q))]
                row[f"probe_L{layer}"]["within_flag_trained_on_shuffled"] = within_auroc(fit_predict(x, sh, prob[m]), flag[m], prob[m], rng)
        res["checkpoints"][str(t)] = row
        print(t, json.dumps(row)[:1500], flush=True)

    # offline policy at 1,000 tokens with the best layer by within-problem AUROC for the flag
    best = max(meta["layers"], key=lambda L: res["checkpoints"]["1000"][f"probe_L{L}"]["within_flag"]["value"])
    m, s = held[(1000, best)]
    score = np.full(len(idx), np.inf); score[m] = s
    pol = {"layer": best, "folds": {}}
    pp_probe, pp_rand = {}, {}
    rand = np.full(len(idx), np.inf); rand[m] = rng.permutation(s)             # the same scores given to random samples: same stop rate
    for f in range(5):
        tr = [i for i in range(len(idx)) if prob[i] % 5 != f]; te = [i for i in range(len(idx)) if prob[i] % 5 == f]
        cands = np.quantile(s, np.linspace(0.02, 0.6, 30))
        ok = []
        for thr in cands:
            r, _ = policy(score[tr], thr, [idx[i] for i in tr])
            base_tokens = np.mean([idx[i]["n_tokens"] for i in tr])
            if r["tokens_per_problem"] <= 1.3 * base_tokens:
                ok.append((r["right_of_500"], thr))
        thr = max(ok)[1]
        r, pp = policy(score[te], thr, [idx[i] for i in te]); rr, ppr = policy(rand[te], thr, [idx[i] for i in te])
        pol["folds"][f] = {"threshold": round(float(thr), 4), "probe": r, "random": rr}
        pp_probe.update(pp); pp_rand.update(ppr)
    ps = sorted(pp_probe)
    a, b = np.array([pp_probe[p] for p in ps]), np.array([pp_rand[p] for p in ps])
    single = np.array([np.mean([idx[i]["score_v3"] for i in np.flatnonzero(prob == p)]) for p in ps])
    bs = rng.integers(0, len(ps), (5000, len(ps)))
    def ci(x):
        v = x[bs].mean(1) * 100
        return [round(float(np.percentile(v, 2.5)), 2), round(float(np.percentile(v, 97.5)), 2)]
    pol["probe_right_of_500"] = round(float(a.sum()), 1); pol["random_right_of_500"] = round(float(b.sum()), 1); pol["single_right_of_500_mean_of_4"] = round(float(single.sum()), 1)
    pol["tokens_per_problem"] = {k: round(float(np.mean([pol["folds"][f][k]["tokens_per_problem"] for f in range(5)]))) for k in ("probe", "random")}
    pol["single_tokens_per_problem"] = round(float(ntok.mean()))
    pol["probe_minus_random_points"] = {"value": round(float((a - b).mean() * 100), 2), "ci95": ci(a - b)}
    pol["probe_minus_single_points"] = {"value": round(float((a - single).mean() * 100), 2), "ci95": ci(a - single)}
    res["policy_at_1000_tokens"] = pol
    print(json.dumps(pol, indent=1))

    # one pair ordered right and one ordered wrong by the probe, with their real fields
    ex = []
    for want in (True, False):
        for p in np.unique(prob[m]):
            q = np.flatnonzero(m & (prob == p))
            g, b_ = q[flag[q] == 1], q[flag[q] == 0]
            if len(g) and len(b_) and (score[g[0]] > score[b_[0]]) == want:
                ex.append({"ordered_right": want, "good": idx[g[0]] | {"probe_score": round(float(score[g[0]]), 3)}, "bad": idx[b_[0]] | {"probe_score": round(float(score[b_[0]]), 3)}})
                break
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(res, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    (OUT / "run.json").write_text(json.dumps({"job": job, "command": f"python -m studies.rlneurons.analysis.critic_probe {job}", "raw": f"runs/{job}/ (uv run tools/gpu.py get {job})"}, indent=1) + "\n")


if __name__ == "__main__":
    main()
