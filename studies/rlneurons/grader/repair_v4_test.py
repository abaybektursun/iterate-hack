"""Grader v4 checks (specs/SPEC_repair.md, "Planted tests"). Plain asserts:

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.grader.repair_v4_test

A wrong answer must stay wrong under every rule alone and under v4; each rule must turn one planted right answer that v3
scores wrong into right; the audited rows of v3 stay right. Fail loud: no try/except.
"""
import json

from studies.rlneurons.grader import repair_v4 as G
from studies.rlneurons.grader import rln4_grader_v3_test as T3
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

FAR = "\n".join(f"Step {i}: more work here." for i in range(6))
# (gold, text, finish_reason, why): must be wrong under every rule set
WRONG = [(g, t, "stop", w) for g, t, w in T3.WRONG] + [(g, "Answer: " + x, "stop", "planted unequal pair") for g, x in S.PLANTED_NEQ] + [
    ("7", "So the total is \\boxed{4}.\n\nAnswer: $Answer$", "stop", "placeholder after a boxed wrong value"),
    ("7", "First, \\boxed{7}.\n" + FAR + "\nAnswer: $Answer$", "stop", "placeholder, the only box more than 5 lines above"),
    ("12", "We get $x = 12$.\nThen adding 3 gives $x + 3 = 15$", "stop", "last line holds another value than the gold"),
    ("12", "We compute and the total is $12$", "length", "cap hit: R3 must not fire"),
    ("12", "Answer: 112}", "stop", "trailing brace on a wrong number"),
    ("\\text{(C)}", "Answer: (B) Line", "stop", "wrong choice letter with words"),
    ("12", "Answer: 21st grade", "stop", "wrong ordinal"),
    ("12", "The total number of students is twelve (12) in all", "stop", "last line over 30 characters, no math"),
    ("12", "the answer is 14", "stop", "lower-case marker with a wrong value"),
    ("5", "Answer: $Answer$", "stop", "placeholder only"),
    ("5", "no answer given", "stop", "nothing to extract"),
]
# (gold, text, finish_reason, rule): wrong under v3, right under v3 + the rule and under v4
RIGHT = [
    ("7", "So the total is \\boxed{7}.\n\nAnswer: $Answer$", "stop", "R1"),
    ("14", "Adding up all of the five parts, the answer is 14", "stop", "R2"),
    ("12", "Adding the two parts gives $5 + 7 = 12$", "stop", "R3"),
    ("12", "**Result**\n\n12.", "stop", "R3"),
    ("\\text{Evelyn}", "Answer: Evelyn}", "stop", "R4"),
    ("\\text{(C)}", "Answer: (C) Plane", "stop", "R5"),
    ("12", "Answer: 12th grade", "stop", "R5"),
]
# Known limit (asserted so that it is visible): a gold-equal intermediate value where the fallback looks, then another final
# answer that no rule extracts. v4 scores these right although the model's last statement is not the gold.
LIMIT = [
    ("12", "First \\boxed{12}.\nBut that misses a case, the result is fifteen.\n\nAnswer: $Answer$", "stop"),
    ("12", "So we get fifteen, which differs from the first guess $12$", "stop"),
]


# Known miss: the value stands on its own line before a placeholder line, without a box or a marker. No rule reads it.
MISS = [("7", "**Final Answer**\n$7$\n\nAnswer: $\\text{Answer}$", "stop")]


# v4a only (the amendment): wrong under v4a, and accepted by v4 as first written (asserted, so the reason for v4a is visible)
WRONG_A = [
    ("12", "So the answer is 12. But how?\nThe other count gives fifteen. Let me redo the whole computation from", "length"),
    ("12.5", "So the answer is 12.5. Let me verify. 6.2 + 6.3 equals 12.5. So the answer should be 12.5.\n\n\n15.5", "stop"),
]


def run():
    T3.run()                                                         # v3 unchanged
    sets = [(r,) for r in G.RULES] + [G.RULES]
    cases = json.loads(T3.CASES.read_text())
    for c in cases:                                                  # audited v3 rows stay right under v4
        assert G.grade_v4(c["gold"], c["text"], "stop")["score_v4"] == 1, (c["cell"], c["problem_index"])
    for gold, text, fin, why in WRONG:
        for rules in sets:
            g = G.grade_v4(gold, text, fin, rules)
            assert g["score_v4"] == 0, (why, rules, g)
    for gold, text, fin, rule in RIGHT:
        assert R.grade_v3(gold, text)["score_v3"] == 0, (rule, text)
        for rules in ((rule,), G.RULES):
            g = G.grade_v4(gold, text, fin, rules)
            assert g["score_v4"] == 1 and rule in g["fired_v4"], (rule, rules, g)
        others = [r for r in G.RULES if r != rule]
        assert G.grade_v4(gold, text, fin, others)["score_v4"] == 0, (rule, "another rule also repairs this case")
    for gold, text, fin in LIMIT:
        assert G.grade_v4(gold, text, fin)["score_v4"] == 1, text
    for gold, text, fin in WRONG_A:
        assert G.grade_v4(gold, text, fin)["score_v4"] == 1 and G.grade_v4(gold, text, fin, amended=True)["score_v4"] == 0, text
    for gold, text, fin, why in WRONG:
        assert G.grade_v4(gold, text, fin, amended=True)["score_v4"] == 0, (why, "v4a")
    for gold, text, fin, rule in RIGHT:
        assert G.grade_v4(gold, text, fin, amended=True)["score_v4"] == 1, (rule, "v4a")
    for c in cases:
        assert G.grade_v4(c["gold"], c["text"], "stop", amended=True)["score_v4"] == 1, (c["cell"], c["problem_index"])
    for gold, text, fin in MISS:
        g = G.grade_v4(gold, text, fin)
        assert g["score_v4"] == 0 and g["extracted_v4"] is None, g
    return {"audited_rows": len(cases), "wrong_cases": len(WRONG), "rule_sets": len(sets), "right_cases": len(RIGHT), "limit_cases": len(LIMIT), "wrong_v4a_only": len(WRONG_A)}


if __name__ == "__main__":
    print(run())
