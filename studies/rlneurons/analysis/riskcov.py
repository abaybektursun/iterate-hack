"""Risk-coverage of Think-SFT + cue, RL plain and base + cue on stored rows (specs/SPEC_riskcov.md; laptop, no GPU).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.riskcov \
        --set math500 --out studies/rlneurons/results/riskcov/math500-01 [--think-run runs/<joined>] [--rl-run runs/<job>]
    ... --set hard328 --out studies/rlneurons/results/riskcov/hard328-01 --fixed studies/rlneurons/results/riskcov/math500-01/chosen.json
    ... --set hard328 --read studies/rlneurons/results/riskcov/read-01 --think-run runs/<joined> --rl-run runs/<job>

  --set               hard328 or math500: the three run folders of SETS (rows.jsonl of analysis/day1_vote.py).
  --out               a new run folder: run.json, readout.json, curves.json, table.md, examples.json, chosen.json (math500 only).
  --fixed             chosen.json of the MATH-500 run: the length cut of each model, scored once here. Without it the cut is chosen here.
  --think-run, --rl-run  job folders with answers.jsonl: adds the end of the text to the examples; required by --read.
  --read              instead of the analysis: writes the 25 rows of the hand read (seed 0) with the end of their text.

Only attempt 0 of each sample is read, for all three models (the RL and base runs have restarts, Think-SFT has none). A signal
sees n_new, cap_hit and extracted_v3, never score_v3 or gold. Fails loud when the vote does not reproduce VOTE.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.lib import n13_score as S

RES = pathlib.Path("studies/rlneurons/results")
SPEC = "studies/rlneurons/specs/SPEC_riskcov.md"
SETS = {"hard328": {"think": "thinkvote/hard328_sft1_cue_s4-01", "rl": "day1_3/hard328_rl_plain_s4r2-01", "base": "day1_3/hard328_base_cue_s4r2-01"},
        "math500": {"think": "thinkvote/math500_sft1_cue_s4-01", "rl": "day1_3/math500_rl-01", "base": "day1_3/math500_base_cue-01"}}
VOTE = {"hard328": {"think": 241, "rl": 221, "base": 192}, "math500": {"think": 481, "rl": 474, "base": 446}}   # posted rows (result-818c20)
LABEL = {"think": "Think-SFT + cue", "rl": "RL plain", "base": "base + cue"}
PAIRS = (("think", "rl"), ("think", "base"), ("rl", "base"))
SIGNALS = ("finished", "length", "agreement", "agreement_length", "finished_length", "shuffled")
GRID = [round(0.05 * k, 2) for k in range(1, 21)]
BINS = [0, 2000, 4000, 8000, 12000, 16384]
CUTS = [2000, 3000, 4000, 6000, 8000, 10000, 12000, 14000, 16000]
LAMBDAS = (0, 0.5, 1)
BOOT, BOOT_VOTE = 2000, 5000
OUTCOME = ("abstained", "wrong", "right")


def load(folder) -> dict:
    """{problem index: the attempt-0 rows of its samples, in sample order}."""
    by = {}
    for r in map(json.loads, open(pathlib.Path(folder) / "rows.jsonl")):
        if r["attempt"] == 0:
            by.setdefault(r["problem_index"], []).append(r)
    for rows in by.values():
        rows.sort(key=lambda r: r["sample"])
        assert [r["sample"] for r in rows] == [0, 1, 2, 3], "a problem without its four samples"
    return dict(sorted(by.items()))


def arrays(by: dict) -> dict:
    """Per problem x sample: n_new, cap, ans (has an extracted answer), right, agree (samples of the problem that agree with this
    one's answer, itself included; 0 without an answer). Per problem: the vote's outcome (0 abstained, 1 wrong, 2 right)."""
    f = lambda k, t: np.array([[r[k] for r in rows] for rows in by.values()], t)
    a = {"idx": list(by), "n_new": f("n_new", int), "cap": f("cap_hit", bool), "right": f("score_v3", bool),
         "ans": np.array([[r["extracted_v3"] is not None for r in rows] for rows in by.values()])}
    assert not (a["right"] & ~a["ans"]).any(), "a right sample without an extracted answer"
    a["agree"] = np.zeros_like(a["n_new"])
    a["vote"] = np.zeros(len(by), int)
    for p, rows in enumerate(by.values()):
        v = V.vote(rows)
        for g in v["groups"]:
            a["agree"][p, g] = len(g)
        a["vote"][p] = 0 if v["winner"] is None else 1 + v["score"]
    a["sample"] = np.where(a["ans"], 1 + a["right"], 0)               # outcome of every sample
    return a


def keys(a: dict, signal: str, tie) -> np.ndarray:
    """Confidence key of every sample, lower = kept first; inf for a sample without an answer (never kept)."""
    n, cap, ag = a["n_new"].astype(float), a["cap"], a["agree"]
    k = {"finished": cap * 1.0, "length": n, "agreement": -ag * 1.0, "agreement_length": -ag * 1e6 + n,
         "finished_length": cap * 1e6 + n, "shuffled": np.zeros_like(n)}[signal]
    return np.where(a["ans"], k + 0.5 * tie, np.inf)


def precision_at(key, right, grid, clip=False) -> np.ndarray:
    """Precision of the round(c x samples) most confident samples for every coverage c of grid. nan where fewer samples have an
    answer; with clip (bootstrap resamples) the count is cut to the answered samples instead."""
    key, right = key.ravel(), right.ravel()
    cum = np.cumsum(right[np.argsort(key, kind="stable")])
    n_ans = int(np.isfinite(key).sum())
    out = []
    for c in grid:
        m = round(c * key.size)
        m = min(m, n_ans) if clip else m
        out.append(cum[m - 1] / m if 0 < m <= n_ans else np.nan)
    return np.array(out)


def curves(arr: dict, rng) -> dict:
    """Per signal: each model's precision on GRID with a bootstrap band over problems, the area (mean precision over the grid up to
    the common coverage) and the paired differences at matched coverage."""
    n = len(arr["think"]["idx"])
    tie = rng.random((n, 4))
    boots = rng.integers(0, n, (BOOT, n))
    common = min(a["ans"].mean() for a in arr.values())
    shared = [g for g, c in enumerate(GRID) if c <= common]
    pct = lambda x: [None if np.isnan(v) else float(v) for v in x]
    band = lambda x: [pct(np.nanpercentile(x, q, axis=0)) for q in (2.5, 97.5)]
    out = {"grid": GRID, "common_coverage": float(common), "common_grid": [GRID[g] for g in shared], "signals": {}}
    for sig in SIGNALS:
        pt, bs = {}, {}
        for m, a in arr.items():
            k = keys(a, sig, tie)
            pt[m] = precision_at(k, a["right"], GRID)
            bs[m] = np.array([precision_at(k[i], a["right"][i], GRID, clip=True) for i in boots])
            bs[m][:, np.isnan(pt[m])] = np.nan
        d = {"models": {m: {"answered_share": float(arr[m]["ans"].mean()), "precision": pct(pt[m]), "band95": band(bs[m]),
                            "area": float(pt[m][shared].mean()), "area95": band(bs[m][:, shared].mean(1)[:, None])} for m in arr}, "matched": {}}
        for x, y in PAIRS:
            d["matched"][f"{x} - {y}"] = {"points": pct(100 * (pt[x] - pt[y])[shared]), "interval95": band(100 * (bs[x] - bs[y])[:, shared]),
                                          "area_points": float(100 * (pt[x] - pt[y])[shared].mean()),
                                          "area_interval95": band(100 * (bs[x] - bs[y])[:, shared].mean(1)[:, None])}
        out["signals"][sig] = d
    return out


def bins(a: dict, problems) -> dict:
    """Finished answered samples of the given problems by generated tokens: the fixed BINS and the model's own quartiles."""
    fin = (a["ans"] & ~a["cap"])[problems]
    n, right = a["n_new"][problems][fin], a["right"][problems][fin]
    q = np.quantile(n, [0.25, 0.5, 0.75])

    def table(edges):
        rows = []
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = (n > lo) & (n <= hi)
            k, t = int(right[m].sum()), int(m.sum())
            rows.append({"tokens": [float(lo), float(hi)], "samples": t, "right": k, "precision": k / t if t else None, "wilson95": S.wilson(k, t)})
        return rows
    return {"finished_answered": int(fin.sum()), "right": int(right.sum()), "fixed": table(BINS), "quartiles": table([0, *q, 16384])}


