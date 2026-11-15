"""WSP-1 Part 2 readout (specs/SPEC_wsp1.md, both amendments): MATH-500 cells at T 1.0 / top-p 1.0 on the base, the RL model and
the edited models of jobs/wsp_edit.py (top8, bulk, rand8, late3, sft1, sft05, ...), plain and cue prompt; grader v3.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.wsp1_readout

Run from the repository root. Inputs (not committed): runs/<job-id>/ (`uv run tools/gpu.py get <job-id>`, sameraslan's Modal
workspace): answers.jsonl, metrics.json and, for an edited model, edit.json. A job of CELLS with no answers.jsonl yet, or whose
metrics.json is not "done", is skipped with a printed note. Writes results/wsp1/readout.json and one run folder per cell,
results/wsp1/<experiment>/<label>_<prompt>-01/{run.json,metrics.json,examples.json,per_problem.json}. An existing run folder is
rewritten only if its run.json has the same job id; another job for the same cell fails (a rerun gets the next number).

Every job's config is checked against CELLS (model label, prompt, seed, n, temperature, top-p) and every edit.json against EDITS;
each stored score_v3 is checked against a rescore with rln4_lib.grade_v3, and the counts against the job's own metrics.json.

The full500 cells have no reference cells of their own. `full500_vs_references` compares them by problem index with T1 (cued
base) and T2 (RL plain) of results/rln4/t1_t2_items-01/per_problem.json. T3 (plain base) and the weight-difference cells of
results/day1_wdiff/ have no per-problem rows in git, only counts: T3 gets an unpaired difference, the others are skipped.
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import statistics

from studies.rlneurons.analysis.day1_hard328 import rows_by_index
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "wsp1"
WHO = "sameraslan-1114-"

# The cell table: (label, prompt, job id, experiment, seed base). Add a row per finished or running job.
CELLS = [
    ("base", "plain", WHO + "154255-ff2f", "screen100", 80000000),
    ("rl", "plain", WHO + "154304-be68", "screen100", 80000000),
    ("top8", "plain", WHO + "184550-429d", "screen100", 80000000),
    ("bulk", "plain", WHO + "184605-5e13", "screen100", 80000000),
    ("rand8", "plain", WHO + "184610-37bf", "screen100", 80000000),
    ("late3", "plain", WHO + "184615-7f7e", "screen100", 80000000),
    ("sft1", "plain", WHO + "184623-b0fc", "screen100", 80000000),
    ("base", "cue", WHO + "154311-93e3", "screen100", 81000000),
    ("sft1", "cue", WHO + "184627-f7eb", "screen100", 81000000),
    ("sft05", "cue", WHO + "184632-401b", "screen100", 81000000),
    # Amendment 2
    ("top1", "plain", WHO + "185952-2e78", "screen100", 80000000),
    ("bulk64", "plain", WHO + "185958-fb46", "screen100", 80000000),
    ("top8", "plain", WHO + "185934-b0a9", "full500", 180000000),
    ("sft1", "cue", WHO + "185940-514f", "full500", 181000000),
    ("sft1", "plain", WHO + "185947-4681", "full500", 182000000),
    # Amendment 3
    ("rand8", "plain", WHO + "193553-cf1f", "full500", 183000000),
]
EXPERIMENTS = {"screen100": 100, "full500": 500}          # experiment -> the first n MATH-500 problems
REFERENCES = ("base", "rl")                               # released models (run_cell --model); every other label needs an edit.json
# label -> what its edit.json must say: (recipe, k, other, alpha)
EDITS = {"top8": ("top8", 8, "rl_math", None), "bulk": ("bulk", 8, "rl_math", None), "rand8": ("rand8", 8, "rl_math", None),
         "late3": ("late3", 3, "rl_math", None), "sft1": ("interp", None, "think_sft", 1.0), "sft05": ("interp", None, "think_sft", 0.5),
         "top1": ("top8", 1, "rl_math", None), "bulk64": ("bulk", 64, "rl_math", None)}
CONTROLS = [("top8", "rand8"), ("top1", "rand8")]         # plain cells: edited minus its matched control
# right of n stated in the spec (Amendment 2); a cell listed here must reproduce it
SPEC_COUNTS = {("screen100", "base", "plain"): 34, ("screen100", "rl", "plain"): 96, ("screen100", "top8", "plain"): 88,
               ("screen100", "bulk", "plain"): 91, ("screen100", "rand8", "plain"): 36, ("screen100", "late3", "plain"): 41,
               ("screen100", "sft1", "plain"): 91, ("screen100", "base", "cue"): 82, ("screen100", "sft1", "cue"): 92,
               ("screen100", "sft05", "cue"): 88}
# References of the full500 cells (Amendment 2): all 500 problems, T 1.0 / top-p 1.0, grader v3, one sample; right of 500 as in README.md
ITEMS = STUDY / "results" / "rln4" / "t1_t2_items-01" / "per_problem.json"    # T1 and T2 by problem, one reader's failure labels
WDIFF = STUDY / "results" / "day1_wdiff" / "readout.json"                     # counts only: these cells have no per-problem rows in git
REF_ROWS = {"T1_base_cue": ("t1_right", 410), "T2_rl_plain": ("t2_right", 463)}      # name -> (column of ITEMS, right)
REF_COUNTS = {"T3_base_plain": 224, "theta0.25_plain": 405, "theta0.5_plain": 443}   # name -> right, checked in WDIFF
UNPAIRED = ("T3_base_plain",)                             # of REF_COUNTS: unpaired difference; the others are skipped
VS = [("sft1_cue", "T1_base_cue"), ("sft1_cue", "T2_rl_plain"), ("sft1_plain", "T2_rl_plain"), ("top8_plain", "T2_rl_plain"),
      ("top8_plain", "theta0.25_plain"), ("top8_plain", "theta0.5_plain"), ("top8_plain", "T3_base_plain"),
      ("rand8_plain", "T3_base_plain"), ("top8_plain", "rand8_plain")]               # full500 cell minus reference or full500 cell
T, TOP_P, N_BOOT = 1.0, 1.0, 5000
SETUP, PY = "bash studies/rlneurons/jobs/setup_vllm.sh && ", "/opt/rln-vllm/bin/python -m studies.rlneurons.jobs."
EDIT_KEYS = ("recipe", "k", "alpha", "rounding", "seed", "late_layers", "reference", "n_tensors", "n_edited", "n_unchanged")
KEEP = 1500                                               # characters kept at each end of an example's text


def command(m, edit):
    """The job's command rebuilt from metrics.json config and edit.json args (the submitted shell string is only in the Modal
    job record). The arguments are the ones the job recorded; their order in the submitted string may differ."""
    c = m["config"]
    cell = f"--prompt {c['prompt']} --set {c['set']} --temperature {c['temperature']} --top-p {c['top_p']} --seed {c['seed']}"
    cell += (f" --n {c['n']}" if c["n"] is not None else "") + f" --commit {c['commit']}"
    if edit is None:
        return f"{SETUP}{PY}run_cell --model {c['model']} {cell}"
    a = edit["args"]
    args = f"--recipe {a['recipe']} --other {a['other']}" + (f" --alpha {a['alpha']}" if a["recipe"] == "interp" else "")
    args += (f" --k {a['k']}" if a["k"] is not None else "") + f" --rounding {a['rounding']} --seed {a['seed']} --dir {a['dir']}"
    return f"{SETUP}{PY}wsp_edit {args} && {PY}run_cell --model-path {c['model_path']} --model-label {c['model_label']} {cell}"


def load(label, prompt, job, exp, seed, gold):
    """Metrics, edit.json or None, and the rows by problem index of one finished job, after every check."""
    n = EXPERIMENTS[exp]
    m = json.loads((RUNS / job / "metrics.json").read_text())
    c, cnt = m["config"], m["counts"]
    want = {"prompt": prompt, "seed": seed, "temperature": T, "top_p": TOP_P, "set": "math500", "samples": 1, "restarts": 0}
    got = {k: c[k] for k in want}
    assert got == want, (job, "config differs from CELLS", got, want)
    assert c["n"] == n or (c["n"] is None and n == 500), (job, "n", c["n"], n)
    assert m["job_id"] == job and m["commit"] == c["commit"] and cnt["n"] == c["n_problems"] == n, (job, m["job_id"], cnt["n"])
    edit_file = RUNS / job / "edit.json"
    if label in REFERENCES:
        assert c["model"] == label and c["model_label"] is None and not edit_file.exists(), (job, "model", c["model"], c["model_label"])
        edit = None
    else:
        assert c["model"] is None and c["model_label"] == label, (job, "model label", c["model"], c["model_label"], label)
        edit = json.loads(edit_file.read_text())          # an edited model without edit.json fails here
        got = (edit["recipe"], edit["k"], edit["args"]["other"], edit["alpha"])
        assert got == EDITS[label], (job, "edit.json differs from EDITS", got, EDITS[label])
    rows = rows_by_index(RUNS / job / "answers.jsonl", range(n))
    for i, r in rows.items():
        assert r["seed"] == seed + i and r["sample"] == 0 and r["attempt"] == 0, (job, i, r["seed"])
        assert r["model"] == label and r["prompt_arm"] == prompt and r["gold"] == gold[i], (job, i, r["model"], r["prompt_arm"])
        assert r["score_v3"] == R.grade_v3(gold[i], r["text"])["score_v3"], (job, i, "stored v3 score differs from the rescore")
    tot = (sum(r["score_v3"] for r in rows.values()), sum(r["cap_hit"] for r in rows.values()), sum(r["n_new"] for r in rows.values()))
    assert tot == (cnt["correct_v3"], cnt["cap_hits"], cnt["generated_tokens"]), (job, "rows differ from metrics.json counts", tot)
    return m, edit, rows


def measure(rows, edit):
    rs = list(rows.values())
    n, right = len(rs), [r for r in rs if r["score_v3"]]
    lo, hi = S.wilson(len(right), n)
    tokens = [r["n_generated"] for r in rs]
    okay = sum("Okay" in r["text"][:80] for r in rs)
    empty = sum(r["n_generated"] <= 3 for r in rs)
    res = {"n": n, "right_v3": len(right), "acc_v3": round(100 * len(right) / n, 2), "wilson95": [round(lo, 1), round(hi, 1)],
           "cap_hits": sum(r["cap_hit"] for r in rs),
           "mean_generated_tokens": round(statistics.mean(tokens), 1), "median_generated_tokens": statistics.median(tokens),
           "median_tokens_right": statistics.median(r["n_generated"] for r in right) if right else None,
           "okay_first80": okay, "okay_first80_share": round(okay / n, 3),
           "wait_per_answer": round(sum(r["text"].count("wait") + r["text"].count("Wait") for r in rs) / n, 2),
           "empty": empty, "empty_share": round(empty / n, 3)}
    if edit is not None:
        res["edit"] = {**{k: edit[k] for k in EDIT_KEYS}, "other": edit["args"]["other"], **edit["totals"]}
    return res


def example(r):
    if r is None:
        return None
    t = r["text"]
    cut = len(t) > 2 * KEEP
    text = f"{t[:KEEP]}\n[... {len(t) - 2 * KEEP} characters left out ...]\n{t[-KEEP:]}" if cut else t
    return {"problem_index": r["problem_index"], "unique_id": r["unique_id"], "seed": r["seed"], "gold": r["gold"],
            "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "cap_hit": r["cap_hit"], "n_generated": r["n_generated"],
            "text_characters": len(t), "text_truncated": cut, "text": text}


def write_run(name, exp, job, files):
    d = OUT / exp / f"{name}-01"
    if d.exists():
        old = json.loads((d / "run.json").read_text())["job_id"]
        assert old == job, f"{d} holds job {old}, not {job}: a rerun gets the next number"
    d.mkdir(parents=True, exist_ok=True)
    for file, text in files.items():
        (d / file).write_text(text)
    return f"studies/rlneurons/results/{OUT.name}/{exp}/{d.name}"


def dump(x):
    return json.dumps(x, indent=1) + "\n"


def diff(rows, x, y):
    assert rows[x].keys() == rows[y].keys(), (x, y)
    idx = sorted(rows[x])
    vx, vy = [rows[x][i]["score_v3"] for i in idx], [rows[y][i]["score_v3"] for i in idx]
    lo, hi = S.paired_bootstrap(vx, vy, n_boot=N_BOOT, seed=0)
    return {"n": len(idx), "points": round(100 * (sum(vx) - sum(vy)) / len(idx), 2), "ci95": [round(lo, 2), round(hi, 2)]}


def unpaired(k1, k2, n):
    """Difference of two cells of n problems with no shared rows: Newcombe's interval from the two Wilson 95 % intervals."""
    (l1, u1), (l2, u2), p1, p2 = S.wilson(k1, n), S.wilson(k2, n), 100 * k1 / n, 100 * k2 / n
    lo, hi = p1 - p2 - math.hypot(p1 - l1, u2 - p2), p1 - p2 + math.hypot(u1 - p1, p2 - l2)
    return {"n": n, "points": round(p1 - p2, 2), "ci95": [round(lo, 2), round(hi, 2)]}


