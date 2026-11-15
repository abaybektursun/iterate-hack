"""Laptop side of the LLM arm: raw generations -> forecast CSV, and the same-cells comparison.

  python -I -B studies/gpuprice/jobs/llm_score.py parse <gen_variant.jsonl> <forecast.csv>
  python -I -B studies/gpuprice/jobs/llm_score.py compare <eval name> [<eval name> ...]

parse: one row per cell with at least MIN_OK parsed samples; other cells are left out (eval.sh scores them as last value)
and counted. A parsed value outside [last/3, 3 * last] counts as unparsed.
  sample, cot: empirical q10/q50/q90 of the sampled answers.
  quant: the median over samples of each stated quantile, sorted.
  prob: mean probabilities and median levels over samples (a missing level is accepted on a side with P <= 0.10); q50 leaves the last value only if one side has P > 0.5,
        q10 only if P(lower) > 0.10, q90 only if P(higher) > 0.10.
compare: pooled skill and in-band share of each named eval (runs/gpuprice/evals/<name>/cells.csv) on the cells that the
first one forecast (its forecast.csv).
"""
import json, re, sys
import numpy as np, pandas as pd

MIN_OK = 5
NUM = r"-?\d+(?:\.\d+)?"


def ok(x, m0):
    return x is not None and m0 / 3 <= x <= 3 * m0


def parse_one(variant, text, m0):
    """One sample -> a number (sample, cot) or a dict (quant, prob), or None."""
    if variant == "sample":
        m = re.fullmatch(rf"\s*\$?({NUM})\s*(?:USD.*)?", text.strip())
        x = float(m.group(1)) if m else None
        return x if ok(x, m0) else None
    if variant == "cot":
        m = re.findall(rf"ANSWER:\s*\**\s*\$?({NUM})", text)
        x = float(m[-1]) if m else None
        return x if ok(x, m0) else None
    m = re.search(r"\{.*?\}", text, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    keys = ("q10", "q50", "q90") if variant == "quant" else ("p_lower", "p_same", "p_higher", "level_if_lower", "level_if_higher")
    num = lambda k: isinstance(d.get(k), (int, float))
    if variant == "quant":
        return d if all(num(k) and ok(d[k], m0) for k in keys) else None
    if not all(num(k) for k in keys[:3]) or abs(d["p_lower"] + d["p_same"] + d["p_higher"] - 1) > 0.05:
        return None
    for side in ("lower", "higher"):          # the model writes null or 0 as the level of a side it gives no probability
        k = "level_if_" + side
        if not (num(k) and ok(d[k], m0)):
            if d["p_" + side] > 0.10:
                return None
            d[k] = float("nan")
    return d


def parse(src, dst):
    rows, dropped, n_samples, n_ok = [], 0, 0, 0
    for line in open(src):
        r = json.loads(line)
        m0, v = r["last_value"], r["variant"]
        s = [x for x in (parse_one(v, t, m0) for t in r["samples"]) if x is not None]
        n_samples += len(r["samples"]); n_ok += len(s)
        if len(s) < MIN_OK:
            dropped += 1
            continue
        if v in ("sample", "cot"):
            q = np.quantile(s, [0.1, 0.5, 0.9])
        elif v == "quant":
            q = np.sort([np.median([d[k] for d in s]) for k in ("q10", "q50", "q90")])
        else:
            pl, ph = np.mean([d["p_lower"] for d in s]), np.mean([d["p_higher"] for d in s])
            lv = {k: [d[k] for d in s if not np.isnan(d[k])] for k in ("level_if_lower", "level_if_higher")}
            lo = min(np.median(lv["level_if_lower"]), m0) if lv["level_if_lower"] else m0
            hi = max(np.median(lv["level_if_higher"]), m0) if lv["level_if_higher"] else m0
            q = [lo if pl > 0.10 else m0, lo if pl > 0.5 else hi if ph > 0.5 else m0, hi if ph > 0.10 else m0]
        rows.append((r["series_id"], r["origin_date"], r["horizon_days"], round(q[0], 6), round(q[1], 6), round(q[2], 6), len(s)))
    pd.DataFrame(rows, columns=["series_id", "origin_date", "horizon_days", "q10", "q50", "q90", "n_parsed"]).to_csv(dst, index=False)
    print(f"{src}: {len(rows)} cells written, {dropped} left out, {n_ok} of {n_samples} samples parsed -> {dst}")


def compare(names):
    key = ["series_id", "origin_date", "horizon_days"]
    mine = pd.read_csv(f"runs/gpuprice/evals/{names[0]}/forecast.csv")[key]
    for n in names:
        c = pd.read_csv(f"runs/gpuprice/evals/{n}/cells.csv").merge(mine, on=key)
        c = c[c.status == "scored"]
        band = ((c.q10 <= c.y) & (c.y <= c.q90)).mean()
        byh = {h: round(1 - g.loss.sum() / g.baseline_loss.sum(), 3) for h, g in c.groupby("horizon_days")}
        print(f"{n}: cells {len(c)}, pooled skill {1 - c.loss.sum() / c.baseline_loss.sum():+.3f}, by horizon {byh}, in band {band:.2f}")


if __name__ == "__main__":
    if sys.argv[1] == "parse":
        parse(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "compare":
        compare(sys.argv[2:])
    else:
        raise SystemExit(__doc__)
