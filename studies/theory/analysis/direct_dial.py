"""Direct test of run-05/f2-m01, the finish dial (specs/SPEC_direct_dial.md).

    uv run --no-project --with numpy python studies/theory/analysis/direct_dial.py

Condition on one cued-base sample's outcome per problem (finished-right FR, finished-wrong FW, cap hit CH) and give the
right rate of a second base sample, of base + 1.5x top-8 RL-Math directions, and of RL plain in each group, pooled over
the choice of the conditioning sample; comparison samples on another seed than the conditioning one where seeds are shared.
Signed side: base - 1x top-8 on hard328 (one sample) and on 250 odd MATH-500 problems. 90 % bootstrap over problems.
Writes studies/theory/results/direct/dial-01/.
"""
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
D13 = ROOT / "studies" / "rlneurons" / "results" / "day1_3"
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "dial-01"
M1X_HARD_JOB = "abaybektursun-1115-031209-1273"
EDIT_HARD_JOB = "abaybektursun-1115-055641-b417"
M1X_MATH = ROOT / "studies" / "theory" / "results" / "experiments" / "cell-r9-m11-01" / "per_problem.json"
GROUPS = ("FR", "FW", "CH")
B, RNG = 10000, np.random.default_rng(0)
BOOT = {}


def load(path, n, samples):
    """Rows of attempt 0 as (problems, samples) arrays; problems in order of problem_index (hard328 indexes a pool of 400)."""
    rows = [json.loads(line) for line in open(path)]
    rows = [r for r in rows if r.get("attempt", 0) == 0]
    probs = sorted({r["problem_index"] for r in rows})
    pos = {p: k for k, p in enumerate(probs)}
    keys = sorted((pos[r["problem_index"]], r["sample"]) for r in rows)
    assert keys == sorted((p, s) for p in range(n) for s in range(samples)), path
    right, cap = np.zeros((n, samples), int), np.zeros((n, samples), bool)
    seed = np.zeros((n, samples), int)
    for r in rows:
        right[pos[r["problem_index"]], r["sample"]] = r["score_v3"]
        cap[pos[r["problem_index"]], r["sample"]] = r["cap_hit"]
        seed[pos[r["problem_index"]], r["sample"]] = r["seed"]
    return right, cap, seed, probs


def boot_idx(n):
    if n not in BOOT:
        BOOT[n] = RNG.integers(0, n, size=(B, n))
    return BOOT[n]


def ci(per_num, per_den):
    """Pooled ratio sum(num)/sum(den) and its 90 % interval over problems; per_* are (problems,) arrays."""
    idx = boot_idx(len(per_num))
    r = per_num[idx].sum(1) / per_den[idx].sum(1)
    return [float(per_num.sum() / per_den.sum()), float(np.quantile(r, 0.05)), float(np.quantile(r, 0.95))]


def ci_diff(n1, d1, n2, d2, scale=100.0):
    idx = boot_idx(len(n1))
    r = n1[idx].sum(1) / d1[idx].sum(1) - n2[idx].sum(1) / d2[idx].sum(1)
    pt = n1.sum() / d1.sum() - n2.sum() / d2.sum()
    return [float(scale * pt), float(scale * np.quantile(r, 0.05)), float(scale * np.quantile(r, 0.95))]


def outcome(right, cap):
    return np.where(cap, 2, np.where(right == 1, 0, 1))


