"""Direct test scatter4-01 (run-08/f2-m05), specs/SPEC_direct_scatter4.md.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_scatter4

Run from the repository root. Vote over 4 on the cued base's 12 MATH-500 samples (rows of result-1c9e40), real wrong
answers (S) against every finished wrong answer merged into one (M), over all 495 four-sample subsets.
"""
import itertools
import json
import pathlib
import subprocess

import numpy as np

from studies.rlneurons.analysis.votek import agree_table, vote

SRC = pathlib.Path("studies/rlneurons/results/votek/math500_base_cue-01/rows.jsonl")
OUT = pathlib.Path("studies/theory/results/direct/scatter4-01")
SUBS = list(itertools.combinations(range(12), 4))
B = 10_000


def keys(r, same, cap_abstains):
    """Key per sample: 'R' if right, None if it abstains, else its team-vote group (formed once over the 12 samples)."""
    first, out = [], []
    for s in range(12):
        if r[s]["extracted_v3"] is None:
            out.append(None)
            continue
        g = next((f for f in first if same[f][s]), None)
        if g is None:
            first.append(s)
            g = s
        out.append(None if cap_abstains and r[s]["cap_hit"] else "R" if r[s]["score_v3"] == 1 else g)
    return out


def win(k, sub):
    """Plurality over non-abstaining keys of `sub`; ties go to the key whose earliest sample comes first in `sub`."""
    cnt, firsts = {}, {}
    for i, s in enumerate(sub):
        if k[s] is not None:
            cnt[k[s]] = cnt.get(k[s], 0) + 1
            firsts.setdefault(k[s], i)
    if not cnt:
        return 0
    return int(min(cnt, key=lambda x: (-cnt[x], firsts[x])) == "R")


def v4(k, order):
    return float(np.mean([win(k, [order[s] for s in sub]) for sub in SUBS]))


def arms(k, order=tuple(range(12))):
    m = [None if x is None else "R" if x == "R" else "W" for x in k]
    return v4(k, order), v4(m, order)


def boot(x, rng):
    x = np.asarray(x, float)
    m = x[rng.integers(0, len(x), (B, len(x)))].mean(1)
    return [round(float(np.percentile(m, 5)), 4), round(float(np.percentile(m, 95)), 4)]


