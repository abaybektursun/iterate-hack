"""The verified data layer of the short paper on the token cap ("comparisons change with the cap, not all the same way").

    uv run --no-project --with numpy python studies/rlneurons/paper-two-caps/build_facts.py

Reads only files in git (no runs/, no model). Writes, next to this file:
  facts.json     every number the paper may use: {value, ci95, n, unit, source, note}; `checks_against_readouts` lists each
                 recomputed number that was asserted against a stored readout, README table or board comment.
  examples.json  one problem Think-SFT does not finish at 16,384 and gets right at 32,768; one RL finishes wrong at both.

Conventions (every comparison):
  per problem, accuracy = mean of score_v3 over the arm's samples (first attempt only, no restarts);
  gain A - B = mean over problems of (acc_A - acc_B), in points (x 100); interval: paired bootstrap over problems,
  10,000 resamples, numpy seed 0, 2.5 / 97.5 percentiles;
  a sample "hits the cap" when cap_hit is true (it generated the cap without finishing); a problem is "cut off" for an arm
  when any of its samples hits the cap; "no-cap problems" = problems where no sample of either arm hits the cap;
  precision = samples right and finished / samples finished.
Cap-32,768 cells (one sample) are scored twice from one text: at 32,768 as generated, and at 16,384 by the rule of
analysis/cap32.py (right only if n_new <= 16,384 and not cut off; tokens min(n_new, 16,384)).
"""
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
RES = STUDY / "results"
B = 10000
CHECKS = []


def rel(p):
    return str(pathlib.Path(p).resolve().relative_to(ROOT))


def check(name, got, want, tol=0.0):
    assert abs(got - want) <= tol, f"{name}: recomputed {got}, stored {want} (tolerance {tol})"
    CHECKS.append({"name": name, "recomputed": got, "stored": want, "tolerance": tol})


def fact(value, n, unit, source, note="", ci95=None):
    return {"value": value, "ci95": ci95, "n": n, "unit": unit, "source": source, "note": note}


def r2(x):
    return None if x is None else round(float(x), 2)


# ---------------------------------------------------------------- cells: {problem: [sample dicts]}
def rows(path, arm=None, key="sample"):
    """first attempts of a rows.jsonl, grouped by problem; a sample = {s score, c cap hit, t tokens, e answer}."""
    by = {}
    for line in open(RES / path):
        r = json.loads(line)
        if r.get("attempt", 0) != 0 or (arm is not None and r.get("arm") != arm):
            continue
        k = r["seed"] - r["problem_index"] if key == "seed" else r["sample"]
        by.setdefault(r["problem_index"], {})[k] = {"s": r["score_v3"], "c": bool(r["cap_hit"]), "t": r["n_new"],
                                                    "e": r["extracted_v3"]}
    ks = sorted(next(iter(by.values())))
    assert all(sorted(v) == ks for v in by.values()), (path, arm)
    return {"src": f"results/{path}" + (f" (arm {arm})" if arm else ""), "keys": ks,
            "p": {p: [v[k] for k in ks] for p, v in by.items()}}


def step100_cue():
    """step 100 + cue on MATH-500: sample 0 from per_problem.json, samples 1-3 from rows.jsonl (as readout3.json)."""
    c = rows("ckptcue/s0100_cue_s123-01/rows.jsonl")
    for x in json.loads((RES / "ckptcue/s0100_cue-01/per_problem.json").read_text()):
        c["p"][x["problem_index"]].insert(0, {"s": x["score_v3"], "c": bool(x["cap_hit"]), "t": x["n_generated"],
                                              "e": x["extracted_v3"]})
    c["keys"] = [0] + c["keys"]
    c["src"] = "results/ckptcue/s0100_cue-01/per_problem.json (sample 0) + results/ckptcue/s0100_cue_s123-01/rows.jsonl"
    return c


def cap32(f, arm=None):
    """one cap-32,768 cell -> (scored at 16,384, scored at 32,768), the same texts. arm: key of a two-model row (cap32_m2)."""
    c16, c32, raw = {}, {}, {}
    for line in open(RES / f):
        r0 = json.loads(line)
        r = r0 if arm is None else {**r0[arm], "problem_index": r0["problem_index"], "seed": r0["seed"]}
        p = r["problem_index"]
        fin16 = r["n_new"] <= 16384 and not r["cap_hit"]
        c32[p] = [{"s": r["score_v3"], "c": bool(r["cap_hit"]), "t": r["n_new"], "e": r["extracted_v3"]}]
        c16[p] = [{"s": r["score_v3"] if fin16 else 0, "c": not fin16, "t": min(r["n_new"], 16384), "e": r["extracted_v3"]}]
        raw[p] = r
    src = f"results/{f}" + (f" ({arm})" if arm else "")
    return {"src": src + " scored at 16,384", "keys": [0], "p": c16}, {"src": src, "keys": [0], "p": c32}, raw


def right_per_sample(c):
    return [sum(v[i]["s"] for v in c["p"].values()) for i in range(len(c["keys"]))]


def caps_per_sample(c):
    return [sum(v[i]["c"] for v in c["p"].values()) for i in range(len(c["keys"]))]


# ---------------------------------------------------------------- statistics
def boot(d, seed=0, level=95.0):
    """paired bootstrap interval; any level uses the same resamples (same seed, same n)."""
    d = np.asarray(d, dtype=float)
    if len(d) == 0:
        return None
    m = d[np.random.default_rng(seed).integers(0, len(d), (B, len(d)))].mean(1)
    a = (100 - level) / 2
    return [r2(np.percentile(m, a)), r2(np.percentile(m, 100 - a))]


def acc(v):
    return sum(x["s"] for x in v) / len(v)


def anycap(v):
    return any(x["c"] for x in v)


def arm_stats(c, ps):
    xs = [x for p in ps for x in c["p"][p]]
    fin = [x for x in xs if not x["c"]]
    return {"source": c["src"], "samples": len(c["keys"]), "right_per_sample": right_per_sample(c),
            "right_mean": r2(sum(x["s"] for x in xs) / len(c["keys"])),
            "accuracy_pct": r2(100 * sum(x["s"] for x in xs) / len(xs)),
            "cap_hits_per_sample": caps_per_sample(c), "cap_hit_rate_pct": r2(100 * (len(xs) - len(fin)) / len(xs)),
            "problems_cut_off_any_sample": sum(anycap(c["p"][p]) for p in ps),
            "tokens_per_problem": r2(sum(x["t"] for x in xs) / len(xs)),
            "precision_finished": {"right": sum(x["s"] for x in fin), "finished": len(fin),
                                   "pct": r2(100 * sum(x["s"] for x in fin) / len(fin))},
            "right_but_cut_off": sum(x["s"] for x in xs if x["c"])}


