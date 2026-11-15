"""Shared helpers for the independent recomputation of round-04 predictions (r4-m10 p1,2,3,5; r4-m01 p2,3,4).

Row files are fetched by fetch.sh into runs/replication/ (not committed)."""
import json
import random
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
ROWS = ROOT / "runs" / "replication"


def rows(name):
    return [json.loads(line) for line in open(ROWS / name)]


def first_sample0(name, key="problem_index"):
    """Rows with sample == 0; first row in file order per key."""
    out = {}
    for r in rows(name):
        if r["sample"] == 0 and r[key] not in out:
            out[r[key]] = r
    return out


def cap_hit(r):
    """Recipe: the boolean cap_hit; if missing, finish_reason == 'length' counts as a cap hit."""
    if "cap_hit" in r and r["cap_hit"] is not None:
        return bool(r["cap_hit"])
    return r["finish_reason"] == "length"


def ratio(s, level=None):
    b = s.encode("utf-8")
    c = zlib.compress(b) if level is None else zlib.compress(b, level)
    return len(c) / len(b)


def auroc(scores, labels):
    """Mann-Whitney AUROC of score for label True; ties count 0.5."""
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return None
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p > n else 0.5 if p == n else 0.0
    return wins / (len(pos) * len(neg))


def bootstrap(items, stat, n=2000, seed=0):
    """Percentile 90 % interval of stat over resamples of items (with replacement)."""
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        v = stat([items[rng.randrange(len(items))] for _ in items])
        if v is not None:
            vals.append(v)
    vals.sort()
    return [vals[int(0.05 * len(vals))], vals[int(0.95 * len(vals)) - 1]]


def paired_rate_diff(a, b, keys):
    """Fraction of keys with cap hit in a minus in b, with paired bootstrap 90 % interval over keys."""
    pairs = [(int(cap_hit(a[k])), int(cap_hit(b[k]))) for k in keys]
    diff = lambda ps: sum(x - y for x, y in ps) / len(ps)
    return {
        "value": diff(pairs),
        "n": len(pairs),
        "cap_hits_A": sum(x for x, _ in pairs),
        "cap_hits_B": sum(y for _, y in pairs),
        "interval_90": bootstrap(pairs, diff),
    }
