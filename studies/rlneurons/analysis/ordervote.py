"""Every posted vote over 4 and every contrast that uses one, as the expectation over the tie-break (specs/SPEC_ordervote.md,
idea-49a7af). day1_vote.vote gives a tie to the group seen first in sample order; the posted numbers use the one stored
order. Here a problem's score is its probability of being right under a uniformly random choice among the largest groups
(selector.tie_random), beside the mean, minimum and maximum over the 24 orders of the 4 samples. Committed rows only.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.ordervote --nn 01

Writes results/ordervote/{hard328,fresh2026,math500}-<nn>/: run.json, readout.json, table.md, examples.json.
The vote, the expectation, the rules, the mixes, the share and the bootstrap are imported (day1_vote, selector, frontier,
config_table, n13_score), not copied. Stops if a posted number is not reproduced in the stored order.
"""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import config_table as C     # also memoises rln4_lib.agree
from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.analysis import frontier as F
from studies.rlneurons.analysis import selector as SEL

RES, BOOT, ORDERS = C.RES, C.BOOT, C.ORDERS
NAME = {"think": "Think-SFT + cue", "rl": "RL plain", "base": "base + cue", "rl_restart": "RL plain, vote after restart",
        "base_restart": "base + cue, vote after restart", "edit": "base + 1.5 x top-8 RL directions + cue",
        "cap32": "Think-SFT + cue, cap 32,768", "cap16": "Think-SFT + cue, the same answers cut at 16,384"}
RUNS = {"hard328": {**C.RUNS["hard328"], "edit": C.DIAL4}, "math500": C.RUNS["math500"],
        "fresh2026": {"think": C.FRESH["sft"][1], "rl": C.FRESH["rl"][1], "base": C.FRESH["base"][1]}}
RESTARTS = {"hard328": ("rl", "base"), "math500": ("rl", "base"), "fresh2026": ()}
CAP32 = {"hard328": "cap32vote/hard328_sft1_cue_s4-01", "fresh2026": "cap32vote/fresh2026_sft1_cue_s4-01"}
MIXES = ({"rl": 2, "think": 2}, {"rl": 2, "base": 2}, {"think": 2, "base": 2}, {"rl": 4, "think": 4}, {"think": 4, "base": 4})
VOTES = {"hard328": {"think": 241, "rl": 221, "base": 192, "rl_restart": 224, "base_restart": 195, "edit": 214, "cap32": 244, "cap16": 238,
                     "mix|2rl+2think": 228.1, "mix|2rl+2base": 207.6, "mix|2think+2base": 220.8, "mix|4rl+4think": 239.0, "mix|4think+4base": 238.0},
         "fresh2026": {"think": 75, "rl": 57, "base": 38, "cap32": 75, "cap16": 73},
         "math500": {"think": 481, "rl": 474, "base": 446, "rl_restart": 475, "base_restart": 450}}
TIESHORT = {"hard328": {"think": 238.9, "rl": 215.9, "base": 184.6}, "fresh2026": {"think": 75.5, "rl": 55.8, "base": 38.8},
            "math500": {"think": 480.8, "rl": 474.3, "base": 448.2}}                                    # result-3e4a54
# (x, y, posted points, posted interval or None when no interval was posted, where posted)
CONTRASTS = {
    "hard328": [("think", "rl", 6.1, (3.0, 9.5), "result-818c20"), ("rl", "base", 8.8, (5.2, 12.8), "result-5c961a"), ("think", "base", None, None, ""),
                ("rl_restart", "base_restart", 8.8, (5.5, 12.5), "result-5c961a"),
                ("mix|2rl+2think", "rl", 2.2, (0.3, 4.2), "result-0033d7"), ("mix|2rl+2think", "think", -3.9, (-6.2, -1.8), "result-0033d7"),
                ("edit", "rl", -2.1, (-5.2, 0.6), "result-95a4dc"), ("edit", "base", 6.7, (3.4, 10.4), "result-95a4dc"),
                ("cap32", "cap16", 1.8, (-0.9, 4.9), "result-dd26fe"), ("cap16", "rl", 5.2, (1.8, 8.5), "result-dd26fe audit, same cap"),
                ("cap32", "rl", 7.0, (3.7, 10.4), "result-dd26fe, unequal caps")],
    "fresh2026": [("think", "rl", 13.2, (7.4, 19.1), "result-5251c9"), ("think", "base", 27.2, (19.9, 35.3), "result-5251c9"), ("rl", "base", 14.0, (8.1, 19.9), "result-5251c9"),
                  ("cap32", "cap16", 1.5, (-2.9, 5.9), "result-dd26fe"), ("cap16", "rl", 11.8, (5.2, 18.4), "result-dd26fe audit, same cap"),
                  ("cap32", "rl", 13.2, (6.6, 19.9), "result-dd26fe, unequal caps")],
    "math500": [("think", "rl", 1.4, (-0.4, 3.2), "result-818c20"), ("rl", "base", 5.6, (3.6, 7.8), "README Day-1 #3"), ("think", "base", None, None, ""), ("rl_restart", "base_restart", None, None, "")]}


