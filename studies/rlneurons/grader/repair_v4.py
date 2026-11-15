"""Grader v4 = grader v3 plus five label-free answer-statement rules (specs/SPEC_repair.md, "Part A (b)"). A grader version:
it changes extraction and normalization for every model alike and never reads the gold. rln4_lib.grade_v3 is unchanged.

    R1 placeholder     the v3 answer is a placeholder ('$Answer$'): the candidate before it, within 5 non-empty lines
    R2 lower-case mark nothing extracted: the rest of the last line after 'answer:' / 'answer is', any case
    R3 last-line math  nothing extracted, answer ended with the stop token: the last math span of the last line
    R4 trailing brace  more '}' than '{' in the extracted string: '}' removed from its end
    R5 form            '(C) Plane' -> 'C'; '12th grade' -> '12'

Fail loud: no try/except.
"""
from __future__ import annotations

import re

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

RULES = ("R1", "R2", "R3", "R4", "R5")
PLACEHOLDERS = {"", "answer", "youranswer", "finalanswer", "theanswer", "textanswer", "boxedanswer"}
JUNK = re.compile(r"[\s$*_.:\\()\[\]{}<>]")
MARK_ANY = re.compile(r"(?i:answer)(?:\*\*|\*|__)?\s*(?::|\bis\b)")
SPAN = re.compile(r"\$\$(.+?)\$\$|(?<!\\)\$(.+?)(?<!\\)\$|\\\((.+?)\\\)|\\\[(.+?)\\\]")
WINDOW, MAXLINE = 5, 30
CHOICE = re.compile(r"^\(?([A-E])\)\s+\S.*$")
ORDINAL = re.compile(r"^(\d+)(?:st|nd|rd|th)\b\D*$")


def unusable(ext) -> bool:
    return ext is None or JUNK.sub("", ext).lower() in PLACEHOLDERS


def _window_start(text: str, pos: int) -> int:
    """Offset of the first of the WINDOW non-empty lines that end with the line holding pos."""
    start, seen = 0, 0
    line_start = text.rfind("\n", 0, pos) + 1
    while True:
        end = text.find("\n", line_start)
        if text[line_start:len(text) if end < 0 else end].strip():
            seen += 1
            start = line_start
        if seen == WINDOW or line_start == 0:
            return start
        line_start = text.rfind("\n", 0, line_start - 1) + 1


def _r1(text: str, start: int):
    lo, cut = _window_start(text, start), start
    while True:
        mode, ext, s = R.extract_v3(text[:cut])
        if ext is None or s < lo:
            return "none", None
        if not unusable(ext):
            return mode, ext
        cut = s


def _r2(text: str):
    hit = None
    for m in MARK_ANY.finditer(text):
        end = text.find("\n", m.end())
        rest = R.DELIM_V3.sub("", text[m.end():len(text) if end < 0 else end]).strip().strip("*_").strip()
        if not unusable(rest):
            hit = rest
    return hit


def _r3(text: str):
    lines = [l for l in text.split("\n") if re.search(r"[A-Za-z0-9]", l)]
    if not lines:
        return None
    spans = [next(g for g in m.groups() if g is not None).strip() for m in SPAN.finditer(lines[-1])]
    if spans:
        return None if unusable(spans[-1]) else spans[-1]
    s = lines[-1].strip(" *_#\t")
    s = s[:-1] if s.endswith(".") else s
    return s if len(s) <= MAXLINE and re.search(r"\d", s) and not unusable(s) else None


def _r4(s: str) -> str:
    n = lambda c: len(re.findall(r"(?<!\\)" + re.escape(c), s))
    while n("}") > n("{") and s.rstrip().endswith("}") and not s.rstrip().endswith("\\}"):
        s = s.rstrip()[:-1]
    return s.rstrip()


def _r5(s: str) -> str:
    m = CHOICE.match(s.strip()) or ORDINAL.match(s.strip())
    return m.group(1) if m else s


def extract_v4(text: str, finish_reason: str, rules=RULES) -> tuple:
    """(mode, extracted string, rules that changed the v3 result). finish_reason is the stored field ('stop' or 'length')."""
    mode, ext, start = R.extract_v3(text)
    fired = []
    if "R1" in rules and ext is not None and unusable(ext):
        mode, ext = _r1(text, start)
        fired.append("R1")
    if "R2" in rules and ext is None and _r2(text) is not None:
        mode, ext = "lower_marker", _r2(text)
        fired.append("R2")
    if "R3" in rules and ext is None and finish_reason == "stop" and _r3(text) is not None:
        mode, ext = "last_line", _r3(text)
        fired.append("R3")
    if ext is not None:
        for name, f in (("R4", _r4), ("R5", _r5)):
            if name in rules and f(ext) != ext:
                ext = f(ext)
                fired.append(name)
    return mode, ext, fired


def grade_v4(gold: str, text: str, finish_reason: str, rules=RULES) -> dict:
    mode, ext, fired = extract_v4(text, finish_reason, rules)
    score = 0 if ext is None else S.grade(R.norm_v3(gold), R.norm_v3(ext))["score"]
    return {"mode_v4": mode, "extracted_v4": ext, "score_v4": score, "fired_v4": fired}
