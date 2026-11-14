"""Grader v3 checks (studies/rlneurons/SPEC4.md, "Grader v3"). Plain asserts; run with math-verify 0.9.0 installed:

    python -m studies.rlneurons.grader.rln4_grader_v3_test

Registered failing inputs: the 22 audited saved answers in rln4/grader_v3/cases.json are wrong under v2 and must be right under
v3. Negative cases must stay wrong under v3. Fail loud: no try/except.
"""
import json
import pathlib

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

CASES = pathlib.Path(__file__).resolve().parent / "cases.json"

# (gold, text) pairs that v3 must score right (format and marker cases written by hand, plus two regressions from the first draft)
RIGHT = [
    ("\\$36", "Answer: $36.00"),                                                    # money with cents, already right under v1
    ("3", "So r = 3.\n\n**Answer:** The radius of the sphere is 3 units."),          # sentence ending in a period (draft bug)
    ("6", "so \\(\\boxed{\\mathrm{6}}\\).\n\n   \\[Answer:\\mathrm{6}\\]"),            # marker inside \[ \] (draft bug)
    ("(-\\infty, 2]", "**Answer:** (-∞, 2]"),
    ("2\\sqrt{3}", "Answer: 2√3"),
    ("-2,1", "the roots are \\(\\boxed{1}\\) and \\(\\boxed{-2}\\)."),
    ("\\begin{pmatrix} 1 \\\\ 2 \\\\ 3 \\end{pmatrix}", "\\boxed{\\begin{pmatrix} 1 \\\\ 2 \\\\ 3 \\end{pmatrix}}"),
]
# (gold, text, why) pairs that v3 must score wrong
WRONG = [
    ("\\frac{16}{27}", "**Answer:** 15/27 gallons.", "wrong number followed by units"),
    ("72", "Answer: 71 degrees", "wrong number followed by units"),
    ("12", "First we get 12.\nAnswer: 12\nWait, that misses a case.\n\\boxed{14}", "correct intermediate, different final box"),
    ("12", "So x = 12 at first. Rechecking, x = 14.\n\nThe final answer is 14.", "correct intermediate, different final marker"),
    ("12", "Answer: 112", "gold only as a substring"),
    ("12", "\\boxed{112}", "gold only as a substring"),
    ("x = 2, 3", "Answer: x = 2", "one root of two"),
    ("3, 5", "\\boxed{3} is wrong; the correct value is \\boxed{5}", "boxes separated by words are not joined"),
    ("2", "Answer: 2xy", "two-letter tail is not cut"),       # ("2ab" is not used: math-verify itself reads it as 2, under v1 too)
    ("5", "no answer given", "nothing extracted"),
]


def run():
    assert S.selfcheck() and R.selfcheck()                     # v1 and v2 unchanged
    cases = json.loads(CASES.read_text())
    assert len(cases) == 22, len(cases)
    for c in cases:
        v2 = R.grade_v2(c["gold"], c["text"])["score_v2"]
        g3 = R.grade_v3(c["gold"], c["text"])
        assert v2 == 0, (c["cell"], c["problem_index"], "v2 already right")
        assert g3["score_v3"] == 1, (c["cell"], c["problem_index"], g3)
    for gold, text in RIGHT:
        assert R.grade_v3(gold, text)["score_v3"] == 1, (gold, text, R.grade_v3(gold, text))
    for gold, text, why in WRONG:
        assert R.grade_v3(gold, text)["score_v3"] == 0, (why, gold, text, R.grade_v3(gold, text))
    eq = [S.grade(R.norm_v3(g), R.norm_v3(x))["score"] for g, x in S.PLANTED_EQ]
    neq = [S.grade(R.norm_v3(g), R.norm_v3(x))["score"] for g, x in S.PLANTED_NEQ]
    assert sum(eq) == len(eq) and sum(neq) == 0, (eq, neq)
    return {"audited_rows": len(cases), "right_cases": len(RIGHT), "wrong_cases": len(WRONG), "planted_eq": len(eq), "planted_neq": len(neq)}


if __name__ == "__main__":
    print(run())