def by_caps(group: dict, target: dict, base: dict, rng) -> list:
    """Problems by k = cap hits among `group`'s four samples. Per k (and k >= 1): `target`'s precision on finished answered samples,
    its cap rate, and the precision expected from difficulty: target's precision per stratum (the base's number of right samples,
    0 to 4), over all problems (`expected`) and over the problems outside the row (`expected_outside`), weighted by the row's
    target samples per stratum. Strata with no target sample in the reference are left out of both sides."""
    k = group["cap"].sum(1)
    fin = target["ans"] & ~target["cap"]
    f, r, s = fin.sum(1).astype(float), (fin & target["right"]).sum(1).astype(float), base["right"].sum(1)
    n = len(k)
    boots = [np.bincount(i, minlength=n).astype(float) for i in rng.integers(0, n, (BOOT, n))]

    def stat(w, g, ref):
        fs, rs = np.bincount(s, w * f * ref, 5), np.bincount(s, w * r * ref, 5)
        gs, gr = np.bincount(s, w * f * g, 5), np.bincount(s, w * r * g, 5)
        ok = fs > 0
        if gs[ok].sum() == 0:
            return np.nan, np.nan
        return gr[ok].sum() / gs[ok].sum(), ((rs[ok] / fs[ok]) * gs[ok]).sum() / gs[ok].sum()

    rows = []
    for name, g in [*((str(j), k == j) for j in range(5)), (">=1", k >= 1)]:
        g = g.astype(float)
        row = {"k": name, "problems": int(g.sum()), "finished_answered": int((f * g).sum()), "right": int((r * g).sum()),
               "cap_rate": float((target["cap"].sum(1) * g).sum() / (4 * g.sum())) if g.sum() else None,
               "base_precision": float(((base["ans"] & ~base["cap"] & base["right"]).sum(1) * g).sum() / max(1, ((base["ans"] & ~base["cap"]).sum(1) * g).sum()))}
        for key, ref in (("expected", np.ones(n)), ("expected_outside", 1 - g)):
            o, e = stat(np.ones(n), g, ref)
            d = np.array([np.subtract(*stat(w, g, ref)) for w in boots])
            row["precision"] = None if np.isnan(o) else float(o)
            row[key] = None if np.isnan(e) else float(e)
            row[key + "_minus_points"] = None if np.isnan(o - e) else {"points": float(100 * (o - e)), "interval95": [float(100 * np.nanpercentile(d, q)) for q in (2.5, 97.5)]}
        rows.append(row)
    return rows


