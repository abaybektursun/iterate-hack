"""Direct tests karpcap-01 (round-13/s1-a) and karpagree-01 (round-13/s1-b) (specs/SPEC_direct_karp13.md).

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_karp13

On hard328, problems the Karpathy method loses although the cued base solves them (k >= 2 of 4) against the
difficulty-matched problems it wins: share whose cued-base right samples are all longer than 4,096 tokens (L', N'),
and agreement of the Karpathy wrong winner with the cued base's finished wrong answers (A_K') against the base's own
wrong-answer agreement (A_B). 90 % bootstrap over problems. Writes results/direct/karpcap-01/ and karpagree-01/.
"""
import itertools
import json
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.lib import rln4_lib as R

ROOT = pathlib.Path(__file__).resolve().parents[3]
KARP = ROOT / "studies/autobench/results/math500-loop/finals-01/hard328-karpathy-000.json"
BASE = ROOT / "studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl"
OUT = ROOT / "studies/theory/results/direct"
CAP, B = 4096, 10000
RNG = np.random.default_rng(0)

karp = {x["index"]: x for x in json.load(open(KARP))}
assert len(karp) == 328 and sum(x["right"] for x in karp.values()) == 139
rows = [json.loads(line) for line in open(BASE)]
by = {}
for r in rows:
    if r["sample"] < 4:
        by.setdefault(r["problem_index"], []).append(r)
assert set(by) == set(karp)
gold = {p: v[0]["gold"] for p, v in by.items()}

# instrument checks
assert R.agree("1/2", "\\frac{1}{2}") and not R.agree("1/2", "2")
agree_gold = {g: [R.agree(karp[p]["extracted"], gold[p]) for p in karp if karp[p]["right"] == g] for g in (0, 1)}
check = {"karp_right_agree_gold": f"{sum(agree_gold[1])}/{len(agree_gold[1])}",
         "karp_wrong_agree_gold": f"{sum(agree_gold[0])}/{len(agree_gold[0])}"}
assert sum(agree_gold[1]) >= 0.97 * len(agree_gold[1]) and sum(agree_gold[0]) <= 0.03 * len(agree_gold[0]), check


def right_ok(r):
    return r["score_v3"] == 1 and not r["cap_hit"]


a0 = {p: [r for r in v if r["attempt"] == 0] for p, v in by.items()}
assert all(len(v) == 4 for v in a0.values())
k = {p: sum(right_ok(r) for r in v) for p, v in a0.items()}
lost = sorted(p for p in karp if karp[p]["right"] == 0 and k[p] >= 2)
null = sorted(p for p in karp if karp[p]["right"] == 1 and k[p] >= 2)


def long_only(p, cap=CAP):
    """1 when every right cued-base sample (attempt 0) is longer than cap generated tokens."""
    return int(all(r["n_new"] > cap for r in a0[p] if right_ok(r)))


for c, want in ((16384, 0), (0, 1)):
    assert all(long_only(p, c) == want for p in lost + null), c
Lv = np.array([long_only(p) for p in lost])
Nv = np.array([long_only(p) for p in null])


def boot(f, *arrs):
    out = np.array([f(*[a[RNG.integers(0, len(a), len(a))] for a in arrs]) for _ in range(B)])
    return [round(float(x), 4) for x in np.percentile(out, [5, 95])]


Lp, Np = Lv.mean(), Nv.mean()
L_ci, N_ci = boot(np.mean, Lv), boot(np.mean, Nv)
D_ci = boot(lambda a, b: a.mean() - b.mean(), Lv, Nv)


def wrongs(p):
    """Extracted answers of the cued base's finished wrong samples (all attempts of samples 0-3)."""
    return [r["extracted_v3"] for r in by[p] if not r["cap_hit"] and r["score_v3"] == 0 and r["extracted_v3"] is not None]


# per lost problem: (agreeing K-B pairs, K-B pairs, agreeing B-B pairs, B-B pairs)
cnt = []
for p in lost:
    w = wrongs(p)
    kb = [R.agree(karp[p]["extracted"], x) for x in w]
    bb = [R.agree(x, y) for x, y in itertools.combinations(w, 2)]
    cnt.append((sum(kb), len(kb), sum(bb), len(bb)))
cnt = np.array(cnt)


def adiff(c):
    return c[:, 0].sum() / c[:, 1].sum() - c[:, 2].sum() / c[:, 3].sum()


