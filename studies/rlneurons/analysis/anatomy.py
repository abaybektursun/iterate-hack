"""Gap anatomy (specs/SPEC_anatomy.md, idea-9e3dff): where the RL-minus-base gap of the Day-1 #3 four-sample runs sits.
Attempt 0 of samples 0 to 3 of both models, grader v3 scores as stored by run_cell.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.anatomy \
        --base runs/abaybektursun-1114-153825-208b --rl runs/abaybektursun-1114-183640-e828 \
        --out studies/rlneurons/results/anatomy/math500-01

Writes readout.json (analyses a to e of the spec), examples.json, pool_k_le3.json, pairs.json (the divergence pairs with
the proxy's position, for the hand check) and run.json. Fails if the run is unfinished or the out folder exists.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import re
import subprocess
import sys
from math import comb

import numpy as np

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.lib import n13_score as S

HERE = pathlib.Path(__file__).resolve().parent.parent
BOOT, K = 5000, 4
NUM = re.compile(r"\d+\.\d+|\d{2,}")


def load(run: pathlib.Path) -> dict:
    """{problem index: [attempt 0 of sample 0, ..., of sample 3]}; V.chains asserts the run is complete."""
    rows = [json.loads(l) for l in (run / "answers.jsonl").open()]
    cfg = json.loads((run / "metrics.json").read_text())["config"]
    assert cfg["samples"] == K, cfg["samples"]
    ch = V.chains(rows, cfg["n_problems"], K, cfg["restarts"])
    return {i: [c[0] for c in ch[i]] for i in sorted(ch)}


def kind(r: dict) -> str:
    if r["score_v3"]:
        return "right"
    return "cap_hit" if r["cap_hit"] else "no_answer" if r["extracted_v3"] is None else "finished_wrong"


def boot_share(contrib: np.ndarray, seed: int = 0) -> list:
    """contrib[problem, class] in samples. Per class: share of the total and its 95 % bootstrap interval over problems."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(contrib), (BOOT, len(contrib)))
    tot = contrib[idx].sum(1)                                    # BOOT x classes
    sh = tot / tot.sum(1, keepdims=True)
    return [{"share": float(contrib[:, c].sum() / contrib.sum()), "ci95": [float(x) for x in np.percentile(sh[:, c], [2.5, 97.5])]}
            for c in range(contrib.shape[1])]


def boot_mean(x: np.ndarray, seed: int = 0) -> list:
    rng = np.random.default_rng(seed)
    return [float(v) for v in np.percentile(x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1), [2.5, 97.5])]


def joint(B: np.ndarray, Rl: np.ndarray) -> dict:
    b, r = B.sum(1), Rl.sum(1)
    gap = int(r.sum() - b.sum())
    table = [[int(((b == i) & (r == j)).sum()) for j in range(K + 1)] for i in range(K + 1)]
    share = [[table[i][j] * (j - i) / gap for j in range(K + 1)] for i in range(K + 1)]
    pb, pr = b.sum() / b.size / K, r.sum() / r.size / K
    binom = lambda p: [comb(K, k) * p ** k * (1 - p) ** (K - k) for k in range(K + 1)]
    null = [[len(b) * x * y for y in binom(pr)] for x in binom(pb)]
    contrib = np.zeros((len(b), K + 1))
    contrib[np.arange(len(b)), b] = r - b
    return {"base_right_samples": int(b.sum()), "rl_right_samples": int(r.sum()), "gap_samples": gap,
            "table_rows_base_k_cols_rl_k": table, "gap_share_per_cell": share,
            "gross_gain_samples": int((r - b)[r > b].sum()), "gross_loss_samples": int((b - r)[b > r].sum()),
            "gap_share_by_base_k": boot_share(contrib),
            "gap_share_base_k_ge2": float(sum(share[i][j] for i in range(2, K + 1) for j in range(K + 1))),
            "base_k_hist": [int((b == k).sum()) for k in range(K + 1)], "rl_k_hist": [int((r == k).sum()) for k in range(K + 1)],
            "homogeneous_null": {"p_base": float(pb), "p_rl": float(pr), "expected_table": null,
                                 "base_k_hist": [len(b) * x for x in binom(pb)], "rl_k_hist": [len(b) * x for x in binom(pr)]}}


