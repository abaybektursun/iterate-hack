"""r4-m11 prediction 5: v3 wrong rate among finished T1 answers that continue > 300 characters past the first marker and state another marker.

Run from the repository root: python3 <this script>. Standard library plus the repository's grader code
(studies/rlneurons/lib/rln4_lib.py, the code behind studies/rlneurons/grader/rln4_grader_v3.py), whose equivalence step needs the
math_verify package. Prints one JSON object as the last line.
"""
import json
import os
import re
import subprocess
import sys
import types

ROOT = os.getcwd()
T1 = ("s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl",
      os.path.join(ROOT, "runs", "theory-tests", "s3", "T1.jsonl"))
BOXED = "\\boxed{"


def out(d):
    print(json.dumps(d, ensure_ascii=False))
    sys.exit(0)


def not_computable(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": reason, "example_row": None})


def fetch_s3(uri, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr", "--only-show-errors"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            not_computable(f"could not fetch {uri}: {r.stderr.strip()[:300]}")
    rows = []
    with open(path) as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_grader():
    sys.path.insert(0, ROOT)
    try:
        import numpy  # noqa: F401
    except ImportError:
        # numpy is imported at module level by n13_score / alwayson_edit (annotations only, deferred); grade/norm_v3 do not use it.
        sys.modules["numpy"] = types.ModuleType("numpy")
    try:
        import math_verify  # noqa: F401
    except ImportError:
        not_computable("grader v3 (rln4_lib.grade_v3 -> n13_score.grade) needs the math_verify package, which this python3 does not "
                       "have; the standard library cannot reproduce grader v3's equivalence test")
    from studies.rlneurons.lib import rln4_lib as R
    return R


# ------------------------------------------------------------------ first marker, as the recipe defines it
def balanced_box(text, i):
    """Content and end (just after the matching closing brace) of the box starting at i; (None, len(text)) when unbalanced."""
    depth, j = 1, i + len(BOXED)
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    if depth == 0:
        return text[i + len(BOXED):j - 1], j
    return None, len(text)


def first_marker(text):
    """Earliest of (a) a line whose left-stripped text begins with 'Answer:' (content = rest of that line; end = end of that line)
    and (b) the first '\\boxed{' (content = brace-balanced contents; end = just after the closing brace).
    Returns None or dict(kind, start, content, end)."""
    a, pos = None, 0
    for line in text.split("\n"):
        s = line.lstrip()
        if s.startswith("Answer:"):
            st = pos + len(line) - len(s)
            a = {"kind": "answer_line", "start": st, "content": s[len("Answer:"):], "end": pos + len(line)}
            break
        pos += len(line) + 1
    b, i = None, text.find(BOXED)
    if i >= 0:
        c, e = balanced_box(text, i)
        b = {"kind": "boxed", "start": i, "content": c, "end": e}
    cands = [m for m in (a, b) if m is not None]
    return min(cands, key=lambda m: m["start"]) if cands else None


def first_marker_v3(R, text):
    """Other reading: the first candidate under grader v3's own candidate set (MARK_V3 anywhere in a line with non-empty rest,
    or any balanced box)."""
    cands = []
    for m in R.MARK_V3.finditer(text):
        end = text.find("\n", m.end())
        end = len(text) if end < 0 else end
        rest = R.DELIM_V3.sub("", text[m.end():end]).strip().strip("*_").strip()
        if rest:
            cands.append({"kind": "v3_marker", "start": m.start(), "content": rest, "end": end})
            break
    bx = R._boxes(text)
    if bx:
        cands.append({"kind": "v3_boxed", "start": bx[0][0], "content": bx[0][2], "end": bx[0][1]})
    return min(cands, key=lambda m: m["start"]) if cands else None


def score_marker(R, gold, m):
    if m is None or m["content"] is None:
        return 0
    return int(R.grade_v3(gold, "Answer: " + m["content"])["score_v3"])


def compact(r, **extra):
    d = {k: r.get(k) for k in ("cell", "problem_index", "sample", "attempt", "gold", "cap_hit", "finish_reason", "n_new", "score_v3")
         if k in r}
    d["text_head"] = r["text"][:300]
    d["text_tail"] = r["text"][-600:]
    d.update(extra)
    return d


# ------------------------------------------------------------------ recipe
def main():
    R = load_grader()
    rows = fetch_s3(*T1)
    for r in rows:
        for f in ("text", "gold", "cap_hit"):
            if f not in r:
                not_computable(f"a T1 row has no {f} field")
    kept = kept_wrong = kept_a = kept_wrong_a = 0
    example = None
    for r in rows:
        if r["cap_hit"] is not False:                    # filter: cap_hit false
            continue
        text = r["text"]
        m = first_marker(text)
        if m is None:                                    # filter: at least one marker
            continue
        rest = text[m["end"]:]
        line_starts = [0] + [i + 1 for i, ch in enumerate(text) if ch == "\n"]
        another_line = False
        for st in line_starts:
            if st < m["end"]:
                continue
            e = text.find("\n", st)
            if text[st:len(text) if e < 0 else e].lstrip().startswith("Answer:"):
                another_line = True
                break
        further = another_line or (BOXED in rest)
        if not further:
            continue
        v3_last = None
        if len(rest) > 300:                              # main reading: text after the first marker's end > 300 characters
            v3_last = int(R.grade_v3(r["gold"], text)["score_v3"])
            kept += 1
            kept_wrong += v3_last == 0
            if example is None or (v3_last == 0 and example["v3_last"] == 1):
                example = compact(r, v3_last=v3_last, first_marker_kind=m["kind"], first_content=m["content"],
                                  first_marker_end=m["end"], chars_after_first_marker=len(rest))
        if len(text) > 300:                              # other reading: the whole answer > 300 characters
            if v3_last is None:
                v3_last = int(R.grade_v3(r["gold"], text)["score_v3"])
            kept_a += 1
            kept_wrong_a += v3_last == 0
    print(f"rows {len(rows)}  kept {kept}  kept wrong {kept_wrong}  alt kept {kept_a} alt wrong {kept_wrong_a}")
    alt = kept_wrong_a / kept_a if kept_a else None
    if kept == 0:                                        # recipe: undefined counts as refuted
        out({"measured": None, "refuted_by_met": True, "alt_measured": None, "not_computable": None, "example_row": None})
    measured = kept_wrong / kept
    out({"measured": measured, "refuted_by_met": measured < 0.20, "alt_measured": alt, "not_computable": None, "example_row": example})


if __name__ == "__main__":
    main()
