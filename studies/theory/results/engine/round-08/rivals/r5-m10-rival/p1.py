import json
import os
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, binomial, report, not_computable, refuted_without_number  # noqa: F401

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
LOCAL = "runs/theory-tests/s3k/r4/modal_t3-01/t3/T3.jsonl"
BOXED = "\\boxed{"


def load_rows():
    """First row per problem_index in file order."""
    if not os.path.exists(LOCAL):
        os.makedirs(os.path.dirname(LOCAL), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3, LOCAL, "--profile", "iterate-ecr"], check=True,
                       stdout=subprocess.DEVNULL)
    seen, out = set(), []
    for line in open(LOCAL):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["problem_index"] in seen:
            continue
        seen.add(r["problem_index"])
        out.append(r)
    return out


def self_opened(text):
    return "\nOkay" in text[:60]


def v3_last(gold, text):
    """Grader v3 on the full text; an empty extraction counts 0 (grade_v3 already gives 0 when nothing is extracted)."""
    g = R.grade_v3(gold, text)
    return 1 if (g["extracted_v3"] is not None and g["score_v3"] == 1) else 0


def first_marker(text):
    """Literal reading. Returns (start, end, content) or None.
    (a) first line whose lstrip() begins with 'Answer:'; start = position of 'Answer:', content = rest of line after it,
        end = end of that line (or end of text). (b) first '\\boxed{'; content = brace-balanced contents, end just after the
        matching '}', or (unbalanced) content = rest of text, end = end of text. Earliest start wins."""
    cand = []
    pos = 0
    for line in text.split("\n"):
        s = line.lstrip()
        if s.startswith("Answer:"):
            a = pos + (len(line) - len(s))
            cand.append((a, pos + len(line), line[(len(line) - len(s)) + len("Answer:"):]))
            break
        pos += len(line) + 1
    i = text.find(BOXED)
    if i >= 0:
        depth, j = 1, i + len(BOXED)
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        if depth == 0:
            cand.append((i, j, text[i + len(BOXED):j - 1]))
        else:
            cand.append((i, len(text), text[i + len(BOXED):]))
    if not cand:
        return None
    return min(cand, key=lambda c: c[0])


def first_marker_alt(text):
    """Other reading: the first answer candidate as grader v3 itself defines candidates (MARK_V3 anywhere in a line,
    'Answer:'/'Final Answer:'/'Answer is', with a non-empty rest of line; only brace-balanced boxes). Same (start, end, content)."""
    cand = []
    for m in R.MARK_V3.finditer(text):
        e = text.find("\n", m.end())
        e = len(text) if e < 0 else e
        rest = R.DELIM_V3.sub("", text[m.end():e]).strip().strip("*_").strip()
        if rest:
            cand.append((m.start(), e, text[m.end():e]))
            break
    boxes = R._boxes(text)
    if boxes:
        cand.append(boxes[0])
    if not cand:
        return None
    return min(cand, key=lambda c: c[0])


def first_score(gold, marker):
    if marker is None:
        return 0
    g = R.grade_v3(gold, "Answer: " + marker[2])
    return 1 if (g["extracted_v3"] is not None and g["score_v3"] == 1) else 0


def has_answer_line(s):
    return any(line.lstrip().startswith("Answer:") for line in s.split("\n"))


def has_alt_marker(s):
    for m in R.MARK_V3.finditer(s):
        e = s.find("\n", m.end())
        rest = R.DELIM_V3.sub("", s[m.end():len(s) if e < 0 else e]).strip().strip("*_").strip()
        if rest:
            return True
    return bool(R._boxes(s))


def example(r, **extra):
    d = {k: r[k] for k in ("problem_index", "unique_id", "gold", "cap_hit", "finish_reason", "n_new")}
    d["text_head"] = r["text"][:600]
    d["text_tail"] = r["text"][-600:]
    d.update(extra)
    return d


def main():
    rows = [r for r in load_rows() if not self_opened(r["text"])]
    items = []
    for r in rows:
        last = v3_last(r["gold"], r["text"])
        if last != 0:
            continue
        items.append((r, first_score(r["gold"], first_marker(r["text"])), first_score(r["gold"], first_marker_alt(r["text"]))))
    if not items:
        not_computable("no non-self-opened rows with v3_last == 0: the recipe says report nothing")
        return

    def stat(sample):
        return sum(x[1] == 1 for x in sample) / len(sample)

    measured = stat(items)
    alt = sum(x[2] == 1 for x in items) / len(items)
    ex = next((x for x in items if x[1] == 1), items[0])
    report(measured, len(items), bootstrap(stat, items), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=example(ex[0], v3_last=0, first_score=ex[1], first_score_alt=ex[2]))


main()
