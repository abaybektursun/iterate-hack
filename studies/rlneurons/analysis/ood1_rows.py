"""Per-item rows and the answered-only control of the test outside math and code (specs/SPEC_ood1.md, board result-1a80e9).

    uv run --with numpy python -m studies.rlneurons.analysis.ood1_rows

Reads runs/<job-id>/answers.jsonl of the four cells named in results/ood1/readout.json. Writes results/ood1/rows-01/rows.json
(per item and cell: grader v2 letter, mode, right, cap hit, generated tokens) and results/ood1/rows-01/answered.json: for each
pair of cells, the items where both give an option letter under grader v2, right counts on them and the paired bootstrap
(5,000) of the difference, in points. A gain that is only "the model now writes an answer" disappears on these items."""
from __future__ import annotations

import json
import pathlib

from studies.rlneurons.lib import mcq_lib as M
from studies.rlneurons.lib import n13_score as S

RES = pathlib.Path(__file__).resolve().parents[1] / "results" / "ood1"


def main():
    readout = json.loads((RES / "readout.json").read_text())
    items = {x["uid"]: x for x in json.loads((RES.parents[1] / "data" / "ood1" / "ood1_items.json").read_text())}
    rows = {u: {"bench": x["bench"], "group": x["group"], "gold": x["gold"]} for u, x in items.items()}
    for arm, c in readout["cells"].items():
        for line in (pathlib.Path("runs") / c["job_id"] / "answers.jsonl").read_text().splitlines():
            r = json.loads(line)
            g = M.grade_v2(r["text"], r["gold"], items[r["uid"]]["n_options"])
            rows[r["uid"]][arm] = {"letter": g["letter"], "mode": g["mode"], "right": g["right"], "right_v1": r["right"],
                                   "cap_hit": r["cap_hit"], "n_new": r["n_new"]}
    out = RES / "rows-01"
    out.mkdir(exist_ok=False)
    (out / "rows.json").write_text(json.dumps(rows, indent=0) + "\n")
    arms, ans = list(readout["cells"]), {"no_letter": {}, "pairs": {}}
    for a in arms:
        ans["no_letter"][a] = {b: sum(r[a]["mode"] != "answer" for r in rows.values() if b in ("all", r["bench"])) for b in ("mmlupro", "bbh", "all")}
    for i, a in enumerate(arms):
        for b in arms[i + 1:]:
            for bench in ("mmlupro", "bbh", "all"):
                both = [r for r in rows.values() if bench in ("all", r["bench"]) and r[a]["mode"] == r[b]["mode"] == "answer"]
                x, y = [int(r[a]["right"]) for r in both], [int(r[b]["right"]) for r in both]
                ans["pairs"][f"{b} - {a} | {bench}"] = {"n_both_answer": len(both), "right_first": sum(y), "right_second": sum(x),
                                                        "points": 100 * (sum(y) - sum(x)) / len(both), "bootstrap95": S.paired_bootstrap(y, x, 5000)}
    (out / "answered.json").write_text(json.dumps(ans, indent=1) + "\n")
    print(json.dumps(ans["no_letter"]))
    for k, v in ans["pairs"].items():
        print(k, v["n_both_answer"], v["right_first"], v["right_second"], round(v["points"], 1), [round(z, 1) for z in v["bootstrap95"]])


if __name__ == "__main__":
    main()
