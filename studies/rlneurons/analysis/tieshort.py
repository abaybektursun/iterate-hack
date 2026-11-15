"""Does "vote ties go to the shortest finished sample" (selector.RULES["tie_short"]) raise the vote over 4 on the stored 16,384
draws? (specs/SPEC_tieshort.md, idea-2b2aa1.) Three models x three sets, from committed rows.jsonl only.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.tieshort --nn 01

Writes results/tieshort/{hard328,fresh2026,math500}-<nn>/: run.json, readout.json, table.md, examples.json.
The vote, the tie rule, the replay over the 24 draw orders and the bootstrap are imported (day1_vote, selector, frontier,
n13_score), not copied. Stops if a posted number is not reproduced.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.analysis import frontier as F
from studies.rlneurons.analysis import selector as SEL
from studies.rlneurons.lib import n13_score as S

RES = pathlib.Path("studies/rlneurons/results")
BOOT, SHUFFLES = 5000, 200
MODELS = {"think": "Think-SFT + cue", "rl": "RL plain", "base": "base + cue"}
SETS = {"hard328": {"think": "thinkvote/hard328_sft1_cue_s4-01", "rl": "day1_3/hard328_rl_plain_s4r2-01", "base": "day1_3/hard328_base_cue_s4r2-01"},
        "fresh2026": {"think": "fresh/sft1_cue_s4-01", "rl": "fresh/rl_plain_s4-01", "base": "fresh/base_cue_s4-01"},
        "math500": {"think": "thinkvote/math500_sft1_cue_s4-01", "rl": "day1_3/math500_rl-01", "base": "day1_3/math500_base_cue-01"}}
# posted plain votes and, where posted, the rule (README; SPEC_tieshort.md "What is already known")
POSTED = {("hard328", "think"): (241, 239), ("hard328", "rl"): (221, 222), ("hard328", "base"): (192, 191),
          ("fresh2026", "think"): (75, 76), ("fresh2026", "rl"): (57, 60), ("fresh2026", "base"): (None, 38),
          ("math500", "think"): (481, 481), ("math500", "rl"): (474, 475), ("math500", "base"): (446, 453)}
CAP32 = {"hard328": {"32768": (244, 252), "16384": (238, 246)}, "fresh2026": {"32768": (75, 81), "16384": (73, 75)}}   # result-dd26fe
RULES = {m: F.RULES[m] for m in ("vote4", "vote4_short", "seq4", "seq4_short")}


def diff(x, y) -> dict:
    lo, hi = S.paired_bootstrap(x, y, BOOT)
    return {"problems": round(float(sum(x) - sum(y)), 2), "points": round(100 * float(np.mean(x) - np.mean(y)), 2), "interval95": [round(lo, 2), round(hi, 2)]}


def shuffled(rows: list, rng) -> list:
    """The rows with n_new permuted among the finished samples: a tie-break that cannot read length."""
    fin = [k for k, r in enumerate(rows) if not r["cap_hit"]]
    new = dict(zip(fin, (rows[p]["n_new"] for p in rng.permutation(fin))))
    return [{**r, "n_new": new.get(k, r["n_new"])} for k, r in enumerate(rows)]


def ties(first: dict, seed: int = 0) -> dict:
    """The problems whose plain vote has a tie for first, stored order."""
    rng, out, per = np.random.default_rng(seed), {"n": 0, "low": 0, "short": 0, "long": 0, "random": 0.0, "shuffled": 0.0, "no_finished_tied_group": 0,
                                                  "short_group": [0, 0], "other_tied_groups": [0, 0], "sizes": {}}, []
    for i in sorted(first):
        rows = first[i]
        v = V.vote(rows)
        if not v["tie"]:
            continue
        tied = [g for g in v["groups"] if len(g) == v["votes"]]
        k = SEL.pick(rows, SEL.RULES["tie_short"])[0]
        out["n"] += 1
        out["low"] += v["score"]
        out["short"] += rows[k]["score_v3"]
        out["long"] += SEL.pick(rows, SEL.CONTROLS["tie_long"])[1]
        out["random"] += SEL.tie_random(rows)
        out["shuffled"] += float(np.mean([SEL.pick(shuffled(rows, rng), SEL.RULES["tie_short"])[1] for _ in range(SHUFFLES)]))
        key = f"{len(tied)} groups of {v['votes']}"
        out["sizes"][key] = out["sizes"].get(key, 0) + 1
        if all(rows[j]["cap_hit"] for g in tied for j in g):
            out["no_finished_tied_group"] += 1
        else:
            sg = next(g for g in tied if k in g)
            out["short_group"][0] += rows[sg[0]]["score_v3"]
            out["short_group"][1] += 1
            for g in tied:
                if g is not sg:
                    out["other_tied_groups"][0] += rows[g[0]]["score_v3"]
                    out["other_tied_groups"][1] += 1
        per.append(i)
    out["problems"] = per
    return out


def cell(folder: pathlib.Path) -> dict:
    m, ch = F.load(folder)
    idxs = sorted(ch)
    first = {i: [c[0] for c in ch[i]] for i in idxs}
    per = F.replay(ch, RULES)
    assert per["vote4"]["s0"] == [V.vote(first[i])["score"] for i in idxs], "frontier vote4 is not day1_vote.vote"
    assert per["vote4_short"]["s0"] == [SEL.pick(first[i], SEL.RULES["tie_short"])[1] for i in idxs], "frontier vote4_short is not selector tie_short"
    t = ties(first)
    v, s = per["vote4"], per["vote4_short"]
    n = len(idxs)
    return {"folder": str(folder), "job_id": m["job_id"], "n": n, "idx": idxs, "first": first, "per": per,
            "row": {"vote_stored": int(sum(v["s0"])), "rule_stored": int(sum(s["s0"])), "fixed": sum(a > b for a, b in zip(s["s0"], v["s0"])),
                    "broken": sum(a < b for a, b in zip(s["s0"], v["s0"])), "rule_minus_vote_stored": diff(s["s0"], v["s0"]),
                    "vote_24": round(sum(v["s"]), 2), "rule_24": round(sum(s["s"]), 2), "rule_minus_vote_24": diff(s["s"], v["s"]),
                    "rule_shuffled_lengths_stored": round(sum(v["s0"]) - t["low"] + t["shuffled"], 2),
                    "tokens_vote4": round(sum(v["t0"]) / n),
                    "seq4_24": round(sum(per["seq4"]["s"]), 2), "seq4_short_24": round(sum(per["seq4_short"]["s"]), 2),
                    "seq4_short_minus_seq4_24": diff(per["seq4_short"]["s"], per["seq4"]["s"]),
                    "seq4_tokens_24": round(sum(per["seq4"]["t"]) / n), "seq4_short_tokens_24": round(sum(per["seq4_short"]["t"]) / n),
                    "seq4_short_stored": int(sum(per["seq4_short"]["s0"])), "seq4_stored": int(sum(per["seq4"]["s0"])),
                    "ties": {k: (round(x, 2) if isinstance(x, float) else x) for k, x in t.items()}}}


def cap32(name: str) -> dict:
    """The post hoc numbers of result-dd26fe from its committed rows, both views."""
    rows = [json.loads(l) for l in (RES / "cap32vote" / f"{name}_sft1_cue_s4-01" / "rows.jsonl").read_text().splitlines()]
    out = {}
    for view, f in (("32768", lambda r: r), ("16384", lambda r: {**r, **{k: r[k + "_16"] for k in ("n_new", "cap_hit", "extracted_v3", "score_v3")}})):
        by = {}
        for r in sorted(rows, key=lambda r: (r["problem_index"], r["sample"])):
            by.setdefault(r["problem_index"], []).append(f(r))
        got = (sum(V.vote(x)["score"] for x in by.values()), sum(SEL.pick(x, SEL.RULES["tie_short"])[1] for x in by.values()))
        assert got == CAP32[name][view], f"cap32vote {name} {view}: {got}, posted {CAP32[name][view]}"
        t = ties(by)
        out[view] = {"vote": got[0], "rule": got[1], "ties": {k: (round(x, 2) if isinstance(x, float) else x) for k, x in t.items() if k != "problems"}}
    return out


def example(c: dict, want_fix: bool):
    v, s = c["per"]["vote4"]["s0"], c["per"]["vote4_short"]["s0"]
    j = next((j for j in range(c["n"]) if (s[j] > v[j] if want_fix else s[j] < v[j])), None)
    if j is None:
        return None
    rows = c["first"][c["idx"][j]]
    return {"problem_index": c["idx"][j], "gold": rows[0]["gold"], "vote_pick": V.vote(rows)["winner"], "rule_pick": SEL.pick(rows, SEL.RULES["tie_short"])[0],
            "vote_score": v[j], "rule_score": s[j], "groups": V.vote(rows)["groups"],
            "samples": [{k: r[k] for k in ("sample", "n_new", "cap_hit", "extracted_v3", "score_v3")} for r in rows]}


def pooled(cells: dict, sets=("hard328", "fresh2026")) -> dict:
    """Rule minus plain vote over the problems of both held-out sets, and the model contrasts of H2."""
    d = {m: {k: np.concatenate([np.array(cells[s, m]["per"]["vote4_short"][k], float) - np.array(cells[s, m]["per"]["vote4"][k], float) for s in sets])
             for k in ("s", "s0")} for m in MODELS}
    z = np.zeros(len(d["think"]["s"]))
    out = {"sets": list(sets), "n": len(z)}
    for m in MODELS:
        out[m] = {"24_orders": diff(d[m]["s"], z), "stored_order": diff(d[m]["s0"], z)}
    for m in ("rl", "base"):
        out[f"think_minus_{m}"] = {"24_orders": diff(d["think"]["s"], d[m]["s"]), "stored_order": diff(d["think"]["s0"], d[m]["s0"])}
    return out


def fmt(d: dict) -> str:
    return f"{d['problems']:+g} ({d['points']:+.1f} [{d['interval95'][0]:+.1f}, {d['interval95'][1]:+.1f}])"


def table(name: str, cells: dict, pool: dict, c32) -> str:
    n = cells[name, "think"]["n"]
    md = [f"# Vote ties to the shortest finished sample, {name}, n = {n}, stored 16,384 draws, 4 samples, T 1.0 / top-p 1.0, grader v3", "",
          "Rule: `selector.RULES[\"tie_short\"]`. Differences: rule minus plain vote, problems (points [95 %], paired bootstrap over problems, 5,000 resamples).", "",
          "| Model | plain vote, stored order | rule, stored order | fixed / broken | difference, stored order | plain vote, 24 orders | rule, 24 orders | difference, 24 orders | rule with lengths shuffled |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m, label in MODELS.items():
        r = cells[name, m]["row"]
        md.append(f"| {label} | {r['vote_stored']} | {r['rule_stored']} | {r['fixed']} / {r['broken']} | {fmt(r['rule_minus_vote_stored'])} | {r['vote_24']:.1f} | {r['rule_24']:.1f} | "
                  f"{fmt(r['rule_minus_vote_24'])} | {r['rule_shuffled_lengths_stored']:.1f} |")
    md += ["", "Ties for first in the plain vote (stored order) and right answers inside them:", "",
           "| Model | ties | lowest sample (plain vote) | shortest (rule) | longest (control) | random, expected | lengths shuffled | shortest tied group right | other tied groups right | ties with no finished tied group | shapes |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, label in MODELS.items():
        t = cells[name, m]["row"]["ties"]
        md.append(f"| {label} | {t['n']} | {t['low']} | {t['short']} | {t['long']} | {t['random']:.1f} | {t['shuffled']:.1f} | {t['short_group'][0]} of {t['short_group'][1]} | "
                  f"{t['other_tied_groups'][0]} of {t['other_tied_groups'][1]} | {t['no_finished_tied_group']} | {', '.join(f'{k}: {x}' for k, x in sorted(t['sizes'].items()))} |")
    md += ["", "Sequential vote, stop when two agree, at most 4 (means over the 24 draw orders):", "",
           "| Model | `seq4` right | `seq4_short` right | difference | tokens per problem | vote over 4 tokens |", "|---|---|---|---|---|---|"]
    for m, label in MODELS.items():
        r = cells[name, m]["row"]
        md.append(f"| {label} | {r['seq4_24']:.1f} | {r['seq4_short_24']:.1f} | {fmt(r['seq4_short_minus_seq4_24'])} | {r['seq4_short_tokens_24']:,} | {r['tokens_vote4']:,} |")
    md += ["", f"Pooled over {' + '.join(pool['sets'])} (n = {pool['n']}), rule minus plain vote:", "", "| | 24 orders | stored order |", "|---|---|---|"]
    for k in (*MODELS, "think_minus_rl", "think_minus_base"):
        md.append(f"| {MODELS.get(k, k.replace('_', ' '))} | {fmt(pool[k]['24_orders'])} | {fmt(pool[k]['stored_order'])} |")
    if c32:
        md += ["", "The post hoc lead (result-dd26fe), reproduced from `results/cap32vote/` rows (Think-SFT + cue, other draws of the same problems):", "",
               "| view | plain vote | rule | ties | lowest sample right | shortest right | random, expected | shortest tied group right | other tied groups right |", "|---|---|---|---|---|---|---|---|---|"]
        for view, x in c32.items():
            t = x["ties"]
            md.append(f"| {view} | {x['vote']} | {x['rule']} | {t['n']} | {t['low']} | {t['short']} | {t['random']:.1f} | {t['short_group'][0]} of {t['short_group'][1]} | "
                      f"{t['other_tied_groups'][0]} of {t['other_tied_groups'][1]} |")
    return "\n".join(md) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nn", default="01")
    a = ap.parse_args()
    outs = {s: RES / "tieshort" / f"{s}-{a.nn}" for s in SETS}
    for o in outs.values():
        assert not o.exists(), f"{o} exists: a rerun gets the next number"
    cells = {(s, m): cell(RES / f) for s, ms in SETS.items() for m, f in ms.items()}
    for key, (vote, rule) in POSTED.items():
        r = cells[key]["row"]
        assert vote in (None, r["vote_stored"]) and rule == r["rule_stored"], f"{key}: {r['vote_stored']}, {r['rule_stored']}; posted {vote}, {rule}"
    c32 = {s: cap32(s) for s in CAP32}
    pool = pooled(cells)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    for s, out in outs.items():
        out.mkdir(parents=True)
        (out / "run.json").write_text(json.dumps({"commit": commit, "command": " ".join(sys.argv), "job_id": None, "spec": "studies/rlneurons/specs/SPEC_tieshort.md",
                                                  "inputs": {m: {"folder": cells[s, m]["folder"], "job_id": cells[s, m]["job_id"]} for m in MODELS},
                                                  "cap32vote_rows": f"studies/rlneurons/results/cap32vote/{s}_sft1_cue_s4-01/rows.jsonl" if s in c32 else None}, indent=1) + "\n")
        (out / "readout.json").write_text(json.dumps({"set": s, "rule": "selector.RULES['tie_short']", "boot": BOOT, "shuffles": SHUFFLES,
                                                      "models": {m: cells[s, m]["row"] for m in MODELS}, "pooled_hard328_fresh2026": pool,
                                                      "cap32vote_lead_reproduced": c32.get(s),
                                                      "per_problem": {m: {"problem_indices": cells[s, m]["idx"], **{f"{k}_{o}": cells[s, m]["per"][k][o] for k in RULES for o in ("s0", "s")}}
                                                                      for m in MODELS}}, indent=1) + "\n")
        (out / "examples.json").write_text(json.dumps({m: {"rule_fixes": example(cells[s, m], True), "rule_breaks": example(cells[s, m], False)} for m in MODELS}, indent=1) + "\n")
        (out / "table.md").write_text(table(s, cells, pool, c32.get(s)))
        print(table(s, cells, pool, c32.get(s)))


if __name__ == "__main__":
    main()
