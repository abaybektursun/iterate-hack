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

The hard328 cells (amendment 5: the 328 clean harder problems, data/rln3/hard.json by its `index`) are compared by problem
index with the Day-1 #1 cells, whose per-problem 0/1 scores are in results/axis/hard328-01/vectors.json (counts checked
against results/day1_hard328/readout.json): `hard328_vs_references` of results/wsp1/readout.json.

WSP-2 (specs/SPEC_wsp2.md, jobs/wsp_handedit.py) cells are in CELLS2: an edited model with handedit.json in place of
edit.json, checked against HANDEDITS. They write results/wsp2/<experiment>/<label>_<prompt>-01/ and results/wsp2/readout.json,
compared by problem with the WSP-1 screen100 cells and, on all 500, with T1, T2, `top8`, `rand8` (paired) and T3 (unpaired).
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
    # Amendment 4: slices of the Think-SFT delta
    ("sfttop8", "plain", WHO + "193945-bc28", "screen100", 80000000),
    ("sfttop64", "plain", WHO + "193951-d055", "screen100", 80000000),
    ("sft025", "plain", WHO + "193957-0cd5", "screen100", 80000000),
    ("sft025", "cue", WHO + "194003-f897", "screen100", 81000000),
    ("top8", "plain", WHO + "185934-b0a9", "full500", 180000000),
    ("sft1", "cue", WHO + "185940-514f", "full500", 181000000),
    ("sft1", "plain", WHO + "185947-4681", "full500", 182000000),
    # Amendment 3
    ("rand8", "plain", WHO + "193553-cf1f", "full500", 183000000),
    # Amendment 5: the 328 clean harder problems
    ("sft1", "cue", WHO + "204845-1055", "hard328", 3000000),
    ("sft1", "plain", WHO + "204852-d527", "hard328", 3000000),
]
# WSP-2 (specs/SPEC_wsp2.md and its amendment 1): the hand-written edit of jobs/wsp_handedit.py and its random-value control
CELLS2 = [
    ("cueprog", "plain", WHO + "215214-d12f", "screen100", 80000000),
    ("cueprog_rand", "plain", WHO + "215228-f78f", "screen100", 80000000),
    ("cueprog", "plain", WHO + "221130-eb90", "full500", 184000000),
    ("cueprog_rand", "plain", WHO + "221138-a65c", "full500", 185000000),
]
OUT2 = STUDY / "results" / "wsp2"
EXPERIMENTS = {"screen100": ("math500", 100), "full500": ("math500", 500), "hard328": ("hard328", 328)}   # experiment -> (set, first n)
REFERENCES = ("base", "rl")                               # released models (run_cell --model); every other label needs an edit.json
# label -> what its edit.json must say: (recipe, k, other, alpha)
EDITS = {"top8": ("top8", 8, "rl_math", None), "bulk": ("bulk", 8, "rl_math", None), "rand8": ("rand8", 8, "rl_math", None),
         "late3": ("late3", 3, "rl_math", None), "sft1": ("interp", None, "think_sft", 1.0), "sft05": ("interp", None, "think_sft", 0.5),
         "top1": ("top8", 1, "rl_math", None), "bulk64": ("bulk", 64, "rl_math", None),
         "sfttop8": ("top8", 8, "think_sft", None), "sfttop64": ("top8", 64, "think_sft", None), "sft025": ("interp", None, "think_sft", 0.25)}
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
# hard328 references: Day-1 #1 cells; per-problem rows from AXIS (arm name there), counts and cap hits from DAY1_328
AXIS = STUDY / "results" / "axis" / "hard328-01" / "vectors.json"
DAY1_328 = STUDY / "results" / "day1_hard328" / "readout.json"
REF328 = {"base_cue_T1": ("base_cue", 164), "rl_plain_T1": ("rl_plain", 206), "rl_cue_T1": ("rl_cue", 205),
          "base_plain_T1": ("base_plain", 76)}                                        # name -> (arm of AXIS, right of 328)