def compare(name, A, Bc, note=""):
    ps = sorted(A["p"])
    assert ps == sorted(Bc["p"]), name
    d = np.array([100 * (acc(A["p"][p]) - acc(Bc["p"][p])) for p in ps])
    cA = {p: anycap(A["p"][p]) for p in ps}
    cB = {p: anycap(Bc["p"][p]) for p in ps}
    groups = {"A_cut_B_not": [p for p in ps if cA[p] and not cB[p]], "B_cut_A_not": [p for p in ps if cB[p] and not cA[p]],
              "neither_cut": [p for p in ps if not cA[p] and not cB[p]], "both_cut": [p for p in ps if cA[p] and cB[p]]}
    pos = {p: i for i, p in enumerate(ps)}
    nc = groups["neither_cut"]
    dnc = d[[pos[p] for p in nc]]
    accA_nc = 100 * np.mean([acc(A["p"][p]) for p in nc])
    accB_nc = 100 * np.mean([acc(Bc["p"][p]) for p in nc])
    out = {"A": A["src"], "B": Bc["src"], "note": note,
           "full": fact(r2(d.mean()), len(ps), "points (A - B)", [A["src"], Bc["src"]], ci95=boot(d),
                        note=f"samples A {len(A['keys'])}, B {len(Bc['keys'])}; = {d.sum() / 100:+.2f} problems"),
           "no_cap": fact(r2(dnc.mean()), len(nc), "points (A - B) on problems where no sample of either arm hits the cap",
                          [A["src"], Bc["src"]], ci95=boot(dnc),
                          note=f"accuracy there A {accA_nc:.1f} %, B {accB_nc:.1f} %; headroom of B {100 - accB_nc:.1f} points; "
                               f"= {dnc.sum() / 100:+.2f} problems, {100 * dnc.sum() / d.sum() if d.sum() else float('nan'):.0f} % of the full gain"),
           "no_cap_accuracy_pct": {"A": r2(accA_nc), "B": r2(accB_nc)},
           "no_cap_share_of_B_errors_fixed": r2(dnc.mean() / (100 - accB_nc)) if accB_nc < 100 else None,
           "decomposition_problems": {g: {"n_problems": len(v), "gain_problems": r2(d[[pos[p] for p in v]].sum() / 100)}
                                      for g, v in groups.items()},
           "arms": {"A": arm_stats(A, ps), "B": arm_stats(Bc, ps)}}
    assert abs(sum(v["gain_problems"] for v in out["decomposition_problems"].values()) - d.sum() / 100) < 0.05
    return name, out


# ---------------------------------------------------------------- matched-difficulty control (hard328)
def split_strata(A, Bc, ps):
    """difficulty = B's samples 0-1 (mean 0, .5, 1); gain = A (all samples) - B (samples 2-3): no regression to the mean."""
    st = {}
    for p in ps:
        b = Bc["p"][p]
        k = (b[0]["s"] + b[1]["s"]) / 2
        st.setdefault(k, []).append(100 * (acc(A["p"][p]) - (b[2]["s"] + b[3]["s"]) / 2))
    return st


def heldout_B(Bc, ps):
    """B's accuracy on samples 2-3, per stratum of samples 0-1, in percent."""
    st = {}
    for p in ps:
        b = Bc["p"][p]
        st.setdefault((b[0]["s"] + b[1]["s"]) / 2, []).append(50 * (b[2]["s"] + b[3]["s"]))
    return {k: np.mean(v) for k, v in st.items()}