def held_out(B: np.ndarray, Rl: np.ndarray) -> dict:
    """Class problems by some samples, score the others (spec, 'What sampling noise alone predicts' 2 and 3)."""
    n = len(B)
    out = {}
    # leave one out: class by j right of 3, score the fourth, over the 4 choices of the held-out sample
    for name, X in (("class_by_base", B), ("class_by_rl", Rl)):
        cls = np.stack([X.sum(1) - X[:, h] for h in range(K)], 1)            # n x 4, values 0..3
        rows = []
        contrib = np.zeros((n, K))
        for j in range(K):
            m = cls == j
            contrib[:, j] = ((Rl - B) * m).sum(1)
            rows.append({"j_right_of_3": j, "problem_holdouts": int(m.sum()), "problems_per_holdout": m.sum() / K,
                         "base_held_out_right": int(B[m].sum()), "rl_held_out_right": int(Rl[m].sum()),
                         "base_held_out_rate": float(B[m].mean()) if m.any() else None,
                         "rl_held_out_rate": float(Rl[m].mean()) if m.any() else None})
        for row, s in zip(rows, boot_share(contrib)):
            row["held_out_gap_share"] = s
        out["leave_one_out_" + name] = rows
    # halves: class by the base's k of 2 on one half, score both models on the other; 3 pairings, both directions
    contrib, cnt, bs, rs = np.zeros((n, 3)), np.zeros(3), np.zeros(3), np.zeros(3)
    corr = {"base": [], "rl": []}
    for a in ((0, 1), (0, 2), (0, 3)):
        o = tuple(s for s in range(K) if s not in a)
        corr["base"].append(float(np.corrcoef(B[:, a].sum(1), B[:, o].sum(1))[0, 1]))
        corr["rl"].append(float(np.corrcoef(Rl[:, a].sum(1), Rl[:, o].sum(1))[0, 1]))
        for sel, tst in ((a, o), (o, a)):
            c = B[:, sel].sum(1)
            for k in range(3):
                m = c == k
                contrib[:, k] += (Rl[:, tst].sum(1) - B[:, tst].sum(1)) * m
                cnt[k] += m.sum()
                bs[k] += B[:, tst][m].sum()
                rs[k] += Rl[:, tst][m].sum()
    rows = [{"base_k_of_2_on_selection_half": k, "problems_mean_over_6_splits": cnt[k] / 6,
             "base_test_half_rate": bs[k] / (2 * cnt[k]), "rl_test_half_rate": rs[k] / (2 * cnt[k]),
             "held_out_gap_share": s} for k, s in zip(range(3), boot_share(contrib))]
    out["halves_class_by_base"] = rows
    out["half_to_half_correlation_of_k_of_2"] = {m: {"three_pairings": v, "mean": float(np.mean(v))} for m, v in corr.items()}
    return out


def by_group(B, Rl, meta, key) -> list:
    d = Rl.sum(1) - B.sum(1)
    gap, rows = d.sum(), []
    for g in sorted({m[key] for m in meta}):
        m = np.array([x[key] == g for x in meta])
        contrib = np.stack([d * m, d * ~m], 1).astype(float)
        rows.append({key: g, "problems": int(m.sum()), "share_of_problems": float(m.mean()),
                     "base_right_samples": int(B[m].sum()), "rl_right_samples": int(Rl[m].sum()),
                     "base_rate": float(B[m].mean()), "base_wilson95": S.wilson(int(B[m].sum()), int(B[m].size)),
                     "rl_rate": float(Rl[m].mean()), "rl_wilson95": S.wilson(int(Rl[m].sum()), int(Rl[m].size)),
                     "gap_samples": int(d[m].sum()), "gap_samples_per_problem": float(d[m].mean()),
                     "gap_per_problem_ci95": boot_mean(d[m].astype(float)), "share_of_gap": boot_share(contrib)[0]})
    return rows


