"""r8-m09 prediction 1: share of Think-SFT cue finished, v3-wrong hard328 answers whose candidate after the last
'Answer:' (or the last non-empty line) agrees with gold. Pooled over 4 single-sample jobs."""
import json
import os
import subprocess

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable

JOBS = ["abaybektursun-1115-000503-1e5f", "abaybektursun-1115-000525-ea4e",
        "abaybektursun-1115-014823-ef56", "abaybektursun-1115-014833-1daa"]


def fetch(job):
    path = os.path.join("runs", "theory-tests", job, "answers.jsonl")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", path], check=True)
    return path


def load_first(path):
    out = {}
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            pi = r.get("problem_index")
            if pi not in out:
                out[pi] = r
    return out


def finished(r):
    return r.get("cap_hit") is not True and r.get("finish_reason") != "length"


def wrong(r):
    return r.get("score_v3") != 1


def last_boxed_content(c):
    i = c.rfind("\\boxed{")
    j = i + len("\\boxed{")
    depth, k = 1, j
    while k < len(c) and depth:
        depth += {"{": 1, "}": -1}.get(c[k], 0)
        k += 1
    return c[j:k - 1] if depth == 0 else c[j:]


def candidate(text):
    text = text or ""
    if "Answer:" in text:
        s = text[text.rfind("Answer:") + len("Answer:"):]
        parts = [p for p in s.split("\n") if p.strip()]
        c = parts[0] if parts else ""
    else:
        parts = [p for p in text.split("\n") if p.strip()]
        c = parts[-1] if parts else ""
    c = c.strip()
    c = c.replace("$", "").replace("*", "")
    if c.startswith("\\[") or c.startswith("\\("):
        c = c[2:]
    if c.endswith("\\]") or c.endswith("\\)"):
        c = c[:-2]
    if c.endswith("."):
        c = c[:-1]
    if "\\boxed{" in c:
        c = last_boxed_content(c)
    return c


def main():
    files = []
    for job in JOBS:
        try:
            files.append(load_first(fetch(job)))
        except Exception as e:  # noqa: BLE001
            not_computable(f"cannot read {job}/answers.jsonl: {e}")
            return
    for rows in files:
        for r in rows.values():
            if "text" not in r or "gold" not in r:
                not_computable("row lacks text or gold field")
                return
    # per-problem entries: list of (counted_main, counted_alt) for each finished wrong row of that problem
    problems = sorted(set().union(*[set(f) for f in files]), key=lambda x: (x is None, x))
    entries, example = [], None
    for pi in problems:
        e = []
        for rows in files:
            r = rows.get(pi)
            if r is None or not finished(r) or not wrong(r):
                continue
            c = candidate(r["text"])
            main_ok = bool(c) and rln4_lib.agree(c, r["gold"])
            alt_ok = bool(c) and rln4_lib.agree(r["gold"], c)
            e.append((int(main_ok), int(alt_ok)))
            if example is None and main_ok:
                example = {k: v for k, v in r.items() if k not in ("text", "prompt", "logprobs", "onsets")}
                example["candidate"] = c
        if e:
            entries.append(tuple(e))
    n_fw = sum(len(e) for e in entries)
    if n_fw == 0:
        report(None, 0, None, "none", refuted_by_met=True)
        return

    def stat(sample):
        d = sum(len(e) for e in sample)
        return sum(x[0] for e in sample for x in e) / d if d else 0.0

    def stat_alt(sample):
        d = sum(len(e) for e in sample)
        return sum(x[1] for e in sample for x in e) / d

    m = stat(entries)
    if example is None:
        for rows in files:
            for r in rows.values():
                if finished(r) and wrong(r):
                    example = {k: v for k, v in r.items() if k not in ("text", "prompt", "logprobs", "onsets")}
                    break
            if example:
                break
    report(m, n_fw, bootstrap(stat, entries), "bootstrap", refuted_by_met=(m < 0.025 or n_fw < 40),
           alt_measured=stat_alt(entries), example_row=example)


main()