def main():
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    per = {}
    for line in open(SRC):
        r = json.loads(line)
        per.setdefault(r["problem_index"], {}).setdefault(r["sample"], r)
    probs = sorted(per)
    assert len(probs) == 500 and all(sorted(per[p]) == list(range(12)) for p in probs)
    rows = {p: [per[p][s] for s in range(12)] for p in probs}
    same = {p: agree_table(rows[p]) for p in probs}

    # Instrument check 1: the team's vote reproduces the posted counts of result-1c9e40.
    n4 = sum(vote(rows[p], same[p], range(4))["score"] for p in probs)
    n12 = sum(vote(rows[p], same[p], range(12))["score"] for p in probs)
    assert (n4, n12) == (446, 466), (n4, n12)
    K = {p: keys(rows[p], same[p], True) for p in probs}
    Kt = {p: keys(rows[p], same[p], False) for p in probs}
    plan12 = sum(win(K[p], range(12)) for p in probs)
    team12 = sum(win(Kt[p], range(12)) for p in probs)
    primary = "plan" if abs(plan12 - 466) <= 2 else "team"
    KK = K if primary == "plan" else Kt

    right = {p: sum(x["score_v3"] == 1 for x in rows[p]) for p in probs}
    band = [p for p in probs if 2 <= right[p] <= 10]
    res = {p: arms(KK[p]) for p in band}
    d = {p: res[p][0] - res[p][1] for p in band}

    # Instrument check 2: merging changes nothing where all finished wrong samples share one key; giving every wrong
    # sample its own key can only help the right answer.
    for p in band:
        wk = {x for x in KK[p] if x not in (None, "R")}
        if len(wk) <= 1:
            assert d[p] == 0, p
        own = [x if x in (None, "R") else ("w", s) for s, x in enumerate(KK[p])]
        assert v4(own, tuple(range(12))) >= res[p][0] - 1e-12, p
    # Planted failure: an S arm whose wrong samples all share one key must give D = 0 (the instrument then reads 0).
    planted = float(np.mean([v4([None if x is None else "R" if x == "R" else 0 for x in KK[p]], tuple(range(12))) - res[p][1] for p in band]))
    assert planted == 0, planted

    rng = np.random.default_rng(0)
    D = float(np.mean([d[p] for p in band]))
    ci = boot([d[p] for p in band], rng)
    n = len(band)
    verdict = "holds" if n >= 50 and ci[0] >= 0.05 else "refuted" if ci[1] < 0.05 else "undecided"

    def sub_D(ps, kk=None, order_rng=None):
        out = []
        for p in ps:
            k = (kk or KK)[p]
            o = tuple(order_rng.permutation(12)) if order_rng is not None else tuple(range(12))
            s, m = arms(k, o)
            out.append(s - m)
        return out

    lo = [p for p in band if right[p] <= 4]
    hi = [p for p in band if right[p] >= 5]
    edge = [p for p in probs if right[p] in (1, 11)]
    shuf = sub_D(band, order_rng=np.random.default_rng(1))
    other = sub_D(band, kk=Kt if primary == "plan" else K)
    rep = []
    for p in band:
        wk = [x for x in KK[p] if x not in (None, "R")]
        rep += [wk.count(x) >= 2 for x in wk]

    def summ(x):
        return {"D": round(float(np.mean(x)), 4), "ci90": boot(x, np.random.default_rng(0)), "n": len(x)} if x else None

    metrics = {
        "mechanism": "run-08/f2-m05", "spec": "studies/theory/specs/SPEC_direct_scatter4.md", "source": str(SRC),
        "statistic": "D = mean over band problems of V4_S - V4_M (vote over 4, all 495 subsets; S real wrong keys, M every finished wrong key merged)",
        "check_team_vote_k4_samples_0_3": n4, "check_team_vote_k12": n12,
        "check_plan_rule_vote_k12": plan12, "check_team_rule_keys_vote_k12": team12, "primary_abstention": primary,
        "planted_all_wrong_one_key_D": planted,
        "n": n, "D": round(D, 4), "ci90": ci, "null_value": 0.0, "threshold": 0.05,
        "V4_S_mean": round(float(np.mean([res[p][0] for p in band])), 4), "V4_M_mean": round(float(np.mean([res[p][1] for p in band])), 4),
        "verdict": verdict,
        "rule": "holds if n >= 50 and 90 % lower end >= 0.05; refuted if 90 % upper end < 0.05; else undecided",
        "bootstrap": "10,000 resamples of band problems, numpy default_rng(0), 90 % percentile interval",
        "descriptive": {
            "share_finished_wrong_key_repeats": round(float(np.mean(rep)), 4), "finished_wrong_samples": len(rep),
            "problems_d_positive": sum(d[p] > 0 for p in band), "problems_d_zero": sum(d[p] == 0 for p in band),
            "problems_d_negative": sum(d[p] < 0 for p in band),
            "D_r_2_4": summ([d[p] for p in lo]), "D_r_5_10": summ([d[p] for p in hi]),
            "D_r_1_or_11": summ(sub_D(edge)), "D_shuffled_order": summ(shuf),
            "D_other_abstention_rule": summ(other),
            "hard328": "not computed: day1_3/hard328_base_cue_s4r2-01 stores 4-12 rows per problem (191 of 328 have 4), not 12 samples",
        },
        "per_problem": {str(p): {"right": right[p], "V4_S": round(res[p][0], 4), "V4_M": round(res[p][1], 4), "keys": KK[p]} for p in band},
    }
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    def item(p, counts):
        r = rows[p]
        return {"problem_index": p, "counts_for_statistic": counts, "gold": r[0]["gold"], "right": right[p],
                "V4_S": res[p][0] if p in res else None, "V4_M": res[p][1] if p in res else None, "d": d.get(p), "keys": KK[p],
                "answers": [{"sample": s, "extracted_v3": r[s]["extracted_v3"], "score_v3": r[s]["score_v3"], "cap_hit": r[s]["cap_hit"]} for s in range(12)]}

    yes = max(band, key=lambda p: d[p])
    no = next(p for p in probs if right[p] == 12)
    (OUT / "examples.json").write_text(json.dumps([item(yes, True), {**item(no, False), "why_not": "r = 12, outside the 2-10 band"}], indent=1) + "\n")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({"spec": metrics["spec"], "commit": commit, "board": "work-bc42f2",
        "command": "uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_scatter4",
        "inputs": [str(SRC)]}, indent=1) + "\n")
    print({k: v for k, v in metrics.items() if k != "per_problem"})


if __name__ == "__main__":
    main()