def split(b_right, b_cap, arms, shared_seed):
    """Per problem and group: right, finished-right, finished and total samples of each arm.
    arms: name -> (right matrix, cap matrix, exclude the conditioning sample's index)."""
    n, S = b_right.shape
    out = outcome(b_right, b_cap)
    allarms = {"base2": (b_right, b_cap, True), **arms}
    cnt = {a: {c: np.zeros((n, 3)) for c in ("right", "fin_right", "fin", "tot")} for a in allarms}
    rows = np.arange(n)
    for i in range(S):
        g = out[:, i]
        for a, (r, c, excl) in allarms.items():
            cols = [k for k in range(r.shape[1]) if not (excl and k == i)]
            cnt[a]["right"][rows, g] += r[:, cols].sum(1)
            cnt[a]["fin_right"][rows, g] += (r[:, cols] * ~c[:, cols]).sum(1)
            cnt[a]["fin"][rows, g] += (~c[:, cols]).sum(1)
            cnt[a]["tot"][rows, g] += len(cols)
    res = {"shared_seed_excluded": shared_seed, "groups": {}}
    for gi, gname in enumerate(GROUPS):
        row = {"n_problem_samples": int(cnt["base2"]["tot"][:, gi].sum() / (S - 1)),
               "n_problems": int((cnt["base2"]["tot"][:, gi] > 0).sum())}
        for a, k in cnt.items():
            row[f"rate_{a}"] = ci(k["right"][:, gi], k["tot"][:, gi])
            row[f"n_{a}"] = int(k["tot"][:, gi].sum())
            row[f"cap_rate_{a}"] = 1 - k["fin"][:, gi].sum() / k["tot"][:, gi].sum()
            row[f"right_per_finished_{a}"] = ci(k["fin_right"][:, gi], k["fin"][:, gi])
        for a in arms:
            row[f"D_{a}_minus_base2_pts"] = ci_diff(cnt[a]["right"][:, gi], cnt[a]["tot"][:, gi], cnt["base2"]["right"][:, gi], cnt["base2"]["tot"][:, gi])
            row[f"D_{a}_minus_base2_right_per_finished_pts"] = ci_diff(cnt[a]["fin_right"][:, gi], cnt[a]["fin"][:, gi],
                                                                       cnt["base2"]["fin_right"][:, gi], cnt["base2"]["fin"][:, gi])
        row["D_edit_minus_rl_pts"] = ci_diff(cnt["edit"]["right"][:, gi], cnt["edit"]["tot"][:, gi], cnt["rl"]["right"][:, gi], cnt["rl"]["tot"][:, gi])
        res["groups"][gname] = row
    # share of the edit's gain over base2 in each group: n_g D_g / sum_g n_g D_g, n_g the conditioning count
    num, den, bnum, bden = cnt["edit"]["right"], cnt["edit"]["tot"], cnt["base2"]["right"], cnt["base2"]["tot"]

    def gains(ix):
        return np.array([bden[ix, gi].sum(-1) / (S - 1) * (num[ix, gi].sum(-1) / den[ix, gi].sum(-1) - bnum[ix, gi].sum(-1) / bden[ix, gi].sum(-1))
                         for gi in range(3)])

    pt, bs = gains(rows), gains(boot_idx(n))
    for gi, gname in enumerate(GROUPS):
        sh = bs[gi] / bs.sum(0)
        res[f"edit_gain_share_{gname}"] = [float(pt[gi] / pt.sum()), float(np.quantile(sh, 0.05)), float(np.quantile(sh, 0.95))]
    res["edit_gain_problems_x_samples_by_group"] = {g: float(pt[k]) for k, g in enumerate(GROUPS)}
    return res, out


def always_finished(b_right, b_cap, arms):
    """Added after the first readout: problems on which no base sample hits the cap; right rate of each arm there."""
    keep = ~b_cap.any(1)
    res = {"n_problems": int(keep.sum()), "rate_base": ci(b_right[keep].sum(1).astype(float), np.full(keep.sum(), b_right.shape[1], float))}
    for a, (r, c) in arms.items():
        rn, rd = r[keep].sum(1).astype(float), np.full(keep.sum(), r.shape[1], float)
        res[f"rate_{a}"] = ci(rn, rd)
        res[f"cap_rate_{a}"] = float(c[keep].mean())
        res[f"D_{a}_minus_base_pts"] = ci_diff(rn, rd, b_right[keep].sum(1).astype(float), np.full(keep.sum(), b_right.shape[1], float))
    return res


def verdict(fw_edit, fw_rl):
    lo, hi = fw_edit[1], fw_edit[2]
    if lo > 0:
        return "adds skill"
    if lo <= 0 <= hi and hi < 0.5 * fw_rl[0]:
        return "pure dial"
    return "undecided"


