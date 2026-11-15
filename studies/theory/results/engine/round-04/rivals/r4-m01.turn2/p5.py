"""k=5: Spearman rho between opening compressibility (zlib ratio of text[:3000])
and rule-A loop onset (onset_A_char) among base cue T0.6/top-p1.0 loops with onset >= 4000."""
import json
import os
import subprocess
import sys
import zlib

import numpy as np

ROOT = os.getcwd()
DIR = os.path.join(ROOT, "runs", "theory-tests", "duel-r4-m01.turn2")
JOB = "abaybektursun-1114-151718-d4fa"


def out(measured, refuted, alt, nc, example):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": example}))


def short(row):
    return {k: (v[:300] + "...[truncated]" if isinstance(v, str) and len(v) > 300 else v)
            for k, v in row.items()}


def fetch():
    path = os.path.join(DIR, f"{JOB}_answers.jsonl")
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        os.makedirs(DIR, exist_ok=True)
        if os.path.exists(path):
            os.remove(path)
        r = subprocess.run(["modal", "volume", "get", "iterate-runs", f"{JOB}/answers.jsonl", path],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            raise RuntimeError(f"cannot fetch iterate-runs:{JOB}/answers.jsonl: {r.stderr.strip()}")
    return path


def avg_ranks(x):
    """Ranks 1..n with ties given the average rank (as scipy.stats.rankdata 'average')."""
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    ranks = np.empty(len(x), dtype=float)
    i = 0
    n = len(x)
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def spearman(a, b):
    """Same as scipy.stats.spearmanr(a, b).correlation: Pearson r of average ranks."""
    ra, rb = avg_ranks(a), avg_ranks(b)
    ra -= ra.mean()
    rb -= rb.mean()
    den = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if den == 0:
        return None
    return float((ra * rb).sum() / den)


def ratio(text):
    b = text[:3000].encode("utf-8")
    return len(zlib.compress(b, 9)) / len(b)


def onset_ok(r):
    o = r.get("onset_A_char")
    return isinstance(o, (int, float)) and not isinstance(o, bool) and o >= 4000


def main():
    try:
        path = fetch()
        rows = [json.loads(l) for l in open(path) if l.strip()]
    except Exception as e:  # noqa: BLE001
        out(None, False, None, f"file not readable: {e}", None)
        return
    for fld in ("loop_A", "onset_A_char", "text"):
        if not any(fld in r for r in rows):
            out(None, False, None, f"field {fld} missing in rows", None)
            return

    kept = [r for r in rows if r.get("loop_A") is True and onset_ok(r)]
    # alt reading: onset_A_char present and >= 4000, without requiring the loop_A flag
    kept_alt = [r for r in rows if onset_ok(r)]
    print(f"rows: {len(rows)}; kept: {len(kept)}; kept (alt, no loop_A requirement): {len(kept_alt)}",
          file=sys.stderr)
    print(f"kept_rows={len(kept)} kept_rows_alt={len(kept_alt)}")

    def rho(rs):
        if len(rs) < 2:
            return None
        s = [ratio(r["text"]) for r in rs]
        o = [float(r["onset_A_char"]) for r in rs]
        return spearman(s, o)

    m = rho(kept)
    alt = rho(kept_alt)
    if m is None or (isinstance(m, float) and np.isnan(m)):
        out(None, False, None,
            f"Spearman undefined: {len(kept)} kept rows (fewer than 2 or a constant variable)", None)
        return
    out(m, False, alt, None, short(kept[0]))


if __name__ == "__main__":
    main()