def cell(rows: dict) -> dict:
    """rows = {problem: its rows in sample order}. The plain vote in the stored order, in each of the orders of the samples
    (4 samples: 24), and its expectation under a uniformly random tie-break."""
    idxs = sorted(rows)
    orders = list(itertools.permutations(range(len(rows[idxs[0]]))))
    stored = np.array([V.vote(rows[i])["score"] for i in idxs], float)
    per_order = np.array([[V.vote([rows[i][k] for k in o])["score"] for i in idxs] for o in orders], float)
    exp = np.array([SEL.tie_random(rows[i]) for i in idxs], float)
    ties = [j for j, i in enumerate(idxs) if V.vote(rows[i])["tie"]]
    gap = np.abs(per_order.mean(0) - exp)
    return {"idx": idxs, "stored": stored, "per_order": per_order, "s": exp, "ties": ties,
            "row": {"posted_stored_order": float(stored.sum()), "order_mean": float(per_order.mean(0).sum()), "expected_random_tie": float(exp.sum()),
                    "order_min": float(per_order.sum(1).min()), "order_max": float(per_order.sum(1).max()), "order_sd": float(per_order.sum(1).std()),
                    "ties": len(ties), "ties_right_stored": float(stored[ties].sum()), "ties_right_expected": float(exp[ties].sum()),
                    "ties_right_min_max_over_orders": [float(per_order[:, ties].sum(1).min()), float(per_order[:, ties].sum(1).max())] if ties else [0.0, 0.0],
                    "largest_per_problem_gap_order_mean_vs_expected": float(gap.max()), "problems_where_they_differ": [idxs[j] for j in np.flatnonzero(gap > 1e-9)]}}


def mix_cell(chs: dict, counts: dict) -> dict:
    """A mixed vote of the configuration table: posted = config_table.mixed (first-seen ties, mean over combinations and
    rotations); expected = tie_random on every combination (the rotation cannot matter under a random tie-break)."""
    posted = C.mixed(chs, counts)
    sam = {m: C.samples(chs[m]) for m in counts}
    n = len(sam[next(iter(counts))][0])
    exp, ties = [], []
    for combo in itertools.product(*[itertools.combinations(range(4), counts[m]) for m in counts]):
        rows = [[sam[m][s][j] for m, pick in zip(counts, combo) for s in pick] for j in range(n)]
        exp.append([SEL.tie_random(r) for r in rows])
        ties.append(sum(V.vote(r)["tie"] for r in rows))
    exp = np.array(exp, float)
    return {"stored": posted["s"], "s": exp.mean(0),
            "row": {"posted_stored_order": float(posted["s"].sum()), "order_mean": None, "expected_random_tie": float(exp.mean(0).sum()),
                    "order_min": float(posted["range"][0]), "order_max": float(posted["range"][1]), "ties": float(np.mean(ties)), "combinations": len(exp),
                    "note": "posted = mean over combinations and rotations, first-seen ties; min and max = over those; ties = mean per combination"}}


def cap_views(name: str) -> dict:
    """{view: {problem: 4 rows}} of result-dd26fe: the answers as written at 32,768 and the same answers cut at 16,384."""
    rows = [json.loads(x) for x in (RES / CAP32[name] / "rows.jsonl").read_text().splitlines()]
    out = {"cap32": {}, "cap16": {}}
    for r in sorted(rows, key=lambda r: (r["problem_index"], r["sample"])):
        out["cap32"].setdefault(r["problem_index"], []).append(r)
        out["cap16"].setdefault(r["problem_index"], []).append({**r, **{k: r[k + "_16"] for k in ("n_new", "cap_hit", "extracted_v3", "score_v3")}})
    return out


