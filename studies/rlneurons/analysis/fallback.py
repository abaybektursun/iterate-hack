"""Late answers as fallback votes (specs/SPEC_fallback.md, idea-016ff5): Think-SFT + cue, 4 samples at cap 32,768. Label-free
rules that use the answers finished after token 16,384 only when nothing earlier exists, against the plain 32,768 vote and the
vote over the same answers cut at 16,384. hard328 chooses the rule; fresh2026 is scored once with --fixed.

    uv run --no-project --with numpy --with math-verify==0.9.0 --with tokenizers python -m studies.rlneurons.analysis.fallback \
        --set hard328 --texts <runs>/cap32vote_hard328_s4/answers.jsonl --nn 01
    uv run --no-project --with numpy --with math-verify==0.9.0 --with tokenizers python -m studies.rlneurons.analysis.fallback \
        --set fresh2026 --texts <runs>/cap32vote_fresh_s4/answers.jsonl --fixed studies/rlneurons/results/fallback/hard328-01/chosen.json --nn 01

  --texts  the joined run's answers.jsonl (not in git): read for the script switch (drift.one, unchanged) and the examples.
  --fixed  chosen.json of the development set: only that rule and the controls are scored; nothing is chosen.
Rows: results/cap32vote/<set>_sft1_cue_s4-01/rows.jsonl (committed). Writes results/fallback/<set>-<nn>/: run.json, readout.json,
table.md, rows.jsonl, examples.json and, without --fixed, chosen.json. The vote, the sequential plan, the bootstrap and the
switch detector are imported (day1_vote, frontier, n13_score, drift). Stops if a posted number is not reproduced.
"""
from __future__ import annotations

import argparse
import collections
import functools
import itertools
import json
import multiprocessing
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.analysis import drift as D
from studies.rlneurons.analysis import frontier as F
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

RES = pathlib.Path("studies/rlneurons/results")
SPEC = "studies/rlneurons/specs/SPEC_fallback.md"
OLD, BOOT, SHUFFLES, DRAW = 16384, 5000, 50, 0.05
ROWS = {"hard328": "cap32vote/hard328_sft1_cue_s4-01", "fresh2026": "cap32vote/fresh2026_sft1_cue_s4-01"}
# result-dd26fe, stored order: plain vote, cut vote, right to wrong, wrong to right, late answers (right, finished, all). Its text says
# "99 right of 362" for hard328: 99 is the right count of all 368 late answers; 96 of the 362 finished ones are right (832 + 96 = 928).
POSTED = {"hard328": {"R4": 244, "R5": 238, "right_to_wrong": 9, "wrong_to_right": 15, "late": {"right": 99, "finished": 362, "all": 368}},
          "fresh2026": {"R4": 75, "R5": 73, "right_to_wrong": 4, "wrong_to_right": 6, "late": {"right": 50, "finished": 259, "all": 260}}}
FRONTIER = {"single_32": (232.8, 11650), "seq4_16": (239.8, 30807), "seq4_32": (245.2, 31732)}     # hard328, result-dd26fe
DRIFT_SAMPLE0 = {"late": 93, "switched": 24, "switched_right": 1, "others_right": 22}             # hard328 sample 0, result-997be4
CANDIDATES = ("R1", "R2", "R3")
TEXT = {"R1": "fallback: the 16,384 vote; late answers only when it has no ballot", "R2": "late answers count half a vote",
        "R3": "fallback, late answers that switched script before 16,384 dropped", "R4": "control: plain vote at 32,768",
        "R5": "control: vote over the answers cut at 16,384", "R6": "planted control: fallback with the late flags permuted inside the problem"}


def late(s: dict) -> bool:
    return s["n_new"] > OLD


def b32(s: dict) -> dict:
    return {"extracted_v3": s["extracted_v3"], "score_v3": s["score_v3"]}


def b16(s: dict) -> dict:
    return {"extracted_v3": s["extracted_v3_16"], "score_v3": s["score_v3_16"]}


