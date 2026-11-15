"""r8-m10 prediction 4: hard328, precision of Think-SFT cue's finished answers with 14000 <= n_new <= 16383."""
import json
import os
from collections import OrderedDict

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

PATH = "studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01/rows.jsonl"


def load(path):
    """attempt == 0 (missing = 0), then first row per (problem_index, sample) in file order."""
    out = OrderedDict()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            att = r.get("attempt")
            if att is None:
                att = 0
            if att != 0:
                continue
            key = (r["problem_index"], r["sample"])
            if key not in out:
                out[key] = r
    return list(out.values())


def finished(r):
    return r.get("cap_hit") is not True and r.get("finish_reason") != "length"


def keep(r):
    return finished(r) and 14000 <= r["n_new"] <= 16383


def keep_alt(r):
    """Other reading: the top bound taken as the 16,384 cap itself (inclusive)."""
    return finished(r) and 14000 <= r["n_new"] <= 16384


def right(r):
    return r.get("score_v3") == 1


def make_stat(pred):
    def stat(problems):
        k = [r for rows in problems for r in rows if pred(r)]
        return sum(map(right, k)) / len(k) if k else 0.0
    return stat


def main():
    if not os.path.exists(PATH):
        not_computable(f"file not readable: {PATH}")
        return
    rows = load(PATH)
    if any(r.get("n_new") is None for r in rows):
        not_computable("a row lacks n_new")
        return
    by = {}
    for r in rows:
        by.setdefault(r["problem_index"], []).append(r)
    # resampling unit: problems that contribute at least one kept row (other problems add nothing to the statistic)
    problems = [by[p] for p in sorted(by) if any(map(keep, by[p]))]
    kept = [r for rows_ in problems for r in rows_ if keep(r)]
    if not kept:
        refuted_without_number()  # fewer than 20 kept rows refutes
        return
    stat = make_stat(keep)
    measured = stat(problems)
    alt_k = [r for r in rows if keep_alt(r)]
    alt = sum(map(right, alt_k)) / len(alt_k) if alt_k else None
    refuted = measured < 0.42 or len(kept) < 20
    report(measured, len(kept), bootstrap(stat, problems), "bootstrap",
           refuted_by_met=refuted, alt_measured=alt, example_row=kept[0])


main()
