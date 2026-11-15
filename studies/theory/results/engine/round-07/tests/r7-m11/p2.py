"""r7-m11 prediction 2: C - A, cross-file agreement between day1_3 cued wrong answers and min-p (T 1.0 / min-p 0.1) cued wrong
answers, minus within-file agreement A of the day1_3 cued wrong answers.

Main: agreement = rln4_lib.agree(a, b) with a = the CUE answer (for A: the lower sample index of the pair), b = the other.
Alt: agreement in either order.
"""
import functools
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, refuted_without_number

ROOT = pathlib.Path.cwd()
CUE = ROOT / "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
MINP = ROOT / "runs/theory-tests/frustea-1114-180849-456c/answers.jsonl"


def fetch():
    if not MINP.exists():
        MINP.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", "frustea-1114-180849-456c/answers.jsonl", str(MINP)], check=True)


def is_wrong(r):
    ext = r.get("extracted_v3")
    return (r.get("cap_hit") is not True and r.get("finish_reason") != "length" and r.get("score_v3") == 0
            and isinstance(ext, str) and ext.strip() != "")


@functools.lru_cache(maxsize=None)
def ag(a, b):
    return bool(R.agree(a, b))


def ag_sym(a, b):
    return ag(a, b) or ag(b, a)


def short(r):
    r = dict(r)
    for k in ("text", "prompt"):
        if isinstance(r.get(k), str) and len(r[k]) > 300:
            r[k] = r[k][:150] + " ... " + r[k][-150:]
    return r


def main():
    fetch()
    cue = {}
    for line in open(CUE):
        r = json.loads(line)
        if r.get("attempt") != 0:
            continue
        key = (r["problem_index"], r["sample"])
        if key not in cue:
            cue[key] = r
    cue_wrong = {}
    for (p, s), r in sorted(cue.items()):
        if is_wrong(r):
            cue_wrong.setdefault(p, []).append(r)
    minp = {}
    for line in open(MINP):
        r = json.loads(line)
        if "attempt" in r and r["attempt"] != 0:
            continue
        if r["problem_index"] not in minp:
            minp[r["problem_index"]] = r
    minp_wrong = {p: r for p, r in minp.items() if is_wrong(r)}

    problems = sorted(set(p for p, _ in cue) | set(minp))
    entries = [(tuple(cue_wrong.get(p, [])), minp_wrong.get(p)) for p in problems]

    def parts(sample, f):
        a_num = a_den = c_num = c_den = 0
        for cw, mw in sample:
            xs = [r["extracted_v3"] for r in cw]
            for i in range(len(xs)):
                for j in range(i + 1, len(xs)):
                    a_den += 1
                    a_num += f(xs[i], xs[j])
            if mw is not None:
                for x in xs:
                    c_den += 1
                    c_num += f(x, mw["extracted_v3"])
        return a_num, a_den, c_num, c_den

    def stat_with(f):
        def stat(sample):
            a_num, a_den, c_num, c_den = parts(sample, f)
            if a_den == 0 or c_den == 0:
                return float("-inf")
            return c_num / c_den - a_num / a_den
        return stat

    a_num, a_den, c_num, c_den = parts(entries, ag)
    if a_den == 0 or c_den == 0:
        refuted_without_number()
        return
    measured = c_num / c_den - a_num / a_den
    sa_num, sa_den, sc_num, sc_den = parts(entries, ag_sym)
    alt = sc_num / sc_den - sa_num / sa_den
    n_a = sum(1 for cw, _ in entries if len(cw) >= 2)
    n_c = sum(1 for cw, mw in entries if len(cw) >= 1 and mw is not None)
    print(json.dumps({"groups": {"A: problems with >=2 CUE wrong answers": n_a,
                                 "C: problems with >=1 CUE wrong and a MINP wrong answer": n_c}}))
    ex = next((mw for cw, mw in entries if len(cw) >= 1 and mw is not None), None)
    report(measured, min(n_a, n_c), bootstrap(stat_with(ag), entries), "bootstrap",
           refuted_by_met=measured < -0.08, alt_measured=alt, example_row=short(ex) if ex else None)


if __name__ == "__main__":
    main()
