"""r8-m02 prediction 4: among cued-base finished MATH-500 answers with exactly one switch marker, share whose text
after the switch is shorter than before it, finished-wrong minus right."""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

JOB = "abaybektursun-1114-153825-208b"
SW = re.compile(r"(?<![A-Za-z])(Alternatively|Another approach|Another way|Let me try (?:a )?(?:different|another)"
                r"|Let's try (?:a )?(?:different|another)|Instead, let)")


def path_for(job):
    p = f"runs/theory-rows/{job}/answers.jsonl"
    if os.path.exists(p):
        return p
    q = f"runs/theory-tests/{job}/answers.jsonl"
    if not os.path.exists(q):
        os.makedirs(os.path.dirname(q), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", q], check=True)
    return q


def kept_rows(path):
    """attempt == 0, sample in 0..3, first row per (problem_index, sample) in file order, cap hits dropped."""
    seen, out = set(), []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("attempt") != 0 or r.get("sample") not in (0, 1, 2, 3):
                continue
            key = (r["problem_index"], r["sample"])
            if key in seen:
                continue
            seen.add(key)
            if r.get("cap_hit") is True or r.get("finish_reason") == "length":
                continue
            out.append(r)
    return out


def slim(r):
    d = {k: r.get(k) for k in ("cell", "problem_index", "sample", "attempt", "n_new", "cap_hit", "finish_reason",
                               "extracted_v3", "gold", "score_v3")}
    d["text_len"] = len(r["text"])
    d["match_starts"] = [m.start() for m in SW.finditer(r["text"])]
    d["text_head"] = r["text"][:200]
    return d


def main():
    try:
        rows = kept_rows(path_for(JOB))
    except Exception as e:
        not_computable(f"cannot read {JOB}/answers.jsonl: {e}")
        return
    main_p, alt_p = {}, {}
    ex = None
    for r in rows:
        text = r.get("text") or ""
        ms = list(SW.finditer(text))
        wrong = r.get("score_v3") != 1
        if len(ms) == 1:
            p = ms[0].start()
            main_p.setdefault(r["problem_index"], []).append((wrong, (len(text) - p) < p))
            if ex is None:
                ex = r
        if ms:  # alt reading: rows with >= 1 match, position of the last switch
            p = ms[-1].start()
            alt_p.setdefault(r["problem_index"], []).append((wrong, (len(text) - p) < p))

    def diff(sample):
        w = [sf for rs in sample for wr, sf in rs if wr]
        g = [sf for rs in sample for wr, sf in rs if not wr]
        fw = sum(w) / len(w) if w else 0.0  # empty group inside a resample: share taken as 0
        fr = sum(g) / len(g) if g else 0.0
        return fw - fr

    problems = [main_p[k] for k in sorted(main_p)]
    n_w = sum(1 for rs in problems for wr, _ in rs if wr)
    n_r = sum(1 for rs in problems for wr, _ in rs if not wr)
    print(json.dumps({"groups": {"finished-wrong rows with one switch": n_w, "right rows with one switch": n_r,
                                 "problems with a kept row": len(problems)}}))
    if n_w < 10 or n_r < 10:
        refuted_without_number()
        return
    alt_problems = [alt_p[k] for k in sorted(alt_p)]
    alt_w = sum(1 for rs in alt_problems for wr, _ in rs if wr)
    alt_r = sum(1 for rs in alt_problems for wr, _ in rs if not wr)
    alt_val = diff(alt_problems) if alt_w and alt_r else None
    val = diff(problems)
    report(val, min(n_w, n_r), bootstrap(diff, problems), "bootstrap", refuted_by_met=val < -0.03,
           alt_measured=alt_val, example_row=slim(ex))


main()
