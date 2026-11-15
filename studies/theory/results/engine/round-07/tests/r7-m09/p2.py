"""r7-m09 prediction 2: answer-type dependence.
Among W (E4 problems where Think-SFT cue gives a finished v3-wrong answer), share whose gold is not a plain integer."""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, refuted_without_number

BASE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
CUE = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"


def path_of(p):
    if os.path.exists(p):
        return p
    dst = os.path.join("runs/theory-tests/r7-m09", p)
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(subprocess.run(["git", "show", "HEAD:" + p], check=True, capture_output=True).stdout)
    return dst


def load_jsonl(p):
    with open(path_of(p)) as f:
        return [json.loads(l) for l in f if l.strip()]


def first_per_problem(p):
    with open(path_of(p)) as f:
        rows = json.load(f)
    out = {}
    for r in rows:
        if r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return out


def e4_set(base_rows):
    by = {}
    for r in base_rows:
        if r.get("attempt") == 0:
            by.setdefault(r["problem_index"], []).append(r)
    return sorted(pi for pi, rs in by.items()
                  if len(rs) == 4 and all(x.get("score_v3") == 1 and x.get("cap_hit") is not True for x in rs))


def wholly_boxed_inside(s):
    """If s is exactly \\boxed{...} (the opening brace closes at the last character), return the inside, else None."""
    pre = "\\boxed{"
    if not (s.startswith(pre) and s.endswith("}")):
        return None
    depth = 0
    for i in range(len(pre) - 1, len(s)):
        c = s[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[len(pre):i] if i == len(s) - 1 else None
    return None


def normalise(g):
    s = g.strip().replace("$", "")
    s = re.sub(r"\s+", "", s)
    inside = wholly_boxed_inside(s)
    if inside is not None:
        s = inside
    s = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", s)
    return s


def is_int(g):
    return re.fullmatch(r"-?\d+", normalise(g)) is not None


def is_int_alt(g):
    """Other reading: an integer value written with unit/decoration markup (degrees, percent, \\text{units},
    \\! spacing, a leading +) also counts as a plain integer."""
    s = normalise(g)
    s = s.replace("\\!", "").replace("\\,", "")
    s = re.sub(r"\^\{?\\circ\}?", "", s)
    s = s.replace("\\%", "").replace("%", "")
    s = re.sub(r"\\(?:text|mbox|mathrm)\{[^{}]*\}", "", s)
    s = s.lstrip("+")
    return re.fullmatch(r"-?\d+", s) is not None


def main():
    base = load_jsonl(BASE)
    cue = first_per_problem(CUE)
    E4 = e4_set(base)
    gold = {}
    for r in base:
        if r.get("attempt") == 0 and r["problem_index"] not in gold:
            gold[r["problem_index"]] = r["gold"]
    W = [pi for pi in E4 if pi in cue and cue[pi].get("score_v3") == 0 and cue[pi].get("cap_hit") is not True]
    if not W:
        refuted_without_number()
        return
    items = [(pi, gold[pi]) for pi in W]

    def stat(sample):
        return sum(not is_int(g) for _, g in sample) / len(sample)

    def stat_alt(sample):
        return sum(not is_int_alt(g) for _, g in sample) / len(sample)

    m = stat(items)
    ex_pi = W[0]
    ex = {"cue": cue[ex_pi], "gold": gold[ex_pi], "gold_normalised": normalise(gold[ex_pi]),
          "gold_is_integer": is_int(gold[ex_pi])}
    report(m, len(items), bootstrap(stat, items), "bootstrap", refuted_by_met=m < 0.45,
           alt_measured=stat_alt(items), example_row=ex)


main()
