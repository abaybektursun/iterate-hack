"""r6-m05 p1: R(d >= 1500) / R(d < 200), T2 (RL, plain) over T1 (base, cue), MATH-500, cap hits excluded.
HALF = False: exposure and events over the whole text. (p3 is the same code with HALF = True.)"""
import bisect, json, math, os, re, subprocess, sys
from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

HALF = False
FILES = {
    "base": ("runs/theory-rows/s3k/r4/base_rl-02/out/T1.jsonl",
             "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl"),
    "rl": ("runs/theory-rows/s3k/r4/modal_t2-01/t2/T2.jsonl",
           "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t2-01/t2/T2.jsonl"),
}
BINS = [(0, 200), (200, 600), (600, 1500), (1500, math.inf)]
COMMA = re.compile(r"(?<=\d),(?=\d{3})")
EQ = re.compile(r"=\s*-?\d+(?:\.\d+)?")
EVENT = re.compile(r"(?<![A-Za-z])(Wait|Hmm)(?![A-Za-z])")


def fetch(local, s3):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", s3, local, "--profile", "iterate-ecr"], check=True)


def load(local):
    rows = []
    with open(local) as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def result_positions(t):
    pos = [m.end() for m in EQ.finditer(t)]
    start = 0
    while True:
        j = t.find("\\boxed{", start)
        if j < 0:
            break
        k = j + len("\\boxed{")
        depth, close = 1, None
        while k < len(t):
            c = t[k]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    close = k
                    break
            k += 1
        if close is not None:
            pos.append(close + 1)
        start = j + 1  # every occurrence, including nested ones
    return sorted(set(pos))


def bin_of(d):
    for b, (lo, hi) in enumerate(BINS):
        if lo <= d < hi:
            return b
    raise ValueError(d)


def row_counts(text):
    """(exposure[4], events[4]) for one kept row."""
    t = COMMA.sub("", text)
    n = len(t)
    limit = math.ceil(n / 2) if HALF else n  # integer i < n/2  <=>  i < ceil(n/2)
    pos = result_positions(t)
    origins = sorted(set([0] + [p for p in pos if p <= n]))  # d(i) = i when no result <= i: origin 0
    exp = [0, 0, 0, 0]
    for a, o in enumerate(origins):
        end = origins[a + 1] if a + 1 < len(origins) else n
        end = min(end, limit)
        L = end - o  # indices o..end-1 have d = 0..L-1
        if L <= 0:
            continue
        for b, (lo, hi) in enumerate(BINS):
            hi2 = min(hi, L)
            if hi2 > lo:
                exp[b] += int(hi2 - lo)
    ev = [0, 0, 0, 0]
    for m in EVENT.finditer(t):
        s = m.start()
        if s >= limit:
            continue
        o = origins[bisect.bisect_right(origins, s) - 1]
        ev[bin_of(s - o)] += 1
    return exp, ev


def kept(r):
    return r is not None and r.get("cap_hit") is False and isinstance(r.get("text"), str) and r["text"] != ""


def main():
    data = {}
    for m, (local, s3) in FILES.items():
        try:
            fetch(local, s3)
            data[m] = load(local)
        except Exception as e:
            return not_computable(f"cannot read {local}: {e}")
        for r in data[m]:
            if "cap_hit" not in r or "text" not in r or "unique_id" not in r:
                return not_computable(f"{local}: row without cap_hit/text/unique_id")
    by = {m: {r["unique_id"]: r for r in rows} for m, rows in data.items()}
    ids = sorted(set(by["base"]) | set(by["rl"]))
    # one entry per problem: (base counts or None, rl counts or None, both_kept)
    problems = []
    example = None
    for u in ids:
        entry = []
        for m in ("base", "rl"):
            r = by[m].get(u)
            if kept(r):
                entry.append(row_counts(r["text"]))
                if example is None:
                    example = r
            else:
                entry.append(None)
        problems.append((entry[0], entry[1]))

    def totals(sample, paired):
        tot = {m: ([0] * 4, [0] * 4) for m in (0, 1)}
        for p in sample:
            if paired and (p[0] is None or p[1] is None):
                continue
            for m in (0, 1):
                if p[m] is not None:
                    for b in range(4):
                        tot[m][0][b] += p[m][0][b]
                        tot[m][1][b] += p[m][1][b]
        return tot

    def compute(sample, paired=False):
        """Returns the statistic, or None if undefined (counts as refuted)."""
        tot = totals(sample, paired)
        (be, bv), (re_, rv) = tot[0], tot[1]
        if be[0] == 0 or be[3] == 0 or bv[0] == 0 or bv[3] == 0:  # base rate in B1 or B4 is 0 (or undefined)
            return None
        if HALF and re_[3] == 0:  # T2 exposure in B4 is 0
            return None
        if re_[0] == 0:
            return None
        rate = lambda ev, ex, b: 1000.0 * ev[b] / ex[b]
        R1 = rate(rv, re_, 0) / rate(bv, be, 0)
        R4 = rate(rv, re_, 3) / rate(bv, be, 3)
        if R1 == 0:
            return None
        return R4 / R1

    main_val = compute(problems)
    if main_val is None:
        return refuted_without_number()
    alt = compute(problems, paired=True)

    def stat(sample):
        v = compute(sample)
        return math.inf if v is None else v  # undefined resample: +inf (sorts to the top)

    interval = bootstrap(stat, problems)
    ex = dict(example)
    ex["text"] = ex["text"][:300] + ("...[truncated]" if len(ex["text"]) > 300 else "")
    report(main_val, len(problems), interval, "bootstrap", refuted_by_met=False, alt_measured=alt, example_row=ex)


if __name__ == "__main__":
    main()
