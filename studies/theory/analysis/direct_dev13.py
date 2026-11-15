"""Direct tests devcut-01 (round-13/s5-a) and devmode-01 (round-13/s5-b). Spec: studies/theory/specs/SPEC_direct_dev13.md.

Usage: uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_dev13 [--plain ROWS.jsonl]
ROWS.jsonl: the kept autobench method's dev100 per-sample rows, one per (seed, problem_index, sample), with fields
seed, problem_index, sample, finish_reason ('stop', 'length' at the final 4,096 limit, 'time'), extracted_v3, score_v3.
Without --plain (the rows sit only in frustea's Modal Volume autobench-runs), both verdicts are undecided; the script
computes the null of b (G_cue) and the instrument checks on the votek rows.
"""
import json
import random
import sys
from pathlib import Path

from studies.rlneurons.lib.rln4_lib import agree

ROOT = Path(__file__).resolve().parents[3]
VOTEK = ROOT / "studies/rlneurons/results/votek/math500_base_cue-01/rows.jsonl"
DEV = ROOT / "studies/autobench/data/dev100-v1.json"
OUT = ROOT / "studies/theory/results/direct"
SAMPLES = 12
B = 2000


def groups(rows):
    """Answer groups of finished, answer-bearing samples, first-member rule in sample order: [[answer, n, right]]."""
    gs = []
    for r in sorted(rows, key=lambda r: r["sample"]):
        a = r["extracted_v3"]
        if r["finish_reason"] != "stop" or not a:
            continue
        for g in gs:
            if agree(g[0], a):
                g[1] += 1
                break
        else:
            gs.append([a, 1, r["score_v3"] == 1])
    return gs


def pair_stats(rows):
    gs = groups(rows)
    n_ans = sum(g[1] for g in gs)
    win = max(gs, key=lambda g: g[1]) if gs else None   # max keeps the first group on ties (sample order)
    wrong = [g[1] for g in gs if not g[2]]
    return {
        "vote_right": bool(win and win[2]),
        "c": (SAMPLES - sum(r["finish_reason"] == "stop" for r in rows)) / SAMPLES,
        "r": sum(r["score_v3"] == 1 for r in rows if r["finish_reason"] == "stop" and r["extracted_v3"]) / n_ans if n_ans else 0.0,
        "g": max(wrong) / n_ans if wrong else 0.0,
        "n_ans": n_ans,
    }


def by_pair(rows):
    out = {}
    for r in rows:
        out.setdefault((r.get("seed_run", 0), r["problem_index"]), []).append(r)
    return {k: pair_stats(v) for k, v in out.items()}


def boot(pairs, stat):
    """90 % interval of stat(pairs) over 2,000 resamples of problems."""
    probs = sorted({k[1] for k in pairs})
    idx = {p: [k for k in pairs if k[1] == p] for p in probs}
    rng = random.Random(13)
    vals = []
    for _ in range(B):
        sample = [k for p in rng.choices(probs, k=len(probs)) for k in idx[p]]
        v = stat({i: pairs[k] for i, k in enumerate(sample)})
        if v is not None:
            vals.append(v)
    vals.sort()
    return [round(vals[int(0.05 * len(vals))], 4), round(vals[int(0.95 * len(vals)) - 1], 4)]


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def G(pairs):
    return mean([s["g"] for s in pairs.values() if not s["vote_right"]])


def D(pairs):
    w = [s["c"] for s in pairs.values() if not s["vote_right"]]
    m = [s["c"] for s in pairs.values() if s["vote_right"] and s["r"] <= 0.75]
    return mean(w) - mean(m) if w and m else None


def votek_rows(cut_at=None):
    rows = [json.loads(l) for l in VOTEK.open()]
    for r in rows:
        r["finish_reason"] = "length" if r["cap_hit"] else r["finish_reason"]
        if cut_at is not None and r["n_new"] > cut_at:
            r["finish_reason"] = "length"
    return rows


