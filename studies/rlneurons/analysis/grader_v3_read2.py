"""Second read of every grader v1-to-v3 flip of the first table (board idea-884e91, DIRECTION.md open item "Grader").

The first read (grader/rln4_grader_v3.py, flip_review) covered 40 of the 113 wrong-to-right flips and the 1 right-to-wrong flip.
This file lists all 114, with the judgement of a second reader (Claude Fable 5.2, 2026-11-15) who read the answer tail of each
and the longer context of the ones noted. Laptop only. Download the cells as rln4_grader_v3.py describes, then

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.grader_v3_read2 --data <dir>
"""
import argparse
import hashlib
import json
import pathlib

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parent.parent
FIRST = STUDY / "results" / "rln4" / "grader_v3" / "readout.json"
OUT = STUDY / "results" / "rln4" / "grader_v3_read2" / "readout.json"
# Keys: (cell, problem_index). Every flip not listed was judged a correct change of score.
JUDGED_INCORRECT = {
    ("base_plain_1.0", 142): "wrong-to-right: the box holds 2 x 5! x 5! x 1!, which equals the gold 28800, but the line above "
                             "evaluates it to 24,000; the answer the model states as a number is wrong",
    ("base_plain_1.0", 146): "right-to-wrong: the answer to the problem is given and right; the model then writes a new problem "
                             "and v3 takes the mid-line 'Answer: $60$' of that one",
}
NOTES = {
    ("base_opener_1.0", 132): "right: '**Answer: 4**' is stated before the model writes a follow-up question; v3 reads the 4 of that follow-up",
    ("base_plain_1.0", 205): "right: the last box is [-2, -14, -7]; a 'Reflection' paragraph follows it",
    ("base_opener_1.0", 399): "right: 326.5 is stated three times; the final worked addition mislabels the digits but ends on 326.5",
    ("base_opener_1.0", 37): "right: '72Answer' is 72 with a repeated marker word",
    ("base_plain_1.0", 493): "right: the last box is 20; v1 had extracted unrelated text from earlier in the answer",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=pathlib.Path, required=True)
    data = ap.parse_args().data
    first = json.loads(FIRST.read_text())
    items, texts = [], {}
    for cell, f in first["flips_v1_to_v3"].items():
        p = data / f"{cell}.jsonl"
        assert hashlib.sha256(p.read_bytes()).hexdigest() == first["files"][cell]["sha256"], cell
        rows = {r["problem_index"]: r for r in map(json.loads, open(p))}
        for kind, want in (("wrong_to_right", (0, 1)), ("right_to_wrong", (1, 0))):
            for i in f[kind]:
                r = rows[i]
                x1, g = S.extract(r["text"])[1], R.grade_v3(r["gold"], r["text"])
                assert (S.grade(r["gold"], x1)["score"], g["score_v3"]) == want, (cell, i)
                texts.setdefault(hashlib.sha256(r["text"].encode()).hexdigest(), []).append((cell, i))
                items.append({"cell": cell, "problem_index": i, "kind": kind, "gold": r["gold"], "extracted_v1": x1,
                              "extracted_v3": g["extracted_v3"], "mode_v3": g["mode_v3"], "tail": r["text"][-350:],
                              "judged_incorrect": JUDGED_INCORRECT.get((cell, i)), "note": NOTES.get((cell, i))})
    keys = {(x["cell"], x["problem_index"]) for x in items}
    assert set(JUDGED_INCORRECT) <= keys and set(NOTES) <= keys
    up = [x for x in items if x["kind"] == "wrong_to_right"]
    down = [x for x in items if x["kind"] == "right_to_wrong"]
    assert (len(up), len(down)) == (first["flip_review"]["n_wrong_to_right"], first["flip_review"]["n_right_to_wrong"])
    per_cell = {c: {"wrong_to_right_judged_incorrect": sum(x["cell"] == c and x["judged_incorrect"] is not None for x in up),
                    "right_to_wrong_judged_incorrect": sum(x["cell"] == c and x["judged_incorrect"] is not None for x in down)}
                for c in first["flips_v1_to_v3"]}
    out = {"reader": "Claude Fable 5.2 (second reader), 2026-11-15", "first_read": str(FIRST.relative_to(STUDY.parent.parent)),
           "n_wrong_to_right": len(up), "n_wrong_to_right_read": len(up),
           "wrong_to_right_judged_incorrect": sum(x["judged_incorrect"] is not None for x in up),
           "n_right_to_wrong": len(down), "right_to_wrong_judged_incorrect": sum(x["judged_incorrect"] is not None for x in down),
           "distinct_texts": len(texts), "texts_shared_by_two_cells": sum(len(v) > 1 for v in texts.values()),
           "per_cell": per_cell,
           "example_judged_correct": next(x for x in up if x["judged_incorrect"] is None),
           "example_judged_incorrect": next(x for x in up if x["judged_incorrect"] is not None),
           "items": items}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print({k: v for k, v in out.items() if k not in ("items", "example_judged_correct", "example_judged_incorrect")})


if __name__ == "__main__":
    main()
