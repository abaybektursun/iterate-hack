"""Regrade stored Code pair cells with code_lib.extract_v2 (specs/SPEC_code_think.md amendment 1). No model: a job only because the
tests run model-written programs, which the laptop does not do.

    ih submit l40s-small --hours 1 -- "aws s3 cp --recursive --only-show-errors s3://<bucket>/<prefix>/ /tmp/in/ &&
        /opt/ih/bin/python -m studies.rlneurons.jobs.regrade_code_v2 --inp /tmp/in --out \\$OUT_DIR"

  --inp  one folder per cell, each holding the answers.jsonl that run_code_cell wrote.
  --out  check.json, then <cell>/answers_v2.jsonl (every row; v1 fields kept, plus mode_v2, passed_v2, exit_v2) and metrics_v2.json.

Order: (1) instrument check on the 538 scored problems: the reference program written in the unopened form (`python`, program,
closing fence, no opening fence) must pass under extract_v2 and fail under extract; the planted wrong program in that form must
fail under extract_v2. The job stops otherwise. (2) each cell: rows whose v1 mode is "block" keep their v1 outcome (extract_v2
returns the same program); the other rows are extracted with extract_v2 and run.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from concurrent.futures import ThreadPoolExecutor

from studies.rlneurons.jobs.run_code_cell import STUDY, WORKERS, load
from studies.rlneurons.lib import code_lib as C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    fz = json.loads((STUDY / "data" / "code1" / "frozen_code1.json").read_text())
    t = fz["test_timeout_s"]
    probs = {p["uid"]: p for p in load(fz, None) if p["uid"] not in fz["excluded"]}
    assert len(probs) == 538, len(probs)

    def unopened(code):
        return "reasoning\n</think>\n\npython\n" + code + "\n```"

    def check(p):
        ref = p["reference"][len(p["pre"]):] if p["pre"] else p["reference"]
        m2, c2 = C.extract_v2(unopened(ref))
        m1, c1 = C.extract(unopened(ref))
        mw, cw = C.extract_v2(unopened(C.WRONG.format(entry=p["entry"])))
        return {"uid": p["uid"], "modes": [m2, m1, mw], "ref_v2": C.run(C.program(p, c2), t)["passed"],
                "ref_v1": C.run(C.program(p, c1), t)["passed"], "wrong_v2": C.run(C.program(p, cw), t)["passed"]}

    with ThreadPoolExecutor(WORKERS) as ex:
        chk = list(ex.map(check, probs.values()))
    bad = [c for c in chk if c["modes"] != ["unopened", "none", "unopened"] or not c["ref_v2"] or c["ref_v1"] or c["wrong_v2"]]
    out.mkdir(parents=True, exist_ok=True)
    (out / "check.json").write_text(json.dumps({"n": len(chk), "bad": bad}, indent=1))
    assert not bad, f"instrument check: {len(bad)} problems, first {bad[:3]}"

    def grade(r):
        if r["mode"] == "block":
            return {**r, "mode_v2": "block", "passed_v2": r["passed"], "exit_v2": r["exit"]}
        mode, code = C.extract_v2(r["text"])
        g = C.run(C.program(probs[r["uid"]], code), t)
        return {**r, "mode_v2": mode, "code_v2": code, "passed_v2": g["passed"], "exit_v2": g["exit"], "stderr_tail_v2": g["stderr_tail"]}

    for cell in sorted(pathlib.Path(a.inp).iterdir()):
        rows = [json.loads(line) for line in open(cell / "answers.jsonl")]
        assert len(rows) == 538, (cell.name, len(rows))
        with ThreadPoolExecutor(WORKERS) as ex:
            rows = list(ex.map(grade, rows))
        (out / cell.name).mkdir()
        (out / cell.name / "answers_v2.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        m = {"cell": cell.name, "n": len(rows), "passed_v1": sum(r["passed"] for r in rows), "passed_v2": sum(r["passed_v2"] for r in rows),
             "unopened": sum(r["mode_v2"] == "unopened" for r in rows),
             "unopened_passed": sum(r["passed_v2"] for r in rows if r["mode_v2"] == "unopened"),
             "none_v2": sum(r["mode_v2"] == "none" for r in rows)}
        (out / cell.name / "metrics_v2.json").write_text(json.dumps(m, indent=1))
        print(json.dumps(m))


if __name__ == "__main__":
    main()