def references(rows):
    """The finished full500 cells against the study's reference cells: differences (VS), the sft1 cue cell on the problems
    that RL solves and the cued base does not, and the 2 x 2 table of top8 plain against RL."""
    items = json.loads(ITEMS.read_text())
    by = {r["problem_index"]: r for r in items}
    assert len(items) == len(by) == 500 and set(by) == set(range(500)), (ITEMS, "not the 500 distinct problem indices")
    sc = {f"{lab}_{p}": rs for (e, lab, p), rs in rows.items() if e == "full500"}
    refs = {}
    for name, (col, right) in REF_ROWS.items():
        assert sum(r[col] for r in items) == right, (name, sum(r[col] for r in items), "differs from the README's count", right)
        sc[name] = {i: {"score_v3": r[col]} for i, r in by.items()}
        refs[name] = {"n": 500, "right_v3": right, "rows": f"studies/rlneurons/results/rln4/{ITEMS.parent.name}/{ITEMS.name} ({col})"}
    wd = json.loads(WDIFF.read_text())["cells"]
    for name, right in REF_COUNTS.items():
        assert (wd[name]["n"], wd[name]["right_v3"]) == (500, right), (name, wd[name]["right_v3"], "differs from the README's count", right)
        refs[name] = {"n": 500, "right_v3": right, "rows": None, "count": f"studies/rlneurons/results/day1_wdiff/{WDIFF.name}"}
    diffs, skipped = {}, []
    for x, y in VS:
        if x not in sc or (y not in sc and y not in REF_COUNTS):
            continue                                      # a full500 cell that is not finished
        if y in sc:                                       # diff asserts equal index sets
            diffs[f"{x} minus {y}"] = {**diff(sc, x, y), "paired": True}
        elif y in UNPAIRED:
            diffs[f"{x} minus {y}"] = {**unpaired(sum(r["score_v3"] for r in sc[x].values()), REF_COUNTS[y], 500), "paired": False}
        else:
            skipped.append(f"{x} minus {y}: no per-problem rows of {y} in git, only its count {REF_COUNTS[y]} of 500")
    res = {"references": refs, "differences": diffs, "skipped": skipped,
           "intervals": f"paired: by problem index, bootstrap as above ({N_BOOT:,} resamples, seed 0, 95 % percentile); unpaired (the "
                        "reference has no per-problem rows in git): Newcombe's interval from the two Wilson 95 % intervals; in points"}
    cell = {c: [r for r in items if (r["t1_right"], r["t2_right"]) == k] for c, k in (("rl_only", (0, 1)), ("both", (1, 1)))}
    assert (len(cell["rl_only"]), len(cell["both"])) == (65, 398) and all(r["cell"] == c for c, rs in cell.items() for r in rs)
    assert all((r["failure_type"] is not None) == (r["cell"] == "rl_only") for r in items), "failure labels are not on the 65 rows"
    if "sft1_cue" in sc:
        ok = {i: r["score_v3"] for i, r in sc["sft1_cue"].items()}
        types = collections.Counter(r["failure_type"] for r in cell["rl_only"])
        res["sft1_cue_on_T1_T2_cells"] = {
            "rl_only": {"what": "T1 (cued base) wrong, T2 (RL) right", "n": 65, "solved": sum(ok[r["problem_index"]] for r in cell["rl_only"]),
                        "by_failure_type": {t: {"n": n, "solved": sum(ok[r["problem_index"]] for r in cell["rl_only"] if r["failure_type"] == t)}
                                            for t, n in types.most_common()},
                        "failure_type": "hand label of T1's failure by one reader (t1_t2_items-01/notes.md)",
                        "unsolved_indices": [r["problem_index"] for r in cell["rl_only"] if not ok[r["problem_index"]]]},
            "both": {"what": "T1 right, T2 right", "n": 398, "wrong": sum(not ok[r["problem_index"]] for r in cell["both"]),
                     "wrong_indices": [r["problem_index"] for r in cell["both"] if not ok[r["problem_index"]]]}}
    if "top8_plain" in sc:
        n = collections.Counter((sc["top8_plain"][i]["score_v3"], by[i]["t2_right"]) for i in by)
        res["top8_plain_by_T2_rl_plain"] = {"both": n[1, 1], "only_top8": n[1, 0], "only_rl": n[0, 1], "neither": n[0, 0]}
    return res


