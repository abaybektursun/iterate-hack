"""editreach-02 (rerun of editreach-01 over all problem ids): direct test of the judge's disagreement round-15/d1 (spec: studies/theory/specs/SPEC_direct_editreach.md).

    cd <checkout holding runs/> && uv run --no-project --with numpy python <worktree>/studies/theory/analysis/direct_editreach.py

Scores come from committed rows (day1_3 rows.jsonl, cap32/rows-02). Full texts for the freshness check and the examples
come from runs/<job>/answers.jsonl in the current directory and from CAP32_RAW (not in git). Writes
studies/theory/results/direct/editreach-02/ in the worktree holding this script.
"""
import hashlib
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "studies/rlneurons/results"
OUT = ROOT / "studies/theory/results/direct/editreach-02"  # -01 came from commit d52d13d, which read only ids < 328
CELLS = {"base": "day1_3/hard328_base_cue_s4r2-01", "edit": "day1_3/hard328_top8x1.5_cue_s4-01",
         "rl": "day1_3/hard328_rl_plain_s4r2-01"}
CAP32_ROWS = RES / "cap32/rows-02/base_cue.jsonl"
CAP32_RAW = pathlib.Path("../iterate-hack-shots/runs/cap32_base_cue_joined/answers.jsonl")
CUT = 16384
RANGES = {"account-1": (0.10, 0.45), "account-2": (0.60, 1.40), "null": (-0.15, 0.08)}
NB = 10000


def committed(cell):
    return [json.loads(line) for line in open(RES / CELLS[cell] / "rows.jsonl")]


def count_matches(rows, cell):
    return sum(r["score_v3"] for r in rows) == json.load(open(RES / CELLS[cell] / "metrics.json"))["counts"]["correct_v3"]


def job(cell):
    return json.load(open(RES / CELLS[cell] / "run.json"))["job_id"]


def raw(path):
    return [json.loads(line) for line in open(path)]


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


rows = {c: committed(c) for c in CELLS}
# Instrument check: each committed file reproduces its posted right count; a wrong file must not.
for c in CELLS:
    assert count_matches(rows[c], c), c
assert not count_matches(rows["rl"], "edit"), "count check passed on the wrong file"

# Per-problem attempt-0 scores of samples 0-3.
S4 = {c: {} for c in CELLS}
for c in CELLS:
    for r in rows[c]:
        if r["attempt"] == 0:
            S4[c].setdefault(r["problem_index"], {})[r["sample"]] = r["score_v3"]
cap = {r["problem_index"]: r for r in map(json.loads, open(CAP32_ROWS))}
assert len(cap) == 328
IDS = sorted(cap)  # hard328 problem ids run 0-399, not 0-327
assert all(sorted({r["problem_index"] for r in rows[c]}) == IDS for c in CELLS)


def cap_right(r, cut):
    return int(r["score_v3"] == 1 and r["n_new"] <= cut and not r["cap_hit"])


assert sum(cap_right(r, CUT) for r in cap.values()) == 152  # cap32 readout: right_at_16384_same_answers
assert sum(r["score_v3"] for r in cap.values()) == 156  # right_at_32768

# Freshness: cap32 text vs the cued base's s4r2 samples 0-3 (same seed as sample 0).
base_raw = [r for r in raw(pathlib.Path("runs") / job("base") / "answers.jsonl") if r["attempt"] == 0]
base_sha = {}
for r in base_raw:
    base_sha.setdefault(r["problem_index"], set()).add(sha(r["text"]))
cap_raw = {r["problem_index"]: r for r in raw(CAP32_RAW)}
assert len(cap_raw) == 328 and all(cap_raw[p]["score_v3"] == cap[p]["score_v3"] for p in cap)

full = [p for p in IDS if all(sorted(S4[c].get(p, {})) == [0, 1, 2, 3] for c in CELLS) and p in cap]
base0 = [p for p in IDS if sorted(S4["base"].get(p, {})) == [0, 1, 2, 3] and sum(S4["base"][p].values()) == 0]
not_fresh = [p for p in base0 if sha(cap_raw[p]["text"]) in base_sha[p]]
sel = [p for p in base0 if p in full and p not in not_fresh]

e = np.array([sum(S4["edit"][p].values()) / 4 for p in sel])
r_ = np.array([sum(S4["rl"][p].values()) / 4 for p in sel])
b = np.array([cap_right(cap[p], CUT) for p in sel], dtype=float)
b32 = np.array([cap[p]["score_v3"] for p in sel], dtype=float)
idx = np.random.default_rng(0).integers(0, len(sel), size=(NB, len(sel)))


def ci(x):
    return [float(v) for v in np.percentile(x, [5, 95])]


