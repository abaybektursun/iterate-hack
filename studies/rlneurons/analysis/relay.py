"""Relay readout on hard328 (specs/SPEC_relay.md): writer {think, rl} x finisher {think, rl} x cut. Scores the raw rows of
jobs/handoff_gen.py --plan plan_v2.json with analysis/handoff.py's scorer (grader v3 on prefix + continuation) and writes one run
folder per job and the tables.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.relay \
        --run runs/<job> --run runs/<job> ... --out studies/rlneurons/results/relay --nn 01

Writes <out>/<finisher>_c<cuts>-<nn>/ (run.json, metrics.json, rows.jsonl without text, examples.json: one right, one wrong) and
<out>/readout-<nn>/: readout.json, readout.txt, examples.json (think -> rl at 50 %: 10 problems it gets right where the Think-SFT
sample is wrong, 10 it loses, 6 cap-hit prefixes). Every arm must be complete (328 rows). Fail loud.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil

from studies.rlneurons.analysis import handoff as A

STUDY = A.STUDY
CUTS = (25, 50)
MODELS = ("think", "rl")
GROUPS = {"all": lambda p: True, "right": lambda p: p["stratum"] == "right", "wrong": lambda p: p["stratum"] == "wrong", "cap": lambda p: p["stratum"] == "cap",
          "not_cap": lambda p: p["stratum"] != "cap", "aime": lambda p: p["source"].startswith("aime"), "not_aime": lambda p: not p["source"].startswith("aime")}


def readout(rows: dict, plan: dict) -> dict:
    """rows: {(finisher, writer, cut, problem): compact row}."""
    P = {(r["problem_index"], r["writer"]): r for r in plan["rows"]}
    pool = plan["pool"]
    out = {"n": len(pool), "stored": {}, "arms": {}, "arm_minus_stored": {}, "cross_minus_own_same_writer": {}, "cross_minus_own_same_finisher": {}}
    for w in MODELS:
        for g, ok in GROUPS.items():
            ps = [P[i, w] for i in pool if ok(P[i, w])]
            out["stored"][f"{w}|{g}"] = {"right": sum(p["writer_score"] for p in ps), "n": len(ps), "cap_hits": sum(p["stratum"] == "cap" for p in ps),
                                         "tokens_per_problem": sum(p["n_ids"] for p in ps) / len(ps)}
    for w in MODELS:
        other = MODELS[1 - MODELS.index(w)]
        for c in CUTS:
            for g, ok in GROUPS.items():
                probs = [i for i in pool if ok(P[i, w])]                       # groups are by the writer sample's outcome and source
                for f in MODELS:
                    out["arms"][f"{w}->{f}|{c}|{g}"] = A.cell([rows[f, w, c, i] for i in probs])
                    for m in MODELS:                                            # against each model's stored sample 0 on the same problems
                        out["arm_minus_stored"][f"{w}->{f}|{c}|{g}|minus_{m}"] = A.diff([rows[f, w, c, i]["score_v3"] for i in probs], [P[i, m]["writer_score"] for i in probs])
                out["cross_minus_own_same_writer"][f"{w}->{other} minus {w}->{w}|{c}|{g}"] = A.diff(
                    [rows[other, w, c, i]["score_v3"] for i in probs], [rows[w, w, c, i]["score_v3"] for i in probs])
            out["cross_minus_own_same_finisher"][f"{w}->{other} minus {other}->{other}|{c}|all"] = A.diff(
                [rows[other, w, c, i]["score_v3"] for i in pool], [rows[other, other, c, i]["score_v3"] for i in pool])
    return out


def table(ro: dict) -> str:
    L = ["Relay on hard328 (n = %d), T 1.0 / top-p 1.0, grader v3, one sample. right/n [Wilson 95 %%], cap hits, tokens per problem generated (total with prefix)." % ro["n"], ""]
    for key, s in ro["stored"].items():
        L.append("stored %-22s %d/%d cap hits %d, tokens %.0f" % (key, s["right"], s["n"], s["cap_hits"], s["tokens_per_problem"]))
    L.append("")
    for key, x in ro["arms"].items():
        L.append("%-26s %d/%d [%.0f, %.0f] cap hits %d (wrong %d), no answer %d, tokens %.0f (%.0f)" % (
            key, x["right"], x["n"], *x["wilson95"], x["cap_hits"], x["wrong_cap_hits"], x["wrong_no_answer"], x["tokens_generated_per_problem"], x["tokens_total_per_problem"]))
    for name in ("cross_minus_own_same_writer", "cross_minus_own_same_finisher", "arm_minus_stored"):
        L.append("")
        for key, d in ro[name].items():
            L.append("%s %-44s %d vs %d of %d: %+.1f points [%+.1f, %+.1f], only x %d, only y %d" % (name, key, d["x_right"], d["y_right"], d["n"], d["points"], *d["ci95"], d["x_only"], d["y_only"]))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True, help="a job directory with answers.jsonl and metrics.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--nn", default="01")
    a = ap.parse_args()
    plan = json.loads((STUDY / "data" / "handoff" / "plan_v2.json").read_text())
    P = {(r["problem_index"], r["writer"]): r for r in plan["rows"]}
    rows, raws, info = {}, {}, {}
    for d in map(pathlib.Path, a.run):
        m = json.loads((d / "metrics.json").read_text())
        fin, cuts = m["config"]["finisher"], m["config"]["cuts"]
        assert m["status"] == "done" and m["config"]["plan"] == "plan_v2.json" and m["config"]["n"] is None, d
        raw = [json.loads(l) for l in (d / "answers.jsonl").read_text().splitlines()]
        assert len(raw) == m["config"]["n_requests"] == 2 * len(plan["pool"]) * len(cuts), (d, len(raw))
        comp = [A.score(r, P[r["problem_index"], r["writer"]]) for r in raw]
        name = f"{fin}_c{'-'.join(map(str, cuts))}-{a.nn}"
        folder = pathlib.Path(a.out) / name
        folder.mkdir(parents=True)
        order = sorted(range(len(raw)), key=lambda k: (comp[k]["writer"], comp[k]["cut"], comp[k]["problem_index"]))
        (folder / "rows.jsonl").write_text("".join(json.dumps({k: comp[k_][k] for k in A.COMPACT}) + "\n" for k_ in order))
        shutil.copy(d / "metrics.json", folder / "metrics.json")
        (folder / "run.json").write_text(json.dumps({"commit": m["commit"], "job_id": m["job_id"], "config": m["config"], "status": m["status"], "rows": len(raw),
                                                     "raw": f"answers.jsonl in $OUT_DIR of {m['job_id']} (Volume iterate-runs)"}, indent=1) + "\n")
        ex = {kind: next((A.example(raw[k], comp[k]) for k in order if comp[k]["score_v3"] == s and not comp[k]["cap_hit"] and comp[k]["writer"] != fin), None)
              for kind, s in (("right", 1), ("wrong", 0))}
        (folder / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
        info[name] = {"job_id": m["job_id"], "rows": len(raw), "loop_errors": sum(r["loop_error"] is not None for r in comp), "loop_A": sum(bool(r["loop_A"]) for r in comp),
                      "generated_tokens": sum(r["n_new"] for r in comp), "counts": m["counts"], "wall_s": m["wall_s"], "gpu": m["engine"].get("gpu")}
        for r, c in zip(raw, comp):
            key = (fin, c["writer"], c["cut"], c["problem_index"])
            assert key not in rows, key
            rows[key], raws[key] = c, r
        print(name, info[name])
    ro = {"runs": info, **readout(rows, plan)}
    folder = pathlib.Path(a.out) / f"readout-{a.nn}"
    folder.mkdir(parents=True)
    (folder / "readout.json").write_text(json.dumps(ro, indent=1) + "\n")
    (folder / "readout.txt").write_text(table(ro))
    key = lambda i: ("rl", "think", 50, i)
    pick = {"win_over_think_sample": [i for i in plan["pool"] if rows[key(i)]["score_v3"] and not P[i, "think"]["writer_score"]][:10],
            "loss_against_think_sample": [i for i in plan["pool"] if not rows[key(i)]["score_v3"] and P[i, "think"]["writer_score"]][:10],
            "cap_hit_prefix": [i for i in plan["pool"] if P[i, "think"]["stratum"] == "cap"][:6]}
    (folder / "examples.json").write_text(json.dumps({k: [{**A.example(raws[key(i)], rows[key(i)]), "think_own_prefix_score": rows["think", "think", 50, i]["score_v3"],
                                                           "rl_stored_score": P[i, "rl"]["writer_score"]} for i in v] for k, v in pick.items()}, indent=1) + "\n")
    print(table(ro))


if __name__ == "__main__":
    main()