def signed(m_right, m_cap, b_right, b_cap):
    """-1x one sample per problem against the base's samples on the same problems."""
    fin = ~m_cap
    bfin = ~b_cap
    res = {"n": int(len(m_right)), "right": int(m_right.sum()), "cap_hits": int(m_cap.sum()),
           "base_right_per_sample": float(b_right.sum(0).mean()), "base_cap_hits_per_sample": float(b_cap.sum(0).mean())}
    res["right_per_finished_m1x"] = ci(m_right * fin, fin.astype(float))
    res["right_per_finished_base"] = ci((b_right * bfin).sum(1).astype(float), bfin.sum(1).astype(float))
    res["right_per_finished_m1x_minus_base_pts"] = ci_diff((m_right * fin).astype(float), fin.astype(float),
                                                           (b_right * bfin).sum(1).astype(float), bfin.sum(1).astype(float))
    # on problems where -1x finished and the base finished at least once
    keep = fin & (bfin.sum(1) > 0)
    res["n_problems_both_finish"] = int(keep.sum())
    mn, md = (m_right * keep).astype(float), keep.astype(float)
    bn, bd = ((b_right * bfin).sum(1) * keep).astype(float), (bfin.sum(1) * keep).astype(float)
    res["same_problems_m1x_rate"] = ci(mn, md)
    res["same_problems_base_finished_rate"] = ci(bn, bd)
    res["same_problems_m1x_minus_base_pts"] = ci_diff(mn, md, bn, bd)
    return res


def norm(s):
    return "".join(str(s).replace("$", "").replace("\\!", "").split()).lower()


