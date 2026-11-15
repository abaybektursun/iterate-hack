"""One table from day1_length_rules.py --fixed run folders (one per model, each made with --base or --rl alone) and the
day1_vote.py run folders of the same joined runs: per model the rows single, the fixed rules, vote and pass@k, each with right,
Wilson interval, tokens per problem and the paired difference against that model's single row. With the RL folders also RL
minus base per row and the equal-tokens line: the base's fixed rule with the most right answers among those whose tokens per
problem do not exceed RL's single row (ties: fewer tokens), against RL single. Without them the base's table alone.
It scores nothing itself: every 0/1 comes from per_problem.tsv and readout.json of the given folders.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules_headline \
        --rules-base studies/rlneurons/results/day1_length_rules/<set>_base-<nn> --vote-base studies/rlneurons/results/day1_3/<base arm>-<nn> \
        [--rules-rl studies/rlneurons/results/day1_length_rules/<set>_rl-<nn> --vote-rl studies/rlneurons/results/day1_3/<rl arm>-<nn>] \
        --out studies/rlneurons/results/day1_length_rules/<set>_headline-<nn>

--out is a new folder: run.json, metrics.json.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

from studies.rlneurons.lib import n13_score as S

BOOT = 5000


def diff(x: list, y: list) -> dict:
    return {"points": 100 * (sum(x) - sum(y)) / len(x), "interval95": list(S.paired_bootstrap(x, y, BOOT))}


def model_rows(m: str, rules_dir: str, vote_dir: str) -> tuple:
    """(rows of the table, {row: per-problem 0/1 in problem order}) of one model."""
    rules = json.loads((pathlib.Path(rules_dir) / "metrics.json").read_text())
    assert rules["mode"] == "fixed" and list(rules["models"]) == [m], f"{rules_dir}: not a --fixed run of {m} alone"
    v = json.loads((pathlib.Path(vote_dir) / "readout.json").read_text())
    lines = (pathlib.Path(rules_dir) / "per_problem.tsv").read_text().splitlines()
    keys = lines[0].split("\t")[3:]
    assert keys[0] == "single" and keys == list(rules["models"][m]["rows"])
    per, idx = {k: [] for k in keys}, []
    for x in lines[1:]:
        f = x.split("\t")
        assert f[0] == m
        idx.append(int(f[1]))
        for k, c in zip(keys, f[3:]):
            per[k].append(int(c.split(" ")[0]))
    assert idx == v["problem_indices"] and per["single"] == v["per_problem"]["single"], f"{m}: the rules run and the vote run are not the same rows"
    rows = {}
    for k in keys:
        r = rules["models"][m]["rows"][k]
        assert sum(per[k]) == r["right"]
        rows[k] = {f: r[f] for f in ("right", "n", "percent", "wilson95", "tokens_per_problem", "minus_single", "fixed", "broke")}
    for k in ("vote", "pass_at_k"):
        per[k] = v["per_problem"][k]
        rows[k] = {**v["rows"][k], "minus_single": diff(per[k], per["single"]),
                   "fixed": sum(q > p for p, q in zip(per["single"], per[k])), "broke": sum(q < p for p, q in zip(per["single"], per[k]))}
    return rows, per, idx, {"set": rules["set"], "n": rules["n"], "samples": v["samples"], "restarts": v["restarts"], "fixed_from": rules["fixed_from"]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("--rules-base", "--vote-base", "--out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--rules-rl", default=None)
    ap.add_argument("--vote-rl", default=None)
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    assert bool(a.rules_rl) == bool(a.vote_rl), "give both RL folders or neither"
    table, per, idx, info = {}, {}, {}, {}
    table["base"], per["base"], idx["base"], info["base"] = model_rows("base", a.rules_base, a.vote_base)
    if a.rules_rl:
        table["rl"], per["rl"], idx["rl"], info["rl"] = model_rows("rl", a.rules_rl, a.vote_rl)
        assert idx["rl"] == idx["base"] and info["rl"] == info["base"], "the two models are not on the same problems, samples and fixed setting"
    keys = list(table["base"])
    res = {**info["base"], "bootstrap_resamples": BOOT, "sources": {k: v for k, v in vars(a).items() if k != "out"}, "rows": table}
    if a.rules_rl:
        res["rl_minus_base"] = {k: diff(per["rl"][k], per["base"][k]) for k in keys}
        rules_keys = [k for k in keys if k not in ("single", "vote", "pass_at_k")]
        budget = table["rl"]["single"]["tokens_per_problem"]
        within = [k for k in rules_keys if table["base"][k]["tokens_per_problem"] <= budget]
        best = min(within, key=lambda k: (-table["base"][k]["right"], table["base"][k]["tokens_per_problem"])) if within else None
        res["equal_tokens"] = {
            "budget_tokens_per_problem": budget, "budget_is": "RL single row, same problems", "candidates": rules_keys, "within_budget": within,
            "base_setting": best,
            "base": None if best is None else {**{f: table["base"][best][f] for f in ("right", "n", "percent", "wilson95", "tokens_per_problem")},
                                               "minus_rl_single": diff(per["base"][best], per["rl"]["single"])},
            "base_single_minus_rl_single": diff(per["base"]["single"], per["rl"]["single"])}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
                            cwd=pathlib.Path(__file__).resolve().parent).stdout.strip()
    out.mkdir(parents=True)
    (out / "run.json").write_text(json.dumps({"analysis_commit": commit, "command": sys.argv if argv is None else list(argv), "sources": res["sources"]}, indent=1) + "\n")
    (out / "metrics.json").write_text(json.dumps(res, indent=1) + "\n")
    for m in table:
        for k, r in table[m].items():
            d = r["minus_single"]
            g = res["rl_minus_base"][k] if a.rules_rl else None
            print(f"{m:4s} {k:13s} {r['right']:3d}/{r['n']} {r['percent']:5.1f} [{r['wilson95'][0]:.1f}, {r['wilson95'][1]:.1f}] {r['tokens_per_problem']:7.0f} tok  "
                  f"vs single {d['points']:+5.1f} [{d['interval95'][0]:+.1f}, {d['interval95'][1]:+.1f}] fixed {r['fixed']} broke {r['broke']}"
                  + (f"  RL-base {g['points']:+5.1f} [{g['interval95'][0]:+.1f}, {g['interval95'][1]:+.1f}]" if g else ""))
    if a.rules_rl:
        print(json.dumps(res["equal_tokens"]))


if __name__ == "__main__":
    main()