def transition(x, y) -> dict:
    """Counts of (outcome of x, outcome of y) over paired units."""
    return {f"{OUTCOME[i]} / {OUTCOME[j]}": int(((x == i) & (y == j)).sum()) for i in range(3) for j in range(3)}


def cut_vote(rows: list, L: int, fallback: bool) -> int:
    """Outcome (0 abstained, 1 wrong, 2 right) of the vote after dropping every sample longer than L tokens."""
    v = V.vote([r if r["n_new"] <= L else {**r, "extracted_v3": None} for r in rows])
    if v["winner"] is None and fallback:
        v = V.vote(rows)
    return 0 if v["winner"] is None else 1 + v["score"]


def cuts(by: dict, a: dict) -> dict:
    """Every (variant, L): right, wrong, abstained problems, tokens per problem as run and with generation stopped at L, and the
    per-problem scores. `plain` is the vote over 4."""
    out = {"plain": {"right": int((a["vote"] == 2).sum()), "wrong": int((a["vote"] == 1).sum()), "abstained": int((a["vote"] == 0).sum()),
                     "tokens_as_run": float(a["n_new"].sum() / len(by)), "tokens_stopped": float(a["n_new"].sum() / len(by)),
                     "per_problem": (a["vote"] == 2).astype(int).tolist()}}
    for variant in ("strict", "fallback"):
        for L in CUTS:
            o = np.array([cut_vote(rows, L, variant == "fallback") for rows in by.values()])
            stopped = np.minimum(a["n_new"], L).sum(1)
            if variant == "fallback":                                   # the fallback problems ran their samples in full
                none_left = ~((a["n_new"] <= L) & a["ans"]).any(1)
                stopped = np.where(none_left, a["n_new"].sum(1), stopped)
            out[f"{variant}_{L}"] = {"variant": variant, "L": L, "right": int((o == 2).sum()), "wrong": int((o == 1).sum()), "abstained": int((o == 0).sum()),
                                     "tokens_as_run": float(a["n_new"].sum() / len(by)), "tokens_stopped": float(stopped.sum() / len(by)),
                                     "per_problem": (o == 2).astype(int).tolist()}
    return out