VS328 = [("sft1_cue", "base_cue_T1"), ("sft1_cue", "rl_plain_T1"), ("sft1_cue", "rl_cue_T1"), ("sft1_plain", "rl_plain_T1"),
         ("sft1_plain", "base_plain_T1")]
# WSP-2: label -> control flag that handedit.json must carry; the one tensor it may change
HANDEDITS = {"cueprog": False, "cueprog_rand": True}
HAND_TENSOR = "model.layers.31.mlp.down_proj.weight"
SCREEN2 = [(("cueprog", "plain"), ("cueprog_rand", "plain")), (("cueprog", "plain"), ("base", "plain")),
           (("cueprog", "plain"), ("base", "cue")), (("cueprog", "plain"), ("top8", "plain")), (("cueprog", "plain"), ("rl", "plain")),
           (("cueprog_rand", "plain"), ("base", "plain"))]  # screen100, (label, prompt) x minus y, paired by problem
VS2 = [("cueprog_plain", "cueprog_rand_plain"), ("cueprog_plain", "T1_base_cue"), ("cueprog_plain", "T2_rl_plain"),
       ("cueprog_plain", "top8_plain"), ("cueprog_plain", "rand8_plain"), ("cueprog_plain", "T3_base_plain"),
       ("cueprog_rand_plain", "rand8_plain"), ("cueprog_rand_plain", "T3_base_plain")]  # full500, x minus y
N_OPEN, OPEN_CHARS = 5, 120                               # WSP-2 examples: how the first answers open
T, TOP_P, N_BOOT = 1.0, 1.0, 5000
SETUP, PY = "bash studies/rlneurons/jobs/setup_vllm.sh && ", "/opt/rln-vllm/bin/python -m studies.rlneurons.jobs."
EDIT_KEYS = ("recipe", "k", "alpha", "rounding", "seed", "late_layers", "reference", "n_tensors", "n_edited", "n_unchanged")
KEEP = 1500                                               # characters kept at each end of an example's text


def command(m, edit, hand=None):
    """The job's command rebuilt from metrics.json config and edit.json (or handedit.json) args (the submitted shell string is
    only in the Modal job record). The arguments are the ones the job recorded; their order in the submitted string may differ."""
    c = m["config"]
    cell = f"--prompt {c['prompt']} --set {c['set']} --temperature {c['temperature']} --top-p {c['top_p']} --seed {c['seed']}"
    cell += (f" --n {c['n']}" if c["n"] is not None else "") + f" --commit {c['commit']}"
    if hand is not None:
        a = hand["args"]
        args = f"--dir {a['dir']} --layer {a['layer']} --batch {a['batch']} --rounding {a['rounding']}" + (" --control" if a["control"] else "")
        return f"{SETUP}{PY}wsp_handedit {args} && {PY}run_cell --model-path {c['model_path']} --model-label {c['model_label']} {cell}"
    if edit is None:
        return f"{SETUP}{PY}run_cell --model {c['model']} {cell}"
    a = edit["args"]
    args = f"--recipe {a['recipe']} --other {a['other']}" + (f" --alpha {a['alpha']}" if a["recipe"] == "interp" else "")
    args += (f" --k {a['k']}" if a["k"] is not None else "") + f" --rounding {a['rounding']} --seed {a['seed']} --dir {a['dir']}"
    return f"{SETUP}{PY}wsp_edit {args} && {PY}run_cell --model-path {c['model_path']} --model-label {c['model_label']} {cell}"