NONE = {"extracted_v3": None, "score_v3": 0}


def r4(ss: list) -> int:
    return V.vote([b32(s) for s in ss])["score"]


def r5(ss: list) -> int:
    return V.vote([b16(s) for s in ss])["score"]


def r1(ss: list) -> int:
    v = V.vote([b16(s) for s in ss])
    return v["score"] if v["winner"] is not None else r4(ss)


def weights(ss: list) -> tuple:
    """The groups of the 32,768 ballots and their weights: an early sample counts 1, a late sample 0.5."""
    groups = V.vote([b32(s) for s in ss])["groups"]
    return groups, [sum(0.5 if late(ss[k]) else 1.0 for k in g) for g in groups]


def r2(ss: list) -> int:
    groups, w = weights(ss)
    return ss[groups[w.index(max(w))][0]]["score_v3"] if groups else 0     # index of the first maximum: ties to the group seen first


def r3(ss: list) -> int:
    v = V.vote([b16(s) for s in ss])
    if v["winner"] is not None:
        return v["score"]
    v = V.vote([NONE if s["switched"] else b32(s) for s in ss])
    return v["score"] if v["winner"] is not None else r4(ss)


def r6(ss: list, flags: list) -> int:
    """R1 with planted late flags: a sample flagged early casts its 32,768 ballot in the first stage."""
    v = V.vote([NONE if f else b32(s) for s, f in zip(ss, flags)])
    return v["score"] if v["winner"] is not None else r4(ss)


RULES = {"R1": r1, "R2": r2, "R3": r3, "R4": r4, "R5": r5}


def _chain(ss: list, view: int) -> list:
    k = "" if view == 32 else "_16"
    return [[{"n_new": s["n_new" + k], "cap_hit": s["cap_hit" + k], "extracted_v3": s["extracted_v3" + k], "id": j}] for j, s in enumerate(ss)]


def seq4(ss: list, view: int) -> tuple:
    o = F.decide(F.RULES["seq4"], _chain(ss, view))
    return (0 if o["answer"] is None else (b32 if view == 32 else b16)(ss[o["answer"]])["score_v3"]), o["tokens"]


def seqfb_resume(ss: list) -> tuple:
    """seq4 on the 16,384 view; with no ballot there, the stopped samples are resumed under the same plan."""
    o = F.decide(F.RULES["seq4"], _chain(ss, 16))
    if o["answer"] is not None:
        return ss[o["answer"]]["score_v3_16"], o["tokens"]
    o2 = F.decide(F.RULES["seq4"], _chain(ss, 32))
    extra = sum(s["n_new"] - s["n_new_16"] for s in ss[:o2["drawn"]])
    return (0 if o2["answer"] is None else ss[o2["answer"]]["score_v3"]), o["tokens"] + extra


def seqfb_online(ss: list) -> tuple:
    """One sample at a time, no resuming: a sample is stopped at 16,384 once an early ballot exists, else it runs on."""
    drawn, tokens, early = [], 0, False
    for s in ss:
        stop = early or s["extracted_v3_16"] is not None
        tokens += s["n_new_16"] if stop else s["n_new"]
        early = early or s["extracted_v3_16"] is not None
        drawn.append(s)
        if F.agreed([b16(x) for x in drawn]):
            break
    v = V.vote([b16(x) for x in drawn])
    return (v["score"] if v["winner"] is not None else r4(drawn)), tokens


def seq4_half(ss: list) -> tuple:
    """R2 drawn in seq4's plan (2, 1, 1), every sample to the end: stop after a batch when a group weighs 2 (two early, or one
    early and two late), else R2 over what was drawn."""
    drawn = []
    for size in F.SEQ:
        drawn += ss[len(drawn):len(drawn) + size]
        if any(x >= 2 for x in weights(drawn)[1]):
            break
    return r2(drawn), sum(s["n_new"] for s in drawn)


