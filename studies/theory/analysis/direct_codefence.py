"""Direct test codefence-01 (theory round 14): the cued base's Code-cue pass rate on the problems where Think-SFT
(Code cue) wrote no fenced code block. Shared test of rival pairs round-14/s1 and round-14/s2.

uv run python studies/theory/analysis/direct_codefence.py <think-sft codecue answers.jsonl> <base codecue answers.jsonl>
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

OUT = Path("studies/theory/results/direct/codefence-01")
RANGES = {
    "round-14/s1": {"a": [0.72, 1.0], "b": [0.0, 0.46], "null": [0.52, 0.66]},
    "round-14/s2": {"a": [0.72, 1.0], "b": [0.0, 0.45], "null": [0.51, 0.67]},
}
NULL = 317 / 538
RAW_ROWS_READ = (
    "Read 10 of the 106 (every 11th): 7 are short answers (716-1,956 new tokens) that copy the prompt's template as "
    "'python / CODE / program / ```', missing only the template's opening fence line; the base passes 4 of these 7 "
    "problems. 2 are cap hits drifting into Chinese text (base fails both) and 1 is a 9,334-token answer ending in a bare "
    "program plus 'CODE'. Median length of the 106 is 1,343 new tokens against 2,020 for fenced answers."
)
# Unopened block: after the last </think>, a line that is only 'python' (the prompt template's form without its opening
# fence). This finds 99 of the 106; the posted 97 (README 'Think-SFT on the Code pair') was a hand count with no code
# rule, and the audit branch's extract_v2 rule finds 101, so the sub-split is reported, not checked.
UNOPENED = re.compile(r"^python[ \t]*$", re.M)


def load(path):
    rows = [json.loads(line) for line in open(path)]
    by_uid = {r["uid"]: r for r in rows}
    assert len(by_uid) == len(rows) == 538, (path, len(rows), len(by_uid))
    return rows, by_uid


def unopened(text):
    return bool(UNOPENED.search(text.rsplit("</think>", 1)[-1])) and "</think>" in text


def wilson(k, n, z=1.645):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [c - h, c + h]


def verdict(lo, hi, rng):
    out = {}
    for name, other in (("a", "b"), ("b", "a")):
        mine, theirs = rng[name], rng[other]
        if mine[0] <= lo and hi <= mine[1]:
            out[name] = "holds"
        elif theirs[0] <= lo and hi <= theirs[1]:
            out[name] = "refuted"
        elif hi < mine[0] or lo > mine[1]:
            out[name] = "refuted"
        else:
            out[name] = "undecided"
    return out


def main(sft_path, base_path):
    sft, _ = load(sft_path)
    _, base = load(base_path)
    # Instrument check: the posted counts (result-9d38d9, result-59ed1a, README 'Think-SFT on the Code pair').
    none = [r for r in sft if r["mode"] == "none"]
    checks = {
        "sft_passed": (sum(r["passed"] for r in sft), 301),
        "sft_no_block": (len(none), 106),
        "base_passed": (sum(r["passed"] for r in base.values()), 317),
        "base_no_block": (sum(r["mode"] == "none" for r in base.values()), 34),
    }
    for k, (got, want) in checks.items():
        assert got == want, (k, got, want)

    x = np.array([base[r["uid"]]["passed"] for r in none], dtype=float)
    n = len(x)
    stat = x.mean()
    rng = np.random.default_rng(0)
    boot = x[rng.integers(0, n, size=(10_000, n))].mean(axis=1)
    lo, hi = np.percentile(boot, [5, 95])
    wl = wilson(int(x.sum()), n)

    unop = np.array([base[r["uid"]]["passed"] for r in none if unopened(r["text"])], dtype=float)
    other = np.array([base[r["uid"]]["passed"] for r in none if not unopened(r["text"])], dtype=float)
    fenced = np.array([base[r["uid"]]["passed"] for r in sft if r["mode"] != "none"], dtype=float)
    bench = {}
    for b in ("humanevalplus", "mbppplus"):
        sel = [r for r in none if r["bench"] == b]
        allb = [r for r in base.values() if r["bench"] == b]
        bench[b] = {"n_none": len(sel), "base_passed_on_none": sum(base[r["uid"]]["passed"] for r in sel),
                    "base_rate_all": sum(r["passed"] for r in allb) / len(allb)}

    verdicts = {pair: verdict(lo, hi, rr) for pair, rr in RANGES.items()}
    verdicts_wilson = {pair: verdict(wl[0], wl[1], rr) for pair, rr in RANGES.items()}
    metrics = {
        "statistic": "r_U = share of Think-SFT Code-cue problems with no fenced code block (stored mode 'none') whose "
                     "cued-base Code-cue row passed",
        "value": stat,
        "passes": int(x.sum()),
        "n": n,
        "ci90_bootstrap": [lo, hi],
        "ci90_wilson": wl,
        "null_value": NULL,
        "ranges": RANGES,
        "verdict": verdicts,
        "verdict_if_wilson": verdicts_wilson,
        "unopened_bare_python_line": {"n": len(unop), "passes": int(unop.sum()), "rate": unop.mean()},
        "other": {"n": len(other), "passes": int(other.sum()), "rate": other.mean()},
        "fenced_432_complement": {"n": len(fenced), "passes": int(fenced.sum()), "rate": fenced.mean()},
        "by_bench": bench,
        "raw_rows_read": RAW_ROWS_READ,
        "instrument_checks": {k: v[0] for k, v in checks.items()},
        "files": [sft_path, base_path],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")

    keep = ["uid", "bench", "mode", "passed", "exit", "n_new", "cap_hit", "finish_reason"]
    yes = next(r for r in none if base[r["uid"]]["passed"])
    no = next(r for r in none if not base[r["uid"]]["passed"])
    examples = []
    for tag, r in (("counts (base passes)", yes), ("does not count (base fails)", no)):
        b = base[r["uid"]]
        examples.append({
            "role": tag,
            "think_sft": {**{k: r[k] for k in keep}, "answer_tail": r["text"].rsplit("</think>", 1)[-1][-1500:]},
            "base": {**{k: b[k] for k in keep}, "code": b["code"]},
        })
    (OUT / "examples.json").write_text(json.dumps(examples, indent=1) + "\n")
    print(json.dumps({k: metrics[k] for k in ("value", "passes", "n", "ci90_bootstrap", "ci90_wilson", "verdict",
                                              "verdict_if_wilson", "unopened_bare_python_line", "other",
                                              "fenced_432_complement", "by_bench")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
