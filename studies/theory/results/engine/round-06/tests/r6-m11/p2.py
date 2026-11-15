"""r6-m11 prediction 2: among early-group, v3-wrong, finished cued-base T1 answers, the share whose final (v3-extracted)
answer equals the first-marker value.

Main reading (literal): same = grade_v3(gold=final answer, text='Answer: ' + content)['score_v3'] (grader v3's extraction runs
on the built response, then norm_v3 + n13_score.grade).
Alt reading: grader v3's equivalence applied straight to the two strings, without re-extracting from the built response:
n13_score.grade(norm_v3(final), norm_v3(content cleaned like a v3 marker candidate))['score'].
"""
import json
import os
import subprocess

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, refuted_without_number

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"
RECIPE_PATH = "runs/theory-rows/s3k/r4/base_rl-02/out/T1.jsonl"
FETCH_PATH = "runs/theory-tests/s3k/r4/base_rl-02/out/T1.jsonl"
BOXED = "\\boxed{"


def load():
    path = RECIPE_PATH if os.path.exists(RECIPE_PATH) else FETCH_PATH
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3, path, "--profile", "iterate-ecr"], check=True)
    rows = [json.loads(line) for line in open(path)]
    assert len(rows) == 500 and len({r["problem_index"] for r in rows}) == 500
    return rows


def answer_line(text):
    """First line whose left-stripped text begins with 'Answer:' -> (start of 'A', end of line, rest of line after 'Answer:')."""
    pos = 0
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("Answer:"):
            start = pos + (len(line) - len(stripped))
            end = pos + len(line)
            return start, end, text[start + len("Answer:"):end]
        pos += len(line) + 1
    return None


def first_box(text):
    i = text.find(BOXED)
    if i < 0:
        return None
    depth, j = 1, i + len(BOXED)
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    if depth == 0:
        return i, j, text[i + len(BOXED):j - 1]
    return i, len(text), text[i + len(BOXED):]          # unbalanced: end = end of text, content = rest of text


def first_marker(text):
    cands = [c for c in (answer_line(text), first_box(text)) if c is not None]
    return min(cands, key=lambda c: c[0]) if cands else None


def is_early(text, mk):
    start, end, _ = mk
    return start / len(text) < 0.5 and len(text) - end > 300


def alt_same(final, content):
    c = R.DELIM_V3.sub("", content).strip().strip("*_").strip()
    if not c:
        return 0
    return S.grade(R.norm_v3(final), R.norm_v3(c))["score"]


def stat(sample):
    return sum(x["same"] for x in sample) / len(sample)


def main():
    kept = []
    for r in load():
        if r["cap_hit"] is not False:
            continue
        mk = first_marker(r["text"])
        if mk is None or not is_early(r["text"], mk):
            continue
        if R.grade_v3(r["gold"], r["text"])["score_v3"] != 0:
            continue
        final = R.extract_v3(r["text"])[1]
        if final is None or final.strip() == "":
            continue
        content = mk[2]
        same = R.grade_v3(final, "Answer: " + content)["score_v3"]
        kept.append({"same": same, "alt": alt_same(final, content), "row": r, "mk": mk, "final": final})
    if not kept:
        refuted_without_number()
        return
    measured = stat(kept)
    alt = sum(x["alt"] for x in kept) / len(kept)
    ex = kept[0]
    r = dict(ex["row"])
    r["text"] = r["text"][:1500]
    r["_derived"] = {"first_marker_start": ex["mk"][0], "first_marker_end": ex["mk"][1], "content": ex["mk"][2][:300],
                     "final_v3": ex["final"], "same": ex["same"], "same_alt": ex["alt"], "len_text": len(ex["row"]["text"])}
    refuted = len(kept) < 8 or measured < 0.6
    report(measured, len(kept), bootstrap(stat, kept), "bootstrap", refuted_by_met=refuted, alt_measured=alt, example_row=r)


main()
