"""Direct tests votesplit-01 (round-13/s3-a) and votetie-01 (round-13/s3-b), specs/SPEC_direct_vote13.md.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_vote13

Run from the repository root. Reads the stored rows of result-1c9e40 and votes with studies/rlneurons/analysis/votek.py.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis.votek import agree_table, vote

SRC = pathlib.Path("studies/rlneurons/results/votek/math500_base_cue-01/rows.jsonl")
OUT = pathlib.Path("studies/theory/results/direct")
B = 10_000


def groups(rows, same, sub):
    """The groups of votek.vote over `sub`, in creation order."""
    gs = []
    for s in sub:
        if rows[s]["extracted_v3"] is None:
            continue
        g = next((g for g in gs if same[g[0]][s]), None)
        gs.append([s]) if g is None else g.append(s)
    return gs


def boot(flags, rng):
    f = np.asarray(flags, dtype=float)
    m = f[rng.integers(0, len(f), (B, len(f)))].mean(1)
    return m


def ci(m):
    return [round(float(np.percentile(m, 5)), 3), round(float(np.percentile(m, 95)), 3)]


def main():
    per = {}
    for line in open(SRC):
        r = json.loads(line)
        per.setdefault(r["problem_index"], {}).setdefault(r["sample"], r)          # first in file order
    probs = sorted(per)
    assert len(probs) == 500 and all(sorted(per[p]) == list(range(12)) for p in probs)
    rows = {p: [per[p][s] for s in range(12)] for p in probs}
    same = {p: agree_table(rows[p]) for p in probs}
    v4 = {p: vote(rows[p], same[p], range(4)) for p in probs}
    v12 = {p: vote(rows[p], same[p], range(12)) for p in probs}
    n4, n12 = sum(v4[p]["score"] for p in probs), sum(v12[p]["score"] for p in probs)
    assert (n4, n12) == (446, 466), (n4, n12)                                       # posted counts of result-1c9e40

    info = {}
    for p in probs:
        r = rows[p]
        nr = sum(x["score_v3"] == 1 for x in r)
        g4 = groups(r, same[p], range(4))
        top = max((len(g) for g in g4), default=0)
        tops = [g for g in g4 if len(g) == top]
        assert not g4 or max(g4, key=len)[0] == v4[p]["winner"]
        T = int(len(tops) >= 2 and any(r[g[0]]["score_v3"] == 1 for g in tops))
        R = [s for s in range(12) if r[s]["score_v3"] == 1]
        W = [s for s in range(12) if r[s]["score_v3"] != 1 and r[s]["extracted_v3"] is not None]
        null12 = int(len(R) > len(W) or (len(R) == len(W) and R and R[0] < W[0]))
        info[p] = {"p": nr / 12, "right": nr, "T": T, "null12": null12, "no_answer": sum(x["extracted_v3"] is None for x in r),
                   "cap_hits": sum(bool(x["cap_hit"]) for x in r), "k4_sizes": [len(g) for g in g4],
                   "k12_sizes": [len(g) for g in groups(r, same[p], range(12))],
                   "k12_wrong_groups": sum(1 for g in groups(r, same[p], range(12)) if r[g[0]]["score_v3"] != 1),
                   "right_in_0_3": sum(r[s]["score_v3"] == 1 for s in range(4))}

    G = [p for p in probs if v12[p]["score"] == 1 and v4[p]["score"] == 0]
    L = [p for p in probs if v12[p]["score"] == 0 and v4[p]["score"] == 1]
    assert len(G) - len(L) == n12 - n4
    Gn = [p for p in probs if info[p]["null12"] == 1 and v4[p]["score"] == 0]
    F = [p for p in probs if v4[p]["score"] == 0 and info[p]["right_in_0_3"] >= 1 and p not in G]
    rng = np.random.default_rng(0)

    a_flags = [info[p]["p"] < 0.5 for p in G]
    S_a = float(np.mean(a_flags))
    kept = sum(p in Gn for p in G) / len(G)
    S_null = float(np.mean([info[p]["p"] < 0.5 for p in Gn])) if Gn else None
    a_ref = S_a < 0.50 or kept >= 0.80
    b_flags = [info[p]["T"] == 1 and info[p]["p"] >= 0.5 for p in G]
    f_flags = [info[p]["T"] == 1 and info[p]["p"] >= 0.5 for p in F]
    S_b, S_nb = float(np.mean(b_flags)), float(np.mean(f_flags))
    mb, mf = boot(b_flags, rng), boot(f_flags, rng)
    b_ref = S_b < 0.60 or S_b - S_nb < 0.20

    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    common = {"source": str(SRC), "result": "result-1c9e40", "vote_k4_samples_0_3": n4, "vote_k12": n12,
              "G_size": len(G), "lost_size": len(L), "G": G, "lost": L,
              "G_rows": {str(p): info[p] for p in G}}
    readouts = {
        "votesplit-01": {**common, "mechanism": "round-13/s3-a", "S_a": round(S_a, 3), "S_a_ci90": ci(boot(a_flags, rng)),
                         "G_null_size": len(Gn), "kept_by_merge": round(kept, 3), "removed_by_merge": sum(p not in Gn for p in G),
                         "S_null": S_null, "p_of_G": sorted(info[p]["right"] for p in G),
                         "rule": "refuted if S_a < 0.50 or kept_by_merge >= 0.80", "verdict": "refuted" if a_ref else "holds"},
        "votetie-01": {**common, "mechanism": "round-13/s3-b", "S_b": round(S_b, 3), "S_b_ci90": ci(mb),
                       "F_size": len(F), "S_null_b": round(S_nb, 3), "S_null_b_ci90": ci(mf),
                       "S_b_minus_null": round(S_b - S_nb, 3), "S_b_minus_null_ci90": ci(mb - mf),
                       "T_in_G": sum(info[p]["T"] for p in G), "p_ge_half_in_G": sum(info[p]["p"] >= 0.5 for p in G),
                       "rule": "refuted if S_b < 0.60 or S_b - S_null_b < 0.20", "verdict": "refuted" if b_ref else "holds"},
    }

    def item(p, flag):
        r = rows[p]
        return {"problem_index": p, "gold": r[0]["gold"], "supports_claim": flag, **info[p],
                "answers": [{"sample": s, "extracted_v3": r[s]["extracted_v3"], "score_v3": r[s]["score_v3"], "cap_hit": r[s]["cap_hit"]} for s in range(12)],
                "vote_k4": {"winner_sample": v4[p]["winner"], "score": v4[p]["score"]}, "vote_k12": {"winner_sample": v12[p]["winner"], "score": v12[p]["score"]}}

    for name, flags in (("votesplit-01", a_flags), ("votetie-01", b_flags)):
        d = OUT / name
        assert not d.exists(), f"{d} exists: a rerun gets the next number"
        d.mkdir(parents=True)
        (d / "readout.json").write_text(json.dumps(readouts[name], indent=1) + "\n")
        yes = next((p for p, f in zip(G, flags) if f), None)
        no = next((p for p, f in zip(G, flags) if not f), None)
        ex = [item(p, f) for p, f in ((yes, True), (no, False)) if p is not None]
        (d / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
        (d / "run.json").write_text(json.dumps({"spec": "studies/theory/specs/SPEC_direct_vote13.md", "commit": commit,
            "command": "uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_vote13",
            "inputs": [str(SRC)], "input_jobs": ["abaybektursun-1114-153825-208b", "ih-1115-* shards (see metrics.json of the source folder)"],
            "vote_code": "studies/rlneurons/analysis/votek.py agree_table, vote (rln4_lib.agree on norm_v3)",
            "bootstrap": "10,000 resamples of problems, numpy default_rng(0), 90 % percentile interval", "board": "work-5d6316"}, indent=1) + "\n")
    for name, r in readouts.items():
        print(name, {k: v for k, v in r.items() if k not in ("G", "lost", "G_rows")})
    for p in G:
        print(p, info[p], "k4 winner", v4[p]["winner"], "k12 winner", v12[p]["winner"])


if __name__ == "__main__":
    sys.exit(main())
