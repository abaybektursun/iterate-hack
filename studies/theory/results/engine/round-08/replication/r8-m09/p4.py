"""k=4: blank v3 share among finished answers, arm sft1_rl20 (H) minus arm think (T), transplant hard328-01."""
import json
import os
import re

from studies.theory.lib.noise import bootstrap, report, not_computable

PATH = "studies/rlneurons/results/transplant/hard328-01/rows.jsonl"
CHARS = set("$*:.,")
SUBS = ["\\[", "\\]", "\\(", "\\)", "\\boxed{}", "{}"]


def is_blank(ext):
    """Literal reading: delete whitespace, then the characters $ * : . , then each substring in the listed order once."""
    if ext is None:
        return True
    s = re.sub(r"\s", "", str(ext))
    s = "".join(ch for ch in s if ch not in CHARS)
    for sub in SUBS:
        s = s.replace(sub, "")
    return s == ""


def is_blank_fix(ext):
    """Other reading: repeat the deletions until nothing changes (handles nested leftovers like '\\boxed{{}}')."""
    if ext is None:
        return True
    s = str(ext)
    while True:
        prev = s
        s = re.sub(r"\s", "", s)
        s = "".join(ch for ch in s if ch not in CHARS)
        for sub in SUBS:
            s = s.replace(sub, "")
        if s == prev:
            break
    return s == ""


def finished(r):
    return r.get("cap_hit") is not True


def main():
    if not os.path.exists(PATH):
        not_computable(f"{PATH} not found")
        return
    rows = [json.loads(l) for l in open(PATH) if l.strip()]
    if not rows or "extracted_v3" not in rows[0] and not any("extracted_v3" in r for r in rows):
        not_computable("extracted_v3 field absent")
        return
    by_p = {}
    for r in rows:
        if r.get("arm") in ("sft1_rl20", "think"):
            h, t = by_p.setdefault(r["problem_index"], ([], []))
            (h if r["arm"] == "sft1_rl20" else t).append(r)
    problems = [by_p[p] for p in sorted(by_p)]

    def make_stat(blank):
        def stat(sample):
            fh = [r for h, _ in sample for r in h if finished(r)]
            ft = [r for _, t in sample for r in t if finished(r)]
            if not fh or not ft:
                return float("nan")
            return sum(blank(r.get("extracted_v3")) for r in fh) / len(fh) - \
                sum(blank(r.get("extracted_v3")) for r in ft) / len(ft)
        return stat

    stat = make_stat(is_blank)
    fh = [r for h, _ in problems for r in h if finished(r)]
    ft = [r for _, t in problems for r in t if finished(r)]
    if not fh or not ft:
        not_computable("an arm has no finished rows")
        return
    ph = sum(1 for h, _ in problems if h)
    pt = sum(1 for _, t in problems if t)
    print(json.dumps({"groups": {"H_sft1_rl20_problems": ph, "T_think_problems": pt,
                                 "H_finished_rows": len(fh), "T_finished_rows": len(ft)}}))
    measured = stat(problems)
    alt = make_stat(is_blank_fix)(problems)
    example = next((r for r in fh if is_blank(r.get("extracted_v3"))), fh[0])
    report(measured, min(ph, pt), bootstrap(stat, problems), "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=example)


main()
