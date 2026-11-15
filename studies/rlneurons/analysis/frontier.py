"""Token frontier (specs/SPEC_frontier.md): right answers against generated tokens per problem for the base with the cue and
for RL, under reward-free test-time rules replayed on the stored rows of two run_cell --samples 4 --restarts 2 runs.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.frontier \
        --base studies/rlneurons/results/day1_3/math500_base_cue-01 --rl studies/rlneurons/results/day1_3/math500_rl-01 \
        --out studies/rlneurons/results/frontier/math500-01 [--fixed <chosen.json of another set>] [--base-run runs/<job>] [--rl-run runs/<job>]

  --base, --rl          run folders of analysis/day1_vote.py: rows.jsonl and metrics.json.
  --out                 a new run folder: run.json, readout.json, frontier.md, frontier.json, examples.json, chosen.json.
  --fixed               scores only `single` and the rules of a chosen.json made on another problem set; nothing is chosen.
  --base-run, --rl-run  optional job folders with answers.jsonl: adds the prompt and the end of each text to the examples.

A rule sees n_new, cap_hit and extracted_v3 of each attempt, never score_v3 or gold (`blind`). Tokens of a problem = every
generated token of every attempt the rule drew; a sample abandoned at L costs L.
"""
from __future__ import annotations

import argparse
import functools
import itertools
import json
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import day1_length_rules as LR
from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.analysis import selector as SEL
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

BOOT, FOLDS = 5000, 5
BUDGETS = (5000, 7500, 10000, 12500, 15000, 17500, 20000)
SPEC = "studies/rlneurons/specs/SPEC_frontier.md"
SEEN = ("n_new", "cap_hit", "extracted_v3")          # all a rule receives of an attempt
TIE = {"low": SEL.RULES["vote"], "short": SEL.RULES["tie_short"]}
SEQ = [2, 1, 1]                                      # batches of the sequential vote: stop after a batch when two agree

RULES = {
    "single": {"plan": [1]},
    "restart": {"plan": [1], "mode": "restart"},
    "R8000": {"R": 8000},
    "R12000": {"R": 12000},
    "vote2": {"plan": [2]}, "vote3": {"plan": [3]}, "vote4": {"plan": [4]},
    "vote2_short": {"plan": [2], "tie": "short"}, "vote3_short": {"plan": [3], "tie": "short"}, "vote4_short": {"plan": [4], "tie": "short"},
    "vote4_restart": {"plan": [4], "mode": "restart"},
    "vote4_restart_short": {"plan": [4], "mode": "restart", "tie": "short"},
    "seq3": {"plan": [2, 1]},
    "seq4": {"plan": SEQ},
    "seq4_short": {"plan": SEQ, "tie": "short"},
    "seq_2then4": {"plan": [2, 2]},
    "seq_2then4_short": {"plan": [2, 2], "tie": "short"},
    "seq4_restart": {"plan": SEQ, "mode": "restart"},
    "seq4_restart_short": {"plan": SEQ, "mode": "restart", "tie": "short"},
    "seq4_stop1000": {"plan": [1, 1, 1, 1], "stop_n": 1000},
    "seq4_stop2000": {"plan": [1, 1, 1, 1], "stop_n": 2000},
    "seq4_L8000": {"plan": SEQ, "L": 8000},
    "seq4_L12000": {"plan": SEQ, "L": 12000},
    "par4_m2": {"par": True},
}
NOT_CANDIDATES = ("par4_m2",)
TEXT = {
    "single": "one sample", "restart": "one sample, sampled again after a cap hit (up to 2 times)",
    "R8000": "one sample, abandoned at 8,000 tokens and drawn again", "R12000": "one sample, abandoned at 12,000 tokens and drawn again",
    "vote2": "vote over 2", "vote3": "vote over 3", "vote4": "vote over 4",
    "vote2_short": "vote over 2, ties to the shortest finished sample", "vote3_short": "vote over 3, ties to the shortest finished sample",
    "vote4_short": "vote over 4, ties to the shortest finished sample",
    "vote4_restart": "vote over 4 after restart", "vote4_restart_short": "vote over 4 after restart, ties to the shortest",
    "seq3": "sequential vote: stop when two agree, at most 3 samples", "seq4": "sequential vote: stop when two agree, at most 4 samples",
    "seq4_short": "sequential vote, at most 4, ties to the shortest finished sample",
    "seq_2then4": "draw 2; if they differ draw 2 more; vote", "seq_2then4_short": "draw 2; if they differ draw 2 more; vote, ties to the shortest",
    "seq4_restart": "sequential vote, at most 4, each sample restarted after a cap hit",
    "seq4_restart_short": "sequential vote, at most 4, restarts, ties to the shortest",
    "seq4_stop1000": "sequential vote, at most 4; a finished answer of at most 1,000 tokens is accepted at once",
    "seq4_stop2000": "sequential vote, at most 4; a finished answer of at most 2,000 tokens is accepted at once",
    "seq4_L8000": "sequential vote, at most 4, samples abandoned at 8,000 tokens", "seq4_L12000": "sequential vote, at most 4, samples abandoned at 12,000 tokens",
    "par4_m2": "4 in parallel, all stop when two finished answers agree",
}


