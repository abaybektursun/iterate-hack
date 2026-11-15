"""r3-across-2 prediction 5: fraction of the base-to-RL hold-on rate increase reached by theta(0.25), cued, T 1.0.

Files: S3 T1.jsonl (base cue, a = 0), iterate-runs abaybektursun-1114-153102-b029 (theta0.25_cue) and
abaybektursun-1114-153110-e985 (rl_cue). One row per problem_index (highest attempt if duplicated); keep cap_hit false.
Rate = case-sensitive \\b(Wait|Hmm)\\b matches / total text characters x 10,000, pooled.
Statistic = (rate(theta0.25) - rate(T1)) / (rate(rl_cue) - rate(T1)). Refuted if below 0.35.
"""
import json
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

D = "runs/theory-tests/r3-across-2"
PAT = re.compile(r"\b(Wait|Hmm)\b")
T1 = ("s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl", f"{D}/T1.jsonl")
JOBS = {"theta0.25_cue": "abaybektursun-1114-153102-b029", "rl_cue": "abaybektursun-1114-153110-e985"}


def read(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def load_t1():
    uri, path = T1
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr"], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return read(path)


def load_job(job):
    path = f"{D}/{job}/answers.jsonl"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", path], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return read(path)


def dedup(rows):
    best = {}
    for r in rows:
        k = r["problem_index"]
        if k not in best or r.get("attempt", 0) >= best[k].get("attempt", 0):
            best[k] = r
    return best


def rate(rows):
    chars = sum(len(r["text"]) for r in rows)
    hits = sum(len(PAT.findall(r["text"])) for r in rows)
    return float("nan") if chars == 0 else hits / chars * 10000


def main():
    files = {"T1": load_t1()}
    for arm, job in JOBS.items():
        files[arm] = load_job(job)
    for name, rows in files.items():
        if rows is None:
            return not_computable(f"{name} row file not readable")
        if any(("text" not in r) or ("cap_hit" not in r) or ("problem_index" not in r) for r in rows):
            return not_computable(f"{name} rows lack text, cap_hit or problem_index")
    one = {name: dedup(rows) for name, rows in files.items()}
    kept = {name: {k: r for k, r in d.items() if r["cap_hit"] is False} for name, d in one.items()}

    keys = sorted(set().union(*[set(d) for d in one.values()]))
    problems = [tuple(kept[name].get(k) for name in ("T1", "theta0.25_cue", "rl_cue")) for k in keys]

    def stat(sample):
        r0 = rate([p[0] for p in sample if p[0] is not None])
        rq = rate([p[1] for p in sample if p[1] is not None])
        r1 = rate([p[2] for p in sample if p[2] is not None])
        den = r1 - r0
        if den != den or rq != rq or den == 0:
            return float("nan")
        return (rq - r0) / den

    measured = stat(problems)
    # other reading: only problems finished (cap_hit false) in all three files
    common = [p for p in problems if all(x is not None for x in p)]
    alt = stat(common) if common else None

    sizes = {name: len(d) for name, d in kept.items()}
    print(json.dumps({"groups": {f"{n} kept (cap_hit false)": s for n, s in sizes.items()}}))
    ex = dict(kept["theta0.25_cue"][min(kept["theta0.25_cue"])])
    ex["text"] = ex["text"][:300]
    ex.pop("prompt", None)
    report(measured, min(sizes.values()), bootstrap(stat, problems), "bootstrap",
           refuted_by_met=(measured == measured and measured < 0.35), alt_measured=alt, example_row=ex)


if __name__ == "__main__":
    main()
