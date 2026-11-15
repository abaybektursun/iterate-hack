"""Readout of the test outside math and code (specs/SPEC_ood1.md) from run_mcq_cell outputs copied by `gpu.py get` to runs/<job-id>/.

    python3 -m studies.rlneurons.analysis.ood1_readout base_plain=<job-id> base_cue=<job-id> rl_plain=<job-id> sft_cue=<job-id>

Writes results/ood1/<arm>-01/ per cell (run.json, metrics.json, examples.json: the first right and the first wrong item with
prompt, answer, extracted letter and gold) and results/ood1/readout.json: right of 500 and per benchmark with Wilson intervals,
under grader v1 (the job's) and grader v2 (mcq_lib.grade_v2, SPEC_ood1.md amendment 1, computed here from the same text),
cap hits, answers without a letter, tokens per item, right per group, and each pair of cells by paired bootstrap (5,000) on the
500 and on each benchmark."""
from __future__ import annotations

import collections
import json
import pathlib
import sys

from studies.rlneurons.lib import mcq_lib as M
from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
RES = STUDY / "results" / "ood1"
BENCHES = ("mmlupro", "bbh", "all")
N_OPTIONS = {x["uid"]: x["n_options"] for x in json.loads((STUDY / "data" / "ood1" / "ood1_items.json").read_text())}


def main():
    cells = dict(a.split("=") for a in sys.argv[1:])
    rows, out = {}, {"cells": {}, "differences": {}}
    for arm, job in cells.items():
        run = pathlib.Path("runs") / job
        m = json.loads((run / "metrics.json").read_text())
        assert m["status"] == "done" and m["n_items"] == 500, (arm, m["status"], m["n_items"])
        rs = [json.loads(l) for l in (run / "answers.jsonl").read_text().splitlines()]
        for r in rs:                                          # grader v2 (amendment 1), from the same text
            g = M.grade_v2(r["text"], r["gold"], N_OPTIONS[r["uid"]])
            r.update(mode_v2=g["mode"], letter_v2=g["letter"], right_v2=g["right"])
        rows[arm] = {r["uid"]: r for r in rs}
        d = RES / f"{arm}-01"
        d.mkdir(parents=True, exist_ok=False)
        keep = ("uid", "seed", "prompt", "text", "mode", "letter", "gold", "right", "letter_v2", "right_v2", "n_new", "cap_hit")
        (d / "examples.json").write_text(json.dumps([{k: r[k] for k in keep} for want in (True, False)
                                                     for r in [next(r for r in rs if r["right"] is want)]], indent=1))
        (d / "metrics.json").write_text(json.dumps(m, indent=1))
        (d / "run.json").write_text(json.dumps({"job_id": job, "commit": m["commit"], "config": m["config"]}, indent=1))
        c = {}
        for b in BENCHES:
            sel = [r for r in rs if b in ("all", r["bench"])]
            k = sum(r["right"] for r in sel)
            c[b] = {"n": len(sel), "right": k, "pct": 100 * k / len(sel), "wilson95": S.wilson(k, len(sel)),
                    "right_v2": sum(r["right_v2"] for r in sel), "pct_v2": 100 * sum(r["right_v2"] for r in sel) / len(sel),
                    "wilson95_v2": S.wilson(sum(r["right_v2"] for r in sel), len(sel)),
                    "no_answer_v2": sum(r["mode_v2"] != "answer" for r in sel),
                    "cap_hits": sum(r["cap_hit"] for r in sel), "no_answer": sum(r["mode"] != "answer" for r in sel),
                    "tokens_per_item": sum(r["n_new"] for r in sel) / len(sel)}
        groups = collections.defaultdict(lambda: [0, 0, 0])      # right v1, right v2, n
        for r in rs:
            g = groups[f"{r['bench']}/{r['group']}"]
            g[0], g[1], g[2] = g[0] + r["right"], g[1] + r["right_v2"], g[2] + 1
        out["cells"][arm] = {"job_id": job, "commit": m["commit"], "model": m["model_repo"], "prefix_text": m["prefix_text"], **c,
                             "groups": dict(sorted(groups.items()))}
    arms = list(cells)
    for i, a in enumerate(arms):
        for b in arms[i + 1:]:
            assert sorted(rows[a]) == sorted(rows[b]), (a, b)
            for bench in BENCHES:
                uids = sorted(u for u, r in rows[a].items() if bench in ("all", r["bench"]))
                for key, ver in (("right", "v1"), ("right_v2", "v2")):
                    x, y = [int(rows[a][u][key]) for u in uids], [int(rows[b][u][key]) for u in uids]
                    out["differences"][f"{a} - {b} | {bench} | {ver}"] = {
                        "points": 100 * (sum(x) - sum(y)) / len(uids), "bootstrap95": S.paired_bootstrap(x, y, 5000),
                        "only_first": sum(p > q for p, q in zip(x, y)), "only_second": sum(q > p for p, q in zip(x, y))}
    (RES / "readout.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"cells": {a: {b: (v[b]["right"], v[b]["right_v2"], v[b]["n"], v[b]["cap_hits"], v[b]["no_answer"], v[b]["no_answer_v2"], round(v[b]["tokens_per_item"]))
                                    for b in BENCHES} for a, v in out["cells"].items()}, "differences": out["differences"]}, indent=1))


if __name__ == "__main__":
    main()