def blind(chains: list) -> list:
    """The chains of one problem as a rule sees them: n_new, cap_hit, extracted_v3 and an id; no score, no gold."""
    return [[{**{k: a[k] for k in SEEN}, "id": (s, j)} for j, a in enumerate(c)] for s, c in enumerate(chains)]


def _v(rows: list) -> list:
    """day1_vote.vote and day1_length_rules.apply read score_v3 of the row they return; a rule has none, so it passes 0."""
    return [{**r, "score_v3": 0} for r in rows]


def winner(drawn: list, tie: str):
    """The index in `drawn` of the plurality answer, or None when no drawn sample has an answer."""
    groups = V.vote(_v(drawn))["groups"]
    return TIE[tie](drawn, groups) if groups else None


def agreed(drawn: list) -> bool:
    return any(len(g) >= 2 for g in V.vote(_v(drawn))["groups"])


def decide(rule: dict, chains: list) -> dict:
    """One problem under one rule. chains: blind chains in draw order. Returns answer (the id of the attempt answered with, or
    None), tokens, drawn (samples started) and ran_out (the last stored sample ran in full although it exceeded L)."""
    first = [c[0] for c in chains]
    if "R" in rule:
        o = LR.apply(_v(first), None, rule["R"])
        return {"answer": first[o["answer"]]["id"], "tokens": o["tokens"], "drawn": o["answer"] + 1,
                "ran_out": o["answer"] == len(first) - 1 and first[-1]["n_new"] > rule["R"]}
    if rule.get("par"):
        pairs = [(max(a["n_new"], b["n_new"]), i) for i, a in enumerate(first) for b in first[i + 1:]
                 if a["extracted_v3"] is not None and b["extracted_v3"] is not None and R.agree(R.norm_v3(a["extracted_v3"]), R.norm_v3(b["extracted_v3"]))]
        if not pairs:
            return decide(RULES["vote4"], chains)
        t, i = min(pairs)
        return {"answer": first[i]["id"], "tokens": sum(min(r["n_new"], t) for r in first), "drawn": len(first), "ran_out": False}
    L, drawn, ran_out = rule.get("L"), [], False
    for size in rule["plan"]:
        for _ in range(size):
            c = chains[len(drawn)]
            d = {**c[-1], "cost": sum(a["n_new"] for a in c)} if rule.get("mode") == "restart" else {**c[0], "cost": c[0]["n_new"]}
            if L and d["n_new"] > L:
                if len(drawn) < len(chains) - 1:
                    d = {"n_new": L, "cap_hit": True, "extracted_v3": None, "cost": L, "id": d["id"]}     # abandoned: no vote
                else:
                    ran_out = True
            drawn.append(d)
            if rule.get("stop_n") and not d["cap_hit"] and d["extracted_v3"] is not None and d["n_new"] <= rule["stop_n"]:
                return {"answer": d["id"], "tokens": sum(x["cost"] for x in drawn), "drawn": len(drawn), "ran_out": ran_out}
        if agreed(drawn):
            break
    k = winner(drawn, rule.get("tie", "low"))
    return {"answer": None if k is None else drawn[k]["id"], "tokens": sum(x["cost"] for x in drawn), "drawn": len(drawn), "ran_out": ran_out}


