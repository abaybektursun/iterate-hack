"""Readout of the test outside math and code (specs/SPEC_ood1.md) from run_mcq_cell outputs copied by `gpu.py get` to runs/<job-id>/.

    python3 -m studies.rlneurons.analysis.ood1_readout base_plain=<job-id> base_cue=<job-id> rl_plain=<job-id> sft_cue=<job-id>

Writes results/ood1/<arm>-01/ per cell (run.json, metrics.json, examples.json: the first right and the first wrong item with
prompt, answer, extracted letter and gold) and results/ood1/readout.json: right of 500 and per benchmark with Wilson intervals,
cap hits, answers without a letter, tokens per item, right per group, and each pair of cells by paired bootstrap (5,000) on the
500 and on each benchmark."""
from __future__ import annotations

import collections
import json
import pathlib
import sys

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
RES = STUDY / "results" / "ood1"
BENCHES = ("mmlupro", "bbh", "all")


def main():
    cells = dict(a.split("=") for a in sys.argv[1:])
    rows, out = {}, {"cells": {}, "differences": {}}
    for arm, job in cells.items():
        run = pathlib.Path("runs") / job
        m = json.loads((run / "metrics.json").read_text())
        assert m["status"] == "done" and m["n_items"] == 500, (arm, m["status"], m["n_items"])
        rs = [json.loads(l) for l in (run / "answers.jsonl").read_text().splitlines()]
        rows[arm] = {r["uid"]: r for r in rs}
        d = RES / f"{arm}-01"
        d.mkdir(parents=True, exist_ok=False)
        keep = ("uid", "seed", "prompt", "text", "mode", "letter", "gold", "right", "n_new", "cap_hit")
        (d / "examples.json").write_text(json.dumps([{k: r[k] for k in keep} for want in (True, False)
                                                     for r in [next(r for r in rs if r["right"] is want)]], indent=1))
        (d / "metrics.json").write_text(json.dumps(m, indent=1))
        (d / "run.json").write_text(json.dumps({"job_id": job, "commit": m["commit"], "config": m["config"]}, indent=1))
        c = {}
        for b in BENCHES:
            sel = [r for r in rs if b in ("all", r["bench"])]
            k = sum(r["right"] for r in sel)
            c[b] = {"n": len(sel), "right": k, "pct": 100 * k / len(sel), "wilson95": S.wilson(k, len(sel)),
                    "cap_hits": sum(r["cap_hit"] for r in sel), "no_answer": sum(r["mode"] != "answer" for r in sel),
                    "tokens_per_item": sum(r["n_new"] for r in sel) / len(sel)}
        groups = collections.defaultdict(lambda: [0, 0])
        for r in rs:
            groups[f"{r['bench']}/{r['group']}"][0] += r["right"]
            groups[f"{r['bench']}/{r['group']}"][1] += 1
        out["cells"][arm] = {"job_id": job, "commit": m["commit"], "model": m["model_repo"], "prefix_text": m["prefix_text"], **c,
                             "groups": dict(sorted(groups.items()))}
    arms = list(cells)
    for i, a in enumerate(arms):
        for b in arms[i + 1:]:
            assert sorted(rows[a]) == sorted(rows[b]), (a, b)
            for bench in BENCHES:
                uids = sorted(u for u, r in rows[a].items() if bench in ("all", r["bench"]))
                x, y = [int(rows[a][u]["right"]) for u in uids], [int(rows[b][u]["right"]) for u in uids]
                out["differences"][f"{a} - {b} | {bench}"] = {
                    "points": 100 * (sum(x) - sum(y)) / len(uids), "bootstrap95": S.paired_bootstrap(x, y, 5000),
                    "only_first": sum(p > q for p, q in zip(x, y)), "only_second": sum(q > p for p, q in zip(x, y))}
    (RES / "readout.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"cells": {a: {b: (v[b]["right"], v[b]["n"], v[b]["cap_hits"], v[b]["no_answer"], round(v[b]["tokens_per_item"]))
                                    for b in BENCHES} for a, v in out["cells"].items()}, "differences": out["differences"]}, indent=1))


if __name__ == "__main__":
    main()