def load(label, prompt, job, exp, seed, gold):
    """Metrics, edit.json or None, handedit.json or None, and the rows by problem index of one finished job, after every check.
    gold: set -> {problem index: answer}."""
    pset, n = EXPERIMENTS[exp]
    keep = sorted(gold[pset])[:n]
    gold = gold[pset]
    m = json.loads((RUNS / job / "metrics.json").read_text())
    c, cnt = m["config"], m["counts"]
    want = {"prompt": prompt, "seed": seed, "temperature": T, "top_p": TOP_P, "set": pset, "samples": 1, "restarts": 0}
    got = {k: c[k] for k in want}
    assert got == want, (job, "config differs from CELLS", got, want)
    assert c["n"] == n or (c["n"] is None and n == len(gold)), (job, "n", c["n"], n)
    assert m["job_id"] == job and m["commit"] == c["commit"] and cnt["n"] == c["n_problems"] == n, (job, m["job_id"], cnt["n"])
    edit_file, hand_file = RUNS / job / "edit.json", RUNS / job / "handedit.json"
    edit = hand = None
    if label in REFERENCES:
        assert c["model"] == label and c["model_label"] is None and not edit_file.exists(), (job, "model", c["model"], c["model_label"])
    elif label in HANDEDITS:
        assert c["model"] is None and c["model_label"] == label and not edit_file.exists(), (job, "model label", c["model"], c["model_label"])
        hand = json.loads(hand_file.read_text())          # a hand-edited model without handedit.json fails here
        ctl = HANDEDITS[label]
        got = (hand["job_id"], hand["control"], hand["args"]["control"], hand["written"], hand["tensor"], hand["layer"], hand["dir_written"])
        assert got == (job, ctl, ctl, "control" if ctl else "real", HAND_TENSOR, 31, True), (job, "handedit.json differs from HANDEDITS", got)
        assert hand["stops_real"] == [] and hand["args"]["dir"] == c["model_path"], (job, hand["stops_real"], hand["args"]["dir"])
    else:
        assert c["model"] is None and c["model_label"] == label, (job, "model label", c["model"], c["model_label"], label)
        edit = json.loads(edit_file.read_text())          # an edited model without edit.json fails here
        got = (edit["recipe"], edit["k"], edit["args"]["other"], edit["alpha"])
        assert got == EDITS[label], (job, "edit.json differs from EDITS", got, EDITS[label])
    rows = rows_by_index(RUNS / job / "answers.jsonl", keep)
    for i, r in rows.items():
        assert r["seed"] == seed + i and r["sample"] == 0 and r["attempt"] == 0, (job, i, r["seed"])
        assert r["model"] == label and r["prompt_arm"] == prompt and r["gold"] == gold[i], (job, i, r["model"], r["prompt_arm"])
        assert r["score_v3"] == R.grade_v3(gold[i], r["text"])["score_v3"], (job, i, "stored v3 score differs from the rescore")
    tot = (sum(r["score_v3"] for r in rows.values()), sum(r["cap_hit"] for r in rows.values()), sum(r["n_new"] for r in rows.values()))
    assert tot == (cnt["correct_v3"], cnt["cap_hits"], cnt["generated_tokens"]), (job, "rows differ from metrics.json counts", tot)
    return m, edit, hand, rows


def handedit(h):
    """The fields of one handedit.json that a WSP-2 cell reports: the written edit (real or control), per cue position its scale
    and the cue token's probability on the held-out prompts before and after, the KL and the size of the edit."""
    w = h["written"]
    e = h["edits"][w]
    pos = [{"cue_id": p["cue_id"], "scale": p["scale"], "held_before_mean": p["held_before"]["mean"],
            "held_before_min": p["held_before"]["min"], "held_after_mean": p["held_after"][w]["mean"],
            "held_after_min": p["held_after"][w]["min"], "cal_after_mean": p["cal_after"][w]["mean"]} for p in h["positions"]]
    return {"control": h["control"], "written": w, "layer": h["layer"], "tensor": h["tensor"], "batch": h["batch"],
            "rounding": h["rounding"], "target": h["target"], "lambda": h["lambda"], "solution": h["solution"],
            "calibration": h["calibration"], "held_out": h["held_out"], "positions": pos, "kl_nats": e["kl"],
            "kl_at_last_cue_nats": e["kl_at_last_cue"], "fro_dW_over_W": e["fro_dW_over_W"], "fro_dW": e["fro_dW"],
            "changed_share": e["changed_share"], "value_cos_real": e["value_cos_real"]}


def measure(rows, edit, hand=None):
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
    if hand is not None:
        res["mean_new_tokens"] = round(statistics.mean(r["n_new"] for r in rs), 1)
        res["handedit"] = handedit(hand)
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