def gold_in(extracted, gold):
    return norm(gold) != "" and norm(gold) in norm(extracted)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    readout = {"spec": "studies/theory/specs/SPEC_direct_dial.md"}

    # hard328
    br, bc, bs, hp = load(D13 / "hard328_base_cue_s4r2-01" / "rows.jsonl", 328, 4)
    er, ec, es, hp2 = load(D13 / "hard328_top8x1.5_cue_s4-01" / "rows.jsonl", 328, 4)
    rr, rc, rs, hp3 = load(D13 / "hard328_rl_plain_s4r2-01" / "rows.jsonl", 328, 4)
    assert hp == hp2 == hp3 and (bs == es).all() and (bs == rs).all()
    h, h_out = split(br, bc, {"edit": (er, ec, True), "rl": (rr, rc, True)}, True)
    h["base_always_finishes"] = always_finished(br, bc, {"edit": (er, ec), "rl": (rr, rc)})
    h["counts"] = {"base_right_per_sample": br.sum(0).tolist(), "edit_right_per_sample": er.sum(0).tolist(),
                   "rl_right_per_sample": rr.sum(0).tolist(), "base_cap": bc.sum(0).tolist(),
                   "edit_cap": ec.sum(0).tolist(), "rl_cap": rc.sum(0).tolist()}
    h["edit_right_on_base_cap_hits_that_hit_cap_itself"] = int((er * ec).sum())
    readout["hard328"] = h

    # MATH-500
    mbr, mbc, _, mp = load(D13 / "math500_base_cue-01" / "rows.jsonl", 500, 4)
    mrr, mrc, _, mp2 = load(D13 / "math500_rl-01" / "rows.jsonl", 500, 4)
    mer, mec, _, mp3 = load(ROOT / "studies" / "rlneurons" / "results" / "xreward" / "dial15_math500-01" / "rows.jsonl", 500, 1)
    assert mp == mp2 == mp3 == list(range(500))
    m, _ = split(mbr, mbc, {"edit": (mer, mec, False), "rl": (mrr, mrc, False)}, False)
    m["base_always_finishes"] = always_finished(mbr, mbc, {"edit": (mer, mec), "rl": (mrr, mrc)})
    m["counts"] = {"base_right_per_sample": mbr.sum(0).tolist(), "edit_right": int(mer.sum()), "rl_right_per_sample": mrr.sum(0).tolist(),
                   "base_cap": mbc.sum(0).tolist(), "edit_cap": int(mec.sum()), "rl_cap": mrc.sum(0).tolist()}
    readout["math500"] = m

    readout["verdict_hard328"] = verdict(h["groups"]["FW"]["D_edit_minus_base2_pts"], h["groups"]["FW"]["D_rl_minus_base2_pts"])
    readout["verdict_math500"] = verdict(m["groups"]["FW"]["D_edit_minus_base2_pts"], m["groups"]["FW"]["D_rl_minus_base2_pts"])

    # signed side, hard328: rows of the -1x job (raw answers on the Modal volume, copied by gpu.py get)
    raw = [json.loads(line) for line in open(ROOT / "runs" / M1X_HARD_JOB / "answers.jsonl")]
    assert sorted(r["problem_index"] for r in raw) == hp and all(r["seed"] == 3000000 + r["problem_index"] for r in raw)
    raw.sort(key=lambda r: r["problem_index"])
    keep = ("problem_index", "seed", "n_new", "cap_hit", "finish_reason", "loop_A", "extracted_v3", "score_v3", "gold")
    (OUT / "m1x_hard328_rows.jsonl").write_text("".join(json.dumps({k: r[k] for k in keep}) + "\n" for r in raw))
    xr = np.array([r["score_v3"] for r in raw])
    xc = np.array([r["cap_hit"] for r in raw])
    sh = signed(xr, xc, br, bc)
    fw = [r for r in raw if not r["cap_hit"] and r["score_v3"] == 0]
    sh["m1x_finished_wrong_gold_in_extracted"] = [sum(gold_in(r["extracted_v3"], r["gold"]) for r in fw), len(fw)]
    braw = [json.loads(line) for line in open(D13 / "hard328_base_cue_s4r2-01" / "rows.jsonl")]
    bfw = [r for r in braw if r["attempt"] == 0 and not r["cap_hit"] and r["score_v3"] == 0]
    sh["base_finished_wrong_gold_in_extracted"] = [sum(gold_in(r["extracted_v3"], r["gold"]) for r in bfw), len(bfw)]
    readout["signed_m1x_hard328"] = sh

    # signed side, MATH-500 odd problems (cell-r9-m11-01), same seeds as base sample 0
    pp = json.loads(M1X_MATH.read_text())
    idx = np.array([p["problem_index"] for p in pp])
    assert len(idx) == 250 and (idx % 2 == 1).all()
    assert all(p["base_score_v3"] == mbr[p["problem_index"], 0] and p["base_cap_hit"] == mbc[p["problem_index"], 0] for p in pp)
    yr = np.array([p["score_v3"] for p in pp])
    yc = np.array([p["cap_hit"] for p in pp])
    sm = signed(yr, yc, mbr[idx], mbc[idx])
    fw = [p for p in pp if not p["cap_hit"] and p["score_v3"] == 0]
    sm["m1x_finished_wrong_gold_in_extracted"] = [sum(gold_in(p["extracted_v3"], p["gold"]) for p in fw), len(fw)]
    readout["signed_m1x_math500_odd250"] = sm

    (OUT / "readout.json").write_text(json.dumps(readout, indent=1) + "\n")

    # examples of the deciding group: edit samples (k != i) on hard328 problems where base sample 0 finished wrong
    eraw = {(r["problem_index"], r["sample"]): r for r in map(json.loads, open(ROOT / "runs" / EDIT_HARD_JOB / "answers.jsonl"))}
    fw0 = [p for p in range(328) if h_out[p, 0] == 1]  # positions; eraw is keyed by problem_index
    ex = {}
    for label, want in (("right", 1), ("wrong", 0)):
        p, s = next((p, s) for p in fw0 for s in (1, 2, 3) if er[p, s] == want and not ec[p, s])
        r = eraw[(hp[p], s)]
        ex[label] = {"problem_index": hp[p], "sample": s, "base_sample0": {"score_v3": int(br[p, 0]), "cap_hit": bool(bc[p, 0])},
                     "prompt": r["prompt"], "gold": r["gold"], "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"],
                     "n_new": r["n_new"], "answer_tail": r["text"][-1500:]}
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    print(json.dumps({k: readout[k] for k in ("verdict_hard328", "verdict_math500")}))


if __name__ == "__main__":
    main()