def matched(src_name, A1, B1, tgt_name, A2, B2, seed=0):
    """no-cap problems of both comparisons; source gains reweighted to the target's distribution of B-difficulty."""
    def nocap(A, Bc):
        return [p for p in sorted(A["p"]) if not anycap(A["p"][p]) and not anycap(Bc["p"][p])]
    s1, s2 = split_strata(A1, B1, nocap(A1, B1)), split_strata(A2, B2, nocap(A2, B2))
    n2 = sum(len(v) for v in s2.values())
    w = {k: len(v) / n2 for k, v in s2.items()}
    assert all(k in s1 for k in w), "a target stratum is empty in the source"
    rng = np.random.default_rng(seed)

    def rw(st, rs=None):
        return sum(w[k] * (np.mean(st[k]) if rs is None else np.mean(rng.choice(st[k], len(st[k])))) for k in w)

    def ci(st):
        m = [rw(st, True) for _ in range(B // 5)]
        return [r2(np.percentile(m, 2.5)), r2(np.percentile(m, 97.5))]
    h1, h2 = heldout_B(B1, nocap(A1, B1)), heldout_B(B2, nocap(A2, B2))
    table = {str(k): {"target_n": len(s2.get(k, [])), "target_gain": r2(np.mean(s2[k])) if k in s2 else None,
                      "target_B_heldout_acc_pct": r2(h2.get(k)),
                      "source_n": len(s1.get(k, [])), "source_gain": r2(np.mean(s1[k])) if k in s1 else None,
                      "source_B_heldout_acc_pct": r2(h1.get(k))}
             for k in sorted(set(s1) | set(s2))}
    return {"what": f"{src_name} on its no-cap problems, reweighted to the B-difficulty mix of {tgt_name}'s no-cap problems",
            "difficulty": "B's samples 0 and 1 (0, 0.5 or 1 right); gain measured on A all samples minus B samples 2 and 3",
            "strata": table,
            "source_reweighted": fact(r2(rw(s1)), sum(len(v) for v in s1.values()), "points", src_name, ci95=ci(s1),
                                      note=f"bootstrap within strata, {B // 5} resamples"),
            "target_same_estimator": fact(r2(rw(s2)), n2, "points", tgt_name, ci95=ci(s2))}


def headroom_share(name, A, Bc, seed=0):
    """no-cap problems: share of B's held-out errors (samples 2-3) that A removes = sum(A - B23) / sum(1 - B23)."""
    ps = [p for p in sorted(A["p"]) if not anycap(A["p"][p]) and not anycap(Bc["p"][p])]
    g = np.array([acc(A["p"][p]) - (Bc["p"][p][2]["s"] + Bc["p"][p][3]["s"]) / 2 for p in ps])
    h = np.array([1 - (Bc["p"][p][2]["s"] + Bc["p"][p][3]["s"]) / 2 for p in ps])
    idx = np.random.default_rng(seed).integers(0, len(ps), (B, len(ps)))
    hs = h[idx].sum(1)
    m = g[idx].sum(1)[hs > 0] / hs[hs > 0]
    return fact(r2(g.sum() / h.sum()), len(ps), "share of B's held-out errors on no-cap problems that A removes", name,
                ci95=[r2(np.percentile(m, 2.5)), r2(np.percentile(m, 97.5))],
                note=f"B held-out accuracy there {100 * (1 - h.mean()):.1f} % ({h.sum():.1f} held-out errors); gain "
                     f"{100 * g.mean():+.2f} points; {int((hs == 0).sum())} of {B} resamples without a B error dropped")


# ---------------------------------------------------------------- review of draft 1
THREE = {"RL - base+cue": "RL - base+cue (seed 3,000,000)", "Think-SFT - RL": "Think-SFT - RL (seed 3,000,000)",
         "M(2) - Think-SFT (seed 3,010,000)": "M(2) - Think-SFT (seed 3,010,000)"}


def review(C, c32, CH, per_model, RAW, m2pair):
    N = 328
    out = {}
    # 1. Bonferroni over the three changes
    out["bonferroni"] = {"what": "98.33 % paired bootstrap interval (0.833 / 99.167 percentiles) of each 16,384-view -> 32,768 change; "
                                 "same 10,000 resamples (seed 0) as the 95 % interval",
                         **{lab: fact(c32[k]["change_32k_minus_16k"]["value"], N, "points", c32[k]["change_32k_minus_16k"]["source"],
                                      ci95=c32[k]["change_32k_minus_16k"]["ci95"], note=f"ci98.33 {boot(CH[k], level=100 - 5 / 3)}")
                            | {"ci98_33": boot(CH[k], level=100 - 5 / 3)} for k, lab in THREE.items()}}

    # 2. strict 32,768: an answer that reaches the cap is wrong
    m16, m32, t16, t32, m_raw, t_raw = m2pair

    def strict(c):
        return {"src": c["src"] + " (cut off = wrong)", "keys": c["keys"],
                "p": {p: [{**x, "s": 0 if x["c"] else x["s"]} for x in v] for p, v in c["p"].items()}}
    sm, st = strict(m32), strict(t32)
    full = compare("strict", sm, st)[1]["full"]
    ch = [100 * ((acc(sm["p"][p]) - acc(st["p"][p])) - (acc(m16["p"][p]) - acc(t16["p"][p]))) for p in sorted(sm["p"])]
    check("strict: Think-SFT seed 3,010,000 right at 32,768 (auditor: 233)", right_per_sample(st)[0], 233)
    check("strict: M(2) - Think-SFT at 32,768 (auditor: +3.7)", full["value"], 3.7, 0.05)
    reach = {nm: {"reach_32768": sum(bool(r["cap_hit"]) for r in raw.values()),
                  "of_them_graded_right": sum(r["score_v3"] for r in raw.values() if r["cap_hit"]),
                  "problems": [p for p, r in raw.items() if r["cap_hit"] and r["score_v3"]]} for nm, raw in RAW.items()}
    out["strict_32768"] = {
        "M(2) - Think-SFT at 32,768, cut off = wrong": full,
        "change_32k_minus_16k_view": fact(r2(np.mean(ch)), N, "points", "results/transplant/cap32_m2_s1-01/rows.jsonl", ci95=boot(ch),
                                          note=f"ci98.33 {boot(ch, level=100 - 5 / 3)}"),
        "answers_reaching_32768_per_cell": reach,
        "note": "the 16,384 view already scores a cut answer wrong; only the 32,768 side changes"}

    # 3. right-but-cut-off in the real 16,384 runs
    rate = {}
    for nm, k in (("Think-SFT + cue", "h_sft"), ("RL plain", "h_rl"), ("M(2)", "h_M2"), ("base + cue", "h_base")):
        c = C[k]
        tot = sum(x["s"] for v in c["p"].values() for x in v if x["c"])
        rate[nm] = {"right_but_cut_off_total": tot, "samples": len(c["keys"]), "per_sample": r2(tot / len(c["keys"])),
                    "cut_off_samples_total": sum(x["c"] for v in c["p"].values() for x in v), "source": c["src"]}
    for nm, want in (("Think-SFT + cue", 3.5), ("RL plain", 1.75), ("M(2)", 2.0), ("base + cue", 1.0)):
        check(f"right but cut off per sample at 16,384, {nm} (reviewer)", rate[nm]["per_sample"], want, 0.005)
    pairs = {"RL - base+cue": ("RL plain", "base + cue"), "Think-SFT - RL": ("Think-SFT + cue", "RL plain"),
             "M(2) - Think-SFT (seed 3,010,000)": ("M(2)", "Think-SFT + cue")}
    eff = {}
    for k, (a, b) in pairs.items():
        shift = 100 * (rate[a]["per_sample"] - rate[b]["per_sample"]) / N
        v = c32[k]["change_32k_minus_16k"]["value"]
        eff[THREE[k]] = {"16384_view_gain_shift_points": r2(shift), "change_as_reported": v, "change_if_credited_estimate": r2(v - shift)}
    out["right_but_cut_off_16384"] = {"per_model": rate, "effect_on_changes": eff,
                                      "note": "ESTIMATE: the 16,384 view scores every cut answer 0; a real 16,384 run grades some cut texts right "
                                              "(an answer found in the cut text). Crediting each arm at its stored per-sample rate shifts the 16,384-view "
                                              "gain by (rate_A - rate_B) / 328 and the change by minus that; problem identity is not modelled."}

    # 4. Think-SFT in its own chat format (readouts only; rows not in git)
    nh = json.loads((RES / "native/hard328-01/readout.json").read_text())
    nm5 = json.loads((RES / "native/math500-01/readout.json").read_text())
    check("native hard328 right at 32,768", nh["cap_32768"]["native_right"], 232)
    check("native hard328 right at 16,384 view", nh["cap_16384"]["native_right"], 204)
    check("native readout cue cell = cap32 sft_cue at 32,768", nh["cap_32768"]["cue_right"], c32["Think-SFT - RL"]["at_32768"]["arms"]["A"]["right_per_sample"][0])
    check("native readout cue cell at 16,384 view", nh["cap_16384"]["cue_right"], c32["Think-SFT - RL"]["at_16384"]["arms"]["A"]["right_per_sample"][0])
    rl16 = c32["Think-SFT - RL"]["at_16384"]["arms"]["B"]["right_per_sample"][0]
    rl32 = c32["Think-SFT - RL"]["at_32768"]["arms"]["B"]["right_per_sample"][0]
    out["native_format"] = {
        "arm": "allenai/Olmo-3-7B-Think-SFT @ 6ff85758 in its own ChatML template with <think> (native tokenizer), no cue; T 1.0 / top-p 1.0, "
               "grader v3 on the whole text, one sample, cap 32,768 scored also at the 16,384 view (analysis/cap32.py rule); "
               "hard328 seed 3,000,000 (the seed of the cap32 cells), MATH-500 seed 182,000,000 (specs/SPEC_native.md)",
        "hard328": {"source": "studies/rlneurons/results/native/hard328-01/readout.json", "readout": nh,
                    "native_minus_RL_points_no_interval": {"at_16384_view": r2(100 * (nh["cap_16384"]["native_right"] - rl16) / N),
                                                           "at_32768": r2(100 * (nh["cap_32768"]["native_right"] - rl32) / N),
                                                           "change": r2(100 * ((nh["cap_32768"]["native_right"] - rl32) - (nh["cap_16384"]["native_right"] - rl16)) / N),
                                                           "note": "from totals only: the native per-problem rows are not in git, so no paired interval; "
                                                                   "RL = the cap32 rl_plain cell (193 / 195), same seed"}},
        "math500": {"source": "studies/rlneurons/results/native/math500-01/readout.json", "readout": nm5}}

    # 5. the RL reference of the cap32 run
    stored = right_per_sample(C["h_rl"])
    t32_right = c32["Think-SFT - RL"]["at_32768"]["arms"]["A"]["right_per_sample"][0]
    alt = 100 * (t32_right - (np.mean(stored) + 2)) / N
    out["rl_reference"] = {
        "cap32_run_RL_at_16384_view": c32["Think-SFT - RL"]["at_16384"]["arms"]["B"]["right_per_sample"][0], "stored_4_samples_same_seeds": stored, "stored_mean": float(np.mean(stored)),
        "spec_rule": "SPEC_cap32.md, Instrument: \"each cell's score at 16,384 must lie within 12 problems of the stored cell at that cap "
                     "(two SD of identical requests is about 11): Think-SFT 212 to 219, RL plain 206, base cue 164. Outside that, the box's "
                     "cell is not comparable and is rerun.\"",
        "triggered": "yes: 193 is 13 below the filed reference 206 (limit 12); not rerun (README cap32 section). Against the 4-sample mean "
                     "200.0 it is 7 below, and inside the range 190-209 of the stored samples.",
        "ThinkSFT_minus_RL_at_32768_with_RL_stored_mean_plus_its_gain": fact(r2(alt), N, "points", "230 (Think-SFT cap32) - (200.0 + 2) over 328",
                                                                             note="no interval: mixes runs; this run's RL sample gives +10.67"),
        "same_with_ThinkSFT_2_samples": r2(100 * ((230 + 234) / 2 - (np.mean(stored) + 2)) / N)}
    check("rl_reference alternative Think-SFT - RL at 32,768 (reviewer: about +8.5)", alt, 8.5, 0.1)

    # 6. late answers and remaining headroom
    late = {}
    for nm, raw in RAW.items():
        lg = [r for r in raw.values() if r["n_new"] > 16384]
        cut = sum(bool(r["cap_hit"]) for r in raw.values())
        late[nm] = {"longer_than_16384": len(lg), "end_right": sum(r["score_v3"] for r in lg),
                    "share_pct": r2(100 * sum(r["score_v3"] for r in lg) / len(lg)),
                    "still_cut_off_at_32768": cut, "max_further_gain_points": r2(100 * cut / N)}
    for nm, (n, k) in {"base + cue": (64, 4), "RL plain": (20, 2), "Think-SFT + cue (seed 3,000,000)": (93, 23),
                       "Think-SFT + cue (seed 3,010,000)": (90, 24), "M(2) (seed 3,010,000)": (56, 13)}.items():
        check(f"late answers {nm}", late[nm]["longer_than_16384"], n)
        check(f"late answers right {nm}", late[nm]["end_right"], k)
    out["late_precision"] = {"per_model": late,
                             "note": "max further gain = every answer still cut at 32,768 turning right with more tokens (an upper bound)"}
    return out


# ---------------------------------------------------------------- main
def main():
    C = {
        "h_base": rows("day1_3/hard328_base_cue_s4r2-01/rows.jsonl"),
        "h_rl": rows("day1_3/hard328_rl_plain_s4r2-01/rows.jsonl"),
        "h_sft": rows("thinkvote/hard328_sft1_cue_s4-01/rows.jsonl"),
        "h_dial": rows("day1_3/hard328_top8x1.5_cue_s4-01/rows.jsonl"),
        "h_M2": rows("transplant/hard328-02/rows.jsonl", "sft1_rl20", key="seed"),
        "h_sft_tp": rows("transplant/hard328-02/rows.jsonl", "think"),
        "m_base": rows("day1_3/math500_base_cue-01/rows.jsonl"),
        "m_rl": rows("day1_3/math500_rl-01/rows.jsonl"),
        "m_sft": rows("thinkvote/math500_sft1_cue_s4-01/rows.jsonl"),
        "m_dial": rows("xreward/dial15_math500-01/rows.jsonl"),
        "m_s100": step100_cue(),
        "f_base": rows("fresh/base_cue_s4-01/rows.jsonl"),
        "f_rl": rows("fresh/rl_plain_s4-01/rows.jsonl"),
        "f_sft": rows("fresh/sft1_cue_s4-01/rows.jsonl"),
        "f_M2": rows("transplant/fresh2026-02/rows.jsonl", "sft1_rl20", key="seed"),
        "f_sft_tp": rows("transplant/fresh2026-02/rows.jsonl", "think"),
    }
    s16, s32, s_raw = cap32("cap32/rows-01/sft_cue.jsonl")
    r16, r32, r_raw = cap32("cap32/rows-01/rl_plain.jsonl")
    b16, b32, b_raw = cap32("cap32/rows-02/base_cue.jsonl")
    M2CAP = "transplant/cap32_m2_s1-01/rows.jsonl"                      # M(2) and Think-SFT, seed 3,010,000, cap 32,768
    m16, m32, m_raw = cap32(M2CAP, "m2")
    t16, t32, t_raw = cap32(M2CAP, "think_sft")
    assert all(m_raw[p]["seed"] == 3010000 + p for p in m_raw)

    # ---- the transplant's Think-SFT reference is the thinkvote cell, row for row
    for a, b in (("h_sft", "h_sft_tp"), ("f_sft", "f_sft_tp")):
        assert C[a]["p"] == C[b]["p"], (a, b)

    # ---- checks against stored readouts
    def each(path):
        return json.loads((RES / path).read_text())["each_sample"]["single_right"]
    for k, path in (("h_base", "day1_3/hard328_base_cue_s4r2-01"), ("h_rl", "day1_3/hard328_rl_plain_s4r2-01"),
                    ("h_sft", "thinkvote/hard328_sft1_cue_s4-01"), ("h_dial", "day1_3/hard328_top8x1.5_cue_s4-01"),
                    ("m_base", "day1_3/math500_base_cue-01"), ("m_rl", "day1_3/math500_rl-01"),
                    ("m_sft", "thinkvote/math500_sft1_cue_s4-01"), ("m_dial", "xreward/dial15_math500-01"),
                    ("f_base", "fresh/base_cue_s4-01"), ("f_rl", "fresh/rl_plain_s4-01"), ("f_sft", "fresh/sft1_cue_s4-01")):
        for i, (g, w) in enumerate(zip(right_per_sample(C[k]), each(path + "/readout.json"))):
            check(f"{k} sample {i} right (readout.json each_sample)", g, w)
    r3 = json.loads((RES / "ckptcue/readout3.json").read_text())["cells"]["s0100_cue"]["samples"]
    for i, s in enumerate(r3):
        check(f"m_s100 sample {i} right (ckptcue/readout3.json)", right_per_sample(C["m_s100"])[i], s["right"])
    for k, want in (("h_M2", [234, 229, 237]), ("f_M2", [69, 75, 70, 75])):
        for i, w in enumerate(want):
            check(f"{k} sample {i} right (README transplant tables)", right_per_sample(C[k])[i], w)
    check("h_dial cap hits per sample (README dial replication) sample 0", caps_per_sample(C["h_dial"])[0], 20)
    check("h_dial cap hits sample 1", caps_per_sample(C["h_dial"])[1], 14)
    for k, cap, fin, rt, tok in (("h_rl", 28.5, 1198, 793, 9325), ("h_sft", 94.5, 934, 822, 10103)):
        st = arm_stats(C[k], sorted(C[k]["p"]))
        check(f"{k} cap hits per sample (README transplant table)", sum(st["cap_hits_per_sample"]) / 4, cap)
        check(f"{k} finished samples", st["precision_finished"]["finished"], fin)
        check(f"{k} right of finished", st["precision_finished"]["right"], rt)
        check(f"{k} tokens per problem", st["tokens_per_problem"], tok, 1.0)
    check("h_M2 cap hits mean of 3", sum(caps_per_sample(C["h_M2"])) / 3, 54.0)
    for k, cap, fin, rt in (("f_rl", 21.0, 460, 197), ("f_sft", 62.0, 296, 238), ("f_M2", 45.75, 361, 285)):
        st = arm_stats(C[k], sorted(C[k]["p"]))
        check(f"{k} cap hits per sample (README fresh2026 transplant table)", sum(st["cap_hits_per_sample"]) / 4, cap)
        check(f"{k} finished", st["precision_finished"]["finished"], fin)
        check(f"{k} right of finished", st["precision_finished"]["right"], rt)
    ro = json.loads((RES / "cap32/readout.json").read_text())["cells"]
    for cell, (c16, c32, raw) in (("sft_cue", (s16, s32, s_raw)), ("rl_plain", (r16, r32, r_raw)), ("base_cue", (b16, b32, b_raw))):
        o = ro[cell]
        long = [r for r in raw.values() if r["n_new"] > 16384]
        check(f"cap32 {cell} right at 32,768", right_per_sample(c32)[0], o["right_at_32768"])
        check(f"cap32 {cell} right at 16,384 same answers", right_per_sample(c16)[0], o["right_at_16384_same_answers"])
        check(f"cap32 {cell} answers past 16,384", len(long), o["answers_longer_than_16384"])
        check(f"cap32 {cell} of them finished", sum(not r["cap_hit"] for r in long), o["of_them_finished"])
        check(f"cap32 {cell} of them right", sum(r["score_v3"] for r in long), o["of_them_right"])
        check(f"cap32 {cell} tokens at 32,768", arm_stats(c32, sorted(c32["p"]))["tokens_per_problem"], o["tokens_per_problem_at_32768"], 0.06)
        check(f"cap32 {cell} tokens at 16,384", arm_stats(c16, sorted(c16["p"]))["tokens_per_problem"], o["tokens_per_problem_at_16384"], 0.06)

    # ---- comparisons at 16,384 (stored multi-sample cells)
    cmps = dict([
        compare("hard328 RL - base+cue", C["h_rl"], C["h_base"]),
        compare("MATH-500 RL - base+cue", C["m_rl"], C["m_base"]),
        compare("fresh2026 RL - base+cue", C["f_rl"], C["f_base"]),
        compare("hard328 Think-SFT - RL", C["h_sft"], C["h_rl"]),
        compare("MATH-500 Think-SFT - RL", C["m_sft"], C["m_rl"]),
        compare("fresh2026 Think-SFT - RL", C["f_sft"], C["f_rl"]),
        compare("hard328 M(2) - Think-SFT", C["h_M2"], C["h_sft"], "M(2) 3 samples, seeds 3.0M / 3.1M / 3.2M"),
        compare("fresh2026 M(2) - Think-SFT", C["f_M2"], C["f_sft"], "same seeds as Think-SFT (7,000,000 + 10,000 s)"),
        compare("hard328 dial 1.5x - base+cue", C["h_dial"], C["h_base"]),
        compare("hard328 dial 1.5x - RL", C["h_dial"], C["h_rl"]),
        compare("MATH-500 dial 1.5x - base+cue", C["m_dial"], C["m_base"], "dial one sample (seed 3,000,000), base 4 samples"),
        compare("MATH-500 dial 1.5x - RL", C["m_dial"], C["m_rl"], "dial one sample, RL 4 samples"),
        compare("MATH-500 step 100 + cue - base+cue", C["m_s100"], C["m_base"], "same seeds (41,000,000 + 10,000 s)"),
    ])
    m2 = cmps["hard328 M(2) - Think-SFT"]["full"]
    check("hard328 M(2) - Think-SFT points (README, third sample)", m2["value"], 7.4, 0.05)
    check("  its interval low", m2["ci95"][0], 5.2, 0.3)
    check("  its interval high", m2["ci95"][1], 9.8, 0.3)
    f2 = cmps["fresh2026 M(2) - Think-SFT"]
    check("fresh2026 M(2) - Think-SFT points (README)", f2["full"]["value"], 9.0, 0.05)
    check("fresh2026 M(2) - Think-SFT no-cap n (board audit work-8b4030)", f2["no_cap"]["n"], 45)
    check("fresh2026 M(2) - Think-SFT no-cap points (board audit)", f2["no_cap"]["value"], 1.1, 0.05)
    check("  its interval low (audit: 0)", f2["no_cap"]["ci95"][0], 0.0, 0.2)
    check("  its interval high (audit: 2.8)", f2["no_cap"]["ci95"][1], 2.8, 0.2)
    check("MATH-500 dial 1.5x - RL (README: 0.0 vs RL sample 0) dial right", right_per_sample(C["m_dial"])[0], 456)

    # ---- the cap-32,768 run: same texts at both caps, one sample, seed 3,000,000
    def two(x, y, tag):
        """Think-SFT's two cap-32,768 samples (seeds 3,000,000 and 3,010,000) as one 2-sample cell."""
        return {"src": f"Think-SFT + cue, 2 samples at cap 32,768 ({tag}): results/cap32/rows-01/sft_cue.jsonl + {M2CAP} (think_sft)",
                "keys": [0, 1], "p": {p: x["p"][p] + y["p"][p] for p in x["p"]}}
    s2_16, s2_32 = two(s16, t16, "16,384 view"), two(s32, t32, "32,768")
    c32, CH = {}, {}
    for nm, (A16, A32, B16, B32) in {"RL - base+cue": (r16, r32, b16, b32), "Think-SFT - RL": (s16, s32, r16, r32),
                                     "Think-SFT - base+cue": (s16, s32, b16, b32),
                                     "M(2) - Think-SFT (seed 3,010,000)": (m16, m32, t16, t32),
                                     "Think-SFT (2 samples) - RL (1 sample)": (s2_16, s2_32, r16, r32)}.items():
        c32[nm] = {"at_16384": compare(nm + " @16k", A16, B16)[1], "at_32768": compare(nm + " @32k", A32, B32)[1]}
        CH[nm] = [100 * ((acc(A32["p"][p]) - acc(B32["p"][p])) - (acc(A16["p"][p]) - acc(B16["p"][p]))) for p in sorted(A16["p"])]
        c32[nm]["change_32k_minus_16k"] = fact(r2(c32[nm]["at_32768"]["full"]["value"] - c32[nm]["at_16384"]["full"]["value"]),
                                               328, "points", [A32["src"], B32["src"]], ci95=boot(CH[nm]),
            note="paired by problem: (A - B at 32,768) - (A - B at the 16,384 view), same texts")
    per_model = {}
    for nm, (A16, A32, raw) in {"Think-SFT + cue": (s16, s32, s_raw), "RL plain": (r16, r32, r_raw), "base + cue": (b16, b32, b_raw),
                                "M(2) (seed 3,010,000)": (m16, m32, m_raw),
                                "Think-SFT + cue (seed 3,010,000)": (t16, t32, t_raw)}.items():
        ps = sorted(raw)
        cut16 = [p for p in ps if A16["p"][p][0]["c"]]
        per_model[nm] = {"gain_32k_minus_16k": fact(r2(100 * np.mean([A32["p"][p][0]["s"] - A16["p"][p][0]["s"] for p in ps])), 328,
                                                    "points", A32["src"], ci95=boot([100 * (A32["p"][p][0]["s"] - A16["p"][p][0]["s"]) for p in ps])),
                         "cut_off_at_16384": len(cut16),
                         "of_them_finished_by_32768": sum(not raw[p]["cap_hit"] for p in cut16),
                         "of_them_right_at_32768": sum(raw[p]["score_v3"] for p in cut16),
                         "precision_of_late_finishers_pct": r2(100 * sum(raw[p]["score_v3"] for p in cut16) / max(1, sum(not raw[p]["cap_hit"] for p in cut16))),
                         "at_16384": arm_stats(A16, ps), "at_32768": arm_stats(A32, ps)}
    # cut off at 16,384 = n_new > 16,384 or cut off at 16,384 exactly; check equals the readout's 'answers past 16,384'
    check("cap32 sft cut at 16,384 = answers past 16,384", per_model["Think-SFT + cue"]["cut_off_at_16384"], 93)
    per_model["Think-SFT + cue, 2 samples (seeds 3,000,000 and 3,010,000)"] = {
        "gain_32k_minus_16k": fact(r2(100 * np.mean([acc(s2_32["p"][p]) - acc(s2_16["p"][p]) for p in sorted(s2_16["p"])])), 328,
                                   "points", s2_32["src"], ci95=boot([100 * (acc(s2_32["p"][p]) - acc(s2_16["p"][p])) for p in sorted(s2_16["p"])]),
                                   note="2 of the 4 Think-SFT samples at 32,768 of work-dc9359; samples 2 and 3 are not in git"),
        "at_16384": arm_stats(s2_16, sorted(s2_16["p"])), "at_32768": arm_stats(s2_32, sorted(s2_32["p"]))}

    # ---- checks against the readout of cap32_m2_s1-01 (analysis/cap32_m2.py)
    mt = json.loads((RES / "transplant/cap32_m2_s1-01/metrics.json").read_text())
    for arm, c16x, c32x, raw in (("m2", m16, m32, m_raw), ("think_sft", t16, t32, t_raw)):
        o = mt[arm]
        check(f"cap32_m2 {arm} right at 32,768", right_per_sample(c32x)[0], o["right_at_32768"])
        check(f"cap32_m2 {arm} right at 16,384 view", right_per_sample(c16x)[0], o["right_at_16384_view"])
        check(f"cap32_m2 {arm} cap hits at 32,768", caps_per_sample(c32x)[0], o["cap_hits_at_32768"])
        check(f"cap32_m2 {arm} cap hits at 16,384 view", caps_per_sample(c16x)[0], o["cap_hits_at_16384_view"])
        check(f"cap32_m2 {arm} tokens at 32,768", arm_stats(c32x, sorted(raw))["tokens_per_problem"], o["tokens_per_problem_at_32768"], 0.06)
        check(f"cap32_m2 {arm} tokens at 16,384 view", arm_stats(c16x, sorted(raw))["tokens_per_problem"], o["tokens_per_problem_at_16384_view"], 0.06)
        long = [r for r in raw.values() if r["n_new"] > 16384]
        check(f"cap32_m2 {arm} answers past 16,384", len(long), mt["answers_longer_than_16384"][arm])
        check(f"cap32_m2 {arm} of them right", sum(r["score_v3"] for r in long), mt["answers_longer_than_16384"][arm + "_right"])
    mm = c32["M(2) - Think-SFT (seed 3,010,000)"]
    for key, got in (("m2_minus_think_at_32768", mm["at_32768"]["full"]), ("m2_minus_think_at_16384_view", mm["at_16384"]["full"]),
                     ("m2_gain_32768_over_16384_view", per_model["M(2) (seed 3,010,000)"]["gain_32k_minus_16k"])):
        check(f"cap32_m2 {key} points", got["value"], mt[key]["points"], 0.005)
        check(f"cap32_m2 {key} interval low", got["ci95"][0], mt[key]["ci95"][0], 0.3)
        check(f"cap32_m2 {key} interval high", got["ci95"][1], mt[key]["ci95"][1], 0.3)
    check("Think-SFT seed 3,010,000 at 32,768 = 234 (README cap32vote samples 230, 234, 235, 232)", right_per_sample(t32)[0], 234)

    # stored 16k cells vs the cap32 run's own 16k score (run-to-run noise of one sample)
    stored_vs_run = {nm: {"stored_samples_right": right_per_sample(C[k]), "cap32_run_at_16384": right_per_sample(c)[0]}
                     for nm, k, c in (("Think-SFT + cue", "h_sft", s16), ("RL plain", "h_rl", r16), ("base + cue", "h_base", b16))}

    # M(2) at 16,384 against Think-SFT at 32,768 (the board comment of result-3387ce), and what is pending
    cross = {}
    for tag, keys in (("M(2) seeds 3.0M, 3.1M (as on the board, 231.5)", [3000000, 3100000]), ("M(2) all 3 seeds (233.3)", [3000000, 3100000, 3200000])):
        idx = [C["h_M2"]["keys"].index(k) for k in keys]
        Mk = {"src": C["h_M2"]["src"] + f" seeds {keys}", "keys": keys, "p": {p: [v[i] for i in idx] for p, v in C["h_M2"]["p"].items()}}
        cross[tag] = compare(tag, Mk, s32, "A at 16,384, B (Think-SFT one sample) at 32,768: different caps")[1]
    check("M(2)@16k (2 seeds) - Think-SFT@32k points (board comment result-3387ce)",
          cross["M(2) seeds 3.0M, 3.1M (as on the board, 231.5)"]["full"]["value"], 0.5, 0.05)
    check("  its interval low (board: -2.7)", cross["M(2) seeds 3.0M, 3.1M (as on the board, 231.5)"]["full"]["ci95"][0], -2.7, 0.3)
    check("  its interval high (board: 3.8)", cross["M(2) seeds 3.0M, 3.1M (as on the board, 231.5)"]["full"]["ci95"][1], 3.8, 0.3)

    # ---- matched-difficulty control on hard328
    ctrl = {
        "RL - base reweighted to M(2) - Think-SFT": matched("hard328 RL - base+cue", C["h_rl"], C["h_base"],
                                                            "hard328 M(2) - Think-SFT", C["h_M2"], C["h_sft"]),
        "Think-SFT - RL reweighted to M(2) - Think-SFT": matched("hard328 Think-SFT - RL", C["h_sft"], C["h_rl"],
                                                                 "hard328 M(2) - Think-SFT", C["h_M2"], C["h_sft"]),
    }
    ctrl["headroom_share_split_sample"] = {nm: headroom_share(nm, C[a], C[b]) for nm, a, b in (
        ("hard328 RL - base+cue", "h_rl", "h_base"), ("hard328 Think-SFT - RL", "h_sft", "h_rl"),
        ("hard328 M(2) - Think-SFT", "h_M2", "h_sft"), ("fresh2026 M(2) - Think-SFT", "f_M2", "f_sft"),
        ("hard328 dial 1.5x - base+cue", "h_dial", "h_base"), ("MATH-500 RL - base+cue", "m_rl", "m_base"),
        ("fresh2026 Think-SFT - RL", "f_sft", "f_rl"))}
    # second control: the no-cap subset restricted to problems B does not solve in all its samples (room to gain)
    room = {}
    for nm in ("hard328 RL - base+cue", "hard328 M(2) - Think-SFT", "fresh2026 M(2) - Think-SFT", "hard328 Think-SFT - RL",
               "MATH-500 RL - base+cue", "hard328 dial 1.5x - base+cue"):
        A, Bc = {"hard328 RL - base+cue": ("h_rl", "h_base"), "hard328 M(2) - Think-SFT": ("h_M2", "h_sft"),
                 "fresh2026 M(2) - Think-SFT": ("f_M2", "f_sft"), "hard328 Think-SFT - RL": ("h_sft", "h_rl"),
                 "MATH-500 RL - base+cue": ("m_rl", "m_base"), "hard328 dial 1.5x - base+cue": ("h_dial", "h_base")}[nm]
        A, Bc = C[A], C[Bc]
        ps = [p for p in sorted(A["p"]) if not anycap(A["p"][p]) and not anycap(Bc["p"][p]) and acc(Bc["p"][p]) < 1]
        d = [100 * (acc(A["p"][p]) - acc(Bc["p"][p])) for p in ps]
        room[nm] = fact(r2(np.mean(d)) if d else None, len(ps), "points", nm, ci95=boot(d),
                        note=f"no-cap problems where B is not right in every sample; B accuracy there "
                             f"{100 * np.mean([acc(Bc['p'][p]) for p in ps]):.1f} %; biased upward by regression to the mean, equally for every row")

    # ---- figure rows
    def cell(f):
        return {"value": f["value"], "ci95": f["ci95"], "n": f["n"]}
    fig = []
    for nm, o in cmps.items():
        row = {"comparison": nm, "gain_16384_all": cell(o["full"]), "gain_16384_no_cap": cell(o["no_cap"]),
               "no_cap_accuracy_B_pct": o["no_cap_accuracy_pct"]["B"]}
        key = {"hard328 RL - base+cue": "RL - base+cue", "hard328 Think-SFT - RL": "Think-SFT - RL"}.get(nm)
        if key:
            row["cap32_run_gain_16384"] = cell(c32[key]["at_16384"]["full"])
            row["cap32_run_gain_32768"] = cell(c32[key]["at_32768"]["full"])
            row["cap32_note"] = "one sample per arm, seed 3,000,000, the same texts scored at both caps"
        if key:
            row["cap32_run_change"] = cell(c32[key]["change_32k_minus_16k"])
        if nm == "hard328 Think-SFT - RL":
            k2 = "Think-SFT (2 samples) - RL (1 sample)"
            row["cap32_2sample_gain_16384"] = cell(c32[k2]["at_16384"]["full"])
            row["cap32_2sample_gain_32768"] = cell(c32[k2]["at_32768"]["full"])
            row["cap32_2sample_change"] = cell(c32[k2]["change_32k_minus_16k"])
            row["cap32_2sample_note"] = ("Think-SFT 2 samples at 32,768 (seeds 3,000,000 and 3,010,000; samples 2-3 of work-dc9359 "
                                         "not in git), RL one sample (seed 3,000,000)")
        if nm == "hard328 M(2) - Think-SFT":
            k2 = "M(2) - Think-SFT (seed 3,010,000)"
            row["cap32_run_gain_16384"] = cell(c32[k2]["at_16384"]["full"])
            row["cap32_run_gain_32768"] = cell(c32[k2]["at_32768"]["full"])
            row["cap32_run_change"] = cell(c32[k2]["change_32k_minus_16k"])
            row["cap32_note"] = ("one sample per arm, seed 3,010,000 (M(2): results/transplant/cap32_m2_s1-01; Think-SFT: its sample 1 "
                                 "of the cap-32,768 vote run), the same texts scored at both caps; not the seed of the other two rows")
        fig.append(row)

    facts = {
        "what": "Comparisons of Olmo 3 7B arms at token cap 16,384 vs 32,768 and on problems no arm is cut off on",
        "conventions": __doc__.split("Conventions (every comparison):")[1].strip(),
        "arms": {
            "base + cue": "allenai/Olmo-3-1025-7B @ a81bae42, pair1 prompt in the RL tokenizer's chat template + prefix ' line!\\n\\nOkay' (ids 1584 2268 33413)",
            "RL plain": "allenai/Olmo-3.1-7B-RL-Zero-Math @ 364820b0, pair1 prompt, no prefix",
            "Think-SFT + cue": "allenai/Olmo-3-7B-Think-SFT @ 6ff85758 (loaded as /tmp/theta, label sft1), same template and cue as the base; not its own ChatML/<think> format",
            "M(2)": "Think-SFT + 2 x (RL-Math - base), every tensor (jobs/delta_sum.py, BF16 stochastic rounding), cue",
            "dial 1.5x": "base + top-8 singular directions per matrix of (RL-Math 3.1 - base) at scale 1.5 (jobs/wsp_edit.py top8 --scale 1.5), cue",
            "step 100 + cue": "allenai/Olmo-3.1-7B-RL-Zero-Math @ 0a45720c (branch step_0100), cue",
            "sampling": "T 1.0 / top-p 1.0, grader v3, first attempt only (restarts ignored), cap 16,384 unless stated",
        },
        "comparisons_16384": cmps,
        "cap32_run": {"comparisons": c32, "per_model": per_model, "stored_16384_cells_vs_this_run_at_16384": stored_vs_run,
                      "M2_at_16384_vs_ThinkSFT_at_32768": cross},
        "matched_difficulty_control": ctrl,
        "no_cap_with_room": room,
        "pending": {
            "M(2) at cap 32,768 on hard328, seed 3,000,000": "second M(2) sample (amendment 3, work-8b4030, vast.ai job ending f975); not in git. "
                                                             "The seed-3,010,000 sample is in (cap32_run.comparisons 'M(2) - Think-SFT (seed 3,010,000)').",
            "Think-SFT at cap 32,768, samples 2 and 3 on hard328 and 4 samples on fresh2026 (work-dc9359)":
                "rows not in git (README quotes 235 and 232 for hard328 samples 2-3 and the vote 238 -> 244; not recomputed). "
                "In git: sample 0 (results/cap32/rows-01) and sample 1 (inside results/transplant/cap32_m2_s1-01/rows.jsonl).",
        },
        "figure": fig,
        "review": review(C, c32, CH, per_model, {"Think-SFT + cue (seed 3,000,000)": s_raw, "RL plain": r_raw, "base + cue": b_raw,
                                                 "M(2) (seed 3,010,000)": m_raw, "Think-SFT + cue (seed 3,010,000)": t_raw},
                         (m16, m32, t16, t32, m_raw, t_raw)),
        "checks_against_readouts": CHECKS,
    }
    (HERE / "facts.json").write_text(json.dumps(facts, indent=1) + "\n")

    # ---- examples
    hard = json.loads((STUDY / "data/rln3/hard.json").read_text())
    text = {h["unique_id"]: h for h in hard}
    late = [p for p in sorted(s_raw) if s_raw[p]["n_new"] > 16384 and s_raw[p]["score_v3"] == 1 and not s_raw[p]["cap_hit"]]
    both = [p for p in late if not r_raw[p]["cap_hit"] and r_raw[p]["n_new"] <= 16384 and r_raw[p]["score_v3"] == 0]
    p = both[0]
    assert s_raw[p]["unique_id"] == r_raw[p]["unique_id"]
    h = text[s_raw[p]["unique_id"]]

    def ex(r, cap):
        return {"tokens": r["n_new"], "cut_off": r["cap_hit"], "answer": r["extracted_v3"], "right": r["score_v3"],
                "right_at_16384": int(r["score_v3"] == 1 and r["n_new"] <= 16384 and not r["cap_hit"]), "tail": r["tail"][-300:]}
    examples = {"problem_index": p, "unique_id": h["unique_id"], "problem_head": h["problem"][:400], "gold": h["answer"],
                "why_this_one": f"first of {len(both)} problems where Think-SFT is cut off at 16,384 and right at 32,768 while RL "
                                f"finishes wrong under 16,384 (so wrong at both caps); {len(late)} problems have the Think-SFT half",
                "think_sft_cue_cap32_run": ex(s_raw[p], 32768), "rl_plain_cap32_run": ex(r_raw[p], 32768),
                "stored_16384_samples": {k: [{"right": x["s"], "cut_off": x["c"], "tokens": x["t"], "answer": x["e"]} for x in C[c]["p"][p]]
                                         for k, c in (("think_sft", "h_sft"), ("rl", "h_rl"), ("base", "h_base"), ("M2", "h_M2"))},
                "source": "results/cap32/rows-01/{sft_cue,rl_plain}.jsonl; problem text data/rln3/hard.json"}
    (HERE / "examples.json").write_text(json.dumps(examples, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(CHECKS)} checks pass; wrote {rel(HERE / 'facts.json')}, {rel(HERE / 'examples.json')}")


if __name__ == "__main__":
    main()