def outcome(rule, chains: list, order=None) -> dict:
    """decide on blind chains in `order` (default: stored), then the score of the answering attempt. rule: a RULES entry or any
    function of the blind chains that returns decide's dict."""
    order = order or range(len(chains))
    b = blind(chains)
    o = (rule if callable(rule) else functools.partial(decide, rule))([b[s] for s in order])
    s, j = o["answer"] if o["answer"] is not None else (None, None)
    return {**o, "score": 0 if s is None else chains[s][j]["score_v3"]}


def replay(ch: dict, rules: dict) -> dict:
    """{rule: per-problem lists}: s0, t0, d0, out0 (score, tokens, samples drawn, ran out; stored order) and s, t (means over
    the 24 draw orders)."""
    idxs = sorted(ch)
    orders = list(itertools.permutations(range(len(ch[idxs[0]]))))
    per = {}
    for m, rule in rules.items():
        o0 = [outcome(rule, ch[i]) for i in idxs]
        oa = [[outcome(rule, ch[i], p) for p in orders] for i in idxs]
        per[m] = {"s0": [o["score"] for o in o0], "t0": [o["tokens"] for o in o0], "d0": [o["drawn"] for o in o0],
                  "out0": [int(o["ran_out"]) for o in o0], "answer0": [o["answer"] for o in o0],
                  "s": [float(np.mean([o["score"] for o in x])) for x in oa], "t": [float(np.mean([o["tokens"] for o in x])) for x in oa]}
    return per


def table_row(p: dict) -> dict:
    n = len(p["s0"])
    return {**V.row(p["s0"], sum(p["t0"])), "right_24": sum(p["s"]), "tokens_per_problem_24": sum(p["t"]) / n,
            "samples_drawn": sum(p["d0"]) / n, "ran_out": sum(p["out0"])}