def cells(name: str) -> tuple:
    ch = {m: F.load(RES / p)[1] for m, p in RUNS[name].items()}
    out = {m: cell({i: [c[0] for c in cs] for i, cs in ch[m].items()}) for m in ch}
    for m in RESTARTS[name]:
        out[m + "_restart"] = cell({i: [c[-1] for c in cs] for i, cs in ch[m].items()})
    if name in CAP32:
        out.update({v: cell(rows) for v, rows in cap_views(name).items()})
    if name == "hard328":
        for counts in MIXES:
            out["mix|" + "+".join(f"{c}{k}" for k, c in counts.items())] = mix_cell(ch, counts)
    idxs = out["rl"]["idx"]
    assert all(c.get("idx", idxs) == idxs for c in out.values()), f"{name}: the cells are not on the same problems"
    return ch, out


def draws(name: str, n: int) -> dict:
    """The resamples the posted intervals used: n13_score.paired_bootstrap(seed 0) = config_table.idx_matrix; the three
    fresh2026 model contrasts were posted with the consecutive draws of one generator (config_table.fresh, fresh_read.py)."""
    d = {None: C.idx_matrix(n)}
    if name == "fresh2026":
        rng = np.random.default_rng(0)
        for pair in (("think", "rl"), ("think", "base"), ("rl", "base")):
            d[pair] = rng.integers(0, n, (BOOT, n))
    return d


def diff(x, y, idx) -> dict:
    v = np.asarray(x, float) - np.asarray(y, float)
    return {"problems": float(v.sum()), "points": float(100 * v.mean()), "interval95": C.interval(100 * v[idx].mean(1))}


def contrast(out: dict, x: str, y: str, posted, ci, where: str, dr: dict) -> dict:
    idx = dr.get((x, y), dr[None])
    st, av = diff(out[x]["stored"], out[y]["stored"], idx), diff(out[x]["s"], out[y]["s"], idx)
    half = (st["interval95"][1] - st["interval95"][0]) / 2
    side = lambda d: int(d["interval95"][0] > 0) - int(d["interval95"][1] < 0)
    return {"x": x, "y": y, "posted_in": where, "posted": {"points": posted, "interval95": ci}, "stored_order": st, "order_averaged": av,
            "change_points": av["points"] - st["points"], "posted_half_width": half, "changes_by_more_than_half_width": bool(abs(av["points"] - st["points"]) > half),
            "conclusion_flips": side(st) != side(av),
            "stored_reproduces_posted": None if posted is None else bool(np.allclose([st["points"], *st["interval95"]], [posted, *ci], atol=0.056))}   # posted to 1 decimal, some rounded twice


def shares(ch: dict, out: dict) -> list:
    """Share of the base-to-RL gap closed under the vote, for every vote-family row of results/table/hard328-02/table.json:
    as posted (stored order where the row was posted in it) and with every vote as its mean over the 24 orders."""
    posted = [r for r in json.loads((RES / "table/hard328-02/table.json").read_text())["rows"] if r["family"] == "vote"]
    idx, res = C.idx_matrix(len(out["rl"]["idx"])), []
    for r in posted:
        m, rule = r["key"].split("|")
        if m in ("mix", "dial4"):
            c = out["edit" if m == "dial4" else r["key"]]
            st, av = c["stored"], c["s"]
        else:
            st = C.play(ch[m], F.RULES[rule], C.STORED if rule.startswith("vote4") else ORDERS)["s"]
            av = out[m + "_restart" * (rule == "vote4_restart" and m != "think")]["s"] if rule in ("vote4", "vote4_restart") else C.play(ch[m], F.RULES[rule], ORDERS)["s"]
        s0, s1 = C.share(st, out["base"]["stored"], out["rl"]["stored"], idx), C.share(av, out["base"]["s"], out["rl"]["s"], idx)
        ok = abs(s0["percent"] - r["share"]["percent"]) < 1e-6 and np.allclose(s0["interval95"], r["share"]["interval95"]) and abs(float(st.sum()) - r["right"]) < 1e-6
        half, side = (s0["interval95"][1] - s0["interval95"][0]) / 2, lambda s, at: int(s["interval95"][0] > at) - int(s["interval95"][1] < at)
        res.append({"change_percent": s1["percent"] - s0["percent"], "posted_half_width": half, "changes_by_more_than_half_width": bool(abs(s1["percent"] - s0["percent"]) > half),
                    "side_of_0_posted_then_averaged": [side(s0, 0), side(s1, 0)], "side_of_100_posted_then_averaged": [side(s0, 100), side(s1, 100)], "key": r["key"], "name": r["name"], "reward": r["reward"], "chosen_on_328": r["chosen_on_328"], "right_posted": float(st.sum()), "right_order_averaged": float(av.sum()),
                    "share_posted": s0, "share_order_averaged": s1, "stored_reproduces_table_json": bool(ok)})
    return res