def write_run(name, exp, job, files, root=OUT):
    d = root / exp / f"{name}-01"
    if d.exists():
        old = json.loads((d / "run.json").read_text())["job_id"]
        assert old == job, f"{d} holds job {old}, not {job}: a rerun gets the next number"
    d.mkdir(parents=True, exist_ok=True)
    for file, text in files.items():
        (d / file).write_text(text)
    return f"studies/rlneurons/results/{root.name}/{exp}/{d.name}"


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


def full500_refs():
    """T1 and T2 rows by problem index (ITEMS) and the counts of REF_COUNTS (WDIFF), each checked against the README's count."""
    items = json.loads(ITEMS.read_text())
    by = {r["problem_index"]: r for r in items}
    assert len(items) == len(by) == 500 and set(by) == set(range(500)), (ITEMS, "not the 500 distinct problem indices")
    sc, refs = {}, {}
    for name, (col, right) in REF_ROWS.items():
        assert sum(r[col] for r in items) == right, (name, sum(r[col] for r in items), "differs from the README's count", right)
        sc[name] = {i: {"score_v3": r[col]} for i, r in by.items()}
        refs[name] = {"n": 500, "right_v3": right, "rows": f"studies/rlneurons/results/rln4/{ITEMS.parent.name}/{ITEMS.name} ({col})"}
    wd = json.loads(WDIFF.read_text())["cells"]
    for name, right in REF_COUNTS.items():
        assert (wd[name]["n"], wd[name]["right_v3"]) == (500, right), (name, wd[name]["right_v3"], "differs from the README's count", right)
        refs[name] = {"n": 500, "right_v3": right, "rows": None, "count": f"studies/rlneurons/results/day1_wdiff/{WDIFF.name}"}
    return items, by, sc, refs


def compare(sc, vs, counts=REF_COUNTS, unpaired_ok=UNPAIRED):
    """Differences x minus y of vs among the scored cells sc (paired by problem); y with only a count: unpaired or skipped."""
    diffs, skipped = {}, []
    for x, y in vs:
        if x not in sc or (y not in sc and y not in counts):
            continue                                      # a cell that is not finished
        n = len(sc[x])
        if y in sc:                                       # diff asserts equal index sets
            diffs[f"{x} minus {y}"] = {**diff(sc, x, y), "paired": True}
        elif y in unpaired_ok:
            diffs[f"{x} minus {y}"] = {**unpaired(sum(r["score_v3"] for r in sc[x].values()), counts[y], n), "paired": False}
        else:
            skipped.append(f"{x} minus {y}: no per-problem rows of {y} in git, only its count {counts[y]} of {n}")
    return diffs, skipped


def references(rows):
    """The finished full500 cells against the study's reference cells: differences (VS), the sft1 cue cell on the problems
    that RL solves and the cued base does not, and the 2 x 2 table of top8 plain against RL."""
    items, by, sc, refs = full500_refs()
    sc |= {f"{lab}_{p}": rs for (e, lab, p), rs in rows.items() if e == "full500"}
    diffs, skipped = compare(sc, VS)
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


