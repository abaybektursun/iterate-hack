"""Checks for analysis/fallback.py (specs/SPEC_fallback.md), from the committed rows only: the posted control numbers, planted
late answers on which a rule must and must not differ from the controls, and hand-built problems.

    uv run --no-project --with numpy --with math-verify==0.9.0 --with tokenizers python -m studies.rlneurons.analysis.fallback_test
"""
import functools

from studies.rlneurons.analysis import fallback as FB
from studies.rlneurons.lib import rln4_lib as R


def s(ans, n_new=1000, right="1", switched=False):
    """One sample; an answer past 16,384 has no ballot in the 16,384 view."""
    late = n_new > FB.OLD
    return {"extracted_v3": ans, "score_v3": int(ans == right), "n_new": n_new, "cap_hit": False, "switched": switched,
            "extracted_v3_16": None if late else ans, "score_v3_16": 0 if late else int(ans == right), "n_new_16": min(n_new, FB.OLD), "cap_hit_16": late}


def plant(prob: dict, right: bool) -> dict:
    """Every late answer made right (the gold) or wrong (an answer of its own)."""
    return {i: [{**x, "extracted_v3": x["gold"] if right else f"99999{i}{x['sample']}", "score_v3": int(right)} if FB.late(x) else x for x in v] for i, v in prob.items()}


def main():
    R.agree, R.norm_v3 = functools.lru_cache(maxsize=None)(R.agree), functools.lru_cache(maxsize=None)(R.norm_v3)
    for name in FB.ROWS:
        prob = FB.load_rows(name)
        print(name, "posted controls reproduced:", FB.controls(name, prob))
        wrong, right = plant(prob, False), plant(prob, True)
        for i in prob:
            no16 = all(x["extracted_v3_16"] is None for x in prob[i])
            for p in FB.ORDERS:
                w, r = [wrong[i][k] for k in p], [right[i][k] for k in p]
                assert FB.r1(w) == FB.r5(w)                                                                                   # late always wrong: R1 is the 16,384 vote
                if no16 and any(FB.late(x) for x in prob[i]):
                    assert FB.r1(w) == 0 and FB.r1(r) == 1 and FB.r1(r) >= FB.r4(r)                                           # late always right: the fallback takes them
        # the plant must be able to fail: with late answers always right the plain vote beats the 16,384 vote somewhere, and R1 follows it only without a 16,384 ballot
        assert sum(FB.r4(v) for v in right.values()) > sum(FB.r5(v) for v in right.values())
        assert any(FB.r1(v) < FB.r4(v) for v in right.values()), "R1 never ignores a right late answer: the plant does not bite"

    e, l = 1000, 20000
    assert FB.r1([s("7", l), s("1", e), s("8", l), s("9", l)]) == 1 and FB.r4([s("7", l), s("1", e), s("8", l), s("9", l)]) == 0    # one early right against three late
    assert FB.r1([s("7", e), s("1", l), s("1", l), s("1", l)]) == 0 and FB.r4([s("7", e), s("1", l), s("1", l), s("1", l)]) == 1    # R1 must fail: early wrong, three late right
    assert FB.r1([s("7", l), s("1", l), s("1", l), s("8", l)]) == 1 and FB.r5([s("7", l), s("1", l), s("1", l), s("8", l)]) == 0    # no early ballot: the plain vote
    assert FB.r2([s("7", l), s("1", e)]) == 1 and FB.r2([s("7", l), s("8", l), s("9", l), s("1", e)]) == 1                          # 1 against 0.5 each
    assert FB.r2([s("7", l), s("7", l), s("1", e)]) == 0 and FB.r2([s("1", e), s("7", l), s("7", l)]) == 1                          # 1 against 1: first seen
    assert FB.r2([s("7", l), s("7", l), s("7", l), s("1", e)]) == 0                                                                 # 1.5 against 1: R2 must fail
    sw = lambda a: s(a, l, switched=True)
    assert FB.r3([sw("7"), sw("7"), s("1", l), s("8", l)]) == 1 and FB.r1([sw("7"), sw("7"), s("1", l), s("8", l)]) == 0            # switched ballots dropped
    assert FB.r3([sw("7"), sw("7"), sw("1"), sw("1")]) == 0 and FB.r3([sw("1"), sw("1"), sw("7"), sw("7")]) == 1                    # all switched: the plain vote
    assert FB.r3([sw("1"), s("7", e)]) == 0                                                                                         # an early ballot wins before the fallback
    assert FB.r6([s("7", l), s("1", e), s("8", l), s("9", l)], [True, False, True, True]) == 1                                      # real flags: R1
    assert FB.r6([s("7", l), s("1", e), s("8", l), s("9", l)], [False, True, True, True]) == 0                                      # permuted flags: the late 7 wins

    a4 = [s("1", 100), s("1", 200), s("7", 400), s("8", 800)]
    assert FB.seqfb_resume(a4) == (1, 300) == FB.seq4(a4, 16) and FB.seqfb_online(a4) == (1, 300)                                   # two early agree: seq4's cost
    none = [s("7", l), s("1", l + 5), s("1", l + 10), s("8", l)]
    assert FB.seq4(none, 16) == (0, 4 * FB.OLD) and FB.seqfb_resume(none) == (1, 4 * FB.OLD + (l - FB.OLD) * 3 + 15)                # resumed 3, two agree
    assert FB.seqfb_online(none) == (1, 4 * l + 15)                                                                                 # no resuming: all four run to the end
    one = [s("7", l), s("1", e), s("1", l), s("1", l)]
    assert FB.seqfb_online(one) == (1, l + e + 2 * FB.OLD) and FB.seqfb_resume(one) == (1, 3 * FB.OLD + e)                          # after an early ballot, samples stop at 16,384
    assert FB.seq4_half(a4) == (1, 300) and FB.seq4_half(none) == (1, 4 * l + 15)                                                   # two late agree: weight 1, all four drawn
    assert FB.seq4_half([s("7", l), s("7", l), s("1", e), s("1", e)]) == (1, 2 * l + 2 * e)                                         # seq4 at 32,768 stops at the late pair: wrong
    assert FB.seq4([s("7", l), s("7", l), s("1", e), s("1", e)], 32) == (0, 2 * l)
    print("fallback_test: all checks pass")


if __name__ == "__main__":
    main()