SEQ = {"single_32": lambda ss: (ss[0]["score_v3"], ss[0]["n_new"]), "seq4_16": lambda ss: seq4(ss, 16), "seq4_32": lambda ss: seq4(ss, 32),
       "seqfb_resume": seqfb_resume, "seqfb_online": seqfb_online, "seq4_half": seq4_half}
ORDERS = list(itertools.permutations(range(4)))


def per_problem(prob: dict, rule) -> tuple:
    """(stored order, mean over the 24 draw orders) of rule's value, per problem."""
    idx = sorted(prob)
    return np.array([rule(prob[i]) for i in idx], float), np.array([np.mean([rule([prob[i][k] for k in p]) for p in ORDERS], axis=0) for i in idx])


def shuffled(prob: dict, seed: int = 0) -> np.ndarray:
    """R6 per problem: mean over the 24 orders and SHUFFLES permutations of the late flags inside the problem."""
    rng = np.random.default_rng(seed)
    out = []
    for i in sorted(prob):
        flags = [late(s) for s in prob[i]]
        out.append(np.mean([r6([prob[i][k] for k in p], [flags[k] for k in rng.permutation(4)]) for p in ORDERS for _ in range(SHUFFLES)]))
    return np.array(out)


def diff(x, y) -> dict:
    lo, hi = S.paired_bootstrap(x, y, BOOT)
    return {"problems": round(float(np.sum(x) - np.sum(y)), 2), "points": round(100 * float(np.mean(x) - np.mean(y)), 2), "interval95": [round(lo, 2), round(hi, 2)]}


def power(d1: np.ndarray, d2: np.ndarray, n: int, draws: int = 2000, boot: int = 1000, seed: int = 0) -> dict:
    """Share of `draws` sets of n problems (drawn from the development set) on which the 95 % bootstrap interval of the mean
    difference lies above 0: for d1 (rule minus plain vote), d2 (rule minus cut vote) and both."""
    rng = np.random.default_rng(seed)
    hit = np.zeros((draws, 2), bool)
    for t in range(draws):
        sub = rng.integers(0, len(d1), n)
        bi = rng.integers(0, n, (boot, n))
        hit[t] = [np.percentile(d[sub][bi].mean(1), 2.5) > 0 for d in (d1, d2)]
    return {"n": n, "draws": draws, "minus_plain_32768": float(hit[:, 0].mean()), "minus_cut_16384": float(hit[:, 1].mean()), "both": float(hit.all(1).mean())}


def switch_test(rows: list, seed: int = 0) -> dict:
    """H2: late answers, switched before 16,384 against not, raw and within problem (problems with both kinds)."""
    rng = np.random.default_rng(seed)
    by = collections.defaultdict(list)
    for r in rows:
        if late(r):
            by[r["set"], r["problem_index"]].append((r["switched"], r["score_v3"]))

    def within(groups: list) -> list:
        return [np.mean([s for f, s in g if f]) - np.mean([s for f, s in g if not f]) for g in groups if 0 < sum(f for f, _ in g) < len(g)]

    groups = list(by.values())
    d = np.array(within(groups))
    boot = d[rng.integers(0, len(d), (BOOT, len(d)))].mean(1) if len(d) else np.array([np.nan])
    null = [np.mean(within([list(zip(rng.permutation([f for f, _ in g]), [s for _, s in g])) for g in groups])) for _ in range(200)]
    sw, ot = [s for g in groups for f, s in g if f], [s for g in groups for f, s in g if not f]
    return {"late_answers": len(sw) + len(ot), "switched": len(sw), "switched_right": int(sum(sw)), "not_switched": len(ot), "not_switched_right": int(sum(ot)),
            "problems_with_both_kinds": len(d), "within_problem_points": round(100 * float(d.mean()), 1) if len(d) else None,
            "interval95": [round(100 * float(np.percentile(boot, q)), 1) for q in (2.5, 97.5)],
            "flags_permuted_inside_problems_points": round(100 * float(np.nanmean(null)), 1)}