def hard328_refs(rows, hard):
    """The hard328 cells against the Day-1 #1 cells, paired by problem index (rows of AXIS), with their cap hits and tokens."""
    v, d1 = json.loads(AXIS.read_text()), json.loads(DAY1_328.read_text())["cells"]
    idx = v["problem_indices"]
    assert v["set"] == "hard328" and v["grader"] == "v3" and idx == sorted(hard), (AXIS, "not the 328 clean problems")
    assert all(hard[i]["unique_id"] == u for i, u in zip(idx, v["unique_ids"])), (AXIS, "unique ids differ from data/rln3/hard.json")
    sc = {f"{lab}_{p}": rs for (e, lab, p), rs in rows.items() if e == "hard328"}
    refs = {}
    for name, (arm, right) in REF328.items():
        c = d1[name]
        assert sum(v["arms"][arm]) == c["right_v3"] == right and c["n"] == 328, (name, sum(v["arms"][arm]), c["right_v3"], right)
        sc[name] = {i: {"score_v3": s} for i, s in zip(idx, v["arms"][arm])}
        refs[name] = {"n": 328, "right_v3": right, "cap_hits": c["cap_hits"], "mean_new_tokens": c["mean_generated_tokens"],
                      "seed_base": c["seed_base"], "job_id": c["job_id"],
                      "rows": f"studies/rlneurons/results/axis/{AXIS.parent.name}/{AXIS.name} (arms.{arm})",
                      "count": f"studies/rlneurons/results/day1_hard328/{DAY1_328.name} (cells.{name})"}
    cells = {f"{lab}_{p}": {"right_v3": sum(r["score_v3"] for r in rs.values()), "cap_hits": sum(r["cap_hit"] for r in rs.values()),
                            "mean_new_tokens": round(statistics.mean(r["n_new"] for r in rs.values()), 1)}
             for (e, lab, p), rs in rows.items() if e == "hard328"}
    diffs, _ = compare(sc, VS328, counts={})
    return {"set": "the 328 clean problems of data/rln3/hard.json (overlap flag none), by its index; T 1.0, top-p 1.0, one sample",
            "references": refs, "cells": cells, "differences": diffs,
            "tokens": "mean_new_tokens: mean of n_new (the references' mean_generated_tokens of analysis/day1_hard328.py is that mean)",
            "intervals": f"paired by problem index, bootstrap ({N_BOOT:,} resamples, seed 0, 95 % percentile), in points"}


def wsp2(rows1, rows2):
    """WSP-2 cells against the WSP-1 screen cells on the same 100 problems and, on all 500, against the references."""
    allrows = rows1 | rows2
    screen = {f"{'_'.join(x)} minus {'_'.join(y)}": diff(allrows, ("screen100", *x), ("screen100", *y))
              for x, y in SCREEN2 if ("screen100", *x) in allrows and ("screen100", *y) in allrows}
    _, _, sc, refs = full500_refs()
    sc |= {f"{lab}_{p}": rs for (e, lab, p), rs in allrows.items() if e == "full500"}
    diffs, skipped = compare(sc, VS2)
    return screen, {"references": refs, "differences": diffs, "skipped": skipped}


def score_cells(table, root, gold):
    """Load, check, measure and write the run folder of every finished job of one cell table."""
    rows, cells, skipped = {}, {}, []
    for label, prompt, job, exp, seed in table:
        name = f"{label}_{prompt}"
        if not (RUNS / job / "answers.jsonl").exists():
            skipped.append({"cell": f"{exp}/{name}", "job_id": job, "why": "no answers.jsonl in runs/"})
            continue
        status = json.loads((RUNS / job / "metrics.json").read_text())["status"]
        if status != "done":
            skipped.append({"cell": f"{exp}/{name}", "job_id": job, "why": f"metrics.json status {status}"})
            continue
        m, edit, hand, rs = load(label, prompt, job, exp, seed, gold)
        met = measure(rs, edit, hand)
        if (exp, label, prompt) in SPEC_COUNTS:
            assert met["right_v3"] == SPEC_COUNTS[exp, label, prompt], (exp, name, met["right_v3"], "differs from the spec's count")
        run = {"job_id": job, "commit": m["commit"], "command": command(m, edit, hand),
               "command_source": "rebuilt from metrics.json config and edit.json args; argument order of the submitted string not recorded",
               "gpu": m["memory"]["gpu"], "seed": seed, "seed_rule": m["config"]["seed_rule"], "n": met["n"], "experiment": exp,
               "label": label, "prompt": prompt, "temperature": T, "top_p": TOP_P, "started_utc": m["started_utc"],
               "raw_answers": f"runs/{job}/answers.jsonl (uv run tools/gpu.py get {job}; sameraslan's Modal workspace)"}
        if hand is not None:
            run["command_source"] = run["command_source"].replace("edit.json", "handedit.json")
        by_index = sorted(rs.values(), key=lambda r: r["problem_index"])
        ex = {"rule": f"lowest problem index scored right and scored wrong; text cut to its first and last {KEEP} characters",
              "right": example(next((r for r in by_index if r["score_v3"]), None)),
              "wrong": example(next((r for r in by_index if not r["score_v3"]), None))}
        if hand is not None:
            ex["openings_rule"] = f"the first {OPEN_CHARS} characters of the answers to the {N_OPEN} lowest problem indices"
            ex["openings"] = [{"problem_index": r["problem_index"], "score_v3": r["score_v3"], "text": r["text"][:OPEN_CHARS]}
                              for r in by_index[:N_OPEN]]
        per = [{k: r[k] for k in ("problem_index", "score_v3", "cap_hit", "n_generated")} for r in by_index]
        folder = write_run(name, exp, job, {"run.json": dump(run), "metrics.json": dump(met), "examples.json": dump(ex),
                                            "per_problem.json": "[\n" + ",\n".join(json.dumps(r) for r in per) + "\n]\n"}, root)
        rows[exp, label, prompt] = rs
        cells[f"{exp}/{name}"] = {"experiment": exp, "label": label, "prompt": prompt, "job_id": job, "seed_base": seed,
                                  "gpu": m["memory"]["gpu"], **met, "run_folder": folder}
    return rows, cells, skipped


