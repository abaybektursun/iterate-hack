"""Planted cases for analysis/tieshort.py (specs/SPEC_tieshort.md, check 2).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.tieshort_test
"""
from studies.rlneurons.analysis import selector as SEL
from studies.rlneurons.analysis import tieshort as T


def s(ans, n_new, cap=False):
    return {"extracted_v3": ans, "score_v3": int(ans == "1"), "n_new": n_new, "cap_hit": cap, "gold": "1"}


def total(first, rule):
    return sum(SEL.pick(first[i], SEL.RULES[rule])[1] for i in first)


def main():
    n = 40
    plain = {i: [s("1", 900), s("1", 800), s("1", 700), s("7", 100)] for i in range(100, 110)}          # no tie: the rule must not move
    # A: 2 against 2, the lowest sample is wrong, the right group holds the shortest sample: the rule gains exactly the ties
    a = {**{i: [s("7", 900), s("1", 500), s("7", 800), s("1", 2000)] for i in range(n)}, **plain}
    t = T.ties(a)
    assert t["n"] == n and total(a, "vote") == 10 and total(a, "tie_short") == 10 + n and (t["low"], t["short"]) == (0, n)
    assert t["short_group"] == [n, n] and t["other_tied_groups"] == [0, n]
    assert abs(t["shuffled"] - n / 2) < 0.1 * n, t["shuffled"]                                          # blind to length: half the ties
    # B: the right group is the lowest sample in every second tie: the vote has half, shuffled lengths gain about 0 over it
    b = {i: [s("7", 900), s("1", 500), s("7", 800), s("1", 2000)] if i % 2 else [s("1", 500), s("7", 900), s("1", 2000), s("7", 800)] for i in range(n)}
    t = T.ties(b)
    assert (t["low"], t["short"]) == (n // 2, n) and abs(t["shuffled"] - t["low"]) < 0.1 * n, t
    # C: the shortest tied group is always wrong and the lowest sample right: the rule loses exactly the ties
    c = {i: [s("1", 900), s("7", 300), s("1", 2000), s("7", 800)] for i in range(n)}
    t = T.ties(c)
    assert (t["low"], t["short"], t["long"]) == (n, 0, n) and t["short_group"] == [0, n]
    # D: every tied sample is a cap hit with an answer: the rule falls back to the lowest sample
    d = {0: [s("7", 16384, True), s("1", 16384, True), s(None, 16384, True), s(None, 16384, True)]}
    t = T.ties(d)
    assert (t["n"], t["low"], t["short"], t["no_finished_tied_group"]) == (1, 0, 0, 1) and t["short_group"] == [0, 0]
    # shuffled keeps a cap hit's length and the multiset of finished lengths
    import numpy as np
    rows = [s("7", 16384, True), s("1", 5), s("7", 6), s("1", 7)]
    x = T.shuffled(rows, np.random.default_rng(0))
    assert x[0]["n_new"] == 16384 and sorted(r["n_new"] for r in x[1:]) == [5, 6, 7]
    print("tieshort_test: ok")


if __name__ == "__main__":
    main()
