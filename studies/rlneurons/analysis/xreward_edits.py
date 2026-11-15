"""xreward Part 2 readout (specs/SPEC_xreward.md, amendments): rank-8 edits with the cue on the 328 harder problems, T 1.0 / top-p 1.0,
grader v3, beside base cue, RL plain, RL cue (Day-1 #1) and theta(0.25), theta(0.5), Code-RL (Day-1 #4b).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.xreward_edits

Run from the repository root. Inputs (not committed): runs/<job-id>/ of every job in OLD, WDIFF and NEW (`uv run tools/gpu.py get`).
Writes results/xreward/edits/readout.json and one run folder results/xreward/edits/<arm>-01/ per new cell (skipped if it exists).
"""
from __future__ import annotations

import json
import pathlib
import shutil

from studies.rlneurons.analysis.day1_hard328 import JOBS as OLD, examples, rows_by_index, score, summary
from studies.rlneurons.analysis.day1_wdiff import diff
from studies.rlneurons.analysis.day1_wdiff328 import NEW as WDIFF, clean_set

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "xreward" / "edits"
# arm -> (job id, wsp_edit recipe arguments); every cell: run_cell --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000
NEW = {
    "top8_math31": ("abaybektursun-1114-221034-007d", "--recipe top8 --other rl_math"),
    "rand8_math31": ("abaybektursun-1114-221040-5f1e", "--recipe rand8 --other rl_math"),
    "top8_code31": ("abaybektursun-1114-221053-fb3f", "--recipe top8 --other rl_code"),
    "bulk_math31": ("abaybektursun-1114-221100-1e31", "--recipe bulk --other rl_math"),
    "top1_math31": ("abaybektursun-1115-000358-d11a", "--recipe top8 --k 1 --other math31"),                 # amendment 3
    "top64_math31": ("abaybektursun-1115-003755-b90d", "--recipe top8 --k 64 --other math31"),
    "top8attn_math31": ("abaybektursun-1115-012835-a431", "--recipe top8 --mods q,k,v,o --other math31"),
    "top8mlp_math31": ("abaybektursun-1115-012846-905e", "--recipe top8 --mods gate,up,down --other math31"),
    "top8x2_math31": ("abaybektursun-1115-012855-d7ed", "--recipe top8 --scale 2 --other math31"),
    "proj_math31_code30": ("abaybektursun-1115-012905-8f73", "--recipe proj --donor code30 --other math31"),
    "projc_math31_code30": ("abaybektursun-1115-012915-6618", "--recipe projc --donor code30 --other math31"),
    "top8_code30": ("abaybektursun-1115-012925-b15d", "--recipe top8 --other code30"),
    "rbulk_math31": ("abaybektursun-1115-012935-2836", "--recipe rbulk --other math31"),                      # amendment 4
    "top8xm1_math31": ("abaybektursun-1115-031209-1273", "--recipe top8 --scale -1 --other math31"),          # amendment 5
    "top8x0.5_math31": ("abaybektursun-1115-031219-19af", "--recipe top8 --scale 0.5 --other math31"),
    "top8x1.5_math31": ("abaybektursun-1115-031229-5991", "--recipe top8 --scale 1.5 --other math31"),
    "top8x3_math31": ("abaybektursun-1115-031240-1106", "--recipe top8 --scale 3 --other math31"),
    "rand8xm1_math31": ("abaybektursun-1115-031249-1dcd", "--recipe rand8 --scale -1 --other math31"),
    "rand8x2_math31": ("abaybektursun-1115-031304-cf34", "--recipe rand8 --scale 2 --other math31"),
    "rand8x3_math31": ("abaybektursun-1115-031315-b328", "--recipe rand8 --scale 3 --other math31"),
    "top8_math30": ("abaybektursun-1115-031326-369f", "--recipe top8 --other math30"),
    "top8_if30": ("abaybektursun-1115-031336-56ff", "--recipe top8 --other if30"),
    "top8_general30": ("abaybektursun-1115-031346-5113", "--recipe top8 --other general30"),
    "top8_think_sft": ("abaybektursun-1115-031356-77f0", "--recipe top8 --other think_sft"),
}
REFS = {"base_cue_T1": OLD["base_cue_T1"][0], "rl_plain_T1": OLD["rl_plain_T1"][0], "rl_cue_T1": OLD["rl_cue_T1"][0],
        "theta0.25_cue": WDIFF["theta0.25_cue"][0], "theta0.5_cue": WDIFF["theta0.5_cue"][0], "code1_cue": WDIFF["code1_cue"][0]}
BASE, RL = "base_cue_T1", "rl_plain_T1"


