"""Cases the grader of mcq_lib must get right, wrong answers included.  python3 -m studies.rlneurons.lib.mcq_lib_test"""
from studies.rlneurons.lib import mcq_lib as M

CASES = [  # (completion, gold, right)
    ("Okay, so ... therefore B.\n\nAnswer: B", "B", True),
    ("thinking\nAnswer: (C)", "C", True),
    ("Answer: A\nwait, no.\nAnswer: D", "D", True),            # the last "Answer:" counts
    ("Answer: A\nwait, no.\nAnswer: D", "A", False),
    ("**Answer:** (J) none of the above", "J", True),
    ("Answer: $\\boxed{E}$", "E", True),
    ("answer: b", "B", False),                                   # a lower-case letter is not an option letter
    ("The correct option is B.", "B", False),                    # no "Answer:"
    ("Answer: I think it is unclear", "I", True),                # known weakness: a capital pronoun reads as option I
    ("Answer: 42", "A", False),
    ("Answer: And so on", "A", False),                           # a letter inside a word is not an answer
    ("Answer: C", "B", False),
]


CASES_V2 = [  # (completion, gold, right) for grade_v2; every case of CASES but the "no Answer:" one must also hold
    ("So D is the answer.\n\nThe answer is (D)", "D", True),
    ("**Answer**: $\\boxed{C}$", "C", True),
    ("as 25% will be bb.\n\n\\boxed{C}", "C", True),
    ("**Final Answer**: \\boxed{A}", "D", False),
    ("**Answer:** $\\boxed{HI}$", "H", False),                    # two letters are not an answer
    ("the answer is that the extra chromosome has no effect on Beauty", "B", False),
    ("The answer is the letter of the correct option.", "A", False),
    ("Answer: B\n\nlater \\boxed{E}", "B", False),              # the last marker counts
    ("no marker at all, option B", "B", False),
    ("So the answer is B.\n\nThe answer is the letter of the correct option.", "B", True),   # the prompt's own sentence is no marker
]


def main():
    for text, gold, right in CASES:
        g = M.grade(text, gold, 18)
        assert g["right"] == right, (text, gold, g)
        if "correct option is" not in text:
            assert M.grade_v2(text, gold, 18)["right"] == right, ("v2", text, gold)
    for text, gold, right in CASES_V2:
        g = M.grade_v2(text, gold, 18)
        assert g["right"] == right, ("v2", text, gold, g)
    assert M.content("Q?", ["x", "y"]) == "Q?\n\nOptions:\n(A) x\n(B) y\n\nThe answer is the letter of the correct option."
    print(f"{len(CASES)} v1 and {len(CASES_V2)} v2 cases ok")


if __name__ == "__main__":
    main()
