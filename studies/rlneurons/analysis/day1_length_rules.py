"""Day-1 length rules (specs/SPEC_day1_length_rules.md): two procedures scored offline from the rows of run_cell --samples 4
--restarts 2, for the base and the RL model. D(S): a finished answer of at most S tokens is checked against the next sample,
and against a third when the two differ. R(L): an answer longer than L tokens is stopped at L and the next sample is taken;
sample 3 runs in full. D(S)+R(L): the cutoff first, then the check on the answering sample. Only attempt 0 of samples 0-3 is
read. No rule reads the gold or a score; score_v3 of the answering sample scores the rule.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules \
        --base runs/<base job> --rl runs/<rl job> --out studies/rlneurons/results/day1_length_rules/<set>-<nn> [--choose | --fixed <chosen.json>]

  --base, --rl  run directories with answers.jsonl and metrics.json (uv run tools/gpu.py get <job-id>). One of them alone gives
                that model's rows. Both give also RL minus base per setting and the equal-tokens block (budget = RL single).
  --out         a new run folder: run.json, metrics.json, per_problem.tsv, examples.json, and chosen.json with --choose.
  --choose      MATH-500 only: writes the base's best setting within the budget (S, L) to chosen.json.
  --fixed       scores only the single row and the setting of a chosen.json made on another problem set (no choice is made).

Tokens of a problem = L for each stopped sample + n_new of the answering sample + n_new of each check sample.
Fail loud: an unfinished run is an assertion error (day1_vote.chains), as is a run with fewer than 4 samples.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.lib import n13_score as S

BOOT = 5000
K = 4                                           # samples a rule may take per problem: attempt 0 of samples 0..3
S_GRID = (None, 1000, 2000, 4000)               # None = off
L_GRID = (None, 8000, 10000, 12000)
GRID = [(s, l) for s in S_GRID for l in L_GRID]  # the first setting, (None, None), is the single row
SPEC = "studies/rlneurons/specs/SPEC_day1_length_rules.md"


def name(s, l) -> str:
    return "+".join(([f"D{s}"] if s else []) + ([f"R{l}"] if l else [])) or "single"


def apply(first: list, s, l) -> dict:
    """One problem under D(s)+R(l). first: its attempt-0 rows in sample order. s or l None = that rule off.
    Returns score, tokens, answer (the answering sample), stopped (samples stopped at l), used (the answering sample, then the
    check samples)."""
    j = 0
    if l is not None:
        while j < len(first) - 1 and first[j]["n_new"] > l:        # stopped at l; the last sample runs in full
            j += 1
    a = first[j]
    used, answer, score = [j], j, a["score_v3"]
    if s is not None and not a["cap_hit"] and a["n_new"] <= s and j + 1 < len(first):
        used.append(j + 1)
        v = V.vote([first[u] for u in used])
        if v["votes"] < 2 and j + 2 < len(first):                  # the two do not agree: a third sample, then the plurality
            used.append(j + 2)
            v = V.vote([first[u] for u in used])
        if v["winner"] is not None:                                # None: no sample used has an answer; sample j stays, score 0
            answer, score = used[v["winner"]], v["score"]
    return {"score": score, "tokens": j * (l or 0) + sum(first[u]["n_new"] for u in used), "answer": answer,
            "stopped": list(range(j)), "used": used}


def firsts(rows: list, cfg: dict) -> dict:
    """{problem index: attempt 0 of samples 0..K-1}. day1_vote.chains asserts that the run is complete."""
    assert cfg["samples"] >= K, f"the run has {cfg['samples']} samples per problem, the rules need {K}"
    ch = V.chains(rows, cfg["n_problems"], cfg["samples"], cfg["restarts"])
    return {i: [c[0] for c in ch[i][:K]] for i in sorted(ch)}


def load(run: pathlib.Path) -> tuple:
    m = json.loads((run / "metrics.json").read_text())
    assert m["status"] == "done", f"{run}: the run's status is {m['status']!r}, not done"
    rows = [json.loads(x) for x in (run / "answers.jsonl").read_text().splitlines()]
    return m, firsts(rows, m["config"])


def scores(outcomes: list) -> list:
    return [o["score"] for o in outcomes]


def diff(x: list, y: list) -> dict:
    return {"points": 100 * (sum(x) - sum(y)) / len(x), "interval95": S.paired_bootstrap(x, y, BOOT)}


def summarize(first: dict, pairs: list) -> tuple:
    """(readout of one model, {setting: per-problem outcomes in problem order}). pairs must start with (None, None)."""
    idxs = sorted(first)
    per = {name(s, l): [apply(first[i], s, l) for i in idxs] for s, l in pairs}
    single = scores(per["single"])
    rows = {}
    for s, l in pairs:
        k = name(s, l)
        sc = scores(per[k])
        rows[k] = {"S": s, "L": l, **V.row(sc, sum(o["tokens"] for o in per[k])), "minus_single": diff(sc, single),
                   "fixed": sum(b > a for a, b in zip(single, sc)), "broke": sum(b < a for a, b in zip(single, sc)),
                   "problems_with_a_check": sum(len(o["used"]) > 1 for o in per[k]),
                   "samples_stopped": sum(len(o["stopped"]) for o in per[k])}
    s0 = [first[i][0] for i in idxs]
    res = {"rows": rows,
           "sample_0": {"cap_hits": sum(r["cap_hit"] for r in s0),
                        "finished_with_at_most": {str(s): {"n": sum(not r["cap_hit"] and r["n_new"] <= s for r in s0),
                                                           "wrong": sum(not r["cap_hit"] and r["n_new"] <= s and not r["score_v3"] for r in s0)}
                                                  for s in S_GRID[1:]},
                        "longer_than": {str(l): {"right": sum(r["n_new"] > l and r["score_v3"] for r in s0),
                                                 "wrong": sum(r["n_new"] > l and not r["score_v3"] for r in s0)}
                                        for l in L_GRID[1:]}}}
    return res, per


def best(rows: dict, keys: list):
    """The setting with the most right answers; ties: fewer tokens per problem, then the order of keys."""
    return min(keys, key=lambda k: (-rows[k]["right"], rows[k]["tokens_per_problem"])) if keys else None


def equal_tokens(summ: dict, per: dict, pick) -> dict:
    """Budget = RL single tokens per problem. Per model: the best setting within the budget (pick None), or the setting pick
    as given (--fixed), with its difference against RL single."""
    budget = summ["rl"]["rows"]["single"]["tokens_per_problem"]
    out = {"budget_tokens_per_problem": budget, "budget_is": "RL single row (sample 0), same problems",
           "setting_is": "fixed by --fixed" if pick else "most right among settings within the budget; ties: fewer tokens, then grid order"}
    for m in ("base", "rl"):
        rows = summ[m]["rows"]
        k = pick or best(rows, [k for k in rows if rows[k]["tokens_per_problem"] <= budget])
        out[m] = None if k is None else {
            "setting": k, **{f: rows[k][f] for f in ("S", "L", "right", "n", "percent", "wilson95", "tokens_per_problem")},
            "within_budget": rows[k]["tokens_per_problem"] <= budget, "minus_rl_single": diff(scores(per[m][k]), scores(per["rl"]["single"]))}
    return out


def examples(first: dict, per: dict, keys: list) -> dict:
    """Per setting: the first problem the rule fixed (single wrong, rule right) and the first it broke, with every sample touched."""
    idxs = sorted(first)

    def one(k, want):
        p = next((p for p in range(len(idxs)) if (per["single"][p]["score"], per[k][p]["score"]) == want), None)
        if p is None:
            return None
        o, rows = per[k][p], first[idxs[p]]
        role = lambda u: "stopped at L (text beyond L was not generated under the rule)" if u in o["stopped"] else "answering" if u == o["used"][0] else "check"
        return {"problem_index": idxs[p], "gold": rows[0]["gold"], "prompt": rows[0]["prompt"], "single_score": want[0], "rule_score": want[1],
                "answer_sample": o["answer"], "tokens": o["tokens"], "samples": [{"role": role(u), **V.tail(rows[u])} for u in o["stopped"] + o["used"]]}

    return {k: {"fixed": one(k, (0, 1)), "broke": one(k, (1, 0))} for k in keys}


def cell(o: dict) -> str:
    """'right tokens samples'; in samples, x after a number = stopped at L, * = the sample answered with."""
    return (f"{o['score']} {o['tokens']} " + "".join(f"{u}x" for u in o["stopped"])
            + "".join(f"{u}*" if u == o["answer"] else str(u) for u in o["used"]))


def table(first: dict, per: dict, model: str) -> list:
    return ["\t".join([model, str(i), ",".join(str(r["n_new"]) for r in first[i])] + [cell(per[k][p]) for k in per])
            for p, i in enumerate(sorted(first))]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None)
    ap.add_argument("--rl", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--choose", action="store_true")
    ap.add_argument("--fixed", default=None)
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    assert a.base or a.rl, "give --base, --rl or both"
    assert not (a.choose and a.fixed), "--choose makes a choice, --fixed applies one: not both"
    src = {m: pathlib.Path(p) for m, p in (("base", a.base), ("rl", a.rl)) if p}
    both = len(src) == 2
    meta, first = {}, {}
    for m, p in src.items():
        meta[m], first[m] = load(p)
        assert meta[m]["config"]["model"] == m, f"--{m} is a run of model {meta[m]['config']['model']!r}"
    cfg = meta[next(iter(src))]["config"]
    if both:
        same = ("set", "temperature", "top_p", "max_tokens")
        assert all(meta["base"]["config"][k] == meta["rl"]["config"][k] for k in same), f"the two runs differ in one of {same}"
        assert sorted(first["base"]) == sorted(first["rl"]), "the two runs are not on the same problems"

    pairs, pick, mode = GRID, None, "choose" if a.choose else "grid"
    if a.fixed:
        ch = json.loads(pathlib.Path(a.fixed).read_text())
        assert ch["chosen_on"]["set"] != cfg["set"], f"{a.fixed} was chosen on {cfg['set']}: the choice is never made on the test set"
        s, l = ch["S"], ch["L"]
        assert (s, l) in GRID, f"{a.fixed}: S {s}, L {l} is not a setting of the grid"
        pairs, pick, mode = list(dict.fromkeys([(None, None), (s, None), (None, l), (s, l)])), name(s, l), "fixed"
    assert all(l is None or l < cfg["max_tokens"] for _, l in pairs), "a cutoff at or above the cap stops no sample"
    if a.choose:
        assert both and cfg["set"] == "math500", "--choose needs both runs on MATH-500"

    summ, per = {}, {}
    for m in src:
        summ[m], per[m] = summarize(first[m], pairs)
    keys = [name(s, l) for s, l in pairs]
    res = {"spec": SPEC, "mode": mode, "grader": "v3 (score_v3 and extracted_v3 as written by run_cell)", "samples_per_problem_allowed": K,
           "bootstrap_resamples": BOOT, "set": cfg["set"], "n": len(first[next(iter(src))]),
           "runs": {m: {"job_id": meta[m]["job_id"], "commit": meta[m]["commit"],
                        **{k: meta[m]["config"][k] for k in ("model", "prompt", "set", "temperature", "top_p", "max_tokens", "seed", "samples", "restarts")}}
                    for m in src},
           "fixed_from": a.fixed, "models": summ}
    if both:
        res["rl_minus_base"] = {k: {**diff(scores(per["rl"][k]), scores(per["base"][k])),
                                    "tokens_per_problem": summ["rl"]["rows"][k]["tokens_per_problem"] - summ["base"]["rows"][k]["tokens_per_problem"]}
                                for k in keys}
        res["equal_tokens"] = equal_tokens(summ, per, pick)
    chosen = None
    if a.choose:
        e = res["equal_tokens"]["base"]
        assert e is not None, "no setting of the base is within the budget"
        chosen = {"S": e["S"], "L": e["L"], "setting": e["setting"], "criterion": "base: " + res["equal_tokens"]["setting_is"],
                  "spec": SPEC, "chosen_on": {"set": cfg["set"], "n": res["n"], "base_job": meta["base"]["job_id"], "rl_job": meta["rl"]["job_id"],
                                              "budget_tokens_per_problem": res["equal_tokens"]["budget_tokens_per_problem"],
                                              "right": e["right"], "tokens_per_problem": e["tokens_per_problem"]}}
        res["chosen"] = chosen

    ex = {}
    for m in src:
        rows = summ[m]["rows"]
        want = keys[1:] if a.fixed else ["D2000", best(rows, [k for k in keys if rows[k]["S"] is None and rows[k]["L"] is not None])]
        if both and not a.fixed and res["equal_tokens"][m] is not None:
            want.append(res["equal_tokens"][m]["setting"])
        ex[m] = examples(first[m], per[m], [k for k in dict.fromkeys(want) if k != "single"])

    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
                            cwd=pathlib.Path(__file__).resolve().parent).stdout.strip()
    out.mkdir(parents=True)
    (out / "run.json").write_text(json.dumps({"analysis_commit": commit, "command": sys.argv if argv is None else ["day1_length_rules"] + list(argv),
                                              "runs": {m: {"source": str(src[m]), "job_id": meta[m]["job_id"], "commit": meta[m]["commit"],
                                                           "config": meta[m]["config"]} for m in src}}, indent=1) + "\n")
    (out / "metrics.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    head = "\t".join(["model", "problem_index", "n_new_samples_0_3"] + keys)
    (out / "per_problem.tsv").write_text("\n".join([head] + [x for m in src for x in table(first[m], per[m], m)]) + "\n")
    if chosen:
        (out / "chosen.json").write_text(json.dumps(chosen, indent=1) + "\n")

    for m in src:
        for k, r in summ[m]["rows"].items():
            d = r["minus_single"]
            print(f"{m:4s} {k:14s} {r['right']:4d} of {r['n']}  {r['percent']:5.1f} %  [{r['wilson95'][0]:.1f}, {r['wilson95'][1]:.1f}]  "
                  f"{r['tokens_per_problem']:8.0f} tokens/problem  {d['points']:+5.1f} [{d['interval95'][0]:+.1f}, {d['interval95'][1]:+.1f}] vs single  "
                  f"fixed {r['fixed']} broke {r['broke']}")
        print(m, "sample_0", json.dumps(summ[m]["sample_0"]))
    if both:
        for k, d in res["rl_minus_base"].items():
            print(f"RL minus base {k:14s} {d['points']:+5.1f} [{d['interval95'][0]:+.1f}, {d['interval95'][1]:+.1f}] points  {d['tokens_per_problem']:+8.0f} tokens/problem")
        print(json.dumps({"equal_tokens": res["equal_tokens"]}, indent=1))
    if chosen:
        print(json.dumps({"chosen": chosen}, indent=1))


if __name__ == "__main__":
    main()