def ratio_interval(a, b) -> tuple:
    """Bootstrap 95 % interval of sum(a) / sum(b) over problems (paired, BOOT resamples, seed 0)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    idx = np.random.default_rng(0).integers(0, len(a), size=(BOOT, len(a)))
    r = a[idx].sum(1) / b[idx].sum(1)
    return (float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5)))


def diff(x, y) -> dict:
    return {"points": 100 * (sum(x) - sum(y)) / len(x), "interval95": S.paired_bootstrap(x, y, BOOT)}


def choose(per: dict, budget: float, js: list, names: list):
    """The candidate with the most right (24-order mean) on problems js among those whose tokens per problem there fit the
    budget; a draw goes to fewer tokens, then to the earlier rule. None when no rule fits."""
    fit = [m for m in names if sum(per[m]["t"][j] for j in js) / len(js) <= budget]
    return max(fit, key=lambda m: (round(sum(per[m]["s"][j] for j in js), 6), -sum(per[m]["t"][j] for j in js), -names.index(m))) if fit else None


def select(per: dict, budget: float, names: list) -> dict:
    """Five folds: the rule chosen on four, scored on the fifth; and the rule chosen on all problems."""
    n = len(per[names[0]]["s"])
    s, s0, t, picks = [0.0] * n, [0] * n, [0.0] * n, []
    for f in range(FOLDS):
        m = choose(per, budget, [j for j in range(n) if j % FOLDS != f], names)
        assert m is not None, f"no rule fits {budget} tokens per problem"
        picks.append(m)
        for j in range(f, n, FOLDS):
            s[j], s0[j], t[j] = per[m]["s"][j], per[m]["s0"][j], per[m]["t"][j]
    return {"budget": budget, "chosen_per_fold": picks, "chosen_on_all": choose(per, budget, list(range(n)), names),
            "held_out_right_24": sum(s), "held_out_right_stored_order": sum(s0), "held_out_tokens_per_problem_24": sum(t) / n,
            "held_out_wilson95": S.wilson(round(sum(s)), n), "per_problem_24": s}


def load(folder: pathlib.Path) -> tuple:
    m = json.loads((folder / "metrics.json").read_text())
    assert m["status"] == "done", f"{folder}: the run's status is {m['status']!r}, not done"
    rows = [json.loads(x) for x in (folder / "rows.jsonl").read_text().splitlines()]
    cfg = m["config"]
    assert cfg["samples"] == 4, "the rules are specified for four samples"
    return m, V.chains(rows, cfg["n_problems"], cfg["samples"], cfg["restarts"])


def example(ch: dict, p: dict, want: int, texts: dict):
    """The first problem where seq4 (stored order) stops after 2 samples with score `want`: all four attempt-0 rows."""
    idxs = sorted(ch)
    j = next((j for j in range(len(idxs)) if p["d0"][j] == 2 and p["s0"][j] == want), None)
    if j is None:
        return None
    first = [c[0] for c in ch[idxs[j]]]
    t = [texts.get((idxs[j], s, 0), {}) for s in range(len(first))]
    return {"problem_index": idxs[j], "gold": first[0]["gold"], "prompt": t[0].get("prompt"), "rule": "seq4", "samples_drawn": 2,
            "tokens": p["t0"][j], "tokens_vote4": sum(r["n_new"] for r in first), "score": want, "answer": p["answer0"][j],
            "samples": [{**{k: r[k] for k in ("sample", "seed", "n_new", "cap_hit", "extracted_v3", "score_v3")}, "drawn": s < 2,
                         "text_last_2000": t[s]["text"][-2000:] if t[s] else None} for s, r in enumerate(first)]}


def others() -> list:
    """Single-sample points of other weights from the committed exchange-rate table: context, not candidates."""
    path = pathlib.Path("studies/rlneurons/results/rate/math500-01/table.json")
    return [{"configuration": r["what"], "model": "other arm, one sample", "right": r["right"], "n": r["n"], "percent": 100 * r["right"] / r["n"],
             "tokens_per_problem": r["tokens_per_problem"], "signal": r["signal"], "source": str(path)}
            for r in json.loads(path.read_text()) if not r["arm"].startswith(("base_cue", "rl_plain"))]


def markdown(res: dict, extra: list) -> str:
    out = [f"# Token frontier, {res['set']}, n = {res['n']}, T 1.0 / top-p 1.0, grader v3", "",
           "Right: stored draw order. Right (24): mean over the 24 draw orders. Tokens: generated tokens per problem, stored order.", "",
           "| Configuration | Model | Right | Percent [95 %] | Right (24) | Tokens per problem | Training signal |", "|---|---|---|---|---|---|---|"]
    for model, label, signal in (("base", "base + cue", "none"), ("rl", "RL plain", "RL reward (weights)")):
        for m, r in sorted(res["models"][model]["rows"].items(), key=lambda kv: kv[1]["tokens_per_problem"]):
            out.append(f"| {TEXT[m]} (`{m}`) | {label} | {r['right']} | {r['percent']:.1f} [{r['wilson95'][0]:.1f}, {r['wilson95'][1]:.1f}] | "
                       f"{r['right_24']:.1f} | {r['tokens_per_problem']:,.0f} | {signal} |")
    for r in extra:
        out.append(f"| {r['configuration']} | {r['model']} | {r['right']:g} | {r['percent']:.1f} | | {r['tokens_per_problem']:,.0f} | {r['signal']} |")
    if "base_minus_rl_single" in res:
        out += ["", "## Base rule against one RL sample (24-order means; paired bootstrap, 5,000 resamples)", "",
                "| Base rule | Base right (24) | minus RL single, points [95 %] | Tokens, multiple of one RL sample [95 %] | RL under the same rule (24) | RL minus base, points [95 %] |",
                "|---|---|---|---|---|---|"]
        for m, c in sorted(res["base_minus_rl_single"].items(), key=lambda kv: kv[1]["token_multiple"]):
            e = res["rl_minus_base"][m]
            out.append(f"| `{m}` | {res['models']['base']['rows'][m]['right_24']:.1f} | {c['points']:+.1f} [{c['interval95'][0]:+.1f}, {c['interval95'][1]:+.1f}] | "
                       f"{c['token_multiple']:.2f} [{c['token_multiple_interval95'][0]:.2f}, {c['token_multiple_interval95'][1]:.2f}] | "
                       f"{res['models']['rl']['rows'][m]['right_24']:.1f} | {e['points']:+.1f} [{e['interval95'][0]:+.1f}, {e['interval95'][1]:+.1f}] |")
    if "selection" in res["models"]["base"]:
        out += ["", "## Rule chosen per token budget (5 folds: chosen on 4, scored on the 5th)", "",
                "| Model | Budget | Chosen on all | Chosen per fold | Held-out right (24) | Held-out tokens |", "|---|---|---|---|---|---|"]
        for model in ("base", "rl"):
            for s in res["models"][model]["selection"]:
                out.append(f"| {model} | {s['budget']:,} | `{s['chosen_on_all']}` | {', '.join(s['chosen_per_fold'])} | {s['held_out_right_24']:.1f} | "
                           f"{s['held_out_tokens_per_problem_24']:,.0f} |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    for k in ("--base", "--rl", "--out"):
        ap.add_argument(k, required=True)
    for k in ("--fixed", "--base-run", "--rl-run"):
        ap.add_argument(k, default=None)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    R.agree, R.norm_v3 = functools.lru_cache(maxsize=None)(R.agree), functools.lru_cache(maxsize=None)(R.norm_v3)   # same pairs in 24 orders
    meta, ch = {}, {}
    for model in ("base", "rl"):
        meta[model], ch[model] = load(pathlib.Path(getattr(a, model)))
    assert sorted(ch["base"]) == sorted(ch["rl"]), "the two runs are not on the same problems"
    pset = meta["base"]["config"]["set"]
    assert meta["rl"]["config"]["set"] == pset
    rules, fixed = RULES, None
    if a.fixed:
        fixed = json.loads(pathlib.Path(a.fixed).read_text())
        assert fixed["set"] != pset, f"{a.fixed} was chosen on {pset}: the rules must be chosen on another set"
        keep = {"single"} | {m for model in fixed["chosen"].values() for m in model.values()}
        rules = {m: r for m, r in RULES.items() if m in keep}
    per = {model: replay(ch[model], rules) for model in ch}
    names = [m for m in rules if m not in NOT_CANDIDATES]
    res = {"set": pset, "n": len(ch["base"]), "spec": SPEC, "grader": "v3 (score_v3 as written by run_cell)", "budgets": BUDGETS,
           "fixed": a.fixed, "problem_indices": sorted(ch["base"]),
           "models": {model: {"rows": {m: table_row(per[model][m]) for m in rules}} for model in per}}
    rl1 = per["rl"]["single"]
    res["rl_single_24"] = {"right": sum(rl1["s"]), "tokens_per_problem": sum(rl1["t"]) / res["n"]}
    res["base_minus_rl_single"] = {m: {**diff(per["base"][m]["s"], rl1["s"]), "token_multiple": sum(per["base"][m]["t"]) / sum(rl1["t"]),
                                       "token_multiple_interval95": ratio_interval(per["base"][m]["t"], rl1["t"])} for m in rules}
    res["rl_minus_base"] = {m: diff(per["rl"][m]["s"], per["base"][m]["s"]) for m in rules}
    if fixed:
        res["chosen"] = fixed["chosen"]
    else:
        chosen = {}
        for model in per:
            sel = [select(per[model], b, names) for b in BUDGETS]
            res["models"][model]["selection"] = sel
            chosen[model] = {str(s["budget"]): s["chosen_on_all"] for s in sel}
    res["per_problem"] = {model: {m: {k: per[model][m][k] for k in ("s0", "t0", "d0", "s", "t")} for m in rules} for model in per}
    ex = {}
    for model in per:
        run = getattr(a, f"{model}_run")
        texts = {(r["problem_index"], r["sample"], r["attempt"]): r for r in map(json.loads, (pathlib.Path(run) / "answers.jsonl").read_text().splitlines())} if run else {}
        if "seq4" in rules:
            ex[model] = {"stops_at_2_right": example(ch[model], per[model]["seq4"], 1, texts), "stops_at_2_wrong": example(ch[model], per[model]["seq4"], 0, texts)}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    extra = [] if fixed else others()
    md = markdown(res, extra)
    out.mkdir(parents=True)
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(sys.argv), "spec": SPEC,
                                              "source_jobs": {k: meta[k]["job_id"] for k in meta}, "source_commits": {k: meta[k]["commit"] for k in meta}}, indent=1) + "\n")
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "frontier.md").write_text(md)
    (out / "frontier.json").write_text(json.dumps({"set": pset, "n": res["n"], "rows": [
        {"configuration": TEXT[m], "rule": m, "model": model, **res["models"][model]["rows"][m], "signal": "none" if model == "base" else "RL reward (weights)"}
        for model in ("base", "rl") for m in rules] + extra}, indent=1) + "\n")
    (out / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    if not fixed:
        (out / "chosen.json").write_text(json.dumps({"set": pset, "spec": SPEC, "budgets_tokens_per_problem": BUDGETS, "chosen": chosen}, indent=1) + "\n")
    print(md)


if __name__ == "__main__":
    main()
