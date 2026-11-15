"""Readout of jobs/xreward_trace.py (specs/SPEC_xreward_trace.md, Amendment T). numpy only.

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.xreward_trace --run runs/<job-id> \
        --answers runs/abaybektursun-1114-151534-e72c/answers.jsonl --out studies/rlneurons/results/xreward/trace-01

r = ||diag(s) V^T x|| / ||W_base x|| per position, stored as layer-band means. Conditions here: math31, random (the mean of the three
random-V seeds, math31's singular values), if30, code31. Every array in readout.json is [band][condition][estimate, 2.5 %, 97.5 %]
unless its key says otherwise; intervals are bootstraps over answers (1,000 resamples, seed 0).

  1 level     mean r (mean over answers of the answer's mean); `alignment` = mean r / the r expected from a random V with the same
              singular values, per layer from the job's metrics.json (math31: against the measured random seeds; if30, code31:
              math31's random r scaled by sqrt(sum s_k^2 / sum s_math31^2)), then the band mean.
  2 markers   r at the positions that predict (`predict`) or come right after (`read`) a marker, over r at all other positions, pooled
              over answers. `over_random` = that ratio / the random condition's ratio. Sets: Wait, Hmm, perhaps, Let me check, their
              union `checks`, and the lexical control `control` (So, Therefore, Then). `checks_over_control` = ratio of the two ratios.
  3 onset     count of cap hits with a loop onset (rln4_lib.onset_lines, onset_period). cap_vs_finished: mean r of cap-hit answers
              over finished answers in the same 1,000-token bin (answers that cover the whole bin), and over_random of it.
              wrong_vs_right: the same between wrong and right finished answers.
  4 deciles   r by decile of relative position over the answer's mean, finished answers no longer than the cut.

Writes readout.json and examples.json (one finished and one cap-hit answer: token strings and per-token r of the first 400 tokens).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

import numpy as np

from studies.rlneurons.lib import rln4_lib as R

MODS = ("up", "gate", "q")
OUT = ("math31", "random", "if30", "code31")
MARKERS = {"Wait": r"\bWait\b", "Hmm": r"\bHmm\b", "perhaps": r"\b[Pp]erhaps\b", "Let me check": r"Let me check"}
CONTROL = {"So": r"\bSo\b", "Therefore": r"\bTherefore\b", "Then": r"\bThen\b"}
BIN, B = 1000, 1000


def boot(fn, groups):
    """fn(list of index arrays, one per group) -> array. Returns [..., 3]: estimate and the 2.5 and 97.5 percentiles."""
    rng = np.random.default_rng(0)
    est = fn(groups)
    bs = np.stack([fn([g[rng.integers(0, len(g), len(g))] for g in groups]) for _ in range(B)])
    out = np.stack([est, np.nanpercentile(bs, 2.5, 0), np.nanpercentile(bs, 97.5, 0)], -1).astype(np.float64).round(4)
    return json.loads(json.dumps(out.tolist()).replace("NaN", "null"))          # null: a bin that no answer of a group reaches


def over_random(x):
    return x / x[..., [OUT.index("random")]]


def load(run):
    ix = json.loads((run / "index.json").read_text())
    conds = ix["conds"]
    rnd = [i for i, c in enumerate(conds) if c.startswith("rand")]
    ans = []
    for sh in ix["shards"]:
        z = np.load(run / sh["file"])
        for j in range(len(z["problem_index"])):
            lo, hi = z["offsets"][j], z["offsets"][j + 1]
            r = {}
            for m in MODS:
                v = z[f"r_{m}"][lo:hi].astype(np.float32)
                r[m] = np.stack([v[:, :, rnd].mean(-1) if c == "random" else v[:, :, conds.index(c)] for c in OUT], -1)       # [n, band, OUT]
            ans.append({"idx": int(z["problem_index"][j]), "cap": bool(z["cap_hit"][j]), "score": int(z["score"][j]), "n_full": int(z["n_full"][j]),
                        "tok": z["tok"][lo:hi], "char": z["char"][lo:hi], "r": r, "n": int(hi - lo)})
    return ix, ans


def masks(a, text, pats):
    """predict: the token where a match starts; read: the token after the match's last token."""
    pred, read = np.zeros(a["n"], bool), np.zeros(a["n"], bool)
    end = int(a["char"][-1])
    for p in pats:
        for mt in re.finditer(p, text):
            if mt.end() > end:
                break
            pred[np.searchsorted(a["char"], mt.start(), "right") - 1] = True
            j = np.searchsorted(a["char"], mt.end() - 1, "right")
            if j < a["n"]:
                read[j] = True
    return {"predict": pred, "read": read}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--answers", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run, out = pathlib.Path(a.run), pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ix, ans = load(run)
    met = json.loads((run / "metrics.json").read_text())
    text = {r["problem_index"]: r["text"] for r in map(json.loads, pathlib.Path(a.answers).read_text().splitlines())}
    A = len(ans)
    every = [np.arange(A)]
    cap = np.array([x["cap"] for x in ans])
    right = np.array([x["score"] == 1 for x in ans])
    res = {"run": str(run), "answers": A, "cap_hits": int(cap.sum()), "finished": int((~cap).sum()), "positions": int(sum(x["n"] for x in ans)),
           "conditions": OUT, "bands": ix["bands"], "layout": "[band][condition][estimate, 2.5 %, 97.5 %]", "mods": {}}

    # the instrument on real text: the token string at a marker's predict position starts the marker
    probe = [(x, i) for x in ans[:40] for i in np.flatnonzero(masks(x, text[x["idx"]], [MARKERS["Wait"]])["predict"])]
    bad = [text[x["idx"]][x["char"][i]:x["char"][i] + 8] for x, i in probe if "Wait" not in text[x["idx"]][x["char"][i]:].lstrip()[:8]]
    assert probe and not bad, f"marker positions do not start the marker: {bad[:5]}"
    res["marker_position_check"] = {"wait_positions_checked": len(probe), "not_starting_wait": len(bad)}

    # 3: loop onsets
    onset = {"cap_hits": int(cap.sum()), "degenerate_skipped": 0, "onset_lines": 0, "onset_period": 0}
    for x in ans:
        if x["cap"]:
            t = text[x["idx"]]
            if not any(len(l.strip()) for l in t.split("\n")):
                onset["degenerate_skipped"] += 1          # only newline lines: onset_lines raises IndexError on it
                continue
            onset["onset_lines"] += R.onset_lines(t) is not None
            onset["onset_period"] += R.onset_period(t) is not None
    onset["note"] = "pre-onset analysis not computed: it needs cap hits with an onset" if not (onset["onset_lines"] or onset["onset_period"]) else "onsets exist: pre-onset analysis not written"
    res["onset"] = onset

    sets = {**{k: [p] for k, p in MARKERS.items()}, "checks": list(MARKERS.values()), "control": list(CONTROL.values())}
    mk = [{k: masks(x, text[x["idx"]], p) for k, p in sets.items()} for x in ans]
    res["marker_counts"] = {k: int(sum(m[k]["predict"].sum() for m in mk)) for k in sets}
    nbin = max(x["n"] for x in ans) // BIN
    short = np.array([x["n"] == x["n_full"] and x["n"] >= 50 and not x["cap"] for x in ans])
    res["deciles_answers"] = int(short.sum())

    for m in MODS:
        o = {}
        # 1: level
        M = np.stack([x["r"][m].mean(0) for x in ans])                                             # [A, band, OUT]
        o["mean_r"] = boot(lambda g: M[g[0]].mean(0), every)
        o["math31_over_random"] = boot(lambda g: (M[g[0], :, 0].mean(0) / M[g[0], :, 1].mean(0)), every)
        o["math31_over_random_layout"] = "[band][estimate, 2.5 %, 97.5 %]"
        by = met["mean_r_by_layer"][m]
        names = sorted({k.split("|")[0] for k in met["top8_singular_values"] if f".{'self_attn.q' if m == 'q' else 'mlp.' + m}_proj." in k},
                       key=lambda n: int(n.split(".")[2]))
        assert len(names) == 32
        ss = {d: np.array([np.square(met["top8_singular_values"][f"{n}|{d}"]).sum() for n in names]) for d in ("math31", "if30", "code31")}
        rnd = np.mean([by[f"rand{j}"] for j in range(3)], 0)
        al = {d: np.array(by[d]) / (rnd * np.sqrt(ss[d] / ss["math31"])) for d in ss}
        o["alignment_by_band"] = {d: [round(float(v[lo:hi].mean()), 3) for lo, hi in ix["bands"]] for d, v in al.items()}
        o["alignment_by_layer"] = {d: v.round(3).tolist() for d, v in al.items()}
        o["random_seed_spread_by_band"] = [[round(float(np.mean(by[f"rand{j}"][lo:hi])), 5) for j in range(3)] for lo, hi in ix["bands"]]

        # 2: markers
        o["markers"] = {}
        for side in ("predict", "read"):
            S, N = {}, {}
            for k in sets:
                S[k] = np.stack([np.stack([x["r"][m][mm[k][side]].sum(0), x["r"][m][~mm[k][side]].sum(0)]) for x, mm in zip(ans, mk)])   # [A, 2, band, OUT]
                N[k] = np.array([[mm[k][side].sum(), (~mm[k][side]).sum()] for mm in mk], dtype=np.float64)                               # [A, 2]

            def ratio(k, g):
                s, n = S[k][g].sum(0), N[k][g].sum(0)
                return (s[0] / n[0]) / (s[1] / n[1])

            o["markers"][side] = {k: {"ratio": boot(lambda g, k=k: ratio(k, g[0]), every),
                                      "over_random": boot(lambda g, k=k: over_random(ratio(k, g[0])), every)} for k in sets}
            o["markers"][side]["checks_over_control"] = boot(lambda g: ratio("checks", g[0]) / ratio("control", g[0]), every)

        # 3b: cap hits against finished answers, wrong against right finished answers, in the same token bins
        Bn = np.full((A, nbin, 4, len(OUT)), np.nan, dtype=np.float32)
        for i, x in enumerate(ans):
            for b in range(x["n"] // BIN):
                Bn[i, b] = x["r"][m][b * BIN:(b + 1) * BIN].mean(0)

        def versus(g):
            return np.nanmean(Bn[g[0]], 0) / np.nanmean(Bn[g[1]], 0)                               # [bin, band, OUT]

        for key, g in (("cap_vs_finished", [np.flatnonzero(cap), np.flatnonzero(~cap)]),
                       ("wrong_vs_right_finished", [np.flatnonzero(~cap & ~right), np.flatnonzero(~cap & right)])):
            o[key] = {"layout": "[1,000-token bin][band][condition][estimate, 2.5 %, 97.5 %]",
                      "n_answers_by_bin": [[int(np.isfinite(Bn[gg, b, 0, 0]).sum()) for gg in g] for b in range(nbin)],
                      "ratio": boot(versus, g), "over_random": boot(lambda q: over_random(versus(q)), g)}

        # 4: deciles of relative position
        D = np.stack([np.stack([c.mean(0) for c in np.array_split(x["r"][m], 10)]) / x["r"][m].mean(0) for x, s in zip(ans, short) if s])   # [A', 10, band, OUT]
        o["deciles"] = {"layout": "[decile][band][condition][estimate, 2.5 %, 97.5 %]", "ratio": boot(lambda g: D[g[0]].mean(0), [np.arange(len(D))]),
                        "over_random": boot(lambda g: over_random(D[g[0]].mean(0)), [np.arange(len(D))])}
        res["mods"][m] = o

    (out / "readout.json").write_text(json.dumps(res, indent=1, allow_nan=False) + "\n")

    def example(x):
        t, n = text[x["idx"]], min(400, x["n"] - 1)
        return {"problem_index": x["idx"], "cap_hit": x["cap"], "score_v3": x["score"], "answer_tokens": x["n_full"],
                "tokens": [t[x["char"][i]:x["char"][i + 1]] for i in range(n)], "markers_predict": np.flatnonzero(masks(x, t, sets["checks"])["predict"][:n]).tolist(),
                "r": {m: x["r"][m][:n].astype(np.float64).round(4).tolist() for m in ("up", "q")}}

    ex = {"what": "r[i] is the drive at the input position that predicts tokens[i]; r is [token][band][condition]", "conditions": OUT, "bands": ix["bands"],
          "finished_right": example(next(x for x in ans if not x["cap"] and x["score"] == 1 and x["n"] >= 600)),
          "cap_hit_wrong": example(next(x for x in ans if x["cap"] and x["score"] == 0))}
    (out / "examples.json").write_text(json.dumps(ex) + "\n")
    print(json.dumps({"onset": onset, "marker_counts": res["marker_counts"],
                      **{m: {"mean_r": [[c[0] for c in b] for b in res["mods"][m]["mean_r"]], "alignment_by_band": res["mods"][m]["alignment_by_band"],
                             "checks_predict_ratio": res["mods"][m]["markers"]["predict"]["checks"]["ratio"],
                             "checks_predict_over_random": res["mods"][m]["markers"]["predict"]["checks"]["over_random"],
                             "control_predict_over_random": res["mods"][m]["markers"]["predict"]["control"]["over_random"]} for m in MODS}}))


if __name__ == "__main__":
    main()
