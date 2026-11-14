"""RLN-4 (studies/rlneurons/SPEC4.md): loop-onset detectors, grader mode v2, answer agreement, prefix encoding.
Standard library, zlib, n13_score (math-verify 0.9.0 lazily). Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import re
import zlib

from studies.rlneurons.lib import n13_score as S

# ------------------------------------------------------------------------------------------------ loop onset, rule A (ours)
# A loop is verified by a window of W characters, starting at a line start, whose zlib ratio is below THR (SPEC3's loop-ratio
# constants: 8,000 characters, 0.10). Its onset is the first line of the repeated block: from the first verified window's start,
# walk back over lines that recur inside that window (digits written as '#', stripped, at least MINLEN characters; blank lines
# pass), then forward to the first line that recurs. No verified window: no loop.
W, THR, MINLEN = 8000, 0.10, 8


def zratio(s: str):
    b = s.encode()
    return len(zlib.compress(b)) / len(b) if b else None


def _norm(line: str) -> str:
    return re.sub(r"\d+", "#", line.strip())


def _lines(text: str):
    out, c = [], 0
    for ln in text.split("\n"):
        out.append((c, ln))
        c += len(ln) + 1
    return out


def onset_lines(text: str):
    """Character offset of the loop onset (rule A), or None."""
    ls = _lines(text)
    k = next((k for k, (c, _) in enumerate(ls) if len(text) - c >= W and zratio(text[c:c + W]) < THR), None)
    if k is None:
        return None
    cstar = ls[k][0]
    rec = {_norm(l) for c, l in ls[k:] if c < cstar + W and len(_norm(l)) >= MINLEN}
    j = k
    while j > 0 and (_norm(ls[j - 1][1]) in rec or not ls[j - 1][1].strip()):
        j -= 1
    while j < len(ls) and _norm(ls[j][1]) not in rec:
        j += 1
    return ls[j][0]


# ------------------------------------------------------------------------------------------------ loop onset, rule B (published)
# arXiv 2611.06095 as relayed by the coordinator: a repeating suffix with period up to 64 characters, at least 2,000 characters and
# 3 cycles. Onset = the start of the longest such periodic suffix over the periods 1..64.
PMAX, MINRUN, CYCLES = 64, 2000, 3


def onset_period(text: str):
    n, best = len(text), None
    for p in range(1, PMAX + 1):
        k = n - 1 - p
        while k >= 0 and text[k] == text[k + p]:
            k -= 1
        run = n - (k + 1)
        if run >= MINRUN and run >= CYCLES * p and (best is None or k + 1 < best):
            best = k + 1
    return best


# ------------------------------------------------------------------------------------------------ grader mode v2
# v1 = n13_score.extract (registered, unchanged). v2 = v1; when v1 finds nothing, the last line that starts (after optional
# spaces) with "**Answer**:" or "**Answer:**", its rest stripped of one \( \) or $ $ pair.
V2_LABEL = re.compile(r" *(?:\*\*Answer\*\*:|\*\*Answer:\*\*)")


def _unwrap(s: str) -> str:
    s = s.strip()
    if s.startswith("\\(") and s.endswith("\\)"):
        s = s[2:-2].strip()
    elif s.startswith("\\[") and s.endswith("\\]"):
        s = s[2:-2].strip()
    return s


def extract_v2(text: str) -> tuple:
    mode, ext, span = S.extract(text)
    if mode != "none":
        return mode, ext, span
    hit = None
    for line in text.split("\n"):
        m = V2_LABEL.match(line)
        if m and _unwrap(line[m.end():]):
            hit = _unwrap(line[m.end():])
    return ("v2_label", hit, None) if hit is not None else ("none", None, None)


def grade_v2(gold: str, text: str) -> dict:
    mode, ext, _ = extract_v2(text)
    return {"mode_v2": mode, "extracted_v2": ext, "score_v2": S.grade(gold, ext)["score"]}


# ------------------------------------------------------------------------------------------------ grader v3 (SPEC4.md, "Grader v3")
# Candidates: every balanced \boxed{} and every answer marker (MARK_V3, anywhere in a line; the candidate is the rest of that line).
# The candidate that starts last in the text wins. A winning box takes the boxes before it that are separated from it only by
# commas, spaces, "and"/"or" and math delimiters, joined with ", ". The gold is never read during extraction.
MARK_V3 = re.compile(r"(?:[Ff]inal [Aa]nswer|Answer)(?:\*\*|\*|__)?\s*(?::|\bis\b)")
BOX_SEP_V3 = re.compile(r"[\s,;$()\[\]\\]*(?:(?:and|or)[\s,;$()\[\]\\]*)?")
SUP_V3 = dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-"))
TRAIL_V3 = re.compile(r"^(.*?[0-9)\]}])\s*(?:[A-Za-z]{3,}\s*)+\.?$")
WORD_V3 = re.compile(r"(?<![\\A-Za-z])[A-Za-z]{3,}")
DELIM_V3 = re.compile(r"\\[\[\]()]")
PMATRIX_V3 = re.compile(r"\\begin\{pmatrix\}([^&]*?)\\end\{pmatrix\}")
BRACKET3_V3 = re.compile(r"^\[([^\[\],]*,[^\[\],]*,[^\[\]]*)\]$")


def _boxes(text: str) -> list:
    out, i = [], text.find(S.BOXED)
    while i >= 0:
        depth, j = 1, i + len(S.BOXED)
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        if depth == 0:
            out.append((i, j, text[i + len(S.BOXED):j - 1]))
        i = text.find(S.BOXED, i + 1)
    return out


def extract_v3(text: str) -> tuple:
    """(mode, extracted string, start offset). Mode 'boxed', 'marker' or 'none'."""
    marks = []
    for m in MARK_V3.finditer(text):
        end = text.find("\n", m.end())
        rest = DELIM_V3.sub("", text[m.end():len(text) if end < 0 else end]).strip().strip("*_").strip()
        if rest:
            marks.append((m.end(), rest))
    boxes = _boxes(text)
    if boxes and (not marks or boxes[-1][0] > marks[-1][0]):
        k = len(boxes) - 1
        while k > 0 and BOX_SEP_V3.fullmatch(text[boxes[k - 1][1]:boxes[k][0]]):
            k -= 1
        items = []
        for b in boxes[k:]:
            if b[2].strip() not in items:
                items.append(b[2].strip())
        return "boxed", ", ".join(items), boxes[k][0]
    if marks:
        return "marker", marks[-1][1], marks[-1][0]
    return "none", None, None


def _sqrt_v3(s: str) -> str:
    s = re.sub(r"√(\d+(?:\.\d+)?|[A-Za-z]|\([^()]*\))", r"\\sqrt{\1}", s)
    return s.replace("√", "\\sqrt")


def norm_v3(s: str) -> str:
    """Normalization applied to the gold and to the extracted answer alike."""
    s = s.strip()
    s = re.sub("[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+", lambda m: "^{" + "".join(SUP_V3[c] for c in m.group()) + "}", s)
    s = _sqrt_v3(s.replace("∞", "\\infty").replace("−", "-"))
    s = PMATRIX_V3.sub(lambda m: "(" + ", ".join(e.strip() for e in m.group(1).split("\\\\") if e.strip()) + ")", s)
    s = BRACKET3_V3.sub(r"(\1)", s)
    t = TRAIL_V3.match(s)
    if t and re.search(r"\d", t.group(1)) and not WORD_V3.search(t.group(1)):
        s = t.group(1)
    return s


def grade_v3(gold: str, text: str) -> dict:
    mode, ext, _ = extract_v3(text)
    score = 0 if ext is None else S.grade(norm_v3(gold), norm_v3(ext))["score"]
    return {"mode_v3": mode, "extracted_v3": ext, "score_v3": score}


def agree(a, b) -> bool:
    """Two attempts' extracted answers agree when the grader's equivalence test (the function that compares to gold) says so."""
    if a is None or b is None:
        return False
    return S.grade(a, b)["score"] == 1


# ------------------------------------------------------------------------------------------------ prefix encoding
def encode_answer(tok, text: str, prefill_text: str, prefill_ids: list):
    """Token ids and character offsets of a saved answer text. The saved records hold text, not ids, so ids are re-tokenized; an
    answer that starts with the opening keeps the opening's three sampled ids (re-tokenizing splits '!\\n\\n')."""
    if text.startswith(prefill_text):
        e = tok(text[len(prefill_text):], add_special_tokens=False, return_offsets_mapping=True)
        n = len(prefill_text)
        assert tok.decode(prefill_ids) == prefill_text and [len(tok.decode([i])) for i in prefill_ids] == [5, 3, 4]
        return list(prefill_ids) + e["input_ids"], [(0, 5), (5, 8), (8, n)] + [(a + n, b + n) for a, b in e["offset_mapping"]]
    e = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    return e["input_ids"], [tuple(x) for x in e["offset_mapping"]]


def tokens_before(offsets, char: int) -> int:
    return sum(1 for a, b in offsets if b <= char)


def selfcheck():
    assert agree("5.5", "\\dfrac{11}{2}") and agree("$x = 2$", "2") and not agree("5.5", "\\frac{11}{3}")
    assert extract_v2("work\n**Answer**: \\(123_4\\)")[:2] == ("v2_label", "123_4")
    assert extract_v2("**Answer:** 7")[:2] == ("answer_line", "7")             # v1 already reads this one
    assert extract_v2("x\n  **Answer:** \\( \\frac{1}{2} \\) now")[0] == "answer_line"   # v1 line rule wins when it fires
    assert extract_v2("no label")[0] == "none" and extract_v2("Answer: 3")[:2] == ("answer_line", "3")
    loop = "Start.\n" + "Wait, let me check the sum of the angles again.\nSo x is 5.\n" * 300
    o = onset_lines(loop)
    assert o == len("Start.\n"), o
    assert onset_lines("Some ordinary text without repeats.\n" + "".join(f"line {i} {i*i} {i**3}\n" for i in range(50))) is None
    assert onset_period("abc" + "xy" * 1500) == 3 and onset_period("ab" * 900) is None
    return True
