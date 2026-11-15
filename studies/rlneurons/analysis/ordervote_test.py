"""Planted cases for analysis/ordervote.py (specs/SPEC_ordervote.md).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.ordervote_test
"""
from studies.rlneurons.analysis import ordervote as O


def rows(*answers, right="1"):
    return [{"extracted_v3": x, "score_v3": int(x == right)} for x in answers]


def main():
    # no ties: stored, every order and the expectation are the same number
    c = O.cell({i: rows("1", "1", "1", "2") if i % 3 else rows("2", "2", "3", None) for i in range(30)})
    r = c["row"]
    assert r["ties"] == 0 and r["posted_stored_order"] == r["order_mean"] == r["expected_random_tie"] == r["order_min"] == r["order_max"] == 20, r
    # every problem a two-way tie with one right group: exactly half in the order mean and in the expectation;
    # the stored order gives all (right group first) or none (wrong group first)
    for first_right, stored in ((True, 40), (False, 0)):
        c = O.cell({i: rows("1", "2", "1", "2") if first_right else rows("2", "1", "2", "1") for i in range(40)})
        r = c["row"]
        assert r["ties"] == 40 and r["posted_stored_order"] == stored and r["order_mean"] == r["expected_random_tie"] == 20, r
        assert (r["order_min"], r["order_max"]) == (0, 40) and r["largest_per_problem_gap_order_mean_vs_expected"] == 0, r
    # four different answers, one right: a quarter; three wrong answers and a sample without an answer: 0
    c = O.cell({0: rows("1", "2", "3", "4"), 1: rows("2", "3", "4", None)})
    assert c["s"].tolist() == [0.25, 0.0] and c["row"]["order_mean"] == 0.25, c["row"]
    # a contrast of a vote with itself is 0 in both views; of the lucky stored order against the unlucky one 100 and 0 points
    a, b = O.cell({i: rows("1", "2", "1", "2") for i in range(40)}), O.cell({i: rows("2", "1", "2", "1") for i in range(40)})
    k = O.contrast({"a": a, "b": b}, "a", "b", None, None, "", {None: O.C.idx_matrix(40)})
    assert k["stored_order"]["points"] == 100 and k["order_averaged"]["points"] == 0 and k["changes_by_more_than_half_width"] and k["conclusion_flips"], k
    print("ordervote_test: all planted cases pass")


if __name__ == "__main__":
    main()