def error_types(own: dict, other: dict) -> dict:
    """Each wrong sample of `own` by type, and what `other`'s four samples do on the same problem."""
    out = {}
    for t in ("finished_wrong", "cap_hit", "no_answer"):
        ws = [(i, r) for i in own for r in own[i] if kind(r) == t]
        ok = [kind(r) for i, _ in ws for r in other[i]]
        probs = sorted({i for i, _ in ws})
        out[t] = {"samples": len(ws), "problems": len(probs),
                  "other_model_samples_on_same_problems": {k: ok.count(k) for k in ("right", "finished_wrong", "cap_hit", "no_answer")},
                  "other_model_right_rate": ok.count("right") / len(ok) if ok else None,
                  "other_model_right_rate_wilson95": S.wilson(ok.count("right"), len(ok)) if ok else None,
                  "own_k_of_4_on_those_problems_hist": [sum(sum(r["score_v3"] for r in own[i]) == k for i in probs) for k in range(K + 1)],
                  "median_tokens": float(np.median([r["n_new"] for _, r in ws])) if ws else None}
    return out


def tokens(S_: dict) -> dict:
    rs = [r for i in S_ for r in S_[i]]
    q = lambda xs: {"n": len(xs), "mean": float(np.mean(xs)), "median": float(np.median(xs))} if xs else {"n": 0}
    out = {"right": q([r["n_new"] for r in rs if r["score_v3"]]), "wrong": q([r["n_new"] for r in rs if not r["score_v3"]]),
           "wrong_finished": q([r["n_new"] for r in rs if not r["score_v3"] and not r["cap_hit"]])}
    for name, keep in (("all_wrong", lambda r: True), ("finished_only", lambda r: not r["cap_hit"])):
        d = []
        for i in S_:
            right = [r["n_new"] for r in S_[i] if r["score_v3"]]
            wrong = [r["n_new"] for r in S_[i] if not r["score_v3"] and keep(r)]
            if right and wrong:
                d.append((np.mean(wrong), np.mean(right)))
        d = np.array(d)
        out["within_problem_" + name] = {"problems": len(d), "mean_tokens_wrong": float(d[:, 0].mean()), "mean_tokens_right": float(d[:, 1].mean()),
                                         "wrong_minus_right": float((d[:, 0] - d[:, 1]).mean()), "ci95": boot_mean(d[:, 0] - d[:, 1]),
                                         "problems_wrong_longer": int((d[:, 0] > d[:, 1]).sum())}
    return out


def first_new_number(text: str, known: set):
    """The spec's proxy: (relative character offset, number) of the first number of `text` absent from `known`, or None."""
    for m in NUM.finditer(text):
        if m.group() not in known:
            return m.start() / len(text), m.group()
    return None


def divergence(S_: dict, problems: list) -> tuple:
    pairs, control = [], []
    for i in S_:
        b = sum(r["score_v3"] for r in S_[i])
        if not 1 <= b <= 3:
            continue
        pnum = set(NUM.findall(problems[i]["problem"]))
        right = [r for r in S_[i] if r["score_v3"]]
        for w in S_[i]:
            if kind(w) != "finished_wrong":
                continue
            p = first_new_number(w["text"], pnum | {x for r in right for x in NUM.findall(r["text"])})
            pairs.append({"problem_index": i, "base_k": b, "wrong_sample": w["sample"], "right_samples": [r["sample"] for r in right],
                          "proxy_position": p and p[0], "proxy_number": p and p[1], "wrong_chars": len(w["text"])})
        for c in right:                                           # control: a right sample against its right siblings
            sib = [r for r in right if r is not c]
            if sib:
                p = first_new_number(c["text"], pnum | {x for r in sib for x in NUM.findall(r["text"])})
                control.append({"problem_index": i, "base_k": b, "siblings": len(sib), "proxy_position": p and p[0]})

    def summ(xs):
        pos = np.array([x["proxy_position"] for x in xs if x["proxy_position"] is not None])
        return {"n": len(xs), "no_new_number": len(xs) - len(pos), "median_position": float(np.median(pos)),
                "quartiles": [float(v) for v in np.percentile(pos, [25, 75])],
                "share_in_first_third": float((pos < 1 / 3).mean()), "share_in_last_third": float((pos > 2 / 3).mean())}
    s = {"wrong_vs_right_siblings": summ(pairs), "right_vs_right_siblings_control": summ(control),
         "wrong_by_number_of_right_siblings": {str(k): summ([x for x in pairs if x["base_k"] == k]) for k in (1, 2, 3)},
         "control_by_number_of_right_siblings": {str(k): summ([x for x in control if x["siblings"] == k]) for k in (1, 2)}}
    return s, pairs