def choose(c: dict) -> str:
    """The cut with the most right problems; ties to the larger L, then to fallback (SPEC_riskcov.md (e))."""
    return max((k for k in c if k != "plain"), key=lambda k: (c[k]["right"], c[k]["L"], c[k]["variant"] == "fallback"))


def penalty(a: dict) -> dict:
    n = len(a["idx"])
    single = {"right": float(a["right"].sum() / 4), "wrong": float((a["ans"] & ~a["right"]).sum() / 4), "abstained": float((~a["ans"]).sum() / 4)}
    vote = {"right": int((a["vote"] == 2).sum()), "wrong": int((a["vote"] == 1).sum()), "abstained": int((a["vote"] == 0).sum())}
    return {k: {**d, "n": n, "score": {str(l): d["right"] - l * d["wrong"] for l in LAMBDAS}} for k, d in (("single_mean_of_4", single), ("vote", vote))}


def texts(run) -> dict:
    return {(r["problem_index"], r["sample"]): r for r in map(json.loads, open(pathlib.Path(run) / "answers.jsonl")) if r["attempt"] == 0}


def pools(arr: dict) -> dict:
    """(problem position, sample) of the three groups of the hand read: long = at least 8,000 tokens, finished and answered."""
    t, r = arr["think"], arr["rl"]
    capped = t["cap"].any(1)[:, None]
    long = lambda a: a["ans"] & ~a["cap"] & (a["n_new"] >= 8000)
    return {"rl_long_wrong_where_think_capped": np.argwhere(long(r) & ~r["right"] & capped),
            "think_long_right": np.argwhere(long(t) & t["right"])}


def tail(row: dict, chars: int) -> dict:
    return {k: row[k] for k in ("problem_index", "sample", "seed", "n_new", "cap_hit", "extracted_v3", "score_v3", "gold")} | {
        "text_chars": len(row["text"]), f"text_last_{chars}": row["text"][-chars:]}


