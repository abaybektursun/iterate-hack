"""r4-m11 prediction 3: net first-marker gain on the Day-1 #3 base + cue answers (iterate-runs:abaybektursun-1114-153825-208b/answers.jsonl).

Filter attempt == 0; rows present are the denominator. v3_last = stored score_v3. first_score as in p1 (earliest line-start
'Answer:' line or first '\\boxed{', graded by grade_v3 as 'Answer: ' + content; no marker -> 0; cap hits included).
Statistic: (sum first_score - sum v3_last) / rows. Refuted when below 0.002.
Alt: first marker under grader v3's own candidate set (MARK_V3 anywhere with non-empty rest, balanced boxes).
The file is fetched with `modal volume get`; when it cannot be fetched the script reports not_computable.
"""
import json
import pathlib
import shutil
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


JOB = "abaybektursun-1114-153825-208b"
DEST = ROOT / "runs/theory-tests" / JOB / "answers.jsonl"


def fetch_volume():
    if not DEST.exists():
        if shutil.which("modal") is None:
            return "modal CLI not found"
        DEST.parent.mkdir(parents=True, exist_ok=True)
        p = subprocess.run(["modal", "volume", "get", "iterate-runs", JOB + "/answers.jsonl", str(DEST)], capture_output=True, text=True)
        if not DEST.exists():
            return (p.stderr or p.stdout).strip()[-200:]
    return None


def main():
    err = fetch_volume()
    if err is not None or DEST.stat().st_size == 0:
        return emit(None, False, None, "iterate-runs:" + JOB + "/answers.jsonl is not readable from this workspace (modal volume get: "
                    + str(err) + ")", None)
    rows = [json.loads(l) for l in open(DEST) if l.strip()]
    if any("attempt" not in r for r in rows):
        return emit(None, False, None, "rows of " + JOB + " have no attempt field", None)
    rows = [r for r in rows if r["attempt"] == 0]
    for r in rows:
        for f in ("score_v3", "text", "gold"):
            if f not in r:
                return emit(None, False, None, "an attempt-0 row of " + JOB + " has no " + f + " field", None)
    # rows whose stored grade or text is null are counted as missing rows and dropped
    present = [r for r in rows if r["score_v3"] is not None and isinstance(r["text"], str) and r["gold"] is not None]
    n_null = len(rows) - len(present)
    if not present:
        return emit(None, False, None, "no attempt-0 rows in " + JOB, None)
    s_last = s_first = s_alt = 0
    ex = None
    for r in present:
        v3_last = int(r["score_v3"])
        fs = score_content(r["gold"], first_marker(r["text"]))
        fa = score_content(r["gold"], first_marker_alt(r["text"]))
        s_last += v3_last
        s_first += fs
        s_alt += fa
        if ex is None or (fs != v3_last and ex[1] == ex[2]):
            ex = (r, fs, v3_last)
    n = len(present)
    measured = (s_first - s_last) / n
    print(f"attempt-0 rows {len(rows)}  dropped null {n_null}  used {n}  sum v3_last {s_last}  sum first {s_first}  sum alt {s_alt}")
    emit(measured, measured < 0.002, (s_alt - s_last) / n, None, ex[0])


main()
