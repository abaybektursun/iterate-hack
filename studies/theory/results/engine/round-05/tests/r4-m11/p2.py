"""r4-m11 prediction 2: among all 500 T1 rows where first_score != v3_last, the share with first_score == 1 (first-right, last-wrong).

Main (literal): first marker as in p1 (earliest line-start 'Answer:' line or first '\\boxed{'); no marker -> first_score 0.
Alt: first marker under grader v3's own candidate set, as in p1. No discordant rows -> refuted without a number.
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
    disc, up, disc_a, up_a, ex = 0, 0, 0, 0, None
    for r in rows:
        v3_last = int(R.grade_v3(r["gold"], r["text"])["score_v3"])
        fs = score_content(r["gold"], first_marker(r["text"]))
        fa = score_content(r["gold"], first_marker_alt(r["text"]))
        if fs != v3_last:
            disc += 1
            up += fs == 1
            if ex is None:
                ex = r
        if fa != v3_last:
            disc_a += 1
            up_a += fa == 1
    print(f"rows {len(rows)}  discordant {disc}  first-right {up}  alt discordant {disc_a}  alt first-right {up_a}")
    if disc == 0:
        return emit(None, True, None, None, None)
    measured = up / disc
    emit(measured, measured < 0.45, (up_a / disc_a) if disc_a else None, None, ex)


main()
