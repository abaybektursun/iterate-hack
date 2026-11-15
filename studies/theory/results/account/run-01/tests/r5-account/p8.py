"""p8: fraction of answer-statement-part problems where at least one base_cue row of repair/offline-01 has
kind == 'no_answer', or score_v4 == 1 and score_v3 == 0 (null scores count as 0)."""
import json
import os

from studies.theory.lib.noise import bootstrap, report, not_computable

PP = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
RP = "studies/rlneurons/results/repair/offline-01/rows.jsonl"
SUBS = ("format", "final line", "garbled", "rejected", "changed")


def is_true(v):
    return v is True or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 1)


def is_false(v):
    return v is False or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 0)


def ft_match(row):
    ft = row.get("failure_type")
    return isinstance(ft, str) and any(s in ft.lower() for s in SUBS)


def sc(v):
    return 0 if v is None else v


def main():
    for p in (PP, RP):
        if not os.path.exists(p):
            return not_computable(f"file not readable: {p}")
    with open(PP) as f:
        pp = json.load(f)
    by_pi = {}
    with open(RP) as f:
        for l in f:
            if not l.strip():
                continue
            r = json.loads(l)
            if r.get("model") == "base_cue" and r.get("sample") in (0, 1, 2, 3):
                by_pi.setdefault(r.get("problem_index"), []).append(r)
    part = [r for r in pp if "t1_right" in r and "t2_right" in r and is_true(r["t2_right"])
            and is_false(r["t1_right"]) and r.get("t1_cap_hit") is not True and ft_match(r)]
    if not part:
        return not_computable("no answer-statement-part problems; fraction is 0/0")

    def counted(pi, kinds=("no_answer",)):
        return any(x.get("kind") in kinds or (sc(x.get("score_v4")) == 1 and sc(x.get("score_v3")) == 0)
                   for x in by_pi.get(pi, []))  # missing rows do not count

    entries = [(r, counted(r["problem_index"])) for r in part]

    def stat(sample):
        return sum(c for _, c in sample) / len(sample)

    measured = stat(entries)
    # alt reading ("unanswered" in the experiment title): a cap_hit sample also counts as unanswered
    alt = stat([(r, counted(r["problem_index"], ("no_answer", "cap_hit"))) for r in part])
    refuted = measured < 0.10
    ex = (by_pi.get(part[0]["problem_index"]) or [part[0]])[0]
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=refuted,
           alt_measured=alt, example_row=ex)


main()
