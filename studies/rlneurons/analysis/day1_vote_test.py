"""Planted cases for analysis/day1_vote.py (specs/SPEC_day1_3.md). Includes inputs that must make the vote score 0 and inputs
that must make the completeness check raise.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote_test
"""
from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.lib import rln4_lib as R

GOLD = "\\frac{1}{2}"


def rows(*answers):
    """One problem's attempt-0 rows; the score is grader v3's on a text that ends with the answer in a box."""
    return [{"extracted_v3": x, "score_v3": 0 if x is None else R.grade_v3(GOLD, f"\\boxed{{{x}}}")["score_v3"]} for x in answers]


def att(i, s, a, cap, score, n_new=100):
    return {"problem_index": i, "sample": s, "attempt": a, "cap_hit": cap, "score_v3": score, "n_new": n_new, "seed": 0,
            "extracted_v3": None if cap else ("0.5" if score else "9"), "gold": GOLD, "prompt": "p", "text": "t"}


def raises(f):
    try:
        f()
    except AssertionError:
        return True
    return False


def main():
    v = V.vote(rows("0.5", "0.5", "0.5", "0.5"))                                   # four agree
    assert (v["winner"], v["votes"], v["tie"], v["score"]) == (0, 4, False, 1), v
    v = V.vote(rows("7", "0.5", "7", "0.5"))                                       # 2-2 tie: the group of the lowest sample wins
    assert (v["winner"], v["votes"], v["tie"], v["score"]) == (0, 2, True, 0), v
    v = V.vote(rows("0.5", "7", "7", "0.5"))                                       # the same tie in another order: the other group wins
    assert (v["winner"], v["votes"], v["tie"], v["score"]) == (0, 2, True, 1), v
    v = V.vote(rows(None, "0.5", "0.5", "7"))                                      # a sample without an answer casts no vote
    assert (v["winner"], v["votes"], v["tie"], v["score"], v["groups"]) == (1, 2, False, 1, [[1, 2], [3]]), v
    v = V.vote(rows(None, None, None, "7"))                                        # one answer beats three samples without one
    assert (v["winner"], v["votes"], v["score"]) == (3, 1, 0), v
    v = V.vote(rows(None, None, None, None))                                       # no answer at all: scored wrong
    assert (v["winner"], v["votes"], v["score"]) == (None, 0, 0), v
    v = V.vote(rows("7", "\\frac{1}{2}", "0.5", "\\dfrac{2}{4}"))                  # equivalent forms are one answer
    assert (v["winner"], v["votes"], v["tie"], v["score"], v["groups"]) == (1, 3, False, 1, [[0], [1, 2, 3]]), v
    v = V.vote(rows("\\frac{1}{3}", "\\frac{1}{2}", "0.5", "\\frac{1}{3}"))        # unequal forms stay apart: 1/3 is not 1/2
    assert (v["groups"], v["tie"], v["score"]) == ([[0, 3], [1, 2]], True, 0), v
    v = V.vote(rows("7", "7", "7", "0.5"))                                         # must fail: a wrong majority beats the right answer
    assert (v["winner"], v["votes"], v["score"]) == (0, 3, 0), v

    # restart merge: problem 0 finishes right at attempt 2; problem 1 hits the cap three times; problem 2 finishes wrong at once
    rs = [att(0, 0, 0, True, 0, 16384), att(0, 0, 1, True, 0, 16384), att(0, 0, 2, False, 1, 500),
          att(1, 0, 0, True, 0, 16384), att(1, 0, 1, True, 0, 16384), att(1, 0, 2, True, 0, 16384), att(2, 0, 0, False, 0, 300)]
    res, ex = V.readout(rs, 3, 1, 2)
    assert res["rows"]["single"]["right"] == 0 and res["rows"]["restart"]["right"] == 1, res["rows"]
    assert res["rows"]["single"]["tokens_per_problem"] == (16384 * 2 + 300) / 3
    assert res["rows"]["restart"]["tokens_per_problem"] == (16384 * 5 + 500 + 300) / 3
    assert res["restart_sample_0"] == {"attempts_hist": {3: 2, 1: 1}, "final_cap_hits": 1, "final_cap_hits_right": 0}
    assert ex["restart"]["right"]["problem_index"] == 0 and len(ex["restart"]["right"]["attempts"]) == 3
    assert raises(lambda: V.readout(rs[:2] + rs[3:], 3, 1, 2))      # must fail: a cap hit without its restart (job killed)
    assert raises(lambda: V.readout(rs[:6], 3, 1, 2))               # must fail: a problem is missing
    assert raises(lambda: V.readout(rs, 3, 2, 2))                   # must fail: sample 1 is missing
    assert raises(lambda: V.readout(rs + [att(2, 0, 1, False, 1)], 3, 1, 2))   # must fail: a restart after a finished attempt
    assert raises(lambda: V.readout(rs + [rs[-1]], 3, 1, 2))        # must fail: a row twice

    # two samples, vote and pass@k rows and their tokens: problem 0 right + wrong (tie, sample 0 wins), problem 1 wrong + right
    rs = [att(0, 0, 0, False, 1, 10), att(0, 1, 0, False, 0, 20), att(1, 0, 0, False, 0, 30), att(1, 1, 0, False, 1, 40)]
    res, _ = V.readout(rs, 2, 2, 0)
    assert [res["rows"][k]["right"] for k in ("single", "vote", "pass_at_k")] == [1, 1, 2], res["rows"]
    assert res["rows"]["vote"]["tokens_per_problem"] == 50 and res["rows"]["single"]["tokens_per_problem"] == 20
    assert res["vote_stats"]["ties_for_first"] == 2 and res["each_sample"]["single_right"] == [1, 1]
    print("day1_vote_test: all planted cases pass")


if __name__ == "__main__":
    main()
