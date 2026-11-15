"""Part B plan of the answer-statement repair (specs/SPEC_repair.md): which stored samples get the forced suffix.

    python3 -m studies.rlneurons.prep.repair_plan --base runs/abaybektursun-1114-153825-208b --rl runs/abaybektursun-1114-183640-e828

Reads results/repair/offline-01/rows.jsonl (eligibility: finished, v3 extraction unusable; never the gold) and the two jobs'
answers.jsonl (for the text hashes). Writes data/repair/plan_v1.json: per model the eligible samples and 100 control samples
(right under v3, finished, random.Random(0)), each with the sha256 of its stored text and its seed.
"""
import argparse
import hashlib
import json
import pathlib
import random

STUDY = pathlib.Path(__file__).resolve().parent.parent
SUFFIX = "\n\nThus, the final answer is \\(\\boxed{"
SEED, MAX_NEW, CONTROLS = 95_000_000, 64, 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--rl", required=True)
    a = ap.parse_args()
    rows = [json.loads(l) for l in (STUDY / "results/repair/offline-01/rows.jsonl").open()]
    plan = {"version": 1, "suffix": SUFFIX, "max_new_tokens": MAX_NEW, "sampling": {"temperature": 1.0, "top_p": 1.0},
            "seed_rule": f"{SEED} + 10000 * sample + problem_index", "rows": []}
    for model, run in (("base_cue", a.base), ("rl", a.rl)):
        sha = {}
        for line in (pathlib.Path(run) / "answers.jsonl").open():
            r = json.loads(line)
            if r["attempt"] == 0:
                sha[(r["problem_index"], r["sample"])] = hashlib.sha256(r["text"].encode()).hexdigest()
        mine = [r for r in rows if r["model"] == model]
        right = [r for r in mine if r["score_v3"] and r["finish_reason"] == "stop"]
        picks = [(r, "eligible") for r in mine if r["eligible_part_b"]] + [(r, "control") for r in random.Random(0).sample(right, CONTROLS)]
        for r, arm in picks:
            k = (r["problem_index"], r["sample"])
            plan["rows"].append({"model": model, "job": pathlib.Path(run).name, "arm": arm, "problem_index": k[0], "sample": k[1],
                                 "text_sha256": sha[k], "seed": SEED + 10000 * k[1] + k[0]})
    out = STUDY / "data/repair/plan_v1.json"
    assert not out.exists(), out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=1))
    print({(m, arm): sum(r["model"] == m and r["arm"] == arm for r in plan["rows"]) for m in ("base_cue", "rl") for arm in ("eligible", "control")})


if __name__ == "__main__":
    main()