def example(c: dict, rows: dict, stored_right: bool):
    """A tied problem where the stored order is right and another order is wrong (or the reverse), with its four answers."""
    for j in c["ties"]:
        po = c["per_order"][:, j]
        if c["stored"][j] == stored_right and (po != stored_right).any():
            o = ORDERS[int(np.flatnonzero(po != stored_right)[0])]
            r = rows[c["idx"][j]]
            return {"problem_index": c["idx"][j], "gold": r[0].get("gold"), "groups_stored_order": V.vote(r)["groups"], "stored_order_score": int(c["stored"][j]),
                    "another_order": list(o), "another_order_score": int(V.vote([r[k] for k in o])["score"]), "orders_right_of_24": int(po.sum()),
                    "expected_score": float(c["s"][j]), "samples": [{k: x.get(k) for k in ("sample", "n_new", "cap_hit", "extracted_v3", "score_v3")} for x in r]}
    return None


def num(x, d=1) -> str:
    return "" if x is None else f"{x:.{d}f}".rstrip("0").rstrip(".") if float(x).is_integer() else f"{x:.{d}f}"


def ci(d: dict, key="points") -> str:
    return f"{d[key]:+.1f} [{d['interval95'][0]:+.1f}, {d['interval95'][1]:+.1f}]"