def example(S_: dict, i: int, problems: list) -> dict:
    return {"problem_index": i, "problem": problems[i]["problem"], "gold": problems[i]["answer"],
            "samples": [dict(V.tail(r), kind=kind(r)) for r in S_[i]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--rl", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True)                                       # fails on an existing run folder
    base, rl = load(pathlib.Path(args.base)), load(pathlib.Path(args.rl))
    problems = json.loads((HERE / "data/rln4/math500.json").read_text())
    meta = json.loads((HERE / "data/anatomy/math500_meta.json").read_text())["rows"]
    assert list(base) == list(rl) == list(range(len(problems))) and all(m["unique_id"] == p["unique_id"] for m, p in zip(meta, problems))
    B = np.array([[r["score_v3"] for r in base[i]] for i in base])
    Rl = np.array([[r["score_v3"] for r in rl[i]] for i in rl])
    b, r = B.sum(1), Rl.sum(1)

    div, pairs = divergence(base, problems)
    readout = {"n_problems": len(B), "samples_per_problem": K, "a_joint": joint(B, Rl), "a_held_out": held_out(B, Rl),
               "b_by_subject": by_group(B, Rl, meta, "subject"), "b_by_level": by_group(B, Rl, meta, "level"),
               "c_base_errors_and_rl_on_same_problem": error_types(base, rl), "c_rl_errors_and_base_on_same_problem": error_types(rl, base),
               "d_tokens": {"base": tokens(base), "rl": tokens(rl)}, "e_divergence_proxy_base": div}
    (out / "readout.json").write_text(json.dumps(readout, indent=1))
    (out / "pairs.json").write_text(json.dumps(pairs, indent=0))
    (out / "pool_k_le3.json").write_text(json.dumps(
        {"what": "MATH-500 problems (index of data/rln4/math500.json) where the cued base has at most 3 right of 4 samples (attempt 0, T 1.0 / top-p 1.0, grader v3), with the right counts of both models",
         "source_jobs": {"base_cue": pathlib.Path(args.base).name, "rl": pathlib.Path(args.rl).name},
         "n": int((b <= 3).sum()), "problems": [{"index": i, "base_k": int(b[i]), "rl_k": int(r[i]), "subject": meta[i]["subject"], "level": meta[i]["level"],
                                                  "base_kinds": [kind(x) for x in base[i]]} for i in range(len(b)) if b[i] <= 3]}, indent=0))
    pick = lambda cond: int(np.flatnonzero(cond)[0])
    cap = next(i for i in base if any(kind(x) == "cap_hit" for x in base[i]))
    (out / "examples.json").write_text(json.dumps({
        "cell_base3_rl4 (base: 3 right samples and 1 wrong; RL: 4 right)": {"base": example(base, pick((b == 3) & (r == 4)), problems)},
        "cell_base0_rl4 (base: 4 wrong; RL: 4 right)": {"base": example(base, pick((b == 0) & (r == 4)), problems), "rl": example(rl, pick((b == 0) & (r == 4)), problems)},
        "cell_base4_rl_below (RL loses samples)": {"rl": example(rl, pick((b == 4) & (r < 4)), problems)},
        "base_cap_hit": {"base": example(base, cap, problems), "rl": example(rl, cap, problems)},
        "divergence_proxy_first_pair": pairs[0]}, indent=1))
    (out / "run.json").write_text(json.dumps({
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=HERE).stdout.strip(),
        "command": " ".join(sys.argv), "source_jobs": {"base_cue": pathlib.Path(args.base).name, "rl": pathlib.Path(args.rl).name},
        "grader": "v3 (score_v3 as stored by run_cell)", "rows": "attempt 0 of samples 0 to 3", "gpu": None}, indent=1))
    j = readout["a_joint"]
    print("gap", j["gap_samples"], "table", j["table_rows_base_k_cols_rl_k"])


if __name__ == "__main__":
    main()