def mechanism(prob: dict) -> dict:
    """H3: precision early / late, and each late finished ballot on a problem with a 16,384 ballot against those ballots."""
    ss = [s for v in prob.values() for s in v]
    fin_e = [s for s in ss if not late(s) and not s["cap_hit"]]
    fin_l = [s for s in ss if late(s) and not s["cap_hit"]]
    o = collections.Counter()
    for v in prob.values():
        early = [s for s in v if s["extracted_v3_16"] is not None]
        for s in v:
            if not (late(s) and not s["cap_hit"] and s["extracted_v3"] is not None and s["extracted_v3_16"] is None):
                continue
            if not early:
                o["no early ballot"] += 1
                o["no early ballot, late right"] += s["score_v3"]
                continue
            o["with an early ballot"] += 1
            if any(R.agree(R.norm_v3(s["extracted_v3"]), R.norm_v3(e["extracted_v3_16"])) for e in early):
                o["agrees"] += 1
                o["agrees, right"] += s["score_v3"]
            else:
                o["disagrees"] += 1
                o["disagrees, late right"] += s["score_v3"]
                o["disagrees, an early ballot right"] += int(any(e["score_v3_16"] for e in early))
                o["disagrees, none right"] += int(not s["score_v3"] and not any(e["score_v3_16"] for e in early))
    keys = ("with an early ballot", "agrees", "agrees, right", "disagrees", "disagrees, late right", "disagrees, an early ballot right", "disagrees, none right",
            "no early ballot", "no early ballot, late right")
    return {"early_finished": len(fin_e), "early_finished_right": sum(s["score_v3"] for s in fin_e), "late_finished": len(fin_l),
            "late_finished_right": sum(s["score_v3"] for s in fin_l), "problems_without_a_16384_ballot": sum(all(s["extracted_v3_16"] is None for s in v) for v in prob.values()),
            "late_finished_ballots": {k: int(o[k]) for k in keys}}


def load_rows(name: str) -> dict:
    prob = collections.defaultdict(list)
    for l in (RES / ROWS[name] / "rows.jsonl").read_text().splitlines():
        r = json.loads(l)
        assert r["attempt"] == 0 and r["sample"] == len(prob[r["problem_index"]])
        prob[r["problem_index"]].append({**r, "set": name})
    assert all(len(v) == 4 for v in prob.values())
    return dict(prob)


def controls(name: str, prob: dict) -> dict:
    """The posted numbers, from the rows (stored order). Asserted."""
    v32, v16 = per_problem(prob, r4)[0], per_problem(prob, r5)[0]
    lt = [s for v in prob.values() for s in v if late(s)]
    got = {"R4": int(v32.sum()), "R5": int(v16.sum()), "right_to_wrong": int((v32 < v16).sum()), "wrong_to_right": int((v32 > v16).sum()),
           "late": {"right": sum(s["score_v3"] for s in lt), "finished": sum(not s["cap_hit"] for s in lt), "all": len(lt)}}
    assert got == POSTED[name], f"{name}: {got} is not the posted {POSTED[name]}"
    return {**got, "late_finished_right": sum(s["score_v3"] for s in lt if not s["cap_hit"])}


def add_switch(prob: dict, texts: pathlib.Path) -> None:
    """Sets `switched` (first non-Latin episode detected at or before token 16,384; drift.one unchanged) on every late sample and
    False on the others."""
    lines = [l for l in texts.read_text().splitlines() if json.loads(l)["n_new"] > OLD]
    with multiprocessing.Pool() as pool:
        feats = {(f["problem_index"], f["sample"]): f for f in pool.imap(D.one, lines, chunksize=8)}
    n = 0
    for v in prob.values():
        for s in v:
            f = feats.get((s["problem_index"], s["sample"]))
            assert (f is not None) == late(s) and (f is None or f["n_new"] == s["n_new"]), "the texts are not the run of the rows"
            s["switch_tok"] = f["episodes"][0]["detect_tok"] if f and f["episodes"] else None
            s["switched"] = s["switch_tok"] is not None and s["switch_tok"] <= OLD
            n += f is not None
    assert n == len(lines)