def table(name: str, out: dict, con: list, sh) -> str:
    n = len(out["rl"]["idx"])
    md = [f"# Vote over 4 as the expectation over the tie-break, {name}, n = {n}, T 1.0 / top-p 1.0, grader v3", "",
          "Posted = `day1_vote.vote` in the stored sample order (a tie goes to the group seen first). Order mean, min, max = over the 24 orders of the 4 samples. "
          "Expected = `selector.tie_random` (uniformly random choice among the largest groups). Ties = problems with a tie for first, stored order.", "",
          "| Vote | posted (stored order) | order mean | expected, random tie-break | min to max over orders | ties | ties right: stored, expected, min to max |", "|---|---|---|---|---|---|---|"]
    for k, c in out.items():
        r = c["row"]
        tr = f"{num(r['ties_right_stored'])}, {num(r['ties_right_expected'])}, {num(r['ties_right_min_max_over_orders'][0])} to {num(r['ties_right_min_max_over_orders'][1])}" if "ties_right_stored" in r else ""
        md.append(f"| {NAME.get(k, k.replace('mix|', 'mixed vote, ') + ' (mean over combinations)')} | {num(r['posted_stored_order'])} | {num(r['order_mean'])} | {num(r['expected_random_tie'])} | "
                  f"{num(r['order_min'])} to {num(r['order_max'])}{' (first-seen ties, over combinations and rotations)' if k.startswith('mix') else ''} | {num(r['ties'])} | {tr} |")
    md += ["", "Contrasts in points [95 %], paired bootstrap over problems, 5,000 resamples, the posted resamples; order-averaged = on the per-problem expected scores.", "",
           "| Contrast | posted in | stored order (as posted) | order-averaged | change | more than the posted half-width | conclusion flips |", "|---|---|---|---|---|---|---|"]
    for c in con:
        md.append(f"| {NAME.get(c['x'], c['x'])} minus {NAME.get(c['y'], c['y'])} | {c['posted_in']} | {ci(c['stored_order'])} | {ci(c['order_averaged'])} | {c['change_points']:+.1f} | "
                  f"{'yes' if c['changes_by_more_than_half_width'] else 'no'} ({c['posted_half_width']:.1f}) | {'yes' if c['conclusion_flips'] else 'no'} |")
    if sh:
        md += ["", "Share of the base-to-RL gap closed under the vote, % [95 %] (interval of the ratio; denominators: stored 221 - 192, order-averaged "
               f"{num(out['rl']['row']['expected_random_tie'])} - {num(out['base']['row']['expected_random_tie'])}):", "",
               "| Row of the configuration table | right, posted | right, order-averaged | share, posted | share, order-averaged | change | more than the posted half-width | reward-trained weights |", "|---|---|---|---|---|---|---|---|"]
        for r in sh:
            f = lambda s: f"{s['percent']:.0f} [{s['interval95'][0]:.0f}, {s['interval95'][1]:.0f}]" + (" unstable" if s["unstable"] else "")
            md.append(f"| {r['name']} | {num(r['right_posted'])} | {num(r['right_order_averaged'])} | {f(r['share_posted'])} | {f(r['share_order_averaged'])} | {r['change_percent']:+.0f} | "
                      f"{'yes' if r['changes_by_more_than_half_width'] else 'no'} ({r['posted_half_width']:.0f}) | {r['reward']} |")
    return "\n".join(md) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nn", default="01")
    a = ap.parse_args()
    outs = {s: RES / "ordervote" / f"{s}-{a.nn}" for s in RUNS}
    for o in outs.values():
        assert not o.exists(), f"{o} exists: a rerun gets the next number"
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=C.STUDY, text=True).strip()
    done = {}
    for name in outs:                                                                    # every check on every set before anything is written
        ch, out = cells(name)
        for k, want in VOTES[name].items():                                              # checks first: the posted votes, then tieshort's order means
            assert round(out[k]["row"]["posted_stored_order"], 1) == want, f"{name} {k}: stored order gives {out[k]['row']['posted_stored_order']}, posted {want}"
        for k, want in TIESHORT[name].items():
            assert round(out[k]["row"]["order_mean"], 1) == want, f"{name} {k}: order mean {out[k]['row']['order_mean']}, result-3e4a54 has {want}"
        dr = draws(name, len(out["rl"]["idx"]))
        con = [contrast(out, *c, dr) for c in CONTRASTS[name]]
        bad = [c for c in con if c["stored_reproduces_posted"] is False]
        assert not bad, f"{name}: posted contrasts not reproduced in the stored order: {[(c['x'], c['y'], c['stored_order']) for c in bad]}"
        sh = shares(ch, out) if name == "hard328" else None
        assert not sh or all(r["stored_reproduces_table_json"] for r in sh), [r["key"] for r in sh if not r["stored_reproduces_table_json"]]
        first = {m: {i: [c[0] for c in cs] for i, cs in ch[m].items()} for m in ch}
        done[name] = (out, con, sh, first)
    for name, o in outs.items():
        out, con, sh, first = done[name]
        o.mkdir(parents=True)
        (o / "run.json").write_text(json.dumps({"commit": commit, "command": "python -m studies.rlneurons.analysis.ordervote " + " ".join(sys.argv[1:]), "job_id": None, "where": "laptop, no GPU",
                                                "spec": "studies/rlneurons/specs/SPEC_ordervote.md", "inputs": {**RUNS[name], **({"cap32, cap16": CAP32[name]} if name in CAP32 else {}),
                                                                                                               **({"shares": "table/hard328-02/table.json"} if sh else {})}}, indent=1) + "\n")
        (o / "readout.json").write_text(json.dumps({"set": name, "n": len(out["rl"]["idx"]), "boot": BOOT, "problem_indices": out["rl"]["idx"], "votes": {k: c["row"] for k, c in out.items()},
                                                    "contrasts": con, "shares_of_the_gap_closed": sh, "per_problem_expected": {k: c["s"] for k, c in out.items()},
                                                    "per_problem_stored_order": {k: c["stored"] for k, c in out.items()}}, indent=1, default=C.jsonable) + "\n")
        (o / "examples.json").write_text(json.dumps({m: {"stored_order_right_another_order_wrong": example(out[m], first[m], True),
                                                         "stored_order_wrong_another_order_right": example(out[m], first[m], False)} for m in first}, indent=1) + "\n")
        (o / "table.md").write_text(table(name, out, con, sh))
        print(table(name, out, con, sh))


if __name__ == "__main__":
    main()
