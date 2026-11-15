"""Code pair readout (specs/SPEC_code1.md) from run_code_cell outputs copied by `gpu.py get` to runs/<job-id>/.

    python3 -m studies.rlneurons.analysis.code1_readout rl_plain=<job-id> base_plain=<job-id> [base_cue=<job-id> ...]

Writes results/code1/<arm>-01/ per cell (run.json, metrics.json, examples.json: the first passed and the first failed problem with
prompt, answer, extracted code and exit) and results/code1/readout.json: passed of 538 with Wilson intervals per set, cap hits,
answers with no fenced block, tokens per problem, each pair of cells by paired bootstrap (5,000), the same without the 3 problems
that overlap the RL training prompts, and the 20 most frequent first words of each cell's answers.

  --out=<folder under results/>  another experiment's folder instead of code1 (xreward/code_dial for SPEC_xreward amendment 7).
  @<arm>=<job-id>                a reference cell that already has its run folder elsewhere: read and compared, no folder written."""
from __future__ import annotations

import collections
import json
import pathlib
import sys

from studies.rlneurons.lib import n13_score as S

STUDY = pathlib.Path(__file__).resolve().parents[1]
RES = STUDY / "results" / "code1"
OVERLAP = {"HumanEval/47", "Mbpp/641", "Mbpp/804"}


def main():
    res = RES
    for a in [a for a in sys.argv[1:] if a.startswith("--out=")]:
        res = STUDY / "results" / a.split("=")[1]
    refs = {a[1:].split("=")[0] for a in sys.argv[1:] if a.startswith("@")}
    cells = dict(a.lstrip("@").split("=") for a in sys.argv[1:] if not a.startswith("--out="))
    rows, out = {}, {"cells": {}, "differences": {}, "overlap_excluded": sorted(OVERLAP)}
    for arm, job in cells.items():
        run = pathlib.Path("runs") / job
        m = json.loads((run / "metrics.json").read_text())
        assert m["status"] == "done", (arm, m["status"])
        rs = [json.loads(l) for l in (run / "answers.jsonl").read_text().splitlines()]
        rows[arm] = {r["uid"]: r for r in rs}
        if arm not in refs:
            d = res / f"{arm}-01"
            d.mkdir(parents=True, exist_ok=False)
            keep = ("uid", "seed", "prompt", "text", "mode", "code", "passed", "exit", "stderr_tail", "n_new", "cap_hit")
            (d / "examples.json").write_text(json.dumps([{k: r[k] for k in keep} for want in (True, False)
                                                         for r in [next(r for r in rs if r["passed"] is want)]], indent=1))
            (d / "metrics.json").write_text(json.dumps(m, indent=1))
            (d / "run.json").write_text(json.dumps({"job_id": job, "commit": m["commit"], "config": m["config"]}, indent=1))
        c = {}
        for b in ("humanevalplus", "mbppplus", "all", "all_no_overlap"):
            sel = [r for r in rs if b == "all" or r["bench"] == b or (b == "all_no_overlap" and r["uid"] not in OVERLAP)]
            k = sum(r["passed"] for r in sel)
            c[b] = {"n": len(sel), "passed": k, "pct": 100 * k / len(sel), "wilson95": S.wilson(k, len(sel)),
                    "cap_hits": sum(r["cap_hit"] for r in sel), "no_block": sum(r["mode"] == "none" for r in sel),
                    "timeouts": sum(r["exit"] == "timeout" for r in sel), "tokens_per_problem": sum(r["n_new"] for r in sel) / len(sel)}
        first = collections.Counter(" ".join(r["text"].split()[:3]) for r in rs)
        out["cells"][arm] = {"job_id": job, "commit": m["commit"], "prefix_text": m["prefix_text"], **c, "first_three_words": first.most_common(20)}
    arms = list(cells)
    for i, a in enumerate(arms):
        for b in arms[i + 1:]:
            uids = sorted(rows[a])
            assert uids == sorted(rows[b]), (a, b)
            x, y = [int(rows[a][u]["passed"]) for u in uids], [int(rows[b][u]["passed"]) for u in uids]
            out["differences"][f"{a} - {b}"] = {"points": 100 * (sum(x) - sum(y)) / len(uids), "bootstrap95": S.paired_bootstrap(x, y, 5000),
                                                "only_first": sum(p > q for p, q in zip(x, y)), "only_second": sum(q > p for p, q in zip(x, y))}
    (res / "readout.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"cells": {a: {b: (v[b]["passed"], v[b]["n"], v[b]["cap_hits"], round(v[b]["tokens_per_problem"])) for b in ("humanevalplus", "mbppplus", "all")}
                                for a, v in out["cells"].items()}, "differences": out["differences"]}, indent=1))


if __name__ == "__main__":
    main()
