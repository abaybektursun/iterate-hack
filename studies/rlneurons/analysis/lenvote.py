"""lenvote (specs/SPEC_lenvote.md): a vote over stored samples weighted by agreement-calibrated answer length, beside the plain
vote, the vote with ties to the shortest, and the shortest sample alone. Offline; label-free rules.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.lenvote <name>=<rows.jsonl> ...

rows.jsonl: one row per problem and sample (problem_index, sample, attempt, n_new, cap_hit, extracted_v3, score_v3), as in
results/thinkvote/ and results/cap32vote/. Writes results/lenvote/<name>-01/ (run.json, readout.json, examples.json).
"""
import collections
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

OUT, BINS = pathlib.Path(__file__).resolve().parents[1] / "results" / "lenvote", 5


def groups(rows):
    g = []
    for k, r in enumerate(rows):
        if r["extracted_v3"] is None or r["cap_hit"]:
            continue
        n = R.norm_v3(r["extracted_v3"])
        for grp in g:
            if R.agree(n, grp["n"]):
                grp["k"].append(k)
                break
        else:
            g.append({"n": n, "k": [k]})
    return g


def readout(path):
    ch = collections.defaultdict(list)
    for r in map(json.loads, open(path)):
        if r.get("attempt", 0) == 0:
            ch[r["problem_index"]].append(r)
    idx = sorted(ch)
    ch = {i: sorted(ch[i], key=lambda r: r["sample"]) for i in idx}
    G = {i: groups(ch[i]) for i in idx}
    obs = [(ch[i][k]["n_new"], len(g["k"]) > 1) for i in idx for g in G[i] for k in g["k"]]     # label-free: length, shared answer
    L, A = np.array([o[0] for o in obs]), np.array([o[1] for o in obs])
    edges = np.quantile(L, np.linspace(0, 1, BINS + 1)[1:-1])
    b = np.searchsorted(edges, L)
    a = [(A[b == j].sum() + 1) / ((b == j).sum() + 2) for j in range(BINS)]
    wt = lambda n: math.log(a[int(np.searchsorted(edges, n))] / (1 - a[int(np.searchsorted(edges, n))]))
    per, picks = collections.defaultdict(list), {}
    for i in idx:
        rows, g = ch[i], G[i]
        short = lambda grp: min(rows[k]["n_new"] for k in grp["k"])
        rules = {"vote": lambda grp: (len(grp["k"]), -min(grp["k"])), "tie_short": lambda grp: (len(grp["k"]), -short(grp)),
                 "weighted": lambda grp: (sum(wt(rows[k]["n_new"]) for k in grp["k"]), -short(grp)), "shortest": lambda grp: -short(grp)}
        picks[i] = {m: max(g, key=key)["k"][0] if g else None for m, key in rules.items()}
        for m, k in picks[i].items():
            per[m].append(0 if k is None else rows[k]["score_v3"])
    out = {"rows": str(path), "n": len(idx), "samples_per_problem": len(ch[idx[0]]), "bin_upper_edges_tokens": [int(e) for e in edges],
           "shared_answer_rate_by_bin": [round(float(x), 3) for x in a],
           "right_rate_by_bin_for_the_reader_only": [round(float(np.mean([ch[i][k]["score_v3"] for i in idx for g in G[i] for k in g["k"]
                                                                          if int(np.searchsorted(edges, ch[i][k]["n_new"])) == j])), 3) for j in range(BINS)],
           "tokens_per_problem": round(sum(r["n_new"] for i in idx for r in ch[i]) / len(idx), 1), "rules": {}}
    for m, v in per.items():
        lo, hi = S.paired_bootstrap(v, per["vote"], n_boot=10000, seed=0)
        out["rules"][m] = {"right": sum(v), "minus_vote": {"problems": sum(v) - sum(per["vote"]), "points": round(100 * (sum(v) - sum(per["vote"])) / len(idx), 2),
                                                           "ci95": [round(lo, 2), round(hi, 2)]},
                           "wrong_to_right": sum(x > y for x, y in zip(v, per["vote"])), "right_to_wrong": sum(x < y for x, y in zip(v, per["vote"]))}
    lo, hi = S.paired_bootstrap(per["weighted"], per["tie_short"], n_boot=10000, seed=0)
    out["weighted_minus_tie_short"] = {"problems": sum(per["weighted"]) - sum(per["tie_short"]), "ci95_points": [round(lo, 2), round(hi, 2)]}
    show = lambda i: {"problem_index": i, "gold": ch[i][0]["gold"], "vote_pick": picks[i]["vote"], "weighted_pick": picks[i]["weighted"],
                      "samples": [{k: r[k] for k in ("sample", "n_new", "cap_hit", "extracted_v3", "score_v3")} for r in ch[i]]}
    flip = lambda want: next((show(i) for j, i in enumerate(idx) if per["weighted"][j] - per["vote"][j] == want), None)
    return out, {"weighted_right_vote_wrong": flip(1), "weighted_wrong_vote_right": flip(-1)}


for arg in sys.argv[1:]:
    name, path = arg.split("=")
    d = OUT / f"{name}-01"
    assert not d.exists(), f"{d} exists: a rerun gets the next number"
    out, ex = readout(path)
    d.mkdir(parents=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (d / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(sys.argv), "rows": path, "spec": "studies/rlneurons/specs/SPEC_lenvote.md"}, indent=1) + "\n")
    (d / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    (d / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    print(name, out["n"], {m: (v["right"], v["minus_vote"]["points"], v["minus_vote"]["ci95"], v["wrong_to_right"], v["right_to_wrong"]) for m, v in out["rules"].items()},
          "w-ts", out["weighted_minus_tie_short"], "shared", out["shared_answer_rate_by_bin"], "right", out["right_rate_by_bin_for_the_reader_only"], out["bin_upper_edges_tokens"], out["tokens_per_problem"])
