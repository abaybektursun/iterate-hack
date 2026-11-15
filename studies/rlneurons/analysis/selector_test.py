"""Planted cases for analysis/selector.py (specs/SPEC_selector.md), including inputs on which a rule must pick the wrong sample.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.selector_test
"""
from studies.rlneurons.analysis import selector as L

BOX = "\\boxed{%s}"


def s(ans, n_new=1000, cap=False, aprob=0.5, mlp=-0.3, text=None, right="1"):
    """One sample; the right answer is `right`."""
    return {"extracted_v3": ans, "score_v3": int(ans == right), "n_new": n_new, "cap_hit": cap, "answer_prob": None if ans is None else aprob,
            "mean_logprob": mlp, "mode_v3": "none" if ans is None else "boxed", "text": text if text is not None else ("work " + BOX % ans if ans else "work"),
            "gold": right, "prompt": "p", "sample": 0}


def got(name, rows):
    return L.pick(rows, L.RULES[name])


def main():
    tie = [s("7", 900), s("1", 500), s("7", 800), s("1", 2000)]                     # 2-2 tie, the right group holds the shortest sample
    assert got("vote", tie) == (0, 0) and got("tie_short", tie) == (1, 1)
    bad = [s("7", 300), s("1", 500), s("7", 800), s("1", 2000)]                     # the shortest sample is wrong: tie_short must fail
    assert got("tie_short", bad) == (0, 0) and got("short1", bad) == (0, 0)
    assert got("tie_short", [s("7", 300, cap=True), s("1", 500)]) == (1, 1)         # a cap hit is never the shortest
    assert got("tie_short", [s("1"), s("7", 10), s("1")]) == (0, 1)                 # no tie: the plurality stands
    conf = [s("7", aprob=0.9, mlp=-0.1), s("1", aprob=0.6, mlp=-0.2), s("1", aprob=0.6, mlp=-0.2)]   # the confident sample is wrong
    assert got("max_aprob", conf) == (0, 0) and got("max_mlp", conf) == (0, 0) and got("tie_aprob", conf) == (1, 1)
    assert got("w_aprob", conf) == (1, 1)                                           # 1.2 against 0.9
    assert got("w_aprob", [s("7", aprob=0.9), s("1", aprob=0.4), s("1", aprob=0.4)]) == (0, 0)       # 0.9 against 0.8: must fail
    t2 = [s("7", aprob=0.9, mlp=-0.5), s("1", aprob=0.2, mlp=-0.1)]
    assert got("tie_aprob", t2) == (0, 0) and got("tie_mlp", t2) == (1, 1)
    assert got("w_invlen", [s("7", 100), s("1", 300), s("1", 300)]) == (0, 0)       # 1/100 against 2/300
    assert got("w_invlen", [s("7", 100), s("1", 150), s("1", 150)]) == (1, 1)
    cap = [s("7", 16384, cap=True), s("7", 16384, cap=True), s("1")]                # two cap hits outvote one finished sample
    assert got("vote", cap) == (0, 0) and got("drop_cap", cap) == (2, 1)
    assert got("drop_cap", [s("7", cap=True), s(None)]) == (0, 0)                   # only cap hits answered: the vote stands
    assert got("short1", [s("7", 50, cap=True), s(None, 10), s("1", 900), s("7", 950)]) == (2, 1)
    dirty = [s("7", text="so " + BOX % "7" + " and then " + "more text " * 40), s("1")]
    assert L.clean(dirty[0]) == 0 and L.clean(dirty[1]) == 1 and got("tie_clean", dirty) == (1, 1)
    assert got("tie_clean", [s("7"), s("1", text=BOX % "1" + "x" * 300)]) == (0, 0)  # the right sample is the dirty one: must fail
    rs = [s("7", text="7 " + BOX % "7"), s("1", text="1 and 1 so 1 " + BOX % "1")]
    assert got("tie_restate", rs) == (1, 1) and got("tie_restate", rs[::-1]) == (0, 1)
    assert got("tie_restate", [s("7", text="7 7 7 " + BOX % "7"), s("1")]) == (0, 0)
    assert got("vote", [s(None), s(None)]) == (None, 0) and got("short1", [s(None), s(None)]) == (None, 0)

    # cv_pick: a rule that is right only on fold 0 must not be chosen for fold 0; a rule that is right everywhere is chosen everywhere
    n = 50
    per = {"vote": [1 if j % 2 else 0 for j in range(n)], "fold0": [int(j % 5 == 0) for j in range(n)]}
    out, chosen = L.cv_pick(per)
    assert chosen[0] == "vote" and out == per["vote"], chosen
    out, chosen = L.cv_pick({**per, "oracle": [1] * n})
    assert chosen == ["oracle"] * 5 and sum(out) == n
    out, chosen = L.cv_pick({"vote": [1] * n, "same": [1] * n})                     # a draw keeps the vote
    assert chosen == ["vote"] * 5

    # readout: a planted rule that reads the score reaches pass@4 through cv_pick; a rule that reads the inverted score falls below the vote
    first = {i: [s("7", 100 + i), s("1" if i % 3 else "7", 500), s("7" if i % 2 else "1", 800), s(None, 16384, cap=True)] for i in range(60)}
    rules = {"vote": L.RULES["vote"], "tie_short": L.RULES["tie_short"],
             "oracle": lambda rows, groups: max((k for g in groups for k in g), key=lambda k: (rows[k]["score_v3"], -k)),
             "anti": lambda rows, groups: min((k for g in groups for k in g), key=lambda k: (rows[k]["score_v3"], k))}
    res = L.readout(first, rules)
    assert res["rows"]["oracle"]["right"] == res["pass_at_4"]["right"] == res["rows"]["cv_pick"]["right"] == 50, res["rows"]["oracle"]
    assert res["rows"]["anti"]["right"] == 0 and res["rows"]["anti"]["minus_vote_interval95"][1] < 0
    assert res["rows"]["oracle"]["minus_vote_interval95"][0] > 0 and res["rows"]["vote"]["minus_vote_interval95"] == (0.0, 0.0)
    assert res["rows"]["tie_short"]["right"] == res["rows"]["vote"]["right"]         # sample 0 is always the shortest and wrong
    assert res["rows"]["vote"]["tokens_per_problem"] == sum(r["n_new"] for v in first.values() for r in v) / 60
    print("selector_test: all planted cases pass")


if __name__ == "__main__":
    main()
