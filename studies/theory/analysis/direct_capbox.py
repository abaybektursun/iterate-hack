"""Direct test of run-08/f2-m02 (specs/SPEC_direct_capbox.md): in native 16,384-cap hard328 runs, what share of the
cap-hit rows does grader v3 credit with a right answer (a box or 'Answer:' line written before the cut)?

    PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 --with tokenizers==0.23.3 \
        python studies/theory/analysis/direct_capbox.py <runs dir holding the answers.jsonl of the jobs below>

Writes readout.json, examples.json, rows10.json (the 10 rows read by hand for reading.md) and run.json in
studies/theory/results/direct/capbox-01/.
"""
import json
import math
import pathlib
import subprocess
import sys

import numpy as np
from tokenizers import Tokenizer

from studies.rlneurons.lib import rln4_lib as L

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "studies/rlneurons/results"
OUT = ROOT / "studies/theory/results/direct/capbox-01"
RUNS = pathlib.Path(sys.argv[1])
CAP = 16384
B = 10_000
TOKENIZER = pathlib.Path.home() / (".cache/huggingface/hub/models--allenai--Olmo-3.1-7B-RL-Zero-Math/snapshots/"
                                   "364820b002fc8e81d11a81c7fc9dd6b49c83cd05/tokenizer.json")
MODELS = {  # folder, jobs holding the texts, attempt-0 cap hits per sample (readout), all-row cap hits (metrics)
    "rl_plain": ("day1_3/hard328_rl_plain_s4r2-01", ["abaybektursun-1114-200505-5ff2"], [35, 26, 24, 29], 171),
    "base_cue": ("day1_3/hard328_base_cue_s4r2-01", ["abaybektursun-1114-200457-e8e6"], [71, 66, 81, 68], 498),
    "sft_cue": ("thinkvote/hard328_sft1_cue_s4-01",
                ["abaybektursun-1115-000503-1e5f", "abaybektursun-1115-000525-ea4e",
                 "abaybektursun-1115-014823-ef56", "abaybektursun-1115-014833-1daa"], [89, 95, 92, 102], 378),
}
DAY1 = {"rl_plain": ("abaybektursun-1114-151540-86ef", 20), "base_cue": ("abaybektursun-1114-151534-e72c", 77)}
CAP32 = {"rl_plain": ("cap32/rows-01/rl_plain.jsonl", "abaybektursun-1115-005823-8ac9"),
         "sft_cue": ("cap32/rows-01/sft_cue.jsonl", "abaybektursun-1115-005756-309b"),
         "base_cue": ("cap32/rows-02/base_cue.jsonl", None)}  # base_cue 32k texts are not in this runs dir


def jl(p):
    return [json.loads(line) for line in open(p)]


def wilson(c, n, z=1.959964):
    p = c / n
    d = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [mid - half, mid + half]


PROBLEMS = json.loads((RES / "day1_3/hard328_rl_plain_s4r2-01/readout.json").read_text())["problem_indices"]
POS = {p: i for i, p in enumerate(PROBLEMS)}
assert len(POS) == 328


def per_problem(rows):
    """(C_i, H_i) per hard328 problem (position 0..327 of its problem index) over the given cap-hit rows."""
    c, h = np.zeros(328), np.zeros(328)
    for r in rows:
        h[POS[r["problem_index"]]] += 1
        c[POS[r["problem_index"]]] += r["score_v3"]
    return c, h


def boot(models_rows):
    """Cluster bootstrap over the 328 problems, one index draw shared by all models. Returns {model: draws of C/H}."""
    rng = np.random.default_rng(0)
    ch = {m: per_problem(rows) for m, rows in models_rows.items()}
    draws = {m: np.empty(B) for m in ch}
    for b in range(B):
        idx = rng.integers(0, 328, 328)
        for m, (c, h) in ch.items():
            draws[m][b] = c[idx].sum() / h[idx].sum()
    return draws


def ci(x, level):
    a = (100 - level) / 2
    return [float(v) for v in np.percentile(x, [a, 100 - a])]


def share_block(rows, draws):
    c, h = sum(r["score_v3"] for r in rows), len(rows)
    return {"C": c, "H": h, "share": c / h, "wilson95": wilson(c, h), "boot90": ci(draws, 90), "boot95": ci(draws, 95)}


