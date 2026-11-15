"""The problem sets and the grading of the autobench study. Runs on the CPU side only, never in the GPU container.
Problems and grader are the rlneurons study's own: run_cell.problems (MATH-500 as frozen in data/rln4, the 328
harder problems) and rln4_lib.grade_v3.

    /opt/rln-vllm/bin/python /trusted/grade.py problems <set>              JSON list of {index, problem}, no answers
    /opt/rln-vllm/bin/python /trusted/grade.py grade <set> <answers.json>  JSON list of {index, right, extracted}

Sets: dev100 = the 100 MATH-500 problems of data/dev100-v1.json (what every experiment is scored on),
      math400 = the other 400 MATH-500 problems, hard328 = the 328 harder problems (both: finals only).
answers.json is a list of [index, text]. A problem without a text is wrong.
"""
import json
import pathlib
import sys

from studies.rlneurons.jobs import run_cell
from studies.rlneurons.lib import rln4_lib as R

DEV = pathlib.Path(__file__).resolve().parent / "dev100-v1.json"


def load(name):
    fz = json.loads((run_cell.D4 / "frozen4.json").read_text())
    if name == "hard328":
        return run_cell.problems("hard328", fz)
    dev = set(json.loads(DEV.read_text())["indices"])
    assert len(dev) == 100
    return [p for p in run_cell.problems("math500", fz) if (int(p["index"]) in dev) == (name == "dev100")]


def main():
    command, name = sys.argv[1], sys.argv[2]
    assert name in ("dev100", "math400", "hard328"), name
    problems = load(name)
    assert len(problems) == {"dev100": 100, "math400": 400, "hard328": 328}[name]
    if command == "problems":
        print(json.dumps([{"index": int(p["index"]), "problem": p["problem"]} for p in problems]))
    elif command == "grade":
        answers = {int(k): v for k, v in json.loads(pathlib.Path(sys.argv[3]).read_text())}
        rows = []
        for p in problems:
            g = R.grade_v3(p["answer"], answers.get(int(p["index"]), ""))
            rows.append({"index": int(p["index"]), "right": g["score_v3"], "extracted": g["extracted_v3"]})
        print(json.dumps(rows))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
