"""Direct test merge328-01 (round-15/account-2/c1), specs/SPEC_direct_merge328.md.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_merge328

Run from the repository root. Cued base on hard328, attempt 0 of samples 0-3: vote over the 4 samples with the real wrong
answers (S) against every finished wrong answer merged into one (M), ties broken at random (mean over the 24 orders).
"""
import itertools
import json
import pathlib
import subprocess

import numpy as np

from studies.rlneurons.analysis.votek import agree_table, vote
from studies.theory.analysis.direct_scatter4 import boot, win

SRC = pathlib.Path("studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl")
OUT = pathlib.Path("studies/theory/results/direct/merge328-01")
ORDERS = list(itertools.permutations(range(4)))
LO, HI = 0.06, 0.40


def keys(r, same, cap_abstains):
    """Key per sample: 'R' if right, None if it abstains, else its wrong-answer group (first earlier agreeing sample)."""
    first, out = [], []
    for s in range(4):
        if r[s]["extracted_v3"] is None:
            out.append(None)
            continue
        g = next((f for f in first if same[f][s]), None)
        if g is None:
            first.append(s)
            g = s
        out.append(None if cap_abstains and r[s]["cap_hit"] else "R" if r[s]["score_v3"] == 1 else g)
    return out


def v(k):
    """P(vote right) under a random tie-break: mean over the 24 orders of 'ties go to the key seen first'."""
    return float(np.mean([win(k, o) for o in ORDERS]))


def merged(k):
    return [None if x is None else "R" if x == "R" else "W" for x in k]


