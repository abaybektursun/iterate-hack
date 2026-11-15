"""r6-m05 prediction 2: R_1 = rate_B1(T2) / rate_B1(T1), the RL/base hold-on rate ratio within 200 characters of the
last numeric result. Same files, filters, comma deletion, result positions, d(i) and events as prediction 1.
Undefined (refuted) if the T1 rate in B1 is 0. alt_measured: only problems where both models have a kept row.
"""
import bisect
import json
import math
import os
import re
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

FILES = {
    "T1": ("runs/theory-rows/s3k/r4/base_rl-02/out/T1.jsonl",
           "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl",
           "runs/theory-tests/s3k/r4/base_rl-02/out/T1.jsonl"),
    "T2": ("runs/theory-rows/s3k/r4/modal_t2-01/t2/T2.jsonl",
           "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t2-01/t2/T2.jsonl",
           "runs/theory-tests/s3k/r4/modal_t2-01/t2/T2.jsonl"),
}
BINS = [(0, 200), (200, 600), (600, 1500), (1500, math.inf)]
COMMA = re.compile(r"(?<=\d),(?=\d{3})")
EQ = re.compile(r"=\s*-?\d+(?:\.\d+)?")
EVENT = re.compile(r"(?<![A-Za-z])(Wait|Hmm)(?![A-Za-z])")
BOX = "\\boxed{"


def locate(name):
    primary, s3, local = FILES[name]
    for p in (primary, local):
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    os.makedirs(os.path.dirname(local), exist_ok=True)
    r = subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr"], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(local):
        return None
    return local


def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def result_positions(text):
    pos = set(m.end() for m in EQ.finditer(text))
    start = text.find(BOX)
    while start != -1:
        j = start + len(BOX)
        depth = 1
        while j < len(text) and depth > 0:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        if depth == 0:
            pos.add(j)  # index just after the closing '}'
        start = text.find(BOX, start + 1)
    return sorted(pos)


def bin_of(d):
    for b, (lo, hi) in enumerate(BINS):
        if lo <= d < hi:
            return b
    raise ValueError(d)


def count_row(row):
    """Per-bin (exposure, events) for one kept row; None if the row contributes nothing."""
    text = row.get("text")
    if not isinstance(text, str) or text == "":
        return None
    text = COMMA.sub("", text)
    L = len(text)
    res = [r for r in result_positions(text) if r <= L]
    starts = [0] + [r for r in res if r > 0]
    ends = starts[1:] + [L]
    exposure = [0, 0, 0, 0]
    for s, e in zip(starts, ends):
        n = e - s  # d runs over 0 .. n-1 in this segment
        if n <= 0:
            continue
        for b, (lo, hi) in enumerate(BINS):
            top = n if hi == math.inf else min(n, hi)
            if top > lo:
                exposure[b] += top - lo
    events = [0, 0, 0, 0]
    for m in EVENT.finditer(text):
        s = m.start()
        k = bisect.bisect_right(res, s)
        d = s - res[k - 1] if k > 0 else s
        events[bin_of(d)] += 1
    return exposure, events


CACHE = {}


def counts(row):
    if row is None:
        return None
    key = id(row)
    if key not in CACHE:
        CACHE[key] = count_row(row)
    return CACHE[key]


def pooled(sample, which):
    exp, ev = [0, 0, 0, 0], [0, 0, 0, 0]
    for pair in sample:
        c = counts(pair[which])
        if c is None:
            continue
        for b in range(4):
            exp[b] += c[0][b]
            ev[b] += c[1][b]
    return exp, ev


def compute(sample):
    """Returns R_1, or None when undefined."""
    e1, v1 = pooled(sample, 0)
    e2, v2 = pooled(sample, 1)
    if e1[0] == 0 or v1[0] == 0 or e2[0] == 0:
        return None  # T1 rate in B1 is 0 (or a B1 rate has no exposure)
    return (1000.0 * v2[0] / e2[0]) / (1000.0 * v1[0] / e1[0])


def stat(sample):
    v = compute(sample)
    # An undefined resample (T1 B1 rate 0) counts as refuted; it is placed at +inf (a refuting value above 1.3).
    # With pooled B1 counts over hundreds of rows it cannot practically occur.
    return math.inf if v is None else v


def main():
    data = {}
    for name in ("T1", "T2"):
        p = locate(name)
        if p is None:
            not_computable(f"{name} row file is not readable (local copy missing and aws s3 cp failed)")
            return
        rows = load(p)
        if not rows or "text" not in rows[0] or "cap_hit" not in rows[0] or "problem_index" not in rows[0]:
            not_computable(f"{name} rows lack text, cap_hit or problem_index")
            return
        data[name] = rows
    kept = {}
    for name, rows in data.items():
        kept[name] = {}
        for r in rows:
            if r.get("cap_hit") is False and isinstance(r.get("text"), str) and r["text"] != "":
                kept[name].setdefault(r["problem_index"], r)
    problems = sorted(set(kept["T1"]) | set(kept["T2"]))
    sample = [(kept["T1"].get(p), kept["T2"].get(p)) for p in problems]
    measured = compute(sample)
    if measured is None:
        refuted_without_number()
        return
    paired = [s for s in sample if s[0] is not None and s[1] is not None]
    alt = compute(paired)
    interval = bootstrap(stat, sample)
    ex = dict(next(s[1] for s in sample if s[1] is not None))
    ex["text"] = ex["text"][:400] + " ...[truncated]"
    if isinstance(ex.get("answer_tokens"), list):
        ex["answer_tokens"] = ex["answer_tokens"][:10]
    report(measured, len(sample), interval, "bootstrap",
           refuted_by_met=(measured > 1.3 or measured < 0.75), alt_measured=alt, example_row=ex)


if __name__ == "__main__":
    main()
