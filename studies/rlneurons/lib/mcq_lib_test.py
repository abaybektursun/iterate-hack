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


def main():
    for text, gold, right in CASES:
        g = M.grade(text, gold, 18)
        assert g["right"] == right, (text, gold, g)
    assert M.content("Q?", ["x", "y"]) == "Q?\n\nOptions:\n(A) x\n(B) y\n\nThe answer is the letter of the correct option."
    print(f"{len(CASES)} cases ok")


if __name__ == "__main__":
    main()