def print_cells(cells):
    print(f"{'cell':<26}{'right/n':>9}{'Wilson 95 %':>14}{'cap':>5}{'mean tok':>10}{'med tok':>9}{'med right':>10}{'Okay80':>8}{'wait':>7}{'empty':>7}{'add_rel':>10}")
    for name, c in cells.items():
        rel = (c.get("edit") or {}).get("add_rel")
        print(f"{name:<26}{c['right_v3']:>5}/{c['n']:<3}{c['wilson95'][0]:>7.1f}-{c['wilson95'][1]:<6.1f}{c['cap_hits']:>5}{c['mean_generated_tokens']:>10.1f}"
              f"{c['median_generated_tokens']:>9.1f}{c['median_tokens_right']:>10.1f}{100 * c['okay_first80_share']:>7.0f}%{c['wait_per_answer']:>7.2f}"
              f"{100 * c['empty_share']:>6.0f}%{'-' if rel is None else format(rel, '.2e'):>10}")


def print_vs(diffs):
    for name, d in diffs.items():
        print(f"{name:<44}{d['points']:>+7.1f}  [{d['ci95'][0]:+.1f}, {d['ci95'][1]:+.1f}]  n {d['n']}  {'paired' if d['paired'] else 'unpaired (Newcombe, Wilson)'}")


def pairs(have, exp):
    """The differences of one experiment, among its finished cells (label, prompt)."""
    plain = [lab for (e, lab, p) in have if e == exp and p == "plain"]
    cue = [lab for (e, lab, p) in have if e == exp and p == "cue"]
    out = [("rl", "base", "plain")] + [(lab, ref, "plain") for lab in plain if lab not in REFERENCES for ref in REFERENCES]
    out += [(x, y, "plain") for x, y in CONTROLS] + [(lab, "base", "cue") for lab in cue if lab != "base"]
    return [(x, y, p) for x, y, p in out if (exp, x, p) in have and (exp, y, p) in have]


