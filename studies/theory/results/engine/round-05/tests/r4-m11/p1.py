"""r4-m11 prediction 1: among T1 rows graded wrong by grader v3 on the full text, the fraction whose FIRST answer marker is right.

Main (literal): first marker = earliest of (a) a line whose left-stripped text begins with 'Answer:' (content = rest of that line)
and (b) the first '\\boxed{' (content = brace-balanced contents; an unclosed first box takes the rest of the text).
first_score = grade_v3(gold, 'Answer: ' + content); no marker -> 0. Filter v3_last == 0 (cap hits included).
Alt: the first marker is the earliest candidate under grader v3's own candidate set (MARK_V3 anywhere in a line with a non-empty
rest, or the first balanced \\boxed{}), graded the same way.
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


def main():
    if not fetch_s3(T1_S3, T1):
        return emit(None, False, None, "T1.jsonl could not be fetched from " + T1_S3, None)
    rows = [json.loads(l) for l in open(T1) if l.strip()]
    for r in rows:
        if not isinstance(r.get("text"), str) or r.get("gold") is None:
            return emit(None, False, None, "a T1 row lacks text or gold", None)
    wrong, hit, hit_alt, ex = 0, 0, 0, None
    for r in rows:
        v3_last = int(R.grade_v3(r["gold"], r["text"])["score_v3"])
        if v3_last != 0:
            continue
        wrong += 1
        fs = score_content(r["gold"], first_marker(r["text"]))
        fa = score_content(r["gold"], first_marker_alt(r["text"]))
        hit += fs == 1
        hit_alt += fa == 1
        if ex is None or (fs == 1 and ex[1] != 1):
            ex = (r, fs)
    if wrong == 0:
        return emit(None, False, None, "no T1 row has v3_last == 0, so the fraction is undefined", None)
    measured = hit / wrong
    print(f"rows {len(rows)}  v3_last==0 {wrong}  first-right {hit}  alt first-right {hit_alt}")
    emit(measured, measured < 0.04, hit_alt / wrong, None, ex[0])


main()
