"""Planted cases for jobs/distill_data.py.

    uv run --no-project --with math-verify==0.9.0 python -m studies.rlneurons.jobs.distill_data_test
"""
import json
import pathlib
import tempfile

from studies.rlneurons.jobs import distill_data as D


def row(i, s, ans, n, cap=False, gold="7"):
    return {"problem_index": i, "sample": s, "attempt": 0, "cap_hit": cap, "finish_reason": "length" if cap else "stop",
            "extracted_v3": ans, "n_new": n, "text": f" line!\n\nOkay p{i} s{s}", "gold": gold, "score_v3": int(ans == gold),
            "parsed_gold": [gold]}


def run(rows):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "answers.jsonl"
        p.write_text("".join(json.dumps(r) + "\n" for r in rows))
        by = D.load(p)
    assert all(set(r) == set(D.KEEP) for v in by.values() for r in v), "a field outside KEEP reached the builder"
    return D.build(by)


def main():
    rows = [
        # problem 0: plurality "5" (samples 0, 2, 3); sample 1 disagrees and is the shortest; sample 3 is a shorter "5" but a cap hit
        row(0, 0, "5", 300), row(0, 1, "6", 50), row(0, 2, "5", 200), row(0, 3, "5", 100, cap=True),
        # problem 1: 2 against 2: no plurality, dropped
        row(1, 0, "1", 10), row(1, 1, "1", 10), row(1, 2, "2", 10), row(1, 3, "2", 10),
        # problem 2: plurality "3" only among cap hits: dropped
        row(2, 0, "3", 99, cap=True), row(2, 1, "3", 99, cap=True), row(2, 2, "4", 10), row(2, 3, None, 10),
        # problem 3: "1/2" and "0.5" agree (one group of 2); the others have no answer
        row(3, 0, "1/2", 40), row(3, 1, "0.5", 30), row(3, 2, None, 5), row(3, 3, None, 6, cap=True),
        # an attempt-1 row must be ignored
        {**row(0, 1, "5", 1), "attempt": 1},
    ]
    arms, why = run(rows)
    pick = {k: [(r["problem_index"], r["sample"]) for r in v] for k, v in arms.items()}
    assert pick["V"] == [(0, 2), (3, 1)], pick
    assert why == {"no_plurality": 1, "plurality_none_finished": 1}, why
    assert pick["S"] == [(0, 1), (3, 2)], pick                       # length control ignores agreement
    assert all(not r["cap_hit"] for v in arms.values() for r in v), "a cap-hit row entered an arm"
    assert [i for i, _ in pick["U"]] == [0, 3], pick
    assert (0, 1) not in pick["V"], "a row that disagrees with the plurality entered V"
    # the gold field is unused: changing every gold (and the score fields) changes nothing
    arms2, why2 = run([{**r, "gold": "999", "score_v3": 0, "parsed_gold": None} for r in rows])
    assert arms2 == arms and why2 == why
    print("distill_data_test: all planted cases pass")


if __name__ == "__main__":
    main()
