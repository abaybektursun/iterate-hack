"""Regrade stored Code pair cells with code_lib.extract_v2 or extract_v3 (specs/SPEC_code_think.md amendments 1 and 2). No model: a
job only because the tests run model-written programs, which the laptop does not do.

    ih submit l40s-small --hours 1 -- "aws s3 cp --recursive --only-show-errors s3://<bucket>/<prefix>/ /tmp/in/ &&
        /opt/ih/bin/python -m studies.rlneurons.jobs.regrade_code --rule v3 --inp /tmp/in --out \\$OUT_DIR"

  --rule v2 | v3
  --inp  one folder per cell, each holding the answers.jsonl that run_code_cell wrote.
  --out  check.json, then <cell>/answers_<rule>.jsonl (every row; v1 fields kept, plus mode_<rule>, code_<rule>, passed_<rule>,
         exit_<rule>, stderr_tail_<rule>) and metrics_<rule>.json.

Order: (1) instrument check on the 538 scored problems. The reference program in the form the rule adds (v2: a `python` line, the
program, a closing fence, no opening fence; v3: that with a line `CODE` before the program) must pass under the rule and fail
under extract; the planted wrong program in that form must fail under the rule. The job stops otherwise. (2) each cell: a row
whose program is the same under the rule as under extract keeps its v1 outcome; the other rows are run.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from concurrent.futures import ThreadPoolExecutor

from studies.rlneurons.jobs.run_code_cell import STUDY, WORKERS, load
from studies.rlneurons.lib import code_lib as C

FORM = {"v2": "reasoning\n</think>\n\npython\n{code}\n```", "v3": "reasoning\n</think>\n\npython\nCODE\n{code}\n```"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", required=True, choices=tuple(FORM))
    ap.add_argument("--inp", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    k, extract, out = a.rule, getattr(C, "extract_" + a.rule), pathlib.Path(a.out)
    fz = json.loads((STUDY / "data" / "code1" / "frozen_code1.json").read_text())
    t = fz["test_timeout_s"]
    probs = {p["uid"]: p for p in load(fz, None) if p["uid"] not in fz["excluded"]}
    assert len(probs) == 538, len(probs)

    def check(p):
        ref = FORM[k].format(code=p["reference"][len(p["pre"]):] if p["pre"] else p["reference"])
        wrong = FORM[k].format(code=C.WRONG.format(entry=p["entry"]))
        return {"uid": p["uid"], "ref_rule": C.run(C.program(p, extract(ref)[1]), t)["passed"],
                "ref_v1": C.run(C.program(p, C.extract(ref)[1]), t)["passed"], "wrong_rule": C.run(C.program(p, extract(wrong)[1]), t)["passed"]}

    with ThreadPoolExecutor(WORKERS) as ex:
        chk = list(ex.map(check, probs.values()))
    bad = [c for c in chk if not c["ref_rule"] or c["ref_v1"] or c["wrong_rule"]]
    out.mkdir(parents=True, exist_ok=True)
    (out / "check.json").write_text(json.dumps({"rule": k, "n": len(chk), "bad": bad}, indent=1))
    assert not bad, f"instrument check: {len(bad)} problems, first {bad[:3]}"

    def grade(r):
        mode, code = extract(r["text"])
        if code == r["code"]:
            return {**r, f"mode_{k}": mode, f"passed_{k}": r["passed"], f"exit_{k}": r["exit"]}
        g = C.run(C.program(probs[r["uid"]], code), t)
        return {**r, f"mode_{k}": mode, f"code_{k}": code, f"passed_{k}": g["passed"], f"exit_{k}": g["exit"], f"stderr_tail_{k}": g["stderr_tail"]}

    for cell in sorted(pathlib.Path(a.inp).iterdir()):
        rows = [json.loads(line) for line in open(cell / "answers.jsonl")]
        assert len(rows) == 538, (cell.name, len(rows))
        with ThreadPoolExecutor(WORKERS) as ex:
            rows = list(ex.map(grade, rows))
        (out / cell.name).mkdir()
        (out / cell.name / f"answers_{k}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        rerun = [r for r in rows if f"code_{k}" in r]
        m = {"cell": cell.name, "rule": k, "n": len(rows), "passed_v1": sum(r["passed"] for r in rows),
             f"passed_{k}": sum(r[f"passed_{k}"] for r in rows), "rerun": len(rerun), "rerun_passed": sum(r[f"passed_{k}"] for r in rerun),
             "modes": {mo: sum(r[f"mode_{k}"] == mo for r in rows) for mo in ("block", "unopened", "none")}}
        (out / cell.name / f"metrics_{k}.json").write_text(json.dumps(m, indent=1))
        print(json.dumps(m))


if __name__ == "__main__":
    main()