def main():
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    rows = {}
    for line in open(SRC):
        r = json.loads(line)
        if r["attempt"] == 0:
            rows.setdefault(r["problem_index"], {})[r["sample"]] = r
    probs = sorted(rows)
    assert len(probs) == 328 and all(sorted(rows[p]) == [0, 1, 2, 3] for p in probs)
    rows = {p: [rows[p][s] for s in range(4)] for p in probs}
    same = {p: agree_table(rows[p]) for p in probs}

    # Instrument check 1: the team vote reproduces result-5c961a (stored order) and result-f941b8 (order average).
    stored = sum(vote(rows[p], same[p], range(4))["score"] for p in probs)
    Kt = {p: keys(rows[p], same[p], False) for p in probs}
    avg = sum(v(Kt[p]) for p in probs)
    assert stored == 192, stored
    assert round(avg, 1) == 184.6, avg

    K = {p: keys(rows[p], same[p], True) for p in probs}
    band = [p for p in probs if "R" in K[p] and any(x not in (None, "R") for x in K[p])]
    band_score = [p for p in probs if any(x["score_v3"] == 1 for x in rows[p])
                  and any(x["score_v3"] == 0 and x["extracted_v3"] is not None and not x["cap_hit"] for x in rows[p])]
    res = {p: (v(K[p]), v(merged(K[p]))) for p in band}
    d = {p: res[p][0] - res[p][1] for p in band}

    # Instrument check 2: no change where all finished wrong samples share one key; own key per wrong sample only helps R.
    for p in band:
        if len({x for x in K[p] if x not in (None, "R")}) <= 1:
            assert d[p] == 0, p
        own = [x if x in (None, "R") else ("w", s) for s, x in enumerate(K[p])]
        assert v(own) >= res[p][0] - 1e-12, p
    # Planted null: an S arm whose wrong samples all share one key must read D = 0.
    planted = float(np.mean([v([None if x is None else "R" if x == "R" else 0 for x in K[p]]) - res[p][1] for p in band]))
    assert planted == 0, planted

    n = len(band)
    D = float(np.mean([d[p] for p in band]))
    ci = boot([d[p] for p in band], np.random.default_rng(0))
    verdict = ("holds" if n >= 50 and LO <= ci[0] and ci[1] <= HI else
               "refuted" if ci[1] < LO or ci[0] > HI else "undecided")
    null_pos = "inside" if -0.03 <= ci[0] and ci[1] <= 0.03 else "outside" if ci[0] > 0.03 or ci[1] < -0.03 else "overlaps"

    other_band = [p for p in probs if "R" in Kt[p] and any(x not in (None, "R") for x in Kt[p])]
    other = [v(Kt[p]) - v(merged(Kt[p])) for p in other_band]
    rep = []
    for p in band:
        wk = [x for x in K[p] if x not in (None, "R")]
        rep += [wk.count(x) >= 2 for x in wk]
    nr = {p: K[p].count("R") for p in band}
    by_r = {str(r): {"n": sum(nr[p] == r for p in band), "D": round(float(np.mean([d[p] for p in band if nr[p] == r])), 4)}
            for r in (1, 2, 3) if any(nr[p] == r for p in band)}

    metrics = {
        "mechanism": "round-15/account-2/c1", "spec": "studies/theory/specs/SPEC_direct_merge328.md", "source": str(SRC),
        "statistic": "D = mean over kept problems of V_S - V_M (vote over attempt-0 samples 0-3, random tie-break as mean of 24 orders; S real wrong keys, M every finished wrong key merged; cap-hit samples abstain)",
        "rows": "hard328 problems with >= 1 right and >= 1 finished wrong (not cap-hit) sample among attempt-0 samples 0-3",
        "check_team_vote_stored_order": stored, "check_team_vote_order_average": round(avg, 2),
        "planted_all_wrong_one_key_D": planted,
        "n": n, "n_if_right_includes_cap_hit_right": len(band_score),
        "D": round(D, 4), "ci90": ci, "null_value": 0.0, "null_range": [-0.03, 0.03], "account_2_range": [LO, HI],
        "V_S_mean": round(float(np.mean([res[p][0] for p in band])), 4),
        "V_M_mean": round(float(np.mean([res[p][1] for p in band])), 4),
        "verdict": verdict, "ci90_vs_null_range": null_pos,
        "rule": "holds if n >= 50 and the 90 % interval lies inside [0.06, 0.40]; refuted if it lies wholly outside; else undecided",
        "bootstrap": "10,000 resamples of kept problems, numpy default_rng(0), 90 % percentile interval",
        "descriptive": {
            "problems_d_positive": sum(d[p] > 0 for p in band), "problems_d_zero": sum(d[p] == 0 for p in band),
            "problems_d_negative": sum(d[p] < 0 for p in band),
            "share_finished_wrong_key_repeats": round(float(np.mean(rep)), 4), "finished_wrong_samples": len(rep),
            "D_by_right_count": by_r,
            "D_team_abstention_rule": {"D": round(float(np.mean(other)), 4), "ci90": boot(other, np.random.default_rng(0)), "n": len(other)},
        },
        "problems": band,
        "per_problem": {str(p): {"V_S": round(res[p][0], 4), "V_M": round(res[p][1], 4), "keys": K[p]} for p in band},
    }
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    def item(p):
        r = rows[p]
        return {"problem_index": p, "gold": r[0]["gold"], "V_S": res[p][0], "V_M": res[p][1], "d": d[p], "keys": K[p],
                "answers": [{"sample": s, "extracted_v3": r[s]["extracted_v3"], "score_v3": r[s]["score_v3"],
                             "cap_hit": r[s]["cap_hit"]} for s in range(4)]}

    yes = max(band, key=lambda p: d[p])
    no = next(p for p in band if d[p] == 0)
    (OUT / "examples.json").write_text(json.dumps([{**item(yes), "merging_changes_vote": True},
                                                   {**item(no), "merging_changes_vote": False}], indent=1) + "\n")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({"spec": metrics["spec"], "commit": commit, "board": "work-b38c6b",
        "command": "uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_merge328",
        "inputs": [str(SRC)]}, indent=1) + "\n")
    print(json.dumps({k: x for k, x in metrics.items() if k not in ("per_problem", "problems")}, indent=1))


if __name__ == "__main__":
    main()
