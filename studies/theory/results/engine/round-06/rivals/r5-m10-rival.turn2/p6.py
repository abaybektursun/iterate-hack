"""p6: plain base, MATH-500. Gold-in-text share among finished (cap_hit false), v3-wrong, not self-opened answers on problems
with an integer gold of |gold| >= 10: F(T3, T 1.0 / top-p 1.0) - F(P_math500, T 0.6 / top-p 0.95).
alt_measured: the same with empty-text rows (no answer generated) also dropped from both files."""
import json
import os
import re
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

BASE = "s3://pg-lineage-769063704696/results/rlneurons/"
FILES = {
    "T3": ("r4/modal_t3-01/t3/T3.jsonl", "first"),
    "P": ("r3/base-01/out/P_math500.jsonl", "min_sample"),
}
LOCAL = "runs/theory-tests/s3k/rlneurons/"
INT = re.compile(r"^-?\d+$")
DIGIT_COMMA = re.compile(r"(?<=\d),(?=\d)")


def fetch(s3, local):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr", "--only-show-errors"], check=False)
    return os.path.exists(local)


def short(r):
    r = dict(r)
    t = r.get("text") or ""
    if len(t) > 600:
        r["text"] = t[:300] + " [...truncated for the report...] " + t[-300:]
    for k in ("prefill_ids", "answer_tokens"):
        r.pop(k, None)
    return r


def gold_int(gold):
    """The gold as a Python int if, after removing '$' and whitespace and unwrapping a whole \\boxed{...}, it fully matches
    ^-?\\d+$; else None."""
    g = re.sub(r"\s", "", gold.replace("$", ""))
    if g.startswith("\\boxed{") and g.endswith("}"):
        depth, j = 0, len("\\boxed")
        close = None
        for j in range(len("\\boxed"), len(g)):
            depth += {"{": 1, "}": -1}.get(g[j], 0)
            if depth == 0:
                close = j
                break
        if close == len(g) - 1:  # the brace opened after \boxed closes at the last character: wholly wrapped
            g = g[len("\\boxed{"):-1]
    return int(g) if INT.fullmatch(g) else None


def load(name):
    key, rule = FILES[name]
    kept = {}
    for line in open(LOCAL + key):
        r = json.loads(line)
        i = r["problem_index"]
        if rule == "first":
            if i not in kept:
                kept[i] = r
        else:
            if "sample" not in r:
                raise KeyError("sample")
            if i not in kept or r["sample"] < kept[i]["sample"]:
                kept[i] = r
    return kept


def classify(r):
    """None if the row is filtered out, else (hit, empty_text)."""
    text = r["text"] or ""
    if "\nOkay" in text[:60]:
        return None
    if r["cap_hit"] is not False:
        return None
    if R.grade_v3(r["gold"], text)["score_v3"] != 0:
        return None
    g = gold_int(r["gold"])
    if g is None or abs(g) < 10:
        return None
    t = DIGIT_COMMA.sub("", text)
    gd = str(abs(g))
    hit = re.search(r"(?<![0-9])" + gd + r"(?![0-9])", t) is not None
    return hit, text.strip() == ""


def F(sample, pos, drop_empty=False):
    vals = [e[pos] for e in sample if e[pos] is not None and not (drop_empty and e[pos][1])]
    return (sum(1 for h, _ in vals if h) / len(vals)) if vals else None


def make_stat(drop_empty):
    def stat(sample):
        a, b = F(sample, 0, drop_empty), F(sample, 1, drop_empty)
        # A bootstrap resample with no kept row in one file contributes 0.0 (the full sample is checked below).
        return 0.0 if a is None or b is None else a - b
    return stat


def main():
    for name, (key, _) in FILES.items():
        if not fetch(BASE + key, LOCAL + key):
            return not_computable(f"{key} could not be fetched from S3")
    try:
        t3, p = load("T3"), load("P")
    except KeyError as e:
        return not_computable(f"field {e} missing in a row")
    for r in list(t3.values()) + list(p.values()):
        for f in ("text", "gold", "cap_hit"):
            if f not in r:
                return not_computable(f"field {f} missing in a row")
    entries, rows = [], {}
    for i in sorted(set(t3) | set(p)):
        a = classify(t3[i]) if i in t3 else None
        b = classify(p[i]) if i in p else None
        if a is None and b is None:
            continue
        entries.append((a, b))
        rows[i] = t3[i] if a is not None else p[i]
    stat = make_stat(False)
    if F(entries, 0) is None or F(entries, 1) is None:
        return not_computable("one file has no kept rows; the recipe says report nothing")
    measured = stat(entries)
    alt_a, alt_b = F(entries, 0, True), F(entries, 1, True)
    alt = None if alt_a is None or alt_b is None else alt_a - alt_b
    ex = next(iter(rows.values()))
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=short(ex))


main()
