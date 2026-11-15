"""Planted cases for analysis/frontier.py (specs/SPEC_frontier.md), including inputs on which a rule must fail.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.frontier_test
"""
from studies.rlneurons.analysis import frontier as F


def a(ans, n_new=1000, cap=False, right="1"):
    """One attempt; the right answer is `right`."""
    return {"extracted_v3": ans, "score_v3": int(ans == right), "n_new": n_new, "cap_hit": cap, "gold": right}


def got(name, chains, order=None):
    o = F.outcome(F.RULES[name], chains, order)
    return o["score"], o["tokens"], o["drawn"]


def raises(f, err):
    try:
        f()
    except err:
        return True
    return False


def main():
    same = [[a("1", 100)], [a("1", 200)], [a("1", 400)], [a("1", 800)]]
    assert got("seq4", same) == (1, 300, 2) and got("vote4", same) == (1, 1500, 4)             # four identical: 2 samples
    assert got("seq4", same, (3, 2, 1, 0)) == (1, 1200, 2)                                       # the draw order sets the cost
    diff4 = [[a("7", 100)], [a("8", 200)], [a("1", 50)], [a("9", 800)]]
    assert got("seq4", diff4) == (0, 1150, 4) and got("seq3", diff4) == (0, 350, 3)             # four different: 4 samples, tie to the first
    assert got("seq4_short", diff4) == (1, 1150, 4)                                             # the shortest finished sample is the right one
    assert got("seq4", [[a("7")], [a("8")], [a("8")], [a("1")]]) == (0, 3000, 3)                # the third agrees with the second
    bad = [[a("7", 100)], [a("7", 200)], [a("1", 400)], [a("1", 800)]]
    assert got("seq4", bad) == (0, 300, 2) and got("seq4_short", bad) == (0, 300, 2)            # two wrong agree first: must fail
    assert got("vote4_short", bad) == (0, 1500, 4) and got("seq4", bad, (2, 3, 0, 1)) == (1, 1200, 2)
    assert got("seq_2then4", diff4) == (0, 1150, 4) and got("seq_2then4", bad) == (0, 300, 2)
    assert got("seq_2then4", [[a("7")], [a("8")], [a("1")], [a("1")]]) == (1, 4000, 4)
    none = [[a(None, 16384, True)], [a(None, 16384, True)], [a(None, 10)], [a(None, 10)]]
    assert got("seq4", none) == (0, 2 * 16384 + 20, 4) and got("single", none) == (0, 16384, 1)  # no answer anywhere: score 0
    chain = [[a(None, 16384, True), a("1", 500)], [a(None, 16384, True), a(None, 16384, True), a("1", 300)], [a("7", 100)], [a("7", 100)]]
    assert got("single", chain) == (0, 16384, 1) and got("restart", chain) == (1, 16884, 1)     # every attempt of the chain costs
    assert got("seq4_restart", chain) == (1, 16884 + 2 * 16384 + 300, 2)
    assert got("seq4", chain) == (0, 2 * 16384 + 200, 4) and got("vote4_restart", chain) == (1, 16884 + 2 * 16384 + 300 + 200, 4)
    lng = [[a("7", 9000)], [a("1", 9000)], [a("1", 500)], [a("1", 12000)]]
    assert got("R8000", lng) == (1, 16500, 3) and got("R12000", lng) == (0, 9000, 1)
    assert got("seq4_L8000", lng) == (1, 16000 + 500 + 12000, 4)                                 # two abandoned at 8,000; the fourth runs in full
    assert F.outcome(F.RULES["seq4_L8000"], lng)["ran_out"] and not F.outcome(F.RULES["seq4_L12000"], lng)["ran_out"]
    assert got("seq4_L12000", lng) == (1, 18500, 3)
    assert got("seq4_stop1000", lng) == (1, 18500, 3) and got("seq4_stop1000", lng, (2, 0, 1, 3)) == (1, 500, 1)
    assert got("seq4_stop1000", [[a("7", 900)], [a("1")], [a("1")], [a("1")]]) == (0, 900, 1)   # a short wrong answer is accepted: must fail
    assert got("seq4_stop1000", [[a(None, 900)], [a("1", 2000)], [a("1", 2000)], [a("7")]]) == (1, 4900, 3)   # no answer: not accepted
    par = [[a("1", 3000)], [a("7", 100)], [a("1", 500)], [a("7", 4000)]]
    assert got("par4_m2", par) == (1, 3000 + 100 + 500 + 3000, 4)                               # 1 and 1 agree at 3,000; the fourth is cut there
    assert got("par4_m2", diff4) == got("vote4", diff4)

    def peek(chains):                                                                           # a rule that reads the score: rejected
        return {"answer": next(c[0]["id"] for c in chains if c[0]["score_v3"]), "tokens": 0, "drawn": 1, "ran_out": False}
    assert raises(lambda: F.outcome(peek, bad), KeyError)
    assert raises(lambda: F.outcome(lambda ch: ch[0][0]["gold"], bad), KeyError)
    assert all(set(r) == {"n_new", "cap_hit", "extracted_v3", "id"} for c in F.blind(bad) for r in c)

    per = {"cheap": {"s": [1, 0, 1, 0, 1] * 2, "t": [10.0] * 10}, "dear": {"s": [1] * 10, "t": [100.0] * 10}}
    assert F.choose(per, 50, list(range(10)), ["cheap", "dear"]) == "cheap" and F.choose(per, 100, list(range(10)), ["cheap", "dear"]) == "dear"
    assert F.choose(per, 5, list(range(10)), ["cheap", "dear"]) is None                         # nothing fits: no silent fallback
    assert raises(lambda: F.select({k: {**v, "s0": v["s"]} for k, v in per.items()}, 5, ["cheap", "dear"]), AssertionError)
    lo, hi = F.ratio_interval([2.0] * 10, [1.0] * 10)
    assert lo == hi == 2.0
    print("frontier_test: all planted cases pass")


if __name__ == "__main__":
    main()