def example(prob: dict, all_texts: pathlib.Path, rule, want: tuple):
    """The first problem (stored order) where (rule, plain vote) scores `want`: gold, prompt and the four samples."""
    i = next((i for i in sorted(prob) if (rule(prob[i]), r4(prob[i])) == want), None)
    if i is None:
        return None
    full = {r["sample"]: r for r in map(json.loads, all_texts.read_text().splitlines()) if r["problem_index"] == i}
    return {"problem_index": i, "gold": prob[i][0]["gold"], "prompt": full[0]["prompt"], "rule_score": want[0], "plain_32768_vote_score": want[1],
            "vote_16384_score": r5(prob[i]),
            "samples": [{**{k: s[k] for k in ("sample", "seed", "n_new", "extracted_v3", "score_v3", "extracted_v3_16", "score_v3_16", "switch_tok")},
                         "late": late(s), "switched_before_16384": s["switched"], "text_last_600": full[s["sample"]]["text"][-600:]} for s in prob[i]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, choices=list(ROWS))
    ap.add_argument("--texts", required=True)
    ap.add_argument("--fixed", default=None)
    ap.add_argument("--nn", required=True)
    a = ap.parse_args()
    out = RES / "fallback" / f"{a.set}-{a.nn}"
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    R.agree, R.norm_v3 = functools.lru_cache(maxsize=None)(R.agree), functools.lru_cache(maxsize=None)(R.norm_v3)   # same pairs in 24 orders
    prob = load_rows(a.set)
    idx, n = sorted(prob), len(prob)
    res = {"spec": SPEC, "set": a.set, "n": n, "rows": str(RES / ROWS[a.set]), "controls_reproduced_stored_order": controls(a.set, prob)}
    add_switch(prob, pathlib.Path(a.texts))
    rows = [s for i in idx for s in prob[i]]
    if a.set == "hard328":
        s0 = [s for s in rows if s["sample"] == 0 and late(s)]
        got = {"late": len(s0), "switched": sum(s["switched"] for s in s0), "switched_right": sum(s["score_v3"] for s in s0 if s["switched"]),
               "others_right": sum(s["score_v3"] for s in s0 if not s["switched"])}
        assert got == DRIFT_SAMPLE0, f"switch detector: {got} is not the drift study's {DRIFT_SAMPLE0}"
        res["switch_detector_reproduces_drift_sample_0"] = got

    if a.fixed:
        fixed = json.loads(pathlib.Path(a.fixed).read_text())
        assert fixed["set"] != a.set, "the rule must be chosen on another set"
        names = [fixed["chosen"], "R4", "R5"]
    else:
        names = list(RULES)
    per = {m: per_problem(prob, RULES[m]) for m in names}
    per["R6"] = (None, shuffled(prob))
    res["rules"] = {m: {"what": TEXT[m], "right_24_orders": round(float(per[m][1].sum()), 2), "right_stored_order": None if per[m][0] is None else int(per[m][0].sum())} for m in per}
    if a.fixed:
        chosen = fixed["chosen"]
    else:
        best = max(per[m][1].sum() for m in CANDIDATES)
        chosen = next(m for m in CANDIDATES if per[m][1].sum() >= best - DRAW)
    res["chosen"] = chosen
    res["differences"] = {m: {"minus R4 (plain 32,768 vote), 24 orders": diff(per[m][1], per["R4"][1]), "minus R5 (16,384-cut vote), 24 orders": diff(per[m][1], per["R5"][1]),
                              "minus R4, stored order": diff(per[m][0], per["R4"][0]), "minus R5, stored order": diff(per[m][0], per["R5"][0]),
                              "stored order, against R4: fixed / broken": [int((per[m][0] > per["R4"][0]).sum()), int((per[m][0] < per["R4"][0]).sum())],
                              "stored order, against R5: fixed / broken": [int((per[m][0] > per["R5"][0]).sum()), int((per[m][0] < per["R5"][0]).sum())]}
                          for m in names if m not in ("R4", "R5")}
    res["differences"]["R6"] = {"minus R4 (plain 32,768 vote), 24 orders": diff(per["R6"][1], per["R4"][1])}
    if a.fixed:
        d = res["differences"][chosen]
        res["H1"] = {"rule": chosen, "held": bool(d["minus R4 (plain 32,768 vote), 24 orders"]["interval95"][0] > 0 and d["minus R5 (16,384-cut vote), 24 orders"]["interval95"][0] > 0),
                     "power_stated_before_scoring": fixed["power_fresh2026"]}
        dev = json.loads((pathlib.Path(a.fixed).parent / "per_problem.json").read_text())
        res["pooled_with_the_development_set_descriptive_only"] = {
            "n": n + len(dev["R4"]), **{f"{chosen} minus {m}, 24 orders": diff(np.concatenate([per[chosen][1], dev[chosen]]), np.concatenate([per[m][1], dev[m]])) for m in ("R4", "R5")}}
    else:
        res["power_fresh2026"] = power(per[chosen][1] - per["R4"][1], per[chosen][1] - per["R5"][1], 136)
    res["H2_switch"] = switch_test(rows)
    if a.fixed:
        dev_rows = [{**json.loads(l), "set": fixed["set"]} for l in (pathlib.Path(a.fixed).parent / "rows.jsonl").read_text().splitlines()]
        res["H2_switch_pooled_with_the_development_set"] = switch_test(rows + dev_rows)
    res["H3_mechanism"] = mechanism(prob)
    seq = {m: per_problem(prob, f) for m, f in SEQ.items()}
    res["sequential"] = {m: {"right_24_orders": round(float(v[1][:, 0].sum()), 1), "tokens_per_problem_24_orders": round(float(v[1][:, 1].mean())),
                             "right_stored_order": int(v[0][:, 0].sum()), "tokens_per_problem_stored_order": round(float(v[0][:, 1].mean()))} for m, v in seq.items()}
    res["sequential_differences_24_orders"] = {f"{x} minus {y}": diff(seq[x][1][:, 0], seq[y][1][:, 0]) for x in ("seqfb_resume", "seqfb_online", "seq4_half") for y in ("seq4_32", "seq4_16")}
    if a.set == "hard328":
        for m, (right, tok) in FRONTIER.items():
            g = res["sequential"][m]
            assert (g["right_24_orders"], g["tokens_per_problem_24_orders"]) == (right, tok), f"{m}: {g} is not the posted {right} at {tok}"

    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    src = json.loads((RES / ROWS[a.set] / "run.json").read_text())
    all_texts = pathlib.Path(a.texts)
    ex = {"rule": chosen, "the rule fixes (rule right, plain 32,768 vote wrong)": example(prob, all_texts, RULES[chosen], (1, 0)),
          "the rule breaks (rule wrong, plain 32,768 vote right)": example(prob, all_texts, RULES[chosen], (0, 1))}
    out.mkdir(parents=True)
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(sys.argv), "job_id": None, "spec": SPEC, "fixed": a.fixed,
                                              "inputs": {"rows": str(RES / ROWS[a.set] / "rows.jsonl"), "job_id": src["job_id"], "texts": a.texts}}, indent=1) + "\n")
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "rows.jsonl").write_text("".join(json.dumps({**{k: s[k] for k in ("problem_index", "sample", "n_new", "extracted_v3", "score_v3", "extracted_v3_16", "score_v3_16",
                                                                                 "switch_tok", "switched")}, "late": late(s)}) + "\n" for s in rows))
    (out / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False) + "\n")
    if not a.fixed:
        (out / "chosen.json").write_text(json.dumps({"set": a.set, "spec": SPEC, "chosen": chosen, "power_fresh2026": res["power_fresh2026"]}, indent=1) + "\n")
        (out / "per_problem.json").write_text(json.dumps({"keys": "24-order mean per problem, in the order of problem_indices", "problem_indices": idx,
                                                          **{m: [round(float(x), 4) for x in per[m][1]] for m in (chosen, "R4", "R5")}}, separators=(",", ":")) + "\n")

    iv = lambda d: f"{d['problems']:+.1f} ({d['points']:+.1f} [{d['interval95'][0]:+.1f}, {d['interval95'][1]:+.1f}])"
    md = [f"# Late answers as fallback votes, {a.set}, n = {n}: Think-SFT + cue, 4 samples, cap 32,768" + (f" (rule fixed on {fixed['set']}: {chosen})" if a.fixed else f" (development set; chosen: {chosen})"), "",
          "Right: mean over the 24 draw orders; stored order next to it. Differences: problems (points [95 %]), paired bootstrap over problems, 5,000 resamples.", "",
          "| rule | right, 24 orders | right, stored order | minus plain 32,768 vote, 24 orders | minus 16,384-cut vote, 24 orders | stored order, against plain: fixed / broken |", "|---|---|---|---|---|---|"]
    for m, r in res["rules"].items():
        d = res["differences"].get(m, {})
        fb = d.get("stored order, against R4: fixed / broken")
        md.append(f"| `{m}` {r['what']} | {r['right_24_orders']:.1f} | {'' if r['right_stored_order'] is None else r['right_stored_order']} | "
                  f"{iv(d['minus R4 (plain 32,768 vote), 24 orders']) if d else ''} | {iv(d['minus R5 (16,384-cut vote), 24 orders']) if 'minus R5 (16,384-cut vote), 24 orders' in d else ''} | "
                  f"{'' if fb is None else f'{fb[0]} / {fb[1]}'} |")
    if a.fixed:
        md += ["", "H1: " + json.dumps(res["H1"]), "", "Pooled with the development set (descriptive only): " + json.dumps(res["pooled_with_the_development_set_descriptive_only"])]
    else:
        md += ["", "Power on fresh2026 (136 problems drawn from these 328, 2,000 draws): " + json.dumps(res["power_fresh2026"])]
    h, m3 = res["H2_switch"], res["H3_mechanism"]
    md += ["", "## H2: late answers by a script switch before token 16,384", "",
           "| late answers | switched: right | not switched: right | problems with both kinds | within problem, points [95 %] | flags permuted inside problems |", "|---|---|---|---|---|---|",
           f"| {h['late_answers']} | {h['switched_right']} of {h['switched']} | {h['not_switched_right']} of {h['not_switched']} | {h['problems_with_both_kinds']} | "
           f"{h['within_problem_points']} {h['interval95']} | {h['flags_permuted_inside_problems_points']} |",
           "", "## H3: early and late finished answers", "", "| | count | right |", "|---|---|---|",
           f"| early finished answers | {m3['early_finished']} | {m3['early_finished_right']} |", f"| late finished answers | {m3['late_finished']} | {m3['late_finished_right']} |"]
    b = m3["late_finished_ballots"]
    md += [f"| late finished ballot, problem has a 16,384 ballot | {b['with an early ballot']} | |", f"| - agrees with a 16,384 ballot | {b['agrees']} | {b['agrees, right']} |",
           f"| - disagrees with every 16,384 ballot | {b['disagrees']} | late right {b['disagrees, late right']}; a 16,384 ballot right {b['disagrees, an early ballot right']}; none right {b['disagrees, none right']} |",
           f"| late finished ballot, problem has no 16,384 ballot ({m3['problems_without_a_16384_ballot']} problems) | {b['no early ballot']} | {b['no early ballot, late right']} |",
           "", "## Sequential rules (generated tokens per problem)", "", "| rule | right, 24 orders | tokens, 24 orders | right, stored order | tokens, stored order |", "|---|---|---|---|---|"]
    md += [f"| `{m}` | {r['right_24_orders']} | {r['tokens_per_problem_24_orders']:,} | {r['right_stored_order']} | {r['tokens_per_problem_stored_order']:,} |" for m, r in res["sequential"].items()]
    md += [""] + [f"- {k}: {iv(v)}" for k, v in res["sequential_differences_24_orders"].items()] + [""]
    (out / "table.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
