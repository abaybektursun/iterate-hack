"""r8-m09 prediction 2: layout-row rate per finished Think-SFT answer on Hard problems (cued base k <= 1 of 4) minus
the rate on Easy problems (k == 4), pooled over 4 hard328 and 4 MATH-500 Think-SFT files."""
import json
import os
import subprocess

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable

SETS = {
    "hard328": (["abaybektursun-1115-000503-1e5f", "abaybektursun-1115-000525-ea4e",
                 "abaybektursun-1115-014823-ef56", "abaybektursun-1115-014833-1daa"],
                "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl"),
    "math500": (["abaybektursun-1115-000512-ee03", "abaybektursun-1115-014843-85d9",
                 "abaybektursun-1115-000607-0e92", "abaybektursun-1115-000621-1d7e"],
                "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"),
}


def fetch(job):
    path = os.path.join("runs", "theory-tests", job, "answers.jsonl")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", path], check=True)
    return path


def read_rows(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def load_first(path):
    out = {}
    for r in read_rows(path):
        if r.get("problem_index") not in out:
            out[r.get("problem_index")] = r
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


def base_k(rows):
    first = {}
    for r in rows:
        if r.get("attempt") != 0 or r.get("sample") not in (0, 1, 2, 3):
            continue
        key = (r.get("problem_index"), r.get("sample"))
        if key not in first:
            first[key] = r
    pis = {r.get("problem_index") for r in rows}
    k = {}
    for pi in pis:
        k[pi] = sum(1 for s in range(4)
                    if (pi, s) in first and first[(pi, s)].get("score_v3") == 1
                    and first[(pi, s)].get("cap_hit") is not True)
    return k


def main():
    entries = []  # (stratum, ((layout_main, layout_alt), ...) over finished rows of that problem)
    example = None
    for name, (jobs, base_path) in SETS.items():
        try:
            files = [load_first(fetch(j)) for j in jobs]
            base = read_rows(base_path)
        except Exception as e:  # noqa: BLE001
            not_computable(f"cannot read a {name} file: {e}")
            return
        ks = base_k(base)
        for pi, k in ks.items():
            if k == 4:
                stratum = "Easy"
            elif k <= 1:
                stratum = "Hard"
            else:
                continue
            fin = []
            for rows in files:
                r = rows.get(pi)
                if r is None or not finished(r):
                    continue
                if "text" not in r or "gold" not in r:
                    not_computable("Think-SFT row lacks text or gold")
                    return
                lm = la = 0
                if wrong(r):
                    c = candidate(r["text"])
                    lm = int(bool(c) and rln4_lib.agree(c, r["gold"]))
                    la = int(bool(c) and rln4_lib.agree(r["gold"], c))
                    if lm and example is None:
                        example = {kk: v for kk, v in r.items() if kk not in ("text", "prompt", "logprobs", "onsets")}
                        example["candidate"], example["base_k"] = c, k
                fin.append((lm, la))
            if fin:
                entries.append((stratum, tuple(fin)))

    def rates(sample, idx):
        num = {"Hard": 0, "Easy": 0}
        den = {"Hard": 0, "Easy": 0}
        for st, fin in sample:
            den[st] += len(fin)
            num[st] += sum(x[idx] for x in fin)
        return num, den

    def stat_idx(sample, idx):
        num, den = rates(sample, idx)
        rh = num["Hard"] / den["Hard"] if den["Hard"] else 0.0
        re_ = num["Easy"] / den["Easy"] if den["Easy"] else 0.0
        return rh - re_

    def stat(sample):
        return stat_idx(sample, 0)

    num, den = rates(entries, 0)
    print(json.dumps({"groups": {"Hard": den["Hard"], "Easy": den["Easy"]}}))
    if den["Hard"] == 0 or den["Easy"] == 0:
        report(None, 0, None, "none", refuted_by_met=True)
        return
    m = stat(entries)
    if example is None:
        example = {"note": "no layout row found"}
    n = min(den["Hard"], den["Easy"])
    report(m, n, bootstrap(stat, entries), "bootstrap",
           refuted_by_met=(m > 0.014 or m < -0.010 or den["Hard"] < 150 or den["Easy"] < 150),
           alt_measured=stat_idx(entries, 1), example_row=example)


main()
