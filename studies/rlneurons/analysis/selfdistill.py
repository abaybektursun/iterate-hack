"""Self-distillation readout (specs/SELFDISTILL_2026-11-15.md): the LoRA models trained on the base's own vote-selected (V) and
random (U) cue samples, scored with run_cell on the 328 harder problems (plain and cue), beside base cue, theta(0.5) cue and RL
plain; the in-distribution sanity cell on MATH-500 first 100; the training reports. Grader v3.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.selfdistill [--hand <arm>]

Inputs (not committed): runs/<job-id>/ of every job below (`uv run tools/gpu.py get <job-id>`), the reference jobs of
analysis/day1_hard328.py and day1_wdiff328.py, runs/s3/r4/... for T1 and T3. Writes results/selfdistill/readout.json and run
folders results/selfdistill/<arm>-01/. --hand <arm> prints 20 finished answers scored wrong (numpy seed 0); findings are HAND.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib

import numpy as np

from studies.rlneurons.analysis.day1_hard328 import JOBS as H328, rows_by_index, score, summary
from studies.rlneurons.analysis.day1_wdiff import diff, write_run
from studies.rlneurons.analysis.day1_wdiff328 import NEW as W328, clean_set

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "selfdistill"
CUE = " line!\n\nOkay"
SOURCE = "abaybektursun-1114-153825-208b"                 # Day-1 #3 base cue rows, the training texts
SETUP, PY = "bash studies/rlneurons/jobs/setup_vllm.sh && ", "/opt/rln-vllm/bin/python -m studies.rlneurons.jobs."
TRAIN = {"V": "abaybektursun-1114-194352-feef", "U": "abaybektursun-1114-194358-195f",
         "S": "abaybektursun-1114-194405-bbb6"}  # arm -> training job: SETUP + PY + "distill_train train --arm <arm>"


def cell_cmd(arm, prompt, cset, seed, n=None):
    return (f"{SETUP}rm -rf /tmp/sd && {PY}distill_train merge --train-dir /runs/{TRAIN[arm]} --dir /tmp/sd && {PY}run_cell --model-path "
            f"/tmp/sd --model-label sd{arm} --prompt {prompt} --set {cset} --temperature 1.0 --top-p 1.0 --seed {seed}" + (f" --n {n}" if n else ""))


# cell -> (job id, commit, train arm, prompt, seed base)
SANITY = ("abaybektursun-1114-200050-c260", "ec6e0f5d6d6ba1581079faa129c5161f18b00a01", "V", "plain", 80000000)
CELLS = {
    "V_plain": ("abaybektursun-1114-201013-47c5", "ec6e0f5d6d6ba1581079faa129c5161f18b00a01", "V", "plain", 81000000),
    "V_cue": ("abaybektursun-1114-201021-095e", "ec6e0f5d6d6ba1581079faa129c5161f18b00a01", "V", "cue", 82000000),
    "U_plain": ("abaybektursun-1114-201028-1adf", "ec6e0f5d6d6ba1581079faa129c5161f18b00a01", "U", "plain", 83000000),
    "U_cue": ("abaybektursun-1114-201035-c6c0", "ec6e0f5d6d6ba1581079faa129c5161f18b00a01", "U", "cue", 84000000),
    "S_cue": ("abaybektursun-1114-201132-3c04", "ec6e0f5d6d6ba1581079faa129c5161f18b00a01", "S", "cue", 85000000),   # length control
}
BASE, RL, TH = "base_cue_T1", "rl_plain_T1", "theta0.5_cue"
HAND = {k: [] for k in CELLS}


def load(job, idx):
    m = json.loads((RUNS / job / "metrics.json").read_text())
    assert m["status"] == "done" and m["counts"]["n"] == len(idx) and m["job_id"] == job, (job, m["status"], m.get("counts"))
    return m, rows_by_index(RUNS / job / "answers.jsonl", idx)


def check_cell(m, rows, train_arm, prompt, cset, seed, job):
    c = m["config"]
    assert c["model_label"] == f"sd{train_arm}" and c["prompt"] == prompt and c["set"] == cset and c["seed"] == seed, (job, c)
    assert c["temperature"] == c["top_p"] == 1.0 and c["max_tokens"] == 16384, (job, c)
    assert all(r["seed"] == seed + i for i, r in rows.items()), job
    mg = json.loads((RUNS / job / "distill_merge.json").read_text())
    tr = json.loads((RUNS / TRAIN[train_arm] / "train.json").read_text())
    assert mg["train_job"] == TRAIN[train_arm] and mg["sha256"] == tr["merge"]["sha256"], (job, mg)
    return mg["sha256"]


def train_report(arm):
    tr = json.loads((RUNS / TRAIN[arm] / "train.json").read_text())
    src = {(r["problem_index"], r["sample"]): r for r in map(json.loads, open(RUNS / SOURCE / "answers.jsonl")) if r["attempt"] == 0}
    ex = json.loads((STUDY / "data" / "selfdistill" / "arms-v1.json").read_text())["arms"][arm]
    right = sum(src[(e["problem_index"], e["sample"])]["score_v3"] for e in ex)
    g = {k: {f: round(v[f], 6) for f in ("rel_norm_lora", "rel_norm_merged", "rel_norm_rl", "cos_lora_rl", "cos_merged_rl", "effective_scale")}
         for k, v in [*tr["merge"]["groups"].items(), ("all", tr["merge"]["all_targets"])]}
    return {"job_id": TRAIN[arm], "commit": tr["commit"], "n_examples": tr["n_examples"], "target_tokens": tr["target_tokens"],
            "prompt_tokens": tr["prompt_tokens"], "steps": len(tr["steps"]), "loss_first_step": tr["loss_first_step"],
            "loss_last_step": tr["loss_last_step"], "loss_epoch_mean": tr["loss_epoch_mean"], "train_s": tr["train_s"],
            "tokens_per_s": tr["tokens_per_s"], "targets_right_v3": right, "targets_right_share": right / len(ex), "groups": g,
            "merged_sha256": tr["merge"]["sha256"], "zero_adapter_sha256": tr["zero_adapter"]["sha256"],
            "generations_before": tr["generations_before"], "generations_after": tr["generations_after"]}


def sanity():
    g = {int(p["index"]): p["answer"] for p in json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())}
    job, commit, arm, prompt, seed = SANITY
    m, rows = load(job, range(100))
    check_cell(m, rows, arm, prompt, "math500", seed, job)
    sc = score(rows, g)
    ref = {k: summary(score(rows_by_index(RUNS / "s3" / f, range(100)), g)) for k, f in
           (("T3_base_plain", "r4/modal_t3-01/t3/T3.jsonl"), ("T1_base_cue", "r4/base_rl-02/out/T1.jsonl"))}
    return {"job_id": job, "V_plain": {**summary(sc), "starts_with_cue": sum(r["text"].startswith(CUE) for r in rows.values())}, **ref,
            "note": "in-distribution: these 100 problems were in the training set; a check that training worked, not a result"}, \
        (job, commit, cell_cmd(arm, prompt, "math500", seed, 100), rows, sc)


def hand(arm):
    clean, gold, _ = clean_set()
    _, rows = load(CELLS[arm][0], clean)
    sc = score(rows, gold)
    wrong = sorted(i for i in sc if sc[i]["v3"] == 0 and not sc[i]["cap"])
    pick = sorted(np.random.default_rng(0).choice(wrong, size=min(20, len(wrong)), replace=False).tolist())
    for i in pick:
        print(f"=== {arm} problem {i} gold {gold[i]!r} extracted_v3 {sc[i]['extracted_v3']!r} tokens {rows[i]['n_new']}")
        print(rows[i]["text"][-700:])
    print(f"{arm}: {len(wrong)} finished wrong; drawn {pick}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hand")
    a = ap.parse_args()
    if a.hand:
        return hand(a.hand)
    clean, gold, source = clean_set()
    rows, sc, cells = {}, {}, {}
    for arm, job in ((BASE, H328[BASE][0]), (RL, H328[RL][0]), (TH, W328[TH][0])):
        m, rows[arm] = load(job, clean)
        sc[arm] = score(rows[arm], gold)
        cells[arm] = {**summary(sc[arm]), "seed_base": m["config"]["seed"], "job_id": job,
                      "starts_with_cue": sum(r["text"].startswith(CUE) for r in rows[arm].values())}
    OUT.mkdir(parents=True, exist_ok=True)
    for arm, (job, commit, tarm, prompt, seed) in CELLS.items():
        m, rows[arm] = load(job, clean)
        h = check_cell(m, rows[arm], tarm, prompt, "hard328", seed, job)
        sc[arm] = score(rows[arm], gold)
        cells[arm] = {**summary(sc[arm]), "seed_base": seed, "job_id": job, "train_job": TRAIN[tarm], "merged_sha256": h,
                      "starts_with_cue": sum(r["text"].startswith(CUE) for r in rows[arm].values()),
                      "empty_answers": sum(r["text"].strip() == "" for r in rows[arm].values()),
                      "tokens_per_s": m["counts"]["tokens_per_s"],
                      "s3_answers": f"s3://pg-lineage-769063704696/results/rlneurons/r5/selfdistill-01/{job}/answers.jsonl",
                      "run_folder": write_run(arm, job, commit, cell_cmd(tarm, prompt, "hard328", seed), 2.0, rows[arm], sc[arm], out=OUT),
                      "hand_read_right_of_20": HAND[arm]}
        cells[arm]["right_corrected"] = cells[arm]["right_v3"] + len(HAND[arm])
    seeds = [c["seed_base"] for c in cells.values()]
    assert len(seeds) == len(set(seeds)), "two compared cells share a seed base"

    identical = {f"{x} | {y}": sum(rows[x][i]["text"] == rows[y][i]["text"] != "" for i in clean) for x, y in itertools.combinations(sorted(rows), 2)}
    assert not any(identical.values()), {k: v for k, v in identical.items() if v}
    pairs = [("V_cue", BASE), ("V_plain", BASE), ("V_plain", "U_plain"), ("V_cue", "U_cue"), ("V_cue", RL), ("V_cue", TH),
             ("U_cue", BASE), ("U_plain", BASE), ("V_cue", "V_plain"), ("S_cue", BASE), ("V_cue", "S_cue"), ("S_cue", "U_cue"), (RL, BASE)]
    diffs = {f"{x} minus {y}": diff(sc, x, y, clean) for x, y in pairs}
    sources = sorted(set(source.values()))
    per_source = {arm: {s: sum(sc[arm][i]["v3"] for i in clean if source[i] == s) for s in sources} for arm in sc}
    per_source["n"] = {s: sum(source[i] == s for i in clean) for s in sources}
    churn = {arm: {"fixed_of_base_cue_wrong": sum(sc[BASE][i]["v3"] == 0 and sc[arm][i]["v3"] == 1 for i in clean),
                   "lost_of_base_cue_right": sum(sc[BASE][i]["v3"] == 1 and sc[arm][i]["v3"] == 0 for i in clean)}
             for arm in [*CELLS, TH, RL]}

    def excl0(d):
        return d["ci95"][0] > 0 or d["ci95"][1] < 0
    d1, d2, d4 = diffs[f"V_plain minus {BASE}"], diffs[f"V_cue minus {BASE}"], diffs[f"V_cue minus {RL}"]
    d3 = {p: diffs[f"V_{p} minus U_{p}"] for p in ("plain", "cue")}
    pred = {
        "D1": {"text": "V plain reaches base cue; refuted if the interval of V plain - base cue is entirely under 0", "diff": d1,
               "status": "refuted" if d1["ci95"][1] < 0 else "held"},
        "D2": {"text": "V cue - base cue > 0 with an interval excluding 0", "diff": d2,
               "status": "held" if d2["ci95"][0] > 0 else "refuted"},
        "D3": {"text": "V beats U at the same prompt arm; refuted if the paired interval includes 0", "diff": d3,
               "status": {p: "held" if d3[p]["ci95"][0] > 0 else "refuted" for p in d3}},
        "D4": {"text": "V cue does not reach RL plain; the headline if the interval of V cue - RL plain includes 0", "diff": d4,
               "status": "held" if d4["ci95"][1] < 0 else "refuted (headline)"},
        "D5": {"text": "V has fewer cap hits than base cue's 77 (both prompt arms)",
               "cap_hits": {k: cells[k]["cap_hits"] for k in ("V_plain", "V_cue", BASE)},
               "status": "held" if max(cells["V_plain"]["cap_hits"], cells["V_cue"]["cap_hits"]) < cells[BASE]["cap_hits"] else "refuted"},
    }
    san, (sjob, scommit, scmd, srows, ssc) = sanity()
    san["run_folder"] = write_run("sanity_V_plain_math500_n100", sjob, scommit, scmd, 1.0, srows, ssc, out=OUT)
    training = {arm: train_report(arm) for arm in TRAIN}
    for arm in TRAIN:
        d = OUT / f"train_{arm}-01"
        if not d.exists():
            d.mkdir(parents=True)
            (d / "train.json").write_text((RUNS / TRAIN[arm] / "train.json").read_text())
            (d / "run.json").write_text(json.dumps({"job_id": TRAIN[arm], "commit": training[arm]["commit"],
                                                    "command": f"{SETUP}{PY}distill_train train --arm {arm} --commit {training[arm]['commit']}",
                                                    "runner": "uv run tools/gpu.py submit h100 --hours 1.5",
                                                    "adapter": f"/runs/{TRAIN[arm]}/adapter.safetensors (Modal Volume iterate-runs)"}, indent=1) + "\n")
    res = {"spec": "studies/rlneurons/specs/SELFDISTILL_2026-11-15.md", "grader": "rln4_lib.grade_v3", "n": 328, "training": training,
           "sanity_math500_first100": san, "cells": cells, "per_source_right_v3": per_source, "differences": diffs,
           "bootstrap": "paired, 5,000 resamples, seed 0, 95 % percentile", "fixed_lost_vs_base_cue": churn,
           "identical_nonempty_texts": identical, "predictions": pred}
    (OUT / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("sanity_math500_first100", "cells", "differences", "fixed_lost_vs_base_cue", "predictions")}, indent=1))
    print(json.dumps({a: {k: v for k, v in t.items() if k not in ("generations_before", "generations_after")} for a, t in training.items()}, indent=1))


if __name__ == "__main__":
    main()