def main():
    for table in (CELLS, CELLS2):
        assert len({(e, lab, p) for lab, p, _, e, _ in table}) == len(table) == len({job for _, _, job, _, _ in table}), "a cell table has a duplicate"
    assert not {job for _, _, job, _, _ in CELLS} & {job for _, _, job, _, _ in CELLS2}, "a job in both cell tables"
    hard_all = json.loads((STUDY / "data" / "rln3" / "hard.json").read_text())
    flags = json.loads((STUDY / "results" / "rln3" / "rln3_overlap.json").read_text())["sets"]["hard"]["flags"]
    clean = sorted(int(i) for i, f in flags.items() if f["flag"] == "none")
    assert len(clean) == 328 and all(int(hard_all[i]["index"]) == i for i in clean), "the clean harder set is not 328 problems"
    hard = {i: hard_all[i] for i in clean}
    gold = {"math500": {int(p["index"]): p["answer"] for p in json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())},
            "hard328": {i: p["answer"] for i, p in hard.items()}}
    rows, cells, skipped = score_cells(CELLS, OUT, gold)

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
    if any(e == "hard328" for e, _, _ in rows):
        res["hard328_vs_references"] = hard328_refs(rows, hard)  # the hard328 cells are the 328 harder problems, not MATH-500
    (OUT / "readout.json").write_text(dump(res))

    rows2, cells2, skipped2 = score_cells(CELLS2, OUT2, gold)
    screen2, full2 = wsp2(rows, rows2)
    res2 = {"spec": "studies/rlneurons/specs/SPEC_wsp2.md", "grader": "rln4_lib.grade_v3 (stored score_v3, equal to a rescore)",
            "set": "the first n MATH-500 problems, plain prompt, T 1.0, top-p 1.0, one sample", "cells": cells2,
            "screen100_differences": screen2,
            "screen100_references": {f"{lab}_{p}": cells[f"screen100/{lab}_{p}"]["right_v3"] for lab, p in
                                     sorted({y for _, y in SCREEN2 if y[0] not in HANDEDITS})},
            "full500_vs_references": full2, "skipped": skipped2,
            "bootstrap": f"paired by problem index, {N_BOOT:,} resamples, seed 0, 95 % percentile, in points; screen100 references are "
                         "the WSP-1 cells of results/wsp1/screen100/ (base cue: seed base 81,000,000, paired by problem)",
            "notes": ["tokens are n_generated (counts the stop token); mean_new_tokens is the mean of n_new",
                      "empty: n_generated <= 3; okay_first80: 'Okay' in the first 80 characters of the text",
                      "handedit: from the job's handedit.json; held-out probabilities are means over the 64 held-out prompts "
                      "(MATH-500 problems 228 to 291) of the cue token's probability in its context; kl_nats is the mean "
                      "KL(base || edited) over 64 tokens of the base's cued continuation"]}
    OUT2.mkdir(parents=True, exist_ok=True)
    (OUT2 / "readout.json").write_text(dump(res2))

    print_cells(cells)
    print(f"\npaired differences, points [95 % bootstrap interval], {N_BOOT:,} resamples")
    for name, d in diffs.items():
        print(f"{name:<44}{d['points']:>+7.1f}  [{d['ci95'][0]:+.1f}, {d['ci95'][1]:+.1f}]  n {d['n']}")
    vs = res["full500_vs_references"]
    print("\nfull500 against the reference cells, right of 500: " + ", ".join(f"{k} {v['right_v3']}" for k, v in vs["references"].items()))
    print_vs(vs["differences"])
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
    if "hard328_vs_references" in res:
        h = res["hard328_vs_references"]
        print("\nhard328 (right of 328, cap hits, mean n_new): " + ", ".join(
            f"{k} {v['right_v3']} / {v['cap_hits']} / {v['mean_new_tokens']}" for k, v in (h["cells"] | h["references"]).items()))
        print_vs(h["differences"])
    for s in skipped:
        print(f"skipped {s['cell']} ({s['job_id']}): {s['why']}")

    print("\nWSP-2")
    print_cells(cells2)
    for name, c in cells2.items():
        e = c["handedit"]
        print(f"{name}: held-out cue probability before " + " ".join(f"{p['held_before_mean']:.3f}" for p in e["positions"])
              + ", after " + " ".join(f"{p['held_after_mean']:.3f}" for p in e["positions"])
              + f"; KL {e['kl_nats']:.2e} nats; |dW|/|W| {e['fro_dW_over_W']:.4f}")
    print("screen100 references, right of 100: " + ", ".join(f"{k} {v}" for k, v in res2["screen100_references"].items()))
    print_vs({k: {**d, "paired": True} for k, d in screen2.items()})
    print("full500 against the reference cells, right of 500: " + ", ".join(f"{k} {v['right_v3']}" for k, v in full2["references"].items()))
    print_vs(full2["differences"])
    for s in full2["skipped"]:
        print(f"skipped {s}")
    for s in skipped2:
        print(f"skipped {s['cell']} ({s['job_id']}): {s['why']}")


if __name__ == "__main__":
    main()
