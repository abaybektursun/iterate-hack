"""Readout of the lens-diff job (specs/SPEC1_lensdiff.md): reads runs/<job-id>/ of jobs/lensdiff.py and writes metrics.json and
examples.json.

    PYTHONPATH=. python3 -m studies.jspace.analysis.lensdiff_analyze runs/<job-id> --map <RLN-5 map run folder> --out <result folder>

Needs numpy only. `--map` is the $OUT_DIR of studies/rlneurons/jobs/rln5_map.py (job sameraslan-1114-135831-c3ec); its rows
must hold the same written tokens (asserted). Presence of a token at a position: it is among the top K word-like tokens of the
fixed readout. All intervals are 95 % percentile intervals of a bootstrap over problems (2,000 resamples). Only generated
positions (kind 1) enter the per-position analyses. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np

STUDY = pathlib.Path(__file__).resolve().parents[1]
ITEMS = STUDY.parent / "rlneurons" / "results" / "rln4" / "t1_t2_items-01" / "per_problem.json"
RNG = np.random.default_rng(0)
B = 2000
HOLD = (" Wait", "Wait", " wait", " Hmm", "Hmm", " hmm")            # the hold-on family, fixed after the smoke run (SPEC1 §Deviations)
WRAP = ("<|endoftext|>", " Answer", "Answer", " So", ".The")        # the wrap-up family, same
MAXLAG = 32


def load_rows(run, cell, arrays):
    index = json.loads((run / "index.json").read_text())
    rows = {}
    for sh in index["shards"]:
        if sh["cell"] != cell:
            continue
        z = np.load(run / sh["file"])
        off = z["offsets"]
        keep = {k: z[k] for k in arrays}
        for r, pi in enumerate(z["problem_index"]):
            rows[int(pi)] = {k: v[off[r]:off[r + 1]] for k, v in keep.items()}
    return rows


def boot_diff(ca, cb, n):
    """Pooled rate difference sum(ca)/sum(n) - sum(cb)/sum(n) over problems, with its bootstrap interval."""
    ca, cb, n = (np.asarray(v, dtype=np.float64) for v in (ca, cb, n))
    pick = RNG.integers(0, len(n), size=(B, len(n)))
    d = (ca[pick].sum(1) - cb[pick].sum(1)) / n[pick].sum(1)
    return {"rate_a": float(ca.sum() / n.sum()), "rate_b": float(cb.sum() / n.sum()), "diff": float((ca.sum() - cb.sum()) / n.sum()),
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))], "problems": int(len(n))}


def boot_dd(c1a, c1b, n1, c2a, c2b, n2):
    """(group 1 difference) minus (group 2 difference), problems resampled within each group."""
    a = [np.asarray(v, dtype=np.float64) for v in (c1a, c1b, n1)]
    b = [np.asarray(v, dtype=np.float64) for v in (c2a, c2b, n2)]
    p1, p2 = RNG.integers(0, len(a[2]), size=(B, len(a[2]))), RNG.integers(0, len(b[2]), size=(B, len(b[2])))
    d = (a[0][p1].sum(1) - a[1][p1].sum(1)) / a[2][p1].sum(1) - (b[0][p2].sum(1) - b[1][p2].sum(1)) / b[2][p2].sum(1)
    point = (a[0].sum() - a[1].sum()) / a[2].sum() - (b[0].sum() - b[1].sum()) / b[2].sum()
    return {"diff_of_diffs": float(point), "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--map", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--top", type=int, default=30)
    a = ap.parse_args()
    run, mp, out = pathlib.Path(a.run), pathlib.Path(a.map), pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    vocab = json.loads((run / "vocab.json").read_text())
    index = json.loads((run / "index.json").read_text())
    checks = json.loads((run / "checks.json").read_text())
    jm = json.loads((run / "metrics.json").read_text())
    assert jm["status"] == "done"
    group = {int(p["problem_index"]): p for p in json.loads(ITEMS.read_text())}
    K, store, W = index["k"], index["store_layers"], index["watch"]

    def tid(s):
        hits = [i for i, v in enumerate(vocab) if v == s]
        assert len(hits) == 1, (s, hits)
        return hits[0]

    hold, wrap = [tid(s) for s in HOLD], [tid(s) for s in WRAP]
    res = {"job_id": jm["job_id"], "commit": jm["commit"], "lens": jm["lens"], "k": K, "store_layers": store,
           "positions": jm["positions"], "n_pos": jm["n_pos"], "families": {"hold_on": list(HOLD), "wrap_up": list(WRAP)},
           "checks": {"plumbing": checks["plumbing"], "hit": checks["hit"]}}

    # a. vocabulary diff from the aggregates, every layer (exploratory)
    z = np.load(run / "agg.npz")
    cells, groups, layers = [str(x) for x in z["cells"]], [str(x) for x in z["groups"]], [int(x) for x in z["layers"]]
    pres, npos = z["presence"].astype(np.float64), z["n_pos"].astype(np.float64)
    res["a_vocab_diff"] = {}
    cand = {}
    for ci, c in enumerate(cells):
        for li, l in enumerate(layers):
            b, r = pres[ci, :, 0, li].sum(0) / npos[ci].sum(), pres[ci, :, 1, li].sum(0) / npos[ci].sum()
            d = r - b
            up, dn = np.argsort(-d)[:a.top], np.argsort(d)[:a.top]
            row = lambda i: {"token": vocab[i], "id": int(i), "base": float(b[i]), "rl": float(r[i]), "diff": float(d[i])}
            res["a_vocab_diff"][f"{c}_L{l}"] = {"rl_more": [row(i) for i in up], "base_more": [row(i) for i in dn]}
            if l in store:
                cand[(c, l)] = [int(i) for i in up] + [int(i) for i in dn]
            fam = lambda ids: {"base": float(b[ids].sum()), "rl": float(r[ids].sum())}
            res["a_vocab_diff"][f"{c}_L{l}"]["families"] = {"hold_on": fam(hold), "wrap_up": fam(wrap)}

    # per-problem counts at the stored layers
    arrays = ["tok", "kind"] + [f"{k}_{m}_{l}" for k in ("top", "watch") for m in ("base", "rl") for l in store]
    rows = {c: load_rows(run, c, arrays) for c in cells}
    maprows = {c: load_rows(mp, c, ["tok", "top1_base", "top1_rl", "kl_base_rl", "kl_rl_base"]) for c in cells}
    for c in cells:
        for pi, r in rows[c].items():
            assert np.array_equal(r["tok"], maprows[c][pi]["tok"]), ("map rows differ", c, pi)
    res["rows"] = {c: len(rows[c]) for c in cells}

    def counts(c, l, ids):
        """[problems, 2 models, len(ids)] presence counts over generated positions, and positions per problem."""
        lut = np.full(len(vocab), -1, dtype=np.int64)
        lut[ids] = np.arange(len(ids))
        pis = sorted(rows[c])
        cnt, n = np.zeros((len(pis), 2, len(ids))), np.zeros(len(pis))
        for k, pi in enumerate(pis):
            g = rows[c][pi]["kind"] == 1
            n[k] = g.sum()
            for mi, m in enumerate(("base", "rl")):
                v = lut[rows[c][pi][f"top_{m}_{l}"][g]]
                cnt[k, mi] = np.bincount(v[v >= 0], minlength=len(ids))
        return pis, cnt, n

    # b. H1: watch tokens, the two families and the candidates of part a, with intervals
    res["b_presence"] = {}
    fam_counts = {}
    for c in cells:
        for l in store:
            ids = list(dict.fromkeys(W["ids"] + hold + wrap + cand[(c, l)]))
            pis, cnt, n = counts(c, l, ids)
            e = {"tokens": {}}
            for k, i in enumerate(ids):
                e["tokens"][vocab[i]] = {**boot_diff(cnt[:, 1, k], cnt[:, 0, k], n), "watch": i in W["ids"],
                                         "self_check": i in W["ids"][:W["n_self_check"]]}
            for name, fam in (("hold_on", hold), ("wrap_up", wrap)):
                # a position counts once if any token of the family is present
                fc = np.zeros((len(pis), 2))
                for k, pi in enumerate(pis):
                    g = rows[c][pi]["kind"] == 1
                    for mi, m in enumerate(("base", "rl")):
                        fc[k, mi] = np.isin(rows[c][pi][f"top_{m}_{l}"][g], fam).any(1).sum()
                e[name] = boot_diff(fc[:, 1], fc[:, 0], n)
                fam_counts[(c, l, name)] = (pis, fc, n)
            res["b_presence"][f"{c}_L{l}"] = e

    # c. H2: the family differences by problem group, and rl_only minus both on the base's own answers (T1)
    res["c_by_group"] = {}
    for (c, l, name), (pis, fc, n) in fam_counts.items():
        e = {}
        for g in groups:
            sel = np.array([group[pi]["cell"] == g for pi in pis])
            if sel.any():
                e[g] = boot_diff(fc[sel, 1], fc[sel, 0], n[sel])
        s1, s2 = (np.array([group[pi]["cell"] == g for pi in pis]) for g in ("rl_only", "both"))
        e["rl_only_minus_both"] = boot_dd(fc[s1, 1], fc[s1, 0], n[s1], fc[s2, 1], fc[s2, 0], n[s2])
        res["c_by_group"][f"{c}_L{l}_{name}"] = e

    # d. H3: does the readout lead the text? Presence of the hold-on family before the RL model's top-1 becomes " Wait"
    wait = tid(" Wait")
    res["d_lead"] = {}
    for c in cells:
        tot = np.zeros(4)
        for pi, r in rows[c].items():
            g = r["kind"] == 1
            tot += [(r["tok"][g] == wait).sum(), (maprows[c][pi]["top1_base"][g] == wait).sum(), (maprows[c][pi]["top1_rl"][g] == wait).sum(), g.sum()]
        res["d_lead"][f"{c}_wait_rates"] = {"written": float(tot[0] / tot[3]), "base_next_token_top1": float(tot[1] / tot[3]),
                                            "rl_next_token_top1": float(tot[2] / tot[3]), "positions": int(tot[3])}
        for l in store:
            ev = {m: np.zeros((MAXLAG + 1, 2)) for m in ("base", "rl")}       # [lag] -> hits, events
            base_rate = {m: np.zeros(2) for m in ("base", "rl")}
            for pi, r in rows[c].items():
                g = r["kind"] == 1
                t1 = maprows[c][pi]["top1_rl"] == wait
                js = np.flatnonzero(t1 & g)
                near = np.zeros(len(t1), dtype=bool)
                for j in js:
                    near[max(j - MAXLAG, 0):j + MAXLAG + 1] = True
                fresh = [j for j in js if j >= MAXLAG and not t1[j - MAXLAG:j].any()]
                for m in ("base", "rl"):
                    p = np.isin(r[f"top_{m}_{l}"], hold).any(1)
                    for j in fresh:
                        ev[m][:, 0] += p[j - np.arange(MAXLAG + 1)]
                        ev[m][:, 1] += 1
                    far = g & ~near
                    base_rate[m] += [p[far].sum(), far.sum()]
            res["d_lead"][f"{c}_L{l}"] = {
                "events": int(ev["rl"][0, 1]),
                "far_positions": int(base_rate["rl"][1]),
                **{f"{m}_readout": {"rate_far_from_events": float(base_rate[m][0] / max(base_rate[m][1], 1)),
                                    "rate_by_lag_0_to_32": [float(x) for x in ev[m][:, 0] / np.maximum(ev[m][:, 1], 1)]}
                   for m in ("base", "rl")}}

    # e. where: the hold-on difference by the token just written, by tenth of the answer, and at top-KL positions
    res["e_where"] = {}
    for c in cells:
        for l in store:
            after, dec, kl = {}, np.zeros((10, 3)), np.zeros((2, 3))
            klkey = "kl_base_rl" if c == "T1" else "kl_rl_base"
            for pi, r in rows[c].items():
                g = np.flatnonzero(r["kind"] == 1)
                if len(g) < 20:
                    continue
                pb, pr = (np.isin(r[f"top_{m}_{l}"], hold).any(1) for m in ("base", "rl"))
                prev = np.concatenate([[-1], r["tok"][:-1]])
                for t in np.unique(prev[g]):
                    s = g[prev[g] == t]
                    after.setdefault(int(t), np.zeros(3))
                    after[int(t)] += [pb[s].sum(), pr[s].sum(), len(s)]
                d = np.minimum((np.arange(len(g)) * 10) // len(g), 9)
                for q in range(10):
                    s = g[d == q]
                    dec[q] += [pb[s].sum(), pr[s].sum(), len(s)]
                k = maprows[c][pi][klkey].astype(np.float32)[g]
                hi = k >= np.percentile(k, 96)
                kl[0] += [pb[g[hi]].sum(), pr[g[hi]].sum(), hi.sum()]
                kl[1] += [pb[g[~hi]].sum(), pr[g[~hi]].sum(), (~hi).sum()]
            big = sorted((t for t in after if t >= 0 and after[t][2] >= 2000), key=lambda t: -(after[t][1] - after[t][0]) / after[t][2])
            fmt = lambda v: {"base": float(v[0] / v[2]), "rl": float(v[1] / v[2]), "positions": int(v[2])}
            res["e_where"][f"{c}_L{l}"] = {
                "after_token_top15": [{"token": vocab[t], **fmt(after[t])} for t in big[:15]],
                "after_token_bottom5": [{"token": vocab[t], **fmt(after[t])} for t in big[-5:]],
                "by_tenth_of_answer": [fmt(v) for v in dec],
                "top_4pct_kl_positions": fmt(kl[0]), "other_positions": fmt(kl[1])}

    (out / "metrics.json").write_text(json.dumps(res, indent=1))

    # examples: per problem, the positions where the RL readout's hold-on log-prob exceeds the base's the most
    q, l = index["qscale"], store[-1]
    widx = [W["tokens"].index(s) for s in (" Wait", " wait", " Hmm")]
    ex = {"layer": l, "note": "gap = sum over (' Wait', ' wait', ' Hmm') of readout log-prob, RL minus base, nats, from values "
                             "stored in steps of 0.1 and capped at 25.5", "problems": []}
    for c in cells:
        for pi in sorted(rows[c]):
            r, p = rows[c][pi], group[pi]
            if not ((c == "T1" and p["cell"] in ("rl_only", "neither", "base_only")) or pi % 25 == 0):
                continue
            gap = (r[f"watch_base_{l}"][:, widx].astype(np.float64) - r[f"watch_rl_{l}"][:, widx].astype(np.float64)).sum(1) / q
            gap[r["kind"] != 1] = -np.inf
            peaks = []
            for j in np.argsort(-gap):
                if len(peaks) == 5 or not np.isfinite(gap[j]):
                    break
                if all(abs(int(j) - x) > 40 for x in peaks):
                    peaks.append(int(j))
            text = lambda lo, hi: "".join(vocab[t] for t in r["tok"][max(lo, 0):max(hi, 0)])
            ex["problems"].append({
                "problem_index": pi, "cell": c, "group": p["cell"], "failure_type": p["failure_type"], "positions": int(len(gap)),
                "peaks": [{"position": j, "relative": j / len(gap), "gap": float(gap[j]), "before": text(j - 80, j), "written_next": text(j, j + 30),
                           "base_top": [vocab[t] for t in r[f"top_base_{l}"][j]], "rl_top": [vocab[t] for t in r[f"top_rl_{l}"][j]],
                           "rl_next_token_top1": vocab[int(maprows[c][pi]["top1_rl"][j])],
                           "base_next_token_top1": vocab[int(maprows[c][pi]["top1_base"][j])]} for j in peaks]})
    (out / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False))
    print(f"wrote {out}/metrics.json and examples.json ({len(ex['problems'])} example problems)")


if __name__ == "__main__":
    main()
