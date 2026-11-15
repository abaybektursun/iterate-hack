"""Freeze the inputs of facts.json `review` that are only in runs/ (reviewer questions).

    uv run --no-project python studies/rlneurons/paper-depth-rank/prep_review.py

Writes data/review/ (fails if it exists):
  rl_cue.jsonl, bulk.jsonl, rbulk.jsonl   hard328 rows (one sample) of RL-Zero-Math with the cue (seed 50,000,000 + i), `bulk`
                                          (RL-Math minus its top-8 directions per matrix) and `rbulk` (RL-Math minus a random rank-8
                                          of the same singular values); asserted against edits/readout.json
  energy.json                             per layer matrix, the share of ||RL - base||^2 in its top 1 and top 8 singular directions
                                          (edit.json `tensors` of the top1 and top8 x1 jobs: top_sq / d_sq)
  cut_right.json                          every hard328 answer that hit the cap and is scored right in the raw texts of the main
                                          cells: where the graded answer sits in the text and what follows it
"""
import glob
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
OUT = HERE / "data" / "review"
P = "abaybektursun-"
ROWS = {"rl_cue": ("1114-132929-a32d", "rl_cue_T1"), "bulk": ("1114-221100-1e31", "bulk_math31"), "rbulk": ("1115-012935-2836", "rbulk_math31")}
ENERGY = {"top1": "1115-000358-d11a", "top8": "1114-221034-007d"}
TEXTS = {"base_cue": ["1114-200457-e8e6"], "all8": ["1115-055641-b417"], "top1x1.5": ["1115-145913-fed1", "1115-145926-720e", "1115-145845-f70e", "1115-145859-a234"],
         "d2-8": ["1115-145941-c2cc", "1115-145956-7546", "1115-122847-824c", "1115-122859-b197"],
         "L0-10": ["1115-105312-7e19", "1115-122708-c6c1", "1115-122720-ad28", "1115-122733-bc4c", "1115-122746-2593", "1115-122759-39f3", "1115-122810-7b2d"],
         "L22-31": ["1115-105335-a886", "1115-122936-1b30", "1115-122949-e563"], "L22-31x3.0": ["1115-145720-8ceb", "1115-145733-af00"]}


def run_dir(job):
    hits = sorted(glob.glob(str(ROOT.parent / "iterate-hack*" / "runs" / (P + job))))
    assert hits, job
    return pathlib.Path(hits[0])


def answers(job):
    return [json.loads(l) for l in (run_dir(job) / "answers.jsonl").read_text().splitlines()]


def main():
    assert not OUT.exists(), "frozen"
    OUT.mkdir(parents=True)
    ed = json.loads((STUDY / "results/xreward/edits/readout.json").read_text())["cells"]
    for name, (job, key) in ROWS.items():
        rs = sorted((r for r in answers(job) if r.get("attempt", 0) == 0), key=lambda r: r["problem_index"])
        assert len(rs) == 328 and ed[key]["job_id"] == P + job
        assert (sum(r["score_v3"] for r in rs), sum(bool(r["cap_hit"]) for r in rs)) == (ed[key]["right_v3"], ed[key]["cap_hits"]), name
        (OUT / f"{name}.jsonl").write_text("".join(json.dumps({"problem_index": r["problem_index"], "sample": 0, "seed": r["seed"], "score_v3": r["score_v3"],
                                                               "cap_hit": r["cap_hit"], "n_new": r["n_new"]}) + "\n" for r in rs))
    en = {}
    for name, job in ENERGY.items():
        t = json.loads((run_dir(job) / "edit.json").read_text())["tensors"]
        en[name] = {"job": P + job, "per_matrix_share": {k: v["sums"]["top_sq"] / v["sums"]["d_sq"] for k, v in t.items() if v["sums"]["d_sq"]},
                    "total_share": sum(v["sums"]["top_sq"] for v in t.values()) / sum(v["sums"]["d_sq"] for v in t.values())}
    (OUT / "energy.json").write_text(json.dumps(en, indent=1) + "\n")
    cr = {}
    for cell, jobs in TEXTS.items():
        rows = [r for j in jobs for r in answers(j) if r.get("attempt", 0) == 0 and r["cap_hit"] and r["score_v3"] == 1]
        out = []
        for r in rows:
            t = r["text"]
            pos = [m.start() for m in re.finditer(r"\\boxed", t)]
            out.append({"problem_index": r["problem_index"], "seed": r["seed"], "n_new": r["n_new"], "finish_reason": r["finish_reason"],
                        "mode_v3": r.get("mode_v3"), "extracted_v3": r["extracted_v3"], "gold": r["gold"], "n_boxed": len(pos),
                        "last_boxed_at_fraction_of_text": round(pos[-1] / len(t), 3) if pos else None,
                        "text_after_last_boxed_400": t[pos[-1]:pos[-1] + 400] if pos else None, "text_tail_300": t[-300:]})
        cr[cell] = out
    (OUT / "cut_right.json").write_text(json.dumps(cr, indent=1, ensure_ascii=False) + "\n")
    print({k: len(v) for k, v in cr.items()}, {k: round(v["total_share"], 4) for k, v in en.items()})


if __name__ == "__main__":
    main()
