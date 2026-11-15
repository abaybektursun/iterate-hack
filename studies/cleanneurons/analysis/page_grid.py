"""cleanneurons Part G, for the page /finding/loop-neurons: what became of each of the 500 problems in each cell (laptop, standard library).

    python3 -m studies.cleanneurons.analysis.page_grid studies/cleanneurons/results/gen/readout_t06.json studies/cleanneurons/results/gen/page_grid.json

Reads the readout of analysis/gen_readout.py and, for the unedited cell and each edited cell, the answers.jsonl in the run dir
that the readout names (raw rows, not committed). Writes per cell one string of 500 characters, character i for problem index
i: r right (grader v3) with no loop, w wrong with no loop, l wrong with a rule-A loop, b right with a rule-A loop (one row of
attr1000: the answer was given before the loop). Next to each string are the cell's totals, recomputed from the rows with
gen_readout.cell and asserted equal to the readout's, so right = r + b and loops = l + b are the numbers of readout_t06.json.
"""
import json
import os
import sys

from studies.cleanneurons.analysis.gen_readout import cell, load

CODES = {(1, 0): "r", (0, 0): "w", (0, 1): "l", (1, 1): "b"}  # (right by grader v3, rule-A loop)
TOTALS = ("n", "right_v3", "cap_hits", "loops_rule_A", "tokens_per_problem")


def main(readout, out):
    res = json.load(open(readout))
    arms = {}
    for name, c in {"baseline": res["baseline"], **res["arms"]}.items():
        R = load(c["dir"])
        totals = cell(R)
        assert totals == {k: c[k] for k in TOTALS}, (name, totals, {k: c[k] for k in TOTALS})
        grid = "".join(CODES[int(R[i]["score_v3"]), int(R[i]["loop_A"])] for i in range(500))
        assert grid.count("r") + grid.count("b") == c["right_v3"] and grid.count("l") + grid.count("b") == c["loops_rule_A"], name
        arms[name] = {"job": os.path.basename(c["dir"].rstrip("/")), **totals, "grid": grid}
    json.dump({"what": "per cell, character i is problem index i: r right, w wrong without a loop, l loop (wrong), b loop and right; "
                       "right_v3 = r + b, loops_rule_A = l + b",
               "readout": readout, "arms": arms}, open(out, "w"), indent=1)
    print(json.dumps({k: {**{t: v[t] for t in TOTALS}, **{ch: v["grid"].count(ch) for ch in "rwlb"}} for k, v in arms.items()}, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