def main():
    plain = sys.argv[sys.argv.index("--plain") + 1] if "--plain" in sys.argv else None
    dev = set(json.load(DEV.open())["indices"])

    cue = by_pair(votek_rows())
    cue_dev = {k: v for k, v in cue.items() if k[1] in dev}
    n_wrong_dev = sum(not s["vote_right"] for s in cue_dev.values())
    cue_null = cue_dev if n_wrong_dev >= 10 else cue
    G_cue = G(cue_null)
    G_cue_ci = boot(cue_null, G)
    cue_wrong = {k: s for k, s in cue_null.items() if not s["vote_right"]}

    # instrument b: R with the null on both sides must be 1.0, below 1.3
    R_self = G(cue_null) / G_cue
    # instrument a: cued base, every sample over 4,096 tokens treated as cut
    cut4k = {k: v for k, v in by_pair(votek_rows(4096)).items() if k[1] in dev}
    W4 = [s for s in cut4k.values() if not s["vote_right"]]
    inst_a = {"D": round(D(cut4k), 4), "D_ci90": boot(cut4k, D), "n_W": len(W4),
              "W_share_c_ge_025": round(mean([s["c"] >= 0.25 for s in W4]), 4),
              "vote_right": sum(s["vote_right"] for s in cut4k.values())}

    if plain is None:
        reason = ("per-sample dev100 rows of the kept method are only in frustea's Modal Volume autobench-runs "
                  "(karpathy/<nnn>/), not committed and not reachable from this workspace; D and G_plain not computed")
        cut_ro = {"mechanism": "round-13/s5-a", "verdict": "undecided", "reason": reason, "D": None, "n_W": None,
                  "threshold": "refuted if D < 0.15 or fewer than half of W pairs have c >= 0.25",
                  "null": "difficulty-matched vote-right pairs (r <= 0.75) of the same runs; not computed",
                  "instrument_votek_cut4096_dev100": inst_a}
        mode_ro = {"mechanism": "round-13/s5-b", "verdict": "undecided", "reason": reason, "G_plain": None, "R": None,
                   "threshold": "refuted if G_plain < 0.40 or R < 1.3",
                   "G_cue": round(G_cue, 4), "G_cue_ci90": G_cue_ci,
                   "G_cue_n_wrong": len(cue_wrong), "G_cue_scope": "dev100" if cue_null is cue_dev else "all 500",
                   "cue_vote_right_dev100": sum(s["vote_right"] for s in cue_dev.values()),
                   "G_plain_needed_for_R_1.3": round(1.3 * G_cue, 4),
                   "instrument_R_null_vs_itself": round(R_self, 4)}
    else:
        p = by_pair([json.loads(l) for l in open(plain)])
        Wp = [s for s in p.values() if not s["vote_right"]]
        d = D(p)
        half = mean([s["c"] >= 0.25 for s in Wp])
        cut_ro = {"mechanism": "round-13/s5-a", "D": round(d, 4), "D_ci90": boot(p, D), "n_W": len(Wp),
                  "W_share_c_ge_025": round(half, 4),
                  "verdict": "holds" if d >= 0.15 and half >= 0.5 else "refuted",
                  "instrument_votek_cut4096_dev100": inst_a}
        gp = G(p)
        R = gp / G_cue
        mode_ro = {"mechanism": "round-13/s5-b", "G_plain": round(gp, 4), "G_plain_ci90": boot(p, G),
                   "G_cue": round(G_cue, 4), "G_cue_ci90": G_cue_ci, "R": round(R, 4),
                   "verdict": "holds" if gp >= 0.40 and R >= 1.3 else "refuted",
                   "instrument_R_null_vs_itself": round(R_self, 4)}

    for name, ro in (("devcut-01", cut_ro), ("devmode-01", mode_ro)):
        d = OUT / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "readout.json").write_text(json.dumps(ro, indent=1) + "\n")
        print(name, json.dumps(ro))

    # raw rows of the cued null for reading: its dev100 vote-wrong problems
    rows = votek_rows()
    lines = []
    for (s, i), st in sorted(cue_wrong.items()):
        rs = [r for r in rows if r["problem_index"] == i]
        lines.append({"problem_index": i, "gold": rs[0]["gold"], "g": round(st["g"], 3), "n_ans": st["n_ans"],
                      "answers": [r["extracted_v3"] if r["finish_reason"] == "stop" else "<" + r["finish_reason"] + ">" for r in rs],
                      "n_new": [r["n_new"] for r in rs]})
    (OUT / "devmode-01" / "null_rows.json").write_text(json.dumps(lines, indent=1) + "\n")


if __name__ == "__main__":
    main()
