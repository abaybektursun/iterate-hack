"""r4-m11 prediction 5: among finished T1 answers (cap_hit false) with a first marker, kept when the text after the end of the
first marker is longer than 300 characters and contains another marker, the fraction with v3_last == 0.

Main (literal): first marker as in p1. End of first marker: for an 'Answer:' line the end of that line (the position of its
newline, so the text after starts with that newline) or the end of text; for '\\boxed{' the position just after its matching
closing brace (an unclosed first box ends at the end of text). Another marker = a line that starts at or after the end and whose
left-stripped text begins 'Answer:', or any '\\boxed{' at or after the end.
Alt: first marker and further markers under grader v3's own candidate set (MARK_V3 anywhere with non-empty rest, balanced boxes).
No kept rows -> refuted without a number.
"""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R

ROOT = pathlib.Path.cwd()
T1 = ROOT / "runs/theory-tests/s3/T1.jsonl"
T1_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"
BOX = "\\boxed{"


def emit(measured, met, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": met, "alt_measured": alt, "not_computable": nc, "example_row": ex},
                     ensure_ascii=False))


def fetch_s3(uri, dest):
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", uri, str(dest), "--profile", "iterate-ecr"], capture_output=True)
    return dest.exists() and dest.stat().st_size > 0


def answer_lines(text, from_pos=0):
    """(start of 'Answer:', content after 'Answer:', end of line) for lines starting at or after from_pos whose
    left-stripped text begins with 'Answer:'."""
    pos = 0
    for line in text.split("\n"):
        ls = line.lstrip()
        if pos >= from_pos and ls.startswith("Answer:"):
            yield pos + len(line) - len(ls), ls[len("Answer:"):], pos + len(line)
        pos += len(line) + 1


def first_box(text, from_pos=0):
    i = text.find(BOX, from_pos)
    if i < 0:
        return None
    depth, j = 1, i + len(BOX)
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    if depth == 0:
        return i, text[i + len(BOX):j - 1], j
    return i, text[i + len(BOX):], len(text)


def first_marker(text):
    """Literal reading: (start, content, end) of the earliest 'Answer:' line or first '\\boxed{', or None."""
    a = next(answer_lines(text), None)
    b = first_box(text)
    c = [x for x in (a, b) if x is not None]
    return min(c, key=lambda x: x[0]) if c else None


def v3_candidates(text):
    """Grader v3's candidates in text order: (start, content, end)."""
    out = []
    for m in R.MARK_V3.finditer(text):
        e = text.find("\n", m.end())
        e = len(text) if e < 0 else e
        rest = R.DELIM_V3.sub("", text[m.end():e]).strip().strip("*_").strip()
        if rest:
            out.append((m.start(), rest, e))
    for i, j, inner in R._boxes(text):
        out.append((i, inner, j))
    return sorted(out, key=lambda x: x[0])


def first_marker_alt(text):
    c = v3_candidates(text)
    return c[0] if c else None


def score_content(gold, fm):
    return 0 if fm is None else int(R.grade_v3(gold, "Answer: " + fm[1])["score_v3"])


def kept_literal(text):
    fm = first_marker(text)
    if fm is None:
        return None
    end = fm[2]
    after = text[end:]
    more = next(answer_lines(text, end), None) is not None or text.find(BOX, end) >= 0
    return len(after) > 300 and more


def kept_alt(text):
    c = v3_candidates(text)
    if not c:
        return None
    end = c[0][2]
    return len(text) - end > 300 and any(x[0] >= end for x in c[1:])


def main():
    if not fetch_s3(T1_S3, T1):
        return emit(None, False, None, "T1.jsonl could not be fetched from " + T1_S3, None)
    rows = [json.loads(l) for l in open(T1) if l.strip()]
    for r in rows:
        if not isinstance(r.get("text"), str) or r.get("gold") is None or r.get("cap_hit") not in (True, False):
            return emit(None, False, None, "a T1 row lacks text, gold or cap_hit", None)
    kept, wrong, kept_a, wrong_a, ex = 0, 0, 0, 0, None
    for r in rows:
        if r["cap_hit"]:
            continue
        k, ka = kept_literal(r["text"]), kept_alt(r["text"])
        if not k and not ka:
            continue
        v3_last = int(R.grade_v3(r["gold"], r["text"])["score_v3"])
        if k:
            kept += 1
            wrong += v3_last == 0
            if ex is None:
                ex = r
        if ka:
            kept_a += 1
            wrong_a += v3_last == 0
    print(f"kept {kept}  wrong {wrong}  alt kept {kept_a}  alt wrong {wrong_a}")
    if kept == 0:
        return emit(None, True, None, None, None)
    measured = wrong / kept
    emit(measured, measured < 0.20, (wrong_a / kept_a) if kept_a else None, None, ex)


main()
