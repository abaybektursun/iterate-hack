"""k=1: plain-base T 1.0 (T3) wrong rate on Q = top8 plain quick finished-wrong problems."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, binomial, report, not_computable

TOP8 = pathlib.Path("studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json")
T3_KEY = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
T3 = pathlib.Path("runs/theory-tests/s3k/r4/modal_t3-01/t3/T3.jsonl")


def fetch(key, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", key, str(path), "--profile", "iterate-ecr", "--only-show-errors"], check=False)
    return path.exists() and path.stat().st_size > 0


def slim(r):
    out = {k: v for k, v in r.items() if k not in ("prefill_ids", "answer_tokens", "cut_ids")}
    if isinstance(out.get("text"), str) and len(out["text"]) > 400:
        out["text"] = out["text"][:400] + "...[truncated]"
    return out


def main():
    if not TOP8.exists():
        return not_computable(f"{TOP8} not readable")
    if not fetch(T3_KEY, T3):
        return not_computable(f"{T3_KEY} could not be fetched")
    top8 = json.loads(TOP8.read_text())
    first = {}
    for r in top8:
        if r.get("score_v3") is None:
            continue
        first.setdefault(r["problem_index"], r)
    Q = [i for i, r in first.items() if r["score_v3"] == 0 and r["cap_hit"] is False and r["n_generated"] <= 2000]

    t3 = {}
    for line in T3.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            t3.setdefault(r["problem_index"], r)

    entries = []  # (wrong main, wrong alt, row)
    for i in Q:
        if i not in t3:
            continue
        r = t3[i]
        s = R.grade_v3(r["gold"], r["text"])["score_v3"]
        cap = bool(r.get("cap_hit"))
        entries.append((int(s == 0 or cap), int(s == 0), r))
    if not entries:
        return not_computable("no problem in Q has a T3 row")

    def stat(sample):
        return sum(e[0] for e in sample) / len(sample)

    def stat_alt(sample):
        return sum(e[1] for e in sample) / len(sample)

    m = stat(entries)
    report(m, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False,
           alt_measured=stat_alt(entries), example_row=slim(entries[0][2]))


main()
