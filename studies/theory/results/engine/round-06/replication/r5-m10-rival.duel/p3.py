"""k=3: among non-self-opened, cap_hit false, v3_last == 0 T3 rows (first row per problem_index), the fraction that
run on: first marker exists, > 300 characters follow its end, and that remainder holds another 'Answer:' line or '\\boxed{'."""
import json
import os
import subprocess

from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
LOCAL = "runs/theory-tests/r4/modal_t3-01/t3/T3.jsonl"


def fetch(s3, local):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def first_rows(path):
    out = {}
    for line in open(path):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return list(out.values())


def self_opened(text):
    return "\nOkay" in text[:60]


def first_marker(text):
    """(start, end, content) of the earliest marker, or None. (a) a line whose lstrip begins 'Answer:' (end = end of
    that line); (b) first '\\boxed{' (end = just after its matching brace, or end of text if unbalanced)."""
    cands = []
    pos = 0
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("Answer:"):
            start = pos + (len(line) - len(stripped))
            cands.append((start, pos + len(line), stripped[len("Answer:"):]))
            break
        pos += len(line) + 1
    i = text.find(S.BOXED)
    if i >= 0:
        depth, j = 1, i + len(S.BOXED)
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        if depth == 0:
            cands.append((i, j, text[i + len(S.BOXED):j - 1]))
        else:
            cands.append((i, len(text), text[i + len(S.BOXED):]))
    if not cands:
        return None
    return min(cands, key=lambda c: c[0])


def line_starts(text):
    out, pos = [], 0
    for line in text.split("\n"):
        out.append((pos, line))
        pos += len(line) + 1
    return out


def run_on(text, m):
    """Main: another line of the text (a line starting at or after the end) whose lstrip begins 'Answer:', or another
    '\\boxed{' in the remainder."""
    if m is None:
        return False
    end = m[1]
    rest = text[end:]
    if not len(rest) > 300:
        return False
    if S.BOXED in rest:
        return True
    return any(p >= end and line.lstrip().startswith("Answer:") for p, line in line_starts(text))


def run_on_alt(text, m):
    """Other reading: split the remainder itself on '\\n' (its first fragment, the tail of the marker's own line after a
    box, also counts as a line)."""
    if m is None:
        return False
    rest = text[m[1]:]
    if not len(rest) > 300:
        return False
    return S.BOXED in rest or any(f.lstrip().startswith("Answer:") for f in rest.split("\n"))


def main():
    fetch(S3, LOCAL)
    rows = [r for r in first_rows(LOCAL) if not self_opened(r["text"])]
    items = []
    for r in rows:
        if r["cap_hit"] is not False:
            continue
        if R.grade_v3(r["gold"], r["text"])["score_v3"] == 1:
            continue
        m = first_marker(r["text"])
        items.append((int(run_on(r["text"], m)), int(run_on_alt(r["text"], m)), r))
    if not items:
        not_computable("no rows kept (recipe: report nothing)")
        return

    def stat(sample):
        return sum(x[0] for x in sample) / len(sample)

    def stat_alt(sample):
        return sum(x[1] for x in sample) / len(sample)

    ex = dict(items[0][2])
    ex["text"] = ex["text"][:2000]
    ex["run_on"] = items[0][0]
    report(stat(items), len(items), bootstrap(stat, items), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(items), example_row=ex)


main()