def read(arr: dict, think_run, rl_run, out: pathlib.Path):
    """The rows of the hand read, drawn with seed 0: 10 of each pool, then 5 Think-SFT cap hits on problems of the first group."""
    rng = np.random.default_rng(0)
    tt, rt, idx = texts(think_run), texts(rl_run), arr["think"]["idx"]
    P = pools(arr)
    pick = {k: v[np.sort(rng.choice(len(v), 10, replace=False))] for k, v in P.items()}
    caps = []
    for p in dict.fromkeys(int(p) for p, _ in pick["rl_long_wrong_where_think_capped"]):
        caps.append((p, int(np.flatnonzero(arr["think"]["cap"][p])[0])))
    res = {"pool_sizes": {k: len(v) for k, v in P.items()}, "seed": 0,
           "rl_long_wrong_where_think_capped": [tail(rt[idx[p], s], 3000) | {"prompt": rt[idx[p], s]["prompt"]} for p, s in pick["rl_long_wrong_where_think_capped"]],
           "think_long_right": [tail(tt[idx[p], s], 3000) for p, s in pick["think_long_right"]],
           "think_cap_hits_same_problems": [tail(tt[idx[p], s], 1500) for p, s in caps[:5]]}
    out.mkdir(parents=True)
    (out / "rows.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(res["pool_sizes"]))


def examples(arr: dict, think_run, rl_run) -> dict:
    """One wrong (RL's longest finished wrong answer on a problem where Think-SFT hit the cap) and one right (Think-SFT's longest
    finished right answer), with the end of the text when the job folders are given."""
    P, idx = pools(arr), arr["think"]["idx"]
    out = {}
    for name, key, m, run in (("wrong", "rl_long_wrong_where_think_capped", "rl", rl_run), ("right", "think_long_right", "think", think_run)):
        if not len(P[key]):
            out[name] = None
            continue
        p, s = max(map(tuple, P[key]), key=lambda ps: arr[m]["n_new"][ps])
        a = arr[m]
        out[name] = {"model": LABEL[m], "problem_index": idx[p], "sample": int(s), "n_new": int(a["n_new"][p, s]), "score_v3": int(a["right"][p, s]),
                     "think_sft_cap_hits_on_problem": int(arr["think"]["cap"][p].sum()), "rl_right_samples_on_problem": int(arr["rl"]["right"][p].sum())}
        if run:
            out[name] |= tail(texts(run)[idx[p], int(s)], 2000) | {"prompt": texts(run)[idx[p], int(s)]["prompt"]}
    return out


def markdown(res: dict, cv: dict) -> str:
    f = lambda x: "" if x is None else f"{100 * x:.1f}"
    iv = lambda p, lo, hi: "" if p is None else f"{p:+.1f} [{lo:+.1f}, {hi:+.1f}]"
    o = [f"# Risk-coverage, {res['set']} (n = {res['n']}, 4 samples, attempt 0, T 1.0 / top-p 1.0, grader v3)", "",
         "Precision = right over kept samples, %. Coverage = kept samples over all samples. Intervals: bootstrap over problems.", ""]
    for sig in ("length", "agreement_length"):
        d = cv["signals"][sig]
        o += [f"## Precision at matched coverage, signal `{sig}`", "",
              "| Coverage | Think-SFT + cue | RL plain | base + cue | Think-SFT - RL, points [95 %] | RL - base, points [95 %] |", "|---|---|---|---|---|---|"]
        for j, c in enumerate(cv["common_grid"]):
            g = GRID.index(c)
            a, b = d["matched"]["think - rl"], d["matched"]["rl - base"]
            o.append(f"| {c:.2f} | " + " | ".join(f(d["models"][m]["precision"][g]) for m in LABEL) +
                     f" | {iv(a['points'][j], a['interval95'][0][j], a['interval95'][1][j])} | {iv(b['points'][j], b['interval95'][0][j], b['interval95'][1][j])} |")
        o += [""]
    o += ["## Area: mean precision over the grid up to the common coverage " + f"{cv['common_coverage']:.3f}", "", "| Signal | " + " | ".join(LABEL.values()) + " | Think-SFT - RL, points [95 %] |",
          "|---|---|---|---|---|"]
    for sig in SIGNALS:
        d = cv["signals"][sig]
        a = d["matched"]["think - rl"]
        o.append(f"| {sig} | " + " | ".join(f(d["models"][m]["area"]) for m in LABEL) + f" | {iv(a['area_points'], a['area_interval95'][0][0], a['area_interval95'][1][0])} |")
    for key, title in (("bins", "all problems"), ("bins_matched", f"the {res['matched_problems']} problems where all three models have a finished answered sample")):
        for kind in ("fixed", "quartiles"):
            o += ["", f"## Finished answered samples by generated tokens, {kind}, {title}", "", "| Bin | " + " | ".join(f"{l}: right / samples, %" for l in LABEL.values()) + " |", "|---|---|---|---|"]
            for j in range(len(res[key]["think"][kind])):
                cell = lambda b: f"{b['right']} / {b['samples']}, {f(b['precision'])} ({b['tokens'][0]:.0f}-{b['tokens'][1]:.0f})"
                o.append(f"| {j + 1} | " + " | ".join(cell(res[key][m][kind][j]) for m in LABEL) + " |")
    for key, title in (("by_think_caps", "Problems by Think-SFT cap hits (k of 4)"), ("by_rl_caps", "Problems by RL cap hits (k of 4)")):
        for m, rows in res[key].items():
            o += ["", f"## {title}: {LABEL[m]} on finished answered samples", "",
                  "| k | Problems | Right / samples | Precision | Expected from base strata | Observed - expected, points [95 %] | Expected, problems outside the row | Observed - expected, points [95 %] | Cap rate | base + cue precision |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for r in rows:
                d = lambda k: "" if r[k] is None else iv(r[k]["points"], *r[k]["interval95"])
                o.append(f"| {r['k']} | {r['problems']} | {r['right']} / {r['finished_answered']} | {f(r['precision'])} | {f(r['expected'])} | {d('expected_minus_points')} | "
                         f"{f(r['expected_outside'])} | {d('expected_outside_minus_points')} | {f(r['cap_rate'])} | {f(r['base_precision'])} |")
    for unit in ("single", "vote"):
        for y in ("rl", "base"):
            t = res["transitions"][unit][f"think / {y}"]
            o += ["", f"## Outcomes, {unit} ({'4 sample pairs per problem, summed' if unit == 'single' else 'problems'}): Think-SFT + cue (rows) against {LABEL[y]} (columns)", "",
                  "| | " + " | ".join(OUTCOME) + " |", "|---|---|---|---|"]
            o += [f"| {a} | " + " | ".join(str(t[f"{a} / {b}"]) for b in OUTCOME) + " |" for a in OUTCOME]
    o += ["", "## Vote after dropping samples longer than L tokens", "", "| Model | Rule | Right | Wrong | Abstained | Tokens as run | Tokens, stopped at L |", "|---|---|---|---|---|---|---|"]
    for m in LABEL:
        for k, c in res["cuts"][m].items():
            o.append(f"| {LABEL[m]} | {k}{' (chosen on MATH-500)' if k == res['chosen'][m]['rule'] else ''} | {c['right']} | {c['wrong']} | {c['abstained']} | {c['tokens_as_run']:.0f} | {c['tokens_stopped']:.0f} |")
    o += ["", "## Chosen cut against the plain vote over 4", "", "| Model | Rule | Right | Plain vote | Difference, points [95 %] |", "|---|---|---|---|---|"]
    o += [f"| {LABEL[m]} | {c['rule']} | {c['right']} | {c['plain_right']} | {iv(c['minus_plain_points'], *c['interval95'])} |" for m, c in res["chosen"].items()]
    o += ["", "## Score = right - lambda x wrong (problems)", "", "| Model | Unit | Right | Wrong | Abstained | lambda 0 | lambda 0.5 | lambda 1 |", "|---|---|---|---|---|---|---|---|"]
    for m in LABEL:
        for unit, d in res["penalty"][m].items():
            o.append(f"| {LABEL[m]} | {unit} | {d['right']:.1f} | {d['wrong']:.1f} | {d['abstained']:.1f} | " + " | ".join(f"{d['score'][str(l)]:.1f}" for l in LAMBDAS) + " |")
    return "\n".join(o) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, choices=list(SETS))
    ap.add_argument("--out")
    ap.add_argument("--fixed")
    ap.add_argument("--read")
    ap.add_argument("--think-run")
    ap.add_argument("--rl-run")
    a = ap.parse_args()
    out = pathlib.Path(a.read or a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    by = {m: load(RES / d) for m, d in SETS[a.set].items()}
    arr = {m: arrays(b) for m, b in by.items()}
    assert arr["think"]["idx"] == arr["rl"]["idx"] == arr["base"]["idx"], "the three runs are not on the same problems"
    got = {m: int((arr[m]["vote"] == 2).sum()) for m in arr}
    assert got == VOTE[a.set], f"instrument check failed: vote over 4 gives {got}, posted {VOTE[a.set]}"
    if a.read:
        return read(arr, a.think_run, a.rl_run, out)
    rng = np.random.default_rng(0)
    n = len(arr["think"]["idx"])
    cv = curves(arr, rng)
    matched = np.all([(x["ans"] & ~x["cap"]).any(1) for x in arr.values()], axis=0)
    everyone = np.ones(n, bool)
    cut = {m: cuts(by[m], arr[m]) for m in arr}
    rule = json.loads(pathlib.Path(a.fixed).read_text()) if a.fixed else {m: choose(cut[m]) for m in arr}
    chosen = {m: {"rule": rule[m], "chosen_on": a.fixed or "this set", "right": cut[m][rule[m]]["right"], "plain_right": cut[m]["plain"]["right"],
                  "minus_plain_points": 100 * (cut[m][rule[m]]["right"] - cut[m]["plain"]["right"]) / n,
                  "interval95": list(S.paired_bootstrap(cut[m][rule[m]]["per_problem"], cut[m]["plain"]["per_problem"], BOOT_VOTE)),
                  "tokens_as_run": cut[m][rule[m]]["tokens_as_run"], "tokens_stopped": cut[m][rule[m]]["tokens_stopped"]} for m in arr}
    res = {"set": a.set, "n": n, "spec": SPEC, "runs": SETS[a.set], "attempt": "0 only, for all three models", "instrument_check_vote": {"got": got, "posted": VOTE[a.set]},
           "counts": {m: {"samples": 4 * n, "cap_hits": int(x["cap"].sum()), "answered": int(x["ans"].sum()), "finished_answered": int((x["ans"] & ~x["cap"]).sum()),
                          "right": int(x["right"].sum()), "right_finished": int((x["right"] & ~x["cap"]).sum()), "cap_hits_with_answer": int((x["cap"] & x["ans"]).sum())} for m, x in arr.items()},
           "matched_problems": int(matched.sum()),
           "bins": {m: bins(x, everyone) for m, x in arr.items()}, "bins_matched": {m: bins(x, matched) for m, x in arr.items()},
           "by_think_caps": {m: by_caps(arr["think"], arr[m], arr["base"], rng) for m in ("rl", "base")},
           "by_rl_caps": {m: by_caps(arr["rl"], arr[m], arr["base"], rng) for m in ("think", "base")},
           "transitions": {"single": {f"think / {y}": transition(arr["think"]["sample"], arr[y]["sample"]) for y in ("rl", "base")},
                           "vote": {f"think / {y}": transition(arr["think"]["vote"], arr[y]["vote"]) for y in ("rl", "base")}},
           "cuts": {m: {k: {x: v for x, v in c.items() if x != "per_problem"} for k, c in cut[m].items()} for m in arr},
           "chosen": chosen, "penalty": {m: penalty(x) for m, x in arr.items()}}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    out.mkdir(parents=True)
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": "python -m studies.rlneurons.analysis.riskcov " + " ".join(sys.argv[1:]), "job_id": None,
                                              "gpu": "none (laptop)", "spec": SPEC, "bootstrap": {"curves": BOOT, "vote": BOOT_VOTE, "seed": 0}}, indent=1) + "\n")
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "curves.json").write_text(json.dumps(cv) + "\n")
    (out / "table.md").write_text(markdown(res, cv))
    (out / "examples.json").write_text(json.dumps(examples(arr, a.think_run, a.rl_run), indent=1, ensure_ascii=False) + "\n")
    if not a.fixed:
        (out / "chosen.json").write_text(json.dumps(rule, indent=1) + "\n")
    print((out / "table.md").read_text())


if __name__ == "__main__":
    main()