E, R, B = e.mean(), r_.mean(), b.mean()
S = (E - B) / (R - B)
Sb = (e[idx].mean(1) - b[idx].mean(1)) / (r_[idx].mean(1) - b[idx].mean(1))
RB = r_[idx].mean(1) - b[idx].mean(1)
ER = e[idx].mean(1) - r_[idx].mean(1)
S32 = (E - b32.mean()) / (R - b32.mean())
S32b = (e[idx].mean(1) - b32[idx].mean(1)) / (r_[idx].mean(1) - b32[idx].mean(1))
lo, hi = ci(Sb)
n = len(sel)
counts_ok = ci(RB)[0] > 0


def verdict(rng):
    if not counts_ok:
        return "does not count (R - B interval includes 0)"
    if rng[0] <= lo and hi <= rng[1] and n >= 50:
        return "holds"
    if hi < rng[0] or lo > rng[1]:
        return "refuted"
    return "undecided"


metrics = {
    "test": "editreach-02", "plan": "round-15/d1", "spec": "studies/theory/specs/SPEC_direct_editreach.md",
    "statistic": "S = (E - B) / (R - B) on hard328 problems with 0 of 4 right among the cued base's attempt-0 samples",
    "S": float(S), "S_ci90": [lo, hi], "n_problems": n, "n_edit_samples": 4 * n,
    "null_value": 0.0, "ranges": {k: list(v) for k, v in RANGES.items()},
    "verdict": {k: verdict(RANGES[k]) for k in ("account-1", "account-2")},
    "null_range_position": ("inside" if RANGES["null"][0] <= lo and hi <= RANGES["null"][1]
                            else "above" if lo > RANGES["null"][1] else "below" if hi < RANGES["null"][0] else "overlaps"),
    "E_edit_rate": float(E), "R_rl_rate": float(R), "B_fresh_base_rate_cut16384": float(B),
    "R_minus_B": float(R - B), "R_minus_B_ci90": ci(RB), "test_counts": bool(counts_ok),
    "E_minus_R": float(E - R), "E_minus_R_ci90": ci(ER),
    "secondary_S_cap32_full_32768": float(S32), "secondary_S_cap32_full_32768_ci90": ci(S32b),
    "B_fresh_base_rate_full_32768": float(b32.mean()),
    "edit_right_samples": int(e.sum() * 4), "rl_right_samples": int(r_.sum() * 4), "fresh_base_right": int(b.sum()),
    "cap_hits_on_selected_of_4n": {c: sum(r["cap_hit"] for r in rows[c] if r["attempt"] == 0 and r["problem_index"] in sel)
                                   for c in CELLS},
    "selection": {"base_0_of_4": len(base0), "dropped_missing_rows": len([p for p in base0 if p not in full]),
                  "dropped_not_fresh": len(not_fresh)},
    "instrument_checks": "committed rows reproduce correct_v3 673/801/827; RL rows fail against the edit count; cap32 rows "
                         "give 152 right at 16,384 and 156 at 32,768 as the readout",
    "bootstrap": "10,000 resamples of problems, numpy default_rng(0), same draw for E, R, B",
    "jobs": {**{c: job(c) for c in CELLS}, "cap32": "cap32_base_cue_joined"},
    "selected_problems": sel,
}
OUT.mkdir(parents=True, exist_ok=True)
json.dump(metrics, open(OUT / "metrics.json", "w"), indent=1)

# Examples: one edit sample right and one wrong on a selected problem, with the input and the output text.
edit_raw = {(r["problem_index"], r["sample"]): r for r in raw(pathlib.Path("runs") / job("edit") / "answers.jsonl")}
right = next((p, s) for p in sel for s in range(4) if S4["edit"][p][s] == 1)
wrong = next((p, s) for p in sel for s in range(4) if S4["edit"][p][s] == 0)


def example(key, label):
    r = edit_raw[key]
    p = key[0]
    return {"scored": label, "cell": CELLS["edit"], "problem_index": p, "sample": key[1], "unique_id": r["unique_id"],
            "prompt": r["prompt"], "output_tail": r["text"][-1500:], "n_new": r["n_new"], "cap_hit": r["cap_hit"],
            "extracted_v3": r["extracted_v3"], "gold": r["gold"], "score_v3": r["score_v3"],
            "problem_e_r_b": [sum(S4["edit"][p].values()) / 4, sum(S4["rl"][p].values()) / 4, cap_right(cap[p], CUT)]}


json.dump([example(right, "right"), example(wrong, "wrong")], open(OUT / "examples.json", "w"), indent=1)
print(json.dumps({k: v for k, v in metrics.items() if k != "selected_problems"}, indent=1))