def regrade_check(rows, texts):
    """Every stored score_v3 / extracted_v3 is reproduced by grade_v3 on the stored text."""
    for r in rows:
        t = texts[(r["problem_index"], r["seed"])]
        g = L.grade_v3(r["gold"], t["text"])
        assert (g["score_v3"], g["extracted_v3"]) == (r["score_v3"], r["extracted_v3"]), (r, g)


def main():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    tok = Tokenizer.from_file(str(TOKENIZER))
    out = {"mechanism": "run-08/f2-m02", "spec": "studies/theory/specs/SPEC_direct_capbox.md", "set": "hard328",
           "cap": CAP, "grader": "studies/rlneurons/lib/rln4_lib.py grade_v3",
           "bootstrap": "cluster over the 328 problems, 10000 resamples, numpy default_rng(0), one draw shared by models"}
    rows_all, texts_all = {}, {}
    for m, (folder, jobs, cap0, capall) in MODELS.items():
        rows = jl(RES / folder / "rows.jsonl")
        assert all(r["cap_hit"] == (r["finish_reason"] == "length") for r in rows)
        got0 = [sum(r["cap_hit"] for r in rows if r["attempt"] == 0 and r["sample"] == s) for s in range(4)]
        assert got0 == cap0 and sum(r["cap_hit"] for r in rows) == capall, (m, got0, cap0)
        texts = {}
        for j in jobs:
            for t in jl(RUNS / j / "answers.jsonl"):
                texts[(t["problem_index"], t["seed"])] = t
        assert len(texts) == len(rows), (m, len(texts), len(rows))
        rows_all[m], texts_all[m] = rows, texts

    capped0 = {m: [r for r in rows if r["cap_hit"] and r["attempt"] == 0] for m, rows in rows_all.items()}
    cappedA = {m: [r for r in rows if r["cap_hit"]] for m, rows in rows_all.items()}
    for m in rows_all:
        regrade_check(cappedA[m], texts_all[m])

    # primary: attempt 0
    d0 = boot(capped0)
    prim = {m: share_block(capped0[m], d0[m]) for m in capped0}
    diff = {}
    for a, b in [("rl_plain", "sft_cue"), ("rl_plain", "base_cue"), ("sft_cue", "base_cue")]:
        x = d0[a] - d0[b]
        diff[f"{a}-{b}"] = {"value": prim[a]["share"] - prim[b]["share"], "ci90": ci(x, 90), "ci95": ci(x, 95)}
    out["primary_attempt0"] = {"per_model": prim, "differences": diff}

    # secondary: all attempts including restarts
    dA = boot(cappedA)
    secA = {m: share_block(cappedA[m], dA[m]) for m in cappedA}
    x = dA["rl_plain"] - dA["sft_cue"]
    out["secondary_all_attempts"] = {"per_model": secA, "rl_plain-sft_cue": {
        "value": secA["rl_plain"]["share"] - secA["sft_cue"]["share"], "ci90": ci(x, 90), "ci95": ci(x, 95)}}

    # per sample, and base sample 0 vs samples 1-3
    out["per_sample_attempt0"] = {m: [[sum(r["score_v3"] for r in capped0[m] if r["sample"] == s),
                                        sum(1 for r in capped0[m] if r["sample"] == s)] for s in range(4)]
                                  for m in capped0}
    b0 = [r for r in capped0["base_cue"] if r["sample"] == 0]
    b13 = [r for r in capped0["base_cue"] if r["sample"] > 0]
    out["base_sample0_vs_1to3"] = {"sample0": [sum(r["score_v3"] for r in b0), len(b0)],
                                   "samples1to3": [sum(r["score_v3"] for r in b13), len(b13)]}

    # text checks on cap-hit rows (attempt 0)
    text_checks = {}
    for m in capped0:
        tx = [texts_all[m][(r["problem_index"], r["seed"])] for r in capped0[m]]
        credited = []
        for r, t in zip(capped0[m], tx):
            if r["score_v3"]:
                mode, ext, start = L.extract_v3(t["text"])
                credited.append({"problem_index": r["problem_index"], "sample": r["sample"], "mode": mode,
                                 "extracted": ext, "gold": r["gold"], "start_share": round(start / len(t["text"]), 4),
                                 "n_boxes": len(L._boxes(t["text"]))})
        text_checks[m] = {
            "H": len(tx),
            "share_any_box": sum("\\boxed{" in t["text"] for t in tx) / len(tx),
            "share_any_extracted": sum(L.extract_v3(t["text"])[1] is not None for t in tx) / len(tx),
            "share_extracted_boxed": sum(L.extract_v3(t["text"])[0] == "boxed" for t in tx) / len(tx),
            "credited_rows": credited,
            "n_tokens_check": sorted({t["n_new"] for t in tx}),
        }
    out["text_checks_attempt0"] = text_checks

    # planted controls of the grader on cut text
    planted = {}
    for m in rows_all:
        fin_right = [r for r in rows_all[m] if not r["cap_hit"] and r["score_v3"] == 1]
        cut_right = 0
        for r in fin_right:
            t = texts_all[m][(r["problem_index"], r["seed"])]["text"]
            _, _, start = L.extract_v3(t)
            cut_right += L.grade_v3(r["gold"], t[:start])["score_v3"]
        unc = [r for r in capped0[m] if r["score_v3"] == 0]
        add_right = sum(L.grade_v3(r["gold"], texts_all[m][(r["problem_index"], r["seed"])]["text"]
                                   + "\n\\boxed{" + r["gold"] + "}")["score_v3"] for r in unc)
        # added after the first run: the cut-before-answer control keeps earlier copies of the answer, so it cannot
        # fail on its own; a wrong box appended after the right answer must turn every right row wrong
        right = fin_right + [r for r in capped0[m] if r["score_v3"] == 1]
        assert all(r["gold"] != "-12345" for r in right)
        wrong_last = sum(L.grade_v3(r["gold"], texts_all[m][(r["problem_index"], r["seed"])]["text"]
                                    + "\n\\boxed{-12345}")["score_v3"] for r in right)
        planted[m] = {"finished_right_cut_before_answer": [cut_right, len(fin_right)],
                      "uncredited_caphit_plus_gold_box": [add_right, len(unc)],
                      "right_rows_plus_wrong_box_after": [wrong_last, len(right)]}
    out["planted_controls"] = planted

    # 32k rows: rescore at 16,384 against cutting the 32k text at 16,384 generated tokens
    c32 = {}
    for m, (path, job) in CAP32.items():
        rows = jl(RES / path)
        late = [r for r in rows if r["n_new"] > CAP]
        rec = {"n_rows": len(rows), "longer_than_16384": len(late),
               "right_at_32768_of_them": sum(r["score_v3"] for r in late),
               "rescore_at_16384_credits": 0}
        if job:
            texts = {t["problem_index"]: t for t in jl(RUNS / job / "answers.jsonl")}
            match, cut_c, cut_rows, gap = 0, 0, [], []
            for r in late:
                t = texts[r["problem_index"]]
                assert t["n_new"] == r["n_new"] and t["score_v3"] == r["score_v3"]
                ids = tok.encode(t["text"], add_special_tokens=False).ids
                match += len(ids) == t["n_new"] + t["n_prefix"]
                gap.append(len(ids) - t["n_new"] - t["n_prefix"])
                cut = tok.decode(ids[:CAP + t["n_prefix"]])
                g = L.grade_v3(r["gold"], cut)
                cut_c += g["score_v3"]
                cut_rows.append({"problem_index": r["problem_index"], "right_at_32768": r["score_v3"],
                                 "cut_mode": g["mode_v3"], "cut_extracted": g["extracted_v3"],
                                 "cut_score": g["score_v3"], "gold": r["gold"]})
            rec.update({"retokenized_length_matches_n_new": [match, len(late)],
                        "retokenized_minus_generated_tokens": {"min": min(gap), "median": float(np.median(gap)),
                                                               "max": max(gap)},
                        "cut_at_16384_tokens_credited": [cut_c, len(late)],
                        "cut_share": cut_c / len(late), "cut_share_wilson95": wilson(cut_c, len(late)),
                        "cut_any_extracted": sum(x["cut_extracted"] is not None for x in cut_rows),
                        "cut_rows": cut_rows})
        c32[m] = rec
    out["cap32_consistency"] = c32

    # day1 single-sample check
    d1 = {}
    for m, (job, cap) in DAY1.items():
        ans = jl(RUNS / job / "answers.jsonl")
        capped = [a for a in ans if a["cap_hit"]]
        assert len(ans) == 328 and len(capped) == cap, (m, len(capped))
        c = sum(a["score_v3"] for a in capped)
        d1[m] = {"job": job, "C": c, "H": cap, "share": c / cap, "wilson95": wilson(c, cap),
                 "share_any_box": sum("\\boxed{" in a["text"] for a in capped) / cap}
    out["day1_single_sample"] = d1

    # verdict by the frozen rule (primary rows)
    rl, dd = prim["rl_plain"], diff["rl_plain-sft_cue"]
    if rl["wilson95"][1] < 0.10 or dd["ci95"][1] <= 0:
        verdict = "refuted"
    elif rl["share"] >= 0.10 and dd["ci95"][0] > 0:
        verdict = "holds"
    else:
        verdict = "undecided"
    rlA, ddA = secA["rl_plain"], out["secondary_all_attempts"]["rl_plain-sft_cue"]
    verdict_all = ("refuted" if rlA["wilson95"][1] < 0.10 or ddA["ci95"][1] <= 0 else
                   "holds" if rlA["share"] >= 0.10 and ddA["ci95"][0] > 0 else "undecided")
    out["verdict"] = verdict
    out["verdict_if_all_attempts"] = verdict_all
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "readout.json").write_text(json.dumps(out, indent=1) + "\n")

    # examples: one credited RL cap-hit row, one RL cap-hit row whose last box is wrong
    def ex(r, texts):
        t = texts[(r["problem_index"], r["seed"])]
        g = L.grade_v3(r["gold"], t["text"])
        start = L.extract_v3(t["text"])[2]
        return {"around_answer": t["text"][max(0, start - 400):start + 300], "model": "rl_plain", "job": MODELS["rl_plain"][1][0], "problem_index": r["problem_index"],
                "sample": r["sample"], "n_new": t["n_new"], "cap_hit": t["cap_hit"], "prompt": t["prompt"],
                "text_tail": t["text"][-1500:], "mode_v3": g["mode_v3"], "extracted_v3": g["extracted_v3"],
                "gold": r["gold"], "score_v3": g["score_v3"]}
    rlt = texts_all["rl_plain"]
    pos = next(r for r in capped0["rl_plain"] if r["score_v3"] == 1)
    neg = next(r for r in capped0["rl_plain"]
               if r["score_v3"] == 0 and L.extract_v3(rlt[(r["problem_index"], r["seed"])]["text"])[0] == "boxed")
    (OUT / "examples.json").write_text(json.dumps({"supports_claim_credited_caphit": ex(pos, rlt),
                                                   "against_claim_caphit_box_wrong": ex(neg, rlt)}, indent=1) + "\n")

    # 10 rows to read by hand: all RL credited (7) and 3 RL uncredited cap-hit rows with a box
    pick = [r for r in capped0["rl_plain"] if r["score_v3"] == 1]
    pick += [r for r in capped0["rl_plain"] if r["score_v3"] == 0
             and "\\boxed{" in rlt[(r["problem_index"], r["seed"])]["text"]][:10 - len(pick)]
    ten = []
    for r in pick:
        t = rlt[(r["problem_index"], r["seed"])]["text"]
        mode, ext, start = L.extract_v3(t)
        ten.append({"problem_index": r["problem_index"], "sample": r["sample"], "score_v3": r["score_v3"],
                    "gold": r["gold"], "mode": mode, "extracted": ext, "start_share": round(start / len(t), 4),
                    "around_answer": t[max(0, start - 300):start + 200], "tail": t[-300:]})
    (OUT / "rows10.json").write_text(json.dumps(ten, indent=1) + "\n")

    (OUT / "run.json").write_text(json.dumps({
        "commit": commit, "command": "PYTHONPATH=. uv run --no-project --with numpy --with math-verify==0.9.0 "
        "--with tokenizers==0.23.3 python studies/theory/analysis/direct_capbox.py runs",
        "job": None, "input_jobs": [j for v in MODELS.values() for j in v[1]] + [v[0] for v in DAY1.values()]
        + [v[1] for v in CAP32.values() if v[1]], "tokenizer": "allenai/Olmo-3.1-7B-RL-Zero-Math@364820b (CPU, no weights)"},
        indent=1) + "\n")
    print(json.dumps({"primary": {m: [v["C"], v["H"], round(v["share"], 4), [round(x, 4) for x in v["wilson95"]]]
                                  for m, v in prim.items()}, "diff": diff, "verdict": verdict,
                      "verdict_all": verdict_all}, indent=1))


if __name__ == "__main__":
    main()