AK, AB = cnt[:, 0].sum() / cnt[:, 1].sum(), cnt[:, 2].sum() / cnt[:, 3].sum()
A_ci = boot(adiff, cnt)
AK_ci = boot(lambda c: c[:, 0].sum() / c[:, 1].sum(), cnt)
AB_ci = boot(lambda c: c[:, 2].sum() / c[:, 3].sum(), cnt)
# where the Karpathy winner agrees with none of the base's wrong answers nor gold: a value of its own
own = int(sum(1 for p, c in zip(lost, cnt) if c[1] > 0 and c[0] == 0))

a_holds = Lp >= 0.45 and Lp - Np >= 0.20
b_holds = Lp <= 0.35 and AK - AB >= 0.10
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
common = {"n_lost": len(lost), "n_null": len(null), "k_rule": "k = right (score_v3 1, no cap hit) of attempt 0, samples 0-3; sets need k >= 2",
          "finals_reproduce": "139/328", "instrument_checks": check,
          "context_finish_counts": {"requests": 7961, "stop": 3331, "length": 3910, "time": 720,
                                    "first_pass_cut_at_least": "2013/3936"},
          "deviation": "plans' per-sample L, N, C, A_K need the 12 Karpathy samples per problem, which are only in frustea's Modal Volume autobench-runs; proxies per specs/SPEC_direct_karp13.md"}
ra = dict(common, mechanism="round-13/s1-a",
          L_prime=round(float(Lp), 4), L_prime_ci90=L_ci, N_prime=round(float(Np), 4), N_prime_ci90=N_ci,
          L_minus_N=round(float(Lp - Np), 4), L_minus_N_ci90=D_ci,
          rule="holds iff L' >= 0.45 and L' - N' >= 0.20", verdict="holds" if a_holds else "refuted")
rb = dict(common, mechanism="round-13/s1-b",
          C_prime=round(float(Lp), 4), C_prime_ci90=L_ci,
          A_K=round(float(AK), 4), A_K_ci90=AK_ci, A_K_pairs=int(cnt[:, 1].sum()),
          A_B=round(float(AB), 4), A_B_ci90=AB_ci, A_B_pairs=int(cnt[:, 3].sum()),
          A_K_minus_A_B=round(float(AK - AB), 4), A_K_minus_A_B_ci90=A_ci,
          lost_with_base_wrongs=int((cnt[:, 1] > 0).sum()), lost_karp_answer_matches_no_base_wrong=own,
          rule="holds iff C' <= 0.35 and A_K - A_B >= 0.10", verdict="holds" if b_holds else "refuted")


def sample(p):
    return {"problem_index": p, "gold": gold[p], "karpathy_winner": karp[p]["extracted"], "karpathy_right": karp[p]["right"],
            "k": k[p], "base_attempt0": [{"sample": r["sample"], "n_new": r["n_new"], "cap_hit": r["cap_hit"],
                                          "extracted": r["extracted_v3"], "score_v3": r["score_v3"]} for r in a0[p]],
            "base_finished_wrong_all_attempts": wrongs(p), "long_only": long_only(p)}


lo = [p for p in lost if long_only(p)]
sh = [p for p in lost if not long_only(p)]
agr = [p for p, c in zip(lost, cnt) if c[0] > 0]
nag = [p for p, c in zip(lost, cnt) if c[1] > 0 and c[0] == 0]
ex = {"karpcap-01": {"supports": sample(lo[0]), "against": sample(sh[0])},
      "karpagree-01": {"supports": sample(agr[0]) if agr else None, "against": sample(nag[0]) if nag else sample(lo[0])}}
for name, res in (("karpcap-01", ra), ("karpagree-01", rb)):
    d = OUT / name
    d.mkdir(parents=True, exist_ok=False)
    json.dump(res, open(d / "readout.json", "w"), indent=1)
    json.dump(ex[name], open(d / "examples.json", "w"), indent=1)
    json.dump({"commit": commit, "command": "uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.theory.analysis.direct_karp13",
               "inputs": [str(KARP.relative_to(ROOT)), str(BASE.relative_to(ROOT))],
               "input_jobs": ["autobench final/hard328-karpathy-000 (frustea Modal)", "abaybektursun-1114-200457-e8e6"]},
              open(d / "run.json", "w"), indent=1)
# 10 raw lost rows for reading.md, printed
for p in lost[:10]:
    s = sample(p)
    print(p, "gold", s["gold"], "K", s["karpathy_winner"], "k", s["k"],
          [(b["n_new"], b["extracted"], b["score_v3"]) for b in s["base_attempt0"]], "wrongs", s["base_finished_wrong_all_attempts"], "long_only", s["long_only"])
print(json.dumps({"a": ra, "b": rb}, indent=1), file=sys.stderr)
