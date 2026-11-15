"""k=2: base / RL switch-marker rate per token on finished MATH-500 rows at T 1.0."""
import json
import math
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

JOBS = {"base": "abaybektursun-1114-153825-208b", "rl": "abaybektursun-1114-183640-e828"}
SW = re.compile(r"(?<![A-Za-z])(Alternatively|Another approach|Another way|Let me try (?:a )?(?:different|another)"
                r"|Let's try (?:a )?(?:different|another)|Instead, let)")


def path_for(job):
    for p in (f"runs/theory-rows/{job}/answers.jsonl", f"runs/theory-tests/{job}/answers.jsonl"):
        if os.path.exists(p):
            return p
    p = f"runs/theory-tests/{job}/answers.jsonl"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", p], check=True)
    return p


def load(job):
    seen, kept = set(), []
    with open(path_for(job)) as f:
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
            seen.add(key)  # first row per (problem_index, sample) in file order, before the finished filter
            if r.get("cap_hit") is True or r.get("finish_reason") == "length":
                continue
            kept.append(r)
    return kept


def S(r):
    return len(SW.findall(r.get("text") or ""))


def ratio(base_rows, rl_rows, tkey):
    sb, tb = sum(S(r) for r in base_rows), sum(r[tkey] for r in base_rows)
    sr, tr = sum(S(r) for r in rl_rows), sum(r[tkey] for r in rl_rows)
    if sr == 0:
        return None if sb == 0 else math.inf  # None = refuted case (both zero)
    if tb == 0 or tr == 0:
        return None
    return (sb / tb) / (sr / tr)


def main():
    try:
        rows = {g: load(j) for g, j in JOBS.items()}
    except Exception as e:  # noqa: BLE001
        not_computable(f"row file not readable: {e}")
        return
    for g in rows:
        for r in rows[g]:
            if "text" not in r or not isinstance(r.get("n_new"), (int, float)):
                not_computable(f"{g} row lacks text or n_new")
                return

    by_prob = {}
    for g in ("base", "rl"):
        for r in rows[g]:
            by_prob.setdefault(r["problem_index"], {"base": [], "rl": []})[g].append(r)
    problems = [(v["base"], v["rl"]) for _, v in sorted(by_prob.items())]

    def stat_for(tkey):
        def stat(sample):
            b = [r for pb, _ in sample for r in pb]
            l = [r for _, pl in sample for r in pl]
            v = ratio(b, l, tkey)
            return math.nan if v is None else v
        return stat

    measured = ratio(rows["base"], rows["rl"], "n_new")
    n_base = len({r["problem_index"] for r in rows["base"]})
    n_rl = len({r["problem_index"] for r in rows["rl"]})
    print(json.dumps({"groups": {"base_problems": n_base, "rl_problems": n_rl,
                                 "base_rows": len(rows["base"]), "rl_rows": len(rows["rl"])}}))
    if measured is None:
        refuted_without_number()
        return
    alt = ratio(rows["base"], rows["rl"], "n_generated") if all("n_generated" in r for g in rows for r in rows[g]) else None
    interval = bootstrap(stat_for("n_new"), problems)
    ex = dict(next(r for r in rows["base"] if S(r) > 0) if any(S(r) > 0 for r in rows["base"]) else rows["base"][0])
    ex = {k: ex.get(k) for k in ("cell", "problem_index", "sample", "attempt", "n_new", "n_generated", "cap_hit",
                                 "finish_reason", "score_v3")} | {"S": S(ex), "text_head": (ex.get("text") or "")[:200]}
    report(measured, min(n_base, n_rl), interval, "bootstrap",
           refuted_by_met=False, alt_measured=alt, example_row=ex)


main()