def main():
    clean, gold, _ = clean_set()
    rows, sc, cells = {}, {}, {}
    for arm, job in {**REFS, **{k: v[0] for k, v in NEW.items()}}.items():
        if not (RUNS / job / "metrics.json").exists():
            print(f"{arm}: runs/{job} is not here, skipped")
            continue
        m = json.loads((RUNS / job / "metrics.json").read_text())
        assert m["status"] == "done" and m["counts"]["n"] == 328 and m["job_id"] == job, (arm, m["status"], m["counts"])
        rows[arm] = rows_by_index(RUNS / job / "answers.jsonl", clean)
        sc[arm] = score(rows[arm], gold)
        cells[arm] = {**summary(sc[arm]), "job_id": job, "seed_base": m["config"]["seed"], "answers": f"runs/{job}/answers.jsonl"}
        if arm in NEW:
            c, e = m["config"], json.loads((RUNS / job / "edit.json").read_text())
            assert c["set"] == "hard328" and c["prompt"] == "cue" and c["temperature"] == c["top_p"] == 1.0 and c["seed"] == 3000000, (arm, c)
            ea = e["args"]
            want = f"--recipe {ea['recipe']}" + "".join(f" --{f} {ea[f]:g}" if isinstance(ea[f], float) else f" --{f} {ea[f]}" for f, dflt in (("k", 8), ("mods", None), ("scale", 1.0), ("donor", None)) if ea.get(f) not in (None, dflt)) + f" --other {ea['other']}"
            assert c["model_label"] == arm and want == NEW[arm][1], (arm, c["model_label"], want)
            cells[arm]["edit"] = {"recipe": e["recipe"], "other": ea["other"], "donor": ea.get("donor"), "mods": ea.get("mods"), "scale": ea.get("scale", 1.0), "k": e["k"],
                                  "rounding": e["rounding"], "n_edited": e["n_edited"], **e["totals"]}
            d = OUT / f"{arm}-01"
            if not d.exists():
                d.mkdir(parents=True)
                (d / "run.json").write_text(json.dumps({"job_id": job, "commit": m["commit"], "command": "wsp_edit " + NEW[arm][1] + " --rounding stochastic --seed 0, then run_cell "
                                                        "--prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000", "runner": "uv run tools/gpu.py submit h100 --hours 2",
                                                        "raw_answers": f"runs/{job}/answers.jsonl (uv run tools/gpu.py get {job})"}, indent=1) + "\n")
                shutil.copy(RUNS / job / "metrics.json", d / "metrics.json")
                e.pop("tensors")
                (d / "edit.json").write_text(json.dumps(e, indent=1) + "\n")
                i0 = min(rows[arm])                                                 # a cell with no right answer (a broken model) saves its first row
                ex = examples(rows[arm], sc[arm]) if any(s["v3"] for s in sc[arm].values()) else {"right": None, "wrong": {
                    "problem_index": i0, "gold": rows[arm][i0]["gold"], "cap_hit": bool(rows[arm][i0]["cap_hit"]), "answer_head": rows[arm][i0]["text"][:800]}}
                (d / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
            cells[arm]["run_folder"] = f"studies/rlneurons/results/xreward/edits/{d.name}"
    new = [a for a in NEW if a in sc]
    more = [("top8_math31", "theta0.5_cue"), ("top8_math31", "top8_code31"), ("bulk_math31", "rl_cue_T1"), ("top8_code31", "code1_cue"), ("top8mlp_math31", "top8attn_math31"),
            ("proj_math31_code30", "projc_math31_code30"), ("top8_code30", "top8_code31"), ("rbulk_math31", "bulk_math31"), ("rbulk_math31", "rl_cue_T1")]
    pairs = [(x, y) for x in new for y in (BASE, RL, "rand8_math31", "top8_math31") if x != y] + [(x, y) for x, y in more if x in sc and y in sc]
    diffs = {f"{x} minus {y}": diff(sc, x, y, clean) for x, y in pairs}
    churn = {a: {"fixed_of_base_cue_wrong": sum(sc[BASE][i]["v3"] == 0 and sc[a][i]["v3"] == 1 for i in clean),
                 "lost_of_base_cue_right": sum(sc[BASE][i]["v3"] == 1 and sc[a][i]["v3"] == 0 for i in clean),
                 "right_of_rl_only": sum(sc[a][i]["v3"] for i in clean if sc[RL][i]["v3"] == 1 and sc[BASE][i]["v3"] == 0)} for a in sc if a != BASE}
    churn["rl_only"] = sum(sc[RL][i]["v3"] == 1 and sc[BASE][i]["v3"] == 0 for i in clean)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "readout.json").write_text(json.dumps({"n": 328, "grader": "v3", "cells": cells, "paired_differences_points": diffs, "churn_against_base_cue": churn}, indent=1) + "\n")
    for a, c in cells.items():
        print(f"{a:>14}  right {c['right_v3']:>3} of 328  cap hits {c['cap_hits']:>3}  tokens {c.get('mean_tokens', c.get('mean_generated_tokens', ''))}")
    print(json.dumps(diffs, indent=1))
    print(json.dumps(churn, indent=1))


if __name__ == "__main__":
    main()
