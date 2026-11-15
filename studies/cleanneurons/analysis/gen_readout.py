"""cleanneurons Part G readout: edited-model cells against the unedited cell, problem by problem (laptop, standard library).

    python3 -m studies.cleanneurons.analysis.gen_readout <out json> <baseline run dir> <name>=<run dir> [<name>=<run dir> ...]

Each run dir holds run_cell's answers.jsonl (one row per problem; same prompt, sampling setting and seeds in every cell, so the
cells differ only by the edit). Per cell: right (grader v3), cap hits, rule-A loops, generated tokens per problem. Per edited cell
against the baseline: the difference in points with a paired bootstrap interval (5,000 resamples, 95 %), newly right and newly
wrong problems, and what became of the baseline's looped problems. A problem that looped in the baseline is a selected bad draw,
so "now right" among them is compared with the same count in the random-neuron control cell, never with zero. Two examples per
edited cell: one baseline loop that the edit finished right and one it finished wrong (problem index, the last 300 characters).
"""
import json
import random
import sys


def load(d):
    rows = {r["problem_index"]: r for r in map(json.loads, open(f"{d}/answers.jsonl"))}
    assert len(rows) == 500, (d, len(rows))
    return rows


def cell(R):
    return {"n": len(R), "right_v3": sum(r["score_v3"] for r in R.values()), "cap_hits": sum(r["cap_hit"] for r in R.values()),
            "loops_rule_A": sum(r["loop_A"] for r in R.values()), "tokens_per_problem": sum(r["n_new"] for r in R.values()) / len(R)}


def main(out, base_dir, *arms):
    base, rng = load(base_dir), random.Random(0)
    loops = [i for i in sorted(base) if base[i]["loop_A"]]
    res = {"baseline": {"dir": base_dir, **cell(base)}, "baseline_loops": len(loops), "arms": {}}
    for spec in arms:
        name, d = spec.split("=")
        R = load(d)
        diff = [R[i]["score_v3"] - base[i]["score_v3"] for i in sorted(base)]
        bs = sorted(sum(rng.choices(diff, k=500)) / 5 for _ in range(5000))
        ex = {}
        for i in loops:
            key = "finished_right" if R[i]["score_v3"] else "finished_wrong" if not R[i]["cap_hit"] else None
            if key and key not in ex:
                ex[key] = {"problem_index": i, "gold": R[i]["gold"], "baseline_tail": base[i]["text"][-300:], "edited_tail": R[i]["text"][-300:], "edited_tokens": R[i]["n_new"]}
        res["arms"][name] = {"dir": d, **cell(R), "points_vs_baseline": sum(diff) / 5, "ci95": [bs[125], bs[4874]], "newly_right": sum(x == 1 for x in diff),
                             "newly_wrong": sum(x == -1 for x in diff),
                             "of_baseline_loops": {"still_loop": sum(R[i]["loop_A"] for i in loops), "cap_hit": sum(R[i]["cap_hit"] for i in loops), "now_right": sum(R[i]["score_v3"] for i in loops)},
                             "examples": ex}
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: ({x: y for x, y in v.items() if x != "examples"} if isinstance(v, dict) else v) for k, v in {"baseline": res["baseline"], **res["arms"]}.items()}, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