def pairs(have, exp):
    """The differences of one experiment, among its finished cells (label, prompt)."""
    plain = [lab for (e, lab, p) in have if e == exp and p == "plain"]
    cue = [lab for (e, lab, p) in have if e == exp and p == "cue"]
    out = [("rl", "base", "plain")] + [(lab, ref, "plain") for lab in plain if lab not in REFERENCES for ref in REFERENCES]
    out += [(x, y, "plain") for x, y in CONTROLS] + [(lab, "base", "cue") for lab in cue if lab != "base"]
    return [(x, y, p) for x, y, p in out if (exp, x, p) in have and (exp, y, p) in have]


def main():
    assert len({(e, lab, p) for lab, p, _, e, _ in CELLS}) == len(CELLS) == len({job for _, _, job, _, _ in CELLS}), "CELLS has a duplicate"
    gold = {int(p["index"]): p["answer"] for p in json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())}
    rows, cells, skipped = {}, {}, []
    for label, prompt, job, exp, seed in CELLS:
        name = f"{label}_{prompt}"
        if not (RUNS / job / "answers.jsonl").exists():
            skipped.append({"cell": f"{exp}/{name}", "job_id": job, "why": "no answers.jsonl in runs/"})
            continue
        status = json.loads((RUNS / job / "metrics.json").read_text())["status"]
        if status != "done":
            skipped.append({"cell": f"{exp}/{name}", "job_id": job, "why": f"metrics.json status {status}"})
            continue
        m, edit, rs = load(label, prompt, job, exp, seed, gold)
        met = measure(rs, edit)
        if (exp, label, prompt) in SPEC_COUNTS:
            assert met["right_v3"] == SPEC_COUNTS[exp, label, prompt], (exp, name, met["right_v3"], "differs from the spec's count")
        run = {"job_id": job, "commit": m["commit"], "command": command(m, edit),
               "command_source": "rebuilt from metrics.json config and edit.json args; argument order of the submitted string not recorded",
               "gpu": m["memory"]["gpu"], "seed": seed, "seed_rule": m["config"]["seed_rule"], "n": met["n"], "experiment": exp,
               "label": label, "prompt": prompt, "temperature": T, "top_p": TOP_P, "started_utc": m["started_utc"],
               "raw_answers": f"runs/{job}/answers.jsonl (uv run tools/gpu.py get {job}; sameraslan's Modal workspace)"}
        by_index = sorted(rs.values(), key=lambda r: r["problem_index"])
        ex = {"rule": f"lowest problem index scored right and scored wrong; text cut to its first and last {KEEP} characters",
              "right": example(next((r for r in by_index if r["score_v3"]), None)),
              "wrong": example(next((r for r in by_index if not r["score_v3"]), None))}
        per = [{k: r[k] for k in ("problem_index", "score_v3", "cap_hit", "n_generated")} for r in by_index]
        folder = write_run(name, exp, job, {"run.json": dump(run), "metrics.json": dump(met), "examples.json": dump(ex),
                                            "per_problem.json": "[\n" + ",\n".join(json.dumps(r) for r in per) + "\n]\n"})
        rows[exp, label, prompt] = rs
        cells[f"{exp}/{name}"] = {"experiment": exp, "label": label, "prompt": prompt, "job_id": job, "seed_base": seed,
                                  "gpu": m["memory"]["gpu"], **met, "run_folder": folder}

    diffs = {}
    for exp in EXPERIMENTS:
        for x, y, p in pairs(rows, exp):
            diffs[f"{exp}: {x}_{p} minus {y}_{p}"] = diff(rows, (exp, x, p), (exp, y, p))
    res = {"spec": "studies/rlneurons/specs/SPEC_wsp1.md", "grader": "rln4_lib.grade_v3 (stored score_v3, equal to a rescore)",
           "set": "the first n MATH-500 problems, T 1.0, top-p 1.0, one sample", "cells": cells, "differences": diffs,
           "bootstrap": f"paired by problem index, {N_BOOT:,} resamples, seed 0, 95 % percentile, in points",
           "full500_vs_references": references(rows), "skipped": skipped,
           "notes": ["tokens are n_generated, which counts the stop token: one more than the job's n_new for an answer that stopped",
                     "empty: n_generated <= 3",
                     "okay_first80: 'Okay' in the first 80 characters of the text; the cue prompt forces ' line!\\n\\nOkay' as the "
                     "first 3 tokens of the text, so the share is 1 in every cue cell by construction",
                     "wait_per_answer: occurrences of 'wait' plus 'Wait' as substrings, mean over all answers",
                     "sft1 is Think-SFT as released (interp, alpha 1, nearest rounding): its edit totals are empty, no tensor is edited"]}
    (OUT / "readout.json").write_text(dump(res))

    print(f"{'cell':<26}{'right/n':>9}{'Wilson 95 %':>14}{'cap':>5}{'mean tok':>10}{'med tok':>9}{'med right':>10}{'Okay80':>8}{'wait':>7}{'empty':>7}{'add_rel':>10}")
    for name, c in cells.items():
        rel = (c.get("edit") or {}).get("add_rel")
        print(f"{name:<26}{c['right_v3']:>5}/{c['n']:<3}{c['wilson95'][0]:>7.1f}-{c['wilson95'][1]:<6.1f}{c['cap_hits']:>5}{c['mean_generated_tokens']:>10.1f}"
              f"{c['median_generated_tokens']:>9.1f}{c['median_tokens_right']:>10.1f}{100 * c['okay_first80_share']:>7.0f}%{c['wait_per_answer']:>7.2f}"
              f"{100 * c['empty_share']:>6.0f}%{'-' if rel is None else format(rel, '.2e'):>10}")
    print(f"\npaired differences, points [95 % bootstrap interval], {N_BOOT:,} resamples")
    for name, d in diffs.items():
        print(f"{name:<44}{d['points']:>+7.1f}  [{d['ci95'][0]:+.1f}, {d['ci95'][1]:+.1f}]  n {d['n']}")
    vs = res["full500_vs_references"]
    print("\nfull500 against the reference cells, right of 500: " + ", ".join(f"{k} {v['right_v3']}" for k, v in vs["references"].items()))
    for name, d in vs["differences"].items():
        print(f"{name:<44}{d['points']:>+7.1f}  [{d['ci95'][0]:+.1f}, {d['ci95'][1]:+.1f}]  n {d['n']}  {'paired' if d['paired'] else 'unpaired (Newcombe, Wilson)'}")
    for s in vs["skipped"]:
        print(f"skipped {s}")
    if "sft1_cue_on_T1_T2_cells" in vs:
        o, b = vs["sft1_cue_on_T1_T2_cells"]["rl_only"], vs["sft1_cue_on_T1_T2_cells"]["both"]
        print(f"sft1_cue solves {o['solved']} of the {o['n']} problems that T2 (RL) solves and T1 (cued base) does not; by T1's failure label: "
              + ", ".join(f"{t} {v['solved']}/{v['n']}" for t, v in o["by_failure_type"].items()))
        print(f"sft1_cue is wrong on {b['wrong']} of the {b['n']} problems that T1 and T2 both solve")
    if "top8_plain_by_T2_rl_plain" in vs:
        t = vs["top8_plain_by_T2_rl_plain"]
        print(f"top8_plain against T2_rl_plain: both right {t['both']}, only top8 {t['only_top8']}, only RL {t['only_rl']}, neither {t['neither']}")
    for s in skipped:
        print(f"skipped {s['cell']} ({s['job_id']}): {s['why']}")


if __name__ == "__main__":
    main()
