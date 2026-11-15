"""Outside math and code (specs/SPEC_ood1.md): the problem text and the grader for multiple-choice items of MMLU-Pro and BBH.

The prompt is the study's unchanged math prompt (n13_score.TEMPLATE["pair1"], which does not name math) around content().
The answer is the first option letter after the last "Answer:" of the completion; a completion with no "Answer:" or no
letter after it is wrong. No model, no network: importable on the laptop."""
from __future__ import annotations

import re

LETTERS = "ABCDEFGHIJKLMNOPQR"
MARK = re.compile(r"Answer\s*:", re.IGNORECASE)
LETTER = re.compile(r"(?<![A-Za-z])([A-R])(?![A-Za-z])")


def content(question: str, options: list | None) -> str:
    """What the template wraps. MMLU-Pro: the question and its lettered options. BBH: the input as it is (it lists its options)."""
    q = question.strip()
    if options:
        q += "\n\nOptions:\n" + "\n".join(f"({LETTERS[i]}) {o}" for i, o in enumerate(options))
    return q + "\n\nThe answer is the letter of the correct option."


def extract(text: str) -> tuple:
    """(mode, letter): mode "answer" = a letter after the last "Answer:"; "no_letter" = an "Answer:" with no option letter after
    it; "none" = no "Answer:". The letter is None unless mode is "answer"."""
    marks = list(MARK.finditer(text))
    if not marks:
        return "none", None
    m = LETTER.search(text[marks[-1].end():])
    return ("answer", m.group(1)) if m else ("no_letter", None)


def grade(text: str, gold: str, n_options: int) -> dict:
    assert gold in LETTERS[:n_options], (gold, n_options)
    mode, letter = extract(text)
    return {"mode": mode, "letter": letter, "right": letter == gold}


# Grader v2 (SPEC_ood1.md amendment 1): v1 misses answers written as "**Answer**: C", "The answer is (D)" or "\boxed{C}".
MARK_V2 = re.compile(r"answer\W{0,4}:|answer is(?! the letter of)|\\boxed\{", re.IGNORECASE)


def extract_v2(text: str) -> tuple:
    """(mode, letter): the first option letter within 40 characters after the last of "Answer:" (markup allowed between the
    word and the colon), "answer is" and "\\boxed{". Modes as in extract()."""
    marks = list(MARK_V2.finditer(text))
    if not marks:
        return "none", None
    m = LETTER.search(text[marks[-1].end():marks[-1].end() + 40])
    return ("answer", m.group(1)) if m else ("no_letter", None)


def grade_v2(text: str, gold: str, n_options: int) -> dict:
    assert gold in LETTERS[:n_options], (gold, n_options)
    mode, letter = extract_v2(text)
    return {"mode": mode, "letter": letter, "right": letter == gold}
