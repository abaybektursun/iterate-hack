"""r7-m03 prediction 4: paired finished-answer error, plain T 1.0 (D = day1_3 math500_base_cue-01, attempt 0) minus the
entropy-gated arm hi6 (T 0.6 where entropy > 0.9 nats) (H = studies/rlneurons/results/egate/math500_hi6-01/rows.jsonl)."""
import json
from collections import OrderedDict

from studies.theory.lib.noise import bootstrap, report, not_computable

GATED = "studies/rlneurons/results/egate/math500_hi6-01/rows.jsonl"
DFILE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def is_cap(r):
    c = r.get("cap_hit")
    if c is None:  # missing
        return r.get("finish_reason") == "length"
    return c is True


def wrong(r):
    return 0 if r.get("score_v3") == 1 else 1


def pairs(G_rows, D_rows, shift):
    """For each (problem_index, sample) in the gated file, first gated row and first D row with attempt == 0 and
    D sample == gated sample - shift. Returns per-problem lists of kept (d_row, g_row) pairs."""
    first_g = OrderedDict()
    for r in G_rows:
        first_g.setdefault((r["problem_index"], r["sample"]), r)
    first_d = {}
    for r in D_rows:
        if r.get("attempt") == 0:
            first_d.setdefault((r["problem_index"], r["sample"]), r)
    by_problem = OrderedDict()
    for (pi, s), g in first_g.items():
        d = first_d.get((pi, s - shift))
        if d is None:
            continue
        if is_cap(d) or is_cap(g):
            continue
        by_problem.setdefault(pi, []).append((d, g))
    return by_problem


def stat(entries):
    ps = [p for e in entries for p in e]
    if not ps:
        return 0.0
    return sum(wrong(d) for d, _ in ps) / len(ps) - sum(wrong(g) for _, g in ps) / len(ps)


def main():
    try:
        G_rows = read_jsonl(GATED)
        D_rows = read_jsonl(DFILE)
    except Exception as e:  # noqa: BLE001
        not_computable(f"file not readable: {e}")
        return
    for r in G_rows + D_rows:
        if "problem_index" not in r or "sample" not in r:
            not_computable("problem_index or sample missing in a row")
            return
    if any("attempt" not in r for r in D_rows):
        not_computable("attempt missing in a D row")
        return

    # Main (literal): same sample number in both files.
    bp = pairs(G_rows, D_rows, 0)
    entries = list(bp.values())
    n_pairs = sum(len(e) for e in entries)
    # Alt: gated samples are numbered from 1 and D samples from 0, so pair gated sample s with D sample s - 1.
    bp_alt = pairs(G_rows, D_rows, 1)
    entries_alt = list(bp_alt.values())
    alt = stat(entries_alt) if entries_alt else None

    print(json.dumps({"groups": {"D_plain_T1_kept": n_pairs, "H_gated_kept": n_pairs}}))
    if n_pairs == 0:
        not_computable("no (problem_index, sample) pair with both rows present and neither a cap hit")
        return
    m = stat(entries)
    interval = bootstrap(stat, entries)
    d0, g0 = entries[0][0]
    report(m, n_pairs, interval, "bootstrap", refuted_by_met=m > 0.017, alt_measured=alt,
           example_row={"D": d0, "H": g0})


if __name__ == "__main__":
    main()
