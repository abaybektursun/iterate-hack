"""Prefix hand-off readout (specs/SPEC_handoff.md). Scores the raw rows of jobs/handoff_gen.py (grader v3 on prefix text +
continuation) and writes, per finisher, a run folder, and the writer x finisher x cut tables.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.handoff \
        --run base=runs/<job> --run rl=runs/<job> --out studies/rlneurons/results/handoff --nn 01

Writes <out>/<finisher>-<nn>/ (run.json, metrics.json, rows.jsonl without text, examples.json) and, with both finishers,
<out>/readout-<nn>/readout.json and readout.txt. A run with missing rows is scored as is when under 2 % are missing; the count
is in the readout. The loop detector (rln4_lib.onset_lines) raises IndexError on some degenerate answers: the error is recorded
in the row (loop_error) and counted, the row keeps its score.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
BOOT = 5000
CUTS = (25, 50, 75)
COMPACT = ("problem_index", "writer", "cut", "finisher", "seed", "n_prefix", "n_new", "cap_hit", "finish_reason", "extracted_v3", "score_v3",
           "loop_A", "loop_error", "stratum", "prefix_has_right", "gold")


def score(rec: dict, prow: dict) -> dict:
    """The compact row of one raw row. prow: the plan row of its (problem, writer)."""
    text = rec["prefix_text"] + rec["gen_text"]
    out = {**{k: rec[k] for k in COMPACT if k in rec}, **R.grade_v3(rec["gold"], text), "loop_A": None, "loop_error": None,
           "stratum": prow["stratum"], "prefix_has_right": prow["prefix_has_right"][str(rec["cut"])]}
    try:
        out["loop_A"] = R.onset_lines(text) is not None
    except IndexError as e:                                      # the reported onset_lines bug: recorded and counted, not hidden
        out["loop_error"] = f"IndexError: {e}"
    del out["mode_v3"]
    return out


def cell(rows: list) -> dict:
    k, n = sum(r["score_v3"] for r in rows), len(rows)
    return {"right": k, "n": n, "wilson95": list(S.wilson(k, n)), "cap_hits": sum(r["cap_hit"] for r in rows),
            "tokens_generated_per_problem": sum(r["n_new"] for r in rows) / n if n else None,
            "tokens_total_per_problem": sum(r["n_new"] + r["n_prefix"] for r in rows) / n if n else None}


def diff(x: list, y: list) -> dict:
    """x minus y on paired 0/1 lists, in points."""
    if not x:
        return {"n": 0}
    return {"n": len(x), "x_right": sum(x), "y_right": sum(y), "points": 100 * (sum(x) - sum(y)) / len(x), "ci95": list(S.paired_bootstrap(x, y, BOOT, 0)),
            "x_only": sum(a > b for a, b in zip(x, y)), "y_only": sum(a < b for a, b in zip(x, y))}


def example(rec: dict, row: dict) -> dict:
    return {**row, "prompt": rec["prompt"], "prefix_last_600_chars": rec["prefix_text"][-600:], "continuation_first_1500_chars": rec["gen_text"][:1500],
            "continuation_last_800_chars": rec["gen_text"][-800:]}


def readout(rows: dict, plan: dict) -> dict:
    """rows: {(finisher, writer, cut, problem): compact row}."""
    P = {(r["problem_index"], r["writer"]): r for r in plan["rows"]}
    pool, U = plan["pool"], set(plan["unbiased"])

    def get(f, w, c, probs):
        return [rows[f, w, c, i] for i in probs if (f, w, c, i) in rows]

    def paired(fx, wx, fy, wy, c, probs):
        both = [i for i in probs if (fx, wx, c, i) in rows and (fy, wy, c, i) in rows]
        return diff([rows[fx, wx, c, i]["score_v3"] for i in both], [rows[fy, wy, c, i]["score_v3"] for i in both])

    out = {"n_pool": len(pool), "n_unbiased": len(U), "strata": {}, "rl_minus_base_finisher": {}, "cross_minus_own": {}, "control_own_minus_stored": {}, "pool": {}}
    for w in ("base", "rl"):
        for s in ("right", "wrong", "cap", "right_answer_not_in_prefix"):
            for c in CUTS:
                probs = [i for i in pool if (P[i, w]["stratum"] == s) or (s == "right_answer_not_in_prefix" and P[i, w]["stratum"] == "right" and not P[i, w]["prefix_has_right"][str(c)])]
                key = f"{w}_writer|{s}|{c}"
                out["strata"][key] = {**{f"{f}_finisher": cell(get(f, w, c, probs)) for f in ("base", "rl")},
                                      "fresh_rate_samples_1_3": {m: 100 * sum(sum(P[i, m]["fresh_scores"]) for i in probs) / (3 * len(probs)) if probs else None for m in ("base", "rl")}}
                out["rl_minus_base_finisher"][key] = paired("rl", w, "base", w, c, probs)
    for c in CUTS:
        for f, other in (("base", "rl"), ("rl", "base")):
            out["pool"][f"{f}_finisher|{f}_writer|{c}"] = cell(get(f, f, c, pool))
            out["pool"][f"{f}_finisher|{other}_writer|{c}"] = cell(get(f, other, c, pool))
            out["cross_minus_own"][f"{f}_finisher|{c}"] = paired(f, other, f, f, c, pool)
        out["cross_minus_own"][f"rl_own_minus_base_own|{c}"] = paired("rl", "rl", "base", "base", c, pool)
        for f, probs in (("base", [i for i in pool if i in U]), ("rl", pool)):
            have = [i for i in probs if (f, f, c, i) in rows]
            out["control_own_minus_stored"][f"{f}|{c}"] = diff([rows[f, f, c, i]["score_v3"] for i in have], [P[i, f]["writer_score"] for i in have])
    out["stored_sample0_right"] = {"base_on_unbiased": sum(P[i, "base"]["writer_score"] for i in U), "rl_on_pool": sum(P[i, "rl"]["writer_score"] for i in pool),
                                   "base_on_pool": sum(P[i, "base"]["writer_score"] for i in pool)}
    return out


def table(ro: dict) -> str:
    L = ["Prefix hand-off, MATH-500 pool of %d, T 1.0 / top-p 1.0, grader v3. right/n [Wilson 95 %%], generated tokens per problem (total with prefix)." % ro["n_pool"], ""]
    for key, v in ro["strata"].items():
        b, r, d = v["base_finisher"], v["rl_finisher"], ro["rl_minus_base_finisher"][key]
        if not b["n"]:
            continue
        f = lambda x: "%d/%d [%.0f, %.0f] %.0f (%.0f)" % (x["right"], x["n"], *x["wilson95"], x["tokens_generated_per_problem"], x["tokens_total_per_problem"])
        L.append("%-44s base finisher %-34s RL finisher %-34s RL-base %+.1f [%+.1f, %+.1f]  fresh base %.0f RL %.0f"
                 % (key, f(b), f(r), d["points"], *d["ci95"], v["fresh_rate_samples_1_3"]["base"], v["fresh_rate_samples_1_3"]["rl"]))
    L.append("")
    for name in ("pool", ):
        for key, x in ro[name].items():
            L.append("%-34s %d/%d [%.0f, %.0f] cap hits %d, tokens %.0f (%.0f)" % (key, x["right"], x["n"], *x["wilson95"], x["cap_hits"], x["tokens_generated_per_problem"], x["tokens_total_per_problem"]))
    L.append("")
    for name in ("cross_minus_own", "control_own_minus_stored"):
        for key, d in ro[name].items():
            L.append("%s %-28s %d vs %d of %d: %+.1f [%+.1f, %+.1f]" % (name, key, d["x_right"], d["y_right"], d["n"], d["points"], *d["ci95"]))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True, help="<finisher>=<directory with answers.jsonl and metrics.json>")
    ap.add_argument("--out", required=True)
    ap.add_argument("--nn", default="01")
    a = ap.parse_args()
    plan = json.loads((STUDY / "data" / "handoff" / "plan_v1.json").read_text())
    P = {(r["problem_index"], r["writer"]): r for r in plan["rows"]}
    rows, info = {}, {}
    for spec in a.run:
        fin, d = spec.split("=")
        d = pathlib.Path(d)
        m = json.loads((d / "metrics.json").read_text())
        assert m["config"]["finisher"] == fin, (fin, m["config"]["finisher"])
        raw = [json.loads(l) for l in (d / "answers.jsonl").read_text().splitlines()]
        missing = m["config"]["n_requests"] - len(raw)
        assert missing <= 0.02 * m["config"]["n_requests"], f"{fin}: {missing} of {m['config']['n_requests']} rows missing"
        comp = [score(r, P[r["problem_index"], r["writer"]]) for r in raw]
        folder = pathlib.Path(a.out) / f"{fin}-{a.nn}"
        folder.mkdir(parents=True)
        order = sorted(range(len(raw)), key=lambda k: (comp[k]["writer"], comp[k]["cut"], comp[k]["problem_index"]))
        (folder / "rows.jsonl").write_text("".join(json.dumps({k: comp[k_][k] for k in COMPACT}) + "\n" for k_ in order))
        shutil.copy(d / "metrics.json", folder / "metrics.json")
        (folder / "run.json").write_text(json.dumps({"commit": m["commit"], "job_id": m["job_id"], "config": m["config"], "status": m["status"],
                                                     "rows": len(raw), "rows_missing": missing, "raw": f"answers.jsonl in $OUT_DIR of {m['job_id']} (Volume iterate-runs)"}, indent=1) + "\n")
        pick = {"right": lambda r: r["score_v3"] == 1 and r["cut"] in CUTS, "wrong": lambda r: r["score_v3"] == 0 and not r["cap_hit"] and r["cut"] in CUTS,
                "recovery_from_wrong_prefix": lambda r: r["stratum"] == "wrong" and r["score_v3"] == 1 and r["cut"] >= 50,
                "spoiled_right_prefix": lambda r: r["stratum"] == "right" and r["score_v3"] == 0 and r["cut"] >= 50 and not r["cap_hit"]}
        ex = {name: next((example(raw[k], comp[k]) for k in order if ok(comp[k])), None) for name, ok in pick.items()}
        (folder / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
        info[fin] = {"job_id": m["job_id"], "status": m["status"], "rows": len(raw), "rows_missing": missing, "loop_errors": sum(r["loop_error"] is not None for r in comp),
                     "loop_A": sum(bool(r["loop_A"]) for r in comp), "generated_tokens": sum(r["n_new"] for r in comp), "counts": m.get("counts")}
        for r in comp:
            rows[fin, r["writer"], r["cut"], r["problem_index"]] = r
        print(fin, info[fin])
    if len(info) == 2:
        ro = {"finishers": info, **readout(rows, plan)}
        folder = pathlib.Path(a.out) / f"readout-{a.nn}"
        folder.mkdir(parents=True)
        (folder / "readout.json").write_text(json.dumps(ro, indent=1) + "\n")
        (folder / "readout.txt").write_text(table(ro))
        print(table(ro))


if __name__ == "__main__":
    main()
